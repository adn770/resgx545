#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The render context's words by the glossary's names, the 11.10 and 11.12 tables, and the
driver's recovery lines in a run's kernel log, case by case: the kernel's debugfs
render_words (a line per word, `space:N=0x...`, as the kernel poke spells it) of the HW render
context (ctx, 17 words), the RT data set (rtds, 20), the PB descriptor (pb, 15), the kernel's own
words (kw: the access word, the pending count, the render target's status, the background
update list) and the render details (rd, 123), named by harness/ukernel-extract/kick3d.py's
layouts; the RT data set's counts (the kernel's pending count, kw:1, against the firmware's
executed count, rtds:1); the kernel's word addresses, from the context page; the 11.10 scripts'
output (snapshots before the first render and after each, the TA/3D control block, the cleanup
trace); the driver's lines of a kernel log by the case each follows (a "resgx545 case NAME"
mark) and by kind: a fault or hang found, a recovery held, a failed cleanup, the core stopped,
the reset, the boot.

    render_words.py tables DIR         write the 11.10 and 11.12 tables under DIR (probes/...)
    render_words.py show FILE          a render_words file, a named word a line
    render_words.py diff A B           the words that differ between two files
    render_words.py report FILE        each case of a script's output: counts by snapshot,
                                       the words each snapshot changed, the cleanup's result
    render_words.py log FILE           a kernel log's driver lines: kinds counted per case,
                                       the time a recovery was held and the lines meanwhile
"""
from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "harness" / "ukernel-extract"))
import kick3d  # noqa: E402

# The render spaces and the structure each holds (kick3d.STRUCTS).
STRUCT = {"ctx": "hw_render_context", "rtds": "hw_rt_data_set", "pb": "hw_pb_desc",
          "rd": "hw_render_details"}
# The kernel's words for the context, in its control page from offset 0x208 (linux fork,
# sgxfive_ctx.h SGXFIVE_RCTX_*): what render details word 52 points at, what the RT data set's
# word 0 points at, the RT data's status words, the background primary-PDS update list.
KW = ["access", "pending_count", "rt_status", "bgpri_list"]
KW_OFF = {"access": 0x208, "pending": 0x20c, "rt_status": 0x210, "bgpri": 0x214,
          "rtds": 0x300, "pbdesc": 0x380}
CCB_CTL_OFF = 0x100               # the context page's CCB control (hw_render_context word 4)
LINE = re.compile(r"^(ctx|rtds|pb|kw|rd):(\d+)=(0x[0-9a-fA-F]+)$")
CASE = re.compile(r"^== (\S+?):(?: |$)")
TA3D = re.compile(r"^ta3d (\w+):(.*)$")


def _leaf_names(struct: str) -> list[str]:
    """A name per dword of a kick3d structure: arrays by [i], multi-dword elements by .k."""
    out = [""] * kick3d._dwords(kick3d.STRUCTS[struct])
    for path, off, width, count, array in kick3d._layout(kick3d.STRUCTS[struct]):
        for i in range(count):
            for k in range(width):
                n = f"{struct}.{path}"
                if array:
                    n += f"[{i}]"
                if width > 1:
                    n += f".{k}"
                out[off + i * width + k] = n
    return out


def names(space: str) -> list[str]:
    """The names of a space's words, in order."""
    if space == "kw":
        return [f"kernel.{k}" for k in KW]
    return _leaf_names(STRUCT[space])


def name(space: str, index: int) -> str:
    if space not in STRUCT and space != "kw":
        raise KeyError(space)
    return names(space)[index]


def parse(text: str) -> dict[str, dict[int, int]]:
    """{space: {word: value}} of a render_words file; other lines are skipped."""
    out: dict[str, dict[int, int]] = {}
    for line in text.splitlines():
        if m := LINE.match(line.strip()):
            out.setdefault(m[1], {})[int(m[2])] = int(m[3], 16)
    return out


def counts(w: dict) -> dict[str, int]:
    """The RT data set's counts: the kernel's pending count (kw:1), the firmware's executed
    count (rtds:1), the out-of-memory and partial-render counts (rtds:3, 4), and the
    context's submitted commands (ctx:5)."""
    def g(s, i):
        return w.get(s, {}).get(i, 0)
    return {"pending": g("kw", 1), "executed": g("rtds", 1), "oom": g("rtds", 3),
            "spm": g("rtds", 4), "submitted": g("ctx", 5)}


def kernel_addresses(w: dict) -> dict[str, int]:
    """The device addresses of the kernel's words, from the context page (the HW render
    context's CCB control, word 4, less 0x100)."""
    page = w["ctx"][4] - CCB_CTL_OFF
    return {"page": page, **{k: page + off for k, off in KW_OFF.items()}}


def pointers(w: dict) -> dict[str, str]:
    """What the pointer words of the snapshot name among the kernel's words and structures."""
    a = kernel_addresses(w)
    at = {a["access"]: "kernel.access", a["pending"]: "kernel.pending_count",
          a["rt_status"]: "kernel.rt_status", a["bgpri"]: "kernel.bgpri_list",
          a["rtds"]: "hw_rt_data_set", a["pbdesc"]: "hw_pb_desc", a["page"]: "hw_render_context"}
    out = {}
    for space, words in w.items():
        for i, v in words.items():
            if v in at:
                out[f"{space}:{i}"] = at[v]
    return out


def diff(a: dict, b: dict) -> list[tuple[str, int, int, int]]:
    """(space, word, before, after) of every word that differs, in space and word order."""
    out = []
    for space in ("ctx", "rtds", "pb", "kw", "rd"):
        wa, wb = a.get(space, {}), b.get(space, {})
        for i in sorted(set(wa) | set(wb)):
            if wa.get(i, 0) != wb.get(i, 0):
                out.append((space, i, wa.get(i, 0), wb.get(i, 0)))
    return out


def diff_lines(a: dict, b: dict) -> list[str]:
    return [f"{s}:{i} {name(s, i)} {x:#010x} -> {y:#010x}" for s, i, x, y in diff(a, b)]


def _label(s: str):
    """A snapshot's label: its render number, or a word (held, after)."""
    return int(s) if s.isdigit() else s


def _order(label) -> tuple:
    return (isinstance(label, str), str(label) if isinstance(label, str) else label)


def case_words(out: str) -> dict[str, dict]:
    """{case: {"words": {N: parsed}, "ta3d": {N: dwords}, "cleanup": lines, "cleanup_ret":
    int or None, "lines": the rest}} of an 11.10 script's output. A snapshot is labelled by
    the render it follows (0 before the first) or by a word: "held" while recovery is held,
    "after" once the context is gone."""
    res: dict[str, dict] = {}
    cur = block = None
    for line in out.splitlines():
        if m := CASE.match(line):
            cur = {"words": {}, "ta3d": {}, "cleanup": [], "cleanup_ret": None, "lines": []}
            res[m[1]] = cur
            block = None
        elif cur is None:
            continue
        elif line.startswith("#### words "):
            block = _label(line.split()[2])
            cur["words"][block] = {}
        elif line == "#### end":
            block = None
        elif block is not None:
            if m := LINE.match(line.strip()):
                cur["words"][block].setdefault(m[1], {})[int(m[2])] = int(m[3], 16)
        elif m := TA3D.match(line):
            cur["ta3d"][_label(m[1])] = [int(x, 16) for x in m[2].split()]
        elif line.startswith("cleanup: "):
            cur["cleanup"].append(line[len("cleanup: "):])
            if (r := re.search(r" ret (-?\d+)$", line)) and cur["cleanup_ret"] is None:
                cur["cleanup_ret"] = int(r[1])
        else:
            cur["lines"].append(line)
    return res


def report(out: str) -> str:
    """Each case: the cleanup's result, then per snapshot the context it shows (render_words
    shows the newest), the counts, the TA/3D control block's DPM slot words (20, 21) and TA
    RT data (25), and the words it changed."""
    lines = []
    for case, c in case_words(out).items():
        lines.append(f"{case}: cleanup ret {c['cleanup_ret']}")
        prev = None
        for n in sorted(c["words"], key=_order):
            w = c["words"][n]
            k = counts(w)
            t = c["ta3d"].get(n, [])
            slots = " ".join(f"{d}={t[d]:#x}" for d in (20, 21, 25) if d < len(t))
            page = f"{w['ctx'][4] - CCB_CTL_OFF:#x}" if 4 in w.get("ctx", {}) else "-"
            lines.append(f"  {n}: ctx {page} pending {k['pending']} executed {k['executed']}"
                         f" oom {k['oom']} spm {k['spm']} submitted {k['submitted']}"
                         + (f"; ta3d {slots}" if slots else ""))
            if prev is not None:
                lines += [f"     {d}" for d in diff_lines(prev, w)]
            prev = w
    return "\n".join(lines) + "\n"


# ---- the driver's lines in a kernel log ----

# kind: the line's pattern (linux fork: sgxfive.c, sgxfive_sched.c, sgxfive_debug.c,
# sgxfive_render.c); the job number, where the line names one, is the group "job"
KINDS = [
    ("fault", r"sgxfive: BIF fault .* stalls job (?P<job>\d+), recovering"),
    ("held", r"sgxfive: job (?P<job>\d+) hung, recovery held"),
    ("hang", r"sgxfive: job (?P<job>\d+) hung, recovering"),
    ("cleanup-failed", r"sgxfive: render context cleanup failed"),
    ("stopped", r"SGX stopped, \d+ events seen"),
    ("reset", r"SGX reset: "),
    ("boot", r"SGX boot: kicking the EDM"),
    ("up", r"SGX boot: EDM up after"),
    ("failed", r"SGX recovery failed"),
]
KLINE = re.compile(r"^\[\s*(\d+\.\d+)\]\s(.*)$")
KMARK = re.compile(r"resgx545 case (\S+)")


def kernel_lines(log: str) -> dict[str, list[dict]]:
    """{case: [{"t": seconds, "kind": kind, "job": int or None, "text": line}]}: the driver's
    lines of a kernel log by the "resgx545 case NAME" mark they follow ("" before any)."""
    res: dict[str, list[dict]] = {"": []}
    cur = ""
    for line in log.splitlines():
        if not (m := KLINE.match(line)):
            continue
        t, text = float(m[1]), m[2]
        if mk := KMARK.search(text):
            cur = mk[1]
            res.setdefault(cur, [])
            continue
        for kind, pat in KINDS:
            if k := re.search(pat, text):
                job = k.groupdict().get("job")
                res[cur].append({"t": t, "kind": kind, "job": int(job) if job else None,
                                 "text": text})
                break
    return res


def log_report(log: str) -> str:
    """Per case: the kinds counted, in first-seen order; while a recovery was held, from the
    held line to the next reset, the time and the driver's lines between them."""
    out = []
    for case, ls in kernel_lines(log).items():
        if not ls:
            continue
        kinds: dict[str, int] = {}
        for x in ls:
            kinds[x["kind"]] = kinds.get(x["kind"], 0) + 1
        out.append(f"{case or '-'}: " + ", ".join(f"{k} {n}" for k, n in kinds.items()))
        for i, x in enumerate(ls):
            if x["kind"] != "held":
                continue
            end = next((j for j in range(i + 1, len(ls))
                        if ls[j]["kind"] in ("stopped", "reset")), None)
            if end is None:
                out.append(f"{case or '-'}: held {x['t']:.3f}, no reset")
                continue
            r = next(j for j in range(end, len(ls)) if ls[j]["kind"] == "reset") \
                if any(y["kind"] == "reset" for y in ls[end:]) else end
            out.append(f"{case or '-'}: held {x['t']:.3f} to reset {ls[r]['t']:.3f} "
                       f"({ls[r]['t'] - x['t']:.3f} s), {end - i - 1} lines between")
    return "\n".join(out) + "\n"


# ---- the 11.10 and 11.12 tables ----

# path: (what it asks, needs, extra top-level fields)
TABLES = {
    "render/pending-counts": (
        "Q029: the pending and executed counts of one to four kicks, read while the context "
        "lives", ["render", "kpoke", "render_words", "render_cleanup", "buf09"], {}),
    "render/pending-rd54": (
        "Q029: render details word 54 moved by 0x8, the counts read",
        ["render", "kpoke", "render_words", "render_cleanup", "buf09"], {}),
    "render/pending-kw": (
        "Q029: the pending count poked one off, and the set's pointer to it moved",
        ["render", "kpoke", "render_words", "render_cleanup", "buf09"], {}),
    "render/slot-words": (
        "Q041: the DPM slot words, the access word and rtds_keep",
        ["render", "kpoke", "render_words", "render_cleanup", "buf09", "rtds_keep", "regs"], {}),
    "render/hold-fault": (
        "Q028, Q003: a faulting render held, the state read, another context's job",
        ["render", "render_words", "render_param", "render_tadata", "hold_recovery", "reset",
         "regs", "kreg", "miscinfo", "status"], {}),
    "render/hold-hang": (
        "Q037, Q028: hung jobs' render memory saved while recovery is held",
        ["render", "render_param", "render_tadata", "hold_recovery", "reset", "regs", "kreg",
         "miscinfo"], {"stage": ["vdm/state1"]}),
    "render/ta3d-ro": (
        "Q006: renders with the TA/3D control block read-only in the client VM",
        ["render", "alias_ta3d_ro", "hold_recovery", "reset", "regs", "render_words"], {}),
    "edm/ta-syncs": (
        "Q034: one context's TA command with an incomplete sync",
        ["render", "kpoke", "render_words", "buf09"], {}),
    "edm/miscinfo-reset": (
        "Q005: GETMISCINFO's answer after a reset, timed", ["render", "reset", "miscinfo"], {}),
    "render/kick-objects-again": (
        "11.6's scenes of one to three kicks again, the kernel counting each kick (E288)",
        ["render", "render_param", "render_tadata", "render_cleanup"], {}),
    "render/held-reset": (
        "render_uapi.md section 13: a reset ending a held fault or hang, a failed cleanup "
        "while held",
        ["render", "hold_recovery", "reset", "miscinfo", "status", "render_cleanup"],
        {"stage": ["vdm/state1"]}),
    "render/replay-pending": (
        "render_uapi.md section 13: the pending count of the renders a reset runs again", ["render", "kpoke", "render_words", "buf09", "hold_recovery",
                            "reset"], {}),
}


def _toml(v) -> str:
    if isinstance(v, str):
        return '"' + v.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return "[" + ", ".join(_toml(x) for x in v) + "]"


def _field(key: str, v) -> str:
    """key = value, a list too long for one line wrapped a few items a line."""
    one = f"{key} = {_toml(v)}"
    if len(one) <= 100 or isinstance(v, str):
        return one
    rows, cur = [], ""
    for x in v:
        item = _toml(x) + ","
        if cur and len(cur) + 1 + len(item) > 95:
            rows.append(cur)
            cur = ""
        cur = f"{cur} {item}" if cur else item
    rows.append(cur)
    return f"{key} = [\n" + "".join(f"    {r}\n" for r in rows) + "]"


def tables() -> dict[str, str]:
    """The 11.10 and 11.12 tables' text: script tables, none with probes of its own."""
    out = {}
    for path, (about, needs, extra) in TABLES.items():
        unit, feature = path.split("/")
        lines = ["# SPDX-License-Identifier: MIT", "# SPDX-FileCopyrightText: 2026 Josep Torra",
                 f"# {unit} {feature.replace('-', ' ')}: 0 probes (written by "
                 "tools/usse-asm/render_words.py).", f"# {about}", _field("needs", needs),
                 f'name = "{unit}-{feature}"', f'script = "{feature}.sh"']
        lines += [_field(k, v) for k, v in extra.items()]
        out[path] = "\n".join(lines) + "\n"
    return out


# ---- the command line ----

def main(argv: list[str] | None = None) -> int:
    a = sys.argv[1:] if argv is None else argv
    if a[:1] == ["tables"] and len(a) == 2:
        for path, text in tables().items():
            f = pathlib.Path(a[1]) / "probes" / f"{path}.toml"
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(text)
        return 0
    if a[:1] == ["show"] and len(a) == 2:
        w = parse(pathlib.Path(a[1]).read_text())
        for space in ("ctx", "rtds", "pb", "kw", "rd"):
            for i, v in sorted(w.get(space, {}).items()):
                print(f"{space}:{i} {name(space, i)} {v:#010x}")
        return 0
    if a[:1] == ["diff"] and len(a) == 3:
        print("\n".join(diff_lines(parse(pathlib.Path(a[1]).read_text()),
                                   parse(pathlib.Path(a[2]).read_text()))))
        return 0
    if a[:1] == ["log"] and len(a) == 2:
        print(log_report(pathlib.Path(a[1]).read_text(errors="replace")), end="")
        return 0
    if a[:1] == ["report"] and len(a) == 2:
        print(report(pathlib.Path(a[1]).read_text()), end="")
        return 0
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
