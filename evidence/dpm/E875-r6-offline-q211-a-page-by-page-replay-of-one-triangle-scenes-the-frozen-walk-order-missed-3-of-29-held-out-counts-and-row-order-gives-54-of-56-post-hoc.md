+++
id = "E875"
claim = "Round 6 offline replay of the partial-render count of one-triangle scenes (Q211; no numeric constant fitted, one walk order picked from a closed family of six on E832's 22 g-qf cells, the rest SEMI since every count had been read before): HU1's regions walked in an order, one 128-byte stream each from its macrotile's current page, 32 a page, a refused page starting a partial render that frees all but the global page, the threshold raised by 0x20 once; the frozen pick, column order (22 of 22 g-qf counts), gave 26 of 29 counts of the scenes it was not picked on (s275 7 of 7, s198 9 of 11, s119 10 of 11, one render too many at each miss), so H-REPLAY with the frozen order is refuted on kept data; read after, row order (and macrotile rows, the same numbers) gives 20 of 22 g-qf, 29 of 29 of the others and 5 of 5 repeats, 54 of 56 kept counts where no spacing of E854's family fits all four scenes, with every run's peak within 3 pages in 29 of 29 and the last run's exact in 19; every member gives E625's and E779's 4096x4096 cells and E625's 1024x768 cells (37, counts only) but the three macrotile-first orders (36); E854's d = 7/4 gives 22 of 22 and 22 of 29, d = 1 17 of 22 and 26 of 29"
unit = "dpm"
method = "Offline, no run (round 6, area dpm, decision R6-1 a; plan closing6/dpm/exp-dpm-r6.md section 3, step F7, from the planner's cnt_sim.py, O6). closing6/dpm/offline/f7_replay.py (standard library only; r6lib.py, and HU1 from render/closing-r5-dpm/gen/hu1.py, unchanged) reads the kept timelines of R3-geo-c g-qf (22 cells, U 287) and g-qh's s275 (U 275), and R5-dpm d-b (five g-qf repeats, s198 and s119, U 198 and 119), takes per job thr0 = P - 0x22, the count of stretches of 0x0658 and each TA run's peak of 0x0724, replays every member of the family (the six orders of cnt_sim.py: rows, columns, macrotile by macrotile with rows or columns inside, macrotiles transposed, macrotile rows), picks W* by the g-qf counts then the g-qf last-run peaks, prints W* cell by cell and every member's tally, and scores the record cells of E625 and E779 (as closing5/dpm/qf_count2.py lists them) and E854's d = 7/4 and d = 1. The family and the pick rule were hashed into FREEZE-f7.sha256 before the first run (FREEZE-LOG.txt). The planner had seen every count, and the row order's run peaks of all four scenes in cnt_sim.out, and the builder read that output's head before the freeze: so the g-qf side is a fit and the rest SEMI; the row order's result is post hoc. Output f7_replay.out; re-run from the published copy (resgx545-data cited/closing6/dpm/offline/): byte-identical"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r3-geo-c:out/g-qf/", "render-closing-r3-geo-c:out/g-qh/", "render-closing-r5-dpm:out/a2/d-b/"]
terms = ["Dynamic Parameter Management (DPM)", "Parameter Buffer (PB)", "CR_DPM_PAGE_STATUS", "CR_DPM_PARTIAL_RENDER"]
+++
**What was done.** E832's 22 cells at U 287 refute E625's count formula, E854's spacing
thr0 + 0x20 - d fits each scene with its own d, and E863 refuted d = 7/4 held out at U 119 and 198;
no one d fits all four scenes. The round 6 planner replaced the spacing with a replay of the pages
themselves (O6): HU1's regions (E773) walked in some order, each taking one stream from its
macrotile's current page and a new page every 32 streams, a refused page starting a partial render
that keeps only the global page, the threshold raised by `0x20` once. No number is fitted; the
walk order is the open detail, so F7 froze a family of six orders and a rule that picks one on
g-qf alone.

**Results [HW; fit, SEMI, post hoc].** `f7_replay.out` (the other cells: s275, s198 and s119;
peaks of those cells):

| order | g-qf counts | g-qf last peak | other counts | all peaks exact | peaks within 3 |
|---|---|---|---|---|---|
| col (W*) | 22 of 22 | 9 | 26 of 29 | 10 | 26 |
| row | 20 of 22 | 10 | 29 of 29 | 19 | 29 |
| mtrow-row | 20 of 22 | 10 | 29 of 29 | 19 | 29 |
| mt-row, mt-col, mtT-row | 17 of 22 | 0 | 29 of 29 | 15 | 24 |

R5-dpm's five g-qf repeats: 5 of 5 for column and row order. W*'s three misses are s198 at thr0
`0x2` and `0x1b` and s119 at `0x13`, one partial render too many each; row order's two are g-qf at
thr0 `0x5` and `0x4c`, also one too many. On the record cells (counts only) column and row order
give E625's ten and E779's nine at 4096x4096 and E625's 18 at 1024x768 (U 19), 37 of 37; the
three macrotile-first orders miss one of E625's. The spacing rivals on the kept cells: d = 7/4
22 of 22 on g-qf and 22 of 29 on the rest, d = 1 17 of 22 and 26 of 29.

**What it shows [infer].** The count of a one-triangle scene follows from the pages it takes when
the walk is the TA's: a replay with no fitted number gives every kept count but two in row order
(54 of 56 over U 287, 275, 198 and 119), and its run peaks to 3 pages, where no spacing constant
fits the four scenes together. What a partial render "loses" is then the part-filled page of every
macrotile the walk has open at the abort, which depends on where the walk is, not on a constant:
that is why E854's d moved with the scene. The frozen pick shows the walk order is not decided by
g-qf's counts: column order fits them all and misses three counts elsewhere.

**What it does not show.** The walk order: the order the frozen rule picked failed on kept data
(26 of 29), and the order that fits 54 of 56 was named after its counts were seen, so H-REPLAY in
row order is post hoc and needs held-out scenes on the hardware (the plan's stage r-b). Row order's
two g-qf misses and the run peaks it misses by 1 to 3 pages are not explained. Scenes of many
objects (E874's replay is for the 1500-vertex scene, with stream blocks of many entries) and
multi-kick scenes (s438) are outside it, and so is Q211's U clause for wide scenes.

**Correction 2026-11-12:** Row order failed its held-out test, and the claim stands as a reading
of the kept counts. Round 6's laptop session R6-dpm ran four new one-triangle scenes at 4096x4096
(U 262, 243, 220 and 179, HU1's needs, measured as predicted) with 8 cells each, frozen from this
record's replay (E883). Every headline there is gated "cannot tell" by an r-a0 control that has no
reading by construction (E881); the scorer's own rows, tallied ungated after the run [HW, post
hoc]: row order gave 28 of 32 counts (s262 4 of 8, one partial render too many each time; the
other three scenes 8 of 8) and every run's peak exactly in 13 of 32 cells, within 3 pages in 28;
the frozen column order 19 of 32 counts, E854's d = 7/4 18 and d = 1 27. So H-REPLAY in row order
(count and every run's peak) does not hold on new scenes, and "54 of 56" above is post hoc only;
the walk order, and what a partial render frees, stay open (Q211).
