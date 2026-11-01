#!/usr/bin/env python3
"""Per frozen client row, the numbers of the fw37 runs: cases on the model, cases that failed, from report.txt of
every probe directory.  Usage: summarize_client_1137.py DATA_USSE_DIR   (prints one JSON object)."""
import json, pathlib, re, sys
data = pathlib.Path(sys.argv[1])
ROWS = {"P37_C7": ("compare", r"-(u|s)cmp-(?!prev)"), "P37_C7prev": ("compare", r"-(u|s)cmp-prev"),
        "P37_C8": ("pred", r""), "P37_C9": ("ima32hi-repeat", r""),
        "P37_C13a": ("narrow", r"-ld(ab|aw)-offsets"), "P37_C13b": ("narrow", r"-ld-unaligned"),
        "P37_C13c": ("narrow", r"-(stab|staw|stad-unaligned-control)")}
out = {}
for row, (tbl, pat) in ROWS.items():
    n = good = failed = probes = settled = 0
    for p in sorted((data / ("fw37-" + tbl)).glob("usse-fw37-*/report.txt")):
        if not re.search(pat, p.parent.name):
            continue
        txt = p.read_text()
        k = len(re.findall(r"^  \[\d+\] ", txt, re.M))
        probes += 1
        n += k
        failed += len(re.findall(r"^  \[\d+\] .*failed", txt, re.M))
        if "SETTLED: model" in txt.splitlines()[0]:
            good += k
            settled += 1
    out[row] = {"probes": probes, "settled_probes": settled, "cases": n, "on_model": good, "failed": failed}
print(json.dumps(out, indent=1))
