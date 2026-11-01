+++
id = "E383"
claim = "SIDEBAND bits 8:6 select the channel only in pack modes 8 and 7: in mode 8 (one byte a pixel) 0 stores alpha, 1 red, 2 green and 3 to 7 blue; in mode 7 (two bytes) 0 stores alpha and red and 1 to 7 green and blue; modes 15, 18 and 28 store green and blue and modes 24 and 25 blue whatever the field; two colours whose bytes all differ, every pixel; sideband bit 12 stores words of no colour in modes 0-6 (the same in both runs) and zeros in modes 7 and 8, and bit 11 faults the job in each of modes 0-8"
unit = "pbe"
method = "probes/pbe/sideband-channels.toml on the laptop over the cable, linux fork b5a86838ae59 with the debug option on: the 64x64 triangle with eot_plain.s and the probe's sideband, pix_colour writing 0xc0804020 and 0x13579bdf (alpha, red, green, blue all different) over the background 0xff203040; bits 8:6 at 0-7 in pack modes 7, 8, 15, 18, 24, 25 and 28 (the two colours, one job each); bit 12 in modes 0-8 twice, bit 11 once; every pixel read back"
tiers = ["HW"]
date = "2026-11-03"
data = ["pbe-sideband-channels"]
terms = ["SIDEBAND.BITS8_6", "SIDEBAND.PACKMODE"]
+++
**Results.** For colour 0xc0804020 (0x13579bdf alike):

| pack mode | bits 8:6 = 0 | 1 | 2 | 3-7 |
|---|---|---|---|---|
| 8 (four pixels a dword) | 0xc0 (alpha) | 0x80 (red) | 0x40 (green) | 0x20 (blue) |
| 7 (two pixels a dword) | 0xc080 (alpha, red) | 0x4020 (green, blue) | the same | the same |
| 15, 18, 28 | 0x4020 at every value | | | |
| 24, 25 | 0x20 at every value | | | |

The background followed the same channels (0xff, 0x20, 0x30, 0x40). So 3 is blue in mode 8, and 4
to 7 read as 3, not as a two-bit field.

Bit 12: modes 0, 1, 2 store 0x0066 and 0x00ff halves (0x00660066 on 1318 dwords), modes 3-6 other
fixed words, the same in both runs; modes 7 and 8 store zeros. Bit 11: every job of modes 0-8
faulted.
