+++
id = "E863"
claim = "R5-dpm stage d-b on the rgn4 module (Q211; 4096x4096, one triangle of the tool, single kick): the five g-qf controls repeated E832's counts (9, 4, 3, 2, 1 at P 0x24, 0x53, 0x54, 0xa2, 0xa3; 10 of 10 rows), two scenes moved to (2560, 0) and (1984, 0) needed 119 and 198 pages with no partial render at P 0x422, the U HU1 gave them before the run (E773's model, 2 of 2), and over 10 held-out cells each (thr0 2 to 0x54, frozen from HU1's U) E854's count rule n = min{n >= 1 : thr0 + n (thr0 + 0x20 - 7/4) >= U} (H-CNT) missed 3 cells at U 119 (thr0 7, 0x13, 0x2c: it predicted one partial render more) and 1 at U 198 (thr0 2): the frozen verdict is 'H-CNT on scene s119 is not supported: 7 held, 3 FAILED' and 'on scene s198: 9 held, 1 FAILED', so H-CNT is refuted held out; of the seven alternatives frozen beside it, d = 1 missed none at either scene and d = 5/4 none at U 198 (post hoc: d = 1 misses 5 of E832's 22 cells at U 287, and no member of E854's family of 2716 fits U 287, 275, 198 and 119 together)"
unit = "dpm"
method = "R5-dpm stage d-b (27 jobs: 5 g-qf controls at 4096x4096 with the default triangle; for each of two scenes, the triangle moved by --move 1:2560,0 and --move 1:1984,0 with HU1 needs 119 and 198 frozen at build by gen/hu1.py, a calibration at P 0x422 and 10 cells picked from HU1's U by the session's gen/r5plan.py (b_cells, the rule of the planner's closing5/dpm/qf_cells.py, whose kept output qf_cells.out is for U 120 and 200) at the rule's steps and where the frozen alternatives differ: d = 1, 5/4, 9/4, 3 and E625's (0, 0x1e), (-1, 0x1e), (2, 0x1f)) of the question-closing pass, round 5, dataset render-closing-r5-dpm, attempt 2 (freeze 2; the first attempt's stop and the lead's cleanup of the laptop's /tmp are in E860's method), on the laptop (host cedar), 2026-11-12, started 09:47:18 Mac time, health ok after it; the count is the number of 0x0658 bit 0 stretches of the job's timeline, U the peak of 0x0724 in the calibration, the scene check every job staying at 1 global page; otherwise as E860 (rgn4 module 99CD90DA, tool e6951558..., 16 registers, frozen score/score_r5.py, a measured U off HU1 would have voided its scene's cells). The scorer re-run at the fold on the kept files printed output byte-identical to score-d-b.txt. Post hoc (2026-11-12, after the run): closing5/fold-sdpm/posthoc/cnt_family.py (pure python, beside its output cnt_family.out and copies of closing5/dpm/qf_pages.out and the kept score-d-b.txt) scores E854's family (d 0 to 6 in sixteenths, k -12 to 15) and E625's form on E832's 22 g-qf cells, s275's 6 and the 20 cells of d-b"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r5-dpm:out/a2/d-b/"]
terms = ["Dynamic Parameter Management (DPM)", "Parameter Buffer (PB)", "CR_DPM_PAGE_STATUS", "CR_DPM_PARTIAL_RENDER"]
+++
**What ran.** E854 fitted the count of partial renders of a one-triangle scene on E832's 22 cells
at U = 287: n = min{n >= 1 : thr0 + n (thr0 + `0x20` - 7/4) >= U}, the one rule four members of a
2716-member family leave, with no held-out test. Its record named one: a scene at another U, its
cells frozen from a measured U. Stage d-b ran two such scenes, each with a calibration that
checks HU1's U, and the five g-qf controls first.

**Results [HW, frozen verdict].** `out/a2/score-d-b.txt`: "the five g-qf controls repeat on rgn4
(10 of 10 rows decided) | H-CNT on scene s119 (HU1 U = 119) is not supported: 7 held, 3 FAILED, 0
cannot tell of 10; alternatives: d=1 0 misses, d=5/4 2 misses, d=9/4 3 misses, d=3 4 misses,
E625(0,0x1e) 3 misses, E625(-1,0x1e) 3 misses, E625(2,0x1f) 4 misses | H-CNT on scene s198 (HU1 U
= 198) is not supported: 9 held, 1 FAILED, 0 cannot tell of 10; alternatives: d=1 0 misses,
d=5/4 0 misses, d=9/4 5 misses, d=3 6 misses, E625(0,0x1e) 5 misses, E625(-1,0x1e) 1 misses,
E625(2,0x1f) 3 misses".

| scene | thr0 | 2 | 3 | 7 | 8 | 9 | `0x13` | `0x14` | `0x15` | `0x2c` | `0x2d` |
|---|---|---|---|---|---|---|---|---|---|---|---|
| s119 | count read | 4 | 4 | 3 | 3 | 3 | 2 | 2 | 2 | 1 | 1 |
| s119 | H-CNT | 4 | 4 | 4 | 3 | 3 | 3 | 2 | 2 | 2 | 1 |

| scene | thr0 | 2 | 3 | 7 | 8 | `0x1a` | `0x1b` | `0x2d` | `0x2e` | `0x53` | `0x54` |
|---|---|---|---|---|---|---|---|---|---|---|---|
| s198 | count read | 6 | 6 | 6 | 5 | 4 | 3 | 3 | 2 | 2 | 1 |
| s198 | H-CNT | 7 | 6 | 6 | 5 | 4 | 3 | 3 | 2 | 2 | 1 |

The calibrations read U = 119 and 198, as HU1 predicted, with no partial render; every job stayed
at one global page.

**Read after the run [HW, post hoc].** `closing5/fold-sdpm/posthoc/cnt_family.out`: of the 2716
members, 4 fit g-qf (U 287, d 1.5625 to 1.75), 754 fit s275, 740 fit s119 and 24 fit s198 (d
0.625 to 1.5); 12 fit both new scenes and none fits all four sets. d = 1, k = 0 misses none at U
275, 198 and 119 and 5 of the 22 cells at U 287; d = 7/4 misses none at 287 and 275. E625's form
with an integer spacing fits 2 pairs at U 198 and none at 287. Every miss of H-CNT predicted one
partial render more than ran.

**What it shows [infer].** The count of partial renders is not one page quotient with a fixed
spacing thr0 + `0x20` - d for one-triangle scenes: the members that fit U 198 (d at most 1.5) and
those that fit U 287 (d at least 1.5625) do not meet, so what each partial render keeps or loses
depends on the scene. HU1 (E773's model) gave the page need of two more scenes held out.

**What it does not show.** The rule of the count; whether d follows U, the scene's macrotiles or
its position (the two new scenes are the same triangle moved). The alternatives were frozen as a
tally, not as hypotheses with a verdict: that d = 1 fits both new scenes is read post hoc, and it
fails g-qf.
