+++
id = "E680"
claim = "Over 590 random triangles with vertices on the 1/256 pixel grid (small, medium, large -9% to +124% of the target except at 4096 x 4096 where no x is negative, vertices at pixel centres, 75 quads cut into two triangles) on 10 targets that E606 did not run or only partly ran (96 x 64, 130 x 66, 200 x 120, 512 x 256, 512 x 512, 640 x 480, 1000 x 600, 1024 x 768, 2048 x 1024, 4096 x 4096; 6 of them with a half-size that is not a power of two, 7 of them taller than 128), the ISP covers pixel (x, y) iff its centre is inside the triangle by the exact integer test with left and top edges owning ties, E606's rule without a change: 0 of 1092224240 pixels (whole images) differ, no tolerance, no clamp; the 75 shared edges leave 0 pixels drawn twice and 0 undrawn; the pixels that test the rule are the 603728 next to a triangle boundary, not the 1092224240 counted"
unit = "isp"
method = "on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed and loaded), stock firmware, own_arm off, tool ~/sgxfive-test-1140 (the 11.38 tool plus tri --pixels-rle, a row a line as runs of equal pixels, and the clip words of the three vertices printed as the job carries them, written test first: test_vertex_words in userspace/libsgxfive/tests/test_render.c and three tests in test_cli.py; sources and binary sha256 in the dataset's env.toml), run/run_p1140.py, one process per job, a marker per job in the kernel log, every raw output gzipped, colour image only (no depth, no iteration); sets, hypotheses, alternatives and criteria frozen by hash (predictions-1140.toml, manifest-1140.sha256) after a pilot of 6 cases outside every set and before the first main job; recompute/recompute_p1140.py (numpy, scratch, shares no code with the run script) on the dumps After the freeze recompute/recompute_p1140.py was changed to read several run directories in one pass (no model or criterion changed): its sha256 no longer matches manifest-1140.sha256 while the other 11 frozen files and predictions-1140.sha256 do (freeze1140.sh verify fails on that one file only). Post hoc and not frozen: recompute/post_neg_1140.py, post_neg2_1140.py, post_tie_1140.py, post_thresh_1140.py, post_dist_1140.py and post_far_power_1140.py (outputs: the post-*-output.txt files of the dataset). manifest-1140.sha256 names the five tool files by tool/userspace/libsgxfive/ paths that the dataset does not have: tool-sources holds three of them (same sha256) under other names, test_render.c and test_cli.py are not in the dataset."
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["isp-coverage-envelope-1140"]
terms = []
+++
**What ran.** 590 jobs of group S1 (seed 1140), one colour image each, vertices integers in 1/256
pixel (y down): per target 12 small (a 1 to 4 pixel box), 12 medium (8 to 40 pixels, at most a third
of the target), 12 large (each vertex uniform from -9% to +124% of the target), 8 centre (vertices
at pixel centres) and 8 quads cut along a diagonal into two triangles (half with centre corners, 16
triangles). Sets declared before any run: fit = 180 cases (512 x 256, 96 x 64, 640 x 480; the only
set a rule may be chosen on), held-out = 410 cases (512 x 512, 1024 x 768, 2048 x 1024, 200 x 120,
1000 x 600, 130 x 66 with 60 each, 4096 x 4096 with 50), plus 30 repeats of fit cases. At 4096 x
4096, 10 cases (ids 1400416 to 1400425, the end of that size's block) were not run for time: 5 of
its 8 quads were not run, 3 quads (6 triangles) ran, so the shared edges rest on 75 quads (fit 24,
held-out 51), not 80. Jobs: 1816 in the main and far runs, 1822 with the pilot of 6 (the dataset's
count), 0 flagged, 0 resets, no fault line in the kernel log. At 4096 x 4096 the large class drew no
negative x (observed x from +5.0% to +120.8% of the width; y reaches -7.9%); on the other sizes the
range -9% to +124% is drawn on both axes.

**Results.** [HW] The model is E606/E607's rule (vertex rounded half up to 1/256 pixel, here a
no-op; centre sample tested with exact integers, an edge owns a sample on it iff dy < 0, or dy = 0
and dx > 0 after the vertices are ordered to one winding). Mismatching pixels over whole images: fit
0 of 26664960 (180 cases); held-out 0 of 1065559280 (410 cases; 4096 x 4096: 0 of 838860800 pixels
in 50 cases), every class 0 (small, medium, large, centre, quad halves), every size 0. The shared
edges of the 75 quads: pixels drawn by both triangles 0; pixels the model gives to exactly one
triangle and the hardware to none 0. The 30 repeats are identical to the first image (30 of 30), the
tool's own triangle count equals the image's in every job, only the two colours (0xff00ff00,
0xff203040) occur. A second implementation (not in the dataset) on all 590 cases (vertices rounded
from the printed float32 clip words as exact rationals) also gives 0 mismatching pixels; every
vertex set so derived equals the case's (largest deviation 0.0068 of a 1/256 step, on 1000 x 600; 0
on the power-of-two sizes). The clip words printed per job are the float32 of px / (half-size x 256)
- 1; on a half-size that is not a power of two (48, 65 x 33, 100 x 60, 500 x 300, 320 x 240) they
are inexact and the image is nevertheless exact. Criteria P1, P2 and P2b of predictions-1140.toml
passed (P2b, the criterion that was expected to be the most exposed because the toml says a float32
window arithmetic at 4096 wide "may move a rounding there": 0 pixels).

**How much the pixel count tests.** The 1092224240 pixels are whole images, most of them far from
any boundary. The pixels next to a boundary (counted from the images with a second script; covered
with an uncovered 4-neighbour, or the reverse) number 603728 in all and 257673 at 4096 x 4096
(0.031% of its 838.9 million pixels). At that size the covered pixels are 35.2 million (centre
class, 8 cases: 14.7 million; large, 12 cases: 20.5 million); the 12 small cases cover 10 pixels in
all, the 12 medium 500, the 6 quad halves 2244. The 4096 x 4096 cases test the integer edge test
only: grid vertices make the rounding a no-op and the float32 clip words are exact there
(power-of-two half-size), so they are not a float32 test of the viewport conversion.

**What it shows.** [HW] For vertices on the 1/256 grid with coordinates from about -9% to +124% of
the target (E606's range; at 4096 x 4096 from +5% to +121% in x and from -8% in y) the coverage rule
needs no change on the ten sizes run, whatever the half-size, and the same holds for sizes of that
kind: even targets, half-sizes that are or are not powers of two. Nothing below 96 x 64 ran here
(E606 covers 64 x 64 up to 256 x 128), no 4096 x small target, no odd size, and at 4096 only the
square power-of-two size; the largest non-power-of-two half-sizes are 500 x 300 (1000 x 600) and 384
(1024 x 768). The depth part is not measured here: no depth store was run. [infer] The float32 clip
coordinate of a grid vertex is within about 2^-11 pixel of the intended window position at 4096
wide, far below the 1/512 pixel at which the rounding of a vertex would move, so the ISP's input at
these sizes is the grid vertex; this is why the images are exact, not a property of the ISP's own
arithmetic. The simulator may apply the rule at the sizes run and sizes of the same kind, with the
caveats of E681 (sub-grid fractions), E682 (edge precision) and E683 (negative coordinates).

**What it does not show.** Targets between the sizes run (odd macrotile alignments other than 130 x
66 and 1000 x 600), heights or widths above 4096 (the tool's limit), odd sizes, the depth plane and
the iterated attributes at these sizes, multisampling, other primitives, w != 1.
