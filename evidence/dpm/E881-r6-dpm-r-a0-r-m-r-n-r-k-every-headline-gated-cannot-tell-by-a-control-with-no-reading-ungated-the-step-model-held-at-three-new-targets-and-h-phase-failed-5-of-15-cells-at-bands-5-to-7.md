+++
id = "E881"
claim = "R6-dpm stages r-a0, r-m, r-n and r-k on the rgn4 module (Q210; the tool's triangle with 1500 vertices; attempt a2 under freeze 2, after attempt a1 stopped in r-a0 on a runner slip): every frozen headline printed 'cannot tell', gated by one r-a0 control, a0-cal-2048f grow, that has no reading by construction (the full calibration runs at knob 0x400 and takes no partial render: a design slip of the builder), while every other r-a0 control held (S2 to S7 0x51, 0x9d, 0xe8, 0x132, 0x181, 0x1ca and the need 0x213 in their brackets, c4-b5 raised, c4-b6 silent, t-s3m7 and t-s3m6 2 and 1 global pages left, g-qf at P 0xa2 two partial renders, 7 of 7 knobs); read ungated after the run (post hoc): E874's step model held at three targets never run before (2048x1024, 1024x2048, 1536x1536: 18 of 18 steps in their brackets and the needs 277, 288 and 314 as predicted), H-PHASE held at their bands 3 and 4 (18 of 18 cells) with R-5's raise 14 of 14 (B3 - 1 raised, B3 silent at all three), H-GREQ held at 15 of 15 r-m cells, but H-PHASE failed 5 of 15 r-m cells at bands 5 to 7 of 2048x2048, where one global page is left from thr0 0x178, 0x1c3 and 0x20d, the model's B_k + 2, + 2 and + 1 (the timeline rival E-TL 10 of 15 too); r-k, with R5-dpm's oomring because both verifiers refuse oomring2, read R-5's sa8 bits at 3 of 3 held-out cells, a repeat of c4-b3 and both controls, and its 2048x4096 creep cell (thr0 0x24a, twice) was voided by the scene check (its S3 0x12c against E874's model 0x129, the known miss); read without that check, both runs had dword 36 = 2, one page left, sa8 & 0x380 = 0 and no raise, as E864's [infer] isub16 order predicts (post hoc)"
unit = "dpm"
method = "R6-dpm stages r-a0 (7 controls), r-m (15 held-out cells: 2048x2048 thr0 B_k - 2 to B_k + 2 around E874's burst ends B5 0x176, B6 0x1c1, B7 0x20c), r-n (21: for 2048x1024, 1024x2048 and 1536x1536 a calibration at P 0x422 and B3 - 1, B3, S4 - 1, B4 - 1, B4, S5 - 1 from the frozen model, S - 1 from the calibration's own step) and r-k (8, last: our own firmware task armed before each job; c4-b5, c4-b6, c4-b3 repeated, S3, S4 + 1, S3 - 6 at 2048x2048 and the 2048x4096 creep cell thr0 0x24a twice) of the question-closing pass, round 6 (decision R6-2 a; plan closing6/dpm/exp-dpm-r6.md section 4, every plan decision a; the session's README.md and PREFLIGHT.md, with its nine deviations), dataset render-closing-r6-dpm, on the laptop (host cedar), 2026-11-12, kernel 7.3.0-resgx545, module srcversion 99CD90DA26E3AFF9C450517 (rgn4; loaded = installed at each stage start), stock firmware, tool ~/sgxfive-test-rgn4 (sha256 e6951558...), ~/regtimeline sampling R5-dpm's 16 registers, a debugfs reset before each job, every file under ~/scratch/r6d (one work directory a job under ~/scratch/tmp, nothing in /tmp, 200 MB free checked before each job), predictions frozen from the offline rules of E873 to E875 (hash-checked at import) against resgx545 main d9b2969 and data e5cdaf0a. Attempt a1 (freeze 1, kept in freeze1/ with the five runner files the laptop got; out/a1, run-r6d-a1.log) started r-a0 at 14:40:13 Mac time and stopped with rc 10 at its fifth job: freeze 1's staging copied the runner files by name and left out run/lib_check.sh, which defines num_eq, so the sourcing failed (r-a0.log line 1), bash went on, and the ctlleft control of a0-t-s3m7 called a missing num_eq and reported a premise stop although its reading (R, 2 pages left) was the frozen one. The lead stopped there, having seen the five readings a1 had printed (a0-cal-2048 S2 to S5 and 2 left, a0-cal-2048f complete with need 0x213, S6 0x181, S7 0x1ca, c4-b5 R with 2 left, c4-b6 N with 1, t-s3m7 R with 2: each the frozen prediction, all r-a0 controls); the builder refroze the staging and the runner's start only (one staged file list, a stop when a sourced file or num_eq is missing, the mock run from the staged tree under env -i, a test that a1's tree reproduces the stop; predictions/ and tables/ byte-identical, PREDICTIONS.sha256 unchanged; README.md, Freeze 2). Attempt a2 (freeze 2, out/a2, run-r6d-a2.log) ran all six stages from 14:56:38 to about 15:21, health ok after every stage, no fault, hang or stop. The frozen score/score_r6.py gates every headline after r-a0 on r-a0's control rows; a0-cal-2048f's grow row (H-GREQ, predicted 0) reads only at a partial render, which a job at knob 0x400 with a need of 0x213 never takes, so it printed 'cannot tell (no reading)' and every later headline 'cannot tell' or a tally tagged [GATED]; the three r-n calibrations have the same row (not in the gate). The scorer re-run at the fold on the kept files gave output byte-identical to out/a2/score-r-a0.txt to score-r-k.txt; attempt a1 was never scored. Post hoc (2026-11-12, after the run and its scores were read): postrun/ungated.py in the dataset (its output postrun/ungated.out) tallies the states the frozen scorer printed line by line without the gate (no re-scoring), reads the two creep jobs with the frozen reader without the scene check, and lists the first thr0 of each r-m band with one page left"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r6-dpm:out/a2/r-a0/", "render-closing-r6-dpm:out/a2/r-m/", "render-closing-r6-dpm:out/a2/r-n/", "render-closing-r6-dpm:out/a2/r-k/", "render-closing-r6-dpm:out/a1/", "render-closing-r6-dpm:postrun/"]
terms = ["Dynamic Parameter Management (DPM)", "CR_DPM_GLOBAL_PAGE_STATUS", "CR_DPM_PAGE_STATUS", "CR_DPM_TA_GLOBAL_LIST", "ta3d_ctl"]
+++
**What ran.** E874 replayed, offline and post hoc, the page take of the tool's 1500-vertex
triangle: the steps S_k come from 67-dword object blocks, the bursts from stream blocks that open
together, and the first partial render leaves 2 global pages iff the first threshold lies between
a step and the model's burst end B_k (H-PHASE). Nothing of it was held out. R6-dpm froze its
predictions from those rules and ran new bands at 2048x2048 (r-m), three targets never run
(r-n), and R-5's guard read by our own task at a creep cell where dword 36 is above the pages
left (r-k), after seven controls (r-a0).

**Results [HW, frozen verdict].** `out/a2/score-r-a0.txt`: "cannot tell: controls: a0-cal-2048f
grow: cannot tell"; every other r-a0 row held (36 of 37 rows; S2 to S7, the need, the classes, the
pages left, the knobs, g-qf's count and run peaks). `score-r-m.txt`: "cannot tell: controls: r-a0
a0-cal-2048f grow: cannot tell | rival E-TL (F4's timeline burst ends): 10 held, 5 FAILED, 0
cannot tell of 15 [GATED: r-a0 a0-cal-2048f grow: cannot tell] | R-5 silent: 0 held, 0 FAILED, 0
cannot tell of 0; H-GREQ no grow: 15 held, 0 FAILED, 0 cannot tell of 15; F9 count (explore): 15
held, 0 FAILED, 0 cannot tell of 15 [GATED: ...]". `score-r-n.txt`: "cannot tell" for H-STEPMODEL
and H-PHASE at each target, with "R-5 4 held", "5 held" and "5 held, 0 FAILED". `score-r-k.txt`:
"cannot tell: controls: r-a0 a0-cal-2048f grow: cannot tell | the creep cell (dword 36 = 2 above
1 page left): cannot tell | counts at the passes: cannot tell (oomring2 refused by both
verifiers; r5's oomring ran, bits only)".

**Read after the run, ungated [HW, post hoc].** `postrun/ungated.out` (the scorer's own rows):

| stage | rule | rows |
|---|---|---|
| r-n | H-STEPMODEL steps S2 to S7 at 2048x1024, 1024x2048, 1536x1536 | 18 of 18 in their brackets |
| r-n | H-STEPMODEL needs `0x115`, `0x120`, `0x13a`, no partial render | 3 of 3 (277, 288, 314) |
| r-n | H-PHASE, bands 3 and 4 | 18 of 18 (6 a target) |
| r-n | R-5 raise (B3 - 1 raised, B3 and later silent) | 14 of 14 |
| r-n | H-GREQ no grow; F9 counts (exploratory) | 18 of 18; 18 of 18 |
| r-m | H-GREQ no grow; F9 counts (exploratory) | 15 of 15; 15 of 15 |
| r-m | H-PHASE (left 2 iff S_k < thr0 < B_k) | 10 of 15 |
| r-m | E-TL (the frozen timeline rule's burst ends) | 10 of 15 |
| r-k | R-5 sa8 bits and class (k-s3, k-s4p1, k-s3m6; c4-b3 repeat) | 3 of 3; 1 of 1 |
| r-k | controls k-b5 `0x180` R, k-b6 0 N | 2 of 2 |

The r-m cells, pages left by the first partial render (H-PHASE predicted 2 below B_k, 1 from it):

| band | thr0 and pages left | first 1 | B_k |
|---|---|---|---|
| 5 | `0x174` 2, `0x175` 2, `0x176` 2, `0x177` 2, `0x178` 1 | `0x178` | `0x176` |
| 6 | `0x1bf` 2, `0x1c0` 2, `0x1c1` 2, `0x1c2` 2, `0x1c3` 1 | `0x1c3` | `0x1c1` |
| 7 | `0x20a` 2, `0x20b` 2, `0x20c` 2, `0x20d` 1, `0x20e` 1 | `0x20d` | `0x20c` |

The creep cells, read by the frozen reader without the scene check: k-creep and k-creep2 both
thr0 `0x24a`, two partial renders (F9's count), one global page left, dword 36 = 2 after the job,
`sa8 & 0x380` = 0 at the decision entry, no raise. Their steps S2 to S4 were `0x9a`, `0x12c`,
`0x1be`: the scene check compared S3 with the frozen model's `0x129`, E874's one miss.

**What it shows [infer].** At three targets the frozen replay gave the steps and the needs before
any job ran there, and the margin of bands 3 and 4 (B3 the first silent cell, so C = B3 + `0x1f`
with R-5's guard): E874's step model and its phase reading hold at bands 3 and 4 beyond the
targets it was read on. At 2048x2048 bands 5 to 7 the margin is wider than the model's burst
by one or two pages: B_k as E874 defines it (the page count once the next object with an index
divisible by 15 is tiled) is not where the second page stops being kept there, so H-PHASE as
frozen is refuted at those bands. With dword 36 at 2 and one page left, the creep cell stayed
silent with `sa8` bits 7 to 9 clear, as `isub16` = source 1 minus source 2 predicts.

**What it does not show.** No frozen verdict: every headline is gated, and the readings above
are post hoc tallies of rows scored as frozen. Why bands 5 to 7 keep the second page longer; the
counts at the passes (oomring2 did not run); the creep reading is outside the frozen scorer and
rests on two runs of one cell. The step model is shown for the tool's triangle only, and its
2048x4096 S3 miss stands.
