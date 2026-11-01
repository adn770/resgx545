+++
id = "E338"
claim = "With glPolygonOffset enabled the closed driver sets ISP word 1 bit 23 on the triangle (not on the clear object) and writes the render details' polygon offset registers: CR_ISP_POLY_OFFSET_FACTOR the GL factor as an IEEE single (1.0 0x3f800000, 2.0 0x40000000, -1.0 0xbf800000, 0 at 0), CR_ISP_POLY_OFFSET_UNITS the GL units as a 32-bit integer (1, 4, -1 as 0xffffffff), CR_ISP_POLY_OFFSET_CLAMP 0; the same with depth off and with depth less"
unit = "isp"
method = "the render-register-gaps capture (polygon offset factor, units 1,0; 0,1; 2,4; -1,-1; and 1,1 over depth less) read with harness/ukernel-extract/state3d.py: the render details' registers and the MTE state blocks' ISP words, against base"
tiers = ["CAP"]
date = "2026-11-03"
data = ["render-register-gaps"]
terms = [
    "ISP1.POLY_OFFSET", "CR_ISP_POLY_OFFSET_FACTOR", "CR_ISP_POLY_OFFSET_UNITS",
    "CR_ISP_POLY_OFFSET_CLAMP",
]
+++

**What runs.** tri's `polyoffset=F,U` enables `GL_POLYGON_OFFSET_FILL` and calls
`glPolygonOffset(F, U)`; the base run leaves it off.

**Results.**

| run | factor | units | clamp | triangle ISP1 | clear ISP1 |
|---|---|---|---|---|---|
| base | 0 | 0 | 0 | `0x000010f0` | `0xf0` |
| 1, 0 | `0x3f800000` | 0 | 0 | `0x008010f0` | `0xf0` |
| 0, 1 | 0 | 1 | 0 | `0x008010f0` | `0xf0` |
| 2, 4 | `0x40000000` | 4 | 0 | `0x008010f0` | `0xf0` |
| -1, -1 | `0xbf800000` | `0xffffffff` | 0 | `0x008010f0` | `0xf0` |
| 1, 1, depth less | `0x3f800000` | 1 | 0 | `0x008010f0` | `0xf0` |

Both kicks of each run carry the same registers. No other render details word and no ISP word 0
changes with the offset; over depth the patches are those of any depth render (E336).

**What it shows.**

- `ISP1.POLY_OFFSET` is the closed driver's polygon offset enable, set on every object drawn with
  the offset on, whatever the two values [CAP].
- `CR_ISP_POLY_OFFSET_FACTOR` holds GL's factor unscaled as a float and
  `CR_ISP_POLY_OFFSET_UNITS` GL's units as a signed integer, the ulps of the stored depth the
  hardware runs measured (§11.2, §11.4); `CR_ISP_POLY_OFFSET_CLAMP` stays 0 (no clamp) [CAP].
- So the hardware's slope factor and its units are GL's own: a driver passes both through
  [CAP; that the hardware scales the factor by the slope as GL does: §11.4's inference].
