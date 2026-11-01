+++
id = "E035"
claim = "With the state words T0 0x07fe0000, T1 0x0d00f00f (RGBA8888, a 16x16 power-of-two texture, TEXTYPE 0) and T3 0x00800800, every one of the 1062 triangle pixels samples the texel (tx, ty) = (((x + 32) / 2) mod 16, ((y + 32) / 2) mod 16), nearest and repeated; texel (tx, ty) is dword i of the texture with ty's bits in the even bits of i and tx's in the odd bits (so the texture is twiddled), and RGBA8888 holds R in byte 0"
unit = "texture"
method = "probes/texture/fetch.toml, texture-fetch-tex-fetch, on the laptop, linux fork with the debug option on: the 64x64 triangle with its pixel PDS program replaced to fetch from a 16x16 RGBA8888 texture in the scratch buffer, whose dword i is 0xd0000000 | i, DOUTI word 0 0x46012201 with two coordinates per vertex; one run"
tiers = ["HW", "infer"]
date = "2026-11-01"
data = ["texture-fetch"]
terms = ["TEXTYPE", "T1.TEXTYPE", "T1.TEXFORMAT", "DOUTI0.TEX_COORD_SOURCE"]
+++

**What runs.** The triangle job (E023) with a pixel PDS program that issues one texture
fetch per pixel and writes the fetched value to o0. The texture state words are T0 0x07fe0000
(nearest filtering, repeat), T1 0x0d00f00f (RGBA8888, power of two, 16x16), T2 the scratch
buffer and T3 0x00800800. Each texel names its own address: dword i holds 0xd0000000 | i.

**Results.**

- The triangle covers 1062 pixels; each holds 0xd0 in bits 31:24 and 0 in bits 15:0, and a
  value in bits 23:16: 233 distinct values, 4 pixels each in most cases (the others at the
  triangle's edges).
- Reading bits 23:16 as the dword index i, with ty from the even bits of i and tx from the odd
  bits, all 1062 pixels satisfy tx = ((x + 32) / 2) mod 16 and ty = ((y + 32) / 2) mod 16:
  two pixels to a texel in each direction, wrapped at 16. With the roles of x and y
  exchanged only 72 pixels fit, and with the dword's byte 0 read as the index only 4.
- The dword 0xd00000c9 therefore comes out as 0xd0c90000: the texel's byte 0 lands in bits
  23:16, the red position of the ARGB word the target holds, and the 0xd0 byte in the alpha
  position.

The 2-pixels-per-texel step and the offset 32 come from the triangle's coordinates (two
per vertex, the texture addressed unscaled with repeat); the fit is the data's, not the
coordinates', which the table does not state.

**Not shown.** That every power-of-two size is twiddled the same way (only 16x16 was run);
that a non-power-of-two texture is not (E041 has the sizes of the mip chain). "Twiddled" is the
name of the interleaved order and is inferred from the T1 type field, not read from it
**[infer]**.
