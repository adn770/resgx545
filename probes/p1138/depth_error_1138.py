#!/usr/bin/env python3
"""depth_error_1138.py: the depth-error figures of record E606, from the stored main-set dumps of the
11.37 arithmetic sweep (data repository, isp/arith-1138/main), with the standard library only.

Usage: RESGX545_DATA=~/src/resgx545-data depth_error_1138.py [DIR]   (DIR: the dataset directory)

For every covered pixel of the fit and held-out depth jobs (colour not the background) the stored
depth dword is read through the E465 layout and compared with the exact plane (rational arithmetic)
through the case's vertices at the pixel centre.  The vertices of the main set are integers in 1/256
pixel and the vertex depths multiples of 1/1024, so the plane is exact.  Units:

  U  = 2^-23 absolute (the spacing of float32 in [1, 2)), the unit of the tolerance of E606;
  true ulp = the spacing of float32 at the stored value (2^-24 for a stored value in [0.5, 1)).

The output is deterministic text; probes/p1138/depth-error-1138.txt holds the one of the landed run."""
import gzip
import math
import os
import struct
import sys
from fractions import Fraction

BG = 0xff203040
U = Fraction(1, 1 << 23)


def f32_bits(x):
    return struct.unpack("<I", struct.pack("<f", x))[0]


def bits_f32(b):
    return struct.unpack("<f", struct.pack("<I", b))[0]


def true_ulp(v):
    """the spacing of float32 at the positive value v (a Fraction of a float32)"""
    if v == 0:
        return Fraction(1, 1 << 149)
    e = max(math.floor(math.log2(float(v))), -126)
    return Fraction(2) ** (e - 23)


def f32_round_nearest(x):
    """x (Fraction, positive) rounded to the nearest float32 (ties to even), decided exactly: the
    candidates are the neighbours of the double rounding"""
    c = f32_bits(float(x))
    best = None
    for b in (c - 1, c, c + 1):
        if b < 0:
            continue
        d = abs(Fraction(bits_f32(b)) - x)
        key = (d, b & 1)
        if best is None or key < best[0]:
            best = (key, b)
    return best[1]


def f32_truncate(x):
    """x (Fraction, positive) rounded toward zero to a float32: the dword"""
    b = f32_round_nearest(x)
    if Fraction(bits_f32(b)) > x:
        b -= 1
    return b


def depth_index(x, y, g):
    """the dword of the depth buffer that holds pixel (x, y), the E465 rule, pitch g + 1 tiles"""
    low = 0
    for k, (v, bit) in enumerate([(y, 0), (x, 0), (y, 1), (x, 1), (y, 2), (x, 2), (y, 3), (x, 3)]):
        low |= ((v >> bit) & 1) << k
    low |= ((x >> 4) & 1) << 8
    return 512 * ((y // 16) * (g + 1) + x // 32) + low


def read_gz(path):
    with gzip.open(path, "rb") as fh:
        return fh.read()


def covered_pixels(text, w, h):
    """the (x, y) of the pixels of the 'row N:' lines that are not the background"""
    out = []
    seen = 0
    for line in text.splitlines():
        i = line.find("row ")
        if i < 0:
            continue
        head, _, rest = line[i + 4:].partition(":")
        if not head.strip().isdigit():
            continue
        y = int(head)
        vals = [int(t, 16) for t in rest.split()]
        if y < h and len(vals) == w:
            seen += 1
            out.extend((x, y) for x, v in enumerate(vals) if v != BG)
    return out if seen == h else None


def load_cases(path):
    cases = []
    for line in open(path):
        f = line.rstrip("\n").split("\t")
        if len(f) < 16:
            continue
        cases.append(dict(id=int(f[0]), set=f[1], cls=f[2], w=int(f[3]), h=int(f[4]),
                          v=[int(t) for t in f[5:11]],
                          z=[round(float(t) * 1024) for t in f[11:14]]))
    return cases


def good_jobs(path):
    ok = {}
    for line in open(path):
        f = line.rstrip("\n").split("\t")
        ok[(int(f[0]), f[1])] = f[2] == "0" and f[6] == "-"
    return ok


def plane(case):
    """(a, b, c) exact, depth = a x + b y + c with x, y in pixels: from the integer vertices"""
    (x0, y0, x1, y1, x2, y2), (z0, z1, z2) = case["v"], case["z"]
    area = (x1 - x0) * (y2 - y0) - (y1 - y0) * (x2 - x0)
    if area == 0:
        return None
    # z = z0 + l1 (z1 - z0) + l2 (z2 - z0), l1 and l2 linear in the window position (1/256 pixel)
    a = Fraction((z1 - z0) * (y2 - y0) - (z2 - z0) * (y1 - y0), 1024 * area) * 256
    b = Fraction((z2 - z0) * (x1 - x0) - (z1 - z0) * (x2 - x0), 1024 * area) * 256
    c = Fraction(z0, 1024) - a * Fraction(x0, 256) - b * Fraction(y0, 256)
    return a, b, c


BANDS = [(0.0, 0.03), (0.03, 0.1), (0.1, 0.3), (0.3, 1.0), (1.0, 3.0), (3.0, 1e18)]
BINADES = [(0.0, 0.125), (0.125, 0.25), (0.25, 0.5), (0.5, 0.75), (0.75, 1.0)]


def analyse(dirn):
    cases = [c for c in load_cases(os.path.join(dirn, "cases.tsv")) if c["set"] in ("fit", "heldout")]
    ok = good_jobs(os.path.join(dirn, "main", "jobs.tsv"))
    px = []          # (gradient, err in U (Fraction), stored, value, nearest-equal, trunc-equal)
    per_tri = {}
    for c in cases:
        if not ok.get((c["id"], "D")):
            continue
        pl = plane(c)
        dp = os.path.join(dirn, "main", "D", "%d.depth.gz" % c["id"])
        if pl is None or not os.path.exists(dp):
            continue
        a, b, c0 = pl
        grad = abs(float(a)) + abs(float(b))
        pix = covered_pixels(read_gz(os.path.join(dirn, "main", "D", "%d.txt.gz" % c["id"])).decode("utf-8", "replace"),
                             c["w"], c["h"])
        if not pix:
            continue
        raw = read_gz(dp)
        words = struct.unpack("<%dI" % (len(raw) // 4), raw[:len(raw) // 4 * 4])
        g = max(1, (c["w"] + 31) // 32 - 1)
        for x, y in pix:
            exact = a * (x + Fraction(1, 2)) + b * (y + Fraction(1, 2)) + c0
            st = words[depth_index(x, y, g)]
            sv = Fraction(bits_f32(st))
            err = (sv - exact) / U
            if exact > 0:
                eq_n = f32_round_nearest(exact) == st
                eq_t = f32_truncate(exact) == st
            else:
                eq_n = eq_t = False
            px.append((grad, err, st, sv, exact, eq_n, eq_t, c["id"]))
            per_tri.setdefault(c["id"], [grad, 0.0])
            per_tri[c["id"]][1] = max(per_tri[c["id"]][1], abs(float(err)))
    return px, per_tri


def pct(n, d):
    return "%.2f%%" % (100.0 * n / d) if d else "-"


def report(px, per_tri, out):
    n = len(px)
    out("covered pixels of the fit and held-out depth jobs: %d, triangles %d" % (n, len(per_tri)))
    ab = [abs(float(p[1])) for p in px]
    out("absolute error in U = 2^-23: within 1 U %s, within 3 U %s, maximum %.1f U"
        % (pct(sum(1 for e in ab if e <= 1), n), pct(sum(1 for e in ab if e <= 3), n), max(ab)))
    tu = []
    for p in px:
        u = true_ulp(p[3]) / U if p[3] > 0 else Fraction(1)
        tu.append(abs(float(p[1])) / float(u))
    out("true float32 ulps of the stored value: within 1 ulp %s, maximum %.1f ulp"
        % (pct(sum(1 for e in tu if e <= 1), n), max(tu)))
    out("")
    out("true-ulp table by stored value (error in U, in true ulps; the unit is absolute, so the same")
    out("error in U is more true ulps for a small value)")
    out("  value range   pixels  within 1 U  max U   within 1 true ulp  max true ulps  mean signed (2^-24)")
    for lo, hi in BINADES:
        sel = [i for i, p in enumerate(px) if lo <= float(p[3]) < hi]
        if not sel:
            continue
        w1 = sum(1 for i in sel if ab[i] <= 1)
        t1 = sum(1 for i in sel if tu[i] <= 1)
        ms = sum(float(px[i][1]) for i in sel) / len(sel) * 2
        out("  %4.3f..%4.3f %8d  %9s %7.1f  %16s  %13.1f  %+19.2f"
            % (lo, hi, len(sel), pct(w1, len(sel)), max(ab[i] for i in sel), pct(t1, len(sel)),
               max(tu[i] for i in sel), ms))
    out("")
    out("error by the gradient of the plane (|dz/dx| + |dz/dy|, depth per pixel), per triangle maximum")
    out("  gradient        triangles  pixels  within 1 U  max U (any pixel)")
    for lo, hi in BANDS:
        tris = [t for t, (gr, mx) in per_tri.items() if lo <= gr < hi]
        sel = [i for i, p in enumerate(px) if lo <= p[0] < hi]
        if not sel:
            continue
        mx = max(ab[i] for i in sel)
        out("  %5.2f..%-6.2f %9d %7d  %9s  %7.1f"
            % (lo, min(hi, 99.99), len(tris), len(sel), pct(sum(1 for i in sel if ab[i] <= 1), len(sel)), mx))
    out("")
    below = sum(1 for p in px if p[1] < 0)
    above = sum(1 for p in px if p[1] > 0)
    zero = n - below - above
    ms = sum(float(p[1]) for p in px) / n * 2
    out("sign of (stored - exact plane): below %d (%s), above %d (%s), exactly equal %d (%s); of the %d "
        "non-zero: below %s" % (below, pct(below, n), above, pct(above, n), zero, pct(zero, n),
                                n - zero, pct(below, n - zero)))
    out("mean signed error %+.2f of 2^-24 (all pixels)" % ms)
    good = [p for p in px if p[0] < 0.03]
    out("")
    out("stored dword equal to the exact plane (rational) converted to float32, pixels of gradient "
        "below 0.03 (%d) and all (%d):" % (len(good), n))
    out("  rounded to nearest: %s and %s" % (pct(sum(1 for p in good if p[5]), len(good)),
                                           pct(sum(1 for p in px if p[5]), n)))
    out("  truncated toward zero: %s and %s" % (pct(sum(1 for p in good if p[6]), len(good)),
                                              pct(sum(1 for p in px if p[6]), n)))
    out("  neither: %d pixels" % (n - sum(1 for p in px if p[5] or p[6])))


def main(argv):
    dirn = argv[1] if len(argv) > 1 else os.path.join(os.environ.get("RESGX545_DATA", os.path.expanduser("~/src/resgx545-data")), "isp", "arith-1138")
    px, per_tri = analyse(dirn)
    report(px, per_tri, print)


if __name__ == "__main__":
    main(sys.argv)
