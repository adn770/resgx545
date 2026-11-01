+++
id = "E278"
claim = "With ISP word 0 bit 28 set a pixel is covered when any of eight samples is inside the triangle, the four bytes of CR_ISP_MULTISAMPLECTL and the four of CR_ISP_SAMPLE_POS, each byte x in bits 3:0 and y in bits 7:4 in sixteenths of a pixel from its top-left corner, under the top-left rule, which predicts all 56 bit-28 images of two runs; the reading with the pixel centre in place of 0x04c8's samples misses 12, 24 or 36 pixels in 10 of the 28 settings (20 of the 56 images); with the bit clear only byte 0 of CR_ISP_MULTISAMPLECTL samples (one run)"
unit = "isp"
method = "probes/isp/coverage-samples.toml and probes/isp/coverage-bytes.toml on the laptop, linux fork with the debug option on: the 64x64 triangle with ISP word 0 0x11d00200 (bit 28) or 0x01d00200, the render command's word 16 (it loads 0x04c8) and render-details word 19 (0x0520, a kernel poke) at 28 pairs of values with bit 28 and 4 with it clear, a shader writing 0xff00ff00, every pixel read back and fitted pixel for pixel by isp_words.py rules; the bit-28 probes twice, the bit-clear probe once"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["isp-coverage-samples", "isp-coverage-bytes"]
terms = ["ISP0.SAMPLE_COVERAGE", "CR_ISP_MULTISAMPLECTL", "CR_ISP_MULTISAMPLECTL.SAMPLE0_X", "CR_ISP_MULTISAMPLECTL.SAMPLE0_Y", "CR_ISP_MULTISAMPLECTL.SAMPLE1_X", "CR_ISP_MULTISAMPLECTL.SAMPLE1_Y", "CR_ISP_MULTISAMPLECTL.SAMPLE2_X", "CR_ISP_MULTISAMPLECTL.SAMPLE2_Y", "CR_ISP_MULTISAMPLECTL.SAMPLE3_X", "CR_ISP_MULTISAMPLECTL.SAMPLE3_Y", "CR_ISP_SAMPLE_POS"]
+++

**What runs.** The triangle job's triangle, (8, 8), (56, 20), (20, 56) on a 64x64 target, over
the background 0xff203040. The render command's word 16 loads `CR_ISP_MULTISAMPLECTL` (0x04c8)
and render-details word 19 `CR_ISP_SAMPLE_POS` (0x0520). With ISP word 0 bit 28 set, the probe
`isp-coverage-samples-bit28` sets 22 pairs of the two words, chosen so that the readings of E214
part: both words at 0xcccccccc and at 0xeeeeeeee, which put all eight samples past the long edge
x + y = 76 (a sample at (a, b) / 16 is inside that edge when a + b < 16); 0x04c8 at those values
with 0x0520 at 0, and the other way round; each byte of either word at 0 with the rest at
0xcccccccc; and 0x0520 with one byte at 0x0f or 0xf0 (the sample at (15, 0) or (0, 15)), 0x04c8
at 0x88. The same probe ran a second time (`-r2`). `isp-coverage-bytes-bit28` (twice) sets one of
bytes 1 to 3 of 0x04c8 to 0x0f or 0xf0 with the rest and 0x0520 at 0xcccccccc. That is 28
settings with bit 28, 56 images over the two runs. Four cases run with bit 28 clear, once.

`isp_words.py rules` predicts each image under each reading: "eight", a pixel covered when any
of the eight samples is inside; "centre", any of 0x0520's four samples or the pixel centre, the
centre inside on every edge; one word's four samples alone; and "single", byte 0 of 0x04c8
alone. Inside is the edge functions positive, zero allowed on the left edge (the edge from
(20, 56) to (8, 8), which runs up the screen), the top-left rule; with it the single sample at
0x88 gives the triangle's 1062 pixels. Of that rule the images show only that a sample on the
long edge is outside: zero allowed or not on the left edge and on the edge from (8, 8) to (56,
20), the fits are the same.

**Results.** Pixels that differ from each reading's prediction, both runs alike:

| 0x04c8 | 0x0520 | pixels | eight | centre | single |
|---|---|---|---|---|---|
| 0x00000088 | 0 | 1098 | 0 | 0 | 36 |
| 0xcccccccc | 0xcccccccc | 1086 | 0 | 36 | - |
| 0xeeeeeeee | 0xeeeeeeee | 1086 | 0 | 36 | - |
| 0xcccccccc | 0 | 1122 | 0 | 24 | - |
| 0xeeeeeeee | 0 | 1122 | 0 | 24 | - |
| 0x00000088 | 0xcccccccc, 0xeeeeeeee | 1122 | 0 | 0 | - |
| 0x00000000 | 0xcccccccc | 1122 | 0 | 0 | - |
| one byte 0, rest 0xcc (4 cases) | 0xcccccccc | 1122 | 0 | 0 | - |
| 0xcccccccc | one byte 0, rest 0xcc (4 cases) | 1122 | 0 | 0 | - |
| 0x00000088 | one byte 0x0f or 0xf0 (6 cases) | 1122 | 0 | 0 | - |
| bytes 1-3 at 0x0f or 0xf0 (6 cases) | 0xcccccccc | 1134 | 0 | 12 | - |

The eight-sample reading predicts all 56 images of the two bit-28 probes and the coverage-bytes
probes, 28 settings each run twice, pixel for pixel. The centre reading misses 12, 24 or 36 pixels
in 10 of the 28 settings, 20 of the 56 images. The images with a byte at 0x0f and at 0xf0 differ in
24 pixels in the coverage-bytes probes (bytes 1 to 3 of 0x04c8) and in 48 in the 0x0520 one-byte
cases, and the reading with x and y swapped in that byte misses as many, so each byte of both words
holds x in bits 3:0 and y in bits 7:4. With bit 28 clear, the four images (0x04c8 at 0xcccccccc,
0xcc, 0x88 and 0xcccccc88 with 0x0520 at 0xcccccccc or 0) are predicted by byte 0 of 0x04c8 alone:
1086 pixels for a sample at (12, 12), 1062 for (8, 8), whatever 0x0520 and bytes 1 to 3 hold.

**What it shows.** ISP word 0 bit 28 widens a single-sampled object's coverage to the union of eight
samples, the four of `CR_ISP_MULTISAMPLECTL` and the four of `CR_ISP_SAMPLE_POS`, which answers
Q031. The centre reading fails wherever 0x04c8's samples cover other pixels than the centre does:
with all four past the long edge, and with one of bytes 1 to 3 at 0x0f or 0xf0. A centre sample
counted inside on every edge, or in place of 0x04c8's samples, is excluded; a centre sample under
the same top-left rule as the eight is not: added to them it also predicts all 56 images, and both
words at 0 (all eight samples at (0, 0)) would tell the two apart. Bytes 1 to 3 of
`CR_ISP_MULTISAMPLECTL` are sample positions laid out as byte 0 is (E064), read only here and under
multisampling (E281); a single-sampled object without bit 28 reads byte 0 only. That the tie rule is
the top-left rule is read from these images and the 1062 of the plain triangle [infer]: only the
long edge's exclusion is seen, and the triangle has no horizontal edge, so the rule's treatment of
one is not seen.
