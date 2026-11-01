#!/usr/bin/env python3
"""Counts, per frozen client row, the cases of the probes the campaign runner settled on the model (verdict line of
report.txt).  Usage: judge_client_1137.py DATA_USSE_DIR TABLE...   Prints one line per probe and per-table totals."""
import pathlib, re, sys, tomllib
data = pathlib.Path(sys.argv[1])
for tbl in sys.argv[2:]:
    d = data / ("fw37-" + tbl)
    tot = ok = 0
    for p in sorted(d.glob("usse-fw37-*/report.txt")):
        txt = p.read_text()
        head = txt.splitlines()[0]
        n = len(re.findall(r"^  \[\d+\] ", txt, re.M))
        failed = len(re.findall(r"^  \[\d+\] .*failed", txt, re.M))
        good = n if "SETTLED: model" in head else 0
        tot += n
        ok += good
        print("%-48s %3d cases %3d on the model  failed %d  %s" % (p.parent.name, n, good, failed, head.split(": ", 1)[1][:70]))
    print("TOTAL %s: %d of %d" % (tbl, ok, tot))
