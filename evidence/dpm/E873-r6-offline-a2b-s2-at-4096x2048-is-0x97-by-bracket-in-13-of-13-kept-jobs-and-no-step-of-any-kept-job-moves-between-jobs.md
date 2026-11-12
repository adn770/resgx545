+++
id = "E873"
claim = "Round 6 offline reading of the kept DPM timelines (Q210, A2b; a reading rule applied to data already seen, post hoc, nothing held out): a step of the global page count between two samples of the first TA run with page counts a and b only places S_k, the count before global page k appears, in [a, max(a, b - 1)]; read so, every one of the 31 (target, scene, step) keys of the kept sessions has a non-empty intersection over its jobs (28 one value, 3 a two-page range, 0 empty), so no step moves between jobs, and S2 of the tool's 1500-vertex triangle at 4096x2048 is 0x97 in 13 of 13 kept jobs, a2b-cal-4x2 included: its bracket is [0x97, 0x98] (as in 5 more jobs of R3-geo g-c5), and the round 5 reading of 0x98 that gated d-a2b (E861) was the upper end max(a, b - 1); every value of E852's table and E861's frozen S lies in the bracket of every job of its key (the point rule gives the same value in all jobs of every key but 4096x2048 S2, 7 of 13); at 2048x2048 S6 and S7 are 0x181 and 0x1ca (6 jobs each)"
unit = "dpm"
method = "Offline, no run (round 6, area dpm, decision R6-1 a; plan closing6/dpm/exp-dpm-r6.md section 3, step F1, from the planner's steps_iv.py, O1). closing6/dpm/offline/f1_brackets.py (with r6lib.py, the planner's reader with the data root from RESGX545_DATA; standard library only) reads every kept register timeline under render/closing-*/out of resgx545-data that sampled 0x0724, 0x072c and 0x0658 (the steps come from R1-pixgeo, R2-geo, R3-geo and R5-dpm; the other sessions show none in a first run), brackets each step of the global count in the first TA run (before the first stretch of 0x0658), intersects the brackets per (target, scene, k), and tests E852's table and E861's frozen S2 = 0x97 at 4096x2048 against each job's bracket. The script and r6lib.py were hashed into FREEZE-f1.sha256 before their first run (FREEZE-LOG.txt beside them); the output is f1_brackets.out. Re-run from the published copy (resgx545-data cited/closing6/dpm/offline/): byte-identical. No frozen prediction: the planner's steps_iv.out had printed the same table before the rule was written, so the reading is post hoc; the rule decides no hardware question by itself"
tiers = ["HW"]
date = "2026-11-12"
data = ["render-closing-r1-pixgeo", "render-closing-r2-geo", "render-closing-r3-geo", "render-closing-r5-dpm"]
terms = ["Dynamic Parameter Management (DPM)", "CR_DPM_GLOBAL_PAGE_STATUS", "CR_DPM_PAGE_STATUS", "CR_DPM_PARTIAL_RENDER"]
+++
**What was done.** The timelines sample the registers about every 8.4 us, and the TA takes up to
several pages between two samples. E852 read each step S_k as one value per job, and R5-dpm's
reader took the count at the sample before the step, or the count after it less one, whichever was
larger. In d-a2b that rule read S2 = `0x98` in a2b-cal-4x2 against the frozen `0x97` (E852's
table), and the frozen gate of the stage marked every headline GATED (E861). The round 6 planner
(O1) read a step as the bracket it is: with a and b the page counts of the two samples around the
step, S_k is somewhere in [a, max(a, b - 1)]. F1 applies that rule to every kept job and asks two
things: does a step stay put between jobs (the brackets of a key intersect), and does each frozen
value lie in every job's bracket.

**Results [HW, post hoc].** `f1_brackets.out`: 31 keys, 0 with an empty intersection.

| key | jobs | intersection | brackets |
|---|---|---|---|
| 4096x2048 S2 | 13 | `0x97` | [97,97] x7, [97,98] x6 |
| 2048x4096 S2 | 13 | `0x9a` | [99,9a] x1, [9a,9a] x12 |
| 4096x2048 S6 | 2 | `0x2db`..`0x2dc` | [2db,2dc] x2 |
| 3072x3072 S6 | 2 | `0x335`..`0x336` | [335,336] x2 |
| 2048x2048 `--tri-full` S2 | 1 | `0x200`..`0x201` | [200,201] x1 |
| 2048x2048 S6, S7 | 6 each | `0x181`, `0x1ca` | one value each |
| the other 24 keys | 2 to 64 | one value | one value each |

The six [`0x97`, `0x98`] brackets at 4096x2048 are a2b-cal-4x2 (R5-dpm d-a2b) and c5a-b1, b2, b4,
b5 and f4 (R3-geo g-c5); the seven [`0x97`, `0x97`] are c5a-cal, b3, f1, f2, f3, f5 and
a2b-4x2-s4. Every value of E852's table and the frozen S of E861 lies in the bracket of every job
of its key (18 keys, 2 to 64 jobs each); the point rule max(a, b - 1) gives the same value in all
jobs of every key except 4096x2048 S2 (7 of 13). The one 2048x4096 calibration that E852 read as
`0x99` has the bracket [`0x99`, `0x9a`], so it holds `0x9a`, the value of the other twelve.

**What it shows.** A2b is closed as a reading: S2 at 4096x2048 is `0x97` in 13 of 13 jobs, and
d-a2b's calibration did not read a step one page late; its two samples straddled the step and the
point rule took the upper end. The gate of d-a2b stands as run (the frozen rule is what the
session ran), but the fact it rested on is not a disagreement with E852 (Correction 2026-11-12 in
E861). No step of any kept job moves between jobs: a step is a fixed page count of a target and
scene, to the resolution the samples allow. S6 and S7 at 2048x2048 are new values from kept jobs
(R2-geo g-c3 and R3-geo g-c6, 6 jobs each).

**What it does not show.** Where inside a two-page bracket a step lies when every job of its key
saw the same bracket (4096x2048 S6, 3072x3072 S6, the `--tri-full` S2). Nothing about why the
steps fall where they do; that is E874. The reading rule is not a hardware law: it is how a sampled
step must be read, and r6's reader and scorer take it.
