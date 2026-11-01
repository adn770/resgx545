# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The 9b runs of phase 11.29 as hardware vectors (vectors/nokernel/usse/fwtask-9b/<run>.vec.json),
kind `firmware`: the program as run (our wrapper with the results address and the continue index
patched as the kernel patched them), the results page and registers that went in, the page and the
registers (as the host read them) that came out. The run ends at the wrapper's tail call: the closed
task it jumps to is not part of a vector.

    make_vectors.py RUN.jsonl BLOB RUNNAME OUTDIR
"""
import datetime
import hashlib
import json
import pathlib
import sys

import fwtask
import layout as L

RES = 0x32140000        # KERNEL_DATA heap base + 0x140000 (the results page)
CONT = {0: 6}           # the closed task the general slot started: E146 (index 6), a jump target only
KEEP = {"x0": 1, "x1": 2, "x10": 2}


def h8(v):
    return f"0x{v:08x}"


def convert(jsonl, blobname, runname):
    blob_bytes = fwtask.blob_of(blobname)
    blob = fwtask.parse_blob(blob_bytes)
    words = fwtask.apply_patches(blob.words, blob.patches, RES, CONT)
    vectors = []
    raw = pathlib.Path(jsonl)
    for i, line in enumerate(raw.read_text().splitlines()):
        r = json.loads(line)
        if not r["done"]:
            continue
        j = r["job"]
        n = j["n"]
        name, kind, _ = L.X9B[n]
        regs = {int(k): v for k, v in j["regs"].items()}
        init_mem = {1: n, 3: r["echo"], 8: j["params"]["8"], 9: j["params"]["9"]}
        for k in range(4):
            init_mem[L.slot(n) + k] = L.INITFILL
        keep = KEEP.get(kind, 1)
        if kind == "x11":           # CR_TIMER counts are not reproducible: seed t0, compare L only
            regs[0x0144] = r["slot"][1]
        out_mem = {1: 0, 2: L.DONE, 5: r["echo"]}
        for k in range(keep):
            out_mem[L.slot(n) + k] = r["slot"][k]
        vectors.append({
            "id": f"{blobname}__{name}__p{j['pair']}r{j['rep']}__{i}",
            "program": {"isa": "usse", "words": [f"0x{w:016x}" for w in words], "entry": 0,
                        "source": "recorded"},
            "init": {"task": "firmware",
                     "page": {"base": h8(RES), "dwords": L.PAGE_DWORDS},
                     "mem": {f"0x{k:03x}": h8(v) for k, v in sorted(init_mem.items())},
                     "regs": {f"0x{k:04x}": h8(v) for k, v in sorted(regs.items())},
                     "ends": "the wrapper's tail call (lapc): the closed task is not run"},
            "readback": {"failed": None,
                         "mem": {f"0x{k:03x}": h8(v) for k, v in sorted(out_mem.items())},
                         "regs": {f"0x{reg:04x}": h8(r["H"][hex(reg)]) for reg in (L.R1, L.R2)}},
            "provenance": {"probe": blobname, "case": name, "table": "firmware-tasks/" + runname,
                           "template": blobname + ".s", "blob_sha256": hashlib.sha256(blob_bytes).hexdigest(),
                           "params": j["params"], "pair": j["pair"], "repeat": j["rep"],
                           "question": "Q134"}})
    return {"format": "sgx545-vectors", "version": 1,
            "run": {"raw": f"firmware-tasks/{runname}/{raw.name}",
                    "raw_sha256": hashlib.sha256(raw.read_bytes()).hexdigest(),
                    "converted": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
                    "tool": "make_vectors.py 1"},
            "vectors": vectors, "orphans": []}


def main(argv):
    jsonl, blob, run, out = argv[1:5]
    f = convert(jsonl, blob, run)
    out = pathlib.Path(out)
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{run}.vec.json").write_text(json.dumps(f, indent=1) + "\n")
    print(f"{run}: {len(f['vectors'])} vectors")


if __name__ == "__main__":
    main(sys.argv)
