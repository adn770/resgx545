# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""pixels.py: reading tri probes' recorded pixels (raw.txt rows)."""
from __future__ import annotations

import struct

import pixels

BG = pixels.BG


def raw(cases: dict) -> str:
    """raw.txt text: cases {name: [row, ...]}, each row a list of dwords."""
    out = []
    for name, rows in cases.items():
        out += [f"probe {name}: row {r}: " + " ".join(f"0x{v:08x}" for v in row)
                for r, row in enumerate(rows)]
    return "\n".join(out) + "\nprobe x__9: failed: job hung\n"


def f32(x: float) -> int:
    return struct.unpack("<I", struct.pack("<f", x))[0]


def test_parse_rows_and_failures():
    img, fail = pixels.parse(raw({"p__0": [[1, 2], [3, BG]]}))
    assert img == {"p__0": [1, 2, 3, BG]} and fail == {"x__9": "job hung"}


def test_summary_counts_drawn_pixels_and_values():
    text = pixels.summary(raw({"p__0": [[1, 1, BG], [2, BG, BG]]}))
    assert "p__0: 3 px, 2 values: 00000001x2 00000002x1" in text
    assert "x__9: FAILED job hung" in text


def test_map_letters_per_value():
    text = pixels.ascii_map(raw({"p__0": [[5, 6], [BG, 5]]}), "p__0", step=1)
    assert text.splitlines()[:2] == ["AB", ".A"] and "A=00000005" in text


def test_same_compares_case_by_case():
    a = raw({"a__0": [[1, 2]], "a__1": [[3, 4]]})
    b = raw({"b__0": [[1, 2]], "b__1": [[3, 5]]})
    assert pixels.same(a, "a", b, "b") == {0: True, 1: False}


def test_table_cells():
    """One value per case: the value as a float (with how many values when mixed), 'varN'
    when more than 20 values, 'FAIL' for a failure."""
    many = [[f32(i / 100) for i in range(30)]]
    text = pixels.table(raw({"q-1-pa0__0": [[f32(0.25), f32(0.25)]], "q-1-pa0__1": many,
                             "q-1-pa0__2": [[f32(1.0), f32(0.5)]]}), "q-1-pa0", 3, floats=True)
    assert text.split() == ["q-1-pa0", "0.25", "var30", "1(2)"]


def test_perspective_fit_tells_affine_from_perspective():
    """persp: pa0 iterated affinely or perspective-correct from three vertex values, with
    w = x + 2 at the vertices: the right model fits every pixel."""
    v = [(-0.75, -0.75), (0.75, -0.375), (-0.375, 0.75)]
    w = [x + 2 for x, _ in v]
    vals = [x for x, _ in v]
    rows = []
    for r in range(64):
        row = []
        for c in range(64):
            x, y = (c + 0.5) / 32 - 1, (r + 0.5) / 32 - 1
            lam = pixels.bary(x, y)
            if min(lam) < 0:
                row.append(BG)
                continue
            q = [l / wi for l, wi in zip(lam, w)]
            row.append(f32(sum(a * b for a, b in zip(q, vals)) / sum(q)))
        rows.append(row)
    text = pixels.persp(raw({"p__0": rows}), w)
    line = next(l for l in text.splitlines() if l.startswith("p__0"))
    assert "persp v=(-0.7500,0.7500,-0.3750)" in line
    persp_fit = int(line.split("persp")[1].split("fit ")[1].split()[0])
    affine_fit = int(line.split("affine")[1].split("fit ")[1].split()[0])
    assert persp_fit > 0.95 * int(line.split()[1]) > affine_fit
