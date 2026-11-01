+++
id = "E333"
claim = "The closed driver's end-of-tile task hands the PBE EMIT0 = 0, EMIT1 = (height - 1) << 16 | (width - 1), EMIT2 = 0x80 << 8 with bits 27:16 the row pitch in pixels / 2 - 1 (the same field for RGB565 and ARGB8888, the pitch a whole number of 8 pixels: 104 for a width of 100), EMIT3 the surface address, and a sideband of pack mode 3 (RGB565) or 0 (ARGB8888) with bit 9, bit 10 while GL dithering is on (also in ARGB8888) and bit 13 only for a render to a texture; 4x multisampling leaves the words as they are"
unit = "pbe"
method = "the render-state-variations capture (sizes 32x32 to 256x64, 100x60, ARGB8888 at two sizes, dithering off, and the other variations), and the render-register-gaps and isp-registers captures (render to a 64x64 texture with and without 2x and 4x multisampling), read with harness/ukernel-extract/state3d.py (eot.*, the four words the end-of-tile task loads and its emit's sideband) and, for the texture renders, summary3d.py; the target's allocation from each snapshot's objects.txt"
tiers = ["CAP"]
date = "2026-11-03"
data = ["render-state-variations", "render-register-gaps", "isp-registers"]
terms = [
    "EMIT0.MINCLIP_X", "EMIT0.MINCLIP_Y", "EMIT1.MAXCLIP_X", "EMIT1.MAXCLIP_Y", "EMIT2.BITS15_8",
    "EMIT2.LINE_STRIDE", "EMIT3.ADDRESS", "SIDEBAND.PACKMODE", "SIDEBAND.BIT9",
    "SIDEBAND.DITHER", "SIDEBAND.MEMLAYOUT", "PACKMODE",
]
+++

**What runs.** The end-of-render program's end-of-tile task loads four words with immediate moves
and emits them with its sideband; `state3d.py` reads them as `eot.pbe0` to `pbe3` and
`eot.sideband`. The texture renders' task has another shape, and `summary3d.py` gives its moves.

**Results.**

| run | target | EMIT1 | EMIT2 | EMIT3 | sideband | allocation |
|---|---|---|---|---|---|---|
| base, 56 more | RGB565 64x64 | `0x003f003f` | `0x001f8000` | `0x08087000` | `0x603` | `0x2000` |
| size 32x32 | RGB565 | `0x001f001f` | `0x000f8000` | `0x08087000` | `0x603` | |
| size 128x32 | RGB565 | `0x001f007f` | `0x003f8000` | `0x08087000` | `0x603` | |
| size 256x64 | RGB565 | `0x003f00ff` | `0x007f8000` | `0x08087000` | `0x603` | `0x8000` |
| size 100x60 | RGB565 | `0x003b0063` | `0x00338000` | `0x08087000` | `0x603` | `0x30c0` |
| format 8888 | ARGB8888 64x64 | `0x003f003f` | `0x001f8000` | `0x08087000` | `0x600` | `0x4000` |
| format 8888, 128x32 | ARGB8888 | `0x001f007f` | `0x003f8000` | `0x08087000` | `0x600` | `0x4000` |
| dither off | RGB565 64x64 | `0x003f003f` | `0x001f8000` | `0x08087000` | `0x203` | |
| texture 64x64 | RGBA texture | `0x003f003f` | `0x001f8000` | `0x080f5000` | `0x2200` | |
| texture, 2x, 4x | RGBA texture | `0x003f003f` | `0x001f8000` | `0x080f5000` | `0x2200` | |

EMIT0 is 0 in every run. Both kicks of a run carry the same words. A scissor, a viewport, a colour
mask, a clear colour or no clear, depth, stencil and blending leave the five words as base.

**What it shows.**

- EMIT0 and EMIT1 are the whole target, `EMIT1.MAXCLIP_X` and `_Y` its width and height minus
  one; the driver clips nothing at the PBE, a scissor included [CAP].
- `EMIT2.BITS15_8` is `0x80` (every unit of the tile stored) and bits 6:0 are 0 [CAP].
- `EMIT2.LINE_STRIDE` is the row pitch in pixels / 2 - 1 whatever the format: 31 for 64 pixels
  in both RGB565 (rows of 128 bytes, an allocation of `0x2000`) and ARGB8888 (256 bytes,
  `0x4000`); a width of 100 gets a pitch of 104 pixels (51; 60 rows of 208 bytes are `0x30c0`).
  At four bytes a pixel that is the (value + 1) x 8 bytes the hardware runs gave; in RGB565 the
  unit is 4 bytes, so the field counts pairs of pixels [CAP].
- `EMIT3.ADDRESS` is the allocation's device address [CAP].
- The sideband's `SIDEBAND.PACKMODE` is 3 for RGB565 and 0 for ARGB8888 and for the RGBA texture,
  `SIDEBAND.BIT9` is always set, `SIDEBAND.DITHER` (bit 10) follows `GL_DITHER` on a pbuffer, in
  ARGB8888 too, and is clear on the texture target with dithering on; `SIDEBAND.MEMLAYOUT`
  (bit 13) is set only when the target is a texture, which the closed driver lays out twiddled
  [CAP; that the texture is twiddled: infer].
- 2x and 4x multisampling of the texture render change none of the five words: the target the
  PBE writes stays 64x64 [CAP].
