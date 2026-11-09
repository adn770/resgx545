+++
id = "Q288"
question = "what rule gives the stored depth of a plane with a non-dyadic gradient in x (class b and c of E731) when the tile-corner value T by rounding, truncation or a walk of RN(32 A) fits 0 of 58 tiles of dp-bx-b0 and no single T fits any tile of dp-bx-b2 and dp-by-b2"
unit = "isp"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E731", "E606"]
terms = ["CR_ISP_ZLSCTL"]
+++
E731: class a (dyadic) fits at 98.4% of tiles, so the interval method works; class b 153 to 167 of
576 and class c 232, 200, 64 of 384 for RN, truncation and the walk. The y direction (dp-by-b0 and
b1) fits truncation and the walk on 63 of 63 and 64 of 64 consistent tiles, the x direction does
not. To settle it: a single row of tiles with a non-dyadic A only (B = 0) read per pixel along x
within one tile, to see whether the step per pixel is A or its float32 rounding, then the tile-to-
tile step; the same with z0 in binade 2 where no tile admits a single T; the three vertex orders
were run for dp-bx-b0 and change nothing.

Status: open. Narrows Q200 (the candidates are not confirmed in x; in y truncation and the walk fit
in b0 and b1; b2 is outside the premise).

Analysis of E731's dumps, 2026-11-09 (existing data, not a new measurement). For each row of
dp-bx-b0 (A = 1/6400, B = 0, depths 0.5 to 0.5625) the stored words w satisfy w <= T0 + g (x +
0.5) < w + ulp(w) for one g over the covered pixels of the row; a row's pairs of pixels bound g
and the bounds of rows 0 to 106 meet: g lies in [1.5624983486e-04, 1.5624985099e-04], the upper
end being exactly the float32 word 0x3923d700 (reproduced in plain Python over the unpacked dump).
The exact A is 0x3923d70a, 10 float32 ulps above the word; the range is about 0.1 ulp wide. So in
b0 one effective gradient word fits every row, each row with its own offset; whether a per-tile
offset also fits was not rechecked. Which rule produces 0x3923d700 from A = 1/6400 is not decided:
the candidate list of the analysis (`grad_candidates`) gives exactly this word for the mantissa of
A truncated to 16, 17, 18 or 20 significant bits, round to nearest at 16 bits, and a fixed-point
gradient with a least bit of 2^-30, 2^-31 or 2^-32 (truncated) or 2^-30 (rounded): nine rules that
every class b job here, one A and one depth step, cannot split. The plain float32 gradient and
round to nearest at 20 bits do not give it. The ramps that would split the nine rules are not run.
The part of the first paragraph that said b2 is "outside the premise" is corrected in E731 and
moved: the dyadic controls themselves deviate below binade 0 in a region bounded by a diagonal
(Q200), so the b1 and b2 failures of the non-dyadic jobs cannot be put to the gradient rule
alone [infer].
