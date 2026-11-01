#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Run the hardware instruction vectors (the data repository's vectors/) under the radare2 fork's ESIL.

Each one-instance USSE vector (doc/specs/vectors.md) is a program and what the hardware
left: o0 and the scratch dwords it stored. Here the program runs under r2's emulation instead of
the simulator (crates/sgx-sim), in the same environment: the scratch buffer at 0x3e003000
filled with 0xd0000000 | i, and a limm of 0x5cafnnnn loading its address + nnnn. A program with
a word that changes registers but has no ESIL is not run (r2 would step over it): it counts as
"no ESIL" under that word's mnemonic. The others must match the hardware.

    esil_vectors.py [--only MNEMONIC[,MNEMONIC...]] [--show] [FILE.vec.json...]

Without files, every vector file of the data repository ($RESGX545_DATA, or resgx545-data
beside this tree); the simulator's skip list (crates/sgx-sim/src/vectors.rs) applies, and so does the simulator's exclusion of the
triangle-host runs (`--tri`), which read back the scene, not the shader. --only
keeps the vectors that use one of the mnemonics; --show prints each mismatch. Needs the fork's
install (R2_PREFIX, or its prefix beside the repository).
"""
from __future__ import annotations

import argparse
import atexit
import collections
import json
import os
import pathlib
import re
import shutil
import struct
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[3]


def data_dir() -> pathlib.Path | None:
    """The vectors directory of the data repository ($RESGX545_DATA, else resgx545-data
    beside this tree, as crates/sgx-sim and tools/records/datasets.py find it), or None."""
    env = os.environ.get("RESGX545_DATA")
    d = (pathlib.Path(env) if env else ROOT.parent / "resgx545-data") / "vectors"
    return d if d.is_dir() else None


DATA = data_dir()
# the radare2 fork's install: R2_PREFIX, or its prefix beside the repository
PREFIX = pathlib.Path(os.environ.get("R2_PREFIX", ROOT.parent / "radare2-prefix"))
SCRATCH, DWORDS = 0x3E003000, 0x4000
LIMM_MASK, LIMM_VAL = 0xFF30_0000_0000_0000, 0xFC20_0000_0000_0000
# no effect on the registers ESIL models (waits, flushes, scheduling, emits)
NO_EFFECT = {"wdf", "idf", "nop", "smlsi", "phas", "ci", "cfi", "emitpds", "lock", "release",
             "emitpix1", "emitpix2"}


def skip_list() -> list[tuple[str, str]]:
    """The (raw prefix, probe or id, reason) rows of vectors::SKIP in crates/sgx-sim/src/
    vectors.rs: the probes whose readback the recorded program cannot reproduce. An empty
    probe matches every vector under the prefix."""
    src = (ROOT / "crates" / "sgx-sim" / "src" / "vectors.rs").read_text()
    block = src[src.index("pub const SKIP"):]
    block = block[:block.index("];")]
    return re.findall(r'\("([^"]*)", "([^"]*)", "([^"]*)"\)', block)


def skipped(skip: list[tuple[str, str, str]], raw: str, probe: str, vid: str) -> bool:
    """vectors::skipped: a row matches by probe or id (any, when empty) and raw prefix."""
    return any((not p or p in (probe, vid)) and raw.startswith(r) for r, p, _ in skip)


def runnable(v: dict, raw: str, skip: list[tuple[str, str, str]]) -> bool:
    """Whether the simulator's tests compare this vector (vectors::kind and SKIP): a USSE
    vector of a one-instance run that read back o0, whose job did not fail, that is not on the
    skip list and did not run on the triangle host (its readback is the scene's, not the
    shader's)."""
    rb, prov = v["readback"], v.get("provenance", {})
    if skipped(skip, raw, prov.get("probe", ""), v.get("id", "")):
        return False
    if "--tri" in prov.get("options", []):
        return False
    return not (v["program"].get("isa") != "usse" or rb.get("failed") or rb.get("o0") is None
                or v["init"].get("pa0") == "coords")


def has_end(disasm: str) -> bool:
    """Whether an instruction's text carries the `end` modifier in any position of its
    mnemonic: `mov.end`, `mov.skipinv.end`, `p0 mov.end`."""
    return any("end" in tok.split(".")[1:] for tok in disasm.split()[:2])


def limm_get(w: int) -> int:
    return (w & 0x1FFFFF) | (w >> 36 & 0x1F) << 21 | (w >> 44 & 0x3F) << 26


def limm_put(w: int, v: int) -> int:
    w &= ~(0x1FFFFF | 0x1F << 36 | 0x3F << 44)
    return w | (v & 0x1FFFFF) | (v >> 21 & 0x1F) << 36 | (v >> 26 & 0x3F) << 44


def patch_scratch(w: int) -> int:
    """sgxfive-test's patch (crates/sgx-sim/src/vectors.rs)."""
    imm = limm_get(w)
    if w & LIMM_MASK == LIMM_VAL and imm & ~0xFFFF == 0x5CAF0000:
        return limm_put(w, SCRATCH + (imm & 0xFFFF))
    return w


def base_mnemonic(text: str) -> str:
    toks = text.split()
    t = toks[0] if toks else "?"
    if (re.fullmatch(r"!?p[0-3]", t) or t == "Pn") and len(toks) > 1:
        t = toks[1]
    return t.split(".")[0]


class R2:
    def __init__(self, prefix: str):
        self.bin = pathlib.Path(prefix) / "bin" / "r2"
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        atexit.register(shutil.rmtree, self.tmp, ignore_errors=True)
        self.fill = self.tmp / "scratch.bin"
        self.fill.write_bytes(b"".join(struct.pack("<I", 0xD0000000 | i) for i in range(DWORDS)))

    def run(self, cmds: list[str], prog: pathlib.Path) -> str:
        return subprocess.run([str(self.bin), "-q", "-a", "usse", "-b", "32", "-e", "scr.color=0",
                               "-e", "io.cache=true", *sum((["-c", c] for c in cmds), []),
                               str(prog)], capture_output=True, text=True, timeout=60).stdout

    def ops(self, prog: pathlib.Path, n: int) -> list[dict]:
        out = self.run([f"aoj {n}"], prog)
        return json.loads(out[out.index("["):]) if "[" in out else []

    def emulate(self, prog: pathlib.Path, end: int, offsets: list[int]) -> tuple[int, dict[int, int]]:
        cmds = [f"on {self.fill} 0x{SCRATCH:x}", "aei", "aeim", "ar pc=0", "e esil.maxsteps=20000",
                f"aesu 0x{end:x}", "ar o0"]
        cmds += [f"pv4 @ 0x{SCRATCH + o:x}" for o in offsets]
        out = self.run(cmds, prog).split()
        vals = [int(x, 16) for x in out[-(1 + len(offsets)):]]
        return vals[0], dict(zip(offsets, vals[1:]))


def files() -> list[pathlib.Path]:
    return sorted(DATA.rglob("*.vec.json")) if DATA else []


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("files", nargs="*", type=pathlib.Path)
    ap.add_argument("--only", default="")
    ap.add_argument("--show", action="store_true")
    a = ap.parse_args(argv)
    if not (PREFIX / "bin" / "r2").exists():
        print(f"no radare2 at {PREFIX}: set R2_PREFIX to an install of the fork", file=sys.stderr)
        return 2
    if not (a.files or DATA):
        print("skip: no resgx545-data/vectors (set RESGX545_DATA or place it beside the tree)",
              file=sys.stderr)
        return 0
    only = {m for m in a.only.split(",") if m}
    r2 = R2(str(PREFIX))
    sys.path.insert(0, str(ROOT / "crates" / "pysgx"))
    import load                                     # the decoder in-process, to filter fast
    pysgx = load.pysgx()
    tally: dict[str, list[int]] = collections.defaultdict(lambda: [0, 0, 0])  # match, mismatch, no ESIL
    shown, dropped, skip = 0, 0, skip_list()
    for f in a.files or files():
        with open(f) as fh:
            d = json.load(fh)
        raw = d.get("run", {}).get("raw", "")
        for v in d["vectors"]:
            rb = v["readback"]
            if not runnable(v, raw, skip):
                continue
            words = [patch_scratch(int(w, 16)) for w in v["program"]["words"]]
            if only and not {base_mnemonic(pysgx.usse_decode(w)) for w in words} & only:
                continue
            prog = r2.tmp / "p.bin"
            prog.write_bytes(b"".join(struct.pack("<Q", w) for w in words))
            ops = r2.ops(prog, len(words))
            mns = {base_mnemonic(o.get("disasm", "?")) for o in ops}
            if only and not mns & only:
                continue
            lacking = sorted({base_mnemonic(o["disasm"]) for o in ops
                              if not o.get("esil") and base_mnemonic(o["disasm"]) not in NO_EFFECT})
            key = sorted(mns & only) if only else sorted(mns - NO_EFFECT - {"mov", "and", "or"})
            if lacking:
                for m in lacking:
                    tally[m][2] += 1
                continue
            ends = [i for i, o in enumerate(ops) if has_end(o.get("disasm", ""))]
            if not ends:
                dropped += 1
                continue
            offs = sorted(int(k, 16) for k in rb.get("scratch", {}))
            o0, got = r2.emulate(prog, 8 * (ends[0] + 1), offs)
            ok = o0 == int(rb["o0"], 16) and all(got[o] == int(rb["scratch"][f"0x{o:03x}"], 16)
                                                 for o in offs)
            for m in key or ["(other)"]:
                tally[m][0 if ok else 1] += 1
            if not ok and a.show and shown < 20:
                shown += 1
                print(f"{v['id']}: o0 r2 0x{o0:08x} hw {rb['o0']}")
    print(f"{'mnemonic':14s} {'match':>7s} {'mismatch':>9s} {'no ESIL':>8s}")
    for m, (ok, bad, none) in sorted(tally.items(), key=lambda x: (-x[1][2], x[0])):
        print(f"{m:14s} {ok:7d} {bad:9d} {none:8d}")
    if dropped:
        print(f"{dropped} vectors without an `end` instruction were not run")
    return 1 if any(t[1] for t in tally.values()) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
