# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Tests of fwtask.py: the register lists, the verifier, the blob, determinism (phase 11.29)."""
import hashlib
import pathlib
import struct
import sys

import pytest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fwtask  # noqa: E402



def asm(text):
    return fwtask.assemble_text(text)


def verify(text, patches=(), **kw):
    return fwtask.verify(asm(text), list(patches), fwtask.load_regs(), **kw)


REGS = fwtask.load_regs()


def test_clock_gate_indices_refused_for_str_and_ldr_by_name():
    names = {c.name for c in REGS.clockgate}
    assert names == {"CR_CLKGATECTL", "CR_CLKGATECTL2", "CR_CLKGATESTATUS", "CR_CLKGATEOVERRIDE"}
    for idx in range(4):
        assert not REGS.str_ok(idx) and not REGS.ldr_ok(idx)
        assert REGS.why_refused(idx, "str").startswith("clock gate")
        assert REGS.why_refused(idx, "ldr").startswith("clock gate")


def test_clock_gate_in_code_str_and_ldr_refused():
    for idx in range(4):
        e = verify(f"str #{idx}, r1\nnop.end")
        assert any("clock gate" in x for x in e), e
        e = verify(f"ldr r1, #{idx}, drc0\nnop.end")
        assert any("clock gate" in x for x in e), e


def test_allowed_registers():
    assert REGS.str_ok(0x0814 // 4) and REGS.str_ok(0x0a78 // 4)
    assert REGS.ldr_ok(0x0814 // 4) and REGS.ldr_ok(0x0a78 // 4)
    assert all(REGS.ldr_ok(i) and not REGS.str_ok(i) for i in (7, 8, 0x0144 // 4))


def test_tier2_and_register3_not_in_this_phase():
    for off in (0x0520, 0x0810, 0x0818, 0x0abc, 0x0a7c, 0x0a80, 0x0800, 0x0b30):
        assert not REGS.str_ok(off // 4) and not REGS.ldr_ok(off // 4), hex(off)


def test_every_deny_offset_refused_for_str():
    for lo, hi in REGS.deny_ranges():
        for off in range(lo, hi + 1, 4):
            assert not REGS.str_ok(off // 4), hex(off)


# the named exceptions to regwidth's DENY: the registers a task of ours may str (round 3,
# R3-K1: the two host clear registers, E3; R3-K10: the EDM timer the closed tick handler writes,
# Q152), all other offsets of the DENY rows stay refused
STR_EXCEPTIONS = {0x0114: "CR_EVENT_HOST_CLEAR2", 0x0134: "CR_EVENT_HOST_CLEAR",
                  0x0acc: "CR_EVENT_TIMER"}


def test_every_regwidth_deny_offset_refused_for_str_and_ldr_except_timer_read():
    for lo, hi in fwtask.regwidth_deny():
        for off in range(lo, hi + 1, 4):
            if off in STR_EXCEPTIONS:
                assert REGS.str_ok(off // 4), hex(off)
            else:
                assert not REGS.str_ok(off // 4), hex(off)
            if off != 0x0144:
                assert not REGS.ldr_ok(off // 4), hex(off)


def test_deny_table_is_a_superset_of_regwidth():
    ours = REGS.deny_ranges()
    for lo, hi in fwtask.regwidth_deny():
        if hi <= 0x000c:
            continue    # the clock-gate rows, kept by name
        for off in range(lo, hi + 1, 4):
            assert off in STR_EXCEPTIONS or any(a <= off <= b for a, b in ours), hex(off)


def test_str_exceptions_are_named_allow_rows_for_str_only():
    for off, name in STR_EXCEPTIONS.items():
        a = REGS._allow[off // 4]
        assert a["name"] == name and a["use"] == "str", hex(off)
        assert not any(lo <= off <= hi for lo, hi in REGS.deny_ranges()), hex(off)


def test_host_clear_registers_str_accepted_ldr_refused_neighbours_refused():
    assert verify("str #69, r1\nnop.end") == []
    assert verify("str #77, r1\nnop.end") == []
    for idx in (69, 77):
        e = verify(f"ldr r1, #{idx}, drc0\nnop.end")
        assert any("not allowed for ldr" in x for x in e), e
    for off in (0x0110, 0x0118, 0x0130, 0x0138, 0x012c, 0x0144):
        e = verify(f"str #{off // 4}, r1\nnop.end")
        assert any("str" in x for x in e), (hex(off), e)


def test_default_deny_unlisted_index():
    assert not REGS.str_ok(1000) and not REGS.ldr_ok(1000)
    assert not REGS.str_ok(0x3fff) and not REGS.ldr_ok(0x3fff)


# ---- the form classes -------------------------------------------------------------------------
@pytest.mark.parametrize("line,kind", [
    ("mov r5, #0xdeadbeef", "MOVLIMM"), ("p0 mov r5, #0x12", "MOVLIMM"),
    ("mov.skipinv r5, #0xdeadbeef", "DENY"),
    ("mov r4, pa0", "MOVREG"), ("mov sa100, r12", "MOVREG"), ("mov i0, r20", "MOVREG"),
    ("nop", "NOP"), ("nop.end", "NOP"),
    ("wdf drc0", "PLAIN"), ("idf drc0, bif", "PLAIN"),
    ("ldad.bypassl1 r2, [r1,+#1], drc0", "LOAD_ABS"),
    ("stad [r1,+#8], r6", "STORE_ABS"),
    ("and.testtanz.chan0 !c0, p0, r6, r6", "PLAIN"),
    ("xor.testtaz.chan0 !c0, p1, r2, #5", "PLAIN"),
    ("ima32.u r8, r8, #1, r9.neg", "IMA32"),
    ("mov pclink, r5", "MOVPCLINK"), ("mov r22, pclink", "MOVFROMPC"), ("lapc", "LAPC"),
    ("br #3", "BR"), ("p0 br -#0x2", "BR"), ("ba #0x4005", "DENY"),
    ("ldr r1, #517, drc0", "LDR"), ("str #517, r1", "STR"),
    ("ldr r1, r2, drc0", "DENY"), ("str r2, r1", "DENY"),
])
def test_classify(line, kind):
    w = asm(line)[0]
    assert fwtask.classify(w)[0] == kind, hex(w)


@pytest.mark.parametrize("line", [
    "emitpds.tasks.taske #0, r2, r3, r4, #0x0",
    "emitpix1.freep #0, r0, r1",
    "bexception #0",
    "phas #0, #0, pixel, end, parallel",
])
def test_denied_forms(line):
    e = verify(line + "\nnop.end")
    assert e and any("not allowed" in x or "unknown" in x for x in e), e


def test_unknown_word_refused():
    e = fwtask.verify([0x0123456789abcdef], [], REGS)
    assert e


def test_str_deny_listed_register_refused():
    for off in (0x0a58, 0x0c00, 0x0080, 0x0b80, 0x0e80, 0x0810, 0x0520, 0x0818):
        e = verify(f"str #{off // 4}, r1\nnop.end")
        assert any("str" in x for x in e), (hex(off), e)


def test_ldr_allowed_and_str_allowed():
    assert verify("ldr r1, #517, drc0\nwdf drc0\nstr #517, r1\nnop.end") == []
    assert verify("ldr r1, #670, drc0\nwdf drc0\nstr #670, r1\nnop.end") == []
    assert verify("ldr r1, #81, drc0\nldr r2, #7, drc0\nldr r3, #8, drc0\nnop.end") == []


def test_str_of_core_id_refused():
    assert verify("str #7, r1\nnop.end")


def test_branch_out_of_blob_refused():
    assert verify("br #5\nnop.end")
    assert verify("br -#0x2\nnop.end")
    assert verify("ba #0x4010\nnop.end")      # blob is 2 words at 0x4000..0x4001
    assert verify("ba #0x0\nnop.end")


def test_branch_inside_ok():
    assert verify("br #2\nnop\nnop.end") == []
    assert verify("nop\nbr -#0x1\nnop.end") == []
    assert verify("ba #0x4001\nnop.end")       # ba is refused whole (R4)


def test_patch_must_be_on_limm():
    w = asm("nop\nmov r5, #0xdeadbeef\nnop.end")
    assert fwtask.verify(w, [fwtask.Patch(1, "res", 0)], REGS) == []
    assert fwtask.verify(w, [fwtask.Patch(0, "res", 0)], REGS)      # a nop
    assert fwtask.verify(w, [fwtask.Patch(7, "res", 0)], REGS)      # past the end
    w2 = asm("mov r4, pa0\nnop.end")
    assert fwtask.verify(w2, [fwtask.Patch(0, "res", 0)], REGS)     # a mov, not a limm


def test_lapc_needs_the_patched_triple():
    p = [fwtask.Patch(0, "cont0", 0)]
    ok = "mov r30, #0xdeadbeef\nmov pclink, r30\nlapc"
    assert fwtask.verify(asm(ok), p, REGS) == []
    assert fwtask.verify(asm("mov r30, #0xdeadbeef\nlapc"), p, REGS)
    # pclink from a register that no patched limm loaded
    assert fwtask.verify(asm("mov r30, #0xdeadbeef\nmov pclink, r5\nlapc"), p, REGS)
    assert fwtask.verify(asm("mov pclink, r30\nlapc"), [], REGS)


def test_blob_roundtrip_and_determinism():
    src = "mov r1, #0xdeadbeef ; @patch res+0x40\nnop.end\n"
    b1 = fwtask.build_blob_text(src)
    b2 = fwtask.build_blob_text(src)
    assert b1 == b2 and hashlib.sha256(b1).hexdigest() == hashlib.sha256(b2).hexdigest()
    parsed = fwtask.parse_blob(b1)
    assert parsed.words == asm("mov r1, #0xdeadbeef\nnop.end")
    assert parsed.patches == [fwtask.Patch(0, "res", 0x40)]
    assert b1[:8] == b"SGXOWN01"
    assert fwtask.verify_blob(b1, REGS) == []


def test_blob_with_bad_content_refused_at_build():
    with pytest.raises(fwtask.VerifyError):
        fwtask.build_blob_text("str #1, r1\nnop.end\n")


def test_labels_resolve_to_relative_br():
    src = "start: nop\n p0 br @end\n nop\nend: nop.end\n"
    w = fwtask.assemble_source(src)
    assert fwtask.classify(w[1])[0] == "BR"
    assert fwtask.br_target(1, w[1]) == 3


def test_entries_and_patch_markers():
    src = "@entry 0\nmov r30, #0xdeadbeef ; @patch cont0\nmov pclink, r30\nlapc\n"
    b = fwtask.build_blob_text(src)
    p = fwtask.parse_blob(b)
    assert p.entries == [0] and p.patches == [fwtask.Patch(0, "cont0", 0)]


def test_blob_size_limit():
    src = "nop\n" * 1025 + "nop.end\n"
    with pytest.raises(fwtask.VerifyError):
        fwtask.build_blob_text(src)


def test_map_has_sha256_of_each_section(tmp_path):
    (tmp_path / "a.s").write_text("nop.end\n")
    m = fwtask.build_map([tmp_path / "a.s"], tmp_path)
    assert m["a"]["sha256"] == hashlib.sha256((tmp_path / "a.blob").read_bytes()).hexdigest()
    assert m["a"]["source_sha256"] == hashlib.sha256((tmp_path / "a.s").read_bytes()).hexdigest()


def test_event_timer_str_accepted_ldr_refused_kicker_and_kicks_refused():
    assert verify(f"str #{0x0acc // 4}, r1\nnop.end") == []
    e = verify(f"ldr r1, #{0x0acc // 4}, drc0\nnop.end")
    assert any("not allowed for ldr" in x for x in e), e
    for off in (0x0ac4, 0x0ac8, 0x0ad0, 0x0aec):
        e = verify(f"str #{off // 4}, r1\nnop.end")
        assert any("str" in x for x in e), (hex(off), e)
