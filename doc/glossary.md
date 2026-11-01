<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
# SGX545 glossary: names and where they come from

*Generated from `glossary/` by `tools/clean-room/glossary.py`; do not edit.*

Every name this project uses for an SGX545 register, firmware structure or field, state-word field,
flag, function, unit or concept must have an open source. This is the list of names that do, each
with the source spellings that support it; its record (`glossary/<group>/<NAME>.toml`) also gives
the citation, the licence and the evidence that ties a name from another core or from Rogue to
SGX545. An external source is cited by a citation record (`citations/<source>/C<nnnn>-*.md`: the
place in the upstream source, a link to it at the pinned version and the line quoted); our own terms
cite our evidence records. Nothing read from inside a closed binary is a source of a name; a string
or exported symbol seen from outside, as a black box, may back one (tier 2; HACKING.md, "Sources").
A thing with no name here gets a descriptive name of our own.

Tiers:

- **1**: the original spelling in open SGX code (GPL or MIT kernel sources, Intel's register list),
  applying to SGX545 directly or at the same offset.
- **1c**: as 1, from another SGX core: the evidence says which, and whether the offset matches.
- **2**: a string or exported symbol of our own Cedarview package, observed as a black box.
- **3**: Imagination's open Rogue code (Linux, Mesa): the same function on the descendant core; an
  analogy, not SGX545's own spelling.
- **4**: Imagination's public SGX documents and patents: unit and concept names.
- **ours**: our own term for a thing no open source names, after what we measured (the citation
  points into this repository); an inference, marked [infer].

Our terms have one form per kind: registers `UNIT_NAME` and their fields `REG.FIELD`; firmware
structures and their fields `lower_snake`, as `struct.field`; state-word fields `WORD.FIELD`; flags
and enums `FAMILY.VALUE`; units and concepts in words. Source prefixes (`EUR_CR_`, `PSB_CR_`,
`ROGUE_CR_`, `SGXMKIF_`, `ui32`...) are never part of our term; exported functions keep their exact
symbol. Each entry lists the source spellings behind it, best tier first.

## 1. Units and concepts

### concept

- `Parameter Buffer (PB)` G0064: memory holding the binned scene (TA output, 3D input). From `PB`
  (4, imgtec-sgx-arch-guide-1.0.13); `Parameter Buffer` (4, imgtec-sgx-arch-guide-1.0.8).
- `Tile Based Deferred Rendering (TBDR)` G0068: bin the whole scene first, then render tile by tile,
  shading only visible pixels. From `TBDR` (4, imgtec-sgx-arch-guide-1.0.13).
- `display list` G0070: per-tile display lists (macrotiles). From `display list` (4,
  patent-US7324115).
- `programmable sample positions` G0333: the samples' positions within the pixel are programmable
  (with 4x multisampling). From `programmable sample positions` (4, ti-omap4430-trm).
- `terminate bounding box` G0334: the screen region outside which tiles are invalid: they are not
  processed at the end of the scene. From `terminate bounding box` (4, patent-US9384584).
- `tile` G0335: 32x16 pixels, two adjacent 16x16 tiles, as the TE writes the control stream. From
  `tile` (4, patent-US8723860).
- `video processor` G0341: the video-processing functions DirectX VA 2 and VA-API ask of a GPU,
  which SGX545 implements in its texture unit and its USE filter block: the YUV-to-RGB transfer
  matrix (CR_TPU_YUV_CSC0/1_*), the nominal range and chroma signedness (CR_TPU_YUV_CSC_INPUT), the
  luma key (CR_TPU_LUMA_KEY_*), codec interpolation, smoothing and difference filters
  (CR_USE_COEFFS*, CR_USE_COEFFS_MODE); ProcAmp folds into the matrix coefficients [infer]. From
  `video processor` (ours, resgx545).

### unit

- `Dynamic Parameter Management (DPM)` G0062 (CR_CLKGATECTL.DPM_CLKG): DPM block (its clock gate).
  From `DPM` (1, sgx545-ce); `Parameter Manager` (3, linux-imagination); `DPM` (4,
  patent-US8669987).
- `Image Synthesis Processor (ISP)` G0063 (CR_CLKGATECTL.ISP_CLKG): ISP block (its clock gate). From
  `ISP` (1, sgx545-ce); `ISP` (4, imgtec-sgx-arch-guide-1.0.13); `Hidden Surface Removal unit` (4,
  patent-US8743117).
- `Pixel Back End (PBE)` G0065 (CR_EVENT_STATUS.PIXELBE_END_RENDER): PBE as spelled in register
  names; signals end of render. From `PIXELBE` (1, sgx545-ce); `PBE` (4,
  imgtec-sgx-arch-guide-1.0.13); `Pixel Back End` (4, powervr-docs); `pixel coprocessor` (4,
  ti-omap4430-trm).
- `Texture and Shading Processor (TSP)` G0066 (CR_CLKGATECTL.TSP_CLKG): TSP block (its clock gate).
  From `TSP` (1, sgx545-ce); `TSP` (4, imgtec-sgx-arch-guide-1.0.13).
- `Tile Accelerator (TA)` G0067 (CR_SOFT_RESET.TA_RESET): TA block (its soft reset). From `TA` (1,
  sgx545-ce); `TA` (4, imgtec-sgx-arch-guide-1.0.13); `Tile Accelerator` (4,
  imgtec-technology-overview-1.0.2e).
- `Universal Scalable Shader Engine (USSE)` G0069 (CR_SOFT_RESET.USE_RESET): USSE block (its soft
  reset); register names use the short abbreviation. From `USE` (1, sgx545-ce); `USSE` (4,
  imgtec-sgx-arch-guide-1.0.8).
- `Z Load Store (ZLS)` G0301 (CR_BIF_ZLS_REQ_BASE): ZLS memory requester (its BIF requestor base).
  From `ZLS` (1, sgx545-ce); `Z load store` (4, imgtec-pvrtune-counters).

## 2. Registers and their fields

### bitfield

- `CR_EVENT_STATUS.TPC_FLUSH` G0351 (0x012c[10]): status: tail-pointer cache flush done. From
  `EUR_CR_EVENT_STATUS_TPC_FLUSH` (1, sgx545-ce).
- `CR_EVENT_STATUS.SW_EVENT` G0092 (0x012c[14]): status: software event. From
  `EUR_CR_EVENT_STATUS_SW_EVENT` (1, sgx545-ce).
- `CR_EVENT_STATUS.OTPM_INV` G0350 (0x012c[20]): status: OTPM invalidated. From
  `EUR_CR_EVENT_STATUS_OTPM_INV` (1, sgx545-ce).
- `CR_EVENT_STATUS.ISP2_ZLS_CSW_FINISHED` G0349 (0x012c[21]): status: second ISP finished a ZLS
  context switch. From `EUR_CR_EVENT_STATUS_ISP2_ZLS_CSW_FINISHED` (1, sgx545-ce).
- `CR_EVENT_STATUS.DPM_INIT_END` G0347 (0x012c[22]): status: DPM initialisation finished. From
  `EUR_CR_EVENT_STATUS_DPM_INITEND` (1, sgx545-ce).
- `CR_EVENT_STATUS.DPM_STATE_STORE` G0348 (0x012c[4]): status: DPM state store done. From
  `EUR_CR_EVENT_STATUS_DPM_STATE_STORE` (1, sgx545-ce).
- `CR_EVENT_STATUS.DPM_CONTROL_STORE` G0346 (0x012c[7]): status: DPM control store done. From
  `EUR_CR_EVENT_STATUS_DPM_CONTROL_STORE` (1, sgx545-ce).
- `CR_EVENT_STATUS.DPM_CONTROL_LOAD` G0345 (0x012c[8]): status: DPM control load done. From
  `EUR_CR_EVENT_STATUS_DPM_CONTROL_LOAD` (1, sgx545-ce).
- `CR_EVENT_STATUS.DPM_CONTROL_CLEAR` G0344 (0x012c[9]): status: DPM control clear done. From
  `EUR_CR_EVENT_STATUS_DPM_CONTROL_CLEAR` (1, sgx545-ce).
- `CR_TE_SCREEN.LAST_TILE_X` G0160 (0x0210 from bit 0 (width open)): x of the screen's last tile, in
  tiles from 0 [infer]. From `CR_TE_SCREEN.LAST_TILE_X` (ours, resgx545).
- `CR_TE_SCREEN.LAST_TILE_Y` G0161 (0x0210 from bit 12 (width open)): y of the screen's last tile,
  in tiles from 0 [infer]. From `CR_TE_SCREEN.LAST_TILE_Y` (ours, resgx545).
- `CR_REG_0400.INVERT_BYTE3` G0153 (0x0400[25]): inverts bits 31:24 of every pixel written [infer].
  From `CR_REG_0400.INVERT_BYTE3` (ours, resgx545).
- `CR_ISP_MSAA.MODE` G0123 (0x042c[1:0]): inferred reading (unconfirmed): Bits 1:0 of register
  0x042c: 0 leaves the single-sample image, 1 and 2 each change the 64x64 triangle's image, and 3
  hangs the job; the sample count each value selects is not shown by the pixel counts. From
  `CR_ISP_MSAA.MODE` (ours, resgx545).
- `CR_ISP_MSAA.ENABLE` G0122 (0x042c[31]): enables the multisampled ISP path: with it clear and
  CR_ISP_MSAA.MODE 1-2 the triangle is tiled but no sample is written; the single-sampled path
  ignores it; set in every capture [infer]. From `CR_ISP_MSAA.ENABLE` (ours, resgx545).
- `CR_ISP_MULTISAMPLECTL.SAMPLE0_X` G0125 (0x04c8[3:0]): x of sample 0's position in the pixel, in
  sixteenths of a pixel, 8 the centre [infer]. From `CR_ISP_MULTISAMPLECTL.SAMPLE0_X` (ours,
  resgx545).
- `CR_ISP_MULTISAMPLECTL.SAMPLE0_Y` G0126 (0x04c8[7:4]): y of sample 0's position in the pixel, in
  sixteenths of a pixel, 8 the centre [infer]. From `CR_ISP_MULTISAMPLECTL.SAMPLE0_Y` (ours,
  resgx545).
- `CR_USE_CODE_BASE_0.ADDR` G0006 (0x0a0c[24:0]): code base address. From `_PSB_CUC_BASE_ADDR_MASK`
  (1c, emgd-psb_regs).
- `CR_USE_CODE_BASE_0.DM` G0007 (0x0a0c[26:25]): data master that owns a USE code base. From
  `EUR_CR_USE_CODE_BASE_DM_00` (1, sgx545-ce); `_PSB_CUC_BASE_DM_MASK` (1c, emgd-psb_regs).
- `CR_USE_COEFFS_MODE.MODE` G0204 (0x0a9c[1:0]): 0: a fixed bank of H.264 and MPEG-4 interpolation
  filters for sets 2-5; 1: VC-1's bicubic filters; 2: smoothing filters; 3: set 2 loaded, sets 3-5
  zero (the closed driver's value for NV12) [infer]. From `CR_USE_COEFFS_MODE.MODE` (ours,
  resgx545).
- `CR_PDS_REG_0ABC.BITS4_1` G0150 (0x0abc[4:1]): inferred reading (unconfirmed): the number of PDS
  task slots shared by every data master (E140): 0 leaves none, so every job hangs. Measured: 7 from
  the init script; 0 hangs the next job, any other value changes nothing seen [infer]. From
  `CR_PDS_REG_0ABC.BITS4_1` (ours, resgx545).
- `CR_EVENT_KICK.NOW` G0091 (0x0ac8[0]): write 1 to trigger. From `EUR_CR_EVENT_KICK_NOW` (1,
  sgx545-ce).
- `CR_USE2_SERV_PIXEL.TASK_COUNT` G0184 (0x0b88[15:0]): tasks served, wrapping [infer]. From
  `CR_USE2_SERV_PIXEL.TASK_COUNT` (ours, resgx545).
- `CR_USE2_SERV_PIXEL.EMPTY` G0183 (0x0b88[16]): queue empty [infer]. From
  `CR_USE2_SERV_PIXEL.EMPTY` (ours, resgx545).
- `CR_USE2_SERV_VERTEX.TASK_COUNT` G0187 (0x0b8c[15:0]): tasks served, wrapping [infer]. From
  `CR_USE2_SERV_VERTEX.TASK_COUNT` (ours, resgx545).
- `CR_USE2_SERV_VERTEX.EMPTY` G0186 (0x0b8c[16]): queue empty [infer]. From
  `CR_USE2_SERV_VERTEX.EMPTY` (ours, resgx545).
- `CR_USE3_SERV_PIXEL.TASK_COUNT` G0190 (0x0b94[15:0]): tasks served, wrapping [infer]. From
  `CR_USE3_SERV_PIXEL.TASK_COUNT` (ours, resgx545).
- `CR_USE3_SERV_PIXEL.EMPTY` G0189 (0x0b94[16]): queue empty [infer]. From
  `CR_USE3_SERV_PIXEL.EMPTY` (ours, resgx545).
- `CR_USE3_SERV_VERTEX.TASK_COUNT` G0193 (0x0b98[15:0]): tasks served, wrapping [infer]. From
  `CR_USE3_SERV_VERTEX.TASK_COUNT` (ours, resgx545).
- `CR_USE3_SERV_VERTEX.EMPTY` G0192 (0x0b98[16]): queue empty [infer]. From
  `CR_USE3_SERV_VERTEX.EMPTY` (ours, resgx545).
- `CR_BIF_FAULT.CID` G0342 (0x0c08[3:0]): directory-list index (context) of the fault. From
  `EUR_CR_BIF_FAULT_CID` (1, sgx545-ce).
- `CR_BIF_FAULT.SB` G0343 (0x0c08[8:4]): SB bits of the fault (meaning open). From
  `EUR_CR_BIF_FAULT_SB` (1, sgx545-ce).
- `CR_BIF_BANK0.INDEX_3D` G0088 (0x0c78[15:12]): directory-list index for 3D requests. From
  `EUR_CR_BIF_BANK0_INDEX_3D` (1, sgx545-ce).

### flag

- `CR_TPU_YUV_CSC_INPUT.Y_NO_OFFSET` G0177 (0x0848[0]): the luma taken as is, without the -16 offset
  [infer]. From `CR_TPU_YUV_CSC_INPUT.Y_NO_OFFSET` (ours, resgx545).
- `CR_TPU_YUV_CSC_INPUT.UV_SIGNED` G0176 (0x0848[2]): U and V taken as signed bytes instead of
  offset by 128 [infer]. From `CR_TPU_YUV_CSC_INPUT.UV_SIGNED` (ours, resgx545).

### register

- `CR_CLKGATECTL` G0036 (0x0000): per-unit clock-gating mode control. From `EUR_CR_CLKGATECTL` (1,
  sgx545-ce); `PSB_CR_CLKGATECTL` (1c, emgd-psb_regs); `ROGUE_CR_CLK_CTRL` (3, linux-imagination).
- `CR_CLKGATECTL2` G0037 (0x0004): clock-gating control, second bank. From `EUR_CR_CLKGATECTL2` (1,
  sgx545-ce); `ROGUE_CR_CLK_CTRL2` (3, linux-imagination).
- `CR_CLKGATESTATUS` G0038 (0x0008): per-unit clock-gating state. From `EUR_CR_CLKGATESTATUS` (1,
  sgx545-ce); `ROGUE_CR_CLK_STATUS` (3, linux-imagination).
- `CR_CORE_ID` G0039 (0x001c): core id and configuration. From `EUR_CR_CORE_ID` (1, sgx545-ce);
  `PSB_CR_CORE_ID` (1c, emgd-psb_regs); `EUR_CR_CORE_ID` (1c, sgx545-ce); `ROGUE_CR_CORE_ID` (3,
  linux-imagination).
- `CR_CORE_REVISION` G0040 (0x0020): silicon revision (designer/major/minor/maint). From
  `EUR_CR_CORE_REVISION` (1, sgx545-ce); `PSB_CR_CORE_REVISION` (1c, emgd-psb_regs);
  `EUR_CR_CORE_REVISION` (1c, sgx545-ce); `ROGUE_CR_CORE_REVISION` (3, linux-imagination).
- `CR_SOFT_RESET` G0052 (0x0080): per-unit soft reset bits. From `EUR_CR_SOFT_RESET` (1, sgx545-ce);
  `PSB_CR_SOFT_RESET` (1c, emgd-psb_regs); `ROGUE_CR_SOFT_RESET` (3, linux-imagination).
- `CR_EVENT_HOST_ENABLE2` G0045 (0x0110): host interrupt enable, bank 2. From
  `EUR_CR_EVENT_HOST_ENABLE2` (1, sgx545-ce); `PSB_CR_EVENT_HOST_ENABLE2` (1c, emgd-psb_regs).
- `CR_EVENT_HOST_CLEAR2` G0043 (0x0114): write-1-to-clear events, bank 2. From
  `EUR_CR_EVENT_HOST_CLEAR2` (1, sgx545-ce); `PSB_CR_EVENT_HOST_CLEAR2` (1c, emgd-psb_regs).
- `CR_EVENT_STATUS` G0049 (0x012c): event (interrupt) status, bank 1. From `EUR_CR_EVENT_STATUS` (1,
  sgx545-ce); `PSB_CR_EVENT_STATUS` (1c, emgd-psb_regs); `PSB_EUR_CR_EVENT_STATUS` (1c,
  emgd-psb_regs); `ROGUE_CR_EVENT_STATUS` (3, linux-imagination).
- `CR_EVENT_HOST_ENABLE` G0044 (0x0130): events routed to the host interrupt, bank 1. From
  `EUR_CR_EVENT_HOST_ENABLE` (1, sgx545-ce); `PSB_EUR_CR_EVENT_HOST_ENABLE` (1c, emgd-psb_regs).
- `CR_EVENT_HOST_CLEAR` G0042 (0x0134): write-1-to-clear events, bank 1. From
  `EUR_CR_EVENT_HOST_CLEAR` (1, sgx545-ce); `PSB_CR_EVENT_HOST_CLEAR` (1c, emgd-psb_regs);
  `ROGUE_CR_EVENT_CLEAR` (3, linux-imagination).
- `CR_PDS_CACHE_HOST_ENABLE` G0051 (0x013c): PDS cache event host enable. From
  `PSB_CR_PDS_CACHE_HOST_ENABLE` (1c, emgd-psb_regs).
- `CR_TIMER` G0053 (0x0144): free-running timer. From `EUR_CR_TIMER` (1, sgx545-ce);
  `ROGUE_CR_TIMER` (3, linux-imagination).
- `CR_REG_0148` G0151 (0x0148): inferred reading (unconfirmed): a per-job base address or mode of
  the 3D and transfer paths for a feature these clients leave off. Measured: per-render word the
  host supplies with the 3D registers (transfer command and render details); 0 in captures [infer].
  From `CR_REG_0148` (ours, resgx545).
- `CR_TE_AA` G0158 (0x0204): tiling-engine anti-aliasing word: 0x20000000 in every single-sample
  capture, bits 31 and 30 more (0xe0000000) with 4x multisampling [infer]. From `ROGUE_CR_TE_AA` (3,
  linux-imagination); `ROGUE_CR_TE_AA` (3, mesa-csbgen).
- `CR_TE_SCREEN` G0159 (0x0210): screen size in tiles for the tiling engine (Rogue analogue). From
  `ROGUE_CR_TE_SCREEN` (3, linux-imagination); `ROGUE_CR_TE_SCREEN` (3, mesa-csbgen).
- `CR_MTE_MULTISAMPLECTL` G0145 (0x0230): the sample positions on the TA side: the TA command word
  that loads it carries CR_ISP_MULTISAMPLECTL's value in every capture, 0x88 with one sample,
  0xeaa26e26 with 4x multisampling [infer]. From `ROGUE_CR_PPP_MULTISAMPLECTL` (3, mesa-csbgen).
- `CR_MTE_RHW_MIN` G0147 (0x0240): minimum 1/w: a vertex whose 1/w is not above this value's
  magnitude has 1/w stored as CR_MTE_RHW_CLAMP in the TA's object (1e-6 from the closed driver: w
  beyond 1e6) [infer]. From `CR_MTE_RHW_MIN` (ours, resgx545).
- `CR_MTE_RHW_CLAMP` G0146 (0x0244): the 1/w the TA stores for a vertex at or below CR_MTE_RHW_MIN
  [infer]. From `CR_MTE_RHW_CLAMP` (ours, resgx545).
- `CR_REG_0400` G0152 (0x0400): inferred reading (unconfirmed): a pixel output conversion control:
  bit 25 inverts byte 3 of every pixel written (CR_REG_0400.INVERT_BYTE3), 0x80 the default of the
  other conversions. Measured: per-render word from the render details or transfer command; 0x80 in
  captures [infer]. From `CR_REG_0400` (ours, resgx545).
- `CR_ISP_CTL` G0119 (0x0414): ISP control word of a render; the EDM sets bit 8 (process empty
  tiles) for partial renders (Rogue analogue). From `ROGUE_CR_ISP_CTL` (3, linux-imagination).
- `CR_ISP_LINE_SAMPLE_POS` G0120 (0x0418): bit 0: where lines are sampled, 1 at the pixel centre, 0
  at its far corner (x + 1, y + 1); triangles do not read it; 1 from the closed driver [infer]. From
  `CR_ISP_LINE_SAMPLE_POS` (ours, resgx545).
- `CR_ISP_POLY_OFFSET_UNITS` G0129 (0x041c): the polygon offset's units, as an integer
  (glPolygonOffset units) [infer]. From `CR_ISP_POLY_OFFSET_UNITS` (ours, resgx545).
- `CR_ISP_POLY_OFFSET_FACTOR` G0128 (0x0420): inferred reading (unconfirmed): Register 0x0420,
  loaded from render-details word 6: set to 4.0 with the offset in word 5 at 0 it left the flat
  triangle's stored depth unchanged, so what it multiplies is not shown by a triangle with no depth
  slope. From `CR_ISP_POLY_OFFSET_FACTOR` (ours, resgx545).
- `CR_ISP_POLY_OFFSET_CLAMP` G0127 (0x0424): the polygon offset's clamp, an IEEE single: the offset
  is capped at it, 0 no cap, a negative one leaving positive offsets alone [infer]. From
  `CR_ISP_POLY_OFFSET_CLAMP` (ours, resgx545).
- `CR_ISP_MSAA` G0121 (0x042c): ISP multisample control: bits 1:0 the mode (CR_ISP_MSAA.MODE), bit
  31 the multisample path's enable (CR_ISP_MSAA.ENABLE) [infer]. From `CR_ISP_MSAA` (ours,
  resgx545).
- `CR_ISP_ZLSCTL` G0143 (0x0480): depth/stencil load-store (ZLS) control (Rogue analogue). From
  `ROGUE_CR_ISP_ZLSCTL` (3, mesa-csbgen).
- `CR_ISP_ZLOAD_BASE` G0142 (0x0484): depth load base: where ZLS loads the depth buffer from, an
  offset from the ZLS requester base [infer]. From `CR_ISP_ZLOAD_BASE` (ours, resgx545).
- `CR_ISP_ZSTORE_BASE` G0144 (0x0488): depth store base: where ZLS stores the depth buffer, IEEE
  singles, an offset from the ZLS requester base [infer]. From `CR_ISP_ZSTORE_BASE` (ours,
  resgx545).
- `CR_ISP_STENCIL_LOAD_BASE` G0133 (0x048c): stencil load base, an offset from the ZLS requester
  base; bit 31 set with a stencil buffer [infer]. From `CR_ISP_STENCIL_LOAD_BASE` (ours, resgx545).
- `CR_ISP_STENCIL_STORE_BASE` G0134 (0x0490): stencil store base (bits 30:0, an offset from the ZLS
  requester base) and its enable (bit 31) [infer]. From `CR_ISP_STENCIL_STORE_BASE` (ours,
  resgx545).
- `CR_ISP_VISIBILITY_CTRL` G0141 (0x0494): visibility-test control: the EDM writes 0xff before each
  render and after it reads the counters [infer]. From `CR_ISP_VISIBILITY_CTRL` (ours, resgx545).
- `CR_ISP_VISIBILITY_COUNT0` G0135 (0x0498): visibility counters 0 and 1, one per 16-bit half,
  accumulated by the EDM into the visibility results [infer]. From `CR_ISP_VISIBILITY_COUNT0` (ours,
  resgx545).
- `CR_ISP_VISIBILITY_COUNT1` G0136 (0x049c): visibility counters 2 and 3, one per 16-bit half,
  accumulated by the EDM into the visibility results [infer]. From `CR_ISP_VISIBILITY_COUNT1` (ours,
  resgx545).
- `CR_ISP_VISIBILITY_COUNT2` G0137 (0x04a0): visibility counters 4 and 5, one per 16-bit half,
  accumulated by the EDM into the visibility results [infer]. From `CR_ISP_VISIBILITY_COUNT2` (ours,
  resgx545).
- `CR_ISP_VISIBILITY_COUNT3` G0138 (0x04a4): visibility counters 6 and 7, one per 16-bit half,
  accumulated by the EDM into the visibility results [infer]. From `CR_ISP_VISIBILITY_COUNT3` (ours,
  resgx545).
- `CR_ISP_VISIBILITY_COUNT4` G0139 (0x04a8): visibility counters 8 and 9, one per 16-bit half,
  accumulated by the EDM into the visibility results [infer]. From `CR_ISP_VISIBILITY_COUNT4` (ours,
  resgx545).
- `CR_ISP_VISIBILITY_COUNT7` G0140 (0x04b4): visibility counters 14 and 15, one per 16-bit half,
  accumulated by the EDM into the visibility results [infer]. From `CR_ISP_VISIBILITY_COUNT7` (ours,
  resgx545).
- `CR_ISP_BGOBJDEPTH` G0118 (0x04b8): background object depth (Rogue analogue). From
  `ROGUE_CR_ISP_BGOBJDEPTH` (3, mesa-csbgen).
- `CR_ISP_MULTISAMPLECTL` G0124 (0x04c8): the pixel's sample positions, a byte per sample (x in bits
  3:0, y in bits 7:4, sixteenths of a pixel): 0x88 one sample at the centre, 0xeaa26e26 four in a
  rotated grid with 4x multisampling (Rogue analogue: PPP_MULTISAMPLECTL). From `ROGUE_CR_ISP_AA`
  (3, mesa-csbgen).
- `CR_ISP_REG_04DC` G0130 (0x04dc): ISP word from the render details; bits 2:0 implemented; bit 1
  set hangs a render with punch-through objects, bits 0 and 2 change nothing seen; 0 from the closed
  driver's renders [infer]. From `CR_ISP_REG_04DC` (ours, resgx545).
- `CR_ISP_REG_04E8` G0131 (0x04e8): inferred reading (unconfirmed): Register 0x04e8: held 0x100
  outside a render, bits 0 and 8 take a write, and in every transfer, depth scene,
  overlapping-triangle scene and textured triangle tried no value of it changed an image; what it
  does is not shown. From `CR_ISP_REG_04E8` (ours, resgx545).
- `CR_ISP_SAMPLE_POS` G0132 (0x0520): four more sample positions, laid out as CR_ISP_MULTISAMPLECTL
  (a byte per sample: x in bits 3:0, y in bits 7:4, sixteenths of a pixel): with
  ISP0.SAMPLE_COVERAGE an object covers a pixel where any of the eight is inside; 4x multisampling
  does not read it; 0 from the closed driver [infer]. From `CR_ISP_SAMPLE_POS` (ours, resgx545).
- `CR_REG_0800` G0154 (0x0800): inferred reading (unconfirmed): Register 0x0800: held 0x30 outside a
  render, 22 bits (0 to 5 and 8 to 23) take a write, and in every transfer, depth scene and
  overlapping-triangle scene tried no value of it changed an image; what it does is not shown. From
  `CR_REG_0800` (ours, resgx545).
- `CR_CACHE_CTRL` G0035 (0x0804): cache control / invalidate. From `PSB_CR_CACHE_CTRL` (1c,
  emgd-psb_regs).
- `CR_REG_0810` G0155 (0x0810): inferred reading (unconfirmed): a tuning enable left at 1. Measured:
  set once by the init script to 0x1; implemented bits 0; no effect on a fill, copy or triangle in
  any value [infer]. From `CR_REG_0810` (ours, resgx545).
- `CR_REG_0814` G0156 (0x0814): inferred reading (unconfirmed): an enable mask or upper limit left
  at or near its widest (0xffff of 17 implemented bits). Measured: set once by the init script to
  0xffff; implemented bits 16:0; no effect on a fill, copy or triangle in any value [infer]. From
  `CR_REG_0814` (ours, resgx545).
- `CR_REG_0818` G0157 (0x0818): inferred reading (unconfirmed): an enable mask or upper limit left
  at its widest (11 bits all ones). Measured: set once by the init script to 0x7ff; implemented bits
  10:0; no effect on a fill, copy or triangle in any value [infer]. From `CR_REG_0818` (ours,
  resgx545).
- `CR_TPU_YUV_CSC0_0` G0165 (0x0820): Word 0 of colour-space set 0, the YUV-to-RGB coefficients a
  UYVY copy applies: Y to R in bits 9:0 and Y to G in bits 25:16, signed in 128ths; the
  limited-range BT.601 numbers are loaded as 0x00950095 (149 and 149). From `CR_TPU_YUV_CSC0_0`
  (ours, resgx545).
- `CR_TPU_YUV_CSC0_1` G0166 (0x0824): Word 1 of colour-space set 0, the YUV-to-RGB coefficients a
  UYVY copy applies: Y to B in bits 9:0 and U to R in bits 25:16, signed in 128ths; the
  limited-range BT.601 numbers are loaded as 0x00000095 (149 and 0). From `CR_TPU_YUV_CSC0_1` (ours,
  resgx545).
- `CR_TPU_YUV_CSC0_2` G0167 (0x0828): Word 2 of colour-space set 0, the YUV-to-RGB coefficients a
  UYVY copy applies: U to G in bits 9:0 and U to B in bits 25:16, signed in 128ths; the
  limited-range BT.601 numbers are loaded as 0x010203ce (-50 and 258). From `CR_TPU_YUV_CSC0_2`
  (ours, resgx545).
- `CR_TPU_YUV_CSC0_3` G0168 (0x082c): Word 3 of colour-space set 0, the YUV-to-RGB coefficients a
  UYVY copy applies: V to R in bits 9:0 and V to G in bits 25:16, signed in 128ths; the
  limited-range BT.601 numbers are loaded as 0x039800cc (204 and -104). From `CR_TPU_YUV_CSC0_3`
  (ours, resgx545).
- `CR_TPU_YUV_CSC0_4` G0169 (0x0830): Word 4 of colour-space set 0, the YUV-to-RGB coefficients a
  UYVY copy applies: V to B in bits 9:0, signed in 128ths; the limited-range BT.601 numbers are
  loaded as 0 (0). From `CR_TPU_YUV_CSC0_4` (ours, resgx545).
- `CR_TPU_YUV_CSC1_0` G0170 (0x0834): inferred reading (unconfirmed): Word 0 of colour-space set 1,
  loaded like set 0; in the UYVY copy tried no value or bit of it selected the set, so what it
  converts is not shown. From `CR_TPU_YUV_CSC1_0` (ours, resgx545).
- `CR_TPU_YUV_CSC1_1` G0171 (0x0838): inferred reading (unconfirmed): Word 1 of colour-space set 1,
  loaded like set 0; in the UYVY copy tried no value or bit of it selected the set, so what it
  converts is not shown. From `CR_TPU_YUV_CSC1_1` (ours, resgx545).
- `CR_TPU_YUV_CSC1_2` G0172 (0x083c): inferred reading (unconfirmed): Word 2 of colour-space set 1,
  loaded like set 0; in the UYVY copy tried no value or bit of it selected the set, so what it
  converts is not shown. From `CR_TPU_YUV_CSC1_2` (ours, resgx545).
- `CR_TPU_YUV_CSC1_3` G0173 (0x0840): inferred reading (unconfirmed): Word 3 of colour-space set 1,
  loaded like set 0; in the UYVY copy tried no value or bit of it selected the set, so what it
  converts is not shown. From `CR_TPU_YUV_CSC1_3` (ours, resgx545).
- `CR_TPU_YUV_CSC1_4` G0174 (0x0844): inferred reading (unconfirmed): Word 4 of colour-space set 1,
  loaded like set 0; in the UYVY copy tried no value or bit of it selected the set, so what it
  converts is not shown. From `CR_TPU_YUV_CSC1_4` (ours, resgx545).
- `CR_TPU_YUV_CSC_INPUT` G0175 (0x0848): Register 0x0848, loaded by one transfer word: in a UYVY
  copy through colour-space set 0, bit 0 drops the 16 luma offset and bit 2 reads U and V as signed
  bytes (U - 256 for 128 and above), and 0xffffffff does both; its other bits changed nothing. From
  `CR_TPU_YUV_CSC_INPUT` (ours, resgx545).
- `CR_TPU_LUMA_KEY_RG` G0164 (0x0860): inferred reading (unconfirmed): Register 0x0860: with the
  copy's luma-key mode on, the R weight in bits 9:0 and the G weight in bits 25:16, in 1024ths, of
  the weighted sum that decides the alpha; it starts at 0x02020106 (weights 262 and 514). From
  `CR_TPU_LUMA_KEY_RG` (ours, resgx545).
- `CR_TPU_LUMA_KEY_B_OFFSET` G0163 (0x0864): inferred reading (unconfirmed): Register 0x0864: with
  the copy's luma-key mode on, the B weight in bits 9:0 (1024ths) and an offset in bits 23:16 that
  enters the sum as 512 times its value; it starts at 0x00210064 (weight 100, offset 33). From
  `CR_TPU_LUMA_KEY_B_OFFSET` (ours, resgx545).
- `CR_TPU_LUMA_KEY_ALPHA` G0162 (0x0868): inferred reading (unconfirmed): Register 0x0868: with the
  copy's luma-key mode on, the threshold in bits 15:8, the alpha written at or below it in bits
  23:16 and the alpha written above it in bits 31:24; it starts at 0xff008000 (alpha 0 below 128,
  0xff above). Bits 7:0 are not explained: values 64, 128 and 255 fit no threshold. From
  `CR_TPU_LUMA_KEY_ALPHA` (ours, resgx545).
- `CR_USE_CTRL` G0058 (0x0a00): USSE control. From `PSB_CR_USE_CTRL` (1c, emgd-psb_regs).
- `CR_USE_CODE_BASE_0` G0005 (0x0a0c): USSE code base 0: address and data master. From
  `EUR_CR_USE_CODE_BASE(X)` (1, sgx545-ce); `EUR_CR_USE_CODE_BASE_0` (1, sgx545-ce);
  `PSB_CR_USE_CODE_BASE(i)` (1c, emgd-psb_regs); `PSB_CR_USE_CODE_BASE0` (1c, emgd-psb_regs).
- `CR_USE_CODE_BASE_10` G0056 (0x0a34): USSE code base 10: address and data master. From
  `EUR_CR_USE_CODE_BASE_10` (1, sgx545-ce); `PSB_CR_USE_CODE_BASE10` (1c, emgd-psb_regs).
- `CR_USE_CODE_BASE_15` G0057 (0x0a48): USSE code base 15: address and data master. From
  `EUR_CR_USE_CODE_BASE_15` (1, sgx545-ce); `PSB_CR_USE_CODE_BASE15` (1c, emgd-psb_regs).
- `CR_EVENT_PDS_ENABLE` G0048 (0x0a58): events that start a PDS event task. From
  `PSB_CR_EVENT_PDS_ENABLE` (1c, emgd-psb_regs).
- `CR_EVENT_OTHER_PDS_EXEC` G0003 (0x0a68): PDS code address of the other-event task. From
  `EUR_CR_EVENT_OTHER_PDS_EXEC` (1c, intel-ctp-santos10).
- `CR_EVENT_OTHER_PDS_DATA` G0002 (0x0a6c): PDS data address of the other-event task. From
  `EUR_CR_EVENT_OTHER_PDS_DATA` (1c, intel-ctp-santos10).
- `CR_EVENT_OTHER_PDS_INFO` G0047 (0x0a70): other-event task sizes. From
  `EUR_CR_EVENT_OTHER_PDS_INFO` (1, intel-ctp-santos10).
- `CR_DMS_CTRL` G0041 (0x0a74): data-master task/partition limits. From `PSB_CR_DMS_CTRL` (1c,
  emgd-psb_regs).
- `CR_PDS_REG_0A78` G0148 (0x0a78): inferred reading (unconfirmed): a PDS tuning value (6 bits,
  0x2c) with no visible effect at our loads. Measured: set once by the init script to 0x2c; not the
  SGX535 register at this offset; implemented bits 5:0; no effect on a fill, copy or triangle in any
  value [infer]. From `CR_PDS_REG_0A78` (ours, resgx545).
- `CR_USE_G0` G0059 (0x0a7c): USSE global value g0. From `PSB_CR_USE_G0` (1c, emgd-psb_regs).
- `CR_USE_G1` G0060 (0x0a80): USSE global value g1. From `PSB_CR_USE_G1` (1c, emgd-psb_regs).
- `CR_USE_COEFFS0_A` G0194 (0x0a84): first tap word of coefficient set 0: signed byte taps at -3,
  -2, -1, 0 from the filter's centre in bytes 3, 2, 1, 0 [infer]. From `CR_USE_COEFFS0_A` (ours,
  resgx545).
- `CR_USE_COEFFS0_B` G0195 (0x0a88): second tap word of coefficient set 0: signed byte taps at +1,
  +2, +3, +4 from the centre in bytes 3, 2, 1, 0 [infer]. From `CR_USE_COEFFS0_B` (ours, resgx545).
- `CR_USE_COEFFS0_BIAS` G0196 (0x0a8c): shift and bias of coefficient set 0: bits 3:0 shift the tap
  sum right, the bits above a signed bias added before the shift; the result saturates to a byte
  [infer]. From `CR_USE_COEFFS0_BIAS` (ours, resgx545).
- `CR_USE_COEFFS1_A` G0197 (0x0a90): first tap word of coefficient set 1: signed byte taps at -3,
  -2, -1, 0 from the filter's centre in bytes 3, 2, 1, 0 [infer]. From `CR_USE_COEFFS1_A` (ours,
  resgx545).
- `CR_USE_COEFFS1_B` G0198 (0x0a94): second tap word of coefficient set 1: signed byte taps at +1,
  +2, +3, +4 from the centre in bytes 3, 2, 1, 0 [infer]. From `CR_USE_COEFFS1_B` (ours, resgx545).
- `CR_USE_COEFFS1_BIAS` G0199 (0x0a98): shift and bias of coefficient set 1: bits 3:0 shift the tap
  sum right, the bits above a signed bias added before the shift; the result saturates to a byte
  [infer]. From `CR_USE_COEFFS1_BIAS` (ours, resgx545).
- `CR_USE_COEFFS_MODE` G0203 (0x0a9c): which coefficient sets the filter instructions use: bits 1:0
  = 0, 1, 2 pick one of three fixed banks for sets 2-5, 3 makes set 2 the third loaded group
  (CR_USE_COEFFS2_*) and sets 3-5 zero; sets 0-1 are always CR_USE_COEFFS0/1_* [infer]. From
  `CR_USE_COEFFS_MODE` (ours, resgx545).
- `CR_USE_TMPREG` G0061 (0x0aac): USSE temporary registers: size and initial value. From
  `PSB_CR_USE_TMPREG` (1c, emgd-psb_regs).
- `CR_PDS_EXEC_BASE` G0004 (0x0ab8): base address of PDS program fetches. From
  `EUR_CR_PDS_EXEC_BASE` (1, sgx545-ce); `PSB_CR_PDS_EXEC_BASE` (1c, emgd-psb_regs).
- `CR_PDS_REG_0ABC` G0149 (0x0abc): set once by the init script to 0xe; not the SGX535 register at
  this offset; implemented bits 5:0; 0 hangs the next job, other values change nothing seen [infer].
  From `CR_PDS_REG_0ABC` (ours, resgx545).
- `CR_EVENT_KICKER` G0046 (0x0ac4): address the event kicker DMA reads. From `EUR_CR_EVENT_KICKER`
  (1, sgx545-ce).
- `CR_EVENT_KICK` G0090 (0x0ac8): host doorbell: start the EDM event task. From `EUR_CR_EVENT_KICK`
  (1, sgx545-ce).
- `CR_EVENT_TIMER` G0050 (0x0acc): EDM periodic timer: period and enable. From `EUR_CR_EVENT_TIMER`
  (1, sgx545-ce); `PSB_CR_EVENT_TIMER` (1c, emgd-psb_regs).
- `CR_USE0_SERV_PIXEL` G0178 (0x0b0c): USSE 0 pixel service-queue status (SGX535 0x0b08). From
  `PSB_CR_USE0_SERV_PIXEL` (1c, emgd-psb_regs).
- `CR_USE0_SERV_VERTEX` G0179 (0x0b10): USSE 0 vertex service-queue status (SGX535 0x0b0c). From
  `PSB_CR_USE0_SERV_VERTEX` (1c, emgd-psb_regs).
- `CR_USE0_SERV_EVENT` G0054 (0x0b14): USSE 0 event service-queue status, the EDM task register
  (SGX535 0x0b10). From `PSB_CR_USE0_SERV_EVENT` (1c, emgd-psb_regs).
- `CR_USE1_SERV_PIXEL` G0180 (0x0b18): USSE 1 pixel service-queue status (SGX535 0x0b14). From
  `PSB_CR_USE1_SERV_PIXEL` (1c, emgd-psb_regs).
- `CR_USE1_SERV_VERTEX` G0181 (0x0b1c): USSE 1 vertex service-queue status (SGX535 0x0b18). From
  `PSB_CR_USE1_SERV_VERTEX` (1c, emgd-psb_regs).
- `CR_USE1_SERV_EVENT` G0055 (0x0b20): USSE 1 event service-queue status, the EDM task register
  (SGX535 0x0b1c). From `PSB_CR_USE1_SERV_EVENT` (1c, emgd-psb_regs).
- `CR_USE_COEFFS2_A` G0200 (0x0b24): first tap word of coefficient set 2: signed byte taps at -3,
  -2, -1, 0 from the filter's centre in bytes 3, 2, 1, 0; set 2 uses only -3 (byte 3) and 0 (byte 0)
  [infer]. From `CR_USE_COEFFS2_A` (ours, resgx545).
- `CR_USE_COEFFS2_B` G0201 (0x0b28): second tap word of coefficient set 2: signed byte taps at +1,
  +2, +3, +4 from the centre in bytes 3, 2, 1, 0; set 2 uses only +3 (byte 1) [infer]. From
  `CR_USE_COEFFS2_B` (ours, resgx545).
- `CR_USE_COEFFS2_BIAS` G0202 (0x0b2c): shift and bias of coefficient set 2: bits 3:0 shift the tap
  sum right, the bits above a signed bias added before the shift; the result saturates to a byte
  [infer]. From `CR_USE_COEFFS2_BIAS` (ours, resgx545).
- `CR_USE2_SERV_PIXEL` G0182 (0x0b88): USSE 2 pixel service-queue status, as CR_USE0_SERV_PIXEL
  [infer]. From `CR_USE2_SERV_PIXEL` (ours, resgx545).
- `CR_USE2_SERV_VERTEX` G0185 (0x0b8c): USSE 2 vertex service-queue status, as CR_USE0_SERV_VERTEX
  [infer]. From `CR_USE2_SERV_VERTEX` (ours, resgx545).
- `CR_USE3_SERV_PIXEL` G0188 (0x0b94): USSE 3 pixel service-queue status, as CR_USE0_SERV_PIXEL
  [infer]. From `CR_USE3_SERV_PIXEL` (ours, resgx545).
- `CR_USE3_SERV_VERTEX` G0191 (0x0b98): USSE 3 vertex service-queue status, as CR_USE0_SERV_VERTEX
  [infer]. From `CR_USE3_SERV_VERTEX` (ours, resgx545).
- `CR_BIF_CTRL` G0030 (0x0c00): MMU control: pause, invalidate, clear fault. From `EUR_CR_BIF_CTRL`
  (1, sgx545-ce); `PSB_CR_BIF_CTRL` (1c, emgd-psb_regs); `ROGUE_CR_BIF_CTRL` (3, linux-imagination).
- `CR_BIF_INT_STAT` G0034 (0x0c04): MMU fault/interrupt status. From `EUR_CR_BIF_INT_STAT` (1,
  sgx545-ce); `PSB_CR_BIF_INT_STAT` (1c, emgd-psb_regs).
- `CR_BIF_FAULT` G0033 (0x0c08): MMU faulting address and context. From `EUR_CR_BIF_FAULT` (1,
  sgx545-ce); `PSB_CR_BIF_FAULT` (1c, emgd-psb_regs).
- `CR_BIF_DIR_LIST_BASE1` G0089 (0x0c38): page-directory base, context 1. From
  `EUR_CR_BIF_DIR_LIST_BASE1` (1, sgx545-ce); `PSB_CR_BIF_DIR_LIST_BASE1` (1c, emgd-psb_regs).
- `CR_BIF_DIR_LIST_BASE15` G0032 (0x0c70): page-directory base, context 15. From
  `EUR_CR_BIF_DIR_LIST_BASE15` (1, sgx545-ce).
- `CR_BIF_BANK_SET` G0029 (0x0c74): selects which bank register each requestor uses. From
  `EUR_CR_BIF_BANK_SET` (1, sgx545-ce); `PSB_CR_BIF_BANK_SET` (1c, emgd-psb_regs).
- `CR_BIF_BANK0` G0028 (0x0c78): directory-list index per requestor, bank 0. From `EUR_CR_BIF_BANK0`
  (1, sgx545-ce); `PSB_CR_BIF_BANK0` (1c, emgd-psb_regs).
- `CR_BIF_DIR_LIST_BASE0` G0031 (0x0c84): page-directory base, context 0. From
  `EUR_CR_BIF_DIR_LIST_BASE0` (1, sgx545-ce); `PSB_CR_BIF_DIR_LIST_BASE0` (1c, emgd-psb_regs).
- `CR_BIF_3D_REQ_BASE` G0001 (0x0cac): 3D requestor base address. From `EUR_CR_BIF_3D_REQ_BASE` (1,
  sgx545-ce); `PSB_CR_BIF_3D_REQ_BASE` (1c, emgd-psb_regs).

## 3. Firmware-interface structures, flags and functions

### field

- `ccb_ctl.write_offset` G0097 (CCB_CTL+0x0): write offset (host advances). From `ui32WriteOffset`
  (1, sgx545-ce).
- `ccb_ctl.read_offset` G0096 (CCB_CTL+0x4): read offset (EDM advances). From `ui32ReadOffset` (1,
  sgx545-ce).
- `cmd_ta.frag_flags` G0303 (CMDTA+0x01c): fragment (3D) flags: depth/stencil buffer present,
  visibility results (FRAG_FLAGS.*). From `flags` (3, linux-imagination).
- `cmd_ta.te_screen` G0316 (CMDTA+0x244): screen size in tiles. From `te_screen` (3,
  linux-imagination).
- `cmd_ta.mte_rhw_min` G0305 (CMDTA+0x260): the TA command's word the EDM loads into CR_MTE_RHW_MIN
  (0x0240) [infer]. From `cmd_ta.mte_rhw_min` (ours, resgx545).
- `cmd_ta.mte_rhw_clamp` G0304 (CMDTA+0x264): the TA command's word the EDM loads into
  CR_MTE_RHW_CLAMP (0x0244) [infer]. From `cmd_ta.mte_rhw_clamp` (ours, resgx545).
- `cmd_ta.use_reg_0a04` G0317 (CMDTA+0x26c): inferred reading (unconfirmed): as CR_USE_REG_0A04's:
  the USSE's context store/resume state base (a 16-byte address) for an interrupted TA's vertex
  tasks. Measured: value the EDM copies verbatim into CR_USE_REG_0A04 (0x0a04); 0 in every capture
  [infer]. From `cmd_ta.use_reg_0a04` (ours, resgx545).
- `cmd_ta.use_reg_0aa0` G0318 (CMDTA+0x270): inferred reading (unconfirmed): as CR_USE_REG_0AA0's: a
  USSE resume task word for an interrupted TA's vertex tasks. Measured: value the EDM copies
  verbatim into CR_USE_REG_0AA0 (0x0aa0); 0 in every capture [infer]. From `cmd_ta.use_reg_0aa0`
  (ours, resgx545).
- `cmd_ta.ta_reg_02b0` G0311 (CMDTA+0x278): inferred reading (unconfirmed): as CR_TA_REG_02B0's:
  context store/resume state of an interrupted TA: an 8-bit field in 31:24 (state flags). Measured:
  value the EDM copies verbatim into CR_TA_REG_02B0 (0x02b0); 0 in every capture [infer]. From
  `cmd_ta.ta_reg_02b0` (ours, resgx545).
- `cmd_ta.ta_reg_02d4` G0314 (CMDTA+0x27c): inferred reading (unconfirmed): as CR_TA_REG_02D4's:
  context store/resume state of an interrupted TA: a 26-bit size or offset. Measured: value the EDM
  copies verbatim into CR_TA_REG_02D4 (0x02d4); 0 in every capture [infer]. From
  `cmd_ta.ta_reg_02d4` (ours, resgx545).
- `cmd_ta.ta_reg_02d0` G0313 (CMDTA+0x280): inferred reading (unconfirmed): as CR_TA_REG_02D0's: the
  TA's context state base (a dword address), read only when an interrupted TA resumes. Measured:
  value the EDM copies verbatim into CR_TA_REG_02D0 (0x02d0); 0 in every capture [infer]. From
  `cmd_ta.ta_reg_02d0` (ours, resgx545).
- `cmd_ta.ta_reg_02b4` G0312 (CMDTA+0x284): inferred reading (unconfirmed): as CR_TA_REG_02B4's: TA
  context status: reads 0xff after any job, a valid or done mask of the stored state. Measured:
  value the EDM copies verbatim into CR_TA_REG_02B4 (0x02b4); 0 in every capture [infer]. From
  `cmd_ta.ta_reg_02b4` (ours, resgx545).
- `cmd_ta.reg_0324` G0306 (CMDTA+0x288): inferred reading (unconfirmed): TA command word 162, loaded
  into register 0x0324; the job leaves it at 0, no value changed the triangle's image, a page
  address in six numberings made no write, and a register readback after 0xffffffff shows only the
  implemented bits (0xfffffff0). From `cmd_ta.reg_0324` (ours, resgx545).
- `cmd_ta.reg_0368` G0308 (CMDTA+0x28c): inferred reading (unconfirmed): as CR_REG_0368's: context
  store/resume state of an interrupted TA: a 15-bit size or count of the stored state. Measured:
  value the EDM copies verbatim into CR_REG_0368 (0x0368); 0 in every capture [infer]. From
  `cmd_ta.reg_0368` (ours, resgx545).
- `cmd_ta.reg_0364` G0307 (CMDTA+0x290): inferred reading (unconfirmed): as CR_REG_0364's: context
  store/resume state of an interrupted TA: a 32-bit resume task word, unused while the TA runs to
  the end. Measured: value the EDM copies verbatim into CR_REG_0364 (0x0364); 0 in every capture
  [infer]. From `cmd_ta.reg_0364` (ours, resgx545).
- `cmd_ta.reg_0370` G0309 (CMDTA+0x294): inferred reading (unconfirmed): as CR_REG_0370's: context
  store/resume state of an interrupted TA: a 32-bit resume task word. Measured: value the EDM copies
  verbatim into CR_REG_0370 (0x0370); 0 in every capture [infer]. From `cmd_ta.reg_0370` (ours,
  resgx545).
- `cmd_ta.reg_0374` G0310 (CMDTA+0x298): inferred reading (unconfirmed): as CR_REG_0374's: context
  store/resume state of an interrupted TA: a 32-bit resume task word. Measured: value the EDM copies
  verbatim into CR_REG_0374 (0x0374); 0 in every capture [infer]. From `cmd_ta.reg_0374` (ours,
  resgx545).
- `cmd_ta.dpm_reg_074c` G0302 (CMDTA+0x29c): inferred reading (unconfirmed): as CR_DPM_REG_074C's:
  the enable (bit 8) and setup of a DPM structure that follows the TA data (a second list, as a
  partial-render or context-switch arrangement would need), off in every client. Measured: value the
  EDM copies verbatim into CR_DPM_REG_074C (0x074c); 0 in every capture [infer]. From
  `cmd_ta.dpm_reg_074c` (ours, resgx545).
- `cmd_ta.te_reg_02a8` G0315 (CMDTA+0x2a0): inferred reading (unconfirmed): as CR_TE_REG_02A8's: the
  tiling engine's resume position after an interrupted TA: an 8-bit field in 19:12. Measured: value
  the EDM copies verbatim into CR_TE_REG_02A8 (0x02a8); 0 in every capture [infer]. From
  `cmd_ta.te_reg_02a8` (ours, resgx545).
- `command.service_address` G0100 (COMMAND+0x00): EDM handler address (aui32HostKickAddr[type]).
  From `ui32ServiceAddress` (1, sgx545-ce).
- `command.cache_control` G0098 (COMMAND+0x04): CACHE_CONTROL.* invalidations done before the
  command. From `ui32CacheControl` (1, sgx545-ce).
- `command.data` G0099 (COMMAND+0x08): six command words; [1] = context/data address. From
  `ui32Data` (1, sgx545-ce).
- `host_ctl.init_status` G0079 (HOST_CTL+0x00): EDM init status; INIT_STATUS.COMPLETE. From
  `ui32InitStatus` (1, sgx545-ce).
- `host_ctl.power_status` G0085 (HOST_CTL+0x04): POWER_STATUS.* bits. From `ui32PowerStatus` (1,
  sgx545-ce).
- `host_ctl.cleanup_status` G0074 (HOST_CTL+0x08): CLEANUP_STATUS.* bits. From `ui32CleanupStatus`
  (1, sgx545-ce).
- `host_ctl.ukernel_detected_lockups` G0086 (HOST_CTL+0x0c): lockups seen by the EDM. From
  `ui32uKernelDetectedLockups` (1, sgx545-ce).
- `host_ctl.host_detected_lockups` G0077 (HOST_CTL+0x10): lockups seen by the host. From
  `ui32HostDetectedLockups` (1, sgx545-ce).
- `host_ctl.hw_recovery_sample_rate` G0078 (HOST_CTL+0x14): lockup check period in timer ticks. From
  `ui32HWRecoverySampleRate` (1, sgx545-ce).
- `host_ctl.ukernel_timer_clock` G0087 (HOST_CTL+0x18): EDM timer period in core clocks. From
  `ui32uKernelTimerClock` (1, sgx545-ce).
- `host_ctl.active_powman_sample_rate` G0071 (HOST_CTL+0x1c): active power latency in ticks. From
  `ui32ActivePowManSampleRate` (1, sgx545-ce).
- `host_ctl.interrupt_flags` G0081 (HOST_CTL+0x20): EDM->host requests (INTERRUPT_FLAGS.*). From
  `ui32InterruptFlags` (1, sgx545-ce).
- `host_ctl.interrupt_clear_flags` G0080 (HOST_CTL+0x24): host acknowledges of
  host_ctl.interrupt_flags. From `ui32InterruptClearFlags` (1, sgx545-ce).
- `host_ctl.bp_set_clear_signal` G0073 (HOST_CTL+0x28): breakpoint set/clear signal. From
  `ui32BPSetClearSignal` (1, sgx545-ce).
- `host_ctl.num_active_power_events` G0082 (HOST_CTL+0x2c): active power-down count. From
  `ui32NumActivePowerEvents` (1, sgx545-ce).
- `host_ctl.edm_ticks` G0075 (HOST_CTL+0x30): EDM timer tick count; the host never writes it. From
  `ui32TimeWraps` (1, sgx545-ce).
- `host_ctl.host_clock` G0076 (HOST_CTL+0x34): host clock at EDM boot. From `ui32HostClock` (1,
  sgx545-ce).
- `host_ctl.assert_fail` G0072 (HOST_CTL+0x38): EDM assert code. From `ui32AssertFail` (1,
  sgx545-ce).
- `host_ctl.perf_group` G0084 (HOST_CTL+0x3c): HW perf counter group. From `ui32PerfGroup` (1,
  sgx545-ce).
- `host_ctl.opencl_delay_count` G0083 (HOST_CTL+0x40): OpenCL task timeout counter. From
  `ui32OpenCLDelayCount` (1, sgx545-ce).
- `hw_render_details.bif_zls_req_base` G0319 (HWRENDERDETAILS+0x004): ZLS requestor base. From
  `EUR_CR_BIF_ZLS_REQ_BASE` (1, sgx545-ce).
- `hw_render_details.reg_0400` G0328 (HWRENDERDETAILS+0x008): inferred reading (unconfirmed): The
  render-side word that loads register 0x0400: bit 25 inverts bits 31:24 of every pixel the job
  writes, and no other bit changed a pixel; the data come from the render command's word 11, which
  loads the same register, not from the render-details word itself. From
  `hw_render_details.reg_0400` (ours, resgx545).
- `hw_render_details.isp_msaa` G0320 (HWRENDERDETAILS+0x010): the render details' word the EDM loads
  into CR_ISP_MSAA (0x80000000 single-sampled, 0x80000002 at 4x) [infer]. From
  `hw_render_details.isp_msaa` (ours, resgx545).
- `hw_render_details.poly_offset_units` G0327 (HWRENDERDETAILS+0x014): Render-details word 5, loaded
  into register 0x041c: the polygon offset in units of one ulp of the stored depth, added to the
  triangle's depth only when ISP word 1 bit 23 is set. From `hw_render_details.poly_offset_units`
  (ours, resgx545).
- `hw_render_details.poly_offset_factor` G0326 (HWRENDERDETAILS+0x018): inferred reading
  (unconfirmed): Render-details word 6, loaded into register 0x0420: set to 4.0 with the units word
  at 0 it left the flat triangle's stored depth unchanged; what it multiplies is not shown. From
  `hw_render_details.poly_offset_factor` (ours, resgx545).
- `hw_render_details.poly_offset_clamp` G0325 (HWRENDERDETAILS+0x01c): value the EDM copies into
  CR_ISP_POLY_OFFSET_CLAMP [infer]. From `hw_render_details.poly_offset_clamp` (ours, resgx545).
- `hw_render_details.isp_zlsctl` G0323 (HWRENDERDETAILS+0x02c): ZLS control. From `isp_zlsctl` (3,
  linux-imagination).
- `hw_render_details.zload_base` G0331 (HWRENDERDETAILS+0x030): value the EDM loads into
  CR_ISP_ZLOAD_BASE (0x0484): the depth load base [infer]. From `hw_render_details.zload_base`
  (ours, resgx545).
- `hw_render_details.zstore_base` G0332 (HWRENDERDETAILS+0x034): value the EDM loads into
  CR_ISP_ZSTORE_BASE (0x0488): the depth store base [infer]. From `hw_render_details.zstore_base`
  (ours, resgx545).
- `hw_render_details.stencil_load_base` G0329 (HWRENDERDETAILS+0x038): value the EDM loads into
  CR_ISP_STENCIL_LOAD_BASE (0x048c): the stencil load base [infer]. From
  `hw_render_details.stencil_load_base` (ours, resgx545).
- `hw_render_details.stencil_store_base` G0330 (HWRENDERDETAILS+0x03c): value the EDM loads into
  CR_ISP_STENCIL_STORE_BASE (0x0490): the stencil store base and its enable [infer]. From
  `hw_render_details.stencil_store_base` (ours, resgx545).
- `hw_render_details.isp_sample_pos` G0322 (HWRENDERDETAILS+0x04c): inferred reading (unconfirmed):
  Render-details word 19, loaded into register 0x0520 (all 32 bits implemented, held 0 outside a
  render); no value of it changed any image tried, and no bit of it made a 4x triangle's pixel
  shader run per sample. From `hw_render_details.isp_sample_pos` (ours, resgx545).
- `hw_render_details.isp_multisamplectl` G0321 (HWRENDERDETAILS+0x050): Render-details word 20: the
  value loaded into register 0x04c8, the same register the render command's word 16 loads (identical
  images bit for bit), holding the sample positions; 22 of its 32 bits moved the samples of a 4x
  triangle by a few samples and the rest changed nothing. From
  `hw_render_details.isp_multisamplectl` (ours, resgx545).
- `hw_render_details.num_pixel_partitions` G0324 (HWRENDERDETAILS+0x13c): DMS_CTRL pixel partitions
  (31 << 22). From `NumPixelPartitions` (2, cdv-libsrv_um).
- `hw_transfer_context.fw_com_ctx_flags` G0105 (HWTRANSFERCONTEXT+0x000): context flags. From
  `fw_com_ctx_flags` (3, linux-imagination).
- `hw_transfer_context.priority` G0107 (HWTRANSFERCONTEXT+0x004): priority. From
  `ui32OffsetOfPriorityField` (1, sgx545-ce); `priority` (3, linux-imagination).
- `hw_transfer_context.pd_dev_paddr` G0106 (HWTRANSFERCONTEXT+0x008): PD physical address (kernel
  writes). From `ui32OffsetToPDDevPAddr` (1, sgx545-ce).
- `hw_transfer_context.ccb_dev_vaddr` G0104 (HWTRANSFERCONTEXT+0x00c): transfer client CCB. From
  `hCCBMemInfo` (1, sgx545-ce); `ccb_fw_addr` (3, linux-imagination).
- `hw_transfer_context.ccb_ctl_dev_vaddr` G0103 (HWTRANSFERCONTEXT+0x010): transfer CCB control.
  From `PVRSRV_SGX_CCB_CTL` (1, sgx545-ce); `ccbctl_fw_addr` (3, linux-imagination).
- `hw_transfer_context.submitted_commands` G0108 (HWTRANSFERCONTEXT+0x014): commands queued. From
  `submitted_commands` (3, linux-imagination).
- `misc_info.flags` G0111 (MISC+0x00): MISC_INFO_FLAGS.* request/ready bits. From
  `ui32MiscInfoFlags` (1, sgx545-ce).
- `misc_info.struct_sizes` G0112 (MISC+0x20): structure sizes block. From `sSGXStructSizes` (1,
  sgx545-ce).
- `misc_info_struct_sizes.sizeof_cmd_ta` G0012 (MISCINFO_STRUCT_SIZES+0x00 (=MISC+0x20); value
  0x2b0): size of CMDTA the EDM was built for: TA command (client CCB entry for TA/3D work). From
  `ui32Sizeof_CMDTA` (1, sgx545-ce).
- `misc_info_struct_sizes.sizeof_cmd_ta_shared` G0013 (MISCINFO_STRUCT_SIZES+0x04 (=MISC+0x24);
  value 0x1e0): size of CMDTA_SHARED the EDM was built for: kernel-written part of the TA command.
  From `ui32Sizeof_CMDTA_SHARED` (1, sgx545-ce).
- `misc_info_struct_sizes.sizeof_transfer_cmd` G0022 (MISCINFO_STRUCT_SIZES+0x08 (=MISC+0x28); value
  0x4c8): size of TRANSFERCMD the EDM was built for: transfer-queue command. From
  `ui32Sizeof_TRANSFERCMD` (1, sgx545-ce).
- `misc_info_struct_sizes.sizeof_transfer_cmd_shared` G0023 (MISCINFO_STRUCT_SIZES+0x0c
  (=MISC+0x2c); value 0xdc): size of TRANSFERCMD_SHARED the EDM was built for: kernel-written part
  of the transfer command. From `ui32Sizeof_TRANSFERCMD_SHARED` (1, sgx545-ce).
- `misc_info_struct_sizes.sizeof_3d_registers` G0011 (MISCINFO_STRUCT_SIZES+0x10 (=MISC+0x30); value
  0xd0): size of 3DREGISTERS the EDM was built for: 3D register block at the start of the render
  details. From `ui32Sizeof_3DREGISTERS` (1, sgx545-ce).
- `misc_info_struct_sizes.sizeof_hw_pb_desc` G0016 (MISCINFO_STRUCT_SIZES+0x14 (=MISC+0x34); value
  0x3c): size of HWPBDESC the EDM was built for: parameter-buffer descriptor. From
  `ui32Sizeof_HWPBDESC` (1, sgx545-ce).
- `misc_info_struct_sizes.sizeof_hw_render_context` G0017 (MISCINFO_STRUCT_SIZES+0x18 (=MISC+0x38);
  value 0x44): size of HWRENDERCONTEXT the EDM was built for: HW render context. From
  `ui32Sizeof_HWRENDERCONTEXT` (1, sgx545-ce).
- `misc_info_struct_sizes.sizeof_hw_render_details` G0018 (MISCINFO_STRUCT_SIZES+0x1c (=MISC+0x3c);
  value 0x1ec): size of HWRENDERDETAILS the EDM was built for: render details (3D registers +
  3D-side state). From `ui32Sizeof_HWRENDERDETAILS` (1, sgx545-ce).
- `misc_info_struct_sizes.sizeof_hw_rt_data` G0019 (MISCINFO_STRUCT_SIZES+0x20 (=MISC+0x40); value
  0x38): size of HWRTDATA the EDM was built for: render-target data, one per TA/3D overlap slot.
  From `ui32Sizeof_HWRTDATA` (1, sgx545-ce).
- `misc_info_struct_sizes.sizeof_hw_rt_data_set` G0020 (MISCINFO_STRUCT_SIZES+0x24 (=MISC+0x44);
  value 0x50): size of HWRTDATASET the EDM was built for: render-target data set (header 0x18 + RT
  data). From `ui32Sizeof_HWRTDATASET` (1, sgx545-ce).
- `misc_info_struct_sizes.sizeof_hw_transfer_context` G0021 (MISCINFO_STRUCT_SIZES+0x28
  (=MISC+0x48); value 0xb4): size of HWTRANSFERCONTEXT the EDM was built for: HW transfer context.
  From `ui32Sizeof_HWTRANSFERCONTEXT` (1, sgx545-ce).
- `misc_info_struct_sizes.sizeof_host_ctl` G0015 (MISCINFO_STRUCT_SIZES+0x2c (=MISC+0x4c); value
  0x44): size of HOST_CTL the EDM was built for: host control block. From `ui32Sizeof_HOST_CTL` (1,
  sgx545-ce).
- `misc_info_struct_sizes.sizeof_command` G0014 (MISCINFO_STRUCT_SIZES+0x30 (=MISC+0x50); value
  0x20): size of COMMAND the EDM was built for: kernel CCB command. From `ui32Sizeof_COMMAND` (1,
  sgx545-ce).
- `transfer_cmd.isp_render` G0117 (TRANSFERCMD+0x00c): ISP render type/scan. From `isp_render` (3,
  linux-imagination).
- `transfer_cmd.bif_3d_req_base` G0025 (TRANSFERCMD+0x018): 3D requestor base. From
  `EUR_CR_BIF_3D_REQ_BASE` (1, sgx545-ce).
- `transfer_cmd.event_pixel_pds_code` G0026 (TRANSFERCMD+0x024): end-of-tile PDS program. From
  `event_pixel_pds_code` (3, linux-imagination).
- `transfer_cmd.reg_0400` G0340 (TRANSFERCMD+0x038): inferred reading (unconfirmed): Transfer
  command word 14, which loads register 0x0400: bit 25 inverts bits 31:24 of every pixel a fill or
  copy writes, and no other bit changed a pixel; over the every-value source exactly the 128 values
  of bits 31:24 with bit 25 set changed the image. From `transfer_cmd.reg_0400` (ours, resgx545).
- `transfer_cmd.pds_exec_base` G0027 (TRANSFERCMD+0x03c): PDS execution base. From
  `EUR_CR_PDS_EXEC_BASE` (1, sgx545-ce).
- `transfer_cmd.cmd_size` G0115 (TRANSFERCMD+0x0a4): command size, 64-byte multiple. From `cmd_size`
  (3, linux-imagination).
- `transfer_cmd.flags` G0116 (TRANSFERCMD+0x0a8): TQ_FLAGS.* of the transfer. From `ui32Flags` (1,
  sgx545-ce); `flags` (3, linux-imagination).
- `transfer_cmd.load_yuv_csc` G0338 (TRANSFERCMD+0x188): boolean: when set the EDM loads
  CR_TPU_YUV_CSC0_0 .. CR_TPU_YUV_CSC1_4 and CR_TPU_YUV_CSC_INPUT (0x0820-0x0848) from the command's
  words [infer]. From `transfer_cmd.load_yuv_csc` (ours, resgx545).
- `transfer_cmd.load_tpu_luma_key` G0336 (TRANSFERCMD+0x18c): boolean: when set the EDM loads the
  luma key's three words from the command [infer]. From `transfer_cmd.load_tpu_luma_key` (ours,
  resgx545).
- `transfer_cmd.load_use_coeffs` G0337 (TRANSFERCMD+0x190): boolean: when set the EDM loads the USE
  filter block (CR_USE_COEFFS0_A .. CR_USE_COEFFS1_BIAS, CR_USE_COEFFS_MODE, CR_USE_COEFFS2_A ..
  CR_USE_COEFFS2_BIAS) from the command's words [infer]. From `transfer_cmd.load_use_coeffs` (ours,
  resgx545).
- `transfer_cmd.num_pixel_partitions` G0339 (TRANSFERCMD+0x194): DMS_CTRL pixel partitions (31 <<
  22). From `NumPixelPartitions` (2, cdv-libsrv_um).

### flag

- `GEOM_FLAGS.FIRST_KICK` G0241 (CMDTA+0x004 bit0 (0x1)): first kick of a scene. From
  `ROGUE_GEOM_FLAGS_FIRSTKICK` (3, linux-imagination).
- `GEOM_FLAGS.LAST_KICK` G0242 (CMDTA+0x004 bit1 (0x2)): last kick of a scene. From
  `ROGUE_GEOM_FLAGS_LASTKICK` (3, linux-imagination).
- `GEOM_FLAGS.NO_DPM_CONTEXT_LOAD` G0243 (CMDTA+0x004 bit3 (0x8)): tested together with
  GEOM_FLAGS.FIRST_KICK (mask 0x9): when either is set the TA kick skips the calls that invalidate
  the caches, set the BIF bank and reload the RT data's stored DPM context (CR_DPM_STATE_BASE0/1,
  CR_DPM_CONTROL_BASE, CR_MTE_OTPM_BASE from hw_rt_data, DPM state task) [infer]. From
  `GEOM_FLAGS.BIT3` (ours, resgx545).
- `MISC_INFO_FLAGS.READY` G0094 (MISC+0x00 bit0): reply ready (0x1). From
  `PVRSRV_USSE_MISCINFO_READY` (1, sgx545-ce).
- `MISC_INFO_FLAGS.GET_STRUCT_SIZES` G0093 (MISC+0x00 bit1): request struct sizes (0x2). From
  `PVRSRV_USSE_MISCINFO_GET_STRUCT_SIZES` (1, sgx545-ce).
- `FRAG_FLAGS.NO_RENDER` G0237 (render flags bit0 (0x1)): skips the render: the scene's memory is
  freed at its last TA end and the render details complete without a render [infer]. From
  `FRAG_FLAGS.NO_RENDER` (ours, resgx545).
- `FRAG_FLAGS.ABORT` G0231 (render flags bit1 (0x2)): complete the command without running it
  [infer]. From `FRAG_FLAGS.ABORT` (ours, resgx545).
- `FRAG_FLAGS.BIT10` G0232 (render flags bit10 (0x400)): inferred reading (unconfirmed): count this
  render as the scene's completion (the scene's last kick). Measured: at scene-done the EDM
  increments the RT data set's executed_count; set by the client on the scene's last kick [infer].
  From `FRAG_FLAGS.BIT10` (ours, resgx545).
- `FRAG_FLAGS.BIT2` G0233 (render flags bit2 (0x4)): inferred reading (unconfirmed): Bit 2 of the
  render flags word: when each job ends with its render, set or clear it changed no image; what it
  keeps in a scene left open is not shown. From `FRAG_FLAGS.BIT2` (ours, resgx545).
- `FRAG_FLAGS.NO_DEALLOCATE` G0236 (render flags bit3 (0x8)): do not deallocate the scene's pages
  during the render (CR_DPM_3D_DEALLOCATE = 0); the scene continues [infer]. From
  `FRAG_FLAGS.NO_DEALLOCATE` (ours, resgx545).
- `FRAG_FLAGS.SET_ZLSCTL_BIT0` G0238 (render flags bit4 (0x10)): when set, the EDM sets bit 0 of
  CR_ISP_ZLSCTL (writes CR_ISP_ZLSCTL | 0x1) before starting the render; when clear it skips that
  write; what ZLS control bit 0 does is not shown [infer]. From `FRAG_FLAGS.BIT4` (ours, resgx545).
- `FRAG_FLAGS.GET_VIS_RESULTS` G0235 (render flags bit5 (0x20)): render produces visibility results.
  From `ROGUE_FRAG_FLAGS_GET_VIS_RESULTS` (3, linux-imagination).
- `FRAG_FLAGS.DEPTH_BUFFER` G0234 (render flags bit7 (0x80)): depth buffer present. From
  `ROGUE_FRAG_FLAGS_DEPTHBUFFER` (3, linux-imagination).
- `FRAG_FLAGS.STENCIL_BUFFER` G0239 (render flags bit8 (0x100)): stencil buffer present. From
  `ROGUE_FRAG_FLAGS_STENCILBUFFER` (3, linux-imagination).
- `FRAG_FLAGS.TA3D_DEPENDENCY` G0240 (render flags bit9 (0x200)): signal the TA->3D dependency sync
  at the render end [infer]. From `FRAG_FLAGS.TA3D_DEPENDENCY` (ours, resgx545).

### struct

- `device_sync_object` G0101 (0x10): pending values + complete-counter addresses of one sync. From
  `PVRSRV_DEVICE_SYNC_OBJECT` (1, sgx545-ce).
- `misc_info_features` G0113 (0x1c at MISC+0x04): core/DDK identification returned by GETMISCINFO.
  From `PVRSRV_SGX_MISCINFO_FEATURES` (1, sgx545-ce).
- `kernel_ccb` G0109 (0x2000): kernel CCB: 256 commands. From `PVRSRV_SGX_KERNEL_CCB` (1,
  sgx545-ce).
- `host_ctl` G0010 (0x44): host control block (init/power/cleanup status, timers). From
  `SGXMKIF_HOST_CTL` (1, sgx545-ce).
- `transfer_cmd` G0114 (0x4c8, ~ TRANSFERCMD): transfer command structure proper; holds
  TRANSFERCMD_SHARED. From `SGXMKIF_TRANSFERCMD` (1, emgd-linux); `rogue_fwif_cmd_transfer` (3,
  linux-imagination).
- `misc_info` G0110 (0x54): misc-info buffer (hKernelSGXMiscMemInfo). From
  `PVRSRV_SGX_MISCINFO_INFO` (1, sgx545-ce).
- `ccb_ctl` G0095 (0x8, ~ PVRSRV_SGX_CCB_CTL): CCB control: write and read offsets (kernel and
  client CCBs). From `PVRSRV_SGX_CCB_CTL` (1, sgx545-ce); `rogue_fwif_ccb_ctl` (3,
  linux-imagination).
- `hw_transfer_context` G0102 (0xb4, ~ HWTRANSFERCONTEXT): HW transfer context. From
  `SGXMKIF_HWTRANSFERCONTEXT` (1, intel-ctp-santos10); `rogue_fwif_fwtransfercontext` (3,
  linux-imagination).
- `ta3d_ctl` G0024 (0xec (hKernelSGXTA3DCtlMemInfo)): TA/3D control block of the EDM. From
  `sTA3DCtl` (1c, emgd-linux).

## 4. State words, ports and instruction-level terms

### bitfield

- `T0.BITS20_19` G0273 (T0 [20:19] (twiddled textures)): with bit 18 clear, 0 keeps level 0 and 1-3
  let mip levels be read; what the value counts is not shown [infer]. From `T0.BITS20_19` (ours,
  resgx545).
- `T0.BITS26_21` G0274 (T0 [26:21] (twiddled textures)): with 0x3f (the closed driver's value) mip
  levels above 0 are read; with 0-7 only level 0 (on stride textures these bits are T0.STRIDE)
  [infer]. From `T0.BITS26_21` (ours, resgx545).
- `T0.NO_MIPMAPS` G0278 (T0 bit 18): set: only level 0 is read, whatever the LOD; the closed driver
  clears it for a mipmapped texture [infer]. From `T0.NO_MIPMAPS` (ours, resgx545).
- `OUTSEL.PLANES` G0252 (outsel [7:0]): inferred reading (unconfirmed): Low bits of the
  output-select word that turn user clip planes on: 0x53001 has plane 0 on and 0x63003 has planes 0
  and 1 on; for an enabled plane the clip-plane value from the fdpc instruction replaces the
  distance dword the vertex wrote, and a disabled plane ignores it. From `OUTSEL.PLANES` (ours,
  resgx545).

### enum

- `TEXTYPE.STRIDE` G0288 (T1 TEXTYPE 6): strided texture: rows a stride apart (T0.STRIDE), sampled
  clamped to the edge [infer]. From `TEXTYPE.STRIDE` (ours, resgx545).
- `TEXFORMAT` G0286 (TEXFORMAT values): texel format enum: on SGX545 2 RGBA4444, 4 RGBA5551, 5
  RGB565, 12 BGRA8888 (ARGB8888 in memory), 13 RGBA8888, 17 RGBA half-float, 18 float32 (RGBA,
  luminance, depth), 23 PVRTC 2 bpp, 24 PVRTC 4 bpp, 27 ETC1, 28 YUYV, 29 UYVY; with the alternate
  format bit set 25 A8, 26 L8, 27 LA88, 30 luminance half-float (Rogue values differ). From `FORMAT`
  (3, mesa-csbgen).
- `TEXTYPE` G0287 (TEXTYPE values (2D, STRIDE...)): texture type enum (Rogue: 1D, 2D, 3D, CUBE,
  STRIDE...): on SGX545 0 a power-of-two 2D texture, 3 a non-power-of-two one and the YUV streams, 6
  strided (also depth textures). From `TEXTYPE` (3, mesa-csbgen).
- `REGTYPE.INDEX` G0260 (USSE index register i): index register operand. From `USEASM_REGTYPE_INDEX`
  (2, cdv-libusc).
- `REGTYPE.FPINTERNAL` G0259 (USSE internal i0-i2, i0-i2): internal (FP) register operand. From
  `USEASM_REGTYPE_FPINTERNAL` (2, cdv-libusc); `intern` (3, mesa-pco).
- `REGTYPE.FPCONSTANT` G0258 (USSE special constant c, c): hardware constant operand. From
  `USEASM_REGTYPE_FPCONSTANT` (2, cdv-libusc); `const` (3, mesa-pco).
- `VDM_BLOCK.TERMINATE` G0290 (VDM terminate block): end of control stream. From `STREAM_TERMINATE`
  (3, mesa-csbgen).
- `PORT.DOUTU` G0009 (doutu port): start a USC task. From `PVR_ROGUE_PDSINST_DOUT_DST_DOUTU` (3,
  mesa-pds-defs).
- `FDUAL.FDDP_IREG_DEST_NUM` G0227 (dual-issue fddp): dual-issue fddp writes this internal register.
  From `SGX545_USE_FDUAL_FDDP_IREG_DEST_NUM` (2, cdv-libusc).
- `SR.TASK_ID` G0267 (g21 (source bank 5, number 85)): inferred reading (unconfirmed): a per-task id
  the scheduler assigns, constant over a 4x4 block of a fill. From `task_id` (3, mesa-pco).
- `SR.SLOT_NUM` G0266 (g22 (source bank 5, number 86)): inferred reading (unconfirmed): a per-slot
  id the scheduler assigns, constant over a quad. From `slot_num` (3, mesa-pco).
- `SR.TILE_X_PIX` G0268 (g23 (source bank 5, number 87)): the pixel's x within its 32x16 tile. From
  `tile_x_pix` (3, mesa-pco).
- `SR.TILE_Y_PIX` G0269 (g24 (source bank 5, number 88)): the pixel's y within its 32x16 tile. From
  `tile_y_pix` (3, mesa-pco).
- `SR.INST_NUM` G0265 (g25 (source bank 5, number 89)): the instance's place in its 2x2 quad (x[0] +
  2*y[0]). From `inst_num` (3, mesa-pco).
- `PACKMODE` G0253 (sideband PACKMODE values): PBE pack formats (Rogue values differ); on SGX545 0
  is ARGB8888, 3 RGB565. From `PACKMODE` (3, mesa-csbgen).
- `USE.NUM_HW_SPECIAL_CONSTS` G0289 (special constant bank): number of hardware constants. From
  `USEASM_NUM_HW_SPECIAL_CONSTS` (2, cdv-libusc).

### field

- `DOUTI.SHADEMODEL` G0206: (Rogue) iteration shade model; placed on SGX545 as DOUTI0.SHADEMODEL.
  From `PVR_ROGUE_PDSINST_DOUT_FIELDS_DOUTI_SRC_SHADEMODEL` (3, mesa-pds-defs).
- `EMIT2.BITS15_8` G0226 (EMIT2 (emit2 src0) [15:8]): inferred reading (unconfirmed): an emit
  control field: bit 7 valid, bit 0 with it (0x81) an emit that writes nothing (a mask or count of
  0). Measured: 0x80 in every closed program and capture [infer]. From `EMIT2.BITS15_8` (ours,
  resgx545).
- `ISP1.VISREG` G0248 (ISP1 [2:0]): index of the visibility counter the object counts into (with
  ISP1.VISTEST). From `visreg` (3, mesa-csbgen).
- `PDS_SIZE.BITS17_16` G0254 (PDS_SIZE [17:16]): inferred reading (unconfirmed): a size or count of
  output register banks: at 0, 1 and 2 the triangle's o1-o3 land elsewhere while o0 does not change,
  3 the plain value [infer]. From `PDS_SIZE.BITS17_16` (ours, resgx545).
- `T0.MINFILTER` G0276 (T0 [11:10]): minification filter: 1 and 2 linear, 0 and 3 nearest. From
  `minfilter` (3, mesa-csbgen).
- `T0.STRIDE` G0279 (T0 [11:9] + [26:17]): stride of a strided texture in dwords - 1: bits 2:0 in T0
  [11:9], bits 12:3 in T0 [26:17]. From `stride` (3, mesa-csbgen).
- `T0.MAGFILTER` G0275 (T0 [13:12]): magnification filter: 1 and 2 linear, 0 and 3 nearest. From
  `magfilter` (3, mesa-csbgen).
- `T0.ADDRMODE_V` G0271 (T0 [5:3]): T (V) wrap mode: 0 repeat, 1 mirror, 2 clamp, 3 mirror once.
  From `addrmode_v` (3, mesa-csbgen).
- `T0.ADDRMODE_U` G0270 (T0 [8:6]): S (U) wrap mode: 0 repeat, 1 mirror, 2 clamp, 3 mirror once.
  From `addrmode_u` (3, mesa-csbgen).
- `T0.MIPFILTER` G0277 (T0 [9]): filter between mipmap levels: 0 the nearest level (a half rounds
  up), 1 a linear blend of the two levels. From `mipfilter` (3, mesa-csbgen).
- `T1.TEXFORMAT` G0280 (T1 [28:24] (TEXFORMAT)): texel format. From `texformat` (3, mesa-csbgen).
- `T1.TEXTYPE` G0281 (T1 [31:29] (TEXTYPE)): texture type. From `textype` (3, mesa-csbgen).
- `T2.TEXADDR` G0282 (T2 [31:2] (TEXADDR)): texture address >> 2. From `texaddr` (3, mesa-csbgen).
- `T3.CONVERT` G0283 (T3 [17:16]): conversion of the fetched texel: 0 none, 1 c10, 2 f16 pairs, 3
  f32 channels [infer]. From `T3.CONVERT` (ours, resgx545).
- `T3.DATA_SIZE` G0284 (T3 [26:23]): inferred reading (unconfirmed): Bits 26:23 of the fourth
  sampler word are named in the sampler sweep but that sweep varied only the conversion fields; the
  6.1 data show nothing about this field beyond its name. From `T3.DATA_SIZE` (ours, resgx545).
- `VDM_STATE1.BITS11_9` G0292 (VDM_STATE1 [11:9]): inferred reading (unconfirmed): Bits 11:9 of the
  state task's second word: 0 removes the 64x64 triangle (4096 background pixels), 1, 3, 4, 5 and 6
  give the baseline image, and 7 hangs the job in the sweep but renders in a probe job, so that
  value is unsettled; the job writes 2. From `VDM_STATE1.BITS11_9` (ours, resgx545).
- `VDM_STATE1.BITS15_13` G0293 (VDM_STATE1 [15:13]): inferred reading (unconfirmed): Bits 15:13 of
  the state task's second word: 0, 5 and 6 hang the job, 2, 3, 4 and 7 give the baseline image; the
  job writes 1. From `VDM_STATE1.BITS15_13` (ours, resgx545).
- `FEEDBACK_CTL.DEPTH_ALWAYS` G0228 (atst8/depthf src1 [3:2]): inferred reading (unconfirmed): Bits
  3:2 of the control word the punch-through pass passes in src1: clear in 0xe001, which keeps the
  nearest copy's pixels (1062 and 36 pixels), and set in 0xffffffff, which keeps the last copy's
  (1074 and 24 pixels, the depth-always result). From `FEEDBACK_CTL.DEPTH_ALWAYS` (ours, resgx545).
- `DOUTI0.BITS10_5` G0208 (douti word 0 [10:5]): modifies the texture fetch's coordinates: bit 6 the
  x axis to the source's last column, bit 7 the y axis to its last row, bit 9 both, bit 10 both to
  texel (0, 0); bits 5 and 8 nothing seen; 0 from the closed driver [infer]. From `DOUTI0.BITS10_5`
  (ours, resgx545).
- `DOUTI0.ATTR_SOURCE` G0207 (douti word 0 [16:11]): what the iterator writes to the task's primary
  attributes: 0 the pixel's window position, 1 the first texture coordinate set, 32 the vertex
  colour (OUTSEL.COLOUR_PRES) packed as ARGB8888 in one dword, default 0xff000000, 33 a second
  colour (0xff000000 when absent), 2-31 zero, 34 the depth plane a punch-through pt phase hands the
  ISP with pcoeff (three components; (0, 0, 0.5) read outside punch-through), 35 zero or a hang, 36
  and above nothing [infer]. From `DOUTI0.ATTR_SOURCE` (ours, resgx545).
- `DOUTI0.VERTEX_FRAC` G0217 (douti word 0 [18]): each vertex's value reduced to its fractional part
  (mod 1) before the iteration [infer]. From `DOUTI0.VERTEX_FRAC` (ours, resgx545).
- `DOUTI0.FLAT` G0211 (douti word 0 [21]): iterate flat: every pixel gets the value of the vertex
  DOUTI0.SHADEMODEL selects (0-2), or the smooth iteration with 3 [infer]. From `DOUTI0.FLAT` (ours,
  resgx545).
- `DOUTI0.SHADEMODEL` G0215 (douti word 0 [26:25]): 0-2 the vertex whose value every pixel takes, 3
  smooth: on the vertex colour (source 32) by itself, on a coordinate set only with DOUTI0.FLAT
  [infer]. From `DOUTI0.SHADEMODEL` (ours, resgx545).
- `DOUTI0.FIXED_OUT` G0210 (douti word 0 [27]): the iterated value written as two's-complement fixed
  point, 28 fractional bits, in bits 29:0 [infer]. From `DOUTI0.FIXED_OUT` (ours, resgx545).
- `DOUTI0.F16` G0209 (douti word 0 [28]): write the iterated values as half floats, two to a dword
  [infer]. From `DOUTI0.F16` (ours, resgx545).
- `DOUTI0.TEX_COORD_SOURCE` G0216 (douti word 0 [4:0]): the iterated value the texture fetch takes
  its coordinates from, numbered as DOUTI0.ATTR_SOURCE: 1 the first coordinate set; 0 no fetch
  [infer]. From `DOUTI0.TEX_COORD_SOURCE` (ours, resgx545).
- `DOUTU0.TEMPS` G0008 (doutu U0 [31:24]): temporaries to allocate, in units of 4. From
  `PVR_ROGUE_PDSINST_DOUT_FIELDS_DOUTU_SRC0_TEMPS` (3, mesa-pds-defs).
- `DOUTU1.BITS11_3` G0220 (doutu U1 [11:3]): it places the end-of-tile write on the target (x); in
  32-pixel tile columns from bit 4; width open [infer]. From `DOUTU1.BITS11_3` (ours, resgx545).
- `DOUTU1.BITS21_12` G0221 (doutu U1 [21:12]): it places the end-of-tile write on the target (y); in
  16-pixel tile rows from bit 13; width open [infer]. From `DOUTU1.BITS21_12` (ours, resgx545).
- `ISP0.PASS_TYPE` G0245 (isp0 [27:25]): pass type. From `passtype` (3, mesa-csbgen).
- `MTECTL.CULL_MODE` G0251 (mtectl [1:0]): cull mode. From `cullmode` (3, mesa-csbgen).
- `SIDEBAND.PACKMODE` G0264 (sideband [5:0]): pixel pack format. From `packmode` (3, mesa-csbgen).
- `SIDEBAND.BITS8_6` G0262 (sideband [8:6] [infer]): inferred reading (unconfirmed): a PBE
  sub-format, downscale or rotation field, 0 for plain output (Rogue downscale/source_pos, AGX
  rotate/flip). Measured: 0 in every closed program and capture [infer]. From `SIDEBAND.BITS8_6`
  (ours, resgx545).
- `SIDEBAND.MEMLAYOUT` G0263 (sideband bit 13): memory layout. From `memlayout` (3, mesa-csbgen).
- `VIEWPORT.X_OFFSET` G0295 (state block vp0 (with PRESENCE.VIEWPORT)): x offset of the viewport
  transform, an IEEE single [infer]. From `VIEWPORT.X_OFFSET` (ours, resgx545).
- `VIEWPORT.X_SCALE` G0296 (state block vp1 (with PRESENCE.VIEWPORT)): x scale of the viewport
  transform, an IEEE single [infer]. From `VIEWPORT.X_SCALE` (ours, resgx545).
- `VIEWPORT.Y_OFFSET` G0297 (state block vp2 (with PRESENCE.VIEWPORT)): y offset of the viewport
  transform, an IEEE single [infer]. From `VIEWPORT.Y_OFFSET` (ours, resgx545).
- `VIEWPORT.Y_SCALE` G0298 (state block vp3 (with PRESENCE.VIEWPORT)): y scale of the viewport
  transform, an IEEE single [infer]. From `VIEWPORT.Y_SCALE` (ours, resgx545).
- `VIEWPORT.Z_OFFSET` G0299 (state block vp4 (with PRESENCE.VIEWPORT)): z offset of the viewport
  transform, an IEEE single [infer]. From `VIEWPORT.Z_OFFSET` (ours, resgx545).
- `VIEWPORT.Z_SCALE` G0300 (state block vp5 (with PRESENCE.VIEWPORT)): z scale of the viewport
  transform, an IEEE single [infer]. From `VIEWPORT.Z_SCALE` (ours, resgx545).
- `VDM_TASK0.MAX_VERTICES` G0294 (vertex-task word 0 [31:28]): the vertices one vertex task takes,
  less one (in index order); 7 for the closed driver's screen-space draws, 15 for compiled shaders;
  0 hangs a larger draw [infer]. From `VDM_TASK0.MAX_VERTICES` (ours, resgx545).

### flag

- `DOUTI.PERSPECTIVE` G0205: (Rogue) perspective-correct iteration; placed on SGX545 as
  DOUTI0.PERSPECTIVE. From `PVR_ROGUE_PDSINST_DOUT_FIELDS_DOUTI_SRC_PERSPECTIVE` (3, mesa-pds-defs).
- `MIPMAPS_PRESENT` G0250: texture has mipmaps. From `mipmaps_present` (3, mesa-csbgen).
- `ISP1.POLY_OFFSET` G0247 (ISP1 [23]): the object takes the polygon offset [infer]. From
  `ISP1.POLY_OFFSET` (ours, resgx545).
- `ISP1.VISTEST` G0249 (ISP1 [3]): visibility test: the object's covered pixels count into the
  counter ISP1.VISREG names. From `vistest` (3, mesa-csbgen).
- `T0.ALPHA_FROM_LUMA_KEY` G0272 (T0 [31]): the texture is read as RGB without alpha, the alpha
  coming from the luma key (CR_TPU_LUMA_KEY_*) [infer]. From `T0.ALPHA_FROM_LUMA_KEY` (ours,
  resgx545).
- `T3.NORMALIZE` G0285 (T3 bit 15): divide converted channel values by 255 (65535 for u16) [infer].
  From `T3.NORMALIZE` (ours, resgx545).
- `VDM_STATE1.BIT8` G0291 (VDM_STATE1 bit 8): inferred reading (unconfirmed): marks the constant or
  no-op state blocks. Measured: set on the captured state blocks whose PDS program our current term
  a constant block or starts a no-op USE task, clear on the MTE-state and vertex blocks [infer].
  From `VDM_STATE1.BIT8` (ours, resgx545).
- `FEEDBACK_CTL.KEEP` G0230 (atst8/depthf src1 bit 0): inferred reading (unconfirmed): Bit 0 of the
  control word the punch-through pass passes in src1: set in both words that draw (0xe001,
  0xffffffff) and clear in 0xe000 and 0xe002, which draw nothing; set alone (0x1, 0x3, 0xf,
  0x80000001) it draws nothing either. From `FEEDBACK_CTL.KEEP` (ours, resgx545).
- `FEEDBACK_CTL.ENABLE` G0229 (atst8/depthf src1 bit 14): inferred reading (unconfirmed): Bit 14 of
  the control word the punch-through pass passes in src1: set in both words that draw (0xe001,
  0xffffffff), clear in seven of the nine words that draw nothing; set with bit 0 clear (0xe000,
  0xe002) still draws nothing. From `FEEDBACK_CTL.ENABLE` (ours, resgx545).
- `DOUTI0.PERSPECTIVE` G0214 (douti word 0 [24]): perspective-correct iteration (the values divided
  by w at the vertices, the result by the iterated 1/w); clear, affine [infer]. From
  `DOUTI0.PERSPECTIVE` (ours, resgx545).
- `DOUTI0.LAST_ITER` G0213 (douti word 0 [29]): set on the program's last iteration without a
  texture fetch: signals the wait of DOUTU1.WAIT_ITER [infer]. From `DOUTI0.LAST_ITER` (ours,
  resgx545).
- `DOUTI0.LAST_FETCH` G0212 (douti word 0 [30]): set on the program's last iteration with a texture
  fetch: signals the wait of DOUTU1.WAIT_FETCH; an iteration with a fetch source delivers its values
  with the texel [infer]. From `DOUTI0.LAST_FETCH` (ours, resgx545).
- `DOUTI1.FLAT` G0218 (douti word 1 [6]): iterate flat: every pixel gets the value of the vertex
  DOUTI0.SHADEMODEL selects (0-2), as DOUTI0.FLAT; with shade model 3 the job hangs [infer]. From
  `DOUTI1.FLAT` (ours, resgx545).
- `DOUTU1.LAST_TILE` G0223 (doutu U1 [22]): carried by the end-of-tile tasks of the render's last
  two 16x16 tiles: the render ends when they do; set on the other tiles' tasks it changes nothing
  seen [infer]. From `DOUTU1.LAST_TILE` (ours, resgx545).
- `DOUTU1.EMITPIX_TASK` G0222 (doutu U1 [23]): set on the tasks whose program ends in emitpix (end
  of tile, end of render) and only on them [infer]. From `DOUTU1.EMITPIX_TASK` (ours, resgx545).
- `DOUTU1.WAIT_ITER` G0225 (doutu U1 [24]): the task waits for its PDS program's iterations (the one
  with DOUTI0.LAST_ITER) before it runs [infer]. From `DOUTU1.WAIT_ITER` (ours, resgx545).
- `DOUTU1.WAIT_FETCH` G0224 (doutu U1 [25]): the task waits for its PDS program's texture fetch
  before it runs [infer]. From `DOUTU1.WAIT_FETCH` (ours, resgx545).
- `DOUTU1.BIT2` G0219 (doutu U1 [2]): inferred reading (unconfirmed): a scheduling hint of pixel and
  secondary tasks: set or clear, no image changes, punch-through included (E137); the ISP visibility
  counter differs between the two punch-through runs and nothing is concluded from it (E137).
  Measured: set (U1 = 4) in the pixel tasks of our fill, copy and triangle jobs [infer]. From
  `DOUTU1.BIT2` (ours, resgx545).
- `PIXEL_EVENT.END_OF_TILE` G0255 (pixel event input ir1 bit 1): the signal that a tile is complete,
  on which the EDM generates the task emitting the tile. From `tile is complete` (4,
  patent-US8046761).
- `PIXEL_EVENT.LAST_TILE` G0256 (pixel event input ir1 bit 2): set on the end-of-tile events of the
  render's last two 16x16 tiles (its bottom-right 32x16 pixels), and on no other; the pixel-event
  program copies it into the end-of-tile task's DOUTU1.LAST_TILE [infer]. From
  `PIXEL_EVENT.LAST_TILE` (ours, resgx545).
- `PIXEL_EVENT.PT_OFF` G0257 (pixel event input ir1 bit 3): inferred reading (unconfirmed): Input
  bit 3 of the pixel-event program is named in the punch-through probes but no probe used it, so the
  6.1 data show nothing about it beyond its name. From `PIXEL_EVENT.PT_OFF` (ours, resgx545).
- `SIDEBAND.BIT9` G0261 (sideband bit 9): inferred reading (unconfirmed): marks the emit that
  completes the tile: the PBE counts the emits with it against its tiles. Measured: needed for an
  emit to complete its tile: with it clear the only emit hangs; an extra emit with it set leaves the
  PBE queue one emit behind, with it clear for one job only; not tile-relative addressing [infer].
  From `tilerelative` (3, mesa-csbgen).

### struct

- `ISP0` G0244 (ISP word 0 (isp0)): ISP state word A: depth, pass, object type. From `STATE_ISPA`
  (3, mesa-csbgen).
- `ISP1` G0246 (ISP word 1): inferred reading (unconfirmed): The second word of the render's ISP
  state; bits 13 to 25 set one at a time left a 4x triangle at the sample rate unchanged, so those
  bits do not turn per-sample shading on. From `ISP1` (ours, resgx545).

## 5. Sources

- `emgd-linux` (tier 1): Intel EMGD for Linux, SGX535 kernel side.
- `emgd-psb_regs` (tier 1): Intel's psb_regs.h in EMGD: the SGX535 (Poulsbo) register list (MIT).
- `intel-ctp-santos10` (tier 1): Samsung's GPL kernel for its santos10 device (Intel Clover Trail+,
  SGX544MP2), DDK 1.9.
- `sgx545-ce` (tier 1): Intel's GPL DDK 1.7 kernel module for Cedarview, our core.
- `cdv-libsrv_um` (tier 2): strings and exports of libsrv_um.so in our Cedarview package.
- `cdv-libusc` (tier 2): strings of libusc.so in our Cedarview package.
- `linux-imagination` (tier 3): Imagination's Rogue kernel driver, drivers/gpu/drm/imagination.
- `mesa-csbgen` (tier 3): Mesa src/imagination/csbgen: Rogue state words (Imagination, MIT).
- `mesa-pco` (tier 3): Mesa src/imagination/pco: the Rogue shader ISA (MIT).
- `mesa-pds-defs` (tier 3): Mesa src/imagination/vulkan/pds: Rogue PDS instructions (MIT).
- `imgtec-pvrtune-counters` (tier 4): Imagination's PVRTune Counter List and Description (2017).
- `imgtec-sgx-arch-guide-1.0.13` (tier 4): Imagination's PowerVR Series 5 SGX Architecture Guide for
  Developers 1.0.13 (2012, public).
- `imgtec-sgx-arch-guide-1.0.8` (tier 4): Imagination's PowerVR Series5 Graphics SGX architecture
  guide for developers 1.0.8 (2011, public).
- `imgtec-technology-overview-1.0.2e` (tier 4): Imagination's PowerVR Technology Overview 1.0.2e
  (2010).
- `patent-US7324115` (tier 4): patent US7324115 (Imagination Technologies).
- `patent-US8046761` (tier 4): patent US8046761 (Imagination Technologies).
- `patent-US8669987` (tier 4): patent US8669987 (Imagination Technologies).
- `patent-US8723860` (tier 4): patent US8723860 (Imagination Technologies).
- `patent-US8743117` (tier 4): patent US8743117 (Imagination Technologies).
- `patent-US9384584` (tier 4): patent US9384584 (Imagination Technologies).
- `powervr-docs` (tier 4): Imagination's public PowerVR architecture guides.
- `ti-omap4430-trm` (tier 4): TI's public OMAP4430 TRM (swpu231ap), chapter 11 on its SGX540:
  Imagination's architecture in its own terms.
- `resgx545` (tier ours): this project: our own term for a thing no open source names, after our
  measurements.
