# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""register_coverage.py: the per-register view is generated from the glossary's register and
field rows and the implemented bits the evidence records measured."""
import pytest

import register_coverage as rc


def row(name, loc, kind="register", evidence="-", citation="C0001", tier="1"):
    return dict(group="registers", id="G0001", name=name, status="named", term=name, kind=kind,
                sgx545=loc, meaning="a meaning", tier=tier, source="sgx545-ce",
                citation=citation, licence="GPL-2.0", evidence=evidence)


def test_the_view_is_current():
    regs = rc.registers()
    if not regs and not rc.DOC.exists():
        pytest.skip("no registers and no document yet")
    assert rc.DOC.exists() and rc.DOC.read_text() == rc.render(regs)


def test_a_register_gathers_its_fields_and_their_bits():
    rows = [row("CR_A", "0x0100"), row("CR_A.LOW", "0x0100[3:0]", "bitfield"),
            row("CR_A.TOP", "0x0100[31]", "flag"),
            row("CR_A.OLD", "SGX535 only: 0x0100[7:4]", "flag", tier="1c"),
            row("CR_B", "0x0104"), row("GlobalThreshold", "CR_DPM_TA_PAGE_THRESHOLD")]
    regs = rc.registers(rows, {})
    assert [r.name for r in regs] == ["CR_A", "CR_B"]
    a = regs[0]
    assert a.offset == 0x100 and a.fields == {"LOW": 0xf, "TOP": 0x80000000}
    assert a.uncovered() == 0x7ffffff0 and a.width is None
    assert regs[1].fields == {} and regs[1].uncovered() is None


def test_a_measured_width_bounds_the_uncovered_bits():
    rows = [row("CR_A", "0x0100"), row("CR_A.LOW", "0x0100[1:0]", "bitfield")]
    a = rc.registers(rows, {0x100: (0x3f, ["E026"])})[0]
    assert a.width == 0x3f and a.uncovered() == 0x3c
    assert "E026" in a.records


def test_widths_from_a_readback_table():
    body = ("| register | value before | bits that took a write |\n"
            "|---|---|---|\n"
            "| 0x0810 | 0x00000001 | 0 |\n"
            "| 0x0814 | 0x0000ffff | 16:0 |\n"
            "| 0x0800 | 0x00000030 | 0x00ffff3f |\n")
    assert rc.widths_in(body) == {0x810: 0x1, 0x814: 0x1ffff, 0x800: 0x00ffff3f}


def test_widths_from_a_sentence_on_implemented_bits():
    body = ("The registers they load read back, after a job with 0xffffffff, the implemented\n"
            "bits only: 0x0a04 0xfffffff0, 0x02b4 0x000000ff (the baseline job already reads\n"
            "that), 0x0368 0x00007fff.\n\nAn unrelated 0x0100 0x00000001 pair.\n")
    assert rc.widths_in(body) == {0xa04: 0xfffffff0, 0x2b4: 0xff, 0x368: 0x7fff}


def test_a_pair_outside_the_implemented_bits_sentence_is_not_a_width():
    body = ("Register 0x0100 0x00000001 held its value; the implemented bits: 0x0104\n"
            "0x0000000f. Then 0x0108 0x000000ff was read back.\n\n"
            "The implemented bits are in another record. 0x010c 0x00000003 is a value.\n")
    assert rc.widths_in(body) == {0x104: 0xf}


def test_a_register_that_takes_no_write_has_width_zero():
    body = ("| register | name | value before | bits that took a write | width |\n"
            "|---|---|---|---|---|\n"
            "| `0x0044` | `CR_HWPERF_COUNTER0` | `0x00000000` | 0x00000000 | 0 |\n"
            "| `0x0040` | `CR_HWPERF_CTRL` | `0x000001ff` | 12:0 | 13 |\n")
    assert rc.widths_in(body) == {0x44: 0, 0x40: 0x1fff}
    rows = [row("CR_C", "0x0044"), row("CR_C.VALUE", "0x0044[31:0]", "bitfield")]
    c = rc.registers(rows, {0x44: (0, ["E246"])})[0]
    assert c.width == 0 and c.uncovered() == 0
    assert "width 0 bits (-, E246)" in "".join(rc.entry(c))


def test_fields_on_bits_that_took_no_write_are_listed():
    rows = [row("CR_A", "0x0100"), row("CR_A.LOW", "0x0100[1:0]", "bitfield"),
            row("CR_A.TOP", "0x0100[31]", "flag")]
    a = rc.registers(rows, {0x100: (0x3, ["E246"])})[0]
    text = " ".join(rc.entry(a))
    assert "fields on bits that took no write: 31." in text
    assert "uncovered - (0 bits)" in text


def test_measured_merges_the_widths_of_several_records(tmp_path, monkeypatch):
    d = tmp_path / "evidence" / "isp"
    d.mkdir(parents=True)
    head = '+++\nid = "{}"\n+++\n\n'
    table = ("| register | bits that took a write |\n|---|---|\n| `0x0418` | {} |\n"
             "| `0x0420` | 31:0 |\n")
    (d / "E001-a.md").write_text(head.format("E001") + table.format("0"))
    (d / "E002-b.md").write_text(head.format("E002") + table.format("2:1"))
    monkeypatch.setattr(rc.evidence, "DIR", tmp_path / "evidence")
    got = rc.measured()
    assert got[0x418] == (0x7, ["E001", "E002"])
    assert got[0x420] == (0xffffffff, ["E001", "E002"])


def test_the_records_of_a_register_are_its_rows_and_its_fields():
    rows = [row("CR_A", "0x0100", evidence="[HW] E005"),
            row("CR_A.LOW", "0x0100[1:0]", "bitfield", citation="E007", tier="ours")]
    assert rc.registers(rows, {})[0].records == ["E005", "E007"]


def test_bit_ranges_print_high_first():
    assert rc.ranges(0x7ffffff0) == "30:4"
    assert rc.ranges(0x80000005) == "31, 2, 0"
    assert rc.ranges(0) == "-"


def test_an_entry_and_the_summary():
    rows = [row("CR_A", "0x0100"), row("CR_A.LOW", "0x0100[3:0]", "bitfield"),
            row("CR_B", "0x0104")]
    text = rc.render(rc.registers(rows, {0x104: (0x7, ["E026"])}))
    assert ("- `0x0100` `CR_A`: width 32 bits assumed; 1 field: LOW [3:0]; uncovered 31:4 "
            "(28 bits).") in text
    assert "- `0x0104` `CR_B`: width 3 bits (2:0, E026); no field rows. Records: E026." in text
    assert "| total | 2 | 1 | 1 | 28 | 0 |" in text


def test_main_writes_the_document_where_doc_does_not_exist(tmp_path, monkeypatch):
    monkeypatch.setattr(rc, "DOC", tmp_path / "doc" / "register_coverage.md")
    regs = rc.registers([row("CR_A", "0x0100")], {})
    monkeypatch.setattr(rc, "registers", lambda: regs)
    assert rc.main(["--check"]) == 1
    assert rc.main([]) == 0
    assert rc.main(["--check"]) == 0
