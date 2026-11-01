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
