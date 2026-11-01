# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Tests for edm_dataflow.py — the whole-firmware dataflow of the EDM.

Synthetic listings only: the encodings are zeros and the instructions are text we wrote, in
the format usse-dis prints. The analysis names its subjects with neutral tokens ({R:0x012c} a
register, {W:HOST_CTL+0x01c} a structure word, {F:STRUCT+0xOFF:bit} a flag bit), so the TSV
does not depend on the glossary; render() resolves them. The generated document is checked
against the TSV when resgx545-data is present."""
import pathlib

import pytest

import edm_dataflow as df
import edmtrace

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent

G = edmtrace.Glossary(
    registers={0x12C: "CR_EVENT_STATUS", 0x200: "CR_VDM_START"},
    fields={("HOST_CTL", 0x038): "host_ctl.assert_fail", ("HOST_CTL", 0x01C): "host_ctl.rate",
            ("HWRENDERCONTEXT", 0x004): "hw_render_context.priority",
            ("HWRENDERCONTEXT", 0x000): "hw_render_context.fw_com_ctx_flags"},
    flags={("HWRENDERCONTEXT", 0x000): {4: "CONTEXT_FLAGS.SUSPEND"}},
)


def listing(*texts, start=0):
    return [f"{start + i:6d}: 0x{0:016X}\t{t}" for i, t in enumerate(texts)]


def arg(struct):
    """A handler's ui32Data[1], typed: a pointer that says where it came from."""
    return df.V("ptr", struct=struct, origin=("S", "COMMAND", 0x0C))


def run(*texts, labels=(0,), handlers=None):
    insns = edmtrace.parse(listing(*texts))
    return df.analyze(insns, list(labels), glossary=G, handlers=handlers or {})


def uses(res, subject, use=None):
    return [r.detail for r in res.rows
            if r.subject == subject and (use is None or r.use == use)]


# --- structure ---------------------------------------------------------------------------

def test_routine_ranges_run_from_label_to_label():
    assert df.ranges([0x10, 0, 0x20, 0x10], 0x30) == [(0, 0xF), (0x10, 0x1F), (0x20, 0x2F)]


def test_successors_follow_absolute_and_relative_branches():
    insns = edmtrace.parse(listing("ba #0x00000003", "p0 ba #0x00000000", "!p1 br #0x00000002",
                                   "lapc", "nop.end", "ba.savelink #0x00000003", "nop"))
    by = {i.index: i for i in insns}
    assert df.successors(by[0], 7) == [3]
    assert df.successors(by[1], 7) == [0, 2]
    assert df.successors(by[2], 7) == [4, 3]                # br is relative to itself
    assert df.successors(by[3], 7) == [] and df.successors(by[4], 7) == []
    assert df.successors(by[5], 7) == [6]                   # the call returns


# --- values ------------------------------------------------------------------------------

def test_structure_words_are_named_by_the_glossary_or_by_offset():
    res = run("ldad.bpcache r2, [sa1,+#14], drc0", "ldad.bpcache r3, [sa1,+#15], drc0",
              "wdf drc0", "lapc")
    assert res.subjects["HOST_CTL+0x038"] == "word"
    assert res.subjects["HOST_CTL+0x03c"] == "word"
    doc = df.render(df.rows_of(res), G)
    assert "`HOST_CTL+0x038` `host_ctl.assert_fail`: read 1×" in doc
    assert "`HOST_CTL+0x03c`: read 1×" in doc
    assert uses(res, "HOST_CTL+0x038", "read") == ["into r2"]


def test_a_word_written_to_a_register_says_so_with_its_transform():
    res = run("ldad.bpcache r2, [sa1,+#7], drc0", "wdf drc0", "and r3, r2, #0x0000FFFF",
              "str #75, r3", "str #128, r2", "lapc")
    assert uses(res, "HOST_CTL+0x01c", "to_reg") == ["{R:0x012c} as & 0xffff",
                                                     "{R:0x0200}"]
    assert uses(res, "0x012c", "write") == ["{W:HOST_CTL+0x01c} & 0xffff"]
    assert uses(res, "HOST_CTL+0x01c", "arith") == ["& 0xffff"]


def test_stores_name_both_sides():
    res = run("ldad.bpcache r2, [sa1,+#7], drc0", "wdf drc0", "stad.bpcache [sa1,+#14], r2",
              "lapc")
    assert uses(res, "HOST_CTL+0x038", "write") == ["{W:HOST_CTL+0x01c}"]
    assert uses(res, "HOST_CTL+0x01c", "to_word") == ["{W:HOST_CTL+0x038}"]


def test_register_reads_flow_to_their_uses():
    res = run("ldr r4, #75, drc0", "and.testtanz.chan0 !c0, p0, r4, #0x00000001",
              "p0 ba #0x00000000", "str #128, r4", "lapc")
    assert uses(res, "0x012c", "read") == ["into r4"]
    assert uses(res, "0x012c", "to_reg") == ["{R:0x0200}"]
    (b,) = uses(res, "0x012c", "branch")
    assert b.startswith("bit 0 set: to 0x0") and "loop" in b


def test_a_simple_skip_lists_what_the_other_path_does():
    res = run("ldad.bpcache r1, [r7,+#0], drc0", "wdf drc0",
              "and.testtaz.chan0 !c0, p0, r1, #0x00000010", "p0 ba #0x00000006",
              "str #128, #0x00000001", "stad.bpcache [r7,+#1], #0", "lapc",
              handlers={0: {"r7": df.ptr("HWRENDERCONTEXT")}})
    assert uses(res, "HWRENDERCONTEXT+0x000", "tested") == ["bit 4 ({F:HWRENDERCONTEXT+0x000:4})"]
    assert uses(res, "HWRENDERCONTEXT+0x000", "branch") == [
        "bit 4 ({F:HWRENDERCONTEXT+0x000:4}) clear: to 0x6; set: runs W {R:0x0200}, "
        "st {W:HWRENDERCONTEXT+0x004}"]


def test_predicated_effects_are_guarded_by_the_test():
    res = run("ldad.bpcache r1, [sa1,+#7], drc0", "wdf drc0",
              "xor.testtaz.chan0 !c0, p1, r1, #0x00000003", "!p1 str #128, #0x00000002", "lapc")
    assert uses(res, "HOST_CTL+0x01c", "guards") == ["!= 0x3: W {R:0x0200} <- 0x2"]
    assert uses(res, "0x0200", "write") == ["0x2 (when {W:HOST_CTL+0x01c} != 0x3)"]


def test_paths_that_disagree_leave_the_value_unresolved():
    res = run("ldad.bpcache r1, [sa1,+#7], drc0", "wdf drc0",
              "and.testtaz.chan0 !c0, p0, r1, #0x00000001", "p0 ba #0x00000006",
              "mov r2, #0x00000001", "ba #0x00000007", "mov r2, #0x00000002",
              "str #128, r2", "lapc")
    assert uses(res, "0x0200", "write") == ["?"]


def test_given_pointer_words_rest_on_records():
    # TA3DCtl's kernel CCB and HWPerf words (E002); the transfer context's client CCB and its
    # control block (transfer §2.2: E018, E021) and its queue links (E015). Every other
    # pointer word is typed by what the firmware stores in it.
    assert df.GLOSSARY_POINTERS == {
        ("TA3D_CTL", 0x058): "KCCB", ("TA3D_CTL", 0x0ac): "HWPERF_CB",
        ("HWTRANSFERCONTEXT", 0x00c): "CCB_TQ", ("HWTRANSFERCONTEXT", 0x010): "CCB_CTL",
        ("HWTRANSFERCONTEXT", 0x0ac): "HWTRANSFERCONTEXT",
        ("HWTRANSFERCONTEXT", 0x0b0): "HWTRANSFERCONTEXT"}


def test_pointers_of_one_type_from_different_words_keep_their_type_at_a_join(monkeypatch):
    # walk a list: the first context comes from sa15, the next from the previous one's link
    # (a stand-in link word)
    monkeypatch.setitem(df.GLOSSARY_POINTERS, ("HWRENDERCONTEXT", 0x034), "HWRENDERCONTEXT")
    res = run("mov sa15, r7", "lapc",
              "mov r0, sa15", "ldad.bpcache r1, [r0,+#1], drc0", "wdf drc0",
              "and.testtaz.chan0 !c0, p0, r1, #0x00000001", "p0 ba #0x00000009",
              "ldad.bpcache r0, [r0,+#13], drc0", "ba #0x00000003", "lapc",
              labels=(0, 2), handlers={0: {"r7": arg("HWRENDERCONTEXT")}})
    assert uses(res, "HWRENDERCONTEXT+0x004", "read") == ["into r1"]
    assert uses(res, "HWRENDERCONTEXT+0x034", "read") == ["into r0"]
    assert not [r for r in res.rows if r.kind == "unresolved"]


def test_pointer_words_type_what_they_load(monkeypatch):
    # a given pointer word (a stand-in) types what is loaded through it
    monkeypatch.setitem(df.GLOSSARY_POINTERS, ("HWRTDATA", 0x000), "HWRENDERCONTEXT")
    res = run("ldad.bpcache r4, [r7,+#0], drc0", "wdf drc0", "ldad.bpcache r5, [r4,+#1], drc0",
              "lapc", handlers={0: {"r7": df.ptr("HWRTDATA")}})
    assert uses(res, "HWRTDATA+0x000", "pointer") == ["to HWRENDERCONTEXT"]
    assert uses(res, "HWRENDERCONTEXT+0x004", "read") == ["into r5"]


def test_an_array_base_plus_an_index_is_an_element():
    # kernel CCB (TA3D_CTL+0x058) + read offset * 32 = a command
    res = run("ldad.bpcache r1, [sa2,+#1], drc0", "ldad.bpcache r0, [sa0,+#22], drc0",
              "wdf drc0", "imae.u r0, r1.low, #32.low, r0, u32",
              "ldad.bpcache r4, [r0,+#0], drc0", "lapc")
    assert uses(res, "COMMAND+0x000", "read") == ["into r4"]


def test_stored_pointers_type_the_slot_they_are_stored_in():
    res = run("mov sa15, r7", "lapc", "mov r0, sa15", "ldad.bpcache r1, [r0,+#1], drc0", "lapc",
              labels=(0, 2), handlers={0: {"r7": arg("HWRENDERCONTEXT")}})
    assert res.inferred == {"sa15": "HWRENDERCONTEXT"}
    assert uses(res, "HWRENDERCONTEXT+0x004", "read") == ["into r1"]


def test_indexed_attributes_with_a_constant_base_are_a_slot_family():
    # sa[15 + priority] <- context; elsewhere sa[15 + i] is read back and dereferenced
    res = run("ldad.bpcache r2, [r7,+#1], drc0", "wdf drc0",
              "imae.u r3, r2.low, #1.low, #15, u32", "mov i.l, r3", "mov sa[il + #0], r7",
              "lapc", "imae.u r1, r8.low, #1.low, #15, u32", "mov i.l, r1",
              "mov r0, sa[il + #0]", "ldad.bpcache r1, [r0,+#1], drc0", "lapc",
              labels=(0, 6), handlers={0: {"r7": arg("HWRENDERCONTEXT")}})
    assert res.inferred == {"sa15": "HWRENDERCONTEXT"}
    assert uses(res, "HWRENDERCONTEXT+0x004", "read") == ["into r2", "into r1"]
    assert uses(res, "sa15", "write") == ["{W:COMMAND+0x00c} (indexed)"]
    assert not [r for r in res.rows if r.use == "sa_indexed"]


def test_a_loop_counter_index_keeps_its_constant_base():
    # i = 0, 1, ...: sa[15 + i] is read in a loop; at the join the index is "15 + something"
    assert df.meet(df.const(16), df.V("idx", value=15)) == df.V("idx", value=15)
    assert df.meet(df.V("idx", value=16), df.V("idx", value=15)) == df.V("idx", value=15)
    assert df.meet(df.const(3), df.V("idx", value=15)) == df.UNKNOWN


def test_a_slot_that_also_receives_untyped_values_stays_untyped():
    # sa7 also receives a transformed word; sa8 only zero, a copy of another slot and values
    # the analysis lost
    res = run("mov sa7, r7", "lapc", "ldad.bpcache r9, [sa1,+#7], drc0", "and r9, r9, #0x00000003",
              "mov sa7, r9", "lapc", "mov sa8, r7", "mov sa8, #0", "mov sa8, r12", "mov sa8, sa9",
              "lapc",
              labels=(0, 2, 6), handlers={0: {"r7": arg("HWRENDERCONTEXT")},
                                          6: {"r7": arg("HWRENDERCONTEXT")}})
    assert res.inferred == {"sa8": "HWRENDERCONTEXT"}


def test_a_merged_pointer_beside_a_lost_value_is_no_evidence(monkeypatch):
    # two paths agree on the type but neither says where the pointer came from, and the slot
    # also receives a value the analysis lost (it may hold another kind of context); the two
    # link words are stand-ins
    for off in (0x030, 0x034):
        monkeypatch.setitem(df.GLOSSARY_POINTERS, ("HWRENDERCONTEXT", off), "HWRENDERCONTEXT")
    res = run("ldad.bpcache r1, [sa1,+#7], drc0", "wdf drc0",
              "and.testtaz.chan0 !c0, p0, r1, #0x00000001", "p0 ba #0x00000006",
              "ldad.bpcache r2, [r7,+#13], drc0", "ba #0x00000007",
              "ldad.bpcache r2, [r7,+#12], drc0", "mov sa7, r2", "mov sa7, r12", "lapc",
              handlers={0: {"r7": df.ptr("HWRENDERCONTEXT")}})
    assert res.inferred == {}


def test_a_counted_loop_over_an_indexed_family_stays_typed():
    # for (i = 0; ; i++) r0 = sa[15 + i]; r0->word 1
    res = run("mov sa15, r7", "lapc",
              "mov r8, #0x00000000", "imae.u r1, r8.low, #1.low, #15, u32", "mov i.l, r1",
              "mov r0, sa[il + #0]", "ldad.bpcache r2, [r0,+#1], drc0", "wdf drc0",
              "imae.u r8, r8.low, #1.low, #1, u32", "p0 ba #0x00000003", "lapc",
              labels=(0, 2), handlers={0: {"r7": arg("HWRENDERCONTEXT")}})
    assert uses(res, "HWRENDERCONTEXT+0x004", "read") == ["into r2"]


def test_unreached_padding_does_not_wipe_reached_code():
    res = run("ldad.bpcache r1, [sa1,+#7], drc0", "ba #0x00000003", "nop", "str #128, r1",
              "lapc")
    assert uses(res, "0x0200", "write") == ["{W:HOST_CTL+0x01c}"]


def test_a_merged_pointer_counts_when_the_slot_receives_nothing_unknown(monkeypatch):
    # two stand-in link words, both to a render context
    for off in (0x030, 0x034):
        monkeypatch.setitem(df.GLOSSARY_POINTERS, ("HWRENDERCONTEXT", off), "HWRENDERCONTEXT")
    res = run("ldad.bpcache r1, [sa1,+#7], drc0", "wdf drc0",
              "and.testtaz.chan0 !c0, p0, r1, #0x00000001", "p0 ba #0x00000006",
              "ldad.bpcache r2, [r7,+#13], drc0", "ba #0x00000007",
              "ldad.bpcache r2, [r7,+#12], drc0", "mov sa7, r2", "mov sa7, #0", "lapc",
              handlers={0: {"r7": df.ptr("HWRENDERCONTEXT")}})
    assert res.inferred == {"sa7": "HWRENDERCONTEXT"}


def test_calls_pass_values_in_and_forget_what_the_callee_writes():
    res = run("ldad.bpcache r16, [sa1,+#7], drc0", "ldad.bpcache r17, [sa1,+#14], drc0",
              "wdf drc0", "ba.savelink #0x00000007", "str #128, r16", "str #75, r17", "lapc",
              "str #75, r16", "mov r17, #0x00000000", "lapc")
    assert uses(res, "HOST_CTL+0x01c", "to_reg") == ["{R:0x0200}", "{R:0x012c}"]
    assert uses(res, "0x012c", "write") == ["?", "{W:HOST_CTL+0x01c}"]


def test_unresolved_accesses_are_counted_not_guessed():
    res = run("ldad.bpcache r1, [r9,+#3], drc0", "str r20, r18", "p2 ba #0x00000000", "lapc")
    got = sorted(r.use for r in res.rows if r.kind == "unresolved")
    assert got == ["branch", "mem", "regaddr"]


def test_unreached_code_is_analysed_from_its_own_root():
    res = run("lapc", "ldad.bpcache r1, [sa1,+#14], drc0", "lapc", labels=(0,))
    assert uses(res, "HOST_CTL+0x038", "read") == ["into r1"]
    assert res.coverage["extra_roots"] == 1


# --- TSV and document --------------------------------------------------------------------

def test_tsv_round_trip(tmp_path):
    res = run("ldad.bpcache r2, [sa1,+#14], drc0", "wdf drc0", "str #75, r2", "lapc")
    p = tmp_path / "df.tsv"
    df.write_tsv(res, p)
    rows = df.read_tsv(p)
    assert {(r["subject"], r["use"]) for r in rows} >= {("HOST_CTL+0x038", "read"),
                                                        ("HOST_CTL+0x038", "to_reg"),
                                                        ("0x012c", "write")}
    assert any(r["kind"] == "meta" and r["subject"] == "insns" for r in rows)
    assert "term" not in df.COLUMNS and "term" not in rows[0]


SOURCE = ("ldad.bpcache r1, [r7,+#0], drc0", "wdf drc0",
          "and.testtaz.chan0 !c0, p0, r1, #0x00000010", "p0 ba #0x00000006",
          "str #128, #0x00000001", "stad.bpcache [r7,+#1], #0", "lapc")


def test_the_tsv_does_not_depend_on_the_glossary(tmp_path):
    insns = edmtrace.parse(listing(*SOURCE))
    handlers = {0: {"r7": df.ptr("HWRENDERCONTEXT")}}
    named, bare = tmp_path / "named.tsv", tmp_path / "bare.tsv"
    df.write_tsv(df.analyze(insns, [0], glossary=G, handlers=handlers), named)
    df.write_tsv(df.analyze(insns, [0], glossary=edmtrace.Glossary({}, {}, {}),
                            handlers=handlers), bare)
    assert named.read_bytes() == bare.read_bytes()
    text = named.read_text()
    for name in ("CR_VDM_START", "CONTEXT_FLAGS", "hw_render_context"):
        assert name not in text


def test_names_are_resolved_at_render_time(tmp_path):
    insns = edmtrace.parse(listing(*SOURCE))
    res = df.analyze(insns, [0], handlers={0: {"r7": df.ptr("HWRENDERCONTEXT")}})
    p = tmp_path / "df.tsv"
    df.write_tsv(res, p)
    rows = df.read_tsv(p)
    named = " ".join(df.render(rows, G).split())
    assert "bit 4 (CONTEXT_FLAGS.SUSPEND) clear: to 0x6; set: runs W CR_VDM_START, " \
        "st hw_render_context.priority" in named
    assert "{" not in named
    bare = " ".join(df.render(rows, edmtrace.Glossary({}, {}, {})).split())
    # without a term: the offset, and a flag bit with no name is just the bit
    assert "bit 4 clear: to 0x6; set: runs W 0x0200, st HWRENDERCONTEXT+0x004" in bare
    assert "{" not in bare and "CR_VDM_START" not in bare


def test_document_lists_words_and_registers(tmp_path):
    res = run("ldad.bpcache r2, [sa1,+#14], drc0", "wdf drc0", "str #75, r2", "lapc")
    p = tmp_path / "df.tsv"
    df.write_tsv(res, p)
    doc = df.render(df.read_tsv(p), G)
    assert "`HOST_CTL+0x038` `host_ctl.assert_fail`: read 1×" in doc
    assert "written to CR_EVENT_STATUS" in doc
    assert "`0x012c` `CR_EVENT_STATUS`: written 1× from host_ctl.assert_fail" in doc
    lines = doc.splitlines()
    assert all(len(ln) <= 100 and ln == ln.rstrip() for ln in lines)


def test_the_document_points_at_the_published_docs(tmp_path):
    p = tmp_path / "df.tsv"
    df.write_tsv(run("lapc"), p)
    doc = " ".join(df.render(df.read_tsv(p), G).split())
    assert "our disassembly of the firmware, for interoperability; facts only, no code" in doc
    assert "doc/specs/hw_spec.md" in doc and "doc/specs/transfer.md" in doc
    assert "doc/glossary.md" in doc and f"Evidence: {df.EVIDENCE} (the dataflow record" in doc
    for old in ("design" "/", "corpus" "/", "[R" "E]", "§1" "3"):
        assert old not in doc


def test_the_document_says_where_given_pointers_come_from(tmp_path):
    p = tmp_path / "df.tsv"
    df.write_tsv(run("lapc"), p)
    doc = " ".join(df.render(df.read_tsv(p), G).split())
    assert "Given: a pointer word a record establishes (E002, E015, `doc/specs/transfer.md` " \
        "§2.2)" in doc
    assert "glossary meaning" not in doc and "TA/3D layouts" not in doc


@pytest.mark.skipif(not df.TSV.exists(), reason="needs the dataflow TSV (resgx545-data)")
def test_the_design_document_is_generated_from_the_tsv():
    assert df.DOC.read_text() == df.render(df.read_tsv(df.TSV))


def test_a_firmware_container_is_refused(tmp_path, capsys):
    """The tools take the cut image (00_ukernel.bin), not the .fw container: its header would
    disassemble as 30 instructions and shift every index."""
    fw = tmp_path / "sgx545_ukernel.fw"
    fw.write_bytes(b"SGX545FW" + bytes(232) + bytes(8))
    tsv, doc = tmp_path / "t.tsv", tmp_path / "d.md"
    assert df.main(["--ukernel", str(fw), "--tsv", str(tsv), "--doc", str(doc)]) == 2
    assert "00_ukernel.bin" in capsys.readouterr().err
    assert not tsv.exists() and not doc.exists()


def test_render_replaces_the_document_from_the_tsv_alone(tmp_path):
    """The document names registers from the glossary, which grows phase by phase: --render
    rewrites it from the TSV (no firmware needed), whatever the document held, and takes
    --tsv and --doc like the full run."""
    tsv, doc = tmp_path / "t.tsv", tmp_path / "d.md"
    df.write_tsv(run("ldad.bpcache r2, [sa1,+#14], drc0", "wdf drc0", "lapc"), tsv)
    doc.write_text("a stale document\n")
    assert df.main(["--render", "--tsv", str(tsv), "--doc", str(doc)]) == 0
    assert doc.read_text() == df.render(df.read_tsv(tsv)) != "a stale document\n"
    # the flags may come in any order
    doc.write_text("stale again\n")
    assert df.main(["--tsv", str(tsv), "--doc", str(doc), "--render"]) == 0
    assert doc.read_text() == df.render(df.read_tsv(tsv))


def test_the_usage_names_every_form(tmp_path, capsys):
    assert df.main(["--bogus"]) == 2
    err = capsys.readouterr().err
    assert "--ukernel" in err and "--check" in err and "--render" in err
