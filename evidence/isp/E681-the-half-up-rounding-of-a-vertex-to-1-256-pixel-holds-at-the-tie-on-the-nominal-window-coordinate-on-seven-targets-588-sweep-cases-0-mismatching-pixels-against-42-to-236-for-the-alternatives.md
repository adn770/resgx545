+++
id = "E681"
claim = "With an edge moved across the half-grid tie in steps of 1/4096 pixel (1/1024 pixel from 2048 wide) at a positive coordinate, on 7 targets (96 x 64, 200 x 120, 512 x 256, 640 x 480, 1024 x 768, 2048 x 1024, 4096 x 4096), the ISP's image equals E607's rule (vertex rounded half up to 1/256 pixel, then the exact centre test) in all 588 cases, taking the nominal window coordinate of the vertex: 0 mismatching pixels, every flip of every sweep at the step the rule gives; round half down would mispredict 42 of the cases, flooring 204, no rounding 236"
unit = "isp"
method = "on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed and loaded), stock firmware, own_arm off, tool ~/sgxfive-test-1140 (the 11.38 tool plus tri --pixels-rle, a row a line as runs of equal pixels, and the clip words of the three vertices printed as the job carries them, written test first: test_vertex_words in userspace/libsgxfive/tests/test_render.c and three tests in test_cli.py; sources and binary sha256 in the dataset's env.toml), run/run_p1140.py, one process per job, a marker per job in the kernel log, every raw output gzipped, colour image only (no depth, no iteration); sets, hypotheses, alternatives and criteria frozen by hash (predictions-1140.toml, manifest-1140.sha256) after a pilot of 6 cases outside every set and before the first main job; recompute/recompute_p1140.py (numpy, scratch, shares no code with the run script) on the dumps After the freeze recompute/recompute_p1140.py was changed to read several run directories in one pass (no model or criterion changed): its sha256 no longer matches manifest-1140.sha256 while the other 11 frozen files and predictions-1140.sha256 do (freeze1140.sh verify fails on that one file only). Post hoc and not frozen: recompute/post_neg_1140.py, post_neg2_1140.py, post_tie_1140.py, post_thresh_1140.py, post_dist_1140.py and post_far_power_1140.py (outputs: the post-*-output.txt files of the dataset). manifest-1140.sha256 names the five tool files by tool/userspace/libsgxfive/ paths that the dataset does not have: tool-sources holds three of them (same sha256) under other names, test_render.c and test_cli.py are not in the dataset."
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["isp-coverage-envelope-1140"]
terms = []
+++
**What ran.** 588 jobs of group S2: on each target four sweeps (a vertical edge owning ties, one not
owning them, a horizontal one of each kind) of an edge through the centre of a pixel (xc + 1/2, yc +
1/2) moved by t units, t from -12 to +12 of 1/4096 pixel (25 cases per sweep) on 512 x 256, 96 x 64,
640 x 480 (fit, 300 cases), 1024 x 768 and 200 x 120 (held-out, 200 cases), and t from -5 to +5 of
1/1024 pixel (11 cases per sweep) on 2048 x 1024 and 4096 x 4096 (held-out, 88 cases): the rounding
grid 1/256 is 16 (4) of these units, the tie 8 (2). The edge is 2L long with L = min(20, width / 8,
height / 8) pixels, the third vertex 2L beyond it. The sweeps sit at one pixel per target, so the
coordinates swept are small: the largest positive coordinate at 1/4096 steps is 447.5 pixels (1024 x
768), 257.5 (512 x 256), 235.5 (640 x 480), 117.5 (200 x 120) and 59.5 (96 x 64); at 1/1024 steps
1055.5 pixels in x (2048 wide) and 1366.5 in x and 1985.5 in y (4096 x 4096).

**Results.** [HW] Against E607's rule: 0 mismatching pixels in fit (300 cases) and held-out (288
cases). The observed flips (the first step at which the covered pixel set differs from the previous
step) are the same on every target and the same as the model's: at 1/4096 the vertical sweeps change
once, at t = +8, the horizontal ones twice, at t = -8 and t = +8; at 1/1024 on 2048 and 4096 wide at
t = +2 (vertical) and t = -2 and +2 (horizontal). The alternatives (computed from the model alone on
the same cases): half down mispredicts 6 cases per target (42), flooring 36 per 1/4096 target and 12
per 1/1024 target (204), no rounding 44 and 8 (236: 5 x 44 + 2 x 8). Criteria P3, P4 and P4b passed.

**What it shows.** [HW] The rounding half up to 1/256 pixel that E607 found at 64 x 64 to 256 x 256
targets at coordinates below 256 pixels holds at the half-grid tie, on the nominal window
coordinate, up to 447.5 pixels at 1/4096 steps and up to 1055.5 (x) and 1985.5 (y) at 1/1024 steps;
1/4096 steps beyond 450 pixels and x beyond 1370 pixels at 4096 wide were not run. It holds on
targets of power-of-two and other half-sizes: 96 x 64 (48 x 32), 200 x 120 (100 x 60), 640 x 480
(320 x 240), 1024 x 768. [infer] On a target whose half-size is not a power of two the float32 clip
words printed by the tool are not the nominal tie: counting the sweep positions that are nominal
ties, the float32-derived position lies 4 below, 14 on and 6 above on 96 wide, 15 below and 9 above
(none on) on 200 wide, 4, 10 and 10 on 640 wide, 5, 14 and 5 on 1024 wide. Rounding that float32
position half up mispredicts 30 (96), 79 (640), 132 (200) and 39 (1024 x 768) pixels in the sweeps;
the nominal coordinate, or float32 c * half + half rounded half up, gives 0 everywhere, and float32
(c + 1) * half gives 15 on 200 wide and 39 on 1024 x 768. So the sweeps at those sizes confirm the
rule only on the nominal coordinate, and the hardware's window conversion, which is not exact in the
clip words, matches float32 c * half + half. As a condition for the simulator: it takes the nominal
window coordinate of the vertex. At 512, 2048 and 4096 wide (power-of-two half-size) the clip words
are exact and these are the clean ties. The ISP's own conversion is not shown to be limited to 8
fractional bits before rounding at positive coordinates in this range. The simulator may round a
window coordinate half up to 1/256 for positive coordinates on these targets, given the nominal
coordinate. Negative coordinates are not covered (E683).
