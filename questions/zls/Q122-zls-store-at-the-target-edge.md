+++
id = "Q122"
question = "what does the ZLS store write for the pixels of an edge tile that lie outside the target, and for the 16 x 16 blocks outside it?"
unit = "zls"
kind = "hw"
value = "low"
phase = 11
evidence = ["E465", "E730", "E831"]
terms = ["CR_ISP_ZLSCTL"]
+++

E465: a 34 x 18 target has four tiles; the store writes all 2048 dwords of them, 612 for the
target's pixels, 312 more for pixels outside it that the full-screen triangle covers (they hold the
ramp), and 1124 dwords of the background depth 1.0 for the rest. So the store writes whole tiles
whatever the target's size, and which outside pixels hold the triangle's depth and which the
background follows some rule of the rasteriser (a 16 x 16 block, a 2 x 2 quad) that one size does
not show.

What is open: that rule, and whether it matters to a depth buffer that a later render loads (it
does if the buffer is read back outside the target). To settle it: the ramp stores of E465 at sizes
that end inside a block (a width of 34, 50, 66, 18) and their outside dwords counted.

Run in 11.39 (E730), re-scored post hoc (the frozen recompute scored 0 of 12 and favoured "whole
tile area stored", 12 of 12; plan.md is not hashed and was edited after the manifest): the stored
triangle depth in a tile is the set x < 1.25 W and y < 1.25 H on 12 of 12 jobs (the centre rule x +
0.5 < 1.25 W is [infer], the edge forms give identical sets) at 6 sizes (34 x 18 control 924 as in
E465; 18 x 18 484, 50 x 26 1984, 66 x 34 3444, 98 x 50 7564, 34 x 50 2604); the rest of the tile
holds the background depth. Answers the open rule at these alignments, on a post hoc re-score; other
alignments are Q287.

Note 2026-11-11 (R3-geo-c g-z, E831). Answered held out at even sizes: rule A (x + 0.5 < 1.25 W,
y + 0.5 < 1.25 H, cut at the tile area) gave the stored set in 10 of 10 new full-screen cells
(fractions .0 and .5 of 1.25 W, and the band past the tile area), ROUND, CEIL and RSTRICT refuted;
a single triangle is stored as its own raster cut by the band, past the target too; the
store writes the target's tiles only, nothing past them (post hoc, 15 of 15 dumps). The odd
sizes (the fraction .75 that separates rule A from FLOOR) are Q287's. User decision R4-1 (a)
retires this question as answered by E831; the retirement waits on the citations of Q122 outside
the records (sgx-pipe `zls.rs` refusals and `OPEN`, `unitvec.rs`, `outcome.rs`, the unit-vector
tests, `pipe_inventory.py`, doc/specs and doc/roadmap.md), which must move to E831 or Q287 first.
