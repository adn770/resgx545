#!/usr/bin/env python3
"""Phase 11.37 (prepared, not run): the jobs, the expected readback and the judge of every
firmware task of gen_1137.py.  Pure functions; the same code judges sgx-sim runs (sim1137.py) and,
later, laptop pages.  Every job has markers of its own (never INITFILL, never one already used)
and every result dword is pre-filled with a sentinel of its own, so a stale read cannot pass."""
import json, pathlib, random, sys
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
LAY = json.load(open(HERE / "layout1137.json"))
IN1, IN2, OUT1, OUT2 = 256, 384, 512, 640
CNT, OVL, ARR = 960, 964, 968
A_, B_ = 0x0a11ce11, 0x0b22ce22
HIT, MISS = 1, 2
INITFILL = 0xdeadc0de
GAPS = [tuple(g) for g in LAY["gaps"]]
WIDE = LAY["wide"]
NS = LAY["NS"]
OFF = [tuple(x) for x in LAY["off_of"]]


class Draw:
    """Unique 32-bit values (top bit set, never INITFILL, never twice in the whole plan)."""
    def __init__(self, seed):
        self.rng, self.used = random.Random(seed), {INITFILL, 0xffffffff, A_, B_}

    def __call__(self):
        while True:
            v = self.rng.getrandbits(32) | 0x80000000
            if v not in self.used:
                self.used.add(v)
                return v


def sentinels(d, base, n):
    return {base + i: d() for i in range(n)}


# ---------------------------------------------------------------- item 8
def jobs_pred(seed=1137, reps=3):
    d = Draw(seed)
    jobs = []
    for r in range(reps):
        for k in range(1, len(GAPS) + 1):
            for P in (0, 1):
                m1, m2 = d(), d()
                jobs.append({"item": 8, "n": k, "P": P, "m1": m1, "m2": m2, "rep": r,
                             "params": {8: P, 9: m1, 10: m2}})
    random.Random(seed).shuffle(jobs)
    return jobs


def expect_pred(j):
    P = j["P"]
    return [A_ if P else j["m1"], j["m2"] if P else B_, HIT if P else MISS, MISS if P else HIT]


def judge_pred(j, slot):
    return list(slot[:4]) == expect_pred(j)


# ---------------------------------------------------------------- item 10
def _vals(kind, n_or_w):
    out = []
    for i, w in enumerate(n_or_w):
        if kind == "Z":
            out.append(w)
        elif kind == "B":
            out.append(w ^ (1 << (i % 32)))
        elif kind == "B2":
            out.append(w ^ (1 << ((i + 16) % 32)))
        elif kind == "S":                       # sign-extended 7-bit reading of n
            out.append(w | 0xffffff80)
    return [v & 0xffffffff for v in out]


def jobs_imm(seed=1138):
    d = Draw(seed)
    jobs = []
    for kind in ("Z", "B", "S", "B2"):
        vals = _vals(kind, list(range(128)))
        p = {IN1 + i: v for i, v in enumerate(vals)}
        p.update(sentinels(d, OUT1, 128))
        jobs.append({"item": 10, "n": 1, "kind": kind, "params": p, "task": "imm"})
    for kind in ("Z", "B", "B2"):
        vals = _vals(kind, WIDE)
        p = {IN1 + i: v for i, v in enumerate(vals)}
        p.update(sentinels(d, OUT1, 64))
        jobs.append({"item": 10, "n": 1, "kind": kind, "params": p, "task": "wide"})
    return jobs


def expect_imm(j):
    """per entry: 0 (V == n: the test reads equal) or 1 (differs)."""
    k = j["kind"]
    if j["task"] == "imm":
        if k == "Z":
            return [0] * 128
        return [1] * 128
    return [0] * 64 if k == "Z" else [1] * 64


def judge_imm(j, page):
    e = expect_imm(j)
    got = [page[OUT1 + i] for i in range(len(e))]
    return got == e, [i for i, (a, b) in enumerate(zip(got, e)) if a != b]


# ---------------------------------------------------------------- item 11
def jobs_regs(seed=1139, reps=3):
    """risk order: regsB, then regsA by range (cmds 3..6), then all at once (1), then r0 (2)."""
    d = Draw(seed)
    jobs = []
    ranges = {3: (1, 31), 4: (32, 63), 5: (64, 95), 6: (96, 123)}
    plan = [("regsB", 1)] + [("regsA", c) for c in (3, 4, 5, 6, 1, 2)]
    for task, cmd in plan:
        base_test = LAY["test_regsA"] if task == "regsA" else LAY["test_regsB"]
        if cmd in ranges:
            test = [n for n in base_test if ranges[cmd][0] <= n <= ranges[cmd][1]]
        else:
            test = base_test if cmd == 1 else [0]
        for r in range(reps):
            p = {IN1 + n: d() for n in range(128)}
            p.update(sentinels(d, OUT1, 128))
            jobs.append({"item": 11, "n": cmd, "task": task, "rep": r, "params": p, "test": test})
    return jobs


def judge_regs(j, page):
    bad = [n for n in j["test"] if page[OUT1 + n] != j["params"][IN1 + n]]
    if j["test"] == [0]:
        return page[OUT1] == j["params"][IN1], [], page[OUT1]   # r0: the marker back (E540 only read it: 0)
    return not bad, bad, None


# ---------------------------------------------------------------- item 12
def jobs_wdf(seed=1140, reps=3):
    d = Draw(seed)
    jobs = []
    for r in range(reps):
        for k, n in enumerate(NS, 1):
            p = {IN1 + i: d() for i in range(128)}
            p.update({IN2 + i: d() for i in range(128)})
            p.update(sentinels(d, OUT1, 128))
            jobs.append({"item": 12, "n": k, "N": n, "rep": r, "params": p})
    for r in range(reps):                                   # the control: cmd 9, last
        p = {IN1 + i: d() for i in range(128)}
        p.update({IN2 + i: d() for i in range(128)})
        p.update(sentinels(d, OUT1, 128))
        jobs.append({"item": 12, "n": 9, "N": 32, "rep": r, "params": p, "control": True})
    return jobs


def expect_wdf(j):
    out = []
    for i in range(j["N"]):
        b, o = OFF[i] if i < len(OFF) else (None, None)
        out.append(j["params"][(IN1, IN2)[b] + o])
    return out


def judge_wdf(j, page):
    if j.get("control"):
        new = [j["params"][IN1 + i] for i in range(32)]
        old = [j["params"][IN2 + i] for i in range(32)]
        got = [page[OUT1 + i] for i in range(32)]
        return {"new": sum(g == a for g, a in zip(got, new)), "old": sum(g == a for g, a in zip(got, old)),
                "other": sum(g != a and g != b for g, a, b in zip(got, new, old))}
    e = expect_wdf(j)
    got = [page[OUT1 + i] for i in range(j["N"])]
    return got == e, [i for i, (a, b) in enumerate(zip(got, e)) if a != b]


# ---------------------------------------------------------------- item 14 (slow4)
def jobs_slow(n_iter, seed=1141):
    d = Draw(seed)
    p = {10: n_iter}
    p.update({CNT + i: 0 for i in range(4)})
    p.update({OVL + i: 0 for i in range(4)})
    p.update({ARR + i: d() for i in range(16)})
    return {"item": 14, "n": 1, "params": p, "iters": n_iter}


def judge_slow(page):
    return {"passes": [page[CNT + i] for i in range(4)], "overlap": [page[OVL + i] for i in range(4)],
            "arrivals": [[page[ARR + 4 * k + j] for j in range(3)] for k in range(4)]}
