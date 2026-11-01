+++
id = "E274"
claim = "In a copy, T3 bits 3:0 and 7:4 offset the texel read in y and in x by a signed 4-bit count (1, 2, 4 and -8 for each single bit), clamped at the source's edge; T3 bit 10 reads texel (0, 0) for every pixel; bits 18 and 19 scale the coordinates by 2 and 4; bits 27 and 28 read half-size and quarter-size images packed after the source; bit 14 reads (x + 32, y + x); bits 13 and 19 fault; T0 bits 27 and 30 change every pixel to values of no texel; T0 bits 2:0, 16:14, 28 and 29 and T3 bits 8, 9, 11, 12 and 20 to 22 change no pixel, over both sources; one run"
unit = "texture"
method = "probes/texture/sampler-bits.toml on the laptop, linux fork with the debug option on: the sweeps texture-sampler-bits-copy and -copy-every, every bit of the 64x32 copy's T0, T1 and T3 flipped and each word at 0 and 0xffffffff (103 cases a source), with --pixels; each changed image matched texel by texel to the plain source pattern; one run, no follow-up"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["texture-sampler-bits"]
terms = ["T0.STRIDE", "T3.CMP_MODE", "T3.DATA_SIZE", "T3.CONVERT", "T3.NORMALIZE", "T3.BITS7_0", "T3.BIT10", "T3.BIT14", "T3.BITS19_18", "T3.BITS28_27", "T0.BIT27", "T0.BIT30"]
+++

**What runs.** The copy's words are T0 0x000e0e00 (a stride of 64 dwords), T1 0xcc03f01f
(strided, TEXFORMAT 12, 64 x 32), T2 the source and T3 0xa0800000. E036 had the flips of T2;
E039 the hashes of T0, T1 and T3 against the luma-key words, without the pixels. Here every case
keeps the pixels, and each changed image of the plain source is matched to the texel each pixel
holds (the pattern names its texel; rows past the source continue it).

**Results**, the bits no field covered before (pixels changed of 2048, plain source; the every-
value source changes as many or a few fewer, where its texels repeat):

| bit | image |
|---|---|
| T3 0, 1, 2 | texel (x, y + 1), (x, y + 2), (x, y + 4), the last rows clamped: 1984 each |
| T3 3 | texel (x, y - 8), the first rows clamped |
| T3 4, 5, 6 | texel (x + 1, y), (x + 2, y), (x + 4, y), the last columns clamped |
| T3 7 | texel (x - 8, y) |
| T3 10 | texel (0, 0) at every pixel: 2047 |
| T3 14 | texel (x + 32, y + x), 903 pixels past the source at the sentinel |
| T3 18 | texel (2x, 2y); 168 pixels past the buffers at the sentinel |
| T3 19 | texel (4x, 4y) for the pixels within the source, then the job faults |
| T3 27 | texel (x / 2, 32 + y / 2): a half-size image after the 32 rows of the source |
| T3 28 | texel (x / 4, 40 + y / 4) |
| T3 13 | the job faults, nothing written |
| T0 27 | every pixel a value of no texel (0x00000000, 0x0cf90cf9, 0x10f910f9, ...) |
| T0 30 | every pixel a value of no texel (0x7f000000, 0x7f040000, ...): 2048 |
| T0 0-2, 14-16, 28, 29 | no pixel changes |
| T3 8, 9, 11, 12, 20-22 | no pixel changes |

The bits with fields behave as their rows have it in a copy: T3 bits 29-31 (`T3.CMP_MODE`), 23-26
(`T3.DATA_SIZE`, one fetch) and 15 (`T3.NORMALIZE`, no conversion) change no pixel; bits 16 and
17 (`T3.CONVERT`) change every pixel; T0 bits 9-11 and 17-26 move the rows (`T0.STRIDE`), and T0
bits 22 to 26 fault.

**What it shows.** T3 bits 7:0 are a texel offset, x in 7:4 and y in 3:0, each a signed 4-bit
count applied before the clamp **[infer]** (only single bits were set). Bits 18 and 19, 27 and
28 select a scale of the coordinates and a smaller image packed after the source, the way a mip
level of a strided texture would be read **[infer]**; the stride of those images is the
source's. Bit 10's single texel, bit 14's sheared read and T0 bit 27's values are not decoded
(Q078); T0 bit 30's are not either (with TEXFORMAT 26 it reads one byte per texel, E040). The
sweeps ran once, with no follow-up run.
