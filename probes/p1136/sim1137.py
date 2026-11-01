#!/usr/bin/env python3
"""sgx-sim (pysgx, built into tables/target) as the reference for the firmware sources of
gen_1137.py: runs every job plan of judge1137.py on the simulator and judges it with the same
code.  What it shows: encodings, control flow, patching, the page layout, the expected readbacks.
Nothing about hardware."""
import sys, pathlib, collections
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import simlib as m
import judge1137 as J
S, L, F = m.S, m.L, m.F

S._source = lambda name: (HERE / "asm" / (name + ".s")).read_text()
S.load = lambda name: F.parse_blob(F.build_blob_text(S._source(name)))


def page_of(r):
    return r.mem


def run(task, cmd, params, **kw):
    return S.run(task, cmd=cmd, params=params, r0=0, max_steps=3_000_000, **kw)


def main():
    res = collections.OrderedDict()
    # item 8
    ok = 0
    jobs = J.jobs_pred(reps=1)
    for j in jobs:
        r = run("p1137_pred", j["n"], j["params"])
        ok += J.judge_pred(j, r.slot(j["n"] if False else 0) if False else r.mem[L.slot(j["n"]):L.slot(j["n"]) + 4])
    res["item 8 pred (sim, %d jobs)" % len(jobs)] = "%d/%d" % (ok, len(jobs))
    for item, task, gen in (("item 10 imm", "p1137_imm", J.jobs_imm),):
        jobs = [j for j in gen() if j["task"] == "imm"]
        ok = sum(J.judge_imm(j, run(task, 1, j["params"]).mem)[0] for j in jobs)
        res["%s (sim, %d jobs)" % (item, len(jobs))] = "%d/%d" % (ok, len(jobs))
    jobs = [j for j in J.jobs_imm() if j["task"] == "wide"]
    ok = sum(J.judge_imm(j, run("p1137_wide", 1, j["params"]).mem)[0] for j in jobs)
    res["item 10 wide (sim, %d jobs)" % len(jobs)] = "%d/%d" % (ok, len(jobs))
    jobs = J.jobs_regs(reps=1)
    ok = 0
    for j in jobs:
        r = run("p1137_" + j["task"], j["n"], j["params"])
        ok += J.judge_regs(j, r.mem)[0]
    res["item 11 regs (sim, %d jobs)" % len(jobs)] = "%d/%d" % (ok, len(jobs))
    jobs = J.jobs_wdf(reps=1)
    ok = 0
    ctl = None
    for j in jobs:
        if j.get("control"):
            try:
                run("p1137_wdf", j["n"], j["params"])
            except Exception as e:           # the simulator refuses a read before the wdf
                ctl = "sim stops: " + str(e)[-70:]
            continue
        r = run("p1137_wdf", j["n"], j["params"])
        ok += J.judge_wdf(j, r.mem)[0]
    res["item 12 wdf (sim, %d jobs)" % (len(jobs) - 1)] = "%d/%d" % (ok, len(jobs) - 1)
    res["item 12 control (sim: ordered model)"] = str(ctl)
    # item 14
    for e in range(4):
        j = J.jobs_slow(50)
        extra = {}
        r = S.run("p1137_slow4", cmd=0, entry=e, pa=(0x11, 0x02000000, 0x01061a70), params=j["params"], r0=0,
                  max_steps=3_000_000)
        res["item 14 entry %d, idle (sim)" % e] = str(J.judge_slow(r.mem)["passes"])
    j = J.jobs_slow(50)
    j["params"][L.STATE] = 1
    r = S.run("p1137_slow4", cmd=0, entry=2, pa=(0x11, 0x02000000, 0x01061a70), params=j["params"], r0=0,
              mem_extra={L.STATE: 1}, max_steps=3_000_000)
    res["item 14 entry 2 while busy (sim)"] = str(J.judge_slow(r.mem))
    r = S.run("p1137_slow4", cmd=1, entry=0, params=J.jobs_slow(100)["params"], r0=0, max_steps=3_000_000)
    res["item 14 slow loop n=100 (sim)"] = str(J.judge_slow(r.mem)["passes"]) + " state=%d" % r.mem[L.STATE]
    r = S.run("p1137_strjob", cmd=1, params={8: 0x1a5a5, 9: 0x2b, 10: 20}, r0=0, max_steps=100000)
    res["item 15 strjob (sim, FwBus ordered model)"] = str([hex(x) for x in r.slot(1)])
    for k, v in res.items():
        print("%-45s %s" % (k, v))


if __name__ == "__main__":
    main()
