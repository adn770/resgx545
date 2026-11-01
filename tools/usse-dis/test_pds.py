# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Tests for the clean-room PDS decoder (pds.c via the pds-dis CLI).

Expected texts are pinned pds-dis output for the same words: a change to a
form that alters them fails here. The words are made up: each sets the fields
of one form to values of our choosing, none is taken from a program.
"""
import pathlib
import struct
import subprocess

import pytest

HERE = pathlib.Path(__file__).resolve().parent


@pytest.fixture(scope="module")
def dis(tmp_path_factory):
    subprocess.run(["make", "-s", "-C", str(HERE), "pds-dis"], check=True)
    blob = tmp_path_factory.mktemp("pds") / "words.bin"

    def run(*words):
        blob.write_bytes(struct.pack(f"<{len(words)}I", *words))
        out = subprocess.run([str(HERE / "pds-dis"), str(blob), "0"],
                             capture_output=True, text=True, check=True).stdout
        return [line.split("\t", 1)[1] for line in out.splitlines()]
    return run


# Made-up words for the movs, halt, tstz, bra and bitwise forms, with variants of their
# fields (pinned.tsv, test_pinned.py, holds one made-up word for every form;
# test_firmware.py checks at run time that the forms the user's EDM programs use are
# among these).
HALT = 0x15 << 27 | 7 << 24          # halt, predicate 7 (always): the form's only word
EDM_FORMS = {
    0x070CA305: "movs doutu, ds0[6], ds0[7], ds1[10], ds0[6]",
    0x0704D885: "movs doutu, ds1[13], ds0[2], ds0[3], ds0[2]",
    0x07100203: "movs doutd, ds0[8], ds0[9], ds0[8], ds0[8]",
    0x07806406: "movs douta, ir0.l, ds1[6], ir0.l, ir0.l",
    0x0788A606: "movs douta, tim.l, ds1[11], tim.l, tim.l",
    HALT: "halt",
    0x87820001: "tstz p1, ir1",
    0x8700C902: "tstz p2, ds1[50]",
    0x81820000: "(p1) tstz p0, ir1",
    0x91000135: "(p1) bra 0x00000135",
    0x9700003A: "bra 0x0000003A",
    0xCF822432: "and ds0[50], ir1, ds1[9]",
    0xCF623074: "and ds1[52], ds0[49], ds1[12]",
    0xD76AC473: "xor ds1[51], ds0[53], ds1[49]",
    0xD164E477: "(p1) xor ds1[55], ds0[50], ds1[57]",
}


def test_edm_program_forms(dis):
    assert dis(*EDM_FORMS) == list(EDM_FORMS.values())


OTHER = {
    0x0F000101: "mov16 ds0[1], ds0[0].h",
    0x17000000 | (0x83 << 9): "mov32 ds0[0], ir1.1",
    0x1F000000 | (0x41 << 10): "mov64 ds0[0], mr23",
    0x27000100: "mov128 ds[0], ds[0], swap",
    0x37000000: "load 0x00000000, ds0[48-54]",
    0x31E1C883: "load 0x0007220C, ds1[56]",
    0x3D9D03AC: "store 0x00040EB0, ds0[55-59]",
    0x6009435A: "(p0) mul ds1[26], ds0[4].h, ds1[16].h",
    0x689CF972: "(p0) abs ds1[50], ds1[30]",
    0xDB859E8D: "(if0) not ds0[13], tim",
    0x7F000001: "rwfence",
    0xB05F8654: "nop",
    0xBF000001: "alum signed",
    0x9F000000 | 0x1234: "call 0x00001234",
    0xF0013E5A: "(p0) shl ds1[26], ds0[1], 62",
    0xFF0000FF: "shr ds1[63], ds0[0], 0",
    0x8F000004: "tstn , ds0[0]",
}


def test_other_groups(dis):
    assert dis(*OTHER) == list(OTHER.values())


SELECTORS = ["ir0", "ir1", "pc", "tim"]


def test_mov_specials_are_a_selector_and_bit_9(dis):
    """mov32/mov16 special sources: selector = index >> 1 over
    ir0, ir1, pc, tim, then bit 9 of the word as .0/.1 (reads 0 through mov16 on SGX545, not
    decoded by mov32); selector 4 and up stays undecoded."""
    mov32 = [0x17000000 | v << 9 for v in range(128, 137)]
    want = [f"mov32 ds0[0], {s}.{b}" for s in SELECTORS for b in (0, 1)]
    assert dis(*mov32) == want + [f".word 0x{mov32[-1]:08X}"]
    mov16 = [0x0F000000 | v << 8 for v in range(256, 273)]
    want = [f"mov16 ds0[0], {s}.{b}.{h}" for s in SELECTORS for b in (0, 1) for h in "lh"]
    assert dis(*mov16) == want + [f".word 0x{mov16[-1]:08X}"]


def test_shift_amount_is_signed(dis):
    assert dis(0xF7004000) == ["shl ds0[0], ds0[0], 4294967232"]      # -64


@pytest.mark.parametrize("word", [
    0x705E4D75,             # reserved arithmetic type
    0x07000000 | 11,        # movs to a reserved destination
    0x07900000,             # movs from a reserved input-register base
    0x47000000 | (0x43 << 17),   # add from a reserved source register
])
def test_reserved_encodings_are_not_guessed(dis, word):
    assert dis(word) == [f".word 0x{word:08X}"]


def test_analysis_api(tmp_path):
    exe = tmp_path / "test_pds_api"
    subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-I", str(HERE), "-o", str(exe),
                    str(HERE / "test_pds_api.c"), str(HERE / "pds.c"), str(HERE / "usse_form.c"),
                    str(HERE / "usse.c")], check=True)
    r = subprocess.run([str(exe)], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout


def _cli(*args):
    subprocess.run(["make", "-s", "-C", str(HERE), "pds-dis"], check=True)
    return subprocess.run([str(HERE / "pds-dis"), *map(str, args)], capture_output=True, text=True)


def test_forms_lists_the_table():
    """--forms: index, mask, value, the bits the form reads and its pattern, as usse-dis
    --forms prints them, at the PDS word's width."""
    lines = _cli("--forms").stdout.splitlines()
    assert lines[0] == "0\tF8000000\t00000000\tFFFFFFEF\t{0}movs {1}, {2}"
    assert lines[22] == "22\tF8000000\tA8000000\tFF000000\t{0}halt"
    assert len(lines) == 27


def test_regs_names_the_data_registers(tmp_path):
    """--regs: each data dword with the register it loads, by the row rule (row r is
    ds0[2r], ds0[2r+1], ds1[2r], ds1[2r+1]); the instructions are unchanged."""
    blob = tmp_path / "p.bin"
    blob.write_bytes(struct.pack("<7I", *range(1, 7), HALT))
    out = _cli("--regs", blob, 6).stdout.splitlines()
    assert [ln.split("\t", 1)[1] for ln in out] == [
        "data ds0[0]", "data ds0[1]", "data ds1[0]", "data ds1[1]", "data ds0[2]", "data ds0[3]",
        "halt"]


def test_which_names_the_decoding_form(tmp_path):
    blob = tmp_path / "p.bin"
    blob.write_bytes(struct.pack("<3I", 5, HALT, 0x77000000))
    out = _cli("--which", blob, 1).stdout.splitlines()
    assert out == ["0: 0x00000005\tdata", "1: 0xAF000000\thalt\t#22",
                   "2: 0x77000000\t.word 0x77000000\t#-1"]
    assert _cli("--bogus", blob, 1).returncode == 2
