+++
id = "E335"
claim = "With depth or stencil on, the closed driver gives the window surface one GENERAL allocation of 0x5000 bytes, depth at its start (64 x 64 four-byte values) and stencil 0x4000 on, loaded and stored at the same addresses in every frame: the render flags carry 0x180 (DEPTH_BUFFER and STENCIL_BUFFER) whichever of the two GL uses, the first render of the surface names the buffer, and a later frame's render loads what the earlier stored; with ExternalZBufferMode=2 the buffer is set up with the context and loaded from the first render, and ExternalZBufferMode=1 and ZLSThreshold=0 change no word"
unit = "zls"
method = "the render-draws-frames-pb capture (depth less over two frames cleared each frame and cleared once, stencil and depth with stencil over two frames, and the app hints ExternalZBufferMode=1 and 2 and ZLSThreshold=0) and the render-register-gaps capture (depth with a mid-frame flush, two frames, a texture with a depth attachment), read with harness/ukernel-extract/state3d.py: per kick the TA command's flags and 3D patches (upd.*), the render details' ZLS registers and the snapshot's allocations"
tiers = ["CAP"]
date = "2026-11-03"
data = ["render-draws-frames-pb", "render-register-gaps"]
terms = [
    "cmd_ta.frag_flags", "FRAG_FLAGS.DEPTH_BUFFER", "FRAG_FLAGS.STENCIL_BUFFER", "FRAG_FLAGS.BIT10",
    "CR_ISP_ZLSCTL", "CR_ISP_ZLOAD_BASE", "CR_ISP_ZSTORE_BASE", "CR_ISP_STENCIL_LOAD_BASE",
    "CR_ISP_STENCIL_STORE_BASE", "CR_BIF_ZLS_REQ_BASE", "cmd_ta.zls_threshold",
]
+++

**What runs.** A frame is a geometry kick and a render kick (render flags with `0x400`); two frames
are four kicks. The render details are the closed driver's memory: the harness completes each
kick without running the firmware, so they hold what the driver wrote, and the 3D patches of each
TA command are what the EDM would store into them before the render (E336).

**Results.** The ZLS words of the two-frame depth run (depth less, cleared each frame).

| kick | render flags | patches | `CR_ISP_ZLSCTL` | depth, stencil load and store bases |
|---|---|---|---|---|
| 0 geometry | 0 | 0 | 0 | 0 |
| 1 render | `0x580` | 6 | patched to `0x0017100c` | patched: `0xf6000`, `0x800fa000` |
| 2 geometry | `0x180` | 0 | the driver writes `0x0011700a` | the same |
| 3 render | `0x580` | 1 | patched to `0x0017700e` | the same |

- Cleared once, stencil only (always, 1), depth and stencil, and depth with ExternalZBufferMode=1
  or with ZLSThreshold=0: the same flags, patches and words. The TA command's `zls_threshold` is
  0 in every kick.
- ExternalZBufferMode=2: the render details hold `CR_ISP_ZLSCTL` `0x0017300e`, bases `0x8a000`
  and `0x8008e000` and `CR_BIF_ZLS_REQ_BASE` `0x08000000` from the first kick on, the first render
  has render flags `0x580` and one patch (`0x0017700e`), the second none.
- The depth allocation is `0x080f6000` (`0x0808a000` with ExternalZBufferMode=2), `0x5000`
  bytes, in the GENERAL heap; the bases are its address less `CR_BIF_ZLS_REQ_BASE`
  (`0x08000000`), the stencil one `0x4000` further with bit 31 set.
- A texture with a depth attachment has its own `0x4000`-byte allocation (`0x080f5000`), render
  flags `0x80` and `0x480` (depth only), `CR_ISP_ZLSCTL` `0x00140008` written by the driver in
  both frames and no patch.

**What it shows.**

- The window's depth and stencil share one allocation, four bytes a depth value and one byte a
  stencil value, and the closed driver turns on both ZLS flags for either [CAP].
- Depth is kept across frames at one address: the first frame's render stores, the second loads
  the same buffer (the load bits of E337) whether or not it clears, the clear being drawn (E332)
  [CAP].
- The ZLS bases are offsets from `CR_BIF_ZLS_REQ_BASE`, not device addresses [CAP; that the BIF
  adds the request base: infer from the name, no hardware run here].
- `ExternalZBufferMode=2` moves the buffer's setup to the context and loads at the first render;
  value 1 and `ZLSThreshold=0` change nothing in these scenes [CAP].
