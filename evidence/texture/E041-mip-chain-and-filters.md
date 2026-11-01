+++
id = "E041"
claim = "A twiddled 16x16 texture's mip levels follow level 0 back to back, largest first, each twiddled at its own size (levels 1 to 4 start 0x100, 0x140, 0x150 and 0x154 dwords after level 0); they are read when T0 bits 26:21 are 0x3f and bit 18 is clear and bits 20:17 are not all clear; T0 bits 11:10 are the minification filter (1 and 2 linear, 0 and 3 nearest) and bit 9 picks the nearest level, a half rounding up (0), or blends the two levels around the LOD by its fraction (1)"
unit = "texture"
method = "probes/texture/mipmaps.toml (mip-level, mip-level-hostfill, mip-t0-field, mip-mipfilter, mip-minfilter, mip-grad, mip-bias) on the laptop, linux fork with the debug option on: smp programs through the probe host over a 16x16 twiddled texture in the scratch buffer with a chain of five levels packed after level 0, one tag per level (top byte 0xd0, 0x40, 0x80, 0xc0, 0xf0), T0 varied; one run"
tiers = ["HW"]
date = "2026-11-01"
data = ["texture-mipmaps"]
terms = ["T0.MINFILTER", "T0.MIPFILTER", "T0.MAGFILTER", "T0.NO_MIPMAPS", "T0.BITS26_21", "T0.BITS20_19", "MIPMAPS_PRESENT"]
+++

**What runs.** The probe host of E033 with a 16x16 RGBA8888 twiddled texture whose five levels
(16x16 down to 1x1) are packed after level 0, each level's texels carrying a tag in the top
byte so the result names the level. The T0 word 0x07fa0000 is nearest filtering, repeat and
mipmaps enabled; the other cases change its fields. smp2dreplace takes the LOD as an operand,
smp2dgrad derives it from the coordinate derivatives and smp2dbias adds a bias.

**Layout (mip-level-hostfill).** With the host's counting fill as the texture, dword i
holding 0xd0000000 | i and level 0 at dword 0x800 of the scratch buffer, smp2dreplace at LOD
1, 2, 3 and 4 returns dwords 0x913, 0x944, 0x951 and 0x954: inside level 1 (0x900 to 0x93f),
level 2 (0x940 to 0x94f), level 3 (0x950 to 0x953) and level 4 (0x954). The levels follow
each other with no gap, level l starting 4 * sum((16 >> k)^2, k < l) bytes after level 0.
Level 0 (LOD 0) returns dword 0x84e. In the tagged chain the same LODs return tags 0x40, 0x80,
0xc0 and 0xf0.

**Results.**

- Level by LOD (mip-level, T0 0x07fa0000): LOD below 0.5 gives level 0 (-1, 0, 0.25),
  0.75 and 1.0 level 1, 2.0 level 2, 3.0 level 3, 4.0, 5.0 and 8.0 level 4 (the last level
  clamps). smp2d without a LOD operand at constant coordinates reads level 0.
- Enabling (mip-t0-field, LOD 2.0, level 2 returns tag 0x80): bits 26:21 at 0x3f with bits
  20:17 at 0xd, 0xc, 0x9 or 0x5 read level 2; with bits 20:17 at 0x0, or at 0xf (bit 18
  set, 0x07fe0000), or at 0xd with bits 26:21 at 0, 1, 2, 3 or 7, the read is level 0. So
  bit 18 clear alone is not enough (bits 20:17 at 0 read level 0), and the values of bits
  26:21 tried below 0x3f (0, 1, 2, 3, 7) do not read the chain.
- Between levels (mip-mipfilter, minification point): with T0 bit 9 clear LOD 0.25 reads
  level 0, 0.5 and 1.0 and 1.25 level 1, 1.5 and 1.75 level 2, 2.5 level 3, 3.5 and 4.0 and
  4.5 level 4, so the nearest level is the LOD rounded half up. With bit 9 set the top byte
  of the result is the blend of the two levels' tags by the fraction of the LOD: 0xac at
  0.25 (three quarters of 0xd0 and a quarter of 0x40), 0x88 at 0.5, 0x50, 0x60 and 0x70 at
  1.25, 1.5 and 1.75, 0xa0 at 2.5, 0xd8 at 3.5; whole LODs give the level's tag, and 4.0 and
  4.5 give level 4. The whole word at LOD 0.5 is 0x88011477.
- The minification filter (mip-minfilter, a level-1 texel at (2.0, 2.5), magnification point): at
  LOD 1.0 bits 11:10 at 0 and 3 return the texel itself (0x40014040) and at 1 and 2 a blend
  with its neighbour (0x40013040, the x byte 0x30 between 0x20 and 0x40); at LOD 0.25 they
  return level 0's texel for 0 and 3 (0xd0000831) and another value, 0xd0000826, for 1 and 2;
  at LOD 0 all four return 0xd0000831, the magnification filter's value.
- LOD from derivatives (mip-grad): footprints of 1, 2, 4, 8 and 16 texels in both axes read
  levels 0 to 4, 32 texels level 4; 4 texels in one axis and 1 in the other level 2, the
  larger. smp2dbias with constant coordinates reads level 0 for biases -1, 0, 1, 2 and 3.

**Not shown.** What makes bits 20:17 matter (the values that read level 2 have a bit set in
20, 19 or 17, bit 18 clear; 0x0 does not); any non-square or larger chain; the filters' arithmetic
beyond the top byte; a second run.
