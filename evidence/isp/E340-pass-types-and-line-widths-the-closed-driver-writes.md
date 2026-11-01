+++
id = "E340"
claim = "Over every captured run the closed driver uses four ISP pass types: 0 for opaque objects and the clear, 1 for every blended object and for the GLES1 alpha test, 4 for a GLSL shader that discards (with or without a depth test), and 3 for the two objects a scissor or a viewport smaller than the target adds (ISP word 0 0x07e00100, no ISP word 1, no pixel program); it writes glLineWidth x 16 into ISP word 1 bits 15:8 (1 0x10, 1.5 0x18, 2 0x20, 3 0x30, 4 0x40, 8 0x80, 15 0xf0) for lines and points alike and 0x10 for triangles, 0 for the clear object, the object type in ISP word 0 bits 17:15 (triangle 0, line 1, point 3), and CR_ISP_LINE_SAMPLE_POS 1 in every render"
unit = "isp"
method = "every MTE state block's ISP words in the render-state-variations, render-register-gaps, render-draws-frames-pb, isp-registers, isp-line-width, texture-textures, texture-samplers, texture-formats, texture-streams, usse-inputs, usse-gles1-programs and usse-shaders captures, read with harness/ukernel-extract/state3d.py; the pass type counted per run, the line widths and the render details' registers per run"
tiers = ["CAP"]
date = "2026-11-03"
data = [
    "render-state-variations", "render-register-gaps", "render-draws-frames-pb", "isp-registers",
    "isp-line-width", "texture-textures", "texture-samplers", "texture-formats", "texture-streams",
    "usse-inputs", "usse-gles1-programs", "usse-shaders",
]
terms = [
    "ISP0.PASS_TYPE", "ISP0.OBJ_TYPE", "ISP1.LINE_WIDTH", "CR_ISP_LINE_SAMPLE_POS", "PRESENCE",
]
+++

**What runs.** The pass type is ISP word 0 bits 27:25 of each MTE state block; the line width
ISP word 1 bits 15:8. The line runs draw `GL_LINES` with `glLineWidth` 1, 1.5, 2, 3, 4, 8 and 15,
and one `GL_POINTS` run with a line width of 8.

**Results.** Runs that hold each pass type, of the twelve tables:

| pass type | where | ISP word 0 |
|---|---|---|
| 0 | every run: the clear object, every unblended triangle, line or point | `0x01d00200` (base) |
| 1 | the four blendings, blending over depth (3 runs), GLES1 alpha test (2) | `0x03d00200` |
| 4 | shaders that discard: alone, on alpha (`0x09d00200`), over depth less | `0x08400200` |
| 3 | scissor (3 runs), a viewport smaller than the target (3 runs) | `0x07e00100` (added) |

Pass types 2, 5, 6 and 7 appear in no run.

| run | ISP0 bits 17:15 | ISP1 |
|---|---|---|
| triangles | 0 | `0x10f0` |
| lines 1, 1.5, 2, 3 | 1 | `0x10f0`, `0x18f0`, `0x20f0`, `0x30f0` |
| lines 4, 8, 15 | 1 | `0x40f0`, `0x80f0`, `0xf0f0` |
| points, line width 8 | 3 | `0x80f0` |

`CR_ISP_LINE_SAMPLE_POS` is 1 in all 815 render details snapshots of the 373 runs that kick
(six never kick).

**What it shows.**

- The closed driver's blended objects take the translucent pass (§11.11), and so does its GLES1
  alpha test, which therefore runs in the pixel program, not as a punch-through; a GLSL `discard`
  takes the punch-through pass 4 (§11.10), over depth with its depth test (less, bit 20 clear:
  `0x08400200`) [CAP].
- Pass type 3, which removes an object on the hardware (§11.1), carries the objects a scissor or a
  small viewport adds; they have no ISP word 1 and no pixel program [CAP; their role: E348's
  region clip, not settled here].
- `ISP1.LINE_WIDTH` is the GL line width in sixteenths, with no rounding at 1.5, up to 15.0
  (`0xf0`); points carry the line width too, not the point size, and triangles 1.0 [CAP]. The
  hardware runs measured the same unit (§11.12).
- `ISP0.OBJ_TYPE` is 1 for lines and 3 for points [CAP].
