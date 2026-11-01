+++
id = "E281"
claim = "CR_ISP_MSAA mode 1 stores two samples of each pixel side by side in x and mode 2 four in a 2x2 block, samples 0 to 3 of CR_ISP_MULTISAMPLECTL in that order (mode 0 its byte 0 alone); under mode 2 the MTE's multisample word and CR_ISP_SAMPLE_POS do not place them, and mode 1's two from bytes 0 and 1 is read from mode 2 [infer: the mode 0 and 1 probes set both words alike]; the layout, position and TE probes ran once; with CR_ISP_MSAA bit 31 clear nothing of the triangle is stored while the parameter buffer and TA data are byte for byte those of bit 31 set; the TE anti-aliasing bits 31 or 30 without bit 29 remove the triangle"
unit = "isp"
method = "probes/isp/msaa-layout.toml, msaa-positions.toml and msaa-te.toml on the laptop, linux fork with the debug option on: a right triangle whose left and top edges sit at 4 + k/16 (k = 0 to 14 by 2; vtx_affine.s maps the library triangle onto it) under CR_ISP_MSAA (render command word 13) 0x80000000 plus the mode 0, 1, 2, the position words of the render command's words 16 (0x04c8) and 10 (the MTE's) at 0xeaa26e26, without and with the TE anti-aliasing bits (word 1, 0xe0000000); words 16 and 10 told apart and CR_ISP_SAMPLE_POS (rd:19) at another word under mode 2; modes 1 and 2 with bit 31 clear and set on the library triangle, the render memory dumped, twice (the only probes run twice); the TE bits one and more at a time under modes 0-2; every pixel read back and fitted by isp_words.py layout --joint"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["isp-msaa-layout", "isp-msaa-positions", "isp-msaa-te"]
terms = ["CR_ISP_MSAA", "CR_ISP_MSAA.MODE", "CR_ISP_MSAA.ENABLE", "CR_ISP_MULTISAMPLECTL", "CR_ISP_MULTISAMPLECTL.SAMPLE1_X", "CR_ISP_MULTISAMPLECTL.SAMPLE1_Y", "CR_ISP_MULTISAMPLECTL.SAMPLE2_X", "CR_ISP_MULTISAMPLECTL.SAMPLE2_Y", "CR_ISP_MULTISAMPLECTL.SAMPLE3_X", "CR_ISP_MULTISAMPLECTL.SAMPLE3_Y", "CR_ISP_SAMPLE_POS", "CR_TE_AA"]
+++

**What runs.** The triangle has a vertical left edge and a horizontal top edge at 4 + k/16 pixels
and legs 10 pixels long, so each sample's x and y position decide which column and row of the corner
it covers. The fitter takes each mode's eight images at once and, for each layout of the stored
samples (1x1, 2x1, 1x2, 2x2, 4x1, 1x4 target pixels a pixel), finds for each slot the sample
positions that miss fewest pixels over all eight. Each probe ran once, but for the bit-31 probes,
which ran twice. The triangle lies inside the target's first 16x16 tile, and a multisampled image is
stored only inside that tile (below), so each image is read there.

**Results.**

| mode | best layout | slots, in sixteenths (x, y), within 1/16 | pixels missed |
|---|---|---|---|
| 0 | 1x1 | (6-7, 2-3) | 0 of 8 x 256 |
| 1 | 2x1 | (6-7, 2-3), (14-15, 6-7) | 0 |
| 2 | 2x2 | (6-7, 2-3), (14-15, 6-7), (2-3, 10-11), (10-11, 14-15) | 0 |

The next layout misses 371 (mode 0), 423 (mode 1, 2x2) and 406 (mode 2, 2x1) pixels. The word
0xeaa26e26 places samples 0 to 3 at (6, 2), (14, 6), (2, 10) and (10, 14). The mode 0 and mode 1
probes set words 16 and 10 both to that word, so they do not tell the two apart. Mode 2 with word 16
at 0xeaa26e26 and word 10 at 0x88888888 gives the same four slots; with word 16 at 0x88888888 and
word 10 at 0xeaa26e26 every slot sits at (8-9, 8-9); with word 16 at 0x2e62a6ea the slots move to
(10, 14), (6, 10), (2, 6), (14, 2), that word's bytes 0 to 3; with 0x0520 at 0x2e62a6ea they stay.

In mode 2 the stored image is the triangle's 2x2 sample image cut at x 16 and y 16 (an 8x8
block from (8, 8) of green), in mode 1 the 2x1 image cut at x 16. With the TE bits (0xe0000000)
none of the small triangle is stored in any mode. On the library triangle the stored images of
modes 1 and 2 (868 and 896 pixels, both runs) are not the 2x1 and 2x2 images inside the tiles
the triangle meets: they are cut to whole 16x16 tiles and shifted (580 and 1248 pixels apart).

With bit 31 clear (`isp-msaa-layout-enable-m1-b310`, `-m2-b310`, both runs) the target holds only
the background; set, 868 (mode 1) and 896 (mode 2) triangle pixels. The four dumps of each run
(mode 1 and 2, bit 31 clear and set) have the same parameter buffer and the same TA data, byte for
byte.

The TE bits on the library triangle, triangle pixels in modes 0, 1 and 2 (`isp-msaa-te` has no case
without TE bits; the mode 0 baseline, 1086, is the single sample at (6, 2) of E278's coverage model,
and the mode 1 and 2 baselines, 868 and 896, are the bit-31 probes'):

| TE word | 0x80000000 | 0x40000000 | 0x20000000 | 0xc0000000 | 0xa0000000 | 0x60000000 | 0xe0000000 |
|---|---|---|---|---|---|---|---|
| mode 0 | 0 | 0 | 1086 | 0 | 1002 | 1086 | 916 |
| mode 1 | 0 | 0 | 868 | 0 | 1276 | 868 | 1260 |
| mode 2 | 0 | 0 | 896 | 0 | 1312 | 832 | 1248 |

**What it shows.** `CR_ISP_MSAA.MODE` 1 is two samples a pixel stored side by side in x and 2 is
four stored as a 2x2 block, each pixel's samples taken from `CR_ISP_MULTISAMPLECTL` in byte order:
mode 1 reads bytes 0 and 1, mode 2 all four, so bytes 1 to 3 hold samples 1 to 3 laid out as byte 0.
This answers what each mode stores (Q030). Under mode 2 the MTE's position word and
`CR_ISP_SAMPLE_POS` do not place the stored samples; that mode 1 takes its two from
`CR_ISP_MULTISAMPLECTL` and not from the MTE's word is read from mode 2 [infer]. Bit 31 acts after
tiling: the TA's output is the same with it clear, and only the stored image loses the triangle
(`CR_ISP_MSAA.ENABLE`). The stored image is a sample image tile by tile, the first 16x16 tile in
place; how the tiles past the first land in the target, and what the TE bits do (bit 31 or 30
without bit 29 removes the triangle, bit 29 alone gives each mode's baseline), are not shown [infer:
the fitter reads the first tile only].
