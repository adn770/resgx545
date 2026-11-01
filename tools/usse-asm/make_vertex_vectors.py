#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Vertex-task vectors from the kept dumps of the 11.33 runs usse/globals-vertex-eot (q053-vtx at
8 vertices a task, q053-vtx2 at 4 and 6): per job one vector whose program is the job's moves
(oN <- gR, as the job's vertex program ran them) and whose readback is the vertex words of the job's
parameter buffer.

A vertex is the 12 dwords that end at a dword equal to the job's marker constant (o14, 0x3f0000NN,
distinct per job); the vertices in ascending address order are the draw's sequence. Words 3 to 10 are
o6 to o13, the 8 registers of the job's group, word 11 the marker. Vertex 67 is cut by the 4 KiB
boundary at 0x2000 (its first 9 dwords, below it, read 0 in all 12 jobs): it is named in init.skip and
not compared. The registers not modelled (g18, g21 and g19, which reads by the instruction, E372) are
left out of the program.

    make_vertex_vectors.py --data DATA --out OUT [--asm usse-asm]

OUT is vectors/nokernel/usse/globals-vertex of the data repository; the run names the dumps it was
made from with their sha256.
"""
import argparse
import gzip
import hashlib
import json
import pathlib
import re
import struct
import subprocess
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
GROUPS = {"A": [16, 17, 18, 19, 20, 21, 22, 23], "B": [24, 25, 26, 27, 28, 29, 30, 31],
          "C": [39, 40, 41, 42, 43, 17, 18, 19]}
NOT_MODELLED = (18, 19, 21)
SCRIPTS = {"q053-vtx": None, "q053-vtx2": {"f3": 4, "f5": 6}}
RAW = "usse/globals-vertex-eot/dumps"
VERTICES = 126


def jobs(data, script):
    """(name, marker, group, vertices a task) of each job of a script, from its case table."""
    out = []
    for line in (data / RAW / script / "cases.tsv").read_text().splitlines()[1:]:
        name, args = line.split("\t")[0], line.split("\t")[-1]
        n = int(re.search(r"-m(\d+)\.bin", args).group(1))
        group = name[-2] if name[-1].isdigit() else name[-1]
        per = 8 if SCRIPTS[script] is None else SCRIPTS[script][re.search(r"-(f\d)-", name).group(1)]
        out.append((name, 0x3F000000 + n, group, per))
    return out


def vertices(dump, marker):
    """The vertices of a parameter buffer dump, 12 dwords each, in address order."""
    words = struct.unpack(f"<{len(dump) // 4}I", dump)
    return [words[i - 11:i + 1] for i, w in enumerate(words) if w == marker]


def readable(v):
    """A vertex whose position dwords read 0 lies across the unwritten page boundary."""
    return any(v[:3])


def assemble(text, asm):
    with tempfile.TemporaryDirectory() as d:
        out = pathlib.Path(d) / "p.bin"
        r = subprocess.run([str(asm), "-o", str(out), "-"], input=text, capture_output=True, text=True)
        if r.returncode:
            raise SystemExit(r.stderr)
        blob = out.read_bytes()
    return [f"0x{w:016x}" for w in struct.unpack(f"<{len(blob) // 8}Q", blob)]


def vector(data, script, job, asm):
    name, marker, group, per = job
    dump = (data / RAW / script / f"{name}.param.bin.gz")
    vs = vertices(gzip.open(dump).read(), marker)
    assert len(vs) == VERTICES, f"{name}: {len(vs)} vertices"
    regs = GROUPS[group]
    keep = [i for i, g in enumerate(regs) if g not in NOT_MODELLED]
    text = "phas #0, #0, pixel, end, parallel\n"
    text += "".join(f"mov.skipinv o{6 + i}, g{regs[i]}\n" for i in keep)
    text += f"mov.skipinv.end o14, #0x{marker:08X}\n"
    outs = [6 + i for i in keep] + [14]
    return {"id": name,
            "program": {"isa": "usse", "entry": 0, "source": "rebuilt", "words": assemble(text, asm)},
            "init": {"task": "vertex", "instances": VERTICES, "per": per, "temps": 32,
                     "skip": [k for k, v in enumerate(vs) if not readable(v)],
                     "outputs": [f"o{o}" for o in outs]},
            "readback": {"vertices": [[f"0x{v[o - 3]:08x}" for o in outs] for v in vs]},
            "note": f"the vertex words of the job {name} in its parameter buffer; the program is the "
                    "job's moves only"}, str(dump.relative_to(data))


def make(data, out, asm):
    out.mkdir(parents=True, exist_ok=True)
    for script in SCRIPTS:
        vecs, raws = [], []
        for job in jobs(data, script):
            v, raw = vector(data, script, job, asm)
            vecs.append(v)
            raws.append(raw)
        shas = [hashlib.sha256((data / r).read_bytes()).hexdigest() for r in raws]
        doc = {"format": "sgx545-vectors", "version": 1,
               "run": {"raw": raws, "raw_sha256": shas, "tool": "make_vertex_vectors.py 1"},
               "vectors": vecs, "orphans": []}
        (out / f"{script}.vec.json").write_text(json.dumps(doc, indent=1) + "\n")
        print(f"{script}: {len(vecs)} vectors")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, type=pathlib.Path)
    ap.add_argument("--out", required=True, type=pathlib.Path)
    ap.add_argument("--asm", default=HERE / "usse-asm", type=pathlib.Path)
    a = ap.parse_args()
    make(a.data, a.out, a.asm)
