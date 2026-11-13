+++
id = "Q202"
question = "do the attribute and depth planes of E606 hold with perspective (w other than 1), which arithmetic forms the window x / w (an exact divide, a float32 divide or a reciprocal: E992's jobs do not part them), and do the coverage rule and the planes hold with ISP word 0 bit 28 widening and for lines and points (the coverage with perspective is E992's, with 2x and 4x sample points E953, E954 and E990's, with vertices well outside the target E979's and on targets whose half-size is not a power of two E680's and E913's)"
unit = "isp"
kind = "hw"
value = "high"
phase = 11
evidence = ["E606", "E214", "E215", "E224", "E281", "E502", "E680", "E913", "E953", "E954", "E979", "E990", "E992"]
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

Narrowed 2026-11-13 (round 10 offline, decisions R10-1 a and R10-7 a, E992). Three clauses are
answered by records this question did not cite: targets whose half-size is not a power of two (E680:
6 of its 10 targets, 0 of 1.09e9 pixels off; E913: 128 x 96, 128 x 144, 64 x 33 and 96 x 47, 240 of
240), vertices well outside the target (E979: one or two vertices at 2^22 to 2^25 pixels, exact
coverage in 10 of 10 rows, clamp and wrap refuted) and the 2x and 4x sample points (E953, E954 and
E990: E281's slots with top-left ties in every tile and window run). Perspective (E992): on
r6-pixel's 114 kept jobs with w from 2.5e-4 to 8027, E606's coverage rule on window x / w draws
every pixel (0 of 466944 off) under four declared rivals for the divide, and no pixel parts them,
the w ramp across each triangle being mild. Open: the depth and attribute planes with perspective
(the pixel side refuses a 1/w other than 1), the divide's arithmetic (a large w ramp with a centre
within about 1e-5 pixel of an edge would split it), ISP word 0 bit 28 (Q031 holds the multisampled
hang) and lines and points (Q159 to Q161 hold their rules).
