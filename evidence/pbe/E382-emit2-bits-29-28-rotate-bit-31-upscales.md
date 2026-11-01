+++
id = "E382"
claim = "With a shader that names each pixel, EMIT2 bits 29:28 rotate the stored image by 90, 180 and 270 degrees at 1, 2 and 3 (the pixel stored at (X, Y) of the 64x64 target is the one from (Y, 63 - X), (63 - X, 63 - Y) and (63 - Y, X)), every one of the 1062 pixels in both runs, so E267's bit 28 is a rotation by 90 degrees, not a mirror; bit 31 scales by two (the pixel at (X, Y) is the one from (X/2, Y/2), after the rotation of bits 29:28 for 0x9-0xb, all 1728 named pixels); bits 30 and 31:30 together store no named pixel; EMIT2 bits 6:0 are fit by an offset into the order in which a tile's pixels are read [infer], an offset of 1 reading the next pixel of the order x0, y0, x1, x2, x3, y1, y2 of each 16x8 block [infer] (1, 2, 4, 8 and 16 fit 928-1053 of about 1050 pixels, 3 fits 1035; carries out of the block do not); counts above 0x80 (0x82-0xfe) store the image with 39 to 2742 pixels changed, mostly at the first places of each tile's order"
unit = "pbe"
method = "probes/pbe/emit-transforms.toml (pbe_words.py table --phase 11.14) on the laptop over the cable, linux fork b5a86838ae59 with the debug option on: the 64x64 triangle with eot_words.s in the end-of-tile slot setting one EMIT2 field per case, pds_iter_xy.s iterating each pixel's x + 0.5 and y + 0.5 into pa0, pa1 and pix_xy.s storing (pa0 & 0xffff0000) | (pa1 >> 16), which names its pixel; bits 31:28 at all 16 values, bits 6:0 at 1, 2, 3, 4, 8, 16, 32, 64 and 127, bits 15:8 at 0x82, 0x84, 0x90, 0xc0, 0xfe; two runs; pbe_words.py place fits each image"
tiers = ["HW", "infer"]
date = "2026-11-03"
data = ["pbe-emit-transforms"]
terms = ["EMIT2.BIT28", "EMIT2.BIT29", "EMIT2.BIT30", "EMIT2.BITS15_8"]
+++
**Results.** Both runs gave the same fits.

| EMIT2 bits 31:28 | where the pixel from (x, y) is stored | pixels |
|---|---|---|
| 0x0 | (x, y) | 1062 of 1062 |
| 0x1 | (63 - y, x): 90 degrees | 1062 |
| 0x2 | (63 - x, 63 - y): 180 degrees | 1062 |
| 0x3 | (y, 63 - x): 270 degrees | 1062 |
| 0x4-0x7, 0xc-0xf | no stored word names a pixel; 1024 dwords written | - |
| 0x8 | (2x, 2y) and its three neighbours | 1728 named |
| 0x9-0xb | the rotation of 0x1-0x3, then the scale by two | 1728 |

Bits 6:0 = 1, 2, 4, 8, 16 fit a read moved by that many pixels of the order (x0, y0, x1, x2,
x3, y1, y2; the order is a fit [infer]) within each 16x8 block: 1053, 1044, 1026, 992 and 928 of
the named pixels fit; 3 fits 1035; 32 and 64 fit 798 and 530, the misfits lying where the offset
carries out of a 16x8 block (their source 32 columns left); 127 fits 8.

**Not shown.** Where a carry out of a 16x8 block goes; what the counts above 0x80 store; bit 30's
averaging with a named image (E267's box average stands).
