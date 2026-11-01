#!/usr/bin/env python3
"""Assemble every case with the landed usse-asm and compare the simulator's pixels with the model."""
import json, pathlib, subprocess, sys, tempfile
HERE = pathlib.Path(__file__).resolve().parent
P = HERE.parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(P / "recompute"))
import catalog, build, texmodel
ASM = pathlib.Path.home() / "src/resgx545/target/debug/usse-asm"
SIM = P / "target/release/examples/texpred"
tmpl = (P / "templates/tx_map.s").read_text()

def program(spec):
    pre, setup, smp = build.case_inputs(spec)
    return tmpl.replace("{PRE}", pre).replace("{SETUP}", setup).replace("{SMP}", smp)

def asm(text, out):
    r = subprocess.run([str(ASM), "-o", str(out), "-"], input=text, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"{out.name}: {r.stderr}\n{text}")

if __name__ == "__main__":
    only = sys.argv[1:]
    tmp = pathlib.Path(tempfile.mkdtemp())
    stats = {"ok": 0, "unsup": 0, "diff": 0}
    for gname, fn in catalog.GROUPS.items():
        for c in fn():
            if only and not any(c["name"].startswith(o) for o in only):
                continue
            f = tmp / (c["name"] + ".bin")
            asm(program(c["spec"]), f)
            r = subprocess.run([str(SIM), str(f), "16"], capture_output=True, text=True)
            first = r.stdout.splitlines()[0] if r.stdout else r.stderr[:100]
            if first.startswith("ERR"):
                stats["unsup"] += 1
                print(f"UNSUP {c['name']}: {first[:110]}")
                continue
            pix = [int(w, 16) for row in r.stdout.splitlines() for w in row.split()]
            want = texmodel.render(c["spec"], c["hyps"][0])
            if want is None:
                print(f"NOMODEL {c['name']}"); continue
            bad = sum(1 for a, b in zip(pix, want) if a != b)
            if bad:
                stats["diff"] += 1
                i = next(k for k, (a, b) in enumerate(zip(pix, want)) if a != b)
                print(f"DIFF {c['name']}: {bad}/2048 first at pixel {i}: sim {pix[i]:08x} model {want[i]:08x}")
            else:
                stats["ok"] += 1
    print(stats)
