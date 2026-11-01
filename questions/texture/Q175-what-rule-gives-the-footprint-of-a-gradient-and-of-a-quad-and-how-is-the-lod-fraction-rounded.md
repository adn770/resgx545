+++
id = "Q175"
question = "what footprint function of dudx, dvdx, dudy and dvdy (and of a quad's own derivatives) does the sampler take the logarithm of, given that on these cases the largest component fits a one-vector gradient and the larger vector length fits four and a quad with a v term but neither fits two u terms or two v terms, and what rounding of the fraction of the LOD in 1/64 does it use (a fraction of 6.946/64 reads as 7/64 where the rest truncate)"
unit = "texture"
kind = "hw"
value = "low"
phase = 11
evidence = ["E563", "E041", "E276"]
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
