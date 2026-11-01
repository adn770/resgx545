#!/usr/bin/env python3
"""Phase 11.37 (prepared, NOT RUN): the Mac side of the firmware (EDM) stages of tables/.  Modelled on
the landed run_1133.py: one stage per call, the frozen predictions checked first, the srcversions
compared, a reset and the gate after every arm, stop at the first trigger and never go on past it.

    run_1137.py NAME STAGE [--dry-run]
    stages (risk order, run one at a time): f8 f10 f11 f12 f15 f14a f14b f14c

--dry-run prints every arm line, job and page read and touches nothing (no ssh).  The landed
tools/fwtask is imported read only.  Every job's parameters, markers and sentinels come from
judge1137.py; the verdicts are written to out/NAME/ and printed as counts."""
import argparse, hashlib, json, os, pathlib, subprocess, sys, time, zlib
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
R = pathlib.Path.home() / "src/resgx545"
sys.path.insert(0, str(R / "tools/fwtask"))
sys.path.insert(0, str(HERE))
import judge1137 as J  # noqa: E402

PRED, FROZEN = HERE / "predictions-1137.toml", HERE / "predictions-1137.sha256"
MANIFEST = HERE / "manifest-1137.sha256"
ARM = {"p1137_pred": "slots=0x1 entry=0", "p1137_imm": "slots=0x1 entry=0", "p1137_wide": "slots=0x1 entry=0",
       "p1137_regsA": "slots=0x1 entry=0 trc=31", "p1137_regsB": "slots=0x1 entry=0 trc=31",
       "p1137_wdf": "slots=0x1 entry=0 trc=31", "p1137_strjob": "slots=0x1 entry=0",
       "p1137_slow4": "slots=0xf entry=0,1,2,3"}


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def check_frozen():
    if not (FROZEN.exists() and FROZEN.read_text().split()[0] == sha(PRED)):
        raise SystemExit("predictions-1137.toml is not the frozen file: stop")
    for line in MANIFEST.read_text().splitlines():
        h, f = line.split()
        if sha(HERE / f) != h:
            raise SystemExit("manifest mismatch for %s: the material changed after the freeze" % f)


class Ctx:
    def __init__(self, a):
        self.dry, self.name = a.dry_run, a.name
        self.out = HERE / "out" / a.name
        if not self.dry:
            self.out.mkdir(parents=True, exist_ok=True)
        self.verdicts = {}
        if not self.dry:
            import run_stage as RS
            self.RS = RS

    def remote(self, sub, args=None, timeout=300):
        if self.dry:
            print("   remote %s %s" % (sub, json.dumps(args)[:100]))
            return {"ok": True, "records": [], "page": [0] * 1024}
        return self.RS.run_remote(sub, args, timeout)

    def ext(self, sub, args, timeout=120):
        if self.dry:
            print("   ext %s %s" % (sub, json.dumps(args)[:100]))
            return {"done": True, "page": [0] * 1024, "ticks": 0, "ticks_expected": 0}
        r = self.RS.lap("sudo -n python3 ~/fwtask/fwext1137.py %s '%s'" % (sub, json.dumps(args)), timeout)
        return json.loads(r.stdout.strip().splitlines()[-1])

    def arm(self, blob, tag):
        line = ARM[blob]
        print("arm %s '%s'" % (blob, line))
        if self.dry:
            return
        data = (HERE / "asm" / (blob + ".blob")).read_bytes()
        r = subprocess.run(self.RS.SSH + ["mkdir -p ~/fwtask && cat > ~/fwtask/%s.blob" % blob], input=data,
                           capture_output=True)
        if r.returncode:
            raise self.RS.StageStop("upload failed")
        out = self.remote("arm", {"blob": "/home/jtorra/fwtask/%s.blob" % blob, "arm": line})
        if not out.get("ok"):
            raise self.RS.StageStop("arm %s refused or unhealthy: %s" % (blob, out))
        self.save(tag + "-arm.json", out)

    def reset(self, tag):
        print("reset to stock + gate")
        if self.dry:
            return
        o = self.remote("reset")
        g = self.remote("gate")
        self.save(tag + "-reset.json", {"reset": o, "gate": g})
        if not (o.get("ok") and g.get("ok")):
            raise self.RS.StageStop("%s: reset or gate not exact; stop" % tag)

    def save(self, fname, obj):
        if not self.dry:
            (self.out / fname).write_text(json.dumps(obj, indent=1, default=str))

    def job(self, j, tag, timeout_ms=100, **kw):
        a = {"name": self.name, "outdir": str(self.out), "seed": 1137,
             "jobs": [{"n": j["n"], "params": j["params"], "runid": 0x3700 + (zlib.crc32(tag.encode()) & 0xff),
                       "timeout_ms": timeout_ms, **kw}]}
        r = self.remote("run", a, 200)
        if not self.dry and (r.get("stop") or not r.get("records")):
            raise self.RS.StageStop("%s: stop %s" % (tag, r.get("stop")))
        page = self.remote("page")["page"]
        return (r["records"][0] if r.get("records") else {"slot": [0] * 4}), page


def stage_f8(c):
    c.arm("p1137_pred", "f8")
    jobs = J.jobs_pred()
    ok = 0
    for i, j in enumerate(jobs):
        rec, _ = c.job(j, "f8-%d" % i)
        good = J.judge_pred(j, rec["slot"])
        ok += good
        c.verdicts[i] = {"n": j["n"], "P": j["P"], "got": rec["slot"], "ok": good}
    print("P37_F8: %d of %d jobs follow p0" % (ok, len(jobs)))
    c.reset("f8")


def stage_f10(c):
    for blob, task in (("p1137_imm", "imm"), ("p1137_wide", "wide")):
        c.arm(blob, "f10-" + task)
        for j in [j for j in J.jobs_imm() if j["task"] == task]:
            _, page = c.job(j, "f10-%s-%s" % (task, j["kind"]))
            ok, bad = J.judge_imm(j, page)
            print("P37_F10 %s %s: %s %s" % (task, j["kind"], "pass" if ok else "FALSIFIED", bad[:8]))
            c.verdicts["%s-%s" % (task, j["kind"])] = {"ok": ok, "bad": bad}
        c.reset("f10-" + task)


def stage_f11(c):
    for blob in ("p1137_regsB", "p1137_regsA"):
        c.arm(blob, "f11-" + blob)
        for i, j in enumerate([j for j in J.jobs_regs() if "p1137_" + j["task"] == blob]):
            _, page = c.job(j, "f11-%s-%d" % (blob, i))
            ok, bad, v = J.judge_regs(j, page)
            print("P37_F11 %s cmd %d: %s bad=%s %s" % (j["task"], j["n"], "pass" if ok else "FALSIFIED", bad[:10], v))
            c.verdicts["%s-%d" % (blob, i)] = {"ok": ok, "bad": bad, "v": v}
        c.reset("f11-" + blob)


def stage_f12(c):
    c.arm("p1137_wdf", "f12")
    for i, j in enumerate(J.jobs_wdf()):
        _, page = c.job(j, "f12-%d" % i)
        v = J.judge_wdf(j, page)
        print("P37_F12 N=%d%s: %s" % (j["N"], " control" if j.get("control") else "", v if j.get("control") else v[0]))
        c.verdicts[i] = {"N": j["N"], "v": v}
    c.reset("f12")


def stage_f15(c):
    """allow-list registers 0x0814 and 0x0a78 only, a client fill running during the spin."""
    c.arm("p1137_strjob", "f15")
    rng = J.Draw(1142)
    for i in range(3):
        v1 = (rng() & 0x1ffff) | 0x10000
        v2 = 0x20 + 3 * i + 1
        p = {8: v1, 9: v2, 10: 30000}
        r = c.ext("slowevent", {"cmd": 1, "params": p, "trigger": "fill", "delay_ms": 0.5, "timeout_ms": 300,
                                "runid": 0x3750 + i})
        s = r["page"][0x44:0x48] if r.get("page") else None
        print("P37_F15 job %d: V1 %#x V2 %#x reads %s fill %s" % (i, v1, v2, [hex(x) for x in (s or [])], r.get("trigger")))
        c.verdicts[i] = {"V1": v1, "V2": v2, "slot": s, "trigger": r.get("trigger")}
    c.reset("f15")


def stage_f14(c, mode):
    c.arm("p1137_slow4", "f14" + mode)
    for n_iter, reps in ((10000, 2), (100000, 3)):
        for k in range(reps):
            j = J.jobs_slow(n_iter, 1141 + k)
            trig = {"a": "none", "b": "kick", "c": "tri"}[mode]
            if mode == "c":
                c.remote_hold("Y")
            r = c.ext("slowevent", {"cmd": 1, "params": j["params"], "trigger": trig,
                                    "delay_ms": 2 if n_iter >= 100000 else 0.3, "timeout_ms": 400,
                                    "runid": 0x3760 + k})
            if mode == "c":
                c.remote_hold("N")
            v = J.judge_slow(r["page"]) if r.get("page") else None
            print("P37_F14%s n=%d: %s ticks %s expected %.1f done %s" % (mode, n_iter, v, r.get("ticks"),
                                                                        r.get("ticks_expected", 0), r.get("done")))
            c.verdicts["%d-%d" % (n_iter, k)] = {"v": v, "ticks": r.get("ticks"), "exp": r.get("ticks_expected")}
            if not r.get("done") or r.get("log_bad"):
                c.reset("f14%s-stop" % mode)
                raise SystemExit("f14%s: trigger; reset and gate done; stop" % mode)
    c.reset("f14" + mode)


def remote_hold(self, val):
    if self.dry:
        print("   hold_recovery %s" % val)
        return
    self.RS.lap("sudo -n sh -c 'echo %s > /sys/kernel/debug/dri/0/sgx/hold_recovery'" % val)


Ctx.remote_hold = remote_hold
STAGES = {"f8": stage_f8, "f10": stage_f10, "f11": stage_f11, "f12": stage_f12, "f15": stage_f15,
          "f14a": lambda c: stage_f14(c, "a"), "f14b": lambda c: stage_f14(c, "b"),
          "f14c": lambda c: stage_f14(c, "c")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("stage", choices=sorted(STAGES))
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    check_frozen()
    c = Ctx(a)
    if not a.dry_run:
        srcv = c.RS.srcversions()
        c.save("env.json", {"srcversions": srcv, "predictions_sha256": sha(PRED), "stage": a.stage})
        c.RS.upload_runner()
        subprocess.run(c.RS.SSH + ["mkdir -p ~/fwtask && cat > ~/fwtask/fwext1137.py"],
                       input=(HERE / "fwext1137.py").read_bytes(), capture_output=True)
    try:
        STAGES[a.stage](c)
    finally:
        c.save("verdicts-%s.json" % a.stage, c.verdicts)
    return 0


if __name__ == "__main__":
    sys.exit(main())
