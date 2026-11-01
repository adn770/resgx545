#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The ISP visibility counters (0x0494-0x04b4) around every sweep case and probe run.

They have counted under some pass types on one boot and never on the next.
Rather than replaying old runs to find what turned them on, every run records them: the case
runs inside regtimeline over the nine registers (sampled from before the job to its exit,
so the first sample is what the previous job left), and its output keeps the timeline.

    counters.py scan PATH...
        PATH: a raw.txt, or a directory searched for raw.txt files (sweep runs, "=== case"
        blocks; probe runs, "probe-case" lines). Prints every case whose counters were
        ever non-zero, with the case before it, then the totals; exit 1 if any counted.
"""
from __future__ import annotations

import pathlib
import re
import sys

LO, HI = 0x0494, 0x04b4
REGS = f"{LO:#06x}-{HI:#06x}"
OFFS = tuple(range(LO, HI + 4, 4))

_HEAD = re.compile(r"^timeline: regs ((?:0x[0-9a-f]+ ?)+)", re.M)


def wrap(argv: list, rt: str) -> list:
    """argv inside regtimeline over the counters, sampling only while it runs."""
    return [rt, "0", "0", REGS, "--", *argv]


def _ranges(regs: str):
    for part in regs.split(","):
        lo, _, hi = part.partition("-")
        yield int(lo, 0), int(hi or lo, 0)


def with_counters(regs: str) -> str:
    """A timeline's register list with the counters added (unless it covers them)."""
    if all(any(lo <= o <= hi for lo, hi in _ranges(regs)) for o in OFFS):
        return regs
    return f"{regs},{REGS}"


def samples(text: str) -> list | None:
    """[{offset: value}] of the counters, one per timeline row of the (last) timeline in
    text; None without a timeline that covers them."""
    heads = list(_HEAD.finditer(text))
    if not heads:
        return None
    m = heads[-1]
    regs = [int(x, 16) for x in m.group(1).split()]
    cols = [i for i, o in enumerate(regs) if o in OFFS]
    if not cols:
        return None
    rows = []
    for line in text[m.end():].splitlines():
        if line.startswith("tl "):
            vals = line.split()[2:]
            rows.append({regs[i]: int(vals[i], 16) for i in cols})
    return rows


def summary(text: str) -> str | None:
    """None without a counters timeline; "" when they stayed 0; else, per register that was
    ever non-zero, its first and highest value ("0x04b4 0x4..0xe")."""
    rows = samples(text)
    if rows is None:
        return None
    parts = []
    for o in OFFS:
        vals = [r[o] for r in rows if o in r]
        if any(vals):
            parts.append(f"{o:#06x} {vals[0]:#x}..{max(vals):#x}")
    return ", ".join(parts)


def cases(text: str) -> list:
    """[(case id, its text)] of a sweep or probe raw.txt."""
    if re.search(r"^=== case ", text, re.M):
        blocks = re.split(r"^=== case ", text, flags=re.M)[1:]
    else:
        blocks = re.split(r"^probe-case ", text, flags=re.M)[1:]
    return [(b.split("\n", 1)[0].strip(), b) for b in blocks]


def scan(paths: list, out=None) -> int:
    """Print the cases that counted; the number of them."""
    out = out or sys.stdout
    files = []
    for p in map(pathlib.Path, paths):
        files += sorted(p.rglob("raw.txt")) if p.is_dir() else [p]
    total = recorded = counted = 0
    for f in files:
        prev = "(the run's start)"
        for cid, text in cases(f.read_text(errors="replace")):
            total += 1
            s = summary(text)
            recorded += s is not None
            if s:
                counted += 1
                print(f"{f}: {cid} ({s}) after {prev}", file=out)
            prev = cid
    print(f"{total} cases: {recorded} recorded, {counted} counted", file=out)
    return counted


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) < 2 or argv[0] != "scan":
        print(__doc__, file=sys.stderr)
        return 2
    return 1 if scan(argv[1:]) else 0


if __name__ == "__main__":
    sys.exit(main())
