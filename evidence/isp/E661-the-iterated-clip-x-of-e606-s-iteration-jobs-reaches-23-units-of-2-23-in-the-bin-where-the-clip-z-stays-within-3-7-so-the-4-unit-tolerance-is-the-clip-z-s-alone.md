+++
id = "E661"
claim = "In the iteration jobs of E606 the clip x iterated at the pixel centre (pa1) is not within the 4 units of 2^-23 that the record gives for the clip z: over the 700 triangles of the fit and held-out sets, in the bin whose value range per root area is below 0.05 (358 triangles, 257 of them with a covered pixel, 126104 pixels) 17 triangles all of the small class (8 of the fit set, 9 of the held-out) have 19 pixels beyond 4 units, the largest 23.0 units (the record's own table of the bin gives max 23.0), against 0 of 132050 pixels in the 116 triangles of the same bin for the clip z (max 3.7); the plane through the vertices' clip x values stays the right plane (coverage 0 wrong in 700 images), 99.69 percent of the bin's pixels (125718 of 126104) are within 1 unit, against 99.49 percent for the clip z (131381 of 132050)"
unit = "isp"
method = "offline, no new run: sgx-pipe examples/arith_stats.rs and tests/isp_arith.rs on the I0 and I1 images of the dataset isp-arith-1138 (700 triangles, the vertices of cases.tsv, pa0 = 2 z - 1 and pa1 = x over half the width minus 1, both exact in float32 on these targets, the plane exact in f64, units of 2^-23 absolute), the conditioning measure of the dataset's analysis (value range over the square root of the triangle's area in pixels squared, the root at least 1e-3); the record's table of the pa1 bins was read after the check, as was its sentence"
tiers = ["HW"]
date = "2026-11-09"
data = ["isp-arith-1138"]
terms = []
+++

**Results.** [HW] E606's text says that the clip x follows "the same conditioning law" as the clip z
(0.5 percent above 1 unit and a maximum of 3.7 for a range per root area of 0 to 0.05) and gives 4
units as the tolerance of the iterated clip z. Its table for the clip x (the dataset's
analysis-main/extra2-errors.txt, the line "0.00..0.05") has, in that bin, 257 triangles and 126104
pixels, 0.34 percent above 1 ulp (true ulps of the value, not units of 2^-23) and a maximum of 23.0.
The 257 are the triangles of the bin with at least one covered pixel; the bin holds 358 triangles of
non-zero area, the other 101 cover no pixel center. Recomputed from the images, in units of 2^-23:
the 19 pixels beyond 4 units are in 17 triangles of the class small (a box of 1 to 4 pixels, 64 and
128 pixel targets), 2, 1, 1, 1, 1, 1, 2 and 1 pixels in the fit set's eight and one pixel in each of
the held-out set's nine, with errors of 4.5 to 23.0 units. The same bin for the clip z has no pixel
beyond 4 units (132050 pixels of 116 triangles, maximum 3.7). The fraction within 1 unit is about
the same for the two (99.69 percent of 126104 pixels for the clip x, 99.49 percent of 132050 for the
clip z), so the two attributes share the plane and differ in the tail.

**What it shows.** A tolerance of 4 units holds for the clip z in the range per root area below 0.05
and is not shown for the clip x; a simulator that reports an iterated value `near` must say which
attribute the bound is for. The pipeline simulator's iterator refuses any attribute but the clip z
(Q200). The tail of the clip x is on small triangles, where the value range is a few pixels' worth
of x; what makes the clip x worse than the clip z there (the magnitude of the values, the range of
the inputs) was not examined, and no arithmetic is claimed (E606).

**What it does not show.** Another attribute, another coordinate set or source (Q098, Q180), the
four-component forms (Q021), the iteration under perspective.
