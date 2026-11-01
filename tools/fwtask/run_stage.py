#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The Mac side of the phase 11.29 laptop runs: one stage per call, each only after the previous
one passed (the stage list of plan 5.2). Prints the installed and the loaded srcversion first and
refuses to run if they differ; stops at the first stop trigger; writes the raw data of every stage
to the data directory (untracked) with env.toml; never continues past a stage that did not pass.

    run_stage.py NAME STAGE [options]      stages: s1 s2 s3 s4 s5 s6r1 s6r2 s12 q033q1 s11 s13 ...
"""
import argparse
import datetime
import hashlib
import json
import os
import pathlib
import random
import subprocess
import sys
import time
import tomllib

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import classify  # noqa: E402
import fwtask  # noqa: E402
import layout as L  # noqa: E402

HOST = os.environ.get("FWTASK_HOST", "jtorra@10.42.0.2")     # the laptop, over the cable
SSH = ["ssh", "-o", "HostKeyAlias=cedar", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10",
       "-o", "ControlMaster=auto", "-o", "ControlPath=/tmp/fwtask-%r@%h", "-o", "ControlPersist=120",
       HOST]
DATA = pathlib.Path(os.environ.get("RESGX545_DATA", ROOT.parent / "resgx545-data")) / "firmware-tasks"
LINUX = pathlib.Path(os.environ.get("RESGX545_LINUX", ROOT.parent / "linux"))     # the fork
PRED = HERE / "predictions.toml"
FROZEN = HERE / "predictions.sha256"


class Frozen(Exception):
    """The laptop did not answer: STOP, boot nothing, report."""


class StageStop(Exception):
    pass


def lap(cmd, timeout=120, inp=None):
    r = subprocess.run(SSH + [cmd], capture_output=True, text=True, timeout=timeout, input=inp)
    if r.returncode == 255:
        raise Frozen(r.stderr.strip())
    return r


def run_remote(sub, args=None, timeout=300):
    r = lap(f"sudo -n python3 ~/fwtask/fwtask_run.py {sub} '{json.dumps(args or {})}'", timeout)
    lines = [ln for ln in r.stdout.splitlines() if ln.startswith("{")]
    if not lines:
        raise StageStop(f"{sub}: no output (rc {r.returncode}): {r.stderr.strip()[:300]}")
    out = json.loads(lines[-1])
    out["_rc"] = r.returncode
    return out


def srcversions():
    r = lap("echo \"$(sudo -n cat /sys/module/gma500_gfx/srcversion) $(modinfo -F srcversion gma500_gfx)\"")
    loaded, installed = r.stdout.split()
    print(f"loaded/installed srcversion: {loaded} {installed}")
    if not loaded or loaded != installed:
        raise StageStop("the loaded module is not the installed one")
    return loaded


class Run:
    def __init__(self, name, stage):
        self.name, self.stage = name, stage
        self.dir = DATA / name
        self.dir.mkdir(parents=True, exist_ok=True)
        self.t0 = time.time()
        self.log = []

    def save(self, fname, obj):
        p = self.dir / fname
        p.write_text(obj if isinstance(obj, str) else json.dumps(obj, indent=1, sort_keys=True) + "\n")

    def env(self, srcv):
        tool = hashlib.sha256()
        for f in sorted(HERE.glob("*.py")) + [HERE / "regs.toml"]:
            tool.update(f.read_bytes())
        fork = subprocess.run(["git", "-C", str(LINUX), "rev-parse", "HEAD"],
                              capture_output=True, text=True).stdout.strip()
        blobs = {f"{p.stem}.blob": hashlib.sha256(fwtask.blob_of(p.stem)).hexdigest() for p in fwtask.sources()}
        txt = ["# phase 11.29 run environment", f'name = "{self.name}"', f'stage = "{self.stage}"',
               f'date = "{datetime.datetime.now().astimezone().isoformat(timespec="seconds")}"',
               f'tool_sha256 = "{tool.hexdigest()}"', f'module_srcversion = "{srcv}"',
               f'fork_tip = "{fork}"', 'fork_base = "6ee9501832af"',
               f'predictions_sha256 = "{FROZEN.read_text().strip() if FROZEN.exists() else ""}"',
               'kernel = "7.3.0-resgx545"', "", "[blobs]"]
        txt += [f'"{k}" = "{v}"' for k, v in blobs.items()]
        self.save("env.toml", "\n".join(txt) + "\n")

    def kernel_log(self):
        since = datetime.datetime.fromtimestamp(self.t0 - 5).strftime("%Y-%m-%d %H:%M:%S")
        r = lap(f"sudo -n journalctl -k --since '{since}' --no-pager")
        self.save("kernel.log", r.stdout)
        return r.stdout


def upload(blobname):
    r = subprocess.run(SSH + [f"mkdir -p ~/fwtask && cat > ~/fwtask/{blobname}.blob"],
                       input=fwtask.blob_of(blobname), capture_output=True)
    if r.returncode:
        raise Frozen(r.stderr.decode()) if r.returncode == 255 else StageStop("upload failed")
    return f"/home/jtorra/fwtask/{blobname}.blob"


def upload_runner():
    with open(HERE / "fwtask_run.py", "rb") as f:
        r = subprocess.run(SSH + ["mkdir -p ~/fwtask && cat > ~/fwtask/fwtask_run.py"], stdin=f,
                           capture_output=True)
    if r.returncode:
        raise Frozen(r.stderr.decode()) if r.returncode == 255 else StageStop("upload failed")


def arm(run, blob, line, tag):
    path = upload(blob)
    out = run_remote("arm", {"blob": path, "arm": line})
    run.save(f"{tag}-arm.json", out)
    if not out.get("ok"):
        raise StageStop(f"arm {blob}: not ok: {json.dumps({k: out.get(k) for k in ('alive', 'health', 'log_bad', 'rate_hz', 'magic')})}")
    return out


def unarm(run, tag):
    out = run_remote("reset")
    run.save(f"{tag}-reset.json", out)
    return out


def check_frozen_predictions():
    if not (FROZEN.exists() and PRED.exists() and FROZEN.read_text().strip() == classify.sha256(PRED)):
        raise StageStop("predictions.toml is not frozen (predictions.sha256 missing or different): "
                        "freeze it before the first str")


def evaluate_9b(rec, reg):
    j = rec["job"]
    n = j["n"]
    name, kind, d = L.X9B[n]
    rr = {"R1": L.R1, "R2": L.R2}.get(reg) if isinstance(reg, str) else reg
    other = L.R2 if rr == L.R1 else L.R1
    A, B, C = j["A"], j["params"]["8"], j["params"]["9"]
    s = rec["slot"]
    H = rec["H"][hex(rr)]
    v = dict(A=A, B=B, C=C, L=s[0], H=H, A2=j["A_other"], R2H=rec["H"][hex(other)],
             L2=s[1], t0=s[1], t1=s[2], landed=rec["done"] and all(x != L.INITFILL for x in s[:{"x10": 2, "x11": 3, "x1": 2}.get(kind, 1)]))
    rid = name
    return classify.evaluate(PRED, rid, **v), v


def jobs_9b(reg, cmds, pairs, repeats, seed):
    rr = {"R1": L.R1, "R2": L.R2}[reg]
    other = L.R2 if rr == L.R1 else L.R1
    A = L.A[rr]
    jobs = []
    for rep in range(repeats):
        for pair in range(pairs):
            for n in cmds:
                # B ^ mask is A for both registers, so the second pair swaps B and C
                B, C = (L.C[rr], L.B[rr]) if pair else (L.B[rr], L.C[rr])
                jobs.append({"n": n, "params": {"8": B, "9": C}, "regs": {str(rr): A, str(other): L.A[other]},
                             "A": A, "A_other": L.A[other], "reg": reg, "pair": pair, "rep": rep})
    random.Random(seed).shuffle(jobs)
    for i, j in enumerate(jobs):
        j["regs"] = {int(k): v for k, v in j["regs"].items()}
    return jobs


def stage_s1(run, a):
    srcv = srcversions()
    run.env(srcv)
    out = run_remote("stock")
    run.save("s1-stock.json", out)
    print(json.dumps({k: out.get(k) for k in ("ok", "rate_hz", "own_arm", "log_bad")}))
    if not out["ok"]:
        raise StageStop("s1: the unarmed stock run is not healthy")


def stage_s2(run, a):
    srcv = srcversions()
    run.env(srcv)
    out = arm(run, "null", "slots=0x1 entry=0", "s2")
    g = run_remote("gate")
    m = run_remote("status")
    run.save("s2-gate.json", g)
    ok = classify.evaluate(PRED, "S2_null", ticks_per_s=out["rate_hz"], fill_diff=0 if g["ok"] else 1,
                           tri_diff=0 if g["ok"] else 1, faults=m["health"]["faults_status"])
    print(f"S2_null: {'pass' if ok else 'FAIL'} rate {out['rate_hz']:.1f} Hz, gate {g['ok']}")
    run.save("s2-verdict.json", {"S2_null": ok, "rate_hz": out["rate_hz"], "gate": g})
    if not ok:
        raise StageStop("s2: null wrapper failed")


def one_job(run, tag, jobs, **kw):
    res = run_remote("run", {"name": run.name, "outdir": str(run.dir), "jobs": jobs, **kw}, timeout=900)
    (run.dir / f"{tag}.jsonl").write_text("\n".join(json.dumps(r, sort_keys=True) for r in res["records"]) + "\n")
    run.save(f"{tag}-summary.json", {k: v for k, v in res.items() if k != "records"})
    if res.get("stop"):
        # the remote already wrote the hang dump; read, reset, check, then stop
        try:
            unarm(run, tag + "-stop")
        finally:
            pass
        raise StageStop(f"{tag}: stop trigger: {res['stop']}")
    return res["records"]


def stage_s3(run, a):
    run.env(srcversions())
    arm(run, "mem", "slots=0x1 entry=0", "s3")
    recs = one_job(run, "s3-mem", [{"n": 1, "params": {"3": 0}, "runid": 31}])
    s = recs[0]["slot"]
    ok = classify.evaluate(PRED, "S3_mem", done=recs[0]["done"], marker=s[3], pa1=s[1], pa2=s[2])
    # the stage passes when our code ran and stored (done, the marker, the tick goes on, no
    # trigger); a falsified prediction about the event words is a result, not a stop
    works = recs[0]["done"] and s[3] == 0x5a5a1129 and s[0] != L.INITFILL
    print(f"S3_mem: prediction {'held' if ok else 'FALSIFIED'}; stage function {'passed' if works else 'FAILED'}; "
          f"slot (pa0, pa1, pa2, marker) {[hex(x) for x in s]}")
    run.save("s3-verdict.json", {"S3_mem": ok, "function": works, "slot": s})
    if not works:
        raise StageStop("s3: our task did not run and store")


def stage_s4(run, a):
    run.env(srcversions())
    arm(run, "ldr", "slots=0x1 entry=0", "s4")
    before = run_remote("status")
    recs = one_job(run, "s4-ldr", [{"n": 1, "params": {"3": 0}, "runid": 41}])
    s = recs[0]["slot"]
    host = run_remote("page")  # keeps the page too
    st = run_remote("status")
    run.save("s4-page.json", host)
    # the host's own reads of the identity registers (the regs file)
    r = lap("sudo -n grep -E '^reg 0x(001c|0020) ' /sys/kernel/debug/dri/0/sgx/regs | head -2").stdout.split()
    core_id, core_rev = int(r[2], 16), int(r[5], 16)
    ok = classify.evaluate(PRED, "S4_ldr", core_id=s[0], host_core_id=core_id, core_rev=s[1],
                           host_core_rev=core_rev, timer_ok=s[2] not in (0, L.INITFILL))
    print(f"S4_ldr: {'pass' if ok else 'FAIL'} {[hex(x) for x in s]} host {hex(core_id)} {hex(core_rev)}")
    run.save("s4-verdict.json", {"S4_ldr": ok, "slot": s})
    if not ok:
        raise StageStop("s4 failed")


def freeze_predictions():
    PRED.write_text(classify.render())
    sha = classify.sha256(PRED)
    FROZEN.write_text(sha + "\n")
    print(f"predictions.toml frozen, sha256 {sha}")
    return sha


def stage_9b(run, a, reg, cmds, tag, repeats=3, pairs=2):
    srcv = srcversions()
    run.env(srcv)
    check_frozen_predictions()
    blob = {"R1": "x9b_r1", "R2": "x9b_r2"}[reg]
    arm(run, blob, "slots=0x1 entry=0", tag)
    jobs = jobs_9b(reg, cmds, pairs, repeats, a.seed)
    recs = one_job(run, tag, jobs, seed=a.seed, check_every=10)
    verdicts, bad = [], []
    for rec in recs:
        ok, v = evaluate_9b(rec, reg)
        name = L.X9B[rec["job"]["n"]][0]
        verdicts.append({"case": name, "reg": reg, "pair": rec["job"]["pair"], "rep": rec["job"]["rep"],
                         "predicted_ok": ok, "L": v["L"], "H": v["H"], "A": v["A"], "B": v["B"],
                         "reading": classify.reading(v["L"], v["H"], v["A"], v["B"])})
        if not ok:
            bad.append(name)
    run.save(f"{tag}-verdicts.json", verdicts)
    n_ok = sum(v["predicted_ok"] for v in verdicts)
    print(f"{tag}: {len(verdicts)} runs, {n_ok} as predicted; falsified: {sorted(set(bad))}")
    return verdicts


def stage_s5(run, a):
    freeze_predictions() if not FROZEN.exists() else None
    v = stage_9b(run, a, "R1", [1, 2], "s5", repeats=3, pairs=2)
    # X0 and X1 falsified: the table stops (plan 4.2)
    if any(not x["predicted_ok"] for x in v):
        raise StageStop("s5: X0 or X1 falsified: stop the table")


def stage_s6(run, a, reg):
    cmds = sorted(L.X9B)
    v = stage_9b(run, a, reg, cmds, f"s6{reg.lower()}", repeats=3, pairs=2)
    return v


def run_remote_rc(sub, args, timeout=300):
    r = lap(f"sudo -n python3 ~/fwtask/fwtask_run.py {sub} '{json.dumps(args)}'", timeout)
    lines = [ln for ln in r.stdout.splitlines() if ln.startswith("{")]
    if not lines:
        raise StageStop(f"{sub}: no output: {r.stderr.strip()[:300]}")
    return json.loads(lines[-1])


def stage_s12(run, a):
    """Item 12 and Q124 (and S4, a client fill between): the pair of tasks, again after the closed
    code ran, then after a client fill. hold_recovery is set for the round with the client job."""
    run.env(srcversions())
    check_frozen_predictions()
    arm(run, "state", "slots=0x1 entry=0", "s12")
    rounds = [{"kind": "first"}, {"kind": "again", "gap_ms": 1200}, {"kind": "again", "gap_ms": 50}]
    out = run_remote_rc("pair", {"outdir": str(run.dir), "rounds": rounds})
    run.save("s12-pair1.json", out)
    if out.get("stop"):
        unarm(run, "s12-stop")
        raise StageStop(f"s12: {out['stop']}")
    verdicts = []
    for k, r in enumerate(out["rounds"]):
        s = {n: r["slots"][str(n)] if str(n) in r["slots"] else r["slots"][n] for n in (2, 3, 4, 5)}
        v = dict(pclink=s[2][0], p0=s[2][1], p1=s[2][2], p2=s[2][3], p3=s[3][0], r20=s[3][1], r21=s[3][2],
                 i0=s[3][3], i1=s[5][1], sa64=s[4][0], sa100=s[4][1], sa127=s[4][2], sa20=s[4][3], sa24=s[5][0])
        v["preds"] = (v["p0"], v["p1"], v["p2"], v["p3"])
        row = {"round": r["kind"], "k": k, "values": {x: v[x] for x in v if x != "preds"}}
        row["S1"] = classify.evaluate(PRED, "S1_sa_high", **v)
        row["S2"] = classify.evaluate(PRED, "S2_sa_low", **v)
        row["S3"] = classify.evaluate(PRED, "S3_regs", **v)
        row["Q124"] = classify.evaluate(PRED, "Q124_pred", p0=v["p0"], p1=v["p1"], p2=v["p2"], p3=v["p3"], pclink=v["pclink"])
        verdicts.append(row)
    run.save("s12-verdicts.json", verdicts)
    for r in verdicts:
        print(r["round"], {k: r[k] for k in ("S1", "S2", "S3", "Q124")})
    # S4: a client fill between, with hold_recovery set (a hang then leaves its state to read)
    lap("sudo -n sh -c 'echo Y > /sys/kernel/debug/dri/0/sgx/hold_recovery'")
    try:
        out4 = run_remote_rc("pair", {"outdir": str(run.dir), "rounds": [{"kind": "first"}, {"kind": "fill", "gap_ms": 10}]})
    finally:
        lap("sudo -n sh -c 'echo N > /sys/kernel/debug/dri/0/sgx/hold_recovery'")
    run.save("s12-pair2-fill.json", out4)
    if out4.get("stop"):
        unarm(run, "s12-s4-stop")
        raise StageStop(f"s12 S4: {out4['stop']}")
    r = out4["rounds"][-1]
    s = {n: r["slots"][str(n)] for n in (2, 3, 4, 5)}
    ok4 = classify.evaluate(PRED, "S4_after_fill", sa64=s[4][0], sa100=s[4][1], sa127=s[4][2])
    run.save("s12-s4-verdict.json", {"S4_after_fill": ok4, "slots": s, "fill": r.get("fill")})
    print("S4_after_fill:", ok4, r.get("fill"))


def stage_q033q1(run, a):
    run.env(srcversions())
    check_frozen_predictions()
    arm(run, "events", "slots=0xf entry=0,1,2,3", "q033")
    out = run_remote_rc("events", {"trigger": "miscinfo"})
    run.save("q033-q1.json", out)
    log = out["log"]
    hit = out["hit_slots"]
    pa1 = log[4 * hit[0] + 2] if hit else None
    ok = classify.evaluate(PRED, "Q033_q1", hit_slots=hit, pa1=pa1)
    print(f"Q033_q1: {'pass' if ok else 'FALSIFIED'} hit_slots {hit} pa1 {hex(pa1) if pa1 is not None else None} log {[hex(x) for x in log]}")
    run.save("q033-q1-verdict.json", {"Q033_q1": ok, "hit_slots": hit, "pa1": pa1, "log": log})
    if out.get("log_bad") or not out["health"]["ok"] or not out["alive"]["advancing"]:
        raise StageStop(f"q033 q1: unhealthy after: {out.get('log_bad')} {out['health']}")


def stage_s11(run, a):
    run.env(srcversions())
    check_frozen_predictions()
    arm(run, "slow", "slots=0x1 entry=0", "s11")
    jobs = []
    for n in [10000] * 4 + [30000] * 3 + [100000] * 3:
        jobs.append({"n": 1, "params": {"10": n}, "ticks": True, "timeout_ms": 100 if n < 100000 else 300})
    recs = one_job(run, "s11", jobs)
    overlap = sum(1 for r in recs if r["overlap"])
    lost = sum(1 for r in recs if r.get("ticks", 0) < r.get("ticks_expected", 0) - 3)
    ok = classify.evaluate(PRED, "I11_overlap", overlap_runs=overlap, lost_ticks=lost)
    run.save("s11-verdict.json", {"I11_overlap": ok, "overlap_runs": overlap, "lost_runs": lost,
                                  "ms": [r["ms"] for r in recs], "ticks": [r.get("ticks") for r in recs],
                                  "expected": [r.get("ticks_expected") for r in recs]})
    print(f"I11_overlap: {'pass' if ok else 'FALSIFIED'} overlap in {overlap} of {len(recs)} runs, runs with lost ticks {lost}; ms {[round(r['ms']) for r in recs]}")


def stage_s13(run, a):
    run.env(srcversions())
    check_frozen_predictions()
    resets = 0
    for t in a.trc:
        hz = ",trc_hazard=1" if t >= 49 else ""
        line = f"slots=0x1 entry=0 trc={t}" + (" trc_hazard=1" if t >= 49 else "")
        try:
            arm(run, f"trc_{t:02d}", line, f"s13-T{t}")
        except StageStop as e:
            run.save(f"s13-T{t}-armfail.txt", str(e))
            if t >= 49:
                print(f"I13_T{t:02d}: hang predicted: {e}")
                unarm(run, f"s13-T{t}")
                continue
            raise
        recs = one_job(run, f"s13-T{t}", [{"n": 1, "params": {"3": 0}, "timeout_ms": 100}])
        s = recs[0]["slot"]
        ok = classify.evaluate(PRED, f"I13_T{t:02d}", marker_back=s[0], hang=False)
        print(f"I13_T{t:02d}: {'as predicted' if ok else 'FALSIFIED'} slot {[hex(x) for x in s]}")
        run.save(f"s13-T{t}-verdict.json", {"ok": ok, "slot": s})


STAGES = {"s1": stage_s1, "s2": stage_s2, "s3": stage_s3, "s4": stage_s4, "s5": stage_s5,
          "s6r1": lambda r, a: stage_s6(r, a, "R1"), "s6r2": lambda r, a: stage_s6(r, a, "R2"), "s12": stage_s12,
          "q033q1": stage_q033q1, "s11": stage_s11, "s13": stage_s13}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("stage")
    ap.add_argument("--seed", type=int, default=1129)
    ap.add_argument("--trc", type=int, nargs="*", default=[8])
    ap.add_argument("--freeze", action="store_true", help="freeze predictions.toml now and exit")
    a = ap.parse_args()
    if a.freeze:
        freeze_predictions()
        return 0
    run = Run(a.name, a.stage)
    try:
        upload_runner()
        STAGES[a.stage](run, a)
        run.kernel_log()
        print(f"stage {a.stage}: PASSED ({a.name})")
        return 0
    except Frozen as e:
        print(f"LAPTOP DID NOT ANSWER: STOP. Report; boot and run nothing further. {e}")
        return 99
    except StageStop as e:
        try:
            run.kernel_log()
        except Exception:
            pass
        print(f"stage {a.stage}: STOPPED: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
