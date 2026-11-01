# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Pin the load/store text of usse-dis for fetch and increment forms.

The printed immediate is the encoded offset field. It is NOT always the first
element accessed: a fetch with a base+offset address starts one element later
(README, "Load/store addressing"). These tests stop anyone from "fixing" that
into the text, which would change the established syntax the assembler and the
radare2 plugin share. Expected texts are pinned usse-dis output for the same words,
which are made up: each sets the fields of one form to values of our choosing.
"""
import pathlib
import struct
import subprocess

import pytest

HERE = pathlib.Path(__file__).resolve().parent

# word -> its pinned text: offset, pre/post increment, fetch counts, cache modes and DRCs
FORMS = {
    0xE8033003A1014180: "ldad.bpcache.fetch4 r8, [r5,+#3], drc1",
    0xE8031002A1805400: "ldad.bpcache.fetch2 r12, [r1,+#40], drc0",
    0xF00230028001858E: "stad.bpcache.fetch4 [r6,+#11], r14",
    0xE82B0201A120C100: "ldad.fcfill r9, [r3,#2++], drc1",
    0xE8032202A1E10280: "ldad.bpcache.fetch3 r15, [r4,#5++], drc0",
    0xF00212028001DE02: "stad.bpcache.fetch2 [r7,#60++], r2",
    0xF02200028002820B: "stad.bpcache [r10,+#4], r11",
    0xE823000BA1A08300: "ldad.bpcache r13, [r2,-#6], drc1",
    0xF02000020000C41E: "stad.bpcache [r3,+r8], r30",
}


def _disasm(tool, tmp_path, words):
    blob = tmp_path / "words.bin"
    blob.write_bytes(struct.pack(f"<{len(words)}Q", *words))
    out = subprocess.run([str(tool), str(blob)], capture_output=True, text=True,
                         check=True).stdout
    return [line.split("\t", 1)[1].strip() for line in out.splitlines() if "\t" in line]


@pytest.fixture(scope="module")
def ours():
    subprocess.run(["make", "-s", "-C", str(HERE), "usse-dis"], check=True)
    return HERE / "usse-dis"


def test_fetch_and_increment_text_is_pinned(ours, tmp_path):
    assert _disasm(ours, tmp_path, list(FORMS)) == list(FORMS.values())

