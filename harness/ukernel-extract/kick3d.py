#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The layouts of the kernel-side structures of the TA/3D kick.

This module names the fields of the structures the GPL kernel defines for a kick: the
SGX_DOKICK bridge input, the CCB kick it carries, the shared block of a TA command and the
device sync list. edmtrace.py and edm_dataflow.py use the layouts for offsets and pointer
typing; a structure with no layout here is traced by offset.

Layouts, all 32-bit, from sgx545-ce (the GPL kernel module of Cedarview) for its build
configuration: SUPPORT_SGX_NEW_STATUS_VALS on (sgx545-ce `Kbuild`:111),
SUPPORT_SGX_GENERALISED_SYNCOBJECTS, SUPPORT_SID_INTERFACE, PDUMP and NO_HARDWARE off.
Counts are sgx545-ce `src/include4/sgxapi_km.h`:83-91 (32 TA and 4 3D status values,
8 source syncs).
"""
from __future__ import annotations

import struct


# A field is (name, dwords) for scalars, (name, dwords, count) for arrays of
# multi-dword elements, or (name, [fields], count) for nested structures.

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

STRUCTS = {
    # PVRSRV_BRIDGE_IN_DOKICK (sgx545-ce `src/services4/include/sgx_bridge.h`:199-208)
    "PVRSRV_BRIDGE_IN_DOKICK": [("ui32BridgeFlags", 1), ("hDevCookie", 1),
                                ("sCCBKick", CCB_KICK, 1)],
    "SGX_CCB_KICK": CCB_KICK,
    "SGXMKIF_CMDTA_SHARED": CMDTA_SHARED,
    "SGXMKIF_HWDEVICE_SYNC_LIST": DEVICE_SYNC_LIST,
}


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
    elements). Only the declared size is read."""
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
