+++
id = "E271"
claim = "Bit 28 of the copy's T1 is the top bit of TEXFORMAT: set, the copy reads its source as YUYV (TEXFORMAT 28) and writes, at all 2048 pixels and over both sources, the colour-space set 0 conversion of the source read as Y0 U Y1 V pairs at the source's stride; with set 0 at zeros that is opaque black; set 0 keeps its words from one job to the next; T1 bits 28 and 24 together (TEXFORMAT 29) read UYVY the same way"
unit = "texture"
method = "the hand-run script of probes/texture/copy-words.toml (section t1-bit28) on the laptop, linux fork with the debug option on: the 64x32 copy over the plain and the every-value source with tex:1 bit 28 flipped, alone, with set 0 loaded with the BT.601 words (xfer:17 bit 0, xfer:18 to xfer:22), with T0 bits 7 and 4, after a copy that loads set 0 and the luma key, and with the luma-key mode; two rounds in one run, every pixel read back and compared with tex_words.yuv_image()"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["texture-copy-words"]
terms = ["T1.TEXFORMAT", "TEXFORMAT", "CR_TPU_YUV_CSC0_0", "transfer_cmd.load_yuv_csc", "T0.ALPHA_FROM_LUMA_KEY"]
+++

**What runs.** The copy's T1 is 0xcc03f01f: TEXTYPE 6 (strided), TEXFORMAT 12, 64 x 32 texels,
with T0 giving a stride of 64 dwords. Flipping bit 28 makes TEXFORMAT 28, the YUYV format of
E040. The model (tools/usse-asm/tex_words.py) reads the source as 4-byte pairs Y0 U Y1 V, 256
bytes a row, and converts each texel by E037's set 0 arithmetic.

**Results.** Each case ran in both rounds. The script's first bit-28 job loads nothing; it is
the first job to read set 0 since the GPU was last reset after a hang.

| case | image, plain and every-value source |
|---|---|
| bit 28, first job of the run | opaque black (0xff000000) at all 2048 pixels, plain source |
| bit 28 with set 0 loaded | the model, 2048 of 2048 pixels, both sources, both rounds |
| the same with T0 bits 7 and 4 flipped | the model, 2048 of 2048 |
| bit 28 in any later job, set 0 not loaded | the model, 2048 of 2048 |
| bits 28 and 24 (TEXFORMAT 29) with set 0 | the model read as U Y0 V Y1, 2048 of 2048 |
| bit 28 with T0 bit 31 and the luma key | the model's RGB, the luma key's alpha |
| set 0 and the luma key loaded, T1 as built | the baseline: the words act only on a YUV read |

**What it shows.** Bit 28 is TEXFORMAT's bit 4, and E039's opaque black image of this flip
(Q010) is the YUYV conversion through a set 0 that held zeros. The colour-space block keeps what
a job loads: later jobs that do not load it convert with the same words; a GPU reset after a hung
job clears it **[infer]** (the black image came after the earlier batches' hangs). TEXFORMAT 28
and 29 read strided sources at their stride, not only the non-power-of-two type of E040.
