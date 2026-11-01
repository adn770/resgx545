# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Markers for probes that write a register and read it back (phase 11.35).

Temporaries and other registers keep their values from job to job (E484), so a probe that writes
the same value to the same register in every job cannot tell a write that landed from a stale
read of an earlier job's. Two helpers:

- fresh_markers(n, seed): n distinct marker values, one per job, from a seed the run records
  (the form E535 used: 0x7nnnnnnn, neither half 0 or 0xffff). A table generator passes them as
  the cases' marker input and as the expected value; the hypotheses name that job's marker.
- fixed_marker_writes(probes, src_dir): the (register, value) pairs a table writes with a
  `mov rN, #imm` in more than one of its jobs (probes of the write-test templates,
  WRITE_TEST_SOURCES). Such a table's read-back is no proof that a write
  landed unless something else tells the jobs apart (an order, a reset between jobs, a different
  register). Constants that are not markers are left out: values below 0x10000 and the scratch
  pointer's 0x5CAF0000 base.

    markers.py [TABLE.toml ...]     the tables with fixed-marker writes (all tables under probes/)
"""
from __future__ import annotations

import pathlib
import random
import re
import sys

import probe

_IMM_WRITE = re.compile(r"^\s*mov(?:\.\w+)*\s+r(\d+)\s*,\s*#(0x[0-9a-fA-F]+|\d+)\s*(?:;.*)?$", re.M)
SCRATCH_BASE = 0x5CAF
# The templates of the register write tests (a marker written to a register, read back): the
# check is made for the probes that use them. Operand constants of the instruction tests (a
# register loaded with a value an instruction then reads) are not markers.
WRITE_TEST_SOURCES = ("temps.s", "temps_phas.s")


def fresh_markers(n: int, seed: int) -> list[int]:
    """n distinct markers 0x7nnnnnnn from the seed: no marker repeats, none ends in 0000 or
    ffff in either half, so a leftover 0 or an all-ones read is never a marker."""
    rng = random.Random(seed)
    used: set[int] = set()
    out = []
    while len(out) < n:
        m = 0x70000000 | rng.getrandbits(28)
        if m in used or m & 0xffff in (0, 0xffff) or m >> 16 & 0xffff in (0x7000, 0x7fff):
            continue
        used.add(m)
        out.append(m)
    return out


def fresh_halves(n: int, seed: int) -> list[int]:
    """n distinct 16-bit halves, one per job, for a marker (half << 16 | register number) whose low
    half names the register, so that a read of another register's value (a wrap) is told from a
    read of an earlier job's (another half). Not 0x7E57 or 0x1E57, the halves the earlier
    tables wrote in every job."""
    rng = random.Random(seed)
    out: list[int] = []
    while len(out) < n:
        h = rng.randrange(0x1000, 0xf000)
        if h not in out and h not in (0x7E57, 0x1E57):
            out.append(h)
    return out


def marker_writes(p: probe.Probe, src_dir: pathlib.Path) -> list[set]:
    """For each job of p: the set of (register, value) markers its program writes with a mov."""
    template = (src_dir / p.source).read_text()
    out = []
    for case in p.cases:
        text = probe.render(p, case, template)
        out.append({(int(r), int(v, 0)) for r, v in _IMM_WRITE.findall(text)
                    if int(v, 0) >= 0x10000 and int(v, 0) >> 16 != SCRATCH_BASE})
    return out


def fixed_marker_writes(probes: list, src_dir: pathlib.Path | None = None,
                        sources: tuple = WRITE_TEST_SOURCES) -> dict:
    """{(register, value): jobs} for the markers written in more than one job of the table."""
    seen: dict = {}
    for p in probes:
        if p.source not in sources:
            continue
        d = src_dir or probe.PROBES_DIR
        for i, ws in enumerate(marker_writes(p, d)):
            for w in ws:
                seen.setdefault(w, []).append(f"{p.name}__{i}")
    return {w: jobs for w, jobs in seen.items() if len(jobs) > 1}


def main(argv: list[str]) -> int:
    paths = [pathlib.Path(a) for a in argv] or sorted(probe.PROBES.glob("*/*.toml"))
    flagged = 0
    for t in paths:
        if "[[probe]]" not in t.read_text():
            continue
        src = t.parent / "templates"
        src = src if src.is_dir() else probe.PROBES_DIR
        fixed = fixed_marker_writes(probe.load(t), src)
        if fixed:
            flagged += 1
            print(f"{t.parent.name}/{t.name}: {len(fixed)} markers written in more than one job "
                  f"(e.g. r{min(fixed)[0]} = 0x{min(fixed)[1]:08x} in {len(next(iter(fixed.values())))} jobs)")
    return 1 if flagged else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
