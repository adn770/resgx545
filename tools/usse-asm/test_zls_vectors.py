# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""zls_vectors.py: unit vectors of the ZLS store, load and control word (12.4)."""
from __future__ import annotations

import os
import pathlib

import pytest

import zls_vectors as zv

DATA = pathlib.Path(os.environ.get("RESGX545_DATA", str(pathlib.Path.home() / "src/resgx545-data")))
needs_data = pytest.mark.skipif(not (DATA / "zls/store-format-dumps/dumps").is_dir(), reason="no data")


def test_a_flip_of_the_control_changes_only_what_e411_says():
    base = zv.CONTROL_FIELDS
    assert zv.flip_fields(2)["store_depth"] is False and zv.flip_fields(2)["store_stencil"] is False
    assert zv.flip_fields(17) == {**base, "store_stencil": False}
    assert zv.flip_fields(18) == {**base, "store_depth": False}
    assert zv.flip_fields(19) == {**base, "negate": True}
    assert zv.flip_fields(24)["fmt"] == 1 and zv.flip_fields(25)["fmt"] == 2 and zv.flip_fields(26)["fmt"] == 4
    assert zv.flip_fields(3)["g"] == 0 and zv.flip_fields(4)["g"] == 3 and zv.flip_fields(11)["g"] == 1 + 256
    for b in (1,):
        assert zv.flip_fields(b) == {**base, "load": True}
    for b in (12, 13, 14, 15, 16, 20, 21, 22, 23, 27, 28, 29, 30, 31):
        assert zv.flip_fields(b) == base, b
    assert zv.flip_fields(0)["store_depth"] is True, "bit 0: the colour image is not written, the store is as the control's"


def test_the_load_lines_of_e467s_output_parse_into_their_cases():
    a = ("bits 1, 14 ctl=0x0017510e job: ok: depth store (32768, {'0 (the clear value of a stencil, or loaded "
         "dword 0)': 1, 'the loaded dword': 32767}) | stencil store (8192, {'0 (the clear value of a stencil, "
         "or loaded dword 0)': 8192})")
    v = zv.parse_load_line(a, "A")
    assert v["init"]["ctl"] == "0x0017510e" and v["init"]["test"] == "never"
    assert v["expect"]["depth"] == {"stored": 32768, "classes": {"zero": 1, "loaded": 32767}}
    assert v["expect"]["stencil"] == {"stored": 8192, "classes": {"zero": 8192}}
    b = ("bit:3 bits 1, 14 ctl=0x0017510e job: ok: triangle pixels ['16384'] of 32768, stored depth "
         "[('3e800000', 16384), ('3f000000', 16384)]")
    v = zv.parse_load_line(b, "B")
    assert v["init"]["depth_fill"] == "bit:3" and v["init"]["test"] == "less"
    assert v["expect"]["drawn"] == 16384
    assert v["expect"]["depth"] == {"stored": 32768, "values": {"3e800000": 16384, "3f000000": 16384}}
    c = "load 0x80000000 bits 1, 13, 14 ctl=0x0017710e job: ok: stored depth [('00000000', 32768)]"
    v = zv.parse_load_line(c, "C")
    assert v["init"]["depth_fill"] == "0x80000000"
    assert v["expect"]["depth"]["values"] == {"00000000": 32768}


RUN = """## A each bit of 0x17100c
== bit3-r1: tri --scratch 16 --poke blk:1=0x00400200
job: ok
scratch page 4: 640 changed, first +0x0 0x00000000
scratch page 12: 1024 changed, first +0x0 0x3f800000
scratch: 1664 dwords changed
target: 64x64 hash 0x99385a04ee01c585
diff: 0 of 4096 pixels
== bit3-r2: tri --scratch 16 --poke blk:1=0x00400200
job: ok
scratch page 4: 640 changed, first +0x0 0x00000000
scratch page 12: 1024 changed, first +0x0 0x3f800000
scratch: 1664 dwords changed
target: 64x64 hash 0x99385a04ee01c585
diff: 0 of 4096 pixels
== bit5-r1: tri --scratch 16 --poke blk:1=0x00400200
job: failed: job faulted, context lost (Input/output error)
scratch page 4: 512 changed, first +0x0 0x00000000
scratch: 512 dwords changed
diff: 3520 of 4096 pixels, first (32, 2) 0xdeadbeef expected 0xff203040
== bit5-r2: tri --scratch 16 --poke blk:1=0x00400200
job: failed: job faulted, context lost (Input/output error)
scratch page 4: 512 changed, first +0x0 0x00000000
scratch: 512 dwords changed
diff: 2976 of 4096 pixels, first (32, 16) 0xdeadbeef expected 0xff00ff00
== bit0-r1: tri --scratch 16 --poke blk:1=0x00400200
job: ok
scratch page 4: 1024 changed, first +0x0 0x00000000
scratch: 1024 dwords changed
diff: 4096 of 4096 pixels, first (0, 0) 0xdeadbeef expected 0xff203040
== bit0-r2: tri --scratch 16 --poke blk:1=0x00400200
job: ok
scratch page 4: 1024 changed, first +0x0 0x00000000
scratch: 1024 dwords changed
diff: 4096 of 4096 pixels, first (0, 0) 0xdeadbeef expected 0xff203040
## B bits 1, 13 and 14
"""


def test_the_flip_runs_are_read_from_the_output_and_the_two_runs_must_agree():
    runs = zv.parse_flip_runs(RUN)
    assert runs[3] == {"ok": True, "pages": {4: 640, 12: 1024}, "wrong": 0}
    assert runs[5]["ok"] is False
    assert runs[0] == {"ok": True, "pages": {4: 1024}, "wrong": 4096}
    # a bit whose two runs differ in a page count is not silently taken from the first
    with pytest.raises(AssertionError):
        zv.parse_flip_runs(RUN.replace("640 changed", "641 changed", 1))


def test_a_flip_vector_states_only_what_a_record_measured_and_refuses_the_rest():
    runs = zv.parse_flip_runs(RUN)
    e = zv.flip_expect(3, runs[3])
    assert e["g"] == 0 and e["pages"] == {"4": 640, "12": 1024} and e["writes_pixels"] is True
    assert "fmt" not in e
    e = zv.flip_expect(0, runs[0])
    assert e["writes_pixels"] is False and e["pages"] == {"4": 1024}
    # the faulted jobs (G bits 2 to 8) and the formats the model does not decode refuse by question
    assert zv.flip_expect(5, runs[5]) == {"refuse": ["Q242"]}
    assert zv.flip_expect(25, {"ok": True, "pages": {4: 1024}, "wrong": 0}) == {"refuse": ["Q242"], "pages": {"4": 1024}}
    assert zv.flip_expect(26, {"ok": True, "pages": {12: 640}, "wrong": 0}) == {"refuse": ["Q120"], "pages": {"12": 640}}


@needs_data
def test_every_flip_of_the_control_bits_run_reads_with_its_two_runs_agreeing():
    runs = zv.parse_flip_runs((DATA / "zls/control-bits/output.txt").read_text())
    assert sorted(runs) == list(range(32))
    assert [b for b in runs if not runs[b]["ok"]] == [5, 6, 7, 8, 9, 10, 11]
    assert runs[3]["pages"] == {4: 640, 12: 1024, 13: 1024, 14: 512}
    assert runs[4]["pages"] == {4: 512, 5: 512, 12: 1024, 14: 1024}
    assert runs[0]["wrong"] == 4096 and runs[1]["wrong"] == 0 and runs[2]["pages"] == {}


@needs_data
def test_the_control_vectors_carry_their_arrangement_and_only_known_keys():
    vs = {v["id"]: v for v in zv.ctl_vectors(DATA)}
    assert len(vs) == 47
    f = vs["zls-ctl__flip-03"]
    assert f["init"]["arrangement"] == "e411-scratch" and f["init"]["stencil"] is True
    allowed = {"g", "fmt", "load", "load_depth", "load_stencil", "store_depth", "store_stencil", "negate",
               "writes_pixels", "pages", "refuse"}
    assert all(set(v["expect"]) <= allowed for v in vs.values())
    assert "arrangement" not in vs["zls-ctl__driver-0017100c"]["init"]
    # the provenance says how the expectations were made: from a script's bit arithmetic and the
    # run's pages, not by hand
    assert "by hand" not in str(vs["zls-ctl__flip-03"]["provenance"])


@needs_data
def test_the_format_dump_counts_equal_the_records_and_the_vectors_are_deterministic():
    one = zv.format_vectors(DATA)
    two = zv.format_vectors(DATA)
    assert one == two
    by = {v["id"]: v for v in one}
    assert len(by) == 11
    assert by["zls-format__f1"]["expect"]["stored"] == 2 * 786432
    assert by["zls-format__f2"]["expect"]["stored"] == 2 * 393216
    assert by["zls-format__f4"]["expect"]["stored"] == 0
    assert by["zls-format__f3"]["expect"]["refuse"] == ["Q120"]
    assert all(v["init"]["stencil"] is False for v in one), "no stencil buffer, stated in every vector"


@needs_data
def test_the_load_vectors_come_from_every_line_of_the_output():
    vs = zv.load_vectors(DATA)
    assert len(vs) == 10 + 12 + 8
    assert len({v["id"] for v in vs}) == 30
