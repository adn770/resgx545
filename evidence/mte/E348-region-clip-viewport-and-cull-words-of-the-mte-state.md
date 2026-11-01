+++
id = "E348"
claim = "In the closed driver's MTE state, the region clip word 0 holds an enable in bit 31 and the first and last 32-pixel tile columns in 30:16 and 15:0, word 1 the first and last 16-pixel tile rows in 31:16 and 15:0, counted from the bottom of the target in GL's window coordinates; a clear or mask fill's block always carries it, a draw's block only when its viewport does not cover the target; the viewport words are x + w/2, w/2, y + h/2, h/2 (y up, a positive scale), (n + f)/2 and (f - n)/2 of glViewport and glDepthRange; the end-of-scene term word holds the last 32-pixel column and row; MTECTL is 0x01555620 on every GLES2 draw (0x15555620 GLES1), plus 2 for cull back and 1 for cull front or cull back with clockwise front faces, 0x40 on the screen-space clear blocks, 0x3a0 on a flat-shaded GLES1 draw; GL_FRONT_AND_BACK drops the draw from the stream"
unit = "mte"
method = "captures/render/state-variations.toml, captures/ta/target-sizes.toml and the other eleven 3D capture tables of 11.11 (the closed GLES1 and GLES2 stacks under the harness on the laptop): the MTE state blocks' clip0-1, vp0-5, mtectl and term words (state3d.py's mte.* paths) over target sizes 32x32 to 256x64, render targets to 256x256, glViewport, glScissor, glDepthRange, glCullFace and glFrontFace runs, compared with diff3d.py"
tiers = ["CAP"]
date = "2026-11-03"
data = [
    "render-state-variations", "render-register-gaps", "render-draws-frames-pb",
    "isp-registers", "isp-line-width", "texture-textures", "texture-samplers",
    "texture-formats", "texture-streams", "usse-inputs", "usse-gles1-programs",
    "usse-shaders", "ta-target-sizes",
]
terms = [
    "VIEWPORT.X_OFFSET", "VIEWPORT.X_SCALE", "VIEWPORT.Y_OFFSET", "VIEWPORT.Y_SCALE",
    "VIEWPORT.Z_OFFSET", "VIEWPORT.Z_SCALE", "MTECTL.CULL_MODE", "MTECTL.NO_TRANSFORM",
    "MTECTL.FLAT_VERTEX", "MTECTL.ATTR_SMOOTH", "TERM.CLIP_RIGHT", "TERM.CLIP_BOTTOM",
    "PRESENCE",
]
+++

**What runs.** The state-variations table's size, viewport, scissor, depth-range, cull and
front-face runs against base (a 64 x 64 target, the full viewport), the 222 target sizes from
1x1 to 4096x4096 that complete (4097 and 8192 wide or high are refused), with the other tables'
blocks for the values that never move.

**Results.**

| run | clip0, clip1 | vp0-vp5 | term |
|---|---|---|---|
| 64x64 (base) | 0x80000001, 0x00000003 (clear) | 32, 32, 32, 32, 0.5, 0.5 | 0x00010001 |
| 32x32 | 0x80000000, 0x00000001 | 16, 16, 16, 16, 0.5, 0.5 | 0x00000000 |
| 128x32 | 0x80000003, 0x00000001 | 64, 64, 16, 16, 0.5, 0.5 | 0x00030000 |
| 100x60 | 0x80000003, 0x00000003 | 50, 50, 30, 30, 0.5, 0.5 | 0x00030001 |
| 256x64 | 0x80000007, 0x00000003 | 128, 128, 32, 32, 0.5, 0.5 | 0x00070001 |
| viewport 8,4,16,16 | triangle 0x80000000, 0x00000001 | 16, 8, 12, 8, 0.5, 0.5 | |
| viewport 0,0,32,32 | triangle 0x80000000, 0x00000001 | 16, 16, 16, 16, 0.5, 0.5 | |
| viewport 40,20,16,30 | triangle 0x80010001, 0x00010003 | 48, 8, 35, 15, 0.5, 0.5 | |
| scissor 4,8,16,32 | fill 0x80000000, 0x00000002 | as base | |
| scissor 0,0,32,16 | fill 0x80000000, 0x00000000 | as base | |
| scissor 40,20,16,30 | fill 0x80010001, 0x00010003 | as base | |
| depth range 0.25-0.75 | | 32, 32, 32, 32, 0.5, 0.25 | |

- The clear's block (0xd4c3) carries the clip for the whole target in every run. With a viewport
  smaller than the target the triangle's block gains the clip (0xdfc3) and the clear is split
  into mask fills (0xd485) and strips; with a scissor the triangle's block has no clip words, and
  the mask fills before it carry the scissor's tiles.
- A render-to-texture target of 256x256 gives the term word 0x00070007 for its render.
- Over the 222 target sizes the clear's clip0 is 0x80000000 | (width - 1) / 32, its clip1
  (height - 1) / 16, and every term word ((width - 1) / 32) << 16 | (height - 1) / 32, in every
  run (integer division).
- MTECTL: base 0x01555620; cull back 0x01555622; cull front and cull back with front face
  clockwise 0x01555621; front face clockwise alone 0x01555620; cull front-and-back writes no
  triangle state block or index list at all. Every GLES2 draw has 0x01555620 apart from the cull
  bits, every GLES1 draw 0x15555620, GLES1's flat-shaded vertex colour 0x000003a0, and every
  screen-space clear or fill 0x00000040.

**What it shows.**

- The region clip is in tiles, 32 pixels across and 16 down, inclusive, and y counts from the
  bottom of the GL target: the far scissor and viewport (y 20 to 49) give rows 1 to 3, which a
  count from the top (rows 0 to 2) would not [CAP].
- The viewport words are GL's viewport transform, word for word: vp0 and vp2 the centres, vp1
  and vp3 the half extents, vp4 and vp5 the depth range's centre and half extent, confirming the
  x/y order E061 rested on one mirror for [CAP].
- The term word's fields are the last 32 x 32 block column and row (`TERM.CLIP_RIGHT`,
  `TERM.CLIP_BOTTOM`), not the 16-row tile [CAP: 222 sizes].
- `MTECTL.CULL_MODE` 2 culls GL's back faces and 1 its front faces with the counter-clockwise
  default; `MTECTL.ATTR_SMOOTH`'s fields are 1 for every attribute the closed driver smooths
  (eight fields in GLES2, ten in GLES1), and flat shading sets `MTECTL.FLAT_VERTEX` to 3, GL's
  last vertex, with the fields at 0 [CAP]; bits 5 and 9 are set on every perspective draw and
  never varied [CAP].
