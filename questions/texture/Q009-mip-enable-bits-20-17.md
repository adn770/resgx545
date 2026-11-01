+++
id = "Q009"
question = "what do T0's maximum level 15 and the LOD bias (bits 26:21) do beyond a five-level chain read with nearest filtering at whole LODs?"
unit = "texture"
phase = 6
evidence = ["E041", "E276"]
terms = ["T0.NO_MIPMAPS", "T0.BITS26_21", "T0.BITS20_19", "T0.MAX_LEVEL", "MIPMAPS_PRESENT"]
+++

On the tagged 16x16 chain, T0 bits 20:17 are the highest level read and bits 26:21 an LOD bias
of (value - 63) / 8; level = max(0, min(round_half_up(LOD + bias), maximum)) fits all 192 reads,
in two runs, a biased LOD below 0 reading level 0 (E276). Bit 18 is not a mipmap disable. So
what the fields do is answered.

What is open: why 15 reads level 0 like 0 (a marker of no mipmaps, or a maximum the chain does
not reach that falls back); the bias with T0.MIPFILTER set (linear between levels) and at
fractional LODs; the fields on a chain of other sizes and on non-square textures.

To settle it: a tagged chain of eight levels (128x128 down to 1x1) with 20:17 at 5 to 15, the
bias at LOD 1.25, 1.5 and 1.75 with T0 bit 9 set, and the same on a 32x16 chain.

Not run in 11.15: the settle plan needs a tagged chain of eight levels and a 32x16 chain; the tool's
tagged chain has five levels and is square. Status: narrowed, not answered; missing: a texture
option for the chain's depth and shape.
