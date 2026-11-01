+++
id = "E276"
claim = "On a twiddled mip chain T0 bits 20:17 are the highest level read (0 and 15 read level 0 only, 1 to 14 cap the level at that value) and bits 26:21 shift the LOD by (value - 63) / 8 before the nearest level is taken: level = max(0, min(round_half_up(LOD + (b - 63) / 8), max)) fits every one of 192 reads, in both runs, a biased LOD below 0 reading level 0; bit 18 alone does not disable the chain"
unit = "texture"
method = "probes/texture/mip-fields.toml (texture-mip-fields-bits20-17: all 16 values at LOD 1, 2, 3, 4 with bits 26:21 at 0x3f; texture-mip-fields-bits26-21: all 64 values at LOD 2 and 4 with bits 20:17 at 0xd) on the laptop, linux fork with the debug option on, and its follow-up run: mip_chain.s, the tagged 16x16 chain of five levels of mipmaps.toml read by smp2dreplace, the level named by the top byte of the result"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["texture-mip-fields", "texture-mip-fields-followup"]
terms = ["T0.NO_MIPMAPS", "T0.BITS26_21", "T0.BITS20_19", "T0.MAX_LEVEL", "MIPMAPS_PRESENT"]
+++

**What runs.** E041's probe reads LOD 2.0 of a 16x16 twiddled texture whose levels 0 to 4 follow
it, tagged 0xd0, 0x40, 0x80, 0xc0 and 0xf0 in the top byte; with T0 0x07fa0000 (bits 26:21 0x3f,
20:17 0xd) it reads level 2, and six other values gave level 0. Here every value of each field
runs at several LODs.

**Results.** Level read, bits 20:17 (bits 26:21 at 0x3f), LOD 1, 2, 3, 4:

| 20:17 | levels | 20:17 | levels |
|---|---|---|---|
| 0x0 | 0, 0, 0, 0 | 0x3 | 1, 2, 3, 3 |
| 0x1 | 1, 1, 1, 1 | 0x4 to 0xe | 1, 2, 3, 4 |
| 0x2 | 1, 2, 2, 2 | 0xf | 0, 0, 0, 0 |

Bits 26:21 (bits 20:17 at 0xd), LOD 2 and 4: 0x00 to 0x22 read level 0 at both; 0x23 to 0x2a
level 0 and 1; 0x2b to 0x32 level 0 and 2; 0x33 to 0x3a level 1 and 3; 0x3b to 0x3f level 2 and
4. Values 0x00 to 0x22 put the biased LOD below 0 at LOD 2 (-5.9 to -1.6), and level 0 is
read. The model above, with its floor at 0, gives all 64 + 128 reads; the follow-up run gave the
same 192. No case asks for a level past the chain's last (4): LOD 4 without bias is the highest
read.

**What it shows.** Bits 20:17 are a maximum level: E041's six values (0xd, 0xc, 0x9, 0x5 read
level 2; 0x0 and 0xf level 0) are its 0, its 15 and values of 2 or more, and bit 18 is not a
mipmap disable (0x2 and 0x6 read the chain). 0 and 15 both keep level 0, which fits 15 marking
a texture without mipmaps **[infer]**. Bits 26:21 are an LOD bias in eighths with 63 as no bias,
and a biased LOD below 0 reads level 0; how they read between levels with linear filtering, and
a level asked past the chain's last, are not run. On a strided texture the same bits are T0's
stride, so the fields hold for twiddled ones.
