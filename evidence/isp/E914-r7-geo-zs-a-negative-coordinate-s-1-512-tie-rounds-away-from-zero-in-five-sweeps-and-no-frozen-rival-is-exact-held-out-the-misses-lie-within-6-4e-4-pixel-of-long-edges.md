+++
id = "E914"
claim = "R7-geo stage zs (Q260; 230 jobs on 512 x 256, vertices in 1/4096 pixel, no fault): no frozen rounding is exact on the 143 held-out rows (half away from zero for negative coordinates, HA, and SETUP with c = 7, the one c the -0.5 x sweep fits, 125 of 143; half up, HU, 121; HU with the far side rounded half down, FAR, 119), and HU at +0.5 y and +64.5 x and y, the positive mirror, gave 42 of 51; read after the run, the image changes one step after the 1/512 tie on the sweeps at -0.5, -3.5 and -64.5 x and -0.5 and -3.5 y (the tie of a negative coordinate going away from zero, every step of those five sweeps HA's), at the tie on the +0.5, +64.5 and far-side sweeps (half up, FAR refuted 2 of 2 at the far tie), and not at all at -64.5 y; the 18 held-out rows no rival matches (all 17 steps of -64.5 y and one of 24 non-tie cases) and the 9 mirror misses (+64.5 y at and after the tie) differ from HU in 1 to 11 pixels, each within 6.4e-4 pixel of an edge 258 to 313 pixels long; controls pass (E681's case 1400606, E683's case 1401234, the +0.5 x sweep 17 of 17 under HU); frozen verdicts 'Q260 H-HA exact on the held-out rows is not supported: 125 held, 18 FAILED' and 'HU at +0.5 y and +64.5 (the mirror) is not supported: 42 held, 9 FAILED'"
unit = "isp"
method = "R7-geo stage zs of the question-closing pass, round 7 (decisions R7-2 a, R7-7 a, decision 4 a of closing7/rank/rank-round7.md; plan R7-3), dataset render-closing-r7-geo, on the laptop (host cedar), 2026-11-12, attempt out/20261112-211113 (stage started 21:50:06 Mac time, run-r7g-2.log), kernel 7.3.0-resgx545, module srcversion 41E2F5C756F96D20F7109A4 (fork 3f0b3e74, installed = loaded, knobs at their defaults at the stage start and end), stock firmware sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a, tool ~/sgxfive-test-rgn4 (t4, sha256 e6951558...); 230 jobs `tri --tri-unit 12 --tri-v ... --pixels` at 512 x 256: E681's and E683's first 512 x 256 cases (kept hashes, controls), 11 sweeps of 17 steps (d = -8 to +8 in 1/4096 pixel about the 1/512 tie above the grid point) of one vertex's coordinate at -0.5, -3.5, -64.5 (x and y), +0.5 (x: control under HU; y: mirror), +64.5 (x and y: mirror) and W + 0.5 / H + 0.5 (the far side), the edge from that vertex aimed through a pixel centre 1, 4 or 100 pixels away, and 24 cases with one non-tie negative coordinate (E683's construction); every job class ok, health ok after the stage. Frozen before the first job (FROZEN.sha256 84ba6d23..., PREDICTIONS.sha256 a52a549b...): HU, HA, FAR and SETUP(c) for c = 0 to 15 (the -0.5 x sweep the fit set, every other row but the controls and the mirror held out), each rounding put on E606's exact coverage (gen/models.py); at 1/4096 the threshold 7/16 of E683's scan is HA, so it is not a separate rival (README deviation 4). The first attempt ran nothing (E909's method). Scored by the frozen score/score_g.py zs (score-zs.txt, with its model-free STEP lines: the steps at which each sweep's image changes); at the fold the same scorer re-ran byte-identical on the kept files, and the 1154 kept files decompress to the raw sha256 the laptop logged (fold/reproduce.sh). Post hoc at the fold, not frozen: fold/zs_read.py (each row's rival matches and pixels off HU, and for each row no rival matches the off pixels' distance from the nearest edge line)"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r7-geo:out/20261112-211113/zs/", "render-closing-r7-geo:fold/"]
terms = []
+++
**What ran.** E607 and E681 hold the ISP's rounding of a window coordinate to 1/256 pixel half up
(HU) at x >= 0. E683 refuted HU for negative coordinates finer than the grid (288 pixels wrong in
149 of 240 cases), found half away from zero (HA) best and still 101 pixels wrong, and Q260 asked
for sweeps across the tie. Stage zs swept one vertex's coordinate in 17 steps of 1/4096 pixel
across the 1/512 tie at -0.5, -3.5 and -64.5 pixels on each axis, with the vertex's edge aimed
through a pixel centre so that the step at which that pixel flips shows the rounding; the same at
+0.5 and +64.5 (the positive mirror, HU predicted by E681) and past the far edge (W + 0.5, H +
0.5); and 24 cases with one negative coordinate away from any tie. The rivals were frozen before
the run: HU, HA, FAR (HU, but half down past the far edge) and SETUP(c) (the negative coordinate
plus a fixed offset c / 16 of a grid step before the floor; c fitted on the -0.5 x sweep).

**Frozen verdict (as printed).** `FIT SETUP(c) on the -0.5 x sweep: c in [7]`; on the 143
held-out rows `Q260 H-HU ... 121 held, 22 FAILED`, `Q260 H-HA ... 125 held, 18 FAILED`, `Q260
H-FAR ... 119 held, 24 FAILED`, `Q260 SETUP(c=7) ... 125 held, 18 FAILED`, each `exact on the
held-out rows is not supported`; `Q260 positive mirror HU: HU at +0.5 y and +64.5 (the mirror) is
not supported: 42 held, 9 FAILED, 0 cannot tell of 51`. The STEP lines: `-0.5 x`, `-0.5 y`, `-3.5
x`, `-3.5 y`, `-64.5 x`: image changes at d = 1; `-64.5 y`: none; `0.5 x`, `0.5 y`, `64.5 x`,
`64.5 y`, `far x`, `far y`: d = 0. The four controls passed.

**Results [HW].** By sweep (`score-zs.txt`, and `fold/zs_read.py` post hoc for the rival of each
step and the pixels off HU's image):

| sweep | image changes at | rows matching HU / HA / FAR | off HU (pixels) |
|---|---|---|---|
| -0.5 x (fit), -0.5 y, -3.5 x, -3.5 y | d = 1 | 16 / 17 / 16 | 1 at d = 0 |
| -64.5 x | d = 1 | 16 / 17 / 16 | 8 at d = 0 |
| -64.5 y | never | 0 / 0 / 0 | 11 below the tie, 2 from it on |
| +0.5 x (control), +0.5 y, +64.5 x | d = 0 | 17 / 17 / 17 | 0 |
| +64.5 y | d = 0 | 8 / 8 / 8 | 7 from the tie on |
| far x, far y | d = 0 | 17 / 17 / 16 | 0 |
| 24 non-tie cases | | 23 / 23 / 23 | 1 in case 01 (y) |

HA and SETUP(7) are the same image on every row here.

**Read after the run (post hoc, not frozen; `fold/zs_read.py`).** Every pixel on which a row that
no rival matches differs from HU's image lies within 6.4e-4 pixel of an edge line of 258 to 313
pixels: -64.5 y loses 11 pixels at 2.6e-4 to 6.4e-4 pixel below the tie and 2 (7.5e-5 and 1.5e-4)
from it on, +64.5 y keeps 7 at 0 to 4.5e-4 pixel from the tie on, non-tie case 01 loses one at
9.1e-5. Those are the y sweeps aimed 100 pixels away and one long y edge; the x sweeps aimed as far
match HA exactly.

**What it shows.** [HW] On five of the six negative sweeps a coordinate 1/512 above a grid point
is rounded down, away from zero, and every other step is rounded to the nearest grid point; on the
positive and far-side sweeps the tie rounds up, so the far side rounds half up as the near side
does (FAR refuted at its own two rows). No frozen rounding reproduces every held-out row: the
misses are not at the swept tie but along the long edges of the y sweeps at +-64.5. [infer] The
misses lie inside the band of E684 (pixels within 5.6e-4 pixel of an edge line with a far vertex
drawn otherwise than the exact rule), so the rounding at a negative tie is HA and what remains is
the edge evaluation of long edges, not a rounding; this was read after the run and is not a rule.

**What it does not show.** Why the y sweeps at +-64.5 differ and not the x ones (the edge
evaluation is not modelled at 1e-4 pixel); ties at other fractions than 1/512 above the grid; other
targets than 512 x 256; whether HA with a rule for those long edges would reproduce E683's 101
pixels.
