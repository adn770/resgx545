+++
id = "Q211"
question = "what rule gives the partial-render count of a one-triangle scene of page need U at the first threshold thr0 = P - 0x22 (E625's 1 + floor((U + k - thr0) / (thr0 + s)) is refuted at U = 287, E779 and E832; E854's spacing thr0 + 0x20 - d fits each scene with its own d and failed held out at U 119 and 198, no one d fitting U 287, 275, 198 and 119, E863; E875's page-by-page replay in row order, post hoc on 56 kept counts, failed on four new scenes, 28 of 32 counts and 13 of 32 run peaks read ungated, E883), and does the page need U of HU1 (E773, E863: exact for E773's 15 held-out scenes made of the tool's triangle and E863's 2) hold for wide scenes of many vertices and other shapes (E630)?"
unit = "dpm"
kind = "hw"
value = "high"
phase = 11
evidence = ["E310", "E625", "E630", "E705", "E735", "E773", "E779", "E832", "E853", "E854", "E863", "E866", "E874", "E875", "E883"]
terms = ["Dynamic Parameter Management (DPM)", "Parameter Buffer (PB)"]
+++

E625: a one-triangle scene overflows exactly when P - 0x22 is below 19 pages (1024x768) or 287
pages (4096x4096), the two numbers E310 gave for the whole-buffer jobs (0x13, 0x11f); the counts
of its partial renders fit 1 + floor((287 + k - thr0) / (thr0 + 0x1f)) for every k from 2 to 13,
with the spacing 0x1f not pinned either (0x1e fits the 4096x4096 counts too). E630: wide scenes of
300 to 900 vertices at 4096x4096 need 2836 to 8318 pages by the same count formula, 9.2 to 9.8
pages a vertex, but the 300-vertex scene gives two ranges (0x40 and 0x23 pages) that do not meet
with the spacing 0x1f and overlap with 0x1e: these are lower bounds of a model that does not
close, not measures of a need, and neither a constant U per scene nor its failure is shown. A
second triangle at 1024x768 needs 23 to 26 pages (E627: overflow in 0x38, completion in 0x3c).

Open: how the lists' pages add up (one page per macrotile list at least, the global list's pages,
the pages the final lists take), what k is and what the pages it adds are, the spacing, and the
exact need of a scene as a function of its triangles and macrotiles, which `dpm.rs` must compute.

To settle it: scenes of 1 to 4 triangles whose whole-buffer page need is read from the free list
(the walk after the job) and the counts of partial renders at three buffer sizes each, with the
spacing fitted first on the one-triangle scene.

Reworded in 11.39: the figure "9.2 to 9.8 pages a vertex" for the wide scenes is dropped from the
question line (E630 calls it a lower bound of a model that does not close, and it does not hold
beyond the one threshold at which it was found); the paragraph above keeps the measurements.

Narrowed in 11.39 (E705). The page need of a one-triangle scene is not 19 pages: the same
triangle at 1024x768 moved by 0, 192, 384 and 576 pixels reaches status 0x13, 0x14, 0x11 and
0xc (19, 20, 17 and 12 pages), and E625's overflow rule (overflow iff P - 0x22 is below the
need) with those needs gives the outcome of all 8 distinct conditions (4 positions at each of
P = 0x28 and 0x30; the 22 renders include 14 repeats of an input already rendered; computed after
the run, so a check, not a held-out test). The planned stacked-against-disjoint comparison was
not made: the tool's -n 4 is four renders, one triangle each, so the two frozen predictions
(disj4 against stack4) are void, and the higher maximum status of disj4 is the position
dependence. Open: the need of a scene of 2 to 4
triangles (a tool option that puts several triangles in one render), the need as a function of
the macrotiles filled, k and the spacing.

Premise noted 2026-11-09. "A tool option that puts several triangles in one render" exists:
`--vertices N` (3 to 1500, whole triangles) draws copies of the triangle in one render (E630's
scenes), and `--geometry N` submits a render as geometry only so that the next render closes the
scene (`userspace/libsgxfive/README.md`, `tools/sgxfive-test.c`). E705 used `-n 4` without
`--geometry`, which is four renders, as its record says; a two-triangle scene that is one render
is run with `--geometry` (E627's two-triangle jobs used it).

Narrowed 2026-11-09 (S1, E735). Scenes of 2 to 4 triangles submitted as one open scene
(`--geometry`) were measured at 1024x768: the page need U, by the peak of status 0x0724 and by the
free-list walk alike, is 29, 35 and 37 pages for 2, 3 and 4 triangles apart and 19, 22 and 22 for 2,
3 and 4 stacked 16 pixels apart (the repeats of 4 apart and 4 stacked gave the same), against 19 for
one triangle (E705); the need does not follow the triangle count (stacked copies add 0, 3 and 0
pages, apart copies 10, 6 and 2). E625's overflow rule (overflow iff P - 0x22 is below U) then held
on the 12 boundary jobs generated from those U and frozen before they ran (overflow at P = U + 0x21,
completion at U + 0x22, 12 of 12, a held-out result; in 2 of the 12 an earlier kick overflowed
first, so the rule held for a smaller scene there). The two count jobs frozen to narrow k and the
spacing are void: at thr0 = 5 and 6 each of the first three kicks overflowed alone and no
four-triangle scene formed. The six U are fit data from now on. Open: the formula of U for a scene
(it needs the stream bytes of sgx-pipe, not computed before the run), k and the spacing (a count job
needs a P above one triangle's need with several triangles still accumulating).

Note 2026-11-10 (an offline model run on the published data, before the round 2 runs). The TA
model of sgx-pipe applied as it stands (`tiling`, `tile_lists` per 16x16 half-region, `walk`, 128
bytes a stream, a page per macrotile that has streams, pages = ceil(streams / 32)) plus 1 global
page gives every U measured so far with residual 0: 16 of 16 in the scratch table (the default
triangle at 64x64, 128x128, 192x128, 256x256, 512x384, 1024x768 and 4096x4096 as 2, 3, 5, 5, 8, 19
and 287; the four positions as 19, 20, 17 and 12; E735's six scenes; E627's two-triangle scene as
24, inside its measured 23 to 26). This is a FIT, not a test: both constants (128 bytes a stream,
1 global page) were picked from a small grid on these very data (64, 96, 160, 192 and 256 bytes
and 0 or 2 global pages miss by 16 to 479 pages in total), and only the structure is E650's. [infer]
It is a candidate for the formula of U, to be held to frozen predictions on scenes not yet run;
k and the spacing are not touched by it.

Narrowed 2026-11-10 (R1-pixgeo, E773 and E779). The U clause is answered for scenes made of the
tool's triangle: HU1 (the TA model of sgx-pipe, 128 bytes a stream, a page per macrotile with
streams, plus 1 global page) was held to frozen predictions on 15 scenes not measured before (the
triangle moved, two to four copies, 640x480 to 4096x4096, U from 7 to 438) and gave the page need
exactly in 15 of 15 (the peak of 0x0724 and the free-list walk agreed in all 17 jobs), the controls
19 and 29 passed, HU2 (macrotiles plus 8) failed 8 of 8 where it differs, and E625's overflow rule
with HU1's U held in 4 of 4 boundary jobs. The first held-out test of the candidate above passed.
The count clause failed: at U = 287 (4096x4096, the default triangle) the partial-render count was
2 at P = 0xa0 and 1 at 0xa3 to 0xa9 and 0xb0, and none of the 24 pairs (k 2 to 13, s 0x1e or 0x1f)
of E625's formula fits (every pair predicts 2 at 0xa3); the step lies between thr0 126 and 129, and
the formula's form fits with k at most 1, a reading not checked against E625's other cells. Open: k
and s, whether the count formula's form holds with another k (P = 0xa1 and 0xa2, the spacing cells
at count 3), and U for wide scenes (E630's 300 to 900 vertices, `--vertices N`) and for shapes other
than the tool's triangle.

Narrowed 2026-11-11 (R3-geo-c g-qf and g-qh, run 2026-11-10, folded in round 4, E832). The
question line asked "what are the constant k and the spacing s of the partial-render count of a
scene of page need U (E625's formula with k from 2 to 13 is refuted at U = 287, E779)". The round
3 offline fit found 20 (k, s) pairs (k -8 to 0, s 0x1b to 0x1e) fitting E625's and E779's cells,
the only ones of k -60 to 60 and s 1 to 0x5f; at U = 287 the count read at 22 values of P (9 at
0x24 down to 1 at 0xa3, never rising with P; 2 at 0xa2, so E779's step from 2 to 1 is between
thr0 128 and 129) fits none of them (frozen verdict REFUTED, controls passed): E625's form is
refuted over that grid. The held-out stage could not test anything (no pair left); its scene
s275 (U 275) gave 6 counts as data (8, 8, 7, 7, 6, 3 at P 0x26, 0x27, 0x2a, 0x2b, 0x31, 0x52),
and s438's cells were void (its geometry-only first render overflowed). Post hoc [infer]: (0,
0x1e) and (-1, 0x1e) miss one cell of each scene, and a scratch refit of c + floor or ceil((U +
a) / (P + b)) and of a two-segment form with a raised first threshold found no member that
fits all 22 cells (`closing4/rank/q211_refit.py`, scratch), so the count is not a plain page quotient. Open: the rule of the
count (what a partial render frees and keeps, with Q210's raise), to be fitted on E832's 22 cells
and held out on s275's 6 before any run; the U clause as above.

Note 2026-11-12 (round 5, offline, E853 and E854; decision R5-1 a, before any session; the question
stays open). [HW, FIT] In g-qf and s275 the first run takes thr0 pages, every later run but the last
peaks at thr0 + `0x20` (the guard's one raise, E853), and each partial render keeps 1 or 2 pages.
The count fits n = min{n >= 1 : thr0 + n (thr0 + `0x20` - 7/4) >= U}, the one rule the four fitting
members of a 2716-member family leave on E832's 22 cells (E854); it gives s275's 6 cells (SEMI: seen
before the fit), E625's and E779's 4096x4096 cells and E625's 1024x768 cells, none of them used in
the fit. E832's "not a plain page quotient" stays true for integer spacings; the fitted spacing is
thr0 + 30.25. The rule does not hold for the 1500-vertex scenes, which do not conserve pages (11 of
17 counts at 2048x2048, post hoc). Open: a held-out test of the rule on one-triangle scenes at other
U, cells frozen from a measured U; what a partial render frees; the count for scenes of many
vertices; the U clause as above.

Narrowed 2026-11-12 (round 5, R5-dpm stage B, E863). The question line asked "what rule gives the
partial-render count of a scene of page need U at the first threshold thr0 = P - 0x22 (E625's 1 +
floor((U + k - thr0) / (thr0 + s)) is refuted at U = 287 for every k from -60 to 60 and s from 1 to
0x5f, E779 and E832, whose 22 cells are the count curve to fit), and does the page need U of HU1
(E773: exact for 15 held-out scenes made of the tool's triangle) hold for wide scenes of many
vertices and other shapes (E630)?". [HW, held out] E854's rule (d = 7/4, k = 0) failed on two scenes
of one moved triangle at U 119 and 198, cells frozen from HU1's U before the run: 3 of 10 and 1 of
10 cells missed, one partial render too many each time; the five g-qf controls repeated E832's
counts and both scenes needed HU1's U with no partial render at P `0x422`. [HW, post hoc] Of the
seven alternatives frozen as a tally, d = 1 missed none at either scene and misses 5 of E832's 22
cells; no member of the 2716-member family fits U 287, 275, 198 and 119 together, so the spacing is
not one constant for one-triangle scenes. Open: what a partial render frees and keeps, by scene (the
fitting d moves with the scene: at least 1.5625 at U 287, at most 1.5 at U 198); the count for
scenes of many vertices; the U clause as above.

Note 2026-11-12 (round 5, session R5-render4x stage o, E866; the U clause, exploratory rows, the
question stays open). The tool's full-screen triangle at 1x and 1024 x 768 completed at P 0x53 with
49 scene pages and overflowed at 0x52, the need the round 5 render plan's model gave before the run
(one stream a 32 x 16 tile, the pages taken a macrotile, HU1 as E773: 16 x 3 + 1), where E846 had
frozen 97; the model fits its one earlier dump (r2-pixel's 320 x 400, 10 pages) and this boundary,
two scenes of another shape than the tool's triangle. At 4x on four arrays U4 = 1 + ceil(2 tiles16 /
32) held at three boundaries one page apart (E866, two of them held out).

Note 2026-11-12 (round 6, offline stage F7 and F9, E875 and E874; decision R6-1 a; the question
stays open). [HW, SEMI and post hoc; infer] A page-by-page replay with no fitted number (HU1's
regions walked in an order, a stream each, a page per macrotile every 32 streams, the one raise)
gives the count of one-triangle scenes where no spacing constant does, if the walk order is right:
the order frozen on g-qf's counts (columns, 22 of 22) missed 3 of the 29 counts of s275, s198 and
s119 (E875), and row order, named after the counts were read, gives 54 of 56 kept counts over U
287, 275, 198 and 119 and every run's peak within 3 pages in 29 of 29. For the 1500-vertex scene
E874's replay with partial renders gives 43 of 43 counts at 2048x2048 (exploratory). Open: the
walk order, held out on new scenes; what row order misses; scenes of many objects in general,
multi-kick scenes; the U clause as above.

Narrowed 2026-11-12 (round 6, laptop session R6-dpm stage r-b, E883; the question stays open). The
question line asked "what rule gives the partial-render count of a one-triangle scene of page need U
at the first threshold thr0 = P - 0x22 (E625's ... refuted at U = 287, E779 and E832; E854's
spacing thr0 + 0x20 - d fits each scene with its own d and failed held out at U 119 and 198, no
one d fitting U 287, 275, 198 and 119, E863), and does the page need U of HU1 ... hold for wide
scenes of many vertices and other shapes (E630)?"; it now adds E883. Every frozen headline of r-b
is "cannot tell", gated by an r-a0 control with no reading (E881). [HW, held out] The four g-qf
controls repeated E832's counts and four new scenes at 4096x4096 needed HU1's U (262, 243, 220,
179), 4 of 4 more for the U clause on scenes of the tool's triangle. [HW, post hoc: the scorer's
rows tallied without the gate] Row order, E875's post hoc walk, gave 28 of 32 counts (s262 4 of 8,
one partial render too many each time) and every run's peak exactly in 13 of 32 cells (within 3
pages in 28), so H-REPLAY as frozen fails on new scenes; column order gave 19 of 32 counts, E854's
d = 7/4 18 and d = 1 27 (E875's correction). Open: the rule of the count (what a partial render
frees, by scene); scenes of many objects and multi-kick scenes; the U clause as above.
