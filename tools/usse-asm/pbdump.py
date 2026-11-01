#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Read the render dumps of dump_render probes (probe.py; the kernel's debugfs render_param
and render_tadata): NAME.param.bin is the render context's parameter slot from its PB on
(slot offset 0x1000), NAME.tadata.bin its TA data. Prints the pages the GPU wrote, the TA's
object at the start of the PB, the region headers and each region's control stream.

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


@dataclasses.dataclass(frozen=True)
class Region:
    index: int
    col: int             # word 0 [23:16]: 2 per 32-pixel column
    row: int             # word 0 [15:0]: 2 per 16-pixel row; 15:12 the macrotile
    flags: int           # word 0 [31:24]
    stream: int          # word 1: the stream block, relative to the parameter slot; 0 empty


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
            cell = f"{w[0] >> 16:04x}" + ("+" if len(w) > 2 else "")
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
    rs = regions(tadata)
    for r in rs:
        if r.stream:
            lines.append(f"region {r.index} col {r.col} row {r.row:#x} flags {r.flags:#04x} "
                         f"-> {r.stream:#x}: " +
                         " ".join(f"{w:08x}" for w in stream(param, r.stream)))
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
