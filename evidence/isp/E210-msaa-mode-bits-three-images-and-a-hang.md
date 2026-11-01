+++
id = "E210"
claim = "With the multisample positions in place, 0x042c bits 1:0 at 0, 1 and 2 give three different images of the 64x64 triangle (1086, 868 and 896 triangle pixels; 916, 1260 and 1248 with the TE anti-aliasing bits) and 3 hangs the job in both settings; which sample count each value selects is not shown, so reading 1 as two samples and 2 as four is an inference of ours"
unit = "isp"
method = "the hand script msaa.sh of probes/isp/msaa.toml (function 042c_modes) on the laptop, linux fork with the debug option on: the 64x64 triangle with cmd:16 and cmd:10 at 0xeaa26e26, cmd:13 at 0x8000000N for N = 0 to 3, without and with cmd:1 = 0xe0000000, every pixel read back; one run"
tiers = ["HW", "infer"]
date = "2026-11-01"
data = ["isp-msaa"]
terms = ["CR_ISP_MSAA", "CR_ISP_MSAA.MODE", "hw_render_details.isp_msaa", "CR_ISP_MULTISAMPLECTL", "CR_TE_AA", "programmable sample positions"]
+++

**What runs.** The triangle job with the sample positions 0xeaa26e26 written to cmd:16 and cmd:10,
and 0x042c (cmd:13) set to 0x80000000 plus N for N = 0, 1, 2, 3. Each N runs twice, once as it
is and once with the TE anti-aliasing bits (cmd:1 = 0xe0000000). The script prints every pixel of
the 64x64 target (the plain end-of-tile program, so one value per pixel) and the count of pixels
of the triangle colour. E074 counts the same jobs; this record adds where the pixels lie.

**Results.** Triangle pixels, with the bounding box of those pixels:

| N | without the TE bits | with the TE bits |
|---|---|---|
| 0 | 1086, x 8-55, y 8-55 | 916, x 8-47, y 8-47 |
| 1 | 868, x 16-63, y 8-43 | 1260, x 0-46, y 10-55 |
| 2 | 896, x 20-63, y 16-47 | 1248, x 0-38, y 4-47 |
| 3 | job hung, context lost | job hung, context lost |

The three images that completed differ in each setting (different hashes), and the target after a
hung job holds only its fill value (0xdeadbeef in all 4096 pixels), the same in the two hangs. The
left edge of the triangle in the N = 1 image without the TE bits is at twice the x of the N = 0
image (x 8, 10, 12, 14, 16 at y 8, 16, 24, 32, 40 become 16, 20, 24, 28, 32) with the same y, but
its rows are not twice as long (30 pixels at y 16 against 31), so the image is not the
single-sampled one stretched in x; the N = 2 image keeps neither the position nor the size of
either.

**Not shown.** That N = 1 stores two samples a pixel and N = 2 four is a reading of ours [infer],
taken from the three different images and from a mode field that counts up (no citation record of
this tree covers another GPU's multisample mode field); this record fits no layout to the pixels,
so the sample count of a mode is not measured.
That N = 3 is an eight-sample mode that needs more state than these words is not shown either: it
only hangs. No follow-up run of this table exists; the counts are one run each.
