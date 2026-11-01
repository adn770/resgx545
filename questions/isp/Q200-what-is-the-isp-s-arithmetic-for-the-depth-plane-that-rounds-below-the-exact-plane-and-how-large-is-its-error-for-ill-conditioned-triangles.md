+++
id = "Q200"
question = "what is the ISP's float32 arithmetic for the depth plane (the stored depth is the exact plane at the pixel centre minus 0.39 of 2^-24 on average, bit-reproduced by none of the 18 variants of E606), and how large is its error as a function of the plane's gradient"
unit = "isp"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E606", "E072", "E465", "E731"]
terms = []
+++
E606: the stored depth of covered pixels is within 1 unit (2^-23, absolute) of the exact plane at
the centre for 99.3% of 409950 pixels, but the error follows the plane's gradient |dz/dx| +
|dz/dy| (below 0.03: maximum 1.9 units; 0.3 to 1: 11; above 3: 145), the stored value is below the
exact plane for 78.7% of the pixels (mean -0.39 of 2^-24), and none of the 18 float32 variants
tried (origin vertex, divide or reciprocal, relative or absolute plane, round to nearest)
reproduces more than 41.2% of the dwords, against 58.8% for the exact plane truncated toward zero
(probes/p1138/depth-error-1138.txt). The rule is not known. Until it is, the simulator does not
claim bit equality of depth: it keeps the exact plane only as a comparison tolerance against
hardware results (3 units, absolute, for a gradient below 0.03), flags depth results as
tolerance-only and refuses planes above the gradient limit.

To settle it: a table of triangles whose plane has a single non-zero gradient (a depth ramp along x
on a wide triangle, then along y) with depths on a lattice, so that the stored mantissas show how
the per-pixel step accumulates (a running sum of a rounded step, a product, a fused form); the
pixel at (x, y) as a function of x on one row says which. Also a depth that is the same at all
vertices (the constant plane: is it exactly the vertex value?) and the dependence on the vertex
order (the six permutations of one triangle).

Run in 11.39 (E731, 21 jobs on a 256 x 128 target), by direction and binade: the dyadic control
fits 378 of 384 tiles for all three candidates (it does not discriminate, and fails in b2: 3 tiles
each in dp-ax-b2 and dp-ay-b2, so it does not validate the tile structure). For a non-dyadic
gradient in y, truncation and the walk fit every consistent tile in b0 (63 of 63) and b1 (64 of
64; RN 63 and 56); in x, dp-bx-b0 fits none of 58 consistent tiles and b1 fits 34, 40, 38 of 43;
in b2 no tile admits a single T, so the premise (stored word = trunc(T + A (x + 0.5) + B (y +
0.5))) fails and no candidate can be refuted there. Class c: 232, 200 and 64 of 384 in total. The
candidates are not confirmed where the premise holds in x; the rule is not found (Q288). The tile
corner "60% in main" statistic is not confirmed as a model of the stored words.
