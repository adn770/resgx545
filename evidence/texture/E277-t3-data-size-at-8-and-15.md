+++
id = "E277"
claim = "With two fetches in a primary program, T3 bits 26:23 of the first at 8 put the second texel in pa8 and at 15 in pa15, as the control at 1 puts it in pa1, image for image; with the first fetch as f32 channels and the field at 8 the second texel is again in pa8 and pa1 holds the first fetch's 0.0"
unit = "texture"
method = "probes/texture/fetch-size.toml on the laptop, linux fork with the debug option on, and its follow-up run: the triangle job's primary pixel program pds_tex2.s with DOUTI0 0x06012201 and 0x46012201, the first T3 0x800 | field << 23 (and conversion 3 at field 8), pa1, pa8 and pa15 read back through pix_pa1.s, pix_pa8.s and pix_pa15.s"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["texture-fetch-size", "texture-fetch-size-followup"]
terms = ["T3.DATA_SIZE", "T3.CONVERT"]
+++

**What runs.** E242 found the second fetch's texel in the primary attribute the first fetch's
field numbers, for 0 to 4 and 6, and left 8 and 15 untried. The reference image is the second
texel in pa1 with the field at 1 (1062 triangle pixels, each a dword 0xd0001000 | i of the second
texture, read as the fetch swizzles it).

**Results**, triangle pixels equal to the reference image, of 1062:

| first fetch | pa1 | pa8 | pa15 |
|---|---|---|---|
| field 1 | 1062 | 238 | 288 |
| field 8 | 223 | 1062 | 278 |
| field 15 | 314 | 365 | 1062 |
| f32 channels, field 8 | 0 (0.0) | 1062 | 236 |

The registers that do not hold the second texel hold second-texture values of other pixels, 223
to 365 of them coinciding with the reference: values left from the earlier cases **[infer]**.
The follow-up run gave the same reading: the same reference image, the second texel in pa8 and
pa15 at all 1062 pixels, pa1 at 0.0; the leftover registers differ from the first run's.

**What it shows.** The field places the next fetch's result at that primary attribute up to 15:
it is the size, in dwords, of a fetch's result in the attribute file **[infer]**.
