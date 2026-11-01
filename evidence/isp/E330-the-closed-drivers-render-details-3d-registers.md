+++
id = "E330"
claim = "Over every closing kick of the closed GLES2 stack's 3D captures the render details' 52-word 3D register block holds the same value in 24 words whatever the state, size or program (among them CR_ISP_CTL 0xf0000, CR_REG_0400 0x80, CR_REG_0800 0x30, CR_ISP_BGOBJDEPTH 1.0 and CR_ISP_BGOBJVALS 0x300 even with a clear depth of 0.5, CR_ISP_SAMPLE_POS 0 even under 4x multisampling, 0x04e8 0x100, 0x04dc 0, 0x0148 0 and the second colour-space set and luma key 0), and the other 28 move only with an address, the scene's buffers, a depth or stencil buffer (the ZLS words, also by 3D patches), the polygon offset (its factor and units as given), 4x multisampling (CR_ISP_MSAA 0x80000002, CR_ISP_MULTISAMPLECTL 0xeaa26e26), a YUV stream (the first colour-space set, or the USSE coefficients for NV12), a render to a texture (0x04c4 bit 8) or the parameter buffer's size (0x04c4 bits 19:12)"
unit = "isp"
method = "the render details each closing kick of the closed GLES2 stack names (TA command dword 14), read at the kick with harness/ukernel-extract/state3d.py (kick3d.py's REGISTER_3D_WRITES layout) with the 3D patches of the command (state3d.py upd.*), over the render, isp, texture, usse and ta capture tables (629 closing kicks); our run render-closed-compare reads the same registers back on the laptop, and the spread of each word over the runs tabulated"
tiers = ["CAP", "HW"]
date = "2026-11-03"
data = ["render-state-variations", "render-draws-frames-pb", "render-register-gaps", "isp-registers", "isp-line-width", "texture-textures", "texture-samplers", "texture-formats", "texture-streams", "usse-inputs", "usse-gles1-programs", "usse-shaders", "ta-target-sizes", "render-closed-compare"]
terms = [
    "CR_ISP_CTL", "CR_REG_0400", "CR_REG_0800", "CR_ISP_BGOBJDEPTH", "CR_ISP_BGOBJVALS",
    "CR_ISP_SAMPLE_POS", "CR_ISP_MSAA", "CR_ISP_MULTISAMPLECTL", "CR_ISP_REG_04E8",
    "CR_ISP_ZLSCTL", "CR_ISP_POLY_OFFSET_FACTOR", "CR_TPU_YUV_CSC0_0", "CR_ISP_REGION_HEADER_BASE",
    "CR_ISP_PARTIAL_REGION_BASE", "CR_ISP_POLY_OFFSET_UNITS", "cmd_ta.patches_3d",
]
+++

**What runs.** 629 closing kicks of the closed stack under the harness: one GL state change per
run (variations3d.txt), draws, flushes, frames and kept depth (track3d.txt), polygon offset,
multisampled render to texture and ZLS (gaps3d.txt), translucency, discard, alpha to coverage
and line widths (isp3d.txt, lines3d.txt), textures, samplers, formats and YUV streams, uniform
and attribute layouts, GLES1 fixed function, 102 single-feature shaders and 222 target sizes
from 1x1 to 4096x4096. The render details are the client's (no firmware runs), read when the
kick is made.

**Results.** The 52 words of the render details' register block (state3d.py's names):

| words | value in every closing kick |
|---|---|
| `bif_3d_req_base` | 0xc0000000 (the parameter heap) |
| `reg_0400` | 0x80, an RGB565 or an RGBA8888 target alike |
| `isp_ctl` | 0xf0000 |
| `poly_offset_clamp`, `reg_0148`, `isp_reg_04dc`, `isp_sample_pos` | 0 |
| `isp_bgobjdepth`, `isp_bgobjvals` | 0x3f800000, 0x300 |
| `reg_0800` | 0x30 |
| pixel-event data size, info | 5, 1 |
| `isp_line_sample_pos` | 1 |
| `isp_reg_04e8` | 0x100 |
| `tpu_yuv_csc0_4`, the second colour-space set (`csc1_0`-`csc1_4`), `tpu_yuv_csc_input`, the three luma-key words | 0 |

| words | what moves them |
|---|---|
| `isp_region_header_base`, `isp_partial_region_base`, pixel-event code | the scene's buffers (E325) |
| `isp_zlsctl`, `bif_zls_req_base`, z and stencil load and store bases | a depth or stencil buffer: 0 without, the command's 3D patches with (six on a scene's first render, one after), and a value in the render details itself where a depth buffer is kept across frames or a texture target has one |
| `poly_offset_factor`, `poly_offset_units` | glPolygonOffset, the factor as a float and the units as an integer (1.0 and 1 give 0x3f800000 and 1; -1 and -1 give 0xbf800000 and 0xffffffff) |
| `isp_msaa`, `isp_multisamplectl` | 0x80000002 and 0xeaa26e26 on a 4x multisampled texture target (2 and 4 samples asked alike) |
| `tpu_yuv_csc0_0`-`csc0_3` | a packed YUV stream (fuyvy, fyuyv): 0x950095, 0x95, 0x10203ce, 0x39800cc |
| the nine USSE coefficient words and their mode | an NV12 stream: the mode 3 and nine values |
| `reg_04c4` | 0x2046400; 0x2046500 (bit 8) when the scene renders to a texture; 0x200a400 with a 98-page parameter buffer (both PBSize runs) |

- `CR_ISP_BGOBJDEPTH` stays 1.0 with glClearDepthf(0.5) (depth_less_cd05), and the background
  values stay 0x300 with every clear colour: the closed driver draws its clears as geometry
  (E324) and never moves the background object's depth or tag.
- `CR_ISP_SAMPLE_POS` is 0 in every kick, the 4x multisampled ones included.
- On the laptop our one-triangle render leaves 0x04c4 at 0x46400 and 0x0520 at 0, and every
  other render-details register in 0x0400-0x0560 at its render-details word (render-closed-compare;
  E326).

**What it shows.**

- Of the render details' register block, the closed driver's values for every state captured
  are the 24 constants above plus a short list of moving words, each tied to one feature
  [CAP]. A render of ours that copies the constants matches the closed driver everywhere but
  where E326 says.
- No GL state captured sets `CR_ISP_SAMPLE_POS`, the second colour-space set, the luma key,
  0x04dc or 0x0148; their meaning cannot come from the closed driver's GLES use.
- 0x04c4 carries at least two fields: bit 8 with a texture target and bits 19:12 that move with
  the parameter buffer's size (0x46 at 0x422 pages, 0x0a at 0x62); bit 25 is always set (Q085).
