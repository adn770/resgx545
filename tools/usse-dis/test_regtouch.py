# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Tests for regtouch.py — firmware MMIO register-access scanner."""
import os

import regtouch

# usse-dis lines, made up (the scanner reads the text; the words are placeholders)
LINES = [
    "     0: 0xFC20411001345678\tmov r9, #0x12345678",
    "     5: 0xFE00000000000000\tldr r9, #100, drc1",
    "     6: 0xFE00000000000000\tp2 str #101, #7",
    "     7: 0xFE00000000000000\t!p0 str #300, r5",
    "     8: 0xFE00000000000000\tstr r6, r4",     # register-supplied address: not static
    "garbage line",
]


def test_scan_finds_immediate_register_accesses():
    acc = regtouch.scan(LINES)
    assert [(a.insn, a.kind, a.reg) for a in acc] == [
        (5, "R", 0x190), (6, "W", 0x194), (7, "W", 0x4B0),
    ]


def test_summarize_counts_reads_and_writes():
    s = regtouch.summarize(regtouch.scan(LINES))
    assert s == {0x190: (1, 0), 0x194: (0, 1), 0x4B0: (0, 1)}


def test_load_names_skips_field_macros(tmp_path):
    p = tmp_path / "defs.h"
    p.write_text("#define EUR_CR_EVENT_STATUS 0x012C\n"
                 "#define EUR_CR_EVENT_STATUS_MASK 0x00000001\n"
                 "#define EUR_CR_EVENT_HOST_CLEAR 0x0134U\n")
    assert regtouch.load_names([p]) == {0x12C: "EUR_CR_EVENT_STATUS",
                                        0x134: "EUR_CR_EVENT_HOST_CLEAR"}


def test_r2_comments_name_each_access_site():
    s = regtouch.r2_comments(regtouch.scan(LINES), {0x190: "EUR_CR_A"})
    assert "CCu read EUR_CR_A @ 0x28" in s                # insn 5 * 8 bytes
    assert "CCu write 0x0194 @ 0x30" in s                 # unnamed -> hex offset


def test_r2_flags_name_the_emulation_window():
    """One flag per touched register at the r2 plugin's register-file window (base 4 GiB)."""
    s = regtouch.r2_flags(regtouch.scan(LINES), {0x190: "EUR_CR_A"})
    assert s.splitlines() == [
        "f sgx.EUR_CR_A 4 @ 0x100000190",
        "f sgx.cr_0x0194 4 @ 0x100000194",
        "f sgx.cr_0x04b0 4 @ 0x1000004b0",
    ]
    assert regtouch.ESIL_CR_BASE == 0x100000000


def test_default_names_come_from_the_gpl_header():
    """No header is built in; the names come from $RESGX545_REGDEFS."""
    assert regtouch.DEFAULT_DEFS == ()


def test_the_environment_names_the_headers(monkeypatch, tmp_path):
    """$RESGX545_REGDEFS (paths joined by os.pathsep) replaces the default; absent files drop."""
    h = tmp_path / "defs.h"
    h.write_text("")
    monkeypatch.setenv("RESGX545_REGDEFS", os.pathsep.join([str(h), str(tmp_path / "none.h")]))
    assert regtouch.default_defs() == [str(h)]
    monkeypatch.setenv("RESGX545_REGDEFS", str(tmp_path / "none.h"))
    assert regtouch.default_defs() == []
    monkeypatch.delenv("RESGX545_REGDEFS")
    assert all(os.path.exists(d) for d in regtouch.default_defs())
