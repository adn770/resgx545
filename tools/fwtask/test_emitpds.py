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


V1_IMAGE = [0, 0, 0, 0, 0, 0, 0x200, 0, 0x07040606, 0x07042CA6, 0x07000305, 0xAF000000]


def dis(tmp_path, words):
    f = tmp_path / "image.bin"
    f.write_bytes(b"".join(w.to_bytes(4, "little") for w in words))
    r = subprocess.run([str(pds_dis()), str(f), "8"], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return [ln.split("\t", 1)[1] for ln in r.stdout.splitlines()]


def test_the_v1_image_is_unchanged_by_the_crumb_image():
    assert gen_verify.pds_image() == V1_IMAGE
    assert gen_verify.pds_image("v1") == V1_IMAGE


def test_the_crumb_image_adds_three_tim_breadcrumbs_and_nothing_else(tmp_path):
    """N3b step B: T1 (tim <- dword 3, 0), the two douta, T2 (tim <- dword 6, 0x200), the doutu,
    T3 (tim <- dword 7, 0x005a3305), halt. No doutd, no load or store, no branch."""
    img = gen_verify.pds_image("crumb")
    assert len(img) == 15
    assert dis(tmp_path, img) == ["data"] * 8 + [
        "movs tim, ds1[1], ds1[1], ds1[1], ds1[1]",
        "movs douta, ds0[2], ds1[1], ds0[2], ds0[2]",
        "movs douta, ds0[3], ds1[2], ds0[3], ds0[3]",
        "movs tim, ds1[2], ds1[2], ds1[2], ds1[2]",
        "movs doutu, ds0[0], ds0[1], ds1[0], ds0[0]",
        "movs tim, ds1[3], ds1[3], ds1[3], ds1[3]",
        "halt"]


def test_the_crumb_markers_are_stopped_values_and_the_rows_are_v1_s():
    img = gen_verify.pds_image("crumb")
    # ds1[1], ds1[2], ds1[3] are dwords 3, 6 and 7 (the banks interleave by pairs of dwords)
    assert [img[3], img[6], img[7]] == [0, 0x200, 0x005A3305]
    for d in (3, 6, 7):
        assert not img[d] & 1 << 24, d          # bit 24 clear: tim holds the value, no count
    assert img[:7] == V1_IMAGE[:7]              # U0-U2, the douta controls, V0, V2 as v1
    assert img[8 + 1:8 + 3] == V1_IMAGE[8:10] and img[8 + 4] == V1_IMAGE[10]
    assert img[-1] == V1_IMAGE[-1]


def test_the_kernel_header_carries_both_images():
    h = gen_verify.render_pds()
    assert "#define SGX_OWN_PDS_WORDS\t12" in h and "#define SGX_OWN_PDS_CRUMB_WORDS\t15" in h
    assert "static const u32 sgx_own_pds_image[SGX_OWN_PDS_WORDS]" in h
    assert "static const u32 sgx_own_pds_crumb[SGX_OWN_PDS_CRUMB_WORDS]" in h
    assert "asm/fwtask/pds/crumb.s" in h
    crumb = h[h.index("sgx_own_pds_crumb["):]
    for w in gen_verify.pds_image("crumb"):
        assert f"0x{w:08x}" in crumb
    assert "0x005a3305" in crumb


# ---- halt and crumb3 (round 38, N3c rows R5 and R4) ---------------------------------------------
CRUMB_IMAGE = [0, 0, 0, 0, 0, 0, 0x200, 0x005A3305, 0x07001FE7, 0x07040606, 0x07042CA6, 0x07003547,
               0x07000305, 0x07003FE7, 0xAF000000]


def dis_n(tmp_path, words, ndata):
    f = tmp_path / "image.bin"
    f.write_bytes(b"".join(w.to_bytes(4, "little") for w in words))
    r = subprocess.run([str(pds_dis()), str(f), str(ndata)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return [ln.split("\t", 1)[1] for ln in r.stdout.splitlines()]


def test_v1_and_crumb_are_byte_for_byte_as_at_round_37():
    assert gen_verify.pds_image("v1") == V1_IMAGE
    assert gen_verify.pds_image("crumb") == CRUMB_IMAGE


def test_the_halt_image_is_v1_s_data_rows_then_halt_alone(tmp_path):
    """N3c R5 (the program floor): v1's 8 data dwords (the kernel fills U0, V0, V2 as for v1),
    then `halt` and nothing else: no output, no doutu."""
    img = gen_verify.pds_image("halt")
    assert img == V1_IMAGE[:8] + [0xAF000000]
    assert dis_n(tmp_path, img, 8) == ["data"] * 8 + ["halt"]


def test_the_crumb3_image_is_crumb_with_a_zero_third_row(tmp_path):
    """N3c R4 (the firmware's #14 mirror): crumb's 8 data dwords plus four zeros (3 rows, as #14),
    then crumb's 7 instructions with every operand unchanged (the third row is ds0[4], ds0[5],
    ds1[4], ds1[5]; nothing names it)."""
    img = gen_verify.pds_image("crumb3")
    assert img[:8] == CRUMB_IMAGE[:8] and img[8:12] == [0, 0, 0, 0] and img[12:] == CRUMB_IMAGE[8:]
    crumb = dis_n(tmp_path, CRUMB_IMAGE, 8)
    assert dis_n(tmp_path, img, 12) == ["data"] * 12 + crumb[8:]


def test_each_image_has_its_own_rows_and_control_word():
    assert gen_verify.PDS_IMAGE_ROWS == {"v1": 2, "crumb": 2, "halt": 2, "crumb3": 3}
    for k, rows in gen_verify.PDS_IMAGE_ROWS.items():
        assert sum(1 for _, t in gen_verify.pds_listing(k) if t == "data") == 4 * rows, k
    assert [gen_verify.pds_ctl(k) for k in ("v1", "crumb", "halt")] == [0x01000100] * 3
    assert gen_verify.pds_ctl("crumb3") == (3 << 23) | 0x100 == 0x01800100


def test_the_kernel_header_carries_every_image_with_its_rows_and_control():
    h = gen_verify.render_pds()
    assert "#define SGX_OWN_PDS_ROWS\t2" in h and "#define SGX_OWN_PDS_CTL\t0x01000100" in h
    for k, n, rows, ctl in (("crumb", 15, 2, 0x01000100), ("halt", 9, 2, 0x01000100),
                            ("crumb3", 19, 3, 0x01800100)):
        u = k.upper()
        assert f"#define SGX_OWN_PDS_{u}_WORDS\t{n}" in h, k
        assert f"#define SGX_OWN_PDS_{u}_ROWS\t{rows}" in h, k
        assert f"#define SGX_OWN_PDS_{u}_CTL\t0x{ctl:08x}" in h, k
        assert f"static const u32 sgx_own_pds_{k}[SGX_OWN_PDS_{u}_WORDS]" in h, k
        assert f"asm/fwtask/pds/{k}.s" in h, k
        body = h[h.index(f"sgx_own_pds_{k}["):]
        body = body[:body.index("};")]
        assert [int(ln.split(",")[0], 16) for ln in body.splitlines()[1:]] == gen_verify.pds_image(k)


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


# ---- emitsn: emitsb's entry 0 without the emit (round 38, N3c row R1) ---------------------------
def emitsn_lines():
    import gen_blobs
    return [ln.strip() for ln in gen_blobs.gen_emitsn().splitlines()
            if ln.strip() and not ln.startswith(";")]


def test_emitsn_has_no_emit_no_pds_patch_and_one_entry():
    blob = fwtask.parse_blob(fwtask.blob_of("emitsn"))
    kinds = [fwtask.classify(w)[0] for w in blob.words]
    assert "EMITPDS" not in kinds
    assert not [p for p in blob.patches if p.kind.startswith("pds")]
    assert len(blob.entries) == 1
    assert fwtask.refusal(fwtask.blob_of("emitsn"), REGS) is None
    assert fwtask.lint((fwtask.ASM / "emitsn.s").read_text()) == []
    src = [ln for ln in emitsn_lines() if not ln.startswith("@")]
    assert not [ln for ln in src if ln.startswith("emitpds") or "@patch pds" in ln]
    assert [ln for ln in emitsn_lines() if ln.startswith("@entry")] == ["@entry 0"]


def test_emitsn_stores_m1_run_id_cmd_0_then_x0_fenced_at_slot_1_dword_2():
    """c1: M1 and the run id in slot 1 (res+272), cmd = 0, a fence, then X0 0x5a5a3303 to
    res+280 (page dword 70) through r9 = res+272, fenced: emitsb's order with the emit gone."""
    raw = emitsn_lines()
    c1 = raw[raw.index("c1:") + 1:]
    assert c1[0].startswith("mov r9, #0xdeadbeef") and c1[0].endswith("@patch res+272")
    i = c1.index("stad [r1,+#1], r4                  ; cmd = 0: one emit per command")
    assert c1[i - 1] == "mov r4, #0x00000000"
    assert c1[1:i - 1] == ["mov r7, #0x5a5a3301", "ldad.bypassl1 r5, [r1,+#3], drc0   ; the run id",
                           "wdf drc0", "stad [r9,+#0], r7", "stad [r9,+#1], r5"]
    assert c1[i + 1:i + 7] == ["idf drc0, bif", "wdf drc0", "mov r7, #0x5a5a3303",
                               "stad [r9,+#2], r7", "idf drc0, bif", "wdf drc0"]
    assert 272 + 4 * 2 == 4 * 70


def test_emitsn_then_does_done_s_sequence_in_slot_4_and_the_tail_call():
    """After X0: M4 0x5a5a3302 and the run id in slot 4 (res+320, page dwords 80-81), the echo,
    a fence, state = 2, then the tail call into the closed task (no own_end: one entry)."""
    raw = emitsn_lines()
    x0 = raw.index("stad [r9,+#2], r7")
    rest = raw[x0 + 3:]
    assert rest[0].startswith("mov r9, #0xdeadbeef") and rest[0].endswith("@patch res+320")
    assert rest[1:] == ["mov r7, #0x5a5a3302", "ldad.bypassl1 r5, [r1,+#3], drc0   ; the run id",
                        "wdf drc0", "stad [r9,+#0], r7", "stad [r9,+#1], r5", "stad [r1,+#5], r5",
                        "mov r3, #0x00000002", "idf drc0, bif", "wdf drc0",
                        "stad [r1,+#2], r3                ; state = done", "br @tail"]
    assert "own_end" not in raw and 320 == 4 * 80


def test_emitsn_is_emitsb_entry_0_without_the_emit():
    """Every line of emitsn is one of emitsb's (entry 1 moved into entry 0's tail, its pa and sa
    reads and S1 gone); emitsb's emit and its three pds limms are the lines it lacks."""
    import collections
    import gen_blobs
    b = collections.Counter(ln.strip() for ln in gen_blobs.gen_emitsb().splitlines()
                            if ln.strip() and not ln.startswith(";"))
    n = collections.Counter(emitsn_lines())
    assert n - b == collections.Counter()
    gone = {ln for ln in (b - n).elements()}
    assert {"emitpds.tasks.taske #0, r2, r3, r4, #0x0", "mov r2, #0xdeadbeef                 ; @patch pds0",
            "mov r3, #0xdeadbeef                 ; @patch pds1",
            "mov r4, #0xdeadbeef                 ; @patch pds2"} <= gone


def test_emitsn_is_in_the_map_and_the_kernel_s_accepted_list():
    """The map names it (the kit's owntask stage checks the staged blob against it), and the
    fork's KUnit list (sgxfive_owntask_blobs.h, round 38's kernel series) carries it."""
    import json
    m = json.loads((fwtask.ASM / "fwtask.map").read_text())
    assert m["emitsn"]["source"] == "emitsn.s"
    assert "emitsn" in gen_verify.OK_BLOBS


# ---- emitsk: emitsb whose emit waits for a host kick pass (round 39, N3d row K) -----------------
KICK_GATE = ["mov r5, pa1", "mov r8, #0x00000100",
             "and.testtanz.chan0 !c0, p0, r5, r8  ; p0 = pa1 bit 8 (a host kick pass, E746)",
             "p0 br @kick", "br @tail", "kick:"]


def emitsk_lines():
    import gen_blobs
    return [ln.strip() for ln in gen_blobs.gen_emitsk().splitlines()
            if ln.strip() and not ln.startswith(";")]


def test_the_emitsk_source_has_one_emit_its_patches_and_two_entries():
    blob = fwtask.parse_blob(fwtask.blob_of("emitsk"))
    kinds = [fwtask.classify(w)[0] for w in blob.words]
    assert kinds.count("EMITPDS") == 1
    assert sorted(p.kind for p in blob.patches if p.kind.startswith("pds")) == ["pds0", "pds1", "pds2"]
    assert len(blob.entries) == 2
    assert fwtask.refusal(fwtask.blob_of("emitsk"), REGS) is None
    assert fwtask.lint((fwtask.ASM / "emitsk.s").read_text()) == []
    (w,) = asm([OWN_EMIT])
    assert [x for x in blob.words if fwtask.classify(x)[0] == "EMITPDS"] == [w]


def test_emitsk_takes_the_emit_path_only_on_cmd_1_with_pa1_bit_8():
    """N3d §3.1: c1 (cmd = 1) first reads pa1 and tests bit 8 (the CCB reader's bit, E746: a
    GETMISCINFO kick has pa1 bits 23:0 = 0x100, a tick 0); without it the tail call follows with
    cmd untouched (no store before it); with it, emitsb's c1 body, unchanged."""
    raw = emitsk_lines()
    c1 = raw[raw.index("c1:") + 1:]
    assert c1[:len(KICK_GATE)] == KICK_GATE
    before = c1[:c1.index("kick:")]
    assert not [ln for ln in before if ln.startswith(("stad", "str", "emitpds", "ldad"))]
    import gen_blobs
    b = [ln.strip() for ln in gen_blobs.gen_emitsb().splitlines()
         if ln.strip() and not ln.startswith(";")]
    body_b = b[b.index("c1:") + 1:b.index("@entry 1")]
    body_k = c1[len(KICK_GATE):c1.index("@entry 1")]
    assert body_k == body_b
    assert body_k.index("stad [r1,+#1], r4                  ; cmd = 0: one emit per command") \
        < next(i for i, ln in enumerate(body_k) if ln.startswith("emitpds"))


def test_emitsk_is_emitsb_plus_the_kick_gate_and_nothing_else():
    import collections
    import gen_blobs
    b = collections.Counter(ln.strip() for ln in gen_blobs.gen_emitsb().splitlines()
                            if ln.strip() and not ln.startswith(";"))
    k = collections.Counter(emitsk_lines())
    assert b - k == collections.Counter()
    assert sorted((k - b).elements()) == sorted(KICK_GATE)


def test_emitsk_keeps_emitsb_s_offsets():
    """M1/X0 at res+272 (dwords 68-70), S1 at res+336 (84), M4 at res+320 (80-81)."""
    import gen_blobs
    import re
    pk = re.findall(r"@patch (res\+\d+)", gen_blobs.gen_emitsk())
    pb = re.findall(r"@patch (res\+\d+)", gen_blobs.gen_emitsb())
    assert pk == pb


def test_the_kick_gate_test_assembles_and_round_trips():
    """The bit test is the alu-test form (`and.testtanz` of two registers: the immediate #0x100
    has no encoding in this form, so the mask is a mov limm into r8, as events_m and oomring2)."""
    (w,) = asm(["and.testtanz.chan0 !c0, p0, r5, r8"])
    assert fwtask.classify(w) == ("PLAIN", "alu-test")
    with pytest.raises(fwtask.VerifyError):
        asm(["and.testtanz.chan0 !c0, p0, r5, #0x100"])
    blob = fwtask.parse_blob(fwtask.blob_of("emitsk"))
    assert w in blob.words


def test_emitsk_is_in_the_map():
    """The map names it (the kit's owntask stage checks the staged blob against it). The fork's
    KUnit list gains it with the next kernel series (round 39, Z); until then the kernel's
    verifier at the pin runs it (test_host_verifier.py, every source)."""
    import json
    m = json.loads((fwtask.ASM / "fwtask.map").read_text())
    assert m["emitsk"]["source"] == "emitsk.s"
