#!/usr/bin/env python3
"""After a stop of a firmware stage: save regs, status, own_res (page) and the kernel log tail from the laptop into
out/NAME/stopsave/, then the landed runner's reset (own_arm back to stock) and gate (fill and triangle exact).  Writes no
register.   stop_recover_1137.py NAME"""
import json, pathlib, subprocess, sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(pathlib.Path.home() / "src/resgx545/tools/fwtask"))
import run_stage as RS  # noqa: E402
name = sys.argv[1]
out = pathlib.Path(__file__).resolve().parent / "out" / name / "stopsave"
out.mkdir(parents=True, exist_ok=True)
D = "/sys/kernel/debug/dri/0/sgx"
for f in ("regs", "status", "own_arm"):
    (out / (f + ".txt")).write_text(RS.lap("sudo -n cat %s/%s 2>&1" % (D, f)).stdout)
(out / "own_res.txt").write_text(RS.lap("sudo -n python3 ~/fwtask/fwtask_run.py page '{}' 2>&1 | tail -c 20000").stdout)
(out / "journal.txt").write_text(RS.lap("sudo -n journalctl -k -n 400 --no-pager 2>&1", 60).stdout)
r = RS.run_remote("reset")
g = RS.run_remote("gate")
(out / "reset.json").write_text(json.dumps({"reset": r, "gate": g}, indent=1, default=str))
print("reset ok %s, gate ok %s" % (r.get("ok"), g.get("ok")))
