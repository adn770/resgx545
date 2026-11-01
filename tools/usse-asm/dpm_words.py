#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The parameter buffer and the DPM by the glossary's names, and the 11.9 tables: the page table
(one 32-bit entry per page at the descriptor's page_table_base, the previous page in the high
half and the next in the low half, 0xffff at the ends: hw_pb_desc.page_table_base), the free
list it chains, the DPM status words (CR_DPM_*_FREE_LIST_STATUS1 the list's tail and head,
STATUS2 the page before the tail), the TA data's DPM state page (DPM_STATE_LIST: a page list
per macrotile and the global list), the TA/3D control block's out-of-memory words, and the
readers of the 11.9 scripts' output (registers, page-table walks, tile maps, timelines).

    dpm_words.py tables DIR            write the 11.9 tables under DIR (probes/dpm/...)
    dpm_words.py pt PARAM PAGES        a render dump's page table walked from its head
    dpm_words.py state TADATA W H      a render dump's DPM state page (context up to W x H)
    dpm_words.py free-list FILE        each case of the free-list script: walk, status, lists
    dpm_words.py tiles FILE            each case of the partial-render script against its
                                       reference, by macrotile
    dpm_words.py timeline FILE         each case's partial renders from a timeline script

The render dump (pbdump.py) starts at the parameter slot's offset 0x1000; the kernel's page
table is at slot offset 0x423000 (dump offset 0x422000), indexed by page number.
"""
from __future__ import annotations

import collections
import pathlib
import re
import struct
import sys

END = 0xffff                      # the missing neighbour at either end of a list
DUMP_BASE = 0x1000                # the dump's first byte, as a parameter slot offset
PT_SLOT = 0x423000                # the kernel's page table, as a slot offset
STATE_LISTS = 17                  # DPM_STATE_LIST entries: 16 macrotiles, then the global list
G, B, S = 0xff00ff00, 0xff203040, 0xdeadbeef   # triangle, background, sentinel

# TA3DCtl dwords of the out-of-memory path (kick3d.py TA3DCTL; E160)
TA3DCTL_OOM = {33: "saved_ta_global_list", 35: "abort_page_count0", 36: "abort_page_count1",
               37: "threshold_ta_global_list", 38: "zls_threshold_step",
               39: "abort_status_mtile", 40: "abort_rt_index"}


# ---- the page table and the free list ----

def host_page_table(pages: int) -> list[int]:
    """The kernel's page table for a PB of pages 1..pages: entry i links i - 1 and i + 1
    (sgx_render_pb), entries 0 and pages + 1 zero."""
    pt = [0] * (pages + 2)
    for i in range(1, pages + 1):
        pt[i] = (END if i == 1 else i - 1) << 16 | (END if i == pages else i + 1)
    return pt


def read_page_table(param: bytes, pages: int) -> list[int]:
    """Entries 0..pages + 1 of a render dump's page table."""
    return list(struct.unpack_from(f"<{pages + 2}I", param, PT_SLOT - DUMP_BASE))


def walk(pt: list[int], pages: int) -> dict:
    """The free list a page table chains: its head (the one entry whose previous page is
    END), its pages in order along the next links, its tail and the page before the tail, and
    the pages whose previous link is not the page walked before them."""
    heads = [i for i in range(1, pages + 1) if pt[i] >> 16 == END]
    order, seen = [], set()
    i = heads[0] if heads else END
    while i != END and i not in seen and 1 <= i <= pages:
        seen.add(i)
        order.append(i)
        i = pt[i] & 0xffff
    bad = [j for k, j in enumerate(order[1:]) if pt[j] >> 16 != order[k]]
    tail = order[-1] if order else END
    return {"heads": heads, "head": heads[0] if heads else END, "tail": tail,
            "prev_of_tail": pt[tail] >> 16 if order else END, "order": order, "bad": bad}


def page_runs(order: list[int]) -> str:
    """Pages as runs of consecutive numbers: 0x3-0x422,0x1-0x2."""
    runs, start = [], None
    for a, b in zip(order, order[1:] + [None]):
        start = a if start is None else start
        if b != a + 1:
            runs.append(f"{start:#x}" if start == a else f"{start:#x}-{a:#x}")
            start = None
    return ",".join(runs)


def run_pages(runs: str) -> list[int]:
    """The pages of page_runs()' text, in order: 0x3-0x5,0x1 is 3, 4, 5, 1."""
    out = []
    for run in filter(None, runs.split(",")):
        a, _, b = run.partition("-")
        out += range(int(a, 16), int(b or a, 16) + 1)
    return out


def free_list_word(w: int) -> dict:
    """A free-list word (CR_DPM_*_FREE_LIST_STATUS1, CR_DPM_TA_ALLOC_FREE_LIST,
    hw_pb_desc.current_stack_top): the tail page in the high half, the head in the low."""
    return {"TAIL": w >> 16, "HEAD": w & 0xffff}


def status2_word(w: int) -> dict:
    """CR_DPM_*_FREE_LIST_STATUS2: the page before the tail in the low half (the descriptor's
    dpm_ta_alloc holds it in the high half, as the store shifts it)."""
    return {"PREV": w & 0xffff, "HIGH": w >> 16}


def status_check(regs: dict[int, int], w: dict) -> list[str]:
    """Where the free-list status registers read in regs disagree with a page-table walk."""
    out = []
    for r in (0x0700, 0x070c):
        if r in regs:
            f = free_list_word(regs[r])
            for k in ("TAIL", "HEAD"):
                if f[k] != w[k.lower()]:
                    out.append(f"{r:#06x} {k} {f[k]:#x}, walk {w[k.lower()]:#x}")
    for r in (0x0710, 0x071c):
        if r in regs and status2_word(regs[r])["PREV"] != w["prev_of_tail"]:
            out.append(f"{r:#06x} PREV {status2_word(regs[r])['PREV']:#x}, "
                       f"walk {w['prev_of_tail']:#x}")
    return out


# ---- the TA data and its DPM state page ----

def mtile_grid(width: int, height: int) -> tuple[int, int, int]:
    """(macrotiles each way, tiles across one, tiles down one) of the kernel's layout
    (sgx_render_layout): 4 from 640 x 480 pixels on, else 2; whole 4-tile blocks."""
    tx, ty = -(-width // 32), -(-height // 16)
    n = 4 if width * height >= 640 * 480 else 2
    mx = -(-(-(-tx // n)) // 4) * 4
    my = -(-(-(-ty // n)) // 4) * 4
    return n, mx, my


def macrotile(x: int, y: int, width: int, height: int) -> int:
    """The macrotile of tile (x, y), numbered down then across, as the DPM state page's lists
    are (DPM_STATE_LIST; E311). Measured on the 4 x 4 grid only: for a 2 x 2 grid the numbering
    by n is assumed."""
    n, mx, my = mtile_grid(width, height)
    return (x // mx) * n + y // my


def tadata_layout(width: int, height: int) -> dict:
    """The kernel's TA data of a context for targets up to width x height
    (sgx_render_tadata_layout): offsets of the tail pointers, DPM control, OTPM, DPM state,
    region headers and ZLS region headers, and the size."""
    n, mx, my = mtile_grid(width, height)
    side = 1
    while side < max(n * mx, n * my):
        side <<= 1
    page = lambda b: -(-b // 4096) * 4096     # noqa: E731
    rgn = 0xc0 * (mx // 4) * (my // 4) * n * n
    t = {"tail": 0, "control": page(4 * side * side)}
    t["otpm"] = t["control"] + 0x1000
    t["state"] = t["otpm"] + 0x1000
    t["rgn"] = t["state"] + 0x1000
    t["zls"] = t["rgn"] + page(rgn)
    t["size"] = t["zls"] + page(rgn)
    return t


def state_lists(words: list[int]) -> list[dict]:
    """The non-empty DPM_STATE_LIST entries of a DPM state page: two dwords each, the page
    count in the first's high half and the head in its low half, the tail in the second;
    entries 0-15 a macrotile's list, 16 the global list."""
    out = []
    for k in range(STATE_LISTS):
        a, b = words[2 * k], words[2 * k + 1]
        if a or b:
            out.append({"index": k, "list": "global" if k == 16 else f"macrotile {k}",
                        "PAGE_COUNT": a >> 16, "HEAD": a & 0xffff, "TAIL": b & 0xffff})
    return out


def list_chain(pt: list[int], lst: dict) -> list[int]:
    """A state list's pages along the page table's next links, from its head to its tail."""
    out, i = [lst["HEAD"]], lst["HEAD"]
    while i != lst["TAIL"] and len(out) <= lst["PAGE_COUNT"] and 0 < i < len(pt):
        i = pt[i] & 0xffff
        out.append(i)
    return out


def ta3dctl_oom(words: list[int]) -> dict:
    """The TA/3D control block's out-of-memory words by kick3d.py's names."""
    return {name: words[i] for i, name in TA3DCTL_OOM.items() if i < len(words)}


# ---- the script readers ----

CASE = re.compile(r"^== (\S+?):(?: |$)")
REG = re.compile(r"reg (0x[0-9a-f]{4}) (0x[0-9a-f]{8})")


def _cases(out: str) -> dict[str, list[str]]:
    cases, cur = {}, None
    for line in out.splitlines():
        if m := CASE.match(line):
            cur = m[1]
            cases[cur] = []
        elif cur is not None:
            cases[cur].append(line)
    return cases


def case_free_list(out: str) -> dict[str, dict]:
    """{case: registers, TA3DCtl, the walk's numbers and order, the TA data's DPM pages}."""
    res = {}
    for name, lines in _cases(out).items():
        c = {"regs": {}, "ta3dctl": [], "walk": {}, "order": "", "tadata": {}, "lines": []}
        for line in lines:
            if line.startswith(("regs:", "reg ")):
                c["regs"].update({int(r, 16): int(v, 16) for r, v in REG.findall(line)})
            elif line.startswith("ta3dctl:"):
                c["ta3dctl"] = [int(x, 16) for x in line.split()[1:]]
            elif m := re.match(r"pt: walk (\d+) pages, tail (\S+) prev of tail (\S+) bad prev "
                               r"(\d+)", line):
                c["walk"] = {"pages": int(m[1]), "tail": int(m[2], 16),
                             "prev_of_tail": int(m[3], 16), "bad": int(m[4])}
            elif line.startswith("pt: order "):
                c["order"] = line[len("pt: order "):]
            elif m := re.match(r"tadata (\w+): nonzero \d+ ?(.*)$", line):
                c["tadata"][m[1]] = {int(a, 16): int(b, 16) for a, b in
                                     re.findall(r"(0x[0-9a-f]+)=(0x[0-9a-f]+)", m[2])}
            else:
                c["lines"].append(line)
        if c["walk"]:
            res[name] = c
    return res


def case_tiles(out: str) -> dict[str, dict]:
    """{case: the tile map's rows, the pixel counts, whether the job overflowed, lines}."""
    res = {}
    for name, lines in _cases(out).items():
        c = {"map": [], "pixels": {}, "overflow": False, "regs": {}, "ta3dctl": [],
             "lines": []}
        for line in lines:
            if m := re.match(r"tiles +\d+: (\S+)$", line):
                c["map"].append(m[1])
            elif line.startswith("pixels: "):
                f = line.split()[1:]
                c["pixels"] = {f[i]: int(f[i + 1]) for i in range(0, len(f), 2)}
            elif line.startswith("reg "):
                c["regs"].update({int(r, 16): int(v, 16) for r, v in REG.findall(line)})
            elif line.startswith("ta3dctl:"):
                c["ta3dctl"] = [int(x, 16) for x in line.split()[1:]]
            else:
                c["overflow"] |= "overflowed" in line
                c["lines"].append(line)
        res[name] = c
    return res


def tile_compare(ref: list[str], case: list[str]) -> dict[str, int]:
    """Over the tiles holding triangle in the reference map (G or g), how many of each
    (reference -> case) pair."""
    out = collections.Counter()
    for rr, rc in zip(ref, case):
        for a, b in zip(rr, rc):
            if a in "Gg":
                out[f"{a}->{b}"] += 1
    return dict(out)


def tile_compare_by_mtile(ref: list[str], case: list[str], width: int,
                          height: int) -> dict[int, dict[str, int]]:
    """tile_compare per macrotile (macrotile())."""
    out: dict[int, collections.Counter] = collections.defaultdict(collections.Counter)
    for y, (rr, rc) in enumerate(zip(ref, case)):
        for x, (a, b) in enumerate(zip(rr, rc)):
            if a in "Gg":
                out[macrotile(x, y, width, height)][f"{a}->{b}"] += 1
    return {k: dict(v) for k, v in sorted(out.items())}


def case_timelines(out: str) -> dict[str, dict]:
    """{case: the sampled registers and each sample (time in ns, {register: value})} from
    regtimeline's "timeline: regs ..." header and "tl NS WORD..." lines."""
    res = {}
    for name, lines in _cases(out).items():
        regs, samples = [], []
        for line in lines:
            if line.startswith("timeline: regs "):
                regs = [int(x, 16) for x in line.split()[2:] if x.startswith("0x")]
            elif line.startswith("tl ") and regs:
                f = line.split()
                samples.append((int(f[1]), dict(zip(regs, (int(x, 16) for x in f[2:])))))
        if regs:
            res[name] = {"regs": regs, "samples": samples}
    return res


def partial_stretches(tl: dict) -> list[dict]:
    """The stretches where CR_DPM_PARTIAL_RENDER (0x0658) reads 1: start and end times (the
    sample that ends it), and at their first sample CR_DPM_ABORT_STATUS_MTILE (0x0720),
    CR_DPM_PAGE_STATUS (0x0724) and CR_DPM_STATE_CONTEXT_ID (0x0630)."""
    out, cur = [], None
    for t, v in tl["samples"]:
        on = v.get(0x0658, 0) == 1
        if on and cur is None:
            cur = {"start": t, "abort_mtile": v.get(0x0720), "page_status": v.get(0x0724),
                   "context_id": v.get(0x0630)}
        elif not on and cur is not None:
            cur.update(end=t, ns=t - cur["start"])
            out.append({k: cur[k] for k in ("start", "end", "ns", "abort_mtile",
                                            "page_status", "context_id")})
            cur = None
    return out


def register_changes(tl: dict, reg: int) -> list[tuple[int, int]]:
    """(time, value) at each change of one register."""
    out, last = [], None
    for t, v in tl["samples"]:
        if v.get(reg) != last:
            last = v.get(reg)
            out.append((t, last))
    return out


# ---- the 11.9 tables ----

GREEN_PROBE = {"source": "pix_op.s", "host": "tri", "slot": "pixel", "dump_render": True,
               "size": [0x40, 0x40], "inputs": ["OP"], "labels": ["green"],
               "cases": [["mov.skipinv.end o0, #0xFF00FF00"]]}

TABLES = {
    "dpm/free-list": (
        "Q036, Q067, Q045: the page table, the DPM status registers and the TA data's DPM pages",
        ["render", "render_param", "render_tadata", "render_pb_pages", "regs", "buf09"],
        "the 64x64 triangle with a green pixel shader, its render memory dumped (the script's "
        "jobs run this shader)"),
    "dpm/partial-renders": (
        "Q038: the missing pixels of an overflowing scene by tile, with and without empty "
        "tiles drawn", ["render", "kpoke", "render_pb_pages", "buf09"], None),
    "dpm/partial-timelines": (
        "Q038, Q036, Q045: the DPM registers through each partial render",
        ["render", "render_pb_pages"], None),
    "dpm/state-base": (
        "CR_DPM_REG_074C bit 8 against CR_DPM_STATE_BASE1",
        ["render", "kpoke", "render_param", "render_tadata", "render_pb_pages", "regs"],
        "the 64x64 triangle with a green pixel shader, its render memory dumped (the script's "
        "probe jobs run this shader)"),
}


def _toml(v) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return f"{v:#x}" if v >= 0x10 else str(v)
    if isinstance(v, str):
        return '"' + v.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return "[" + ", ".join(_toml(x) for x in v) + "]"


def tables() -> dict[str, str]:
    """The 11.9 tables' text: script tables, two with one probe each (the green shader the
    script stages and runs)."""
    out = {}
    for path, (about, needs, green) in TABLES.items():
        unit, feature = path.split("/")
        n = 1 if green else 0
        lines = ["# SPDX-License-Identifier: MIT", "# SPDX-FileCopyrightText: 2026 Josep Torra",
                 f"# {unit} {feature.replace('-', ' ')}: {n} probes (written by "
                 "tools/usse-asm/dpm_words.py).", f"# {about}", f"needs = {_toml(needs)}",
                 f'name = "{unit}-{feature}"', f'script = "{feature}.sh"']
        if green:
            p = {"name": f"{unit}-{feature}-green", "question": green, **GREEN_PROBE}
            lines.append("\n[[probe]]")
            lines += [f"{k} = {_toml(v)}" for k, v in p.items()]
        out[path] = "\n".join(lines) + "\n"
    return out


# ---- the command line ----

def _free_list_report(out: str) -> str:
    lines = []
    for name, c in case_free_list(out).items():
        w = c["walk"]
        st = free_list_word(c["regs"].get(0x0700, 0))
        head = run_pages(c["order"])[:1] or [END]
        lines.append(f"{name}: free list head {head[0]:#x} tail "
                     f"{w['tail']:#x} prev {w['prev_of_tail']:#x}; STATUS1 tail "
                     f"{st['TAIL']:#x} head {st['HEAD']:#x}, STATUS2 PREV "
                     f"{status2_word(c['regs'].get(0x0710, 0))['PREV']:#x}")
        state = c["tadata"].get("state", {})
        words = [state.get(4 * k, 0) for k in range(2 * STATE_LISTS)]
        for lst in state_lists(words):
            lines.append(f"  {lst['list']}: {lst['PAGE_COUNT']} pages, head {lst['HEAD']:#x}, "
                         f"tail {lst['TAIL']:#x}")
        oom = {k: v for k, v in ta3dctl_oom(c["ta3dctl"]).items() if v}
        if oom:
            lines.append("  ta3dctl " + " ".join(f"{k}={v:#x}" for k, v in oom.items()))
    return "\n".join(lines) + "\n"


SIZE = re.compile(r"(\d+)x(\d+)")


def _tiles_report(out: str) -> str:
    cases = case_tiles(out)
    lines = []
    for name, c in cases.items():
        m = SIZE.match(name)
        ref = m and next((k for k in cases if k.startswith(f"{m[0]}-pb0x422-ctl0xf0100")), None)
        if not ref:
            continue
        w, h = int(m[1]), int(m[2])
        px = c["pixels"]
        lines.append(f"{name}: {'overflow' if c['overflow'] else 'ok'}; triangle "
                     f"{px.get('triangle')} background {px.get('background')} sentinel "
                     f"{px.get('sentinel')}")
        for mt, d in tile_compare_by_mtile(cases[ref]["map"], c["map"], w, h).items():
            lost = {k: v for k, v in d.items() if k[-1] not in "Gg"}
            if lost:
                lines.append(f"  macrotile {mt}: " + " ".join(f"{k} {v}"
                                                              for k, v in sorted(lost.items())))
    return "\n".join(lines) + "\n"


def _timeline_report(out: str) -> str:
    lines = []
    for name, tl in case_timelines(out).items():
        st = partial_stretches(tl)
        lines.append(f"{name}: {len(tl['samples'])} samples, {len(st)} partial renders")
        for s in st:
            lines.append(f"  {s['start']} +{s['ns'] / 1e6:.2f} ms abort mtile "
                         f"{s['abort_mtile']:#x} page status {s['page_status']:#010x} context "
                         f"{s['context_id']}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    a = sys.argv[1:] if argv is None else argv
    if a[:1] == ["tables"] and len(a) == 2:
        for path, text in tables().items():
            f = pathlib.Path(a[1]) / "probes" / f"{path}.toml"
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(text)
        return 0
    if a[:1] == ["pt"] and len(a) == 3:
        pages = int(a[2], 0)
        w = walk(read_page_table(pathlib.Path(a[1]).read_bytes(), pages), pages)
        print(f"head {w['head']:#x} tail {w['tail']:#x} prev of tail {w['prev_of_tail']:#x} "
              f"bad {len(w['bad'])}: {page_runs(w['order'])}")
        return 0
    if a[:1] == ["state"] and len(a) == 4:
        t = pathlib.Path(a[1]).read_bytes()
        off = tadata_layout(int(a[2]), int(a[3]))["state"]
        for lst in state_lists(list(struct.unpack_from("<1024I", t, off))):
            print(f"{lst['list']}: {lst['PAGE_COUNT']} pages, head {lst['HEAD']:#x}, tail "
                  f"{lst['TAIL']:#x}")
        return 0
    readers = {"free-list": _free_list_report, "tiles": _tiles_report,
               "timeline": _timeline_report}
    if a[:1] and a[0] in readers and len(a) == 2:
        print(readers[a[0]](pathlib.Path(a[1]).read_text()), end="")
        return 0
    print(__doc__.strip(), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
