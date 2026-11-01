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

- `PBSize` G0480: config key (libsrv_um): parameter buffer size, in DPM pages. From `PBSize` (2,
  cdv-libsrv_um).
- `PDSThreshold` G0489: config key (libsrv_um): PDS page threshold of the parameter buffer; register
  binding unconfirmed. From `PDSThreshold` (2, cdv-libsrv_um).
- `Parameter Buffer (PB)` G0064: memory holding the binned scene (TA output, 3D input). From `PB`
  (4, imgtec-sgx-arch-guide-1.0.13); `Parameter Buffer` (4, imgtec-sgx-arch-guide-1.0.8).
- `Tile Based Deferred Rendering (TBDR)` G0068: bin the whole scene first, then render tile by tile,
  shading only visible pixels. From `TBDR` (4, imgtec-sgx-arch-guide-1.0.13).
- `control stream` G0516: per-tile control stream data written by the TA. From `control stream` (4,
  patent-US8669987).
- `display list` G0070: per-tile display lists (macrotiles). From `display list` (4,
  patent-US7324115).
- `macro tile` G0557: Rogue firmware array of macro tiles (analogue). From `macrotile_array` (3,
  linux-imagination); `macro tile` (4, patent-US7978199).
- `partial render` G0558: Rogue fragment job run when the PM runs out of memory (analogue). From
  `partial render` (3, linux-imagination); `partial render` (4, imgtec-performance-recommendations);
  `Partial render` (4, patent-US8723860).
- `programmable sample positions` G0333: the samples' positions within the pixel are programmable
  (with 4x multisampling). From `programmable sample positions` (4, ti-omap4430-trm).
- `region header` G0562: per-tile region headers written by geometry (Rogue analogue). From `region
  header` (3, linux-imagination); `region header` (4, patent-US9105131); `Region Header` (4,
  patent-US9384584).
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
- `ZLSThreshold` G0505 (CR_DPM_ZLS_PAGE_THRESHOLD): config key (libsrv_um): ZLS page threshold of
  the parameter buffer. From `ZLSThreshold` (2, cdv-libsrv_um).

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

- `CR_HWPERF_CTRL.GROUP` G0416 (0x0040[12:9]): counter group the EDM selects from host control dword
  15 when HWPerf is on; what each group counts is not measured here (PVRTune's groups: 0 overview, 1
  triangles and vertices, 2 tiling, 3 ISP, 4 TSP, 5 USSE, 6 texturing) [infer]. From
  `CR_HWPERF_CTRL.GROUP` (ours, resgx545).
- `CR_SOFT_RESET.TA_RESET` G0439 (0x0080[2]): hold the TA in reset. From
  `EUR_CR_SOFT_RESET_TA_RESET` (1, sgx545-ce).
- `CR_EVENT_STATUS.DPM_3D_MEM_FREE` G0398 (0x012c[0]): status: DPM finished freeing 3D pages. From
  `EUR_CR_EVENT_STATUS_DPM_3D_MEM_FREE` (1, sgx545-ce).
- `CR_EVENT_STATUS.TPC_FLUSH` G0351 (0x012c[10]): status: tail-pointer cache flush done. From
  `EUR_CR_EVENT_STATUS_TPC_FLUSH` (1, sgx545-ce).
- `CR_EVENT_STATUS.TA_TERMINATE` G0404 (0x012c[12]): status: TA terminate done. From
  `EUR_CR_EVENT_STATUS_TA_TERMINATE` (1, sgx545-ce).
- `CR_EVENT_STATUS.TA_FINISHED` G0403 (0x012c[13]): status: TA pass finished. From
  `EUR_CR_EVENT_STATUS_TA_FINISHED` (1, sgx545-ce).
- `CR_EVENT_STATUS.SW_EVENT` G0092 (0x012c[14]): status: software event. From
  `EUR_CR_EVENT_STATUS_SW_EVENT` (1, sgx545-ce).
- `CR_EVENT_STATUS.BREAKPOINT` G0397 (0x012c[15]): status: breakpoint hit. From
  `EUR_CR_EVENT_STATUS_BREAKPOINT` (1, sgx545-ce).
- `CR_EVENT_STATUS.PIXELBE_END_RENDER` G0402 (0x012c[18]): status: pixel back end finished the
  render. From `EUR_CR_EVENT_STATUS_PIXELBE_END_RENDER` (1, sgx545-ce).
- `CR_EVENT_STATUS.DPM_OUT_OF_MEMORY_MT` G0400 (0x012c[1]): status: DPM out of memory (macrotile).
  From `EUR_CR_EVENT_STATUS_DPM_OUT_OF_MEMORY_MT` (1, sgx545-ce).
- `CR_EVENT_STATUS.OTPM_INV` G0350 (0x012c[20]): status: OTPM invalidated. From
  `EUR_CR_EVENT_STATUS_OTPM_INV` (1, sgx545-ce).
- `CR_EVENT_STATUS.ISP2_ZLS_CSW_FINISHED` G0349 (0x012c[21]): status: second ISP finished a ZLS
  context switch. From `EUR_CR_EVENT_STATUS_ISP2_ZLS_CSW_FINISHED` (1, sgx545-ce).
- `CR_EVENT_STATUS.DPM_INIT_END` G0347 (0x012c[22]): status: DPM initialisation finished. From
  `EUR_CR_EVENT_STATUS_DPM_INITEND` (1, sgx545-ce).
- `CR_EVENT_STATUS.TIMER` G0405 (0x012c[29]): status: event timer expired (CR_EVENT_TIMER). From
  `EUR_CR_EVENT_STATUS_TIMER` (1, sgx545-ce).
- `CR_EVENT_STATUS.DPM_OUT_OF_MEMORY_GBL` G0399 (0x012c[2]): status: DPM out of memory (global
  list). From `EUR_CR_EVENT_STATUS_DPM_OUT_OF_MEMORY_GBL` (1, sgx545-ce).
- `CR_EVENT_STATUS.DPM_REACHED_MEM_THRESH` G0401 (0x012c[3]): status: DPM page use reached the
  threshold. From `EUR_CR_EVENT_STATUS_DPM_REACHED_MEM_THRESH` (1, sgx545-ce).
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
- `CR_ISP_CTL.VALID_ID` G0418 (0x0414[5:0]): validation threshold: opaque and translucent objects
  whose ISP1.VALID_ID is below it are not drawn (Rogue analogue). From `ROGUE_CR_ISP_CTL_VALID_ID`
  (3, linux-imagination).
- `CR_ISP_MSAA.MODE` G0123 (0x042c[1:0]): inferred reading (unconfirmed): multisample mode: 0 one
  sample, 1 and 2 change the image, 3 hangs [infer]. From `CR_ISP_MSAA.MODE` (ours, resgx545).
- `CR_ISP_MSAA.ENABLE` G0122 (0x042c[31]): inferred reading (unconfirmed): enables the multisampled
  ISP path: with it clear and CR_ISP_MSAA.MODE at 2 no pixel of the triangle is written; whether the
  triangle is still tiled, and what it does at mode 1 or at mode 0 with other bits set, are not
  shown; set in every capture [infer]. From `CR_ISP_MSAA.ENABLE` (ours, resgx545).
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
- `CR_DMS_CTRL.MAX_NUM_PIXEL_PARTITIONS` G0363 (SGX535: 0x0a74[24:22]; SGX545 position unconfirmed):
  maximum pixel partitions. From `_PSB_CD_CTRL_MAX_NUM_PIXEL_PARTITIONS_MASK` (1c, emgd-psb_regs).
- `CR_DMS_CTRL.MAX_NUM_VERTEX_PARTITIONS` G0364 (SGX535: 0x0a74[27:25]; SGX545 position
  unconfirmed): maximum vertex partitions. From `_PSB_CD_CTRL_MAX_NUM_VERTEX_PARTITIONS_MASK` (1c,
  emgd-psb_regs).

### concept

- `GlobalThreshold` G0470: config key (libsrv_um): global-list page threshold of the parameter
  buffer; binding to CR_DPM_TA_GLOBAL_LIST unconfirmed. From `GlobalThreshold` (2, cdv-libsrv_um).
- `TAThreshold` G0495 (CR_DPM_TA_PAGE_THRESHOLD): config key (libsrv_um): TA page threshold of the
  parameter buffer. From `TAThreshold` (2, cdv-libsrv_um).

### flag

- `CR_SOFT_RESET.TA_RESET` G0439 (0x0080[2]): hold the TA in reset. From `_PSB_CS_RESET_TA_RESET`
  (1c, emgd-psb_regs).
- `CR_EVENT_STATUS.TA_TERMINATE` G0404 (0x012c[12]): status: TA terminate done (Rogue analogue).
  From `ROGUE_CR_EVENT_STATUS_TA_TERMINATE` (3, linux-imagination).
- `CR_EVENT_STATUS.TA_FINISHED` G0403 (0x012c[13]): status: TA pass finished (Rogue analogue). From
  `ROGUE_CR_EVENT_STATUS_TA_FINISHED` (3, linux-imagination).
- `CR_EVENT_STATUS.PIXELBE_END_RENDER` G0402 (0x012c[18]): status: pixel back end finished the
  render (Rogue analogue). From `ROGUE_CR_EVENT_STATUS_PIXELBE_END_RENDER` (3, linux-imagination).
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
- `CR_HWPERF_CTRL` G0415 (0x0040): performance-counter control: 0x1ff (no group, the counters read
  0) with HWPerf status 0; with a non-zero status, the group in bits 12:9 and bits 8:0 clear, and
  the counters count [infer]. From `CR_HWPERF_CTRL` (ours, resgx545).
- `CR_HWPERF_COUNTER0` G0406 (0x0044): HWPerf counter 0: counts the event the selected counter group
  (CR_HWPERF_CTRL.GROUP) routes to it; zero while no group is selected [infer]. From
  `CR_HWPERF_COUNTER0` (ours, resgx545).
- `CR_HWPERF_COUNTER1` G0407 (0x0048): HWPerf counter 1: counts the event the selected counter group
  (CR_HWPERF_CTRL.GROUP) routes to it; zero while no group is selected [infer]. From
  `CR_HWPERF_COUNTER1` (ours, resgx545).
- `CR_HWPERF_COUNTER2` G0408 (0x004c): HWPerf counter 2: counts the event the selected counter group
  (CR_HWPERF_CTRL.GROUP) routes to it; zero while no group is selected [infer]. From
  `CR_HWPERF_COUNTER2` (ours, resgx545).
- `CR_HWPERF_COUNTER3` G0409 (0x0050): HWPerf counter 3: counts the event the selected counter group
  (CR_HWPERF_CTRL.GROUP) routes to it; zero while no group is selected [infer]. From
  `CR_HWPERF_COUNTER3` (ours, resgx545).
- `CR_HWPERF_COUNTER4` G0410 (0x0054): HWPerf counter 4: counts the event the selected counter group
  (CR_HWPERF_CTRL.GROUP) routes to it; zero while no group is selected [infer]. From
  `CR_HWPERF_COUNTER4` (ours, resgx545).
- `CR_HWPERF_COUNTER5` G0411 (0x0058): HWPerf counter 5: counts the event the selected counter group
  (CR_HWPERF_CTRL.GROUP) routes to it; zero while no group is selected [infer]. From
  `CR_HWPERF_COUNTER5` (ours, resgx545).
- `CR_HWPERF_COUNTER6` G0412 (0x005c): HWPerf counter 6: counts the event the selected counter group
  (CR_HWPERF_CTRL.GROUP) routes to it; zero while no group is selected [infer]. From
  `CR_HWPERF_COUNTER6` (ours, resgx545).
- `CR_HWPERF_COUNTER7` G0413 (0x0060): HWPerf counter 7: counts the event the selected counter group
  (CR_HWPERF_CTRL.GROUP) routes to it; zero while no group is selected [infer]. From
  `CR_HWPERF_COUNTER7` (ours, resgx545).
- `CR_HWPERF_COUNTER8` G0414 (0x0064): HWPerf counter 8: counts the event the selected counter group
  (CR_HWPERF_CTRL.GROUP) routes to it; zero while no group is selected [infer]. From
  `CR_HWPERF_COUNTER8` (ours, resgx545).
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
- `CR_PDS_CACHE_HOST_CLEAR` G0429 (0x0140): clear PDS cache invalidate status. From
  `PSB_CR_PDS_CACHE_HOST_CLEAR` (1c, emgd-psb_regs).
- `CR_TIMER` G0053 (0x0144): free-running timer. From `EUR_CR_TIMER` (1, sgx545-ce);
  `ROGUE_CR_TIMER` (3, linux-imagination).
- `CR_REG_0148` G0151 (0x0148): inferred reading (unconfirmed): a per-job base address or mode of
  the 3D and transfer paths for a feature these clients leave off. Measured: per-render word the
  host supplies with the 3D registers (transfer command and render details); 0 in captures [infer].
  From `CR_REG_0148` (ours, resgx545).
- `CR_VDM_START` G0459 (0x0200): starts the VDM (TA) pass. From `PSB_CR_VDM_START` (1c,
  emgd-psb_regs).
- `CR_TE_AA` G0158 (0x0204): tiling-engine anti-aliasing word: 0x20000000 in every single-sample
  capture, bits 31 and 30 more (0xe0000000) with 4x multisampling [infer]. From `ROGUE_CR_TE_AA` (3,
  linux-imagination); `ROGUE_CR_TE_AA` (3, mesa-csbgen).
- `CR_TE_MTILE1` G0448 (0x0208): macro-tile boundaries (four or sixteen macro-tiles). From
  `configuration registers defining the macro-tile boundaries` (4, patent-US8669987).
- `CR_TE_MTILE2` G0449 (0x020c): macro-tile boundaries (four or sixteen macro-tiles). From
  `configuration registers defining the macro-tile boundaries` (4, patent-US8669987).
- `CR_TE_SCREEN` G0159 (0x0210): screen size in tiles for the tiling engine (Rogue analogue). From
  `ROGUE_CR_TE_SCREEN` (3, linux-imagination); `ROGUE_CR_TE_SCREEN` (3, mesa-csbgen).
- `CR_TE_MACROTILE_STRIDE` G0447 (0x0214): inferred reading (unconfirmed): Tiling-engine register
  loaded by the TA kick from the TA command; it reads 0x10 for a 64x64 target and 0x20 for a 256x256
  one, read as a macrotile stride. From `CR_TE_MACROTILE_STRIDE` (ours, resgx545).
- `CR_TE_PSG` G0450 (0x0218): tiling-engine control word: bit 22 set on the kick that ends the
  scene, bit 25 with a depth/stencil buffer (Rogue analogue). From `ROGUE_CR_TE_PSG` (3,
  mesa-csbgen).
- `CR_TE_PSGREGION_ADDR` G0451 (0x021c): base address of the region headers the TA writes (Rogue
  analogue). From `ROGUE_CR_TE_PSGREGION_ADDR` (3, mesa-csbgen).
- `CR_TE_TPC_ADDR` G0454 (0x0220): base address of the tail-pointer cache memory (Rogue analogue).
  From `ROGUE_CR_TE_TPC_ADDR` (3, mesa-csbgen).
- `CR_TE_TPCCONTROL` G0453 (0x0224): tail-pointer cache control (clear/flush). From
  `PSB_CR_TE_TPCCONTROL` (1c, emgd-psb_regs).
- `CR_MTE_MULTISAMPLECTL` G0145 (0x0230): the sample positions on the TA side: the TA command word
  that loads it carries CR_ISP_MULTISAMPLECTL's value in every capture, 0x88 with one sample,
  0xeaa26e26 with 4x multisampling [infer]. From `ROGUE_CR_PPP_MULTISAMPLECTL` (3, mesa-csbgen).
- `CR_MTE_OTPM_BASE` G0427 (0x0234): address of the RT data's OTPM memory, loaded before
  CR_MTE_OTPM_OP on a first kick and on DPM context store/load [infer]. From `CR_MTE_OTPM_BASE`
  (ours, resgx545).
- `CR_VDM_CTRL_STREAM_BASE` G0458 (0x0238): base address of the VDM input control stream (Rogue
  analogue). From `ROGUE_CR_VDM_CTRL_STREAM_BASE` (3, mesa-csbgen).
- `CR_MTE_CTRL` G0426 (0x023c): macro tiling engine control. From `EUR_CR_MTE_CTRL` (1,
  intel-ctp-santos10).
- `CR_MTE_RHW_MIN` G0147 (0x0240): minimum 1/w: a vertex whose 1/w is not above this value's
  magnitude has 1/w stored as CR_MTE_RHW_CLAMP in the TA's object (1e-6 from the closed driver: w
  beyond 1e6) [infer]. From `CR_MTE_RHW_MIN` (ours, resgx545).
- `CR_MTE_RHW_CLAMP` G0146 (0x0244): the 1/w the TA stores for a vertex at or below CR_MTE_RHW_MIN
  [infer]. From `CR_MTE_RHW_CLAMP` (ours, resgx545).
- `CR_PPP_SCREEN` G0430 (0x0248): screen size in pixels: width - 1 (15:0), height - 1 (31:16) (Rogue
  analogue); the square targets measured do not tell which half is the width [infer]. From
  `ROGUE_CR_PPP_SCREEN` (3, mesa-csbgen).
- `CR_MTE_OTPM_OP` G0428 (0x024c): OTPM (object pointer cache) operation. From `PSB_CR_MTE_OTPM_OP`
  (1c, emgd-psb_regs).
- `CR_PPP_SIGNATURE` G0431 (0x026c): running signature of the primitive pipeline's output; the EDM
  waits for it to stop changing (Rogue analogue). From `ROGUE_CR_PPP_SIGNATURE` (3,
  linux-imagination).
- `CR_TE_CONTEXT_STATE` G0444 (0x0274): tiling-engine state saved into the render details at a TA
  end and restored at the next kick of the scene [infer]. From `CR_TE_CONTEXT_STATE` (ours,
  resgx545).
- `CR_TE_DIAG2` G0445 (0x0284): TE diagnostic: post-region primitive-tile count. From
  `PSB_CR_TE_DIAG2` (1c, emgd-psb_regs).
- `CR_TE_DIAG5` G0446 (0x0290): TE diagnostic: PSG control-dword count. From `PSB_CR_TE_DIAG5` (1c,
  emgd-psb_regs).
- `CR_TE_REG_02A8` G0452 (0x02a8): inferred reading (unconfirmed): the tiling engine's resume
  position after an interrupted TA: an 8-bit field in 19:12. Measured: TA command word; 0 in
  captures [infer]. From `CR_TE_REG_02A8` (ours, resgx545).
- `CR_TA_REG_02B0` G0440 (0x02b0): inferred reading (unconfirmed): context store/resume state of an
  interrupted TA: an 8-bit field in 31:24 (state flags). Measured: TA command word; 0 in captures
  [infer]. From `CR_TA_REG_02B0` (ours, resgx545).
- `CR_TA_REG_02B4` G0441 (0x02b4): inferred reading (unconfirmed): TA context status: reads 0xff
  after any job, a valid or done mask of the stored state. Measured: TA command word; 0 in captures
  [infer]. From `CR_TA_REG_02B4` (ours, resgx545).
- `CR_TA_REG_02D0` G0442 (0x02d0): inferred reading (unconfirmed): the TA's context state base (a
  dword address), read only when an interrupted TA resumes. Measured: TA command word; 0 in captures
  [infer]. From `CR_TA_REG_02D0` (ours, resgx545).
- `CR_TA_REG_02D4` G0443 (0x02d4): inferred reading (unconfirmed): context store/resume state of an
  interrupted TA: a 26-bit size or offset. Measured: TA command word; 0 in captures [infer]. From
  `CR_TA_REG_02D4` (ours, resgx545).
- `CR_SETTLE_POLL0` G0437 (0x0308): first of two words the EDM reads twice and compares, looping
  until they agree, in the wait after CR_DMS_CTRL |= 0x7 that does the same with the PPP, TE and ISP
  signature registers; its function inside the core is not shown [infer]. From `CR_REG_0308` (ours,
  resgx545).
- `CR_SETTLE_POLL1` G0438 (0x030c): second of the two words of CR_SETTLE_POLL0's settle wait, read
  twice and compared in the same loop; its function inside the core is not shown [infer]. From
  `CR_REG_030C` (ours, resgx545).
- `CR_REG_0324` G0432 (0x0324): inferred reading (unconfirmed): context store/resume state of an
  interrupted TA: a state base (16-byte aligned, E182), unused while the TA runs to the end.
  Measured: TA command word; 0 in captures [infer]. From `CR_REG_0324` (ours, resgx545).
- `CR_REG_0364` G0433 (0x0364): inferred reading (unconfirmed): context store/resume state of an
  interrupted TA: a 32-bit resume task word, unused while the TA runs to the end. Measured: TA
  command word; 0 in captures [infer]. From `CR_REG_0364` (ours, resgx545).
- `CR_REG_0368` G0434 (0x0368): inferred reading (unconfirmed): context store/resume state of an
  interrupted TA: a 15-bit size or count of the stored state. Measured: TA command word; 0 in
  captures [infer]. From `CR_REG_0368` (ours, resgx545).
- `CR_REG_0370` G0435 (0x0370): inferred reading (unconfirmed): context store/resume state of an
  interrupted TA: a 32-bit resume task word. Measured: TA command word; 0 in captures [infer]. From
  `CR_REG_0370` (ours, resgx545).
- `CR_REG_0374` G0436 (0x0374): inferred reading (unconfirmed): context store/resume state of an
  interrupted TA: a 32-bit resume task word. Measured: TA command word; 0 in captures [infer]. From
  `CR_REG_0374` (ours, resgx545).
- `CR_REG_0400` G0152 (0x0400): inferred reading (unconfirmed): a pixel output conversion control:
  bit 25 inverts byte 3 of every pixel written (CR_REG_0400.INVERT_BYTE3), 0x80 the default of the
  other conversions. Measured: per-render word from the render details or transfer command; 0x80 in
  captures [infer]. From `CR_REG_0400` (ours, resgx545).
- `CR_ISP_REGION_HEADER_BASE` G0420 (0x0408): address of the region headers (or fast-2D stream) the
  ISP renders, relative to CR_BIF_3D_REQ_BASE [infer]. From `CR_ISP_REGION_HEADER_BASE` (ours,
  resgx545).
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
- `CR_ISP_START_RENDER` G0425 (0x0428): starts the 3D render. From `PSB_CR_ISP_START_RENDER` (1c,
  emgd-psb_regs).
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
- `CR_ISP_SIGNATURE0` G0421 (0x04d4): ISP output signature (first block, first word); the EDM waits
  for it to stop changing [infer]. From `CR_ISP_SIGNATURE0` (ours, resgx545).
- `CR_ISP_SIGNATURE1` G0422 (0x04d8): ISP output signature (first block, second word); the EDM waits
  for it to stop changing [infer]. From `CR_ISP_SIGNATURE1` (ours, resgx545).
- `CR_ISP_REG_04DC` G0130 (0x04dc): ISP word from the render details; bits 2:0 implemented; bit 1
  set hangs a render with punch-through objects, bits 0 and 2 change nothing seen; 0 from the closed
  driver's renders [infer]. From `CR_ISP_REG_04DC` (ours, resgx545).
- `CR_ISP_REG_04E8` G0131 (0x04e8): inferred reading (unconfirmed): Register 0x04e8: held 0x100
  outside a render, bits 0 and 8 take a write, and in every transfer, depth scene,
  overlapping-triangle scene and textured triangle tried no value of it changed an image; what it
  does is not shown. From `CR_ISP_REG_04E8` (ours, resgx545).
- `CR_ISP_PARTIAL_REGION_BASE` G0419 (0x050c): region-header address written per render; the partial
  render points it at the macrotile it renders [infer]. From `CR_ISP_PARTIAL_REGION_BASE` (ours,
  resgx545).
- `CR_ISP_SIGNATURE2` G0423 (0x0518): ISP output signature (second block, first word); the EDM waits
  for it to stop changing [infer]. From `CR_ISP_SIGNATURE2` (ours, resgx545).
- `CR_ISP_SIGNATURE3` G0424 (0x051c): ISP output signature (second block, second word); the EDM
  waits for it to stop changing [infer]. From `CR_ISP_SIGNATURE3` (ours, resgx545).
- `CR_ISP_SAMPLE_POS` G0132 (0x0520): four more sample positions, laid out as CR_ISP_MULTISAMPLECTL
  (a byte per sample: x in bits 3:0, y in bits 7:4, sixteenths of a pixel): with ISP0 bit 28 a
  single-sampled object also covers pixels where one of these samples is inside: the union of eight
  samples (these four and the four of CR_ISP_MULTISAMPLECTL) fits every count measured, and these
  four with the pixel centre fit the 55 images at the default CR_ISP_MULTISAMPLECTL too, which rule
  holds being open; under 4x three values give one image; 0 from the closed driver [infer]. From
  `CR_ISP_SAMPLE_POS` (ours, resgx545).
- `CR_DPM_3D_PAGE_TABLE_BASE` G0369 (0x0600): base of the DPM 3D page table. From
  `PSB_CR_DPM_3D_PAGE_TABLE_BASE` (1c, emgd-psb_regs).
- `CR_DPM_3D_FREE_LIST` G0367 (0x0604): DPM 3D free list: head and tail. From
  `PSB_CR_DPM_3D_FREE_LIST` (1c, emgd-psb_regs).
- `CR_DPM_TA_ALLOC_PAGE_TABLE_BASE` G0389 (0x0618): base of the DPM TA allocation page table. From
  `PSB_CR_DPM_TA_ALLOC_PAGE_TABLE_BASE` (1c, emgd-psb_regs).
- `CR_DPM_TA_ALLOC_FREE_LIST` G0388 (0x061c): DPM TA allocation free list: head and tail. From
  `PSB_CR_DPM_TA_ALLOC_FREE_LIST` (1c, emgd-psb_regs).
- `CR_DPM_TA_PAGE_THRESHOLD` G0392 (0x0620): TA page threshold of the DPM. From
  `PSB_CR_DPM_TA_PAGE_THRESHOLD` (1c, emgd-psb_regs).
- `CR_DPM_ZLS_PAGE_THRESHOLD` G0393 (0x0624): ZLS page threshold of the DPM. From
  `EUR_CR_DPM_ZLS_PAGE_THRESHOLD` (1, intel-ctp-santos10); `PSB_CR_DPM_ZLS_PAGE_THRESHOLD` (1c,
  emgd-psb_regs).
- `CR_DPM_TA_GLOBAL_LIST` G0390 (0x0628): DPM global page list: size and policy. From
  `EUR_CR_DPM_TA_GLOBAL_LIST` (1, intel-ctp-santos10); `PSB_CR_DPM_TA_GLOBAL_LIST` (1c,
  emgd-psb_regs).
- `CR_DPM_STATE_BASE0` G0380 (0x062c): DPM context state table address (first register of two); the
  EDM loads it from the RT data on a first kick and on context store/load [infer]. From
  `CR_DPM_STATE_BASE0` (ours, resgx545).
- `CR_DPM_STATE_CONTEXT_ID` G0382 (0x0630): selects DPM context for load/store/alloc. From
  `EUR_CR_DPM_STATE_CONTEXT_ID` (1, intel-ctp-santos10); `PSB_CR_DPM_STATE_CONTEXT_ID` (1c,
  emgd-psb_regs).
- `CR_DPM_CONTROL_BASE` G0372 (0x0634): DPM context control table address, from the RT data [infer].
  From `CR_DPM_CONTROL_BASE` (ours, resgx545).
- `CR_DPM_TA_PAGE_COUNTS` G0391 (0x0638): pages the TA's PB already holds when it is loaded: local
  count in bits 15:0, global in 31:16 [infer]. From `CR_DPM_TA_PAGE_COUNTS` (ours, resgx545).
- `CR_DPM_3D_DEALLOCATE` G0366 (0x063c): start DPM 3D page deallocation. From
  `PSB_CR_DPM_3D_DEALLOCATE` (1c, emgd-psb_regs).
- `CR_DPM_TA_ALLOC` G0387 (0x0648): DPM TA allocation state (previous free-list entry). From
  `PSB_CR_DPM_TA_ALLOC` (1c, emgd-psb_regs).
- `CR_DPM_3D` G0365 (0x064c): DPM 3D state (previous free-list entry). From `PSB_CR_DPM_3D` (1c,
  emgd-psb_regs).
- `CR_DPM_PARTIAL_RENDER` G0376 (0x0658): 1 while a partial render runs: the EDM sets it in the
  partial-render routine and clears it at the resume and at every 3D kick; its effect inside the DPM
  is not shown [infer]. From `CR_DPM_PARTIAL_RENDER` (ours, resgx545).
- `CR_DPM_SPM_SWITCH` G0379 (0x065c): DPM word the EDM writes only in the partial-render routine and
  its resume: 1 just before it switches CR_DPM_STATE_BASE0/1 and flips CR_DPM_STATE_CONTEXT_ID, 0
  just after; 1 around CR_DPM_TASK_CONTROL = 2 on the resume; its function inside the DPM is not
  shown [infer]. From `CR_DPM_REG_065C` (ours, resgx545).
- `CR_DPM_3D_PAGE_COUNTS` G0368 (0x0660): pages the 3D's PB already holds when it is loaded: local
  count in bits 15:0, global in 31:16 [infer]. From `CR_DPM_3D_PAGE_COUNTS` (ours, resgx545).
- `CR_DPM_PDS_THRESHOLD` G0377 (0x0668): PDS page threshold of the parameter buffer, from the PB
  descriptor [infer]. From `CR_DPM_PDS_THRESHOLD` (ours, resgx545).
- `CR_DPM_STATE_BASE1` G0381 (0x0674): DPM context state table address (second register of two),
  written with CR_DPM_STATE_BASE0 [infer]. From `CR_DPM_STATE_BASE1` (ours, resgx545).
- `CR_DPM_TASK_3D_FREE` G0383 (0x0680): DPM task: load the 3D free list. From
  `PSB_CR_DPM_TASK_3D_FREE` (1c, emgd-psb_regs).
- `CR_DPM_TASK_TA_FREE` G0386 (0x0684): DPM task: load the TA free list. From
  `PSB_CR_DPM_TASK_TA_FREE` (1c, emgd-psb_regs).
- `CR_DPM_TASK_STATE` G0385 (0x0694): DPM task: store, clear or load the state. From
  `PSB_CR_DPM_TASK_STATE` (1c, emgd-psb_regs).
- `CR_DPM_TASK_CONTROL` G0384 (0x0698): DPM task: store, clear or load the control table. From
  `PSB_CR_DPM_TASK_CONTROL` (1c, emgd-psb_regs).
- `CR_DPM_OUTOFMEM` G0374 (0x069c): DPM out-of-memory response: restart, abort, abort all. From
  `PSB_CR_DPM_OUTOFMEM` (1c, emgd-psb_regs).
- `CR_DPM_FREE_CONTEXT` G0373 (0x06a0): free the DPM context now. From `PSB_CR_DPM_FREE_CONTEXT`
  (1c, emgd-psb_regs).
- `CR_DPM_ABORT_STATUS_MTILE` G0371 (0x0720): DPM macrotile abort status. From
  `EUR_CR_DPM_ABORT_STATUS_MTILE` (1, intel-ctp-santos10).
- `CR_DPM_PAGE_STATUS` G0375 (0x0724): DPM pages in use: total and TA. From `EUR_CR_DPM_PAGE_STATUS`
  (1, intel-ctp-santos10); `PSB_CR_DPM_PAGE_STATUS` (1c, emgd-psb_regs).
- `CR_DPM_3D_RT_INDEX` G0370 (0x073c): render target index of the render, for render-target arrays
  [infer]. From `CR_DPM_3D_RT_INDEX` (ours, resgx545).
- `CR_DPM_REG_074C` G0378 (0x074c): inferred reading (unconfirmed): the enable (bit 8) and setup of
  a DPM structure that follows the TA data (a second list, as a partial-render or context-switch
  arrangement would need), off in every client. Measured: TA command word; 0 in captures [infer].
  From `CR_DPM_REG_074C` (ours, resgx545).
- `CR_REG_0800` G0154 (0x0800): inferred reading (unconfirmed): an on-chip resource limit (bits 5:0
  = 48, bits 23:8) for work other than pixel tasks (vertex or state tasks, context switches);
  pixel-bound renders ignore it (E136). Measured: set by the init script and per render; 0x30
  everywhere [infer]. From `CR_REG_0800` (ours, resgx545).
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
- `CR_USE_REG_0A04` G0456 (0x0a04): inferred reading (unconfirmed): the USSE's context store/resume
  state base (a 16-byte address) for an interrupted TA's vertex tasks. Measured: USSE word from the
  TA command; 0 in captures [infer]. From `CR_USE_REG_0A04` (ours, resgx545).
- `CR_USE_CACHE` G0455 (0x0a08): USSE instruction cache invalidate. From `PSB_CR_USE_CACHE` (1c,
  emgd-psb_regs).
- `CR_USE_CODE_BASE_0` G0005 (0x0a0c): USSE code base 0: address and data master. From
  `EUR_CR_USE_CODE_BASE(X)` (1, sgx545-ce); `EUR_CR_USE_CODE_BASE_0` (1, sgx545-ce);
  `PSB_CR_USE_CODE_BASE(i)` (1c, emgd-psb_regs); `PSB_CR_USE_CODE_BASE0` (1c, emgd-psb_regs).
- `CR_USE_CODE_BASE_10` G0056 (0x0a34): USSE code base 10: address and data master. From
  `EUR_CR_USE_CODE_BASE_10` (1, sgx545-ce); `PSB_CR_USE_CODE_BASE10` (1c, emgd-psb_regs).
- `CR_USE_CODE_BASE_15` G0057 (0x0a48): USSE code base 15: address and data master. From
  `EUR_CR_USE_CODE_BASE_15` (1, sgx545-ce); `PSB_CR_USE_CODE_BASE15` (1c, emgd-psb_regs).
- `CR_EVENT_PDS_ENABLE` G0048 (0x0a58): events that start a PDS event task. From
  `PSB_CR_EVENT_PDS_ENABLE` (1c, emgd-psb_regs).
- `CR_EVENT_PIXEL_PDS_CODE` G0394 (0x0a5c): PDS code address of the pixel event task (Rogue
  analogue). From `ROGUE_CR_EVENT_PIXEL_PDS_CODE` (3, mesa-csbgen).
- `CR_EVENT_PIXEL_PDS_DATA` G0395 (0x0a60): data size of the pixel-event PDS program in 16-byte rows
  (Rogue: its data address). From `ROGUE_CR_EVENT_PIXEL_PDS_DATA` (3, mesa-csbgen).
- `CR_EVENT_PIXEL_PDS_INFO` G0396 (0x0a64): size word of the pixel-event task, (attributes x 4 + 15)
  >> 4 in the closed library (Rogue: shared-register and temp sizes). From
  `ROGUE_CR_EVENT_PIXEL_PDS_INFO` (3, mesa-csbgen).
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
- `CR_USE_REG_0AA0` G0457 (0x0aa0): inferred reading (unconfirmed): a USSE resume task word for an
  interrupted TA's vertex tasks. Measured: USSE word from the TA command; 0 in captures [infer].
  From `CR_USE_REG_0AA0` (ours, resgx545).
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
- `CR_BIF_TA_REQ_BASE` G0362 (0x0c90): TA requestor base address (heap window). From
  `EUR_CR_BIF_TA_REQ_BASE` (1, sgx545-ce); `PSB_CR_BIF_TA_REQ_BASE` (1c, emgd-psb_regs).
- `CR_BIF_3D_REQ_BASE` G0001 (0x0cac): 3D requestor base address. From `EUR_CR_BIF_3D_REQ_BASE` (1,
  sgx545-ce); `PSB_CR_BIF_3D_REQ_BASE` (1c, emgd-psb_regs).
- `CR_HWPERF_PULSE` G0417 (0x0e80): HWPerf word the EDM pulses: 1 then 0 on consecutive instructions
  right after it writes CR_HWPERF_CTRL = 0x1ff, in the general event path; no other access; the
  SETHWPERFSTATUS handler reaches it through the same routine (E150); what it does is not measured
  [infer]. From `CR_HWPERF_REG_0E80` (ours, resgx545).

## 3. Firmware-interface structures, flags and functions

### enum

- `CLEANUP.RENDER_CONTEXT` G0355 (COMMAND+0x08 ui32Data[0] = 2): clean up a HW render context. From
  `PVRSRV_CLEANUPCMD_RC` (1, sgx545-ce).
- `CLEANUP.PB` G0354 (COMMAND+0x08 ui32Data[0] = 5, ~ COMMAND ui32Data[0]): clean up a PB
  descriptor. From `PVRSRV_CLEANUPCMD_PB` (1, sgx545-ce); `ROGUE_FWIF_CLEANUP_FREELIST` (3,
  linux-imagination).
- `CMD.SET_HWPERF_STATUS` G0356 (aui32HostKickAddr[9]): kernel CCB command 9: set the HWPerf status.
  From `SGXMKIF_CMD_SETHWPERFSTATUS` (1, sgx545-ce).

### field

- `pb_block.next_block_dev_vaddr` G0560: next block of the descriptor's block list (0 = last)
  [infer]. From `pb_block.next_block_dev_vaddr` (ours, resgx545).
- `pb_block.page_count` G0561: pages in this PB block [infer]. From `pb_block.page_count` (ours,
  resgx545).
- `ta3d_ctl.hw_pb_desc_3d` G0563: PB descriptor loaded in the 3D. From `s3DHWPBDesc` (1c,
  emgd-linux).
- `ta3d_ctl.hw_pb_desc_ta` G0564: PB descriptor loaded in the TA. From `sTAHWPBDesc` (1c,
  emgd-linux).
- `ccb_ctl.write_offset` G0097 (CCB_CTL+0x0): write offset (host advances). From `ui32WriteOffset`
  (1, sgx545-ce).
- `ccb_ctl.read_offset` G0096 (CCB_CTL+0x4): read offset (EDM advances). From `ui32ReadOffset` (1,
  sgx545-ce).
- `cmd_ta.pds_bgnd` G0512 (CMDTA+0x008): background object words [3]: dwords 0-2 of the background
  object, the first a pixel PDS reference; copied to the render details' pds_bgnd at the TA kick.
  From `pds_bgnd` (3, linux-imagination).
- `cmd_ta.num_vertex_partitions` G0510 (CMDTA+0x014): DMS_CTRL vertex partitions, pre-shifted. From
  `NumVertexPartitions` (2, cdv-libsrv_um).
- `cmd_ta.frag_flags` G0303 (CMDTA+0x01c): fragment (3D) flags: depth/stencil buffer present,
  visibility results (FRAG_FLAGS.*). From `flags` (3, linux-imagination).
- `cmd_ta.ta_threshold` G0514 (CMDTA+0x028): new TA threshold. From `TAThreshold` (2,
  cdv-libsrv_um); `cmd_ta.ta_threshold` (ours, resgx545).
- `cmd_ta.global_threshold` G0506 (CMDTA+0x030): new global threshold. From `GlobalThreshold` (2,
  cdv-libsrv_um); `cmd_ta.global_threshold` (ours, resgx545).
- `cmd_ta.hw_render_details_dev_vaddr` G0507 (CMDTA+0x038): render details of the kick; the EDM
  records it and writes it into the RT data's hw_render_details_dev_vaddr [infer]. From
  `cmd_ta.hw_render_details_dev_vaddr` (ours, resgx545).
- `cmd_ta.hw_rt_data_dev_vaddr` G0508 (CMDTA+0x044): RT data used by this kick. From
  `sHWRTDataDevAddr` (1, intel-ctp-k900).
- `cmd_ta.num_patches_3d` G0509 (CMDTA+0x054): count of {address, value} pairs in the TA command's
  patches_3d [infer]. From `cmd_ta.num_patches_3d` (ours, resgx545).
- `cmd_ta.shared` G0513 (CMDTA+0x058): embedded cmd_ta_shared block; the kick passes its client-CCB
  offset in ccb_kick.ccb_offset. From `ui32CCBOffset` (1, sgx545-ce).
- `cmd_ta.te_aa` G0515 (CMDTA+0x238): value the EDM loads into CR_TE_AA (0x0204): 0x20000000, bits
  31 and 30 more with 4x multisampling [infer]. From `cmd_ta.te_aa` (ours, resgx545).
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
- `cmd_ta.reg_0324` G0306 (CMDTA+0x288): inferred reading (unconfirmed): as CR_REG_0324's: context
  store/resume state of an interrupted TA: a state base (16-byte aligned, E182), unused while the TA
  runs to the end. Measured: value the EDM copies verbatim into CR_REG_0324 (0x0324); 0 in every
  capture [infer]. From `cmd_ta.reg_0324` (ours, resgx545).
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
- `cmd_ta.patches_3d` G0511 (CMDTA+0x2a8): {address, value} memory writes the EDM applies at the TA
  kick, *address = value: patches to the render details (depth/stencil bases, ZLS control) [infer].
  From `cmd_ta.patches_3d` (ours, resgx545).
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
- `hw_pb_desc.initial_stack_top` G0523 (HWPBDESC+0x008): initial free-list head/tail (tail << 16 |
  head); PB_FLAGS.INIT_PAGE_TABLE resets the PB descriptor's current_stack_top from it [infer]. From
  `hw_pb_desc.initial_stack_top` (ours, resgx545).
- `hw_pb_desc.initial_dpm_ta_alloc` G0522 (HWPBDESC+0x00c): initial value of the PB descriptor's
  dpm_ta_alloc (the page before the tail << 16) [infer]. From `hw_pb_desc.initial_dpm_ta_alloc`
  (ours, resgx545).
- `hw_pb_desc.allocated_page_count` G0518 (HWPBDESC+0x014): pages allocated. From
  `allocated_page_count` (3, linux-imagination).
- `hw_pb_desc.current_stack_top` G0519 (HWPBDESC+0x018): current free list head/tail. From
  `current_stack_top` (3, linux-imagination).
- `hw_pb_desc.dpm_ta_alloc` G0520 (HWPBDESC+0x01c): current allocation word: the EDM loads it into
  CR_DPM_TA_ALLOC (the 3D's matching register for the 3D) and stores the status back [infer]. From
  `hw_pb_desc.dpm_ta_alloc` (ours, resgx545).
- `hw_pb_desc.ta_threshold` G0525 (HWPBDESC+0x028): TA page threshold. From `TAThreshold` (2,
  cdv-libsrv_um); `hw_pb_desc.ta_threshold` (ours, resgx545).
- `hw_pb_desc.zls_threshold` G0526 (HWPBDESC+0x02c): ZLS page threshold. From `ZLSThreshold` (2,
  cdv-libsrv_um).
- `hw_pb_desc.global_threshold` G0521 (HWPBDESC+0x030): global page threshold. From
  `GlobalThreshold` (2, cdv-libsrv_um); `hw_pb_desc.global_threshold` (ours, resgx545).
- `hw_pb_desc.pds_threshold` G0524 (HWPBDESC+0x034): PDS page threshold. From `PDSThreshold` (2,
  cdv-libsrv_um).
- `hw_render_context.priority` G0530 (HWRENDERCONTEXT+0x004): scheduling priority. From
  `ui32OffsetOfPriorityField` (1, sgx545-ce); `priority` (3, linux-imagination).
- `hw_render_context.submitted_commands` G0537 (HWRENDERCONTEXT+0x014): TA commands queued in the
  context's CCB: the CCB handler increments it, the TA end decrements it. From `submitted_commands`
  (3, linux-imagination).
- `hw_render_context.hw_pb_desc_dev_vaddr` G0527 (HWRENDERCONTEXT+0x018): PB descriptor of the
  context. From `sHWPBDescDevVAddr` (1, sgx545-ce).
- `hw_render_context.pending_renders_head` G0528 (HWRENDERCONTEXT+0x020): first render details
  waiting for their scene's TA to finish (pending list) [infer]. From
  `hw_render_context.pending_renders_head` (ours, resgx545).
- `hw_render_context.pending_renders_tail` G0529 (HWRENDERCONTEXT+0x024): last render details of the
  pending list [infer]. From `hw_render_context.pending_renders_tail` (ours, resgx545).
- `hw_render_context.ready_renders_head` G0531 (HWRENDERCONTEXT+0x028): first render details ready
  for the 3D (ready list) [infer]. From `hw_render_context.ready_renders_head` (ours, resgx545).
- `hw_render_context.ready_renders_tail` G0532 (HWRENDERCONTEXT+0x02c): last render details of the
  ready list [infer]. From `hw_render_context.ready_renders_tail` (ours, resgx545).
- `hw_render_context.run_node_prev_ta` G0536 (HWRENDERCONTEXT+0x030): previous context in the EDM's
  TA queue [infer]. From `hw_render_context.run_node_prev_ta` (ours, resgx545).
- `hw_render_context.run_node_next_ta` G0534 (HWRENDERCONTEXT+0x034): next context in the EDM's TA
  queue [infer]. From `hw_render_context.run_node_next_ta` (ours, resgx545).
- `hw_render_context.run_node_prev_3d` G0535 (HWRENDERCONTEXT+0x038): previous context in the EDM's
  3D queue [infer]. From `hw_render_context.run_node_prev_3d` (ours, resgx545).
- `hw_render_context.run_node_next_3d` G0533 (HWRENDERCONTEXT+0x03c): next context in the EDM's 3D
  queue [infer]. From `hw_render_context.run_node_next_3d` (ours, resgx545).
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
- `hw_render_details.isp_partial_region_base` G0539 (HWRENDERDETAILS+0x028): value the EDM copies
  verbatim into CR_ISP_PARTIAL_REGION_BASE (0x050c); a partial render points that register at the
  macrotile it renders [infer]. From `hw_render_details.isp_partial_region_base` (ours, resgx545).
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
  value the EDM copies verbatim into CR_ISP_SAMPLE_POS (0x0520): the four sample positions (0 in the
  capture) [infer]. From `hw_render_details.isp_sample_pos` (ours, resgx545).
- `hw_render_details.isp_multisamplectl` G0321 (HWRENDERDETAILS+0x050): Render-details word 20: the
  value loaded into register 0x04c8, the same register the render command's word 16 loads (identical
  images bit for bit), holding the sample positions; 22 of its 32 bits moved the samples of a 4x
  triangle by a few samples and the rest changed nothing. From
  `hw_render_details.isp_multisamplectl` (ours, resgx545).
- `hw_render_details.access_dev_vaddr` G0538 (HWRENDERDETAILS+0x0d0): access/lock word (SYNCINFO).
  From `sAccessDevAddr` (1, sgx545-ce).
- `hw_render_details.rt_patch_dev_vaddr` G0544 (HWRENDERDETAILS+0x10c): address the 3D kick writes
  the current render target's two-dword entry of rt_patch_list_dev_vaddr to, through the 3D's
  address space; 0 = no write [infer]. From `hw_render_details.rt_patch_dev_vaddr` (ours, resgx545).
- `hw_render_details.rt_patch_list_dev_vaddr` G0545 (HWRENDERDETAILS+0x110): per-RT list of
  two-dword values for rt_patch_dev_vaddr, 8 bytes per render-target index [infer]. From
  `hw_render_details.rt_patch_list_dev_vaddr` (ours, resgx545).
- `hw_render_details.pds_bgnd_list_dev_vaddr` G0541 (HWRENDERDETAILS+0x114): per-RT list of
  background object word 2 (4 bytes per render-target index); the 3D kick writes the entry for the
  current index after pds_bgnd[0..1] [infer]. From `hw_render_details.pds_bgnd_list_dev_vaddr`
  (ours, resgx545).
- `hw_render_details.te_context_state` G0546 (HWRENDERDETAILS+0x124): tiling-engine state: loaded
  into CR_TE_CONTEXT_STATE (0x0274) at each TA kick, stored back at a TA end that is not the last of
  the scene, so the next kick resumes tiling [infer]. From `hw_render_details.te_context_state`
  (ours, resgx545).
- `hw_render_details.render_list_prev_dev_vaddr` G0543 (HWRENDERDETAILS+0x128): previous render
  details in the context's pending or ready render list [infer]. From
  `hw_render_details.render_list_prev_dev_vaddr` (ours, resgx545).
- `hw_render_details.render_list_next_dev_vaddr` G0542 (HWRENDERDETAILS+0x12c): next render details
  in the context's pending or ready render list [infer]. From
  `hw_render_details.render_list_next_dev_vaddr` (ours, resgx545).
- `hw_render_details.pds_bgnd` G0540 (HWRENDERDETAILS+0x130): background object words [3], copied
  from the TA command's pds_bgnd at the TA kick; the 3D kick writes words 0 and 1 into the
  background object. From `pds_bgnd` (3, linux-imagination).
- `hw_render_details.num_pixel_partitions` G0324 (HWRENDERDETAILS+0x13c): DMS_CTRL pixel partitions
  (31 << 22). From `NumPixelPartitions` (2, cdv-libsrv_um).
- `hw_rt_data.hw_render_details_dev_vaddr` G0550 (HWRTDATA+0x004): render details of the scene in
  flight on this RT data; written by the EDM at the TA kick, cleared when the scene is done (the
  client leaves it 0) [infer]. From `hw_rt_data.hw_render_details_dev_vaddr` (ours, resgx545).
- `hw_rt_data.bgobj_dev_vaddr` G0547 (HWRTDATA+0x010): background object of the RT data; the 3D kick
  writes its dwords 0-2 through the 3D's address space [infer]. From `hw_rt_data.bgobj_dev_vaddr`
  (ours, resgx545).
- `hw_rt_data.dpm_state_dev_vaddr` G0549 (HWRTDATA+0x014): DPM context state of this RT data; the
  EDM loads it into CR_DPM_STATE_BASE0/1 and clears it on a first kick [infer]. From
  `hw_rt_data.dpm_state_dev_vaddr` (ours, resgx545).
- `hw_rt_data.dpm_control_dev_vaddr` G0548 (HWRTDATA+0x018): DPM context control table; the EDM
  loads it into CR_DPM_CONTROL_BASE and clears it on a first kick [infer]. From
  `hw_rt_data.dpm_control_dev_vaddr` (ours, resgx545).
- `hw_rt_data.otpm_dev_vaddr` G0551 (HWRTDATA+0x01c): OTPM context memory; the EDM loads it into
  CR_MTE_OTPM_BASE and clears it with CR_MTE_OTPM_OP = 9 on a first kick [infer]. From
  `hw_rt_data.otpm_dev_vaddr` (ours, resgx545).
- `hw_rt_data.rt_status_dev_vaddr` G0552 (HWRTDATA+0x030): one status word per render target: zeroed
  on a first kick, bit 1 set by the partial-render resume, bit 0 set when the RT is rendered; the 3D
  kick adjusts depth/stencil load and store from bit 1 [infer]. From
  `hw_rt_data.rt_status_dev_vaddr` (ours, resgx545).
- `hw_rt_data.state` G0553 (HWRTDATA+0x034): RT data state (0x10 = no render outstanding). From
  `state` (3, linux-imagination).
- `hw_rt_data_set.executed_count` G0554 (HWRTDATASET+0x004): count the EDM increments at each TA end
  that is not the scene's last and at each scene render with FRAG_FLAGS.RENDER_SCENE [infer]. From
  `hw_rt_data_set.executed_count` (ours, resgx545).
- `hw_rt_data_set.num_out_of_mem_signals` G0555 (HWRTDATASET+0x00c): TA out-of-memory count. From
  `ui32NumOutOfMemSignals` (1, sgx545-ce).
- `hw_rt_data_set.num_spm_renders` G0556 (HWRTDATASET+0x010): partial renders run. From
  `ui32NumSPMRenders` (1, sgx545-ce).
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
- `transfer_cmd.patches` G0565 (TRANSFERCMD+0x1a0): {address, value} memory writes the EDM applies
  through the context's address space before the render, to the end of the command [infer]. From
  `transfer_cmd.patches` (ours, resgx545).

### flag

- `GEOM_FLAGS.FIRST_KICK` G0241 (CMDTA+0x004 bit0 (0x1)): first kick of a scene. From
  `ROGUE_GEOM_FLAGS_FIRSTKICK` (3, linux-imagination).
- `GEOM_FLAGS.LAST_KICK` G0242 (CMDTA+0x004 bit1 (0x2)): last kick of a scene. From
  `ROGUE_GEOM_FLAGS_LASTKICK` (3, linux-imagination).
- `GEOM_FLAGS.TA3D_DEPENDENCY` G0469 (CMDTA+0x004 bit10 (0x400)): wait for the TA->3D dependency
  sync (the shared block's ta3d_dependency) before the kick [infer]. From
  `GEOM_FLAGS.TA3D_DEPENDENCY` (ours, resgx545).
- `GEOM_FLAGS.PB_THRESHOLD_UPDATE` G0468 (CMDTA+0x004 bit13 (0x2000)): copy the command's four
  thresholds into the PB descriptor and set PB_FLAGS.THRESHOLD_UPDATE [infer]. From
  `GEOM_FLAGS.PB_THRESHOLD_UPDATE` (ours, resgx545).
- `GEOM_FLAGS.NO_DPM_CONTEXT_LOAD` G0243 (CMDTA+0x004 bit3 (0x8)): tested together with
  GEOM_FLAGS.FIRST_KICK (mask 0x9): when either is set the TA kick skips the calls that invalidate
  the caches, set the BIF bank and reload the RT data's stored DPM context (CR_DPM_STATE_BASE0/1,
  CR_DPM_CONTROL_BASE, CR_MTE_OTPM_BASE from hw_rt_data, DPM state task) [infer]. From
  `GEOM_FLAGS.BIT3` (ours, resgx545).
- `GEOM_FLAGS.INVALIDATE_USE_CACHE` G0467 (CMDTA+0x004 bit4 (0x10)): invalidate the USE cache before
  the TA [infer]. From `GEOM_FLAGS.INVALIDATE_USE_CACHE` (ours, resgx545).
- `GEOM_FLAGS.INVALIDATE_PDS_CACHE` G0466 (CMDTA+0x004 bit5 (0x20)): invalidate the PDS caches
  before the TA [infer]. From `GEOM_FLAGS.INVALIDATE_PDS_CACHE` (ours, resgx545).
- `GEOM_FLAGS.INVALIDATE_DATA_CACHE` G0465 (CMDTA+0x004 bit6 (0x40)): invalidate the data cache
  before the TA (CR_CACHE_CTRL bit 28) [infer]. From `GEOM_FLAGS.INVALIDATE_DATA_CACHE` (ours,
  resgx545).
- `PB_FLAGS.INIT_PAGE_TABLE` G0481 (HWPBDESC+0x000 bit0 (0x1)): rebuild the DPM page table and free
  list from the initial values and the block list [infer]. From `PB_FLAGS.INIT_PAGE_TABLE` (ours,
  resgx545).
- `PB_FLAGS.THRESHOLD_UPDATE` G0482 (HWPBDESC+0x000 bit1 (0x2)): reload the thresholds; the EDM
  clears bits 0-1 [infer]. From `PB_FLAGS.THRESHOLD_UPDATE` (ours, resgx545).
- `CONTEXT_FLAGS.NEW` G0357 (HWRENDERCONTEXT/HWTRANSFERCONTEXT+0x000 bit0 (0x1)): new context: at
  its first mapping the EDM clears the bit and invalidates the caches [infer]. From
  `CONTEXT_FLAGS.NEW` (ours, resgx545).
- `CONTEXT_FLAGS.SUSPEND` G0359 (HWRENDERCONTEXT/HWTRANSFERCONTEXT+0x000 bit4 (0x10)): suspended:
  the EDM's picks skip the context [infer]. From `CONTEXT_FLAGS.SUSPEND` (ours, resgx545).
- `CONTEXT_FLAGS.OWN_PB` G0358 (HWRENDERCONTEXT/HWTRANSFERCONTEXT+0x000 bit5 (0x20)): set: the
  render-context cleanup unloads the context's own PB from the TA and 3D loaded-PB slots (a context
  that owns its PB); clear: the slots stay until the PB cleanup [infer]. From `CONTEXT_FLAGS.OWN_PB`
  (ours, resgx545).
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
- `pb_block` G0559 (pb_block (0x10)): GPL name of the HW PB block allocation. From
  `psHWBlockKernelMemInfo` (1, sgx545-ce).
- `hw_pb_desc` G0517 (~ HWPBDESC): Rogue FW free list = parameter-buffer pages. From
  `rogue_fwif_freelist` (3, linux-imagination).

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
- `VDM_STATE1.BIT12` G0500 (VDM_STATE1 bit 12): set: the TA writes no object for the state's
  primitives and leaves the regions empty, as with bits 11:9 at 0 [infer]. From `VDM_STATE1.BIT12`
  (ours, resgx545).
- `VDM_STATE1.BIT18` G0501 (VDM_STATE1 bit 18): set: the job hangs; what it does is not established
  [infer]. From `VDM_STATE1.BIT18` (ours, resgx545).
- `VDM_STATE1.BIT25` G0502 (VDM_STATE1 bit 25): clearing it changes neither the TA's output nor the
  image of one triangle; what it does is not established [infer]. From `VDM_STATE1.BIT25` (ours,
  resgx545).
- `OUTSEL.PLANES` G0252 (outsel [7:0]): inferred reading (unconfirmed): user clip-plane enables, bit
  N plane N: each enabled plane reads a clip distance from the vertex outputs after the position
  (plane 0 the first; planes 0 and 1 together the first two), and a triangle with a negative
  distance at any vertex is removed whole [infer]. From `OUTSEL.PLANES` (ours, resgx545).

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
- `ISP1.LINE_WIDTH` G0472 (ISP1 [15:8]): inferred reading (unconfirmed): A line width: the TA copies
  ISP word 1's bits 15:8 into both bytes of the object's line-width dword; the unit is not shown by
  the object [infer]. From `ISP1.LINE_WIDTH` (ours, resgx545).
- `ISP1.VISREG` G0248 (ISP1 [2:0]): index of the visibility counter the object counts into (with
  ISP1.VISTEST). From `visreg` (3, mesa-csbgen).
- `ISP1.VALID_ID` G0473 (ISP1 [31:26]): the object's validation ID: an opaque or translucent object
  is drawn only when it is at least CR_ISP_CTL.VALID_ID. From `ISP1.VALID_ID` (ours, resgx545).
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
  sampler data show nothing about this field beyond its name. From `T3.DATA_SIZE` (ours, resgx545).
- `PB_OBJ.RHW` G0487 (TA object TSP data, first dword of each vertex, TA object vertex data):
  inferred reading (unconfirmed): 1/w of the vertex, before its outputs, which are stored undivided
  [infer]. From `PB_OBJ.RHW` (ours, resgx545).
- `PB_OBJ.PDS_WORDS` G0485 (TA object dwords 0-2): the state block's pixel-program words as given:
  secondary pointer, size word, primary pointer [infer]. From `PB_OBJ.PDS_WORDS` (ours, resgx545).
- `PB_OBJ.PRIM_LIST` G0486 (TA object, after ISP word 1: 16 bits per primitive, two to a dword): the
  object's primitives: per primitive three 5-bit vertex numbers (bits 4:0, 9:5, 14:10), the object's
  vertices numbered from 16; the last entry repeated to fill an odd count [infer]. From
  `PB_OBJ.PRIM_LIST` (ours, resgx545).
- `PB_OBJ.LINE_WIDTHS` G0484 (TA object, the dword after the primitive list): ISP1.LINE_WIDTH in
  both bytes (bits 15:8 and 7:0) [infer]. From `PB_OBJ.LINE_WIDTHS` (ours, resgx545).
- `PB_OBJ.SET_MASKS` G0488 (TA object, the four dwords after the format word): bit i for coordinate
  set i (from 1): sets stored at half precision, sets of one component, sets with z, sets with w
  [infer]. From `PB_OBJ.SET_MASKS` (ours, resgx545).
- `PB_OBJ.ISP_WORDS` G0483 (TA object, the two dwords after the TSP data): ISP words 0 and 1 as the
  state block gives them [infer]. From `PB_OBJ.ISP_WORDS` (ours, resgx545).
- `VDM_STATE1.BITS11_9` G0292 (VDM_STATE1 [11:9]): inferred reading (unconfirmed): Bits 11:9 of the
  state task's second word: 0 removes the 64x64 triangle (4096 background pixels), 1, 3, 4, 5 and 6
  give the baseline image, and 7 hangs the job in the sweep but renders in a probe job, so that
  value is unsettled; the job writes 2. From `VDM_STATE1.BITS11_9` (ours, resgx545).
- `VDM_STATE1.BITS15_13` G0293 (VDM_STATE1 [15:13]): inferred reading (unconfirmed): Bits 15:13 of
  the state task's second word: 0, 5 and 6 hang the job, 2, 3, 4 and 7 give the baseline image; the
  job writes 1. From `VDM_STATE1.BITS15_13` (ours, resgx545).
- `FEEDBACK_CTL.DEPTH_ALWAYS` G0228 (atst8/depthf src1 [3:2]): inferred reading (unconfirmed):
  either bit set makes the kept pixel's depth win unconditionally (its depth test as always)
  [infer]. From `FEEDBACK_CTL.DEPTH_ALWAYS` (ours, resgx545).
- `BG.TSP_DWORDS` G0352 (bg object word after the TSP coordinates (dword 4 with no layer) [15:8]):
  the dwords of TSP data each vertex has as iterated (f16 pairs counted unpacked); equal to
  BG.TSP_STORED_DWORDS without half-precision sets [infer]. From `BG.TSP_DWORDS` (ours, resgx545).
- `BG.TSP_STORED_DWORDS` G0353 (bg object word after the TSP coordinates (dword 4 with no layer)
  [7:0]): the dwords of TSP data each vertex takes in the object as stored (2 per (u, v) layer in
  the background object; in the TA's own objects 1/w and the outputs, f16 pairs packed) [infer].
  From `BG.TSP_STORED_DWORDS` (ours, resgx545).
- `CSTREAM.OBJ_PRIMS` G0461 (control-stream object word [31:26]): twice the object's primitives less
  one [infer]. From `CSTREAM.OBJ_PRIMS` (ours, resgx545).
- `CSTREAM.OBJ_ISP_ADDR` G0460 (control-stream object word, low bits (below 26)): the slot address
  of the object's ISP words, in dwords; the region's stream holds one primitive word and object word
  per object [infer]. From `CSTREAM.OBJ_ISP_ADDR` (ours, resgx545).
- `CSTREAM.PRIM_TILES` G0463 (control-stream primitive word [23:16]): which of the region's two 16 x
  16 tiles the object meets, and the masks' layout: 0x90 both (no masks, bits 15:0 0xffff); one tile
  with masks in bits 15:0, 0x80 the left, 0x98 the right; with masks too wide for the word (the
  primitive mask in a further dword), 0x8a the left, 0x8c the right; bit 23 is set in every word
  seen [infer]. From `CSTREAM.PRIM_TILES` (ours, resgx545).
- `CSTREAM.PRIM_VERTICES` G0464 (control-stream primitive word [28:25]): the object's vertices less
  one [infer]. From `CSTREAM.PRIM_VERTICES` (ours, resgx545).
- `COORDFMT.SET_F16` G0360 (coordfmt word, bit i for coordinate set i): carry coordinate set i at
  half precision: its values reach the iterator cut to 10 mantissa bits, towards zero [infer]. From
  `COORDFMT.SET_F16` (ours, resgx545).
- `COORDSIZE.SET_LAYOUT` G0361 (coordsize word, 3 bits per coordinate set from bit 0): the
  components of each coordinate set after the position (the vertex colour first with
  OUTSEL.COLOUR_PRES): 1 x, 2 xy, 3 xyz, 4 xyw, 5 xyzw, 0, 6 and 7 as 2; components a set lacks
  iterate as (0, 0, 0, 1.0); the vertex size, not the fields, decides how many sets there are
  [infer]. From `COORDSIZE.SET_LAYOUT` (ours, resgx545).
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
- `VDM_INDEX2.WORD` G0498 (index list, the first trailing word): inferred reading (unconfirmed): the
  index list's first trailing word: an instance count or split whose 0xf0000000 means none.
  Measured: 0xf0000000 in every capture [infer]. From `VDM_INDEX2.WORD` (ours, resgx545).
- `VDM_INDEX3.INDEX_WRAP` G0499 (index list, the second trailing word): the vertex range the indices
  wrap at: 0 leaves them, 5 takes them modulo 5, 1 removes every triangle (as degenerate, a reading)
  and 8 hangs; only these four values were tried [infer]. From `VDM_INDEX3.INDEX_WRAP` (ours,
  resgx545).
- `VDM_INDEX0.PRIMITIVE_TOPOLOGY` G0496 (index-list header [29:26]): primitive type of the index
  list. From `primitive_topology` (3, mesa-csbgen).
- `ISP0.OBJ_TYPE` G0471 (isp0 [17:15]): object type. From `objtype` (3, mesa-csbgen).
- `ISP0.PASS_TYPE` G0245 (isp0 [27:25]): pass type. From `passtype` (3, mesa-csbgen).
- `MTECTL.CULL_MODE` G0251 (mtectl [1:0]): cull mode. From `cullmode` (3, mesa-csbgen).
- `MTECTL.ATTR_SMOOTH` G0474 (mtectl [29:10], 2 bits per attribute): one field per vertex output
  attribute after the position (attribute i at 11:10 + 2i): non-zero, the vertices the MTE makes
  when it clips interpolate that attribute even under MTECTL.FLAT_VERTEX; 0, they copy the vertex it
  names [infer]. From `MTECTL.ATTR_SMOOTH` (ours, resgx545).
- `MTECTL.FLAT_VERTEX` G0475 (mtectl [8:7]): flat shading's provoking vertex for clipping: 0 the
  vertices the MTE makes interpolate their attributes, 1-3 they take vertex 0's, 1's, 2's values
  (also a vertex clipped away), for the attributes MTECTL.ATTR_SMOOTH leaves flat; it also changes
  how the clipped polygon is cut into triangles [infer]. From `MTECTL.FLAT_VERTEX` (ours, resgx545).
- `MTECTL.NO_TRANSFORM` G0476 (mtectl bit 6): take the vertex positions as window coordinates: no
  division by w (the object's 1/w slot gets w) and no viewport transform; our triangle, in clip
  space, then covers no pixel [infer]. From `MTECTL.NO_TRANSFORM` (ours, resgx545).
- `OUTSEL.VTX_SIZE` G0479 (outsel [19:16]): vertex size in dwords. From `vtxsize` (3, mesa-csbgen).
- `REGION_HDR.POS` G0493 (region header word 0 [23:16], [15:0]): the region's place: bits 23:16 step
  2 per 32-pixel column, the low bits 2 per 16-pixel row, bits 15:12 the macrotile; a region is 32 x
  16 pixels, and every region of the target's macrotiles has a header [infer]. From `REGION_HDR.POS`
  (ours, resgx545).
- `REGION_HDR.FLAGS` G0492 (region header word 0 [31:24]): bit 25 a region outside the target, 26
  the first region of a macrotile, 27 an empty region inside it, 28 the last region of a macrotile,
  31 the last of the scene [infer]. From `REGION_HDR.FLAGS` (ours, resgx545).
- `REGION_HDR.STREAM` G0494 (region header word 1): the region's control-stream block, relative to
  the parameter slot; 0 for an empty region [infer]. From `REGION_HDR.STREAM` (ours, resgx545).
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
- `VDM_TASK1.OUTPUT_SIZE` G0503 (vertex-task word 1 [31:24]): output vertex size. From
  `vs_output_size` (3, mesa-csbgen).

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
  no-op state blocks. Measured: set on the captured state blocks whose PDS program loads a constant
  block or starts a no-op USE task, clear on the MTE-state and vertex blocks [infer]. From
  `VDM_STATE1.BIT8` (ours, resgx545).
- `FEEDBACK_CTL.KEEP` G0230 (atst8/depthf src1 bit 0): inferred reading (unconfirmed): with
  FEEDBACK_CTL.ENABLE, the punch-through feedback keeps the pixel; clear, it discards it [infer].
  From `FEEDBACK_CTL.KEEP` (ours, resgx545).
- `FEEDBACK_CTL.ENABLE` G0229 (atst8/depthf src1 bit 14): inferred reading (unconfirmed): the
  punch-through feedback is valid; clear, the pixel is discarded whatever bit 0 says [infer]. From
  `FEEDBACK_CTL.ENABLE` (ours, resgx545).
- `CSTREAM.PRIM_POINTS` G0462 (control-stream primitive word bit 29 (bit 30 set in every word
  seen)): the object's primitives are points; clear for triangles and lines, which ISP word 0's
  object type tells apart [infer]. From `CSTREAM.PRIM_POINTS` (ours, resgx545).
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
- `VDM_INDEX0.WORDS_PRESENT` G0497 (index-list header bits 22/23): the index list's two trailing
  words are present (bit 22 and bit 23, one word each, read in order after the index base) [infer].
  From `VDM_INDEX0.WORDS_PRESENT` (ours, resgx545).
- `OUTSEL.COLOUR_PRES` G0478 (outsel bit 11): the four dwords after the vertex position are its
  colour (R, G, B, A), iterated by DOUTI0.ATTR_SOURCE 32 [infer]. From `OUTSEL.COLOUR_PRES` (ours,
  resgx545).
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
- `PRESENCE.WCLAMP` G0491 (presence bit 11 (wclamp)): W clamp word present. From `pres_wclamp` (3,
  mesa-csbgen).
- `PRESENCE.COORD` G0490 (presence bits 14/15 (coordsize, coordfmt) [infer]): varying format word
  present. From `pres_varying_word0` (3, mesa-csbgen).
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
- `OUTSEL` G0477 (outsel): output selects of the vertex. From `OUTPUT_SEL` (3, mesa-csbgen).
- `WCLAMP` G0504 (wclamp): W clamp value (float) [infer]. From `WCLAMP` (3, mesa-csbgen).

## 5. Sources

- `emgd-linux` (tier 1): Intel EMGD for Linux, SGX535 kernel side.
- `emgd-psb_regs` (tier 1): Intel's psb_regs.h in EMGD: the SGX535 (Poulsbo) register list (MIT).
- `intel-ctp-k900` (tier 1): Lenovo K900 GPL kernel, Clover Trail+ SGX544MP2, DDK 1.11.
- `intel-ctp-santos10` (tier 1): Samsung's GPL kernel for its santos10 device (Intel Clover Trail+,
  SGX544MP2), DDK 1.9.
- `sgx545-ce` (tier 1): Intel's GPL DDK 1.7 kernel module for Cedarview, our core.
- `cdv-libsrv_um` (tier 2): strings and exports of libsrv_um.so in our Cedarview package.
- `cdv-libusc` (tier 2): strings of libusc.so in our Cedarview package.
- `linux-imagination` (tier 3): Imagination's Rogue kernel driver, drivers/gpu/drm/imagination.
- `mesa-csbgen` (tier 3): Mesa src/imagination/csbgen: Rogue state words (Imagination, MIT).
- `mesa-pco` (tier 3): Mesa src/imagination/pco: the Rogue shader ISA (MIT).
- `mesa-pds-defs` (tier 3): Mesa src/imagination/vulkan/pds: Rogue PDS instructions (MIT).
- `imgtec-performance-recommendations` (tier 4): Imagination's PowerVR Performance Recommendations
  (2018).
- `imgtec-pvrtune-counters` (tier 4): Imagination's PVRTune Counter List and Description (2017).
- `imgtec-sgx-arch-guide-1.0.13` (tier 4): Imagination's PowerVR Series 5 SGX Architecture Guide for
  Developers 1.0.13 (2012, public).
- `imgtec-sgx-arch-guide-1.0.8` (tier 4): Imagination's PowerVR Series5 Graphics SGX architecture
  guide for developers 1.0.8 (2011, public).
- `imgtec-technology-overview-1.0.2e` (tier 4): Imagination's PowerVR Technology Overview 1.0.2e
  (2010).
- `patent-US7324115` (tier 4): patent US7324115 (Imagination Technologies).
- `patent-US7978199` (tier 4): patent US7978199 (Imagination Technologies).
- `patent-US8046761` (tier 4): patent US8046761 (Imagination Technologies).
- `patent-US8669987` (tier 4): patent US8669987 (Imagination Technologies).
- `patent-US8723860` (tier 4): patent US8723860 (Imagination Technologies).
- `patent-US8743117` (tier 4): patent US8743117 (Imagination Technologies).
- `patent-US9105131` (tier 4): patent US9105131 (Imagination Technologies).
- `patent-US9384584` (tier 4): patent US9384584 (Imagination Technologies).
- `powervr-docs` (tier 4): Imagination's public PowerVR architecture guides.
- `ti-omap4430-trm` (tier 4): TI's public OMAP4430 TRM (swpu231ap), chapter 11 on its SGX540:
  Imagination's architecture in its own terms.
- `resgx545` (tier ours): this project: our own term for a thing no open source names, after our
  measurements.
