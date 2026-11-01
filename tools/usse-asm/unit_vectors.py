#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Unit vectors (doc/specs/vectors.md section 5) from landed datasets: the first four of phase
12.0, each the data of a record that states a rule.

    zls-store   E465, E489   zls/store-layout-dumps: 18 cases, the stored depth dumps by digest;
                             expected counts from the dataset's recompute.txt
    te-region   E542         ta/tri-region: 35 jobs, the pixel vertices (the recompute's geometry,
                             an assumption it states) and the tiles the control streams list
    ta-object   E541         ta/object-format: 59 jobs, the object's stored dwords, format word and
                             masks, or the failure
    isp-tile    E503         isp/msaa-ident: 48 runs, the position dumps by digest; expected counts
                             from the dataset's an_ident_rule.txt

    unit_vectors.py --data DATA --out OUT

OUT is unit-vectors/ of the data repository (outside vectors/, so the simulator's replay of
vectors/ is unchanged). The expected values are what the hardware dumps and the datasets' own
recompute output say, never what sgx-pipe computes.
"""
import argparse
import datetime
import gzip
import hashlib
import importlib.util
import json
import pathlib
import re
import struct
import sys

sys.dont_write_bytecode = True  # the dataset's recompute script is read, never compiled beside it
TOOL = "unit_vectors.py 1"
Z = "zls/store-layout-dumps"
T = "ta/tri-region"
F = "ta/object-format"
M = "isp/msaa-ident"


def words(path):
    b = gzip.decompress(pathlib.Path(path).read_bytes())
    return struct.unpack("<%dI" % (len(b) // 4), b[:len(b) // 4 * 4])


def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def ref(data, rel):
    return {"path": rel, "sha256": sha(data / rel)}


def recompute(data):
    """recompute_p1131.py of the ta/tri-region dataset (its decoders, read as the dataset's own)."""
    p = data / T / "analysis/recompute_p1131.py"
    spec = importlib.util.spec_from_file_location("recompute_p1131", p)
    m = importlib.util.module_from_spec(spec)
    sys.modules["recompute_p1131"] = m
    spec.loader.exec_module(m)
    return m


# ---------------------------------------------------------------------------------- zls-store
def zls_classes(w, h, g, ax, ay):
    """The stored dwords of a pair of ramp dumps by class, from the dumps alone (written here, not
    taken from the dataset's recompute): at the rule's address inside the target, at it for a pixel
    past the target (Q122), background past the target in a tile of it (Q122), background or zero
    in a slot that is no tile of the target or all zero (Q107), anything else (unexplained)."""
    def ramp(v, size):
        p = (struct.unpack("<f", struct.pack("<I", v))[0] - 0.25) * 6.0 * size
        q = round(p - 0.5)
        return q if q >= 0 and abs(p - 0.5 - q) <= 0.05 else None

    def index(x, y):
        i = (x >> 4 & 1) << 8
        for b in range(4):
            i |= (y >> b & 1) << 2 * b | (x >> b & 1) << 2 * b + 1
        return i

    c = dict(inside=0, outside=0, bg_outside=0, bg_tiles=0, zero=0, other=0)
    for i, (vx, vy) in enumerate(zip(ax, ay)):
        if vx == 0xDEADBEEF:
            continue
        slot, k = i >> 9, i & 511
        ty, tx = divmod(slot, g + 1)
        in_grid = tx < -(-w // 32) and ty < -(-h // 16)
        x = (k >> 8 & 1) << 4
        y = 0
        for b in range(4):
            y |= (k >> 2 * b & 1) << b
            x |= (k >> 2 * b + 1 & 1) << b
        past = 32 * tx + x >= w or 16 * ty + y >= h
        if vx == vy == 0x3F800000 and (not in_grid or past):
            c["bg_outside" if in_grid else "bg_tiles"] += 1
        elif vx == vy == 0:
            c["zero"] += 1
        else:
            px, py = ramp(vx, w), ramp(vy, h)
            if px is not None and py is not None and 512 * (py // 16 * (g + 1) + px // 32) + index(px % 32, py % 16) == i:
                c["outside" if px >= w or py >= h else "inside"] += 1
            else:
                c["other"] += 1
    return c


def zls_store(data):
    out = []
    for line in (data / Z / "recompute.txt").read_text().splitlines():
        m = re.match(r"(fit|ho)\s+(\d+)x(\d+)\s+G=(\d+)\s+stored\s+(\d+) \| at the rule's address\s+(\d+), "
                     r"not\s+(\d+), background\s+(\d+), undecodable (\d+) \| slots (\d+) of (\d+) "
                     r"\(sets equal (\w+)\)(?: \| pixels at their address (\d+), not (\d+))?", line)
        if not m:
            continue
        name, w, h, g, stored, ok, bad, bg, und, slots, want, eq = m.groups()[:12]
        assert bad == "0" and eq == "True" and slots == want
        w, h, g = int(w), int(h), int(g)
        base = "%s-%dx%d-G%d" % (name, w, h, g)
        cl = zls_classes(w, h, g, words(data / Z / "dumps" / (base + "-rampx.bin.gz")),
                         words(data / Z / "dumps" / (base + "-rampy.bin.gz")))
        # the dataset's own totals must still hold: its "at the rule" is the inside and the
        # outside pixels together, its "background" the two background classes
        assert cl["inside"] + cl["outside"] == int(ok) and cl["bg_outside"] + cl["bg_tiles"] == int(bg), (base, cl)
        assert cl["zero"] == int(und) and cl["other"] == 0
        expect = {"stored": int(stored), "matched": cl["inside"], "refused": {}}
        if cl["outside"] + cl["bg_outside"]:
            expect["refused"]["Q122"] = cl["outside"] + cl["bg_outside"]
        if cl["zero"] + cl["bg_tiles"]:
            expect["refused"]["Q107"] = cl["zero"] + cl["bg_tiles"]
        if m[13] is not None:
            assert m[14] == "0"
            expect["back_ok"] = int(m[13])
        out.append({
            "id": "zls-store__" + base,
            "init": {"task": "zls-store", "w": w, "h": h, "g": g,
                     "depth_ctl": "0x%08x" % ((0x0017100c & ~(0x1ff << 3)) | g << 3),
                     "fill": "0xdeadbeef", "background": "0x3f800000",
                     "x": ref(data, "%s/dumps/%s-rampx.bin.gz" % (Z, base)),
                     "y": ref(data, "%s/dumps/%s-rampy.bin.gz" % (Z, base))},
            "expect": expect,
            "provenance": {"records": ["E465", "E489"], "questions": ["Q107", "Q122"], "table": Z,
                           "case": base, "rule_status": "fitted E465 (fitted on the 1024 x 768 runs)",
                           "rebuilt": False}})
    return out


# ---------------------------------------------------------------------------------- te-region
def observed(R, par, td, nprims):
    """{(x0, y0): 'any' | [primitives]} per 16 x 16 tile of the first control stream of each region
    (an_tb2.py of the dataset; the forms 0x80, 0x90, 0x98 name no primitive of the object)."""
    obs, bad = {}, 0
    for (_i, x0, y0, _f, st) in R.regions(td):
        if not st:
            continue
        sw = R.stream(par, st)
        t = (sw[0] >> 16) & 0xff
        if t in (0x80, 0x98) and nprims <= 8:
            # one tile; the primitive word's bits 7:0 are its primitive mask (recompute_p1131.py's
            # observed_tiles: 39 of 39 single-tile regions agree), so the list is per primitive
            m = [p for p in range(nprims) if sw[0] >> p & 1]
            left, right = (m, False) if t == 0x80 else (False, m)
        elif t in (0x80, 0x90, 0x98):
            left, right = t in (0x80, 0x90) and "any", t in (0x98, 0x90) and "any"
        elif t == 0x88:
            left = [p for p in range(nprims) if sw[2] & (1 << p)]
            right = [p for p in range(nprims) if (sw[2] >> 16) & (1 << p)]
        elif t in (0x8a, 0x8c):
            m = [p for p in range(nprims) if sw[2] & (1 << p)]
            left, right = (m, False) if t == 0x8a else (False, m)
        else:
            bad += 1
            continue
        for key, v in (((x0, y0), left), ((x0 + 16, y0), right)):
            if v is False:
                continue
            old = obs.get(key)
            if v == "any" or old == "any":
                obs[key] = "any"
            else:
                obs[key] = sorted(set(old or []) | set(v))
    return obs, bad


def te_region(data):
    R = recompute(data)
    out = []
    for line in (data / T / "cases.tsv").read_text().splitlines()[1:]:
        p = line.split("\t")
        c = dict(name=p[0], script=p[1], set=p[2], w=int(p[3]), h=int(p[4]), args=p[5])
        d = data / T / "dumps" / c["script"]
        txt, par, td = R.load(d, c["name"])
        if R.outcome(txt) == "fail" or not par:
            continue
        v = R.geometry(c["args"], c["w"], c["h"])
        tris = [v[i:i + 3] for i in range(0, len(v) - 2, 3)]
        obs, bad = observed(R, par, td, len(tris))
        assert bad == 0
        pairs = (c["w"] // 16) * (c["h"] // 16) * len(tris)
        out.append({
            "id": "te-region__" + c["name"],
            "init": {"task": "te-region", "w": c["w"], "h": c["h"], "prims": [[list(q) for q in t] for t in tris]},
            "expect": {"matched": pairs,
                       "listed": [[x, y, obs[(x, y)]] for (x, y) in sorted(obs, key=lambda k: (k[1], k[0]))]},
            "provenance": {"records": ["E542", "E180"], "questions": ["Q070"], "table": T, "case": c["name"],
                           "set": c["set"], "options": c["args"].split(" --dump-render")[0].split(),
                           "geometry": "assumed by the recompute (NDC constants, c / 16 pixel shift), "
                                       "not read from the packed vertices",
                           "rule_status": "fitted E542 (H70-T1, fitted post hoc to E180)",
                           "rebuilt": False}})
    return out


# ---------------------------------------------------------------------------------- ta-object
def ta_object(data):
    R = recompute(data)
    out = []
    base = data / F
    for line in (base / "cases.tsv").read_text().splitlines()[1:]:
        p = line.split("\t")
        name, script, sset, args = p[0], p[1], p[2], p[5]
        d = base / "dumps" / script
        txt, par, td = R.load(d, name)
        n = int(re.search(r"--vtx-coords (\d+)", args)[1])
        m = re.search(r"--blk 16=(\d+) --blk 17=(\d+)", args)
        sizes, fmts = int(m[1]), int(m[2])
        o = R.first_object(par, td) if par and td else None
        expect = {}
        extra = {}
        if R.outcome(txt) == "fail" or not o or "error" in o:
            why = re.search(r"failed: job (\w+)", txt)
            kind = {"faulted": "fault", "hung": "hang"}[why[1]]
            expect = {"outcome": kind, "refuse": ["Q165"]}  # recalled by the model, not predicted
        else:
            expect = {"stored": o["per"], "iterated": (o["fmt"] >> 8) & 0xff,
                      "format_hi": "0x%04x" % (o["fmt"] >> 16), "masks": list(o["masks"])}
            extra = {"format_word": "0x%08x" % o["fmt"]}
        out.append({
            "id": "ta-object__" + name,
            "init": {"task": "ta-object", "n": n, "sizes": sizes, "fmts": fmts},
            "expect": expect,
            "provenance": dict({"records": ["E541", "E308"], "questions": ["Q070", "Q165"], "table": F,
                                "case": name, "set": sset, "script": script,
                                "rule_status": "fitted E541 (H70-F2, written from the first run)",
                                "rebuilt": False}, **extra)})
    return out


# ---------------------------------------------------------------------------------- isp-tile
def isp_tile(data):
    """E503: per run of isp/msaa-ident, the pair of position dumps (x and y of each source pixel as
    the 11.26 reading decodes them) and the counts of an_ident_rule.txt: tiles with decodable
    pixels, and the tiles decodable in all 512 pixels."""
    out = []
    base = data / M
    rule = {}
    for line in (base / "analysis/an_ident_rule.txt").read_text().splitlines():
        m = re.match(r"(\S+)\s+\S+\s+\S+\s+m\d te 0x[0-9a-f]+: tiles (\d+), with decodable pixels (\d+), equal to the "
                     r"rule (\d+), fully decodable (\d+), pixels decodable (\d+) of (\d+)", line)
        if m:
            rule[m[1]] = tuple(int(x) for x in m.groups()[1:])
    rows = [l.split("\t") for l in (base / "cases.tsv").read_text().splitlines()[1:]]
    for name, sset, w, h, mode, te in rows:
        tiles, with_px, equal, full, dec, stored = rule[name]
        assert equal == with_px == tiles   # every tile with a decodable pixel equals the rule
        out.append({
            "id": "isp-tile__" + name,
            "init": {"task": "isp-tile", "w": int(w), "h": int(h), "mode": int(mode), "te_aa": te,
                     "x": ref(data, "%s/dumps/%s-x.txt.gz" % (M, name)),
                     "y": ref(data, "%s/dumps/%s-y.txt.gz" % (M, name))},
            "expect": {"tiles": tiles, "matched": full, "refused": {"Q141": tiles - full} if tiles > full else {},
                       "decodable": dec, "stored": stored},
            "provenance": {"records": ["E503", "E502"], "questions": ["Q141", "Q138"], "table": M, "case": name,
                           "set": sset, "rule_status": "fitted E503 (read post hoc from the 64 x 64 runs)",
                           "rebuilt": False}})
    return out


# ---------------------------------------------------------------------------------- pbe-emit
PM = "pbe/pack-modes"
PC = "pbe/pack-colours"
SENTINEL = "0xdeadbeef"
BG = "0xff203040"  # the triangle jobs' background colour


def pack_values(items, size):
    """The values stored for the background and the shader colour, from a report's `mixed` items
    ("0xVALUExCOUNT"): the two most common words that are not the sentinel, the background first
    (it covers more pixels); two-byte pixels are the halves of the words that hold the same one
    twice."""
    cs = [(int(c), v) for v, c in (i.rsplit("x", 1) for i in items) if v != SENTINEL]
    cs.sort(reverse=True)
    if size == 4:
        return [v for _, v in cs[:2]]
    return ["0x%x" % (int(v, 16) & 0xFFFF) for _, v in cs if int(v, 16) >> 16 == int(v, 16) & 0xFFFF][:2]


def mixed(report, tag):
    """The `mixed` items of the report line for `tag`; none for a mode whose job faulted."""
    for line in report.splitlines():
        if tag in line and "mixed" in line:
            return line.split("mixed", 1)[1].split()
    return []


def pbe_emit(data):
    """E031: per pack mode of pbe/pack-modes, the values the end-of-tile emit stored for the
    background 0xff203040 and the shader colour 0x80ff8040 of the 64 x 64 triangle (modes 0 to 3,
    which the model packs; the other 60 are refused, 22 and 34 under Q012 and the rest under
    Q044), and E268's mode 0 over the ten shader colours of pbe/pack-colours."""
    out = []
    for m in range(64):
        r = (data / PM / ("pbe-pack-modes-packmode-%02d" % m) / "report.txt").read_text()
        v = {"id": "pbe-emit__packmode-%02d" % m,
             "init": {"task": "pbe-emit", "sideband": "0x%x" % (0x200 | m), "reg0400": "0x80",
                      "colours": [BG, "0x80ff8040"]},
             "provenance": {"records": ["E031", "E030"], "questions": ["Q012", "Q044"], "table": PM,
                            "case": "packmode-%02d" % m, "rebuilt": False}}
        if m < 4:
            v["expect"] = {"stored": pack_values(mixed(r, "pack mode %d" % m), 2 if m == 3 else 4)}
        else:
            v["expect"] = {"refuse": ["Q012"] if m in (22, 34) else ["Q044"],
                           "mixed": mixed(r, "pack mode %d" % m)}
        out.append(v)
    r = (data / PC / "pbe-pack-colours-mode0/report.txt").read_text()
    for line in r.splitlines():
        mm = re.match(r"\s+\[(\d+)\] o0 (0x[0-9a-f]+): mixed (.*)", line)
        if not mm:
            continue
        k, o0, items = int(mm[1]), mm[2], mm[3].split()
        stored = pack_values(items, 4)
        out.append({"id": "pbe-emit__colours-mode0-%d" % k,
                    "init": {"task": "pbe-emit", "sideband": "0x200", "reg0400": "0x80", "colours": [o0]},
                    "expect": {"stored": [stored[0] if len(stored) == 1 else [s for s in stored if s != BG][0]]},
                    "provenance": {"records": ["E031"], "questions": [], "table": PC,
                                   "case": "mode0-%d" % k, "rebuilt": False}})
    return out


# ---------------------------------------------------------------------------------- files
FILES = [("zls/store-layout/zls-store-layout-dumps.vec.json", zls_store, Z + "/output.txt"),
         ("ta/te-region/ta-tri-region.vec.json", te_region, T + "/output.txt"),
         ("ta/object-format/ta-object-format.vec.json", ta_object, F + "/output.txt"),
         ("isp/msaa-window/isp-msaa-ident.vec.json", isp_tile, M + "/output.txt"),
         ("pbe/pack-modes/pbe-pack-modes.vec.json", pbe_emit, PM + "/pbe-pack-modes-packmode-00/report.txt")]


def write_all(data, out):
    for rel, fn, raw in FILES:
        vs = fn(data)
        doc = {"format": "sgx545-vectors", "version": 1,
               "run": {"raw": raw, "raw_sha256": sha(data / raw), "tool": TOOL},
               "vectors": vs, "orphans": []}
        p = pathlib.Path(out) / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--data", required=True, type=pathlib.Path)
    ap.add_argument("--out", required=True, type=pathlib.Path)
    a = ap.parse_args(argv)
    write_all(a.data, a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
