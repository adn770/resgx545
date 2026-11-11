+++
id = "Q280"
question = "what makes up to 56 of 2048 pixels of a gradient job differ from the Euclidean footprint of the pairs (op0, op2) and (op1, op3) with a LOD fraction truncated to 1/64 (E721), a rounding of the length, of the logarithm or of the operands, or a footprint that is not exactly Euclidean"
unit = "texture"
kind = "hw"
value = "low"
phase = 11
evidence = ["E721", "E563", "E744"]
terms = ["T0.MIPFILTER"]
+++
E721: the footprint P is the best of six on 8 of 8 held-out jobs and exact on 4, but the other 4
jobs miss by 19 to 56 pixels (whole columns or rows: a boundary shift of one column or row where the
LOD fraction crosses a 1/64 step; the rule holds to better than 0.1%) and 7 of the 8 ladders miss by
8 to 32 pixels (in sample the miss was 8 to 65). The misses are what Q175's rounding and the shape
of the log2 leave. To settle it: for the 4 jobs with a residual (lg-sq1, lg-sq2, lg-ns1, lg-ns2)
list the missing pixels with the level and fraction the pixel gives, and fit the length to the
(level, fraction) that the misses imply, then predict a fifth set before running it; ladders at
1/512 of a fraction step around the misses.

Status: open. Narrows Q175 (the footprint and the truncation are held-out confirmed).

Post hoc 2026-11-09 (S1, E744; not an answer; the frozen verdict was cannot tell, the ladders
having held u and v constant and covered 0.031 of a 1/64 level step). The point-sampled output
follows the level coarsely (bits 11:8 of the constant dword 1, 4, 6, 14 for n = 2, 13, 22, 56,
about n / 4), a resolution nearer 1/16 than 1/64 of a level. A ladder must span at least one such
step to show where the output changes.

Moved 2026-11-11 from Q175 (retired as answered by E721: the footprint is the larger of the two
Euclidean lengths and the LOD fraction truncates to 1/64, held out on 8 of 8 jobs and 8 of 8
ladders). What the answer leaves besides this question's residual: the quad's own derivatives
(`lod-auto`) were not run, so the footprint of a quad that takes its own derivatives is not shown
by E721 and is open here.
