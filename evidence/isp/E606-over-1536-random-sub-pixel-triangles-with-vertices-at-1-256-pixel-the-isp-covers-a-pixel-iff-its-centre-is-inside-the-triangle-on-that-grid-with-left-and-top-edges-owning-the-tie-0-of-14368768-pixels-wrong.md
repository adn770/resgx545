+++
id = "E606"
claim = "Over 1536 triangles with random sub-pixel vertices (integers in 1/256 pixel, within about -9% to +124% of the target) on 64 x 64, 128 x 128 and 256 x 128 targets (3112 jobs, none flagged), the ISP covers pixel (x, y) iff the sample at its centre (x + 0.5, y + 0.5) is inside the triangle whose vertices lie on the 1/256 pixel grid (the grid the ISP rounds every vertex to, E607; rounding to a coarser grid, 1/128 pixel, already mispredicts 61 pixels), the edge test exact, and a sample exactly on an edge belongs to the triangle iff the edge is a left or a top edge: 0 of 14368768 pixels of all main images mispredicted (0 of 413856 pixels of the bounding boxes of the 692 fit triangles, where the one cell of 15360 (snap x sample point in sixteenths of a pixel x ten tie rules) was chosen, and the same cell 0 of 1064683 on the 814 held-out triangles of 128 x 128, 256 x 128 and a second seed batch at 64 x 64), 814 of 814 exact, edges through pixel centres, shared edges (110 pairs: no pixel drawn twice, none lost inside a triangle, 87 centres exactly on the shared edge each drawn once), zero-area and 1/256-wide slivers (0 pixels), 1/16-pixel needles and triangles with vertices off screen included; the coverage is the same under three pixel programs and with the depth store (1576 of 1576 images), and repeats byte-identical (30 of 30). The depth stored through the E465 layout and the iterated clip z and x (coordinate set 0, source 1, two components, the program of E437) equal the plane through the vertices evaluated at the pixel centre up to an absolute error: for depth 99.3% of 409950 covered pixels within 1 unit (the unit is 2^-23 absolute, not a float32 ulp of the stored value), at most 1.9 units where the plane's gradient |dz/dx| + |dz/dy| is below 0.03 (330075 pixels, 3 units as the tolerance), up to 145 units for gradients above 3; for the iterated clip z 3.7 units at most for triangles with a value range per root area below 0.05 (4 units as the tolerance). The stored depth is below the exact plane for 78.7% of the pixels, by 0.39 of 2^-24 on average, and no bit-exact model was found. The position iterated by source 0 (E502: x + 0.375, y + 0.125) is not the point at which these attributes are evaluated. The frozen primary prediction (snap to 1/16 pixel, R1 ties, iteration at x + 0.375) failed; the landed CPU reference (one-pixel band) cannot fail by construction"
unit = "isp"
method = "on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed and loaded), stock firmware, own_arm off, tool ~/sgxfive-test-1138 (a userspace build on the laptop from the 11.35 sgxfive-test.c plus --tri-v X0,Y0,X1,Y1,X2,Y2 (integers in 1/256 pixel, exact clip coordinates on a target of power-of-two half-size) for tri and probe --tri and --tri-z for probe --tri, written test first: test_fine_vertices in userspace/libsgxfive/tests/test_render.c and the new cli tests of userspace/libsgxfive/tests/test_cli.py and test_cli_tri_probe.py, landed with the --tri-unit tool of E607; binary sha256 e915fa768d44296b125bd2090a92452d084a864c5a7944ba47bb83e2f8eb0579, sgxfive-test.c sha256 fcb1aea98b621f4e04137e2e2b818f118f239b4179a09c5e7f05c87d078c01e6, render.c 9c1c3a9a2d1e31c579a08b18901cce1f83218b08a938cfc0876602680b03abc8, sources in the dataset's tool-sources), run/run_p1138.py of the dataset (one process per job, a /dev/kmsg marker per job, every output gzipped, debugfs reset after a flagged job: none was needed; the D jobs' --depth makes the tool write the render words ta:7, rd:1, rd:11, rd:12, rd:13 through the kernel's debugfs kpoke before each render, as E465's recipe does, and no hardware register is written from userspace; the fixed campaign runner of 11.35 was not used, see the dataset's plan.md section 1, whose sections 1 and 5 still say that no register is written and no kpoke is used: this method is the correction, the kpokes are the 5 kernel log lines of each D job in kernel.log.gz, no kreg, no /dev/mem write and no clock-gate register anywhere in the material); job kinds D (tri --depth --depth-ctl with the pitch G = tiles across - 1 --depth-fill 0xdeadbeef --depth-dump, --pixels: the colour image and the depth buffer decoded by E465's rule), I (probe --tri pixpds:12 with E437's primary program, source 1 two components 0x20400800, U1 0x01000004, and the dataset's templates/vtx_attr_zx.s: o4 = the vertex's clip z, o5 = its clip x; pa0 and pa1 as the colour) and C (the plain green probe); cases.tsv (1536 cases, seed 1138, sha256 0a73ca8f4a2dadb6929e14db4d830d13a49116054f084295abfc1f2f90a2102d), predictions-1138.toml (sha256 11ecc93e542e2be23af717601214e78e69bd529e1043423b2d2d24e23a382af0) and the manifest of 33 files frozen before the first job after a 3-case pilot (outside every set) that found a pitch bug in the depth recipe; the fit set (692 cases) ran first, the held-out set (814) and the repeats (30) after; recompute/recompute_p1138.py of the dataset reads only cases.tsv and the dumps; post-freeze post-hoc checks (the dataset's extra_p1138.py to extra6_p1138.py, and probes/p1138/depth_error_1138.py, standard library only, whose output is probes/p1138/depth-error-1138.txt) are marked as such below"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["isp-arith-1138"]
terms = []
+++
**What ran.** 3112 jobs: 1536 depth jobs (D), 1400 iteration probes (I0, I1: 700 triangles) and 176
plain probes (C). Classes of triangle (vertices in 1/256 pixel, y down, depths multiples of 1/1024):
edge sweeps (a vertical, horizontal or 45 degree edge moved in 1/256 steps across a pixel centre,
the third vertex on either side, 262 at 64 x 64 and 134 at 128 x 128), small (inside a 1 to 4 pixel
box), medium (8 to 40), large (vertices over the target, 30% from -9% to +124% of it, off screen),
centre (vertices at pixel centres: edges through centres), shared-edge pairs (a quad cut along a
diagonal, half with centre corners), collinear, slivers (the middle vertex 1 or 2 units off the
line), needles (about 1/16 pixel wide, 20 to 40 long) and 30 reruns. The vertices run from -8.9% to
+124.1% of the target; 27 of the 1536 cases (19 large, 8 needles) have a vertex outside it, and 9
cases have a negative coordinate, all on the grid. Sets, declared before any run: fit = the 692
cases of 64 x 64 batch 1; held-out = 494 at 128 x 128, 70 at 256 x 128 and 250 at 64 x 64 (new
seeds); repeat = 30.

**Results.** [HW] *Coverage.* The hypothesis grid (six snaps: none, round to 1/32, 1/16, 1/8, 1/4,
floor to 1/16; 256 sample points, every sixteenth of a pixel; ten tie rules: eight top-left /
left-right ownerships of the winding-normalised edge, every edge, no edge) was fitted on the fit set
only: exactly one of 15360 cells has 0 mismatching pixels of 413856 (pixels of the bounding boxes
grown by 2): (no rounding coarser than the 1/256 of the vertices, centre (8, 8)/16, rule R4: an edge
of the winding-normalised triangle owns a sample on it iff dy < 0, or dy = 0 and dx > 0, which for a
triangle (0,0), (10,0), (0,10) in y-down coordinates owns the top and the left edge and not the
hypotenuse). The next distinct counts are 78 (round to 1/32), 244 (R2), 256 (round to 1/16 with R4),
346, 476. On the 814 held-out triangles the same cell mispredicts 0 of 1064683 pixels (every class
and size 0), and over the whole images of all 1536 jobs 0 of 14368768; a float32 evaluation of the
edge functions gives the same pixels (0 differ): the edge-function precision is not separated here,
E607 does that. The predictions of the prepared alternatives fail: (r16, centre, R1) mispredicts
1202 of 413856 on fit and 1737 of 1064683 on held-out (350 of 814 triangles inexact); the sample at
(0.375, 0.125) 9292 on fit; snapped grids finer than the first (post hoc, extra5: rounding to 1/128
pixel 61, flooring to it 79, rounding to 1/64 116, flooring to it 210, rounding to 1/32 238
mismatching pixels over fit and held-out). The sample point and the snap are determined only to the
resolution of the grid searched (a sixteenth of a pixel for the sample point; the vertices' own
1/256 for the snap): the nearest alternative on the sample point is not seen below 1/16 pixel.
*Sweeps (post hoc, model-free).* In every sweep the first or last covered pixel of a middle row
changes where the edge crosses the sample point (the tie at f = 128, a step of 4 or 8 in 1/256
pixel): a left or top edge (V+, H+, D+) still covers the pixel at the tie and loses it one step
later, a right or bottom edge (V-, H-, D-) gains it one step after the tie (flips after 128 and at
136 at 64 x 64, 136 and 144 at 128 x 128 where the first sample is 8 off). *Shared edges (post hoc,
extra6, all 110 pairs).* 0 pixels strictly inside either triangle undrawn, 0 drawn twice, 87 centres
exactly on the shared edge each drawn by exactly one triangle, none by none or both; the centres at
the two ends of the shared edge (the pixel centre exactly at a vertex) are drawn by neither (76) or
by one (34), as a rule that needs both incident edges to own the point gives. The frozen pair
criterion counted 5 uncovered centres near the diagonal in 60 pairs, all outside both triangles (the
wedge at the diagonal's ends), and the generator reused pair names in each size group, so the frozen
recompute read only 60 of the 110 pairs. *Degenerate.* 31 collinear triangles and the 30 slivers
draw 0 pixels; 14 of the 29 needles draw pixels (18 in all), as the model says (0 mismatch).
*Independence and repeats.* The plain green probe equals the depth job's coverage in 176 of 176
cases and the two iteration probes in 1400 of 1400 images; the colour image and the depth buffer of
the 30 repeat jobs are byte-identical to the first runs (30 of 30); the depth buffer is below 1.0
exactly where the colour image says covered (0 of 14368768 pixels differ). *Depth.* The stored value
of the covered pixels against the plane through the vertices' screen depths at the centre (the
vertices as given, which are on the grid; the best of 5 snaps x 256 points on fit; a snap to 1/16
pixel fits 47% within 1 unit, no coarser snap 99.3%). The figures that follow are computed by
probes/p1138/depth_error_1138.py over the 409950 covered pixels of the fit and held-out depth jobs
(output: probes/p1138/depth-error-1138.txt). The unit is U = 2^-23 absolute, which is the spacing of
float32 in [1, 2) and 2 true ulps for a stored value in [0.5, 1): the error is absolute, so in true
float32 ulps of the stored value it reads larger for small values. Within 1 U 99.26%, within 3 U
99.94%, maximum 145.2 U; in true ulps 76.4% within 1 ulp, maximum 290.5 ulp. The true-ulp table by
stored value (within 1 U; within 1 true ulp; maximum true ulps; mean signed error in 2^-24): below
0.125 99.8%, 78.0%, 61, -0.05; 0.125 to 0.25 99.8%, 69.2%, 248, -0.13; 0.25 to 0.5 99.6%, 72.4%,
260, -0.27; 0.5 to 0.75 99.1%, 80.9%, 290, -0.53; 0.75 to 1 98.0%, 76.5%, 47, -0.51. The error
follows the plane's gradient (per triangle, the maximum over its pixels): below 0.03 (529 triangles,
330075 pixels) 99.75% within 1 U, maximum 1.9 U; 0.03 to 0.1 (405, 74975) 98.3%, 4.4; 0.1 to 0.3
(114, 4308) 86.2%, 6.3; 0.3 to 1 (102, 485) 48.3%, 11.2; 1 to 3 (33, 84) 15.5%, 49.9; above 3 (16,
23) 8.7%, 145.2: the 145 and the 366 of the iteration are single needles and small triangles (10 and
96 pixels). By value range per root area (extra2, the dataset's analysis-main): 0 to 0.05, 390480
pixels, 0.4% above 1 U, maximum 2.8; 0.05 to 0.2, 19096 pixels, 6%, 49.9; 0.2 to 1, 354, 51%, 145; 1
to 5, 20 pixels. The stored value is below the exact plane for 78.7% of the pixels, above it for
17.7%, equal for 3.6% (81.6% below among the non-zero), mean signed error -0.39 of 2^-24. The 18
float32 variants of the plane arithmetic of extra3 (origin at each vertex, divide or reciprocal,
relative or absolute form, round to nearest) reproduce at most 41.2% of the stored dwords bit for
bit, against 42.7% for the exact plane rounded to nearest and 58.8% for the exact plane truncated
toward zero (probes/p1138/depth_error_1138.py, all 409950 pixels; 61.0% on the pixels of gradient
below 0.03): no arithmetic of the family is the hardware's. *Iteration.* pa0 (clip z, 700 triangles)
and pa1 (clip x) at the pixel centre through the vertices: 95.7% (fit, 24068 pixels) and 98.2%
(held-out, 127072) of pa0, 98.3% and 99.6% of pa1 within 1 U, the same conditioning law (value range
per root area 0 to 0.05: 0.5% above 1 U, maximum 3.7; 0.2 to 1: 59%, maximum 34; 5 and above: 366 U
for one pixel). The sample point of pa0 is the centre (the other 255 points of the 1/16 grid fit
worse, the point (0.375, 0.125) by far); pa1 depends on x only and its best sample x is the centre,
128/256 (the y of its best point is an arbitrary tie).

**Against the predictions (predictions-1138.toml).** P1 failed: the cell (r16, centre, R1)
mispredicts 1202 of 413856 (0.29%) against 0.05% allowed, the grid's best 0. P2 ("vertices are
snapped": the cell (none, centre, R1) misses at least 50 fit pixels) held on its letter (826 pixels)
and not on its premise: the 826 pixels are the tie difference between R1 and R4 (the unsnapped cell
with R4 misses 0), and snapping at 1/16 is refuted; that the vertices are rounded to 1/256 is E607's
finding and cannot be seen in this set (its vertices are on the grid). P3 and P3b failed (1737 of
1064683, 350 of 814). P5 failed as written (5 near-diagonal uncovered centres) and the corrected
measurement says the partition holds. P6 and P6b failed on the maximum (145 and 50 units against 4)
though 99.3% were within 1. P7 failed (the best sample point of pa0 is the centre, not (0.375,
0.125)), as did P7b. P7c (written after the pilot) failed on the fraction (95.7% against 99%) with
the right cell; P7d held (depth at the centre, unsnapped, 99.3%), but P7c and P7d were informed by
the pilot and are not independent predictions. P8 held (30 of 30), P9 held (176 of 176, 1400 of
1400), P10 held (0 pixels from 31 triangles), P11 held (3112 of 3112).

**What it shows.** [HW] For a triangle with 1/256-pixel vertices on a target up to 256 x 128 the
coverage of every pixel is the exact centre-sample test with the top-left tie rule; for such input a
simulator needs no snapping, no per-primitive fill rule beyond it and no tolerance for coverage (0
of 14368768 pixels). The simulator may use this coverage rule only inside the envelope that was
tested: window coordinates in 1/256 pixel (E607 for the float conversion), vertices from about -9%
to +124% of a target of power-of-two half-size up to 256 x 128, w = 1, a single sample, triangles, x
>= 0; the behaviour at negative coordinates with a sub-grid fraction is open (Q199). [HW] The depth
plane is the exact plane through the grid vertices at the pixel centre up to an absolute error: as a
tolerance against hardware vectors, 3 U for depth where the gradient is below 0.03 and 4 U for the
iterated clip z where the value range per root area is below 0.05, in absolute units of 2^-23 and
not in float32 ulps of the value; planes above those limits are outside (the error reaches 145 U).
It is not bit-reproducible by any variant tried and the stored value is systematically low, so the
simulator uses the tolerance only to compare with hardware results, never as its own arithmetic, and
does not claim bit equality of depth or iteration. [infer] The bias, -0.39 of 2^-24 in a mean that
is about -0.5 true ulp in every binade, looks like a truncation of a value that carries an absolute
error of about 2^-24; the form is not shown. [HW] The attribute iterator, for the one iteration
setup used (coordinate set 0, source 1, two components, E437's program), evaluates at the pixel
centre, not at (x + 0.375, y + 0.125): the iterated position source of E437 and E502 is another
matter.

**What it does not show.** Anything finer than 1/256 pixel in this set (E607); targets other than
power-of-two half-sizes (96 wide was not used) and above 256 x 128; multisampling; line and point
primitives; w other than 1 (no perspective); the bit-exact depth arithmetic; the depth with the
compare, the polygon offset or the format bits other than E465's; vertices beyond -9% to +124% of
the target (Q199, Q202); negative coordinates with a sub-grid fraction; any iteration source other
than the one used; a hardware that runs the pixel program differently for other state words.
