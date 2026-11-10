# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The default-deny verifier against crafted blobs (phase 11.29 review R1 to R5): every refusal
checks its reason, not only that the blob is refused, and every word is canonical (a bit that no
field of its form names must be zero or what the form pins). A closed byte is never involved."""
import pathlib
import sys

import pytest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fwtask  # noqa: E402
import gen_verify  # noqa: E402

REGS = fwtask.load_regs()
Y = fwtask.Why
CRAFTED = {name: (data, err, why) for name, data, err, why in gen_verify.crafted_blobs()}


def asm(text):
    return fwtask.assemble_text(text)


def why_of(words, patches=(), entries=()):
    err = fwtask.verify_why(list(words), list(patches), REGS, entries)
    return err[0][1] if err else None


@pytest.mark.parametrize("name", sorted(CRAFTED))
def test_crafted_blob_is_refused_for_its_reason(name):
    data, err, why = CRAFTED[name]
    assert fwtask.refusal(data, REGS) == (why or "parse")
    assert fwtask.verify_blob(data, REGS), name


@pytest.mark.parametrize("review,names", [
    ("R1", ["lapc_stale_limm", "lapc_addend", "br_over_pclink", "pclink_predicated", "pclink_bank",
            "lapc_other_reg", "pclink_elsewhere", "br_to_pclink", "br_to_lapc", "entry_in_triple"]),
    ("R2", ["stad_fetch", "stad_regoff", "alu_add", "base_loaded", "base_unset", "base_overwritten",
            "base_one_path", "base_past_the_page", "base_ima32", "base_ldad"]),
    ("R4", ["ba_in", "ba_out", "ba_savelink", "br_savelink"]),
    ("R5", ["last_nop", "last_cond_br", "last_mov", "last_cond_through"]),
    ("R3-K3", ["mov_pa0", "mov_pa1", "mov_pa5", "mov_pa127"]),
])
def test_each_review_item_has_its_crafted_blobs(review, names):
    for n in names:
        assert n in CRAFTED, (review, n)


# ---- R1: the continue triple ------------------------------------------------------------------
CONT = ["mov r30, #0xdeadbeef", "mov pclink, r30", "lapc"]
C0 = [fwtask.Patch(0, "cont0", 0)]


def test_the_triple_is_accepted_and_needs_nothing_else():
    assert why_of(asm("\n".join(CONT)), C0, [0]) is None
    assert why_of(asm("nop\n" + "\n".join(CONT)), [fwtask.Patch(1, "cont2", 0)], [0]) is None


def test_the_shared_exit_patch_cont4_is_a_continue_patch_and_slot_5_is_not():
    """R3-K11: slot 4 of a continue patch is the closed tasks' shared exit (the kernel resolves
    it only for the firmware the index was read from); slot 5 and up stay a bad slot."""
    w = asm("\n".join(CONT))
    assert why_of(w, [fwtask.Patch(0, "cont4", 0)], [0]) is None
    assert why_of(w, [fwtask.Patch(0, "cont5", 0)], [0]) == Y.PATCH_SLOT
    assert why_of(w, [fwtask.Patch(0, "cont255", 0)], [0]) == Y.PATCH_SLOT
    assert why_of(w, [fwtask.Patch(0, "cont4", 4)], [0]) == Y.PATCH_ADD
    assert fwtask.EXIT_SLOT == 4


def test_cont4_round_trips_and_is_applied_from_the_exit_index_given():
    b = fwtask.build_blob_text("@entry 0\nmov r30, #0xdeadbeef ; @patch cont4\nmov pclink, r30\nlapc\n")
    p = fwtask.parse_blob(b)
    assert p.patches == [fwtask.Patch(0, "cont4", 0)]
    out = fwtask.apply_patches(p.words, p.patches, 0, {4: 0x1234})
    assert fwtask.limm_get(out[0]) == 0x1234 and out[1:] == p.words[1:]


def test_a_branch_to_the_limm_of_the_triple_is_fine():
    w = asm("p0 br #1\nmov r1, #0\n" + "\n".join(CONT).replace("r30", "r30"))
    assert why_of(w, [fwtask.Patch(2, "cont0", 0)], [0]) is None


def test_a_patched_limm_that_is_not_in_the_triple_is_harmless_but_a_pclink_write_is_not():
    w = asm("mov r30, #0xdeadbeef\nmov r5, r30\nnop.end")
    assert why_of(w, C0, [0]) is None
    assert why_of(asm("mov pclink, r5\nnop.end")) == Y.PCLINK


# ---- R2: stores ---------------------------------------------------------------------------------
PAGE = [fwtask.Patch(0, "res", 0)]


def test_a_store_through_the_page_base_is_accepted_up_to_the_end_of_the_page():
    w = asm("mov r1, #0xdeadbeef\nstad [r1,+#127], r4\nnop.end")
    assert why_of(w, [fwtask.Patch(0, "res", 0x1000 - 4 * 128)], [0]) is None
    assert why_of(w, [fwtask.Patch(0, "res", 0x1000 - 4 * 127)], [0]) == Y.BASE
    w = asm("mov r9, #0xdeadbeef\nstad [r9,+#3], r4\nldad.bypassl1 r2, [r9,+#0], drc0\nwdf drc0\nnop.end")
    assert why_of(w, [fwtask.Patch(0, "res", 0xff0)], [0]) is None


def test_a_store_base_must_hold_on_every_path_and_after_every_write():
    base = "mov r1, #0xdeadbeef\n"
    assert why_of(asm(base + "mov r1, r4\nstad [r1,+#0], r4\nnop.end"), PAGE, [0]) == Y.BASE
    assert why_of(asm(base + "ldr r1, #7, drc0\nwdf drc0\nstad [r1,+#0], r4\nnop.end"), PAGE, [0]) == Y.BASE
    assert why_of(asm(base + "mov r22, pclink\nmov r1, pclink\nstad [r1,+#0], r4\nnop.end"), PAGE, [0]) == Y.BASE
    # a write to another register does not matter, nor a write to the same number in another bank
    ok = base + "mov r2, r4\nmov sa1, r4\nmov i1, r4\nstad [r1,+#0], r4\nnop.end"
    assert why_of(asm(ok), PAGE, [0]) is None


def test_a_loop_back_to_the_limm_keeps_the_base():
    w = asm("mov r1, #0xdeadbeef\nstad [r1,+#0], r4\np0 br -#0x1\nnop.end")
    assert why_of(w, PAGE, [0]) is None
    # the loop head does not set it: a path from the entry has no base
    w = asm("stad [r1,+#0], r4\nmov r1, #0xdeadbeef\np0 br -#0x2\nnop.end")
    assert why_of(w, [fwtask.Patch(1, "res", 0)], [0]) == Y.BASE


def test_code_no_entry_reaches_is_not_checked_but_every_word_is_still_canonical():
    w = asm("nop.end\nstad [r5,+#0], r4\nnop.end")
    assert why_of(w, (), [0]) is None
    assert why_of([w[0], 0x0123456789abcdef, w[2]], (), [0]) == Y.UNKNOWN


# ---- R3: canonical words ------------------------------------------------------------------------
CANON = {
    "ldr #7": "ldr r13, #7, drc0", "ldr #517": "ldr r13, #517, drc0",
    "str #517": "str #517, r10", "str #670": "str #670, r10",
    "mov pclink": "mov pclink, r30", "lapc": "lapc", "nop": "nop", "nop.end": "nop.end",
    "clock ldr 0": "ldr r1, #0, drc0", "clock ldr 1": "ldr r1, #1, drc0",
    "clock ldr 2": "ldr r1, #2, drc0", "clock ldr 3": "ldr r1, #3, drc0",
    "clock str 0": "str #0, r1", "clock str 1": "str #1, r1",
    "clock str 2": "str #2, r1", "clock str 3": "str #3, r1",
    "limm": "mov r5, #0x12345678", "mov reg": "mov r4, pa0", "from pclink": "mov r22, pclink",
    "br": "br #2", "stad": "stad [r1,+#8], r6", "ldad": "ldad.bypassl1 r2, [r1,+#1], drc0",
    "idf": "idf drc0, bif", "wdf": "wdf drc0", "alu": "xor.testtaz.chan0 !c0, p1, r2, #5",
    "ima32": "ima32.u r8, r8, #1, r9.neg",
}


def pinned_bits(form):
    row = next(r for r in fwtask.FORMS if r[0] == form)
    return [b for b in range(64) if row[2] >> b & 1]


@pytest.mark.parametrize("label", sorted(CANON))
def test_a_stray_bit_in_a_canonical_word_is_never_accepted_as_the_same_form(label):
    (w,) = asm(CANON[label])
    kind, name = fwtask.classify(w)
    assert kind not in ("UNKNOWN", "DENY"), (label, name)
    flipped_ok = 0
    for b in pinned_bits(name):
        v = w ^ 1 << b
        k2, n2 = fwtask.classify(v)
        assert n2 != name, (label, b)
        if k2 in ("UNKNOWN", "DENY"):
            assert why_of([v, asm("nop.end")[0]]) in (Y.UNKNOWN, Y.DENY), (label, b)
        else:
            flipped_ok += 1             # it is another canonical form: its own checks apply
    assert flipped_ok < 8, label


@pytest.mark.parametrize("label", [k for k in sorted(CANON) if k.startswith("clock")])
def test_no_single_bit_change_of_a_clock_gate_word_is_accepted(label):
    """The word, with each of its 64 bits flipped in turn, is refused in a blob of its own unless
    the bit is in the register index (that is a different register, checked by its number)."""
    (w,) = asm(CANON[label])
    kind, name = fwtask.classify(w)
    idx_bits = {b for b in range(64) if (fwtask.SRC2N | fwtask.SRC0N) >> b & 1}
    for b in range(64):
        if b in idx_bits:
            continue
        v = w ^ 1 << b
        assert why_of([v, asm("nop.end")[0]]) is not None or fwtask.classify(v)[0] in ("LDR", "STR"), (label, b)
        if fwtask.classify(v)[0] in ("LDR", "STR"):
            assert why_of([v, asm("nop.end")[0]]) == Y.CLOCK, (label, b)


def test_the_pa_bank_bit_of_a_mov_makes_it_the_pa_row_not_the_mov_row():
    """bit 33 (the destination bank's high bit) of an allowed mov: the pa destination row, whose
    own number check applies; with bit 51 beside it, no form."""
    (w,) = asm("mov r4, pa0")
    assert fwtask.classify(w ^ 1 << 33) == ("MOVPA", "mov-reg-pa")
    assert why_of([w ^ 1 << 33, asm("nop.end")[0]]) is None          # pa4
    assert fwtask.classify(w ^ 1 << 33 ^ 1 << 51)[0] == "UNKNOWN"
    (w,) = asm("mov r1, pa0")
    assert why_of([w ^ 1 << 33, asm("nop.end")[0]]) == Y.PA           # pa1


def test_ldr_and_str_unnamed_bits_found_by_the_review_are_refused():
    """bit 54, bits 50:49 and bits 31:30 of an allowed ldr #7 (R3: the old masks accepted all)."""
    (w,) = asm("ldr r13, #7, drc0")
    for b in (54, 50, 49, 31, 30, 51, 55, 43):
        assert fwtask.classify(w ^ 1 << b)[0] in ("UNKNOWN", "DENY") or b == 51, b


def test_all_row_masks_pin_every_bit_a_field_does_not_name():
    for name, kind, mask, value in fwtask.FORMS:
        assert value & ~mask == 0, name
        if kind != "DENY":
            assert bin(mask).count("1") >= 8, name


# ---- R4, R5 -------------------------------------------------------------------------------------
def test_ba_and_savelink_are_refused_whatever_the_target():
    for t in (0x4000, 0x4001, 0x0, 0x3ffff):
        assert why_of(asm(f"ba #0x{t:x}\nnop.end")) == Y.DENY
    assert why_of(asm("br.savelink #1\nnop.end")) == Y.DENY


def test_the_last_word_ends_the_task():
    assert why_of(asm("nop")) == Y.LAST
    assert why_of(asm("nop\np0 br -#0x1")) == Y.LAST
    assert why_of(asm("nop\nbr -#0x1")) is None
    assert why_of(asm("nop.end")) is None
    assert why_of(asm("nop\n".replace("nop", "mov r1, #1") + "nop.end")) is None
