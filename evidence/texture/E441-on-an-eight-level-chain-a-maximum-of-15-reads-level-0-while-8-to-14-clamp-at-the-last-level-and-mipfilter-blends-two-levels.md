+++
id = "E441"
claim = "On a 128x128 twiddled chain of eight levels read at whole LODs 1 to 9, T0 bits 20:17 at 1 to 14 give level = min(round_half_up(LOD), maximum, 7) in 84 of 84 reads (the 14 reads of a maximum of 8 to 14 at LOD 8 and 9 all read level 7, the 1x1 level), and 0 and 15 read level 0 at every LOD (6 of 6 each); bits 26:21 at all 64 values and LOD 5 and 7 give level = max(0, min(round_half_up(LOD + (value - 63) / 8), 7)) in 128 of 128 reads; with T0 bit 9 (MIPFILTER) set the result is the channel-wise linear blend of the texels read at levels floor(LOD + bias) and the next, by the fraction of LOD + bias, byte for byte in 15 of 15 cases (bias values 0x3f, 0x3b and 0x37, LOD 1.25 to 7.5), the same in three runs"
unit = "texture"
method = "probes/texture/mip8-fields.toml (tools/usse-asm/tex_words.py, mip_chain8.s) on the laptop (direct cable), linux fork f1fad0ed9d0e with the debug option on, sgxfive-test probe --scratch-pages 24: the scratch buffer (host-filled, dword i = 0xD0000000 | i) as a 128x128 twiddled RGBA8888 texture of eight levels from its start (T1 0x0C07F07F), smp2dreplace at the coordinates 0.21875 and 0.65625 with T0 and the LOD varied, the result in r10 read as the pixel; texture-mip8-fields-max-level (16 values x 6 LODs), -bias (64 values x LOD 5 and 7, maximum 14) and -mipfilter (3 biases x 5 LODs x 3 runs): 269 reads"
tiers = ["HW", "infer"]
date = "2026-11-07"
data = ["texture-mip8-fields"]
terms = ["T0.MAX_LEVEL", "T0.BITS26_21", "T0.MIPFILTER", "T0.MINFILTER", "T0.MAGFILTER"]
+++

**What runs.** The chain's levels follow each other from the buffer's start (128x128, 64x64 down to
1x1, dword offsets 0, 16384, 20480, 21504, 21760, 21824, 21840 and 21844), so a texel read names its
dword: the level follows from the offset (tex_words.py `mip_of`). T0 is `0x3f << 21 | max << 17`
(bits 26:21 at 0x3f, no bias; point filters) except where the table varies it.

**Results.** Level read at whole LODs (T0 bits 20:17 = max, bias none):

| max | LOD 1 | 3 | 5 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|
| 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| 2 | 1 | 2 | 2 | 2 | 2 | 2 |
| 3 | 1 | 3 | 3 | 3 | 3 | 3 |
| 4 | 1 | 3 | 4 | 4 | 4 | 4 |
| 5 | 1 | 3 | 5 | 5 | 5 | 5 |
| 6 | 1 | 3 | 5 | 6 | 6 | 6 |
| 7 to 14 | 1 | 3 | 5 | 7 | 7 | 7 |
| 15 | 0 | 0 | 0 | 0 | 0 | 0 |

The rows follow the model of E276, level = min(round_half_up(LOD), max), with the level also capped
at the chain's last (7): 70 reads of the 84 for maxima of 1 to 14 need no cap, 14 (a maximum of 8
to 14 at LOD 8 and 9) read level 7 where the model asks for 8 or 9. The bias fits (value -
63) / 8 added to LOD 5 and 7 with the same rounding, 128 of 128 reads, the level also clamped at 0
below. MIPFILTER, three runs of each of 15 cases: the result equals blend(texel(L), texel(L + 1), f)
per byte, L = floor(LOD + bias), f its fraction, texel(L) the nearest read of level L in the first
probe (L + 1 capped at the last level): LOD 1.25, 1.5 and 1.75 and 5.25 at biases 0x3f, 0x3b and
0x37, and LOD 7.5 (the last level twice).

The texel read in a level lies where plain twiddling of the coordinates puts it for levels 3 to 7
(x from 0.65625, y from 0.21875: (10, 3), (5, 1), (2, 0), (1, 0), (0, 0)) and elsewhere for levels
0 to 2 ((20, 108), (10, 46) and (5, 23) read for (84, 28), (42, 14) and (21, 7)): the top bit
of each coordinate does not follow the plain decode, which does not change the level read.

**What it shows.** A maximum of 15 is not a maximum the chain does not reach that falls back to
level 0: 8 to 14, also beyond the chain's seven, read the last level, 15 and 0 read level 0, so 15
(like 0) is itself the no-mipmap value [infer]. The bias holds on eight levels and with levels
past the old chain's five. MIPFILTER is a linear blend between two levels, fraction taken after
the bias. The question's other open part, the chain's size, is answered for a 128x128 square chain.

**What it does not show.** Non-square chains (a 32x16 chain: Q104), linear min or mag filters, and
the position bits above.
