# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Pin the text of the table-driven USSE decoder (usse_form.c).

The expected texts are pinned usse-dis output for the same words: a change to
a form that alters them fails here. The words are made up: each sets the
fields of one form to values of our choosing (registers, immediates, flags,
banks), none is taken from a program. They are variants of the fields of the
phas, limm, mov, emitpix and nop forms; pinned.tsv (test_pinned.py) holds one
made-up word for every form. test_firmware.py checks at run time that the forms
the user's transfer programs use are among these.
"""
import pathlib
import struct
import subprocess

import pytest

HERE = pathlib.Path(__file__).resolve().parent

# class-5 mov, skipinv end, o4 from pa3: the base of the bit-flip variants below
MOV = 0x28851001A0800180

FORMS = {
    # phas: immediate and register forms
    0xFA44070300000028: "phas #40, #12, pixel, end, parallel",
    0xFA44270500000007: "phas #7, #20, pixel, end, perinstance",
    0xFA40000000000309: "phas r6, r9",
    # limm: flags, predicates, immediates across the split field and every destination bank
    0xFCA4411100545678: "mov.skipinv.end o2, #0x12345678",
    0xFCA690E10023F00F: "mov.skipinv.end o1, #0xA5C3F00F",
    0xFCA0000000E00400: "mov.skipinv r7, #0x00000400",
    0xFCA0000002A00001: "mov.skipinv r21, #0x00000001",
    0xFC20000001810000: "mov r12, #0x00010000",
    0xFC240851006BCDEF: "p3 mov.end o3, #0x00ABCDEF",
    0xFCAC000108A00010: "mov.skipinv.end g5, #0x00000010",
    0xFCAC000200000077: "mov.skipinv.end i., #0x00000077",
    0xFCAC000200600300: "mov.skipinv.end i.lh, #0x00000300",
    0xFCA4000304600020: "mov.skipinv.end o[il + #3], #0x00000020",
    0xFCA000000FA00003: "mov.skipinv i1, #0x00000003",
    # class-5 mov: flags, repeat, write mask and source banks
    MOV: "mov.skipinv.end o4, pa3",
    0x2825100021400100: "mov.end.repeat2 r10, r2",
    MOV ^ 1 << 49: "mov.skipinv.end o4, #0x00000003",
    MOV ^ 1 << 45: "mov.skipinv.end o4.xy, pa3",
    # emitpix: one and two sources, a register or an immediate
    0xFB20010200210280: "emitpix1.freep #2 /* incp */, r4, r5",
    0xFB24002108E18388: "emitpix2.end.freep #1 /* incp */, r6, r7, r8, #0x00000123",
    0xFB26000B8022428B: "emitpix2.end.freep #3 /* incp */, r9, #5, r11, #0x00000040",
    # nop flags; bits 37:2 lie outside every field and are ignored
    0xF804014000000000 | 0x1234567800: "nop.end",
    0xF884094000000003 | 0x0ABCDE0000: "nop.syncs.nosched.end.tog.trigger",
}


def _disasm(tool, tmp_path, words):
    blob = tmp_path / "words.bin"
    blob.write_bytes(struct.pack(f"<{len(words)}Q", *words))
    out = subprocess.run([str(tool), str(blob)], capture_output=True, text=True,
                         check=True).stdout
    return [line.split("\t", 1)[1].strip() for line in out.splitlines() if "\t" in line]


@pytest.fixture(scope="module", autouse=True)
def build():
    subprocess.run(["make", "-s", "-C", str(HERE), "usse-dis"], check=True)


def test_forms_decode_as_pinned(tmp_path):
    words = list(FORMS)
    got = _disasm(HERE / "usse-dis", tmp_path, words)
    assert dict(zip(words, got)) == FORMS


def test_forms_dump_lists_every_form():
    out = subprocess.run([str(HERE / "usse-dis"), "--forms"], capture_output=True,
                         text=True, check=True).stdout.splitlines()
    assert len(out) > 50
    for line in out:
        idx, mask, val, bits, pat = line.split("\t")
        assert int(val, 16) & ~int(mask, 16) == 0
        assert int(mask, 16) & ~int(bits, 16) == 0
    assert any("emitpix2" in line for line in out)


def test_analysis_api(tmp_path):
    """usse_classify and usse_branch (usse.h), the analysis frontends' view of a word."""
    exe = tmp_path / "test_usse_api"
    subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-I", str(HERE), "-o",
                    str(exe), str(HERE / "test_usse_api.c"), str(HERE / "usse.c"),
                    str(HERE / "usse_form.c")], check=True)
    r = subprocess.run([str(exe)], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout
