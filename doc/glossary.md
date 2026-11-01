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
- `Rogue MIPS wrapper registers` G1152: Rogue's MIPS firmware address remap register, at offset
  0x0818 and 64 bits wide: an analogy at the offset of SGX545's CR_REG_0818 that does not explain
  it, since SGX545 implements bits 10:0 of the dword there (E401). From
  `ROGUE_CR_MIPS_ADDR_REMAP1_CONFIG1` (3, linux-imagination); `ROGUE_CR_MIPS_WRAPPER_CONFIG` (3,
  linux-imagination).
- `Tile Based Deferred Rendering (TBDR)` G0068: bin the whole scene first, then render tile by tile,
  shading only visible pixels. From `TBDR` (4, imgtec-sgx-arch-guide-1.0.13).
- `break point object` G0645: an object in the tile lists whose rasterisation halts the ISP and
  calls the control processor, which may patch the tile list and resume. From `break point (BP)
  object` (4, patent-US20090058848).
- `control stream` G0516: per-tile control stream data written by the TA. From `control stream` (4,
  patent-US8669987).
- `data master` G1137: Rogue firmware list of data masters (analogue). From `data master` (3,
  linux-imagination); `data master` (4, patent-US8046761).
- `display list` G0070: per-tile display lists (macrotiles). From `display list` (4,
  patent-US7324115).
- `free list` G1138: Rogue parameter memory free lists (analogue). From `free list` (3,
  linux-imagination); `free list` (4, patent-US7978199).
- `global list` G1139: the list of object data that falls in more than one macro-tile. From `global
  list` (4, patent-US8669987).
- `macro tile` G0557: Rogue firmware array of macro tiles (analogue). From `macrotile_array` (3,
  linux-imagination); `macro tile` (4, patent-US7978199).
- `object list` G1148: per-tile list of objects from the TA. From `object list` (4,
  patent-US9105131).
- `partial render` G0558: Rogue fragment job run when the PM runs out of memory (analogue). From
  `partial render` (3, linux-imagination); `partial render` (4, imgtec-performance-recommendations);
  `Partial render` (4, patent-US8723860).
- `programmable sample positions` G0333: the samples' positions within the pixel are programmable
  (with 4x multisampling). From `programmable sample positions` (4, ti-omap4430-trm).
- `region header` G0562: per-tile region headers written by geometry (Rogue analogue). From `region
  header` (3, linux-imagination); `region header` (4, patent-US9105131); `Region Header` (4,
  patent-US9384584).
- `tail pointer cache` G1149: keeps the address of the next available control-stream block per tile.
  From `tail pointer cache` (4, patent-US8669987).
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
- `Event Data Master (EDM)` G0628: data master that services events on the USSE without interrupting
  the host. From `EDM` (4, patent-US8046761); `general-purpose data master` (4, ti-omap4430-trm).
- `Image Synthesis Processor (ISP)` G0063 (CR_CLKGATECTL.ISP_CLKG): ISP block (its clock gate). From
  `ISP` (1, sgx545-ce); `ISP` (4, imgtec-sgx-arch-guide-1.0.13); `Hidden Surface Removal unit` (4,
  patent-US8743117).
- `Pixel Back End (PBE)` G0065 (CR_EVENT_STATUS.PIXELBE_END_RENDER): PBE as spelled in register
  names; signals end of render. From `PIXELBE` (1, sgx545-ce); `PBE` (4,
  imgtec-sgx-arch-guide-1.0.13); `Pixel Back End` (4, powervr-docs); `pixel coprocessor` (4,
  ti-omap4430-trm).
- `Programmable Data Sequencer (PDS)` G1124 (CR_CLKGATECTL.PDS0_CLKG): PDS block (clock gate of PDS
  0). From `PDS` (1, sgx545-ce); `PDS` (4, patent-US8046761).
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
- `MADD` G0607 (0x0004[13:12] (MADD0)): inferred reading (unconfirmed): per the SGX540's technical
  reference manual, the wrapper of the main cache: arbitrates the PDS, USSE and texture requests,
  caches them at level 0 and decompresses textures; one of two readings (Q048) [infer]. From
  `mux/arbiter/demux/decompression unit (MADD)` (4, ti-omap4430-trm).
- `CACHEL2` G1116 (0x0004[3:2]): level 2 cache [infer]. From `CACHEL2` (1, sgx545-ce).
- `UCACHEL2` G1133 (0x0004[5:4]): USE level 2 (code) cache [infer]. From `UCACHEL2` (1, sgx545-ce).
- `PPP` G1123 (MTE registers 0x0230, 0x023c, 0x0248): Rogue unit that takes state updates and
  primitives before the clipper and TA; SGX545's counterpart is the MTE. From `PPP` (3,
  mesa-csbgen).

## 2. Registers and their fields

### bitfield

- `CR_ISP_CTL.PROCESS_EMPTY_TILES` G1052 (0x0414[8]): process empty tiles too, so a partial render
  visits every tile (Rogue analogue). From `ROGUE_CR_ISP_CTL_PROCESS_EMPTY_TILES` (3,
  linux-imagination); `process_empty_tiles` (3, mesa-csbgen).
- `CR_CLKGATECTL.DPM_CLKG` G0779 (0x0000[11:10]): clock-gating mode of the DPM (0 on, 1 off, 2 auto
  per psb_regs.h). From `EUR_CR_CLKGATECTL_DPM_CLKG` (1, sgx545-ce);
  `_PSB_C_CLKGATECTL_DPM_CLKG_MASK` (1c, emgd-psb_regs).
- `CR_CLKGATECTL.VDM_CLKG` G0786 (0x0000[13:12]): clock-gating mode of the VDM (0 on, 1 off, 2 auto
  per psb_regs.h). From `EUR_CR_CLKGATECTL_VDM_CLKG` (1, sgx545-ce).
- `CR_CLKGATECTL.PDS0_CLKG` G0783 (0x0000[15:14]): clock-gating mode of the PDS 0 (0 on, 1 off, 2
  auto per psb_regs.h). From `EUR_CR_CLKGATECTL_PDS0_CLKG` (1, sgx545-ce).
- `CR_CLKGATECTL.ISP_CLKG` G0781 (0x0000[1:0]): clock-gating mode of the ISP (0 on, 1 off, 2 auto
  per psb_regs.h). From `EUR_CR_CLKGATECTL_ISP_CLKG` (1, sgx545-ce);
  `_PSB_C_CLKGATECTL_ISP_CLKG_MASK` (1c, emgd-psb_regs).
- `CR_CLKGATECTL.AUTO_MAN_REG` G0778 (0x0000[24]): register-block clock gating: automatic or manual.
  From `EUR_CR_CLKGATECTL_AUTO_MAN_REG` (1, sgx545-ce).
- `CR_CLKGATECTL.ISP2_CLKG` G0780 (0x0000[3:2]): clock-gating mode of the second ISP (0 on, 1 off, 2
  auto per psb_regs.h). From `EUR_CR_CLKGATECTL_ISP2_CLKG` (1, sgx545-ce).
- `CR_CLKGATECTL.TSP_CLKG` G0785 (0x0000[5:4]): clock-gating mode of the TSP (0 on, 1 off, 2 auto
  per psb_regs.h). From `EUR_CR_CLKGATECTL_TSP_CLKG` (1, sgx545-ce);
  `_PSB_C_CLKGATECTL_TSP_CLKG_MASK` (1c, emgd-psb_regs).
- `CR_CLKGATECTL.TE_CLKG` G0784 (0x0000[7:6]): clock-gating mode of the TE (0 on, 1 off, 2 auto per
  psb_regs.h). From `EUR_CR_CLKGATECTL_TE_CLKG` (1, sgx545-ce).
- `CR_CLKGATECTL.MTE_CLKG` G0782 (0x0000[9:8]): clock-gating mode of the MTE (0 on, 1 off, 2 auto
  per psb_regs.h). From `EUR_CR_CLKGATECTL_MTE_CLKG` (1, sgx545-ce).
- `CR_CLKGATECTL2.TEX0_CLKG` G0794 (0x0004[11:10]): clock-gating mode of the texture unit 0 (0 on, 1
  off, 2 auto per psb_regs.h). From `EUR_CR_CLKGATECTL2_TEX0_CLKG` (1, sgx545-ce).
- `CR_CLKGATECTL2.MADD0_CLKG` G0790 (0x0004[13:12]): clock-gating mode of the MADD 0 (0 on, 1 off, 2
  auto per psb_regs.h). From `EUR_CR_CLKGATECTL2_MADD0_CLKG` (1, sgx545-ce).
- `CR_CLKGATECTL2.USE1_CLKG` G0798 (0x0004[15:14]): clock-gating mode of the USSE 1 (0 on, 1 off, 2
  auto per psb_regs.h). From `EUR_CR_CLKGATECTL2_USE1_CLKG` (1, sgx545-ce).
- `CR_CLKGATECTL2.ITR1_CLKG` G0789 (0x0004[17:16]): clock-gating mode of the iterator 1 (0 on, 1
  off, 2 auto per psb_regs.h). From `EUR_CR_CLKGATECTL2_ITR1_CLKG` (1, sgx545-ce).
- `CR_CLKGATECTL2.TEX1_CLKG` G0795 (0x0004[19:18]): clock-gating mode of the texture unit 1 (0 on, 1
  off, 2 auto per psb_regs.h). From `EUR_CR_CLKGATECTL2_TEX1_CLKG` (1, sgx545-ce).
- `CR_CLKGATECTL2.PBE_CLKG` G0792 (0x0004[1:0]): clock-gating mode of the PBE (0 on, 1 off, 2 auto
  per psb_regs.h). From `EUR_CR_CLKGATECTL2_PBE_CLKG` (1, sgx545-ce).
- `CR_CLKGATECTL2.MADD1_CLKG` G0791 (0x0004[21:20]): clock-gating mode of the MADD 1 (0 on, 1 off, 2
  auto per psb_regs.h). From `EUR_CR_CLKGATECTL2_MADD1_CLKG` (1, sgx545-ce).
- `CR_CLKGATECTL2.PDS1_CLKG` G0793 (0x0004[23:22]): clock-gating mode of the PDS 1 (0 on, 1 off, 2
  auto per psb_regs.h). From `EUR_CR_CLKGATECTL2_PDS1_CLKG` (1, sgx545-ce).
- `CR_CLKGATECTL2.CACHEL2_CLKG` G0787 (0x0004[3:2]): clock-gating mode of the L2 cache (0 on, 1 off,
  2 auto per psb_regs.h). From `EUR_CR_CLKGATECTL2_CACHEL2_CLKG` (1, sgx545-ce).
- `CR_CLKGATECTL2.UCACHEL2_CLKG` G0796 (0x0004[5:4]): clock-gating mode of the USSE L2 cache (0 on,
  1 off, 2 auto per psb_regs.h). From `EUR_CR_CLKGATECTL2_UCACHEL2_CLKG` (1, sgx545-ce).
- `CR_CLKGATECTL2.USE0_CLKG` G0797 (0x0004[7:6]): clock-gating mode of the USSE 0 (0 on, 1 off, 2
  auto per psb_regs.h). From `EUR_CR_CLKGATECTL2_USE0_CLKG` (1, sgx545-ce).
- `CR_CLKGATECTL2.ITR0_CLKG` G0788 (0x0004[9:8]): clock-gating mode of the iterator 0 (0 on, 1 off,
  2 auto per psb_regs.h). From `EUR_CR_CLKGATECTL2_ITR0_CLKG` (1, sgx545-ce).
- `CR_CLKGATESTATUS.ISP_CLKS` G0802 (0x0008[0]): clock state of the ISP. From
  `EUR_CR_CLKGATESTATUS_ISP_CLKS` (1, sgx545-ce).
- `CR_CLKGATESTATUS.UCACHEL2_CLKS` G0815 (0x0008[10]): clock state of the USSE L2 cache. From
  `EUR_CR_CLKGATESTATUS_UCACHEL2_CLKS` (1, sgx545-ce).
- `CR_CLKGATESTATUS.USE0_CLKS` G0816 (0x0008[11]): clock state of the USSE 0. From
  `EUR_CR_CLKGATESTATUS_USE0_CLKS` (1, sgx545-ce).
- `CR_CLKGATESTATUS.ITR0_CLKS` G0803 (0x0008[12]): clock state of the iterator 0. From
  `EUR_CR_CLKGATESTATUS_ITR0_CLKS` (1, sgx545-ce).
- `CR_CLKGATESTATUS.TEX0_CLKS` G0811 (0x0008[13]): clock state of the texture unit 0. From
  `EUR_CR_CLKGATESTATUS_TEX0_CLKS` (1, sgx545-ce).
- `CR_CLKGATESTATUS.MADD0_CLKS` G0805 (0x0008[14]): clock state of the MADD 0. From
  `EUR_CR_CLKGATESTATUS_MADD0_CLKS` (1, sgx545-ce).
- `CR_CLKGATESTATUS.USE1_CLKS` G0817 (0x0008[15]): clock state of the USSE 1. From
  `EUR_CR_CLKGATESTATUS_USE1_CLKS` (1, sgx545-ce).
- `CR_CLKGATESTATUS.ITR1_CLKS` G0804 (0x0008[16]): clock state of the iterator 1. From
  `EUR_CR_CLKGATESTATUS_ITR1_CLKS` (1, sgx545-ce).
- `CR_CLKGATESTATUS.TEX1_CLKS` G0812 (0x0008[17]): clock state of the texture unit 1. From
  `EUR_CR_CLKGATESTATUS_TEX1_CLKS` (1, sgx545-ce).
- `CR_CLKGATESTATUS.MADD1_CLKS` G0806 (0x0008[18]): clock state of the MADD 1. From
  `EUR_CR_CLKGATESTATUS_MADD1_CLKS` (1, sgx545-ce).
- `CR_CLKGATESTATUS.PDS1_CLKS` G0810 (0x0008[19]): clock state of the PDS 1. From
  `EUR_CR_CLKGATESTATUS_PDS1_CLKS` (1, sgx545-ce).
- `CR_CLKGATESTATUS.ISP2_CLKS` G0801 (0x0008[1]): clock state of the second ISP. From
  `EUR_CR_CLKGATESTATUS_ISP2_CLKS` (1, sgx545-ce).
- `CR_CLKGATESTATUS.TSP_CLKS` G0814 (0x0008[2]): clock state of the TSP. From
  `EUR_CR_CLKGATESTATUS_TSP_CLKS` (1, sgx545-ce).
- `CR_CLKGATESTATUS.TE_CLKS` G0813 (0x0008[3]): clock state of the TE. From
  `EUR_CR_CLKGATESTATUS_TE_CLKS` (1, sgx545-ce).
- `CR_CLKGATESTATUS.MTE_CLKS` G0807 (0x0008[4]): clock state of the MTE. From
  `EUR_CR_CLKGATESTATUS_MTE_CLKS` (1, sgx545-ce).
- `CR_CLKGATESTATUS.DPM_CLKS` G0800 (0x0008[5]): clock state of the DPM. From
  `EUR_CR_CLKGATESTATUS_DPM_CLKS` (1, sgx545-ce).
- `CR_CLKGATESTATUS.VDM_CLKS` G0818 (0x0008[6]): clock state of the VDM. From
  `EUR_CR_CLKGATESTATUS_VDM_CLKS` (1, sgx545-ce).
- `CR_CLKGATESTATUS.PDS0_CLKS` G0809 (0x0008[7]): clock state of the PDS 0. From
  `EUR_CR_CLKGATESTATUS_PDS0_CLKS` (1, sgx545-ce).
- `CR_CLKGATESTATUS.PBE_CLKS` G0808 (0x0008[8]): clock state of the PBE. From
  `EUR_CR_CLKGATESTATUS_PBE_CLKS` (1, sgx545-ce).
- `CR_CLKGATESTATUS.CACHEL2_CLKS` G0799 (0x0008[9]): clock state of the L2 cache. From
  `EUR_CR_CLKGATESTATUS_CACHEL2_CLKS` (1, sgx545-ce).
- `CR_CORE_ID.CONFIG` G0819 (0x001c[15:0]): core configuration. From `EUR_CR_CORE_ID_CONFIG` (1,
  sgx545-ce); `_PSB_CC_ID_CONFIG_MASK` (1c, emgd-psb_regs); `EUR_CR_CORE_ID_CONFIG` (1c, sgx545-ce).
- `CR_CORE_ID.ID` G0820 (0x001c[31:16]): core identifier. From `EUR_CR_CORE_ID_ID` (1, sgx545-ce);
  `_PSB_CC_ID_ID_MASK` (1c, emgd-psb_regs); `EUR_CR_CORE_ID_ID` (1c, sgx545-ce).
- `CR_CORE_REVISION.MINOR` G0824 (0x0020[15:8]): minor revision. From `EUR_CR_CORE_REVISION_MINOR`
  (1, sgx545-ce); `_PSB_CC_REVISION_MINOR_MASK` (1c, emgd-psb_regs); `EUR_CR_CORE_REVISION_MINOR`
  (1c, sgx545-ce).
- `CR_CORE_REVISION.MAJOR` G0823 (0x0020[23:16]): major revision. From `EUR_CR_CORE_REVISION_MAJOR`
  (1, sgx545-ce); `_PSB_CC_REVISION_MAJOR_MASK` (1c, emgd-psb_regs); `EUR_CR_CORE_REVISION_MAJOR`
  (1c, sgx545-ce).
- `CR_CORE_REVISION.DESIGNER` G0821 (0x0020[31:24]): designer revision. From
  `EUR_CR_CORE_REVISION_DESIGNER` (1, sgx545-ce); `_PSB_CC_REVISION_DESIGNER_MASK` (1c,
  emgd-psb_regs); `EUR_CR_CORE_REVISION_DESIGNER` (1c, sgx545-ce).
- `CR_CORE_REVISION.MAINTENANCE` G0822 (0x0020[7:0]): maintenance revision. From
  `EUR_CR_CORE_REVISION_MAINTENANCE` (1, sgx545-ce); `_PSB_CC_REVISION_MAINTENANCE_MASK` (1c,
  emgd-psb_regs); `EUR_CR_CORE_REVISION_MAINTENANCE` (1c, sgx545-ce).
- `CR_HWPERF_CTRL.GROUP` G0416 (0x0040[12:9]): counter group the EDM selects from host control dword
  15 when HWPerf is on; what each group counts is not measured here (PVRTune's groups: 0 overview, 1
  triangles and vertices, 2 tiling, 3 ISP, 4 TSP, 5 USSE, 6 texturing) [infer]. From
  `CR_HWPERF_CTRL.GROUP` (ours, resgx545).
- `CR_SOFT_RESET.BIF_RESET` G0959 (0x0080[0]): hold the BIF (MMU) in reset. From
  `EUR_CR_SOFT_RESET_BIF_RESET` (1, sgx545-ce).
- `CR_SOFT_RESET.DPM_RESET` G0960 (0x0080[1]): hold the DPM in reset. From
  `EUR_CR_SOFT_RESET_DPM_RESET` (1, sgx545-ce).
- `CR_SOFT_RESET.TA_RESET` G0439 (0x0080[2]): hold the TA in reset. From
  `EUR_CR_SOFT_RESET_TA_RESET` (1, sgx545-ce).
- `CR_SOFT_RESET.USE_RESET` G0963 (0x0080[3]): hold the USSE in reset. From
  `EUR_CR_SOFT_RESET_USE_RESET` (1, sgx545-ce).
- `CR_SOFT_RESET.ISP_RESET` G0961 (0x0080[4]): hold the ISP in reset. From
  `EUR_CR_SOFT_RESET_ISP_RESET` (1, sgx545-ce).
- `CR_SOFT_RESET.TSP_RESET` G0962 (0x0080[5]): hold the TSP in reset. From
  `EUR_CR_SOFT_RESET_TSP_RESET` (1, sgx545-ce).
- `CR_EVENT_HOST_ENABLE2.DPM_TA_FREE_LOAD` G0910 (0x0110[0]): send to host: DPM TA free-list load
  done. From `EUR_CR_EVENT_HOST_ENABLE2_DPM_TA_FREE_LOAD` (1, sgx545-ce).
- `CR_EVENT_HOST_ENABLE2.DCU_INVAL_COMPLETE` G0906 (0x0110[10]): send to host: data cache invalidate
  complete. From `EUR_CR_EVENT_HOST_ENABLE2_DCU_INVALCOMPLETE` (1, sgx545-ce).
- `CR_EVENT_HOST_ENABLE2.OTPM_FLUSHED_INV` G0914 (0x0110[11]): send to host: OTPM flush and
  invalidate done. From `EUR_CR_EVENT_HOST_ENABLE2_OTPM_FLUSHED_INV` (1, sgx545-ce).
- `CR_EVENT_HOST_ENABLE2.OTPM_MEM_CLEARED` G0915 (0x0110[12]): send to host: OTPM memory cleared.
  From `EUR_CR_EVENT_HOST_ENABLE2_OTPM_MEM_CLEARED` (1, sgx545-ce).
- `CR_EVENT_HOST_ENABLE2.VDM_TASK_KICKED` G0920 (0x0110[13]): send to host: VDM task kicked. From
  `EUR_CR_EVENT_HOST_ENABLE2_VDM_TASK_KICKED` (1, sgx545-ce).
- `CR_EVENT_HOST_ENABLE2.VDM_CONTEXT_LOAD` G0919 (0x0110[14]): send to host: VDM context load done.
  From `EUR_CR_EVENT_HOST_ENABLE2_VDM_CONTEXT_LOAD` (1, sgx545-ce).
- `CR_EVENT_HOST_ENABLE2.MTE_STATE_FLUSHED` G0913 (0x0110[15]): send to host: MTE state flushed.
  From `EUR_CR_EVENT_HOST_ENABLE2_MTE_STATE_FLUSHED` (1, sgx545-ce).
- `CR_EVENT_HOST_ENABLE2.DPM_3D_FREE_LOAD` G0907 (0x0110[1]): send to host: DPM 3D free-list load
  done. From `EUR_CR_EVENT_HOST_ENABLE2_DPM_3D_FREE_LOAD` (1, sgx545-ce).
- `CR_EVENT_HOST_ENABLE2.DPM_HOST_FREE_LOAD` G0909 (0x0110[2]): send to host: DPM host free-list
  load done. From `EUR_CR_EVENT_HOST_ENABLE2_DPM_HOST_FREE_LOAD` (1, sgx545-ce).
- `CR_EVENT_HOST_ENABLE2.DPM_DHOST_FREE_LOAD` G0908 (0x0110[3]): send to host: DPM host-deallocation
  free-list load done. From `EUR_CR_EVENT_HOST_ENABLE2_DPM_DHOST_FREE_LOAD` (1, sgx545-ce).
- `CR_EVENT_HOST_ENABLE2.TRIG_DL` G0917 (0x0110[5]): send to host: DL trigger. From
  `EUR_CR_EVENT_HOST_ENABLE2_TRIG_DL` (1, sgx545-ce).
- `CR_EVENT_HOST_ENABLE2.TRIG_3D` G0916 (0x0110[6]): send to host: 3D trigger. From
  `EUR_CR_EVENT_HOST_ENABLE2_TRIG_3D` (1, sgx545-ce).
- `CR_EVENT_HOST_ENABLE2.TRIG_TA` G0918 (0x0110[7]): send to host: TA trigger. From
  `EUR_CR_EVENT_HOST_ENABLE2_TRIG_TA` (1, sgx545-ce).
- `CR_EVENT_HOST_ENABLE2.GSG_LOADED` G0912 (0x0110[8]): send to host: GSG state loaded. From
  `EUR_CR_EVENT_HOST_ENABLE2_GSG_LOADED` (1, sgx545-ce).
- `CR_EVENT_HOST_ENABLE2.GSG_FLUSHED` G0911 (0x0110[9]): send to host: GSG state flushed. From
  `EUR_CR_EVENT_HOST_ENABLE2_GSG_FLUSHED` (1, sgx545-ce).
- `CR_EVENT_HOST_CLEAR2.DPM_TA_FREE_LOAD` G0866 (0x0114[0]): clear: DPM TA free-list load done. From
  `EUR_CR_EVENT_HOST_CLEAR2_DPM_TA_FREE_LOAD` (1, sgx545-ce).
- `CR_EVENT_HOST_CLEAR2.DCU_INVAL_COMPLETE` G0862 (0x0114[10]): clear: data cache invalidate
  complete. From `EUR_CR_EVENT_HOST_CLEAR2_DCU_INVALCOMPLETE` (1, sgx545-ce).
- `CR_EVENT_HOST_CLEAR2.OTPM_FLUSHED_INV` G0870 (0x0114[11]): clear: OTPM flush and invalidate done.
  From `EUR_CR_EVENT_HOST_CLEAR2_OTPM_FLUSHED_INV` (1, sgx545-ce).
- `CR_EVENT_HOST_CLEAR2.OTPM_MEM_CLEARED` G0871 (0x0114[12]): clear: OTPM memory cleared. From
  `EUR_CR_EVENT_HOST_CLEAR2_OTPM_MEM_CLEARED` (1, sgx545-ce).
- `CR_EVENT_HOST_CLEAR2.VDM_TASK_KICKED` G0876 (0x0114[13]): clear: VDM task kicked. From
  `EUR_CR_EVENT_HOST_CLEAR2_VDM_TASK_KICKED` (1, sgx545-ce).
- `CR_EVENT_HOST_CLEAR2.VDM_CONTEXT_LOAD` G0875 (0x0114[14]): clear: VDM context load done. From
  `EUR_CR_EVENT_HOST_CLEAR2_VDM_CONTEXT_LOAD` (1, sgx545-ce).
- `CR_EVENT_HOST_CLEAR2.MTE_STATE_FLUSHED` G0869 (0x0114[15]): clear: MTE state flushed. From
  `EUR_CR_EVENT_HOST_CLEAR2_MTE_STATE_FLUSHED` (1, sgx545-ce).
- `CR_EVENT_HOST_CLEAR2.DPM_3D_FREE_LOAD` G0863 (0x0114[1]): clear: DPM 3D free-list load done. From
  `EUR_CR_EVENT_HOST_CLEAR2_DPM_3D_FREE_LOAD` (1, sgx545-ce).
- `CR_EVENT_HOST_CLEAR2.DPM_HOST_FREE_LOAD` G0865 (0x0114[2]): clear: DPM host free-list load done.
  From `EUR_CR_EVENT_HOST_CLEAR2_DPM_HOST_FREE_LOAD` (1, sgx545-ce).
- `CR_EVENT_HOST_CLEAR2.DPM_DHOST_FREE_LOAD` G0864 (0x0114[3]): clear: DPM host-deallocation
  free-list load done. From `EUR_CR_EVENT_HOST_CLEAR2_DPM_DHOST_FREE_LOAD` (1, sgx545-ce).
- `CR_EVENT_HOST_CLEAR2.TRIG_DL` G0873 (0x0114[5]): clear: DL trigger. From
  `EUR_CR_EVENT_HOST_CLEAR2_TRIG_DL` (1, sgx545-ce).
- `CR_EVENT_HOST_CLEAR2.TRIG_3D` G0872 (0x0114[6]): clear: 3D trigger. From
  `EUR_CR_EVENT_HOST_CLEAR2_TRIG_3D` (1, sgx545-ce).
- `CR_EVENT_HOST_CLEAR2.TRIG_TA` G0874 (0x0114[7]): clear: TA trigger. From
  `EUR_CR_EVENT_HOST_CLEAR2_TRIG_TA` (1, sgx545-ce).
- `CR_EVENT_HOST_CLEAR2.GSG_LOADED` G0868 (0x0114[8]): clear: GSG state loaded. From
  `EUR_CR_EVENT_HOST_CLEAR2_GSG_LOADED` (1, sgx545-ce).
- `CR_EVENT_HOST_CLEAR2.GSG_FLUSHED` G0867 (0x0114[9]): clear: GSG state flushed. From
  `EUR_CR_EVENT_HOST_CLEAR2_GSG_FLUSHED` (1, sgx545-ce).
- `CR_EVENT_STATUS2.DPM_TA_FREE_LOAD` G0938 (0x0118[0]): status: DPM TA free-list load done. From
  `EUR_CR_EVENT_STATUS2_DPM_TA_FREE_LOAD` (1, sgx545-ce).
- `CR_EVENT_STATUS2.DCU_INVAL_COMPLETE` G0934 (0x0118[10]): status: data cache invalidate complete.
  From `EUR_CR_EVENT_STATUS2_DCU_INVALCOMPLETE` (1, sgx545-ce).
- `CR_EVENT_STATUS2.OTPM_FLUSHED_INV` G0942 (0x0118[11]): status: OTPM flush and invalidate done.
  From `EUR_CR_EVENT_STATUS2_OTPM_FLUSHED_INV` (1, sgx545-ce).
- `CR_EVENT_STATUS2.OTPM_MEM_CLEARED` G0943 (0x0118[12]): status: OTPM memory cleared. From
  `EUR_CR_EVENT_STATUS2_OTPM_MEM_CLEARED` (1, sgx545-ce).
- `CR_EVENT_STATUS2.VDM_TASK_KICKED` G0948 (0x0118[13]): status: VDM task kicked. From
  `EUR_CR_EVENT_STATUS2_VDM_TASK_KICKED` (1, sgx545-ce).
- `CR_EVENT_STATUS2.VDM_CONTEXT_LOAD` G0947 (0x0118[14]): status: VDM context load done. From
  `EUR_CR_EVENT_STATUS2_VDM_CONTEXT_LOAD` (1, sgx545-ce).
- `CR_EVENT_STATUS2.MTE_STATE_FLUSHED` G0941 (0x0118[15]): status: MTE state flushed. From
  `EUR_CR_EVENT_STATUS2_MTE_STATE_FLUSHED` (1, sgx545-ce).
- `CR_EVENT_STATUS2.DPM_3D_FREE_LOAD` G0935 (0x0118[1]): status: DPM 3D free-list load done. From
  `EUR_CR_EVENT_STATUS2_DPM_3D_FREE_LOAD` (1, sgx545-ce).
- `CR_EVENT_STATUS2.DPM_HOST_FREE_LOAD` G0937 (0x0118[2]): status: DPM host free-list load done.
  From `EUR_CR_EVENT_STATUS2_DPM_HOST_FREE_LOAD` (1, sgx545-ce).
- `CR_EVENT_STATUS2.DPM_DHOST_FREE_LOAD` G0936 (0x0118[3]): status: DPM host-deallocation free-list
  load done. From `EUR_CR_EVENT_STATUS2_DPM_DHOST_FREE_LOAD` (1, sgx545-ce).
- `CR_EVENT_STATUS2.TRIG_DL` G0945 (0x0118[5]): status: DL trigger. From
  `EUR_CR_EVENT_STATUS2_TRIG_DL` (1, sgx545-ce).
- `CR_EVENT_STATUS2.TRIG_3D` G0944 (0x0118[6]): status: 3D trigger. From
  `EUR_CR_EVENT_STATUS2_TRIG_3D` (1, sgx545-ce).
- `CR_EVENT_STATUS2.TRIG_TA` G0946 (0x0118[7]): status: TA trigger. From
  `EUR_CR_EVENT_STATUS2_TRIG_TA` (1, sgx545-ce).
- `CR_EVENT_STATUS2.GSG_LOADED` G0940 (0x0118[8]): status: GSG state loaded. From
  `EUR_CR_EVENT_STATUS2_GSG_LOADED` (1, sgx545-ce).
- `CR_EVENT_STATUS2.GSG_FLUSHED` G0939 (0x0118[9]): status: GSG state flushed. From
  `EUR_CR_EVENT_STATUS2_GSG_FLUSHED` (1, sgx545-ce).
- `CR_EVENT_STATUS.DPM_3D_MEM_FREE` G0398 (0x012c[0]): status: DPM finished freeing 3D pages. From
  `EUR_CR_EVENT_STATUS_DPM_3D_MEM_FREE` (1, sgx545-ce).
- `CR_EVENT_STATUS.TPC_FLUSH` G0351 (0x012c[10]): status: tail-pointer cache flush done. From
  `EUR_CR_EVENT_STATUS_TPC_FLUSH` (1, sgx545-ce).
- `CR_EVENT_STATUS.TPC_CLEAR` G0932 (0x012c[11]): status: tail-pointer cache clear done. From
  `EUR_CR_EVENT_STATUS_TPC_CLEAR` (1, sgx545-ce).
- `CR_EVENT_STATUS.TA_TERMINATE` G0404 (0x012c[12]): status: TA terminate done. From
  `EUR_CR_EVENT_STATUS_TA_TERMINATE` (1, sgx545-ce).
- `CR_EVENT_STATUS.TA_FINISHED` G0403 (0x012c[13]): status: TA pass finished. From
  `EUR_CR_EVENT_STATUS_TA_FINISHED` (1, sgx545-ce).
- `CR_EVENT_STATUS.SW_EVENT` G0092 (0x012c[14]): status: software event. From
  `EUR_CR_EVENT_STATUS_SW_EVENT` (1, sgx545-ce).
- `CR_EVENT_STATUS.BREAKPOINT` G0397 (0x012c[15]): status: breakpoint hit. From
  `EUR_CR_EVENT_STATUS_BREAKPOINT` (1, sgx545-ce).
- `CR_EVENT_STATUS.ISP_VISIBILITY_FAIL` G0927 (0x012c[16]): status: ISP visibility-test fail. From
  `EUR_CR_EVENT_STATUS_ISP_VISIBILITY_FAIL` (1, sgx545-ce).
- `CR_EVENT_STATUS.PIXELBE_END_RENDER` G0402 (0x012c[18]): status: pixel back end finished the
  render. From `EUR_CR_EVENT_STATUS_PIXELBE_END_RENDER` (1, sgx545-ce).
- `CR_EVENT_STATUS.OTPM_FLUSHED` G0930 (0x012c[19]): status: OTPM flushed. From
  `EUR_CR_EVENT_STATUS_OTPM_FLUSHED` (1, sgx545-ce).
- `CR_EVENT_STATUS.DPM_OUT_OF_MEMORY_MT` G0400 (0x012c[1]): status: DPM out of memory (macrotile).
  From `EUR_CR_EVENT_STATUS_DPM_OUT_OF_MEMORY_MT` (1, sgx545-ce).
- `CR_EVENT_STATUS.OTPM_INV` G0350 (0x012c[20]): status: OTPM invalidated. From
  `EUR_CR_EVENT_STATUS_OTPM_INV` (1, sgx545-ce).
- `CR_EVENT_STATUS.ISP2_ZLS_CSW_FINISHED` G0349 (0x012c[21]): status: second ISP finished a ZLS
  context switch. From `EUR_CR_EVENT_STATUS_ISP2_ZLS_CSW_FINISHED` (1, sgx545-ce).
- `CR_EVENT_STATUS.DPM_INIT_END` G0347 (0x012c[22]): status: DPM initialisation finished. From
  `EUR_CR_EVENT_STATUS_DPM_INITEND` (1, sgx545-ce).
- `CR_EVENT_STATUS.ISP_END_TILE` G0926 (0x012c[23]): status: ISP finished a tile. From
  `EUR_CR_EVENT_STATUS_ISP_END_TILE` (1, sgx545-ce).
- `CR_EVENT_STATUS.DPM_TA_MEM_FREE` G0925 (0x012c[24]): status: DPM finished freeing TA pages. From
  `EUR_CR_EVENT_STATUS_DPM_TA_MEM_FREE` (1, sgx545-ce).
- `CR_EVENT_STATUS.DPM_OUT_OF_MEMORY_ZLS` G0922 (0x012c[25]): status: DPM out of memory (ZLS). From
  `EUR_CR_EVENT_STATUS_DPM_OUT_OF_MEMORY_ZLS` (1, sgx545-ce).
- `CR_EVENT_STATUS.MADD_CACHE_INVAL_COMPLETE` G0928 (0x012c[26]): status: MADD cache invalidate
  complete. From `EUR_CR_EVENT_STATUS_MADD_CACHE_INVALCOMPLETE` (1, sgx545-ce).
- `CR_EVENT_STATUS.TA_DPM_FAULT` G0931 (0x012c[28]): status: TA hit a DPM fault. From
  `EUR_CR_EVENT_STATUS_TA_DPM_FAULT` (1, sgx545-ce).
- `CR_EVENT_STATUS.TIMER` G0405 (0x012c[29]): status: event timer expired (CR_EVENT_TIMER). From
  `EUR_CR_EVENT_STATUS_TIMER` (1, sgx545-ce).
- `CR_EVENT_STATUS.DPM_OUT_OF_MEMORY_GBL` G0399 (0x012c[2]): status: DPM out of memory (global
  list). From `EUR_CR_EVENT_STATUS_DPM_OUT_OF_MEMORY_GBL` (1, sgx545-ce).
- `CR_EVENT_STATUS.MASTER_INTERRUPT` G0929 (0x012c[31]): status: summary: some enabled event is
  pending. From `EUR_CR_EVENT_STATUS_MASTER_INTERRUPT` (1, sgx545-ce).
- `CR_EVENT_STATUS.DPM_REACHED_MEM_THRESH` G0401 (0x012c[3]): status: DPM page use reached the
  threshold. From `EUR_CR_EVENT_STATUS_DPM_REACHED_MEM_THRESH` (1, sgx545-ce).
- `CR_EVENT_STATUS.DPM_STATE_STORE` G0348 (0x012c[4]): status: DPM state store done. From
  `EUR_CR_EVENT_STATUS_DPM_STATE_STORE` (1, sgx545-ce).
- `CR_EVENT_STATUS.DPM_STATE_LOAD` G0924 (0x012c[5]): status: DPM state load done. From
  `EUR_CR_EVENT_STATUS_DPM_STATE_LOAD` (1, sgx545-ce).
- `CR_EVENT_STATUS.DPM_STATE_CLEAR` G0923 (0x012c[6]): status: DPM state clear done. From
  `EUR_CR_EVENT_STATUS_DPM_STATE_CLEAR` (1, sgx545-ce).
- `CR_EVENT_STATUS.DPM_CONTROL_STORE` G0346 (0x012c[7]): status: DPM control store done. From
  `EUR_CR_EVENT_STATUS_DPM_CONTROL_STORE` (1, sgx545-ce).
- `CR_EVENT_STATUS.DPM_CONTROL_LOAD` G0345 (0x012c[8]): status: DPM control load done. From
  `EUR_CR_EVENT_STATUS_DPM_CONTROL_LOAD` (1, sgx545-ce).
- `CR_EVENT_STATUS.DPM_CONTROL_CLEAR` G0344 (0x012c[9]): status: DPM control clear done. From
  `EUR_CR_EVENT_STATUS_DPM_CONTROL_CLEAR` (1, sgx545-ce).
- `CR_EVENT_HOST_ENABLE.DPM_3D_MEM_FREE` G0878 (0x0130[0]): send to host: DPM finished freeing 3D
  pages. From `EUR_CR_EVENT_HOST_ENABLE_DPM_3D_MEM_FREE` (1, sgx545-ce).
- `CR_EVENT_HOST_ENABLE.TPC_FLUSH` G0905 (0x0130[10]): send to host: tail-pointer cache flush done.
  From `EUR_CR_EVENT_HOST_ENABLE_TPC_FLUSH` (1, sgx545-ce).
- `CR_EVENT_HOST_ENABLE.TPC_CLEAR` G0904 (0x0130[11]): send to host: tail-pointer cache clear done.
  From `EUR_CR_EVENT_HOST_ENABLE_TPC_CLEAR` (1, sgx545-ce).
- `CR_EVENT_HOST_ENABLE.TA_TERMINATE` G0902 (0x0130[12]): send to host: TA terminate done. From
  `EUR_CR_EVENT_HOST_ENABLE_TA_TERMINATE` (1, sgx545-ce).
- `CR_EVENT_HOST_ENABLE.TA_FINISHED` G0901 (0x0130[13]): send to host: TA pass finished. From
  `EUR_CR_EVENT_HOST_ENABLE_TA_FINISHED` (1, sgx545-ce).
- `CR_EVENT_HOST_ENABLE.SW_EVENT` G0899 (0x0130[14]): send to host: software event. From
  `EUR_CR_EVENT_HOST_ENABLE_SW_EVENT` (1, sgx545-ce).
- `CR_EVENT_HOST_ENABLE.BREAKPOINT` G0877 (0x0130[15]): send to host: breakpoint hit. From
  `EUR_CR_EVENT_HOST_ENABLE_BREAKPOINT` (1, sgx545-ce).
- `CR_EVENT_HOST_ENABLE.ISP_VISIBILITY_FAIL` G0893 (0x0130[16]): send to host: ISP visibility-test
  fail. From `EUR_CR_EVENT_HOST_ENABLE_ISP_VISIBILITY_FAIL` (1, sgx545-ce).
- `CR_EVENT_HOST_ENABLE.PIXELBE_END_RENDER` G0898 (0x0130[18]): send to host: pixel back end
  finished the render. From `EUR_CR_EVENT_HOST_ENABLE_PIXELBE_END_RENDER` (1, sgx545-ce).
- `CR_EVENT_HOST_ENABLE.OTPM_FLUSHED` G0896 (0x0130[19]): send to host: OTPM flushed. From
  `EUR_CR_EVENT_HOST_ENABLE_OTPM_FLUSHED` (1, sgx545-ce).
- `CR_EVENT_HOST_ENABLE.DPM_OUT_OF_MEMORY_MT` G0884 (0x0130[1]): send to host: DPM out of memory
  (macrotile). From `EUR_CR_EVENT_HOST_ENABLE_DPM_OUT_OF_MEMORY_MT` (1, sgx545-ce).
- `CR_EVENT_HOST_ENABLE.OTPM_INV` G0897 (0x0130[20]): send to host: OTPM invalidated. From
  `EUR_CR_EVENT_HOST_ENABLE_OTPM_INV` (1, sgx545-ce).
- `CR_EVENT_HOST_ENABLE.ISP2_ZLS_CSW_FINISHED` G0891 (0x0130[21]): send to host: second ISP finished
  a ZLS context switch. From `EUR_CR_EVENT_HOST_ENABLE_ISP2_ZLS_CSW_FINISHED` (1, sgx545-ce).
- `CR_EVENT_HOST_ENABLE.DPM_INIT_END` G0882 (0x0130[22]): send to host: DPM initialisation finished.
  From `EUR_CR_EVENT_HOST_ENABLE_DPM_INITEND` (1, sgx545-ce).
- `CR_EVENT_HOST_ENABLE.ISP_END_TILE` G0892 (0x0130[23]): send to host: ISP finished a tile. From
  `EUR_CR_EVENT_HOST_ENABLE_ISP_END_TILE` (1, sgx545-ce).
- `CR_EVENT_HOST_ENABLE.DPM_TA_MEM_FREE` G0890 (0x0130[24]): send to host: DPM finished freeing TA
  pages. From `EUR_CR_EVENT_HOST_ENABLE_DPM_TA_MEM_FREE` (1, sgx545-ce).
- `CR_EVENT_HOST_ENABLE.DPM_OUT_OF_MEMORY_ZLS` G0885 (0x0130[25]): send to host: DPM out of memory
  (ZLS). From `EUR_CR_EVENT_HOST_ENABLE_DPM_OUT_OF_MEMORY_ZLS` (1, sgx545-ce).
- `CR_EVENT_HOST_ENABLE.MADD_CACHE_INVAL_COMPLETE` G0894 (0x0130[26]): send to host: MADD cache
  invalidate complete. From `EUR_CR_EVENT_HOST_ENABLE_MADD_CACHE_INVALCOMPLETE` (1, sgx545-ce).
- `CR_EVENT_HOST_ENABLE.TA_DPM_FAULT` G0900 (0x0130[28]): send to host: TA hit a DPM fault. From
  `EUR_CR_EVENT_HOST_ENABLE_TA_DPM_FAULT` (1, sgx545-ce).
- `CR_EVENT_HOST_ENABLE.TIMER` G0903 (0x0130[29]): send to host: event timer expired
  (CR_EVENT_TIMER). From `EUR_CR_EVENT_HOST_ENABLE_TIMER` (1, sgx545-ce).
- `CR_EVENT_HOST_ENABLE.DPM_OUT_OF_MEMORY_GBL` G0883 (0x0130[2]): send to host: DPM out of memory
  (global list). From `EUR_CR_EVENT_HOST_ENABLE_DPM_OUT_OF_MEMORY_GBL` (1, sgx545-ce).
- `CR_EVENT_HOST_ENABLE.MASTER_INTERRUPT` G0895 (0x0130[31]): send to host: summary: some enabled
  event is pending. From `EUR_CR_EVENT_HOST_ENABLE_MASTER_INTERRUPT` (1, sgx545-ce).
- `CR_EVENT_HOST_ENABLE.DPM_REACHED_MEM_THRESH` G0886 (0x0130[3]): send to host: DPM page use
  reached the threshold. From `EUR_CR_EVENT_HOST_ENABLE_DPM_REACHED_MEM_THRESH` (1, sgx545-ce).
- `CR_EVENT_HOST_ENABLE.DPM_STATE_STORE` G0889 (0x0130[4]): send to host: DPM state store done. From
  `EUR_CR_EVENT_HOST_ENABLE_DPM_STATE_STORE` (1, sgx545-ce).
- `CR_EVENT_HOST_ENABLE.DPM_STATE_LOAD` G0888 (0x0130[5]): send to host: DPM state load done. From
  `EUR_CR_EVENT_HOST_ENABLE_DPM_STATE_LOAD` (1, sgx545-ce).
- `CR_EVENT_HOST_ENABLE.DPM_STATE_CLEAR` G0887 (0x0130[6]): send to host: DPM state clear done. From
  `EUR_CR_EVENT_HOST_ENABLE_DPM_STATE_CLEAR` (1, sgx545-ce).
- `CR_EVENT_HOST_ENABLE.DPM_CONTROL_STORE` G0881 (0x0130[7]): send to host: DPM control store done.
  From `EUR_CR_EVENT_HOST_ENABLE_DPM_CONTROL_STORE` (1, sgx545-ce).
- `CR_EVENT_HOST_ENABLE.DPM_CONTROL_LOAD` G0880 (0x0130[8]): send to host: DPM control load done.
  From `EUR_CR_EVENT_HOST_ENABLE_DPM_CONTROL_LOAD` (1, sgx545-ce).
- `CR_EVENT_HOST_ENABLE.DPM_CONTROL_CLEAR` G0879 (0x0130[9]): send to host: DPM control clear done.
  From `EUR_CR_EVENT_HOST_ENABLE_DPM_CONTROL_CLEAR` (1, sgx545-ce).
- `CR_EVENT_HOST_CLEAR.DPM_3D_MEM_FREE` G0834 (0x0134[0]): clear: DPM finished freeing 3D pages.
  From `EUR_CR_EVENT_HOST_CLEAR_DPM_3D_MEM_FREE` (1, sgx545-ce).
- `CR_EVENT_HOST_CLEAR.TPC_FLUSH` G0861 (0x0134[10]): clear: tail-pointer cache flush done. From
  `EUR_CR_EVENT_HOST_CLEAR_TPC_FLUSH` (1, sgx545-ce).
- `CR_EVENT_HOST_CLEAR.TPC_CLEAR` G0860 (0x0134[11]): clear: tail-pointer cache clear done. From
  `EUR_CR_EVENT_HOST_CLEAR_TPC_CLEAR` (1, sgx545-ce).
- `CR_EVENT_HOST_CLEAR.TA_TERMINATE` G0858 (0x0134[12]): clear: TA terminate done. From
  `EUR_CR_EVENT_HOST_CLEAR_TA_TERMINATE` (1, sgx545-ce).
- `CR_EVENT_HOST_CLEAR.TA_FINISHED` G0857 (0x0134[13]): clear: TA pass finished. From
  `EUR_CR_EVENT_HOST_CLEAR_TA_FINISHED` (1, sgx545-ce).
- `CR_EVENT_HOST_CLEAR.SW_EVENT` G0855 (0x0134[14]): clear: software event. From
  `EUR_CR_EVENT_HOST_CLEAR_SW_EVENT` (1, sgx545-ce).
- `CR_EVENT_HOST_CLEAR.BREAKPOINT` G0833 (0x0134[15]): clear: breakpoint hit. From
  `EUR_CR_EVENT_HOST_CLEAR_BREAKPOINT` (1, sgx545-ce).
- `CR_EVENT_HOST_CLEAR.ISP_VISIBILITY_FAIL` G0849 (0x0134[16]): clear: ISP visibility-test fail.
  From `EUR_CR_EVENT_HOST_CLEAR_ISP_VISIBILITY_FAIL` (1, sgx545-ce).
- `CR_EVENT_HOST_CLEAR.PIXELBE_END_RENDER` G0854 (0x0134[18]): clear: pixel back end finished the
  render. From `EUR_CR_EVENT_HOST_CLEAR_PIXELBE_END_RENDER` (1, sgx545-ce).
- `CR_EVENT_HOST_CLEAR.OTPM_FLUSHED` G0852 (0x0134[19]): clear: OTPM flushed. From
  `EUR_CR_EVENT_HOST_CLEAR_OTPM_FLUSHED` (1, sgx545-ce).
- `CR_EVENT_HOST_CLEAR.DPM_OUT_OF_MEMORY_MT` G0840 (0x0134[1]): clear: DPM out of memory
  (macrotile). From `EUR_CR_EVENT_HOST_CLEAR_DPM_OUT_OF_MEMORY_MT` (1, sgx545-ce).
- `CR_EVENT_HOST_CLEAR.OTPM_INV` G0853 (0x0134[20]): clear: OTPM invalidated. From
  `EUR_CR_EVENT_HOST_CLEAR_OTPM_INV` (1, sgx545-ce).
- `CR_EVENT_HOST_CLEAR.ISP2_ZLS_CSW_FINISHED` G0847 (0x0134[21]): clear: second ISP finished a ZLS
  context switch. From `EUR_CR_EVENT_HOST_CLEAR_ISP2_ZLS_CSW_FINISHED` (1, sgx545-ce).
- `CR_EVENT_HOST_CLEAR.DPM_INIT_END` G0838 (0x0134[22]): clear: DPM initialisation finished. From
  `EUR_CR_EVENT_HOST_CLEAR_DPM_INITEND` (1, sgx545-ce).
- `CR_EVENT_HOST_CLEAR.ISP_END_TILE` G0848 (0x0134[23]): clear: ISP finished a tile. From
  `EUR_CR_EVENT_HOST_CLEAR_ISP_END_TILE` (1, sgx545-ce).
- `CR_EVENT_HOST_CLEAR.DPM_TA_MEM_FREE` G0846 (0x0134[24]): clear: DPM finished freeing TA pages.
  From `EUR_CR_EVENT_HOST_CLEAR_DPM_TA_MEM_FREE` (1, sgx545-ce).
- `CR_EVENT_HOST_CLEAR.DPM_OUT_OF_MEMORY_ZLS` G0841 (0x0134[25]): clear: DPM out of memory (ZLS).
  From `EUR_CR_EVENT_HOST_CLEAR_DPM_OUT_OF_MEMORY_ZLS` (1, sgx545-ce).
- `CR_EVENT_HOST_CLEAR.MADD_CACHE_INVAL_COMPLETE` G0850 (0x0134[26]): clear: MADD cache invalidate
  complete. From `EUR_CR_EVENT_HOST_CLEAR_MADD_CACHE_INVALCOMPLETE` (1, sgx545-ce).
- `CR_EVENT_HOST_CLEAR.TA_DPM_FAULT` G0856 (0x0134[28]): clear: TA hit a DPM fault. From
  `EUR_CR_EVENT_HOST_CLEAR_TA_DPM_FAULT` (1, sgx545-ce).
- `CR_EVENT_HOST_CLEAR.TIMER` G0859 (0x0134[29]): clear: event timer expired (CR_EVENT_TIMER). From
  `EUR_CR_EVENT_HOST_CLEAR_TIMER` (1, sgx545-ce).
- `CR_EVENT_HOST_CLEAR.DPM_OUT_OF_MEMORY_GBL` G0839 (0x0134[2]): clear: DPM out of memory (global
  list). From `EUR_CR_EVENT_HOST_CLEAR_DPM_OUT_OF_MEMORY_GBL` (1, sgx545-ce).
- `CR_EVENT_HOST_CLEAR.MASTER_INTERRUPT` G0851 (0x0134[31]): clear: summary: some enabled event is
  pending. From `EUR_CR_EVENT_HOST_CLEAR_MASTER_INTERRUPT` (1, sgx545-ce).
- `CR_EVENT_HOST_CLEAR.DPM_REACHED_MEM_THRESH` G0842 (0x0134[3]): clear: DPM page use reached the
  threshold. From `EUR_CR_EVENT_HOST_CLEAR_DPM_REACHED_MEM_THRESH` (1, sgx545-ce).
- `CR_EVENT_HOST_CLEAR.DPM_STATE_STORE` G0845 (0x0134[4]): clear: DPM state store done. From
  `EUR_CR_EVENT_HOST_CLEAR_DPM_STATE_STORE` (1, sgx545-ce).
- `CR_EVENT_HOST_CLEAR.DPM_STATE_LOAD` G0844 (0x0134[5]): clear: DPM state load done. From
  `EUR_CR_EVENT_HOST_CLEAR_DPM_STATE_LOAD` (1, sgx545-ce).
- `CR_EVENT_HOST_CLEAR.DPM_STATE_CLEAR` G0843 (0x0134[6]): clear: DPM state clear done. From
  `EUR_CR_EVENT_HOST_CLEAR_DPM_STATE_CLEAR` (1, sgx545-ce).
- `CR_EVENT_HOST_CLEAR.DPM_CONTROL_STORE` G0837 (0x0134[7]): clear: DPM control store done. From
  `EUR_CR_EVENT_HOST_CLEAR_DPM_CONTROL_STORE` (1, sgx545-ce).
- `CR_EVENT_HOST_CLEAR.DPM_CONTROL_LOAD` G0836 (0x0134[8]): clear: DPM control load done. From
  `EUR_CR_EVENT_HOST_CLEAR_DPM_CONTROL_LOAD` (1, sgx545-ce).
- `CR_EVENT_HOST_CLEAR.DPM_CONTROL_CLEAR` G0835 (0x0134[9]): clear: DPM control clear done. From
  `EUR_CR_EVENT_HOST_CLEAR_DPM_CONTROL_CLEAR` (1, sgx545-ce).
- `CR_TIMER.VALUE` G0964 (0x0144[31:0]): current timer count. From `EUR_CR_TIMER_VALUE` (1,
  sgx545-ce).
- `CR_TE_SCREEN.LAST_TILE_X` G0160 (0x0210 from bit 0 (width open)): x of the screen's last tile, in
  tiles from 0 [infer]. From `CR_TE_SCREEN.LAST_TILE_X` (ours, resgx545).
- `CR_TE_SCREEN.LAST_TILE_Y` G0161 (0x0210 from bit 12 (width open)): y of the screen's last tile,
  in tiles from 0 [infer]. From `CR_TE_SCREEN.LAST_TILE_Y` (ours, resgx545).
- `CR_REG_0400.BITS11_0` G1030 (0x0400[11:0]): inferred reading (unconfirmed): twelve bits the
  register takes (0x80 as the library and the closed stack write them) of which bits 7:0 are the
  threshold of ARGB1555's one-bit alpha (pack mode 4, E385) and change no stored pixel in pack modes
  0 to 3, and bits 11:8 change no stored pixel in pack modes 0 to 4 [infer]. From
  `CR_REG_0400.BITS11_0` (ours, resgx545).
- `CR_REG_0400.INVERT_BYTE3` G0153 (0x0400[25]): inverts the alpha channel of every pixel stored:
  bits 31:24 in ARGB8888 and ABGR8888, bits 7:0 in BGRA8888, nothing in RGB565 (the name keeps the
  first reading, byte 3) [infer]. From `CR_REG_0400.INVERT_BYTE3` (ours, resgx545).
- `CR_ISP_CTL.VALID_ID` G0418 (0x0414[5:0]): validation threshold: opaque and translucent objects
  whose ISP1.VALID_ID is below it are not drawn (Rogue analogue). From `ROGUE_CR_ISP_CTL_VALID_ID`
  (3, linux-imagination).
- `CR_ISP_MSAA.MODE` G0123 (0x042c[1:0]): multisample mode: 0 one sample, byte 0 of
  CR_ISP_MULTISAMPLECTL; 1 two samples a pixel stored side by side in x, bytes 0 and 1 [infer: their
  source read from mode 2]; 2 four stored as a 2x2 block, samples 0 to 3 of CR_ISP_MULTISAMPLECTL in
  byte order; 3 hangs. From `CR_ISP_MSAA.MODE` (ours, resgx545).
- `CR_ISP_MSAA.ENABLE` G0122 (0x042c[31]): enables the multisampled ISP path: with it clear and
  CR_ISP_MSAA.MODE at 2 no pixel of the triangle is written; the triangle is still tiled (the
  parameter buffer and TA data are those of the bit set) and mode 1 stores nothing either; what it
  does at mode 0 with other bits set is not shown; set in every capture [infer]. From
  `CR_ISP_MSAA.ENABLE` (ours, resgx545).
- `CR_ISP_BGOBJVALS.STENCIL` G0623 (0x04bc[7:0]): the background's stencil value, which an object's
  stencil test compares against (with bit 8 set) [infer]. From `CR_ISP_BGOBJVALS.STENCIL` (ours,
  resgx545).
- `CR_ISP_MULTISAMPLECTL.SAMPLE1_X` G1053 (0x04c8[11:8]): x of sample 1's position in the pixel, in
  sixteenths of a pixel [infer]. From `CR_ISP_MULTISAMPLECTL.SAMPLE1_X` (ours, resgx545).
- `CR_ISP_MULTISAMPLECTL.SAMPLE1_Y` G1054 (0x04c8[15:12]): y of sample 1's position in the pixel, in
  sixteenths of a pixel [infer]. From `CR_ISP_MULTISAMPLECTL.SAMPLE1_Y` (ours, resgx545).
- `CR_ISP_MULTISAMPLECTL.SAMPLE2_X` G1055 (0x04c8[19:16]): x of sample 2's position in the pixel, in
  sixteenths of a pixel [infer]. From `CR_ISP_MULTISAMPLECTL.SAMPLE2_X` (ours, resgx545).
- `CR_ISP_MULTISAMPLECTL.SAMPLE2_Y` G1056 (0x04c8[23:20]): y of sample 2's position in the pixel, in
  sixteenths of a pixel [infer]. From `CR_ISP_MULTISAMPLECTL.SAMPLE2_Y` (ours, resgx545).
- `CR_ISP_MULTISAMPLECTL.SAMPLE3_X` G1057 (0x04c8[27:24]): x of sample 3's position in the pixel, in
  sixteenths of a pixel [infer]. From `CR_ISP_MULTISAMPLECTL.SAMPLE3_X` (ours, resgx545).
- `CR_ISP_MULTISAMPLECTL.SAMPLE3_Y` G1058 (0x04c8[31:28]): y of sample 3's position in the pixel, in
  sixteenths of a pixel [infer]. From `CR_ISP_MULTISAMPLECTL.SAMPLE3_Y` (ours, resgx545).
- `CR_ISP_MULTISAMPLECTL.SAMPLE0_X` G0125 (0x04c8[3:0]): x of sample 0's position in the pixel, in
  sixteenths of a pixel, 8 the centre [infer]. From `CR_ISP_MULTISAMPLECTL.SAMPLE0_X` (ours,
  resgx545).
- `CR_ISP_MULTISAMPLECTL.SAMPLE0_Y` G0126 (0x04c8[7:4]): y of sample 0's position in the pixel, in
  sixteenths of a pixel, 8 the centre [infer]. From `CR_ISP_MULTISAMPLECTL.SAMPLE0_Y` (ours,
  resgx545).
- `CR_DPM_TA_PAGE_COUNTS.LOCAL` G0620 (0x0638[15:0]): local pages of the TA's PB [infer]. From
  `CR_DPM_TA_PAGE_COUNTS.LOCAL` (ours, resgx545).
- `CR_DPM_TA_PAGE_COUNTS.GLOBAL` G0619 (0x0638[31:16]): global pages of the TA's PB [infer]. From
  `CR_DPM_TA_PAGE_COUNTS.GLOBAL` (ours, resgx545).
- `CR_DPM_3D_PAGE_COUNTS.LOCAL` G0618 (0x0660[15:0]): local pages of the 3D's PB [infer]. From
  `CR_DPM_3D_PAGE_COUNTS.LOCAL` (ours, resgx545).
- `CR_DPM_3D_PAGE_COUNTS.GLOBAL` G0617 (0x0660[31:16]): global pages of the 3D's PB [infer]. From
  `CR_DPM_3D_PAGE_COUNTS.GLOBAL` (ours, resgx545).
- `CR_DPM_TA_ALLOC_FREE_LIST_STATUS1.HEAD` G1083 (0x0700[15:0]): the head page of the TA side's free
  list, the next page the DPM hands out; while the TA runs, one above the pages it has taken. From
  `CR_DPM_TA_ALLOC_FREE_LIST_STATUS1.HEAD` (ours, resgx545).
- `CR_DPM_TA_ALLOC_FREE_LIST_STATUS1.TAIL` G1084 (0x0700[31:16]): the tail page of the TA side's
  free list: each page the 3D frees is appended there, so after a job it is the last page freed.
  From `CR_DPM_TA_ALLOC_FREE_LIST_STATUS1.TAIL` (ours, resgx545).
- `CR_DPM_3D_FREE_LIST_STATUS1.HEAD` G1077 (0x070c[15:0]): the head page of the 3D side's free list,
  the next page the DPM hands out; while the TA runs, one above the pages it has taken. From
  `CR_DPM_3D_FREE_LIST_STATUS1.HEAD` (ours, resgx545).
- `CR_DPM_3D_FREE_LIST_STATUS1.TAIL` G1078 (0x070c[31:16]): the tail page of the 3D side's free
  list: each page the 3D frees is appended there, so after a job it is the last page freed. From
  `CR_DPM_3D_FREE_LIST_STATUS1.TAIL` (ours, resgx545).
- `CR_DPM_TA_ALLOC_FREE_LIST_STATUS2.PREV` G1085 (0x0710[15:0]): the page before the tail of the TA
  side's free list (the PB descriptor's dpm_ta_alloc holds it shifted into its high half); bits
  31:16 read 0 in every sample. From `CR_DPM_TA_ALLOC_FREE_LIST_STATUS2.PREV` (ours, resgx545).
- `CR_DPM_3D_FREE_LIST_STATUS2.PREV` G1079 (0x071c[15:0]): the page before the tail of the 3D side's
  free list (the PB descriptor's dpm_ta_alloc holds it shifted into its high half); bits 31:16 read
  0 in every sample. From `CR_DPM_3D_FREE_LIST_STATUS2.PREV` (ours, resgx545).
- `CR_TPU_LUMA_KEY_ALPHA.THRESHOLD` G1034 (0x0868[15:8]): the high end of the luma band; a luma
  above it takes alpha_above [infer]. From `CR_TPU_LUMA_KEY_ALPHA.THRESHOLD` (ours, resgx545).
- `CR_TPU_LUMA_KEY_ALPHA.BELOW` G1032 (0x0868[23:16]): the alpha written for a luma inside the band
  [infer]. From `CR_TPU_LUMA_KEY_ALPHA.BELOW` (ours, resgx545).
- `CR_TPU_LUMA_KEY_ALPHA.ABOVE` G1031 (0x0868[31:24]): the alpha written for a luma outside the
  band, below or above it [infer]. From `CR_TPU_LUMA_KEY_ALPHA.ABOVE` (ours, resgx545).
- `CR_TPU_LUMA_KEY_ALPHA.LOW` G1033 (0x0868[7:0]): the low end of the luma band: a pixel whose luma
  lies from it to CR_TPU_LUMA_KEY_ALPHA.THRESHOLD takes alpha_below [infer]. From
  `CR_TPU_LUMA_KEY_ALPHA.LOW` (ours, resgx545).
- `CR_USE_CODE_BASE_0.ADDR` G0006 (0x0a0c[24:0]): code base address. From `_PSB_CUC_BASE_ADDR_MASK`
  (1c, emgd-psb_regs).
- `CR_USE_CODE_BASE_0.DM` G0007 (0x0a0c[26:25]): data master that owns a USE code base. From
  `EUR_CR_USE_CODE_BASE_DM_00` (1, sgx545-ce); `_PSB_CUC_BASE_DM_MASK` (1c, emgd-psb_regs).
- `CR_USE_COEFFS_MODE.MODE` G0204 (0x0a9c[1:0]): 0: a fixed bank of H.264 and MPEG-4 interpolation
  filters for sets 2-5; 1: VC-1's bicubic filters; 2: smoothing filters (sets 4, 5) and zero-sum
  difference filters (sets 2, 3); 3: set 2 loaded, sets 3-5 zero [infer]. From
  `CR_USE_COEFFS_MODE.MODE` (ours, resgx545).
- `CR_PDS_EXEC_BASE.ADDR` G0952 (0x0ab8[31:20]): PDS program base, top 12 bits (1 MB aligned). From
  `EUR_CR_PDS_EXEC_BASE_ADDR` (1, sgx545-ce).
- `CR_PDS_REG_0ABC.BITS4_1` G0150 (0x0abc[4:1]): inferred reading (unconfirmed): the number of PDS
  task slots shared by every data master (E140): 0 leaves none, so every job hangs. Measured: 7 from
  the init script; 0 hangs the next job, any other value changes nothing seen [infer]. From
  `CR_PDS_REG_0ABC.BITS4_1` (ours, resgx545).
- `CR_EVENT_KICKER.ADDRESS` G0921 (0x0ac4[31:4]): address the event kicker reads (16-byte aligned).
  From `EUR_CR_EVENT_KICKER_ADDRESS` (1, sgx545-ce).
- `CR_EVENT_KICK.NOW` G0091 (0x0ac8[0]): write 1 to trigger. From `EUR_CR_EVENT_KICK_NOW` (1,
  sgx545-ce).
- `CR_EVENT_TIMER.VALUE` G0950 (0x0acc[23:0]): timer period when written; read back, the count,
  which moves while the timer runs. From `EUR_CR_EVENT_TIMER_VALUE` (1, sgx545-ce);
  `_PSB_CE_TIMER_VALUE_MASK` (1c, emgd-psb_regs).
- `CR_EVENT_TIMER.ENABLE` G0949 (0x0acc[24]): enable the event timer. From
  `EUR_CR_EVENT_TIMER_ENABLE` (1, sgx545-ce).
- `CR_PDS_INV0.DSC` G0954 (0x0ad0[0]): invalidate this PDS data cache. From `EUR_CR_PDS_INV0_DSC`
  (1, sgx545-ce).
- `CR_PDS_INV1.DSC` G0956 (0x0ad4[0]): invalidate this PDS data cache. From `EUR_CR_PDS_INV1_DSC`
  (1, sgx545-ce).
- `CR_PDS_INV_CSC.KICK` G0958 (0x0ae0[0]): invalidate the PDS code cache. From
  `EUR_CR_PDS_INV_CSC_KICK` (1, sgx545-ce).
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
- `CR_BIF_CTRL.NO_REORDER` G0766 (0x0c00[0]): disable memory request reordering. From
  `EUR_CR_BIF_CTRL_NOREORDER` (1, sgx545-ce).
- `CR_BIF_CTRL.MMU_BYPASS_TE` G0762 (0x0c00[10]): bypass MMU translation for TE requests. From
  `EUR_CR_BIF_CTRL_MMU_BYPASS_TE` (1, sgx545-ce).
- `CR_BIF_CTRL.MMU_BYPASS_PBE` G0761 (0x0c00[11]): bypass MMU translation for PBE requests. From
  `EUR_CR_BIF_CTRL_MMU_BYPASS_PBE` (1, sgx545-ce).
- `CR_BIF_CTRL.MMU_BYPASS_TSPP` G0763 (0x0c00[12]): bypass MMU translation for TSP parameter fetch
  requests. From `EUR_CR_BIF_CTRL_MMU_BYPASS_TSPP` (1, sgx545-ce).
- `CR_BIF_CTRL.MMU_BYPASS_ISP` G0760 (0x0c00[13]): bypass MMU translation for ISP requests. From
  `EUR_CR_BIF_CTRL_MMU_BYPASS_ISP` (1, sgx545-ce).
- `CR_BIF_CTRL.MMU_BYPASS_USE` G0764 (0x0c00[14]): bypass MMU translation for USSE requests. From
  `EUR_CR_BIF_CTRL_MMU_BYPASS_USE` (1, sgx545-ce).
- `CR_BIF_CTRL.MMU_BYPASS_HOST` G0759 (0x0c00[15]): bypass MMU translation for host requests. From
  `EUR_CR_BIF_CTRL_MMU_BYPASS_HOST` (1, sgx545-ce).
- `CR_BIF_CTRL.PAUSE` G0767 (0x0c00[1]): pause MMU requests. From `EUR_CR_BIF_CTRL_PAUSE` (1,
  sgx545-ce).
- `CR_BIF_CTRL.FLUSH` G0756 (0x0c00[2]): flush the MMU caches. From `EUR_CR_BIF_CTRL_FLUSH` (1,
  sgx545-ce).
- `CR_BIF_CTRL.INVAL_DC` G0757 (0x0c00[3]): invalidate the MMU directory cache. From
  `EUR_CR_BIF_CTRL_INVALDC` (1, sgx545-ce).
- `CR_BIF_CTRL.CLEAR_FAULT` G0755 (0x0c00[4]): clear the latched MMU fault. From
  `EUR_CR_BIF_CTRL_CLEAR_FAULT` (1, sgx545-ce).
- `CR_BIF_CTRL.MMU_BYPASS_CACHE` G0758 (0x0c00[8]): bypass MMU translation for cache requests. From
  `EUR_CR_BIF_CTRL_MMU_BYPASS_CACHE` (1, sgx545-ce).
- `CR_BIF_CTRL.MMU_BYPASS_VDM` G0765 (0x0c00[9]): bypass MMU translation for VDM requests. From
  `EUR_CR_BIF_CTRL_MMU_BYPASS_VDM` (1, sgx545-ce).
- `CR_BIF_INT_STAT.FAULT_REQ` G0772 (0x0c04[15:0]): requestors that faulted. From
  `EUR_CR_BIF_INT_STAT_FAULT_REQ` (1, sgx545-ce).
- `CR_BIF_INT_STAT.FAULT_TYPE` G0773 (0x0c04[18:16]): fault type. From
  `EUR_CR_BIF_INT_STAT_FAULT_TYPE` (1, sgx545-ce).
- `CR_BIF_INT_STAT.FLUSH_COMPLETE` G0774 (0x0c04[19]): MMU flush complete. From
  `EUR_CR_BIF_INT_STAT_FLUSH_COMPLETE` (1, sgx545-ce).
- `CR_BIF_FAULT.ADDR` G0771 (0x0c08[31:12]): faulting page address. From `EUR_CR_BIF_FAULT_ADDR` (1,
  sgx545-ce).
- `CR_BIF_FAULT.CID` G0342 (0x0c08[3:0]): directory-list index (context) of the fault. From
  `EUR_CR_BIF_FAULT_CID` (1, sgx545-ce).
- `CR_BIF_FAULT.SB` G0343 (0x0c08[8:4]): SB bits of the fault (meaning open). From
  `EUR_CR_BIF_FAULT_SB` (1, sgx545-ce).
- `CR_BIF_DIR_LIST_BASE1.ADDR` G0769 (0x0c38[31:8]): page-directory address. From
  `EUR_CR_BIF_DIR_LIST_BASE1_ADDR` (1, sgx545-ce).
- `CR_BIF_DIR_LIST_BASE15.ADDR` G0770 (0x0c70[31:8]): page-directory address. From
  `EUR_CR_BIF_DIR_LIST_BASE15_ADDR` (1, sgx545-ce).
- `CR_BIF_BANK_SET.SELECT_2D` G0749 (0x0c74[0]): bank register used by 2D core requests. From
  `EUR_CR_BIF_BANK_SET_SELECT_2D` (1, sgx545-ce).
- `CR_BIF_BANK_SET.SELECT_3D` G0750 (0x0c74[3:2]): bank register used by 3D requests. From
  `EUR_CR_BIF_BANK_SET_SELECT_3D` (1, sgx545-ce).
- `CR_BIF_BANK_SET.SELECT_HOST` G0753 (0x0c74[4]): bank register used by host requests. From
  `EUR_CR_BIF_BANK_SET_SELECT_HOST` (1, sgx545-ce).
- `CR_BIF_BANK_SET.SELECT_TA` G0754 (0x0c74[7:6]): bank register used by TA requests. From
  `EUR_CR_BIF_BANK_SET_SELECT_TA` (1, sgx545-ce).
- `CR_BIF_BANK_SET.SELECT_EDM` G0752 (0x0c74[8]): bank register used by EDM requests. From
  `EUR_CR_BIF_BANK_SET_SELECT_EDM` (1, sgx545-ce).
- `CR_BIF_BANK_SET.SELECT_DPM_LSS` G0751 (0x0c74[9]): bank register used by DPM load/store requests.
  From `EUR_CR_BIF_BANK_SET_SELECT_DPM_LSS` (1, sgx545-ce).
- `CR_BIF_BANK0.INDEX_HOST` G0747 (0x0c78[11:8]): directory-list index for host requests. From
  `EUR_CR_BIF_BANK0_INDEX_HOST` (1, sgx545-ce).
- `CR_BIF_BANK0.INDEX_3D` G0088 (0x0c78[15:12]): directory-list index for 3D requests. From
  `EUR_CR_BIF_BANK0_INDEX_3D` (1, sgx545-ce).
- `CR_BIF_BANK0.INDEX_2D` G0745 (0x0c78[19:16]): directory-list index for 2D core requests. From
  `EUR_CR_BIF_BANK0_INDEX_2D` (1, sgx545-ce).
- `CR_BIF_BANK0.INDEX_EDM` G0746 (0x0c78[3:0]): directory-list index for EDM requests. From
  `EUR_CR_BIF_BANK0_INDEX_EDM` (1, sgx545-ce).
- `CR_BIF_BANK0.INDEX_TA` G0748 (0x0c78[7:4]): directory-list index for TA requests. From
  `EUR_CR_BIF_BANK0_INDEX_TA` (1, sgx545-ce).
- `CR_BIF_DIR_LIST_BASE0.ADDR` G0768 (0x0c84[31:8]): page-directory address. From
  `EUR_CR_BIF_DIR_LIST_BASE0_ADDR` (1, sgx545-ce).
- `CR_BIF_TA_REQ_BASE.ADDR` G0775 (0x0c90[31:20]): heap base for these requests (top 12 bits). From
  `EUR_CR_BIF_TA_REQ_BASE_ADDR` (1, sgx545-ce).
- `CR_BIF_3D_REQ_BASE.ADDR` G0744 (0x0cac[31:20]): heap base for these requests (top 12 bits). From
  `EUR_CR_BIF_3D_REQ_BASE_ADDR` (1, sgx545-ce).
- `CR_BIF_ZLS_REQ_BASE.ADDR` G0777 (0x0cb0[31:20]): heap base for these requests (top 12 bits). From
  `EUR_CR_BIF_ZLS_REQ_BASE_ADDR` (1, sgx545-ce).
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

- `CR_SOFT_RESET.BIF_RESET` G0959 (0x0080[0]): hold the BIF (MMU) in reset. From
  `_PSB_CS_RESET_BIF_RESET` (1c, emgd-psb_regs).
- `CR_SOFT_RESET.DPM_RESET` G0960 (0x0080[1]): hold the DPM in reset. From `_PSB_CS_RESET_DPM_RESET`
  (1c, emgd-psb_regs).
- `CR_SOFT_RESET.TA_RESET` G0439 (0x0080[2]): hold the TA in reset. From `_PSB_CS_RESET_TA_RESET`
  (1c, emgd-psb_regs).
- `CR_SOFT_RESET.USE_RESET` G0963 (0x0080[3]): hold the USSE in reset. From
  `_PSB_CS_RESET_USE_RESET` (1c, emgd-psb_regs).
- `CR_SOFT_RESET.ISP_RESET` G0961 (0x0080[4]): hold the ISP in reset. From `_PSB_CS_RESET_ISP_RESET`
  (1c, emgd-psb_regs).
- `CR_SOFT_RESET.TSP_RESET` G0962 (0x0080[5]): hold the TSP in reset. From `_PSB_CS_RESET_TSP_RESET`
  (1c, emgd-psb_regs).
- `CR_EVENT_STATUS2.DPM_TA_FREE_LOAD` G0938 (0x0118[0]): status: DPM TA free-list load done. From
  `_PSB_CE_DPM_TA_FREE_LOAD` (1c, emgd-psb_regs).
- `CR_EVENT_STATUS2.DPM_3D_FREE_LOAD` G0935 (0x0118[1]): status: DPM 3D free-list load done. From
  `_PSB_CE_DPM_3D_FREE_LOAD` (1c, emgd-psb_regs).
- `CR_EVENT_STATUS2.DPM_HOST_FREE_LOAD` G0937 (0x0118[2]): status: DPM host free-list load done.
  From `_PSB_CE_DPM_HOST_FREE_LOAD` (1c, emgd-psb_regs).
- `CR_EVENT_STATUS2.DPM_DHOST_FREE_LOAD` G0936 (0x0118[3]): status: DPM host-deallocation free-list
  load done. From `_PSB_CE_DPM_DHOST_FREE_LOAD` (1c, emgd-psb_regs).
- `CR_EVENT_STATUS2.TRIG_DL` G0945 (0x0118[5]): status: DL trigger. From `PSB_TRIG_DL` (1c,
  emgd-psb_regs).
- `CR_EVENT_STATUS2.TRIG_3D` G0944 (0x0118[6]): status: 3D trigger. From `PSB_TRIG_3D` (1c,
  emgd-psb_regs).
- `CR_EVENT_STATUS2.TRIG_TA` G0946 (0x0118[7]): status: TA trigger. From `PSB_TRIG_TA` (1c,
  emgd-psb_regs).
- `CR_EVENT_STATUS.TA_TERMINATE` G0404 (0x012c[12]): status: TA terminate done (Rogue analogue).
  From `ROGUE_CR_EVENT_STATUS_TA_TERMINATE` (3, linux-imagination).
- `CR_EVENT_STATUS.TA_FINISHED` G0403 (0x012c[13]): status: TA pass finished (Rogue analogue). From
  `ROGUE_CR_EVENT_STATUS_TA_FINISHED` (3, linux-imagination).
- `CR_EVENT_STATUS.PIXELBE_END_RENDER` G0402 (0x012c[18]): status: pixel back end finished the
  render (Rogue analogue). From `ROGUE_CR_EVENT_STATUS_PIXELBE_END_RENDER` (3, linux-imagination).
- `CR_EVENT_HOST_CLEAR.DPM_3D_MEM_FREE` G0834 (0x0134[0]): clear: DPM finished freeing 3D pages.
  From `_PSB_CE_DPM_3D_MEM_FREE` (1c, emgd-psb_regs).
- `CR_EVENT_HOST_CLEAR.TPC_FLUSH` G0861 (0x0134[10]): clear: tail-pointer cache flush done. From
  `_PSB_CE_TPC_FLUSH` (1c, emgd-psb_regs).
- `CR_EVENT_HOST_CLEAR.TPC_CLEAR` G0860 (0x0134[11]): clear: tail-pointer cache clear done. From
  `_PSB_CE_TPC_CLEAR` (1c, emgd-psb_regs).
- `CR_EVENT_HOST_CLEAR.TA_TERMINATE` G0858 (0x0134[12]): clear: TA terminate done. From
  `_PSB_CE_TA_TERMINATE` (1c, emgd-psb_regs).
- `CR_EVENT_HOST_CLEAR.TA_FINISHED` G0857 (0x0134[13]): clear: TA pass finished. From
  `_PSB_CE_TA_FINISHED` (1c, emgd-psb_regs).
- `CR_EVENT_HOST_CLEAR.SW_EVENT` G0855 (0x0134[14]): clear: software event. From `_PSB_CE_SW_EVENT`
  (1c, emgd-psb_regs).
- `CR_EVENT_HOST_CLEAR.BREAKPOINT` G0833 (0x0134[15]): clear: breakpoint hit. From
  `_PSB_CE_BREAKPOINT` (1c, emgd-psb_regs).
- `CR_EVENT_HOST_CLEAR.ISP_VISIBILITY_FAIL` G0849 (0x0134[16]): clear: ISP visibility-test fail.
  From `_PSB_CE_ISP_VISIBILITY_FAIL` (1c, emgd-psb_regs).
- `CR_EVENT_HOST_CLEAR.PIXELBE_END_RENDER` G0854 (0x0134[18]): clear: pixel back end finished the
  render. From `_PSB_CE_PIXELBE_END_RENDER` (1c, emgd-psb_regs).
- `CR_EVENT_HOST_CLEAR.OTPM_FLUSHED` G0852 (0x0134[19]): clear: OTPM flushed. From
  `_PSB_CE_OTPM_FLUSHED` (1c, emgd-psb_regs).
- `CR_EVENT_HOST_CLEAR.DPM_OUT_OF_MEMORY_MT` G0840 (0x0134[1]): clear: DPM out of memory
  (macrotile). From `_PSB_CE_DPM_OUT_OF_MEMORY_MT` (1c, emgd-psb_regs).
- `CR_EVENT_HOST_CLEAR.OTPM_INV` G0853 (0x0134[20]): clear: OTPM invalidated. From
  `_PSB_CE_OTPM_INV` (1c, emgd-psb_regs).
- `CR_EVENT_HOST_CLEAR.DPM_INIT_END` G0838 (0x0134[22]): clear: DPM initialisation finished. From
  `_PSB_CE_DPM_INITEND` (1c, emgd-psb_regs).
- `CR_EVENT_HOST_CLEAR.ISP_END_TILE` G0848 (0x0134[23]): clear: ISP finished a tile. From
  `_PSB_CE_ISP_END_TILE` (1c, emgd-psb_regs).
- `CR_EVENT_HOST_CLEAR.DPM_TA_MEM_FREE` G0846 (0x0134[24]): clear: DPM finished freeing TA pages.
  From `_PSB_CE_DPM_TA_MEM_FREE` (1c, emgd-psb_regs).
- `CR_EVENT_HOST_CLEAR.DPM_OUT_OF_MEMORY_ZLS` G0841 (0x0134[25]): clear: DPM out of memory (ZLS).
  From `_PSB_CE_DPM_OUT_OF_MEMORY_ZLS` (1c, emgd-psb_regs).
- `CR_EVENT_HOST_CLEAR.MADD_CACHE_INVAL_COMPLETE` G0850 (0x0134[26]): clear: MADD cache invalidate
  complete. From `_PSB_CE_MADD_CACHE_INVALCOMPLETE` (1c, emgd-psb_regs).
- `CR_EVENT_HOST_CLEAR.TA_DPM_FAULT` G0856 (0x0134[28]): clear: TA hit a DPM fault. From
  `_PSB_CE_TA_DPM_FAULT` (1c, emgd-psb_regs).
- `CR_EVENT_HOST_CLEAR.TIMER` G0859 (0x0134[29]): clear: event timer expired (CR_EVENT_TIMER). From
  `_PSB_CE_TIMER` (1c, emgd-psb_regs).
- `CR_EVENT_HOST_CLEAR.DPM_OUT_OF_MEMORY_GBL` G0839 (0x0134[2]): clear: DPM out of memory (global
  list). From `_PSB_CE_DPM_OUT_OF_MEMORY_GBL` (1c, emgd-psb_regs).
- `CR_EVENT_HOST_CLEAR.MASTER_INTERRUPT` G0851 (0x0134[31]): clear: summary: some enabled event is
  pending. From `_PSB_CE_MASTER_INTERRUPT` (1c, emgd-psb_regs).
- `CR_EVENT_HOST_CLEAR.DPM_REACHED_MEM_THRESH` G0842 (0x0134[3]): clear: DPM page use reached the
  threshold. From `_PSB_CE_DPM_REACHED_MEM_THRESH` (1c, emgd-psb_regs).
- `CR_EVENT_HOST_CLEAR.DPM_STATE_STORE` G0845 (0x0134[4]): clear: DPM state store done. From
  `_PSB_CE_DPM_STATE_STORE` (1c, emgd-psb_regs).
- `CR_EVENT_HOST_CLEAR.DPM_STATE_LOAD` G0844 (0x0134[5]): clear: DPM state load done. From
  `_PSB_CE_DPM_STATE_LOAD` (1c, emgd-psb_regs).
- `CR_EVENT_HOST_CLEAR.DPM_STATE_CLEAR` G0843 (0x0134[6]): clear: DPM state clear done. From
  `_PSB_CE_DPM_STATE_CLEAR` (1c, emgd-psb_regs).
- `CR_EVENT_HOST_CLEAR.DPM_CONTROL_STORE` G0837 (0x0134[7]): clear: DPM control store done. From
  `_PSB_CE_DPM_CONTROL_STORE` (1c, emgd-psb_regs).
- `CR_EVENT_HOST_CLEAR.DPM_CONTROL_LOAD` G0836 (0x0134[8]): clear: DPM control load done. From
  `_PSB_CE_DPM_CONTROL_LOAD` (1c, emgd-psb_regs).
- `CR_EVENT_HOST_CLEAR.DPM_CONTROL_CLEAR` G0835 (0x0134[9]): clear: DPM control clear done. From
  `_PSB_CE_DPM_CONTROL_CLEAR` (1c, emgd-psb_regs).
- `CR_ISP_BGOBJVALS.BGTAG_ENABLE` G0622 (0x04bc[9]): draw the background object (its tag on every
  pixel); clear, the target keeps its old pixels [infer]. From `CR_ISP_BGOBJVALS.BGTAG_ENABLE`
  (ours, resgx545).
- `CR_TPU_YUV_CSC_INPUT.Y_NO_OFFSET` G0177 (0x0848[0]): the luma taken as is, without the -16 offset
  [infer]. From `CR_TPU_YUV_CSC_INPUT.Y_NO_OFFSET` (ours, resgx545).
- `CR_TPU_YUV_CSC_INPUT.UV_SIGNED` G0176 (0x0848[2]): U and V taken as signed bytes instead of
  offset by 128 [infer]. From `CR_TPU_YUV_CSC_INPUT.UV_SIGNED` (ours, resgx545).
- `CR_EVENT_TIMER.ENABLE` G0949 (0x0acc[24]): enable the event timer. From `_PSB_CE_TIMER_ENABLE`
  (1c, emgd-psb_regs).
- `CR_PDS_INV_CSC.KICK` G0958 (0x0ae0[0]): invalidate the PDS code cache. From `_PSB_CPI_CSC_KICK`
  (1c, emgd-psb_regs).
- `CR_BIF_CTRL.FLUSH` G0756 (0x0c00[2]): flush the MMU caches. From `_PSB_CB_CTRL_FLUSH` (1c,
  emgd-psb_regs).
- `CR_BIF_CTRL.INVAL_DC` G0757 (0x0c00[3]): invalidate the MMU directory cache. From
  `_PSB_CB_CTRL_INVALDC` (1c, emgd-psb_regs).
- `CR_BIF_CTRL.CLEAR_FAULT` G0755 (0x0c00[4]): clear the latched MMU fault. From
  `_PSB_CB_CTRL_CLEAR_FAULT` (1c, emgd-psb_regs).

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
- `CR_EVENT_STATUS2` G0933 (0x0118): event status, bank 2. From `EUR_CR_EVENT_STATUS2` (1,
  sgx545-ce); `PSB_CR_EVENT_STATUS2` (1c, emgd-psb_regs).
- `CR_EVENT_STATUS` G0049 (0x012c): event (interrupt) status, bank 1. From `EUR_CR_EVENT_STATUS` (1,
  sgx545-ce); `PSB_CR_EVENT_STATUS` (1c, emgd-psb_regs); `PSB_EUR_CR_EVENT_STATUS` (1c,
  emgd-psb_regs); `ROGUE_CR_EVENT_STATUS` (3, linux-imagination).
- `CR_EVENT_HOST_ENABLE` G0044 (0x0130): events routed to the host interrupt, bank 1. From
  `EUR_CR_EVENT_HOST_ENABLE` (1, sgx545-ce); `PSB_EUR_CR_EVENT_HOST_ENABLE` (1c, emgd-psb_regs).
- `CR_EVENT_HOST_CLEAR` G0042 (0x0134): write-1-to-clear events, bank 1. From
  `EUR_CR_EVENT_HOST_CLEAR` (1, sgx545-ce); `PSB_CR_EVENT_HOST_CLEAR` (1c, emgd-psb_regs);
  `ROGUE_CR_EVENT_CLEAR` (3, linux-imagination).
- `CR_PDS_CACHE_STATUS` G0951 (0x0138): PDS cache invalidate status. From `PSB_CR_PDS_CACHE_STATUS`
  (1c, emgd-psb_regs).
- `CR_PDS_CACHE_HOST_ENABLE` G0051 (0x013c): PDS cache event host enable. From
  `PSB_CR_PDS_CACHE_HOST_ENABLE` (1c, emgd-psb_regs).
- `CR_PDS_CACHE_HOST_CLEAR` G0429 (0x0140): clear PDS cache invalidate status. From
  `PSB_CR_PDS_CACHE_HOST_CLEAR` (1c, emgd-psb_regs).
- `CR_TIMER` G0053 (0x0144): free-running timer. From `EUR_CR_TIMER` (1, sgx545-ce);
  `ROGUE_CR_TIMER` (3, linux-imagination).
- `CR_REG_0148` G0151 (0x0148): inferred reading (unconfirmed): a one-bit (bit 0) per-job mode of
  the 3D and transfer paths for a feature these clients leave off: no value changes a triangle, five
  copies, a fill or a copy. Measured: per-render word the host supplies with the 3D registers
  (transfer command and render details); 0 in captures [infer]. From `CR_REG_0148` (ours, resgx545).
- `CR_VDM_START` G0459 (0x0200): starts the VDM (TA) pass. From `PSB_CR_VDM_START` (1c,
  emgd-psb_regs).
- `CR_TE_AA` G0158 (0x0204): tiling-engine anti-aliasing word: 0x20000000 in every single-sample
  capture, bits 31 and 30 more (0xe0000000) with 4x multisampling [infer]. From `ROGUE_CR_TE_AA` (3,
  linux-imagination); `ROGUE_CR_TE_AA` (3, mesa-csbgen).
- `CR_TE_MTILE1` G0448 (0x0208): macrotile boundaries in X (Rogue analogue). From
  `ROGUE_CR_TE_MTILE1` (3, mesa-csbgen); `configuration registers defining the macro-tile
  boundaries` (4, patent-US8669987).
- `CR_TE_MTILE2` G0449 (0x020c): macrotile boundaries in Y (Rogue analogue). From
  `ROGUE_CR_TE_MTILE2` (3, mesa-csbgen); `configuration registers defining the macro-tile
  boundaries` (4, patent-US8669987).
- `CR_TE_SCREEN` G0159 (0x0210): screen size in tiles for the tiling engine (Rogue analogue). From
  `ROGUE_CR_TE_SCREEN` (3, linux-imagination); `ROGUE_CR_TE_SCREEN` (3, mesa-csbgen).
- `CR_TE_MACROTILE_STRIDE` G0447 (0x0214): inferred reading (unconfirmed): macrotile stride of the
  tiling engine, from the TA command (0x10 for 64x64) [infer]. From `CR_TE_MACROTILE_STRIDE` (ours,
  resgx545).
- `CR_TE_PSG` G0450 (0x0218): tiling-engine control word: bit 22 set on the kick that ends the scene
  (with the word at 0 the job faults), bit 21 makes the TA mark every target region header
  (REGION_HDR.FLAGS bit 29), bit 25 with a depth/stencil buffer (Rogue analogue). From
  `ROGUE_CR_TE_PSG` (3, mesa-csbgen).
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
  bit 25 inverts the alpha channel of every pixel stored, wherever the pack mode puts it
  (CR_REG_0400.INVERT_BYTE3); bits 7:0 are the threshold of the one-bit alpha of ARGB1555 (pack mode
  4) and change no pixel in pack modes 0 to 3, bits 11:8 change no pixel in modes 0 to 4 (E385),
  0x80 the default of the other conversions. Measured: per-render word from the render details or
  transfer command; 0x80 in captures [infer]. From `CR_REG_0400` (ours, resgx545).
- `CR_ISP_RENDER` G0624 (0x0404): render control: mode, direction, resume (Rogue analogue). From
  `ROGUE_CR_ISP_RENDER` (3, linux-imagination); `ROGUE_CR_ISP_RENDER` (3, mesa-csbgen).
- `CR_ISP_REGION_HEADER_BASE` G0420 (0x0408): address of the region headers (or fast-2D stream) the
  ISP renders, relative to CR_BIF_3D_REQ_BASE [infer]. From `CR_ISP_REGION_HEADER_BASE` (ours,
  resgx545).
- `CR_ISP_CTL` G0119 (0x0414): ISP control word of a render; the EDM sets bit 8 (process empty
  tiles) for partial renders (Rogue analogue). From `ROGUE_CR_ISP_CTL` (3, linux-imagination).
- `CR_ISP_LINE_SAMPLE_POS` G0120 (0x0418): bit 0: where a line's span test samples a column x, x +
  1/2 at 1 and x + 1 at 0, its rows taken at the pixel centre at both values, read from one x-major
  line; triangles do not read it; 1 from the closed driver [infer]. From `CR_ISP_LINE_SAMPLE_POS`
  (ours, resgx545).
- `CR_ISP_POLY_OFFSET_UNITS` G0129 (0x041c): the polygon offset's units, as an integer
  (glPolygonOffset units) [infer]. From `CR_ISP_POLY_OFFSET_UNITS` (ours, resgx545).
- `CR_ISP_POLY_OFFSET_FACTOR` G0128 (0x0420): inferred reading (unconfirmed): the polygon offset's
  factor, an IEEE single (glPolygonOffset factor) [infer]. From `CR_ISP_POLY_OFFSET_FACTOR` (ours,
  resgx545).
- `CR_ISP_POLY_OFFSET_CLAMP` G0127 (0x0424): the polygon offset's clamp, an IEEE single: the offset
  is capped at it, 0 no cap, a negative one leaving positive offsets alone [infer]. From
  `CR_ISP_POLY_OFFSET_CLAMP` (ours, resgx545).
- `CR_ISP_START_RENDER` G0425 (0x0428): starts the 3D render. From `PSB_CR_ISP_START_RENDER` (1c,
  emgd-psb_regs).
- `CR_ISP_MSAA` G0121 (0x042c): ISP multisample control: bits 1:0 the mode (CR_ISP_MSAA.MODE), bit
  31 the multisample path's enable (CR_ISP_MSAA.ENABLE) [infer]. From `CR_ISP_MSAA` (ours,
  resgx545).
- `CR_TSP_PARAMETER_CACHE` G0965 (0x043c): TSP parameter cache invalidate. From
  `PSB_CR_TSP_PARAMETER_CACHE` (1c, emgd-psb_regs).
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
- `CR_ISP_VISIBILITY_CTRL` G0141 (0x0494): visibility-test control: the 3D kick writes 0xff to it
  before each render [infer]. From `CR_ISP_VISIBILITY_CTRL` (ours, resgx545).
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
- `CR_ISP_VISIBILITY_COUNT5` G0625 (0x04ac): visibility counters 10 and 11, one per 16-bit half,
  accumulated by the EDM into the visibility results [infer]. From `CR_ISP_VISIBILITY_COUNT5` (ours,
  resgx545).
- `CR_ISP_VISIBILITY_COUNT6` G0626 (0x04b0): visibility counters 12 and 13, one per 16-bit half,
  accumulated by the EDM into the visibility results [infer]. From `CR_ISP_VISIBILITY_COUNT6` (ours,
  resgx545).
- `CR_ISP_VISIBILITY_COUNT7` G0140 (0x04b4): visibility counters 14 and 15, one per 16-bit half,
  accumulated by the EDM into the visibility results [infer]. From `CR_ISP_VISIBILITY_COUNT7` (ours,
  resgx545).
- `CR_ISP_BGOBJDEPTH` G0118 (0x04b8): background object depth (Rogue analogue). From
  `ROGUE_CR_ISP_BGOBJDEPTH` (3, mesa-csbgen).
- `CR_ISP_BGOBJVALS` G0621 (0x04bc): background object values (Rogue: bit 9 background tag enable,
  bit 8 mask, 7:0 stencil); the 3D kick and the transfer path load it from their commands. From
  `ROGUE_CR_ISP_BGOBJVALS` (3, mesa-csbgen).
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
- `CR_ISP_REG_04E8` G0131 (0x04e8): inferred reading (unconfirmed): what it does is not shown: no
  value tried changes an image or a count in any scene; not the background's stencil or mask (E216);
  0x100 from the init script and per render [infer]. From `CR_ISP_REG_04E8` (ours, resgx545).
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
  samples (these four and the four of CR_ISP_MULTISAMPLECTL) predicts every image pixel for pixel;
  not used to place the samples of a multisampled render; under 4x three values give one image; 0
  from the closed driver [infer]. From `CR_ISP_SAMPLE_POS` (ours, resgx545).
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
- `CR_DPM_CONTEXT_PB_BASE` G0827 (0x0664): parameter-buffer base of the DPM context. From
  `EUR_CR_DPM_CONTEXT_PB_BASE` (1, intel-ctp-santos10).
- `CR_DPM_PDS_THRESHOLD` G0377 (0x0668): PDS page threshold of the parameter buffer, from the PB
  descriptor [infer]. From `CR_DPM_PDS_THRESHOLD` (ours, resgx545).
- `CR_DPM_STATE_BASE1` G0381 (0x0674): DPM context state table address (second register of two): set
  at the start of a partial render to the RT data's state page, CR_DPM_STATE_BASE0's value, and kept
  until the next partial render; not the place CR_DPM_REG_074C bit 8 reaches [infer]. From
  `CR_DPM_STATE_BASE1` (ours, resgx545).
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
- `CR_DPM_TA_ALLOC_FREE_LIST_STATUS1` G0831 (0x0700): DPM TA allocation free-list status, word 1.
  From `EUR_CR_DPM_TA_ALLOC_FREE_LIST_STATUS1` (1, intel-ctp-santos10).
- `CR_DPM_3D_FREE_LIST_STATUS1` G0825 (0x070c): DPM 3D free-list status, word 1. From
  `EUR_CR_DPM_3D_FREE_LIST_STATUS1` (1, intel-ctp-santos10).
- `CR_DPM_TA_ALLOC_FREE_LIST_STATUS2` G0832 (0x0710): DPM TA allocation free-list status, word 2.
  From `EUR_CR_DPM_TA_ALLOC_FREE_LIST_STATUS2` (1, intel-ctp-santos10).
- `CR_DPM_3D_FREE_LIST_STATUS2` G0826 (0x071c): DPM 3D free-list status, word 2. From
  `EUR_CR_DPM_3D_FREE_LIST_STATUS2` (1, intel-ctp-santos10).
- `CR_DPM_ABORT_STATUS_MTILE` G0371 (0x0720): DPM macrotile abort status: the macrotile the DPM
  aborts, numbered down then across, read as the TA stops for a partial render [infer]. From
  `EUR_CR_DPM_ABORT_STATUS_MTILE` (1, intel-ctp-santos10).
- `CR_DPM_PAGE_STATUS` G0375 (0x0724): DPM pages in use: total and TA. From `EUR_CR_DPM_PAGE_STATUS`
  (1, intel-ctp-santos10); `PSB_CR_DPM_PAGE_STATUS` (1c, emgd-psb_regs).
- `CR_DPM_PAGE` G0829 (0x0728): DPM page register: while a 3D frees pages it holds the pages still
  held, as CR_DPM_PAGE_STATUS does, counting down to 0 (to 1, the global list's page, in a partial
  render). From `EUR_CR_DPM_PAGE` (1, intel-ctp-santos10).
- `CR_DPM_GLOBAL_PAGE_STATUS` G0828 (0x072c): DPM global-list pages: total and TA. From
  `EUR_CR_DPM_GLOBAL_PAGE_STATUS` (1, intel-ctp-santos10); `PSB_CR_DPM_GLOBAL_PAGE_STATUS` (1c,
  emgd-psb_regs).
- `CR_DPM_REG_0730` G1080 (0x0730): inferred reading (unconfirmed): the 3D side's global page count:
  1 while the 3D holds the global page, from the first render or partial render of a job until the
  final render frees its last page, the TA's runs between partial renders included; 0 otherwise
  [infer]. From `CR_DPM_REG_0730` (ours, resgx545).
- `CR_DPM_REQUESTING` G0830 (0x0734): DPM requests pending. From `EUR_CR_DPM_REQUESTING` (1,
  intel-ctp-santos10).
- `CR_DPM_REG_0738` G1081 (0x0738): inferred reading (unconfirmed): a DPM flag that reads 1 when no
  render runs and 0 from a render's (or a partial render's) start to its end [infer]. From
  `CR_DPM_REG_0738` (ours, resgx545).
- `CR_DPM_3D_RT_INDEX` G0370 (0x073c): render target index of the render, for render-target arrays
  [infer]. From `CR_DPM_3D_RT_INDEX` (ours, resgx545).
- `CR_DPM_REG_0748` G1082 (0x0748): inferred reading (unconfirmed): a DPM state word: 0x1f idle and
  from the last TA's end, 0xf while the TA holds pages and through a partial render, 0x7 in some
  samples while the TA takes pages, the 1024x768 abort among them; its bits one by one are not shown
  [infer]. From `CR_DPM_REG_0748` (ours, resgx545).
- `CR_DPM_REG_074C` G0378 (0x074c): inferred reading (unconfirmed): the enable (bit 8) of a DPM
  access near offset 0x6010 of the context's TA-data space, fixed whatever CR_DPM_STATE_BASE1 holds;
  with that place mapped the job is unchanged; off in every client. Measured: TA command word; 0 in
  captures [infer]. From `CR_DPM_REG_074C` (ours, resgx545).
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
  copy's luma-key mode on, a luma band and two alphas: bits 7:0 its low end and bits 15:8 its high
  end (the threshold), alpha_below (bits 23:16) for a luma inside the band and alpha_above (bits
  31:24) outside it; it starts at 0xff008000 (a band of 0 to 128, alpha 0 inside, 0xff outside).
  From `CR_TPU_LUMA_KEY_ALPHA` (ours, resgx545).
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
- `CR_EVENT_PIXEL_PDS_INFO` G0396 (0x0a64): info word of the pixel-event task (Rogue:
  shared-register and temp sizes). From `ROGUE_CR_EVENT_PIXEL_PDS_INFO` (3, mesa-csbgen).
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
- `CR_USE0_DM_SLOT` G0966 (0x0aa4): USSE 0 data-master slot allocation. From `PSB_CR_USE0_DM_SLOT`
  (1c, emgd-psb_regs).
- `CR_USE1_DM_SLOT` G0967 (0x0aa8): USSE 1 data-master slot allocation. From `PSB_CR_USE1_DM_SLOT`
  (1c, emgd-psb_regs).
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
- `CR_PDS_INV0` G0953 (0x0ad0): invalidate PDS data cache 0. From `EUR_CR_PDS_INV0` (1, sgx545-ce);
  `PSB_CR_PDS_INV0` (1c, emgd-psb_regs).
- `CR_PDS_INV1` G0955 (0x0ad4): invalidate PDS data cache 1. From `EUR_CR_PDS_INV1` (1, sgx545-ce);
  `PSB_CR_PDS_INV1` (1c, emgd-psb_regs).
- `CR_PDS_INV_CSC` G0957 (0x0ae0): invalidate PDS code cache. From `EUR_CR_PDS_INV_CSC` (1,
  sgx545-ce); `PSB_CR_PDS_INV_CSC` (1c, emgd-psb_regs).
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
- `CR_BIF_ZLS_REQ_BASE` G0776 (0x0cb0): ZLS requestor base address. From `EUR_CR_BIF_ZLS_REQ_BASE`
  (1, sgx545-ce).
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
- `CMD.TA` G0614 (aui32HostKickAddr[0] = 0x11d): kernel CCB command 0: kick a TA (and its 3D) from a
  render context. From `SGXMKIF_CMD_TA` (1, sgx545-ce).
- `CMD.TRANSFER` G0615 (aui32HostKickAddr[1] = 0x103): kernel CCB command 1: kick a transfer from a
  transfer context. From `SGXMKIF_CMD_TRANSFER` (1, sgx545-ce).
- `CMD.2D` G0609 (aui32HostKickAddr[2] = 0 (none)): kernel CCB command 2: 2D blit (no handler in the
  SGX545 firmware). From `SGXMKIF_CMD_2D` (1, sgx545-ce).
- `CMD.POWER` G0613 (aui32HostKickAddr[3] = 0xd4): kernel CCB command 3: power request (POWER.*).
  From `SGXMKIF_CMD_POWER` (1, sgx545-ce).
- `CMD.CONTEXT_SUSPEND` G0611 (aui32HostKickAddr[4] = 0xeb): kernel CCB command 4: suspend or resume
  a context (CONTEXT_SUSPEND.*). From `SGXMKIF_CMD_CONTEXTSUSPEND` (1, sgx545-ce).
- `CMD.CLEANUP` G0610 (aui32HostKickAddr[5] = 0x13a): kernel CCB command 5: release a firmware
  object (CLEANUP.*). From `SGXMKIF_CMD_CLEANUP` (1, sgx545-ce).
- `CMD.GET_MISC_INFO` G0612 (aui32HostKickAddr[6] = 0x173): kernel CCB command 6: fill the misc-info
  buffer. From `SGXMKIF_CMD_GETMISCINFO` (1, sgx545-ce).
- `CMD.SET_HWPERF_STATUS` G0356 (aui32HostKickAddr[9]): kernel CCB command 9: set the HWPerf status.
  From `SGXMKIF_CMD_SETHWPERFSTATUS` (1, sgx545-ce).

### field

- `hw_render_context_dev_vaddr` G1142: device address of the registered render context. From
  `sHWRenderContextDevVAddr` (1, sgx545-ce).
- `pb_block.first_page` G0593: inferred reading (unconfirmed): a PB block's third word: the closed
  client and our kernel both hold the PB descriptor's own address there; how the page-table builder
  uses it is a reading [infer]. From `pb_block.first_page` (ours, resgx545).
- `pb_block.next_block_dev_vaddr` G0560: next block of the descriptor's block list (0 = last)
  [infer]. From `pb_block.next_block_dev_vaddr` (ours, resgx545).
- `pb_block.page_count` G0561: pages in this PB block [infer]. From `pb_block.page_count` (ours,
  resgx545).
- `pb_block.stack_top` G1115: inferred reading (unconfirmed): head (15:0) and tail (31:16) page of
  this PB block [infer]. From `pb_block.stack_top` (ours, resgx545).
- `ta3d_ctl.hw_pb_desc_3d` G0563: PB descriptor loaded in the 3D. From `s3DHWPBDesc` (1c,
  emgd-linux).
- `ta3d_ctl.hw_pb_desc_ta` G0564: PB descriptor loaded in the TA. From `sTAHWPBDesc` (1c,
  emgd-linux).
- `ccb_ctl.write_offset` G0097 (CCB_CTL+0x0): write offset (host advances). From `ui32WriteOffset`
  (1, sgx545-ce).
- `ccb_ctl.read_offset` G0096 (CCB_CTL+0x4): read offset (EDM advances). From `ui32ReadOffset` (1,
  sgx545-ce).
- `cmd_ta.size` G0654 (CMDTA+0x000): TA command word 0, the command's size: when the kick is done
  the TA queue step adds it to the context's CCB read offset [infer]. From `cmd_ta.size` (ours,
  resgx545).
- `cmd_ta.geom_flags` G0648 (CMDTA+0x004): TA command word 1, the TA's flags (GEOM_FLAGS.*), which
  the TA pick and the TA kick test [infer]. From `cmd_ta.geom_flags` (ours, resgx545).
- `cmd_ta.pds_bgnd` G0512 (CMDTA+0x008): background object words [3]: dwords 0-2 of the background
  object, the first a pixel PDS reference; copied to the render details' pds_bgnd at the TA kick.
  From `pds_bgnd` (3, linux-imagination).
- `cmd_ta.num_vertex_partitions` G0510 (CMDTA+0x014): DMS_CTRL vertex partitions, pre-shifted. From
  `NumVertexPartitions` (2, cdv-libsrv_um).
- `cmd_ta.frag_flags` G0303 (CMDTA+0x01c): fragment (3D) flags: depth/stencil buffer present,
  visibility results (FRAG_FLAGS.*). From `flags` (3, linux-imagination).
- `cmd_ta.frame_num` G0566 (CMDTA+0x020): frame number. From `ui32FrameNum` (1, intel-ctp-k900);
  `frame_num` (3, linux-imagination); `cmd_ta.frame_num` (ours, resgx545).
- `cmd_ta.hw_pb_desc_dev_vaddr` G0649 (CMDTA+0x024): PB descriptor of the kick. From
  `sHWPBDescDevVAddr` (1, sgx545-ce); `cmd_ta.hw_pb_desc_dev_vaddr` (ours, resgx545).
- `cmd_ta.ta_threshold` G0514 (CMDTA+0x028): new TA threshold. From `TAThreshold` (2,
  cdv-libsrv_um); `cmd_ta.ta_threshold` (ours, resgx545).
- `cmd_ta.zls_threshold` G0662 (CMDTA+0x02c): new ZLS threshold. From `ZLSThreshold` (2,
  cdv-libsrv_um); `cmd_ta.zls_threshold` (ours, resgx545).
- `cmd_ta.global_threshold` G0506 (CMDTA+0x030): new global threshold. From `GlobalThreshold` (2,
  cdv-libsrv_um); `cmd_ta.global_threshold` (ours, resgx545).
- `cmd_ta.pds_threshold` G0652 (CMDTA+0x034): new PDS threshold. From `PDSThreshold` (2,
  cdv-libsrv_um); `cmd_ta.pds_threshold` (ours, resgx545).
- `cmd_ta.hw_render_details_dev_vaddr` G0507 (CMDTA+0x038): render details of the kick; the EDM
  records it and writes it into the RT data's hw_render_details_dev_vaddr [infer]. From
  `cmd_ta.hw_render_details_dev_vaddr` (ours, resgx545).
- `cmd_ta.dst_sync_list_dev_vaddr` G0647 (CMDTA+0x03c): TA command word 15, the destination sync
  list: the TA pick tests it complete and the TA kick copies it to render details word 56 [infer].
  From `cmd_ta.dst_sync_list_dev_vaddr` (ours, resgx545).
- `cmd_ta.hw_rt_data_set_dev_vaddr` G1101 (CMDTA+0x040): RT data set. From `sHWRTDataSetDevAddr` (1,
  intel-ctp-k900); `hwrt_data_fw_addr` (3, linux-imagination); `cmd_ta.hw_rt_data_set_dev_vaddr`
  (ours, resgx545).
- `cmd_ta.hw_rt_data_dev_vaddr` G0508 (CMDTA+0x044): RT data used by this kick. From
  `sHWRTDataDevAddr` (1, intel-ctp-k900).
- `cmd_ta.z_rt_stride` G0568 (CMDTA+0x04c): inferred reading (unconfirmed): TA command word 19,
  copied by the TA kick to render details word 70, the depth stride per render target [infer]. From
  `cmd_ta.z_rt_stride` (ours, resgx545).
- `cmd_ta.stencil_rt_stride` G0567 (CMDTA+0x050): inferred reading (unconfirmed): TA command word
  20, copied by the TA kick to render details word 71, the stencil stride per render target [infer].
  From `cmd_ta.stencil_rt_stride` (ours, resgx545).
- `cmd_ta.num_patches_3d` G0509 (CMDTA+0x054): count of {address, value} pairs in the TA command's
  patches_3d [infer]. From `cmd_ta.num_patches_3d` (ours, resgx545).
- `cmd_ta.shared` G0513 (CMDTA+0x058): embedded cmd_ta_shared block; the kick passes its client-CCB
  offset in ccb_kick.ccb_offset. From `ui32CCBOffset` (1, sgx545-ce).
- `cmd_ta.te_aa` G0515 (CMDTA+0x238): value the EDM loads into CR_TE_AA (0x0204): 0x20000000, bits
  31 and 30 more with 4x multisampling [infer]. From `cmd_ta.te_aa` (ours, resgx545).
- `cmd_ta.te_mtile1` G0656 (CMDTA+0x23c): macrotile X boundaries. From `te_mtile1` (3,
  linux-imagination).
- `cmd_ta.te_mtile2` G0657 (CMDTA+0x240): macrotile Y boundaries. From `te_mtile2` (3,
  linux-imagination).
- `cmd_ta.te_screen` G0316 (CMDTA+0x244): screen size in tiles. From `te_screen` (3,
  linux-imagination).
- `cmd_ta.te_macrotile_stride` G0655 (CMDTA+0x248): inferred reading (unconfirmed): TA command word
  146, which the TA kick writes to CR_TE_MACROTILE_STRIDE (0x0214); its reading is the register's
  [infer]. From `cmd_ta.te_macrotile_stride` (ours, resgx545).
- `cmd_ta.te_psg` G0658 (CMDTA+0x24c): TE control word (Rogue: carries the end-of-scene bit). From
  `te_psg` (3, linux-imagination).
- `cmd_ta.vdm_ctrl_stream_base` G0661 (CMDTA+0x250): VDM control stream of the kick. From
  `vdm_ctrl_stream_base` (3, linux-imagination).
- `cmd_ta.mte_ctrl` G0650 (CMDTA+0x254): MTE control: the TA kick loads this word into CR_MTE_CTRL
  (0x023c). From `EUR_CR_MTE_CTRL` (1c, openpvrsgx-1.9).
- `cmd_ta.te_psgregion_addr` G0659 (CMDTA+0x258): TA command word 150, which the TA kick writes to
  CR_TE_PSGREGION_ADDR (0x021c) [infer]. From `cmd_ta.te_psgregion_addr` (ours, resgx545).
- `cmd_ta.te_tpc_addr` G0660 (CMDTA+0x25c): TA command word 151, which the TA kick writes to
  CR_TE_TPC_ADDR (0x0220) [infer]. From `cmd_ta.te_tpc_addr` (ours, resgx545).
- `cmd_ta.mte_rhw_min` G0305 (CMDTA+0x260): the TA command's word the EDM loads into CR_MTE_RHW_MIN
  (0x0240) [infer]. From `cmd_ta.mte_rhw_min` (ours, resgx545).
- `cmd_ta.mte_rhw_clamp` G0304 (CMDTA+0x264): the TA command's word the EDM loads into
  CR_MTE_RHW_CLAMP (0x0244) [infer]. From `cmd_ta.mte_rhw_clamp` (ours, resgx545).
- `cmd_ta.ppp_screen` G0653 (CMDTA+0x268): screen size in pixels minus one (x 15:0, y 31:16); the
  EDM copies it into CR_PPP_SCREEN. From `ROGUE_CR_PPP_SCREEN` (3, mesa-csbgen); `cmd_ta.ppp_screen`
  (ours, resgx545).
- `cmd_ta.use_reg_0a04` G0317 (CMDTA+0x26c): inferred reading (unconfirmed): as CR_USE_REG_0A04's:
  the USSE's context store/resume state base (a 16-byte address) for an interrupted TA's vertex
  tasks. Measured: value the EDM copies verbatim into CR_USE_REG_0A04 (0x0a04); 0 in every capture
  [infer]. From `cmd_ta.use_reg_0a04` (ours, resgx545).
- `cmd_ta.use_reg_0aa0` G0318 (CMDTA+0x270): inferred reading (unconfirmed): as CR_USE_REG_0AA0's: a
  USSE resume task word for an interrupted TA's vertex tasks. Measured: value the EDM copies
  verbatim into CR_USE_REG_0AA0 (0x0aa0); 0 in every capture [infer]. From `cmd_ta.use_reg_0aa0`
  (ours, resgx545).
- `cmd_ta.bif_ta_req_base` G0646 (CMDTA+0x274): TA requestor base (parameter heap). From
  `EUR_CR_BIF_TA_REQ_BASE` (1, sgx545-ce).
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
- `cmd_ta.mte_multisamplectl` G0651 (CMDTA+0x2a4): value the EDM copies verbatim into
  CR_MTE_MULTISAMPLECTL (0x0230): the sample positions on the TA side, the same value as
  CR_ISP_MULTISAMPLECTL (0x88, 0xeaa26e26 with 4x multisampling) [infer]. From
  `cmd_ta.mte_multisamplectl` (ours, resgx545).
- `cmd_ta.patches_3d` G0511 (CMDTA+0x2a8): {address, value} memory writes the EDM applies at the TA
  kick, *address = value: patches to the render details (depth/stencil bases, ZLS control) [infer].
  From `cmd_ta.patches_3d` (ours, resgx545).
- `cmd_ta_shared.ctrl_flags` G0666 (CMDTA_SHARED+0x000 (CMDTA+0x058)): CMD_TA_CTRL_FLAGS.*; READY is
  set last by the kernel. From `ui32CtrlFlags` (1, sgx545-ce).
- `cmd_ta_shared.num_status_vals_ta` G0669 (CMDTA_SHARED+0x004 (CMDTA+0x05c)): count of
  sCtlTAStatusInfo. From `ui32NumTAStatusVals` (1, sgx545-ce).
- `cmd_ta_shared.num_status_vals_3d` G0668 (CMDTA_SHARED+0x008 (CMDTA+0x060)): count of
  sCtl3DStatusInfo. From `ui32Num3DStatusVals` (1, sgx545-ce).
- `cmd_ta_shared.tq_sync_ta_write_ops_pending_val` G0679 (CMDTA_SHARED+0x00c (CMDTA+0x064)): TA-side
  TQ sync: write pending value. From `ui32TATQSyncWriteOpsPendingVal` (1, sgx545-ce).
- `cmd_ta_shared.tq_sync_ta_write_ops_complete_dev_vaddr` G0678 (CMDTA_SHARED+0x010 (CMDTA+0x068)):
  TA-side TQ sync: write-complete address. From `sTATQSyncWriteOpsCompleteDevVAddr` (1, sgx545-ce).
- `cmd_ta_shared.tq_sync_ta_read_ops_pending_val` G0677 (CMDTA_SHARED+0x014 (CMDTA+0x06c)): TA-side
  TQ sync: read pending value. From `ui32TATQSyncReadOpsPendingVal` (1, sgx545-ce).
- `cmd_ta_shared.tq_sync_ta_read_ops_complete_dev_vaddr` G0676 (CMDTA_SHARED+0x018 (CMDTA+0x070)):
  TA-side TQ sync: read-complete address. From `sTATQSyncReadOpsCompleteDevVAddr` (1, sgx545-ce).
- `cmd_ta_shared.tq_sync_3d_write_ops_pending_val` G0675 (CMDTA_SHARED+0x01c (CMDTA+0x074)): 3D-side
  TQ sync: write pending value. From `ui323DTQSyncWriteOpsPendingVal` (1, sgx545-ce).
- `cmd_ta_shared.tq_sync_3d_write_ops_complete_dev_vaddr` G0674 (CMDTA_SHARED+0x020 (CMDTA+0x078)):
  3D-side TQ sync: write-complete address. From `s3DTQSyncWriteOpsCompleteDevVAddr` (1, sgx545-ce).
- `cmd_ta_shared.tq_sync_3d_read_ops_pending_val` G0673 (CMDTA_SHARED+0x024 (CMDTA+0x07c)): 3D-side
  TQ sync: read pending value. From `ui323DTQSyncReadOpsPendingVal` (1, sgx545-ce).
- `cmd_ta_shared.tq_sync_3d_read_ops_complete_dev_vaddr` G0672 (CMDTA_SHARED+0x028 (CMDTA+0x080)):
  3D-side TQ sync: read-complete address. From `s3DTQSyncReadOpsCompleteDevVAddr` (1, sgx545-ce).
- `cmd_ta_shared.num_src_syncs` G0667 (CMDTA_SHARED+0x02c (CMDTA+0x084)): source sync count. From
  `ui32NumSrcSyncs` (1, sgx545-ce).
- `cmd_ta_shared.src_syncs` G0670 (CMDTA_SHARED+0x030 (CMDTA+0x088)): source syncs [8]. From
  `asSrcSyncs` (1, sgx545-ce).
- `cmd_ta_shared.ta3d_dependency` G0671 (CMDTA_SHARED+0x0b0 (CMDTA+0x108)): TA->3D dependency sync.
  From `sTA3DDependency` (1, sgx545-ce).
- `cmd_ta_shared.ctl_status_info_ta` G0665 (CMDTA_SHARED+0x0c0 (CMDTA+0x118)): status updates at TA
  end [32]. From `sCtlTAStatusInfo` (1, sgx545-ce).
- `cmd_ta_shared.ctl_status_info_3d` G0664 (CMDTA_SHARED+0x1c0 (CMDTA+0x218)): status updates at
  render end [4]. From `sCtl3DStatusInfo` (1, sgx545-ce).
- `command.service_address` G0100 (COMMAND+0x00): EDM handler address (aui32HostKickAddr[type]).
  From `ui32ServiceAddress` (1, sgx545-ce).
- `command.cache_control` G0098 (COMMAND+0x04): CACHE_CONTROL.* invalidations done before the
  command. From `ui32CacheControl` (1, sgx545-ce).
- `command.data` G0099 (COMMAND+0x08): six command words; [1] = context/data address. From
  `ui32Data` (1, sgx545-ce).
- `dpm_state.mtile_lists` G1091 (DPM_STATE+0x000): the page lists of the sixteen macrotiles, two
  dwords each (DPM_STATE_LIST), the macrotiles numbered down then across. From
  `dpm_state.mtile_lists` (ours, resgx545).
- `dpm_state.global_list` G1090 (DPM_STATE+0x080): the global list's two dwords (DPM_STATE_LIST):
  one page, page 1, the first page of a job on a fresh table, which the 3D frees last [infer:
  global]. From `dpm_state.global_list` (ours, resgx545).
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
- `hw_pb_desc.pb_flags` G0680 (HWPBDESC+0x000): PB descriptor word 0, its flags (PB_FLAGS.*): bit 0
  asks for the page table to be rebuilt and bit 1 for the thresholds to be reloaded; the routines
  clear both [infer]. From `hw_pb_desc.pb_flags` (ours, resgx545).
- `hw_pb_desc.page_count` G1102 (HWPBDESC+0x004): the number of pages of the parameter buffer. From
  `hw_pb_desc.page_count` (ours, resgx545).
- `hw_pb_desc.initial_stack_top` G0523 (HWPBDESC+0x008): initial free-list head/tail (tail << 16 |
  head); PB_FLAGS.INIT_PAGE_TABLE resets the PB descriptor's current_stack_top from it [infer]. From
  `hw_pb_desc.initial_stack_top` (ours, resgx545).
- `hw_pb_desc.initial_dpm_ta_alloc` G0522 (HWPBDESC+0x00c): initial value of the PB descriptor's
  dpm_ta_alloc (the page before the tail << 16) [infer]. From `hw_pb_desc.initial_dpm_ta_alloc`
  (ours, resgx545).
- `hw_pb_desc.page_table_base` G0572 (HWPBDESC+0x010): PB descriptor word 4, the page-table base
  (low 4 bits ignored): loaded into 0x0618 (TA) or 0x0600 (3D), and the base of the page-table
  builder's stores [infer]. From `hw_pb_desc.page_table_base` (ours, resgx545).
- `hw_pb_desc.allocated_page_count` G0518 (HWPBDESC+0x014): pages allocated. From
  `allocated_page_count` (3, linux-imagination).
- `hw_pb_desc.current_stack_top` G0519 (HWPBDESC+0x018): current free list head/tail. From
  `current_stack_top` (3, linux-imagination).
- `hw_pb_desc.dpm_ta_alloc` G0520 (HWPBDESC+0x01c): current allocation word: the EDM loads it into
  CR_DPM_TA_ALLOC (the 3D's matching register for the 3D) and stores the status back [infer]. From
  `hw_pb_desc.dpm_ta_alloc` (ours, resgx545).
- `hw_pb_desc.local_page_count` G0571 (HWPBDESC+0x020): PB descriptor word 8, the local page count:
  loaded into 0x0638 (TA, low half) or 0x0660 (3D), stored back from the status registers, zeroed
  when the table is rebuilt [infer]. From `hw_pb_desc.local_page_count` (ours, resgx545).
- `hw_pb_desc.global_page_count` G0570 (HWPBDESC+0x024): PB descriptor word 9, the global page
  count: loaded into the high half of 0x0638 (TA) or into 0x0660 (3D), stored back, zeroed when the
  table is rebuilt [infer]. From `hw_pb_desc.global_page_count` (ours, resgx545).
- `hw_pb_desc.ta_threshold` G0525 (HWPBDESC+0x028): TA page threshold. From `TAThreshold` (2,
  cdv-libsrv_um); `hw_pb_desc.ta_threshold` (ours, resgx545).
- `hw_pb_desc.zls_threshold` G0526 (HWPBDESC+0x02c): ZLS page threshold. From `ZLSThreshold` (2,
  cdv-libsrv_um).
- `hw_pb_desc.global_threshold` G0521 (HWPBDESC+0x030): global page threshold. From
  `GlobalThreshold` (2, cdv-libsrv_um); `hw_pb_desc.global_threshold` (ours, resgx545).
- `hw_pb_desc.pds_threshold` G0524 (HWPBDESC+0x034): PDS page threshold. From `PDSThreshold` (2,
  cdv-libsrv_um).
- `hw_pb_desc.first_block_dev_vaddr` G0569 (HWPBDESC+0x038): PB descriptor word 14, the address of
  the first PB block, whose list the page-table builder walks [infer]. From
  `hw_pb_desc.first_block_dev_vaddr` (ours, resgx545).
- `hw_render_context.context_flags` G0681 (HWRENDERCONTEXT+0x000): render context word 0, its flags
  (CONTEXT_FLAGS.*): the TA kick clears bit 0, the TA pick and the 3D scheduling skip a context with
  bit 4, the context cleanup tests bit 5 [infer]. From `hw_render_context.context_flags` (ours,
  resgx545).
- `hw_render_context.priority` G0530 (HWRENDERCONTEXT+0x004): scheduling priority. From
  `ui32OffsetOfPriorityField` (1, sgx545-ce); `priority` (3, linux-imagination).
- `hw_render_context.pd_dev_paddr` G1105 (HWRENDERCONTEXT+0x008): page-directory physical address
  (kernel writes). From `ui32OffsetToPDDevPAddr` (1, sgx545-ce); `hw_render_context.pd_dev_paddr`
  (ours, resgx545).
- `hw_render_context.ccb_base_dev_vaddr` G0573 (HWRENDERCONTEXT+0x00c): render context word 3, the
  base of the context's client CCB: the TA pick finds the next TA command at it plus the CCB's read
  offset [infer]. From `hw_render_context.ccb_base_dev_vaddr` (ours, resgx545).
- `hw_render_context.ccb_ctl_dev_vaddr` G0574 (HWRENDERCONTEXT+0x010): TA client CCB control. From
  `PVRSRV_SGX_CCB_CTL` (1, sgx545-ce); `ccbctl_fw_addr` (3, linux-imagination);
  `hw_render_context.ccb_ctl_dev_vaddr` (ours, resgx545).
- `hw_render_context.submitted_commands` G0537 (HWRENDERCONTEXT+0x014): TA commands queued in the
  context's CCB: the CCB handler increments it, the TA end decrements it. From `submitted_commands`
  (3, linux-imagination).
- `hw_render_context.hw_pb_desc_dev_vaddr` G0527 (HWRENDERCONTEXT+0x018): PB descriptor of the
  context. From `sHWPBDescDevVAddr` (1, sgx545-ce).
- `hw_render_context.param_obj_dev_vaddr` G1103 (HWRENDERCONTEXT+0x01c): inferred reading
  (unconfirmed): the address of a 0x40-byte object in the parameter heap, at the DPM page table's
  base plus 0x40000 in both stacks; no path run (a render, a scene, a partial render, a cleanup)
  uses the word's value; the word and the object are unchanged (Q049) [infer]. From
  `hw_render_context.param_obj_dev_vaddr` (ours, resgx545).
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
- `hw_render_context.pid` G0575 (HWRENDERCONTEXT+0x040): owning process. From `pid` (3,
  linux-imagination); `hw_render_context.pid` (ours, resgx545).
- `hw_render_details.bif_3d_req_base` G0682 (HWRENDERDETAILS+0x000): 3D requestor base. From
  `EUR_CR_BIF_3D_REQ_BASE` (1, sgx545-ce).
- `hw_render_details.bif_zls_req_base` G0319 (HWRENDERDETAILS+0x004): ZLS requestor base. From
  `EUR_CR_BIF_ZLS_REQ_BASE` (1, sgx545-ce).
- `hw_render_details.reg_0400` G0328 (HWRENDERDETAILS+0x008): inferred reading (unconfirmed): The
  render-side word that loads register 0x0400: bit 25 inverts bits 31:24 of every pixel the job
  writes, and no other bit changed a pixel; the data come from the render command's word 11, which
  loads the same register, not from the render-details word itself. From
  `hw_render_details.reg_0400` (ours, resgx545).
- `hw_render_details.isp_ctl` G0691 (HWRENDERDETAILS+0x00c): value the EDM copies verbatim into
  CR_ISP_CTL (0x0414) [infer]. From `hw_render_details.isp_ctl` (ours, resgx545).
- `hw_render_details.isp_msaa` G0320 (HWRENDERDETAILS+0x010): the render details' word the EDM loads
  into CR_ISP_MSAA (0x80000000 single-sampled, 0x80000002 at 4x) [infer]. From
  `hw_render_details.isp_msaa` (ours, resgx545).
- `hw_render_details.poly_offset_units` G0327 (HWRENDERDETAILS+0x014): value the EDM copies into
  CR_ISP_POLY_OFFSET_UNITS [infer]. From `hw_render_details.poly_offset_units` (ours, resgx545).
- `hw_render_details.poly_offset_factor` G0326 (HWRENDERDETAILS+0x018): inferred reading
  (unconfirmed): value the EDM copies into CR_ISP_POLY_OFFSET_FACTOR [infer]. From
  `hw_render_details.poly_offset_factor` (ours, resgx545).
- `hw_render_details.poly_offset_clamp` G0325 (HWRENDERDETAILS+0x01c): value the EDM copies into
  CR_ISP_POLY_OFFSET_CLAMP [infer]. From `hw_render_details.poly_offset_clamp` (ours, resgx545).
- `hw_render_details.isp_region_header_base` G0695 (HWRENDERDETAILS+0x020): render details word 8,
  which the 3D kick writes to CR_ISP_REGION_HEADER_BASE (0x0408); a partial render offsets it by the
  render-target index [infer]. From `hw_render_details.isp_region_header_base` (ours, resgx545).
- `hw_render_details.reg_0148` G0696 (HWRENDERDETAILS+0x024): inferred reading (unconfirmed): render
  details word 9, which the 3D kick writes to CR_REG_0148 (0x0148); what it holds is not shown
  [infer]. From `hw_render_details.reg_0148` (ours, resgx545).
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
- `hw_render_details.isp_bgobjdepth` G0689 (HWRENDERDETAILS+0x040): background object depth (clear
  depth). From `isp_bgobjdepth` (3, linux-imagination).
- `hw_render_details.isp_bgobjvals` G0690 (HWRENDERDETAILS+0x044): background object control. From
  `isp_bgobjvals` (3, linux-imagination).
- `hw_render_details.isp_sample_pos` G0322 (HWRENDERDETAILS+0x04c): inferred reading (unconfirmed):
  value the EDM copies verbatim into CR_ISP_SAMPLE_POS (0x0520): the four sample positions (0 in the
  capture) [infer]. From `hw_render_details.isp_sample_pos` (ours, resgx545).
- `hw_render_details.isp_multisamplectl` G0321 (HWRENDERDETAILS+0x050): value the EDM loads into
  CR_ISP_MULTISAMPLECTL (0x04c8): the pixel's sample positions; 0x88 in every single-sample capture
  [infer]. From `hw_render_details.isp_multisamplectl` (ours, resgx545).
- `hw_render_details.isp_reg_04dc` G0693 (HWRENDERDETAILS+0x054): inferred reading (unconfirmed): as
  CR_ISP_REG_04DC's: a punch-through mode word (bit 1 hangs every punch-through pass, E222).
  Measured: value the EDM copies verbatim into CR_ISP_REG_04DC (0x04dc) [infer]. From
  `hw_render_details.isp_reg_04dc` (ours, resgx545).
- `hw_render_details.reg_0800` G0697 (HWRENDERDETAILS+0x058): inferred reading (unconfirmed): as
  CR_REG_0800's: an on-chip resource limit (bits 5:0 = 48, bits 23:8) for work other than pixel
  tasks (vertex or state tasks, context switches); pixel-bound renders ignore it (E136). Measured:
  value the EDM copies verbatim into CR_REG_0800 (0x0800) (it holds 0x30 outside a render, E225)
  [infer]. From `hw_render_details.reg_0800` (ours, resgx545).
- `hw_render_details.event_pixel_pds_code` G0684 (HWRENDERDETAILS+0x05c): end-of-tile pixel PDS
  program. From `event_pixel_pds_code` (3, linux-imagination).
- `hw_render_details.event_pixel_pds_data` G0685 (HWRENDERDETAILS+0x060): its data size. From
  `event_pixel_pds_data` (3, linux-imagination).
- `hw_render_details.event_pixel_pds_info` G0686 (HWRENDERDETAILS+0x064): its info word. From
  `event_pixel_pds_info` (3, linux-imagination).
- `hw_render_details.isp_line_sample_pos` G0692 (HWRENDERDETAILS+0x068): value the EDM copies
  verbatim into CR_ISP_LINE_SAMPLE_POS (0x0418): the line sample position, 1 the pixel centre (1 in
  the capture) [infer]. From `hw_render_details.isp_line_sample_pos` (ours, resgx545).
- `hw_render_details.use_coeffs0_a` G0712 (HWRENDERDETAILS+0x06c): value the EDM copies verbatim
  into CR_USE_COEFFS0_A (0x0a84): first tap word of coefficient set 0: signed byte taps at -3, -2,
  -1, 0 from the filter's centre in bytes 3, 2, 1, 0 [infer]. From `hw_render_details.use_coeffs0_a`
  (ours, resgx545).
- `hw_render_details.use_coeffs0_b` G0713 (HWRENDERDETAILS+0x070): value the EDM copies verbatim
  into CR_USE_COEFFS0_B (0x0a88): second tap word of coefficient set 0: signed byte taps at +1, +2,
  +3, +4 from the centre in bytes 3, 2, 1, 0 [infer]. From `hw_render_details.use_coeffs0_b` (ours,
  resgx545).
- `hw_render_details.use_coeffs0_bias` G0714 (HWRENDERDETAILS+0x074): value the EDM copies verbatim
  into CR_USE_COEFFS0_BIAS (0x0a8c): shift and bias of coefficient set 0: bits 3:0 shift the tap sum
  right, the bits above a signed bias added before the shift; the result saturates to a byte
  [infer]. From `hw_render_details.use_coeffs0_bias` (ours, resgx545).
- `hw_render_details.use_coeffs1_a` G0715 (HWRENDERDETAILS+0x078): value the EDM copies verbatim
  into CR_USE_COEFFS1_A (0x0a90): first tap word of coefficient set 1: signed byte taps at -3, -2,
  -1, 0 from the filter's centre in bytes 3, 2, 1, 0 [infer]. From `hw_render_details.use_coeffs1_a`
  (ours, resgx545).
- `hw_render_details.use_coeffs1_b` G0716 (HWRENDERDETAILS+0x07c): value the EDM copies verbatim
  into CR_USE_COEFFS1_B (0x0a94): second tap word of coefficient set 1: signed byte taps at +1, +2,
  +3, +4 from the centre in bytes 3, 2, 1, 0 [infer]. From `hw_render_details.use_coeffs1_b` (ours,
  resgx545).
- `hw_render_details.use_coeffs1_bias` G0717 (HWRENDERDETAILS+0x080): value the EDM copies verbatim
  into CR_USE_COEFFS1_BIAS (0x0a98): shift and bias of coefficient set 1: bits 3:0 shift the tap sum
  right, the bits above a signed bias added before the shift; the result saturates to a byte
  [infer]. From `hw_render_details.use_coeffs1_bias` (ours, resgx545).
- `hw_render_details.use_coeffs2_a` G0718 (HWRENDERDETAILS+0x084): value the EDM copies verbatim
  into CR_USE_COEFFS2_A (0x0b24): first tap word of coefficient set 2: signed byte taps at -3, -2,
  -1, 0 from the filter's centre in bytes 3, 2, 1, 0; set 2 uses only -3 (byte 3) and 0 (byte 0)
  [infer]. From `hw_render_details.use_coeffs2_a` (ours, resgx545).
- `hw_render_details.use_coeffs2_b` G0719 (HWRENDERDETAILS+0x088): value the EDM copies verbatim
  into CR_USE_COEFFS2_B (0x0b28): second tap word of coefficient set 2: signed byte taps at +1, +2,
  +3, +4 from the centre in bytes 3, 2, 1, 0; set 2 uses only +3 (byte 1) [infer]. From
  `hw_render_details.use_coeffs2_b` (ours, resgx545).
- `hw_render_details.use_coeffs2_bias` G0720 (HWRENDERDETAILS+0x08c): value the EDM copies verbatim
  into CR_USE_COEFFS2_BIAS (0x0b2c): shift and bias of coefficient set 2: bits 3:0 shift the tap sum
  right, the bits above a signed bias added before the shift; the result saturates to a byte
  [infer]. From `hw_render_details.use_coeffs2_bias` (ours, resgx545).
- `hw_render_details.use_coeffs_mode` G0721 (HWRENDERDETAILS+0x090): value the EDM copies verbatim
  into CR_USE_COEFFS_MODE (0x0a9c): which coefficient sets the filter instructions use: bits 1:0 =
  0, 1, 2 pick one of three fixed banks for sets 2-5, 3 makes set 2 the third loaded group
  (CR_USE_COEFFS2_*) and sets 3-5 zero; sets 0-1 are always CR_USE_COEFFS0/1_* [infer]. From
  `hw_render_details.use_coeffs_mode` (ours, resgx545).
- `hw_render_details.tpu_yuv_csc0_0` G0701 (HWRENDERDETAILS+0x094): value the EDM copies verbatim
  into CR_TPU_YUV_CSC0_0 (0x0820) [infer]. From `hw_render_details.tpu_yuv_csc0_0` (ours, resgx545).
- `hw_render_details.tpu_yuv_csc0_1` G0702 (HWRENDERDETAILS+0x098): value the EDM copies verbatim
  into CR_TPU_YUV_CSC0_1 (0x0824) [infer]. From `hw_render_details.tpu_yuv_csc0_1` (ours, resgx545).
- `hw_render_details.tpu_yuv_csc0_2` G0703 (HWRENDERDETAILS+0x09c): value the EDM copies verbatim
  into CR_TPU_YUV_CSC0_2 (0x0828) [infer]. From `hw_render_details.tpu_yuv_csc0_2` (ours, resgx545).
- `hw_render_details.tpu_yuv_csc0_3` G0704 (HWRENDERDETAILS+0x0a0): value the EDM copies verbatim
  into CR_TPU_YUV_CSC0_3 (0x082c) [infer]. From `hw_render_details.tpu_yuv_csc0_3` (ours, resgx545).
- `hw_render_details.tpu_yuv_csc1_0` G0706 (HWRENDERDETAILS+0x0a4): value the EDM copies verbatim
  into CR_TPU_YUV_CSC1_0 (0x0834) [infer]. From `hw_render_details.tpu_yuv_csc1_0` (ours, resgx545).
- `hw_render_details.tpu_yuv_csc1_1` G0707 (HWRENDERDETAILS+0x0a8): value the EDM copies verbatim
  into CR_TPU_YUV_CSC1_1 (0x0838) [infer]. From `hw_render_details.tpu_yuv_csc1_1` (ours, resgx545).
- `hw_render_details.tpu_yuv_csc1_2` G0708 (HWRENDERDETAILS+0x0ac): value the EDM copies verbatim
  into CR_TPU_YUV_CSC1_2 (0x083c) [infer]. From `hw_render_details.tpu_yuv_csc1_2` (ours, resgx545).
- `hw_render_details.tpu_yuv_csc1_3` G0709 (HWRENDERDETAILS+0x0b0): value the EDM copies verbatim
  into CR_TPU_YUV_CSC1_3 (0x0840) [infer]. From `hw_render_details.tpu_yuv_csc1_3` (ours, resgx545).
- `hw_render_details.tpu_yuv_csc0_4` G0705 (HWRENDERDETAILS+0x0b4): value the EDM copies verbatim
  into CR_TPU_YUV_CSC0_4 (0x0830) [infer]. From `hw_render_details.tpu_yuv_csc0_4` (ours, resgx545).
- `hw_render_details.tpu_yuv_csc1_4` G0710 (HWRENDERDETAILS+0x0b8): value the EDM copies verbatim
  into CR_TPU_YUV_CSC1_4 (0x0844) [infer]. From `hw_render_details.tpu_yuv_csc1_4` (ours, resgx545).
- `hw_render_details.tpu_yuv_csc_input` G0711 (HWRENDERDETAILS+0x0bc): the value the EDM copies
  verbatim into CR_TPU_YUV_CSC_INPUT [infer]. From `hw_render_details.tpu_yuv_csc_input` (ours,
  resgx545).
- `hw_render_details.tpu_luma_key_rg` G0700 (HWRENDERDETAILS+0x0c0): the value the EDM copies
  verbatim into CR_TPU_LUMA_KEY_RG [infer]. From `hw_render_details.tpu_luma_key_rg` (ours,
  resgx545).
- `hw_render_details.tpu_luma_key_b_offset` G0699 (HWRENDERDETAILS+0x0c4): the value the EDM copies
  verbatim into CR_TPU_LUMA_KEY_B_OFFSET [infer]. From `hw_render_details.tpu_luma_key_b_offset`
  (ours, resgx545).
- `hw_render_details.tpu_luma_key_alpha` G0698 (HWRENDERDETAILS+0x0c8): the value the EDM copies
  verbatim into CR_TPU_LUMA_KEY_ALPHA [infer]. From `hw_render_details.tpu_luma_key_alpha` (ours,
  resgx545).
- `hw_render_details.isp_reg_04e8` G0694 (HWRENDERDETAILS+0x0cc): inferred reading (unconfirmed): as
  CR_ISP_REG_04E8's: what it does is not shown; not the background's stencil or mask (E216).
  Measured: value the EDM copies verbatim into CR_ISP_REG_04E8 (0x04e8) [infer]. From
  `hw_render_details.isp_reg_04e8` (ours, resgx545).
- `hw_render_details.access_dev_vaddr` G0538 (HWRENDERDETAILS+0x0d0): access/lock word (SYNCINFO).
  From `sAccessDevAddr` (1, sgx545-ce).
- `hw_render_details.frag_flags` G0687 (HWRENDERDETAILS+0x0d4): fragment (3D) flags: depth/stencil
  buffer present, visibility results (FRAG_FLAGS.*). From `flags` (3, linux-imagination);
  `hw_render_details.frag_flags` (ours, resgx545).
- `hw_render_details.count_rt_data_set` G1074 (HWRENDERDETAILS+0x0d8): render details word 54, the
  RT data set the firmware counts the scene in: the render's completion (with FRAG_FLAGS.BIT10) and
  the finish of a kick that is not the scene's last add one to its executed count, the dword after
  the set's start (the firmware's code); on the hardware the count follows the word. From
  `hw_render_details.count_rt_data_set` (ours, resgx545).
- `hw_render_details.hw_rt_data_dev_vaddr` G0688 (HWRENDERDETAILS+0x0dc): RT data. From
  `sHWRTDataDevAddr` (1, intel-ctp-k900); `hw_render_details.hw_rt_data_dev_vaddr` (ours, resgx545).
- `hw_render_details.dst_sync_list_dev_vaddr` G0683 (HWRENDERDETAILS+0x0e0): render details word 56,
  the destination sync list, copied from TA command word 15: the 3D scheduling tests the entry for
  the render-target index and the completion updates it [infer]. From
  `hw_render_details.dst_sync_list_dev_vaddr` (ours, resgx545).
- `hw_render_details.tq_3d_write_pending` G0589 (HWRENDERDETAILS+0x0e4): render details word 57: the
  write-ops pending value of the 3D transfer-queue sync, copied from the TA command's shared block
  [infer]. From `hw_render_details.tq_3d_write_pending` (ours, resgx545).
- `hw_render_details.tq_3d_write_complete_dev_vaddr` G0588 (HWRENDERDETAILS+0x0e8): render details
  word 58: the address of the write-ops complete word of the 3D transfer-queue sync [infer]. From
  `hw_render_details.tq_3d_write_complete_dev_vaddr` (ours, resgx545).
- `hw_render_details.tq_3d_read_pending` G0587 (HWRENDERDETAILS+0x0ec): render details word 59: the
  read-ops pending value of the 3D transfer-queue sync; the completion writes it plus 1 to the
  read-complete word [infer]. From `hw_render_details.tq_3d_read_pending` (ours, resgx545).
- `hw_render_details.tq_3d_read_complete_dev_vaddr` G0586 (HWRENDERDETAILS+0x0f0): render details
  word 60: the address of the read-ops complete word of the 3D transfer-queue sync [infer]. From
  `hw_render_details.tq_3d_read_complete_dev_vaddr` (ours, resgx545).
- `hw_render_details.ta3d_dep_write_pending` G0585 (HWRENDERDETAILS+0x0fc): render details word 63:
  the write-ops pending value of the TA to 3D dependency, copied from the TA command with render
  flag 0x200 [infer]. From `hw_render_details.ta3d_dep_write_pending` (ours, resgx545).
- `hw_render_details.ta3d_dep_write_complete_dev_vaddr` G0584 (HWRENDERDETAILS+0x100): render
  details word 64: the address of the write-ops complete word of the TA to 3D dependency [infer].
  From `hw_render_details.ta3d_dep_write_complete_dev_vaddr` (ours, resgx545).
- `hw_render_details.num_rts` G0577 (HWRENDERDETAILS+0x104): render details word 65, the number of
  render targets: the render completes target by target until the index reaches it [infer]. From
  `hw_render_details.num_rts` (ours, resgx545).
- `hw_render_details.rt_index` G0580 (HWRENDERDETAILS+0x108): render details word 66, the render
  target the 3D renders next; the completion steps it and sets it to 0 after the last [infer]. From
  `hw_render_details.rt_index` (ours, resgx545).
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
- `hw_render_details.z_rt_stride` G0590 (HWRENDERDETAILS+0x118): inferred reading (unconfirmed):
  render details word 70: for a render target other than the first the 3D kick adds its index times
  this word to the Z load and store bases (0x0484, 0x0488) [infer]. From
  `hw_render_details.z_rt_stride` (ours, resgx545).
- `hw_render_details.stencil_rt_stride` G0583 (HWRENDERDETAILS+0x11c): inferred reading
  (unconfirmed): render details word 71: for a render target other than the first the 3D kick adds
  its index times this word to the stencil load and store bases (0x048c, 0x0490) [infer]. From
  `hw_render_details.stencil_rt_stride` (ours, resgx545).
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
- `hw_render_details.frame_num` G0576 (HWRENDERDETAILS+0x140): frame number. From `ui32FrameNum` (1,
  intel-ctp-k900); `hw_render_details.frame_num` (ours, resgx545).
- `hw_render_details.num_status_3d` G0579 (HWRENDERDETAILS+0x144): render details word 81: the
  number of 3D status pairs that follow it [infer]. From `hw_render_details.num_status_3d` (ours,
  resgx545).
- `hw_render_details.status_3d` G0582 (HWRENDERDETAILS+0x148): render details words 82 to 89: up to
  four 3D status pairs, an address and a value; the completion stores each value at its address
  [infer]. From `hw_render_details.status_3d` (ours, resgx545).
- `hw_render_details.num_src_syncs` G0578 (HWRENDERDETAILS+0x168): source sync count. From
  `ui32NumSrcSyncs` (1, sgx545-ce); `hw_render_details.num_src_syncs` (ours, resgx545).
- `hw_render_details.src_syncs` G0581 (HWRENDERDETAILS+0x16c): source syncs [8]. From `asSrcSyncs`
  (1, sgx545-ce); `hw_render_details.src_syncs` (ours, resgx545).
- `hw_rt_data.hw_render_context_dev_vaddr` G1108 (HWRTDATA+0x000): owning HW render context. From
  `sHWRenderContextDevVAddr` (1, sgx545-ce); `hw_rt_data.hw_render_context_dev_vaddr` (ours,
  resgx545).
- `hw_rt_data.hw_render_details_dev_vaddr` G0550 (HWRTDATA+0x004): render details of the scene in
  flight on this RT data; written by the EDM at the TA kick, cleared when the scene is done (the
  client leaves it 0) [infer]. From `hw_rt_data.hw_render_details_dev_vaddr` (ours, resgx545).
- `hw_rt_data.blocks_per_mtile` G1106 (HWRTDATA+0x008): inferred reading (unconfirmed): a size word
  of the RT data that follows the macrotile rule: the blocks of one macrotile [infer]. From
  `hw_rt_data.blocks_per_mtile` (ours, resgx545).
- `hw_rt_data.mtile_region_bytes` G1109 (HWRTDATA+0x00c): inferred reading (unconfirmed): a size
  word of the RT data: 0xc0 bytes per block of hw_rt_data.blocks_per_mtile [infer]. From
  `hw_rt_data.mtile_region_bytes` (ours, resgx545).
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
- `hw_rt_data.te_tpc_dev_vaddr` G1111 (HWRTDATA+0x020): the address of the TE's tail pointer cache,
  the value CR_TE_TPC_ADDR takes. From `hw_rt_data.te_tpc_dev_vaddr` (ours, resgx545).
- `hw_rt_data.te_tpc_bytes` G1110 (HWRTDATA+0x024): the size in bytes of the TE's tail pointer
  cache. From `hw_rt_data.te_tpc_bytes` (ours, resgx545).
- `hw_rt_data.num_rts` G0591 (HWRTDATA+0x028): RT data word 10, the number of render targets: a
  first TA kick clears the DPM state once per render target it counts [infer]. From
  `hw_rt_data.num_rts` (ours, resgx545).
- `hw_rt_data.region_header_rt_stride` G0592 (HWRTDATA+0x02c): inferred reading (unconfirmed): RT
  data word 11: for a render target other than the first the 3D kick adds its index times this word
  to the region header base (0x0408) [infer]. From `hw_rt_data.region_header_rt_stride` (ours,
  resgx545).
- `hw_rt_data.rt_status_dev_vaddr` G0552 (HWRTDATA+0x030): one status word per render target: zeroed
  on a first kick, bit 1 set by the partial-render resume, bit 0 set when the RT is rendered; the 3D
  kick adjusts depth/stencil load and store from bit 1 [infer]. From
  `hw_rt_data.rt_status_dev_vaddr` (ours, resgx545).
- `hw_rt_data.state` G0553 (HWRTDATA+0x034): RT data state (0x10 = no render outstanding). From
  `state` (3, linux-imagination).
- `hw_rt_data_set.pending_count_dev_vaddr` G1092 (HWRTDATASET+0x000): the address of the host's
  pending count: the set's cleanup completes only when the word it points at equals the set's
  executed_count. From `hw_rt_data_set.pending_count_dev_vaddr` (ours, resgx545).
- `hw_rt_data_set.executed_count` G0554 (HWRTDATASET+0x004): count the EDM increments at each TA end
  that is not the scene's last and at each scene render with FRAG_FLAGS.BIT10, in the set render
  details word 54 points at, a count there following that word on the hardware; the set's cleanup
  completes only when it equals the word the set's word 0 points at
  (hw_rt_data_set.pending_count_dev_vaddr), the host's pending count. From
  `hw_rt_data_set.executed_count` (ours, resgx545).
- `hw_rt_data_set.tiles_across` G1113 (HWRTDATASET+0x008): inferred reading (unconfirmed): the
  number of macrotiles across times the macrotile's width in tiles, as the size rule of the TA words
  gives it [infer]. From `hw_rt_data_set.tiles_across` (ours, resgx545).
- `hw_rt_data_set.num_out_of_mem_signals` G0555 (HWRTDATASET+0x00c): TA out-of-memory count. From
  `ui32NumOutOfMemSignals` (1, sgx545-ce).
- `hw_rt_data_set.num_spm_renders` G0556 (HWRTDATASET+0x010): partial renders run. From
  `ui32NumSPMRenders` (1, sgx545-ce).
- `hw_rt_data_set.num_rt_data` G1112 (HWRTDATASET+0x014): the number of RT data that follow the
  set's header, used in turn one per scene. From `hw_rt_data_set.num_rt_data` (ours, resgx545).
- `hw_rt_data_set.hw_rt_data` G1145 (HWRTDATASET+0x018): the set's hw_rt_data array, 0x38 bytes
  each; the TA command's hw_rt_data_dev_vaddr points at one [infer]. From
  `hw_rt_data_set.hw_rt_data` (ours, resgx545).
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
- `hw_transfer_context.dst_sync_write_ops_pending_val` G0974 (HWTRANSFERCONTEXT+0x0a0): HW transfer
  context word 40, which the EDM copies over the command's destination sync write-pending value
  (TRANSFERCMD+0x13c) when the command has a destination sync [infer]. From
  `hw_transfer_context.dst_sync_write_ops_pending_val` (ours, resgx545).
- `hw_transfer_context.dst_sync_write_ops_complete_dev_vaddr` G0973 (HWTRANSFERCONTEXT+0x0a4): HW
  transfer context word 41, which the EDM copies over the command's destination sync write-complete
  address (TRANSFERCMD+0x140) when the command has a destination sync [infer]. From
  `hw_transfer_context.dst_sync_write_ops_complete_dev_vaddr` (ours, resgx545).
- `hw_transfer_context.pid` G0975 (HWTRANSFERCONTEXT+0x0a8): owning process. From `pid` (3,
  linux-imagination).
- `hw_transfer_context.run_node_prev` G0977 (HWTRANSFERCONTEXT+0x0ac): previous context in EDM list.
  From `run_node` (3, linux-imagination).
- `hw_transfer_context.run_node_next` G0976 (HWTRANSFERCONTEXT+0x0b0): next context in EDM list.
  From `run_node` (3, linux-imagination).
- `misc_info.flags` G0111 (MISC+0x00): MISC_INFO_FLAGS.* request/ready bits. From
  `ui32MiscInfoFlags` (1, sgx545-ce).
- `misc_info.struct_sizes` G0112 (MISC+0x20): structure sizes block. From `sSGXStructSizes` (1,
  sgx545-ce).
- `misc_info_features.core_rev` G1146 (MISCINFO_FEATURES+0x00 (=MISC+0x04)): core revision. From
  `ui32CoreRev` (1, sgx545-ce).
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
- `ccb_kick.ccb_offset` G1135 (SGX_CCB_KICK+0x1f0): client-CCB offset of CMDTA_SHARED. From
  `ui32CCBOffset` (1, sgx545-ce).
- `ta3d_ctl.ta3d_ctl_dev_vaddr` G0739 (TA3D_CTL+0x000): the control block's own address, copied into
  sa0, the base the EDM reads the block through [infer]. From `ta3d_ctl.ta3d_ctl_dev_vaddr` (ours,
  resgx545).
- `ta3d_ctl.host_ctl_dev_vaddr` G0727 (TA3D_CTL+0x004): the host control block's address, copied
  into sa1 [infer]. From `ta3d_ctl.host_ctl_dev_vaddr` (ours, resgx545).
- `ta3d_ctl.ccb_ctl_dev_vaddr` G0726 (TA3D_CTL+0x008): the kernel CCB control's address, copied into
  sa2: its word 0 the write offset, word 1 the read offset [infer]. From
  `ta3d_ctl.ccb_ctl_dev_vaddr` (ours, resgx545).
- `ta3d_ctl.dpm_slot0_rt_data_dev_vaddr` G0595 (TA3D_CTL+0x050): the RT data that owns DPM context
  slot 0; the TA and the 3D kick take a slot that holds their RT data, else a free one [infer]. From
  `ta3d_ctl.dpm_slot0_rt_data_dev_vaddr` (ours, resgx545).
- `ta3d_ctl.dpm_slot1_rt_data_dev_vaddr` G0596 (TA3D_CTL+0x054): the RT data that owns DPM context
  slot 1 [infer]. From `ta3d_ctl.dpm_slot1_rt_data_dev_vaddr` (ours, resgx545).
- `ta3d_ctl.kernel_ccb_dev_vaddr` G0729 (TA3D_CTL+0x058): the kernel CCB's address, copied into sa22
  [infer]. From `ta3d_ctl.kernel_ccb_dev_vaddr` (ours, resgx545).
- `ta3d_ctl.page_dir_phys_addr` G0733 (TA3D_CTL+0x05c): the physical address of the EDM's page
  directory, copied into sa23: a value, not a pointer [infer]. From `ta3d_ctl.page_dir_phys_addr`
  (ours, resgx545).
- `ta3d_ctl.cmd_ta_dev_vaddr` G0594 (TA3D_CTL+0x060): the TA command the TA runs, recorded by the TA
  kick [infer]. From `ta3d_ctl.cmd_ta_dev_vaddr` (ours, resgx545).
- `ta3d_ctl.hw_rt_data_ta` G0603 (TA3D_CTL+0x064): the RT data of the TA's job, recorded by the TA
  kick [infer]. From `ta3d_ctl.hw_rt_data_ta` (ours, resgx545).
- `ta3d_ctl.hw_render_details_ta` G0601 (TA3D_CTL+0x068): the render details of the TA's job (the
  command's word 14), recorded by the TA kick [infer]. From `ta3d_ctl.hw_render_details_ta` (ours,
  resgx545).
- `ta3d_ctl.hw_render_context_ta` G0599 (TA3D_CTL+0x06c): the render context of the TA's job,
  recorded by the TA kick [infer]. From `ta3d_ctl.hw_render_context_ta` (ours, resgx545).
- `ta3d_ctl.hw_rt_data_3d` G0602 (TA3D_CTL+0x070): the RT data of the 3D's job, recorded by the 3D
  kick [infer]. From `ta3d_ctl.hw_rt_data_3d` (ours, resgx545).
- `ta3d_ctl.hw_render_details_3d` G0600 (TA3D_CTL+0x074): the render details the 3D renders,
  recorded by the 3D kick [infer]. From `ta3d_ctl.hw_render_details_3d` (ours, resgx545).
- `ta3d_ctl.rt_index_3d` G0606 (TA3D_CTL+0x078): the render-target index the 3D renders, recorded by
  the 3D kick [infer]. From `ta3d_ctl.rt_index_3d` (ours, resgx545).
- `ta3d_ctl.requests` G0734 (TA3D_CTL+0x07c): the request word: a routine ORs its request bits in
  and starts PDS program #14, whose three tasks each remove the bits they serve [infer]. From
  `ta3d_ctl.requests` (ours, resgx545).
- `ta3d_ctl.cleanup_pb_desc` G1075 (TA3D_CTL+0x080): TA3DCtl dword 32, the PB descriptor of the last
  render-context cleanup; the cleanup clears the TA's and the 3D's loaded PB descriptor words that
  equal it [infer]. From `ta3d_ctl.cleanup_pb_desc` (ours, resgx545).
- `ta3d_ctl.saved_ta_global_list` G0735 (TA3D_CTL+0x084): inferred reading (unconfirmed):
  CR_DPM_TA_GLOBAL_LIST as the out-of-memory path saves it before it grows the TA's global list; the
  global kind of out-of-memory writes it back [infer]. From `ta3d_ctl.saved_ta_global_list` (ours,
  resgx545).
- `ta3d_ctl.abort_page_count0` G0722 (TA3D_CTL+0x08c): inferred reading (unconfirmed): a page count
  saved at a macrotile abort, from 0x0724 (CR_DPM_PAGE_STATUS) less 2, which a later out-of-memory
  compares with the current one [infer]. From `ta3d_ctl.abort_page_count0` (ours, resgx545).
- `ta3d_ctl.abort_page_count1` G0723 (TA3D_CTL+0x090): inferred reading (unconfirmed): a page count
  saved at a macrotile abort, from 0x072c less 2, which a later out-of-memory compares with the
  current one [infer]. From `ta3d_ctl.abort_page_count1` (ours, resgx545).
- `ta3d_ctl.threshold_ta_global_list` G0740 (TA3D_CTL+0x094): inferred reading (unconfirmed): the TA
  global list as the out-of-memory path saves it when it raises the ZLS page threshold [infer]. From
  `ta3d_ctl.threshold_ta_global_list` (ours, resgx545).
- `ta3d_ctl.zls_threshold_step` G0741 (TA3D_CTL+0x098): inferred reading (unconfirmed): the step
  (0x20) the out-of-memory path adds to CR_DPM_ZLS_PAGE_THRESHOLD when it raises the threshold
  [infer]. From `ta3d_ctl.zls_threshold_step` (ours, resgx545).
- `ta3d_ctl.abort_status_mtile` G0725 (TA3D_CTL+0x09c): CR_DPM_ABORT_STATUS_MTILE as a macrotile
  abort saves it; the partial render works out the partial-region base from it [infer]. From
  `ta3d_ctl.abort_status_mtile` (ours, resgx545).
- `ta3d_ctl.abort_rt_index` G0724 (TA3D_CTL+0x0a0): bits 13:5 of the aborted macrotile's status, its
  render-target index, saved at a macrotile abort [infer]. From `ta3d_ctl.abort_rt_index` (ours,
  resgx545).
- `ta3d_ctl.frame_num_ta` G0598 (TA3D_CTL+0x0a4): the frame number of the TA's job, copied from the
  TA command by the TA kick [infer]. From `ta3d_ctl.frame_num_ta` (ours, resgx545).
- `ta3d_ctl.frame_num_3d` G0597 (TA3D_CTL+0x0a8): the frame number of the 3D's job, copied from the
  render details by the 3D kick [infer]. From `ta3d_ctl.frame_num_3d` (ours, resgx545).
- `ta3d_ctl.hwperf_buffer_dev_vaddr` G0728 (TA3D_CTL+0x0ac): the HWPerf circular buffer's address,
  copied into sa43 [infer]. From `ta3d_ctl.hwperf_buffer_dev_vaddr` (ours, resgx545).
- `ta3d_ctl.signature_ta_dev_vaddr` G0738 (TA3D_CTL+0x0b0): the TA signature buffer's address,
  copied into sa44 [infer]. From `ta3d_ctl.signature_ta_dev_vaddr` (ours, resgx545).
- `ta3d_ctl.signature_3d_dev_vaddr` G0737 (TA3D_CTL+0x0b4): the 3D signature buffer's address,
  copied into sa45 [infer]. From `ta3d_ctl.signature_3d_dev_vaddr` (ours, resgx545).
- `ta3d_ctl.render_context_count` G1076 (TA3D_CTL+0x0c4): inferred reading (unconfirmed): TA3DCtl
  dword 49: the bus interface directory list (0 to 14) the EDM last gave a render context's page
  directory: a kick whose directory is in no list writes it into the next list's
  CR_BIF_DIR_LIST_BASEn (BASE0 for 0) and advances the word, mod 15 because list 15 is the EDM's
  own; the name is older than the reading [infer]. From `ta3d_ctl.render_context_count` (ours,
  resgx545).
- `ta3d_ctl.pid_ta` G0605 (TA3D_CTL+0x0c8): the PID of the TA's render context, recorded by the TA
  kick [infer]. From `ta3d_ctl.pid_ta` (ours, resgx545).
- `ta3d_ctl.pid_3d` G0604 (TA3D_CTL+0x0cc): the PID of the 3D's render context, recorded by the 3D
  kick [infer]. From `ta3d_ctl.pid_3d` (ours, resgx545).
- `ta3d_ctl.settle_count` G0736 (TA3D_CTL+0x0d0): the nesting count of the settle loop: incremented
  on entry, decremented at the release, which clears the CR_DMS_CTRL gate bits when it reaches 0
  [infer]. From `ta3d_ctl.settle_count` (ours, resgx545).
- `ta3d_ctl.kick_marks` G0732 (TA3D_CTL+0x0d8): inferred reading (unconfirmed): kick marks: bit 0
  set by the TA kick and the TA-finished handler, bit 1 by the 3D kick; what reads them is not shown
  [infer]. From `ta3d_ctl.kick_marks` (ours, resgx545).
- `ta3d_ctl.kick_clear_ta` G0731 (TA3D_CTL+0x0dc): inferred reading (unconfirmed): a word the TA
  kick, the TA-finished handler and the out-of-memory path clear; what sets it is not shown [infer].
  From `ta3d_ctl.kick_clear_ta` (ours, resgx545).
- `ta3d_ctl.kick_clear_3d` G0730 (TA3D_CTL+0x0e4): inferred reading (unconfirmed): a word the 3D
  kick clears; what sets it is not shown [infer]. From `ta3d_ctl.kick_clear_3d` (ours, resgx545).
- `transfer_cmd.isp_background_tag` G0980 (TRANSFERCMD+0x000): transfer command word 0, which the
  EDM loads into register 0x04c4 before it starts the render: bits 23:0 locate the background object
  above transfer_cmd.bif_3d_req_base in 16-byte units, and bits 30:25 count its texture layers (0
  for a fill, 1 for a copy) [infer]. From `transfer_cmd.isp_background_tag` (ours, resgx545).
- `transfer_cmd.isp_bgobjvals` G0982 (TRANSFERCMD+0x004): background object control. From
  `isp_bgobjvals` (3, linux-imagination).
- `transfer_cmd.isp_bgobjdepth` G0981 (TRANSFERCMD+0x008): background depth. From `isp_bgobjdepth`
  (3, linux-imagination).
- `transfer_cmd.isp_render` G0117 (TRANSFERCMD+0x00c): ISP render type/scan. From `isp_render` (3,
  linux-imagination).
- `transfer_cmd.isp_region` G0985 (TRANSFERCMD+0x010): region base. From `isp_rgn` (3,
  linux-imagination).
- `transfer_cmd.isp_ctl` G0983 (TRANSFERCMD+0x014): transfer command word 5, which the EDM loads
  into CR_ISP_CTL (0x0414) before it starts the render; 0x100 in every captured and template-built
  command [infer]. From `transfer_cmd.isp_ctl` (ours, resgx545).
- `transfer_cmd.bif_3d_req_base` G0025 (TRANSFERCMD+0x018): 3D requestor base. From
  `EUR_CR_BIF_3D_REQ_BASE` (1, sgx545-ce).
- `transfer_cmd.isp_msaa` G0743 (TRANSFERCMD+0x01c): the transfer command's word the EDM loads into
  CR_ISP_MSAA (0x80000000) [infer]. From `transfer_cmd.isp_msaa` (ours, resgx545).
- `transfer_cmd.isp_multisamplectl` G0984 (TRANSFERCMD+0x020): transfer command word 8, which the
  EDM loads into CR_ISP_MULTISAMPLECTL (0x04c8) before it starts the render; 0x88 in every captured
  and template-built command [infer]. From `transfer_cmd.isp_multisamplectl` (ours, resgx545).
- `transfer_cmd.event_pixel_pds_code` G0026 (TRANSFERCMD+0x024): end-of-tile PDS program. From
  `event_pixel_pds_code` (3, linux-imagination).
- `transfer_cmd.event_pixel_pds_data` G0978 (TRANSFERCMD+0x028): its data size. From
  `event_pixel_pds_data` (3, linux-imagination).
- `transfer_cmd.event_pixel_pds_info` G0742 (TRANSFERCMD+0x02c): its info. From
  `event_pixel_pds_info` (3, linux-imagination).
- `transfer_cmd.isp_render_origin` G0987 (TRANSFERCMD+0x030): top-left tile of the render: y in 9:0
  and x in 24:16 (y0 / 16 | (x0 / 32) << 16), 32 x 16 tiles; the EDM copies it into register 0x040c.
  From `isp_render_origin` (3, linux-imagination).
- `transfer_cmd.isp_render_end` G0986 (TRANSFERCMD+0x034): transfer command word 13, which the EDM
  loads into register 0x0410 before it starts the render: the last tile of the render, inclusive, in
  the form of transfer_cmd.isp_render_origin (y / 16 in the low half, x / 32 << 16, 32 x 16 tiles)
  [infer]. From `transfer_cmd.isp_render_end` (ours, resgx545).
- `transfer_cmd.reg_0400` G0340 (TRANSFERCMD+0x038): inferred reading (unconfirmed): Transfer
  command word 14, which loads register 0x0400: bit 25 inverts bits 31:24 of every pixel a fill or
  copy writes, and no other bit changed a pixel; over the every-value source exactly the 128 values
  of bits 31:24 with bit 25 set changed the image. From `transfer_cmd.reg_0400` (ours, resgx545).
- `transfer_cmd.pds_exec_base` G0027 (TRANSFERCMD+0x03c): PDS execution base. From
  `EUR_CR_PDS_EXEC_BASE` (1, sgx545-ce).
- `transfer_cmd.reg_0148` G0989 (TRANSFERCMD+0x040): transfer command word 16, which the EDM loads
  into CR_REG_0148 (0x0148) before it starts the render [infer]. From `transfer_cmd.reg_0148` (ours,
  resgx545).
- `transfer_cmd.tpu_yuv_csc0_0` G0994 (TRANSFERCMD+0x044): transfer command word 17, which the EDM
  loads into CR_TPU_YUV_CSC0_0 (0x0820) only when transfer_cmd.load_yuv_csc (+0x188) is not 0; 0 in
  every captured command, which leaves the load word 0 [infer]. From `transfer_cmd.tpu_yuv_csc0_0`
  (ours, resgx545).
- `transfer_cmd.tpu_yuv_csc0_1` G0995 (TRANSFERCMD+0x048): transfer command word 18, which the EDM
  loads into CR_TPU_YUV_CSC0_1 (0x0824) only when transfer_cmd.load_yuv_csc (+0x188) is not 0; 0 in
  every captured command, which leaves the load word 0 [infer]. From `transfer_cmd.tpu_yuv_csc0_1`
  (ours, resgx545).
- `transfer_cmd.tpu_yuv_csc0_2` G0996 (TRANSFERCMD+0x04c): transfer command word 19, which the EDM
  loads into CR_TPU_YUV_CSC0_2 (0x0828) only when transfer_cmd.load_yuv_csc (+0x188) is not 0; 0 in
  every captured command, which leaves the load word 0 [infer]. From `transfer_cmd.tpu_yuv_csc0_2`
  (ours, resgx545).
- `transfer_cmd.tpu_yuv_csc0_3` G0997 (TRANSFERCMD+0x050): transfer command word 20, which the EDM
  loads into CR_TPU_YUV_CSC0_3 (0x082c) only when transfer_cmd.load_yuv_csc (+0x188) is not 0; 0 in
  every captured command, which leaves the load word 0 [infer]. From `transfer_cmd.tpu_yuv_csc0_3`
  (ours, resgx545).
- `transfer_cmd.tpu_yuv_csc0_4` G0998 (TRANSFERCMD+0x054): transfer command word 21, which the EDM
  loads into CR_TPU_YUV_CSC0_4 (0x0830) only when transfer_cmd.load_yuv_csc (+0x188) is not 0; 0 in
  every captured command, which leaves the load word 0 [infer]. From `transfer_cmd.tpu_yuv_csc0_4`
  (ours, resgx545).
- `transfer_cmd.tpu_yuv_csc1_0` G0999 (TRANSFERCMD+0x058): transfer command word 22, which the EDM
  loads into CR_TPU_YUV_CSC1_0 (0x0834) only when transfer_cmd.load_yuv_csc (+0x188) is not 0; 0 in
  every captured command, which leaves the load word 0 [infer]. From `transfer_cmd.tpu_yuv_csc1_0`
  (ours, resgx545).
- `transfer_cmd.tpu_yuv_csc1_1` G1000 (TRANSFERCMD+0x05c): transfer command word 23, which the EDM
  loads into CR_TPU_YUV_CSC1_1 (0x0838) only when transfer_cmd.load_yuv_csc (+0x188) is not 0; 0 in
  every captured command, which leaves the load word 0 [infer]. From `transfer_cmd.tpu_yuv_csc1_1`
  (ours, resgx545).
- `transfer_cmd.tpu_yuv_csc1_2` G1001 (TRANSFERCMD+0x060): transfer command word 24, which the EDM
  loads into CR_TPU_YUV_CSC1_2 (0x083c) only when transfer_cmd.load_yuv_csc (+0x188) is not 0; 0 in
  every captured command, which leaves the load word 0 [infer]. From `transfer_cmd.tpu_yuv_csc1_2`
  (ours, resgx545).
- `transfer_cmd.tpu_yuv_csc1_3` G1002 (TRANSFERCMD+0x064): transfer command word 25, which the EDM
  loads into CR_TPU_YUV_CSC1_3 (0x0840) only when transfer_cmd.load_yuv_csc (+0x188) is not 0; 0 in
  every captured command, which leaves the load word 0 [infer]. From `transfer_cmd.tpu_yuv_csc1_3`
  (ours, resgx545).
- `transfer_cmd.tpu_yuv_csc1_4` G1003 (TRANSFERCMD+0x068): transfer command word 26, which the EDM
  loads into CR_TPU_YUV_CSC1_4 (0x0844) only when transfer_cmd.load_yuv_csc (+0x188) is not 0; 0 in
  every captured command, which leaves the load word 0 [infer]. From `transfer_cmd.tpu_yuv_csc1_4`
  (ours, resgx545).
- `transfer_cmd.tpu_yuv_csc_input` G1004 (TRANSFERCMD+0x06c): transfer command word 27, which the
  EDM loads into CR_TPU_YUV_CSC_INPUT (0x0848) only when transfer_cmd.load_yuv_csc (+0x188) is not
  0; 0 in every captured command, which leaves the load word 0 [infer]. From
  `transfer_cmd.tpu_yuv_csc_input` (ours, resgx545).
- `transfer_cmd.tpu_luma_key_rg` G0993 (TRANSFERCMD+0x070): transfer command word 28, which the EDM
  loads into CR_TPU_LUMA_KEY_RG (0x0860) only when transfer_cmd.load_tpu_luma_key (+0x18c) is not 0;
  0 in every captured command, which leaves the load word 0 [infer]. From
  `transfer_cmd.tpu_luma_key_rg` (ours, resgx545).
- `transfer_cmd.tpu_luma_key_b_offset` G0992 (TRANSFERCMD+0x074): transfer command word 29, which
  the EDM loads into CR_TPU_LUMA_KEY_B_OFFSET (0x0864) only when transfer_cmd.load_tpu_luma_key
  (+0x18c) is not 0; 0 in every captured command, which leaves the load word 0 [infer]. From
  `transfer_cmd.tpu_luma_key_b_offset` (ours, resgx545).
- `transfer_cmd.tpu_luma_key_alpha` G0991 (TRANSFERCMD+0x078): transfer command word 30, which the
  EDM loads into CR_TPU_LUMA_KEY_ALPHA (0x0868) only when transfer_cmd.load_tpu_luma_key (+0x18c) is
  not 0; 0 in every captured command, which leaves the load word 0 [infer]. From
  `transfer_cmd.tpu_luma_key_alpha` (ours, resgx545).
- `transfer_cmd.use_coeffs_mode` G1014 (TRANSFERCMD+0x07c): transfer command word 31, which the EDM
  loads into CR_USE_COEFFS_MODE (0x0a9c) only when transfer_cmd.load_use_coeffs (+0x190) is not 0; 0
  in every captured command, which leaves the load word 0 [infer]. From
  `transfer_cmd.use_coeffs_mode` (ours, resgx545).
- `transfer_cmd.use_coeffs0_a` G1005 (TRANSFERCMD+0x080): transfer command word 32, which the EDM
  loads into CR_USE_COEFFS0_A (0x0a84) only when transfer_cmd.load_use_coeffs (+0x190) is not 0; 0
  in every captured command, which leaves the load word 0 [infer]. From `transfer_cmd.use_coeffs0_a`
  (ours, resgx545).
- `transfer_cmd.use_coeffs0_b` G1006 (TRANSFERCMD+0x084): transfer command word 33, which the EDM
  loads into CR_USE_COEFFS0_B (0x0a88) only when transfer_cmd.load_use_coeffs (+0x190) is not 0; 0
  in every captured command, which leaves the load word 0 [infer]. From `transfer_cmd.use_coeffs0_b`
  (ours, resgx545).
- `transfer_cmd.use_coeffs0_bias` G1007 (TRANSFERCMD+0x088): transfer command word 34, which the EDM
  loads into CR_USE_COEFFS0_BIAS (0x0a8c) only when transfer_cmd.load_use_coeffs (+0x190) is not 0;
  0 in every captured command, which leaves the load word 0 [infer]. From
  `transfer_cmd.use_coeffs0_bias` (ours, resgx545).
- `transfer_cmd.use_coeffs1_a` G1008 (TRANSFERCMD+0x08c): transfer command word 35, which the EDM
  loads into CR_USE_COEFFS1_A (0x0a90) only when transfer_cmd.load_use_coeffs (+0x190) is not 0; 0
  in every captured command, which leaves the load word 0 [infer]. From `transfer_cmd.use_coeffs1_a`
  (ours, resgx545).
- `transfer_cmd.use_coeffs1_b` G1009 (TRANSFERCMD+0x090): transfer command word 36, which the EDM
  loads into CR_USE_COEFFS1_B (0x0a94) only when transfer_cmd.load_use_coeffs (+0x190) is not 0; 0
  in every captured command, which leaves the load word 0 [infer]. From `transfer_cmd.use_coeffs1_b`
  (ours, resgx545).
- `transfer_cmd.use_coeffs1_bias` G1010 (TRANSFERCMD+0x094): transfer command word 37, which the EDM
  loads into CR_USE_COEFFS1_BIAS (0x0a98) only when transfer_cmd.load_use_coeffs (+0x190) is not 0;
  0 in every captured command, which leaves the load word 0 [infer]. From
  `transfer_cmd.use_coeffs1_bias` (ours, resgx545).
- `transfer_cmd.use_coeffs2_a` G1011 (TRANSFERCMD+0x098): transfer command word 38, which the EDM
  loads into CR_USE_COEFFS2_A (0x0b24) only when transfer_cmd.load_use_coeffs (+0x190) is not 0; 0
  in every captured command, which leaves the load word 0 [infer]. From `transfer_cmd.use_coeffs2_a`
  (ours, resgx545).
- `transfer_cmd.use_coeffs2_b` G1012 (TRANSFERCMD+0x09c): transfer command word 39, which the EDM
  loads into CR_USE_COEFFS2_B (0x0b28) only when transfer_cmd.load_use_coeffs (+0x190) is not 0; 0
  in every captured command, which leaves the load word 0 [infer]. From `transfer_cmd.use_coeffs2_b`
  (ours, resgx545).
- `transfer_cmd.use_coeffs2_bias` G1013 (TRANSFERCMD+0x0a0): transfer command word 40, which the EDM
  loads into CR_USE_COEFFS2_BIAS (0x0b2c) only when transfer_cmd.load_use_coeffs (+0x190) is not 0;
  0 in every captured command, which leaves the load word 0 [infer]. From
  `transfer_cmd.use_coeffs2_bias` (ours, resgx545).
- `transfer_cmd.cmd_size` G0115 (TRANSFERCMD+0x0a4): command size, 64-byte multiple. From `cmd_size`
  (3, linux-imagination).
- `transfer_cmd.flags` G0116 (TRANSFERCMD+0x0a8): TQ_FLAGS.* of the transfer. From `ui32Flags` (1,
  sgx545-ce); `flags` (3, linux-imagination).
- `transfer_cmd.shared` G0990 (TRANSFERCMD+0x0ac): embedded transfer_cmd_shared block; the kick
  passes its client-CCB offset in transfer_kick.shared_cmd_ccb_offset. From `ui32SharedCmdCCBOffset`
  (1, sgx545-ce).
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
- `transfer_cmd.fence_id` G0979 (TRANSFERCMD+0x198): transfer command word 102, the command's
  running number in its context, counted from 0; the closed stack's status value is this word plus
  one, and the EDM reads it with no use [infer]. From `transfer_cmd.fence_id` (ours, resgx545).
- `transfer_cmd.num_patches` G0988 (TRANSFERCMD+0x19c): transfer command word 103, the count of
  {address, value} updates in transfer_cmd.patches that the EDM applies through the context's page
  directory; 0 in every captured command [infer]. From `transfer_cmd.num_patches` (ours, resgx545).
- `transfer_cmd.patches` G0565 (TRANSFERCMD+0x1a0): {address, value} memory writes the EDM applies
  through the context's address space before the render, to the end of the command [infer]. From
  `transfer_cmd.patches` (ours, resgx545).
- `transfer_cmd_shared.num_src_syncs` G1019 (TRANSFERCMD_SHARED+0x00 (TRANSFERCMD+0x0ac)): source
  sync count. From `ui32NumSrcSyncs` (1, sgx545-ce).
- `transfer_cmd_shared.src_syncs` G1021 (TRANSFERCMD_SHARED+0x04 (TRANSFERCMD+0x0b0)): source syncs
  [8]. From `asSrcSyncs` (1, sgx545-ce).
- `transfer_cmd_shared.num_dst_syncs` G1018 (TRANSFERCMD_SHARED+0x84 (TRANSFERCMD+0x130)):
  destination sync count. From `ui32NumDstSyncs` (1, sgx545-ce).
- `transfer_cmd_shared.dst_syncs` G1017 (TRANSFERCMD_SHARED+0x88 (TRANSFERCMD+0x134)): destination
  sync [1]. From `asDstSyncs` (1, sgx545-ce).
- `transfer_cmd_shared.sync_ta_write_ops_pending_val` G1029 (TRANSFERCMD_SHARED+0x98
  (TRANSFERCMD+0x144)): TA sync write pending. From `ui32TASyncWriteOpsPendingVal` (1, sgx545-ce).
- `transfer_cmd_shared.sync_ta_write_ops_complete_dev_vaddr` G1028 (TRANSFERCMD_SHARED+0x9c
  (TRANSFERCMD+0x148)): TA sync write-complete addr. From `sTASyncWriteOpsCompleteDevVAddr` (1,
  sgx545-ce).
- `transfer_cmd_shared.sync_ta_read_ops_pending_val` G1027 (TRANSFERCMD_SHARED+0xa0
  (TRANSFERCMD+0x14c)): TA sync read pending. From `ui32TASyncReadOpsPendingVal` (1, sgx545-ce).
- `transfer_cmd_shared.sync_ta_read_ops_complete_dev_vaddr` G1026 (TRANSFERCMD_SHARED+0xa4
  (TRANSFERCMD+0x150)): TA sync read-complete addr. From `sTASyncReadOpsCompleteDevVAddr` (1,
  sgx545-ce).
- `transfer_cmd_shared.sync_3d_write_ops_pending_val` G1025 (TRANSFERCMD_SHARED+0xa8
  (TRANSFERCMD+0x154)): 3D sync write pending. From `ui323DSyncWriteOpsPendingVal` (1, sgx545-ce).
- `transfer_cmd_shared.sync_3d_write_ops_complete_dev_vaddr` G1024 (TRANSFERCMD_SHARED+0xac
  (TRANSFERCMD+0x158)): 3D sync write-complete addr. From `s3DSyncWriteOpsCompleteDevVAddr` (1,
  sgx545-ce).
- `transfer_cmd_shared.sync_3d_read_ops_pending_val` G1023 (TRANSFERCMD_SHARED+0xb0
  (TRANSFERCMD+0x15c)): 3D sync read pending. From `ui323DSyncReadOpsPendingVal` (1, sgx545-ce).
- `transfer_cmd_shared.sync_3d_read_ops_complete_dev_vaddr` G1022 (TRANSFERCMD_SHARED+0xb4
  (TRANSFERCMD+0x160)): 3D sync read-complete addr. From `s3DSyncReadOpsCompleteDevVAddr` (1,
  sgx545-ce).
- `transfer_cmd_shared.num_status_vals` G1020 (TRANSFERCMD_SHARED+0xb8 (TRANSFERCMD+0x164)): status
  update count. From `ui32NumStatusVals` (1, sgx545-ce).
- `transfer_cmd_shared.ctl_status_info` G1016 (TRANSFERCMD_SHARED+0xbc (TRANSFERCMD+0x168)): status
  updates [4] incl. the fence. From `sCtlStatusInfo` (1, sgx545-ce).

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
- `GEOM_FLAGS.BIT2` G0630 (CMDTA+0x004 bit2 (0x4)): inferred reading (unconfirmed): tested together
  with GEOM_FLAGS.FIRST_KICK (mask 0x5): when either is set the EDM keeps the stores that link the
  command's render details into the context; no run sets the bit alone [infer]. From
  `GEOM_FLAGS.BIT2` (ours, resgx545).
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
- `CMD_TA_CTRL_FLAGS.READY` G1117 (CMDTA+0x058 bit0): shared block complete; set last (0x1). From
  `SGXMKIF_CMDTA_CTRLFLAGS_READY` (1, sgx545-ce).
- `PB_FLAGS.INIT_PAGE_TABLE` G0481 (HWPBDESC+0x000 bit0 (0x1)): rebuild the DPM page table and free
  list from the initial values and the block list [infer]. From `PB_FLAGS.INIT_PAGE_TABLE` (ours,
  resgx545).
- `PB_FLAGS.THRESHOLD_UPDATE` G0482 (HWPBDESC+0x000 bit1 (0x2)): reload the thresholds; the EDM
  clears bits 0-1 [infer]. From `PB_FLAGS.THRESHOLD_UPDATE` (ours, resgx545).
- `CONTEXT_FLAGS.NEW` G0357 (HWRENDERCONTEXT/HWTRANSFERCONTEXT+0x000 bit0 (0x1)): new context: at
  its first mapping the EDM clears the bit and invalidates the caches [infer]. From
  `CONTEXT_FLAGS.NEW` (ours, resgx545).
- `CONTEXT_FLAGS.DUMMY_TRANSFER` G0616 (HWRENDERCONTEXT/HWTRANSFERCONTEXT+0x000 bit1 (0x2)):
  transfer context: the EDM clears the bit and takes the dummy (no render) path once [infer]. From
  `CONTEXT_FLAGS.DUMMY_TRANSFER` (ours, resgx545).
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
- `TQ_FLAGS.NO_SYNC_UPDATE` G0971 (TRANSFERCMD+0x0a8 bit0): do not update src/dst syncs (0x1). From
  `SGXMKIF_TQFLAGS_NOSYNCUPDATE` (1, sgx545-ce).
- `TQ_FLAGS.KEEP_PENDING` G0970 (TRANSFERCMD+0x0a8 bit1): kernel does not bump pending counts (0x2).
  From `SGXMKIF_TQFLAGS_KEEPPENDING` (1, sgx545-ce).
- `TQ_FLAGS.TA_TQ_SYNC` G0972 (TRANSFERCMD+0x0a8 bit2): update the TA-side TQ sync
  (transfer_cmd_shared.sync_ta_*) (0x4). From `SGXMKIF_TQFLAGS_TATQ_SYNC` (1, sgx545-ce).
- `TQ_FLAGS.3D_TQ_SYNC` G0968 (TRANSFERCMD+0x0a8 bit3): update the 3D-side TQ sync
  (transfer_cmd_shared.sync_3d_*) (0x8). From `SGXMKIF_TQFLAGS_3DTQ_SYNC` (1, sgx545-ce).
- `TQ_FLAGS.DUMMY_TRANSFER` G0969 (TRANSFERCMD+0x0a8 bit5): no render, sync/status only (0x20). From
  `SGXMKIF_TQFLAGS_DUMMYTRANSFER` (1, sgx545-ce).
- `FRAG_FLAGS.NO_RENDER` G0237 (render flags bit0 (0x1)): skips the render: the scene's memory is
  freed at its last TA end and the render details complete without a render [infer]. From
  `FRAG_FLAGS.NO_RENDER` (ours, resgx545).
- `FRAG_FLAGS.ABORT` G0231 (render flags bit1 (0x2)): complete the command without running it
  [infer]. From `FRAG_FLAGS.ABORT` (ours, resgx545).
- `FRAG_FLAGS.BIT10` G0232 (render flags bit10 (0x400)): inferred reading (unconfirmed): count this
  render in its RT data set: at the render's completion the EDM adds one to the executed count of
  the set render details word 54 points at; without it the render is drawn and adds nothing, so the
  set's cleanup completes only if the host's pending count leaves the render out too (the kernel's
  does since it counts each kick); set by the client on the scene's last kick [infer]. From
  `FRAG_FLAGS.BIT10` (ours, resgx545).
- `FRAG_FLAGS.BIT2` G0233 (render flags bit2 (0x4)): inferred reading (unconfirmed): Bit 2 of the
  render flags word: when each job ends with its render, set or clear it changed no image; after the
  render it keeps TA3DCtl dword 20, the DPM slot's RT data, as NO_DEALLOCATE does; a later render
  with it clear clears the word, and a new context at the same addresses renders exactly and clears
  it; a context at another address is not tried. From `FRAG_FLAGS.BIT2` (ours, resgx545).
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

### function

- `DevInitSGXPart2KM` G1118: kernel side of SGXDevInitPart2. From `DevInitSGXPart2KM` (1,
  sgx545-ce).
- `SGXCleanupRequest` G1125: SGXMKIF_CMD_CLEANUP + wait. From `SGXCleanupRequest` (1, sgx545-ce).
- `SGXDevInitPart2` G1126: srvinit: hand init info to kernel. From `SGXDevInitPart2` (2,
  cdv-libsrv_um).
- `SGXDoKickKM` G1127: kernel side of SGXKickTA. From `SGXDoKickKM` (1, sgx545-ce).
- `SGXGetInfoForSrvinitKM` G1128: kernel side of SGXGetInfoForSrvInit. From `SGXGetInfoForSrvinitKM`
  (1, sgx545-ce).
- `SGXGetMiscInfoKM` G1129: kernel side of SGXGetMiscInfo. From `SGXGetMiscInfoKM` (1, sgx545-ce).
- `SGXScheduleCCBCommandKM` G1130: queue a kernel CCB command. From `SGXScheduleCCBCommandKM` (1,
  sgx545-ce).
- `SGXScheduleProcessQueuesKM` G1131: kernel side of SGXScheduleProcessQueues. From
  `SGXScheduleProcessQueuesKM` (1, sgx545-ce).

### struct

- `hw_2d_context` G1140: HW 2D context; no 2D core on SGX545. From `SGXMKIF_HW2DCONTEXT` (1,
  intel-ctp-santos10).
- `device_sync_object` G0101 (0x10): pending values + complete-counter addresses of one sync. From
  `PVRSRV_DEVICE_SYNC_OBJECT` (1, sgx545-ce).
- `misc_info_features` G0113 (0x1c at MISC+0x04): core/DDK identification returned by GETMISCINFO.
  From `PVRSRV_SGX_MISCINFO_FEATURES` (1, sgx545-ce).
- `cmd_ta_shared` G0663 (0x1e0 at CMDTA+0x058): kernel-written sync/status block of the TA command.
  From `SGXMKIF_CMDTA_SHARED` (1, sgx545-ce).
- `kernel_ccb` G0109 (0x2000): kernel CCB: 256 commands. From `PVRSRV_SGX_KERNEL_CCB` (1,
  sgx545-ce).
- `ccb_kick` G1134 (0x22c (i386)): bridge payload of SGX_DOKICK (kernel-side kick of a CMDTA). From
  `SGX_CCB_KICK` (1, sgx545-ce).
- `cmd_ta` G1136 (0x2b0, ~ CMDTA): TA command structure proper; CMDTA_SHARED is part of it. From
  `SGXMKIF_CMDTA` (1, emgd-linux); `rogue_fwif_cmd_geom` (3, linux-imagination).
- `misc_info_struct_sizes` G1147 (0x34): structure sizes reported by GETMISCINFO. From
  `SGX_MISCINFO_STRUCT_SIZES` (1, sgx545-ce).
- `host_ctl` G0010 (0x44): host control block (init/power/cleanup status, timers). From
  `SGXMKIF_HOST_CTL` (1, sgx545-ce).
- `hw_render_context` G1141 (0x44, ~ HWRENDERCONTEXT): HW render context (suspend/resume target).
  From `SGXMKIF_HWRENDERCONTEXT` (1, intel-ctp-santos10); `rogue_fwif_fwrendercontext` (3,
  linux-imagination).
- `transfer_cmd` G0114 (0x4c8, ~ TRANSFERCMD): transfer command structure proper; holds
  TRANSFERCMD_SHARED. From `SGXMKIF_TRANSFERCMD` (1, emgd-linux); `rogue_fwif_cmd_transfer` (3,
  linux-imagination).
- `transfer_kick` G1150 (0x50 (i386)): bridge payload of SGX_SUBMITTRANSFER. From
  `PVRSRV_TRANSFER_SGX_KICK` (1, sgx545-ce).
- `misc_info` G0110 (0x54): misc-info buffer (hKernelSGXMiscMemInfo). From
  `PVRSRV_SGX_MISCINFO_INFO` (1, sgx545-ce).
- `ccb_ctl` G0095 (0x8, ~ PVRSRV_SGX_CCB_CTL): CCB control: write and read offsets (kernel and
  client CCBs). From `PVRSRV_SGX_CCB_CTL` (1, sgx545-ce); `rogue_fwif_ccb_ctl` (3,
  linux-imagination).
- `hw_transfer_context` G0102 (0xb4, ~ HWTRANSFERCONTEXT): HW transfer context. From
  `SGXMKIF_HWTRANSFERCONTEXT` (1, intel-ctp-santos10); `rogue_fwif_fwtransfercontext` (3,
  linux-imagination).
- `transfer_cmd_shared` G1015 (0xdc at TRANSFERCMD+0x0ac): kernel-written sync/status block of the
  transfer command. From `SGXMKIF_TRANSFERCMD_SHARED` (1, sgx545-ce).
- `ta3d_ctl` G0024 (0xec (hKernelSGXTA3DCtlMemInfo)): TA/3D control block of the EDM. From
  `sTA3DCtl` (1c, emgd-linux).
- `dpm_state` G1089 (DPM_STATE (0x88 of the state page)): an RT data's DPM state page (its state
  word, CR_DPM_STATE_BASE0) as the DPM leaves it after a partial render: sixteen macrotile page
  lists, then the global list (DPM_STATE_LIST). From `dpm_state` (ours, resgx545).
- `pb_block` G0559 (pb_block (0x10)): GPL name of the HW PB block allocation. From
  `psHWBlockKernelMemInfo` (1, sgx545-ce).
- `hw_pb_desc` G0517 (~ HWPBDESC): Rogue FW free list = parameter-buffer pages. From
  `rogue_fwif_freelist` (3, linux-imagination).
- `hw_render_details` G1143 (~ HWRENDERDETAILS): Rogue fragment (3D) command. From
  `rogue_fwif_cmd_frag` (3, linux-imagination).
- `hw_rt_data` G1144 (~ HWRTDATA/HWRTDATASET): Rogue FW render-target data (PM state, tail pointers,
  region headers). From `rogue_fwif_hwrtdata` (3, linux-imagination).

## 4. State words, ports and instruction-level terms

### bitfield

- `ISP0.TWO_SIDED` G0633 (isp0 bit 11): (Rogue) two-sided stencil testing. From `two_sided` (3,
  mesa-csbgen); `ISP0.TWO_SIDED` (ours, resgx545).
- `EMIT2.BIT28` G1039 (EMIT2 (emit2 src0) [28]): inferred reading (unconfirmed): set, the
  end-of-tile emit stores the image rotated by 90 degrees (bits 29:28 at 1): on a 64x64 target the
  pixel stored at (X, Y) is the one from (Y, 63 - X); with bit 29 as well (3) the rotation is by 270
  degrees (E382). From `EMIT2.BIT28` (ours, resgx545).
- `EMIT2.BIT29` G1040 (EMIT2 (emit2 src0) [29]): inferred reading (unconfirmed): set, the
  end-of-tile emit stores the image rotated by 180 degrees (bits 29:28 at 2): on a 64x64 target the
  pixel stored at (X, Y) is the one from (63 - X, 63 - Y); with bit 28 as well (3) the rotation is
  by 270 degrees (E382). From `EMIT2.BIT29` (ours, resgx545).
- `EMIT2.BIT30` G1041 (EMIT2 (emit2 src0) [30]): inferred reading (unconfirmed): set, the
  end-of-tile emit stores each 32x16 tile downscaled by 2 in x and y into the tile's top-left 16x8
  pixels, each pixel the 2x2 box average of its four (each byte summed, divided by 4, the remainder
  dropped), and leaves the rest of the tile unwritten [infer]. From `EMIT2.BIT30` (ours, resgx545).
- `T0.BITS20_19` G0273 (T0 [20:19] (twiddled textures)): bits 3:2 of T0.MAX_LEVEL (20:17), the
  highest mip level read [infer]. From `T0.BITS20_19` (ours, resgx545).
- `T0.BITS26_21` G0274 (T0 [26:21] (twiddled textures)): an LOD bias of (value - 63) / 8 added
  before the nearest level is taken: 0x3f (the closed driver's value) is no bias, 0x22 or less keeps
  LOD 4 at level 0 (on stride textures these bits are T0.STRIDE) [infer]. From `T0.BITS26_21` (ours,
  resgx545).
- `T0.BIT27` G1045 (T0 [27]): inferred reading (unconfirmed): changes the form texels are read in:
  set in a copy, every pixel takes a value of no source texel (0x00000000, 0x0cf90cf9, 0x10f910f9,
  ...) [infer]. From `T0.BIT27` (ours, resgx545).
- `T0.NO_MIPMAPS` G0278 (T0 bit 18): inferred reading (unconfirmed): bit 1 of T0.MAX_LEVEL (20:17),
  not a mipmap disable: values of the field with this bit set (2, 3, 6, 7, ...) read the chain up to
  that level [infer]. From `T0.NO_MIPMAPS` (ours, resgx545).
- `T3.BIT10` G1047 (T3 [10]): inferred reading (unconfirmed): set in a copy, every pixel reads texel
  (0, 0); what it selects is not decoded [infer]. From `T3.BIT10` (ours, resgx545).
- `T3.BIT14` G1048 (T3 [14]): inferred reading (unconfirmed): set in a copy, pixel (x, y) reads
  texel (x + 32, y + x), past the source at the sentinel; what it selects is not decoded [infer].
  From `T3.BIT14` (ours, resgx545).
- `T3.CMP_MODE` G0642 (T3 [31:29]): the comparison of smp.pcf/.pcff16 against the reference: 0
  never, 1 less, 2 equal, 3 less or equal, 4 greater, 5 greater or equal, 6 not equal, 7 always.
  From `cmp_mode` (3, mesa-csbgen).
- `VDM_STATE1.BIT12` G0500 (VDM_STATE1 bit 12): set: the TA writes no object for the state's
  primitives and leaves the regions empty, as with bits 11:9 at 0 [infer]. From `VDM_STATE1.BIT12`
  (ours, resgx545).
- `VDM_STATE1.BIT18` G0501 (VDM_STATE1 bit 18): set: the job hangs; what it does is not established
  [infer]. From `VDM_STATE1.BIT18` (ours, resgx545).
- `VDM_STATE1.BIT25` G0502 (VDM_STATE1 bit 25): clearing it changes neither the TA's output nor the
  image of one triangle; what it does is not established [infer]. From `VDM_STATE1.BIT25` (ours,
  resgx545).
- `PDS_MOV128.LASTPAIR` G1151 (mov128 [15]): inferred reading (unconfirmed): Bit 15 of a mov128
  word, which the assembler spells `, lastpair`: set, the instruction writes to both halves of its
  destination row the ds0 pair that the last mov32 or movs read from a data row, whatever its source
  row and swap (E379); measured only after the instructions E379 lists [infer]. From
  `PDS_MOV128.LASTPAIR` (ours, resgx545).
- `OUTSEL.PLANES` G0252 (outsel [7:0]): inferred reading (unconfirmed): user clip-plane enables, bit
  N plane N: each enabled plane removes the triangle whole while its held state is outside: fdpc on
  cpN sets the state, and it outlives the job; the vertex's distance dwords after the position
  (plane 0 the first, planes 0 and 1 the first two) decided in one session and decided nothing in
  another [infer]. From `OUTSEL.PLANES` (ours, resgx545).

### enum

- `ADDRMODE` G0608: (Rogue) texture address modes REPEAT, FLIP, CLAMP_TO_EDGE...; on SGX545 the T0
  wrap fields: 0 repeat, 1 mirror, 2 clamp, 3 mirror once (T0.ADDRMODE_U, T0.ADDRMODE_V). From
  `ADDRMODE` (3, mesa-csbgen).
- `PORT.DOUTC` G0637: (Rogue) compute data-out port; on SGX545 the port value it would name is open.
  From `PVR_ROGUE_PDSINST_DOUT_DST_DOUTC` (3, mesa-pds-defs).
- `HEAP.PIXELSHADER` G0631 (0xF4000000): pixel USE code heap base (USE_CODE_BASE_0). From
  `SGX_PIXELSHADER_HEAP_BASE` (1, sgx545-ce).
- `PDS_PRIMARY.USE_KICK` G0634 (PDS primary program): the primary pixel PDS program of the transfer
  templates (PDS_PRIM): it starts the USE program its first dword, a DOUTU word, names [infer]. From
  `PDS_PRIMARY.USE_KICK` (ours, resgx545).
- `PDS_SECONDARY.USE_KICK` G0635 (PDS secondary program): the secondary pixel PDS program of the
  transfer templates (PDS_SEC): it starts the USE program its first dword, a DOUTU word, names
  [infer]. From `PDS_SECONDARY.USE_KICK` (ours, resgx545).
- `TEXTYPE.STRIDE` G0288 (T1 TEXTYPE 6): strided texture: rows a stride apart (T0.STRIDE), sampled
  clamped to the edge [infer]. From `TEXTYPE.STRIDE` (ours, resgx545).
- `TEXFORMAT` G0286 (TEXFORMAT values): texel format enum: on SGX545 2 RGBA4444, 4 RGBA5551, 5
  RGB565, 12 BGRA8888 (ARGB8888 in memory), 13 RGBA8888, 17 RGBA half-float, 18 float32 (RGBA,
  luminance, depth), 23 PVRTC 2 bpp, 24 PVRTC 4 bpp, 27 ETC1, 28 YUYV, 29 UYVY; with T0.BIT30 set 26
  reads one byte per texel (Rogue values differ). From `FORMAT` (3, mesa-csbgen).
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
- `PASS_TYPE` G1119 (isp0 [27:25] values): OPAQUE, TRANSLUCENT, PUNCH_THROUGH, VIEWPORT_OBJECT....
  From `PASSTYPE` (3, mesa-csbgen).
- `PACKMODE` G0253 (sideband PACKMODE values): PBE pack formats (Rogue values differ); on SGX545 0
  is ARGB8888, 3 RGB565. From `PACKMODE` (3, mesa-csbgen).
- `USE.NUM_HW_SPECIAL_CONSTS` G0289 (special constant bank): number of hardware constants. From
  `USEASM_NUM_HW_SPECIAL_CONSTS` (2, cdv-libusc).

### field

- `DOUTI.SHADEMODEL` G0206: (Rogue) iteration shade model; placed on SGX545 as DOUTI0.SHADEMODEL.
  From `PVR_ROGUE_PDSINST_DOUT_FIELDS_DOUTI_SRC_SHADEMODEL` (3, mesa-pds-defs).
- `DOUTD1.OFFSET` G1096 (DOUTD1 [19:8]): the destination attribute dword. From `DOUTD1.OFFSET`
  (ours, resgx545).
- `DOUTD1.STRIDE` G1098 (DOUTD1 [29:22], doutd word 1 [29:22]): inferred reading (unconfirmed):
  distance between burst lines - 1 [infer]. From `DOUTD1.STRIDE` (ours, resgx545).
- `DOUTD1.BURST` G1094 (DOUTD1 [3:0]): dwords per line, less one. From `DOUTD1.BURST` (ours,
  resgx545).
- `DOUTD1.LINES` G1095 (DOUTD1 [7:4]): lines, less one. From `DOUTD1.LINES` (ours, resgx545).
- `DPM_STATE_LIST.HEAD` G1086 (DPM_STATE_LIST word 0 [15:0]): the list's first page; a list of one
  page has its head and tail equal. From `DPM_STATE_LIST.HEAD` (ours, resgx545).
- `DPM_STATE_LIST.PAGE_COUNT` G1087 (DPM_STATE_LIST word 0 [31:16]): the pages in the list. From
  `DPM_STATE_LIST.PAGE_COUNT` (ours, resgx545).
- `DPM_STATE_LIST.TAIL` G1088 (DPM_STATE_LIST word 1 [15:0]): the list's last page; a list of one
  page has its head and tail equal. From `DPM_STATE_LIST.TAIL` (ours, resgx545).
- `EMIT0.MINCLIP_X` G1035 (EMIT0 (emit1 src0) [12:0]): clip rectangle min x. From `minclip_x` (3,
  mesa-csbgen).
- `EMIT2.BITS15_8` G0226 (EMIT2 (emit2 src0) [15:8]): inferred reading (unconfirmed): a count, in
  units of four pixels, of what an emit stores of its 32x16 tile: 0 stores nothing, every odd value
  hangs the job, an even value v up to 0x80 stores 4v pixels of each tile, and above 0x80 the tile
  is stored with other values over it. Measured: 0x80 in every closed program and capture [infer].
  From `EMIT2.BITS15_8` (ours, resgx545).
- `EMIT3.ADDRESS` G1043 (EMIT3 (emit2 src1) [31:2]): surface address >> 2 (the surface base; the PBE
  adds the tile offset). From `address_low` (3, mesa-csbgen).
- `ISP1.LINE_WIDTH` G0472 (ISP1 [15:8]): line width in pixels, unsigned 4.4 fixed point [infer].
  From `ISP1.LINE_WIDTH` (ours, resgx545).
- `ISP1.VISREG` G0248 (ISP1 [2:0]): index of the visibility counter the object counts into (with
  ISP1.VISTEST). From `visreg` (3, mesa-csbgen).
- `ISP1.VALID_ID` G0473 (ISP1 [31:26]): the object's validation ID: an opaque or translucent object
  is drawn only when it is at least CR_ISP_CTL.VALID_ID. From `ISP1.VALID_ID` (ours, resgx545).
- `ISP1.CMASK` G1099 (ISP1 [7:4]): the colour write mask: bit 7 red, 6 green, 5 blue, 4 alpha, from
  glColorMask. From `ISP1.CMASK` (ours, resgx545).
- `PDS_SIZE.BITS17_16` G0254 (PDS_SIZE [17:16]): inferred reading (unconfirmed): a size or count of
  output register banks: at 0, 1 and 2 the triangle's o1-o3 land elsewhere while o0 does not change,
  3 the plain value [infer]. From `PDS_SIZE.BITS17_16` (ours, resgx545).
- `PDS_SIZE.BITS24_18` G0636 (PDS_SIZE [24:18]): inferred reading (unconfirmed): bits 24:18 of the
  PDS size word; at 4, 1 and 0 a fill's secondary program still passes all sixteen douta words, so
  what they size is not shown [infer]. From `PDS_SIZE.BITS24_18` (ours, resgx545).
- `T0.MINFILTER` G0276 (T0 [11:10]): minification filter: 1 and 2 linear, 0 and 3 nearest. From
  `minfilter` (3, mesa-csbgen).
- `T0.STRIDE` G0279 (T0 [11:9] + [26:17]): stride of a strided texture in dwords - 1: bits 2:0 in T0
  [11:9], bits 12:3 in T0 [26:17]. From `stride` (3, mesa-csbgen).
- `T0.MAGFILTER` G0275 (T0 [13:12]): magnification filter: 1 and 2 linear, 0 and 3 nearest. From
  `magfilter` (3, mesa-csbgen).
- `T0.MAX_LEVEL` G1046 (T0 [20:17] (twiddled textures)): the highest mip level read: 1 to 14 cap the
  level at that value, 0 and 15 read level 0 only; on stride textures these bits are part of
  T0.STRIDE; it holds the older rows T0.BITS20_19 and T0.NO_MIPMAPS. From `T0.MAX_LEVEL` (ours,
  resgx545).
- `T0.ADDRMODE_V` G0271 (T0 [5:3]): T (V) wrap mode: 0 repeat, 1 mirror, 2 clamp, 3 mirror once.
  From `addrmode_v` (3, mesa-csbgen).
- `T0.ADDRMODE_U` G0270 (T0 [8:6]): S (U) wrap mode: 0 repeat, 1 mirror, 2 clamp, 3 mirror once.
  From `addrmode_u` (3, mesa-csbgen).
- `T0.MIPFILTER` G0277 (T0 [9]): filter between mipmap levels: 0 the nearest level (a half rounds
  up), 1 a linear blend of the two levels. From `mipfilter` (3, mesa-csbgen).
- `T1.HEIGHT` G0640 (T1 [11:0] (HEIGHT)): height - 1. From `height` (3, mesa-csbgen).
- `T1.WIDTH` G0641 (T1 [23:12] (WIDTH)): width - 1. From `width` (3, mesa-csbgen).
- `T1.TEXFORMAT` G0280 (T1 [28:24] (TEXFORMAT)): texel format. From `texformat` (3, mesa-csbgen).
- `T1.TEXTYPE` G0281 (T1 [31:29] (TEXTYPE)): texture type. From `textype` (3, mesa-csbgen).
- `T2.TEXADDR` G0282 (T2 [31:2] (TEXADDR)): texture address >> 2. From `texaddr` (3, mesa-csbgen).
- `T3.CONVERT` G0283 (T3 [17:16]): conversion of the fetched texel: 0 none, 1 c10, 2 f16 pairs, 3
  f32 channels [infer]. From `T3.CONVERT` (ours, resgx545).
- `T3.BITS19_18` G1049 (T3 [19:18]): inferred reading (unconfirmed): a scale of the texel
  coordinates: bit 18 reads (2x, 2y), bit 19 (4x, 4y) in a copy [infer]. From `T3.BITS19_18` (ours,
  resgx545).
- `T3.DATA_SIZE` G0284 (T3 [26:23]): inferred reading (unconfirmed): Bits 26:23 of the fourth
  sampler word are named in the sampler sweep but that sweep varied only the conversion fields; the
  sampler data show nothing about this field beyond its name. From `T3.DATA_SIZE` (ours, resgx545).
- `T3.BITS28_27` G1050 (T3 [28:27]): inferred reading (unconfirmed): in a copy, bit 27 reads a
  half-size image packed 32 rows (8 KiB) after the source and bit 28 a quarter-size one 40 rows
  after it, at the source's stride: a level select of strided textures [infer]. From `T3.BITS28_27`
  (ours, resgx545).
- `T3.BITS7_0` G1051 (T3 [7:0]): inferred reading (unconfirmed): a texel offset: bits 7:4 in x and
  3:0 in y, each a signed 4-bit count (single bits move the read by 1, 2, 4 and -8 texels), clamped
  at the texture's edge [infer]. From `T3.BITS7_0` (ours, resgx545).
- `PB_OBJ.RHW` G0487 (TA object TSP data, first dword of each vertex, TA object vertex data):
  inferred reading (unconfirmed): 1/w of the vertex, before its outputs, which are stored undivided
  [infer]. From `PB_OBJ.RHW` (ours, resgx545).
- `PB_OBJ.PDS_WORDS` G0485 (TA object dwords 0-2): the state block's words 3 to 5, the pixel
  program's secondary pointer, size word and primary pointer, copied as given. From
  `PB_OBJ.PDS_WORDS` (ours, resgx545).
- `PB_OBJ.PRIM_LIST` G0486 (TA object, after ISP word 1: 16 bits per primitive, two to a dword): the
  object's primitives: per primitive three 5-bit vertex numbers (bits 4:0, 9:5, 14:10), the object's
  vertices numbered from 16; the last entry repeated to fill an odd count [infer]. From
  `PB_OBJ.PRIM_LIST` (ours, resgx545).
- `PB_OBJ.FORMAT` G1073 (TA object, the dword after the line widths): inferred reading
  (unconfirmed): the object's format word: bits 7:0 the dwords a vertex takes in the object, bits
  15:8 the dwords it iterates; bit 18 with the 1/w output select, bit 19 with the vertex colour; the
  other bits are not shown [infer]. From `PB_OBJ.FORMAT` (ours, resgx545).
- `PB_OBJ.LINE_WIDTHS` G0484 (TA object, the dword after the primitive list): ISP1.LINE_WIDTH in
  both bytes (bits 15:8 and 7:0) [infer]. From `PB_OBJ.LINE_WIDTHS` (ours, resgx545).
- `PB_OBJ.SET_MASKS` G0488 (TA object, the four dwords after the format word): bit i for coordinate
  set i (from 1): sets stored at half precision, sets of one component, sets with z, sets with w
  [infer]. From `PB_OBJ.SET_MASKS` (ours, resgx545).
- `PB_OBJ.ISP_WORDS` G0483 (TA object, the two dwords after the TSP data): ISP words 0 and 1 as the
  state block gives them [infer]. From `PB_OBJ.ISP_WORDS` (ours, resgx545).
- `VDM_STATE1.BITS11_9` G0292 (VDM_STATE1 [11:9]): inferred reading (unconfirmed): Bits 11:9 of the
  state task's second word: 0 removes the 64x64 triangle (4096 background pixels), 1, 3, 4, 5 and 6
  give the baseline image, and 7 hangs some runs of either job and completes others, tiling as 2
  when it completes; the job writes 2. From `VDM_STATE1.BITS11_9` (ours, resgx545).
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
  primitive mask in a further dword), 0x8a the left, 0x8c the right; 0x88 in the two-lines scene,
  also with a further dword in the block (which tiles 0x88 means is not shown); bit 23 is set in
  every word seen [infer]. From `CSTREAM.PRIM_TILES` (ours, resgx545).
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
- `DOUTI0.COMPONENTS` G0627 (douti word 0 [23:22]): the iteration's components less one: 1 to 3
  measured (x; x, y; x, y, 0), the fetch's texel in the dword after them; 4 open [infer]. From
  `DOUTI0.COMPONENTS` (ours, resgx545).
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
- `EMIT0.MINCLIP_Y` G1036 (emit1 src0 [28:16]): clip rectangle min y. From `minclip_y` (3,
  mesa-csbgen).
- `EMIT1.MAXCLIP_X` G1037 (emit1 src1 [12:0]): clip rectangle max x (inclusive). From `maxclip_x`
  (3, mesa-csbgen).
- `EMIT1.MAXCLIP_Y` G1038 (emit1 src1 [28:16]): clip rectangle max y (inclusive). From `maxclip_y`
  (3, mesa-csbgen).
- `EMIT2.LINE_STRIDE` G1042 (emit2 src0 [27:16]): surface line stride, in pairs of pixels less one:
  the row pitch in pixels / 2 - 1, in RGB565 and ARGB8888 alike. From `linestride` (3, mesa-csbgen).
- `VDM_INDEX2.WORD` G0498 (index list, the first trailing word): inferred reading (unconfirmed): the
  index list's first trailing word: an offset of the list's first index in its low bits [infer: 1,
  2, 3, 5 and 0xff fit; 0x0f000000 drops two of five triangles, which such an offset does not
  explain]; bits 31:28 change nothing seen. Measured: 0xf0000000 in every capture. From
  `VDM_INDEX2.WORD` (ours, resgx545).
- `VDM_INDEX3.INDEX_WRAP` G0499 (index list, the second trailing word): the vertex range the indices
  wrap at: 0 leaves them, 5 takes them modulo 5, 1 removes every triangle (as degenerate, a reading)
  and 8 hangs; only these four values were tried [infer]. From `VDM_INDEX3.INDEX_WRAP` (ours,
  resgx545).
- `VDM_INDEX0.PRIMITIVE_TOPOLOGY` G0496 (index-list header [29:26]): primitive type of the index
  list. From `primitive_topology` (3, mesa-csbgen).
- `ISP0.OBJ_TYPE` G0471 (isp0 [17:15]): object type. From `objtype` (3, mesa-csbgen).
- `ISP0.DCMP_MODE` G1060 (isp0 [24:22]): depth compare mode. From `dcmpmode` (3, mesa-csbgen).
- `ISP0.PASS_TYPE` G0245 (isp0 [27:25]): pass type. From `passtype` (3, mesa-csbgen).
- `ISP0.SREF` G1063 (isp0 [7:0]): stencil reference. From `sref` (3, mesa-csbgen).
- `ISP2.SCMP_MASK` G1066 (isp2 [15:8]): stencil compare mask. From `scmpmask` (3, mesa-csbgen).
- `ISP2.SOP3` G1070 (isp2 [18:16]): depth-pass operation. From `sop3` (3, mesa-csbgen).
- `ISP2.SOP2` G1069 (isp2 [21:19]): depth-fail operation. From `sop2` (3, mesa-csbgen).
- `ISP2.SOP1` G1068 (isp2 [24:22]): stencil-fail operation. From `sop1` (3, mesa-csbgen).
- `ISP2.SCMP_MODE` G1067 (isp2 [27:25]): stencil compare. From `scmpmode` (3, mesa-csbgen).
- `ISP2.SW_MASK` G1071 (isp2 [7:0]): stencil write mask. From `swmask` (3, mesa-csbgen).
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
  29 every region of the target when CR_TE_PSG bit 21 is set, 31 the last of the scene [infer]. From
  `REGION_HDR.FLAGS` (ours, resgx545).
- `REGION_HDR.STREAM` G0494 (region header word 1): the region's control-stream block, relative to
  the parameter slot; 0 for an empty region [infer]. From `REGION_HDR.STREAM` (ours, resgx545).
- `SIDEBAND.PACKMODE` G0264 (sideband [5:0]): pixel pack format. From `packmode` (3, mesa-csbgen).
- `SIDEBAND.BITS8_6` G0262 (sideband [8:6] [infer]): inferred reading (unconfirmed): the channel a
  one-channel pack mode stores: in mode 8, 0 alpha, 1 red, 2 green, 3 reads as blue and 4 to 7 give
  the same bytes (both colours run have blue 0x40, so blue is not told apart from another source of
  that byte); no effect seen in the modes that store several channels, under multisampling or on
  several tiles. Measured: 0 in every closed program and capture [infer]. From `SIDEBAND.BITS8_6`
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
- `TERM.CLIP_BOTTOM` G0643 (term [15:0]): last block row; unit open on SGX545: 1 -> 0 drops only the
  bottom 16 rows of a 64x64 target [HW]. From `clip_bottom` (3, mesa-csbgen).
- `TERM.CLIP_RIGHT` G0644 (term [31:16]): last block column, in 32-pixel columns: (width - 1) / 32.
  From `clip_right` (3, mesa-csbgen).
- `VDM_TASK0.MAX_VERTICES` G0294 (vertex-task word 0 [31:28]): the vertices one vertex task takes,
  less one (in index order); 7 for the closed driver's screen-space draws, 15 for compiled shaders;
  0 hangs a larger draw [infer]. From `VDM_TASK0.MAX_VERTICES` (ours, resgx545).
- `VDM_TASK1.OUTPUT_SIZE` G0503 (vertex-task word 1 [31:24]): output vertex size. From
  `vs_output_size` (3, mesa-csbgen).

### flag

- `DOUTI.PERSPECTIVE` G0205: (Rogue) perspective-correct iteration; placed on SGX545 as
  DOUTI0.PERSPECTIVE. From `PVR_ROGUE_PDSINST_DOUT_FIELDS_DOUTI_SRC_PERSPECTIVE` (3, mesa-pds-defs).
- `MIPMAPS_PRESENT` G0250: texture has mipmaps. From `mipmaps_present` (3, mesa-csbgen).
- `PRESENCE.ISP_BACK` G0638 (presence bits 3 (back isp0), 4 (back isp1, by its place), 5 (back
  isp2)): (Rogue) back-face ISP word A present. From `pres_ispctl_ba` (3, mesa-csbgen);
  `PRESENCE.ISP_BACK` (ours, resgx545).
- `ISP1.POLY_OFFSET` G0247 (ISP1 [23]): the object takes the polygon offset; the closed driver sets
  it on every object it draws with GL_POLYGON_OFFSET_FILL and on no other [infer]. From
  `ISP1.POLY_OFFSET` (ours, resgx545).
- `ISP1.VISTEST` G0249 (ISP1 [3]): visibility test: the object's covered pixels count into the
  counter ISP1.VISREG names. From `vistest` (3, mesa-csbgen).
- `FEATURE.SECONDARY_REQUIRES_USE_KICK` G0629 (PDS secondary program, DOUTU): a secondary PDS
  program must start a USE task. From `SGX_FEATURE_SECONDARY_REQUIRES_USE_KICK` (1, sgx545-ce).
- `T0.BIT30` G0639 (T0 [30]): inferred reading (unconfirmed): with it TEXFORMAT 26 reads one byte
  per texel, written as grey; without it TEXFORMAT 26 gives values that differ from run to run; no
  other format is tried with it [infer]. From `T0.BIT30` (ours, resgx545).
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
- `ISP0.DWRITE_DISABLE` G1061 (isp0 bit 20): depth write disable. From `dwritedisable` (3,
  mesa-csbgen).
- `ISP0.TAGWRITE_DISABLE` G1064 (isp0 bit 21 (colour write off)): object not forwarded to the TSP.
  From `tagwritedisable` (3, mesa-csbgen).
- `ISP0.SAMPLE_COVERAGE` G0632 (isp0 bit 28): the object covers a pixel when any of eight samples is
  inside: the four of CR_ISP_MULTISAMPLECTL and the four of CR_ISP_SAMPLE_POS; single-sampled only
  (it hangs a 4x render); the pixel centre counted inside on every edge, or in place of
  CR_ISP_MULTISAMPLECTL's samples, takes no part, while a centre sample under the top-left rule
  added to the eight is not excluded; of the top-left tie rule only the long edge's exclusion is
  seen, on a triangle with no horizontal edge [infer]. From `ISP0.SAMPLE_COVERAGE` (ours, resgx545).
- `ISP0.ISP2_PRESENT` G1062 (isp0 bit 8): inferred reading (unconfirmed): ISP word 2 follows
  [infer]. From `ISP0.ISP2_PRESENT` (ours, resgx545).
- `ISP0.BIT9` G1059 (isp0 bit 9): inferred reading (unconfirmed): set in every ISP word 0 the
  library builds; clearing it changes no image of five overlapping copies, so what it selects is not
  shown, and the block's layout does not move with it [infer]. From `ISP0.BIT9` (ours, resgx545).
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
- `SIDEBAND.DITHER` G1044 (sideband bit 10): enable dither. From `dither` (3, mesa-csbgen).
- `SIDEBAND.BIT9` G0261 (sideband bit 9): inferred reading (unconfirmed): marks the emit that
  completes the tile: the PBE counts the emits with it against its tiles. Measured: needed for an
  emit to complete its tile: with it clear the only emit hangs; an extra emit with it set leaves the
  PBE queue one emit behind, with it clear for one job only; not tile-relative addressing [infer].
  From `tilerelative` (3, mesa-csbgen).

### struct

- `ISP0` G0244 (ISP word 0 (isp0)): ISP state word A: depth, pass, object type. From `STATE_ISPA`
  (3, mesa-csbgen).
- `ISP1` G0246 (ISP word 1): inferred reading (unconfirmed): ISP colour-mask and line-width word of
  the MTE state [infer]. From `ISP1` (ours, resgx545).
- `ISP2` G1065 (ISP word 2 (isp2)): ISP stencil word. From `STATE_ISPB` (3, mesa-csbgen).
- `PRESENCE` G1072 (MTE state block presence word (S.2)): presence word: each set bit adds its state
  words. From `STATE_HEADER` (3, mesa-csbgen).
- `PDS_PRIMARY` G1120 (MTE state, after the size word (presence bit 6)): primary pixel PDS program
  pointer (starts the pixel shader). From `STATE_PDS_SHADERBASE` (3, mesa-csbgen).
- `PDS_SECONDARY` G1121 (MTE state, first PDS word (presence bit 6)): secondary (uniform/constant)
  pixel PDS program pointer. From `STATE_PDS_UNIFORMDATABASE` (3, mesa-csbgen).
- `DOUTD1` G1093 (doutd word 1): the second word of a PDS doutd: a two-dimensional copy into the
  USSE attributes. From `DOUTD1` (ours, resgx545).
- `OUTSEL` G0477 (outsel): output selects of the vertex. From `OUTPUT_SEL` (3, mesa-csbgen).
- `PDS_SIZE` G1122 (pds_size): pixel PDS/USC size word. From `STATE_PDS_SIZEINFO1` (3, mesa-csbgen).
- `TERM` G1132 (term): end-of-scene clip words. From `STATE_TERMINATE0` (3, mesa-csbgen).
- `WCLAMP` G0504 (wclamp): W clamp value (float) [infer]. From `WCLAMP` (3, mesa-csbgen).

## 5. Sources

- `emgd-linux` (tier 1): Intel EMGD for Linux, SGX535 kernel side.
- `emgd-psb_regs` (tier 1): Intel's psb_regs.h in EMGD: the SGX535 (Poulsbo) register list (MIT).
- `intel-ctp-k900` (tier 1): Lenovo K900 GPL kernel, Clover Trail+ SGX544MP2, DDK 1.11.
- `intel-ctp-santos10` (tier 1): Samsung's GPL kernel for its santos10 device (Intel Clover Trail+,
  SGX544MP2), DDK 1.9.
- `openpvrsgx-1.9` (tier 1): openpvrsgx archive, DDK 1.9 kernel side.
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
- `patent-US20090058848` (tier 4): published application US20090058848 (Imagination Technologies).
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
