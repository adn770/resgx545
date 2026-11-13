+++
id = "Q261"
question = "how large is the error band of the ISP's edge evaluation (E684: 16 pixels in 14 of 208 cases within 5.6e-4 pixel of an edge line) as a function of the far vertex's distance and the edge's length, and where does the vertex format saturate, wrap or cull beyond 2^21 pixels (the 24.8 range of 2^23 pixels, Q199)"
unit = "isp"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E684", "E682", "E979", "E984"]
terms = []
+++
E684 puts one vertex, on the 1/256 grid, at 2^9 to 2^21 pixels, on 64 x 64 and 512 x 512 targets
only; the coverage is the exact one except in a band of 3.5e-5 to 5.6e-4 pixel around the edges (14
of 208 cases, 1 or 2 pixels each), no clamp up to 2^20, no wrap up to 2^21, no fault. E682's edges
of 2200 pixels inside a 4096 target are exact at +-1 of a 1/65536 pixel squared, so the band is tied
to the vertex being outside the target (or the edge being long), not to the size of the cross
product alone. The tool takes below 2^30 units, so 2^22 pixels at the unit 1/256 and the 2^23 of a
24.8 word were not reached.

To settle it: a tool option that takes vertices in 1/256 pixel above 2^30 (the clip coordinate
itself is a float32: 2^23 pixels is 2^18 on 64 wide), E684's cases at k = 22 to 26 one at a time
(they may hang the TA); edge cases of E682's kind with the far vertex at 2^10, 2^14 and 2^18 pixels
to measure the band against the cross product; the same on a target with a half-size that is not a
power of two (where the clip coordinate is inexact too).

Status: open.

Narrowed 2026-11-13 (E979). The vertex format does not saturate, wrap or cull at 2^23 pixels: up to
2^24 both ways and -2^25 the image is the exact one outside the 1e-3 pixel band (10 of 10 rows,
H-SAT and H-WRAP refuted). Open: the band's width against the far vertex's distance and the edge's
length (band pixels were not scored).

Narrowed 2026-11-13 (round 10 offline, decision R10-1 a; E984, post hoc). E979's band pixels are
not noise: the 26 that lie on a far edge between its near vertex and the far one (rows with the
vertex at 2^23, 2^24 and -2^25 pixels along x) are all drawn, just outside the exact line, and the
20 others agree. With the near vertices fixed, the far vertex moved alone fits them only from 43,
52 and 42 pixels in y (or -171, -206 and -167 in x), a one-sided bound about the same at the three
distances. Open: the displacement itself and its dependence on the distance, the axis and the
edge's length (the seeds plan's stage pivot, closing10/seeds/exp-seeds-r10.md section 9, sweeps
the far vertex to pin it), and the format past 2^25 pixels (Q199).
