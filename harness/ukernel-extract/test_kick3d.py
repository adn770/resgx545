# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Tests for kick3d.py — the layouts of the kernel-side structures of the TA/3D kick.

The tests use word-index buffers (word i holds i) to pin every field position.
"""
import struct

import pytest

import kick3d


def index_words(n: int) -> bytes:
    return struct.pack(f"<{n}I", *range(n))


def test_only_the_kernel_side_structures_have_layouts():
    # the layouts the GPL kernel defines (sgx545-ce); nothing else is laid out here
    assert set(kick3d.STRUCTS) == {"PVRSRV_BRIDGE_IN_DOKICK", "SGX_CCB_KICK",
                                   "SGXMKIF_CMDTA_SHARED", "SGXMKIF_HWDEVICE_SYNC_LIST"}


# --- structure sizes ---------------------------------------------------------------

def test_shared_ta_block_size_matches_what_the_microkernel_reports():
    # SGX_MISCINFO_STRUCT_SIZES from the captured init info (initinfo.py)
    assert kick3d.size("SGXMKIF_CMDTA_SHARED") == 0x1E0


def test_kick_bridge_in_is_564_bytes():
    # ui32BridgeFlags + hDevCookie + SGX_CCB_KICK, as captured from SGX_DOKICK.
    assert kick3d.size("PVRSRV_BRIDGE_IN_DOKICK") == 564
    assert kick3d.size("SGX_CCB_KICK") == 556


# --- field positions -----------------------------------------------------------------

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
