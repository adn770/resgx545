#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Phase 11.33 part 1: arm TRC T = 32, 36, 40, 44, 48 with trc_hazard=1, one job per arm, a reset and
the gate after each.

    run_1133.py NAME first|repeat [--seed N]

Stops at the first trigger (no done in 100 ms, tick not advancing, BIF fault, EVENT_STATUS2 not
0x400, a failed gate, an arm that failed, more than 3 recovery resets) after a reset and a gate, and
never goes on past it. A refused arm of T stops the stage. No other T and no other use of the hazard
word: t1133.arm_line refuses them.
"""
import argparse
import datetime
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_stage as RS  # noqa: E402
import t1133  # noqa: E402

PRED = HERE / "predictions-1133.toml"
FROZEN = HERE / "predictions-1133.sha256"
MAX_RESETS = 3


def stock_ok(run, tag):
    """The stock firmware (own_arm off) and the gate exact."""
    g = RS.run_remote("gate")
    st = RS.run_remote("status")
    run.save(f"{tag}-gate.json", {"gate": g, "status": st})
    return bool(g["ok"]) and st["health"]["ok"] and st["alive"]["advancing"]


def stage(run, a):
    srcv = RS.srcversions()
    run.env(srcv)
    if not (FROZEN.exists() and t1133.check_frozen(PRED, FROZEN.read_text().strip())):
        raise RS.StageStop("predictions-1133.toml is not frozen")
    run.save("env33.toml", f'predictions_sha256 = "{t1133.sha256(PRED)}"\nstage = "{a.stage}"\n'
             f'module_srcversion = "{srcv}"\nseed = {a.seed}\n')
    if not stock_ok(run, "pre"):
        raise RS.StageStop("the gate before the stage is not exact")
    jobs = t1133.make_jobs(t1133.TS, 1, seed=a.seed if a.stage == "first" else a.seed + 1)
    resets = 0
    verdicts = []
    for i, j in enumerate(jobs):
        t = j["T"]
        tag = f"{a.stage}-T{t}"
        line = t1133.arm_line(t)                 # refuses anything but 32..48
        print(f"{tag}: arm '{line}' marker {j['marker']:#010x}")
        try:
            out = RS.arm(run, "trcp_%d" % t, line, tag)
        except RS.StageStop as e:
            run.save(f"{tag}-armfail.txt", str(e))
            raise
        res = RS.run_remote("run", {"name": run.name, "outdir": str(run.dir), "seed": a.seed,
                                    "jobs": [{"n": 1, "params": j["params"], "runid": 0x3300 + i,
                                              "timeout_ms": 100}]}, timeout=120)
        run.save(f"{tag}-run.json", res)
        rec = res["records"][0] if res["records"] else None
        stop = res.get("stop")
        v = {"T": t, "marker": j["marker"], "stop": stop, "arm_rate_hz": out["rate_hz"]}
        if rec:
            v.update(t1133.judge(j["marker"], rec))
            v["slot"] = rec["slot"]
        alive = res.get("alive", {}).get("advancing")
        hl = res.get("health", {}).get("ok")
        v["alive"], v["health_ok"] = bool(alive), bool(hl)
        v["log_bad"] = res.get("log_bad")
        rst = RS.unarm(run, tag)                 # the reset back to stock
        v["reset_ok"] = rst.get("ok")
        if stop or not rst.get("ok"):
            resets += 1
        v["gate_ok"] = stock_ok(run, tag)
        pass_ = (not stop and v.get("done") and v.get("marker_back") and v.get("r0_zero") and v["alive"]
                 and v["health_ok"] and not v["log_bad"] and v["gate_ok"])
        v["P33"] = bool(pass_)
        verdicts.append(v)
        run.save(f"{a.stage}-verdicts.json", verdicts)
        print(f"{tag}: {json.dumps({k: v.get(k) for k in ('done', 'marker_back', 'r0_zero', 'top', 'alive', 'health_ok', 'gate_ok', 'stop', 'P33')})}")
        if stop or not v["gate_ok"] or not v["alive"] or not v["health_ok"] or resets > MAX_RESETS:
            raise RS.StageStop(f"{tag}: trigger {stop or 'unhealthy or gate failed'}; reset and gate done; stage stopped")
        if not v.get("done"):
            raise RS.StageStop(f"{tag}: no done")
    print("all jobs ran; verdicts", [(v["T"], v["P33"]) for v in verdicts])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("stage", choices=["first", "repeat"])
    ap.add_argument("--seed", type=int, default=1133)
    a = ap.parse_args()
    run = RS.Run(a.name, "s33-" + a.stage)
    try:
        RS.upload_runner()
        stage(run, a)
        run.kernel_log()
        print(f"stage {a.stage}: PASSED ({a.name})")
        return 0
    except RS.Frozen as e:
        print(f"LAPTOP DID NOT ANSWER: STOP. Report; boot and run nothing further. {e}")
        return 99
    except RS.StageStop as e:
        try:
            run.kernel_log()
        except Exception:
            pass
        print(f"stage {a.stage}: STOPPED: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
