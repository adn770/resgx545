#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The vertex side of a render by the glossary's names, and the 11.8 tables: the VDM stream's
blocks (VDM_STATE1, VDM_INDEX0-3, VDM_TASK0-1, VDM_BLOCK.TERMINATE), the TA's object
(pbdump.object_fields: PB_OBJ), the region test of doc/specs/3d.md §10.2 against fresh
triangles, and the readers of the 11.8 scripts' output (pixels, the TA/3D control block).

    ta_words.py tables DIR            write the 11.8 tables under DIR (probes/<unit>/...)
    ta_words.py vdm WORD...           a VDM stream, block by block, by the glossary's fields
    ta_words.py object DIR NAME       a render dump's first object by the PB_OBJ fields
    ta_words.py regions DIR PROBE     the region test over a random-triangle probe's dumps
    ta_words.py pixels FILE A B       the pixels case A of a script's output shares with B
    ta_words.py states FILE           each case's TA/3D control block and cleanup lines

A block's type is its first word's bits 31:30 (1 a state block of two words, 2 an index list,
3 terminate), the reading the library's stream and its runs share (E059, E060, E188, E189);
an index list is its header, the index base, the trailing words its header's bits 22 and 23
announce (VDM_INDEX0.WORDS_PRESENT), and the vertex task's two words.
"""
from __future__ import annotations

import collections
import pathlib
import random
import re
import sys

import isp_words
import pbdump
import region_tiles

first_object = pbdump.first_object
f32 = isp_words.f32
SEED = 1108                      # the 11.8 random triangles
RANDOM_SIZE = 128                # their target, W = H
RANDOM_COUNT = 24


def _bits(w: int, hi: int, lo: int) -> int:
    return (w >> lo) & ((1 << (hi - lo + 1)) - 1)


def _state(w: list[int]) -> dict:
    s1 = w[1]
    return {"w0[29]": _bits(w[0], 29, 29), "w0[27:0]": _bits(w[0], 27, 0),
            "VDM_STATE1.BIT8": _bits(s1, 8, 8), "VDM_STATE1.BITS11_9": _bits(s1, 11, 9),
            "VDM_STATE1.BIT12": _bits(s1, 12, 12), "VDM_STATE1.BITS15_13": _bits(s1, 15, 13),
            "VDM_STATE1.BIT18": _bits(s1, 18, 18), "VDM_STATE1.BIT25": _bits(s1, 25, 25),
            "w1[7:0]": _bits(s1, 7, 0), "w1[31:26]": _bits(s1, 31, 26)}


def vdm_blocks(words: list[int]) -> list[dict]:
    """A VDM stream as its blocks: kind, first word's index, words and fields by name. A word
    whose type is not one of the three ends the walk as an "unknown" block."""
    out, i = [], 0
    while i < len(words):
        w = words[i]
        kind = w >> 30
        if kind == 1 and i + 1 < len(words):
            out.append({"kind": "state", "at": i, "words": words[i:i + 2],
                        "fields": _state(words[i:i + 2])})
            i += 2
        elif kind == 2:
            present = _bits(w, 23, 22)
            n = 2 + bin(present).count("1")
            blk = words[i:i + n + 2]
            f = {"VDM_INDEX0.PRIMITIVE_TOPOLOGY": _bits(w, 29, 26),
                 "VDM_INDEX0.WORDS_PRESENT": present, "w0[21:0]": _bits(w, 21, 0),
                 "index base": blk[1] if len(blk) > 1 else None}
            k = 2
            if present & 1 and k < len(blk):
                f["VDM_INDEX2.WORD"] = blk[k]
                k += 1
            if present & 2 and k < len(blk):
                f["VDM_INDEX3.INDEX_WRAP"] = blk[k]
                k += 1
            if k + 1 < len(blk):
                f["VDM_TASK0.MAX_VERTICES"] = blk[k] >> 28
                f["task w0[27:0]"] = _bits(blk[k], 27, 0)
                f["VDM_TASK1.OUTPUT_SIZE"] = blk[k + 1] >> 24
            out.append({"kind": "index", "at": i, "words": blk, "fields": f})
            i += len(blk)
        elif kind == 3:
            out.append({"kind": "terminate", "at": i, "words": [w], "fields": {}})
            i += 1
        else:
            out.append({"kind": "unknown", "at": i, "words": words[i:], "fields": {}})
            break
    return out


def vdm_text(words: list[int]) -> str:
    lines = []
    for b in vdm_blocks(words):
        lines.append(f"{b['at']:2d} {b['kind']}: " + " ".join(f"{w:08x}" for w in b["words"]))
        lines += [f"   {k} {v:#x}" if isinstance(v, int) and v > 9 else f"   {k} {v}"
                  for k, v in b["fields"].items()]
    return "\n".join(lines) + "\n"


# ---- the region test against fresh triangles ----

def random_triangles(seed: int, n: int, size: int) -> list[tuple]:
    """n triangles in 1/16 pixel on a size x size target, vertices from 1/8 of the target
    outside it to as far past its far edges, of at least 24 square pixels (seeded)."""
    rnd, out = random.Random(seed), []
    lo, hi = -size // 8 * 16, (size + size // 8) * 16
    while len(out) < n:
        t = tuple((rnd.randrange(lo, hi), rnd.randrange(lo, hi)) for _ in range(3))
        (ax, ay), (bx, by), (cx, cy) = t
        if abs((bx - ax) * (cy - ay) - (by - ay) * (cx - ax)) >= 2 * 24 * 256:
            out.append(t)
    return out


def predicted_regions(t16: tuple, width: int, height: int) -> dict:
    """{(column, row) of each 32 x 16 region of the target: (left tile, right tile)} that the
    fitted test (region_tiles.tiles: bounding box, then edges, against the 16 x 16 tiles)
    gives the triangle t16 (vertices in 1/16 pixel)."""
    t = [(x / 16, y / 16) for x, y in t16]
    out = {}
    for row in range((height + 15) // 16):
        for col in range((width + 31) // 32):
            k = region_tiles.tiles(t, col * 32, row * 16)
            if any(k):
                out[(col, row)] = k
    return out


def seen_regions(param: bytes, tadata: bytes) -> dict:
    """{(column, row): the first stream word's PRIM_TILES} of a dump's regions with a stream."""
    out = {}
    for r in pbdump.regions(tadata):
        if r.stream:
            out[(r.col // 2, (r.row & 0xfff) // 2)] = \
                pbdump.prim_word(pbdump.stream(param, r.stream)[0])["PRIM_TILES"]
    return out


def region_check(want: dict, seen: dict) -> dict:
    """The regions the test predicts against those streamed: missing, extra, and the streamed
    ones whose PRIM_TILES is not a form of the predicted tile pair (region_tiles.TILE_FORMS)."""
    return {"regions": len(want),
            "missing": sorted(set(want) - set(seen)),
            "extra": sorted(set(seen) - set(want)),
            "form": sorted(k for k in set(want) & set(seen)
                           if seen[k] not in region_tiles.TILE_FORMS.get(want[k], ()))}


def random_report(d: pathlib.Path, probe: str, seed: int = SEED, n: int = RANDOM_COUNT,
                  size: int = RANDOM_SIZE) -> str:
    lines, tot = [], collections.Counter()
    for k, t in enumerate(random_triangles(seed, n, size)):
        stem = d / f"{probe}__{k}"
        if not pathlib.Path(f"{stem}.param.bin").exists():
            lines.append(f"{k}: no dump")
            continue
        seen = seen_regions(pathlib.Path(f"{stem}.param.bin").read_bytes(),
                            pathlib.Path(f"{stem}.tadata.bin").read_bytes())
        r = region_check(predicted_regions(t, size, size), seen)
        tot["regions"] += r["regions"]
        tot["seen"] += len(seen)
        for key in ("missing", "extra", "form"):
            tot[key] += len(r[key])
        lines.append(f"{k}: {t} predicted {r['regions']} streamed {len(seen)} missing "
                     f"{r['missing']} extra {r['extra']} form {r['form']}")
    lines.append(f"total: predicted {tot['regions']}, streamed {tot['seen']}, missing "
                 f"{tot['missing']}, extra {tot['extra']}, wrong form {tot['form']}")
    return "\n".join(lines) + "\n"


# ---- readers of the 11.8 scripts' output ----

CASE = re.compile(r"^== (\S+?):(?: |$)")
ROW = re.compile(r"^row (\d+): (.*)$")
HEXWORD = re.compile(r"(?<![\w])(?:0x)?([0-9a-f]{8})(?![\w])")


def _cases(out: str) -> dict[str, list[str]]:
    cases, cur = {}, None
    for line in out.splitlines():
        if m := CASE.match(line):
            cur = m[1]
            cases[cur] = []
        elif cur is not None:
            cases[cur].append(line)
    return cases


def case_pixels(out: str) -> dict[str, list[list[int]]]:
    """{case: rows of pixels} from a script's --pixels output. A row keeps its hex words
    only: a line the tool's error message cut into keeps the words around the message."""
    res = {}
    for name, lines in _cases(out).items():
        rows = {int(m[1]): [int(x, 16) for x in HEXWORD.findall(m[2])]
                for line in lines if (m := ROW.match(line))}
        if rows:
            res[name] = [rows[y] for y in sorted(rows)]
    return res


def agreeing(a: list[list[int]], b: list[list[int]]) -> list[tuple[int, int]]:
    """(x, y) of the pixels two images share."""
    return [(x, y) for y, (ra, rb) in enumerate(zip(a, b))
            for x, (p, q) in enumerate(zip(ra, rb)) if p == q]


def case_states(out: str) -> dict[str, dict]:
    """{case: {"ta3dctl": dwords, "cleanup": lines, "lines": the rest}} of a script's output."""
    res = {}
    for name, lines in _cases(out).items():
        s = {"ta3dctl": [], "cleanup": [], "lines": []}
        for line in lines:
            if line.startswith("ta3dctl:"):
                s["ta3dctl"] = [int(x, 16) for x in line.split()[1:]]
            elif line.startswith("cleanup: "):
                s["cleanup"].append(line[len("cleanup: "):])
            else:
                s["lines"].append(line)
        res[name] = s
    return res


# ---- the 11.8 tables ----

GREEN = isp_words.GREEN
OP_PIX = ["mov.skipinv.end o0, o0"]
PDS_SIZE_JOB = 0x00030001        # the triangle's state block word 4 (PDS size, one row)


def _probe(name, question, cases, labels, **kw) -> dict:
    return isp_words._probe(name, question, cases, labels, **kw)


def _sets(sets):
    return isp_words._sets(sets)


def _green(n: int) -> list[list[str]]:
    return [isp_words._pix() for _ in range(n)]


def state1_split_probes() -> list[dict]:
    """Q015: the sweep's word on the probe's triangle with its own colour, with o0 copied and
    no readback, and as the original probe."""
    word = 0x0a022e05
    ps = [
        _probe("vdm-state1-split-green", "VDM state word 1 bits 11:9 = 7 on the probe's "
               "triangle with a shader writing its colour, pixels read, render dumped",
               _green(1), ["green"], vdm={"1": word}, dump_render=True),
        _probe("vdm-state1-split-op-plain", "the same with o0 copied (the original probe's "
               "shader), no pixel readback, no render dump", [OP_PIX], ["o0 = o0"],
               vdm={"1": word}),
        _probe("vdm-state1-split-op", "the original probe: o0 copied, pixels read, render "
               "dumped", [OP_PIX], ["o0 = o0"], vdm={"1": word}, dump_render=True),
    ]
    ps[1]["pixels"] = False
    return ps


TRAILING_VALUES = [0xf0000000, 0, 1, 2, 3, 5, 0xff, 0x0f000000, 0x80000000]


def index2_probes() -> list[dict]:
    """Q042: the index list's first trailing word over the five-copy job, dumped."""
    out = []
    for run in ("", "-r2"):
        out.append(_probe(
            f"vdm-index2-copies{run}", "the five-copy job with VDM_INDEX2 at small values, "
            "single fields and the job's own 0xf0000000", _green(len(TRAILING_VALUES)),
            [f"VDM_INDEX2 0x{v:08x}" for v in TRAILING_VALUES], vertices=15, dump_render=True,
            case_set=_sets([{"vdm": {4: v}} for v in TRAILING_VALUES])))
    return out


def reg0148_probes() -> list[dict]:
    """Q043: render details dword 9 over five copies."""
    vals = [0, 0xffffffff, 0x0000ffff, 0xffff0000]
    return [_probe("render-reg-0148-copies", "render details dword 9 (CR_REG_0148) over the "
                   "five-copy job", _green(len(vals)), [f"rd:9 0x{v:08x}" for v in vals],
                   vertices=15, case_set=_sets([{"kpoke": [f"rd:9=0x{v:x}"]} for v in vals]))]


PDS_WORDS = [{4: PDS_SIZE_JOB}, {4: 0x00030002}, {4: 0x00020001}, {4: 0x00010001},
             {4: 0x00000001}, {3: 0x08000004}, {5: 0x08000000}]


def object_probes() -> list[dict]:
    """Q070: the object's header words over the state block's PDS words; the region test on
    fresh random triangles."""
    out = [_probe("ta-object-words-pds", "the TA object's three header words against the state "
                  "block's pixel PDS words (3 secondary, 4 size, 5 primary) varied one at a time",
                  _green(len(PDS_WORDS)),
                  [", ".join(f"blk:{k} 0x{v:08x}" for k, v in w.items()) for w in PDS_WORDS],
                  dump_render=True, case_set=_sets([{"blk": w} for w in PDS_WORDS]))]
    cases, labels = [], []
    for t in random_triangles(SEED, RANDOM_COUNT, RANDOM_SIZE):
        a = isp_words.affine_params(t, RANDOM_SIZE, RANDOM_SIZE)
        cases.append([f"0x{f32(v):08X}" for v in a])
        labels.append(" ".join(f"({x / 16:g}, {y / 16:g})" for x, y in t))
    out.append(_probe("ta-object-words-random", f"the regions a fresh random triangle on "
                      f"{RANDOM_SIZE}x{RANDOM_SIZE} is binned into (seed {SEED})", cases, labels,
                      source="vtx_affine.s", slot="vtxuse", slots={"pixel": "pix_green.s"},
                      temps=8, size=[RANDOM_SIZE, RANDOM_SIZE], dump_render=True,
                      inputs=["A", "B", "C", "D", "E", "F"]))
    return out


SCRIPTS = {
    "vdm/state1-split": ("state1-split.sh", "Q015: the sweep's bits 11:9 = 7 split three ways",
                         ["render", "render_param", "render_tadata"], state1_split_probes),
    "vdm/index2": (None, "Q042: VDM_INDEX2 over the five-copy job",
                   ["render", "render_param", "render_tadata"], index2_probes),
    "render/bg-pds-word": ("bg-pds-word.sh", "Q014: render command word 23, the background "
                           "object's first PDS word", ["render", "kpoke"], None),
    "render/reg-0148": ("reg-0148.sh", "Q043: render details dword 9 bit by bit",
                        ["render", "kpoke"], reg0148_probes),
    "render/frag-flags": ("frag-flags.sh", "Q041, Q065: the TA/3D control block after render "
                          "flags and render counts", ["render", "kpoke", "buf09",
                                                      "render_cleanup"], None),
    "render/rtds-words": ("rtds-words.sh", "the RT data set words of the TA command and the "
                          "render details", ["render", "kpoke", "render_cleanup"], None),
    "ta/te-psg": ("te-psg.sh", "Q064: CR_TE_PSG and CR_DPM_STATE_CONTEXT_ID",
                  ["render", "kpoke", "render_param", "render_tadata"], None),
    "ta/object-words": (None, "Q070: the object's header words and the region test",
                        ["render", "render_param", "render_tadata"], object_probes),
}


def tables() -> dict[str, str]:
    out = {}
    for path, (script, about, needs, gen) in SCRIPTS.items():
        unit, feature = path.split("/")
        ps = gen() if gen else []
        head = {"name": f"{unit}-{feature}"}
        if script:
            head["script"] = script
        text = isp_words.table_text(unit, feature.replace("-", " "), about, ps, needs=needs,
                                    head=head)
        out[path] = text.replace("(written by tools/usse-asm/isp_words.py)",
                                 "(written by tools/usse-asm/ta_words.py)")
    return out


def main(argv: list[str] | None = None) -> int:
    a = sys.argv[1:] if argv is None else argv
    if a[:1] == ["tables"] and len(a) == 2:
        for path, text in tables().items():
            f = pathlib.Path(a[1]) / "probes" / f"{path}.toml"
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(text)
        return 0
    if a[:1] == ["vdm"] and len(a) > 1:
        print(vdm_text([int(x, 0) for x in a[1:]]), end="")
        return 0
    if a[:1] == ["object"] and len(a) == 3:
        d = pathlib.Path(a[1])
        o = first_object((d / f"{a[2]}.param.bin").read_bytes(),
                         (d / f"{a[2]}.tadata.bin").read_bytes())
        print("\n".join(pbdump.object_lines(o)) if o else "no object")
        return 0
    if a[:1] == ["regions"] and len(a) == 3:
        print(random_report(pathlib.Path(a[1]), a[2]), end="")
        return 0
    if a[:1] == ["pixels"] and len(a) == 4:
        px = case_pixels(pathlib.Path(a[1]).read_text())
        same = agreeing(px[a[2]], px[a[3]])
        print(f"{len(same)} pixels agree: {same}")
        return 0
    if a[:1] == ["states"] and len(a) == 2:
        for name, s in case_states(pathlib.Path(a[1]).read_text()).items():
            w = s["ta3dctl"]
            print(f"{name}: " + " ".join(s["lines"]))
            if w:
                print("  " + " ".join(f"{i}:{w[i]:08x}" for i in range(len(w)) if w[i]))
            for c in s["cleanup"]:
                print(f"  {c}")
        return 0
    print(__doc__.strip(), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
