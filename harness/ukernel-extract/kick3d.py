#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The layouts of the structures of the TA/3D kick.

This module names the fields of the structures a kick involves. kickwalk.py, part of the 3D
capture tooling, decodes a captured kick and walks its pointers with them; edmtrace.py and
edm_dataflow.py use the layouts for offsets and pointer typing; a structure with no layout
here is traced by offset.

Two kinds of layout, all 32-bit:

- The kernel-side structures, from sgx545-ce (the GPL kernel module of Cedarview) for its
  build configuration: SUPPORT_SGX_NEW_STATUS_VALS on (sgx545-ce `Kbuild`:111),
  SUPPORT_SGX_GENERALISED_SYNCOBJECTS, SUPPORT_SID_INTERFACE, PDUMP and NO_HARDWARE off.
  Counts are sgx545-ce `src/include4/sgxapi_km.h`:83-91 (32 TA and 4 3D status values,
  8 source syncs). They keep the kernel's names.
- The client structures, which no lawful tree defines: the TA command, its TA register block,
  the render details with their 3D register block, the RT data and RT data set, the HW render
  context, the PB descriptor and a PB block; and the EDM's TA/3D control block, where the kicks
  record the job each pipe runs. Every field has our own name, at the offset an evidence record
  or a glossary row gives (the comment of each structure names them); a word no record reaches
  is unnamed padding (pad_0x<offset>). A structure's size is the one the microkernel reports
  (SGX_MISCINFO_STRUCT_SIZES, E001), or what a record shows (the control block's 0xec, E002).

The flag tables (FLAGS) name only the bits a record or a glossary row names; flag_names()
prints any other bit as hex.
"""
from __future__ import annotations

import struct


# A field is (name, dwords) for scalars, (name, dwords, count) for arrays of
# multi-dword elements, or (name, [fields], count) for nested structures.

# --- kernel-side structures (sgx545-ce) -----------------------------------------------------

# PVRSRV_DEVICE_SYNC_OBJECT (sgx545-ce `src/services4/include/servicesint.h`:164-171):
#   ui32ReadOpsPendingVal, sReadOpsCompleteDevVAddr, ui32WriteOpsPendingVal,
#   sWriteOpsCompleteDevVAddr
DEVSYNC = 4
# CTL_STATUS (sgx545-ce `src/include4/sgxapi_km.h`:187-191): sStatusDevAddr, ui32StatusValue
CTL_STATUS = 2
# SGX_INTERNEL_STATUS_UPDATE (sgx545-ce `src/services4/include/sgxinfo.h`:228-236):
#   CTL_STATUS + hKernelMemInfo
STATUS_UPDATE = 3

# SGXMKIF_COMMAND (sgx545-ce `src/services4/include/sgx_mkif_km.h`:49-54)
COMMAND = [("ui32ServiceAddress", 1), ("ui32CacheControl", 1), ("ui32Data", 1, 6)]

# SGX_CCB_KICK (sgx545-ce `src/services4/include/sgxinfo.h`:239-337)
CCB_KICK = [
    ("sCommand", COMMAND, 1), ("hCCBKernelMemInfo", 1), ("ui32NumDstSyncObjects", 1),
    ("hKernelHWSyncListMemInfo", 1), ("pahDstSyncHandles", 1), ("ui32NumTAStatusVals", 1),
    ("ui32Num3DStatusVals", 1), ("asTAStatusUpdate", STATUS_UPDATE, 32),
    ("as3DStatusUpdate", STATUS_UPDATE, 4), ("bFirstKickOrResume", 1), ("bLastInScene", 1),
    ("ui32CCBOffset", 1), ("ui32NumSrcSyncs", 1), ("ahSrcKernelSyncInfo", 1, 8),
    ("bTADependency", 1), ("hTA3DSyncInfo", 1), ("hTASyncInfo", 1), ("h3DSyncInfo", 1),
    ("hDevMemContext", 1),
]

# SGXMKIF_CMDTA_SHARED (sgx545-ce `src/services4/include/sgx_mkif_km.h`:115-155); its size,
# 0x1e0, is the one the microkernel reports (SGX_MISCINFO_STRUCT_SIZES, initinfo.py)
CMDTA_SHARED = [
    ("ui32CtrlFlags", 1), ("ui32NumTAStatusVals", 1), ("ui32Num3DStatusVals", 1),
    ("ui32TATQSyncWriteOpsPendingVal", 1), ("sTATQSyncWriteOpsCompleteDevVAddr", 1),
    ("ui32TATQSyncReadOpsPendingVal", 1), ("sTATQSyncReadOpsCompleteDevVAddr", 1),
    ("ui323DTQSyncWriteOpsPendingVal", 1), ("s3DTQSyncWriteOpsCompleteDevVAddr", 1),
    ("ui323DTQSyncReadOpsPendingVal", 1), ("s3DTQSyncReadOpsCompleteDevVAddr", 1),
    ("ui32NumSrcSyncs", 1), ("asSrcSyncs", DEVSYNC, 8), ("sTA3DDependency", DEVSYNC, 1),
    ("sCtlTAStatusInfo", CTL_STATUS, 32), ("sCtl3DStatusInfo", CTL_STATUS, 4),
]

# SGXMKIF_HWDEVICE_SYNC_LIST (sgx545-ce `src/services4/include/sgx_mkif_km.h`:213-219)
DEVICE_SYNC_LIST = [("sAccessDevAddr", 1), ("ui32NumSyncObjects", 1), ("asSyncData", DEVSYNC, 1)]

# --- client structures (our names over the records' offsets) ------------------------------

# The TA register block: the TA kick writes the command's dwords 142 to 169 to these
# registers, one str each, in this order (E159). A word is named after the register it lands
# in (the glossary's register term, without CR_); cmd_ta.* rows of the glossary name the same
# words (E182, E183, E197).
TA_REGISTER_WRITES = [
    (0x0204, "te_aa"), (0x0208, "te_mtile1"), (0x020C, "te_mtile2"), (0x0210, "te_screen"),
    (0x0214, "te_macrotile_stride"), (0x0218, "te_psg"), (0x0238, "vdm_ctrl_stream_base"),
    (0x023C, "mte_ctrl"), (0x021C, "te_psgregion_addr"), (0x0220, "te_tpc_addr"),
    (0x0240, "mte_rhw_min"), (0x0244, "mte_rhw_clamp"), (0x0248, "ppp_screen"),
    (0x0A04, "use_reg_0a04"), (0x0AA0, "use_reg_0aa0"), (0x0C90, "bif_ta_req_base"),
    (0x02B0, "ta_reg_02b0"), (0x02D4, "ta_reg_02d4"), (0x02D0, "ta_reg_02d0"),
    (0x02B4, "ta_reg_02b4"), (0x0324, "reg_0324"), (0x0368, "reg_0368"), (0x0364, "reg_0364"),
    (0x0370, "reg_0370"), (0x0374, "reg_0374"), (0x074C, "dpm_reg_074c"),
    (0x02A8, "te_reg_02a8"), (0x0230, "mte_multisamplectl"),
]
TA_REGISTERS = [(name, 1) for _addr, name in TA_REGISTER_WRITES]

# The 3D register block, render details dwords 0 to 51: the 3D kick writes them to these
# registers, one str each, in this order (E163; its size, 0xd0, is the microkernel's). A word
# is named as the glossary's hw_render_details.* row at its offset where there is one, else
# after the register it lands in (the register term without CR_, or reg_<address> for the two
# registers the glossary has no row for).
REGISTER_3D_WRITES = [
    (0x0CAC, "bif_3d_req_base"), (0x0CB0, "bif_zls_req_base"), (0x0400, "reg_0400"),
    (0x0414, "isp_ctl"), (0x042C, "isp_msaa"), (0x041C, "poly_offset_units"),
    (0x0420, "poly_offset_factor"), (0x0424, "poly_offset_clamp"),
    (0x0408, "isp_region_header_base"), (0x0148, "reg_0148"),
    (0x050C, "isp_partial_region_base"),
    (0x0480, "isp_zlsctl"), (0x0484, "zload_base"), (0x0488, "zstore_base"),
    (0x048C, "stencil_load_base"), (0x0490, "stencil_store_base"),
    (0x04B8, "isp_bgobjdepth"), (0x04BC, "reg_04bc"), (0x04C4, "reg_04c4"),
    (0x0520, "isp_sample_pos"),
    (0x04C8, "isp_multisamplectl"), (0x04DC, "isp_reg_04dc"), (0x0800, "reg_0800"),
    (0x0A5C, "event_pixel_pds_code"), (0x0A60, "event_pixel_pds_data"),
    (0x0A64, "event_pixel_pds_info"),
    (0x0418, "isp_line_sample_pos"), (0x0A84, "use_coeffs0_a"), (0x0A88, "use_coeffs0_b"),
    (0x0A8C, "use_coeffs0_bias"), (0x0A90, "use_coeffs1_a"), (0x0A94, "use_coeffs1_b"),
    (0x0A98, "use_coeffs1_bias"), (0x0B24, "use_coeffs2_a"), (0x0B28, "use_coeffs2_b"),
    (0x0B2C, "use_coeffs2_bias"), (0x0A9C, "use_coeffs_mode"),
    (0x0820, "tpu_yuv_csc0_0"), (0x0824, "tpu_yuv_csc0_1"), (0x0828, "tpu_yuv_csc0_2"),
    (0x082C, "tpu_yuv_csc0_3"), (0x0834, "tpu_yuv_csc1_0"), (0x0838, "tpu_yuv_csc1_1"),
    (0x083C, "tpu_yuv_csc1_2"), (0x0840, "tpu_yuv_csc1_3"),
    (0x0830, "tpu_yuv_csc0_4"), (0x0844, "tpu_yuv_csc1_4"), (0x0848, "tpu_yuv_csc_input"),
    (0x0860, "tpu_luma_key_rg"), (0x0864, "tpu_luma_key_b_offset"),
    (0x0868, "tpu_luma_key_alpha"), (0x04E8, "isp_reg_04e8"),
]
REGISTERS_3D = [(name, 1) for _addr, name in REGISTER_3D_WRITES]

# The TA command, as the EDM reads it from the context's CCB (E161); size 0x2b0, the
# microkernel's. Dword 0 the command size (E156); 1 the flags (GEOM_FLAGS: E159, E172);
# 2-4 the PDS background-object words (E158, E162); 5 the vertex partitions (E159); 7 the
# render flags (FRAG_FLAGS: E158, E169); 8 the frame number (E158); 9 the PB descriptor (E156);
# 10-13 the thresholds (E161); 14 the render details (E159); 15 the destination sync list
# (E161, E158); 17 the RT data (E158, E161); 19 and 20 the per-render-target depth and stencil
# strides (E158 copies them to render details dwords 70 and 71, E163); 21 and 170 the 3D patch
# count and pairs (E158); 22 the shared block (the CCB offset SGX_DOKICK passes points at it,
# glossary cmd_ta.shared); 142-169 the TA register block (E159).
CMDTA = [
    ("size", 1), ("geom_flags", 1), ("pds_bgnd", 1, 3), ("num_vertex_partitions", 1),
    ("pad_0x18", 1), ("frag_flags", 1), ("frame_num", 1), ("hw_pb_desc_dev_vaddr", 1),
    ("ta_threshold", 1), ("zls_threshold", 1), ("global_threshold", 1), ("pds_threshold", 1),
    ("hw_render_details_dev_vaddr", 1), ("dst_sync_list_dev_vaddr", 1), ("pad_0x40", 1),
    ("hw_rt_data_dev_vaddr", 1), ("pad_0x48", 1), ("z_rt_stride", 1), ("stencil_rt_stride", 1),
    ("num_patches_3d", 1), ("shared", CMDTA_SHARED, 1), ("ta_registers", TA_REGISTERS, 1),
    ("patches_3d", 2, 1),
]

# The render details; size 0x1ec, the microkernel's. Dwords 0-51 the 3D register block
# (E163); 52 the access word (E164; glossary hw_render_details.access_dev_vaddr); 53 the render
# flags (E158 copies command dword 7 here, E163, E169); 55 the RT data and 66 the render-target
# index (E163); 56 the destination sync list (E164, E165); 57-60 the 3D transfer-queue sync,
# copied from the shared block's (E158; E164, E165 test and complete it); 63 and 64 the TA to 3D
# dependency (E158, E164); 65 the render-target count (E164); 67 and 68 the per-render-target
# patch address and list (E163); 69 the background-object word list (E162); 70 and 71 the
# per-render-target depth and stencil strides (E163); 73 the tiling engine state (E156, E158);
# 74 and 75 the render list links (E156); 76-78 the PDS background-object words (E158, E162);
# 79 the pixel partitions (E163); 80 the frame number (E158, E163); 81 and 82-89 the 3D status
# count and pairs, 90 and 91-122 the source syncs (E158, E164, E165).
RENDERDETAILS = [
    ("registers_3d", REGISTERS_3D, 1), ("access_dev_vaddr", 1), ("frag_flags", 1),
    ("pad_0xd8", 1), ("hw_rt_data_dev_vaddr", 1), ("dst_sync_list_dev_vaddr", 1),
    ("tq_3d_write_pending", 1), ("tq_3d_write_complete_dev_vaddr", 1),
    ("tq_3d_read_pending", 1), ("tq_3d_read_complete_dev_vaddr", 1), ("pad_0xf4", 1, 2),
    ("ta3d_dep_write_pending", 1), ("ta3d_dep_write_complete_dev_vaddr", 1), ("num_rts", 1),
    ("rt_index", 1), ("rt_patch_dev_vaddr", 1), ("rt_patch_list_dev_vaddr", 1),
    ("pds_bgnd_list_dev_vaddr", 1), ("z_rt_stride", 1), ("stencil_rt_stride", 1),
    ("pad_0x120", 1), ("te_context_state", 1), ("render_list_prev_dev_vaddr", 1),
    ("render_list_next_dev_vaddr", 1), ("pds_bgnd", 1, 3), ("num_pixel_partitions", 1),
    ("frame_num", 1), ("num_status_3d", 1), ("status_3d", CTL_STATUS, 4), ("num_src_syncs", 1),
    ("src_syncs", DEVSYNC, 8),
]

# The RT data; size 0x38, the microkernel's. Dword 1 the render details (E159, E164); 4 the
# background object (E162); 5-7 the DPM state, DPM control and OTPM (E158); 10 the
# render-target count (E158); 11 the region-header stride per render target (E163); 12 the RT
# status words (E158, E164); 13 the state word (E156, E158, E164).
RTDATA = [
    ("pad_0x00", 1), ("hw_render_details_dev_vaddr", 1), ("pad_0x08", 1, 2),
    ("bgobj_dev_vaddr", 1), ("dpm_state_dev_vaddr", 1), ("dpm_control_dev_vaddr", 1),
    ("otpm_dev_vaddr", 1), ("pad_0x20", 1, 2), ("num_rts", 1), ("region_header_rt_stride", 1),
    ("rt_status_dev_vaddr", 1), ("state", 1),
]

# The RT data set; size 0x50, the microkernel's: a 0x18-byte header and the RT data (glossary
# misc_info_struct_sizes.sizeof_hw_rt_data_set). Dword 1 the executed count (E156, E166);
# 3 and 4 the out-of-memory and partial-render counts (E160).
RTDATASET = [
    ("pad_0x00", 1), ("executed_count", 1), ("pad_0x08", 1), ("num_out_of_mem_signals", 1),
    ("num_spm_renders", 1), ("pad_0x14", 1), ("hw_rt_data", RTDATA, 1),
]

# The HW render context; size 0x44, the microkernel's. Dword 0 the flags (CONTEXT_FLAGS: E159,
# E161, E167); 1 the priority (E157; glossary hw_render_context.priority); 3 and 4 the client
# CCB and its control (E161); 5 the submitted commands (E157); 6 the PB descriptor (E159, E167);
# 8-11 the pending and ready render lists (E156, E157, E165); 12-15 the TA and 3D queue links
# (E157, E165); 16 the PID (E159, E163).
RENDERCONTEXT = [
    ("context_flags", 1), ("priority", 1), ("pad_0x08", 1), ("ccb_base_dev_vaddr", 1),
    ("ccb_ctl_dev_vaddr", 1), ("submitted_commands", 1), ("hw_pb_desc_dev_vaddr", 1),
    ("pad_0x1c", 1), ("pending_renders_head", 1), ("pending_renders_tail", 1),
    ("ready_renders_head", 1), ("ready_renders_tail", 1), ("run_node_prev_ta", 1),
    ("run_node_next_ta", 1), ("run_node_prev_3d", 1), ("run_node_next_3d", 1), ("pid", 1),
]

# The PB descriptor; size 0x3c, the microkernel's. Dword 0 the flags (PB_FLAGS); 2 and 3 the
# initial free list; 4 the page-table base; 6 and 7 the current free list; 8 and 9 the local and
# global page counts; 10-13 the thresholds; 14 the first block (E200, E201); 5 the allocated
# page count (E156).
PBDESC = [
    ("pb_flags", 1), ("pad_0x04", 1), ("initial_stack_top", 1), ("initial_dpm_ta_alloc", 1),
    ("page_table_base", 1), ("allocated_page_count", 1), ("current_stack_top", 1),
    ("dpm_ta_alloc", 1), ("local_page_count", 1), ("global_page_count", 1),
    ("ta_threshold", 1), ("zls_threshold", 1), ("global_threshold", 1), ("pds_threshold", 1),
    ("first_block_dev_vaddr", 1),
]

# A PB block, as the page-table builder reads it: the page count in its first dword, a
# first-page field in its third and the next block in its fourth (E201, E200).
PBBLOCK = [("page_count", 1), ("pad_0x04", 1), ("first_page", 1), ("next_block_dev_vaddr", 1)]

# The EDM's TA/3D control block (glossary ta3d_ctl), its 0xec bytes (E002). PDS #11 copies it
# into the secondary attributes, so sa<k> is dword k (E002, E003). The glossary's ta3d_ctl.*
# rows name the kicks' job words; the other words a record names have our names here:
# - E002: dword 0 the block itself, 1 the host control, 2 the kernel CCB control, 22 the kernel
#   CCB, 23 the page directory's physical address (a value; E008, E011), 43 the HWPerf buffer,
#   44 and 45 the TA and 3D signature buffers;
# - the kicks: 20 and 21 the RT data owning each DPM context slot (E158); 24, 26 and 27 the TA's
#   command, render details and context (E159); 25 the TA's RT data (E158, E159); 28, 29 and 30
#   the 3D's RT data, render details and render-target index (E163); 41 and 42 the TA's and the
#   3D's frame numbers (E158, E163); 46 and 47 the PB descriptors loaded in the TA and the 3D
#   (E200); 50 and 51 the TA's and the 3D's PIDs (E159, E163);
# - 31 the request word PDS #14's tasks serve (E146, E154);
# - the out-of-memory path (E160): 33 the TA global list saved while the list grows, 35 and 36
#   the page counts saved at an abort (from CR_DPM_PAGE_STATUS and from 0x072c), 37 the global
#   list saved and 38 the step added to CR_DPM_ZLS_PAGE_THRESHOLD when the threshold is raised,
#   39 CR_DPM_ABORT_STATUS_MTILE saved at an abort and 40 its bits 13:5, the macrotile's RT index;
# - 52 the nesting count of the settle loop (E153);
# - 54 the kick marks, bit 0 set by the TA kick and the TA-finished handler (E158, E156), bit 1
#   by the 3D kick (E163); 55 the word the TA kick, the TA-finished handler and the out-of-memory
#   path clear (E158, E156, E160); 57 the word the 3D kick clears (E163).
TA3DCTL = [
    ("ta3d_ctl_dev_vaddr", 1), ("host_ctl_dev_vaddr", 1), ("ccb_ctl_dev_vaddr", 1),
    ("pad_0x0c", 1, 17), ("dpm_slot0_rt_data_dev_vaddr", 1), ("dpm_slot1_rt_data_dev_vaddr", 1),
    ("kernel_ccb_dev_vaddr", 1), ("page_dir_phys_addr", 1), ("cmd_ta_dev_vaddr", 1),
    ("hw_rt_data_ta", 1), ("hw_render_details_ta", 1), ("hw_render_context_ta", 1),
    ("hw_rt_data_3d", 1), ("hw_render_details_3d", 1), ("rt_index_3d", 1),
    ("requests", 1), ("pad_0x80", 1), ("saved_ta_global_list", 1), ("pad_0x88", 1),
    ("abort_page_count0", 1), ("abort_page_count1", 1), ("threshold_ta_global_list", 1),
    ("zls_threshold_step", 1), ("abort_status_mtile", 1), ("abort_rt_index", 1),
    ("frame_num_ta", 1), ("frame_num_3d", 1), ("hwperf_buffer_dev_vaddr", 1),
    ("signature_ta_dev_vaddr", 1), ("signature_3d_dev_vaddr", 1),
    ("hw_pb_desc_ta", 1), ("hw_pb_desc_3d", 1), ("pad_0xc0", 1, 2), ("pid_ta", 1),
    ("pid_3d", 1), ("settle_count", 1), ("pad_0xd4", 1), ("kick_marks", 1),
    ("kick_clear_ta", 1), ("pad_0xe0", 1), ("kick_clear_3d", 1), ("pad_0xe8", 1),
]

STRUCTS = {
    # PVRSRV_BRIDGE_IN_DOKICK (sgx545-ce `src/services4/include/sgx_bridge.h`:199-208)
    "PVRSRV_BRIDGE_IN_DOKICK": [("ui32BridgeFlags", 1), ("hDevCookie", 1),
                                ("sCCBKick", CCB_KICK, 1)],
    "SGX_CCB_KICK": CCB_KICK,
    "SGXMKIF_CMDTA_SHARED": CMDTA_SHARED,
    "SGXMKIF_HWDEVICE_SYNC_LIST": DEVICE_SYNC_LIST,
    "cmd_ta": CMDTA,
    "ta_registers": TA_REGISTERS,
    "registers_3d": REGISTERS_3D,
    "hw_render_details": RENDERDETAILS,
    "hw_rt_data": RTDATA,
    "hw_rt_data_set": RTDATASET,
    "hw_render_context": RENDERCONTEXT,
    "hw_pb_desc": PBDESC,
    "pb_block": PBBLOCK,
    "ta3d_ctl": TA3DCTL,
}

# Flag bits by the glossary's names, only where a record or a glossary row names the bit.
FLAGS = {
    # the TA command's dword 1: E172 (0x1, 0x8, the mask tests), E166 and E156 (0x2), E159
    # (0x1 the reset; 0x10, 0x20, 0x40 the invalidations), E161 (0x400, 0x2000)
    "GEOM_FLAGS": {0x1: "FIRST_KICK", 0x2: "LAST_KICK", 0x8: "NO_DPM_CONTEXT_LOAD",
                   0x10: "INVALIDATE_USE_CACHE", 0x20: "INVALIDATE_PDS_CACHE",
                   0x40: "INVALIDATE_DATA_CACHE", 0x400: "TA3D_DEPENDENCY",
                   0x2000: "PB_THRESHOLD_UPDATE"},
    # the render flags, command dword 7 and render details dword 53: E156 (0x1), E161 (0x2),
    # E050-E053 (0x4), E163 and E156 (0x8), E169 (0x10), E164 (0x20, 0x200, 0x400), E163 and
    # E058 (0x80, 0x100), E165 (0x1 and 0x2 skip the render)
    "FRAG_FLAGS": {0x1: "NO_RENDER", 0x2: "ABORT", 0x4: "BIT2", 0x8: "NO_DEALLOCATE",
                   0x10: "SET_ZLSCTL_BIT0", 0x20: "GET_VIS_RESULTS", 0x80: "DEPTH_BUFFER",
                   0x100: "STENCIL_BUFFER", 0x200: "TA3D_DEPENDENCY", 0x400: "BIT10"},
    # the HW render context's dword 0: E159 (0x1), E161 and E165 (0x10), E167 and E168 (0x20)
    "CONTEXT_FLAGS": {0x1: "NEW", 0x10: "SUSPEND", 0x20: "OWN_PB"},
    # the PB descriptor's dword 0: E200, E201
    "PB_FLAGS": {0x1: "INIT_PAGE_TABLE", 0x2: "THRESHOLD_UPDATE"},
}

# The flag words of each structure and the table that names their bits.
FLAG_WORDS = {
    "cmd_ta": {"geom_flags": "GEOM_FLAGS", "frag_flags": "FRAG_FLAGS"},
    "hw_render_details": {"frag_flags": "FRAG_FLAGS"},
    "hw_render_context": {"context_flags": "CONTEXT_FLAGS"},
    "hw_pb_desc": {"pb_flags": "PB_FLAGS"},
}


def flag_names(kind: str, value: int) -> list[str]:
    """The names of the set bits of a flags word; the bits no record names, as one hex value."""
    names, rest = [], value
    for bit, name in FLAGS[kind].items():
        if value & bit:
            names.append(name)
            rest &= ~bit
    if rest:
        names.append(f"{rest:#x}")
    return names


def _layout(fields, prefix=""):
    """Yield (path, dword offset, element dwords, count, is_array) for every leaf."""
    off = 0
    for f in fields:
        name, shape = f[0], f[1]
        count = f[2] if len(f) > 2 else 1
        if isinstance(shape, list):
            for path, o, w, c, arr in _layout(shape):
                yield f"{prefix}{name}.{path}", off + o, w, c, arr
            off += _dwords(shape) * count
        else:
            yield f"{prefix}{name}", off, shape, count, len(f) > 2
            off += shape * count


def _dwords(fields) -> int:
    n = 0
    for f in fields:
        shape, count = f[1], f[2] if len(f) > 2 else 1
        n += (_dwords(shape) if isinstance(shape, list) else shape) * count
    return n


def size(name: str) -> int:
    return 4 * _dwords(STRUCTS[name])


def offset(name: str, field: str) -> int:
    for path, off, _w, _c, _a in _layout(STRUCTS[name]):
        if path == field or path.startswith(field + "."):
            return 4 * off
    raise KeyError(field)


def decode(name: str, raw: bytes) -> dict:
    """Name every field: scalars as ints, arrays as lists (of lists for multi-dword
    elements). Only the declared size is read: the variable-length 3D patch pairs of a
    command are decoded as their first entry."""
    need = size(name)
    if len(raw) < need:
        raise ValueError(f"{name}: need {need} bytes, got {len(raw)}")
    w = struct.unpack(f"<{len(raw) // 4}I", raw[:len(raw) // 4 * 4])
    out = {}
    for path, off, width, count, array in _layout(STRUCTS[name]):
        if not array:
            out[path] = w[off]
        elif width == 1:
            out[path] = list(w[off:off + count])
        else:
            out[path] = [list(w[off + i * width:off + (i + 1) * width]) for i in range(count)]
    return out
