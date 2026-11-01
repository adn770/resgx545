#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The recompute of the 11.33 fold (E570 to E574), written independently of the batch's own
recompute: it reads the kept dumps of the data repository ($RESGX545_DATA, else ../resgx545-data
beside the tree) and prints the numbers the records quote.

    fold_recompute.py vtx | o23 | eot | bif | dpm | all

vtx: the 12 vertex jobs (a vertex is the 12 dwords that end at the job's marker constant); o23:
the pairs of o1 (tag 2) and the raster and region-header rules; eot: the faults and the stored
values of the end-of-tile jobs; bif: the 30 alias runs; dpm: the 36 timelines.
"""
import collections
import csv
import gzip
import math
import os
import pathlib
import re
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
DATA = pathlib.Path(os.environ.get("RESGX545_DATA") or ROOT.parent / "resgx545-data")
BG = 0xFF203040


def z(path, text=False):
    return gzip.open(path, "rt" if text else "rb").read()


def table(path):
    return list(csv.DictReader(open(path), delimiter="\t"))


# ---------------------------------------------------------------------------- vtx
GROUPS = {"A": [16, 17, 18, 19, 20, 21, 22, 23], "B": [24, 25, 26, 27, 28, 29, 30, 31],
          "C": [39, 40, 41, 42, 43, 17, 18, 19]}


def vtx():
    base = DATA / "usse/globals-vertex-eot/dumps"
    jobs = []
    for script in ("q053-vtx", "q053-vtx2"):
        for r in table(base / script / "cases.tsv"):
            n = int(re.search(r"-m(\d+)\.bin", r["args"]).group(1))
            name = r["name"]
            per = 8 if script == "q053-vtx" else {"f3": 4, "f5": 6}[re.search(r"-(f\d)-", name).group(1)]
            jobs.append((script, name, 0x3F000000 + n, name[-2] if name[-1].isdigit() else name[-1], per))

    def reg(v, g, grp):
        return v[3 + GROUPS[grp].index(g)]

    def q(g, k, per):
        t, lane = divmod(k, per)
        return {25: lane % 4, 22: lane // 4 % 2, 39: 4 * (lane // 4 % 2), 24: 8 * (t % 2), 17: t % 4,
                23: 0x10 * (t // 2 % 2)}[g]

    def f(g, k, per):
        return {25: k % 4, 22: k // 4 % 2, 39: 4 * (k // 4 % 2), 24: 8 * (k // 8 % 2), 17: k // 8 % 4}[g]

    for script, name, marker, grp, per in jobs:
        w = struct.unpack("<%dI" % (len(z(base / script / (name + ".param.bin.gz"))) // 4),
                          z(base / script / (name + ".param.bin.gz")))
        vs = [w[i - 11:i + 1] for i, x in enumerate(w) if x == marker]
        cut = [k for k, v in enumerate(vs) if not any(v[:3])]
        out = [f"{name} per {per} vertices {len(vs)} unreadable {cut}"]
        for g in GROUPS[grp]:
            if g in (17, 22, 23, 24, 25, 39):
                hq = sum(reg(v, g, grp) == q(g, k, per) for k, v in enumerate(vs) if k != 67)
                hf = (sum(reg(v, g, grp) == f(g, k, per) for k, v in enumerate(vs) if k != 67)
                      if g != 23 else None)
                out.append(f"g{g} Q {hq}/125 F {hf}")
            elif g not in (18, 21):
                c = collections.Counter(reg(v, g, grp) for k, v in enumerate(vs) if k != 67)
                out.append(f"g{g} " + ",".join(f"{a:#x}x{b}" for a, b in c.most_common()))
        print(" | ".join(out))


# ---------------------------------------------------------------------------- o23
def rows(path):
    d = {}
    for line in z(path, True).splitlines():
        m = re.match(r"probe \S+: row (\d+): (.*)$", line)
        if m:
            d[int(m.group(1))] = [int(x, 16) for x in m.group(2).split()]
    return [d[i] for i in sorted(d)]


def regions(td):
    page = 0x1000
    pg = next((i for i in range(len(td) // page) if any(td[i * page:(i + 1) * page])), None)
    ws = struct.unpack("<%dI" % (page // 4), td[pg * page:(pg + 1) * page])
    return [(((ws[3 * i] >> 16) & 0xFF) * 16, (ws[3 * i] & 0xFFF) * 8, ws[3 * i + 1]) for i in range(len(ws) // 3)
            if ws[3 * i] or ws[3 * i + 1]]


def f32(v):
    return struct.unpack("<f", struct.pack("<I", v))[0]


def o23():
    base = DATA / "usse/output-room-tiles/dumps"
    tot = collections.Counter()
    for script in ("o23-order", "o23-size"):
        cfgs = collections.OrderedDict()
        for r in table(base / script / "cases.tsv"):
            n = int(re.search(r"o23[de]?-m(\d+)\.bin", r["args"]).group(1))
            size = int(re.search(r"blk 4=(0x[0-9a-f]+)", r["args"]).group(1), 16) >> 16 & 3
            cfgs.setdefault(r["name"][:-2], {"W": int(r["W"]), "H": int(r["H"]), "size": size})[r["name"][-1]] = (
                r["name"], n)
        for key, c in cfgs.items():
            W, H = c["W"], c["H"]
            (xn, xm), (yn, ym) = c["x"], c["y"]
            rx, ry = rows(base / script / (xn + ".txt.gz")), rows(base / script / (yn + ".txt.gz"))
            L = {(x // 32, y // 16): i for i, (x, y, st) in
                 enumerate(t for t in regions(z(base / script / (xn + ".tadata.bin.gz"))) if t[2])}
            cols = math.ceil(W / 32)
            n = ras = hdr = pairs = 0
            for y, row in enumerate(rx):
                for x, vx in enumerate(row):
                    vy = ry[y][x]
                    if vx == BG or vy == BG or (vx & 0xFFFF) - 16 * xm != 2 or (vy & 0xFFFF) - 16 * ym != 2:
                        continue
                    pairs += 1
                    sx = round(f32(vx & 0xFFFF0000) * W / 2 + W / 2 - 0.5)
                    sy = round(f32(vy & 0xFFFF0000) * H / 2 + H / 2 - 0.5)
                    if sx % 32 != x % 32 or sy % 16 != y % 16:
                        continue
                    n += 1
                    s, d = (sx // 32, sy // 16), (x // 32, y // 16)
                    ras += (s[1] * cols + s[0]) - (d[1] * cols + d[0]) == 1
                    hdr += d in L and s in L and L[s] - L[d] == 1
            if pairs:
                print(f"{script} {W}x{H} size {c['size']} {key}: pairs {pairs} at the same place {n} "
                      f"raster {ras} header {hdr}")
            tot[(script, "pairs")] += pairs
            tot[(script, "place")] += n
            tot[(script, "raster")] += ras
            tot[(script, "header")] += hdr
    for k, v in sorted(tot.items()):
        print(k, v)
    print("all: place", sum(v for (s, k), v in tot.items() if k == "place"),
          "raster", sum(v for (s, k), v in tot.items() if k == "raster"),
          "header", sum(v for (s, k), v in tot.items() if k == "header"))


# ---------------------------------------------------------------------------- eot
def eot():
    base = DATA / "usse/globals-vertex-eot/dumps"
    for script in ("q053-eot-first", "q053-eot", "q053-eotcap", "q053-eotst", "q053-eot2"):
        log = (base / script / "kernel.log").read_text()
        faults = collections.Counter(re.findall(r"BIF fault 0x[0-9a-f]+ at (0x[0-9a-f]+)", log))
        print(script, "faults", dict(faults))
    for i, r in enumerate(table(base / "q053-eot2/cases.tsv"), 1):
        t = z(base / "q053-eot2" / (r["name"] + ".txt.gz"), True)
        print(i, r["name"], "failed" if "failed:" in t else "ok",
              re.findall(r"scratch \+(0x[0-9a-f]+) (0x[0-9a-f]+)", t))


# ---------------------------------------------------------------------------- bif
def bif():
    base = DATA / "bif/alias-skip/dumps"
    for script in ("bif-alias-safe", "bif-alias-risky"):
        for r in table(base / script / "cases.tsv"):
            t = z(base / script / (r["name"] + ".txt.gz"), True)
            hdr = re.search(r"timeline: regs (.*)", t).group(1).split()
            tl = [ln.split() for ln in t.splitlines() if ln.startswith("tl ")]
            col = lambda a: sorted({ln[2 + hdr.index(a)] for ln in tl})  # noqa: E731
            print(r["name"], "ok" if re.search(r"tri: \d+ renders ok", t) else "FAILED", "BASE1", col("0x0c38"),
                  "BASE2", col("0x0c3c"), "BASE15", col("0x0c70"), "BANK0", col("0x0c78"))


# ---------------------------------------------------------------------------- dpm
def dpm():
    base = DATA / "dpm/bit2-grid/dumps"
    failed = 0
    for script in ("dpm-bit2-safe", "dpm-bit2-risky"):
        for r in table(base / script / "cases.tsv"):
            t = z(base / script / (r["name"] + ".txt.gz"), True).splitlines()
            hdr = next(ln for ln in t if ln.startswith("timeline: regs"))
            regs = re.search(r"regs (.*?) samples", hdr).group(1).split()
            tl = [ln.split() for ln in t if ln.startswith("tl ")]
            v = lambda a, k: int(tl[k][2 + regs.index(a)], 16)  # noqa: E731
            hi = {(v("0x0710", k) >> 16, v("0x071c", k) >> 16, v("0x0740", k)) for k in range(len(tl))}
            clr = [k for k in range(len(tl)) if not v("0x0748", k) & 4]
            gaps = [int(tl[k + 1][1]) - int(tl[k][1]) for k in clr if k + 1 < len(tl)]
            failed += any("failed:" in ln for ln in t)
            print(r["name"], "lines", len(tl), "samples", re.search(r"samples (\d+)", hdr).group(1), "hi/0740", hi,
                  "bit2 clear", clr, "ns", gaps)
    print("failed jobs", failed)


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    for name, fn in (("vtx", vtx), ("o23", o23), ("eot", eot), ("bif", bif), ("dpm", dpm)):
        if what in (name, "all"):
            print(f"## {name}")
            fn()
