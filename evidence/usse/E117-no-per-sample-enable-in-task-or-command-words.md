+++
id = "E117"
claim = "Nothing tried turns on per-sample shading: with the pixel shader's phas at the sample rate on a 4x triangle, no unknown bit of the pixel task's U1 (bits 0, 1, 22, 23, 26 to 31), no bit of its U2 (all 32), no bit of the render command's te_aa (word 1) or aa_mode_3d (word 13), and no free bit of ISP words 0 and 1 makes a pixel's four samples differ; aa_mode_3d bit 1 cleared gives a 916-pixel image without the 4x layout, bit 0 hangs and bit 31 draws nothing, te_aa bit 29 draws nothing and bits 30 and 31 change the coverage (1312 and 832 pixels), and ISP word 0 bit 28 hangs a 4x render"
unit = "usse"
method = "on the laptop, linux fork with the debug option on: probes/usse/sample-rate.toml, probes usse-sample-rate-aarate-control, -aarate-cmd1, -aarate-cmd13, -aarate-isp0, -aarate-isp1, -taskrate-u1 and -taskrate-u2 (the 4x triangle of E115 at the sample rate, pix_rate.s writing o0 from its g-bank place, one bit of a word changed per case; the pixel PDS ORs one bit into U1 or sets one bit of U2), 131 cases (three of them controls), one run"
tiers = ["HW"]
date = "2026-11-01"
data = ["usse-sample-rate"]
terms = ["ISP0", "ISP1"]
+++

**What runs.** The control is the 4x triangle at the sample rate with the host's words: 1248
samples drawn in 324 2x2 blocks, every block holding one value. Each case changes one bit:
U1 bits 0, 1, 22, 23 and 26 to 31 (10 cases) and U2 bits 0 to 31 (32 cases) of the pixel task's
words; each bit of the render command's word 1 (te_aa, 32 cases) and word 13 (aa_mode_3d, 32
cases), flipped; ISP word 0 bits 10, 12 to 14, 19 and 28 to 31 (9 cases) and ISP word 1 bits
13 to 25 (13 cases) set.

**Results.** Every case that completes is compared with the control, image against image and
block against block.

- The task words: all 10 U1 cases and all 32 U2 cases give the control's image, pixel for
  pixel.
- te_aa: 29 of 32 flips give the control's image. Bit 29 completes and draws nothing; bit 30
  draws 1312 samples and bit 31 832; in every block of those images the drawn samples hold one
  value.
- aa_mode_3d: 29 flips give the control's image. Bit 0 hangs the job. Bit 1 (the 4x flag
  cleared) completes with a 916-pixel single-sample image, with no 2x2 layout. Bit 31 completes
  and draws nothing.
- ISP word 0: 8 of 9 give the control's image; bit 28 hangs the job. ISP word 1: all 13 give
  the control's image.

In no completed 4x image does a block hold two different instance values (the 916-pixel
single-sample image has no blocks). Every baseline triangle
before and after a probe, the two hangs included, was exact. No visibility counter counted.

**What it shows.** No bit of these words turns per-sample shading on; the shader still runs once
per pixel (E115) in every case. The words that would be the natural switch were swept, and none
did; whether the core has the mode at all is not shown.

**Not shown.** Bits whose change alters the coverage or the layout draw too few or too different
samples to say anything about the shader's rate for them. One run per case.
