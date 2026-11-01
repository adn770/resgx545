#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Convert the usse/ runs of 11.23, 11.24, 11.25 and 11.27 to hardware vectors.

The converter of the tree (tools/usse-asm/vectors.py) is run on the raw readbacks and the programs
as the runs recorded them (bins/), with the probe tables of the tree. The vectors go to OUT in the
layout of doc/specs/vectors.md (OUT/usse/<feature>/<run>.vec.json); the data repository keeps them
as vectors/nokernel/. The features are the usse/ runs of the four phases that had no vectors
before 11.28 (FEATURES).

    convert_extra.py --tree TREE --data DATA --out OUT [FEATURE...]
"""
import argparse
import pathlib
import struct
import sys

FEATURES = [
    "callfalse", "callfalse2", "compare32", "compare32-pad", "compare32x", "emit-addend",
    "emit-addend2", "emitpds", "fence-batching", "fence-growth", "iaddu32-pairs", "ima32-forms",
    "ima32-full", "ima32-neg", "ima32hi", "ima32hi-generic", "ima32hi-signed", "imae-neg", "link",
    "load-readers", "pa-dest", "pclink", "pclink-repeat", "pflow", "phas-high-a", "phas-high-b",
    "phas-high-c", "phas-high-d", "phas-high-e", "phas-low", "phas-low2", "phas-mod", "place",
    "place-ctl", "place-ctl2", "place-link", "place-more", "place2", "raw25", "rawchan-1",
    "rawchan-2", "rawchan-3", "rawchan-4", "rawchan-5", "rawchan-6", "rawchan-7", "rawcond",
    "rawcond2", "rawjoin-o", "rawjoin-o2-and7", "rawjoin-o2-or", "rawjoin-o2-xor", "reload-growth",
    "repeat-ptrs", "risky", "rot-imm", "scmp", "store-own", "store-own2", "store-own3",
    "store-repeat", "store-repeat-regs", "store-repeat-regs2", "task-state", "temps-bound",
    "temps-bound2", "temps-bound3", "temps-max", "temps-past", "temps-sparse", "temps-wrap",
    "ucmp2", "ucmp2-pad", "ucmp2-random"
]

ap = argparse.ArgumentParser()
ap.add_argument("--tree", required=True)
ap.add_argument("--data", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("features", nargs="*", default=FEATURES)
a = ap.parse_args()
tree, data, out = map(pathlib.Path, (a.tree, a.data, a.out))
sys.path.insert(0, str(tree / "tools" / "usse-asm"))
import probe, vectors  # noqa: E402

base = probe.load()
total = 0
for feat in a.features:
    for raw in sorted((data / "usse" / feat).glob("*/raw.txt")):
        tbl, dirs = vectors.tables_for(raw, base)
        bins = raw.parent / "bins"
        batch = vectors.convert(raw.read_text(), tbl, raw_name=str(raw.relative_to(data)),
                                bins=bins if bins.is_dir() else None, dirs=dirs)
        # a program placed in the code heap (sgxfive-test --place OFFSET=FILE): the fill's own
        # program is a stub, the placed one (FILE under bins/) is what runs, so the vector
        # carries it: init.placed = {"offset": heap offset, "words": [...]}
        for v in batch["vectors"]:
            opts = v["provenance"].get("options") or []
            if "--place" in opts:
                off, _, name = opts[opts.index("--place") + 1].partition("=")
                blob = (bins / name).read_bytes()
                words = struct.unpack(f"<{len(blob) // 8}Q", blob)
                v["init"]["placed"] = {"offset": int(off), "words": [f"0x{w:016x}" for w in words]}
        dst = out / "usse" / feat / f"{raw.parent.name}.vec.json"
        dst.parent.mkdir(parents=True, exist_ok=True)
        vectors.dump(dst, batch)
        n = len(batch["vectors"])
        total += n
        print(f"{feat}/{raw.parent.name}: {n} vectors, {len(batch['orphans'])} orphans")
print("total", total)
