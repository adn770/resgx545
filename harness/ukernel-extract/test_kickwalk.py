# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Tests for kickwalk.py: decoding the VDM control stream and walking the pointers of the
TA/3D kick the closed GLES2 stack submits.

The synthetic tests use word-index buffers (word i holds i) and small hand-built streams.
The capture tests run only when the gitignored extracted/gles2_tri/ capture is present.
"""
import pathlib
import struct

import pytest

import kick3d
import kickwalk

HERE = pathlib.Path(__file__).resolve().parent
CAPTURE = HERE / "extracted" / "gles2_tri" / "dump3d"


def index_words(n: int) -> bytes:
    return struct.pack(f"<{n}I", *range(n))


# --- VDM control stream ------------------------------------------------------------

def test_vdm_stream_blocks():
    words = [
        0x40000000 | (0xEC011000 >> 4), (3 << 26) | (1 << 25) | (1 << 17) | 3,   # state
        0x80C00003, 0x080C3000, 0xF0000000, 0x003FFFFF,                          # index list
        0xF0000000 | (0xEC01E000 >> 4), (1 << 24) | (3 << 22) | (1 << 7) | 2,    # its vertex PDS
        0x60000000 | (0xEC001000 >> 4), 1 << 26,                                 # last state
        0xC0000000,                                                              # terminate
        0x12345678,                                                              # not read
    ]
    blocks = kickwalk.decode_vdm(words)
    assert [b["type"] for b in blocks] == ["STATE", "INDEXLIST", "STATE", "TERMINATE"]
    s = blocks[0]
    assert s["pds_base"] == 0xEC011000 and s["data_bytes"] == 48
    assert s["flags"] == ["SD", "MTE emit"] and s["use_attr_bytes"] == 48
    i = blocks[1]
    assert i["primitive"] == "triangles" and i["count"] == 3 and i["words"] == 6
    assert i["index_base"] == 0x080C3000 and i["extra"] == [0xF0000000, 0x003FFFFF]
    assert blocks[2]["flags"][0] == "last task" and blocks[2]["pds_base"] == 0xEC001000
    assert blocks[3]["offset"] == 10


def test_vdm_index_list_carries_the_vertex_pds_program():
    # The two words after an index list (and its optional words) start the vertex task:
    # partition size (31:28) and PDS address >> 4, then the output vertex size in
    # 4-dword units (31:24), bits 23:22, the USE attribute size in 16-byte rows (14:7)
    # and the PDS data size in 16-byte rows (6:0).
    i = kickwalk.decode_vdm([0x80C00003, 0x080F5000, 0xF0000000, 0x003FFFFF,
                           0xFEC01E00, 0x02C00103, 0xC0000000])[0]
    v = i["vertex"]
    assert v["pds_base"] == 0xEC01E000 and v["partitions"] == 0xF
    assert v["vertex_dwords"] == 8 and v["advance"] == 3
    assert v["use_attr_bytes"] == 32 and v["data_bytes"] == 48
    assert v["word2"] == 0x02C00103


def test_vdm_index_list_word_count_follows_present_bits():
    blocks = kickwalk.decode_vdm([0x80000006, 0x1000, 0x70000000, 0x01000082, 0xC0000000])
    assert blocks[0]["words"] == 4 and blocks[0]["count"] == 6
    assert blocks[0]["vertex"]["partitions"] == 7
    assert blocks[1]["type"] == "TERMINATE"


def test_vdm_stream_follows_no_link_and_stops_at_end():
    assert kickwalk.decode_vdm([0x40000000 | 0x0EC0110, 0x0])[-1]["type"] == "STATE"
    assert kickwalk.decode_vdm([]) == []


# --- object graph ------------------------------------------------------------------

class Mem:
    """A device memory image: {dva: bytes} objects, as the capture snapshots them."""

    def __init__(self, objs):
        self.objs = objs

    def read(self, dva, n):
        for base, data in self.objs.items():
            if base <= dva and dva + n <= base + len(data):
                return data[dva - base:dva - base + n]
        raise KeyError(hex(dva))


def put(buf: bytearray, struct_name: str, field: str, value: int):
    off = kick3d.offset(struct_name, field)
    buf[off:off + 4] = struct.pack("<I", value)


def test_walk_assigns_roles_from_pointer_fields():
    ccb, ctx, pbdesc, details = 0xF0003000, 0xF0016000, 0xF0001000, 0xF0033000
    rtdata, vdm = 0xF0038018, 0x0808C000
    cmd = bytearray(0x400)
    put(cmd, "cmd_ta", "hw_pb_desc_dev_vaddr", pbdesc)
    put(cmd, "cmd_ta", "hw_render_details_dev_vaddr", details)
    put(cmd, "cmd_ta", "hw_rt_data_dev_vaddr", rtdata)
    put(cmd, "cmd_ta", "ta_registers.vdm_ctrl_stream_base", vdm)
    put(cmd, "cmd_ta", "ta_registers.bif_ta_req_base", 0xC0000000)
    kick = bytearray(564)
    data1 = kick3d.offset("PVRSRV_BRIDGE_IN_DOKICK", "sCCBKick.sCommand.ui32Data") + 4
    kick[data1:data1 + 4] = struct.pack("<I", ctx)        # ui32Data[1]: HW render context
    put(kick, "PVRSRV_BRIDGE_IN_DOKICK", "sCCBKick.ui32CCBOffset", 0x58)
    details_buf = bytearray(0x1EC)
    put(details_buf, "hw_render_details", "registers_3d.event_pixel_pds_code", 0xE4004000)
    put(details_buf, "hw_render_details", "registers_3d.event_pixel_pds_data", 5)
    mem = Mem({ccb: bytes(cmd), ctx: bytes(0x44), pbdesc: bytes(0x3C), details: bytes(details_buf),
               rtdata: bytes(0x38), vdm: struct.pack("<I", 0xC0000000),
               0xE4004000: bytes(0x100)})
    roles = kickwalk.walk(bytes(kick), ccb, mem)
    by_dva = {r["dva"]: r for r in roles}
    assert by_dva[ccb]["role"] == "TA command (cmd_ta)"
    assert by_dva[ctx]["struct"] == "hw_render_context"
    assert by_dva[pbdesc]["struct"] == "hw_pb_desc"
    assert by_dva[details]["struct"] == "hw_render_details"
    assert by_dva[rtdata]["struct"] == "hw_rt_data"
    assert by_dva[vdm]["role"] == "VDM control stream"
    assert by_dva[0xE4004000]["role"] == "end-of-render PDS program (pixel event)"
    assert by_dva[0xE4004000]["pds_data_dwords"] == 20
    assert by_dva[0xC0000000]["role"] == "TA requestor base (parameter heap)"


class Snap(Mem):
    """A Mem with the two lookups report() makes of a capture snapshot."""

    def by_handle(self, handle):
        return 0xF0003000

    def find(self, dva):
        base = next((b for b, d in self.objs.items() if b <= dva < b + len(d)), None)
        return None if base is None else {"index": 0, "heap_name": "GENERAL", "dva": base}


def test_report_names_the_flag_bits_a_record_names():
    ccb, ctx = 0xF0003000, 0xF0016000
    cmd = bytearray(0x2C0)
    put(cmd, "cmd_ta", "geom_flags", 0x1003)
    put(cmd, "cmd_ta", "frag_flags", 0x180)
    kick = bytearray(564)
    data1 = kick3d.offset("PVRSRV_BRIDGE_IN_DOKICK", "sCCBKick.sCommand.ui32Data") + 4
    kick[data1:data1 + 4] = struct.pack("<I", ctx)
    put(kick, "PVRSRV_BRIDGE_IN_DOKICK", "sCCBKick.ui32CCBOffset", 0x58)
    context = bytearray(0x44)
    put(context, "hw_render_context", "context_flags", 0x21)
    text = kickwalk.report(bytes(kick), Snap({ccb: bytes(cmd), ctx: bytes(context)}))
    assert "geom_flags" in text and "0x1003 ['FIRST_KICK', 'LAST_KICK', '0x1000']" in text
    assert "0x180 ['DEPTH_BUFFER', 'STENCIL_BUFFER']" in text
    assert "0x21 ['NEW', 'OWN_PB']" in text


def test_walk_reads_pds_programs_from_the_vdm_stream():
    ccb, vdm, pds = 0xF0003000, 0x0808C000, 0xEC011000
    cmd = bytearray(0x2C0)
    put(cmd, "cmd_ta", "ta_registers.vdm_ctrl_stream_base", vdm)
    kick = bytearray(564)
    put(kick, "PVRSRV_BRIDGE_IN_DOKICK", "sCCBKick.ui32CCBOffset", 0x58)
    stream = struct.pack("<3I", 0x40000000 | (pds >> 4), 3 << 26, 0xC0000000)
    mem = Mem({ccb: bytes(cmd), vdm: stream, pds: bytes(0x80)})
    by_dva = {r["dva"]: r for r in kickwalk.walk(bytes(kick), ccb, mem)}
    assert by_dva[pds]["role"] == "PDS state program (VDM word 0)"
    assert by_dva[pds]["pds_data_dwords"] == 12


def test_walk_reads_the_vertex_program_of_an_index_list():
    ccb, vdm, vtx = 0xF0003000, 0x0808C000, 0xEC01E000
    cmd = bytearray(0x2C0)
    put(cmd, "cmd_ta", "ta_registers.vdm_ctrl_stream_base", vdm)
    kick = bytearray(564)
    put(kick, "PVRSRV_BRIDGE_IN_DOKICK", "sCCBKick.ui32CCBOffset", 0x58)
    stream = struct.pack("<5I", 0x80000003, 0x080F5000, 0xF0000000 | (vtx >> 4), 0x01C00082,
                         0xC0000000)
    mem = Mem({ccb: bytes(cmd), vdm: stream, vtx: bytes(0x80)})
    by_dva = {r["dva"]: r for r in kickwalk.walk(bytes(kick), ccb, mem)}
    assert by_dva[vtx]["role"] == "PDS vertex program (VDM word 0)"
    assert by_dva[vtx]["pds_data_dwords"] == 8


def test_snapshot_reads_objects_and_zero_fills_dropped_files(tmp_path):
    (tmp_path / "objects.txt").write_text(
        "  0 heap=0  GENERAL                  dva=08001000 size=0x000008 mapped=0x001000 "
        "attribs=00000001 kind=0\n"
        "  2 heap=11 PERCONTEXT_3DPARAMETERS  dva=c0001000 size=0x002000 mapped=0x002000 "
        "attribs=00000001 kind=0\n")
    (tmp_path / "obj000_08001000.bin").write_bytes(struct.pack("<2I", 7, 9) + bytes(0xFF8))
    snap = kickwalk.Snapshot(tmp_path)
    assert snap.read(0x08001004, 4) == struct.pack("<I", 9)
    # capture copies may leave out the all-zero parameter buffer pages: they read as zeros
    assert snap.read(0xC0001ff0, 0x20) == bytes(0x20)


# --- the capture (gitignored; skipped without it) ------------------------------------

@pytest.mark.skipif(not CAPTURE.exists(), reason="gles2_tri capture not present")
def test_capture_kicks_are_consistent():
    for n in (0, 1):
        k = kick3d.decode("PVRSRV_BRIDGE_IN_DOKICK", (CAPTURE / f"kick0{n}_in.bin").read_bytes())
        assert k["sCCBKick.ui32NumTAStatusVals"] <= 32
        assert k["sCCBKick.bLastInScene"] == n
        snap = kickwalk.Snapshot(CAPTURE / f"kick0{n}")
        ccb = snap.by_handle(k["sCCBKick.hCCBKernelMemInfo"])
        cmd_off = k["sCCBKick.ui32CCBOffset"] - kick3d.offset("cmd_ta", "shared")
        cmd = kick3d.decode("cmd_ta", snap.read(ccb + cmd_off, kick3d.size("cmd_ta")))
        assert cmd["size"] >= kick3d.size("cmd_ta")
        assert cmd["shared.ui32CtrlFlags"] & 1                         # READY, set by the kernel
        # E161: the EDM finds the command at the context's CCB base plus the read offset
        ctx = kick3d.decode("hw_render_context",
                            snap.read(k["sCCBKick.sCommand.ui32Data"][1], 0x44))
        assert ctx["ccb_base_dev_vaddr"] == ccb


def test_vdm_complex_state_has_no_plain_data_size():
    # With the complex flag (bit 28) the second word has another layout, not decoded yet.
    b = kickwalk.decode_vdm([0x70000000 | (0xEC003040 >> 4), 0x02C00082, 0xC0000000])[0]
    assert b["pds_base"] == 0xEC003040 and "complex" in b["flags"]
    assert b["data_bytes"] is None and b["use_attr_bytes"] is None
