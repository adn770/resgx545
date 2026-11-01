#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Summary of the cases of a script table's output: the scripts' one() helper prints a block
per run, "== NAME: tri ARGS", then the tool's lines ("job: ok", "target: WxH hash H", "diff: N of
M pixels", "tri WxH #1: N us", "reg 0x.... V", "scratch ...") and "rc N".

    casesummary.py OUTPUT.TXT [--reference NAME]   one line a case: job, wrong pixels, hash, time,
                                                   and whether it differs from the reference
                                                   (default: the first case)
"""
from __future__ import annotations

import argparse
import dataclasses
import re
import sys

CASE_RE = re.compile(r"^== ([^:\n]+): tri(?: (.*))?$", re.M)
TIME_RE = re.compile(r"^tri \d+x\d+ #\d+: (\d+) us$", re.M)
HASH_RE = re.compile(r"^target: \d+x\d+ hash (0x[0-9a-f]+)$", re.M)
DIFF_RE = re.compile(r"^diff: (\d+) of \d+ pixels", re.M)
JOB_RE = re.compile(r"^job: (.*)$", re.M)
RC_RE = re.compile(r"^rc (-?\d+)$", re.M)


@dataclasses.dataclass(frozen=True)
class Case:
    name: str
    args: str
    job: str | None
    wrong: int | None
    hash: str | None
    us: int | None
    rc: int | None
    scratch: list
    regs: list


def parse(text: str) -> list:
    """The cases of an output.txt, in order."""
    marks = list(CASE_RE.finditer(text))
    out = []
    for i, m in enumerate(marks):
        body = text[m.end(): marks[i + 1].start() if i + 1 < len(marks) else len(text)]
        body = re.split(r"^(?:## |== end)", body, maxsplit=1, flags=re.M)[0]
        j, h, d, t, r = (JOB_RE.search(body), HASH_RE.search(body), DIFF_RE.search(body),
                         TIME_RE.search(body), RC_RE.search(body))
        out.append(Case(m[1], m[2] or "", j and j[1], d and int(d[1]), h and h[1], t and int(t[1]),
                        r and int(r[1]), re.findall(r"^scratch.*$", body, re.M),
                        re.findall(r"^reg 0x.*$", body, re.M)))
    return out


def table(cases: list, reference: str | None = None) -> str:
    """One line per case; "reference" marks the control, "differs" a case whose job, wrong
    pixel count, hash or scratch lines are not the control's."""
    if not cases:
        return ""
    ref = next((c for c in cases if c.name == reference), cases[0])
    lines = []
    for c in cases:
        if c is ref:
            tag = "reference"
        elif c.job != "ok" or (c.wrong, c.hash, c.scratch) != (ref.wrong, ref.hash, ref.scratch):
            tag = "differs"
        else:
            tag = "same"
        w = "-" if c.wrong is None else c.wrong
        lines.append(f"{c.name:<28} {(c.job or '-')[:24]:<24} wrong {w!s:<6} {c.hash or '-':<20} "
                     f"{c.us if c.us is not None else '-':>8} us  {tag}")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("output")
    ap.add_argument("--reference")
    a = ap.parse_args(argv)
    sys.stdout.write(table(parse(open(a.output).read()), a.reference))
    return 0


if __name__ == "__main__":
    sys.exit(main())
