+++
id = "E861"
claim = "R5-dpm stages d-a2 and d-a2b on the rgn4 module (Q210; the tool's triangle with 1500 vertices, cells picked by frozen rules from the session's own calibrations, none run before): at 2048x2048 and 4096x4096 the first abort grew the TA's global list at every cell whose first threshold thr0 equals a step S_k and at none one page either side (H-GREQ 16 of 16 rows; grow at S2, S3 twice and S5 at 2048x2048 and S3 twice and S4 twice at 4096x4096), and the five raising-side step cells (S2 0x51 and S3 0x9d twice at 2048x2048, S3 0x240 twice at 4096x4096, 1 or 2 global pages at the abort) all raised the threshold by 0x20: the frozen verdict is H-PEND (R-5's guard intact, c4-b3 a sampling artefact of the count estimate) for 5 of 5, H-BLOCK FAILED in 5 of 5; the S4 cells at 4096x4096 stayed silent (2 of 2), the guard placed 6 of the 8 neighbours (S5 - 1 and S5 + 1 cannot tell: one partial render, no second entry), and the S5 cell gave no reading for the same reason; in d-a2b the S4 cells at 4096x2048, 2048x4096 and 3072x3072 grew and stayed silent, 3 of 3, but every headline of the stage is GATED because a2b-cal-4x2 read S2 = 0x98 against the frozen 0x97 and had no abort to read a grow from"
unit = "dpm"
method = "R5-dpm stages d-a2 (16 jobs, held out: 2048x2048 S3 - 1, S3 twice, S3 + 1, S2 - 1, S2, S2 + 1, S5 - 1, S5, S5 + 1; 4096x4096 S4 twice, S3 - 1, S3 twice, S3 + 1, S_k read by the runner from a0-cal-2048 and a0-cal-4096 of the same attempt) and d-a2b (6 jobs: a calibration at P 0x422 and the S4 cell at 4096x2048, 2048x4096 and 3072x3072) of the question-closing pass, round 5, dataset render-closing-r5-dpm, attempt 2 (freeze 2; the first attempt's stop and the lead's cleanup of the laptop's /tmp are in E860's method), on the laptop (host cedar), 2026-11-12, d-a2 started 09:43:01 and d-a2b 09:45:12 Mac time, health ok after each; setup and scoring as E860 (rgn4 module 99CD90DA, tool e6951558..., 16 registers, frozen score/score_r5.py). The decision table was frozen before the run (plan closing5/dpm/exp-dpm-r5.md section 2): grow and raise in all raising-side S cells = H-PEND, grow and silent in all = H-BLOCK, mixed = no conclusion, no grow = void. The scorer re-run at the fold on the kept files printed output byte-identical to score-d-a2.txt and score-d-a2b.txt. Post hoc (read after the run from the runner's reading lines in out/a2/d-a2.log and d-a2b.log, not scored): the global page counts at the abort and at the last in-stretch sample, the number of partial renders of the S5 cells, and the calibrations' further steps"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r5-dpm:out/a2/d-a2/", "render-closing-r5-dpm:out/a2/d-a2b/"]
terms = ["Dynamic Parameter Management (DPM)", "CR_DPM_GLOBAL_PAGE_STATUS", "CR_DPM_PAGE_STATUS", "CR_DPM_TA_GLOBAL_LIST", "CR_DPM_ZLS_PAGE_THRESHOLD", "ta3d_ctl"]
+++
**What ran.** H-PEND (after a grow the page the TA asked for is served after the resume has read
the count, so R-5's guard stands) and H-BLOCK (the grow leaves a state that prevents the raise)
both predict c4-b3's silence (E860); they part at the steps on the raising side, where the abort
leaves 1 or 2 global pages, dword 36 floors at 0 and the guard raises: H-PEND raises there, H-BLOCK
stays silent. d-a2 ran those cells, their neighbours and the silent-side steps, all held out;
d-a2b ran the S4 cell at the three other targets of E801.

**Results [HW, frozen verdict].** d-a2 (`out/a2/score-d-a2.txt`): "H-GREQ: 16 held, 0 FAILED, 0
cannot tell of 16 | raising-side S cells: H-PEND (guard intact; c4-b3 a sampling artefact of the
count estimate): [('a2-42-s2', 'H-PEND'), ('a2-42-s3a', 'H-PEND'), ('a2-42-s3b', 'H-PEND'),
('a2-44-s3a', 'H-PEND'), ('a2-44-s3b', 'H-PEND')] | R-5's guard off the steps (the neighbours):
6 held, 0 FAILED, 2 cannot tell of 8".

| target | cells (thr0) | grow | global pages at abort | raise |
|---|---|---|---|---|
| 2048x2048 | S2 - 1, S2, S2 + 1 (`0x50` to `0x52`) | no, yes, no | 1, 1, 2 | all |
| 2048x2048 | S3 - 1, S3 x2, S3 + 1 (`0x9c` to `0x9e`) | no, yes, yes, no | 2, 2, 2, 3 | all |
| 2048x2048 | S5 - 1, S5, S5 + 1 (`0x131` to `0x133`) | no, yes, no | 4, 4, 5 | no reading |
| 4096x4096 | S3 - 1, S3 x2, S3 + 1 (`0x23f` to `0x241`) | no, yes, yes, no | 2, 2, 2, 3 | all |
| 4096x4096 | S4 x2 (`0x35b`) | yes, yes | 3, 3 | none |

d-a2b (`out/a2/score-d-a2b.txt`): the S4 cells (`0x1b9`, `0x1be`, `0x1ef`) grew and stayed silent
at 4096x2048, 2048x4096 and 3072x3072 (H-GREQ, H-PEND and H-BLOCK 3 held each), every line
"[GATED: a2b-cal-4x2 S2: FAILED; a2b-cal-4x2 grow: cannot tell]". The calibrations of 2048x4096 and
3072x3072 read E852's steps (S2 to S5, 8 of 8).

**Read after the run [HW, post hoc].** The S5 cells and both neighbours had one partial render: the
scene ended before a second out-of-memory entry, so no raise could be decided there. a2b-cal-4x2
needs 1015 pages and P `0x422` gives `0x400`, so it never aborted (no grow to read); its S2 read one
page late, as E852 saw S2 of 2048x4096 read `0x99` in its calibration and `0x9a` in the other jobs,
and the S4 job itself read S2 = `0x97`. The calibrations also read S5 to S7: `0x24a`, `0x2dc`,
`0x36c` at 4096x2048, S6 and S7 `0x2e8`, `0x37b` at 2048x4096 and `0x336`, `0x3d9` at 3072x3072,
so within a target the steps are nearly evenly spaced: `0x8e` to `0x93` pages apart at 4096x2048,
`0x92` to `0x97` at 2048x4096, `0xa2` to `0xa4` at 3072x3072, `0x4a` to `0x4c` at 2048x2048 and
`0x11b` at 4096x4096. At 4096x4096 a2-44-s4b read 2 global
pages at the last in-stretch sample and 1 in a2-44-s4a, both silent: the pattern of c4-b3 (E860).

**What it shows [infer].** The raise is not blocked by a grow: where the guard raises with no grow
it raises with one. So R-5's guard stands and c4-b3's silence is the guard's own answer with the
count the resume read, one page below what the timeline sometimes samples at the end of the
partial render (H-PEND; the resume's count is read directly in E864). H-GREQ held out: the first
entry grows the global list exactly when thr0 is a step, at both targets and at every step tried.

**What it does not show.** Why the steps fall where they do, or why a page is pending at the
resume only after a grow (Q210). S5 at 2048x2048 decides nothing. d-a2b's rows are gated by the
frozen rule: the three other targets are read, not held out.

**Correction 2026-11-12:** "a2b-cal-4x2 read S2 = 0x98" is the session reader's point rule, the
larger of the count before the step and the count after it less one. Read as the bracket the two
samples allow (E873), that job's S2 lies in [`0x97`, `0x98`], which holds the frozen `0x97`, as do
the brackets of all 13 kept jobs at 4096x2048; the S2 = `0x99` that E852 read in the 2048x4096
calibration is likewise the upper end of [`0x99`, `0x9a`]. So the calibration did not read a step
one page late. The stage's gate stands as it ran: its frozen rule marked the headlines GATED, and
the three other targets stay read, not held out. The S4 results of d-a2b are unchanged.
