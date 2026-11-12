+++
id = "E854"
claim = "Round 5 offline fit of the partial-render count (Q211; a FIT, nothing held out by a frozen prediction): for the tool's triangle at 4096x4096 the count n at the first threshold thr0 = P - 0x22 fits n = min{n >= 1 : thr0 + n (thr0 + 0x20 - 7/4) >= U}, the one rule left by the 4 of 2716 members of thr0 + n (thr0 + 0x20 - d) >= U + k (d 0 to 6 in sixteenths, k -12 to 15) that fit E832's 22 cells at U = 287 (d 1.5625 to 1.75, k 0 or 1, the same count at every thr0 for U 287 and 275); it gives s275's 6 cells (U 275; SEMI, their counts had been seen; 754 of the 2716 members give them too), E625's ten 4096x4096 cells, E779's nine and E625's 18 cells at 1024x768 (U 19), none used in the fit, and E625's form with an integer spacing fits none of the 22; the rule does not hold for the 1500-vertex scenes, whose pages taken less pages kept are not U (544 to 898 at 2048x2048 for U = 0x213) and whose counts at 2048x2048 it gives in 11 of 17 jobs (post hoc)"
unit = "dpm"
method = "Offline, no run (round 5, area dpm, decision R5-1 a; plan closing5/dpm/exp-dpm-r5.md section 3.2 to 3.4). closing5/dpm/qf_pages.py (published in resgx545-data-private because it takes its timeline loader from closing4/p7/guard.py; its output qf_pages.out, page counts only, in resgx545-data) reads the kept timelines of R3-geo-c g-qf and g-qh (dataset render-closing-r3-geo-c) and prints per job thr0 (0x0624 at the first stretch of 0x0658), the count of stretches, each TA run's peak of 0x0724 and the pages each partial render left (0x0724 at the stretch's last sample, and the minimum over its last three). closing5/dpm/qf_count2.py (pure python, reads qf_pages.out) scans the family on E832's 22 g-qf cells (U = 287, E773's HU1), then scores the fitting members on s275's 6 cells (Q211's note of 2026-11-11 named them as the held-out set before any fit; the planner had seen their counts in qf_pages.out before the script ran, so SEMI) and on E625's and E779's cells as those records list them. closing5/dpm/tri1500_pages.py reads the DPM jobs of R1-pixgeo g-c1 and g-c1f, R2-geo g-c3 and g-c2 and R3-geo g-c4, g-c5, g-c6 and g-d36 the same way (1350 and 1500 vertices, and two default-triangle jobs of g-c2); in the fold (2026-11-12) closing5/dpm/fold_tri1500_rule.py applied the rule (d = 7/4, k = 0) to its 2048x2048 lines with U = 0x213 (E785). Every script re-run from its published copy printed output byte-identical to the kept .out files. No frozen verdict"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r3-geo-c:out/g-qf/", "render-closing-r3-geo-c:out/g-qh/", "render-closing-r3-geo:out/g-c4/", "render-closing-r3-geo:out/g-c5/", "render-closing-r3-geo:out/g-c6/", "render-closing-r3-geo:out/g-d36/", "render-closing-r2-geo:out/g-c3/", "render-closing-r2-geo:out/g-c2/", "render-closing-r1-pixgeo:out/g-c1/", "render-closing-r1-pixgeo:out/g-c1f/"]
terms = ["Dynamic Parameter Management (DPM)", "Parameter Buffer (PB)", "CR_DPM_PAGE_STATUS", "CR_DPM_PARTIAL_RENDER"]
+++
**What was done.** E832 refuted E625's count formula at U = 287 over every (k, s) of a wide grid,
and a round 4 scratch refit found no plain page quotient that fits its 22 cells (Q211's note of
2026-11-11, which named s275's 6 cells as the held-out set of the next fit). The round 5 planner
first read what each run takes and each partial render keeps (`closing5/dpm/qf_pages.py`), then
fitted a family built on that (`qf_count2.py`), offline.

**Results [HW, read offline].** What the kept timelines show (`qf_pages.out`, 22 g-qf and 6 s275
jobs): the first run takes thr0 pages; every later run but the last peaks at thr0 + `0x20` (the
raise of E853's first decision); each partial render leaves 1 or 2 pages at its stretch's last
sample (0 or 1 at the minimum of its last three); the pages taken over all runs less the pages
left are U - 2 to U + 7 (U + 1 to U + 11 by the minimum), more with more partial renders.

The fit (`qf_count2.out`): of 2716 members of n = min{n >= 1 : thr0 + n (thr0 + `0x20` - d) >= U +
k}, four fit all 22 g-qf cells: d from 1.5625 to 1.75 and k 0 or 1. They predict the same count at
every thr0 for U 287 and 275, so they are one rule on these scenes, written with d = 7/4, k = 0 as
4 thr0 + n (4 thr0 + 121) >= 4 U. The fitting members give all cells of each other set:

| set (not used in the fit) | cells | U | all four members | members of the grid that give them |
|---|---|---|---|---|
| s275 (E832, SEMI) | 6 | 275 | 6 of 6 | 754 of 2716 |
| E625, 4096x4096 | 10 | 287 | 10 of 10 | 1120 of 2716 |
| E779 | 9 | 287 | 9 of 9 | 582 of 2716 |
| E625, 1024x768 | 18 | 19 | 18 of 18 | 2380 of 2716 |

E625's own form 1 + floor((U + k - thr0) / (thr0 + s)) with an integer s from `0x18` to `0x21` and
k from -12 to 15 fits none of the 22 cells, as E832 says for its grid.

Scope (`tri1500_pages.out`, `fold_tri1500_rule.out`): in the 1500-vertex jobs the pages taken less
the pages kept are 544 to 898 at 2048x2048 (544 to 713 with at most three partial renders), for a
need of `0x213` (531); the last run's peak clusters at `0x4d` to `0x52`, `0x9b` to `0x9c` and
`0xe3` to `0xe6` at 2048x2048, a few pages below S2, S3 and S4 (E852), and at `0x11b` to `0x12c`,
`0x234` to `0x240` and `0x352` at 4096x4096 (1350 and 1500 vertices), near S2, S3 and S4 there
(the two default-triangle jobs the script also lists end at 2 and `0x20`). The rule with U =
`0x213` gives the count of 11 of the 17 jobs at 2048x2048 and misses at thr0 `0x60`, `0x70`,
`0xb0`, `0xc0` and `0x100` (twice).

**What it shows [infer].** For one-triangle scenes the count is a page quotient with spacing thr0 +
30.25: E832's "not a plain page quotient" holds for integer spacings, and a fractional spacing fits
every kept cell of the tool's triangle at 4096x4096 and 1024x768. A reading of d = 1.75: the page
each partial render keeps plus about 3/4 page lost per render; a fraction says the rule averages a
mechanism, it is not the mechanism. The 1500-vertex scenes do not conserve pages, and their last
runs end near the global steps of E852: the abort may discard the macrotile under way.

**What it does not show.** A held-out test: the constants were picked on g-qf by the script, s275
was seen before, and the older cells pass most of the grid (the 1024x768 cells nearly all of it).
The rule needs a scene at a U other than 287 and 275, its cells frozen from a measured U, to stand;
one cell of a one-triangle scene off the rule would refute it. What a partial render frees, and the
count for scenes of many vertices or several triangles, stay open (Q211).

**Correction 2026-11-12:** The rule failed its held-out test. Round 5's R5-dpm session ran two
one-triangle scenes at U 119 and 198 (HU1's needs, measured as predicted) with cells frozen from
them: the rule missed 3 of 10 and 1 of 10 cells, one partial render too many each time (E863).
Read after that run, no member of the family scanned here fits U 287, 275, 198 and 119 together,
so "for one-triangle scenes the count is a page quotient with spacing thr0 + 30.25" above does not
hold beyond the scenes it was fitted on. The fit and its table stand as a fit.
