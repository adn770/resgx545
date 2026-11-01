# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The prediction table of phase 11.29 and its classifier.

`classify.py write predictions.toml` writes the table; the file is frozen (its sha256 recorded in
the run log) BEFORE the first `str`, and `evaluate()` reads only that file. A prediction is the
first line of each row (`declared`); `falsifier` is what contradicts it; `expect` is the
machine-checked form, a Python expression over the names of the row's `vars`.
"""
import hashlib
import pathlib
import sys
import tomllib

import layout as L

NINE_B = [
    # id, declared, falsifier, expect
    ("X0", "L = A and H = A (control: the register does not move by itself)",
     "any other value: the register moves by itself, stop the table", "L == A and H == A"),
    ("X1", "L = A and H = A (the first str ever, the same value)",
     "any change: the bit pattern was not what we thought, stop", "L == A and H == A"),
]
for d in (0, 1, 2, 4, 16):
    NINE_B.append((f"X2_d{d}", f"L = B and H = B at distance {d}: a str is ordered before a later "
                   "ldr of the same register with no fence",
                   "L = A (the ldr overtook) or H = A (the str did not land)", "L == B and H == B"))
NINE_B += [
    ("X3", "same as X2_d0 (a wdf with nothing outstanding between)",
     "differs from X2_d0: a wdf matters", "L == B and H == B"),
    ("X4", "same as X2_d0 (idf then wdf between)", "differs: idf matters", "L == B and H == B"),
    ("X5", "same as X2_d0 (idf between, no wdf)", "differs", "L == B and H == B"),
    ("X6_d0", "L = A (an earlier ldr is not overtaken by a later str) and H = B",
     "L = B: a str can pass an outstanding ldr", "L == A and H == B"),
    ("X6_d4", "L = A and H = B, four nops between", "L = B", "L == A and H == B"),
    ("X7", "L = C and H = C (stores in order)", "L or H = B", "L == C and H == C"),
    ("X8", "L = R2's own start value and R2 H unchanged (registers do not alias)",
     "R2 changes: the registers alias", "L == A2 and R2H == A2"),
    ("X9", "every result read with done set although no idf came before state = done",
     "a 0xdeadc0de result with done: an unfenced stad at the end of a task is not complete",
     "landed and L == B and H == B"),
    ("X10", "the second ldr after 64 nops reads B (and the first too)",
     "A then: str dropped; B after an A first: a delay, not a loss", "L == B and L2 == B and H == B"),
    ("X11", "t1 - t0 (CR_TIMER counts, 25-bit) is at most 800 for str+ldr+wdf (2 microseconds at "
     "about 400 MHz [infer])", "no meaning on its own: an upper bound", "(t1 - t0) % (1 << 25) <= 800"),
]

STAGES = [
    ("S2_null", "HostCtl dword 12 advances at about 997 Hz, miscinfo is answered, fill and "
     "triangle diff 0, no fault, with the null wrapper armed",
     "no tick, no answer, a fault or a diff: the retargeted word or the closed handler failed",
     "ticks_per_s >= 900 and ticks_per_s <= 1100 and fill_diff == 0 and tri_diff == 0 and faults == 0"),
    ("S3_mem", "the memory-only wrapper: state done within 100 ms, marker 0x5a5a1129 stored, "
     "pa1 = 0 (a tick), pa2 nonzero",
     "no done: our code or the results page is not reached; a wrong marker: the page is not the "
     "one the task sees",
     "done and marker == 0x5a5a1129 and pa1 == 0 and pa2 != 0"),
    ("S4_ldr", "ldr returns CORE_ID, CORE_REVISION as the host reads them and CR_TIMER advancing",
     "a different value: ldr in an EDM task does not read the register as the host does",
     "core_id == host_core_id and core_rev == host_core_rev and timer_ok"),
    ("S1_sa_high", "sa64, sa100 and sa127 are retained 3 of 3, in task 2 and after 1000 closed "
     "tasks", "any reads 0 or another value", "sa64 == 0xa5000040 and sa100 == 0xa5000064 and sa127 == 0xa500007f"),
    ("S2_sa_low", "sa20 and sa24 retained as S1", "any reads another value",
     "sa20 == 0xa5000014 and sa24 == 0xa5000018"),
    ("S3_regs", "r20, r21, i0, i1 retained in task 2",
     "any reads another value", "r20 == 0xb5000020 and r21 == 0xb5000021 and i0 == 0xb5000020 and i1 == 0xb5000021"),
    ("S4_after_fill", "sa retained after a client fill ran between", "sa changed: the EDM and the "
     "client data masters share sa", "sa64 == 0xa5000040 and sa100 == 0xa5000064 and sa127 == 0xa500007f"),
    ("Q124_pred", "p0..p3 survive (1010) and pclink keeps bits 17:0 (0x2a5a5)",
     "a pattern 0000, 1111 or the closed code's: the state is reset at task start",
     "(p0, p1, p2, p3) == (1, 0, 1, 0) and pclink == 0x2a5a5"),
    ("Q033_q1", "one miscinfo reaches the general slot (0) with pa1 = 0x100 (reversed status bit 14)",
     "pa1 = 0x4000 (E146's same-position reading) or a slot other than 0",
     "hit_slots == [0] and pa1 == 0x100"),
    ("Q033_q2", "TA finished arrives in the bit-9 fast slot with pa1 = 0x200",
     "the general slot with 0x2000", "hit_slots == [1] and pa1 == 0x200"),
    ("I11_overlap", "no overlap: overlap = 0 in 10 of 10 runs and no tick is lost",
     "overlap = 1 in any run, or HostCtl dword 12 behind by the ticks of the window",
     "overlap_runs == 0 and lost_ticks == 0"),
]
for t in (8, 9, 12, 16, 24, 31):
    STAGES.append((f"I13_T{t:02d}", f"TRC {t}: r{min(4 * t - 1, 123)} is real storage; the register "
                   "past the allocation reads r(n mod 4T) or not at all", "the marker is not read back: "
                   "the EDM allocator differs", f"marker_back == 0x{0x7a110000 + t:08x}"))
for t in (32, 40, 48):
    STAGES.append((f"I13_T{t:02d}", f"TRC {t}: runs; only r123 is usable", "a hang", "marker_back == 0x%08x" % (0x7a110000 + t)))
for t in (49, 64):
    STAGES.append((f"I13_T{t:02d}", f"TRC {t}: hangs the EDM (a client job hung at T mod 256 in 196 "
                   "to 252 or 0)", "it runs: the EDM allocator differs from the clients'", "hang"))


def table():
    rows = []
    for rid, decl, fals, expect in NINE_B:
        rows.append(dict(id=rid, stage="9b", declared=decl, falsifier=fals, expect=expect))
    for rid, decl, fals, expect in STAGES:
        rows.append(dict(id=rid, stage=rid.split("_")[0], declared=decl, falsifier=fals, expect=expect))
    return rows


def render() -> str:
    out = ["# SPDX-License-Identifier: MIT", "# SPDX-FileCopyrightText: 2026 Josep Torra", "#",
           "# Phase 11.29 predictions, frozen before the first str. classify.py reads only this file.",
           "# A: the start value the host wrote; B, C: the task's values; L: the ldr result; H: the",
           "# register as the host reads it after the task; A2, R2H: the other register (X8).",
           "# R1 = 0x0814: A 0x15a5a, B 0x0a5a5, C 0x0f0f0; R2 = 0x0a78: A 0x15, B 0x2a, C 0x0c.", ""]
    for r in table():
        out.append("[[row]]")
        for k in ("id", "stage", "declared", "falsifier", "expect"):
            out.append(f'{k} = "{r[k]}"')
        out.append("")
    return "\n".join(out)


def load(path):
    return tomllib.loads(pathlib.Path(path).read_text())["row"]


def evaluate(path, row_id, **vars):
    """True when the row's expectation holds for the measured values; reads only the file."""
    rows = {r["id"]: r for r in load(path)}
    r = rows[row_id]
    if r["expect"] == "hang":
        return bool(vars.get("hang"))
    return bool(eval(r["expect"], {"__builtins__": {}}, vars))


def reading(Lv, H, A, B):
    """The row of plan 4.2 for the (L, H) pair of a case."""
    if (Lv, H) == (B, B):
        return "(B,B): landed and ordered: no fence needed for this register"
    if (Lv, H) == (A, B):
        return "(A,B): landed but the ldr did not see it"
    if (Lv, H) == (A, A):
        return "(A,A): the str did not land"
    if (Lv, H) == (B, A):
        return "(B,A): impossible for a plain register: check the restore and an unseen writer"
    return "other: a partial or masked store"


def sha256(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def main(argv):
    if argv[1] == "write":
        pathlib.Path(argv[2]).write_text(render())
        print(sha256(argv[2]))
        return 0
    if argv[1] == "sha":
        print(sha256(argv[2]))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
