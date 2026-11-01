+++
id = "E040"
claim = "No bit of T0, T1 or T3 (103 cases) and no bit of the colour-space set 1 words or of 0x0848 makes the UYVY copy follow the set 1 numbers (BT.709): every converting case keeps set 0; TEXFORMAT 28 (TEXTYPE 3) reads YUYV, Y0 U Y1 V, converted by set 0 at all 2048 pixels, and TEXFORMAT 26 with T0 bit 30 reads one byte per texel, rows of 64 bytes, written unconverted as grey with alpha 0xff at all 2048 pixels, in both runs; TEXFORMAT 26 without T0 bit 30 gives values that differ from run to run"
unit = "texture"
method = "sweep copy-uyvy-csc-select (103 cases) of probes/texture/tpu-csc.toml and hand-run script probes/texture/templates/tpu-csc.sh (csc-set1-formats), on the laptop, linux fork with the debug option on: the UYVY copy of E037 over the every-value source with set 0 loaded as the BT.601 words (xfer:18 to xfer:22) and set 1 as limited-range BT.709 words (xfer:23 to xfer:27 = 0x00950095, 0x00000095, 0x010e03e5, 0x03bc00e6, 0); two runs, the second is the follow-up run"
tiers = ["HW"]
date = "2026-11-01"
data = ["texture-tpu-csc", "texture-tpu-csc-followup"]
terms = ["CR_TPU_YUV_CSC1_0", "CR_TPU_YUV_CSC1_1", "CR_TPU_YUV_CSC1_2", "CR_TPU_YUV_CSC1_3", "CR_TPU_YUV_CSC1_4", "CR_TPU_YUV_CSC_INPUT", "TEXFORMAT", "TEXTYPE"]
+++

**What runs.** The UYVY copy of E037 with both colour-space sets loaded. Computed with the set 1
words (the Y coefficient 149, R from V 230, G from U -27 and from V -68, B from U 270, in
128ths) the image of the same copy would have the hash 0x42aa0a911101b775; with set 0 it has
0xb6067a95fa98de2d (E037). The sweep flips each bit of T0, T1 and T3 of this copy and sets
each to 0 and 0xffffffff (103 cases). The hand runs then change the texture format.

**Results.**

- The hand run with both sets loaded gives the set 0 image (hash 0xb6067a95fa98de2d), 2048 of
  2048 pixels, in both runs.
- The sweep: 45 cases leave the image unchanged, 46 change it, 11 fault; 50 distinct hashes
  occur in all, and the set 1 hash 0x42aa0a911101b775 is none of them. The 46 changed cases
  change more than the colour matrix (the format, the size, the type), so the test is that no
  case selects set 1, not that each is converted by set 0. xfer:28 bit 1 (the second bit of
  the word that loads 0x0848) leaves the baseline hash (E038).
- TEXFORMAT 28 (T1 = 0x7c03f01f): the target equals, at all 2048 pixels and in both runs
  (hash 0x22baa46d8c059625), the set 0 conversion of a texture read as Y0 U Y1 V (the bytes of
  each pair in that order), 64 texels to a row.
- TEXFORMAT 26 (T1 = 0x7a03f01f) with T0 bit 30: the target is, at all 2048 pixels and in
  both runs (hash 0xb48035ae6acbd325), 0xff000000 | b * 0x010101 for b the source byte
  of the pixel's index (64 bytes to a row): one byte per texel, no conversion.
- TEXFORMAT 26 without T0 bit 30: two runs give two hashes (0xe7c847c7a178e1f7 and
  0x5ee8806bcaf784d8), so the values are not repeatable. They are not one of the two forms
  above.

**Not shown.** What does select set 1 (a path other than this copy's read: a write to a YUV
format, or a format not tried); the 46 changed cases of the sweep are not classified further.
