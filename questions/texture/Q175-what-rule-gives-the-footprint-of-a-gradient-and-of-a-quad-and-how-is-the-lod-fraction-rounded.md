+++
id = "Q175"
question = "what footprint function of dudx, dvdx, dudy and dvdy (and of a quad's own derivatives) does the sampler take the logarithm of, given that on these cases the largest component fits a one-vector gradient and the larger vector length fits four and a quad with a v term but neither fits two u terms or two v terms, and what rounding of the fraction of the LOD in 1/64 does it use (a fraction of 6.946/64 reads as 7/64 where the rest truncate)"
unit = "texture"
kind = "hw"
value = "low"
phase = 11
evidence = ["E563", "E041", "E276", "E721"]
terms = ["T0.MIPFILTER"]
+++

E563 leaves the log2 shape settled (a piecewise-linear exponent-plus-mantissa is exact on 0 of 21
gradient jobs) and the footprint open: on these cases gr-vx (dudx and dvdx) fits the largest
component, gr-all (all four) and au-vx, au-vy and au-vx4 (a quad with a v term) the Euclidean
length, and gr-uu, gr-vv and gr-uvy fit neither. The partition was read from the vectors after the
run and is not held out (held-out exacts: euc 1 of 7), so "fits" means on these cases. To settle
it: sweep two components at a time over a grid of values (not powers of two) and fit rho = f(a, b)
per pixel from the (level, fraction) each pixel gives; run the fraction at 1/64 steps around 7/64,
0.5 and 1 to see the rounding (the column x = 5 of the diagonal ladders k = 2, 3 and 4 is the lead).

Run in 11.39 (E721, 16 held-out jobs): on four independent operand sets on 64 x 64 and four on
128 x 32 the footprint "larger of hypot(op0 W, op2 H) and hypot(op1 W, op3 H)" has the highest
count on 8 of 8 (1992 to 2048 of 2048 pixels; E563's pairing at most 61, the other four at most
256), and the LOD fraction truncated to 1/64 gives 2016 to 2048 of 2048 on 8 of 8 ladders
(rounding 1160 to 1840). The rule is not exact: 4 of 8 gradient jobs and 1 of 8 ladders match
every pixel, residuals up to 56 pixels in whole columns or rows (a boundary shift of one column or
row where the fraction crosses a 1/64 step; the rule holds to better than 0.1%). "Best of six
declared footprints", not a proof of the Euclidean form against length approximations. Status:
narrowed to the residual (Q280); the quad's own derivatives (lod-auto) were not run.
