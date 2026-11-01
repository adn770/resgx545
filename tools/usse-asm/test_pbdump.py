# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""pbdump.py: reading the render dumps (the parameter slot from its PB, the TA data)."""
from __future__ import annotations

import os
import pathlib
import struct

import pytest

import pbdump

PAGE = 4096
ROOT = pathlib.Path(__file__).resolve().parents[2]
DATA = pathlib.Path(os.environ.get("RESGX545_DATA") or ROOT.parent / "resgx545-data")


def dwords(n_pages: int, at: dict) -> bytes:
    """n_pages zero pages with dword values at byte offsets."""
    b = bytearray(n_pages * PAGE)
    for off, v in at.items():
        b[off:off + 4] = struct.pack("<I", v)
    return bytes(b)


def test_written_pages():
    assert pbdump.written(dwords(3, {PAGE + 8: 1})) == [1]
    assert pbdump.written(dwords(2, {})) == []


def test_object_is_the_first_pb_page_to_its_last_word():
    param = dwords(2, {0: 0x04000004, 8: 0x04000000, 12: 0x3f800000})
    assert pbdump.obj(param) == [0x04000004, 0, 0x04000000, 0x3f800000]


def test_regions_decode_the_headers():
    """Region headers: three dwords each on the first written TA data page; word 0's bits
    23:16 the column, its low 16 bits the row (bit 12 the second macrotile's rows), 31:24
    the flags; word 1 the stream block."""
    td = dwords(5, {4 * PAGE: 0x04000000, 4 * PAGE + 4: 0x2000,
                    4 * PAGE + 12: 0x02020000,
                    4 * PAGE + 24: 0x10061008, 4 * PAGE + 28: 0x2080})
    r = pbdump.regions(td)
    assert r[0] == pbdump.Region(0, 0, 0, 0x04, 0x2000)
    assert r[1] == pbdump.Region(1, 2, 0, 0x02, 0)
    assert r[2] == pbdump.Region(2, 6, 0x1008, 0x10, 0x2080)


def test_stream_stops_at_the_filler():
    """A region's stream block: its words up to the 0xc0000000 filler."""
    param = dwords(3, {PAGE: 0x4490ffff, PAGE + 4: 0x04000406, PAGE + 8: 0xc0000000,
                       PAGE + 12: 0xc0000000, PAGE + 0x80: 0x4a803f03})
    assert pbdump.stream(param, 0x2000) == [0x4490ffff, 0x04000406]
    assert pbdump.stream(param, 0x2080) == [0x4a803f03]


def test_primitive_and_object_words_by_their_glossary_fields():
    """CSTREAM: a stream holds per object a primitive word (PRIM_TILES [23:16], PRIM_VERTICES
    [28:25], PRIM_POINTS bit 29) and an object word (OBJ_PRIMS [31:26], OBJ_ISP_ADDR below)."""
    assert pbdump.prim_word(0x4490ffff) == {"PRIM_TILES": 0x90, "PRIM_VERTICES": 2,
                                            "PRIM_POINTS": 0}
    assert pbdump.prim_word(0x6a803f03)["PRIM_POINTS"] == 1
    assert pbdump.obj_word(0x04000406) == {"OBJ_PRIMS": 1, "OBJ_ISP_ADDR": 0x406}
    assert pbdump.objects([0x4490ffff, 0x04000406, 0x4480ffff]) == [
        (pbdump.prim_word(0x4490ffff), pbdump.obj_word(0x04000406), None),
        (pbdump.prim_word(0x4480ffff), None, None)]


def test_a_wide_mask_form_takes_a_third_dword():
    """PRIM_TILES 0x8a and 0x8c (masks too wide for the primitive word): the block is the
    primitive word, the object word and a mask dword (E177, E180: five copies, 0x5c8a7fff with
    0x1f)."""
    five = [0x5c8a7fff, 0x24000412, 0x1f]
    assert pbdump.objects(five) == [
        (pbdump.prim_word(0x5c8a7fff), pbdump.obj_word(0x24000412), 0x1f)]
    assert pbdump.objects([0x5c8c7fff, 0x24000412, 0x1f, 0x4490ffff, 0x04000406]) == [
        (pbdump.prim_word(0x5c8c7fff), pbdump.obj_word(0x24000412), 0x1f),
        (pbdump.prim_word(0x4490ffff), pbdump.obj_word(0x04000406), None)]
    # both tiles take every primitive: two dwords whatever the vertices (0x5c90ffff, 15)
    assert len(pbdump.objects([0x5c90ffff, 0x24000412])) == 1


def test_the_lines_form_takes_a_third_dword():
    """PRIM_TILES 0x88 (two lines, E181: 0x4688000f): the block is the primitive word, the
    object word and a further dword, as for the wide-mask forms."""
    assert 0x88 in pbdump.THIRD_DWORD_TILES
    assert pbdump.objects([0x4688000f, 0x0c000407, 0x00010003]) == [
        (pbdump.prim_word(0x4688000f), pbdump.obj_word(0x0c000407), 0x00010003)]


def _ta_dumps():
    return sorted((DATA / "ta").glob("*/*/dumps/*.param.bin"))


@pytest.mark.skipif(not _ta_dumps(), reason="needs the ta datasets (resgx545-data)")
def test_every_stream_of_the_ta_dumps_splits_into_whole_blocks():
    """Over the ta-objects, ta-regions and ta-zero-words dumps every region's stream reads as
    whole blocks whose primitive word has bit 23 set (the PRIM_TILES forms 0x80 to 0x98): a
    third dword read as a primitive word would not have it. The two-lines dump has 0x88."""
    forms = set()
    for p in _ta_dumps():
        stem = p.name[:-len(".param.bin")]
        param, td = p.read_bytes(), (p.parent / f"{stem}.tadata.bin").read_bytes()
        for r in pbdump.regions(td):
            for prim, _ob, _m in pbdump.objects(pbdump.stream(param, r.stream) if r.stream
                                                 else []):
                assert prim["PRIM_TILES"] & 0x80, (stem, r.index)
                forms.add(prim["PRIM_TILES"])
    assert {0x80, 0x88, 0x90, 0x98} <= forms


def test_region_flags_by_their_glossary_bits():
    """REGION_HDR.FLAGS, word 0 [31:24]: bit 25 outside the target, 26 a macrotile's first
    region, 27 empty inside it, 28 a macrotile's last region, 31 the scene's last."""
    assert pbdump.region_flags(0x04) == ["first of a macrotile"]
    assert pbdump.region_flags(0x98) == ["empty", "last of a macrotile", "last of the scene"]
    assert pbdump.region_flags(0x41) == ["0x41"]           # bits no record names, as hex


def test_region_flag_bit_29_is_the_te_psg_mark():
    """REGION_HDR.FLAGS bit 29: every target region's header with CR_TE_PSG bit 21 (E305)."""
    assert pbdump.region_flags(0x24) == ["first of a macrotile", "TE_PSG bit 21 mark"]


def test_report_lists_pages_object_regions_streams(tmp_path):
    (tmp_path / "t__0.param.bin").write_bytes(
        dwords(3, {0: 0x04000004, PAGE: 0x4490ffff, PAGE + 4: 0x04000406,
                   PAGE + 8: 0xc0000000}))
    (tmp_path / "t__0.tadata.bin").write_bytes(
        dwords(5, {4 * PAGE: 0x04000000, 4 * PAGE + 4: 0x2000, 4 * PAGE + 12: 0x02020000}))
    text = pbdump.report(tmp_path, "t__0")
    assert "PB pages 0x1000 0x2000" in text and "TA data pages 4" in text
    assert "object (1 dwords): 04000004" in text
    assert "region 0 col 0 row 0x0 flags 0x04 -> 0x2000: 4490ffff 04000406" in text
    assert "1 empty regions" in text
    # the words by the glossary's terms (PB_OBJ, REGION_HDR, CSTREAM)
    assert "  PB_OBJ.PDS_WORDS 04000004\n" in text
    assert "  REGION_HDR.FLAGS first of a macrotile" in text
    assert ("  CSTREAM PRIM_TILES 0x90 PRIM_VERTICES 2 PRIM_POINTS 0, "
            "OBJ_PRIMS 1 OBJ_ISP_ADDR 0x406\n") in text


def test_report_prints_the_mask_apart_from_the_object_word(tmp_path):
    (tmp_path / "t__0.param.bin").write_bytes(
        dwords(3, {0: 0x04000004, PAGE: 0x5c8a7fff, PAGE + 4: 0x24000412, PAGE + 8: 0x1f,
                   PAGE + 12: 0xc0000000}))
    (tmp_path / "t__0.tadata.bin").write_bytes(
        dwords(5, {4 * PAGE: 0x04000000, 4 * PAGE + 4: 0x2000}))
    text = pbdump.report(tmp_path, "t__0")
    assert ("  CSTREAM PRIM_TILES 0x8a PRIM_VERTICES 14 PRIM_POINTS 0, "
            "OBJ_PRIMS 9 OBJ_ISP_ADDR 0x412, mask 0x1f\n") in text


def test_report_names_the_lines_third_dword_apart_from_a_mask(tmp_path):
    (tmp_path / "t__0.param.bin").write_bytes(
        dwords(3, {0: 0x04000004, PAGE: 0x4688000f, PAGE + 4: 0x0c000407, PAGE + 8: 0x00010003,
                   PAGE + 12: 0xc0000000}))
    (tmp_path / "t__0.tadata.bin").write_bytes(
        dwords(5, {4 * PAGE: 0x04000000, 4 * PAGE + 4: 0x2000}))
    text = pbdump.report(tmp_path, "t__0")
    assert ("  CSTREAM PRIM_TILES 0x88 PRIM_VERTICES 3 PRIM_POINTS 0, "
            "OBJ_PRIMS 3 OBJ_ISP_ADDR 0x407, dword 0x10003\n") in text


def test_regions_read_past_64_headers():
    """A large target's list runs past 64 headers (128 for 256 x 256): every non-zero header
    on the page is read."""
    td = dwords(5, {4 * PAGE + 12 * 100: 0x980e301e, 4 * PAGE: 0x0c000000})
    r = pbdump.regions(td)
    assert [x.index for x in r] == [0, 100] and r[1].flags == 0x98 and r[1].row == 0x301e


def test_form_map():
    """map: the regions as a grid (rows of 16 pixels, columns of 32), each cell the top half
    of its stream's first word, '+' when more objects follow, '....' without a stream."""
    td = dwords(5, {4 * PAGE: 0x04000000, 4 * PAGE + 4: 0x2000,
                    4 * PAGE + 12: 0x00020000, 4 * PAGE + 16: 0x2080,
                    4 * PAGE + 24: 0x02000002})
    param = dwords(3, {PAGE: 0x4490ffff, PAGE + 4: 0x04000406, PAGE + 8: 0xc0000000,
                       PAGE + 0x80: 0x44800701, PAGE + 0x84: 0x04000406,
                       PAGE + 0x88: 0x4490ffff, PAGE + 0x8c: 0x04000c06})
    assert pbdump.form_map(param, td).splitlines() == ["4490   4480+", "...."]
    # one object with a mask dword is one object: no '+'
    td = dwords(5, {4 * PAGE: 0x04000000, 4 * PAGE + 4: 0x2000})
    param = dwords(3, {PAGE: 0x5c8a7fff, PAGE + 4: 0x24000412, PAGE + 8: 0x1f,
                       PAGE + 12: 0xc0000000})
    assert pbdump.form_map(param, td).splitlines() == ["5c8a"]


def test_diff_lists_the_differing_dwords():
    """--diff: every dword that differs between two dumps, by file, slot offset and value."""
    a = dwords(2, {0: 1, PAGE + 4: 2})
    b = dwords(2, {0: 1, PAGE + 4: 3, 8: 7})
    assert pbdump.diff_words(a, b, base=0x1000) == [(0x1008, 0, 7), (0x2004, 2, 3)]
    assert pbdump.diff_words(a, a) == []


def test_prim_list_entries_keep_bit_15():
    # 0x0f000000 in VDM_INDEX2 and one winding of the random triangles set bit 15 of an entry
    assert pbdump._entries(0x56934a30) == [(16, 17, 18, 0), (19, 20, 21, 0)]
    assert pbdump._entries(0xd693ca30) == [(16, 17, 18, 1), (19, 20, 21, 1)]
    assert pbdump._entries(0x4a30ca30) == [(16, 17, 18, 1), (16, 17, 18, 0)]


def test_the_object_flags_the_entries_with_bit_15():
    ws = [0x04000004, 0x00030001, 0x04000000] + [0x3f800000] * 6 + [0x01d00200, 0x10f0]
    ws += [0xd693ca30, 0x1010, 0x00040101, 0, 0, 0, 0] + [0] * 8
    o = pbdump.object_fields(ws, isp_at=9, vertices=6, prims=2)
    assert o["PB_OBJ.PRIM_LIST"] == [(16, 17, 18), (19, 20, 21)]
    assert o["PB_OBJ.PRIM_LIST bit 15"] == [1, 1]
    lines = pbdump.object_lines(o)
    assert "  PB_OBJ.PRIM_LIST (16, 17, 18) (19, 20, 21), bit 15 in entries 0 1" in lines
    o["PB_OBJ.PRIM_LIST bit 15"] = [0, 0]
    assert "  PB_OBJ.PRIM_LIST (16, 17, 18) (19, 20, 21)" in pbdump.object_lines(o)
