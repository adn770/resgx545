+++
id = "E037"
claim = "A copy that reads its source as UYVY and loads colour-space set 0 with the limited-range BT.601 words writes, at every one of 2048 pixels and in both runs, sat_u8((cY * (Y - 16) + cU * (U - 128) + cV * (V - 128)) >> 7) in each channel, the arithmetic shift truncating; with the set loaded as zeros, or not loaded, the copy writes opaque black"
unit = "texture"
method = "hand-run script probes/texture/templates/tpu-csc.sh (csc-set0-uyvy-copy and csc-set1-formats) on the laptop, linux fork with the debug option on: a 64x32 copy over the every-value source with --pixels, the texture words poked to a UYVY form (tex:1 = 0x7d03f01f, tex:0 bits 7 and 4 set), the transfer command's colour-space load flag (xfer:17 bit 0) set and set 0 loaded through xfer:18 to xfer:22; two runs, the second is the follow-up run"
tiers = ["HW"]
date = "2026-11-01"
data = ["texture-tpu-csc", "texture-tpu-csc-followup"]
terms = ["CR_TPU_YUV_CSC0_0", "CR_TPU_YUV_CSC0_1", "CR_TPU_YUV_CSC0_2", "CR_TPU_YUV_CSC0_3", "CR_TPU_YUV_CSC0_4", "transfer_cmd.load_yuv_csc", "TEXTYPE", "TEXFORMAT"]
+++

**What runs.** The copy of E028's every-value source, with its texture words changed so that
the source buffer is read as two-byte texels (T1 = 0x7d03f01f: TEXTYPE 3, TEXFORMAT 29, a
UYVY form; T0 bits 7 and 4). The 8192-byte source is then 64 texels to a row of 128 bytes:
each pair of texels is four bytes U, Y0, V, Y1. Three runs differ in the transfer command's
colour-space block: not loaded; set 0 loaded with 0x00950095, 0x00000095, 0x010203ce,
0x039800cc and 0 (the limited-range BT.601 numbers in 128ths); set 0 loaded with zeros. Every
pixel of the target is printed.

**Results.**

- Set 0 loaded with the BT.601 words: the target hash is 0xb6067a95fa98de2d. Computing, for
  each of the 2048 pixels, Y (Y0 for an even texel, Y1 for an odd one), U and V from the plain
  source's bytes and then
  R = (149 (Y - 16) + 204 (V - 128)) >> 7,
  G = (149 (Y - 16) - 50 (U - 128) - 104 (V - 128)) >> 7,
  B = (149 (Y - 16) + 258 (U - 128)) >> 7,
  each saturated to 0 to 255, with alpha 0xff, gives all 2048 pixels exactly and the same
  hash. The numbers are the words' fields read as signed 10-bit and 16-bit coefficients, a
  reading the fit confirms. The follow-up run gives the same hash and the same pixels. The
  csc-set1-formats run with both sets loaded (below) gives it a third time.
- Set 0 loaded with zeros, and the load flag clear: both give a target of 0xff000000 in all
  2048 pixels (hash 0xd3522437a14b6325), in both runs.
- The offsets of 16 and 128 are in the arithmetic: dropping the 16 is the 0x0848 bit of E038,
  and the hash it gives is the hash of the same model without the 16.

**Not shown.** What the block holds when the load flag is clear: here it reads as zeros
in both runs, which does not say whether the block is reset for each job or kept from
earlier ones. Other source sizes, strides or texture formats (E040 has two).
