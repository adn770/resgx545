+++
id = "E336"
claim = "The closed driver names a window surface's depth buffer through the TA command's 3D patches, not its render details: the surface's first render with the ZLS flags carries six {address, value} pairs, in this order CR_ISP_ZLSCTL (0x0017100c), CR_BIF_ZLS_REQ_BASE (0x08000000), CR_ISP_ZLOAD_BASE and CR_ISP_ZSTORE_BASE (both the depth offset), CR_ISP_STENCIL_LOAD_BASE and CR_ISP_STENCIL_STORE_BASE (both the stencil offset with bit 31), each address a render details register word; every later render of the surface carries one pair, CR_ISP_ZLSCTL 0x0017700e; renders without the flags carry none"
unit = "zls"
method = "the render-draws-frames-pb and render-register-gaps captures (every run with depth or stencil, one or two frames, a mid-frame flush, polygon offset, a texture with depth) and the isp-registers capture (blending, stencil, a discarding shader and 64 draws over depth), read with harness/ukernel-extract/state3d.py: each TA command's num_patches_3d and its pairs, named by the render details word each address falls on (upd.*)"
tiers = ["CAP"]
date = "2026-11-03"
data = ["render-draws-frames-pb", "render-register-gaps", "isp-registers"]
terms = [
    "cmd_ta.num_patches_3d", "cmd_ta.patches_3d", "hw_render_details.isp_zlsctl",
    "hw_render_details.bif_zls_req_base", "CR_ISP_ZLSCTL", "CR_BIF_ZLS_REQ_BASE",
    "CR_ISP_ZLOAD_BASE", "CR_ISP_ZSTORE_BASE", "CR_ISP_STENCIL_LOAD_BASE",
    "CR_ISP_STENCIL_STORE_BASE",
]
+++

**What runs.** The TA command holds a count of 3D patches and as many {address, value} pairs
(E158); `state3d.py` names each pair by the render details word its address falls on. The runs:
one frame and two frames with depth (cleared each frame or once), stencil, depth and stencil,
depth with a mid-frame flush, polygon offset over depth, blending, stencil and 64 draws over
depth, a 4x multisampled texture with depth, and the window's two frames after a texture render
with a depth attachment.

**Results.**

| render | patches, in order |
|---|---|
| the surface's first, render flags `0x180` | the six of the list below |
| every later render of the surface | `isp_zlsctl` `0x0017700e` |
| a render without depth or stencil | none |
| a texture's, its depth attachment | none (render flags `0x80`) |
| ExternalZBufferMode=2, first render | `isp_zlsctl` `0x0017700e` (the rest set with the context) |

The six: `isp_zlsctl` `0x0017100c`; `bif_zls_req_base` `0x08000000`; `zload_base` and
`zstore_base`, both the depth offset (`0xf6000`, or `0xfe000` and `0xff000` where a texture took
the lower allocation); `stencil_load_base` and `stencil_store_base`, both the depth offset +
`0x4000` with bit 31. For the texture's depth attachment the driver writes `isp_zlsctl`
`0x00140008` and the bases into the render details itself.

With a mid-frame flush the scene's flushed kicks (geometry flags `0x60`, render flags 0) carry no
patch and the scene's closing render the six. The pairs' addresses are render details words in
every run: no pair names another structure.

**What it shows.**

- The 3D patches are how the closed driver puts a surface's ZLS state into the render: the full
  set once, at the first render that uses the buffer, then only the control word [CAP].
- The order is fixed: control, request base, the two depth bases, the two stencil bases [CAP].
- Between frames the driver also writes the render details' own `isp_zlsctl` (`0x0011700a`,
  E335), which the next render's patch overrides; what reads the unpatched word is not shown
  [CAP; Q088].
