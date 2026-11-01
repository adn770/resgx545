+++
id = "E726"
claim = "Exploratory (no rule was declared; the plan's prediction was only that faces 1, 3 and 5 appear for the negative axes, which they do): with TEXTYPE 2 the 6 axis directions read one face each over 2048 of 2048 pixels, faces 0 to 5 for +x, -x, +y, -y, +z, -z in blocks of 256 dwords (the mapping and the dominant-axis rule are post hoc [infer]), and a w sweep moves the read from +x to +z"
unit = "texture"
method = "on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed and loaded), firmware /lib/firmware/sgx545_ukernel.fw sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a, tool ~/sgxfive-test-1138b sha256 ba6baa62fe33a5aa510c05ea1aa9a04c25798c60c4954655882682f05a5b8291, the 13 scripts of p1141/tex run in one pass by run-all-1141tex.sh on 2026-11-09 (14:25 to 14:31; 140 jobs, one process per job, a marker per job in the kernel log, every raw output gzipped and kept); declared.tsv, predictions-declared.tsv (380 rows) and manifest-1141tex.sha256 written before the first job (file times 14:16 to 14:20, first job 14:25:01) and verified here by sha256 (5dae7939..., f4187d25..., 144da32e...; 27 of 28 manifest lines by sha256sum -c, the 28th, the 74 staged programs, by the sha256 of sha256sum stage-bins/*.bin); recompute/recompute_p1141tex.py (numpy, scratch, shares no code with the run scripts) run on the dumps, its output in recompute-output.txt. Post hoc and not frozen: post/post_1141tex.py with post-output.txt"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["texture-isp-msaa-verification-1141"]
terms = ["TEXTYPE"]
+++
**What ran.** tex-h-cube: 8 jobs, rc 0 and 2048 pixels each, declared exploration, no model: cu-
xp, cu-xn, cu-yp, cu-yn, cu-zp, cu-zn (smp3d on TEXTYPE 2, a 16 x 16 twiddled chain, the axis
operand constant +1 or -1 and the other two linear ramps 1.5 (1 + p / 64) - 2.25, from -0.75 to
+0.73 (x) and +0.70 (y), so the constant axis is the largest in magnitude at every pixel) and
cu-w02 and cu-w11 (u a mapped ramp, v 0.53125, w a ramp from 0 to 1.94 and from -1 to 0.94). The
plan's only prediction was an outcome: faces 1, 3 and 5 appear for negative axes (a cube) or none
(a three-face layout).

**Results.** [HW] The tag of every pixel gives the face as (index div 256): cu-xp 0, cu-xn 1, cu-
yp 2, cu-yn 3, cu-zp 4, cu-zn 5, each on all 2048 pixels, the face-local index from 12 to 252 (144
to 169 distinct values a job). The criterion of the plan is met: faces 1, 3 and 5 appear for the
three negative axes. cu-w02 reads face 0 on 1568 pixels and face 4 on 480; cu-w11 face 0 on all
2048.

**Population.** No rule was frozen; nothing is scored beyond the outcome (faces 1, 3, 5 for the
negative axes). The +x, +y, +z to 0, 2, 4 mapping and the dominant-axis rule are post hoc. A
reviewer's check on cu-w02: the dominant axis |w| > |u| gives face 4 on exactly the 480 pixels and
face 0 elsewhere (2048 of 2048, no ties), so the inference holds on that job. The six directions are
the whole data for the face order; the (s, t) mapping inside a face was not decoded.

**What it shows.** [HW] TEXTYPE 2 with smp3d selects a face by the three coordinates; the six
faces are six 256-dword blocks of the index space in the order +x, -x, +y, -y, +z, -z (a cube, not
three faces). [infer] The face follows the coordinate of largest magnitude and its sign (the six
directions, and the +x to +z change in cu-w02 as w grows), but the boundary |w| = |u| was not
tested.

**What it does not show.** The face's (s, t) orientation, the edge filtering and the sizes other
than 16 x 16 (Q284); Q113's TEXTYPE value (2) is settled by this and E567 together.
