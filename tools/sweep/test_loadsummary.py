# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""loadsummary.py: the runs of a register-limits output, the held runs, the times."""
from __future__ import annotations

import pathlib
import subprocess
import sys

import loadsummary

TEXT = """## start: 0810=0x1
== run 1 init fill: rc 0 wall 230 ms
job: ok
job time: 500 us
target: 64x32 hash 0xaa
diff: 0 of 2048 pixels
== run 1 init tri: rc 0 wall 300 ms
job: ok
target: 64x64 hash 0xbb
diff: 0 of 4096 pixels
tri 64x64 #1: 6000 us
tri: 1 renders ok
== run 1 r0818=0x3ff fill: rc 0 wall 230 ms
job time: 520 us
target: 64x32 hash 0xaa
diff: 0 of 2048 pixels
== run 1 r0818=0x3ff tri: rc 1 wall 300 ms
target: 64x64 hash 0xcc
diff: 90 of 4096 pixels, first (1, 2) 0x0 expected 0x1
tri 64x64 #1: 6100 us
klog: gma500: hang
== run 2 r0818=0x3ff fill: rc 0 wall 230 ms
job time: 540 us
target: 64x32 hash 0xaa
diff: 0 of 2048 pixels
## case 2 end: 0810=0x1
"""


def test_parse_runs():
    runs = loadsummary.parse(TEXT)
    assert [(r.case, r.workload, r.rc, r.us, r.hash, r.wrong, r.klog) for r in runs] == [
        ("init", "fill", 0, 500, "0xaa", 0, 0), ("init", "tri", 0, 6000, "0xbb", 0, 0),
        ("r0818=0x3ff", "fill", 0, 520, "0xaa", 0, 0),
        ("r0818=0x3ff", "tri", 1, 6100, "0xcc", 90, 1),
        ("r0818=0x3ff", "fill", 0, 540, "0xaa", 0, 0)]


def test_table_counts_the_held_runs_and_the_ratio_to_the_reference():
    t = loadsummary.table(loadsummary.parse(TEXT))
    assert "fill: reference init: 1 runs, job time min 500 median 500 max 500 us\n" in t
    assert "  r0818=0x3ff: 2 of 2 held, median 530 us (1.060 of the reference)\n" in t
    assert "  r0818=0x3ff: 0 of 1 held, median 6100 us (1.017 of the reference), " \
           "1 log lines\n" in t


def test_cli(tmp_path):
    f = tmp_path / "output.txt"
    f.write_text(TEXT)
    r = subprocess.run([sys.executable, str(pathlib.Path(loadsummary.__file__)), str(f),
                        "--reference", "r0818=0x3ff"], capture_output=True, text=True)
    assert r.returncode == 0
    assert "fill: reference r0818=0x3ff: 2 runs" in r.stdout
