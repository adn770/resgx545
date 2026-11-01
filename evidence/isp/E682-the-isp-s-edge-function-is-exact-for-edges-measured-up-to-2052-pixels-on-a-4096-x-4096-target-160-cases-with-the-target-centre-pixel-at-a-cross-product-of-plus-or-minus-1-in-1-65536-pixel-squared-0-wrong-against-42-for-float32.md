+++
id = "E682"
claim = "For a long edge (the generator's bounds are 64 to 270 pixels on 512 x 512, 128 to 540 on 1024 x 1024, 256 to 1090 on 2048 x 2048, 512 to 2170 on 4096 x 4096; the edge nearest the target centre measures 105 to 238, 218 to 442, 453 to 1064 and 961 to 2052 pixels; vertices on the 1/256 grid) that passes the pixel centre (W/2, H/2) at a cross product of +1 or -1 in 1/65536 pixel squared (a distance of 1e-8 to 1e-7 pixel), the ISP draws that pixel iff the exact integer edge function says so, in 160 of 160 cases (40 on each of 512 x 512, 1024 x 1024, 2048 x 2048, 4096 x 4096, half with the pixel just inside, half just outside), 0 wrong pixels in the whole images; an edge function in float32 from pixel-unit coordinates would be wrong in 42 of them (9, 13, 11 and 9); only the target-centre pixel tests the edge; the prediction that the 4096 x 4096 cases would not be exact (P8b) failed"
unit = "isp"
method = "on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed and loaded), stock firmware, own_arm off, tool ~/sgxfive-test-1140 (the 11.38 tool plus tri --pixels-rle, a row a line as runs of equal pixels, and the clip words of the three vertices printed as the job carries them, written test first: test_vertex_words in userspace/libsgxfive/tests/test_render.c and three tests in test_cli.py; sources and binary sha256 in the dataset's env.toml), run/run_p1140.py, one process per job, a marker per job in the kernel log, every raw output gzipped, colour image only (no depth, no iteration); sets, hypotheses, alternatives and criteria frozen by hash (predictions-1140.toml, manifest-1140.sha256) after a pilot of 6 cases outside every set and before the first main job; recompute/recompute_p1140.py (numpy, scratch, shares no code with the run script) on the dumps After the freeze recompute/recompute_p1140.py was changed to read several run directories in one pass (no model or criterion changed): its sha256 no longer matches manifest-1140.sha256 while the other 11 frozen files and predictions-1140.sha256 do (freeze1140.sh verify fails on that one file only). Post hoc and not frozen: recompute/post_neg_1140.py, post_neg2_1140.py, post_tie_1140.py, post_thresh_1140.py, post_dist_1140.py and post_far_power_1140.py (outputs: the post-*-output.txt files of the dataset). manifest-1140.sha256 names the five tool files by tool/userspace/libsgxfive/ paths that the dataset does not have: tool-sources holds three of them (same sha256) under other names, test_render.c and test_cli.py are not in the dataset."
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["isp-coverage-envelope-1140"]
terms = []
+++
**What ran.** 160 jobs of group S5, built as E607's tiny-edge cases (extended Euclid: the edge's
integer direction (dx, dy), coprime, between 1/8 and 3/8 of the target in 1/256 units, and the
vertex v0 chosen so that dx (sy - y0) - dy (sx - x0) = +1 or -1 at the sample (sx, sy) = pixel (W/2,
H/2)'s centre; the third vertex on the interior side, all vertices inside the target at least a
pixel from its border): fit 80 (512 x 512, 1024 x 1024), held-out 80 (2048 x 2048, 4096 x 4096), 20
directions per target and both signs. The cross product of such an edge at a pixel across the target
is up to about 2^38 in units of 1/65536 pixel squared on the largest target.

**Results.** [HW] The sample pixel is drawn exactly when the model's sign says it is (e = +1: drawn;
e = -1: not drawn; the edge's own ties do not occur): 160 of 160; 0 mismatching pixels in the whole
images against the exact model (fit 0 of 80 inexact, 2048: 0 of 40, 4096: 0 of 40). The float32
variant of the model mispredicts 9 (512), 13 (1024), 11 (2048) and 9 (4096) of the 40. Criteria P7,
P7b and P8a passed; P8b, written as "at least one 4096 x 4096 case differs, because the edge
function is not exact to the 42 bits of its cross product", failed.

**What it shows.** [HW] The ISP's inside test on the 1/256 grid is an exact integer test, at the
target-centre pixel, for edges measured up to 2052 pixels on a target 4096 pixels wide (the
generator's bound is 2170): the cross product reaches 2^38 and resolves to 1. [infer] Its edge setup
therefore has at least 39 bits of exactness for such edges (a 24 bit float or a 32 bit integer would
fail), or evaluates relative to a vertex with enough bits; this is the width the simulator needs for
on-screen triangles and no more is shown: E684's far vertices (edges up to 2^21 pixels, cross
products up to 2^58) are not exact (a few pixels in 14 of 208 cases). The simulator may use exact
integers (64 bit) for the edge functions of triangles that lie inside a target up to 4096 x 4096.

**Both sides.** [HW] The test is two-sided, unlike E607's: the edge nearest the centre has a cross
product of exactly +1 in 80 cases and -1 in 80 (20 each per size and sign), the sample pixel is
covered in all the +1 cases and uncovered in all the -1 cases, and that edge has dy < 0 in 20, 14,
18 and 24 and dy > 0 in 20, 26, 22 and 16 cases (512, 1024, 2048, 4096), so both edge orientations
occur; the other edges are 1e8 to 1e10 units away. Only the target-centre pixel was tested; the
origin of the ISP's edge function is unknown (the [infer] clause above).
