#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Render scene vectors with an image to reproduce (doc/specs/vectors.md section 6.7, 12.3).

    isp_scenes.py --data DATA --tool build/sgxfive-test --bins DIR --out OUT TABLE...

Tables: `first-triangle` (E023, E148, E174: the library's triangle on the sizes the records ran, each
with the recorded image hash), `arith` (a sample of the E606 and E607 depth jobs: the vertices of
`cases.tsv` with the recorded image hash and the dump of the depth they stored) and `inventory` (the
triangle-host vectors of the data repository: the recorded image of each, rebuilt from the
options of its `provenance`). The words are REBUILT (`sgxfive-test --mock probe --tri ... --emit-scene`):
the pixel program is the file the case names; nothing here is a capture of the closed driver.
One file per table, `OUT/isp/<table>.scene.json`.
"""
import argparse
import csv
import gzip
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ta_scenes  # noqa: E402

TOOL = "isp_scenes.py 1"
HASH = re.compile(r"target: (\d+)x(\d+) hash (0x[0-9a-f]+)")


def sparse(dwords):
    return ta_scenes.sparse(dwords)


def scene_words(s, regs=None):
    """The scene's fields common to every table: the rebuilt words of an `--emit-scene` file."""
    sc = {"kind": "render", "target": s["target"], "cmd": s["cmd"], "vertices": s["vertices"],
          "layout": s["layout"],
          "memory": [{"role": m["role"], "base": m["base"], "source": "rebuilt", "dwords": sparse(m["dwords"])}
                     for m in s["memory"]]}
    if regs:
        sc["regs"] = regs
    return sc


def hashes(path):
    """{(w, h): [hash of render 1, hash of render 2, ...]} of a target-sizes style output."""
    out = {}
    for m in HASH.finditer(pathlib.Path(path).read_text()):
        out.setdefault((int(m.group(1)), int(m.group(2))), []).append(m.group(3))
    return out


FIRST_SIZES = [(64, 64), (64, 128), (64, 144), (64, 160), (64, 192), (64, 256), (128, 64), (128, 128),
               (128, 144), (128, 256), (256, 64), (256, 128), (256, 256), (128, 96), (1024, 768), (4096, 4096)]
# E174's two large sizes: the hash of the first render of each (dpm/parameter-buffer baselines)
LARGE = {(1024, 768): ("dpm/parameter-buffer/pb-1024x768/raw.txt", "E174"),
         (4096, 4096): ("dpm/parameter-buffer/pb-4096x4096/raw.txt", "E174")}


# the targets E606 ran: only these are inside the envelope (r123 item 3)
E606_TARGETS = {(64, 64), (128, 128), (256, 128)}


def open_questions(w, h):
    """The questions open for a target of this size, from the size alone (never from a result): E606's
    sizes are 64 x 64, 128 x 128 and 256 x 128 (Q240); the TA's macrotile rule of four macrotiles
    a row from 640 x 480 pixels on was dumped for two only (Q139, Q100, Q086)."""
    q = []
    if (w, h) not in E606_TARGETS:
        q.append("Q240")
    if w * h >= 640 * 480:
        q += ["Q100", "Q139", "Q086"]
    return q


def plane_questions(v, z):
    """Questions open for the triangle itself, from its vertices (1/256 pixel) and depths: a triangle
    with no area has no winding mark in the TA's object (Q230); a depth plane of gradient 0.03 or more
    is compared with no known tolerance (Q200, E606); a vertex depth outside [0, 1] under a depth compare
    or a depth write is clamped on its way (E287, Q241)."""
    (x0, y0), (x1, y1), (x2, y2) = v
    area = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)
    if area == 0:
        return ["Q230"]
    z0, z1, z2 = z
    gx = ((z1 - z0) * (y2 - y0) - (z2 - z0) * (y1 - y0)) / area
    gy = ((z2 - z0) * (x1 - x0) - (z1 - z0) * (x2 - x0)) / area
    q = ["Q200"] if (abs(gx) + abs(gy)) * 256 >= 0.03 else []
    if any(not (0.0 <= d <= 1.0) for d in z):
        q.append("Q241")
    return q


def first_triangle(data, tool, bins):
    root = pathlib.Path(data)
    rec = hashes(root / "render/target-sizes/output.txt")
    rec.update({k: v for k, v in hashes(root / "render/client-jobs/output.txt").items() if k not in rec})
    for k, (rel, _) in LARGE.items():
        p = root / rel
        if p.exists():
            rec[k] = hashes(p).get(k, [])
    scenes, excluded = [], []
    for (w, h) in FIRST_SIZES:
        if (w, h) not in rec or not rec[(w, h)]:
            excluded.append({"case": f"{w}x{h}", "why": "no recorded image hash"})
            continue
        cmd = ["probe", "--tri", "pixel", "--width", str(w), "--height", str(h), "--temps", "32",
               str(bins / "pix_green.bin")]
        sc = scene_words(ta_scenes.emit([str(tool)], cmd))
        sc.update({"id": f"first-triangle/{w}x{h}",
                   "expect": {"image": {"hash": rec[(w, h)][0]}, "outside": 0, "refuse": open_questions(w, h)},
                   "provenance": {"probe": "first-triangle", "table": "first-triangle", "rebuilt": True,
                                  "options": cmd[:-1], "records": ["E023", "E148", "E174"],
                                  "hash_of": "the first render of the run's output (colours 0xff00ff00 on 0xff203040)"}})
        scenes.append(sc)
    return scenes, excluded


def read_gz_text(p):
    return gzip.open(p).read().decode("utf-8", "replace")


def arith(data, tool, bins, step):
    root = pathlib.Path(data) / "isp/arith-1138"
    scenes, excluded = [], []
    for tsv, d in (("cases.tsv", "main"), ("cases-fine.tsv", "fine"), ("cases-fine2.tsv", "fine2")):
        rows = [r for r in csv.reader(open(root / tsv), delimiter="\t") if len(r) >= 16]
        for n, r in enumerate(rows):
            if "D" not in r[15] or n % step:
                continue
            cid, w, h = r[0], int(r[3]), int(r[4])
            unit = int(r[16]) if len(r) > 16 else 8
            if unit != 8:
                excluded.append({"case": cid, "why": "--tri-unit scenes are checked at the unit level only"})
                continue
            txt = read_gz_text(root / d / "D" / f"{cid}.txt.gz")
            m = HASH.search(txt)
            if not m:
                excluded.append({"case": cid, "why": "no hash in the recorded output"})
                continue
            g = max(1, (w + 31) // 32 - 1)
            cmd = ["probe", "--tri", "pixel", "--width", str(w), "--height", str(h), "--temps", "32",
                   "--tri-v", ",".join(r[5:11]), "--tri-z", ",".join(r[11:14]), "--blk", "1=0x00400200",
                   str(bins / "pix_green.bin")]
            try:
                s = ta_scenes.emit([str(tool)], cmd)
            except RuntimeError as e:
                excluded.append({"case": cid, "why": str(e)[:120]})
                continue
            sc = scene_words(s, regs={"0x0480": f"{0x17100c & ~(0x1ff << 3) | g << 3:#x}", "0x0488": "0x3e001000"})
            sc.update({"id": f"arith/{d}/{cid}",
                       "expect": {"image": {"hash": m.group(3)}, "outside": 0, "refuse": open_questions(w, h) + plane_questions(
                           [(int(r[5 + 2 * i]), int(r[6 + 2 * i])) for i in range(3)], [float(x) for x in r[11:14]])},
                       "provenance": {"probe": "arith-1138", "case": cid, "table": tsv, "class": r[2], "set": r[1],
                                      "rebuilt": True, "options": cmd[:-1], "records": ["E606", "E607", "E465"],
                                      "depth": {"file": f"isp/arith-1138/{d}/D/{cid}.depth.gz", "g": g}}})
            scenes.append(sc)
    return scenes, excluded


def fnv64(words):
    h = 0xcbf29ce484222325
    for w in words:
        for b in int(w, 16).to_bytes(4, "little"):
            h = ((h ^ b) * 0x100000001b3) & 0xffffffffffffffff
    return f"{h:#x}"


NOT_REBUILT = ("--kpoke", "--kpoke-render")


def inventory(data, tool, out_dir, only=None):
    """One scene file per vector file with triangle-host vectors (`--tri` in `provenance.options`): the
    scene rebuilt from the options and the programs of the run's `bins/`, the recorded image of the
    vector as its expectation (a hung or faulted job as `outcome`). A vector the tool cannot rebuild, a
    kernel poke or a job without an image is listed as excluded with the reason. Returns the counts."""
    root = pathlib.Path(data)
    counts = {}
    for f in sorted((root / "vectors").rglob("*.vec.json")):
        rel = f.relative_to(root / "vectors")
        if only and not str(rel).startswith(only):
            continue
        doc = json.load(open(f))
        scenes, excluded = [], []
        for v in doc["vectors"]:
            o = v.get("provenance", {}).get("options", [])
            if "--tri" not in o:
                continue
            rb = v.get("readback", {})
            run_dir = (root / doc["run"]["raw"]).parent
            if any(k in o for k in NOT_REBUILT):
                excluded.append({"case": v["id"], "why": "a kernel poke: the words are not in the tool's pages"})
                continue
            failed = rb.get("failed")
            if rb.get("pixels"):
                expect = {"image": {"hash": fnv64(rb["pixels"])}}
            elif rb.get("mixed"):
                expect = {"image": {"mixed": rb["mixed"]}}
            elif failed and "hung" in failed:
                expect = {"outcome": "hang"}
            elif failed and "faulted" in failed:
                expect = {"outcome": "fault"}
            else:
                excluded.append({"case": v["id"], "why": f"no image to compare with ({failed})"})
                continue
            cmd, i = ["probe"], 0
            while i < len(o):
                a = o[i]
                if a == "--dump-render":      # an output option: the scene is the same
                    i += 2
                    continue
                if a == "--slot":
                    name, _, fn = o[i + 1].partition("=")
                    cmd += [a, f"{name}={run_dir / 'bins' / fn}"]
                    i += 2
                    continue
                cmd.append(a)
                i += 1
            prog = run_dir / "bins" / f"{v['id']}.bin"
            if not prog.exists():
                excluded.append({"case": v["id"], "why": "no program file in the run's bins"})
                continue
            try:
                s = ta_scenes.emit([str(tool)], cmd + [str(prog)])
            except RuntimeError as e:
                excluded.append({"case": v["id"], "why": "the tool refused: " + str(e)[:100].replace("\n", " ")})
                continue
            sc = scene_words(s)
            sc.update({"id": f"inventory/{rel}/{v['id']}", "expect": expect,
                       "provenance": {"probe": v["provenance"].get("probe"), "table": str(rel), "rebuilt": True,
                                      "options": o, "recorded": "readback of the vector"}})
            scenes.append(sc)
        if scenes or excluded:
            out = pathlib.Path(out_dir) / "inventory" / str(rel).replace(".vec.json", ".scene.json")
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps({"format": "sgx545-scene-vectors", "version": 1,
                                       "run": {"tool": TOOL, "table": str(rel), "excluded": excluded},
                                       "scenes": scenes}) + "\n")
            counts[str(rel)] = (len(scenes), len(excluded))
    return counts


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--tool", required=True)
    ap.add_argument("--bins", required=True, help="the staged programs (pix_green.bin, ...)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--step", type=int, default=8, help="every STEPth case of the arith table")
    ap.add_argument("--only", default=None, help="inventory: only the vector files whose path starts so")
    ap.add_argument("table", nargs="+")
    a = ap.parse_args(argv)
    bins = pathlib.Path(a.bins)
    for t in a.table:
        if t == "first-triangle":
            scenes, excluded = first_triangle(a.data, a.tool, bins)
        elif t == "arith":
            scenes, excluded = arith(a.data, a.tool, bins, a.step)
        elif t == "inventory":
            c = inventory(a.data, a.tool, pathlib.Path(a.out) / "inv", a.only)
            print(f"inventory: {len(c)} files, {sum(x[0] for x in c.values())} scenes, {sum(x[1] for x in c.values())} excluded")
            continue
        else:
            sys.exit(f"unknown table {t}")
        doc = {"format": "sgx545-scene-vectors", "version": 1,
               "run": {"tool": TOOL, "table": t, "excluded": excluded}, "scenes": scenes}
        out = pathlib.Path(a.out) / "isp" / (t + ".scene.json")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(doc, indent=1) + "\n")
        print(f"{out}: {len(scenes)} scenes, {len(excluded)} excluded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
