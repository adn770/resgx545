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

## 2. Registers and their fields

### bitfield

- `CR_USE_CODE_BASE_0.ADDR` G0006 (0x0a0c[24:0]): code base address. From `_PSB_CUC_BASE_ADDR_MASK`
  (1c, emgd-psb_regs).
- `CR_USE_CODE_BASE_0.DM` G0007 (0x0a0c[26:25]): data master that owns a USE code base. From
  `EUR_CR_USE_CODE_BASE_DM_00` (1, sgx545-ce); `_PSB_CUC_BASE_DM_MASK` (1c, emgd-psb_regs).

### register

- `CR_USE_CODE_BASE_0` G0005 (0x0a0c): USSE code base 0: address and data master. From
  `EUR_CR_USE_CODE_BASE(X)` (1, sgx545-ce); `EUR_CR_USE_CODE_BASE_0` (1, sgx545-ce);
  `PSB_CR_USE_CODE_BASE(i)` (1c, emgd-psb_regs); `PSB_CR_USE_CODE_BASE0` (1c, emgd-psb_regs).
- `CR_EVENT_OTHER_PDS_EXEC` G0003 (0x0a68): PDS code address of the other-event task. From
  `EUR_CR_EVENT_OTHER_PDS_EXEC` (1c, intel-ctp-santos10).
- `CR_EVENT_OTHER_PDS_DATA` G0002 (0x0a6c): PDS data address of the other-event task. From
  `EUR_CR_EVENT_OTHER_PDS_DATA` (1c, intel-ctp-santos10).
- `CR_PDS_EXEC_BASE` G0004 (0x0ab8): base address of PDS program fetches. From
  `EUR_CR_PDS_EXEC_BASE` (1, sgx545-ce); `PSB_CR_PDS_EXEC_BASE` (1c, emgd-psb_regs).
- `CR_BIF_3D_REQ_BASE` G0001 (0x0cac): 3D requestor base address. From `EUR_CR_BIF_3D_REQ_BASE` (1,
  sgx545-ce); `PSB_CR_BIF_3D_REQ_BASE` (1c, emgd-psb_regs).

## 3. Firmware-interface structures, flags and functions

### field

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
