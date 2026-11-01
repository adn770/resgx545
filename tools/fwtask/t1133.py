# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Phase 11.33 part 1 (item 13, Q133): TRC 32 to 48 with trc_hazard=1 on the fixed module.

Pure helpers (arm line, jobs, verdicts, the frozen prediction table) for run_1133.py. Only
T = 32, 36, 40, 44, 48 may be armed; 49 and above, and any other use of trc_hazard, are refused.
"""
import hashlib
import pathlib
import random
import tomllib

import layout as L

TS = (32, 36, 40, 44, 48)


def arm_line(t):
    if t not in TS:
        raise ValueError(f"TRC {t}: only {TS} may be armed with trc_hazard=1")
    return f"slots=0x1 entry=0 trc={t} trc_hazard=1"


def make_jobs(ts, reps, seed):
    """One pass per repeat over `ts` in order (the first pass is one job per T, then the repeats);
    every job has its own random marker, never INITFILL, never one already used."""
    rng = random.Random(seed)
    used = {L.INITFILL}
    jobs = []
    for rep in range(reps):
        for t in ts:
            while True:
                m = rng.getrandbits(32) | 0x80000000
                if m not in used and m != 0xffffffff:
                    break
            used.add(m)
            jobs.append({"T": t, "rep": rep, "marker": m, "params": {"8": m}})
    return jobs


def judge(marker, rec):
    s = rec["slot"]
    return {"done": bool(rec["done"]), "marker_back": bool(rec["done"]) and s[0] == marker,
            "r0_zero": s[2] == 0, "top": s[0], "r0": s[2]}


# (id, declared, falsifier, expect)
ROWS = []
for _t in TS:
    ROWS.append((f"P33_T{_t}", f"TRC {_t} (trc_hazard=1) arms and the job runs: done within 100 ms, r123 reads "
                 "back the job's own marker, r0 reads 0, the tick advances (900 to 1100 Hz), EVENT_STATUS2 is 0x400, "
                 "no BIF fault, the gate is exact after",
                 "no done, a marker not read back (a stale or zero read), r0 not 0, a hang, a fault or a failed gate",
                 "done and marker_back and r0_zero and alive and health_ok and gate_ok"))
ROWS.append(("P33_REPEAT", "the repeat of every T gives the same outcome as its first job, each with its own "
             "marker", "a repeat that differs from its first job", "same_as_first"))
ROWS.append(("P33_TOP", "for every T the top register tested is r123 (the highest that can be named; 4T - 1 is "
             "127 to 191 and cannot be named)", "a result that names another register", "top == 123"))
ROWS.append(("P33_PAST", "no register past the allocation exists to name for T >= 32 (r124 and up are not "
             "encodable), so no result about it is declared and none is claimed", "n/a: not run", "not_run"))


def render_predictions():
    out = ["# phase 11.33 predictions, frozen before the first run (sha256 recorded)", ""]
    for rid, declared, falsifier, expect in ROWS:
        out += ["[[row]]", f'id = "{rid}"', f'declared = "{declared}"', f'falsifier = "{falsifier}"',
                f'expect = "{expect}"', ""]
    return "\n".join(out)


def sha256(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def check_frozen(path, want):
    return sha256(path) == want


def load_predictions(path):
    return {r["id"]: r for r in tomllib.loads(pathlib.Path(path).read_text())["row"]}
