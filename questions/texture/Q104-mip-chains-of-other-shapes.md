+++
id = "Q104"
question = "do T0's maximum level, LOD bias and MIPFILTER read a non-square chain (32x16) as they read the square ones, and how many levels does such a chain have?"
unit = "texture"
phase = 11
evidence = ["E276", "E441"]
terms = ["T0.MAX_LEVEL", "T0.BITS26_21", "T0.MIPFILTER"]
+++
 On the 16x16 chain of five levels (E276) and a 128x128 chain of eight (E441) the level read
follows level = max(0, min(round_half_up(LOD + (bias field - 63) / 8), maximum, last level)), a
maximum of 15 and 0 read level 0, and MIPFILTER blends the two levels around LOD + bias byte for
byte. Both are square. What a chain of a texture whose sides differ does is not run: whether its
levels halve both sides down to 1x1 (a 32x16 chain of six levels, the short side stopping at 1) or
stop with the short side, where each level lies, and whether the same fields read it.

To settle it: the eight-level generator of tex_words.py (the scratch buffer as the texture, each
texel naming its dword) for a 32x16 and a 128x16 chain, T0 bits 20:17, bits 26:21 and MIPFILTER as
E441 varies them.
