# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""gen_verify.py: the kernel header is the table of regs.toml and fwtask.FORMS, and every form
row is a mask and value of doc/specs/usse_isa.md's listings."""
import pathlib
import sys

import pytest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fwtask  # noqa: E402
import gen_verify  # noqa: E402


def test_header_is_reproducible(tmp_path):
    a = gen_verify.render(fwtask.load_regs())
    assert a == gen_verify.render(fwtask.load_regs())
    assert a.startswith("/* SPDX-License-" "Identifier: GPL-2.0-only OR MIT */")


def test_header_lists_exactly_the_allowed_registers():
    h = gen_verify.render(fwtask.load_regs())
    assert "static const u16 sgx_own_str_regs[] __maybe_unused = { 69, 77, 517, 670, 691 };" in h
    assert "static const u16 sgx_own_ldr_regs[] __maybe_unused = { 7, 8, 81, 517, 670 };" in h
    assert "static const u16 sgx_own_clockgate_regs[] __maybe_unused = { 0, 1, 2, 3 };" in h


def test_header_deny_rows_leave_out_the_allowed_str_registers():
    h = gen_verify.render(fwtask.load_regs())
    for lo, hi in ((0x0110, 0x0110), (0x0118, 0x0130), (0x0138, 0x0144), (0x0ac4, 0x0ac8),
                   (0x0ad0, 0x0aec)):
        assert f"{{ 0x{lo:04x}, 0x{hi:04x} }}," in h
    assert "{ 0x0110, 0x0144 }," not in h and "{ 0x0ac4, 0x0aec }," not in h


def test_every_form_row_is_in_the_spec_listing():
    spec = pathlib.Path(gen_verify.spec_path()).read_text()
    for name, kind, mask, value in fwtask.FORMS:
        assert gen_verify.in_spec(spec, mask, value), name


def test_header_forms_follow_fwtask():
    h = gen_verify.render(fwtask.load_regs())
    for name, kind, mask, value in fwtask.FORMS:
        assert f"0x{mask:016x}ULL, 0x{value:016x}ULL, SGX_OWN_{kind}" in h


def test_committed_header_is_current():
    p = gen_verify.SGXFIVE / "sgx_own_regs.h"
    if not p.is_file():
        pytest.skip(f"SKIPPED, NOT PASSED: no fork checkout at {gen_verify.LINUX} (RESGX545_LINUX)")
    assert p.read_text() == gen_verify.render(fwtask.load_regs())


def test_test_blobs_header_is_reproducible_and_lists_both_kinds():
    h = gen_verify.render_test_blobs(fwtask.ASM)
    assert h == gen_verify.render_test_blobs(fwtask.ASM)
    assert "own_ok_x9b_r1" in h and "own_ok_null" in h
    for name in ("clock_str_ctl2", "clock_ldr_status", "str_reg_index", "emit", "br_out", "phas",
                 "cfi_other",
                 "patch_not_limm", "lapc_unpatched", "str_0a58", "str_core_id", "bad_magic"):
        assert f"own_bad_{name}" in h, name


def test_crafted_blobs_are_all_refused_by_the_python_verifier_for_their_reason():
    regs = fwtask.load_regs()
    for name, data, err, why in gen_verify.crafted_blobs():
        assert fwtask.refusal(data, regs) == (why or "parse"), name


def test_kernel_blobs_header_matches_the_sources():
    """The blobs the kernel's KUnit accepts are the ones the sources build now (the fork's copy)."""
    p = gen_verify.SGXFIVE / "sgxfive_owntask_blobs.h"
    if not p.is_file():
        pytest.skip(f"SKIPPED, NOT PASSED: no fork checkout at {gen_verify.LINUX} (RESGX545_LINUX)")
    assert p.read_text() == gen_verify.render_test_blobs(fwtask.ASM)
