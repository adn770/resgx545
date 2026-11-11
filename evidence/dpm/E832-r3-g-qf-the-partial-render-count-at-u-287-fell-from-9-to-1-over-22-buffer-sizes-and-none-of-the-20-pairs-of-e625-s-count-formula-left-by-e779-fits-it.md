+++
id = "E832"
claim = "R3-geo-c stages g-qf and g-qh (36 jobs at 4096x4096, the first threshold thr0 = P - 0x22 set by render_pb_pages and read from the job's own 0x0624, the count of partial renders read as the 0x0658 bit 0 stretches of the job's timeline): at U = 287 (the tool's triangle, one render) the controls passed (2 at P 0xa0, 1 at 0xb0 and 0xa3, as E625 and E779) and the 19 fit cells read a count that never rises with P, 9 at P 0x24 and 0x25, 8 at 0x27 to 0x29, 7 at 0x2c to 0x31, 6 at 0x32, 5 at 0x39 to 0x43, 4 at 0x44 and 0x53, 3 at 0x54 and 0x6d, 2 at 0x6e to 0xa2: the frozen verdict is that E625's count formula 1 + floor((U + k - thr0) / (thr0 + s)) is REFUTED at U = 287, none of the 20 (k, s) pairs that fit E625's and E779's cells (k -8 to 0, s 0x1b to 0x1e, the only pairs of k -60 to 60 and s 1 to 0x5f that do) fitting the 19 cells; in g-qh both scene gates passed (U 275 and 438, no partial render at P 0x422), the scene s275 (one triangle moved by 1024, 0) read 8 at P 0x26 and 0x27, 7 at 0x2a and 0x2b, 6 at 0x31 and 3 at 0x52, and the six cells of s438 were void by the frozen rule (the geometry-only first render overflowed before the last); the held-out verdict (REFUTED, none of the 0 pairs the fit left) follows from g-qf's and tests nothing more"
unit = "dpm"
method = "R3-geo-c stages g-qf and g-qh of the question-closing pass, round 3 (session L1b, the add-on C2 of decision R3-R1 a and R3-R2 a; second and third of three stages: g-qf 22 jobs, 3 controls and 19 fit cells; g-qh 14 jobs, 2 scene gates and 12 held-out cells, 6 a scene), dataset render-closing-r3-geo-c, on the laptop (host cedar, direct cable), 2026-11-10, stages started 16:54:23 and 17:03:04 laptop time (out/g-qf.log, out/g-qh.log), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded), stock firmware, tool ~/sgxfive-test-r1 (sha256 bf4f8be2d8a8fe50034559450928e05695dc96d396d4892f9b00ea6bc0d4f053); g-qf each job E779's command, tri --width 4096 --height 4096 -n 1 --keep-overflow --wait-ms 20000 --words --regs 0x0700-0x074c, g-qh E773's scenes with --keep-going (s275: -n 1 --move 1:1024,0; s438: -n 2 --geometry 1 --move 2:0,1024), the knob render_pb_pages written to P and read back, regtimeline 0x0624-0x0628, 0x0654-0x0660, 0x0700-0x0710, 0x0720-0x072c and 0x0748, a debugfs reset before each job, all 36 of class ok (rc 0, rc 1 for qc-s438); the 20 pairs re-derived by gen/r3_geo.py fit_pairs over the grid k -60 to 60, s 1 to 0x5f from E625's 10 and E779's 9 cells, every pair's count at every cell frozen in predictions/g-qf.tsv and g-qh.tsv before the run; counts, knob proofs, gates and verdicts by the frozen score/score_r3.py g-qf and g-qh (out/score-g-qf.txt, out/score-g-qh.txt; g-qh reads g-qf's kept data for the pairs the fit left), re-run on the kept files on 2026-11-11 with byte-identical output; the hits of each frozen pair over the cells at the end were counted after the run from the frozen prediction tables by a scratch script, not in the copy"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["render-closing-r3-geo-c:out/g-qf/", "render-closing-r3-geo-c:out/g-qh/"]
terms = ["Dynamic Parameter Management (DPM)", "Parameter Buffer (PB)"]
+++
**What ran.** E779 refuted E625's count formula, partial renders = 1 + floor((U + k - thr0) /
(thr0 + s)) with thr0 = P - 0x22, for the 24 pairs E625 had kept (k 2 to 13, s 0x1e or 0x1f). The
round 3 offline fit searched k from -60 to 60 and s from 1 to 0x5f and found 20 pairs that fit
E625's 10 and E779's 9 cells together: (-8, 0x1b), (-7, 0x1b), (-7, 0x1c), (-6, 0x1c),
(-6, 0x1d), (-5, 0x1c to 0x1e), (-4, 0x1c to 0x1e), (-3, 0x1c to 0x1e), (-2, 0x1c to 0x1e),
(-1, 0x1d), (-1, 0x1e) and (0, 0x1e). G-qf ran the 19 cells of P between 0x24 and 0xa2 where
those pairs predict different counts at U = 287 (the default triangle at 4096x4096, E773's HU1),
with E625's and E779's cells as controls. G-qh then held out the pairs that g-qf left on two
scenes of E773 (U 275 and 438), six cells each, chosen so that the 12 cells separate all 20.

**Frozen verdicts (as printed).** g-qf: `controls pass; monotone; E625's count family REFUTED at
U = 287: none of 20 (k, s) pairs fits the 19 usable fit cells; void []`. g-qh: `held out (6 cells
of scenes ['s275']): REFUTED, none of the 0 pairs the fit left predicts all held-out counts; void
['qh-s438-0x38', 'qh-s438-0x39', 'qh-s438-0x48', 'qh-s438-0x79', 'qh-s438-0x7b',
'qh-s438-0xec']`, with both scene gates `ok` (U 275 and 438, E773's).

**Results [HW].** Partial renders at U = 287 (every job's 0x0624 read P - 0x22):

| P | 0x24 | 0x25 | 0x27 | 0x28 | 0x29 | 0x2c | 0x2d | 0x31 | 0x32 | 0x39 | 0x3a |
|---|---|---|---|---|---|---|---|---|---|---|---|
| count | 9 | 9 | 8 | 8 | 8 | 7 | 7 | 7 | 6 | 5 | 5 |

| P | 0x43 | 0x44 | 0x53 | 0x54 | 0x6d | 0x6e | 0xa0 | 0xa1 | 0xa2 | 0xa3 | 0xb0 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| count | 5 | 4 | 4 | 3 | 3 | 2 | 2 | 2 | 2 | 1 | 1 |

0xa0, 0xa3 and 0xb0 are the controls. With E779 the step from 2 to 1 is now exact: 2 at 0xa2
(thr0 128), 1 at 0xa3 (thr0 129). Scene s275 (U = 275): 8 at P 0x26 and 0x27, 7 at 0x2a and
0x2b, 6 at 0x31, 3 at 0x52. Scene s438: in each of its six cells (P 0x38 to 0xec) the first render,
submitted as geometry only, overflowed, so no count of the closed scene was read: void by the
frozen rule of E773.

**What it shows.** [HW] The first dense count curve of one scene: 22 buffer sizes at U = 287,
monotone. No pair (k, s) with k in -60 to 60 and s in 1 to 0x5f fits E625's, E779's and these
cells together, since any such pair would be one of the 20 and each misses at least one of the 19
cells: E625's form is refuted over that grid at U = 287. G-qh's held-out verdict is empty: with no
pair left there was nothing to hold out, so s275's six counts are data, not a test.

**Read after the run [infer; post hoc, not held out].** Counted from the frozen prediction tables:
the pairs (0, 0x1e) and (-1, 0x1e) miss one g-qf cell each (0x27: 9 predicted, 8 read) and one
s275 cell (0x2a: 8 predicted, 7 read); (-2, 0x1e) to (-5, 0x1e) predict all six s275 cells and
miss 3 or more g-qf cells. So the form comes within one cell of both scenes but no pair fits both.
A planner's scratch refit on 2026-11-11 (`closing4/rank/q211_refit.py`, not in the copy) found no
c + floor or ceil((U + a) / (P + b)) and no two-segment form with a raised first threshold that
fits the 22 cells: the count is not a plain page quotient of these kinds. s438's cells were all at
P - 0x22 below 287 pages, so its first render (one triangle at 4096x4096, E773) could not fit
whole; the cells could not have been read as designed.

**What it does not show.** The page walk behind the count (what a partial render frees, Q210's
raise of the threshold); scenes other than the tool's triangle at 4096x4096; whether the count
depends on anything but U and P (s275's cells were not a test).
