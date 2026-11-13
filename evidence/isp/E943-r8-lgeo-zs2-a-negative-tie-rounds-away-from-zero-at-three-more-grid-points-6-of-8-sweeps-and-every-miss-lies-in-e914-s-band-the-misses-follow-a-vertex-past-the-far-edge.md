+++
id = "E943"
claim = "R8-lgeo stage zs2 (Q260; 160 sweep steps and 5 controls, 512 x 256 and 256 x 512, vertices in 1/4096 pixel, no fault): a negative coordinate 1/512 above the grid rounds away from zero at -1/256, -1.25 and -17.75 on both axes (the aimed pixel flips between d 0 and +1: HA's step held on 6 of 8 sweeps, HU's on 0), the two others, -200.5 x and -100.5 y, aiming at a pixel within 4e-5 pixel of an edge of 300 to 600 pixels; on the long-edge sweeps E914's step table held on 10 of 24, H-SHORT (exactly HA's where no edge reaches 250 pixels) on 66 of 70 rows, H-BAND (off HA's image only within 6.4e-4 pixel of an edge of 250 pixels or more) on 90 of 90, and on 256 x 512 the misses followed the transposed scene (H-GEOM 16 of 24, H-YAXIS 8); read after the run, every one of the 738 pixels off HA's image lies within 6.4e-4 pixel of an edge of 195 to 904 pixels, and every sweep with a vertex past the target's far edge misses (12 of 12); frozen verdicts 'Q260 negative ties at other grid points: HA's step ... held is not supported: 6 held, 2 FAILED', 'E914's step table ... 10 held, 14 FAILED', 'H-SHORT ... 66 held, 4 FAILED', 'H-BAND ... held (90 of 90 rows decided)', 'H-YAXIS ... 8 held, 16 FAILED', 'H-GEOM ... 16 held, 8 FAILED'"
unit = "isp"
method = "R8-lgeo stage zs2 of the question-closing pass, round 8 (decision R8-8; plan closing8/leftovers/exp-leftovers-r8.md section 3, session L2), dataset render-closing-r8-lgeo, on the laptop, 2026-11-13, one attempt out/20261113-024441 (lead log out/run-r8m.log; no stop, no lead decision), kernel 7.3.0-resgx545, module srcversion 37EC97AB0CB37213C42FCCC (fork 664fd0d0), stock firmware, tool ~/sgxfive-test-rgn4 (t4, sha256 e6951558..., resgx545 4623753), built on the session kit (resgx545 91f21da); 165 jobs `tri --keep-overflow --wait-ms 20000 --width W --height H --tri-unit 12 --tri-v ... --pixels`: E681's and E683's first 512 x 256 cases and E914's -0.5 x sweep at d -1, 0, +1 (controls, kept hashes); sweeps of five steps d = -2 to +2 of 1/4096 pixel about the 1/512 tie above a grid point, E914's construction (gen/zsmodel.py: the swept vertex's edge aimed through a pixel centre C, B = C + 2 (C - A) beyond it, the third vertex 40 pixels past B level with A): (g) -1/256, -1.25, -17.75 and -200.5 (x) / -100.5 (y) aimed at pixel 0, (l) -64.5 and +64.5 on both axes aimed 65 and 68 (at -64.5; 1 and 4 at +64.5), 100 and 300 (x) / 200 (y; +64.5 y 190) pixels away at 512 x 256, (t) the 100 and long aims again on 256 x 512 with the scene transposed; every job class ok. Frozen before the first job (FROZEN.sha256 90ab0f4d..., PREDICTIONS.sha256 df01463d..., FROZEN.commits at resgx545 91f21da and resgx545-data 1e83dc86): per row the covered image under HA (half away from zero for negative coordinates, half up otherwise) and HU on E606's exact coverage (gen/zsmodel.py, which reproduces r7-geo's covered images of all 230 E914 rows, tests/test_models.py), the aimed pixel's state per step and the longest edge; H-SHORT and H-BAND split by that edge at 250 pixels; H-YAXIS against H-GEOM on the 256 x 512 rows that miss HA. Scored by the frozen score/score.py zs2 in the run (score-zs2.txt); at the fold the same scorer re-ran byte-identical on the kept files and every kept file decompresses to the raw sha256 the laptop logged (out/fold/reproduce.sh). Post hoc at the fold, not frozen: out/fold/zs2_read.py (each pixel off HA's image, its distance from the nearest edge line of the HA-rounded triangle and that edge's length; the aimed pixel's distance) and out/fold/zs2_far.py (whether a vertex lies past the far edge, against the sweeps that miss)"
tiers = ["HW", "infer"]
date = "2026-11-13"
data = ["render-closing-r8-lgeo:out/20261113-024441/zs2/", "render-closing-r8-lgeo:out/fold/"]
terms = []
+++
**What ran.** E914 found the tie of a negative coordinate going away from zero on five sweeps,
the rest of its misses on long y edges within 6.4e-4 pixel of the edge line (post hoc). Stage zs2
froze HA (half away from zero) and swept ties at other grid points (-1/256, -1.25, -17.75,
-200.5 x, -100.5 y), long edges at -64.5 and +64.5 on both axes at four aims each, and the 100 and
long aims again on a transposed 256 x 512 target, with E914's step table, H-SHORT, H-BAND and the
y-axis question (H-YAXIS against H-GEOM) frozen.

**Frozen verdict (as printed).** `Q260 negative ties at other grid points: HA's step (the aimed
pixel flips between d 0 and +1) held is not supported: 6 held, 2 FAILED, 0 cannot tell of 8`;
`HU's step held is not supported: 0 held, 8 FAILED`; `Q260 long edges, E914's step table (d +1
negative, d 0 positive): the step table held is not supported: 10 held, 14 FAILED`; `Q260
H-SHORT: ... is not supported: 66 held, 4 FAILED`; `Q260 H-BAND: the image differs from HA's only
within 6.4e-4 pixel of an edge of 250 pixels or more (90 of 90 rows decided)`; on 256 x 512
`H-YAXIS ... 8 held, 16 FAILED` and `H-GEOM ... 16 held, 8 FAILED`. The five controls passed.

**Results [HW].** The aimed pixel flips one step after the tie on the six (g) sweeps at -1/256,
-1.25 and -17.75 (x and y) and on -64.5 x aimed 65, 68 and 100 (100 on both targets), at the
tie on +64.5 aimed 1 and 4 (x and y) and x 100 (both targets); it does not flip at all on -200.5 x,
-100.5 y, -64.5 y (every aim),
-64.5 x 300, +64.5 x 300, +64.5 y 100 and 190. 35 rows on 512 x 256 and 24 on 256 x 512 are off
HA's image; the same scene gives the same misses on either target (-64.5 aimed 300: 51 pixels on
both).

**Read after the run (post hoc, not frozen; out/fold/zs2_read.py, zs2_far.py).** All 738 pixels
off HA's image lie within 6.4e-4 pixel (0 to 6.4e-4; 9 exactly on the line) of an edge line of
195 to 904 pixels. On every sweep that does not flip, the aimed pixel lies 1.9e-5 to 3.7e-4 pixel
from a long edge. A vertex of the rounded triangle lies past the target's far edge (x > W or y >
H) on 12 sweeps, and all 12 miss; of the 20 without one, 16 are exact and 4 miss 1 to 3 pixels
(-200.5 x, -100.5 y, -64.5 y aimed 65 and 68, from d +1 only). The transposed scene keeps a far
vertex where the original had one, which is why the misses follow it; E914's y-only misses at
+-64.5 aimed 100 were the sweeps whose third vertex lay past H = 256.

**What it shows.** [HW] A negative window coordinate 1/512 above the 1/256 grid is rounded away
from zero wherever the aimed pixel is clear of E914's band (the 6 (g) sweeps at three more grid
points on both axes and 4 at -64.5 x, with E914's five), and HU's step is refuted on all 8 (g)
sweeps. Every image differs
from HA's only within 6.4e-4 pixel of an edge line. [infer] The rounding is HA; what remains is
the evaluation of pixels within 6.4e-4 pixel of a long edge, more often wrong when a vertex lies
past the far edge (E684's far-vertex band), not a rounding of the swept vertex.

**What it does not show.** Which arithmetic decides the pixels in the band (which side each goes),
whether an edge shorter than 195 pixels or a vertex past the near edge alone ever misses, and the
far-vertex reading as a rule (post hoc, not held out).
