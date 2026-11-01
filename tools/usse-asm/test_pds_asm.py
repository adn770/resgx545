# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""pds-asm: assemble PDS text as pds-dis prints it, with a data segment and labels.

Every form of the PDS table is checked through the made-up word that
tools/usse-dis/pinned.tsv pins for it: its text assembles to exactly that word.
The other texts are of our own choosing; several encodings print the same
text (unused operand fields), so they are compared through their decodes.
"""
import pytest

from test_usse_asm import pinned

OTHER = [
    "mov16 ds0[1], ds0[0].h", "mov32 ds0[0], ir1.1", "mov64 ds0[0], mr23",
    "mov128 ds[0], ds[0], swap",
    "load 0x00000000, ds0[48-54]", "load 0x00012340, ds1[56]", "store 0x00001230, ds0[55-59]",
    "(p0) mul ds1[26], ds0[4].h, ds1[16].h", "(p0) abs ds1[50], ds1[30]", "(if0) not ds0[13], tim",
    "rwfence", "rfence", "nop", "alum signed", "call 0x00001234", "(p0) shl ds1[26], ds0[1], 62",
    "shr ds1[63], ds0[0], 0", "shl ds0[0], ds0[0], 4294967232", "tstn , ds0[0]", "(alun) rtn",
    "movsa doutd, tim.l, ds1[2], tim.h, ds1[3]", "(aluz) sbc ds0[1], ds0[63], ds1[0]",
    "movs doutu, ds0[2], ds0[3], ds1[1], ds0[2]", "(p0) bra 0x00000007", "halt",
]


def test_every_pinned_form_assembles_to_its_word(pds_asm):
    rows = pinned("pds")
    assert len(rows) > 20
    assert pds_asm("\n".join(t for _, _, t in rows)) == [w for _, w, _ in rows]


def test_other_groups_round_trip(pds_asm, pds_dis):
    assert pds_dis(pds_asm("\n".join(OTHER))) == OTHER


def test_data_segment_and_labels(pds_asm, pds_dis):
    src = """
        .word 0x00000008        ; data dword 0
        .word 2
        tstz p0, ds1[48]
        (p0) bra skip           ; index counted from the first instruction
        halt
    skip:
        nop
        bra skip
    """
    words = pds_asm(src)
    assert words[:2] == [8, 2]
    assert pds_dis(words, 2)[2:] == ["tstz p0, ds1[48]", "(p0) bra 0x00000003", "halt", "nop",
                                     "bra 0x00000003"]


def test_listing_input(pds_asm):
    """pds-dis output assembles back: a data line takes its value from the hex column, an
    instruction line from its text."""
    src = "0: 0x00000008\tdata\n1: 0x12345678\tmovs doutu, ds0[2], ds0[3], ds1[1], ds0[2]\n"
    assert pds_asm(src) == [8] + pds_asm("movs doutu, ds0[2], ds0[3], ds1[1], ds0[2]")


def test_reserved_text_is_refused(pds_asm):
    for bad in ["movs ir1, ds0[0], ds0[0], ds0[0], ds0[0]",       # reserved port
                "movs doutu, ds0[0], ds0[2], ds0[0], ds0[0]",     # two ds0 pairs
                "add ds0[0], ir2, ds1[0]", "bra nowhere"]:
        assert pds_asm(bad, check=False).returncode == 1, bad


@pytest.mark.parametrize("text", ["shl ds0[0], ds0[0], 64", "load 0x00000002, ds0[48]"])
def test_unencodable_values_are_refused(pds_asm, text):
    assert pds_asm(text, check=False).returncode == 1


def test_a_data_line_reads_its_hex_column_in_either_case(pds_asm):
    assert pds_asm("0: 0X00000008\tdata\n1: 0x0000000A\tdata\nhalt\n")[:2] == [8, 10]


def test_a_word_wider_than_32_bits_is_refused(pds_asm):
    r = pds_asm(".word 0x100000000\nnop\n", check=False)
    assert r.returncode == 1 and ":1: bad .word value" in r.stderr
