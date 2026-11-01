#!/usr/bin/env python3
"""Job counts, job times (min, max, microseconds) and baselines of a campaign run directory.
Usage: stats_client_1137.py DIR  (DIR = ~/src/resgx545-data/usse/fw37-X)"""
import pathlib, re, sys, tomllib
d = pathlib.Path(sys.argv[1])
times, jobs, nopix = [], 0, 0
for r in sorted(d.glob("usse-fw37-*/raw.txt")):
    t = r.read_text()
    times += [int(x) for x in re.findall(r"job time: (\d+) us", t)]
    jobs += len(re.findall(r"^probe-case ", t, re.M))
env = tomllib.load(open(d / "env.toml", "rb"))
ba = [(v.get("before"), v.get("after")) for v in env.get("probes", {}).values()]
print("%s: %d jobs, %d job times %s..%s us, baselines before/after clean %d of %d" % (
    d.name, jobs, len(times), min(times, default=0), max(times, default=0),
    sum(1 for b, a in ba if b == a == "diff: 0 of 4096 pixels"), len(ba)))
k = d / "kernel.log"
if k.exists():
    lg = k.read_text()
    print("kernel.log: %d lines, case markers %d, BIF_FAULT nonzero %d, 'fault' %d, 'hang' %d" % (
        lg.count("\n"), lg.count("resgx545 case"), len(re.findall(r"BIF_FAULT 0x[0-9a-f]*[1-9a-f]", lg)),
        len(re.findall(r"fault", lg, re.I)) - lg.count("BIF_FAULT 0x0"), len(re.findall(r"hang", lg, re.I))))
