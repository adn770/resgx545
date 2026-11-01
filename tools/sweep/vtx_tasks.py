#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Read a vtx_task.s run (probes vdm-vertex-tasks-vtxtask-*, the sweep log's E189): the
quads the vertex tasks formed, as vertex indices of the 42 copies' 126 vertices.

    vtx_tasks.py RAW [PROBE]    each quad on a line, '-' for an empty instance
"""
from __future__ import annotations

import re
import struct
import sys

SENTINEL = 0x3F800000
W = 64
CORNERS = [(8, 8), (56, 20), (20, 56)]     # sgxfive_tri_default's, in 1/16 pixel x 16


def _f32(v: float) -> int:
    return struct.unpack("<I", struct.pack("<f", v))[0]


def vertex_x(n: int = 126, width: int = W) -> dict[int, int]:
    """{x bits: vertex index} of put_copies' vertices (copy d = i / 3 moved d/16 pixel)."""
    return {_f32((CORNERS[i % 3][0] * 16 + i // 3) / (8 * width) - 1): i for i in range(n)}


def slots(text: str, probe: str | None = None) -> dict[int, list[int]]:
    """{scratch byte offset of a 16-byte slot: its four dwords} from a probe run's raw.txt."""
    d: dict[int, int] = {}
    for m in re.finditer(r"probe (\S+): scratch \+0x([0-9a-f]+) 0x([0-9a-f]+)", text):
        if probe is None or m[1].startswith(probe + "__"):
            d[int(m[2], 16)] = int(m[3], 16)
    return {o: [d.get(o + 4 * k, 0) for k in range(4)] for o in sorted(d) if o % 16 == 0}


def quads(text: str, probe: str | None = None) -> list[tuple]:
    """The quads, each the sorted vertex indices of its valid instances (None for a value
    that is no vertex's x), in order of their first vertex."""
    vx = vertex_x()
    out = set()
    for w in slots(text, probe).values():
        q = [vx.get(v) for v in w if v != SENTINEL]
        out.add(tuple(sorted(q, key=lambda v: (v is None, v))))
    return sorted(out, key=lambda q: (q[0] is None, q[0] or 0))


def main(argv: list[str] | None = None) -> int:
    a = sys.argv[1:] if argv is None else argv
    if not a:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    text = open(a[0]).read()
    for q in quads(text, a[1] if len(a) > 1 else None):
        print(" ".join("?" if v is None else str(v) for v in q) + " -" * (4 - len(q)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
