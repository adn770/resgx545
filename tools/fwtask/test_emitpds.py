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
    "emitpds.tasks.taske #1, r2, r3, r4, #0x0", "emitpds.tasks.taske #0, r2, r3, r4, #0x4",
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
    assert gen_verify.PDS_IMAGE_ROWS == {"v1": 2, "crumb": 2, "halt": 2, "crumb3": 3, "land": 3,
                                         "mark": 3, "landv": 3, "crumbz": 3, "landq": 3}
    for k, rows in gen_verify.PDS_IMAGE_ROWS.items():
        assert sum(1 for _, t in gen_verify.pds_listing(k) if t == "data") == 4 * rows, k
    assert [gen_verify.pds_ctl(k) for k in ("v1", "crumb", "halt")] == [0x01000100] * 3
    assert gen_verify.pds_ctl("crumb3") == (3 << 23) | 0x100 == 0x01800100


def test_the_kernel_header_carries_every_image_with_its_rows_and_control():
    h = gen_verify.render_pds()
    assert "#define SGX_OWN_PDS_ROWS\t2" in h and "#define SGX_OWN_PDS_CTL\t0x01000100" in h
    for k, n, rows, ctl in (("crumb", 15, 2, 0x01000100), ("halt", 9, 2, 0x01000100),
                            ("crumb3", 19, 3, 0x01800100), ("land", 16, 3, 0x01800100),
                            ("mark", 21, 3, 0x01800100), ("landv", 18, 3, 0x01800100),
                            ("crumbz", 17, 3, 0x01800100), ("landq", 18, 3, 0x01800100)):
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
    """The map names it (the kit's owntask stage checks the staged blob against it). The kernel's
    verifier at the pin runs it (test_host_verifier.py, every source), and the fork's KUnit list
    carries it since round 39's kernel series (below)."""
    import json
    m = json.loads((fwtask.ASM / "fwtask.map").read_text())
    assert m["emitsk"]["source"] == "emitsk.s"


# ---- the fw14 form: ours with #14's sideband (round 39, N3d row Z) -------------------------------
FW14_EMIT = "emitpds.tasks.taske #0, r2, r3, r4, #0x843"
FW14_WORD = 0xFB20B10800C08184


def sideband(w):
    """The 14-bit field of usse-dis form #149 (N3d O1): value bits 5:0 = word bits 27:22, 11:6 =
    word bits 40:35, 13:12 = word bits 55:54."""
    return (w >> 22 & 0x3F) | (w >> 35 & 0x3F) << 6 | (w >> 54 & 3) << 12


def test_the_fw14_form_is_ours_with_14_s_sideband_and_nothing_else():
    """O1 (data-private firmware/fwsim/n3d-o1/facts.txt): against our word only the sideband
    differs at #14's emit, and #14's is 0x0843 (#12's too; #11's 0x0c43)."""
    (w,) = asm([FW14_EMIT])
    assert w == FW14_WORD
    assert sideband(w) == 0x0843 and sideband(0xFB20B00000008184) == 0
    mask = (0x3F << 22) | (0x3F << 35) | (3 << 54)
    assert w & ~mask == 0xFB20B00000008184 & ~mask
    assert fwtask.classify(w) == ("EMITPDS", "emitpds-fw14")
    row = next(r for r in fwtask.FORMS if r[0] == "emitpds-fw14")
    assert row[1] == "EMITPDS" and row[2] == fwtask.ALL and row[3] == w
    spec = pathlib.Path(gen_verify.spec_path()).read_text()
    assert gen_verify.in_spec(spec, row[2], row[3])


FW14_GOOD = SETUP + [FW14_EMIT, "nop.end", "nop.end"]


def test_the_fw14_form_keeps_every_rule_of_the_owned_form():
    assert why_of(FW14_GOOD) is None
    assert why_of(FW14_GOOD, []) == Y.EMIT_ARGS
    assert why_of(FW14_GOOD, [P(0, "pds1"), P(1, "pds0"), P(2, "pds2")]) == Y.EMIT_ARGS
    assert why_of(SETUP + ["mov r4, r5", FW14_EMIT, "nop.end", "nop.end"],
                  entries=(0, 6)) == Y.EMIT_ARGS
    assert why_of(FW14_GOOD, entries=(0,)) == Y.EMIT_ENTRY
    # one emit a task, whichever the word: the two forms together are two
    assert why_of(SETUP + [OWN_EMIT, FW14_EMIT, "nop.end", "nop.end"], entries=(0, 6)) == Y.EMIT_ONCE
    assert why_of(SETUP + [FW14_EMIT, "p0 br -#0x1", "nop.end", "nop.end"],
                  entries=(0, 6)) == Y.EMIT_ONCE


@pytest.mark.parametrize("word", [
    "emitpds.tasks.taske #0, r2, r3, r4, #0xc03", "emitpds.tasks.taske #0, r2, r3, r4, #0x443",
    "emitpds.tasks.taske #0, r2, r3, r4, #0x844", "emitpds.tasks.taske #0, r2, r3, r4, #0x1843",
    "emitpds.tasks.taske #0, r2, r3, r4, #0x847", "emitpds #0, r2, r3, r4, #0x843",
    "emitpds.tasks.taske.freep #0, r2, r3, r4, #0x843", "emitpds.tasks.taske #1, r2, r3, r4, #0x843",
    "emitpds.tasks.taske #0, r5, r3, r4, #0x843", "emitpds.tasks.taske #0, sa2, r3, r4, #0x843",
])
def test_every_other_sideband_or_field_with_it_is_still_unknown(word):
    assert why_of(SETUP + [word, "nop.end", "nop.end"]) == Y.UNKNOWN


SB_MASK = (0x3F << 22) | (0x3F << 35) | (3 << 54)        # the sideband's word bits (#149)


def test_no_single_bit_change_outside_the_sideband_of_a_listed_word_is_an_emit_form():
    """Round 40 (N3e): the list (below) differs in the sideband only; a change of any other bit of
    any listed word is no emitpds form, and a sideband change is a listed word or none."""
    listed = {w for _, _, w in fwtask.EMIT_FORMS}
    for w in listed:
        for b in range(64):
            k = fwtask.classify(w ^ 1 << b)
            if SB_MASK >> b & 1:
                assert (k[0] == "EMITPDS") == ((w ^ 1 << b) in listed), (hex(w), b)
            else:
                assert k[0] != "EMITPDS", (hex(w), b)


def test_the_crafted_blobs_refuse_sidebands_off_the_list():
    """Round 40 (N3e): #11's 0x0c43 and our 0x001 are listed now; the crafted refusals take
    sidebands the list leaves out: bit 2 (0x004), bit 10 with 0 and 1 and 11 but not 6 (0x0c03),
    bit 12 (0x1843, no firmware value sets 13:12)."""
    rows = {n: (want, why) for n, _, want, why in gen_verify.crafted_blobs()}
    for n in ("emitpds_sideband", "emitpds_sideband_c03", "emitpds_sideband_1843"):
        assert rows[n] == ("EPERM", Y.UNKNOWN), n
    assert "emitpds_sideband_11" not in rows
    words = {n: d for n, d, _, _ in gen_verify.crafted_blobs()}
    sb = {n: [sideband(w) for w in fwtask.parse_blob(words[n]).words
              if w & ~SB_MASK == 0xFB20B00000008184 & ~SB_MASK]
          for n in ("emitpds_sideband", "emitpds_sideband_c03", "emitpds_sideband_1843")}
    assert sb == {"emitpds_sideband": [0x004], "emitpds_sideband_c03": [0xC03],
                  "emitpds_sideband_1843": [0x1843]}


def test_emitsk14_is_emitsk_with_the_fw14_word_and_nothing_else():
    import gen_blobs
    k = [ln for ln in gen_blobs.gen_emitsk().splitlines() if not ln.startswith(";")]
    f = [ln for ln in gen_blobs.gen_emitsk14().splitlines() if not ln.startswith(";")]
    assert len(k) == len(f)
    diff = [(a.strip(), b.strip()) for a, b in zip(k, f) if a != b]
    assert diff == [(OWN_EMIT, FW14_EMIT)]
    blob = fwtask.parse_blob(fwtask.blob_of("emitsk14"))
    assert [w for w in blob.words if fwtask.classify(w)[0] == "EMITPDS"] == [FW14_WORD]
    assert fwtask.refusal(fwtask.blob_of("emitsk14"), REGS) is None
    assert fwtask.lint((fwtask.ASM / "emitsk14.s").read_text()) == []
    kb = fwtask.parse_blob(fwtask.blob_of("emitsk"))
    assert blob.entries == kb.entries and blob.patches == kb.patches


def test_emitsk_and_emitsk14_are_in_the_kernel_s_accepted_list():
    """Round 39's kernel series (r39-kernel) carries both in the fork's KUnit list."""
    import json
    m = json.loads((fwtask.ASM / "fwtask.map").read_text())
    assert m["emitsk14"]["source"] == "emitsk14.s"
    assert "emitsk" in gen_verify.OK_BLOBS and "emitsk14" in gen_verify.OK_BLOBS


# ---- emitsb14: emitsb with #14's emit word (round 40, Q128 row S-PASS) --------------------------
def test_emitsb14_is_emitsb_with_the_fw14_word_and_nothing_else():
    """Row S-PASS splits the kick pass from Z: Z's word on emitsb's timer pass (no pa1 gate)."""
    import gen_blobs
    b = [ln for ln in gen_blobs.gen_emitsb().splitlines() if not ln.startswith(";")]
    f = [ln for ln in gen_blobs.gen_emitsb14().splitlines() if not ln.startswith(";")]
    assert len(b) == len(f)
    diff = [(x.strip(), y.strip()) for x, y in zip(b, f) if x != y]
    assert diff == [(OWN_EMIT, FW14_EMIT)]
    blob = fwtask.parse_blob(fwtask.blob_of("emitsb14"))
    assert [w for w in blob.words if fwtask.classify(w)[0] == "EMITPDS"] == [FW14_WORD]
    assert fwtask.refusal(fwtask.blob_of("emitsb14"), REGS) is None
    assert fwtask.lint((fwtask.ASM / "emitsb14.s").read_text()) == []
    bb = fwtask.parse_blob(fwtask.blob_of("emitsb"))
    assert blob.entries == bb.entries and blob.patches == bb.patches
    assert [w for w in blob.words if fwtask.classify(w)[0] != "EMITPDS"] == \
        [w for w in bb.words if fwtask.classify(w)[0] != "EMITPDS"]


def test_emitsb14_is_in_the_map_and_the_kernel_s_accepted_list():
    """Round 40's kernel series (r40-kernel, N3e) carries it in the fork's KUnit list."""
    import json
    m = json.loads((fwtask.ASM / "fwtask.map").read_text())
    assert m["emitsb14"]["source"] == "emitsb14.s"
    assert "emitsb14" in gen_verify.OK_BLOBS


# ---- emitsb14d: emitsb14 with the landing survey (round 40, N3e row D0) -------------------------
def _code(text):
    """The instruction lines of a source (comments and blank lines gone, labels kept)."""
    out = []
    for ln in text.splitlines():
        c = ln.split(";")[0].strip()
        if c:
            out.append(c)
    return out


def _survey():
    import gen_blobs
    return _code(gen_blobs.gen_emitsb14d())


PRE_AT, POST_SA_AT, POST_PA_AT = 128, 160, 192     # page dwords (N3e §3.1)


def _block(lines, start, end):
    i, j = lines.index(start), lines.index(end)
    return lines[i + 1:j]


def _reads_and_stores(block, base_reg, base_dword):
    """Pairs (source, page dword) in a block: each `mov rN, src` read, then `stad [base,+#j], rN`."""
    import re as _re
    cur, out = {}, []
    for ln in block:
        m = _re.fullmatch(r"mov (r\d+), ((?:pa|sa)\d+)", ln)
        if m:
            cur[m.group(1)] = m.group(2)
            continue
        m = _re.fullmatch(r"stad \[%s,\+#(\d+)\], (r\d+)" % base_reg, ln)
        if m:
            out.append((cur.pop(m.group(2)), base_dword + int(m.group(1))))
    return out


def test_emitsb14d_pre_reads_sa0_to_sa31_into_dwords_128_on():
    """Entry 0, out of line (after entry 1's end; its br takes the place of c1's `mov r4, #0`,
    which the block does last, so entry 1 keeps emitsb14's index and the kernel's U0 is ST's):
    r10 = res+512, sa0-sa31 to dwords 128-159, reached from c1 after the M1/run-id stores and
    before the cmd store and the fence that precede the emit."""
    s = _survey()
    pre = _block(s, "pre:", "br @back")
    assert pre[0] == "mov r10, #0xdeadbeef" and pre[-1] == "mov r4, #0x00000000"
    assert _reads_and_stores(pre, "r10", PRE_AT) == [(f"sa{k}", PRE_AT + k) for k in range(32)]
    c1 = s[s.index("c1:") + 1:s.index("back:")]
    assert c1[-3:] == ["stad [r9,+#0], r7", "stad [r9,+#1], r5", "br @pre"]
    after = s[s.index("back:") + 1:]
    assert after[:3] == ["stad [r1,+#1], r4", "idf drc0, bif", "wdf drc0"]
    assert s.index("pre:") > s.index("@entry 1") and s[-1] == "br @back"
    import gen_blobs
    assert "@patch res+512" in gen_blobs.gen_emitsb14d()


def test_emitsb14d_post_reads_sa_and_pa_after_s1_before_m4():
    """Entry 1: after S1 and the pa0-pa3/sa0-sa3 slots, before M4: sa0-sa31 to dwords 160-191
    and pa0-pa15 to dwords 192-207, through r9."""
    import gen_blobs
    src = gen_blobs.gen_emitsb14d()
    s = _survey()
    e1 = s[s.index("@entry 1"):s.index("pre:")]
    i = e1.index("mov r7, #0x5a5a3304")
    j = e1.index("mov r7, #0x5a5a3302")
    body = e1[i:j]
    sa = body.index("mov r9, #0xdeadbeef", body.index("mov r4, sa0") + 1)
    pa = body.index("mov r9, #0xdeadbeef", sa + 1)
    assert _reads_and_stores(body[sa:pa], "r9", POST_SA_AT) == \
        [(f"sa{k}", POST_SA_AT + k) for k in range(32)]
    assert _reads_and_stores(body[pa:], "r9", POST_PA_AT) == \
        [(f"pa{k}", POST_PA_AT + k) for k in range(16)]
    assert "@patch res+640" in src and "@patch res+768" in src


def test_emitsb14d_is_emitsb14_plus_the_survey_only():
    """Putting c1's `mov r4, #0` back in place of the branch out and removing the survey lines
    (the pre block, the two post blocks) leaves emitsb14's code; the word and entries 0 and 1
    (so U0) are kept."""
    import gen_blobs
    s = _survey()
    b = _code(gen_blobs.gen_emitsb14())
    e1 = s.index("@entry 1")
    i = s.index("mov r7, #0x5a5a3302", e1)
    first_post = [k for k in range(e1, i) if s[k] == "mov r9, #0xdeadbeef"][-3]
    kept = s[:s.index("br @pre")] + ["mov r4, #0x00000000"] + \
        s[s.index("back:") + 1:first_post] + \
        s[i - 1:s.index("pre:")]
    assert kept == b
    blob = fwtask.parse_blob(fwtask.blob_of("emitsb14d"))
    bb = fwtask.parse_blob(fwtask.blob_of("emitsb14"))
    assert blob.entries == bb.entries                  # entry 1's index: U0 as ST's
    assert [w for w in blob.words if fwtask.classify(w)[0] == "EMITPDS"] == [FW14_WORD]
    assert fwtask.refusal(fwtask.blob_of("emitsb14d"), REGS) is None
    assert fwtask.lint((fwtask.ASM / "emitsb14d.s").read_text()) == []


def test_emitsb14d_is_in_the_map_and_the_kernel_s_accepted_list():
    import json
    m = json.loads((fwtask.ASM / "fwtask.map").read_text())
    assert m["emitsb14d"]["source"] == "emitsb14d.s"
    assert "emitsb14d" in gen_verify.OK_BLOBS


# ---- the sideband list (round 40, N3e §3.2, the user's decision A (a)) --------------------------
# the design's table: form= name, sideband, word (computed there from our word with #149's field)
N3E_LIST = [("own", 0x000, 0xFB20B00000008184), ("sb001", 0x001, 0xFB20B00000408184),
            ("sb002", 0x002, 0xFB20B00000808184), ("sb003", 0x003, 0xFB20B00000C08184),
            ("sb040", 0x040, 0xFB20B00800008184), ("sb041", 0x041, 0xFB20B00800408184),
            ("sb042", 0x042, 0xFB20B00800808184), ("sb043", 0x043, 0xFB20B00800C08184),
            ("sb800", 0x800, 0xFB20B10000008184), ("sb801", 0x801, 0xFB20B10000408184),
            ("sb802", 0x802, 0xFB20B10000808184), ("sb803", 0x803, 0xFB20B10000C08184),
            ("sb840", 0x840, 0xFB20B10800008184), ("sb841", 0x841, 0xFB20B10800408184),
            ("sb842", 0x842, 0xFB20B10800808184), ("fw14", 0x843, 0xFB20B10800C08184),
            ("sbc43", 0xC43, 0xFB20B18800C08184), ("sb403", 0x403, 0xFB20B08000C08184)]
# round 42 (N3g §2 item 1, the user's decisions A (a) and F (a)): sb402 (bit 10 with bits 1:0 = 2,
# row Q) and sb400 (bit 10 alone: the word only, no row), after N3e's list so no index moves
N3G_LIST = [("sb402", 0x402, 0xFB20B08000808184), ("sb400", 0x400, 0xFB20B08000008184)]
EMIT_LIST = N3E_LIST + N3G_LIST
SB_FORMS = [n for n, _, _ in EMIT_LIST if n.startswith("sb")]


def test_the_emit_list_is_the_design_s_18_words_in_its_order():
    """The 16 subsets of 0x843's set bits {0, 1, 6, 11}, then #11's 0xc43 and 0x403; own and fw14
    keep their words (round 33's and round 39's, unchanged)."""
    assert fwtask.EMIT_FORMS[:18] == N3E_LIST
    subsets = {sum(b for j, b in enumerate((1, 2, 0x40, 0x800)) if k >> j & 1) for k in range(16)}
    assert {s for _, s, _ in N3E_LIST} == subsets | {0xC43, 0x403} and len(N3E_LIST) == 18
    for name, sb, w in N3E_LIST:
        assert fwtask.emit_word(sb) == w, name
        assert sideband(w) == sb, name
        assert w & ~SB_MASK == 0xFB20B00000008184 & ~SB_MASK, name
        (a,) = asm([f"emitpds.tasks.taske #0, r2, r3, r4, #0x{sb:x}"])
        assert a == w, name
    assert dict((n, w) for n, _, w in N3E_LIST)["fw14"] == FW14_WORD
    assert dict((n, w) for n, _, w in N3E_LIST)["own"] == 0xFB20B00000008184


def test_n3g_adds_sb402_and_sb400_after_n3e_s_list():
    """sb402 is sb403's word with bit 22 clear (n3e §0's field placement), sb400 with bits 22 and 23
    clear; both ours but the sideband, appended so every N3e index (the kernel's enum) stays."""
    assert fwtask.EMIT_FORMS == EMIT_LIST and len(EMIT_LIST) == 20
    sb403 = dict((n, w) for n, _, w in N3E_LIST)["sb403"]
    assert dict((n, w) for n, _, w in EMIT_LIST)["sb402"] == sb403 & ~(1 << 22)
    assert dict((n, w) for n, _, w in EMIT_LIST)["sb400"] == sb403 & ~(3 << 22)
    for name, sb, w in N3G_LIST:
        assert fwtask.emit_word(sb) == w and sideband(w) == sb, name
        (a,) = asm([f"emitpds.tasks.taske #0, r2, r3, r4, #0x{sb:x}"])
        assert a == w, name


def test_every_listed_word_is_an_emitpds_form_row_of_the_listing():
    spec = pathlib.Path(gen_verify.spec_path()).read_text()
    rows = [r for r in fwtask.FORMS if r[1] == "EMITPDS"]
    assert [(r[0], r[3]) for r in rows] == [(f"emitpds-{n}", w) for n, _, w in EMIT_LIST]
    for name, kind, mask, value in rows:
        assert mask == fwtask.ALL and gen_verify.in_spec(spec, mask, value), name
        assert fwtask.classify(value) == ("EMITPDS", name)


@pytest.mark.parametrize("name", [n for n, _, _ in EMIT_LIST])
def test_every_listed_word_keeps_every_rule_of_the_owned_form(name):
    sb = dict((n, s) for n, s, _ in EMIT_LIST)[name]
    e = f"emitpds.tasks.taske #0, r2, r3, r4, #0x{sb:x}"
    good = SETUP + [e, "nop.end", "nop.end"]
    assert why_of(good) is None
    assert why_of(good, []) == Y.EMIT_ARGS
    assert why_of(good, entries=(0,)) == Y.EMIT_ENTRY
    assert why_of(SETUP + [OWN_EMIT, e, "nop.end", "nop.end"], entries=(0, 6)) == Y.EMIT_ONCE


def test_the_kernel_header_carries_the_form_list_and_its_names():
    """sgx_own_regs.h: the enum own_arm's form= indexes (SGX_OWN_FORM_<NAME>, own first, then the
    design's order) and the table of names and words the arm and sgx_own_emit_form() read."""
    h = gen_verify.render(fwtask.load_regs())
    enum = h[h.index("enum sgx_own_form {"):]
    enum = enum[:enum.index("};")]
    assert [ln.strip().rstrip(",") for ln in enum.splitlines()[1:]] == \
        [f"SGX_OWN_FORM_{n.upper()}" for n, _, _ in EMIT_LIST] + ["SGX_OWN_FORM_COUNT"]
    tab = h[h.index("sgx_own_emit_forms[SGX_OWN_FORM_COUNT]"):]
    tab = tab[:tab.index("};")]
    for name, sb, w in EMIT_LIST:
        assert f'\t{{ "{name}", 0x{w:016x}ULL }},\t/* sideband 0x{sb:03x} */' in tab, name
    assert tab.count("ULL }") == 20


# ---- emitsb_<f>: emitsb14d with each listed word (round 40, N3e §3.2) --------------------------
@pytest.mark.parametrize("name", SB_FORMS)
def test_emitsb_form_is_emitsb14d_with_that_word_and_nothing_else(name):
    """One blob per listed word: emitsb14d (row D0's survey included) with only the emit word
    changed, so every row also reads D0's pre/post landing slots."""
    import gen_blobs
    sb, w = next((s, x) for n, s, x in EMIT_LIST if n == name)
    d = [ln for ln in gen_blobs.gen_emitsb14d().splitlines() if not ln.startswith(";")]
    f = [ln for ln in gen_blobs.gen_emitsb_form(name).splitlines() if not ln.startswith(";")]
    assert len(d) == len(f)
    diff = [(a.strip(), b.strip()) for a, b in zip(d, f) if a != b]
    assert diff == [(FW14_EMIT, f"emitpds.tasks.taske #0, r2, r3, r4, #0x{sb:x}")]
    src = f"emitsb_{name}"
    blob = fwtask.parse_blob(fwtask.blob_of(src))
    db = fwtask.parse_blob(fwtask.blob_of("emitsb14d"))
    assert [x for x in blob.words if fwtask.classify(x)[0] == "EMITPDS"] == [w]
    assert blob.entries == db.entries and blob.patches == db.patches
    assert [x for x in blob.words if fwtask.classify(x)[0] != "EMITPDS"] == \
        [x for x in db.words if fwtask.classify(x)[0] != "EMITPDS"]
    assert fwtask.refusal(fwtask.blob_of(src), REGS) is None
    assert fwtask.lint((fwtask.ASM / f"{src}.s").read_text()) == []


def test_the_emitsb_forms_are_in_the_map_and_the_kernel_s_accepted_list():
    """Round 40's kernel series (r40-kernel) carries emitsb14, emitsb14d and every emitsb_<f>."""
    import json
    m = json.loads((fwtask.ASM / "fwtask.map").read_text())
    for name in SB_FORMS:
        assert m[f"emitsb_{name}"]["source"] == f"emitsb_{name}.s"
        assert f"emitsb_{name}" in gen_verify.OK_BLOBS
    assert "emitsb_own" not in m and "emitsb_fw14" not in m
    import gen_blobs
    with pytest.raises(ValueError):
        gen_blobs.gen_emitsb_form("fw14")       # that is emitsb14d itself
    with pytest.raises(ValueError):
        gen_blobs.gen_emitsb_form("sb004")


# ---- the land image (round 40, N3e §3.2, the user's decision C (a)) ------------------------------
LAND = [0, 0, 0, 0x00001800, 0x5A5A3A18, 0x5A5A3A1A, 0x00001A00, 0, 0, 0, 0, 0,
        0x07040606, 0x07042CA6, 0x07000305, 0xAF000000]


def test_the_land_image_is_crumb3_s_layout_with_markers_and_no_tim(tmp_path):
    """crumb3's 3 rows and its douta, doutu and halt words (operands unchanged), its two tim lines
    and T3's dword gone: dword 3 (ds1[1]) the douta control of attribute 24, dword 6 (ds1[2])
    attribute 26, dwords 4 and 5 (ds0[2], ds0[3]) the markers Ma and Mb, constants of the image."""
    img = gen_verify.pds_image("land")
    assert img == LAND
    c3 = gen_verify.pds_image("crumb3")
    assert img[12:] == [w for w in c3[12:] if w not in (0x07001FE7, 0x07003547, 0x07003FE7)]
    assert dis_n(tmp_path, img, 12) == ["data"] * 12 + dis_n(tmp_path, c3, 12)[13:15] + \
        [dis_n(tmp_path, c3, 12)[16], "halt"]
    assert img[3] >> 8 & 0xFFF == 24 and img[6] >> 8 & 0xFFF == 26
    assert gen_verify.PDS_IMAGE_ROWS["land"] == 3
    assert gen_verify.pds_ctl("land") == 0x01800100
    assert 0x005A3305 not in img


def test_the_kernel_fills_u0_alone_in_land():
    """The kernel fills U0, V0 and V2 in every image but land, where dwords 4 and 5 are the markers:
    the header says so per image (SGX_OWN_PDS_<K>_FILLV)."""
    assert gen_verify.PDS_FILLV == {"v1": 1, "crumb": 1, "halt": 1, "crumb3": 1, "land": 0,
                                    "mark": 1, "landv": 1, "crumbz": 1, "landq": 0}
    h = gen_verify.render_pds()
    for k in ("crumb", "halt", "crumb3"):
        assert f"#define SGX_OWN_PDS_{k.upper()}_FILLV\t1" in h, k
    assert "#define SGX_OWN_PDS_LAND_FILLV\t0" in h
    assert "#define SGX_OWN_PDS_LAND_WORDS\t16" in h and "#define SGX_OWN_PDS_LAND_CTL\t0x01800100" in h
    assert "asm/fwtask/pds/land.s" in h


# ---- emitsb_<f>s: an after-read of the EDM's own sa0-sa31 (round 41, N3f §3.1) ----------------
# the forms N3f's rows arm (N3f §3.1, the user's decision A (a)): fw14 the
# control (emitsb14s), sbc43 (rows X, LC, T) and sb403 (row Y)
AFTER_FORMS = [("fw14", "emitsb14s", "emitsb14d"), ("sbc43", "emitsb_sbc43s", "emitsb_sbc43"),
               ("sb403", "emitsb_sb403s", "emitsb_sb403"),
               ("sb402", "emitsb_sb402s", "emitsb_sb402")]       # round 42 (N3g row Q)
AFTER_AT, M6, SLOT6 = 224, 0x5A5A3306, 0x40 + 4 * 6       # page dwords 224-255; slot 6 = 88-91


def _after(name):
    import gen_blobs
    return _code(gen_blobs.gen_emitsb_after(name))


def _base(name):
    import gen_blobs
    return _code(gen_blobs.gen_emitsb14d() if name == "fw14" else gen_blobs.gen_emitsb_form(name))


@pytest.mark.parametrize("name,blob,base", AFTER_FORMS)
def test_emitsb_after_is_its_base_plus_the_cmd_6_branch_only(name, blob, base):
    """The dispatch's last `br @tail` becomes `br @more` (same place, so entry 1 and U0 do not
    move); `more:` and `c6:` follow the base's last line. Without them and with the tail branch
    back, the code is the base's, line for line."""
    s, b = _after(name), _base(name)
    i = s.index("work:")
    assert s[i:i + 4] == ["work:", "xor.testtaz.chan0 !c0, p1, r2, #1", "p1 br @c1", "br @more"]
    kept = s[:i + 3] + ["br @tail"] + s[i + 4:s.index("more:")]
    assert kept == b
    assert s.index("more:") > s.index("@entry 1") and s.index("more:") > s.index("pre:")


@pytest.mark.parametrize("name,blob,base", AFTER_FORMS)
def test_the_cmd_6_branch_stores_sa0_to_sa31_then_m6_and_ends_the_command(name, blob, base):
    """more: cmd 6 goes to c6, any other to the tail. c6: sa0-sa31 into page dwords 224-255
    (through r9), then M6 0x5a5a3306 and the run id in slot 6 (dwords 88-89), the echo, cmd 0, a
    fence, state 2 and the tail call: no emit, no pa read, no other store."""
    import gen_blobs
    s = _after(name)
    more = s[s.index("more:") + 1:s.index("c6:")]
    assert more == ["xor.testtaz.chan0 !c0, p1, r2, #6", "p1 br @c6", "br @tail"]
    c6 = s[s.index("c6:") + 1:]
    assert c6[0] == "mov r9, #0xdeadbeef"
    k = c6.index("mov r9, #0xdeadbeef", 1)
    assert _reads_and_stores(c6[:k], "r9", AFTER_AT) == [(f"sa{j}", AFTER_AT + j) for j in range(32)]
    assert c6[k:] == ["mov r9, #0xdeadbeef", "mov r7, #0x5a5a3306",
                      "ldad.bypassl1 r5, [r1,+#3], drc0", "wdf drc0",
                      "stad [r9,+#0], r7", "stad [r9,+#1], r5", "stad [r1,+#5], r5",
                      "mov r4, #0x00000000", "stad [r1,+#1], r4", "idf drc0, bif", "wdf drc0",
                      "mov r3, #0x00000002", "stad [r1,+#2], r3", "br @tail"]
    src = gen_blobs.gen_emitsb_after(name)
    assert "@patch res+%d" % (4 * AFTER_AT) in src and "@patch res+%d" % (4 * SLOT6) in src
    assert not [x for x in c6 if x.startswith("emitpds") or " pa" in x]
    assert sum(1 for x in s if x.startswith("emitpds")) == 1


@pytest.mark.parametrize("name,blob,base", AFTER_FORMS)
def test_emitsb_after_keeps_the_base_s_entries_emit_word_and_patches_and_is_accepted(name, blob,
                                                                                    base):
    """Entry 1's index (so the kernel's U0 and the firmware-page write) and the emit word are the
    base's; the verifier takes it; it is in the map, not in the fork's KUnit list (the pin's
    header: the round's KUnit shim runs it)."""
    import json
    b = fwtask.parse_blob(fwtask.blob_of(blob))
    bb = fwtask.parse_blob(fwtask.blob_of(base))
    assert b.entries == bb.entries
    assert [w for w in b.words if fwtask.classify(w)[0] == "EMITPDS"] == \
        [w for w in bb.words if fwtask.classify(w)[0] == "EMITPDS"]
    assert {p.kind for p in b.patches} == {p.kind for p in bb.patches}
    assert fwtask.refusal(fwtask.blob_of(blob), REGS) is None
    assert fwtask.lint((fwtask.ASM / f"{blob}.s").read_text()) == []
    m = json.loads((fwtask.ASM / "fwtask.map").read_text())
    assert m[blob]["source"] == f"{blob}.s"
    assert blob not in gen_verify.OK_BLOBS


def test_emitsb_after_takes_only_the_design_s_four_forms():
    import gen_blobs
    assert gen_blobs.AFTER_FORMS == ("fw14", "sbc43", "sb403", "sb402")
    assert gen_blobs.after_blob("fw14") == "emitsb14s"
    assert gen_blobs.after_blob("sbc43") == "emitsb_sbc43s"
    assert gen_blobs.after_blob("sb402") == "emitsb_sb402s"
    for bad in ("own", "sb001", "sb400", "sbc4"):
        with pytest.raises(ValueError):
            gen_blobs.gen_emitsb_after(bad)
    srcs = gen_blobs.all_sources()
    assert {n for n in srcs if n.endswith("s") and n.startswith("emitsb")} >= \
        {"emitsb14s", "emitsb_sbc43s", "emitsb_sb403s", "emitsb_sb402s"}


# ---- round 42 (N3g §2): emitsb_sb402s, and the images mark and landv ------------------------------
def test_emitsb_sb402s_is_emitsb_sbc43s_but_the_word():
    """Row Q's blob (N3g §2): emitsb_sbc43s (X's) with the emit word of sideband 0x402 and nothing
    else: every other code line, the entries, the patches; entry 1 at index 30, so the kernel's U0
    is 0x080401ef as every after-read blob's (H1-H4, LC2) and the firmware-page write is crumb3's."""
    import gen_blobs
    q = _code(gen_blobs.gen_emitsb_after("sb402"))
    x = _code(gen_blobs.gen_emitsb_after("sbc43"))
    assert len(q) == len(x)
    assert [(a, b) for a, b in zip(x, q) if a != b] == [
        ("emitpds.tasks.taske #0, r2, r3, r4, #0xc43", "emitpds.tasks.taske #0, r2, r3, r4, #0x402")]
    bq = fwtask.parse_blob(fwtask.blob_of("emitsb_sb402s"))
    bx = fwtask.parse_blob(fwtask.blob_of("emitsb_sbc43s"))
    assert bq.entries == bx.entries and bq.patches == bx.patches
    assert [w for w in bq.words if fwtask.classify(w)[0] == "EMITPDS"] == [0xFB20B08000808184]
    assert [w for w in bq.words if fwtask.classify(w)[0] != "EMITPDS"] == \
        [w for w in bx.words if fwtask.classify(w)[0] != "EMITPDS"]
    e1 = bq.entries[1]
    assert e1 == 30 and (8 << 24 | (0x4000 + e1) << 4 | 0xF) == 0x080401EF


R41_AFTER_SHA = {  # round 41's map (main cfd5d523): rows C and S arm emitsb14s, M and LV emitsb_sbc43s
    "emitsb14s": "c3f9ce90c2ea24208d6b8bcafef3a1f77e105c03bc8c51b4bee5fbcd04e7fb39",
    "emitsb14d": "52c6c8a23db4540d338799ac2b73438f5a0b92dbc68a2b51e8fb0119990867d1",
    "emitsb_sbc43s": "987b0e4e1dc0ba9ec6e2583bb0edd77afef230d7121070daa18a8171dd4a86ad",
    "emitsb_sbc43": "211bb43872a3d6c0c36b0c40baa711fe8f31a1422a13c9f4ec9f3e8e6f5893bf",
}


def test_fw14_s_and_sbc43_s_words_and_blobs_are_unchanged_by_round_42():
    """N3g adds words after the list and one after-read blob: fw14's and sbc43's words, their
    after-read blobs (rows C, S, M and LV arm them) and their map entries stay round 41's."""
    import json
    w = dict((n, x) for n, _, x in fwtask.EMIT_FORMS)
    assert w["fw14"] == 0xFB20B10800C08184 and w["sbc43"] == 0xFB20B18800C08184
    m = json.loads((fwtask.ASM / "fwtask.map").read_text())
    for name, sha in R41_AFTER_SHA.items():
        assert m[name]["sha256"] == sha, name


MARK_DATA = [0, 0, 0, 0, 0, 0, 0x200, 0x005A3305, 0x005D3000, 0x005D1000, 0x00000D00, 0x00000100]
LANDV_DATA = [0, 0, 0, 0, 0, 0, 0x200, 0x1800, 0x5A5A3A18, 0x5A5A3A1A, 0x1A00, 0]


def test_the_mark_image_is_crumb3_with_two_markers_in_its_third_row(tmp_path):
    """N3g §2 item 2, decision B (a): crumb3's 8 data dwords; its third row M13 0x005d3000 (ds0[4]),
    M1 0x005d1000 (ds0[5]) and their douta controls, attribute 13 (ds1[4]) and 1 (ds1[5]); crumb3's
    T1 and two douta, then the two marker douta, then crumb3's T2, doutu, T3 and halt: 21 dwords."""
    img = gen_verify.pds_image("mark")
    c3 = gen_verify.pds_image("crumb3")
    assert img[:12] == MARK_DATA and img[:8] == c3[:8] and len(img) == 21
    assert img[12:15] == c3[12:15] and img[17:] == c3[15:]
    assert img[10] >> 8 & 0xFFF == 13 and img[11] >> 8 & 0xFFF == 1
    d = dis_n(tmp_path, img, 12)
    assert d == ["data"] * 12 + dis_n(tmp_path, c3, 12)[12:15] + [
        "movs douta, ds0[4], ds1[4], ds0[4], ds0[4]",
        "movs douta, ds0[5], ds1[5], ds0[5], ds0[5]"] + dis_n(tmp_path, c3, 12)[15:]
    assert gen_verify.PDS_IMAGE_ROWS["mark"] == 3 and gen_verify.pds_ctl("mark") == 0x01800100
    assert gen_verify.PDS_FILLV["mark"] == 1
    # the markers name pages below 0x10000000, none of round 41's kept words (n3g §2 item 2)
    assert all(x < 0x10000000 for x in img[8:10])


def test_the_landv_image_is_land_with_v0_and_v2_to_attributes_0_and_2(tmp_path):
    """N3g §2 item 3: dwords 0-3 U0, U1, U2, the douta control of attribute 0; 4-7 V0, V2 (the
    kernel's), attribute 2's control, attribute 24's; 8-11 Ma, Mb, attribute 26's, 0. Program:
    crumb3's two douta (V0, V2), douta Ma (ds0[4], ds1[3]) and Mb (ds0[5], ds1[4]), land's doutu
    and halt; no tim. 18 dwords, the kernel fills U0, V0 and V2."""
    img = gen_verify.pds_image("landv")
    c3, land = gen_verify.pds_image("crumb3"), gen_verify.pds_image("land")
    assert img[:12] == LANDV_DATA and len(img) == 18
    assert [img[3] >> 8 & 0xFFF, img[6] >> 8 & 0xFFF, img[7] >> 8 & 0xFFF,
            img[10] >> 8 & 0xFFF] == [0, 2, 24, 26]
    assert img[12:14] == c3[13:15] and img[16:] == land[14:]
    assert dis_n(tmp_path, img, 12) == ["data"] * 12 + [
        "movs douta, ds0[2], ds1[1], ds0[2], ds0[2]",
        "movs douta, ds0[3], ds1[2], ds0[3], ds0[3]",
        "movs douta, ds0[4], ds1[3], ds0[4], ds0[4]",
        "movs douta, ds0[5], ds1[4], ds0[5], ds0[5]",
        "movs doutu, ds0[0], ds0[1], ds1[0], ds0[0]",
        "halt"]
    assert not [w for w in img[12:] if w in (0x07001FE7, 0x07003547, 0x07003FE7)]
    assert gen_verify.PDS_IMAGE_ROWS["landv"] == 3 and gen_verify.pds_ctl("landv") == 0x01800100
    assert gen_verify.PDS_FILLV["landv"] == 1


def test_the_kernel_header_carries_mark_and_landv():
    h = gen_verify.render_pds()
    for k, n in (("mark", 21), ("landv", 18)):
        u = k.upper()
        assert f"#define SGX_OWN_PDS_{u}_WORDS\t{n}" in h and f"#define SGX_OWN_PDS_{u}_FILLV\t1" in h
        assert f"asm/fwtask/pds/{k}.s" in h


# ---- round 45 (N3j §9.0, decision E (c)): the images crumbz and landq --------------------------
LANDQ_DATA = [0, 0, 0, 0x1800, 0x5A5A3A18, 0x5A5A3A1A, 0x1A00, 0, 0x005D2000, 0x005D1000, 0, 0x100]


def test_the_crumbz_image_is_crumb3_without_its_two_douta(tmp_path):
    """N3j §9.0: crumb3's 12 data dwords word for word (the kernel fills U0, V0 and V2, so the data
    rows match crumb3's on the page) and crumb3's program without the douta of V0 and V2: T1, T2,
    the doutu, T3 and halt, every operand unchanged; it writes no attribute. 17 dwords."""
    img = gen_verify.pds_image("crumbz")
    c3 = gen_verify.pds_image("crumb3")
    assert len(img) == 17 and img[:12] == c3[:12]
    assert img[12:] == c3[12:13] + c3[15:]
    d3 = dis_n(tmp_path, c3, 12)
    assert dis_n(tmp_path, img, 12) == ["data"] * 12 + d3[12:13] + d3[15:]
    assert not [t for t in dis_n(tmp_path, img, 12) if "douta" in t]
    assert [t.split(",")[0] for t in dis_n(tmp_path, img, 12)[12:]] == [
        "movs tim", "movs tim", "movs doutu", "movs tim", "halt"]
    assert gen_verify.PDS_IMAGE_ROWS["crumbz"] == 3 and gen_verify.pds_ctl("crumbz") == 0x01800100
    assert gen_verify.PDS_FILLV["crumbz"] == 1


def test_the_landq_image_is_land_with_q0_and_m1_to_attributes_0_and_1(tmp_path):
    """N3j §9.0: land's 12 data dwords with its third row Q0 0x005d2000 (ds0[4]), M1 0x005d1000
    (ds0[5]) and the douta controls of attributes 0 (ds1[4]) and 1 (ds1[5]); land's two marker
    douta, then Q0 to attribute 0 and M1 to attribute 1, then land's doutu and halt; no tim. The
    kernel fills U0 only (dwords 4 and 5 are Ma and Mb). 18 dwords; sa0's word above sa1's."""
    img = gen_verify.pds_image("landq")
    land, mark = gen_verify.pds_image("land"), gen_verify.pds_image("mark")
    assert img[:12] == LANDQ_DATA and img[:8] == land[:8] and len(img) == 18
    assert [img[3] >> 8 & 0xFFF, img[6] >> 8 & 0xFFF, img[10] >> 8 & 0xFFF,
            img[11] >> 8 & 0xFFF] == [24, 26, 0, 1]
    assert img[12:14] == land[12:14] and img[14:16] == mark[15:17] and img[16:] == land[14:]
    assert dis_n(tmp_path, img, 12) == ["data"] * 12 + [
        "movs douta, ds0[2], ds1[1], ds0[2], ds0[2]",
        "movs douta, ds0[3], ds1[2], ds0[3], ds0[3]",
        "movs douta, ds0[4], ds1[4], ds0[4], ds0[4]",
        "movs douta, ds0[5], ds1[5], ds0[5], ds0[5]",
        "movs doutu, ds0[0], ds0[1], ds1[0], ds0[0]",
        "halt"]
    assert not [w for w in img[12:] if w in (0x07001FE7, 0x07003547, 0x07003FE7)]
    assert img[9] == mark[9] == 0x005D1000 and img[8] > img[9]
    assert all(x < 0x10000000 for x in img[8:10])
    assert gen_verify.PDS_IMAGE_ROWS["landq"] == 3 and gen_verify.pds_ctl("landq") == 0x01800100
    assert gen_verify.PDS_FILLV["landq"] == 0


def test_the_kernel_header_carries_crumbz_and_landq():
    h = gen_verify.render_pds()
    for k, n, fillv in (("crumbz", 17, 1), ("landq", 18, 0)):
        u = k.upper()
        assert f"#define SGX_OWN_PDS_{u}_WORDS\t{n}" in h and f"#define SGX_OWN_PDS_{u}_FILLV\t{fillv}" in h
        assert f"asm/fwtask/pds/{k}.s" in h
    assert "crumb3.s, land.s, mark.s, landv.s, crumbz.s and landq.s" in h
