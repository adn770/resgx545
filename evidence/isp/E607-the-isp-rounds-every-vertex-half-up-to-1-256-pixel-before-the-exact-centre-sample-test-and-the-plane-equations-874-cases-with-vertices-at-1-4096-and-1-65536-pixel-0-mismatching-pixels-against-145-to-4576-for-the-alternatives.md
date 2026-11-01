+++
id = "E607"
claim = "The ISP rounds every window-coordinate vertex at x >= 0 to the nearest 1/256 pixel, ties up, before it tests the pixel centres and builds the planes: on 874 cases with vertices at 1/4096 and 1/65536 pixel (edge sweeps in single steps across the tie on 64 x 64 targets and at 1/65536 on 256 x 128, 100 small, 60 medium and 60 near-centre random triangles) the rule (round half up to 1/256, then the exact centre-sample test with the left/top tie rule of E606) mispredicts 0 pixels, against 145 for half-down, 1156 for floor, 4572 for ceil, 577 for rounding to 1/512, 1157 to 1/128 and 4576 for no rounding; an edge moved in steps of 1/4096 pixel across a pixel centre changes the covered pixel 8 steps after the tie (a left or top edge loses the centre then, a right or bottom edge gains it), the depth stored through the rounded vertices is within 1 unit (2^-23 absolute) for 98.8 to 100% of the covered pixels of the sweeps (maximum 1.7 units), and a held-out confirmation, 422 further cases with 0 mismatching pixels in 342 of them, every sweep flip equal, and 80 edges passing a pixel centre at a cross product of plus or minus 1 unit of 1/65536 pixel squared all decided as the exact integer test does: the 40 at +1 are all drawn (the hardware does not drop a centre that is 1 unit inside an edge; one-sided: the 40 at -1 are not drawn, but another edge excludes their centre by 4.5e7 to 2.1e8 units squared, so they test nothing). The depth of 75 cases with exactly one coordinate on an exact tie (even and odd integer parts, x and y) fits the plane through the half-up rounded vertices (59 of 75 within 1 unit at the median, none within 1 unit rounded down) and 3 cases at 127/256 of a grid unit round down: the threshold is in (127/256, 1/2] of a grid unit. The frozen predictions PF1 (flips at the tie), PF2 (the exact model misses at most 0.05% and a 1/256 snap more than 50 pixels) and PF3 failed: the vertex grid exists and is 1/256"
unit = "isp"
method = "on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed and loaded), stock firmware, tool ~/sgxfive-test-1138b (the E606 tool plus --tri-unit K: vertices of --tri-v in 1/2^K pixel, K 5 to 20, exact clip coordinates while half the target width times 2^K stays below 2^24; tests first: test_fine_unit in userspace/libsgxfive/tests/test_render.c and the new cli tests of userspace/libsgxfive/tests/test_cli.py and test_cli_tri_probe.py; binary sha256 ba6baa62fe33a5aa510c05ea1aa9a04c25798c60c4954655882682f05a5b8291, sgxfive-test.c sha256 c6036a26592760062286af3c0c07354dae530783e2e1d45aa751bdf0ae5c9558, render.c d53ee1a4df1085c544227af9b25dcd9b45eac2d8b63429ff6daeae40ad895bc0; these sources are the landed userspace/libsgxfive/tools/sgxfive-test.c and src/render.c), run/run_p1138b.py of the dataset (run_p1138.py with the unit), D jobs only (tri --depth ... as E606, with the same kernel kpokes of render words), cases-fine.tsv (874 cases, seed 11380, sha256 6c895cd8186e13e115553620223b411e8f88ee04b80564dbe50912001a57c30e) frozen with predictions-fine-1138.toml (sha256 95cef526e604f8f80392c8da360fa447caa19d058d19111263da8b438d50726e) after the main fit set was read and before any fine job; recompute/fine_p1138.py (frozen) and the post hoc recompute/fine_extra_p1138.py of the dataset, and probes/p1138/tie_depth_1138.py (standard library only; output probes/p1138/tie-depth-1138.txt) for the depth of the tie cases; no job was flagged, no reset was needed"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["isp-arith-1138"]
terms = []
+++

**What ran.** E606's main fit said that "no snapping" down to 1/256 pixel is the unique
zero-mismatch cell, but its vertices were all multiples of 1/256: it could not tell a vertex grid of
1/256 from no grid. This follow-up (declared after the main fit set was read, with predictions
frozen) puts vertices between the grid points. FA: 6 edge kinds (vertical, horizontal, 45 degree,
the third vertex on either side) x 65 steps of one unit (1/4096 pixel) across the tie on 64 x 64;
FB: 100 small, 60 medium and 60 near-centre random triangles at 1/4096 (the near-centre ones have
half-integer vertices jittered by 0 to 3 units); FC: 33 steps of 1/65536 pixel across the tie on
256 x 128, near the origin and far from it (x about 215, y about 100). 874 D jobs, none flagged.
No vertex of the fine or fine2 sets is negative (the smallest is 0.49 pixel).

**Results.** [HW] *The sweeps.* With the edge at the tie plus g units of 1/4096 pixel the first
covered pixel of a middle row flips between g = 7 and g = 8 in all six FA kinds (each: the exact
model, no rounding, flips between 0 and 1): the 1/256 grid with round half up (128 + g/16 reaches
128.5 at g = 8) is the one that does it; round half down would flip at 9, floor at 16, a grid of
1/512 at 4. The FC sweeps (steps of 1/65536 over +-16, that is 1/4096 pixel in all) do not change
at all, as the rounding says (the exact model flips in the middle); PF3 cannot be judged by them,
and at x near 215 a float32 window coordinate has a resolution of 2^-16 pixel, the resolution of
the input itself. *Coverage of every case.* Exact test on the vertices rounded half-up to 1/256:
0 mismatching pixels in 874 of 874 cases (every class); half-down 145 (6 sweeps and 1 medium),
floor 1156 (48 sweeps, 4 medium), ceil 4572, round to 1/512 577, to 1/128 1157, to 1/1024 1069, no
rounding 4576 (170 sweeps, 52 near-centre triangles, 1 small). *Depth* through the rounded
vertices at the centre: within 1 unit (2^-23 absolute) 98.8% (centre class, maximum 4.04 units),
99.4 to 100% (sweeps, maximum 1.3 to 1.6), 92% on the 60 medium triangles (maximum 7.3), and 38% on
the 63 pixels of the 100 small ones; the vertices as given (not rounded) fit 3 to 15% within 1
unit. *The tie and the threshold (post hoc, probes/p1138/tie-depth-1138.txt).* The fine and fine2
cases with exactly one coordinate on an exact tie (the fraction of 256 x exactly 1/2) are 75:
x and y, the integer part even (53) and odd (22). Their covered pixels' median error against the
plane through the half-up rounded vertices is at most 1 unit in 59 cases and at most 5.1 in all;
through half-down rounded vertices it is at least 3.3 in every case and reaches 12382. Half up
therefore holds in both parities and both axes, which excludes round-half-even, and it is a second
line of evidence beside the flips (which rest on 7 sweep kinds at one parity). Three near-centre
cases with a coordinate at 127/256 of a grid unit (at 1/65536 pixel) round down (median error 0.10
to 0.34 units, against 3.6 to 54.7 if rounded up). So the threshold of the rounding lies in
(127/256, 1/2] of a grid unit: nearest, with ties up, to 1/65536 pixel; the sweeps alone give
1/16 of a unit.

**Against the predictions (predictions-fine-1138.toml).** PF1 failed (484 of 654 sweep cases equal
the no-rounding model's; every one of the 874 equals the rounding model's), PF2 failed (the exact
model missed 239 near-centre pixels, the 1/256 snap 0 on the same triangles; 1 pixel each in 100
small), PF3 failed (68 of 132, uninformative as above). The direction of the prediction was wrong:
the ISP does round.

**What it shows.** [HW] The ISP's vertex grid is 1/256 pixel and a window coordinate x >= 0 is
rounded to the nearest unit, ties up; the coverage test and (depth) plane use the rounded vertices.
[infer] That is a 24.8-style fixed-point conversion of the float window coordinate after the
viewport; the 1/256 value is [HW] (8 fractional bits), the form of the rounding is [infer]. A
simulator converts a window coordinate x >= 0 to integer units of 1/256 pixel by floor(256 x +
0.5), for which the evidence is x >= 0 only (at a negative tie this equals round half up and
differs from round half away from zero and from a truncating conversion after an addition, which
were not tested), and then everything of E606 is exact integer arithmetic.

The comment of the frozen predictions-fine2 file cites the sweep-only counts (144, 1152); the
totals are the ones above.

**What it does not show.** The integer range of the format (where large vertices saturate or wrap;
E606 used up to +124% of a 256 pixel target); the rounding at negative coordinates, tie or not;
the width of the edge function beyond products of 2^30; the viewport scale itself: E606 and E607
used the tool's clip coordinates, which are exact floats on power-of-two targets; the float32
resolution of the window coordinate is also the resolution of the sweeps at x near 215.

**FINE2 (held out from the rule above, predictions-fine2-1138.toml frozen after the fine analysis
and before the first job).** A held-out set, 422 D jobs (none flagged): 150 random triangles at
1/4096 on 128 x 128 (50 small, 50 medium, 50 near-centre with half-integer vertices jittered by 0
to 8 units), 60 near-centre ones at 1/65536 on 256 x 128, 132 sweep cases (33 steps of 1/4096
across the tie, four edge kinds, 128 x 128) and 80 tiny edges (a 50 to 120 pixel long edge, 40
directions, passing the centre of pixel (128, 128) of a 256 x 256 target at a cross product of +1
or -1 in units of (1/256 pixel)^2 = 1/65536 pixel squared, the vertices on the 1/256 grid). [HW]
The rule (round half up to 1/256, exact test, left/top ties) mispredicts 0 of 6586368 pixels of
the 342 non-tiny cases and every sweep flips after the same step (agreement 132 of 132; the change
is after case index 23 = g 7 in every one); the alternatives mispredict 280 (half-down), 1403
(floor), 1226 (round to 1/512) and 1717 pixels (no rounding); the depth through the rounded
vertices is within 1 unit for 98.1% of the sweep pixels (maximum 1.7), 99.2% and 99.6% on the
near-centre triangles (maximum 2.0 and 1.9), 95.6% on the medium ones (maximum 9.1). The 80
tiny-edge images equal the exact integer model's in 80 of 80 cases. The test is one-sided: at +1
the pixel is drawn in 40 of 40, so the hardware does not drop a centre that lies 1 unit of
1/65536 pixel squared inside an edge of up to 135 pixels; at -1 it is drawn in 0 of 40, but in
every one of those 40 a second edge puts the centre 4.5e7 to 2.1e8 units squared outside, so
the half cannot discriminate and counts for nothing. Predictions PH1 to PH4 of
predictions-fine2-1138.toml all hold (PH3 after the analysis bug described next; as frozen it asked
for 95% at +1 or -1 and was passable with the 40 informative cases alone, it held 40 of 40).

The first analysis of the tiny edges said 51 of 80 (PH3 failed): the post-hoc rounding function of
the frozen `fine_extra_p1138.py` added one unit to every coordinate when the vertex unit already
equals the grid (1/256), which only the tiny-edge cases have; the fix (and a test) is in
`fine_extra_p1138.py`, which therefore no longer matches `manifest-fine2-1138.sha256` (nor does
tests/test_fine2.py, changed later; neither the tests nor the stage binaries the manifests name are
in the dataset); the fine set (units 12 and 16) never reached that branch. [HW] So the integer edge
setup of the ISP does not lose the +1 centre for products of up to about 2^30 (an edge of 135
pixels is 34560 units: 34560 x 34560 = 1.2e9 units squared), more than a float32 mantissa holds;
[infer] it is an integer (or wide fixed-point) computation of the cross product of the rounded
vertices. How a float32 evaluation of the edge functions would classify these cases depends on the
form of the evaluation and is not claimed here.
