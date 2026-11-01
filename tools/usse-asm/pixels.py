#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Read the pixels tri probes record (raw.txt, "probe CASE: row R: ..." lines, pixels = true).

    pixels.py summary RAW...              per case: drawn pixels, values, the commonest three
    pixels.py map RAW CASE                every other row and column, a letter per value
    pixels.py same RAW_A PROBE_A RAW_B PROBE_B   case by case, bit for bit
    pixels.py table RAW PROBE... [--cases N] [--floats]   one cell per probe and case
    pixels.py persp RAW [W0 W1 W2]        pa0 fitted as an affine and a perspective-correct
                                          iteration of three vertex values (w = x + 2 default)

The triangle's vertices are (-0.75, -0.75), (0.75, -0.375), (-0.375, 0.75) in clip space and
its background 0xff203040 (sgxfive_tri_default).
"""
from __future__ import annotations

import collections
import re
import struct
import sys

BG = 0xff203040
V = [(-0.75, -0.75), (0.75, -0.375), (-0.375, 0.75)]
LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def parse(text: str) -> tuple[dict, dict]:
    """{case: pixels row by row}, {case: why it failed}."""
    img: dict = {}
    fail = {}
    for line in text.splitlines():
        m = re.match(r"probe (\S+): row (\d+): (.*)", line)
        if m:
            img.setdefault(m[1], []).extend(int(v, 16) for v in m[3].split())
            continue
        m = re.match(r"probe (\S+): failed: (.*)", line)
        if m:
            fail[m[1]] = m[2]
    return img, fail


def _rows(text: str, case: str) -> dict:
    rows = {}
    for line in text.splitlines():
        m = re.match(r"probe (\S+): row (\d+): (.*)", line)
        if m and m[1] == case:
            rows[int(m[2])] = [int(v, 16) for v in m[3].split()]
    return rows


def summary(text: str) -> str:
    img, fail = parse(text)
    out = []
    for case in sorted(set(img) | set(fail)):
        if case in fail:
            out.append(f"{case}: FAILED {fail[case]}")
            continue
        c = collections.Counter(v for v in img[case] if v != BG)
        top = " ".join(f"{v:08x}x{n}" for v, n in c.most_common(3))
        out.append(f"{case}: {sum(c.values())} px, {len(c)} values: {top}")
    return "\n".join(out) + "\n"


def ascii_map(text: str, case: str, step: int = 2) -> str:
    rows = _rows(text, case)
    keys: dict = {}
    out = []
    for r in sorted(rows)[::step]:
        line = ""
        for v in rows[r][::step]:
            if v == BG:
                line += "."
                continue
            keys.setdefault(v, LETTERS[len(keys) % 26])
            line += keys[v] if len(keys) <= 26 else "*"
        out.append(line)
    out.append(" ".join(f"{k}={v:08x}" for v, k in list(keys.items())[:8]))
    return "\n".join(out) + "\n"


def _by_index(text: str, probe: str) -> dict:
    img, _ = parse(text)
    out = {}
    for case, px in img.items():
        m = re.fullmatch(re.escape(probe) + r"__(\d+)", case)
        if m:
            out[int(m[1])] = px
    return out


def same(text_a: str, probe_a: str, text_b: str, probe_b: str) -> dict:
    """{case index: whether both probes' images of it are equal}, for the cases A has."""
    a, b = _by_index(text_a, probe_a), _by_index(text_b, probe_b)
    return {i: a[i] == b.get(i) for i in sorted(a)}


def _f32(u: int) -> float:
    return struct.unpack("<f", struct.pack("<I", u))[0]


def table(text: str, probes: list | str, cases: int, floats: bool = False) -> str:
    img, fail = parse(text)
    out = []
    for p in [probes] if isinstance(probes, str) else probes:
        cells = []
        for i in range(cases):
            k = f"{p}__{i}"
            if k in fail:
                cells.append("FAIL")
                continue
            c = collections.Counter(v for v in img.get(k, []) if v != BG)
            if not c:
                cells.append("none")
                continue
            v, n = c.most_common(1)[0]
            if len(c) > 20:
                cells.append(f"var{len(c)}")
                continue
            s = f"{_f32(v):g}" if floats else f"{v:08x}"
            cells.append(s + ("" if n == sum(c.values()) else f"({len(c)})"))
        out.append(" ".join([p] + cells))
    return "\n".join(out) + "\n"


def _solve3(a, b):
    """Gaussian elimination of a 3x3 system."""
    m = [list(r) + [x] for r, x in zip(a, b)]
    for i in range(3):
        k = max(range(i, 3), key=lambda j: abs(m[j][i]))
        m[i], m[k] = m[k], m[i]
        for j in range(3):
            if j != i:
                f = m[j][i] / m[i][i]
                m[j] = [x - f * y for x, y in zip(m[j], m[i])]
    return [m[i][3] / m[i][i] for i in range(3)]


def bary(px: float, py: float) -> list[float]:
    """The barycentric coordinates of a clip-space point in the triangle."""
    t = [[V[0][0], V[1][0], V[2][0]], [V[0][1], V[1][1], V[2][1]], [1, 1, 1]]
    return _solve3(t, [px, py, 1.0])


def _lstsq(a, b):
    ata = [[sum(r[i] * r[j] for r in a) for j in range(3)] for i in range(3)]
    atb = [sum(r[i] * x for r, x in zip(a, b)) for i in range(3)]
    return _solve3(ata, atb)


def persp(text: str, w: list[float] | None = None) -> str:
    """Per case: the vertex values that fit pa0 best, affine and perspective-correct with
    the vertices' w, and how many pixels each fits to 1e-4. The image may be flipped in y."""
    w = w or [x + 2 for x, _ in V]
    img, _ = parse(text)
    out = []
    for case in sorted(img):
        rows = _rows(text, case)
        pts: list = []
        for flip in (False, True):
            pts = [((c + 0.5) / 32 - 1, ((-1 if flip else 1) * ((r + 0.5) / 32 - 1)), u)
                   for r, vals in rows.items() for c, u in enumerate(vals) if u != BG]
            if not pts or sum(min(bary(x, y)) > -0.02 for x, y, _ in pts) > 0.95 * len(pts):
                break
        keep = [(bary(x, y), _f32(u)) for x, y, u in pts if abs(_f32(u)) < 1e6]
        line = [f"{case}: {len(pts)} px, {len(keep)} finite"]
        if len(keep) >= 3:
            lam = [k[0] for k in keep]
            val = [k[1] for k in keep]
            q = [[l / wi for l, wi in zip(r, w)] for r in lam]
            for name, a in (("affine", lam), ("persp", [[x / sum(r) for x in r] for r in q])):
                v = _lstsq(a, val)
                err = [abs(sum(x * y for x, y in zip(r, v)) - t) for r, t in zip(a, val)]
                line.append(f"{name} v=({v[0]:.4f},{v[1]:.4f},{v[2]:.4f}) max {max(err):.2g} "
                            f"fit {sum(e < 1e-4 for e in err)}")
        out.append("  ".join(line))
    return "\n".join(out) + "\n"


def main(argv: list[str] | None = None) -> int:
    a = sys.argv[1:] if argv is None else argv
    if not a:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    read = lambda p: open(p).read()  # noqa: E731
    if a[0] == "summary":
        for p in a[1:]:
            print(summary(read(p)), end="")
    elif a[0] == "map":
        print(ascii_map(read(a[1]), a[2]), end="")
    elif a[0] == "same":
        for i, ok in same(read(a[1]), a[2], read(a[3]), a[4]).items():
            print(f"case {i}: {'same' if ok else 'DIFFERS'}")
    elif a[0] == "table":
        floats = "--floats" in a
        rest = [x for x in a[2:] if x != "--floats"]
        n = 4
        if "--cases" in rest:
            k = rest.index("--cases")
            n = int(rest[k + 1])
            del rest[k:k + 2]
        print(table(read(a[1]), rest, n, floats), end="")
    elif a[0] == "persp":
        print(persp(read(a[1]), [float(x) for x in a[2:5]] if len(a) > 4 else None), end="")
    else:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
