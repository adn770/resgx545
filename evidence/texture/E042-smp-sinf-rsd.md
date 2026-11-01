+++
id = "E042"
claim = "smp.sinf returns no texel: its first register is 0 and its second the level, and with the mip filter linear the first holds the blend fraction between the two levels in bits 23:16 (0x41, 0x82 and 0xc3 for a quarter, a half and three quarters: a six-bit fraction with its top two bits repeated below it) and the second the lower level; smp.rsd returns the same texel as the plain sample under point filtering, and under linear filtering at LOD 1.5, where the plain sample returns one blended word, eight registers: four texels of level 1 and four of level 2, the 2x2 footprint of each level, without filtering"
unit = "texture"
method = "probe texture-sampler-smp-srd (15 cases) of probes/texture/sampler.toml on the laptop, linux fork with the debug option on: smp2d and smp2dreplace with the .sinf and .rsd modes over the tagged five-level chain of E041, with T0 bit 9 clear and set and the magnification and minification filters linear in the last two cases; registers r10 to r17 read back; one run"
tiers = ["HW", "infer"]
date = "2026-11-01"
data = ["texture-sampler"]
terms = ["T0.MIPFILTER", "T0.MINFILTER", "T0.MAGFILTER"]
+++

**What runs.** The probe host of E033 over the mip chain of E041, each level tagged. Each case runs
one `smp` variant and prints the eight registers from r10 (the destination) on; registers the sample
does not write read as the sentinel the case wrote first (0xa4a5a6a7, 0xa8a9aaab and so on).

**Results.**

- Control, smp2dreplace at LOD 1.0: r10 is 0x400120a0, a level 1 texel.
- `.sinf`, mip filter off (T0 bit 9 clear): r10 is 0 and r11 the level, 1 for LOD 0.5, 1
  for LOD 1.0, 2 for 2.0, 3 for 2.75, 4 for 4.0 and 4 for 6.0 (the nearest level, a half
  rounding up, clamped to the last); smp2d without a LOD operand gives r11 = 0. No other
  register is written.
- `.sinf`, mip filter linear: r10 is 0x00410000, 0x00820000 and 0x00c30000 for LOD 0.25, 1.5
  and 2.75, and r11 is 0, 1 and 2, the lower of the two levels. Bits 23:16 hold the fraction
  of the LOD between the levels: a quarter as 0x41, a half as 0x82, three quarters as 0xc3.
  A six-bit fraction of 010000, 100000 or 110000 with its top two bits repeated below it
  (01000001, 10000010, 11000011) gives these; that reading is an inference **[infer]**, as
  the fractions 0.25, 0.5 and 0.75 are the only three tried.
- `.rsd`, point filtering: smp2dreplace at LOD 1.0 returns the same r10, 0x400120a0, as the
  plain sample and writes no other register; smp2d.rsd without a LOD returns level 0's
  texel, 0xd000084e.
- `.rsd`, mip, magnification and minification filters linear, LOD 1.5: the plain sample
  returns the one value 0x60021a6e in r10. The `.rsd` sample writes eight registers:
  r10 to r13 = 0x40012080, 0x40014080, 0x400120a0, 0x400140a0 (four texels of level 1, tag
  0x40) and r14 to r17 = 0x80020040, 0x80022040, 0x80020060, 0x80022060 (four of level 2, tag
  0x80): the 2x2 footprint of each level, in place of their blend.

**Not shown.** The fractions between 0 and 1 other than the three; `.sinf` and `.rsd` under
other state or formats; the order of the four texels (two columns, two rows) is read from the
values only.
