#!/usr/bin/env python3
"""tie_depth_1138.py: the depth evidence for the vertex rounding of record E607, from the stored fine
and fine2 dumps of the 11.37 arithmetic sweep, with the standard library only.

Usage: RESGX545_DATA=~/src/resgx545-data tie_depth_1138.py [DIR]   (DIR: the dataset directory)

The stored depth uses the rounded vertices.  For each case with exactly one coordinate that is an
exact tie (the fraction of 256 x is exactly 1/2 of a grid unit) and for each case with one coordinate
at 127/256 of a grid unit, the covered pixels' depth is compared with the exact plane through the
vertices rounded half up and rounded half down (error in units of 2^-23, as depth_error_1138.py).
Per case the median absolute error over its covered pixels; the table gives the smallest and the
largest of these per class.  The other coordinates round alike in both rules."""
import os
import statistics
import struct
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import depth_error_1138 as D  # noqa: E402


def load_fine(path):
    out = []
    for line in open(path):
        f = line.rstrip("\n").split("\t")
        if len(f) < 17:
            continue
        out.append(dict(id=int(f[0]), set=f[1], cls=f[2], w=int(f[3]), h=int(f[4]),
                        v=[int(t) for t in f[5:11]], z=[round(float(t) * 1024) for t in f[11:14]],
                        k=int(f[16])))
    return out


def rounded(v, k, mode):
    """vertex coordinates in 1/2^k pixel to integers in 1/256 pixel, half up or half down"""
    s = k - 8
    if s <= 0:
        return [t << -s for t in v]
    half = 1 << (s - 1)
    return [(t + half - (1 if mode == "down" else 0)) >> s for t in v]


def frac_at(v, k, num):
    """indices of the coordinates whose fraction of a grid unit is exactly num / 256"""
    s = k - 8
    if s < 8:
        return [i for i, t in enumerate(v) if s > 0 and (t % (1 << s)) * 256 == num * (1 << s)]
    return [i for i, t in enumerate(v) if (t % (1 << s)) * 256 == num * (1 << s)]


def case_errors(c, dirn, setdir, v256):
    pl = D.plane(dict(v=v256, z=c["z"]))
    if pl is None:
        return None
    a, b, c0 = pl
    base = os.path.join(dirn, setdir, "D", "%d" % c["id"])
    pix = D.covered_pixels(D.read_gz(base + ".txt.gz").decode("utf-8", "replace"), c["w"], c["h"])
    if not pix:
        return None
    raw = D.read_gz(base + ".depth.gz")
    words = struct.unpack("<%dI" % (len(raw) // 4), raw[:len(raw) // 4 * 4])
    g = max(1, (c["w"] + 31) // 32 - 1)
    errs = []
    for x, y in pix:
        exact = a * (x + Fraction(1, 2)) + b * (y + Fraction(1, 2)) + c0
        sv = Fraction(D.bits_f32(words[D.depth_index(x, y, g)]))
        errs.append(abs(float((sv - exact) / D.U)))
    return statistics.median(errs)


def analyse(dirn):
    res = {}
    for name, setdir in (("cases-fine.tsv", "fine"), ("cases-fine2.tsv", "fine2")):
        ok = D.good_jobs(os.path.join(dirn, setdir, "jobs.tsv"))
        for c in load_fine(os.path.join(dirn, name)):
            if c["cls"].startswith("tinyedge") or not ok.get((c["id"], "D")):
                continue
            ties = frac_at(c["v"], c["k"], 128)
            near = frac_at(c["v"], c["k"], 127)
            if len(ties) == 1 and not near:
                i = ties[0]
                up = case_errors(c, dirn, setdir, rounded(c["v"], c["k"], "up"))
                down = case_errors(c, dirn, setdir, rounded(c["v"], c["k"], "down"))
                par = "even" if (rounded(c["v"], c["k"], "down")[i] % 2 == 0) else "odd"
                if up is not None and down is not None:
                    res.setdefault(("tie", par, "x" if i % 2 == 0 else "y"), []).append((up, down))
            elif len(near) == 1 and not ties:
                rule = rounded(c["v"], c["k"], "up")          # 127/256 is below the tie: rounds down
                forced = list(rule)
                forced[near[0]] += 1                          # the alternative: rounded up
                a = case_errors(c, dirn, setdir, rule)
                b = case_errors(c, dirn, setdir, forced)
                if a is not None and b is not None:
                    res.setdefault(("127/256", "-", "-"), []).append((a, b))
    return res


def report(res, out_raw):
    def out(line):
        out_raw(line.rstrip())
    n = sum(len(v) for k, v in res.items() if k[0] == "tie")
    out("cases with exactly one coordinate at an exact tie of the 1/256 grid: %d" % n)
    out("  class                  cases  median error half up (min..max)  half down (min..max), in 2^-23")
    out("  (the 127/256 row: the columns are rounded down, the rule, and rounded up)")
    for k in sorted(res):
        v = res[k]
        up = [t[0] for t in v]
        dn = [t[1] for t in v]
        out("  %-8s %-5s axis %-1s %6d   %7.2f .. %-8.2f   %8.2f .. %-8.2f"
            % (k[0], k[1], k[2], len(v), min(up), max(up), min(dn), max(dn)))
    ties = [t for k, v in res.items() if k[0] == "tie" for t in v]
    out("tie cases: half up has the smaller median in %d of %d" % (sum(1 for t in ties if t[0] < t[1]), len(ties)))
    out("tie cases with a median error of at most 1 U: half up %d, half down %d"
        % (sum(1 for t in ties if t[0] <= 1), sum(1 for t in ties if t[1] <= 1)))
    near = res.get(("127/256", "-", "-"), [])
    out("cases with one coordinate at 127/256 of a grid unit: %d; median error rounded down (the rule) "
        "%s, rounded up %s (2^-23)" % (len(near), ", ".join("%.2f" % t[0] for t in near),
                                       ", ".join("%.2f" % t[1] for t in near)))


def main(argv):
    dirn = argv[1] if len(argv) > 1 else os.path.join(
        os.environ.get("RESGX545_DATA", os.path.expanduser("~/src/resgx545-data")), "isp", "arith-1138")
    report(analyse(dirn), print)


if __name__ == "__main__":
    main(sys.argv)
