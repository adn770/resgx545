+++
id = "E214"
claim = "With ISP word 0 bit 28 set, 55 values of 0x0520 give 6 distinct images of the 64x64 triangle, each reproduced pixel for pixel by one rule: a pixel is covered when the pixel centre, the pixel's top-left corner or any of four samples placed by the value's bytes (x in bits 3:0, y in bits 7:4 of each byte, sixteenths of a pixel) is inside the triangle; a second rule fits the same images, and no value removes a pixel"
unit = "isp"
method = "the 55 probes isp-sample-positions-isp0b28-0520-* of probes/isp/sample-positions.toml on the laptop, linux fork with the debug option on: ISP word 0 = 0x11d00200 on the default triangle (8, 8), (56, 20), (20, 56), 0x0520 (rd:19) poked to one value per probe, every pixel read back, the images fitted offline with exact fractions and the top-left tie rule (a pixel centre on the left edge counts as inside, on the other two edges as outside); one run"
tiers = ["HW"]
date = "2026-11-01"
data = ["isp-sample-positions"]
terms = ["CR_ISP_SAMPLE_POS", "CR_ISP_MULTISAMPLECTL", "hw_render_details.isp_sample_pos", "programmable sample positions", "ISP0"]
+++

**What runs.** The triangle job with ISP word 0 bit 28 set and 0x0520 set before the render to
one of 55 values: 0 to 0x1f, 0x30, 0x40, 0x80, 0xf0, 0xff, 0x100, 0x1000, 0x6000, 0x10000,
0x100000, 0x1000000, 0x10000000, 0x20000000, 0x3e000000, 0x3e006000, 0x3e006004, 0x3e006040,
0x3e007000, 0x3f800000, 0x40000000, 0x7fffffff, 0x80000000 and 0xffffffff. The pixel shader writes
one colour, so a pixel is covered or not. Two more probes run bit 28 with 0x0520 at the scratch
buffer's address (0x3e006000) and with 0x0520 left at 0. The job's 0x04c8 word is the default 0x88
(E064).

**Results.** Without bit 28 the triangle covers 1062 pixels (the base probe). With it:

| triangle pixels | gained over the 1062 | values of 0x0520 |
|---|---|---|
| 1098 | the 36 pixels whose centres lie on the long edge (56, 20)-(20, 56) | 30 |
| 1110 | those 36 and 12 more along the left edge | 8 |
| 1122 | those 36 and 24 more along the left edge | 13 |
| 1122 | those 36 and 24 more along the top edge | 1 (0xf0) |
| 1122 | those 36 and 24, along both edges | 2 (0xff, 0xffffffff) |
| 1134 | those 36 and 36 more | 1 (0x7fffffff) |

No value loses a pixel against the 1062. The probe with 0x0520 at the scratch address gives the
1122-pixel image that the value 0x3e006000 gives in the sweep, and with 0x0520 at 0 the 1098-pixel
image of value 0.

The fit: byte k of 0x0520 places sample k at (low nibble, high nibble) / 16 of a pixel from the
pixel's top-left corner, and a pixel is covered when any of those four samples, the pixel centre
or the pixel's top-left corner is inside the triangle (a point on the left edge counts as inside,
on the other two edges as outside). That rule reproduces all 55 images, and so does the four
samples plus the centre counted inside on every edge (without the corner). The four samples alone
fit 1 of the 55, the four plus the centre under the tie rule 53 (the two misses are 0x7fffffff and
0xffffffff), and reading the high nibble as x fits 30. The 36 on-edge pixels appear with every
value, so something other than the four samples covers them; the corner sample of the rule is the
simplest such thing and is what the default 0x04c8 word would supply (E215).

All the other bits tried with 0x0520 at the scratch address left the 1062-pixel image: ISP word 0
bits 10 to 14, 19 and 29 to 31, ISP word 1 bits 16 to 22 and 24 to 31, and ISP word 1 bit 3 (the
visibility test). ISP word 0 bit 18 faulted the job both with 0x0520 at the scratch address and at
0. No probe printed a changed scratch dword.

**Not shown.** Which of the two fitting rules is right (E215 varies 0x04c8), and whether bit 28
also changes the pixels' later stages, which one colour cannot show. The sweep has 6 distinct
images, so the 55 cases are fewer independent checks of the fit than 55. Ties on the long edge and
the top edge were settled by the 1062 baseline only. The kind of fault of bit 18 is not in the data
beyond "job faulted". One run.
