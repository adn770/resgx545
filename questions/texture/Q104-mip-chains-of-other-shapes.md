+++
id = "Q104"
question = "does a mip chain of a 1D texture, of a texture with a side of 1 at level 0, or of a format other than 32 bits read as the non-square chains of E562 do (both sides halving to 1, T0's fields reading it as a square chain)?"
unit = "texture"
kind = "hw"
value = "low"
phase = 11
evidence = ["E276", "E441", "E562", "E1052"]
terms = ["T0.MAX_LEVEL", "T0.BITS26_21", "T0.MIPFILTER"]
+++

On the 16x16 chain of five levels (E276) and a 128x128 chain of eight (E441) the level read follows
level = max(0, min(round_half_up(LOD + (bias field - 63) / 8), maximum, last level)), a maximum of
15 and 0 read level 0, and MIPFILTER blends the two levels around LOD + bias byte for byte. Both
are square.

Narrowed in 11.32 (E562, 108 jobs). On twiddled 32-bit textures of 32x16, 128x16, 16x32, 64x4 and
8x64 the chain halves both sides down to 1x1 (the last level 1x1, a LOD above it clamping there):
8 of 8 fit and 49 of 49 held-out jobs exact, the reading where the short side stops the chain and
the square-padded reading falsified, and T0's maximum, bias and MIPFILTER fields read it as they
read a square chain (44 jobs, 22 of 22 and 22 of 22). That answers the question as it was first put:
how many levels, where each lies and whether the same fields read it.

What is open is what that run did not reach: a 1D texture, a texture with a side of 1 at level 0,
a format other than 32 bits in a chain, and non-square chains with a long side above 128 or a short
side above 16 (E562 measures short sides of 4 to 16, 32 only in the control).

To settle it: the generator of E562's shapes (the scratch buffer as the texture, each texel naming
its dword) at those sizes and formats, with T0 bits 20:17, bits 26:21 and MIPFILTER as E441 varies
them.

Note 2026-11-14 (round 15, session r15-tex, decision R15-1 a; E1052). Every open clause is decided
by held-out rows with passing controls (E562's shp-32x16-l5 and shp-128x16-l7-x0 rerun): the chain
halves both sides down to 1 x 1, levels back to back, on a side of 1 at level 0 (1 x 32, 32 x 1), on
a 1D texture (smp1dreplace on 64 x 1) and on 64 x 32 and 256 x 32, 11 of 11 rows (the chain stopping
at the short side's 1 and the square-padded chain 0 of 11 and 0 of 9); T0's maximum (3 on 64 x 1)
and bias (0x33 on 32 x 1) read these chains by E441's rule; on u16 (32 x 16, 16 x 64) the levels are
packed back to back in 16-bit texels (4 of 4; in dwords of a 32-bit chain 0 of 4), and MIPFILTER
blends two 16-bit levels as one 16-bit lerp (a (64 - f) + b f + 32) >> 6, not per byte (one row, f
32). "1D" reads smp1dreplace on a W x 1 texture [infer] (R15-6 a). sgx-sim reads these chains.
Retirement proposed per R15-6 a (the lead confirms).
