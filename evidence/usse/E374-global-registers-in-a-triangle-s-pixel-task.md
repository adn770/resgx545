+++
id = "E374"
claim = "In the triangle's pixel program, on 64x64 and 128x128 targets, g16, g19 (through mov), g26-g31 and g40 read 0, g20 and g41 read 1, g42 0x3f800000 and g43 0xff000000 on every covered pixel, as in the 64x32 fill; g17, g18, g21-g25 and g39 vary from pixel to pixel in both (g39 takes 0, 4, 8 and 12); two runs each"
unit = "usse"
method = "on the laptop, linux fork b5a86838ae59 with the debug option on: probes/usse/globals.toml: mov.end o0, gN for g16-g31 and g39-g43 as the first triangle's pixel program (pix_op.s, host tri, slot pixel) on 64x64 and 128x128 targets, every pixel read back, and the same registers as the 64x32 fill's pixel (value.s); two runs each"
tiers = ["HW"]
date = "2026-11-03"
data = ["usse-globals"]
terms = []
+++

**Results.** Constant on every pixel the triangle covers (1062 of 4096 at 64x64, 4284 of 16384
at 128x128) and on the fill's 2048: g16 0, g19 0, g20 1, g26-g31 0, g40 0, g41 1, g42
0x3f800000 (1.0), g43 0xff000000. Varying: g17 0-3, g18 even values (0x10-0x16 in the fill,
0x0e-0x16 at 64x64, 0x0a-0x16 at 128x128), g21 up to 31, g22 up to 11 or 15, g23 and g24 (the
pixel's x and y in its tile), g25 its place in the quad, g39 0, 4, 8 or 12 (not 4 x g25). Both
runs give the same values.

**Not shown.** A vertex task's and the end-of-tile task's global registers (Q053).
