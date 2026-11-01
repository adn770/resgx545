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
import classify1129  # noqa: E402
import classify_b2  # noqa: E402
import fwtask  # noqa: E402
import layout as L  # noqa: E402

HOST = os.environ.get("FWTASK_HOST", "jtorra@10.42.0.2")     # the laptop, over the cable
SSH = ["ssh", "-o", "HostKeyAlias=cedar", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10",
       "-o", "ControlMaster=auto", "-o", "ControlPath=/tmp/fwtask-%r@%h", "-o", "ControlPersist=120",
       HOST]
DATA = pathlib.Path(os.environ.get("RESGX545_DATA", ROOT.parent / "resgx545-data")) / "firmware-tasks"
LINUX = pathlib.Path(os.environ.get("RESGX545_LINUX", ROOT.parent / "linux"))     # the fork
PRED = HERE / "predictions-1130.toml"           # the 11.30 table; the 11.29 stages read PRED29
FROZEN = HERE / "predictions-1130.sha256"
PRED29 = HERE / "predictions.toml"
FROZEN29 = HERE / "predictions.sha256"


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
        txt = ["# phase 11.30 run environment", f'name = "{self.name}"', f'stage = "{self.stage}"',
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


def check_frozen_predictions(pred=None, frozen=None, cl=None):
    """The table is frozen: its sha256 file exists and is the file's (the 11.30 table by default)."""
    pred, frozen, cl = pred or PRED, frozen or FROZEN, cl or classify
    if not (frozen.exists() and pred.exists() and frozen.read_text().strip() == cl.sha256(pred)):
        raise StageStop(f"{pred.name} is not frozen ({frozen.name} missing or different): "
                        "freeze it before the first run")


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
    return classify1129.evaluate(PRED29, rid, **v), v


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
    ok = classify1129.evaluate(PRED29, "S2_null", ticks_per_s=out["rate_hz"], fill_diff=0 if g["ok"] else 1,
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
    ok = classify1129.evaluate(PRED29, "S3_mem", done=recs[0]["done"], marker=s[3], pa1=s[1], pa2=s[2])
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
    ok = classify1129.evaluate(PRED29, "S4_ldr", core_id=s[0], host_core_id=core_id, core_rev=s[1],
                           host_core_rev=core_rev, timer_ok=s[2] not in (0, L.INITFILL))
    print(f"S4_ldr: {'pass' if ok else 'FAIL'} {[hex(x) for x in s]} host {hex(core_id)} {hex(core_rev)}")
    run.save("s4-verdict.json", {"S4_ldr": ok, "slot": s})
    if not ok:
        raise StageStop("s4 failed")


def freeze_predictions():
    """Write the 11.30 tables (stage B and the rest; stage B2) and their sha256 files. Freeze the
    B2 table only after stage B's results are read: its rows may depend on them."""
    for pred, frozen, cl in ((PRED, FROZEN, classify), (PRED_B2, FROZEN_B2, classify_b2)):
        pred.write_text(cl.render())
        sha = classify.sha256(pred)
        frozen.write_text(sha + "\n")
        print(f"{pred.name} frozen, sha256 {sha}")


def freeze_predictions1129():
    PRED29.write_text(classify1129.render())
    sha = classify1129.sha256(PRED29)
    FROZEN29.write_text(sha + "\n")
    print(f"phase 11.29 predictions.toml frozen, sha256 {sha}")
    return sha


def stage_9b(run, a, reg, cmds, tag, repeats=3, pairs=2):
    srcv = srcversions()
    run.env(srcv)
    check_frozen_predictions(PRED29, FROZEN29, classify1129)
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
                         "reading": classify1129.reading(v["L"], v["H"], v["A"], v["B"])})
        if not ok:
            bad.append(name)
    run.save(f"{tag}-verdicts.json", verdicts)
    n_ok = sum(v["predicted_ok"] for v in verdicts)
    print(f"{tag}: {len(verdicts)} runs, {n_ok} as predicted; falsified: {sorted(set(bad))}")
    return verdicts


def stage_s5(run, a):
    freeze_predictions1129() if not FROZEN29.exists() else None
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


def b_entry(r):
    s = r["slots"]
    return dict(pclink=s["10"][0], p=tuple(s["10"][1:4]) + (s["11"][0],), r20=s["11"][1], r21=s["11"][2],
                i0=s["11"][3], i1=s["13"][1], sa=tuple(s["12"]) + (s["13"][0],))

def judge_b(run, ctl, out, marks, pat):
    c0, c1 = b_entry(ctl["rounds"][0]), b_entry(ctl["rounds"][1])
    verdicts = []
    for k in range(3):
        w, g, f = out["rounds"][3 * k], out["rounds"][3 * k + 1], out["rounds"][3 * k + 2]
        m = marks[k]
        ent = b_entry(w)
        row = {"round": k, "next": ent, "gap_sa": b_entry(g)["sa"], "fill_sa": b_entry(f)["sa"], "markers": m}
        sa_m = (m[0], m[1], m[2], m[3], m[4])            # sa64, sa100, sa127, sa20, sa24
        row["B_sa_high_next"] = classify.evaluate(PRED, "B_sa_high_next", sa_high=ent["sa"][:3], markers_high=tuple(m[:3]))
        row["B_sa_low_next"] = classify.evaluate(PRED, "B_sa_low_next", sa_low=ent["sa"][3:], markers_low=tuple(m[3:5]))
        row["B_sa_gap"] = classify.evaluate(PRED, "B_sa_gap", sa_all=b_entry(g)["sa"], markers_all=sa_m)
        row["B_sa_fill"] = classify.evaluate(PRED, "B_sa_fill", sa_all=b_entry(f)["sa"], markers_all=sa_m)
        row["B_r_gone"] = classify.evaluate(PRED, "B_r_gone", r_vals=(ent["r20"], ent["r21"]), markers_r=(m[5], m[6]))
        row["B_i_kept"] = classify.evaluate(PRED, "B_i_kept", i_vals=(ent["i0"], ent["i1"]), markers_i=(m[7], m[8]))
        row["B_p_gone"] = classify.evaluate(PRED, "B_p_gone", p_vals=ent["p"], p_pattern=tuple(pat))
        verdicts.append(row)
    rates = [r["rate_hz"] for r in out["rounds"]]
    alive_ok = all(r["alive"]["advancing"] for r in out["rounds"])
    wd = all(out["rounds"][3 * k].get("writer_ms") is not None for k in range(3))
    rd = all(r["reader_cleared"] for r in out["rounds"])
    pcl = [c0["pclink"], c1["pclink"]] + [b_entry(out["rounds"][3 * k])["pclink"] for k in range(3)]
    ctl_cmp = lambda c: (c["r20"], c["r21"], c["i0"], c["i1"], c["p"], c["pclink"])
    summ = {"B_alive": classify.evaluate(PRED, "B_alive", rounds_alive=alive_ok, writer_done=wd, reader_done=rd, min_rate=min(rates)),
            "B_ctl_stable": classify.evaluate(PRED, "B_ctl_stable", ctl_a=ctl_cmp(c0), ctl_b=ctl_cmp(c1)),
            "B_pclink_const": classify.evaluate(PRED, "B_pclink_const", pclinks=pcl),
            "rates": rates, "pclinks": [hex(x) for x in pcl], "fill": [r.get("fill") for r in out["rounds"] if r["kind"] == "fill"]}
    run.save("b-verdicts.json", {"rounds": verdicts, "summary": summ})
    for v in verdicts:
        print("round", v["round"], {k: v[k] for k in v if k.startswith("B_")})
    print(summ)
    # the stage's own criterion: the writer and the reader ran and the tick went on; the
    # predictions are judged separately
    if not (alive_ok and wd and rd):
        raise StageStop("b: the tail-calling pair did not run as a pair")


def stage_b(run, a):
    """Item 12 and Q124 with the tail-calling writer (state2.s): 2 controls, then 3 rounds of
    writer + next-event reader, a reader after 1200 ms of closed ticks, a reader after a client fill."""
    run.env(srcversions())
    check_frozen_predictions()
    arm(run, "state2", "slots=0x1 entry=0", "b")
    rng = random.Random(a.seed)
    lap("sudo -n sh -c 'echo Y > /sys/kernel/debug/dri/0/sgx/hold_recovery'")
    try:
        ctl = run_remote_rc("tailpair", {"outdir": str(run.dir), "rounds": [{"kind": "control"}, {"kind": "control"}]})
        run.save("b-controls.json", ctl)
        if ctl.get("stop"):
            raise StageStop(f"b controls: {ctl['stop']}")

        c0, c1 = b_entry(ctl["rounds"][0]), b_entry(ctl["rounds"][1])
        pat = [1 - x for x in c0["p"]]
        seen = {v for c in (c0, c1) for v in (c["r20"], c["r21"], c["i0"], c["i1"]) + c["sa"]}
        rounds, marks = [], []
        for k in range(3):
            vals = []
            while len(vals) < 9:
                v = rng.getrandbits(32) | 0x80000000
                if v not in seen and v not in vals and v != L.INITFILL:
                    vals.append(v)
            marks.append(vals)
            rounds += [{"kind": "write", "vals": vals, "pflags": pat}, {"kind": "gap", "gap_ms": 1200}, {"kind": "fill"}]
        out = run_remote_rc("tailpair", {"outdir": str(run.dir), "rounds": rounds}, timeout=300)
        run.save("b-rounds.json", out)
        run.save("b-markers.json", {"markers": marks, "p_pattern": pat, "controls": [c0, c1]})
        if out.get("stop"):
            raise StageStop(f"b: {out['stop']}")
        judge_b(run, ctl, out, marks, pat)
    finally:
        lap("sudo -n sh -c 'echo N > /sys/kernel/debug/dri/0/sgx/hold_recovery'")


PRED_B2 = HERE / "predictions-1130-b2.toml"
FROZEN_B2 = HERE / "predictions-1130-b2.sha256"


def judge_b2(run, rounds, marks, pat):
    """rounds: [control, write, control, write, ...] (the write rounds carry the cmd)."""
    lst = {c: dict(pcl_next=[], pcl_ctl=[], p1_next=[], p1_ctl=[], sa_extra=[], sa_extra_marked=[], sa64_next=[]) for c in (1, 2, 3, 4)}
    rows = []
    for k in range(0, len(rounds), 2):
        ctl, w = b_entry_x(rounds[k]), rounds[k + 1]
        ent = b_entry_x(w)
        cmd = w["cmd"]
        d = lst[cmd]
        d["pcl_next"].append(ent["pclink"]); d["pcl_ctl"].append(ctl["pclink"])
        d["p1_next"].append(ent["p"][1]); d["p1_ctl"].append(ctl["p"][1])
        if cmd in (1, 4):
            m = marks[k // 2]
            d["sa_extra"] += [ent["sa65"], ent["sa63"]]; d["sa_extra_marked"] += [m[9], m[10]]
            d["sa64_next"].append(ent["sa"][0])
        rows.append({"cmd": cmd, "ctl": ctl, "next": ent})
    cat = lambda *cs: {key: sum((lst[c][key] for c in cs), []) for key in lst[1]}
    ok = {"B2_armonly": classify.evaluate(PRED_B2, "B2_armonly", **lst[2]),
          "B2_ponly": classify.evaluate(PRED_B2, "B2_ponly", **lst[3]),
          "B2_saonly": classify.evaluate(PRED_B2, "B2_saonly", **lst[4]),
          "B2_full": classify.evaluate(PRED_B2, "B2_full", **lst[1]),
          "B2_sa63_65": classify.evaluate(PRED_B2, "B2_sa63_65", **cat(1, 4)),
          "B2_sa64": classify.evaluate(PRED_B2, "B2_sa64", **cat(1, 4))}
    run.save("b2-verdicts.json", {"rows": rows, "lists": {str(c): lst[c] for c in lst}, "predictions": ok})
    for c in (1, 2, 3, 4):
        print("cmd", c, {k: [hex(x) if isinstance(x, int) and x > 9 else x for x in v] for k, v in lst[c].items() if k in ("pcl_next", "pcl_ctl", "p1_next", "p1_ctl")})
    print(ok)


def b_entry_x(r):
    e = b_entry(r)
    s = r["slots"]
    e["sa65"], e["sa63"] = s["13"][2], s["13"][3]
    return e


def stage_b2(run, a):
    """Stage B2: the writer variants of state3.s (cmd 1 all, 2 arm only, 3 p only, 4 sa/r/i only), 3 each in a
    seeded shuffle, every one preceded by a plain reader (the control of that moment)."""
    run.env(srcversions())
    if not (FROZEN_B2.exists() and FROZEN_B2.read_text().strip() == classify.sha256(PRED_B2)):
        raise StageStop("predictions-1130-b2.toml is not frozen")
    arm(run, "state3", "slots=0x1 entry=0", "b2")
    rng = random.Random(a.seed)
    lap("sudo -n sh -c 'echo Y > /sys/kernel/debug/dri/0/sgx/hold_recovery'")
    try:
        c = run_remote_rc("tailpair", {"outdir": str(run.dir), "rounds": [{"kind": "control"}]})
        c0 = b_entry_x(c["rounds"][0])
        pat = [1 - x for x in c0["p"]]
        order = [1, 2, 3, 4] * 3
        rng.shuffle(order)
        seen = set(c0["sa"]) | {c0["r20"], c0["r21"], c0["i0"], c0["i1"], c0["sa65"], c0["sa63"]}
        rounds, marks = [], []
        for cmd in order:
            vals = []
            while len(vals) < 11:
                v = rng.getrandbits(32) | 0x80000000
                if v not in seen and v not in vals and v != L.INITFILL and v != 2:
                    vals.append(v)
            marks.append(vals)
            rounds += [{"kind": "control"}, {"kind": "write", "cmd": cmd, "vals": vals[:9], "pflags": pat, "extra": vals[9:11]}]
        out = run_remote_rc("tailpair", {"outdir": str(run.dir), "rounds": rounds}, timeout=300)
        run.save("b2-rounds.json", out)
        run.save("b2-markers.json", {"order": order, "markers": marks, "p_pattern": pat, "first_control": c0})
        if out.get("stop"):
            raise StageStop(f"b2: {out['stop']}")
        for rd_, cm in zip(out["rounds"][1::2], order):
            rd_["cmd"] = cm
        judge_b2(run, out["rounds"], marks, pat)
        if not all(r["alive"]["advancing"] and r["reader_cleared"] for r in out["rounds"]):
            raise StageStop("b2: a round did not run")
    finally:
        lap("sudo -n sh -c 'echo N > /sys/kernel/debug/dri/0/sgx/hold_recovery'")


def stage_q033q1(run, a):
    run.env(srcversions())
    check_frozen_predictions()
    arm(run, "events_m", "slots=0xf entry=0,1,2,3", "q033")
    out = run_remote_rc("events", {"trigger": "miscinfo", "quiet_ms": 50})
    run.save("q033-q1.json", out)
    log, quiet = out["log"], out["quiet_log"]
    hit = out["hit_slots"]
    qhits = [k for k in range(4) if quiet[4 * k] == 1]
    pa1 = log[4 * hit[0] + 2] if hit else 0
    ok = classify.evaluate(PRED, "Q033_q1m", hit_slots=hit, pa1=pa1)
    okq = classify.evaluate(PRED, "Q033_quiet", quiet_hits=qhits)
    print(f"Q033_quiet: {'held' if okq else 'FALSIFIED'} quiet hits {qhits} quiet log {[hex(x) for x in quiet]}")
    print(f"Q033_q1m: {'held' if ok else 'FALSIFIED'} hit_slots {hit} pa1 {hex(pa1)} log {[hex(x) for x in log]}")
    run.save("q033-q1-verdict.json", {"Q033_q1m": ok, "Q033_quiet": okq, "hit_slots": hit, "pa1": pa1, "log": log,
                                      "quiet": quiet, "quiet_hits": qhits})
    if out.get("log_bad") or not out["health"]["ok"] or not out["alive"]["advancing"]:
        raise StageStop(f"q033 q1: unhealthy after: {out.get('log_bad')} {out['health']}")


def stage_q033q2(run, a):
    """Q033 Q2: a triangle on the unmodified render node with the event stubs in the path."""
    run.env(srcversions())
    check_frozen_predictions()
    arm(run, "events_m", "slots=0xf entry=0,1,2,3", "q033q2")
    lap("sudo -n sh -c 'echo Y > /sys/kernel/debug/dri/0/sgx/hold_recovery'")
    try:
        out = run_remote_rc("events", {"trigger": "tri", "quiet_ms": 0})
    finally:
        lap("sudo -n sh -c 'echo N > /sys/kernel/debug/dri/0/sgx/hold_recovery'")
    run.save("q033-q2.json", out)
    log = out["log"]
    hit = out["hit_slots"]
    pa1s = log[4 * 1 + 2]
    ok = classify.evaluate(PRED, "Q033_q2", hit_slots=hit, pa1_slot1=pa1s)
    print(f"Q033_q2: {'held' if ok else 'FALSIFIED'} hit_slots {hit} log {[hex(x) for x in log]} tri {out['trigger']}")
    run.save("q033-q2-verdict.json", {"Q033_q2": ok, "hit_slots": hit, "log": log})
    if out.get("log_bad") or not out["health"]["ok"] or not out["alive"]["advancing"]:
        raise StageStop(f"q033 q2: unhealthy after: {out.get('log_bad')} {out['health']}")


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


TRC_HAZARD_FROM = 32     # the lowest T that fails to arm without the hazard word (E540: the arm of 32)


def trc_arm_line(t, hazard_ok=False):
    """The own_arm line of a TRC of T. From 32 up it takes the hazard word, which only an explicit
    --trc-hazard gives (never by default: the arm with it has not been approved)."""
    if t < TRC_HAZARD_FROM:
        return f"slots=0x1 entry=0 trc={t}"
    if not hazard_ok:
        raise StageStop(f"TRC {t} needs the hazard word; not armed without --trc-hazard")
    return f"slots=0x1 entry=0 trc={t} trc_hazard=1"


def stage_s13(run, a):
    run.env(srcversions())
    check_frozen_predictions()
    hazard_ok = getattr(a, "trc_hazard", False)
    lines = [trc_arm_line(t, hazard_ok) for t in a.trc]       # refuse before arming anything
    for t, line in zip(a.trc, lines):
        try:
            arm(run, f"trc_{t:02d}", line, f"s13-T{t}")
        except StageStop as e:
            run.save(f"s13-T{t}-armfail.txt", str(e))
            if t >= 49:
                ok = classify.evaluate(PRED, f"I13_T{t:02d}", hang=True)
                print(f"I13_T{t:02d}: hang as predicted ({ok}): {e}")
                run.save(f"s13-T{t}-verdict.json", {"ok": ok, "hang": True, "why": str(e)})
                unarm(run, f"s13-T{t}")
                print("a hang ends the stage (no further T)")
                break
            raise
        recs = one_job(run, f"s13-T{t}", [{"n": 1, "params": {"3": 0}, "timeout_ms": 100}])
        s = recs[0]["slot"]
        rows = {}
        rows[f"I13_T{t:02d}"] = classify.evaluate(PRED, f"I13_T{t:02d}", marker_back=s[0], hang=False)
        if t in (9, 12, 16, 24):
            rows[f"I13_P{t:02d}"] = classify.evaluate(PRED, f"I13_P{t:02d}", past_back=s[1])
        print(f"I13 T{t}: {rows} slot (top, past, r0) {[hex(x) for x in s[:3]]}")
        run.save(f"s13-T{t}-verdict.json", {"rows": rows, "slot": s})


STAGES = {"b": stage_b, "b2": stage_b2, "q033q2": stage_q033q2, "s1": stage_s1, "s2": stage_s2, "s3": stage_s3, "s4": stage_s4, "s5": stage_s5,
          "s6r1": lambda r, a: stage_s6(r, a, "R1"), "s6r2": lambda r, a: stage_s6(r, a, "R2"),
          "q033q1": stage_q033q1, "s11": stage_s11, "s13": stage_s13}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("stage")
    ap.add_argument("--seed", type=int, default=1130)
    ap.add_argument("--trc", type=int, nargs="*", default=[8])
    ap.add_argument("--trc-hazard", action="store_true",
                    help="give the hazard word for a TRC of 32 or more (off: such a T is refused)")
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
