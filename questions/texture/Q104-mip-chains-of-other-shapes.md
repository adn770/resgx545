+++
id = "Q104"
question = "does a mip chain of a 1D texture, of a texture with a side of 1 at level 0, or of a format other than 32 bits read as the non-square chains of E562 do (both sides halving to 1, T0's fields reading it as a square chain)?"
unit = "texture"
kind = "hw"
value = "low"
phase = 11
evidence = ["E276", "E441", "E562"]
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
