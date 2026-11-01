# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Tests for kick3d.py: the layouts of the structures of the TA/3D kick.

The kernel-side layouts are the GPL kernel's (sgx545-ce). The client structures carry our own
names, each at the offset an evidence record or a glossary row gives; the tests pin those
offsets record by record, check every glossary row of the structures against the layouts, and
use word-index buffers (word i holds i) to pin decode().
"""
import pathlib
import re
import struct
import tomllib

import pytest

import kick3d

GLOSSARY = pathlib.Path(__file__).resolve().parents[2] / "glossary" / "structs"


def index_words(n: int) -> bytes:
    return struct.pack(f"<{n}I", *range(n))


def dword(name: str, field: str) -> int:
    return kick3d.offset(name, field) // 4


KERNEL_SIDE = {"PVRSRV_BRIDGE_IN_DOKICK", "SGX_CCB_KICK", "SGXMKIF_CMDTA_SHARED",
               "SGXMKIF_HWDEVICE_SYNC_LIST", "SGXMKIF_TRANSFERCMD_SHARED"}
CLIENT = {"cmd_ta", "ta_registers", "registers_3d", "hw_render_details", "hw_rt_data",
          "hw_rt_data_set", "hw_render_context", "hw_pb_desc", "pb_block", "ta3d_ctl",
          "transfer_cmd", "hw_transfer_context"}


def test_the_layouts_are_the_kernel_side_ones_and_the_client_structures():
    assert set(kick3d.STRUCTS) == KERNEL_SIDE | CLIENT


# --- structure sizes ---------------------------------------------------------------

def test_sizes_are_the_ones_the_microkernel_reports():
    # SGX_MISCINFO_STRUCT_SIZES (E001; glossary misc_info_struct_sizes.*)
    assert kick3d.size("cmd_ta") == 0x2B0
    assert kick3d.size("SGXMKIF_CMDTA_SHARED") == 0x1E0
    assert kick3d.size("registers_3d") == 0xD0
    assert kick3d.size("hw_render_details") == 0x1EC
    assert kick3d.size("hw_rt_data") == 0x38
    assert kick3d.size("hw_rt_data_set") == 0x50
    assert kick3d.size("hw_render_context") == 0x44
    assert kick3d.size("hw_pb_desc") == 0x3C
    assert kick3d.size("transfer_cmd") == 0x4C8
    assert kick3d.size("SGXMKIF_TRANSFERCMD_SHARED") == 0xDC
    assert kick3d.size("hw_transfer_context") == 0xB4


def test_register_block_and_pb_block_sizes_are_what_the_records_show():
    assert kick3d.size("ta_registers") == 28 * 4          # E159: command dwords 142 to 169
    assert kick3d.size("pb_block") == 0x10                # E201: four dwords read


def test_kick_bridge_in_is_564_bytes():
    # ui32BridgeFlags + hDevCookie + SGX_CCB_KICK, as captured from SGX_DOKICK.
    assert kick3d.size("PVRSRV_BRIDGE_IN_DOKICK") == 564
    assert kick3d.size("SGX_CCB_KICK") == 556


# --- the TA command ------------------------------------------------------------------

def test_ta_command_words_by_record():
    assert dword("cmd_ta", "size") == 0                            # E156
    assert dword("cmd_ta", "geom_flags") == 1                      # E159, E172
    assert dword("cmd_ta", "pds_bgnd") == 2                        # E158, E162
    assert dword("cmd_ta", "num_vertex_partitions") == 5           # E159
    assert dword("cmd_ta", "frag_flags") == 7                      # E158, E169
    assert dword("cmd_ta", "frame_num") == 8                       # E158
    assert dword("cmd_ta", "hw_pb_desc_dev_vaddr") == 9            # E156
    assert [dword("cmd_ta", f) for f in ("ta_threshold", "zls_threshold", "global_threshold",
                                         "pds_threshold")] == [10, 11, 12, 13]   # E161
    assert dword("cmd_ta", "hw_render_details_dev_vaddr") == 14    # E159
    assert dword("cmd_ta", "dst_sync_list_dev_vaddr") == 15        # E161
    assert dword("cmd_ta", "hw_rt_data_dev_vaddr") == 17           # E158, E161
    assert dword("cmd_ta", "z_rt_stride") == 19                    # E158, E163
    assert dword("cmd_ta", "stencil_rt_stride") == 20
    assert dword("cmd_ta", "num_patches_3d") == 21                 # E158
    assert dword("cmd_ta", "shared") == 22                         # sgx545-ce SGX_DOKICK
    assert dword("cmd_ta", "ta_registers") == 142                  # E159
    assert dword("cmd_ta", "patches_3d") == 170                    # E158


def test_ta_command_shared_block_is_the_kernels():
    assert kick3d.offset("cmd_ta", "shared.ui32CtrlFlags") == 0x58
    # E161: the transfer-queue sync is command dwords 25 to 28; E158: the source syncs from 34
    assert dword("cmd_ta", "shared.ui32TATQSyncWriteOpsPendingVal") == 25
    assert dword("cmd_ta", "shared.ui32NumSrcSyncs") == 33
    assert dword("cmd_ta", "shared.asSrcSyncs") == 34
    assert dword("cmd_ta", "shared.sTA3DDependency") == 66       # E161: dwords 68 and 69
    assert dword("cmd_ta", "shared.sCtlTAStatusInfo") == 70      # E156
    assert dword("cmd_ta", "shared.sCtl3DStatusInfo") == 134     # E158


def test_ta_registers_follow_the_kick_store_order():
    # E159: command dwords 142 to 169 go to these registers, one str each, in order
    assert [a for a, _ in kick3d.TA_REGISTER_WRITES] == [
        0x0204, 0x0208, 0x020C, 0x0210, 0x0214, 0x0218, 0x0238, 0x023C, 0x021C, 0x0220,
        0x0240, 0x0244, 0x0248, 0x0A04, 0x0AA0, 0x0C90, 0x02B0, 0x02D4, 0x02D0, 0x02B4,
        0x0324, 0x0368, 0x0364, 0x0370, 0x0374, 0x074C, 0x02A8, 0x0230]
    assert kick3d.offset("cmd_ta", "ta_registers.te_aa") == 0x238
    assert kick3d.offset("cmd_ta", "ta_registers.vdm_ctrl_stream_base") == 0x250
    assert kick3d.offset("cmd_ta", "ta_registers.ppp_screen") == 0x268
    assert kick3d.offset("cmd_ta", "ta_registers.dpm_reg_074c") == 0x29C
    assert kick3d.offset("cmd_ta", "ta_registers.mte_multisamplectl") == 0x2A4


def test_ta_command_gaps_stay_unnamed():
    names = [path for path, *_ in kick3d._layout(kick3d.STRUCTS["cmd_ta"])]
    assert {"pad_0x18", "pad_0x48"} <= set(names)


def test_the_capture_backed_words_are_named():
    # 11.11: the closed client's captured words (E323, E325, E327, E328, E331)
    named = {s: {p for p, *_ in kick3d._layout(kick3d.STRUCTS[s])} for s in kick3d.STRUCTS}
    assert "hw_rt_data_set_dev_vaddr" in named["cmd_ta"]
    assert {"pd_dev_paddr", "param_obj_dev_vaddr"} <= named["hw_render_context"]
    assert {"tiles_across", "num_rt_data"} <= named["hw_rt_data_set"]
    assert {"hw_render_context_dev_vaddr", "blocks_per_mtile", "mtile_region_bytes",
            "te_tpc_dev_vaddr", "te_tpc_bytes"} <= named["hw_rt_data"]
    assert "page_count" in named["hw_pb_desc"] and "stack_top" in named["pb_block"]
    for s in ("hw_rt_data", "hw_rt_data_set", "hw_render_context", "hw_pb_desc", "pb_block"):
        assert not any(p.startswith("pad_") for p in named[s]), s


def test_ta_command_decode():
    c = kick3d.decode("cmd_ta", index_words(172))
    assert c["geom_flags"] == 1 and c["pds_bgnd"] == [2, 3, 4]
    assert c["shared.ui32CtrlFlags"] == 22
    assert c["ta_registers.te_aa"] == 142 and c["ta_registers.mte_multisamplectl"] == 169
    assert c["patches_3d"] == [[170, 171]]


# --- the render details -----------------------------------------------------------

def test_3d_registers_follow_the_kick_store_order():
    # E163: render details dwords 0 to 51 go to these registers, one str each, in order
    assert [a for a, _ in kick3d.REGISTER_3D_WRITES] == [
        0x0CAC, 0x0CB0, 0x0400, 0x0414, 0x042C, 0x041C, 0x0420, 0x0424,
        0x0408, 0x0148, 0x050C,
        0x0480, 0x0484, 0x0488, 0x048C, 0x0490,
        0x04B8, 0x04BC, 0x04C4, 0x0520,
        0x04C8, 0x04DC, 0x0800, 0x0A5C, 0x0A60, 0x0A64,
        0x0418, 0x0A84, 0x0A88,
        0x0A8C, 0x0A90, 0x0A94, 0x0A98, 0x0B24, 0x0B28, 0x0B2C, 0x0A9C,
        0x0820, 0x0824, 0x0828, 0x082C, 0x0834, 0x0838, 0x083C, 0x0840,
        0x0830, 0x0844, 0x0848,
        0x0860, 0x0864, 0x0868, 0x04E8]
    assert kick3d.offset("hw_render_details", "registers_3d") == 0
    assert kick3d.offset("hw_render_details", "registers_3d.isp_zlsctl") == 0x2C
    assert kick3d.offset("hw_render_details", "registers_3d.event_pixel_pds_code") == 0x5C
    # a word is named after the register it lands in once the glossary has its row: 0x04bc
    # is CR_ISP_BGOBJVALS (E216); 0x04c4 has no row
    assert kick3d.offset("hw_render_details", "registers_3d.isp_bgobjvals") == 0x44
    assert kick3d.offset("hw_render_details", "registers_3d.reg_04c4") == 0x48


def test_render_details_words_by_record():
    rd = "hw_render_details"
    assert dword(rd, "access_dev_vaddr") == 52                    # E164
    assert dword(rd, "count_rt_data_set") == 54            # E304
    assert dword(rd, "frag_flags") == 53                          # E163, E169
    assert dword(rd, "hw_rt_data_dev_vaddr") == 55                # E163
    assert dword(rd, "dst_sync_list_dev_vaddr") == 56             # E164, E165
    assert dword(rd, "tq_3d_write_pending") == 57                 # E158, E165
    assert dword(rd, "tq_3d_read_complete_dev_vaddr") == 60       # E164
    assert dword(rd, "ta3d_dep_write_pending") == 63              # E158, E164
    assert dword(rd, "ta3d_dep_write_complete_dev_vaddr") == 64
    assert dword(rd, "num_rts") == 65                             # E164
    assert dword(rd, "rt_index") == 66                            # E163
    assert dword(rd, "rt_patch_dev_vaddr") == 67                  # E163
    assert dword(rd, "rt_patch_list_dev_vaddr") == 68
    assert dword(rd, "pds_bgnd_list_dev_vaddr") == 69             # E162
    assert dword(rd, "z_rt_stride") == 70                         # E163
    assert dword(rd, "stencil_rt_stride") == 71
    assert dword(rd, "te_context_state") == 73                    # E156, E158
    assert dword(rd, "render_list_prev_dev_vaddr") == 74          # E156
    assert dword(rd, "render_list_next_dev_vaddr") == 75
    assert dword(rd, "pds_bgnd") == 76                            # E158, E162
    assert dword(rd, "num_pixel_partitions") == 79                # E163
    assert dword(rd, "frame_num") == 80                           # E158, E163
    assert dword(rd, "num_status_3d") == 81                       # E158, E164
    assert dword(rd, "status_3d") == 82
    assert dword(rd, "num_src_syncs") == 90                       # E158, E165
    assert dword(rd, "src_syncs") == 91


# E158: the TA kick's copy routine, command dword -> render details dword
COPIED = [("frag_flags", "frag_flags", 7, 53), ("frame_num", "frame_num", 8, 80),
          ("shared.ui323DTQSyncWriteOpsPendingVal", "tq_3d_write_pending", 29, 57),
          ("shared.s3DTQSyncReadOpsCompleteDevVAddr", "tq_3d_read_complete_dev_vaddr", 32, 60),
          ("dst_sync_list_dev_vaddr", "dst_sync_list_dev_vaddr", 15, 56),
          ("shared.ui32NumSrcSyncs", "num_src_syncs", 33, 90),
          ("shared.asSrcSyncs", "src_syncs", 34, 91),
          ("z_rt_stride", "z_rt_stride", 19, 70),
          ("stencil_rt_stride", "stencil_rt_stride", 20, 71),
          ("pds_bgnd", "pds_bgnd", 2, 76), ("shared.ui32Num3DStatusVals", "num_status_3d", 24, 81),
          ("shared.sCtl3DStatusInfo", "status_3d", 134, 82)]


@pytest.mark.parametrize("cmd_field,rd_field,cmd_dw,rd_dw", COPIED)
def test_the_copy_routine_moves_command_words_to_render_details_words(cmd_field, rd_field,
                                                                         cmd_dw, rd_dw):
    assert dword("cmd_ta", cmd_field) == cmd_dw
    assert dword("hw_render_details", rd_field) == rd_dw


def test_render_details_decode():
    d = kick3d.decode("hw_render_details", index_words(123))
    assert d["registers_3d.bif_3d_req_base"] == 0 and d["registers_3d.isp_reg_04e8"] == 51
    assert d["frag_flags"] == 53 and d["pds_bgnd"] == [76, 77, 78]
    assert d["status_3d"][3] == [88, 89]
    assert d["src_syncs"][7] == [119, 120, 121, 122]


# --- RT data, RT data set, render context, PB descriptor and block ------------------

def test_rt_data_words_by_record():
    rt = "hw_rt_data"
    assert dword(rt, "hw_render_details_dev_vaddr") == 1          # E159
    assert dword(rt, "bgobj_dev_vaddr") == 4                      # E162
    assert dword(rt, "dpm_state_dev_vaddr") == 5                  # E158
    assert dword(rt, "dpm_control_dev_vaddr") == 6
    assert dword(rt, "otpm_dev_vaddr") == 7
    assert dword(rt, "num_rts") == 10
    assert dword(rt, "region_header_rt_stride") == 11             # E163
    assert dword(rt, "rt_status_dev_vaddr") == 12                 # E158, E164
    assert dword(rt, "state") == 13                               # E156, E158


def test_rt_data_set_words_and_its_embedded_rt_data():
    s = "hw_rt_data_set"
    assert dword(s, "pending_count_dev_vaddr") == 0               # E315
    assert dword(s, "executed_count") == 1                        # E156, E166
    assert dword(s, "num_out_of_mem_signals") == 3                # E160
    assert dword(s, "num_spm_renders") == 4
    # misc-info's size row: a 0x18-byte header, then the RT data
    assert kick3d.offset(s, "hw_rt_data") == 0x18
    assert kick3d.offset(s, "hw_rt_data.state") == 0x18 + 0x34
    d = kick3d.decode(s, index_words(20))
    assert d["hw_rt_data.hw_render_details_dev_vaddr"] == 7


def test_render_context_words_by_record():
    c = "hw_render_context"
    assert dword(c, "context_flags") == 0                         # E159, E161, E167
    assert dword(c, "priority") == 1                              # E157
    assert dword(c, "ccb_base_dev_vaddr") == 3                    # E161
    assert dword(c, "ccb_ctl_dev_vaddr") == 4
    assert dword(c, "submitted_commands") == 5                    # E157
    assert dword(c, "hw_pb_desc_dev_vaddr") == 6                  # E159, E167
    assert [dword(c, f) for f in ("pending_renders_head", "pending_renders_tail",
                                  "ready_renders_head", "ready_renders_tail")] == [8, 9, 10, 11]
    assert [dword(c, f) for f in ("run_node_prev_ta", "run_node_next_ta", "run_node_prev_3d",
                                  "run_node_next_3d")] == [12, 13, 14, 15]   # E157, E165
    assert dword(c, "pid") == 16                                  # E159, E163


def test_pb_descriptor_words_by_record():
    p = "hw_pb_desc"
    assert dword(p, "pb_flags") == 0                              # E201
    assert dword(p, "initial_stack_top") == 2
    assert dword(p, "initial_dpm_ta_alloc") == 3
    assert dword(p, "page_table_base") == 4
    assert dword(p, "allocated_page_count") == 5                  # E156
    assert dword(p, "current_stack_top") == 6
    assert dword(p, "dpm_ta_alloc") == 7
    assert dword(p, "local_page_count") == 8
    assert dword(p, "global_page_count") == 9
    assert [dword(p, f) for f in ("ta_threshold", "zls_threshold", "global_threshold",
                                  "pds_threshold")] == [10, 11, 12, 13]
    assert dword(p, "first_block_dev_vaddr") == 14


def test_pb_block_words_by_record():
    # E201: the page count in the first dword, a first-page field in the third, the next block
    # in the fourth
    b = kick3d.decode("pb_block", index_words(4))
    assert (b["page_count"], b["first_page"], b["next_block_dev_vaddr"]) == (0, 2, 3)


def test_ta3d_ctl_words_by_record():
    t = "ta3d_ctl"
    assert [dword(t, f) for f in ("dpm_slot0_rt_data_dev_vaddr",
                                  "dpm_slot1_rt_data_dev_vaddr")] == [20, 21]       # E158
    assert [dword(t, f) for f in ("cmd_ta_dev_vaddr", "hw_rt_data_ta",
                                  "hw_render_details_ta",
                                  "hw_render_context_ta")] == [24, 25, 26, 27]  # E159
    assert [dword(t, f) for f in ("hw_rt_data_3d", "hw_render_details_3d",
                                  "rt_index_3d")] == [28, 29, 30]                   # E163
    assert [dword(t, f) for f in ("frame_num_ta", "frame_num_3d")] == [41, 42]      # E158, E163
    assert [dword(t, f) for f in ("hw_pb_desc_ta", "hw_pb_desc_3d")] == [46, 47]    # E200
    assert [dword(t, f) for f in ("pid_ta", "pid_3d")] == [50, 51]                  # E159, E163
    assert kick3d.size(t) == 0xec            # the whole block (E002)


def test_ta3d_ctl_words_other_records_name():
    t = "ta3d_ctl"
    e002 = ("ta3d_ctl_dev_vaddr", "host_ctl_dev_vaddr", "ccb_ctl_dev_vaddr",
            "kernel_ccb_dev_vaddr", "page_dir_phys_addr", "hwperf_buffer_dev_vaddr",
            "signature_ta_dev_vaddr", "signature_3d_dev_vaddr")
    assert [dword(t, f) for f in e002] == [0, 1, 2, 22, 23, 43, 44, 45]            # E002
    assert dword(t, "requests") == 31                                               # E146, E154
    assert [dword(t, f) for f in ("saved_ta_global_list", "abort_page_count0",
                                  "abort_page_count1", "threshold_ta_global_list",
                                  "zls_threshold_step", "abort_status_mtile",
                                  "abort_rt_index")] == [33, 35, 36, 37, 38, 39, 40]  # E160
    assert dword(t, "settle_count") == 52                                           # E153
    assert [dword(t, f) for f in ("cleanup_pb_desc",
                                  "render_context_count")] == [32, 49]               # E303
    assert [dword(t, f) for f in ("kick_marks", "kick_clear_ta",
                                  "kick_clear_3d")] == [54, 55, 57]           # E156, E158, E163


def test_ta3d_ctl_gaps_stay_unnamed():
    # only the words no record names are padding: 3-19, 34, 48, 53, 56 and 58
    pads = {o + k for p, o, _w, c, _a in kick3d._layout(kick3d.STRUCTS["ta3d_ctl"])
            if p.startswith("pad_") for k in range(c)}
    assert pads == {*range(3, 20), 34, 48, 53, 56, 58}


# --- the transfer command and the HW transfer context --------------------------------

def test_transfer_registers_follow_the_load_order():
    # E015: command words 0 to 16 go to these registers, in this order of words
    assert [a for a, _ in kick3d.TRANSFER_REGISTER_WRITES] == [
        0x04C4, 0x04BC, 0x04B8, 0x0404, 0x0408, 0x0414, 0x0CAC, 0x042C, 0x04C8, 0x0A5C,
        0x0A60, 0x0A64, 0x040C, 0x0410, 0x0400, 0x0AB8, 0x0148]
    assert [kick3d.offset("transfer_cmd", n) for _a, n in kick3d.TRANSFER_REGISTER_WRITES] \
        == list(range(0, 0x44, 4))


def test_transfer_register_words_carry_the_register_and_glossary_names():
    names = dict(kick3d.TRANSFER_REGISTER_WRITES)
    # the GPL DDK's register names (E004, fw_format.md §9.5) and the 3D block's
    assert names[0x0CAC] == "bif_3d_req_base" and names[0x0AB8] == "pds_exec_base"
    assert names[0x0A5C] == "event_pixel_pds_code" and names[0x0404] == "isp_render"
    assert names[0x04C4] == "isp_background_tag" and names[0x0410] == "isp_render_end"
    assert names[0x040C] == "isp_render_origin" and names[0x0400] == "reg_0400"


def test_transfer_coefficient_groups_go_to_their_registers():
    # E015: +0x044-+0x06c to 0x0820-0x0848 with the load word at +0x188, +0x070-+0x078 to
    # 0x0860-0x0868 with +0x18c, +0x07c-+0x0a0 to 0x0a9c, 0x0a84-0x0a98, 0x0b24-0x0b2c with +0x190
    groups = kick3d.TRANSFER_LOAD_GROUPS
    assert [(load, kick3d.offset("transfer_cmd", words[0][1])) for load, words in groups] == [
        ("load_yuv_csc", 0x044), ("load_tpu_luma_key", 0x070), ("load_use_coeffs", 0x07C)]
    assert [a for a, _ in groups[0][1]] == list(range(0x0820, 0x084C, 4))
    assert [a for a, _ in groups[1][1]] == [0x0860, 0x0864, 0x0868]
    assert [a for a, _ in groups[2][1]] == [0x0A9C, *range(0x0A84, 0x0A9C, 4),
                                            0x0B24, 0x0B28, 0x0B2C]
    assert [kick3d.offset("transfer_cmd", load) for load, _w in groups] == [0x188, 0x18C, 0x190]
    words = [n for _l, ws in groups for _a, n in ws]
    assert [kick3d.offset("transfer_cmd", n) for n in words] == list(range(0x044, 0x0A4, 4))


def test_transfer_command_words_by_record():
    off = lambda f: kick3d.offset("transfer_cmd", f)
    assert off("cmd_size") == 0x0A4 and off("flags") == 0x0A8          # E015, E016
    assert off("shared") == 0x0AC                                      # E016, transfer.md §2.1
    assert off("num_pixel_partitions") == 0x194                        # E015, fw_format.md §9.5
    assert off("fence_id") == 0x198 and off("num_patches") == 0x19C    # E016, E015
    assert off("patches") == 0x1A0                                     # E015, E018


def test_transfer_shared_block_is_the_kernels():
    # sgx545-ce sgx_mkif_km.h:168-192, as transfer.md §2.1 lays it out; E016 places the
    # status count at command offset 0x164 and its first value at 0x16c
    off = lambda f: kick3d.offset("transfer_cmd", "shared." + f)
    assert off("ui32NumSrcSyncs") == 0x0AC and off("asSrcSyncs") == 0x0B0
    assert off("ui32NumDstSyncs") == 0x130 and off("asDstSyncs") == 0x134
    assert off("ui32TASyncWriteOpsPendingVal") == 0x144
    assert off("sTASyncReadOpsCompleteDevVAddr") == 0x150
    assert off("ui323DSyncWriteOpsPendingVal") == 0x154
    assert off("s3DSyncReadOpsCompleteDevVAddr") == 0x160
    assert off("ui32NumStatusVals") == 0x164 and off("sCtlStatusInfo") == 0x168
    assert kick3d.offset("transfer_cmd", "load_yuv_csc") == 0x0AC + 0xDC


def test_hw_transfer_context_words_by_record():
    off = lambda f: kick3d.offset("hw_transfer_context", f)
    # transfer.md §2.2 (E018, E021): flags, priority, directory, CCB, its control, count
    assert [off(f) for f in ("fw_com_ctx_flags", "priority", "pd_dev_paddr", "ccb_dev_vaddr",
                             "ccb_ctl_dev_vaddr", "submitted_commands")] == list(range(0, 24, 4))
    # E015: +0xa0 and +0xa4 copied into the command's destination sync, +0xa8 into TA3DCtl
    # dword 51, the queue links +0xac and +0xb0
    assert off("dst_sync_write_ops_pending_val") == 0xA0
    assert off("dst_sync_write_ops_complete_dev_vaddr") == 0xA4
    assert off("pid") == 0xA8 and off("run_node_prev") == 0xAC and off("run_node_next") == 0xB0


def test_hw_transfer_context_gap_stays_unnamed():
    pads = {o + k for p, o, _w, c, _a in kick3d._layout(kick3d.STRUCTS["hw_transfer_context"])
            if p.startswith("pad_") for k in range(c)}
    assert pads == set(range(6, 40))


def test_transfer_decode():
    c = kick3d.decode("transfer_cmd", index_words(0x4C8 // 4))
    assert c["isp_background_tag"] == 0 and c["reg_0148"] == 16
    assert c["tpu_yuv_csc0_0"] == 17 and c["use_coeffs2_bias"] == 40
    assert c["shared.asDstSyncs"] == [[77, 78, 79, 80]]
    assert c["shared.sCtlStatusInfo"][0] == [90, 91]
    assert c["fence_id"] == 102 and c["patches"][100] == [304, 305]
    h = kick3d.decode("hw_transfer_context", index_words(0xB4 // 4))
    assert h["submitted_commands"] == 5 and h["run_node_next"] == 44


# --- the glossary agrees with the layouts --------------------------------------------

PREFIXES = {"cmd_ta": "CMDTA", "hw_render_details": "HWRENDERDETAILS",
            "hw_rt_data": "HWRTDATA", "hw_rt_data_set": "HWRTDATASET",
            "hw_render_context": "HWRENDERCONTEXT", "hw_pb_desc": "HWPBDESC",
            "ta3d_ctl": "TA3D_CTL", "transfer_cmd": "TRANSFERCMD",
            "hw_transfer_context": "HWTRANSFERCONTEXT"}
FIELD_LOC = re.compile(r"^([A-Z_0-9]+)\+0x([0-9a-fA-F]+)$")
FLAG_LOC = re.compile(r"^(?:([A-Z_0-9/]+)\+0x([0-9a-fA-F]+)|render flags) bit(\d+)\b")


def glossary_rows(stem: str) -> list[tuple[str, str]]:
    path = GLOSSARY / f"{stem}.toml"
    rows = []
    for t in tomllib.loads(path.read_text())["term"]:
        for s in t.get("source", []):
            rows.append((t["name"], s.get("sgx545", "").strip()))
    return rows


@pytest.mark.skipif(not GLOSSARY.is_dir(), reason="no glossary next to the harness")
@pytest.mark.parametrize("name", sorted(PREFIXES))
def test_every_glossary_field_is_named_at_its_offset(name):
    # a glossary field is a top-level field (a nested block's offset is its first word's) or
    # a word of a register block, named by its leaf
    at = {}
    for path, off, *_ in kick3d._layout(kick3d.STRUCTS[name]):
        parts = path.split(".")
        at.setdefault(parts[-1], set()).add(4 * off)
        at.setdefault(parts[0], set()).add(kick3d.offset(name, parts[0]))
    n = 0
    for term, loc in glossary_rows(name):
        m = FIELD_LOC.match(loc)
        if not m or "." not in term:
            continue
        assert m.group(1) == PREFIXES[name], (term, loc)
        field = term.split(".", 1)[1]
        assert int(m.group(2), 16) in at.get(field, ()), (term, loc)
        n += 1
    assert n


FLAG_WORD_OF = {"GEOM_FLAGS": ("cmd_ta", "geom_flags"), "FRAG_FLAGS": None,
                "CONTEXT_FLAGS": ("hw_render_context", "context_flags"),
                "PB_FLAGS": ("hw_pb_desc", "pb_flags"), "TQ_FLAGS": ("transfer_cmd", "flags")}


@pytest.mark.skipif(not GLOSSARY.is_dir(), reason="no glossary next to the harness")
@pytest.mark.parametrize("kind", sorted(FLAG_WORD_OF))
def test_flag_tables_are_the_glossary_rows(kind):
    want = {}
    for term, loc in glossary_rows(kind):
        m = FLAG_LOC.match(loc)
        assert m, (term, loc)
        if FLAG_WORD_OF[kind]:
            struct_name, field = FLAG_WORD_OF[kind]
            assert PREFIXES[struct_name] in m.group(1).split("/")
            assert int(m.group(2), 16) == kick3d.offset(struct_name, field)
        want[1 << int(m.group(3))] = term.split(".", 1)[1]
    assert kick3d.FLAGS[kind] == want


# Every word of the client layouts has a glossary row, and the row at its offset carries its
# name: the structure rows by location (STRUCT+0xOFF, a nested layout's words also at its own
# prefix), named <layout>.<field> for our layouts and spelled as the kernel spells the field
# for the kernel's (the shared blocks); a word with no row at any of its offsets by name
# (pb_block.page_count); and the register rows by offset.
LAYOUT_PREFIX = {**PREFIXES, "pb_block": "PB_BLOCK", "SGXMKIF_CMDTA_SHARED": "CMDTA_SHARED",
                 "SGXMKIF_TRANSFERCMD_SHARED": "TRANSFERCMD_SHARED"}
REGISTER_BLOCKS = {"ta_registers": kick3d.TA_REGISTER_WRITES,
                   "registers_3d": kick3d.REGISTER_3D_WRITES}
ANY_LOC = re.compile(r"([A-Z][A-Z0-9_/]*)\+0x([0-9a-fA-F]+)")


def glossary_index() -> tuple[set, dict, dict]:
    """(term names, {(prefix, byte offset): {(term, spelling)}} of the structure rows,
    {register offset: term})."""
    names, at, regs = set(), {}, {}
    for f in sorted(GLOSSARY.parent.glob("*/*.toml")):
        for t in tomllib.loads(f.read_text())["term"]:
            names.add(t["name"])
            for s in t["source"]:
                loc = s.get("sgx545", "").strip()
                if s["kind"] == "register" and re.fullmatch(r"0x[0-9a-fA-F]+", loc):
                    regs[int(loc, 16)] = t["name"]
                elif s["kind"] == "field" and " bit" not in loc:
                    for m in ANY_LOC.finditer(loc):
                        for p in m.group(1).split("/"):
                            at.setdefault((p, int(m.group(2), 16)), set()).add(
                                (t["name"], s["term"]))
    return names, at, regs


def leaves(layout: str, base: int = 0, levels: tuple = ()):
    """(field name, dword in the outer layout, ((layout, its first dword, its field that holds
    the word), ...) outer first) for every scalar or array field, through the nested layouts."""
    off = base
    for f in kick3d.STRUCTS[layout]:
        shape, count = f[1], f[2] if len(f) > 2 else 1
        here = levels + ((layout, base, f[0]),)
        if isinstance(shape, list):
            inner = next(k for k, v in kick3d.STRUCTS.items() if v is shape)
            yield from leaves(inner, off, here)
            off += kick3d._dwords(shape) * count
        else:
            yield f[0], off, here
            off += shape * count


def named_at(levels: tuple, dword: int, at: dict) -> bool | None:
    """Whether a row at one of the word's offsets carries its name (None: no row there). At a
    level, the word's field there or a field of a level inside it names it (a nested layout's
    words are named at the outer prefix too)."""
    seen = False
    for i, (lay, first, _field) in enumerate(levels):
        if lay not in LAYOUT_PREFIX:
            continue
        rows = at.get((LAYOUT_PREFIX[lay], 4 * (dword - first)), set())
        seen |= bool(rows)
        inner = [f for _l, _o, f in levels[i:]]
        if lay in KERNEL_SIDE:
            if any(spelled in inner for _t, spelled in rows):
                return True
        elif any(term in {f"{lay}.{f}" for f in inner} for term, _s in rows):
            return True
    return False if seen else None


@pytest.mark.skipif(not GLOSSARY.is_dir(), reason="no glossary next to the harness")
@pytest.mark.parametrize("name", sorted(LAYOUT_PREFIX.keys() - KERNEL_SIDE))
def test_every_word_of_the_client_layouts_has_a_glossary_row(name):
    # a register block's word with no structure row has its register's row and is named
    # after it (the term without CR_), or is reg_<offset> where the glossary has no such row
    names, at, regs = glossary_index()
    missing, misnamed = [], []
    for leaf, dword, levels in leaves(name):
        if leaf.startswith("pad_"):
            continue
        named = named_at(levels, dword, at)
        if named is False:
            misnamed.append(f"{leaf} ({LAYOUT_PREFIX[name]}+{4 * dword:#05x})")
        if named is not None:
            continue
        if any(f"{lay}.{leaf}" in names for lay, _o, _f in levels if lay in LAYOUT_PREFIX):
            continue
        lay, first, _f = levels[-1]
        if lay in REGISTER_BLOCKS:
            reg = REGISTER_BLOCKS[lay][dword - first][0]
            if leaf == (regs[reg][3:].lower() if reg in regs else f"reg_{reg:04x}"):
                continue
        missing.append(f"{leaf} ({LAYOUT_PREFIX[name]}+{4 * dword:#05x})")
    assert not missing and not misnamed, (missing, misnamed)


def test_a_word_named_otherwise_than_the_row_at_its_offset_is_caught():
    at = {("CMDTA", 0x10): {("cmd_ta.size", "size")},
          ("CMDTA_SHARED", 0x2c): {("cmd_ta_shared.num_src_syncs", "ui32NumSrcSyncs")}}
    assert named_at((("cmd_ta", 0, "size"),), 4, at) is True
    assert named_at((("cmd_ta", 0, "length"),), 4, at) is False
    assert named_at((("cmd_ta", 0, "flags"),), 5, at) is None
    shared = (("cmd_ta", 0, "shared"), ("SGXMKIF_CMDTA_SHARED", 22, "ui32NumSrcSyncs"))
    assert named_at(shared, 33, at) is True
    assert named_at((shared[0], (shared[1][0], 22, "num_src_syncs")), 33, at) is False


# --- flags ---------------------------------------------------------------------------

def test_flag_names():
    assert kick3d.flag_names("GEOM_FLAGS", 0x3) == ["FIRST_KICK", "LAST_KICK"]
    assert kick3d.flag_names("GEOM_FLAGS", 0x71) == [
        "FIRST_KICK", "INVALIDATE_USE_CACHE", "INVALIDATE_PDS_CACHE", "INVALIDATE_DATA_CACHE"]
    assert kick3d.flag_names("FRAG_FLAGS", 0x180) == ["DEPTH_BUFFER", "STENCIL_BUFFER"]
    assert kick3d.flag_names("CONTEXT_FLAGS", 0x21) == ["NEW", "OWN_PB"]
    assert kick3d.flag_names("PB_FLAGS", 0x3) == ["INIT_PAGE_TABLE", "THRESHOLD_UPDATE"]
    assert kick3d.flag_names("TQ_FLAGS", 0x28) == ["3D_TQ_SYNC", "DUMMY_TRANSFER"]


def test_bits_no_record_names_print_as_hex():
    assert kick3d.flag_names("GEOM_FLAGS", 0x1000) == ["0x1000"]
    assert kick3d.flag_names("GEOM_FLAGS", 0x1004) == ["BIT2", "0x1000"]
    assert kick3d.flag_names("FRAG_FLAGS", 0x80000040) == ["0x80000040"]
    assert kick3d.flag_names("CONTEXT_FLAGS", 0x43) == ["NEW", "DUMMY_TRANSFER", "0x40"]


def test_flag_words_name_the_flag_table_of_each_flags_field():
    assert kick3d.FLAG_WORDS == {
        "cmd_ta": {"geom_flags": "GEOM_FLAGS", "frag_flags": "FRAG_FLAGS"},
        "hw_render_details": {"frag_flags": "FRAG_FLAGS"},
        "hw_render_context": {"context_flags": "CONTEXT_FLAGS"},
        "hw_pb_desc": {"pb_flags": "PB_FLAGS"},
        "transfer_cmd": {"flags": "TQ_FLAGS"},
        "hw_transfer_context": {"fw_com_ctx_flags": "CONTEXT_FLAGS"}}


# --- the kernel-side layouts (sgx545-ce) ---------------------------------------------

def test_ccb_kick_fields():
    k = kick3d.decode("PVRSRV_BRIDGE_IN_DOKICK", index_words(141))
    assert k["sCCBKick.sCommand.ui32ServiceAddress"] == 2
    assert k["sCCBKick.sCommand.ui32Data"] == [4, 5, 6, 7, 8, 9]
    assert k["sCCBKick.hCCBKernelMemInfo"] == 10
    assert k["sCCBKick.ui32NumTAStatusVals"] == 14
    assert k["sCCBKick.asTAStatusUpdate"][0] == [16, 17, 18]
    assert k["sCCBKick.as3DStatusUpdate"][3] == [121, 122, 123]
    assert k["sCCBKick.bFirstKickOrResume"] == 124
    assert k["sCCBKick.ui32CCBOffset"] == 126
    assert k["sCCBKick.ahSrcKernelSyncInfo"] == list(range(128, 136))
    assert k["sCCBKick.h3DSyncInfo"] == 139
    assert k["sCCBKick.hDevMemContext"] == 140


def test_shared_ta_block_fields():
    s = kick3d.decode("SGXMKIF_CMDTA_SHARED", index_words(120))
    assert s["ui32CtrlFlags"] == 0 and s["ui32Num3DStatusVals"] == 2
    assert s["s3DTQSyncReadOpsCompleteDevVAddr"] == 10
    assert s["ui32NumSrcSyncs"] == 11
    assert s["asSrcSyncs"][7] == [40, 41, 42, 43]
    assert s["sTA3DDependency"] == [[44, 45, 46, 47]]
    assert kick3d.offset("SGXMKIF_CMDTA_SHARED", "sCtlTAStatusInfo") == 0xC0
    assert s["sCtlTAStatusInfo"][0] == [48, 49]
    assert s["sCtl3DStatusInfo"][3] == [118, 119]


def test_device_sync_list_fields():
    d = kick3d.decode("SGXMKIF_HWDEVICE_SYNC_LIST", index_words(6))
    assert d["sAccessDevAddr"] == 0 and d["ui32NumSyncObjects"] == 1
    assert d["asSyncData"] == [[2, 3, 4, 5]]


def test_offset_of_a_nested_field():
    assert kick3d.offset("PVRSRV_BRIDGE_IN_DOKICK", "sCCBKick.ui32CCBOffset") == 4 * 126
    with pytest.raises(KeyError):
        kick3d.offset("SGX_CCB_KICK", "no_such_field")


def test_decode_rejects_short_buffers():
    with pytest.raises(ValueError):
        kick3d.decode("SGXMKIF_HWDEVICE_SYNC_LIST", index_words(5))
    with pytest.raises(ValueError):
        kick3d.decode("hw_pb_desc", index_words(14))
