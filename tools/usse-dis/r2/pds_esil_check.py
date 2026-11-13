#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Check the radare2 fork's PDS ESIL against the simulator (crates/sgx-sim, `sgx-sim --pds`).

A PDS program runs twice: in the simulator, whose semantics are doc/specs/pds_isa.md's and
are held to the hardware vectors, and under r2's ESIL (`aesu` to its `halt`, the data segment
loaded into the ds0_n/ds1_n registers by the row rule). Every register the simulator ends up
knowing (the temporaries the program wrote, the predicates and flags it set) must be equal.

The random programs are straight-line, built so that the simulator never stops on an open
semantic: sources are data registers or temporaries already written, the flags are read only
right after the add or sub that set them, adc and sbc follow an add or sub in the unsigned mode,
mov16 writes halves of written temporaries, and an shr by 32 or more runs in the unsigned mode.

    pds_esil_check.py fixed                     # the program below, every modelled form
    pds_esil_check.py random [--count N] [--seed S]

Needs the Rust tools built (cargo build -p sgx-tools) and the fork's install (R2_PREFIX, or its
prefix beside the repository).
"""
from __future__ import annotations

import argparse
import os
import pathlib
import random
import re
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[3]
# the radare2 fork's install: R2_PREFIX, or its prefix beside the repository
PREFIX = pathlib.Path(os.environ.get("R2_PREFIX", ROOT.parent / "radare2-prefix"))
sys.path.insert(0, str(ROOT / "crates" / "pysgx"))
import load  # noqa: E402

BIN = load.cargo_target_dir() / "debug"
FLAGS = ("p0", "p1", "p2", "aluz", "alun")

FIXED = """\
        .word 0xffffffff, 5, 1, 2
        .word 0x80000010, 0xffff, 0x00020000, 0xf0f0
        .word 0x11112222, 3, 0xaaaabbbb, 0
        add ds0[48], ds0[0], ds1[0]
        adc ds0[49], ds0[1], ds1[1]
        sub ds0[50], ds0[48], ds1[0]
        sbc ds0[51], ds0[1], ds1[1]
        sub ds0[53], ds0[1], ds1[1]
        (aluz) mov32 ds0[52], ds1[3]
        and ds0[54], ds0[3], ds1[3]
        or ds0[55], ds0[3], ds1[2]
        xor ds0[56], ds0[3], ds1[3]
        nor ds0[57], ds0[3], ds1[3]
        nand ds0[58], ds0[3], ds1[3]
        not ds0[59], ds0[2]
        shl ds0[60], ds0[2], 4
        shr ds0[61], ds0[2], 4
        shl ds0[62], ds0[2], 40
        mul ds0[63], ds0[3].l, ds1[2].h
        abs ds1[48], ds0[2]
        mov32 ds1[49], ds0[4]
        mov16 ds1[99], ds1[4].h
        mov64 ds1[50], ds0[4]
        mov128 ds[52], ds[4], swap
        tstz p0, ds1[5]
        tstn p1, ds0[2]
        (p1) tstz p2, ds0[1]
        alum signed
        shr ds1[54], ds0[2], 4
        mul ds1[55], ds0[3].l, ds1[2].h
        abs ds1[56], ds0[2]
        sub ds1[57], ds0[0], ds1[0]
        (alun) mov32 ds1[58], ds0[1]
        alum unsigned
        call fn
        bra loop0
        nop
fn:     xor ds1[60], ds0[1], ds1[1]
        rtn
loop0:  mov32 ds0[48], ds0[5]
loop:   sub ds0[48], ds0[48], ds1[0]
        add ds0[49], ds0[49], ds1[0]
        tstz p0, ds0[48]
        (p0) bra end
        bra loop
end:    halt
"""


def assemble(src: str, tmp: pathlib.Path) -> tuple[list[int], int]:
    """The program's words and its data dwords (the .word lines before the first instruction)."""
    s = tmp / "p.s"
    s.write_text(src)
    subprocess.run([str(BIN / "pds-asm"), "-o", str(tmp / "p.bin"), str(s)], check=True)
    raw = (tmp / "p.bin").read_bytes()
    ndata = 0
    for line in src.splitlines():
        line = line.split(";")[0].strip()
        if not line:
            continue
        if not line.startswith(".word"):
            break
        ndata += len(line[5:].split(","))
    return [int.from_bytes(raw[i:i + 4], "little") for i in range(0, len(raw), 4)], ndata


def simulate(src: str, tmp: pathlib.Path) -> dict[str, int]:
    s = tmp / "p.s"
    s.write_text(src)
    out = subprocess.run([str(BIN / "sgx-sim"), "--pds", str(s)], capture_output=True,
                         text=True)
    if out.returncode:
        raise RuntimeError(f"sgx-sim stopped: {out.stderr.strip()}\n{src}")
    want = {k.replace("[", "_").rstrip("]"): int(v, 16)
            for k, v in re.findall(r"^(ds[01]\[\d+\]) = (0x[0-9a-f]+)$", out.stdout, re.M)}
    m = re.search(r"^p = (.)(.)(.) \(p2-p0\), aluz (.), alun (.)$", out.stdout, re.M)
    for name, v in zip(("p2", "p1", "p0", "aluz", "alun"), m.groups()):
        if v != "?":
            want[name] = int(v)
    return want


def emulate(words: list[int], ndata: int, regs: list[str]) -> dict[str, int]:
    r2 = PREFIX / "bin" / "r2"
    data, code = words[:ndata], words[ndata:]
    cmds = ["wx " + "".join(w.to_bytes(4, "little").hex() for w in code), "aei", "aeim",
            "ar pc=0"]
    for i, w in enumerate(data):
        cmds.append(f"ar ds{i >> 1 & 1}_{(i >> 2) * 2 + (i & 1)}=0x{w:x}")
    cmds.append(f"aesu 0x{4 * code.index(0xAF000000):x}")
    cmds += [f"ar {r}" for r in regs]
    out = subprocess.run([str(r2), "-q", "-a", "pds", "-b", "32", "-e", "scr.color=0",
                          *sum((["-c", c] for c in cmds), []), "malloc://65536"],
                         capture_output=True, text=True, check=True).stdout.split()
    return {r: int(v, 16) for r, v in zip(regs, out[-len(regs):])}


def check(src: str) -> list[str]:
    """The registers on which the simulator and r2 disagree."""
    with tempfile.TemporaryDirectory() as t:
        tmp = pathlib.Path(t)
        want = simulate(src, tmp)
        words, ndata = assemble(src, tmp)
        got = emulate(words, ndata, sorted(want))
    return [f"{r}: sim 0x{v:x}, r2 0x{got[r]:x}" for r, v in sorted(want.items()) if got[r] != v]


def random_program(rng: random.Random, n: int = 40) -> str:
    """A straight-line program the simulator models end to end."""
    data = [rng.choice([0, 1, 0x7FFFFFFF, 0x80000000, 0xFFFFFFFF, rng.getrandbits(32)])
            for _ in range(16)]
    lines = [f"        .word {', '.join(f'0x{w:08x}' for w in data[i:i + 4])}"
             for i in range(0, 16, 4)]
    known = [set(range(8)), set(range(8))]        # rows 0-3: ds0[0..7], ds1[0..7]
    signed, after_addsub = False, False

    def src(b: int, below: int = 64) -> int:
        return rng.choice(sorted(i for i in known[b] if i < below))

    def dst() -> tuple[int, int]:
        b, n = rng.randrange(2), rng.randrange(64)
        known[b].add(48 + (n & 15))
        return b, n

    for _ in range(n):
        k = rng.choice(["alu", "alu", "addsub", "not", "abs", "shift", "mul", "mov32", "mov16",
                        "mov64", "mov128", "tst", "alum"])
        was, after_addsub = after_addsub, False
        if k == "addsub":
            a, b = src(0), src(1)
            d = dst()
            lines.append(f"        {rng.choice(['add', 'sub'])} ds{d[0]}[{d[1]}], ds0[{a}], ds1[{b}]")
            after_addsub = True
            if not signed and rng.random() < 0.5:
                a, b = src(0), src(1)
                d = dst()
                lines.append(f"        {rng.choice(['adc', 'sbc'])} ds{d[0]}[{d[1]}], ds0[{a}], ds1[{b}]")
                after_addsub = False
        elif k == "alu":
            a, b = src(0), src(1)
            d = dst()
            lines.append(f"        {rng.choice(['and', 'or', 'xor', 'nor', 'nand'])} "
                         f"ds{d[0]}[{d[1]}], ds0[{a}], ds1[{b}]")
        elif k in ("not", "abs"):
            if rng.random() < 0.5:
                s = f"ds0[{src(0)}]"
            else:
                s = f"ds1[{src(1, 32 if k == 'abs' else 64)}]"
            d = dst()
            lines.append(f"        {k} ds{d[0]}[{d[1]}], {s}")
        elif k == "shift":
            b = rng.randrange(2)
            s, amt = src(b), rng.choice([0, 1, 4, 16, 31, 32, 40, 63])
            op = rng.choice(["shl", "shr"])
            if op == "shr" and signed and amt >= 32:
                amt = 31
            d = dst()
            lines.append(f"        {op} ds{d[0]}[{d[1]}], ds{b}[{s}], {amt}")
        elif k == "mul":
            a, b = src(0), src(1)
            d = dst()
            lines.append(f"        mul ds{d[0]}[{d[1]}], ds0[{a}].{rng.choice('lh')}, "
                         f"ds1[{b}].{rng.choice('lh')}")
        elif k == "mov32":
            b = rng.randrange(2)
            s = src(b)
            if was and rng.random() < 0.5:
                # right after an add or sub, under a flag; the destination stays as
                # known as it was (a write that may not happen)
                db, t = rng.randrange(2), 48 + rng.randrange(16)
                lines.append(f"        ({rng.choice(['aluz', 'alun'])}) mov32 ds{db}[{t}], ds{b}[{s}]")
            else:
                d = dst()
                lines.append(f"        mov32 ds{d[0]}[{d[1]}], ds{b}[{s}]")
        elif k == "mov16":
            temps = [(b, i) for b in (0, 1) for i in known[b] if i >= 48]
            if not temps:
                continue
            db, di = rng.choice(temps)
            b = rng.randrange(2)
            lines.append(f"        mov16 ds{db}[{2 * di + rng.randrange(2)}], "
                         f"ds{b}[{src(b)}].{rng.choice('lh')}")
        elif k == "mov64":
            pairs = [(b, i) for b in (0, 1) for i in range(0, 64, 2)
                     if i in known[b] and i + 1 in known[b]]
            sb, si = rng.choice(pairs)
            db, di = rng.randrange(2), 2 * rng.randrange(32)
            known[db] |= {48 + (di & 15), 48 + ((di + 1) & 15)}
            lines.append(f"        mov64 ds{db}[{di}], ds{sb}[{si}]")
        elif k == "mov128":
            sk, dk = 2 * rng.randrange(4), 2 * rng.randrange(32)
            for b in (0, 1):
                known[b] |= {48 + (dk & 15), 48 + ((dk + 1) & 15)}
            lines.append(f"        mov128 ds[{dk}], ds[{sk}]{rng.choice(['', ', swap'])}")
        elif k == "tst":
            if rng.random() < 0.5:
                s = f"ds0[{src(0)}]"
            else:
                s = f"ds1[{src(1)}]"
            lines.append(f"        {rng.choice(['tstz', 'tstn'])} p{rng.randrange(3)}, {s}")
        elif k == "alum":
            signed = rng.random() < 0.5
            lines.append(f"        alum {'signed' if signed else 'unsigned'}")
    lines.append("        halt")
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("mode", choices=["fixed", "random"])
    ap.add_argument("--count", type=int, default=200)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args(argv)
    if not (PREFIX / "bin" / "r2").exists():
        print(f"no radare2 at {PREFIX}: set R2_PREFIX to an install of the fork", file=sys.stderr)
        return 2
    progs = [FIXED] if a.mode == "fixed" else \
        [random_program(random.Random(a.seed * 100003 + i)) for i in range(a.count)]
    bad = 0
    for i, p in enumerate(progs):
        diff = check(p)
        if diff:
            bad += 1
            print(f"program {i}:\n{p}" + "\n".join(diff))
    print(f"{len(progs)} programs, {bad} with differences")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
