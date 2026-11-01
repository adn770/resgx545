+++
id = "E328"
claim = "In every TA command of the closed GLES1 and GLES2 stacks the size word is 0x2a8 plus 8 per 3D patch rounded up to 64 bytes (0x2c0 for none or one, 0x300 for six) and the commands lie back to back in the client CCB; dwords 5 and 6 both hold 0x50000000, the four threshold words are 0, dword 16 holds the RT data set and dword 18 0; the shared block names seven TA and three 3D status updates and, on the closing kick only, the 3D transfer-queue sync; and of the TA register block's 28 words the zero-word registers are 0 in every run, and the rest hold, for a single-sampled target, the values our tri job writes: CR_TE_AA 0x20000000, CR_MTE_CTRL 0xa2, the 1/w floats 0x358637bd, CR_MTE_MULTISAMPLECTL 0x88, the tiling words by the size rule, CR_PPP_SCREEN (w - 1) | (h - 1) << 16, the region header base the render details also name and the TE tail pointer cache"
unit = "ta"
method = "the TA command of every kick of the closed GLES1 and GLES2 stacks under the harness (the render, isp, texture and usse capture tables: 412 first or middle kicks and 407 closing kicks), read with harness/ukernel-extract/state3d.py (kick3d.py's cmd_ta layout) and its spread over the runs tabulated; the CCB offsets from the bridge input (kick3d.py PVRSRV_BRIDGE_IN_DOKICK); our tri job's words from userspace/libsgxfive/src/render.c (render_cmd)"
tiers = ["CAP"]
date = "2026-11-03"
data = ["render-state-variations", "render-draws-frames-pb", "render-register-gaps", "isp-registers", "isp-line-width", "texture-textures", "texture-samplers", "texture-formats", "texture-streams", "usse-inputs", "usse-gles1-programs", "usse-shaders"]
terms = [
    "cmd_ta.size", "cmd_ta.num_vertex_partitions", "cmd_ta.ta_threshold",
    "cmd_ta.num_patches_3d", "cmd_ta.patches_3d", "cmd_ta.hw_rt_data_dev_vaddr",
    "cmd_ta.shared", "CR_TE_AA", "CR_MTE_CTRL", "CR_MTE_RHW_MIN", "CR_MTE_MULTISAMPLECTL",
    "CR_TE_MTILE1", "CR_TE_MTILE2", "CR_TE_SCREEN", "CR_TE_MACROTILE_STRIDE", "CR_PPP_SCREEN",
    "CR_TE_PSGREGION_ADDR", "CR_TE_PSG", "CR_VDM_CTRL_STREAM_BASE", "CR_TE_TPC_ADDR",
    "CR_BIF_TA_REQ_BASE", "CR_MTE_RHW_CLAMP", "CR_ISP_REGION_HEADER_BASE",
]
+++

**What runs.** Twelve capture tables of the closed stack under the harness, 373 runs that kick: the
state variations, the draws, flushes and frames, the render-details gaps, the ISP registers and
line widths, textures, samplers, formats and YUV streams, uniform and attribute layouts, GLES1
fixed function and 102 shaders. Each kick's TA command is read from the client CCB at the
offset the bridge input names, at the kick.

**Results.**

- **Header.** `size` is 0x2c0 in every command with no or one 3D patch and 0x300 with six:
  the patch pairs start at byte 0x2a8, and the size is that plus 8 per patch rounded up to a
  multiple of 0x40. Each command starts where the previous one ends (CCB offsets 0x58, 0x318,
  0x618, 0x8d8 in a run whose second command has six patches).
- **Words 2 to 21.** The PDS background-object words (dwords 2-4) as the background object
  record gives them; dwords 5 and 6 0x50000000 in every command; dword 8, the frame number, 0
  but for one render (E324); the PB descriptor (dword 9); the four thresholds (dwords 10-13) 0;
  the render details (14), the destination sync list (15), the RT data set's address (16), the
  RT data (17: the set plus 0x50, or plus 0x18 for the other scene of a pair, E325), dword 18 0,
  the depth and stencil strides (19, 20) 0, the 3D patch count (21: 0, 1 or 6).
- **Shared block.** Control flags 1, seven TA and three 3D status updates (E324), no source
  sync, no TA-to-3D dependency, the TA transfer-queue syncs 0; the 3D transfer-queue write and
  read completion addresses (a SYNCINFO object's +0x4 and +0xc) on the closing kick only.
- **TA register block.** Over all 819 kicks:

| register | values |
|---|---|
| `CR_TE_AA` | 0x20000000; 0xe0000000 with a 4x multisampled target |
| `CR_TE_MTILE1`, `CR_TE_MTILE2`, `CR_TE_MACROTILE_STRIDE`, `CR_TE_SCREEN` | by size (E331); 0x802002, 0x802002, 0x4 with 4x multisampling |
| `CR_TE_PSG` | 0; 0x400000 on the closing kick; plus 0x2000000 with a depth or stencil buffer |
| `CR_VDM_CTRL_STREAM_BASE` | where the kick's stream starts (E324) |
| `CR_MTE_CTRL` | 0xa2 |
| `CR_TE_PSGREGION_ADDR` | the render details' `CR_ISP_REGION_HEADER_BASE` of the same scene |
| `CR_TE_TPC_ADDR` | a 0x100-byte TA data object of the render target |
| `CR_MTE_RHW_MIN`, its clamp | 0x358637bd (1e-6) both |
| `CR_PPP_SCREEN` | (w - 1) \| (h - 1) << 16 |
| `CR_BIF_TA_REQ_BASE` | 0xc0000000, the parameter heap's base |
| `CR_MTE_MULTISAMPLECTL` | 0x88; 0xeaa26e26 with 4x multisampling |
| the zero-word registers (0x02a8, 0x02b0, 0x02b4, 0x02d0, 0x02d4, 0x0324, 0x0364, 0x0368, 0x0370, 0x0374, 0x0a04, 0x0aa0, 0x074c) | 0 |

- Our tri job (render.c) writes the same TA register values for a 64x64 target: TE_AA, MTE_CTRL,
  the two 1/w floats, the screen words, MTE_MULTISAMPLECTL and the tiling words by the same
  rule; our TA command leaves the zero-word registers 0 as well.

**What it shows.**

- The closed driver never loads a nonzero value into any of the zero-word TA registers, in any
  state, size or frame captured: those registers stay unexplained by the client's use [CAP].
- The TA command's thresholds are unused by the closed client (the descriptor carries them,
  E327); dwords 5 and 6 carry the same constant, so dword 6 is either a copy the firmware never
  reads or a field the client fills with the same partition word.
- The command's size is a 64-byte-rounded length that grows with the 3D patch list, so a
  command with more than one patch takes a larger CCB slot [CAP].
- Our tri job's TA register values are the closed driver's for a plain triangle [CAP].
