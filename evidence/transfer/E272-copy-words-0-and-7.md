+++
id = "E272"
claim = "With the copy's transfer word 0 (the background object tag) at 0 or with bit 24 or bit 30 flipped, every pixel of the 64x32 copy is the source's last texel (63, 31), over both sources; with word 7 (the word that loads CR_ISP_MSAA) bit 1 flipped, mode 2, only the first 32x16 tile is written, pixel (x, y) holding texel (16 + x / 2, 8 + y / 2), and the other 1536 pixels keep the sentinel"
unit = "transfer"
method = "the hand-run script of probes/texture/copy-words.toml (section xfer-0-7) on the laptop, linux fork with the debug option on: the 64x32 copy over the plain and the every-value source with xfer:0 bit 24, bit 30 or 0, and xfer:7 bit 1; two rounds, every pixel read back and matched to the source texels"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["texture-copy-words"]
terms = ["transfer_cmd", "transfer_cmd.isp_background_tag", "transfer_cmd.isp_msaa", "CR_ISP_MSAA.MODE"]
+++

**What runs.** E028 counted 2047 and 2040 changed pixels for word 0's flips and 2047 and 2044
for word 7 bit 1, over the plain and the every-value source, without the pixels. The library
writes word 0 as the background object's offset in 16-byte units with the layer count (1 for a
copy) in bits 30:25, and word 7, the word that loads `CR_ISP_MSAA`, as 0x80000000 (mode 0).

**Results**, both rounds alike:

- Word 0 with bit 24 flipped, bit 30 flipped or at 0: every pixel holds 0xa51f3f20 over the
  plain source, the texel at x 63, y 31, and 0xff6648dc over the every-value source, the same
  texel. So the 1 pixel (plain) and 8 pixels (every-value) E028 found unchanged are the pixels
  whose own texel equals the last one.
- Word 7 bit 1: 512 pixels written, those of x 0-31 and y 0-15; pixel (x, y) holds the texel at
  (16 + floor(x / 2), 8 + floor(y / 2)), the source enlarged twice about its centre; 1536
  pixels keep 0xdeadbeef. The every-value source gives the same placement.

**What it shows.** A copy whose tag no longer names its one-layer background object reads one
texel for every pixel, the coordinates of the last vertex **[infer]**: no per-pixel function of
the value. Word 7 bit 1 is `CR_ISP_MSAA` mode 2, which E210 reads as four samples a pixel: the
copy's one tile then holds the samples of a 16x8 area, stored as 32x16 pixels without a
downsample **[infer]**; only that tile lands.
