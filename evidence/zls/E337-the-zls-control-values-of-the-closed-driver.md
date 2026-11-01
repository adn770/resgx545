+++
id = "E337"
claim = "The closed driver's CR_ISP_ZLSCTL values are 0x0017100c for a window surface's first render (bits 2, 3, 12, 16-18, 20), 0x0017700e for every later one (bits 1, 13 and 14 added), 0x0017300e set with the context under ExternalZBufferMode=2 (bits 1 and 13 added, 14 not), 0x0011700a written between frames (bits 2, 17 and 18 cleared from 0x0017700e) and 0x00140008 for a texture's depth attachment (bits 3, 18, 20; depth flag only); so bits 1, 13 and 14 are what a render that loads the kept buffer adds, and bits 2, 12, 16 and 17 are absent with the depth flag alone"
unit = "zls"
method = "the render-draws-frames-pb, render-register-gaps and isp-registers captures, read with harness/ukernel-extract/state3d.py: CR_ISP_ZLSCTL in each render's 3D patches and in the render details at each kick, beside the render flags"
tiers = ["CAP"]
date = "2026-11-03"
data = ["render-draws-frames-pb", "render-register-gaps", "isp-registers"]
terms = [
    "CR_ISP_ZLSCTL", "FRAG_FLAGS.DEPTH_BUFFER", "FRAG_FLAGS.STENCIL_BUFFER", "cmd_ta.patches_3d",
]
+++

**What runs.** E335 and E336 give where each value appears. The values, by bit:

| value | where | bits set |
|---|---|---|
| `0x0017100c` | first render, render flags `0x180` (patch) | 2, 3, 12, 16, 17, 18, 20 |
| `0x0017700e` | later renders; ExternalZBufferMode=2's first (patch) | 1-3, 12-14, 16-18, 20 |
| `0x0017300e` | ExternalZBufferMode=2, written with the context | 1, 2, 3, 12, 13, 16, 17, 18, 20 |
| `0x0011700a` | written between frames, before the next geometry kick | 1, 3, 12, 13, 14, 16, 20 |
| `0x00140008` | a texture's depth attachment, render flags `0x80` | 3, 18, 20 |

**What it shows.**

- A render that follows a stored render of the same buffer, cleared or not, adds bits 1, 13 and 14
  to the first render's value: these are the load bits the driver uses [CAP]. Which of them loads
  depth and which stencil is not shown: every window render here has both flags.
- With the depth flag alone (the texture's attachment) bits 2, 12, 16 and 17 of the first
  render's value are absent and the rest kept, so those four go with the stencil flag in the
  driver's values; the 3D kick's own adjustment for a clear stencil flag (§11.5) removes only
  `0x22000` (bits 13 and 17), so the driver chooses the others itself [CAP for the values; the
  bit-to-flag reading: infer from one texture case].
- Bits 3 and 20 are in every value with a buffer [CAP].
- The between-frames word lacks bits 2, 17 and 18 of the later renders' value; what reads it is
  open (Q088).
