+++
id = "E341"
claim = "Streaming a YUV buffer through IMG_texture_stream2, the closed driver samples a packed UYVY or YUYV buffer (pixel formats 73 and 74) in one fetch, TEXTYPE 3 with TEXFORMAT 29 or 28, and loads colour-space set 0 in the render details as 0x00950095, 0x00000095, 0x010203ce, 0x039800cc and 0 with set 1, the input word and the USE coefficients at 0; it samples NV12 (format 64) as two fetches, the luma plane as TEXFORMAT 26 and the half-size chroma plane after it as TEXFORMAT 27, both with T0 bit 30, and loads the USE coefficient registers instead (CR_USE_COEFFS_MODE 3, three groups of taps and biases) with the colour-space sets at 0; the formats 69, 71, 195, 196, 199 and 200 are refused at the bind and the draw samples a 1x1 RGBA8888 texture; one capture each"
unit = "texture"
method = "captures/texture/streams.toml (texture-streams): the closed GLES2 stack under the harness on the laptop, tri.c stream=FMT[,WxH] through fakedrm.c's buffer-class device (bufclass.h's format codes), 64x64 buffers and one NV12 buffer of 32x16, against tex_8888 (a 64x64 RGBA8888 texture); the primary pixel program's doutt words (state3d.py's mte.pri program, its data words) and the render details' 3D registers (state3d.py rd.registers_3d.*), compared with diff3d.py"
tiers = ["CAP"]
date = "2026-11-03"
data = ["texture-streams"]
terms = [
    "CR_TPU_YUV_CSC0_0", "CR_TPU_YUV_CSC0_1", "CR_TPU_YUV_CSC0_2", "CR_TPU_YUV_CSC0_3",
    "CR_TPU_YUV_CSC0_4", "CR_TPU_YUV_CSC_INPUT", "CR_USE_COEFFS0_A", "CR_USE_COEFFS0_B",
    "CR_USE_COEFFS0_BIAS", "CR_USE_COEFFS1_A", "CR_USE_COEFFS1_B", "CR_USE_COEFFS1_BIAS",
    "CR_USE_COEFFS2_A", "CR_USE_COEFFS2_B", "CR_USE_COEFFS2_BIAS", "CR_USE_COEFFS_MODE",
    "T1.TEXFORMAT", "T1.TEXTYPE", "T0.BIT30", "T2.TEXADDR",
]
+++

**What runs.** Twelve runs of the stream table, each a 64 x 64 RGB565 target with one triangle
sampling the stream; the buffer-class device offers the buffer under the pixel format code each
run names. Every run completes with two kicks.

**Results.** The texture words are the operands of the primary pixel program's doutt; the
registers are the render details' 3D register words, which the EDM loads before the render.

| run (format code) | fetches | T0 | T1 | registers that differ from tex_8888 |
|---|---|---|---|---|
| tex_8888 (RGBA8888) | 1 | 0x07fe0000 | 0x0d03f03f | |
| fuyvy (73) | 1 | 0x07fe0090 | 0x7d03f03f | colour-space set 0, four words |
| fyuyv (74) | 1 | 0x07fe0090 | 0x7c03f03f | colour-space set 0, four words |
| nv12 (64) | 2 | 0x47fe0090 | 0x7a03f03f, 0x7b01f01f | the USE coefficients, ten words |
| nv12 32x16 (64) | 2 | 0x47fe0090 | 0x7a01f00f, 0x7b00f007 | the USE coefficients, ten words |
| uyvy 71, yuyv 69, c0 196 and 195, c1 200 and 199 | 1 | 0x07fe0090 | 0x0d000000 | none |

- The packed runs load `CR_TPU_YUV_CSC0_0` to `_3` as 0x00950095, 0x00000095, 0x010203ce and
  0x039800cc; `CR_TPU_YUV_CSC0_4`, set 1 (0x0834-0x0844), `CR_TPU_YUV_CSC_INPUT` and the USE
  coefficient registers stay 0.
- The NV12 runs load `CR_USE_COEFFS_MODE` = 3 and the three groups: set 0 0x00000066,
  0x00262500, 0x000c8456; set 1 0xce000098, 0x004b4a00, 0x00043ca7; set 2 0x41000000,
  0x00002500, 0x000dd655 (A, B and bias words each). The colour-space sets stay 0.
- The NV12 texture words: TEXTYPE 3 for both planes, the luma plane at the buffer's address
  with TEXFORMAT 26 and the full size, the chroma plane `0x1000` bytes later (64 x 64 luma
  bytes; `0x200` for the 32 x 16 buffer) with TEXFORMAT 27 and half the width and height. T0 bit
  30 is set on both, clear on every other stream run.
- The six refused runs: tri.out reports the stream device's query giving no size, format or
  buffer count and the bind failing (GL error 0x501), and the triangle samples a 1x1 RGBA8888
  texture at another address. No register changes. The accepted runs bind with no error.
- T3 is 0x00800800 in every run. The wrap fields of T0 are clamp on both axes (0x90) in every
  stream run.

**What it shows.**

- A packed YUV stream is converted by the texture unit through colour-space set 0, which the
  closed driver loads with the limited-range BT.601 numbers whose conversion E037 measured, word
  for word the values of that record [CAP]. Set 1 and the input word are never loaded by the
  closed GLES stack in these runs, so they give no reading of set 1.
- NV12 is not converted by the texture unit: its planes are fetched as one-byte and two-byte
  textures (TEXFORMAT 26 and 27 under T0 bit 30, the readings E040 gives those codes with that
  bit) and the conversion is left to the pixel program with the USE coefficient registers loaded
  [CAP]; that the three groups hold the YUV-to-RGB weights in 64ths (102 for V to R, 37 and 38 or
  74 and 75 for the luma weight split over two taps, 65 for half of U to B) is a reading of the
  values only [infer].
- Of the buffer-class format codes only 64, 73 and 74 are accepted by the stream extension; the
  other codes of the GPL enum's YUV group are refused [CAP].
