+++
id = "E853"
claim = "Round 5 offline test of R-5's guard of the firmware's raise (Q210, Q211): the guard as written on 2026-11-11 (closing4/p7/guard.py, imported unchanged) on the kept timelines of R3-geo-c that R-5 never read placed 121 of 121 decisions in g-qf (22 jobs, 88) and scene s275 (6 jobs, 33), held out by construction, every job one raise at its first decision and aborts after it, and the dword rule (dword 35 the page count at the last abort less 2, dword 36 the global page count less 2, floor 0) in 34 of 34 jobs; the two-kick scene s438 gave 27 of 33 as run and 27 of 27 only after each timeline was cut at its second kick, a cut added after the 6 misses were seen (SEMI); every cell holds one global page, so these test the floor of dword 36 and bit 9, not the compare of two counts"
unit = "dpm"
method = "Offline, no run (round 5, area dpm, decision R5-1 a; plan closing5/dpm/exp-dpm-r5.md section 3.1). closing5/dpm/qf_guard.py imports R-5's closing4/p7/guard.py unchanged (written 2026-11-11 from our reading of the firmware's out-of-memory routine and resume, then run on R1-pixgeo, R2-geo and R3-geo stages only) and applies its simulate(rows, 'last') to every job of R3-geo-c g-qf and g-qh (dataset render-closing-r3-geo-c, the kept NAME.txt.gz timelines and after.buf09 control blocks), counting a decision right when the guard's raise or abort matches the timeline's (a raise of 0x0624 before the next stretch of 0x0658, else an abort); the dword rule compares dwords 35 and 36 after the job with the counts of the last sample before the last abort. closing5/dpm/qf_guard2.py, written after qf_guard.out showed 6 misses all in s438, cuts each timeline where no sample changed for more than 0.1 s outside a partial render (the second kick of a --geometry job starts a new TA job; the TA finish clears sa8 bits 7 to 10, 3d.md 4.5) and runs the same guard on each piece. Scripts, outputs and guard.py are published in resgx545-data-private (cited/closing5/dpm/, cited/closing4/p7/guard.py) because guard.py encodes a reading of the firmware; re-run from those copies (guard.py byte-identical to the scratch file the scripts import) both printed output byte-identical to the kept .out files. No frozen verdict: the counts are the scripts' printed lines; the plan states s438 as 21 of 27 before the cut, the output reads 27 of 33"
tiers = ["HW", "RE", "infer"]
date = "2026-11-12"
data = ["render-closing-r3-geo-c:out/g-qf/", "render-closing-r3-geo-c:out/g-qh/"]
terms = ["Dynamic Parameter Management (DPM)", "ta3d_ctl", "CR_DPM_GLOBAL_PAGE_STATUS", "CR_DPM_PAGE_STATUS", "CR_DPM_ZLS_PAGE_THRESHOLD"]
+++
**What ran.** Offline. R-5's guard (3d.md §6.4; Q210's note of 2026-11-11): at each out-of-memory
entry after a resume, the raise happens iff `sa8` bit 7 is set, bit 9 clear and the count the entry
sees is above the one the last abort saved; dword 36 is the global page count at the abort less 2,
floor 0, dword 35 the page count less 2; bit 9 is set by a raise. Its offline test placed 288 of
289 decisions in 107 jobs of the stages R-5 read. R3-geo-c's g-qf (22 jobs at U = 287) and g-qh
(the scenes s275 and s438, E832) were not among them, so `qf_guard.py` ran the unchanged guard on
those timelines, which makes them held out for the guard by construction.

**Results [HW].** From `qf_guard.out` and `qf_guard2.out`:

| set | jobs with a partial render | decisions placed | dword rule |
|---|---|---|---|
| g-qf (U 287) | 22 | 88 of 88 | 22 of 22 |
| g-qh s275 (U 275) | 6 | 33 of 33 | 6 of 6 |
| g-qh s438, as run | 6 | 27 of 33 | 6 of 6 |
| g-qh s438, cut at the second kick | 6 | 27 of 27 | - |

In each of the 28 g-qf and s275 jobs the first decision is a raise and every later one an abort, as
the guard says (with one global page the saved count floors at 0, so the first entry raises, and
the raise sets bit 9, so later entries abort). The two scene gates (P `0x422`) had no partial
render. In s438 as run, five jobs raised a second time where the guard said abort and one aborted
where it said raise.

**Read after the misses [SEMI].** The six misses were all in s438, whose scene is two kicks (its
first render submitted as geometry only, E832). `qf_guard2.py` cuts a timeline at the gap of the
second kick and runs the guard on each piece, so that the TA finish between the kicks clears bits
7 to 10 as 3d.md §4.5 reads it; then all 27 decisions are placed. The cut was added after seeing
the misses; g-qf and s275 need none. The planner's text states s438 as 21 of 27 before the cut;
the script's output reads 27 of 33.

**What it shows.** [HW, RE] The guard read from the instructions holds on 121 decisions it was
not written on, with nothing fitted, and the dword rule on 34 more jobs. [infer] With the cut, the
guard read per TA job, s438 fits too, which is what the TA finish's clear of bits 7 to 10 predicts.

**What it does not show.** The compare of two non-zero counts: every one of these cells holds one
global page through the job, so they exercise the floor of dword 36 and bit 9 only, not the place
of the flips (E852's c4-b3 stays open). The `sa8` bits themselves were not read: the guard's
semantics stay a static reading [RE, static], tested through the timelines only. s438 is SEMI, not
held out.
