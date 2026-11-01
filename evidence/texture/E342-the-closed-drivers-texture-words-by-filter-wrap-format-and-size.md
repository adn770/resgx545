+++
id = "E342"
claim = "The closed driver's texture words T0 and T1, one GL sampler or format change at a time: GL_LINEAR minification sets T0 bits 11:10 to 1 and magnification bits 13:12 to 1, a linear mip filter sets bit 9, any mipmapped minification sets bits 20:17 to 13 instead of 15, bits 26:21 stay 0x3f; S wrap is bits 8:6 and T wrap bits 5:3 (0 repeat, 1 mirror, 2 clamp); T1 holds TEXTYPE (31:29: 0 power of two, 3 NPOT and streams, 6 depth), TEXFORMAT (28:24) and width and height less one (23:12, 11:0); RGBA4444 2, RGBA5551 4, RGB565 5, BGRA8888 12, RGB and RGBA8888 13, RGBA half float 17, float 18, PVRTC 2 bpp 23, PVRTC 4 bpp 24, ETC1 27, and with T0 bit 30 alpha 25, luminance 26, luminance-alpha 27 and luminance half float 30; a float RGBA texture is four one-channel fetches and a half-float one two; depth textures are TEXTYPE 6 float 18 with a 32-dword stride; T3 is 0x00800800 in every texture but the luminance half-float one (0x01000800); one capture each"
unit = "texture"
method = "captures/texture/samplers.toml, formats.toml and textures.toml (texture-samplers, texture-formats, texture-textures): the closed GLES2 stack under the harness on the laptop, tri.c tex=, texmin=, texmag=, texwraps=, texwrapt=, texfilter=, texwrap=, texfmt= and fbo= one at a time against tex_base (a 16x16 RGBA8888 texture, nearest, repeat); the doutt operands of each primary pixel program (state3d.py's mte.pri programs) and the texture objects' sizes in the snapshots"
tiers = ["CAP"]
date = "2026-11-03"
data = ["texture-samplers", "texture-formats", "texture-textures"]
terms = [
    "T0.MINFILTER", "T0.MAGFILTER", "T0.MIPFILTER", "T0.MAX_LEVEL", "T0.BITS26_21",
    "T0.ADDRMODE_U", "T0.ADDRMODE_V", "T0.BIT30", "T0.STRIDE", "T1.TEXTYPE", "T1.TEXFORMAT",
    "T1.WIDTH", "T1.HEIGHT", "T2.TEXADDR", "T3.DATA_SIZE", "TEXFORMAT", "TEXTYPE",
]
+++

**What runs.** 74 captures over three tables, each a 64 x 64 triangle sampling one texture; a
texture's state is the four operands of its primary pixel program's doutt (T0 to T3, in that
order). tex_base gives T0 0x07fe0000, T1 0x0d00f00f, T3 0x00800800.

**Results.** One field moves per change against tex_base, unless the table says otherwise.

| change | T0 | T1 |
|---|---|---|
| min linear / mag linear | 0x07fe0400 / 0x07fe1000 | |
| min nearest-mipmap-nearest (16x16 and 64x64) | 0x07fa0000 | |
| min linear-mipmap-nearest | 0x07fa0400 | |
| min nearest-mipmap-linear | 0x07fa0200 | |
| min linear-mipmap-linear | 0x07fa0600 | |
| the same, linear magnification (16, 64, 256 texels) | 0x07fa1600 | |
| S clamp / T clamp | 0x07fe0080 / 0x07fe0010 | |
| S mirror / T mirror | 0x07fe0040 / 0x07fe0008 | |
| both clamp / both mirror | 0x07fe0090 / 0x07fe0048 | |
| 1x1, 8x8, 32x32 | | 0x0d000000, 0x0d007007, 0x0d01f01f |
| 64x16, 16x64, 1024x1024 | | 0x0d03f00f, 0x0d00f03f, 0x0d3ff3ff |
| NPOT 12x12 and 100x60 (clamped) | 0x07fe0090 | 0x6d00b00b, 0x6d06303b |
| RGBA4444, RGBA5551, RGB565, RGB888 | | TEXFORMAT 2, 4, 5, 13 |
| BGRA8888, RGBA half float, RGBA float, luminance float | | 12, 17, 18, 18 |
| PVRTC 4 and 2 bpp (RGB and RGBA alike), ETC1 | | 24, 23, 27 |
| alpha, luminance, luminance-alpha (8-bit) | 0x47fe0000 | 25, 26, 27 |
| luminance half float | 0x47fe0000 (T3 0x01000800) | 30 |
| depth 16 and depth 32 | 0x00060e00 | 0xd200f00f |

- A float RGBA texture gives four doutt fetches, T2 `0x400` bytes apart (four planes of one
  32-bit channel, the 16x16 object `0x1000` bytes), a half-float one two fetches `0x400` apart
  (`0x800` bytes); luminance float and luminance half float one fetch each.
- The depth textures (TEXTYPE 6, TEXFORMAT 18) have T0's stride field at 31 (32 dwords), and the
  upload fills the first 16 dwords of each 32-dword row of a `0x1000`-byte object.
- Render-to-texture targets are sampled as RGBA8888 (13) with both wraps clamped, whatever the
  pixel format of the window.
- T2 is the texture's address in every run (the object holding the upload); the compressed
  textures' objects are `0x80` bytes for 16x16.
- The cube-map runs, the copy and the readback runs give no doutt with data-segment operands, so
  their texture words are not read here.

**What it shows.**

- The filter and wrap fields of T0 (`T0.MINFILTER`, `T0.MAGFILTER`, `T0.MIPFILTER`,
  `T0.ADDRMODE_U` on GL's S axis, `T0.ADDRMODE_V` on T) are where the hardware records place them,
  and GL's linear is 1 in each filter field [CAP].
- For a mipmapped minification the closed driver writes `T0.MAX_LEVEL` 13, above any level of the
  chains captured, and 15 (level 0 only) otherwise; it never moves the LOD bias (0x3f) [CAP].
- TEXFORMAT 25, 26 and 27 name one-channel and two-channel byte formats under T0 bit 30, while 27
  is ETC1 without it; 30 under bit 30 is a one-channel half float [CAP]. `T3.DATA_SIZE` reads 1
  in every texture of these tables, 2 for the luminance half float alone; what it sizes is not
  separated from the format by one capture.
- The four-plane float layout means the closed driver does not sample a 128-bit texel in one
  fetch [CAP].
