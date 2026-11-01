+++
id = "E334"
claim = "In every render the closed driver submits, the background object's primary PDS program (cmd_ta.pds_bgnd word 2) holds in its data segment texture words describing the render target itself, in every run of the two tables captured: T1 a strided texture (TEXTYPE 6) of the target's format and size, T0 a clamped stride of the target's pitch in dwords minus one, T2 the target's address, T3 0x00800000 (that the program samples them is [infer]); the words are the same with a clear, without one and on a frame that does not clear, and CR_ISP_BGOBJVALS stays 0x300 and CR_ISP_BGOBJDEPTH 1.0 whatever the clear depth"
unit = "isp"
method = "the render-state-variations capture (base, no clear, the clear colours and depth, ARGB8888, sizes 100x60, 256x64, 128x32) and the render-draws-frames-pb capture (two frames, cleared each frame and cleared once), read with harness/ukernel-extract/state3d.py: the TA command's pds_bgnd words, the data segment of the primary program they point at (spec.pri.d*), the background object's words (bg.w*) and the render details' ISP registers, per kick"
tiers = ["CAP"]
date = "2026-11-03"
data = ["render-state-variations", "render-draws-frames-pb"]
terms = [
    "cmd_ta.pds_bgnd", "hw_render_details.pds_bgnd", "T0.STRIDE", "T0.ADDRMODE_U", "T0.ADDRMODE_V",
    "T1.TEXTYPE", "T1.TEXFORMAT", "T1.WIDTH", "T1.HEIGHT", "T2.TEXADDR", "TEXTYPE.STRIDE",
    "CR_ISP_BGOBJVALS", "CR_ISP_BGOBJDEPTH",
]
+++

**What runs.** The TA command's `pds_bgnd` words name the background object's secondary and
primary pixel programs (§5.3). The primary program's data segment, dwords 6 to 9, holds what
reads as a sampler's four words; the target is the pbuffer the end-of-tile task stores to (E333).

**Results.** Data dwords 6 to 9 of the background object's primary program, and the target.

| run | d6 (T0) | d7 (T1) | d8 (T2) | d9 (T3) | target |
|---|---|---|---|---|---|
| base and the others | `0x00060e90` | `0xc503f03f` | `0x08087000` | `0x00800000` | RGB565 64x64 |
| ARGB8888 | `0x000e0e90` | `0xcc03f03f` | `0x08087000` | `0x00800000` | ARGB8888 64x64 |
| ARGB8888 128x32 | `0x001e0e90` | `0xcc07f01f` | `0x08087000` | `0x00800000` | ARGB8888 128x32 |
| 100x60 | `0x000c0690` | `0xc506303b` | `0x08087000` | `0x00800000` | RGB565, pitch 104 |
| 256x64 | `0x001e0e90` | `0xc50ff03f` | `0x08087000` | `0x00800000` | RGB565 256x64 |

In the two-frame runs all four kicks carry base's words, whether the second frame clears or not;
only `pds_bgnd` word 2, the primary program's address, moves at the second frame (the driver
writes a new copy). The background object's own words (`bg.w*`) are the same in every run.
`CR_ISP_BGOBJVALS` is `0x300` and `CR_ISP_BGOBJDEPTH` `0x3f800000` (1.0) in every run, the clear
depth of 0.5 included.

Base's words hold with no clear, other clear colours, depth and stencil.

**What it shows.**

- The texture words decode as a texture of the target: `T1.TEXTYPE` 6 (`TEXTYPE.STRIDE`),
  `T1.TEXFORMAT` 5 (RGB565) or 12 (ARGB8888), `T1.WIDTH` and `T1.HEIGHT` the size minus one,
  `T2.TEXADDR` the target's address, `T0.STRIDE` the pitch in dwords minus one (31, 63, 51 and
  127 for rows of 128, 256, 208 and 512 bytes), `T0.ADDRMODE_U` and `_V` 2 (clamp) [CAP].
- So the background object can reload the target's previous colour in every render; the clear
  is drawn as an object over it (E332), and a frame that does not clear gets the same background
  [CAP for the words; that the program samples them into the pixel: infer, the program's
  instructions are not read here].
- The clear depth is not written into `CR_ISP_BGOBJDEPTH`: the clear object writes it (E332)
  [CAP].
