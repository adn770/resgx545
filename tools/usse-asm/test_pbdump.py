# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""pbdump.py: reading the render dumps (the parameter slot from its PB, the TA data)."""
from __future__ import annotations

import struct

import pbdump

PAGE = 4096


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


def test_diff_lists_the_differing_dwords():
    """--diff: every dword that differs between two dumps, by file, slot offset and value."""
    a = dwords(2, {0: 1, PAGE + 4: 2})
    b = dwords(2, {0: 1, PAGE + 4: 3, 8: 7})
    assert pbdump.diff_words(a, b, base=0x1000) == [(0x1008, 0, 7), (0x2004, 2, 3)]
    assert pbdump.diff_words(a, a) == []
