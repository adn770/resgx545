+++
id = "E385"
claim = "The low byte of the word that loads CR_REG_0400 is the threshold of the one-bit alpha of pack mode 4 (ARGB1555): with an alpha that varies over x, the stored alpha bit is set where the alpha is above the low byte and clear where it is below (low byte 0: set from 2 up; 0x40: clear to 62, set from 66; 0x80: clear to 120, set from 132; 0xc0: clear to 188, set from 196; 0xff: clear everywhere), every triangle pixel in both runs; bits 8-11 change nothing in modes 0 and 4 and bits 7:0 nothing in mode 0; bit 25 inverts the alpha in modes 4 and 5 (all 2048 dwords) and changes nothing in mode 8"
unit = "pbe"
method = "probes/pbe/reg-0400-alpha.toml on the laptop over the cable, linux fork b5a86838ae59 with the debug option on: the 64x64 triangle, pds_iter_xy.s and a shader whose alpha is bits 23:16 of x + 0.5 as a single (64 values from 0 to 252 over the columns) with 0x00ff8040, eot_plain.s, the render command's word 11 (it loads CR_REG_0400) at 0x80, low byte 0, 0x40, 0xc0, 0xff, bits 8, 9, 10, 11 set, in pack modes 0 and 4, and bit 25 against 0x80 in modes 4, 5 and 8; two runs; every pixel read back"
tiers = ["HW"]
date = "2026-11-03"
data = ["pbe-reg-0400-alpha"]
terms = ["CR_REG_0400", "CR_REG_0400.INVERT_BYTE3", "SIDEBAND.PACKMODE"]
+++
**Results.** Mode 0 stored the ramp's alpha at all 1062 triangle pixels under every value, both
runs. Mode 4 (two pixels a dword, the alpha in bit 15 of each half), at the triangle's pixels:

| low byte | alpha bit 0 for alpha up to | alpha bit 1 from |
|---|---|---|
| 0x00 | (none) | 2 |
| 0x40 | 62 | 66 |
| 0x80 (as built; and with bit 8, 9, 10 or 11 set) | 120 | 132 |
| 0xc0 | 188 | 196 |
| 0xff | 252 | (none) |

No pixel had an alpha equal to the low byte, so whether equal sets the bit is not shown.
