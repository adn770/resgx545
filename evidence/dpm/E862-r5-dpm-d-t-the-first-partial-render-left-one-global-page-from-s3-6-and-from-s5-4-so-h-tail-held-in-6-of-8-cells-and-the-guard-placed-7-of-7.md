+++
id = "E862"
claim = "R5-dpm stage d-t on the rgn4 module (Q210; exploratory; 2048x2048, the tool's triangle with 1500 vertices, thr0 S3 - 7 to S3 - 4 = 0x96 to 0x99 and S5 - 7 to S5 - 4 = 0x12b to 0x12e): the global pages left at the last in-stretch sample of the first partial render were 2, 1, 1, 1 below S3 and 2, 2, 2, 1 below S5, so H-TAIL (2, 2, 1, 1 in each band, the margin m = 6 of E852's S4 carried to the other steps) held in 6 of 8 cells and FAILED at S3 - 6 and S5 - 5; the band below S3 raised and the band below S5 stayed silent, R-5's guard 7 held and 1 cannot tell of 8 (S5 - 4: one partial render), with no grow and every control held (8 of 8)"
unit = "dpm"
method = "R5-dpm stage d-t (8 jobs, exploratory, cells from the S3 and S5 that the runner read from a0-cal-2048 of the same attempt) of the question-closing pass, round 5, dataset render-closing-r5-dpm, attempt 2 (freeze 2; the first attempt's stop and the lead's cleanup of the laptop's /tmp are in E860's method), on the laptop (host cedar), 2026-11-12, started 09:46:09 Mac time, health ok after it; setup and scoring as E860 (rgn4 module 99CD90DA, tool e6951558..., 16 registers, frozen score/score_r5.py). H-TAIL was frozen as an exploratory analogy [infer]: the last m - 1 pages before any step leave one global page fewer, with m fitted on E852's band below S4; a miss refutes the analogy, not the guard (plan closing5/dpm/exp-dpm-r5.md section 2). The scorer re-run at the fold on the kept files printed output byte-identical to score-d-t.txt. Post hoc (read after the run from the runner's reading lines in out/a2/d-t.log, not scored): the global page counts at the abort and the number of partial renders"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r5-dpm:out/a2/d-t/"]
terms = ["Dynamic Parameter Management (DPM)", "CR_DPM_GLOBAL_PAGE_STATUS", "CR_DPM_PAGE_STATUS", "CR_DPM_PARTIAL_RENDER"]
+++
**What ran.** E852 placed the raise flips 6 to 10 pages below S4 at the five targets: from S3 to
S4 - m the partial render leaves 2 of 3 global pages (raise), in the last m - 1 pages before S4 it
leaves 1 (silent). The planner carried that margin, m = 6 at 2048x2048, to the bands below S3
(where dword 36 floors at 0 and the guard raises whatever is left) and S5 (where 4 pages at the
abort make dword 36 = 2 and the guard is silent whatever is left), as an exploratory test of the
page accounting, not of the guard.

**Results [HW, frozen verdict].** `out/a2/score-d-t.txt`: "CTL: 8 held, 0 FAILED, 0 cannot tell of
8 | H-GREQ: 8 held, 0 FAILED, 0 cannot tell of 8 | H-TAIL: 6 held, 2 FAILED, 0 cannot tell of 8 |
R-5: 7 held, 0 FAILED, 1 cannot tell of 8".

| band | thr0 | pages left, predicted | pages left, read | raise |
|---|---|---|---|---|
| S3 - 7 to S3 - 4 | `0x96` to `0x99` | 2, 2, 1, 1 | 2, 1, 1, 1 | raise in all |
| S5 - 7 to S5 - 4 | `0x12b` to `0x12e` | 2, 2, 1, 1 | 2, 2, 2, 1 | none (S5 - 4: no reading) |

**Read after the run [HW, post hoc].** The aborts held 2 global pages below S3 and 4 below S5 in all
eight cells; S5 - 4 had one partial render, so no second entry decided a raise there. The drop from
2 pages left to 1 came 6 pages below S3 and 4 below S5, against 5 below S4 in E852's table, which
read the same kept quantity.

**What it shows [infer].** The margin is not one constant at a target: below S3, S4 and S5 at
2048x2048 the partial render leaves one global page fewer from 6, 5 and 4 pages before the step
(m = 7, 6 and 5 in E852's terms). The guard placed every cell that decided, on bands where its
outcome does not depend on the pages left (dword 36 floored at 0 below S3, 2 below S5).

**What it does not show.** What sets the margin. These are single runs of exploratory cells, read
from the timeline's last in-stretch sample, which E860 and E861 show can read one page high after
a grow (no cell here grew). The guard's compare of two non-zero counts is not tested by them.
