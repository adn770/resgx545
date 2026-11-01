+++
id = "E332"
claim = "Under the harness the closed GLES2 driver writes ISP word 0's depth compare as the GL function's order (never 0, less 1, equal 2, less or equal 3, greater 4, not equal 5, greater or equal 6, always 7), sets bit 20 when depth is off or its writes masked and bit 21 with a colour mask of 0000, sets ISP word 2 (presence bit 2, ISP word 0 bit 8, the reference in bits 7:0) with GL's stencil function, masks and the three operations in the codes of ISP2's fields, and puts glColorMask in ISP word 1 bits 7:4 (red bit 7, green 6, blue 5, alpha 4); blending gives pass type 1, and bit 9 is set in every clear object and triangle (the pass-type-3 objects have it clear)"
unit = "isp"
method = "the render-state-variations capture (64 runs of tri under the harness, one piece of GL state each) and the isp-registers capture (blending over depth, a read-only depth with blending, stencil with depth, a discarding shader over depth), read with harness/ukernel-extract/state3d.py: the MTE state blocks' ISP words of the clear object and of the triangle, against base"
tiers = ["CAP"]
date = "2026-11-03"
data = ["render-state-variations", "isp-registers"]
terms = [
    "ISP0", "ISP0.DCMP_MODE", "ISP0.DWRITE_DISABLE", "ISP0.TAGWRITE_DISABLE", "ISP0.PASS_TYPE",
    "ISP0.ISP2_PRESENT", "ISP0.SREF", "ISP0.BIT9", "ISP1", "ISP2", "ISP2.SCMP_MODE",
    "ISP2.SCMP_MASK", "ISP2.SW_MASK", "ISP2.SOP1", "ISP2.SOP2", "ISP2.SOP3", "PRESENCE",
    "ISP1.CMASK",
]
+++

**What runs.** Each run of the closed GLES2 stack under the harness draws one triangle after a
`glClear` into a 64x64 RGB565 pbuffer; the driver draws the clear as an object of its own, so
every scene has two state blocks: the clear's (presence `0xd4c3`) and the triangle's (`0xdf43`).
One option changes per run: the depth function, `glDepthMask`, the stencil function, masks and
operations, `glColorMask`, blending, culling and the primitive.

**Results.** ISP words of the clear object and the triangle (ISP word 2 only where present).

| run | clear ISP0 | clear ISP1 | triangle ISP0 | triangle ISP1 | ISP2 (clear, triangle) |
|---|---|---|---|---|---|
| base (no depth) | `0x01d00200` | `0xf0` | `0x01d00200` | `0x10f0` | |
| depth never .. always | `0x01c00200` | `0xf0` | `0x00000200` + n `<< 22` | `0x10f0` | |
| depth less, `glDepthMask(0)` | `0x01d00200` | `0xf0` | `0x00500200` | `0x10f0` | |
| stencil always, 1 | `0x01d00300` | `0xf0` | `0x01d00301` | `0x10f0` | `0x0e0200ff`, `0x0e02ffff` |
| stencil equal, 3 | `0x01d00300` | | `0x01d00303` | | `0x0e0200ff`, `0x0402ffff` |
| stencil less, 3 | | | `0x01d00303` | | `0x0e0200ff`, `0x0202ffff` |
| stencil always, 85 | | | `0x01d00355` | | `0x0e0200ff`, `0x0e02ffff` |
| stencil masks 0x0f, 0xf0 | | | `0x01d00301` | | `0x0e0200f0`, `0x0e020ff0` |
| ops zero, incr, invert | | | | | `0x0e0200ff`, `0x0e5dffff` |
| ops decr, incrwrap, decrwrap | | | | | `0x0e0200ff`, `0x0f37ffff` |
| depth less + stencil | `0x01c00300` | | `0x00400301` | | `0x0e0200ff`, `0x0e02ffff` |
| colour mask 1110 | | `0xe0` | | `0x10e0` | |
| colour mask 1000 | | `0x80` | | `0x1080` | |
| colour mask 0000 | (no clear object) | | `0x01f00200` | `0x1000` | |
| blending (four equations) | | | `0x03d00200` | | |
| blending over depth less | `0x01c00200` | | `0x02400200` | | |
| the same with `glDepthMask(0)` | `0x01d00200` | | `0x02500200` | | |
| a shader that discards, depth less | `0x01c00200` | | `0x08400200` | | |

The depth runs give the triangle's ISP word 0 n = 0 to 7 for never, less, equal, less or equal,
greater, not equal, greater or equal and always, with bit 20 clear. Blank cells are base's. The
clear colour, the colour, the viewport, the size, the format, culling of front or back faces,
the front-face winding, dithering, the shift and scale of the vertices and the depth range leave
every ISP word as base; with both faces culled the triangle's block is gone.

**What it shows.**

- `ISP0.DCMP_MODE` takes the GL depth functions in their enum order, so the four values the
  hardware runs could not tell apart (2, 3, 5, 6) are the driver's equal, less or equal, not
  equal and greater or equal [CAP].
- `ISP0.DWRITE_DISABLE` is set with depth off and with `glDepthMask(0)`; the clear object with
  depth on compares always and writes depth (`0x01c00200`), so the driver clears depth by drawing
  [CAP].
- The stencil state is GL's, field for field: `ISP0.SREF` the reference, `ISP2.SCMP_MODE` the
  function in the order of §11.3, `ISP2.SCMP_MASK` (15:8) the function's mask and `ISP2.SW_MASK`
  (7:0) the write mask, which the clear object takes too; `ISP2.SOP1`, `SOP2` and `SOP3` the
  stencil-fail, depth-fail and pass operations, keep 0, zero 1, replace 2, increment 3,
  decrement 4, invert 5, increment wrapping 6, decrement wrapping 7. The clear object replaces the
  stencil with reference 0 and a compare mask of 0 [CAP].
- ISP word 1 bits 7:4 are `glColorMask`, one bit per channel, red in bit 7 and alpha in bit 4;
  with all four masked the driver drops the clear object and sets `ISP0.TAGWRITE_DISABLE` on the
  triangle [CAP]. Whether the ISP or the PBE acts on bits 7:4 is not shown.
- A discarding shader over depth keeps its depth compare and writes in pass type 4
  (`0x08400200`, E340).
- Blending gives `ISP0.PASS_TYPE` 1, with or without depth, and the blended object keeps the
  depth test and its depth writes as GL sets them [CAP].
- `ISP0.BIT9` is set in the ISP word 0 of every clear object and triangle of the runs; the
  pass-type-3 objects a scissor or a smaller viewport adds (ISP word 0 `0x07e00100`) have it
  clear [CAP].
