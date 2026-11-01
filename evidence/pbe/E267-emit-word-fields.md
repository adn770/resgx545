+++
id = "E267"
claim = "The end-of-tile emit stores only the pixels inside the rectangle EMIT0 (minimum x in bits 12:0, y in 28:16) and EMIT1 (maximum x and y, inclusive) give; EMIT3 is a byte address whose bits 1:0 are ignored; EMIT2 bits 27:16 give the row pitch as (value + 1) x 8 bytes; bits 15:13 and 31:29 of EMIT0 and EMIT1 are ignored but EMIT1 bit 31, which hangs the job; EMIT2 bits 6:0 and 31:28 change the image and bit 7 does not: bit 28 stores the image mirrored in x, bit 29 rotated by 180 degrees (or anti-transposed; this image does not tell them apart), bit 30 each 32x16 tile's 2x2 box average into the tile's top-left 16x8 pixels, and bit 31 a triangle of another shape in the same two colours"
unit = "pbe"
method = "the probes pbe-emit-words-fields and pbe-emit-words-followup-fields of probes/pbe/emit-words.toml and emit-words-followup.toml on the laptop, linux fork with the debug option on: the 64x64 triangle with eot_words.s in the end-of-tile slot, which sets r = r & AND | OR on one of the PBE words r0-r3 before the emits, pix_colour.s writing 0x00ff8040 over the background 0xff203040; 61 cases, every pixel read back, each compared with the case that leaves the words as built"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["pbe-emit-words", "pbe-emit-words-followup"]
terms = ["EMIT0.MINCLIP_X", "EMIT0.MINCLIP_Y", "EMIT1.MAXCLIP_X", "EMIT1.MAXCLIP_Y", "EMIT2.LINE_STRIDE", "EMIT3.ADDRESS", "EMIT2.BITS15_8", "EMIT2.BIT28", "EMIT2.BIT29", "EMIT2.BIT30"]
+++

**What runs.** The library builds the four PBE words of a W x H ARGB8888 target at address A as
EMIT0 = 0, EMIT1 = (W - 1) | (H - 1) << 16, EMIT2 = 0x8000 | (4W / 8 - 1) << 16 and EMIT3 = A
(fw_format.md §9.6); for 64x64 EMIT1 is 0x003f003f and EMIT2 0x001f8000. Each case replaces one
field or flips one bit outside the fields of one word, in the end-of-tile program, after the
host has loaded the words. The base case writes the plain image: 3034 background pixels and 1062
of the triangle colour, every pixel written.

**Results.** Both runs agree on every case but EMIT2 bits 1, 2, 3, 5 and 6, whose images differ
between the runs in 2 to 95 pixels (the values of no colour below); bit 4's agree.

| case | image |
|---|---|
| EMIT0 = 8, 0 / 0, 8 / 8, 8 | only x 8-63 / y 8-63 / both written, those pixels as the base |
| EMIT0 = 32, 16 / 40, 24 | only x 32-63, y 16-63 / x 40-63, y 24-63 |
| EMIT1 = 31, 63 / 63, 31 | only x 0-31 / y 0-31 written |
| EMIT1 = 40, 40 / 15, 15 | only x 0-40, y 0-40 (1681 pixels) / x 0-15, y 0-15 (256) |
| EMIT3 + 4 / + 0x40 / + 0x100 | the image moved 1 pixel right / 16 right / 1 row down |
| EMIT3 bit 0, bit 1 | the base image |
| EMIT2 bits 27:16 = 63 | row y lands on row 2y; the odd rows keep the sentinel (2048) |
| EMIT2 bits 27:16 = 15 | row y starts 128 bytes after row y - 1: 2016 unwritten |
| EMIT2 bits 27:16 = 0 | rows land 8 bytes apart: rows 0-2 written (190 pixels) |
| EMIT0, EMIT1 bits 13, 14, 15, 29, 30 | the base image |
| EMIT0 bit 31 | the base image |
| EMIT1 bit 31 | the job hangs, the context is lost |
| EMIT2 bit 7 | the base image |
| EMIT2 bits 0 to 6 | 140 to 1404 differ: colours moved, and values of no colour (below) |
| EMIT2 bits 28, 29 | 752 and 956 pixels differ: the same 3034 and 1062 values at other places |
| EMIT2 bit 30 | 1024 written, 16 in each half of rows 0-7, 16-23, 32-39, 48-55; 42 of no colour |
| EMIT2 bit 31 | every pixel written, 1650 differ: 2368 background and 1728 triangle pixels |

The values of no colour that EMIT2 bits 0 to 6 bring are words of the end-of-tile task's own
registers and of other programs: with bit 0, 0x00000000 in 8 pixels; with bit 1, also
0x003f003f (EMIT1, r1) in 8; with bit 2, 0x001f8004 (EMIT2 as the case set it, r2) and
0x3e001000 (EMIT3, the target's address, r3); with bits 4 to 6, dozens of other words, among
them 0xa4a5a6a7, 0xb0b1b2b3 and 0xb4b5b6b7, the presets the probe template dump.s writes to
r11, r14 and r15 in other jobs. So the PBE reads the tile's colours from a place in the USSE
register store that these bits move, and a larger offset reaches registers that are not the
tile's outputs **[infer]**.

EMIT2 bits 28 to 30, read pixel by pixel against the base image B, in both runs:

- Bit 28: pixel (x, y) holds B(63 - x, y) at all 4096 pixels, the image mirrored in x.
- Bit 29: pixel (x, y) holds B(63 - x, 63 - y) at all 4096, the image rotated by 180 degrees.
- Bit 30: in each 32x16 tile, pixel (i, j) of the top-left 16x8 holds the average of the tile's
  pixels (2i, 2j), (2i + 1, 2j), (2i, 2j + 1) and (2i + 1, 2j + 1), each byte summed and divided
  by 4, the remainder dropped: 1024 of 1024 pixels; the rest of the tile keeps the sentinel. The
  42 pixels of no colour are these averages where a box holds both colours (0x7f8f5840 two of
  each, 0xbf574440 three of the background and one of the triangle).
- Bit 31: only the two colours, at 2368 and 1728 pixels, in a triangle of another shape; no
  mirror, rotation, transpose or per-tile rearrangement of the base gives it.

The triangle is symmetric about its diagonal x = y (B(x, y) = B(y, x) at every pixel), so a
transform and the same transform after a transpose give one image here: bit 29's image is also
the anti-transpose B(63 - y, 63 - x), and bit 28's also the rotation by 90 degrees B(y, 63 - x).
These readings are told apart only by an image without that symmetry **[infer]**.

Where the clip leaves pixels, they hold the base image's values, and the job completes; the clip
is therefore not a scissor of what the tile computes but of what the PBE stores **[infer]**. The
moved images (EMIT3) leave their first row or column at the sentinel and write their last into
the area after the target.

**What it shows.** EMIT0 and EMIT1 are an inclusive store rectangle, x in bits 12:0 and y in
28:16, the bits around them read by nothing seen but EMIT1 bit 31; EMIT3 bits 31:2 are the
address of pixel (0, 0); EMIT2 bits 27:16 + 1 is the row pitch in 8-byte units, as fw_format.md
§9.6 writes it. EMIT2 bits 6:0 move where the colours are read from [infer]. Bits 28 and 29
fit a flip and a rotation of the stored image, and bit 30 a 2x2 box downscale of each tile, by
these images alone **[infer]**; they are named EMIT2.BIT28 to EMIT2.BIT30 for now. The old
glossary reading of SIDEBAND bits 8:6 as a downscale, rotation or flip field, by analogy with
Rogue's downscale and AGX's rotate and flip, finds its functions here in EMIT2, not in the
sideband (E269). Bit 31 is not decoded (Q040).
