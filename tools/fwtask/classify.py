# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The prediction table of phase 11.30 and its classifier (the 11.29 table is classify1129.py).

`classify.py write predictions-1130.toml` writes the table; the file is frozen (its sha256 recorded
in the run log) BEFORE the first run of stage B, and `evaluate()` reads only that file. A prediction is the
first line of each row (`declared`); `falsifier` is what contradicts it; `expect` is the
machine-checked form, a Python expression over the names of the row's `vars`.
"""
import hashlib
import pathlib
import sys
import tomllib

import layout as L

NINE_B = []        # phase 11.29's 9b rows are frozen in predictions.toml and classify1129.py, not repeated

# (id, declared, falsifier, expect)
STAGES = [
    ("B_alive", "with the tail-calling writer armed (the closed task runs after our writes) the tick keeps "
     "advancing (900 to 1100 Hz after each round), the writer is done and the next event runs the reader, "
     "within 100 ms", "the tick stops again (as E533) or no reader: the closed task is not what re-arms the tick",
     "rounds_alive and writer_done and reader_done and 900 <= min_rate <= 1100"),
    ("B_ctl_stable", "two controls (reader only, nothing written) read the same r20, r21, i0, i1, "
     "p0 to p3 and pclink at entry", "they differ: the leftovers are not a function of the task before",
     "ctl_a == ctl_b"),
    ("B_sa_high_next", "sa64, sa100 and sa127 read at the next event are the markers the writer stored, in 3 of 3 rounds",
     "any other value: the closed task, the task start or a reset of the bank changed them",
     "sa_high == markers_high"),
    ("B_sa_low_next", "sa20 and sa24 read at the next event are the markers, 3 of 3 rounds",
     "any other value", "sa_low == markers_low"),
    ("B_sa_gap", "sa64, sa100, sa127, sa20 and sa24 are still the markers after 1200 ms (about 1200 closed ticks), 3 of 3",
     "any other value", "sa_all == markers_all"),
    ("B_sa_fill", "sa64, sa100, sa127, sa20 and sa24 are still the markers after a client fill ran between, 3 of 3",
     "any other value: client data masters and the EDM share these sa", "sa_all == markers_all"),
    ("B_r_gone", "r20 and r21 read at the next event are not the writer's markers (the closed task or the "
     "task start reuses the temporaries), in 3 of 3 rounds", "r20 or r21 equals the marker in a round: temporaries persist",
     "r_vals != markers_r"),
    ("B_i_kept", "i0 and i1 read at the next event are the writer's markers, 3 of 3 rounds",
     "any other value", "i_vals == markers_i"),
    ("B_p_gone", "p0 to p3 at the entry of the next task are not the writer's pattern (the complement of the control's), "
     "in 3 of 3 rounds", "the pattern equals ours in a round: predicates persist", "p_vals != p_pattern"),
    ("B_pclink_const", "pclink at the entry of a task is the same value in the controls and in every round",
     "it differs: it depends on what our task did", "len(set(pclinks)) == 1"),
    ("Q033_q1m", "one miscinfo, with pa1 bit 25 masked in the stubs, hits the general slot only, with pa1 & 0xfdffffff == 0x100",
     "pa1 = 0x4000 (E146's reading), another slot, or no hit", "hit_slots == [0] and (pa1 & 0xfdffffff) == 0x100"),
    ("Q033_quiet", "with the mask, 50 ms of ticks with no event log nothing in any slot (the tick's bit 25 is masked)",
     "a hit in the quiet window: the tick has other pa1 bits, or the mask failed", "quiet_hits == []"),
    ("Q033_q2", "TA finished arrives in the bit-9 fast slot with pa1 = 0x200 (the last event of slot 1 logged)",
     "the general slot with 0x2000", "1 in hit_slots and (pa1_slot1 & 0xfdffffff) == 0x200"),
    ("I11_overlap", "no overlap: overlap = 0 in 10 of 10 runs and no tick is lost",
     "overlap = 1 in any run, or HostCtl dword 12 behind by the ticks of the window",
     "overlap_runs == 0 and lost_ticks == 0"),
]
for t in (8, 9, 12, 16, 24, 31):
    STAGES.append((f"I13_T{t:02d}", f"TRC {t}: r{min(4 * t - 1, 123)} is real storage in a firmware task: the marker "
                   "written is read back", "the marker is not read back: the EDM allocator differs",
                   f"marker_back == 0x{0x7a110000 + t:08x}"))
for t in (9, 12, 16, 24):
    STAGES.append((f"I13_P{t:02d}", f"TRC {t}: the register past the allocation (r{4 * t}) does not hold the marker written "
                   "to it (a write past the allocation is dropped, E486)", "it reads the marker: the write landed",
                   f"past_back != 0x{0x7b220000 + t:08x}"))
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
           "# Phase 11.30 predictions (the tail-calling writer, Q033 Q1 with the mask, items 11 and 13), frozen before the first run of stage B. classify.py reads only this file.",
           "# Stage B vars: markers_* are what the writer stored (random per round, host seed 1130);",
           "# ctl_a, ctl_b the two controls' entry values; p_pattern the complement of the control's p0..p3.", ""]
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
    return bool(eval(r["expect"], {"__builtins__": {"len": len, "set": set, "min": min, "max": max, "all": all, "any": any, "zip": zip}}, vars))


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
