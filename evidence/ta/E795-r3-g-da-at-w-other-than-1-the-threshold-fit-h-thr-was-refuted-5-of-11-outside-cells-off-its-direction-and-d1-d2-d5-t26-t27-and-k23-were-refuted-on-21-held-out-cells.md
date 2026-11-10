+++
id = "E795"
claim = "R3-geo stage g-da (27 jobs: the tool's triangle on a 64x64 target with x and y scaled by w, z and w the same at the three vertices, z / w in (-1, -0.5] so that the sum 0.5 + 0.5 q is exact; 6 controls and 21 held-out cells placed by the fraction of |z RZ(1/w)| in its float32 ulp): the 6 controls passed (E783's controls 0x3f000000 and 0x3e800000, the repeats of t4-m2p6-3 0x3d88888c and t4-m6p1-7 0x3d83a840, and w = 2 and 0.5 0x3e333340 and 0x3e1999a0), the object was written unclipped at the original position in 21 of 21 held-out cells, H-thr (the post hoc fit of E783's and Q230's notes: the product rounded away from zero iff its fraction exceeds one t in (0.3655, 0.4667)) was REFUTED with 5 of the 11 outside cells off its frozen direction (da-lo1 at fraction 0.0400 and da-mid2 at 0.3300 went up where it says down; da-mid3 at 0.3479, da-up1 at 0.5334 and da-up2 at 0.5916 stored a word that is neither neighbour of the product), and each of the six frozen depth formulas was refuted (misses of 21: D1 16, D2 10, D5 16, T26 8, T27 8, K23 19); the ten inside cells went down at fractions 0.3710, 0.3800 and 0.3989, neither neighbour at 0.4037 and up from 0.4112 to 0.4610; read after the run (no frozen row), the stored 1/w was RZ of 1/w in the 6 controls and 16 of the 21 held-out cells and one ulp above it in the 5 at w = 9 and 0.7"
unit = "ta"
method = "R3-geo stage g-da of the question-closing pass, round 3 (session L1, decisions R3-G1 and R3-G2; the first of nine stages, 27 jobs, R1's simulator-checked template vtx_wzclip.s with the constants Z and W), dataset render-closing-r3-geo, on the laptop (host cedar, direct cable), 2026-11-10, stage started 15:45:48 Mac time (out-l1.log), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded), stock firmware, tool ~/sgxfive-test-r1 (sha256 bf4f8be2d8a8fe50034559450928e05695dc96d396d4892f9b00ea6bc0d4f053); each job probe --temps 32 --pixels --tri vtxuse --width 64 --height 64 --dump-render with the job's vertex program, all 27 of class ok (rc 0), a debugfs reset before each job; the object decoded by the session's decoder over the landed pbdump and scored by the frozen score/score_r3.py g-da (out/score-g-da.txt), which refuses unless the freeze verifies; the candidate words come from gen/r3models.py (exact float32 arithmetic by rationals); the direction table (down = RZ of the product, up = one ulp above it, other = neither) and the H-thr verdict are the scorer's; the six control words were read after the run with the same decoder (the scorer prints only 'controls pass'), and the 1/w words (printed by the scorer) were compared with RZ of 1/w and the directions recomputed against the stored 1/w after the run, by scratch arithmetic in exact rationals not in the dataset"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["render-closing-r3-geo:out/g-da/"]
terms = ["PB_OBJ.RHW", "PB_OBJ.ISP_WORDS"]
+++
**What ran.** E783 recorded six depth words at w other than 1 that none of six frozen formulas
gave, and a dated note on E783 and Q230, made before this run, fitted one family to them post hoc
(H-thr: |z RZ(1/w)| rounded away from zero iff its fraction in its ulp exceeds one t in (0.3655,
0.4667)), resting on one word, t4-m2p6-3. G-da tests that fit on cells it was not fitted to: with
z / w in (-1, -0.5] the stored word is 0.5 + 0.5 q' with q' the float32 the product was rounded to,
so each cell reads as "down" (RZ of the product) or "up" (one ulp above it). The frozen direction:
the low and mid cells (fractions 0.02 to 0.10 and 0.30 to 0.36) down, the high cells (0.47 to
0.498) and those above one half up, the ten inside cells flipping once along the fraction. The
frozen formulas D1, D2, D5, T26 (t = 3/8), T27 (t = 7/16) and K23 were scored on every held-out
cell.

**Frozen verdict (as printed).** `controls pass; H-thr REFUTED: 5 of 11 outside cells off the
frozen direction (low and mid down, high and above half up); held out: consistent ['in band (x, y
scaled by w): no clip (21)'], refuted ['D1 (RN(z RZ(1/w)), the product to nearest) (16 of 21)',
'D2 (RZ(z/w)) (10 of 21)', 'D5 (RZ(z RZ(1/w)), the product toward zero) (16 of 21)', 'T26 (...)
(8 of 21)', 'T27 (...) (8 of 21)', 'K23 (z cut to 23 bits, the product rounded away from zero) (19
of 21)']`. The counts in the refuted list are misses. The generic tally of the same line lists
"void runs for" the cell geometry, the two frame rows and H-thr: rows it does not score; the H-thr
verdict is the stage's own reading before it.

**Results [HW].** The controls stored the words frozen for them: 0x3f000000 (z = 0, w = 3),
0x3e800000 (z = -0.5, w = 1), 0x3d88888c (the repeat of t4-m2p6-3, the one word the fit rests on),
0x3d83a840 (t4-m6p1-7), 0x3e333340 (w = 2) and 0x3e1999a0 (w = 0.5). The 21 held-out objects were
unclipped at the original window position, and the 1/w words were those of the w used. The stored
depth word per cell, in the order of the fraction:

| job | z, w | fraction | cell | word | direction | frozen |
|---|---|---|---|---|---|---|
| da-lo1 | -8.64, 9 | 0.0400 | low | 0x3ca3d700 | up | down |
| da-lo2 | -4.605, 5 | 0.0790 | low | 0x3d21cac8 | down | down |
| da-mid1 | -8.69, 11 | 0.3088 | mid | 0x3dd70a44 | down | down |
| da-mid2 | -22.586, 23 | 0.3300 | mid | 0x3c1374c0 | up | down |
| da-mid3 | -0.5565, 0.7 | 0.3479 | mid | 0x3dd1eb80 | other | down |
| da-in1 | -11.248, 19 | 0.3710 | inside | 0x3e50e562 | down | one flip |
| da-in2 | -3.72, 6 | 0.3800 | inside | 0x3e428f5e | down | one flip |
| da-in3 | -1.0621, 1.3 | 0.3989 | inside | 0x3dbb6458 | down | one flip |
| da-in4 | -0.6174, 0.7 | 0.4037 | inside | 0x3d71a9f8 | other | one flip |
| da-in5 | -0.2979, 0.3 | 0.4112 | inside | 0x3b656100 | up | one flip |
| da-in6 | -1.1739, 1.3 | 0.4247 | inside | 0x3d46a7e8 | up | one flip |
| da-in7 | -8.151, 11 | 0.4425 | inside | 0x3e049ba6 | up | one flip |
| da-in8 | -0.2904, 0.3 | 0.4512 | inside | 0x3c831280 | up | one flip |
| da-in9 | -16.302, 19 | 0.4568 | inside | 0x3d916874 | up | one flip |
| da-in10 | -4.695, 5 | 0.4610 | inside | 0x3cf9db20 | up | one flip |
| da-hi1 | -4.6, 5 | 0.4800 | high | 0x3d23d710 | up | up |
| da-hi2 | -0.285, 0.3 | 0.4800 | high | 0x3ccccce0 | up | up |
| da-hi3 | -1.1167, 1.3 | 0.4885 | high | 0x3d906248 | up | up |
| da-hi4 | -16.511, 19 | 0.4977 | high | 0x3d8624e0 | up | up |
| da-up1 | -8.199, 9 | 0.5334 | above half | 0x3d364598 | other | up |
| da-up2 | -8.676, 9 | 0.5916 | above half | 0x3c9374c0 | other | up |

z and w are the float32 constants of the tables (shown rounded). "Other" is a word that is neither
RZ of the product z RZ(1/w) nor one ulp above it.

**Read after the run [HW, no frozen row].** The stored 1/w word (the same at the three vertices of
a job) was RZ of 1/w in the six controls and in 16 of the 21 held-out cells (w = 0.3, 1.3, 5, 6,
11, 19 and 23), and one ulp above it in 5: every cell at w = 9 (da-lo1, da-up1, da-up2:
0x3de38e39, RZ 0x3de38e38) and at w = 0.7 (da-mid3, da-in4: 0x3fb6db6e, RZ 0x3fb6db6d). Four of
the five cells off H-thr's frozen direction (all but da-mid2) and the inside cell that read "other"
(da-in4) are these five.

**The same directions against the stored 1/w [infer: arithmetic after the run, exact rationals,
not a test].** Taking the product as z times the stored 1/w word, da-lo1 reads down at fraction
0.120, da-mid3 up at 0.461, da-in4 up at 0.639 and da-up1 and da-up2 up (0.558, 0.676); the other
sixteen cells keep their reading. Then da-mid2 (w = 23, stored 1/w = RZ) went up at 0.3300 while
da-in1 to da-in3 went down at 0.3710 to 0.3989, so no single threshold t fits the cells in this
reading either.

**What it shows and does not.** The fit's one word repeated (0x3d88888c), so the run reads the same
hardware as E783, and the threshold family it suggested does not hold: five of the eleven outside
cells are off its direction as frozen, and read against the stored 1/w (after the run) a cell at
fraction 0.33 still goes up below three that go down. None of D1, D2, D5, T26, T27 and K23 fits.
The stored 1/w is not RZ of 1/w at every w: it was one ulp above at w = 9 and 0.7, in all seven
jobs at those w across g-da and g-db (E796), where E754, E782 and E783 saw RZ at the w they ran;
what decides it is not read here (Q230). The object stays unclipped at the original position. No
depth rule at w other than 1 is offered; the words are recorded here and the simulator keeps
refusing the depth at w other than 1 (Q230).
