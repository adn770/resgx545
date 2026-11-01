#!/usr/bin/env python3
"""Per case of fw37-narrow: the label, the readback (r10 and the two dwords 16/17 after the job) and which hypotheses of
the frozen table equal it.  Usage: narrow_table_1137.py DATA_DIR"""
import pathlib, re, sys, tomllib
d = pathlib.Path(sys.argv[1])
tbl = tomllib.load(open(pathlib.Path(__file__).resolve().parent / "probes/usse/fw37-narrow.toml", "rb"))
for p in tbl["probe"]:
    rep = (d / ("usse-fw37-narrow-" + p["name"][len("fw37-"):]) / "report.txt")
    if not rep.exists():
        print(p["name"], "no report")
        continue
    txt = rep.read_text()
    print(txt.splitlines()[0][:110])
    for i, lab in enumerate(p["labels"]):
        m = re.search(r"^  \[%d\] .*$" % i, txt, re.M)
        line = m.group(0) if m else "(no line)"
        o0 = re.search(r": (0x[0-9a-f]{8}) scratch", line)
        dw = dict(re.findall(r"\+0x([0-9a-f]{3})=(0x[0-9a-f]{8})", line))
        hit = []
        for h, e in p["hypotheses"].items():
            ex = e[i]
            if o0 and int(o0.group(1), 16) == ex["o0"] and all(int(dw.get("%03x" % k, "0x0"), 16) == v for k, v in enumerate(ex.get("dwords", [])) if False):
                hit.append(h.split(":")[0])
        print("  %-48s o0 %s d16 %s d17 %s  o0-matches %s" % (lab[:48], o0.group(1) if o0 else "?", dw.get("020", dw.get("0x020", "?")), dw.get("024", "?"), hit))
