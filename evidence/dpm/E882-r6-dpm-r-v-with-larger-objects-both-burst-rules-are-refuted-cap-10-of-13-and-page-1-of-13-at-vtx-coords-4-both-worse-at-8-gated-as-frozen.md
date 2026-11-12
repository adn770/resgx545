+++
id = "E882"
claim = "R6-dpm stage r-v on the rgn4 module (Q210, the cause of the bursts; 2048x2048, the tool's triangle with 1500 vertices and --vtx-coords 4 or 8, objects larger than E874's 67 dwords): the frozen verdict, tagged [GATED: r-a0 a0-cal-2048f grow: cannot tell] as every stage of the session (E881), is 'both refuted' at both N; at N 4 the calibration's dump read L = 127 dwords, the 67 + 15 N the plan inferred, and H-BURST-CAP's replay at that L placed 10 of 13 calibration rows (12 steps and the need 538: S4, S9 and S10 off by 3, 2 and 2 pages) and H-BURST-PAGE's 1 of 13, while at its two band 3 cells (thr0 0x99, 0x9a, both 2 pages left) H-PHASE with PAGE's burst end placed 2 of 2 and with CAP's 0 of 2; at N 8 CAP placed 1 of 19 and PAGE 1 of 14 and the frozen reader found no L (read after the run: the head pair of PB page 1 recurs at 187, 187, 198, 198 and 198 dwords), so its cells could not be scored; read after the run, the global steps come in pairs and triples a few pages apart near the 1500-vertex scene's own steps (N 4: 0x4f 0x52, 0x98 0x9f, 0xe7, 0x12e 0x133, 0x17d 0x182, 0x1c7 0x1cd, 0x214), not one a burst"
unit = "dpm"
method = "R6-dpm stage r-v (6 jobs: for N = 4 and 8, a calibration at P 0x422 with --dump-render, then E - 1 and E of the first band from 3 on whose burst end F4's frozen timeline rule finds in the calibration, P 0xbb and 0xbc) of the question-closing pass, round 6, dataset render-closing-r6-dpm, attempt a2 (freeze 2; attempt a1's stop and the refreeze are in E881's method), on the laptop (host cedar), 2026-11-12, started 15:02:38 Mac time, health ok after it; otherwise as E881 (rgn4 module 99CD90DA, tool e6951558..., probe --tri pixel --vertices 1500 --vtx-coords N, never run on the hardware before; the calibration a premise: a 1500-vertex scene that reaches a second global page, its dump required). The predictions: gen/r6model.py, the session's formalization of the plan's two hypotheses on E874's frozen replay (f5lib.py, hash-checked) with L the object block's dwords: CAP keeps the stream blocks opening every 15 entries, PAGE opens a block in every region at each object b_k that starts a global page (deviation 4 of PREFLIGHT.md); a cell's 'rule' prediction is F4's frozen phase rule at the job's thr0 with the L read from its calibration's dump. The verdict line of score/score_r6.py names CAP when CAP misses none and PAGE some, PAGE the other way, 'both refuted' when both miss. The scorer re-run at the fold on the kept files gave output byte-identical to out/a2/score-r-v.txt. Post hoc (after the run): postrun/ungated.py and its output list the head-pair offsets of the two calibration dumps; the step pairs above are read from the kept score file's observed brackets"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r6-dpm:out/a2/r-v/", "render-closing-r6-dpm:postrun/"]
terms = ["Dynamic Parameter Management (DPM)", "CR_DPM_GLOBAL_PAGE_STATUS", "CR_DPM_PAGE_STATUS", "CR_DPM_TA_GLOBAL_LIST"]
+++
**What ran.** E874 read the bursts of the page take as the stream blocks of every covering region
opening together at objects 0, 15, 30, ..., with the entry of each object b_k that starts a global
page one dword longer. Two causes fit the 67-dword scene: the blocks fill after a fixed number of
entries that happens to be near the 15.28 objects of a list page (H-BURST-CAP), or the step itself
opens them (H-BURST-PAGE). Larger objects part them: the global steps come more often in objects,
and CAP keeps the bursts where they were while PAGE gives one burst a step. Stage r-v ran the
same triangle with 4 and 8 coordinate pairs a vertex.

**Results [HW, frozen verdict].** `out/a2/score-r-v.txt`: "--vtx-coords 4: L 127 (L0 127); steps
CAP 10 held, 3 FAILED, 0 cannot tell of 13, PAGE 1 held, 12 FAILED, 0 cannot tell of 13: both
refuted; cells H-PHASE|CAP 0 held, 2 FAILED, 0 cannot tell of 2, |PAGE 2 held, 0 FAILED, 0 cannot
tell of 2, E-TL 1 held, 1 FAILED, 0 cannot tell of 2 [GATED: r-a0 a0-cal-2048f grow: cannot tell]
| --vtx-coords 8: L None (L0 187); steps CAP 1 held, 17 FAILED, 1 cannot tell of 19, PAGE 1 held,
13 FAILED, 0 cannot tell of 14: both refuted; cells H-PHASE|CAP 0 held, 0 FAILED, 2 cannot tell
of 2, |PAGE 0 held, 0 FAILED, 2 cannot tell of 2, E-TL 1 held, 0 FAILED, 1 cannot tell of 2
[GATED: ...]". The gate is the r-a0 control without a reading (E881); r-v's own premise held at
both N (13 and 18 global pages at the calibration, both completed).

| N | rule | S2 .. S7 predicted | read (brackets' lower ends) | need read; predicted |
|---|---|---|---|---|
| 4 | CAP | `0x4f 0x52 0x9b 0x9f 0xe7 0x12e` | `0x4f 0x52 0x98 0x9f 0xe7 0x12e` | 538; `0x21a` |
| 4 | PAGE | `0x4f 0x97 0xe1 0x12b 0x174 0x1bc` | as above | 538; `0x3bd` |
| 8 | CAP | `0x4f 0x50 0x53 0x99 0x9d 0xe6` | `0x4f 0x98 0x9e 0xe5 0xe7 0x12d` | 691; `0x263` |
| 8 | PAGE | `0x4f 0x97 0xe1 0x12b 0x172 0x1bd` | as above | 691; above `0x400` |

At N 4, S8 to S13 read `0x133 0x17d 0x182 0x1c7 0x1cd 0x214` against CAP's `0x133 0x17b 0x180
0x1c7 0x1cd 0x214`. Both N 4 cells (thr0 `0x99` and `0x9a`) left 2 global pages; both N 8 cells
left 2 and raised.

**Read after the run [HW, post hoc].** The N 4 dump's head pair recurs every 127 dwords (8 of 8
periods); the N 8 dump's at offsets 0, 187, 374, 572, 770 and 968, so two block sizes, 187 and
198 dwords, and the reader's one-period rule returns none. At both N the global steps fall in
groups a few pages apart near the 1500-vertex scene's steps (`0x51`, `0x9d`, `0xe8`, `0x132`,
`0x181`, `0x1ca`, `0x213`): N 4 one or two steps a group, N 8 two or three (`0x210`, `0x215`;
`0x25d`, `0x260`).

**What it shows [infer].** Neither burst rule as frozen gives the steps of larger objects. PAGE's
one burst a step is far off from S3 on (the steps do not spread out evenly in pages), so a global
step does not by itself open every region's block; CAP's shape, the steps bunched between bursts
that stay near the same page counts, is what the data show, and its replay places 10 of 13 at N 4
but misses by 2 or 3 pages there and fails at N 8, where the object blocks are not of one size.
L0 = 67 + 15 N held at N 4.

**What it does not show.** No frozen verdict: the stage is gated (E881), and "both refuted" is the
scorer's line under that tag. Why the N 8 blocks have two sizes; where the bursts are exactly for
larger objects; the margin at these scenes (the N 8 cells were not scored, the N 4 cells test one
band). That the bursts stay near fixed page counts is read after the run from one calibration
each.

**Correction 2026-11-12:** The N 8 readings above are of one run, not of a fixed scene. Round 7's
R7-dpm ran the same calibration commands again (E917, exploration): at N 4 every step, the need
538 and the 127-dword blocks repeated, but at N 8 the dump's blocks ran 187, 198, 187, 198, 187
dwords (here 187, 187, 198, 198, 198), the steps were others from S3 on (`0x50`, `0x53`, `0x99`,
...) and the need 610 pages against 691 [HW]. So "the N 8 blocks have two sizes" and the N 8 steps
in the table above describe this run only.
