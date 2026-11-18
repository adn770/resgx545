# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The one emitpds form a task of ours may hold (round 33, user decision N3 b): the exact word
`emitpds.tasks.taske #0, r2, r3, r4, #0x0`, its three sources the kernel's patched values (the
image's control word, address and argument) on every path, once per task run, and never from the
task the image starts (entry 1). Every other emitpds stays refused. The image is ours
(asm/fwtask/pds/emit.s), a constant of the kernel (sgx_own_pds.h)."""
import pathlib
import subprocess
import sys

import pytest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fwtask  # noqa: E402
import gen_verify  # noqa: E402

REGS = fwtask.load_regs()
Y = fwtask.Why
P = fwtask.Patch
OWN_EMIT = "emitpds.tasks.taske #0, r2, r3, r4, #0x0"
SETUP = ["mov r2, #0xdeadbeef", "mov r3, #0xdeadbeef", "mov r4, #0xdeadbeef"]
PDS = [P(0, "pds0"), P(1, "pds1"), P(2, "pds2")]


def asm(lines):
    return fwtask.assemble_text("\n".join(lines))


def why_of(lines, patches=PDS, entries=(0, 5)):
    err = fwtask.verify_why(asm(lines), list(patches), REGS, entries)
    return err[0][1] if err else None


# a task that emits (entry 0) and the started task (entry 5: nop.end)
GOOD = SETUP + [OWN_EMIT, "nop.end", "nop.end"]


def test_the_owned_form_is_one_exact_word_of_the_listing():
    (w,) = asm([OWN_EMIT])
    assert w == 0xFB20B00000008184
    assert fwtask.classify(w) == ("EMITPDS", "emitpds-own")
    row = next(r for r in fwtask.FORMS if r[0] == "emitpds-own")
    assert row[2] == fwtask.ALL and row[3] == w
    spec = pathlib.Path(gen_verify.spec_path()).read_text()
    assert gen_verify.in_spec(spec, row[2], row[3])


def test_the_owned_form_with_its_operands_patched_is_accepted():
    assert why_of(GOOD) is None


@pytest.mark.parametrize("word", [
    "emitpds #0, r2, r3, r4, #0x0", "emitpds.tasks #0, r2, r3, r4, #0x0",
    "emitpds.taske #0, r2, r3, r4, #0x0", "emitpds.tasks.taske.freep #0, r2, r3, r4, #0x0",
    "emitpds.nosched.tasks.taske #0, r2, r3, r4, #0x0", "emitpds.end.tasks.taske #0, r2, r3, r4, #0x0",
    "emitpds.tasks.taske #1, r2, r3, r4, #0x0", "emitpds.tasks.taske #0, r2, r3, r4, #0x1",
    "emitpds.tasks.taske #0, r2, r3, r4, #0x2000", "emitpds.tasks.taske #0, r5, r3, r4, #0x0",
    "emitpds.tasks.taske #0, r2, r5, r4, #0x0", "emitpds.tasks.taske #0, r2, r3, r5, #0x0",
    "emitpds.tasks.taske #0, sa2, r3, r4, #0x0", "emitpds.tasks.taske #0, r2, sa3, r4, #0x0",
])
def test_every_other_emitpds_is_an_unknown_form(word):
    assert why_of(SETUP + [word, "nop.end", "nop.end"]) == Y.UNKNOWN


def test_no_single_bit_change_of_the_owned_word_is_the_owned_form():
    (w,) = asm([OWN_EMIT])
    for b in range(64):
        assert fwtask.classify(w ^ 1 << b)[1] != "emitpds-own", b


def test_the_operands_must_be_the_kernel_s_values():
    # unpatched, swapped, a results-page patch, a stale value, one path only
    assert why_of(GOOD, []) == Y.EMIT_ARGS
    assert why_of(GOOD, [P(0, "pds1"), P(1, "pds0"), P(2, "pds2")]) == Y.EMIT_ARGS
    assert why_of(GOOD, [P(0, "pds0"), P(1, "res"), P(2, "pds2")]) == Y.EMIT_ARGS
    assert why_of(GOOD, [P(0, "pds0"), P(1, "pds1")]) == Y.EMIT_ARGS
    assert why_of(SETUP + ["mov r3, r5", OWN_EMIT, "nop.end", "nop.end"],
                  entries=(0, 6)) == Y.EMIT_ARGS
    assert why_of(SETUP + ["mov r4, r5", OWN_EMIT, "nop.end", "nop.end"],
                  entries=(0, 6)) == Y.EMIT_ARGS
    both = ["p0 br #3", "mov r2, #0xdeadbeef", "br #2", "mov r2, #0xdeadbeef"] + SETUP[1:] + [
        OWN_EMIT, "nop.end", "nop.end"]
    assert why_of(both, [P(1, "pds0"), P(3, "pds0"), P(4, "pds1"), P(5, "pds2")], (0, 8)) is None
    one_path = ["mov r2, #0xdeadbeef", "p0 br #2"] + SETUP[1:] + [OWN_EMIT, "nop.end", "nop.end"]
    assert why_of(one_path, [P(0, "pds0"), P(2, "pds1"), P(3, "pds2")], (0, 6)) == Y.EMIT_ARGS


def test_a_pds_value_is_not_a_store_base():
    lines = SETUP + ["stad [r3,+#0], r4", OWN_EMIT, "nop.end", "nop.end"]
    assert why_of(lines, entries=(0, 6)) == Y.BASE


def test_the_pds_patch_kind_has_three_slots_and_no_addend():
    assert why_of(GOOD, [P(0, "pds0"), P(1, "pds1"), P(2, "pds3")]) == Y.PATCH_SLOT
    assert why_of(GOOD, [P(0, "pds0", 4), P(1, "pds1"), P(2, "pds2")]) == Y.PATCH_ADD
    assert why_of(GOOD, [P(0, "pds0"), P(0, "pds1"), P(2, "pds2")]) == Y.PATCH_TWICE
    assert why_of(["nop", "mov r2, #0xdeadbeef", OWN_EMIT, "nop.end"],
                  [P(0, "pds0")], (0, 3)) == Y.PATCH_LIMM


def test_the_pds_patch_round_trips_through_the_blob():
    b = fwtask.pack_blob(asm(GOOD), PDS, [0, 5])
    assert fwtask.parse_blob(b).patches == PDS
    assert b[16 + 8 * 6:16 + 8 * 6 + 4] == bytes([0, 0, 3, 0])       # index 0, kind 3, slot 0


def test_once_per_run():
    # two words, a loop through it, reached from the started task's entry
    assert why_of(SETUP + [OWN_EMIT, OWN_EMIT, "nop.end", "nop.end"], entries=(0, 6)) == Y.EMIT_ONCE
    assert why_of(SETUP + [OWN_EMIT, "p0 br -#0x1", "nop.end", "nop.end"],
                  entries=(0, 6)) == Y.EMIT_ONCE
    assert why_of(SETUP + [OWN_EMIT, "nop.end", "br -#0x5"], entries=(0, 5)) == Y.EMIT_ONCE
    # a loop before the setup that does not pass the emit is fine
    assert why_of(["p0 br #0"] + SETUP + [OWN_EMIT, "nop.end", "nop.end"],
                  [P(1, "pds0"), P(2, "pds1"), P(3, "pds2")], (0, 6)) is None


def test_the_started_task_needs_its_entry():
    assert why_of(GOOD, entries=(0,)) == Y.EMIT_ENTRY
    assert why_of(GOOD, entries=()) == Y.EMIT_ENTRY
    # without the emit one entry is as before
    assert why_of(["nop.end"], [], (0,)) is None


def test_the_crafted_emit_blobs_are_in_the_kernel_s_list():
    names = {n for n, _, _, _ in gen_verify.crafted_blobs()}
    for n in ("emitpds", "emitpds_flags", "emitpds_sideband", "emitpds_incp", "emitpds_regs",
              "emitpds_bank", "emitpds_twice", "emitpds_loop", "emitpds_from_entry1",
              "emitpds_one_entry", "emitpds_unpatched", "emitpds_swapped", "emitpds_overwritten",
              "emitpds_one_path", "emitpds_res_patch", "pds_slot3", "pds_addend", "pds_base"):
        assert n in names, n


# ---- the image ----------------------------------------------------------------------------------
def pds_dis():
    dis = HERE.parent / "usse-dis" / "pds-dis"
    r = subprocess.run(["make", "-s", "-C", str(dis.parent), "pds-dis"], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return dis


def test_the_image_is_two_rows_of_data_and_four_instructions():
    img = gen_verify.pds_image()
    assert len(img) == 12 and gen_verify.PDS_ROWS == 2
    assert img[:8] == [0, 0, 0, 0, 0, 0, 0x200, 0]     # U0, U1, U2, ctl 0, V0, V2, ctl 2, unused
    assert gen_verify.PDS_CTL == (2 << 23) | 0x100 == 0x01000100


def test_the_image_does_douta_douta_doutu_halt_and_nothing_else(tmp_path):
    """The words, disassembled by our pds-dis: two douta to attributes 0 and 2 (the controls of
    dwords 3 and 6) of the values in dwords 4 and 5, a doutu of U0-U2, halt. No doutd, no load or
    store, no branch, no other port."""
    f = tmp_path / "image.bin"
    f.write_bytes(b"".join(w.to_bytes(4, "little") for w in gen_verify.pds_image()))
    r = subprocess.run([str(pds_dis()), str(f), "8"], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    text = [ln.split("\t", 1)[1] for ln in r.stdout.splitlines()]
    assert text == ["data"] * 8 + [
        "movs douta, ds0[2], ds1[1], ds0[2], ds0[2]",
        "movs douta, ds0[3], ds1[2], ds0[3], ds0[3]",
        "movs doutu, ds0[0], ds0[1], ds1[0], ds0[0]",
        "halt"]


def test_the_kernel_header_carries_the_image_and_its_dword_roles():
    h = gen_verify.render_pds()
    assert h == gen_verify.render_pds()
    assert "#define SGX_OWN_PDS_ROWS\t2" in h and "#define SGX_OWN_PDS_CTL\t0x01000100" in h
    for name, i in (("U0", 0), ("U1", 1), ("U2", 2), ("V0", 4), ("V2", 5)):
        assert f"#define SGX_OWN_PDS_{name}\t{i}" in h
    for w in gen_verify.pds_image():
        assert f"0x{w:08x}" in h


def test_the_committed_kernel_pds_header_is_current():
    p = gen_verify.SGXFIVE / "sgx_own_pds.h"
    if not p.is_file():
        pytest.skip(f"SKIPPED, NOT PASSED: no fork commit {gen_verify.forkpin.pin()} with sgx_own_pds.h "
                    f"in {gen_verify.LINUX} (RESGX545_LINUX)")
    assert p.read_text() == gen_verify.render_pds()


def test_the_emitsa_source_has_one_emit_its_patches_and_two_entries():
    blob = fwtask.parse_blob(fwtask.blob_of("emitsa"))
    kinds = [fwtask.classify(w)[0] for w in blob.words]
    assert kinds.count("EMITPDS") == 1
    assert sorted(p.kind for p in blob.patches if p.kind.startswith("pds")) == ["pds0", "pds1", "pds2"]
    assert len(blob.entries) == 2
    assert fwtask.refusal(fwtask.blob_of("emitsa"), REGS) is None


# ---- emitsb: emitsa with two breadcrumbs (round 37, N3b) ----------------------------------------
def emitsb_lines():
    import gen_blobs
    return gen_blobs.gen_emitsb().splitlines()


def test_the_emitsb_source_has_one_emit_its_patches_and_two_entries():
    blob = fwtask.parse_blob(fwtask.blob_of("emitsb"))
    kinds = [fwtask.classify(w)[0] for w in blob.words]
    assert kinds.count("EMITPDS") == 1
    assert sorted(p.kind for p in blob.patches if p.kind.startswith("pds")) == ["pds0", "pds1", "pds2"]
    assert len(blob.entries) == 2
    assert fwtask.refusal(fwtask.blob_of("emitsb"), REGS) is None
    assert fwtask.lint((fwtask.ASM / "emitsb.s").read_text()) == []


def test_emitsb_x0_is_the_first_store_after_the_emit_at_slot_1_dword_2():
    """X0: right after the emit, 0x5a5a3303 to res+280 (slot 1 dword 2, page dword 70) through
    r9 = res+272, fenced, then the tail call."""
    raw = emitsb_lines()
    i = next(k for k, ln in enumerate(raw) if ln.strip().startswith("emitpds"))
    after = [ln.strip() for ln in raw[i + 1:]]
    assert after[:5] == ["mov r7, #0x5a5a3303", "stad [r9,+#2], r7", "idf drc0, bif", "wdf drc0",
                         "br @tail"]
    base = [ln for ln in raw[:i] if ln.strip().startswith("mov r9,")]
    assert base[-1].endswith("@patch res+272")
    assert 272 + 4 * 2 == 4 * 70


def test_emitsb_s1_is_entry_1_s_first_store_before_any_attribute_read():
    """S1: entry 1 starts with 0x5a5a3304 to res+336 (slot 5 dword 0, page dword 84), fenced,
    before any pa or sa read; the rest of entry 1 is emitsa's."""
    raw = emitsb_lines()
    e1 = [ln.strip() for ln in raw[next(k for k, ln in enumerate(raw) if ln == "@entry 1") + 1:]]
    e1 = [ln for ln in e1 if not ln.endswith(":")]
    assert e1[0].startswith("mov r9, #0xdeadbeef") and e1[0].endswith("@patch res+336")
    assert e1[1:5] == ["mov r7, #0x5a5a3304", "stad [r9,+#0], r7", "idf drc0, bif", "wdf drc0"]
    first_attr = next(k for k, ln in enumerate(e1) if " pa" in ln or " sa" in ln)
    first_store = next(k for k, ln in enumerate(e1) if ln.startswith("stad"))
    assert first_store < first_attr
    assert 336 == 4 * 84


def test_emitsb_is_emitsa_plus_the_two_breadcrumbs():
    import gen_blobs
    a = [ln for ln in gen_blobs.gen_emitsa().splitlines() if not ln.startswith(";")]
    b = [ln for ln in gen_blobs.gen_emitsb().splitlines() if not ln.startswith(";")]
    import collections
    extra = collections.Counter(b) - collections.Counter(a)
    assert collections.Counter(a) - collections.Counter(b) == collections.Counter()
    assert sorted(ln.strip() for ln in extra.elements()) == sorted([
        "mov r7, #0x5a5a3303", "stad [r9,+#2], r7", "idf drc0, bif", "wdf drc0",
        "mov r9, #0xdeadbeef                ; @patch res+336", "mov r7, #0x5a5a3304",
        "stad [r9,+#0], r7", "idf drc0, bif", "wdf drc0"])


def test_emitsb_is_in_the_map_and_the_kernel_s_accepted_list():
    import json
    m = json.loads((fwtask.ASM / "fwtask.map").read_text())
    assert m["emitsb"]["source"] == "emitsb.s"
    assert "emitsb" in gen_verify.OK_BLOBS
