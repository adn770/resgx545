+++
id = "Q202"
question = "do the coverage rule (centre sample, vertices on the 1/256 grid, top-left ties) and the attribute and depth planes of E606 hold with perspective (w other than 1), under multisampling (the 2x and 4x sample points), with ISP word 0 bit 28 widening, for lines and points, with vertices well outside the target (a guard band) and on targets whose half-size is not a power of two (the clip coordinate is then inexact in float32)"
unit = "isp"
kind = "hw"
value = "high"
phase = 11
evidence = ["E606", "E214", "E215", "E224", "E281", "E502"]
terms = []
+++
E606 used w = 1, single sampling, triangles, vertices from -9% to +124% of the target (27 of 1536
cases outside it) and half-sizes of 32, 64, 128. The sample-position rules of E214, E224 and 3d.md
11.8 were fitted without this arithmetic, so the eight-sample rule's tie handling may differ from
the centre rule's. Phase 12.3 and 12.8 need each of these before the ISP model leaves its
refusals.

To settle it, in this order: w = 2 and a w ramp across the triangle (the same sweeps, the plane at
the pixel centre with perspective correction: is the coverage test on window x/w exact?); the
sample-position sweeps of E606 under CR_ISP_MULTISAMPLECTL and CR_ISP_SAMPLE_POS with bit 28 (a
per-sample exact test); 4x with the closed driver's words; vertices at -4 and +4 target widths (a
clip or guard-band effect); 96 and 160 wide targets with vertices placed by the viewport words, not
by the tool's clip coordinate.
