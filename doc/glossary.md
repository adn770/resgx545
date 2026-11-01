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

### unit

- `Dynamic Parameter Management (DPM)` G0062 (CR_CLKGATECTL.DPM_CLKG): DPM block (its clock gate).
  From `DPM` (1, sgx545-ce); `Parameter Manager` (3, linux-imagination); `DPM` (4,
  patent-US8669987).
- `Image Synthesis Processor (ISP)` G0063 (CR_CLKGATECTL.ISP_CLKG): ISP block (its clock gate). From
  `ISP` (1, sgx545-ce); `ISP` (4, imgtec-sgx-arch-guide-1.0.13); `Hidden Surface Removal unit` (4,
  patent-US8743117).
- `Pixel Back End (PBE)` G0065 (CR_EVENT_STATUS.PIXELBE_END_RENDER): PBE as spelled in register
  names; signals end of render. From `PIXELBE` (1, sgx545-ce); `PBE` (4,
  imgtec-sgx-arch-guide-1.0.13); `Pixel Back End` (4, powervr-docs).
- `Texture and Shading Processor (TSP)` G0066 (CR_CLKGATECTL.TSP_CLKG): TSP block (its clock gate).
  From `TSP` (1, sgx545-ce); `TSP` (4, imgtec-sgx-arch-guide-1.0.13).
- `Tile Accelerator (TA)` G0067 (CR_SOFT_RESET.TA_RESET): TA block (its soft reset). From `TA` (1,
  sgx545-ce); `TA` (4, imgtec-sgx-arch-guide-1.0.13); `Tile Accelerator` (4,
  imgtec-technology-overview-1.0.2e).
- `Universal Scalable Shader Engine (USSE)` G0069 (CR_SOFT_RESET.USE_RESET): USSE block (its soft
  reset); register names use the short abbreviation. From `USE` (1, sgx545-ce); `USSE` (4,
  imgtec-sgx-arch-guide-1.0.8).

## 2. Registers and their fields

### bitfield

- `CR_USE_CODE_BASE_0.ADDR` G0006 (0x0a0c[24:0]): code base address. From `_PSB_CUC_BASE_ADDR_MASK`
  (1c, emgd-psb_regs).
- `CR_USE_CODE_BASE_0.DM` G0007 (0x0a0c[26:25]): data master that owns a USE code base. From
  `EUR_CR_USE_CODE_BASE_DM_00` (1, sgx545-ce); `_PSB_CUC_BASE_DM_MASK` (1c, emgd-psb_regs).

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
- `CR_CACHE_CTRL` G0035 (0x0804): cache control / invalidate. From `PSB_CR_CACHE_CTRL` (1c,
  emgd-psb_regs).
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
- `CR_USE_G0` G0059 (0x0a7c): USSE global value g0. From `PSB_CR_USE_G0` (1c, emgd-psb_regs).
- `CR_USE_G1` G0060 (0x0a80): USSE global value g1. From `PSB_CR_USE_G1` (1c, emgd-psb_regs).
- `CR_USE_TMPREG` G0061 (0x0aac): USSE temporary registers: size and initial value. From
  `PSB_CR_USE_TMPREG` (1c, emgd-psb_regs).
- `CR_PDS_EXEC_BASE` G0004 (0x0ab8): base address of PDS program fetches. From
  `EUR_CR_PDS_EXEC_BASE` (1, sgx545-ce); `PSB_CR_PDS_EXEC_BASE` (1c, emgd-psb_regs).
- `CR_EVENT_KICKER` G0046 (0x0ac4): address the event kicker DMA reads. From `EUR_CR_EVENT_KICKER`
  (1, sgx545-ce).
- `CR_EVENT_TIMER` G0050 (0x0acc): EDM periodic timer: period and enable. From `EUR_CR_EVENT_TIMER`
  (1, sgx545-ce); `PSB_CR_EVENT_TIMER` (1c, emgd-psb_regs).
- `CR_USE0_SERV_EVENT` G0054 (0x0b14): USSE 0 event service-queue status, the EDM task register
  (SGX535 0x0b10). From `PSB_CR_USE0_SERV_EVENT` (1c, emgd-psb_regs).
- `CR_USE1_SERV_EVENT` G0055 (0x0b20): USSE 1 event service-queue status, the EDM task register
  (SGX535 0x0b1c). From `PSB_CR_USE1_SERV_EVENT` (1c, emgd-psb_regs).
- `CR_BIF_CTRL` G0030 (0x0c00): MMU control: pause, invalidate, clear fault. From `EUR_CR_BIF_CTRL`
  (1, sgx545-ce); `PSB_CR_BIF_CTRL` (1c, emgd-psb_regs); `ROGUE_CR_BIF_CTRL` (3, linux-imagination).
- `CR_BIF_INT_STAT` G0034 (0x0c04): MMU fault/interrupt status. From `EUR_CR_BIF_INT_STAT` (1,
  sgx545-ce); `PSB_CR_BIF_INT_STAT` (1c, emgd-psb_regs).
- `CR_BIF_FAULT` G0033 (0x0c08): MMU faulting address and context. From `EUR_CR_BIF_FAULT` (1,
  sgx545-ce); `PSB_CR_BIF_FAULT` (1c, emgd-psb_regs).
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
- `transfer_cmd.bif_3d_req_base` G0025 (TRANSFERCMD+0x018): 3D requestor base. From
  `EUR_CR_BIF_3D_REQ_BASE` (1, sgx545-ce).
- `transfer_cmd.event_pixel_pds_code` G0026 (TRANSFERCMD+0x024): end-of-tile PDS program. From
  `event_pixel_pds_code` (3, linux-imagination).
- `transfer_cmd.pds_exec_base` G0027 (TRANSFERCMD+0x03c): PDS execution base. From
  `EUR_CR_PDS_EXEC_BASE` (1, sgx545-ce).

### struct

- `host_ctl` G0010 (0x44): host control block (init/power/cleanup status, timers). From
  `SGXMKIF_HOST_CTL` (1, sgx545-ce).
- `ta3d_ctl` G0024 (0xec (hKernelSGXTA3DCtlMemInfo)): TA/3D control block of the EDM. From
  `sTA3DCtl` (1c, emgd-linux).

## 4. State words, ports and instruction-level terms

### enum

- `PORT.DOUTU` G0009 (doutu port): start a USC task. From `PVR_ROGUE_PDSINST_DOUT_DST_DOUTU` (3,
  mesa-pds-defs).

### field

- `DOUTU0.TEMPS` G0008 (doutu U0 [31:24]): temporaries to allocate, in units of 4. From
  `PVR_ROGUE_PDSINST_DOUT_FIELDS_DOUTU_SRC0_TEMPS` (3, mesa-pds-defs).

## 5. Sources

- `emgd-linux` (tier 1): Intel EMGD for Linux, SGX535 kernel side.
- `emgd-psb_regs` (tier 1): Intel's psb_regs.h in EMGD: the SGX535 (Poulsbo) register list (MIT).
- `intel-ctp-santos10` (tier 1): Samsung's GPL kernel for its santos10 device (Intel Clover Trail+,
  SGX544MP2), DDK 1.9.
- `sgx545-ce` (tier 1): Intel's GPL DDK 1.7 kernel module for Cedarview, our core.
- `linux-imagination` (tier 3): Imagination's Rogue kernel driver, drivers/gpu/drm/imagination.
- `mesa-pds-defs` (tier 3): Mesa src/imagination/vulkan/pds: Rogue PDS instructions (MIT).
- `imgtec-sgx-arch-guide-1.0.13` (tier 4): Imagination's PowerVR Series 5 SGX Architecture Guide for
  Developers 1.0.13 (2012, public).
- `imgtec-sgx-arch-guide-1.0.8` (tier 4): Imagination's PowerVR Series5 Graphics SGX architecture
  guide for developers 1.0.8 (2011, public).
- `imgtec-technology-overview-1.0.2e` (tier 4): Imagination's PowerVR Technology Overview 1.0.2e
  (2010).
- `patent-US7324115` (tier 4): patent US7324115 (Imagination Technologies).
- `patent-US8669987` (tier 4): patent US8669987 (Imagination Technologies).
- `patent-US8743117` (tier 4): patent US8743117 (Imagination Technologies).
- `powervr-docs` (tier 4): Imagination's public PowerVR architecture guides.
