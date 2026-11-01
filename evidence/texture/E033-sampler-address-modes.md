+++
id = "E033"
claim = "On a stride texture (T1 type 6) the sampler clamps to the edge for each address mode 1 to 7 tried; on a twiddled 16x16 texture the modes 0 to 3 act as repeat, mirror (period twice the size), clamp to the edge and mirror once (the absolute coordinate, then clamped), at all seven positions tried, and the low three bits of the mode field do not act on the u coordinate; modes 4 to 7 read texels that none of 0 to 3 gives"
unit = "texture"
method = "probes/texture/sampler.toml, texture-sampler-smp-address (40 cases) and texture-sampler-smp-address-border (4), on the laptop, linux fork with the debug option on: smp2d programs run through the probe host, the four state words built in registers, over a 16x16 texture in the scratch buffer whose dword i holds 0xd0000400 | i, one run"
tiers = ["HW"]
date = "2026-11-01"
data = ["texture-sampler"]
terms = ["T0.ADDRMODE_U", "T0.ADDRMODE_V", "T0.STRIDE", "T1.TEXTYPE", "TEXTYPE", "TEXTYPE.STRIDE"]
+++

**What runs.** Each case builds the four state words T0 to T3 and a coordinate pair in
registers, runs one `smp2d` and reads the result register back. The texture is 16 wide and
16 high with dword i holding 0xd0000400 | i, so the result names the texel it came from; the
coordinates are normalized floats, 1.09375 for u = 17.5 texels, and v is 0.5 texel except in
the V cases. For a twiddled texture (T1 type 0) the texel (x, y) is the dword whose odd bits
are x's and even bits are y's (E035). Modes sit in T0 bits 8:6 for U and 5:3 for V.

**Results.**

- Stride texture, U and V mode both 1, 2, 3, 4, 5, 6 and 7, at (u, v) = (17.5, -1.5): every
  case returns 0xd000040f, dword 15 of the first row: u clamped to the last texel and v to the
  first. Mode 0 was not run on the stride texture, and only one position was.
- Twiddled texture, texel x returned for U mode m at u (y is 0 in all of these):

| u | mode 0 repeat | mode 1 mirror | mode 2 clamp | mode 3 mirror once |
|---|---|---|---|---|
| 17.5 | 1 | 14 | 15 | 15 |
| 33.5 | 1 | 1 | 15 | 15 |
| -17.5 | 14 | 14 | 0 | 15 |
| 40.5 | 8 | 8 | 15 | 15 |
| 31.5 | 15 | 0 | 15 | 15 |
| 16.5 | 0 | 15 | 15 | 15 |
| -0.5 | 15 | 0 | 0 | 0 |

- V at v = -1.5: mode 0 returns row 14, mode 1 row 1, mode 2 row 0, mode 3 row 1.
- State T0 with bits 2:0 = 2 and U mode 0 at u = 17.5 returns the texel of the plain mode 0
  case (x = 1): those bits do not act on u.
- Modes 4, 5, 6 and 7 for U at u = 17.5 return dwords 0xb6 (x 13, y 6), 0x94, 0x15e and 0x15e
  past the texture base: not a texel of the 16x16 image for modes 6 and 7, and not a texel the
  clamp, repeat or mirror modes give for 4 and 5. They are recorded and not explained.

The report of the table lists its hypotheses (stride clamps; modes 0, 1, 2, 3 as above) as
settled by these cases. Nothing here varies: the table ran once.

**Not shown.** That mode 0 clamps on a stride texture; other stride sizes; V modes 4 to 7;
what the modes above 3 read.
