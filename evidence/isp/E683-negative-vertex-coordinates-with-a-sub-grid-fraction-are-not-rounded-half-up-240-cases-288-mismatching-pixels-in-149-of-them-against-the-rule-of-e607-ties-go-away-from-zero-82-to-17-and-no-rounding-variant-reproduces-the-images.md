+++
id = "E683"
claim = "With vertices at negative window coordinates (one to three negative coordinates per triangle, from -1/256 pixel down to -843 pixels, in x, in y or in both) with fractions of 1/4096 pixel and an edge aimed at a pixel centre, E607's rule (every coordinate rounded half up to 1/256 pixel, then the exact centre test) is wrong: 76 pixels in 51 of 80 fit cases and 212 pixels in 98 of 160 held-out cases (criteria P5 and P6 failed), on 64 x 64, 96 x 64, 130 x 66, 512 x 256, 640 x 480 and 1024 x 768; none of seven other rounding variants reproduces them (half away from zero: 23 pixels in 16 fit cases and 78 in 51 held-out cases, the best; half down 33 and 109, half to even 62 and 147, no rounding 84 and 240, floor 142 and 358, ceil 157 and 491, toward zero 153 and 379), and post hoc, the exact ties at a negative coordinate go away from zero in 82 of 99 decided cases (a coordinate of x -3.5/256 pixel goes to -4/256, not -3/256)"
unit = "isp"
method = "on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed and loaded), stock firmware, own_arm off, tool ~/sgxfive-test-1140 (the 11.38 tool plus tri --pixels-rle, a row a line as runs of equal pixels, and the clip words of the three vertices printed as the job carries them, written test first: test_vertex_words in userspace/libsgxfive/tests/test_render.c and three tests in test_cli.py; sources and binary sha256 in the dataset's env.toml), run/run_p1140.py, one process per job, a marker per job in the kernel log, every raw output gzipped, colour image only (no depth, no iteration); sets, hypotheses, alternatives and criteria frozen by hash (predictions-1140.toml, manifest-1140.sha256) after a pilot of 6 cases outside every set and before the first main job; recompute/recompute_p1140.py (numpy, scratch, shares no code with the run script) on the dumps After the freeze recompute/recompute_p1140.py was changed to read several run directories in one pass (no model or criterion changed): its sha256 no longer matches manifest-1140.sha256 while the other 11 frozen files and predictions-1140.sha256 do (freeze1140.sh verify fails on that one file only). Post hoc and not frozen: recompute/post_neg_1140.py, post_neg2_1140.py, post_tie_1140.py, post_thresh_1140.py, post_dist_1140.py and post_far_power_1140.py (outputs: the post-*-output.txt files of the dataset). manifest-1140.sha256 names the five tool files by tool/userspace/libsgxfive/ paths that the dataset does not have: tool-sources holds three of them (same sha256) under other names, test_render.c and test_cli.py are not in the dataset."
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["isp-coverage-envelope-1140"]
terms = []
+++
**What ran.** 240 jobs of group S3 (fit 80: 64 x 64 and 512 x 256; held-out 160: 96 x 64, 640 x 480,
1024 x 768, 130 x 66; 40 each), coordinates in 1/4096 pixel (tool unit 12). Each case: a random
pixel centre C, a vertex A with one or both coordinates negative (a magnitude of 1 to 399 multiples
of 1/256 pixel, up to 16 times more in half of them; 25 of the 240 cases have a coordinate below -25
pixels, 13 below -100, the minimum is -843.2 pixels, so the far-vertex band of E684 (vertices 512
pixels and more away) cannot be excluded in those 25; with a fraction of 7, 8 or 9 sixteenths of the
1/256 step in 5 of 6, i.e. at or next to the tie), a second vertex B on the ray from A through C (so
the edge A-B runs within 1/8192 pixel of C), the third vertex random; kept only when the seven
rounding variants (below) gave at least three different images, so the cases separate the variants
by construction (the selection used the model, not the hardware).

**Results.** [HW] The image of each case compared with the model under each rounding of the 1/4096
coordinate to the 1/256 grid (mismatching pixels, cases with at least one): half up (E607's rule:
floor(n + 1/2)) fit 76 (51), held-out 212 (98); half down 33 (24), 109 (64); floor 142 (64), 358
(131); ceil 157 (69), 491 (147); toward zero 153 (70), 379 (150); half away from zero 23 (16), 78
(51); half to even 62 (39), 147 (71); no rounding at all 84 (55), 240 (121). So no variant fits (0
was needed) and the rule chosen on fit (half up) is refuted, on fit and held-out; criteria P5 and P6
failed, P5b (each alternative mispredicts) passed. The one criterion that was frozen for a pass, the
rule of E607, fails only at negative coordinates (the positive vertices of the same cases are on the
same footing as E681's). Post hoc (recompute/post_tie_1140.py, post_neg_1140.py, post_neg2_1140.py,
post_thresh_1140.py and post_dist_1140.py, none frozen): taking one coordinate that sits exactly on
a tie (fraction 8/16) and letting it go down instead of up, the image is reproduced alone in 82
negative cases (39 x, 43 y) and the half-up value alone in 17 (9 x, 8 y); for positive ties 16 half
up (8 and 8) and 5 down: ties at negative coordinates mostly go away from zero. A threshold scan
(post_thresh_1140.py) t in floor((n + t)/16) for negative n gives its minimum at t = 7 (the
half-away rounding: 23 and 78 pixels), t = 8: 76 and 212, t >= 9: 84 and 227 and more. The 101
pixels that half-away leaves wrong (post_dist_1140.py) lie 3e-6 to 2.2e-3 pixel from an edge line of
the rounded triangle (median 3.6e-4; the largest are about the 1/512 pixel of a one-step move of a
vertex), so they reach above the 5.6e-4 pixel band of E684, but the mismatch rate does not depend on
the distance of the vertex (coordinate above -1.6 pixels: 72 of 124 cases inexact; below -25 pixels:
19 of 25), so the far-vertex band does not explain them; post_neg2_1140.py lists, for the 16 fit
cases that half away from zero leaves wrong, the offsets of the six coordinates (-1, 0, +1 of 1/256
pixel) from that rounding that reproduce the image (post-neg2-output.txt: the fewest moves are one
step in 12 of the 16 cases, two in 1, three in 2, and none reproduces the image in 1); in 10 of 149
inexact cases no combination of floor or ceil of the six coordinates reproduces the image.

**What it shows.** [HW] The vertex rounding of E607 does not hold at negative coordinates with a
sub-grid fraction: E607's rule is a statement about x >= 0 and stays so. [infer] The ties go away
from zero (the sign is kept, the magnitude rounded half up); this does not close it, since 101
pixels remain, which the sign-magnitude rounding does not explain: an effect of a different size (an
edge anchored at another vertex, a coordinate offset) acts at negative coordinates as well, and the
simulator must not claim it (Q260). The simulator keeps refusing vertices with a negative coordinate
that has a fraction finer than 1/256 pixel; negative vertices on the 1/256 grid (E606's 9 cases with
a negative coordinate, and the large cases of E680 down to -9%) remain exact (no fraction to round).
A variant on the vertex as the float32 clip words give it (exact, float32 (c + 1) * half, float32 c
* half + half) was also tried against the eight roundings: none reaches 0 (the best, half away from
zero, leaves 23 fit and 78 held-out pixels on the first two), so the refutation does not depend on
the float32 viewport; this check is post hoc and not in the dataset. A positive mirror control (the
same construction at x > W) was not run (Q260).
