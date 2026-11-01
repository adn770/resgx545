+++
id = "E034"
claim = "T3 bits 17:16 convert the fetched texel on the laptop (1 gives 10-bit fields, 2 half-float pairs, 3 one single float per channel) and, with conversion 3, T3 bit 15 divides the converted values by 255 (65535 for a 16-bit channel); the bit was not run with conversions 1 and 2"
unit = "texture"
method = "probes/texture/sampler.toml, texture-sampler-smp-convert (48 cases), on the laptop, linux fork with the debug option on: one smp2d per case over a 16x16 counting texture, T3 conversion 1, 2 or 3 (and 3 with bit 15), formats 12, 13, 5, 0, 7 and 9 at two texels each, one run"
tiers = ["HW"]
date = "2026-11-01"
data = ["texture-sampler"]
terms = ["T3.CONVERT", "T3.NORMALIZE", "T3.DATA_SIZE", "T1.TEXFORMAT"]
+++

**What runs.** The same probe host as E033: the four state words and the coordinate are built in
registers, one `smp2d` runs, and the result registers are read back with the registers after
them. The texture's dword i holds 0xd0000400 | i. For format 12 the texel (15, 15) is the
dword 0xd00004ff: bytes 0xff, 0x04, 0x00, 0xd0 from the low byte up. The cases fix the format,
the conversion field of T3 (bits 17:16) and bit 15, and change the texel.

**Results**, format 12, texel (15, 15):

- Conversion 1: register 0 is 0x000010ff and register 1 is 0x000000d0. In register 0 the
  10-bit fields (bits 9:0, 19:10, 29:20) hold 255, 4 and 0, the byte values unscaled, and
  register 1 the byte 0xd0 (208): the bytes in the order of the dword, low byte first, the
  last byte in the second register.
- Conversion 2: register 0 is 0x44000000 and register 1 is 0x5a805bf8: half floats in pairs,
  low half first. Register 0 holds the third byte (0.0) then the second (4.0), register 1 the
  first (255.0 as 0x5bf8) then the fourth (208.0 as 0x5a80).
- Conversion 3: four registers, 255.0 (0x437f0000), 4.0 (0x40800000), 0.0 and 208.0
  (0x43500000): one single float per channel, first byte first, the integer values.
- Conversion 3 with bit 15: 1.0 (0x3f800000), 4/255 (0x3c808081), 0.0 and 208/255
  (0x3f50d0d1): each value divided by 255. The same at texel (2, 5): 82.0 (0x42a40000)
  becomes 82/255 (0x3ea4a4a5).
- Format 13 (red and blue swapped): the same values with the first and third channels
  exchanged (conversion 1: 0x0ff01000, then 0xd0).
- Format 5 has no alpha channel here: with conversions 1 and 3 the register that would hold
  alpha is left as the sentinel the case wrote (0xa4a5a6a7 for conversion 1, 0xacadaeaf for
  conversion 3, the last of four), and conversion 2 returns 1.0 (0x3c00) in the high half of
  register 1, normalized or not.
- Formats 0, 7 and 9 (one byte, two bytes, one 16-bit channel): conversion 1 returns the
  value in the low field of register 0 (0xd0 for format 0 at (15, 15)), conversion 2 a half
  float (0x5a80 = 208.0) and conversion 3 a single float (0x43500000 = 208.0); format 7
  returns two channels, low byte first, in two fields, halves or registers. For the 16-bit
  channel of format 9 conversion 3 gives 53248.0 (0x47500000) and with bit 15
  0x3f5000d0, which is 53248/65535.

**Not shown.** Bit 15 with conversions 1 and 2; any other T3 field; the formats beyond these
six. Which byte of a texel is which colour is read from the order of the bytes only.
