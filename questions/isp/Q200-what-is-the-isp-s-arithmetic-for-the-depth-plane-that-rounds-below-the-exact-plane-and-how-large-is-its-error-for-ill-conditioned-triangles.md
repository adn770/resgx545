+++
id = "Q200"
question = "why do the dyadic controls of E731 store one or two ulps below the truncated exact plane, below binade 0, in a region bounded by a diagonal line (dp-ax-b1: the pixels with x + 2y >= 319), and what error of the ISP's depth plane that region does not explain remains as a function of the gradient (its rule is Q288's)"
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

Rescoped 2026-11-09 (from the dumps of E731, an analysis and not a new measurement; E731 carries
the dated correction). The question as first worded asked for the arithmetic of the depth plane
and its error against the gradient in one. They separate. The gradient's rule is Q288: for a
non-dyadic gradient the stored words follow one effective gradient word, 0x3923d700 for A =
1/6400, where nine rules still fit. What stays here is an effect no gradient error can make,
because a dyadic gradient has none: dp-ax-b1 (A = 2^-13, B = 0, every exact value representable
in float32) stores 9216 of 32768 pixels one ulp below the truncation of the exact plane, exactly
those with x + 2y >= 319; dp-ax-b2 and dp-ay-b2 store 7680 one ulp and 1536 two ulps below, in
the same counts per tile row (0, 0, 256, 768, 1280, 1792, 2304, 2816 in tile rows 0 to 7) and per
macrotile column (1024 and 8192 in the two columns of 128 pixels), whichever way the gradient
runs. Binade 0 has none (dp-ax-b0 and dp-ay-b0: 32768 of 32768 exact). The mechanism is
unexplained. Open: what the diagonal is (a line in pixels, x + 2y, against a 32 x 16 tile grid;
whether it moves with the target size, the vertices or the depth's binade), what the second ulp
in b2 depends on, and whether the same region lies under the non-dyadic jobs of b1 and b2 and
adds to the gradient's error. To settle it: a dyadic ramp at the binades 0 to 3 on targets of
other sizes and with the triangle's vertices moved, the words compared with the truncated
exact plane pixel by pixel.
