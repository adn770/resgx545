#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Read the render dumps of dump_render probes (probe.py; the kernel's debugfs render_param
and render_tadata): NAME.param.bin is the render context's parameter slot from its PB on
(slot offset 0x1000), NAME.tadata.bin its TA data. Prints the pages the GPU wrote, the TA's
object at the start of the PB, the region headers and each region's control stream, the words
also by the glossary's fields (PB_OBJ, REGION_HDR, CSTREAM).

    pbdump.py DIR [NAME...]     every NAME.param.bin in DIR by default
    pbdump.py --map DIR NAME    the regions as a grid of their streams' primitive-word forms
    pbdump.py --diff A B        the dwords that differ between two dumps (PREFIX.param.bin and
                                PREFIX.tadata.bin each), by slot offset
"""
from __future__ import annotations

import dataclasses
import pathlib
import struct
import sys

PAGE = 4096
PB_BASE = 0x1000         # the parameter slot offset of the dump's first byte
FILLER = 0xc0000000      # what a region's stream block holds after its words
HEADERS = PAGE // 12     # region headers a TA data page holds


# REGION_HDR.FLAGS, region header word 0 [31:24]: the bits the glossary row names, by bit of
# the word
REGION_FLAG_BITS = {25: "outside the target", 26: "first of a macrotile", 27: "empty",
                    28: "last of a macrotile", 31: "last of the scene"}


@dataclasses.dataclass(frozen=True)
class Region:
    """A region header (REGION_HDR): three dwords, the first two read."""
    index: int
    col: int             # REGION_HDR.POS, word 0 [23:16]: 2 per 32-pixel column
    row: int             # REGION_HDR.POS, word 0 [15:0]: 2 per 16-pixel row; 15:12 the macrotile
    flags: int           # REGION_HDR.FLAGS, word 0 [31:24]
    stream: int          # REGION_HDR.STREAM, word 1: the stream block, relative to the
    #                      parameter slot; 0 for an empty region


def region_flags(flags: int) -> list[str]:
    """REGION_HDR.FLAGS (word 0 [31:24]) by its named bits; the others as one hex value."""
    out, rest = [], flags
    for bit, name in REGION_FLAG_BITS.items():
        if flags >> (bit - 24) & 1:
            out.append(name)
            rest &= ~(1 << (bit - 24))
    return out + ([f"{rest:#04x}"] if rest else [])


def prim_word(w: int) -> dict[str, int]:
    """A control-stream primitive word by the glossary's CSTREAM fields."""
    return {"PRIM_TILES": (w >> 16) & 0xff, "PRIM_VERTICES": (w >> 25) & 0xf,
            "PRIM_POINTS": (w >> 29) & 1}


def obj_word(w: int) -> dict[str, int]:
    """A control-stream object word by the glossary's CSTREAM fields."""
    return {"OBJ_PRIMS": w >> 26, "OBJ_ISP_ADDR": w & 0x3ffffff}


# CSTREAM.PRIM_TILES forms whose masks do not fit the primitive word: the object's block holds
# one more dword after the object word, the mask (E177, E180; the glossary's PRIM_TILES row)
WIDE_MASK_TILES = (0x8a, 0x8c)


def objects(words: list[int]) -> list[tuple[dict, dict | None, int | None]]:
    """A region's stream as (primitive word, object word, mask dword) per object: 2 dwords, or
    3 when PRIM_TILES is a wide-mask form (the mask after the object word); None for a dword
    the stream does not hold or a block with no mask."""
    out, i = [], 0
    while i < len(words):
        prim = prim_word(words[i])
        wide = prim["PRIM_TILES"] in WIDE_MASK_TILES
        ob = obj_word(words[i + 1]) if i + 1 < len(words) else None
        mask = words[i + 2] if wide and i + 2 < len(words) else None
        out.append((prim, ob, mask))
        i += 3 if wide else 2
    return out


def _fields(d: dict | None) -> str:
    return " ".join(f"{k} {v:#x}" if k in ("PRIM_TILES", "OBJ_ISP_ADDR") else f"{k} {v}"
                    for k, v in (d or {}).items())


def _words(buf: bytes, start: int, n: int) -> list[int]:
    return list(struct.unpack(f"<{n}I", buf[start:start + 4 * n]))


def written(buf: bytes) -> list[int]:
    """The indices of the pages with a non-zero byte."""
    return [i for i in range(len(buf) // PAGE) if any(buf[i * PAGE:(i + 1) * PAGE])]


def obj(param: bytes) -> list[int]:
    """The first PB page's dwords up to its last non-zero one: the TA's first object."""
    ws = _words(param, 0, PAGE // 4)
    last = max((i for i, w in enumerate(ws) if w), default=-1)
    return ws[:last + 1]


def regions(tadata: bytes) -> list[Region]:
    """The region headers on the first written TA data page, three dwords each: every
    non-zero one (the list's length follows the target's macrotiles)."""
    pages = written(tadata)
    if not pages:
        return []
    ws = _words(tadata, pages[0] * PAGE, 3 * HEADERS)
    return [Region(i, (ws[3 * i] >> 16) & 0xff, ws[3 * i] & 0xffff, ws[3 * i] >> 24,
                   ws[3 * i + 1]) for i in range(HEADERS) if ws[3 * i] or ws[3 * i + 1]]


def stream(param: bytes, addr: int) -> list[int]:
    """A region's stream block at slot offset addr: its words up to the filler."""
    out = []
    for w in _words(param, addr - PB_BASE, 32):
        if w == FILLER:
            break
        out.append(w)
    while out and not out[-1]:
        out.pop()
    return out


def form_map(param: bytes, tadata: bytes) -> str:
    """The regions as a grid (rows of 16 pixels, columns of 32, macrotiles placed by their
    rows): each cell the top half of its stream's first word, '+' when more objects follow,
    '....' for a region without a stream."""
    cells = {}
    for r in regions(tadata):
        cell = "...."
        if r.stream:
            w = stream(param, r.stream)
            cell = f"{w[0] >> 16:04x}" + ("+" if len(objects(w)) > 1 else "")
        cells[((r.row & 0xfff) // 2, r.col // 2)] = cell
    if not cells:
        return ""
    rows = max(k[0] for k in cells) + 1
    cols = max(k[1] for k in cells) + 1
    return "\n".join("  ".join(cells.get((y, x), "    ").ljust(5) for x in range(cols)).rstrip()
                     for y in range(rows)) + "\n"


def diff_words(a: bytes, b: bytes, base: int = 0) -> list[tuple[int, int, int]]:
    """[(offset + base, a's dword, b's dword)] where two dumps differ (the shorter padded)."""
    n = max(len(a), len(b)) // 4
    a, b = a.ljust(4 * n, b"\0"), b.ljust(4 * n, b"\0")
    wa, wb = struct.unpack(f"<{n}I", a), struct.unpack(f"<{n}I", b)
    return [(base + 4 * i, x, y) for i, (x, y) in enumerate(zip(wa, wb)) if x != y]


def report(d: pathlib.Path, name: str) -> str:
    param = (d / f"{name}.param.bin").read_bytes()
    tadata = (d / f"{name}.tadata.bin").read_bytes()
    lines = [f"== {name}: PB pages " +
             " ".join(f"{PB_BASE + PAGE * i:#x}" for i in written(param)) +
             ", TA data pages " + " ".join(str(i) for i in written(tadata))]
    o = obj(param)
    lines.append(f"object ({len(o)} dwords): " + " ".join(f"{w:08x}" for w in o))
    lines.append("  PB_OBJ.PDS_WORDS " + " ".join(f"{w:08x}" for w in o[:3]))
    rs = regions(tadata)
    for r in rs:
        if r.stream:
            words = stream(param, r.stream)
            lines.append(f"region {r.index} col {r.col} row {r.row:#x} flags {r.flags:#04x} "
                         f"-> {r.stream:#x}: " + " ".join(f"{w:08x}" for w in words))
            lines.append("  REGION_HDR.FLAGS " + (", ".join(region_flags(r.flags)) or "0x00"))
            lines += [f"  CSTREAM {_fields(p)}" + (f", {_fields(ob)}" if ob else "")
                      + (f", mask {m:#x}" if m is not None else "")
                      for p, ob, m in objects(words)]
    lines.append(f"{sum(not r.stream for r in rs)} empty regions")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    if argv[0] == "--map" and len(argv) == 3:
        d = pathlib.Path(argv[1])
        print(form_map((d / f"{argv[2]}.param.bin").read_bytes(),
                       (d / f"{argv[2]}.tadata.bin").read_bytes()), end="")
        return 0
    if argv[0] == "--diff" and len(argv) == 3:
        for kind, base in (("param", PB_BASE), ("tadata", 0)):
            ds = diff_words(pathlib.Path(f"{argv[1]}.{kind}.bin").read_bytes(),
                            pathlib.Path(f"{argv[2]}.{kind}.bin").read_bytes(), base)
            print(f"{kind}: {len(ds)} dwords differ")
            for off, x, y in ds[:64]:
                print(f"  {off:#08x}: {x:08x} -> {y:08x}")
        return 0
    d = pathlib.Path(argv[0])
    names = argv[1:] or sorted(p.name[:-len(".param.bin")] for p in d.glob("*.param.bin"))
    for n in names:
        print(report(d, n), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
