+++
id = "E115"
claim = "phas's sample and selective rates change nothing a triangle shows at 1x or 4x: the pixel shader still runs once per pixel (all 324 pixels drawn at 4x hold one value over their four samples, one instance's g23, g24 and g25), every image is identical to the pixel rate's, and setm #1, #3, #5 and #15 mask nothing at any rate"
unit = "usse"
method = "on the laptop, linux fork with the debug option on: probes/usse/sample-rate.toml, the six probes usse-sample-rate-{pixel,sample,selective}-{1x,4x} (the 64x64 triangle at 1x and at 4x with render command words 1, 10, 13 and 16 as 0xe0000000, 0xeaa26e26, 0x80000002, 0xeaa26e26; pixel shader pix_rate.s: phas at the rate, then nop or setm #k, then o0 = 0xFF000000 | g25 << 16 | g24 << 8 | g23), five cases each (no setm and setm #1, #3, #5, #15), one run"
tiers = ["HW"]
date = "2026-11-01"
data = ["usse-sample-rate"]
terms = []
+++

**What runs.** The o0 value names the instance's place in its quad and tile. At 4x each pixel's
four samples sit over 2x2 pixels of the image, so a shader that ran per sample would leave the
four different.

**Results.** All 30 cases complete. At each resolution all 15 images (three rates, five
cases) are identical, pixel for pixel: at 1x one image of 1062 drawn pixels, at 4x one image of
1248 drawn samples. In the 4x image the 1248 samples fall in 324 2x2 blocks, and in every block
all drawn samples hold one value, so no pixel's samples came from different instances. The
`setm #1`, `#3`, `#5` and `#15` cases equal the no-`setm` case at every rate. Baselines before
and after each probe were exact; no visibility counter counted.

**What it shows.** The rate field alone does not turn per-sample shading on: under sample and
selective the shader still runs once per pixel, and `setm` masks nothing at any of the rates
(E099, E103). What turns per-sample shading on, and what selective selects, is not shown here;
E117 and E120 sweep the words that could.

**Not shown.** One run per probe.
