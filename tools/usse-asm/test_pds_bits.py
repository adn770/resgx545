# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The encoding-bit probes (pds_bits.py): the unmapped bits of each PDS form, the table that
flips them one per case, and the reading of a run against each probe's unflipped case."""
from __future__ import annotations

import pathlib
import tomllib

import pytest

import pds_bits as B
import probe

ROOT = pathlib.Path(__file__).resolve().parents[2]
TEMPLATES = ROOT / "probes" / "pds" / "templates"


def test_unmapped_bits_are_neither_identifying_nor_in_a_field():
    forms = {f["order"]: f for f in B.forms()}
    assert forms[2420]["unmapped"] == 0x07ffffff            # nop: all but the opcode
    assert forms[2340]["unmapped"] == 0x00ff02f8            # tstz p, ds1[n]
    assert forms[2190]["unmapped"] == 0x00000010            # movs: bit 4
    # bra and call take 24 bits and abs's ds1[n] bits 15:10 (pds-encoding-bits-*): 281 were
    # unmapped before 11.4
    assert forms[2380]["unmapped"] == forms[2390]["unmapped"] == 0
    assert forms[2290]["unmapped"] == 0x00ff0280
    # mov128's bit 15 became the field lastpair in 11.14 (E379)
    assert forms[2240]["unmapped"] == 0x00ff0283
    assert sum(bin(f["unmapped"]).count("1") for f in forms.values()) == 269


def test_bits_lists_each_unmapped_bit_low_first():
    assert B.bits(0x00f80000) == [19, 20, 21, 22, 23]
    assert B.bits(0) == []


def test_every_base_names_a_form_and_assembles_to_it():
    forms = {f["order"]: f for f in B.forms()}
    for base in B.BASES:
        word = B.base_word(base)
        assert forms[base.order]["mask"] & word == forms[base.order]["val"], base.name


def test_the_table_flips_one_unmapped_bit_per_case():
    ps = B.probes()
    names = [p["name"] for p in ps]
    forms = {f["order"]: f for f in B.forms()}
    # a form with no unmapped bit left has no probe
    bases = [b for b in B.BASES if forms[b.order]["unmapped"]]
    assert len(names) == len(set(names)) == len(bases) == len(B.BASES) - 2
    for base, p in zip(bases, ps):
        un = B.bits(forms[base.order]["unmapped"])
        assert len(p["cases"]) == 1 + len(un)
        assert p["labels"][0] == "base" and p["labels"][1:] == [f"bit {b}" for b in un]
        word = B.base_word(base)
        slot = ["OP", "POST", "END"].index(base.slot)
        assert p["cases"][0][slot].count(f"0x{word:08X}") == 1
        for b, case in zip(un, p["cases"][1:]):
            assert case[slot].count(f"0x{word ^ 1 << b:08X}") == 1, (base.name, b)


def test_the_measured_forms_are_left_out():
    orders = {b.order for b in B.BASES}
    # mov32's and alum's unused bits have their own probes (pds-moves-mov32-spare,
    # pds-alu-alum-spare)
    assert 2220 not in orders and 2430 not in orders
    assert len(orders) == 25


def test_the_tables_load_and_every_case_assembles(tmp_path):
    B.main(["table", str(tmp_path)])
    names = {}
    for group, table in B.GROUPS.items():
        path = tmp_path / f"{table}.toml"
        text = path.read_text()
        assert all(line.rstrip() == line for line in text.splitlines())
        d = tomllib.loads(text)
        assert d["needs"] == (["render", "vm_low"] if group == "memory" else ["render"])
        ps = probe.load(path)
        for p in ps:
            probe.build(p, tmp_path / "bins", TEMPLATES)
        assert all(p.name.startswith(f"pds-{table}-") for p in ps)
        names[group] = {p.name.removeprefix(f"pds-{table}-") for p in ps}
        assert all(bool(p.low) == (group == "memory") for p in ps)
    assert names["memory"] == {"fence", "load", "store"}
    assert names["flow"] == {"rtn", "halt", "nop"}
    assert len(names["data"]) == 17


def test_before_regenerates_the_committed_tables(tmp_path):
    # the tables run on the laptop were written with bra/call bits 23:19 and abs ds1[n]'s bit
    # 15 unmapped (BEFORE); --before writes them again byte for byte
    B.main(["table", str(tmp_path), "--before"])
    for table in B.GROUPS.values():
        committed = (ROOT / "probes" / "pds" / f"{table}.toml").read_text()
        assert (tmp_path / f"{table}.toml").read_text() == committed, table
    forms = {f["order"]: f for f in B.forms(before=True)}
    assert sum(bin(f["unmapped"]).count("1") for f in forms.values()) == 281
    assert forms[2240]["unmapped"] == 0x00ff8283 and forms[2240]["pat"].endswith("ds[{2}]{3}")


def _obs(o0=0x0da7a000, scratch=((0, 1),), failed=None):
    return probe.Obs(o0=o0, mixed=(), failed=failed, scratch=tuple(scratch), pixels=None)


def test_classify_reads_each_case_against_the_base():
    obs = {"p__0": _obs(), "p__1": _obs(), "p__2": _obs(scratch=((0, 2),)),
           "p__3": _obs(failed="job hung")}
    got = B.classify("p", ["base", "bit 4", "bit 5", "bit 6"], obs)
    assert got == [("bit 4", "same"), ("bit 5", "differs: +0x000 0x00000001 -> 0x00000002"),
                   ("bit 6", "failed: job hung")]


def test_classify_without_a_base_reading_says_so():
    with pytest.raises(B.BitsError):
        B.classify("p", ["base", "bit 4"], {"p__1": _obs()})


def test_the_mov128_follow_up_marks_every_input_dword():
    """11.14 (E379): each data dword holds its own marker, so a dword read back names its
    source; bit 15 is set with each companion bit in turn, every case in RUNS runs."""
    ps = B.mov128_probes()
    assert [p["name"] for p in ps] == ["pds-mov128-bit15-companions", "pds-mov128-bit15-markers2",
                                       "pds-mov128-bit15-mr"]
    p = ps[0]
    marks = {int(v, 16) for v in p["params"].values()}
    assert len(marks) == 16
    assert len(p["cases"]) == len(p["labels"]) == B.MOV128_RUNS * len(B.MOV128_CASES)
    assert p["labels"][0].startswith("run 1: ") and p["labels"][-1].startswith(
        f"run {B.MOV128_RUNS}: ")
    base = B.mov128_word(52, 2)
    assert base == 0x27000868                    # mov128 ds[52], ds[4] (E261's words)
    words = [c[0].rsplit(" ", 1)[1] for c in p["cases"][:len(B.MOV128_CASES)]]
    assert words[0] == f"0x{base:08X}" and words[1] == f"0x{base | 1 << 15:08X}"
    assert f"0x{base | 1 << 15 | 1 << 16:08X}" in words
    assert f"0x{base | 1 << 15 | 0xff << 16:08X}" in words


def test_the_mov128_follow_up_assembles(tmp_path):
    t = tmp_path / "mov128-bit15.toml"
    B.main(["table", str(tmp_path), "--mov128"])
    t = tmp_path / "mov128-bit15.toml"
    assert tomllib.loads(t.read_text())["needs"] == ["render"]
    for p in probe.load(t):
        assert p.name.startswith("pds-mov128-bit15-")
        assert probe.build(p, tmp_path / p.name, TEMPLATES)


def test_locate_names_the_input_dword_a_value_came_from():
    params = {"A": "0xA0000002", "B": "0xA0000003", "I": "0xB0000002"}
    assert B.locate(0xA0000003, params) == "ds0[3]"
    assert B.locate(0x5FFFFFFD, params) == "~ds0[2]"           # a complemented temporary
    assert B.locate(0xB0000002, params) == "ds1[2]"
    assert B.locate(0x12345678, params) is None


def test_the_mr_follow_up_writes_mr_before_the_mov128_in_each_case():
    """The companions run showed bit 15 reading what movs mr wrote: the mr probe tells a value
    from a selection of registers (the source changed after the movs), and mr from any port."""
    p = B.mov128_probes()[2]
    word = f"0x{B.mov128_word(52, 2) | 1 << 15:08X}"
    assert len(p["labels"]) == B.MOV128_RUNS * len(B.MOV128_MR)
    for (label, before), case in zip(B.MOV128_MR, p["cases"]):
        assert before in case[0] and case[0].index(before) < case[0].index("/* ")
        assert case[0].endswith(word) or "without bit 15" in label
