+++
id = "E684"
claim = "With one vertex at +-2^k pixels (k = 9 to 21, up to 2^29 units of 1/256, in x, in y or both, 8 directions) and the other two vertices inside a 64 x 64 or a 512 x 512 target (one far vertex only, on the 1/256 grid in all 208 cases: no sub-grid fraction; no 4096 target), 208 jobs, none flagged and none needing a GPU reset, the ISP's coverage equals the exact rule of E606/E607 in 194 of 208 cases and differs by 1 or 2 pixels (16 pixels in all) in 14 (2 of 104 on 64 x 64, 12 of 104 on 512 x 512), each of those pixels within 5.6e-4 pixel of an edge line of the triangle (median 1.2e-4, nearest 3.5e-5) and on edges from 1008 to 262551 pixels long; no case of any k shows a clamp or a wrap of the vertex range: every clamp to 2^20 pixels or less and every wrap into 2^21 pixels or less is excluded by the cases on which it would differ; criteria P9 (all cases with |v| <= 2^15 pixels exact: 9 mismatch) and P10 (first mismatch at k = 16: it is at 10 on 64 x 64 and 9 on 512 x 512) failed"
unit = "isp"
method = "on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed and loaded), stock firmware, own_arm off, tool ~/sgxfive-test-1140 (the 11.38 tool plus tri --pixels-rle, a row a line as runs of equal pixels, and the clip words of the three vertices printed as the job carries them, written test first: test_vertex_words in userspace/libsgxfive/tests/test_render.c and three tests in test_cli.py; sources and binary sha256 in the dataset's env.toml), run/run_p1140.py, one process per job, a marker per job in the kernel log, every raw output gzipped, colour image only (no depth, no iteration); sets, hypotheses, alternatives and criteria frozen by hash (predictions-1140.toml, manifest-1140.sha256) after a pilot of 6 cases outside every set and before the first main job; recompute/recompute_p1140.py (numpy, scratch, shares no code with the run script) on the dumps After the freeze recompute/recompute_p1140.py was changed to read several run directories in one pass (no model or criterion changed): its sha256 no longer matches manifest-1140.sha256 while the other 11 frozen files and predictions-1140.sha256 do (freeze1140.sh verify fails on that one file only). Post hoc and not frozen: recompute/post_neg_1140.py, post_neg2_1140.py, post_tie_1140.py, post_thresh_1140.py, post_dist_1140.py and post_far_power_1140.py (outputs: the post-*-output.txt files of the dataset). manifest-1140.sha256 names the five tool files by tool/userspace/libsgxfive/ paths that the dataset does not have: tool-sources holds three of them (same sha256) under other names, test_render.c and test_cli.py are not in the dataset."
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["isp-coverage-envelope-1140"]
terms = []
+++
**What ran.** Group S4, run last and one job at a time (a plain 64 x 64 triangle had to draw before
each job): for k = 9 to 21 and 8 directions (+x, -x, +y, -y and the four diagonal directions) a triangle with
two vertices at random positions inside the target (at least 1/8 from the border) and the third at
(+-2^k, y) or (x, +-2^k) or (+-2^k, +-2^k) pixels, the other coordinate inside the target when not
far; fit 104 cases on 64 x 64, held-out 104 on 512 x 512. A power of two is an exact float32 clip
coordinate on these power-of-two half-sizes. The largest value is 2^21 pixels = 2^29 units of 1/256;
the tool takes coordinates below 2^30 units, so 2^22 pixels and more were not reachable in the 1/256
unit. The run took a few minutes, with no timeout, no fault line and no recovery.

**Results.** [HW] Against the exact rule (E606/E607): 194 of 208 cases 0 pixels wrong; 14 cases with
1 pixel (12) or 2 pixels (2) wrong, 16 in all, spread over k = 9 to 20 (the first at k = 9 on 512 x
512 and k = 10 on 64 x 64; none at k = 21) and in no preferred direction. Every one of the 16 pixels
has its centre within 3.5e-5 to 5.6e-4 pixel of an edge line of the exactly rounded triangle (edges
of 1008 to 262551 pixels), and none agrees with any alternative range limit. The model alone says
which limits the set could separate: a clamp of every coordinate to +-2^P pixels differs from the
exact coverage in 60, 46, 30, 21, 7, 4 and 1 of the cases for P = 14 to 20 (0 for 21, 22, 23), a
wrap into the signed P+1 bit range in 122, 106, 90, 74, 58, 42, 26 and 10 for P = 14 to 21 (0 for
22, 23); on every one of these cases the hardware's image is the exact one (within 2 pixels), not
the limited one. Triangles with a vertex at 2^21 pixels (areas up to about 2^42 pixels squared,
cross products up to 2^58 units) draw without a fault. Criteria P9 and P10 failed (P12 passed).

**What it shows.** [HW] The vertex range of the ISP is not limited by a clamp to 2^20 pixels or by a
wrap to 2^21 pixels: a vertex up to 2^21 pixels away gives the coverage of the exact triangle up to
a band of about 6e-4 pixel around its edges. That the band exists at k = 9 (a vertex 512 pixels
away, an edge of 1000 pixels) while E682 found exactness for edges of 2200 pixels that lie inside
the target says the inexactness is in how an edge to a far vertex is evaluated, not in the size of
the number alone. [infer] The edge arithmetic has an error of the order of 1e-4 pixel for an edge of
1000 to 1e5 pixels when one of its vertices lies outside the target by that much (a rounding of a
slope or an offset to a word narrower than the 59 bits of the exact product); the form is not shown
(Q261). For one far vertex on the 1/256 grid up to 2^21 pixels, on 64 x 64 and 512 x 512 targets,
the simulator may draw the exact rule and must mark the pixels within 1e-3 pixel of an edge line as
undetermined (the band is 1e-3 pixel for that case only: nothing is shown for a far vertex with a
sub-grid fraction, for two or three far vertices, or for a 4096 target); it must refuse a vertex at
2^22 pixels or more (not run: Q261), and keep the saturation of the integer format (2^23 pixels in a
24.8 word?) open.

**How far the band is supported.** [HW] Over the 208 images (post hoc, recompute/post_dist_1140.py,
not frozen; distances from the exactly rounded triangle's edge segments): pixels within 1e-4 pixel
of an edge segment 19, of which 8 wrong; within 1e-3 pixel 181, of which 16 wrong; between 5.6e-4
and 1e-2 pixel 1920, none wrong. So 1e-3 pixel holds as the band for what ran, with a margin of 1.8
over the largest distance of a wrong pixel and none wrong in 1920 pixels at 5.6e-4 to 1e-2; the
support at k = 19 to 21 is thin (at k = 21 6 pixels within 1e-3 and 75 within 1e-2, no mismatch).
The clamp and wrap statements hold as written: on the cases where a limit differs from the exact
coverage the image equals the exact one (a clamp to 2^20 or less: 1 case, at P = 20; a wrap into
2^21 or less: 10 cases); nothing is said for 2^22 pixels and more. The failed criteria are as
frozen; nothing was refitted.

Q199 is narrowed by this record, not closed: its own list of what would settle it (a 4096 target, a
vertex on a tie far away) is not answered.
