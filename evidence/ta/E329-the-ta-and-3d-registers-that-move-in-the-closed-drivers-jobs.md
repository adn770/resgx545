+++
id = "E329"
claim = "Across the closed GLES1 and GLES2 stacks' 3D captures (819 kicks of 12 capture tables, and the target sizes) the TA register block moves in eight registers and three address words only: CR_TE_SCREEN, CR_PPP_SCREEN, CR_TE_MTILE1, CR_TE_MTILE2 and CR_TE_MACROTILE_STRIDE with the target's size and with 4x multisampling, CR_TE_AA and CR_MTE_MULTISAMPLECTL with 4x multisampling, CR_TE_PSG with the scene's close and a depth or stencil buffer, and the three address words (control stream, region headers, tail pointer cache) with the kick and the scene; the 3D side moves as E330 lists; GEOM_FLAGS and FRAG_FLAGS move with the kick's place in the scene, a depth or stencil buffer and a render to a texture"
unit = "ta"
method = "every kick of the closed GLES1 and GLES2 stacks under the harness (render, isp, texture and usse capture tables: 412 first or middle kicks and 407 closing kicks; ta-target-sizes for the size words), each TA command and the render details it names read with harness/ukernel-extract/state3d.py, and the spread of each word over the runs tabulated by first or middle against closing kick"
tiers = ["CAP"]
date = "2026-11-03"
data = ["render-state-variations", "render-draws-frames-pb", "render-register-gaps", "isp-registers", "isp-line-width", "texture-textures", "texture-samplers", "texture-formats", "texture-streams", "usse-inputs", "usse-gles1-programs", "usse-shaders", "ta-target-sizes"]
terms = [
    "CR_TE_SCREEN", "CR_PPP_SCREEN", "CR_TE_MTILE1", "CR_TE_MTILE2", "CR_TE_MACROTILE_STRIDE",
    "CR_TE_AA", "CR_MTE_MULTISAMPLECTL", "CR_TE_PSG", "CR_VDM_CTRL_STREAM_BASE",
    "CR_TE_PSGREGION_ADDR", "CR_TE_TPC_ADDR", "GEOM_FLAGS.FIRST_KICK", "GEOM_FLAGS.LAST_KICK",
    "FRAG_FLAGS.DEPTH_BUFFER", "FRAG_FLAGS.STENCIL_BUFFER", "FRAG_FLAGS.BIT10",
]
+++

**What runs.** The twelve capture tables of the closed stack under the harness (one GL state
change per run; draws, flushes and frames; render-details gaps; ISP states and line widths;
textures, samplers, formats and YUV streams; uniform and attribute layouts; GLES1 fixed
function; 102 shaders), and the 225 sizes of sizes3d.txt (222 that kick) for the tiling words
(E331).

**Results.** The TA register block, over the 819 kicks:

| register | moves with | values |
|---|---|---|
| `CR_TE_SCREEN`, `CR_PPP_SCREEN` | the target's size | E331 |
| `CR_TE_MTILE1`, `CR_TE_MTILE2`, `CR_TE_MACROTILE_STRIDE` | the size; 4x multisampling | E331; 0x802002, 0x802002, 0x4 at 64x64 |
| `CR_TE_AA` | 4x multisampling | 0x20000000; 0xe0000000 |
| `CR_MTE_MULTISAMPLECTL` | 4x multisampling | 0x88; 0xeaa26e26 |
| `CR_TE_PSG` | the closing kick; a depth or stencil buffer | 0, 0x400000; 0x2000000, 0x2400000 |
| `CR_VDM_CTRL_STREAM_BASE` | every kick | where its stream starts (E324) |
| `CR_TE_PSGREGION_ADDR` | the scene, the render target | the scene's region headers (E325) |
| `CR_TE_TPC_ADDR` | the render target | its tail pointer cache |

The other 17 words of the block hold one value in every kick (E328): four nonzero constants
and 13 zero-word registers (0).

The flag words (TA command dwords 1 and 7):

| word | first kick | middle kick | closing kick |
|---|---|---|---|
| GEOM_FLAGS | 0x71 on a context's first, 0x61 after | 0x60 | 0x62 |
| FRAG_FLAGS | 0; 0x180 or 0x80 with a depth buffer kept | 0 | 0x400; 0x580 with depth and stencil, 0x480 with depth alone (a texture target's depth renderbuffer) |

- `FRAG_FLAGS.DEPTH_BUFFER` and `STENCIL_BUFFER` (0x80, 0x100) are set together on every scene
  whose window has a depth buffer (the GLES1 runs' default configuration, the depth and stencil
  state variations, gl_FragCoord in a shader); a texture target with a depth renderbuffer alone
  sets `DEPTH_BUFFER` only. Before the closing kick they appear on the kicks of a texture target
  with a depth renderbuffer (0x80), on the first kick of a second frame whose depth is kept
  (0x180: depth_f2 and the external-Z runs' second frames), and on the first kick of
  ExternalZBufferMode=2 (0x180); `CR_TE_PSG` bit 25 is set on exactly those 15 kicks.
- No state, size or program captured moves any other TA register or command flag.

**What it shows.**

- The closed driver's TA setup is the same in every job but for the size, 4x multisampling and
  the scene's buffers: a job of ours needs per-job values in eight TA registers, three address
  words and the flags, and constants everywhere else [CAP].
- `CR_TE_PSG` bit 25 goes with `FRAG_FLAGS.DEPTH_BUFFER` or `STENCIL_BUFFER` on the same kick:
  the TA learns of a depth or stencil buffer from both words [CAP].
