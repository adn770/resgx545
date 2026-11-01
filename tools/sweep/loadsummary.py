#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Summary of a script table's runs of jobs under register values (probes/platform/
register-limits.sh): per workload, the time of the job under the first case (the reference)
and under every other, and whether the output and the exit status held.

The script prints, per run, "== run REP CASE WORKLOAD: rc N wall MS ms", then the tool's job
lines ("job time: N us", "tri WxH #1: N us", "probe X: job time: N us", "target: WxH hash H",
"diff: N of M pixels") and the driver's log lines ("klog: ..."). A run is "held" when its exit
status is 0 and its diff line counts no wrong pixel and its target hash is its workload's
reference hash; "differs" otherwise.

    loadsummary.py OUTPUT.TXT [--reference CASE]    print the table (default reference: the
                                                    first case of the file)
"""
from __future__ import annotations

import argparse
import dataclasses
import re
import statistics
import sys

RUN_RE = re.compile(r"^== run (\d+) (\S+) (\S+): rc (-?\d+) wall (\d+) ms$", re.M)
TIME_RE = re.compile(r"^(?:job time: |probe \S+: job time: |tri \d+x\d+ #\d+: )(\d+) us$", re.M)
HASH_RE = re.compile(r"^target: \d+x\d+ hash (0x[0-9a-f]+)$", re.M)
DIFF_RE = re.compile(r"^diff: (\d+) of \d+ pixels", re.M)


@dataclasses.dataclass(frozen=True)
class Run:
    rep: int
    case: str
    workload: str
    rc: int
    wall_ms: int
    us: int | None          # the first job's time
    hash: str | None
    wrong: int | None       # pixels the tool counted wrong (the diff line)
    klog: int               # driver log lines the run printed


def parse(text: str) -> list:
    """The runs of an output.txt, in order."""
    marks = list(RUN_RE.finditer(text))
    runs = []
    for i, m in enumerate(marks):
        body = text[m.end(): marks[i + 1].start() if i + 1 < len(marks) else len(text)]
        body = re.split(r"^## ", body, maxsplit=1, flags=re.M)[0]
        t, h, d = TIME_RE.search(body), HASH_RE.search(body), DIFF_RE.search(body)
        runs.append(Run(int(m[1]), m[2], m[3], int(m[4]), int(m[5]), t and int(t[1]),
                        h and h[1], d and int(d[1]), len(re.findall(r"^klog: ", body, re.M))))
    return runs


def table(runs: list, reference: str | None = None) -> str:
    """One line per workload and case: runs, median job time, its ratio to the reference
    case's median, and the runs that held (exit 0, no wrong pixel, the reference hash)."""
    if not runs:
        return ""
    reference = reference or runs[0].case
    by: dict = {}
    for r in runs:
        by.setdefault(r.workload, {}).setdefault(r.case, []).append(r)
    lines = []
    for wl, cases in by.items():
        ref = cases.get(reference, [])
        hashes = {r.hash for r in ref if r.hash}
        rt = [r.us for r in ref if r.us]
        rmed = statistics.median(rt) if rt else None
        lines.append(f"{wl}: reference {reference}: {len(ref)} runs"
                     + (f", job time min {min(rt)} median {rmed:.0f} max {max(rt)} us" if rt
                        else ""))
        for case, rs in cases.items():
            held = sum(r.rc == 0 and not r.wrong and (not hashes or r.hash in hashes)
                       for r in rs)
            ts = [r.us for r in rs if r.us]
            med = statistics.median(ts) if ts else None
            ratio = f" ({med / rmed:.3f} of the reference)" if med and rmed else ""
            lines.append(f"  {case}: {held} of {len(rs)} held"
                         + (f", median {med:.0f} us{ratio}" if med else "")
                         + (f", {sum(r.klog for r in rs)} log lines"
                            if any(r.klog for r in rs) else ""))
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("output")
    ap.add_argument("--reference")
    a = ap.parse_args(argv)
    with open(a.output) as f:
        sys.stdout.write(table(parse(f.read()), a.reference))
    return 0


if __name__ == "__main__":
    sys.exit(main())
