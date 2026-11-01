#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Recompute the 11.32 results from the kept dumps, sharing no code with the run scripts.

    python3 -B recompute/recompute_p1132.py DIR            report on DIR/<script>/ (cases.tsv, NAME.txt.gz)
    python3 -B recompute/recompute_p1132.py DIR --raw OUT  also write campaign-form raw.txt and bins/ under OUT
    python3 -B recompute/recompute_p1132.py --selftest     dumps made by validate/fakehw.py, then recompute

DIR holds one subdirectory per script (the laptop's ~/p1132-dumps/*). Each case is read from its gz
output (the 2048 pixels of `probe NAME: row Y:` lines), compared with the declared predictions of
predictions-declared.tsv (re-rendered by texmodel.py and checked against the declared sha256), scored
per hypothesis by group and set, then analysed per group (sections D1 to D9). A case that is in DIR
and not in declared.tsv is listed. Nothing here writes a laptop file.
"""
from __future__ import annotations

import collections
import gzip
import json
import math
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
P = HERE.parent
sys.path.insert(0, str(HERE))
import texmodel as tm   # noqa: E402

SPECS = json.loads((P / "gen" / "specs.json").read_text())
ROW = re.compile(r"row (\d+):(.*)$")


def load_declared():
    pred = collections.defaultdict(dict)
    for ln in (P / "predictions-declared.tsv").read_text().splitlines()[1:]:
        s, c, st, h, sha = ln.split("\t")
        pred[c][h] = sha
    decl = {}
    for ln in (P / "declared.tsv").read_text().splitlines()[1:]:
        s, c, st, rk, q = ln.split("\t")
        decl[c] = (s, st, rk, q)
    return pred, decl


def read_case(path: pathlib.Path):
    """(pixels or None, failed text or None) of one kept output."""
    txt = gzip.open(path, "rt", errors="replace").read()
    rows = {}
    for ln in txt.splitlines():
        m = ROW.search(ln)
        if m:
            rows[int(m.group(1))] = [int(v[2:] if v.startswith("0x") else v, 16) for v in m.group(2).split()]
    failed = next((ln for ln in txt.splitlines() if re.search(r"failed|faulted|hung", ln)), None)
    pix = [v for y in sorted(rows) for v in rows[y]]
    return (pix if len(pix) in (2048, 4096) else None), failed


def name_idx(v: int):
    return v & 0xFFFF if v >> 28 == 0xD and not v & 0x0FFF0000 else None


# ------------------------------------------------------------------------------- loading
def load_dir(root: pathlib.Path):
    cases = {}
    for sd in sorted(p for p in root.iterdir() if p.is_dir()):
        tsv = sd / "cases.tsv"
        if not tsv.exists():
            continue
        for ln in tsv.read_text().splitlines()[1:]:
            f = ln.split("\t")
            name = f[0]
            gz = sd / f"{name}.txt.gz"
            if not gz.exists():
                cases[name] = {"script": sd.name, "status": "not run", "set": f[2], "risk": f[3]}
                continue
            pix, failed = read_case(gz)
            cases[name] = {"script": sd.name, "pix": pix, "failed": failed, "set": f[2], "risk": f[3],
                           "status": "ok" if pix and not failed else ("failed" if failed else "no pixels")}
    return cases


def sha(pix):
    return tm.digest(pix)


# ------------------------------------------------------------------------------- scoring
def score(cases, pred):
    print("== B. predictions: declared sha256 against the dumps, per group, set and hypothesis")
    tab = collections.defaultdict(lambda: [0, 0])
    stale = 0
    for name, c in cases.items():
        sp = SPECS.get(name)
        if not sp or c["status"] != "ok":
            continue
        obs = sha(c["pix"])
        for h, want in pred.get(name, {}).items():
            k = (sp["group"], c["set"], h)
            tab[k][1] += 1
            tab[k][0] += obs == want
        # the declared predictions must still be what the model renders (none are declared for the
        # explorations of formats and TEXTYPEs the records do not model)
        for rl, hl in zip(sp["rules"] if name in pred else [], sp["hyps"]):
            px = tm.render(sp["spec"], rl)
            if px is not None and pred.get(name, {}).get(hl) != sha(px):
                stale += 1
    for (g, st, h), (ok, n) in sorted(tab.items()):
        print(f"  {g:18s} {st:8s} {h:34s} exact {ok:3d} of {n:3d}")
    print(f"  declared predictions that the model no longer renders: {stale}")
    return tab


def pixel_agree(name, c, rules):
    sp = SPECS[name]
    px = tm.render(sp["spec"], rules)
    return sum(a == b for a, b in zip(px, c["pix"])) if px else None


# ------------------------------------------------------------------------------- D1: twiddle
def gf2_solve(rows, rhs, n):
    """x with parity(row & x) = rhs for every row (x of n bits, free bits 0), or None."""
    piv = {}
    for r, b in zip(rows, rhs):
        for p in sorted(piv, reverse=True):
            if r >> p & 1:
                r ^= piv[p][0]
                b ^= piv[p][1]
        if r == 0:
            if b:
                return None
            continue
        piv[r.bit_length() - 1] = (r, b)
    x = 0
    for p in sorted(piv):
        r, b = piv[p]
        if b ^ (bin(r & x & ~(1 << p)).count("1") & 1):
            x |= 1 << p
    return x


def texel_of(spec, x, y):
    _, ax, a, xo, _e = spec["u"]
    _, ay, b, yo, _f = spec["v"]
    return (x | xo) & ((1 << a) - 1), (y | yo) & ((1 << b) - 1)


def d1_twiddle(cases):
    print("== D1. twiddle at size (N1): index of texel (X, Y) of a W x H level 0")
    by = collections.defaultdict(dict)
    bad = collections.Counter()
    for name, c in cases.items():
        sp = SPECS.get(name)
        if not sp or sp["group"] != "twiddle" or c["status"] != "ok":
            continue
        t1 = sp["spec"]["t1"]
        w, h = (t1 >> 12 & 0xFFF) + 1, (t1 & 0xFFF) + 1
        for y in range(32):
            for x in range(64):
                i = name_idx(c["pix"][y * 64 + x])
                if i is None:
                    bad[(w, h)] += 1
                    continue
                full = texel_of(sp["spec"], x, y)
                prev = by[(w, h)].get(full)
                if prev is not None and prev != i:
                    bad[(w, h, "inconsistent")] += 1
                by[(w, h)][full] = i
    for (w, h), m in sorted(by.items()):
        bw, bh = w.bit_length() - 1, h.bit_length() - 1
        plain = sum(i == tm.morton(x, y, w, h) for (x, y), i in m.items())
        n = bw + bh + 1
        deps = []
        ok = True
        for j in range(bw + bh):
            rows = [sum(((x >> b) & 1) << b for b in range(bw)) | sum(((y >> b) & 1) << (bw + b) for b in range(bh))
                    | 1 << (bw + bh) for (x, y) in m]
            rhs = [i >> j & 1 for i in m.values()]
            x_ = gf2_solve(rows, rhs, n)
            if x_ is None:
                ok = False
                break
            deps.append(x_)
        txt = "not GF(2)-affine"
        if ok:
            def nm(v):
                return "+".join(([f"x{b}" for b in range(bw) if v >> b & 1] + [f"y{b}" for b in range(bh) if v >> (bw + b) & 1]
                                 + (["1"] if v >> (bw + bh) & 1 else []))) or "0"
            txt = "affine: " + " ".join(f"i{j}={nm(d)}" for j, d in enumerate(deps))
        print(f"  {w:3d}x{h:<3d} texels seen {len(m):5d}, plain Morton {plain:5d}, non-name or inconsistent "
              f"{bad.get((w, h), 0) + bad.get((w, h, 'inconsistent'), 0)}; {txt if plain != len(m) else 'plain Morton throughout'}")


# ------------------------------------------------------------------------------- D2: chain shapes
def d2_shapes(cases):
    print("== D2. chains of other shapes (Q104): per shape and LOD, the dword range read; hypotheses A, B, D")
    seen = collections.defaultdict(set)
    for name, c in cases.items():
        sp = SPECS.get(name)
        if not sp or sp["group"] != "shapes" or c["status"] != "ok":
            continue
        t1 = sp["spec"]["t1"]
        w, h = (t1 >> 12 & 0xFFF) + 1, (t1 & 0xFFF) + 1
        lod = int(round(tm.fb(sp["spec"]["lod"][1])))
        for v in c["pix"]:
            seen[(w, h, lod)].add(name_idx(v))
    for (w, h, lod), s in sorted(seen.items()):
        names = sorted(i for i in s if i is not None)
        o = f"{len(names)} dwords {names[0]}..{names[-1]}" if names else "no names"
        want = {}
        for r in "ABD":
            ch = tm.chain(w, h, r)
            l = min(lod, len(ch) - 1)
            want[r] = f"{ch[l][2]}+{ch[l][0] * ch[l][1]}"
        print(f"  {w:3d}x{h:<3d} LOD {lod}: read {o}; level base+size A {want['A']} B {want['B']} D {want['D']}"
              + ("   (non-name values %d)" % (None in s) if None in s else ""))


# ------------------------------------------------------------------------------- D3: LOD fraction
def blend(a, b, f):
    return sum((((a >> 8 * c & 255) * (64 - f) + (b >> 8 * c & 255) * f + 32) >> 6) << 8 * c for c in range(4))


def d3_lod(cases):
    print("== D3. LOD of gradients and of the quad (Q050, Q115): LOD read per pixel as level + fraction / 64")
    for name, c in cases.items():
        sp = SPECS.get(name)
        if not sp or sp["group"] not in ("lod-grad", "lod-auto") or c["status"] != "ok":
            continue
        spec = sp["spec"]
        tex = tm.Tex(spec["t0"], spec["t1"], spec["base"], spec["t3"], 16, dict(tm.RULES))
        obs = []
        unres = 0
        prev = None
        for y in range(32):
            for x in range(64):
                u, v = tm.ev(spec["u"], x, y), tm.ev(spec["v"], x, y)
                got = c["pix"][y * 64 + x]
                sols = []
                for L in range(0, 6):
                    a, b = tex.level_read(u, v, L, False), tex.level_read(u, v, L + 1, False)
                    sols += [L + f / 64 for f in range(64) if blend(a, b, f) == got]
                if not sols:
                    unres += 1
                    obs.append(None)
                    continue
                # several (level, fraction) pairs can make the same value: keep the one nearest the
                # neighbour on the left (the first pixel of a row: nearest the one above)
                ref = prev if prev is not None else sols[0]
                hit = min(sols, key=lambda t: abs(t - ref))
                obs.append(hit)
                prev = hit
        dev = {}
        for r in ("max4", "euc", "min", "pwl_max4", "pwl_euc"):
            rl = {"lodf": r}
            px = tm.render(spec, rl)
            dev[r] = sum(a == b for a, b in zip(px, c["pix"]))
        best = max(dev, key=dev.get)
        row0 = " ".join("%.2f" % o if o is not None else "  ? " for o in obs[0:64:8])
        print(f"  {name:14s} unresolved {unres:4d}; exact pixels " + " ".join(f"{k} {v}" for k, v in dev.items())
              + f"; best {best}; LOD at x=0,8..56 (y=0): {row0}")


# ------------------------------------------------------------------------------- D4: anisotropy
def d4_afilt(cases):
    print("== D4. anisotropy (Q115): ratio sweep against single-level bilinear; bit flips against the control")
    ctl = cases.get("an-ctl")
    for name, c in sorted(cases.items()):
        sp = SPECS.get(name)
        if not sp or sp["group"] != "afilt" or c["status"] != "ok":
            continue
        ex = {r: pixel_agree(name, c, {"lodf": r}) for r in ("max4", "euc", "min")}
        d = "" if not ctl or ctl["status"] != "ok" else f"; differs from control at {sum(a != b for a, b in zip(ctl['pix'], c['pix']))}"
        print(f"  {name:10s} single-level bilinear, exact pixels max4 {ex['max4']} euc {ex['euc']} min {ex['min']}{d}")


# ------------------------------------------------------------------------------- D5: border
def d5_border(cases):
    print("== D5. address modes 4 to 7 (Q050, E033): decoded texel column along y = 8 (a u sweep) or row along x = 8")
    for name, c in sorted(cases.items()):
        sp = SPECS.get(name)
        if not sp or sp["group"] != "border" or c["status"] != "ok":
            continue
        t1 = sp["spec"]["t1"]
        w, h = (t1 >> 12 & 0xFFF) + 1, (t1 & 0xFFF) + 1
        base = sp["spec"]["base"]
        ty = t1 >> 29

        def dec(v):
            i = name_idx(v)
            if i is None:
                return "B%x" % (v & 0xFFFF)
            i -= base
            if ty == 6:
                return "%d,%d" % (i % 64, i // 64)
            x = sum((i >> (2 * b + 1) & 1) << b for b in range(5))
            y = sum((i >> (2 * b) & 1) << b for b in range(5))
            return f"{x},{y}" if i < w * h else f"+{i}"
        horiz = [dec(c["pix"][8 * 64 + x]) for x in range(0, 64, 3)]
        vert = [dec(c["pix"][y * 64 + 8]) for y in range(0, 32, 2)]
        print(f"  {name:14s} {sp['set']:8s} row y=8: " + " ".join(horiz))
        print(f"  {'':14s} {'':8s} col x=8: " + " ".join(vert))


# ------------------------------------------------------------------------------- D6: T3 bits
def d6_t3(cases):
    print("== D6. T3 and T0 bits in smp (Q078): decoded (column, row) of the strided texture, against the control")
    for name, c in sorted(cases.items()):
        sp = SPECS.get(name)
        if not sp or sp["group"] not in ("t3bits", "t3risky") or c["status"] != "ok":
            continue
        spec = sp["spec"]
        ex = {hl: pixel_agree(name, c, r) for hl, r in zip(sp["hyps"], sp["rules"])}
        ty = spec["t1"] >> 29
        dx, dy = collections.Counter(), collections.Counter()
        for y in range(32):
            for x in range(64):
                i = name_idx(c["pix"][y * 64 + x])
                if i is None:
                    dx["B"] += 1
                    continue
                if ty == 6:
                    X, Y = texel_of_stride(spec, x, y)
                    dx[(i % 64) - X] += 1
                    dy[(i // 64) - Y] += 1
        print(f"  {name:18s} exact pixels " + " ".join(f"{k} {v}" for k, v in ex.items())
              + ("; col-x %s row-y %s" % (dx.most_common(3), dy.most_common(3)) if dx or dy else ""))


def texel_of_stride(spec, x, y):
    w = (spec["t1"] >> 12 & 0xFFF) + 1
    h = (spec["t1"] & 0xFFF) + 1
    return min(x, w - 1), min(y, h - 1)


# ------------------------------------------------------------------------------- D7: types
def d7_types(cases):
    print("== D7. TEXTYPE and the third coordinate (Q113, Q114): each job against the 2D control of its type")
    ctl = {"ty0": cases.get("ty0-2d"), "ty6": cases.get("ty6-2d"), "ty3": cases.get("ty3-2d")}
    for name, c in sorted(cases.items()):
        sp = SPECS.get(name)
        if not sp or sp["group"] not in ("types", "types-risky") or c["status"] != "ok":
            continue
        t1 = sp["spec"]["t1"]
        key = f"ty{t1 >> 29}"
        ref = ctl.get(key) if sp["group"] == "types" else None
        d = ""
        if ref and ref["status"] == "ok":
            d = f"; differs from its 2D control at {sum(a != b for a, b in zip(ref['pix'], c['pix']))} of 2048"
        ex = pixel_agree(name, c, {"w3d": "ignore"})
        print(f"  {name:12s} {key} ignore-w exact {ex}{d}; distinct {len(set(c['pix']))}")
    for name in ("wsw-ty0", "wsw-ty3", "wsw-ty6"):
        c = cases.get(name)
        if c and c["status"] == "ok":
            col = [name_idx(c["pix"][y * 64 + 4]) for y in range(0, 32, 4)]
            print(f"  {name}: dword at x=4, rows 0,4..28 (the third coordinate 0 to 2): {col}")
    print("  indicator (a job whose image differs from its control, to run the follow-up on): "
          + (", ".join(n for n, c in sorted(cases.items())
                       if n.startswith(("ind-t", "ty6-3d", "ty0-3d", "ty3-3d")) and c["status"] == "ok"
                       and ctl_of(cases, n) and c["pix"] != ctl_of(cases, n)["pix"]) or "none"))


def ctl_of(cases, n):
    if n.startswith("ind-t"):
        return cases.get("ind-ctl")
    return cases.get("ty" + n[2] + "-2d") if n.startswith("ty") else None


# ------------------------------------------------------------------------------- D8: formats
def d8_formats(cases):
    print("== D8. formats 23 to 29 (Q050): names maps, block order and index bits, YUV")
    for name, c in sorted(cases.items()):
        sp = SPECS.get(name)
        if not sp or not sp["group"].startswith("formats") or c["status"] != "ok":
            continue
        if sp["group"] == "formats-names":
            cc = collections.Counter(c["pix"])
            print(f"  {name}: {len(cc)} distinct values; commonest " + " ".join("%08x x%d" % kv for kv in cc.most_common(3)))
        elif sp["group"].startswith("formats-yuv"):
            ex = pixel_agree(name, c, {})
            print(f"  {name}: exact pixels against the E037 model ({'csc' if sp['spec'].get('csc') else 'black'}) {ex}")
    for f in (23, 24, 27):
        d1 = {k: cases.get(f"fb-{f}-{k}") for k in ("base", "ordA", "ordB", "lo", "hi")}
        if not all(v and v["status"] == "ok" for v in d1.values()):
            continue
        img = lambda k: [[d1[k]["pix"][y * 64 + x] for x in range(16)] for y in range(16)]
        base, a, b = img("base"), img("ordA"), img("ordB")
        # blocks of bw x bh texels: the largest cell in which ordA is constant
        res = []
        for bw, bh in ((4, 4), (8, 4), (4, 8)):
            ok = all(len({a[y][x] for y in range(by, by + bh) for x in range(bx, bx + bw)}) == 1
                     for by in range(0, 16, bh) for bx in range(0, 16, bw))
            res.append(f"{bw}x{bh} cells constant {ok}")
        print(f"  format {f}: ordA {len({v for r in a for v in r})} distinct values; " + "; ".join(res))
        cell = lambda im, bx, by, bw=4, bh=4: im[by * bh][bx * bw]
        orders = {"raster": lambda i: (i % 4, i // 4), "morton-y0": lambda i: (sum((i >> (2 * k + 1) & 1) << k for k in range(2)),
                                                                                   sum((i >> (2 * k) & 1) << k for k in range(2))),
                  "morton-x0": lambda i: (sum((i >> (2 * k) & 1) << k for k in range(2)), sum((i >> (2 * k + 1) & 1) << k for k in range(2)))}
        okc = {}
        for on, fn in orders.items():
            ca = {fn(i): cell(a, *fn(i)) for i in range(16)}
            cb = {fn(i): cell(b, *fn(i)) for i in range(16)}
            # block i holds payload i in job A and sigma(i) = (5 i + 3) mod 16 in job B (an affine map,
            # which a permutation of the index bits, as raster and Morton are of each other, does not
            # respect: 15 - i would, and every such order would pass): in the right order the colour
            # of cell fn(i) in B is the colour that cell fn(sigma(i)) has in A
            okc[on] = sum(cb[fn(i)] == ca[fn((5 * i + 3) % 16)] for i in range(16))
            print(f"    order {on:10s}: cell(i) in B equals cell(sigma(i)) in A for {okc[on]} of 16 blocks")
        best = max(okc, key=okc.get)
        if okc[best] >= 14:
            fn = orders[best]
            for k in ("lo", "hi"):
                im = img(k)
                maps = []
                for i in range(16):
                    bx, by = fn(i)
                    maps.append([(x - 4 * bx, y - 4 * by) for y in range(4 * by, 4 * by + 4)
                                 for x in range(4 * bx, 4 * bx + 4) if im[y][x] != base[y][x]])
                one = sum(len(m) == 1 for m in maps)
                print(f"    {k} ({best}): {one} of 16 blocks change exactly one pixel; bit -> (dx, dy): "
                      + " ".join(f"{i}:{m[0][0]},{m[0][1]}" if len(m) == 1 else f"{i}:{len(m)}px" for i, m in enumerate(maps)))
        else:
            for k in ("lo", "hi"):
                diff = [(x, y) for y in range(16) for x in range(16) if img(k)[y][x] != base[y][x]]
                print(f"    {k}: {len(diff)} pixels differ from base (no block order fits); first {diff[:6]}")


# ------------------------------------------------------------------------------- D9: douti4
def d9_douti(cases):
    print("== D9. DOUTI0 with four components (Q021): the dword in pa2 to pa5, on a vertex set 0.25 and x + y")
    for name, c in sorted(cases.items()):
        if not name.startswith("tx-douti4"):
            continue
        if c["status"] != "ok":
            print(f"  {name}: {c['status']}")
            continue
        cc = collections.Counter(c["pix"])
        print(f"  {name}: {len(cc)} distinct; commonest " + " ".join("%08x x%d" % kv for kv in cc.most_common(3)))


# ------------------------------------------------------------------------------- raw for vectors
def write_raw(cases, out: pathlib.Path):
    """Campaign form: OUT/<table>/raw.txt (probe-case blocks and the tool's lines) and bins/, next to
    OUT/<table>.toml and OUT/tx_map.s, so that vectors.py convert finds them (doc/specs/vectors.md)."""
    import shutil
    out.mkdir(parents=True, exist_ok=True)
    shutil.copy(P / "templates" / "tx_map.s", out / "tx_map.s")
    groups = collections.defaultdict(list)
    for name, c in cases.items():
        sp = SPECS.get(name)
        if sp and c.get("status") == "ok":
            groups[sp["group"]].append((name, sp, c))
    for g, items in groups.items():
        d = out / f"tx-{g}"
        (d / "bins").mkdir(parents=True, exist_ok=True)
        shutil.copy(P / "probes" / "texture" / f"tx-{g}.toml", out / f"tx-{g}.toml")
        lines = []
        for name, sp, c in sorted(items, key=lambda t: int(re.search(r"__(\d+)", t[1]["bin"]).group(1))):
            b = sp["bin"]
            stem = b[:-4]
            shutil.copy(P / "stage-bins" / b, d / "bins" / b)
            lines += [f"probe-case {stem}", "programs asm", f"probe {stem}: scratch at 0x3e003000 (64 KiB)"]
            cc = collections.Counter(c["pix"])
            top = cc.most_common(4)
            if len(cc) == 1:
                lines.append(f"probe {stem}: o0 0x{top[0][0]:08x} (2048 of 2048)")
            else:
                lines.append(f"probe {stem}: o0 mixed " + " ".join(f"0x{v:08x} x{n}" for v, n in top)
                             + (f" other x{sum(cc.values()) - sum(n for _, n in top)}" if len(cc) > 4 else ""))
            for y in range(32):
                lines.append(f"probe {stem}: row {y}: " + " ".join(f"{v:08x}" for v in c["pix"][y * 64:(y + 1) * 64]))
            lines.append(f"probe {stem}: scratch unchanged")
        (d / "raw.txt").write_text("\n".join(lines) + "\n")
    print(f"== raw: {sum(len(v) for v in groups.values())} cases in {len(groups)} tables under {out}")


# ------------------------------------------------------------------------------- main
def main(argv):
    if "--selftest" in argv:
        import subprocess
        sys.exit(subprocess.call([sys.executable, "-B", str(P / "validate" / "selftest.py")] + argv[1:]))
    root = pathlib.Path(argv[0])
    cases = load_dir(root)
    pred, decl = load_declared()
    print(f"== A. inventory: {len(cases)} cases in {root}")
    by = collections.Counter((c["script"], c["status"]) for c in cases.values())
    for (s, st), n in sorted(by.items()):
        print(f"  {s:16s} {st:10s} {n}")
    extra = [n for n in cases if n not in decl]
    print(f"  cases not in declared.tsv: {len(extra)} {extra[:5]}")
    score(cases, pred)
    d1_twiddle(cases)
    d2_shapes(cases)
    d3_lod(cases)
    d4_afilt(cases)
    d5_border(cases)
    d6_t3(cases)
    d7_types(cases)
    d8_formats(cases)
    d9_douti(cases)
    if "--raw" in argv:
        write_raw(cases, pathlib.Path(argv[argv.index("--raw") + 1]))


if __name__ == "__main__":
    main(sys.argv[1:])
