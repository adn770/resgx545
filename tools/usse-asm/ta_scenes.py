#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Render scene vectors (doc/specs/vectors.md section 6) of the dumped triangle jobs of the ta tables.

A `--tri` probe of a ta table ran once per case on the laptop and saved the render's parameter
buffer and TA data (`--dump-render`, gzipped in the data repository). This tool rebuilds each case's
words offline (`sgxfive-test --mock probe --tri ... --emit-scene`, no laptop), checks them against
the dump they belong to (the TA copies the state block's pixel PDS words and ISP words into the
object unchanged: E306, E178) and pairs them with the dump as `expect.buffers`:

    ta_scenes.py --data DATA --tool build/sgxfive-test --out OUT [--table tri-region]

One file per table, `OUT/ta/<table>.scene.json`. The words are REBUILT (the builder's, not a
capture); the probe's pixel program is a placeholder (the TA does not read it), so a job whose
vertex program or PDS data a `--slot` replaced is listed as excluded, not built. A case whose rebuilt
header words differ from its dump is excluded and listed.
"""
import argparse
import csv
import gzip
import hashlib
import json
import os
import pathlib
import shlex
import struct
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
TOOL = "ta_scenes.py 1"
PB_BASE = 0x1000          # the parameter slot offset of a param dump's first byte (pbdump.py)
PB_WINDOW = (0x1000, 0x6000)   # the pages the TA writes for the targets of these tables
TA_WINDOW_BASE = 0x4000   # where the region headers start in a TA data dump
RECORDS = ["E176", "E177", "E180", "E306", "E541", "E542"]


def probe_command(args, placeholder):
    """(the sgxfive-test arguments, the options that matter) of a case's recorded command line."""
    t = shlex.split(args)
    cmd, opts, i = [], {"w": 64, "h": 64, "vertices": 3, "blk": {}, "slots": []}, 0
    while i < len(t):
        a = t[i]
        if a in ("--dump-render", "--kpoke", "--kpoke-render") and i + 1 < len(t):
            i += 2
            continue
        if a == "--pixels":
            i += 1
            continue
        if a in ("--obj2-pixel", "--obj2-pixpds") and i + 1 < len(t):
            cmd += [a, placeholder if a == "--obj2-pixel" else t[i + 1]]   # not part of the TA's input
            i += 2
            continue
        if a == "--width":
            opts["w"] = int(t[i + 1], 0)
        elif a == "--height":
            opts["h"] = int(t[i + 1], 0)
        elif a == "--vertices":
            opts["vertices"] = int(t[i + 1], 0)
        elif a == "--blk" and "^=" not in t[i + 1]:
            k, v = t[i + 1].split("=")
            opts["blk"][int(k)] = int(v, 0)
        elif a == "--slot":
            opts["slots"].append(t[i + 1].split("=")[0])
        cmd.append(a)
        i += 1
    cmd[-1] = placeholder                      # the recorded program file of the laptop
    return cmd, opts


def probe_of_toml(probe, placeholder):
    """(the sgxfive-test arguments, the options) of a probe of a probes/ta table: host tri, the pixel
    slot, a size, `vertices` and `blk` words. Another knob (`slots`, `vtx_coords`, `vdm`, `cmd`,
    `kpoke`) puts its name in `slots`: the job is not built."""
    w, h = probe["size"]
    opts = {"w": w, "h": h, "vertices": probe.get("vertices", 3), "blk": {}, "slots": []}
    cmd = ["probe", "--tri", probe["slot"], "--width", str(w), "--height", str(h)]
    if "vertices" in probe:
        cmd += ["--vertices", str(probe["vertices"])]
    for k, v in probe.get("blk", {}).items():
        opts["blk"][int(k)] = v
        cmd += ["--blk", f"{int(k)}={v:#x}"]
    opts["slots"] += [k for k in ("slots", "vtx_coords", "vdm", "cmd", "kpoke", "isp2", "obj2") if k in probe]
    return cmd + [placeholder], opts


def window_words(buf, lo, base, hi):
    """({address: value} of the non-zero dwords at addresses [lo, hi), how many lie outside)."""
    n = len(buf) // 4
    ws = struct.unpack(f"<{n}I", buf[:4 * n])
    inside, outside = {}, 0
    for i, w in enumerate(ws):
        if not w:
            continue
        a = base + 4 * i
        if lo <= a < hi:
            inside[f"{a:#x}"] = f"{w:#x}"
        else:
            outside += 1
    return inside, outside


def check_header(blk, dump_words):
    """None when the dump's object starts with the state block's pixel PDS words (E306); else why
    not. Three words, the same in every job: a consistency check of the rebuilt state block, not
    of the vertices, the viewport or the indices."""
    if not any(PB_BASE + 4 * k in dump_words for k in range(3)):
        return None      # no object in the dump (culled): nothing to compare the rebuilt words with
    for k in range(3):
        if dump_words.get(PB_BASE + 4 * k) != blk[3 + k]:
            return f"object word {k} is {dump_words.get(PB_BASE + 4 * k)}, the rebuilt block has {blk[3 + k]:#x}"
    return None


def read_gz(path):
    return gzip.open(path).read()


def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def sparse(dwords):
    n = len(dwords)
    while n and dwords[n - 1] == "0x0":
        n -= 1
    return dwords[:n]


def emit(tool, cmd):
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "s.json")
        # the options come before the program files
        r = subprocess.run([*tool, "--mock", *cmd[:-1], "--emit-scene", out, cmd[-1]],
                           capture_output=True, text=True, timeout=120)
        if not os.path.exists(out):
            raise RuntimeError(f"{cmd}: {r.stdout[-200:]}{r.stderr[-200:]}")
        return json.load(open(out))


def scene_of(tool, cmd, opts, name, table, probe, setname, options, param_p, tad_p, root, param, tad):
    """The scene of one case: rebuilt words and the dump's windows, or (None, why)."""
    s = emit(tool, cmd)
    mem = {m["role"]: m for m in s["memory"]}
    blk = [int(w, 16) for w in mem["pdsv"]["dwords"][0x100 // 4:0x100 // 4 + 18]]
    pb, pb_out = window_words(param, PB_WINDOW[0], PB_BASE, PB_WINDOW[1])
    ta, ta_out = window_words(tad, TA_WINDOW_BASE, 0, TA_WINDOW_BASE + 0x1000)
    words = {int(k, 16): int(v, 16) for k, v in pb.items()}
    why = check_header(blk, words)
    if why:
        return None, why
    return {
        "id": f"{table}/{name}", "kind": "render",
        "target": s["target"], "cmd": s["cmd"], "vertices": s["vertices"], "layout": s["layout"],
        "memory": [{"role": m["role"], "base": m["base"], "source": "rebuilt", "dwords": sparse(m["dwords"])}
                   for m in s["memory"]],
        "expect": {"buffers": {
            "param": {"sparse": pb, "window": [[f"{PB_WINDOW[0]:#x}", f"{PB_WINDOW[1]:#x}"]]},
            "tadata": {"sparse": ta, "window": [[f"{TA_WINDOW_BASE:#x}", f"{TA_WINDOW_BASE + 0x1000:#x}"]]}}},
        "provenance": {
            "probe": probe, "case": name, "table": table, "set": setname, "options": options,
            "rebuilt": True, "header_checked": any(PB_BASE + 4 * k in words for k in range(3)),
            "raw": [str(param_p.relative_to(root)), str(tad_p.relative_to(root))],
            "raw_sha256": [sha(param_p), sha(tad_p)],
            "outside_window_nonzero": {"param": pb_out, "tadata": ta_out},
            "records": RECORDS, "questions": []}}, None


def read_any(path):
    return read_gz(path) if str(path).endswith(".gz") else pathlib.Path(path).read_bytes()


def build(data, tool, table, placeholder):
    """A table with a cases.tsv (the p1131 tables), or a probes/ta/<table>.toml one (the older ones)."""
    root = pathlib.Path(data)
    scenes, excluded = [], []
    area, _, name_ = table.partition("/") if "/" in table else ("ta", "", table)
    table = name_ if "/" in (table or "") else table
    tsv = root / area / table / "cases.tsv"
    if tsv.exists():
        items = []
        for r in csv.DictReader(open(tsv), delimiter="\t"):
            p = root / area / table / "dumps" / r["script"] / f"{r['name']}.param.bin.gz"
            cmd, opts = probe_command(r["args"], placeholder)
            if "--tri" not in cmd or cmd[cmd.index("--tri") + 1] != "pixel":
                opts["slots"].append("pixel-slot")
            items.append((r["name"], r["script"], r["set"], r["args"].split(" /home/")[0], p, cmd, opts))
    else:
        import tomllib
        toml = HERE / ".." / ".." / "probes" / area / f"{table}.toml"
        items = []
        for pr in tomllib.load(open(toml, "rb")).get("probe", []):
            p = root / area / table / pr["name"] / "dumps" / f"{pr['name']}__0.param.bin"
            cmd, opts = probe_of_toml(pr, placeholder)
            items.append((pr["name"], pr["name"], "", " ".join(cmd[:-1]), p, cmd, opts))
    for name, probe, setname, options, param_p, cmd, opts in items:
        tad_p = pathlib.Path(str(param_p).replace(".param.bin", ".tadata.bin"))
        if not param_p.exists():
            excluded.append({"case": name, "why": "no dump"})
        elif opts["slots"]:
            excluded.append({"case": name, "why": "a replaced program or knob the scene builder cannot rebuild: " + ",".join(opts["slots"])})
        else:
            sc, why = scene_of(tool, cmd, opts, name, table, probe, setname, options, param_p, tad_p, root,
                               read_any(param_p), read_any(tad_p))
            if sc:
                scenes.append(sc)
            else:
                excluded.append({"case": name, "why": why})
    return {"format": "sgx545-scene-vectors", "version": 1,
            "run": {"tool": TOOL, "table": f"{area}/{table}", "excluded": excluded}, "scenes": scenes}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--tool", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--table", action="append")
    a = ap.parse_args(argv)
    with tempfile.TemporaryDirectory() as d:
        ph = os.path.join(d, "pix.bin")
        pathlib.Path(ph).write_bytes(bytes(8))
        for t in a.table or ["tri-region", "regions"]:
            doc = build(a.data, [a.tool], t, ph)
            out = pathlib.Path(a.out) / "ta" / (t.replace("/", "-") + ".scene.json")
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(doc, indent=1) + "\n")
            print(f"{out}: {len(doc['scenes'])} scenes, {len(doc['run']['excluded'])} excluded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
