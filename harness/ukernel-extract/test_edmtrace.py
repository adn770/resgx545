# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Tests for edmtrace.py, a linear value tracer over usse-dis listings of the EDM.

Synthetic listings, the encodings zeros and the instructions text we wrote in the format
usse-dis prints; the checks on the real ukernel run when $RESGX545_UKERNEL is given."""
import os
import pathlib
import subprocess

import pytest

import edmtrace

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
UKERNEL = pathlib.Path(os.environ.get("RESGX545_UKERNEL", "/nonexistent"))
USSE_DIS = ROOT / "tools" / "usse-dis" / "usse-dis"

# Register and field names as the glossary gives them (our terms; not every offset has one).
NAMES = {0x204: "CR_TE_AA", 0x208: "CR_TE_MTILE_1", 0x200: "CR_VDM_START",
         0x12C: "CR_EVENT_STATUS"}
FIELDS = {("CMDTA", 0x238): "cmd_ta.te_aa", ("CMDTA", 0x01C): "cmd_ta.frag_flags",
          ("CMDTA", 0x038): "cmd_ta.hw_render_details_dev_vaddr",
          ("CMDTA", 0x008): "cmd_ta.pds_bgnd", ("CMDTA", 0x2A8): "cmd_ta.patches_3d",
          ("HWRENDERDETAILS", 0x0D4): "hw_render_details.frag_flags",
          ("HWRENDERDETAILS", 0x16C): "hw_render_details.src_syncs",
          ("HWRTDATA", 0x004): "hw_rt_data.hw_render_details_dev_vaddr",
          ("HWRTDATA", 0x034): "hw_rt_data.state"}


def listing(*texts, start=0):
    return [f"{start + i:6d}: 0x{0:016X}\t{t}" for i, t in enumerate(texts)]


def trace(lines, seeds=None, labels=None, start=None, end=None):
    insns = edmtrace.parse(lines)
    lo = insns[0].index if start is None else start
    hi = insns[-1].index if end is None else end
    return edmtrace.trace(insns, lo, hi, names=NAMES, seeds=seeds or {}, labels=labels or {},
                          fields=FIELDS)


def texts(events):
    return [e.text for e in events]


# --- parsing --------------------------------------------------------------------------------

def test_parse_splits_predicate_and_mnemonic():
    insns = edmtrace.parse(listing("p0 ba #0x00000010", "!p1 mov r1, #0x00000002", "nop"))
    assert [(i.index, i.pred, i.op) for i in insns] == [(0, "p0", "ba"), (1, "!p1", "mov"),
                                                         (2, None, "nop")]
    assert insns[1].args == ["r1", "#0x00000002"]


def test_parse_keeps_bracketed_operands_whole():
    (i,) = edmtrace.parse(listing("ldad.bpcache.fetch2 r4, [r2,#0++], drc0"))
    assert i.op == "ldad" and i.mods == ["bpcache", "fetch2"]
    assert i.args == ["r4", "[r2,#0++]", "drc0"]


def test_r2_labels_are_instruction_indices():
    labels = edmtrace.load_labels(["f edm.ta @ 0x8e8", "CCu a comment @ 0x8e8",
                                   "f hwperf.log @ 0xcbc8"])
    assert labels == {0x11D: "edm.ta", 0x1979: "hwperf.log"}


# --- memory operand semantics (tools/usse-dis/README.md) -------------------------------------

@pytest.mark.parametrize("mods,operand,dwords,step", [
    ([], "[r1,+#5]", [5], 0),                        # plain: b + k
    ([], "[r1,-#2]", [-2], 0),
    ([], "[r2,#1++]", [0], 1),                       # post-increment: b, then b += k
    (["fetch4"], "[r1,+#24]", [25, 26, 27, 28], 0),  # fetch: one element after the offset
    (["fetch2"], "[r2,#0++]", [0, 1], 2),            # fetch, post-increment: b += N
    (["fetch2"], "[r1,#82++]", [82, 83], 2),
])
def test_memory_operand_dwords(mods, operand, dwords, step):
    assert edmtrace.mem_dwords(mods, operand) == ("r" + operand[2], dwords, step)


def test_register_offsets_are_not_resolved():
    assert edmtrace.mem_dwords([], "[r17,+r19]") is None


# --- tracing --------------------------------------------------------------------------------

def test_mmio_write_of_a_constant_and_of_an_immediate():
    ev = trace(listing("mov r2, #0x00004000", "str #75, r2", "str #128, #1"))
    assert texts(ev) == ["W CR_EVENT_STATUS <- 0x4000", "W CR_VDM_START <- 0x1"]
    assert [e.index for e in ev] == [1, 2]


def test_mmio_read_names_the_register():
    ev = trace(listing("ldr r4, #75, drc0", "str #128, r4"))
    assert texts(ev) == ["R CR_EVENT_STATUS -> r4", "W CR_VDM_START <- CR_EVENT_STATUS"]


def test_registers_without_a_glossary_term_print_their_offset():
    ev = trace(listing("ldr r4, #198, drc0", "str #199, r4"))
    assert texts(ev) == ["R 0x0318 -> r4", "W 0x031c <- 0x0318"]


def test_constants_fold_through_or_and_and_not():
    ev = trace(listing("mov r1, #0x00010000", "or r1, r1, #0x00000011",
                       "and r1, r1, ~#0x00000001", "str #128, r1"))
    assert texts(ev)[-1] == "W CR_VDM_START <- 0x10010"


def test_struct_fields_flow_from_loads_to_register_writes():
    # r1 = a TA command; the loads start at byte 0x238 (dword 142)
    lines = listing("mov r2, #0x00000238", "imae.u r2, r2.low, #1.low, r1, u32",
                    "ldad.bpcache.fetch2 r3, [r2,#0++], drc0", "wdf drc0",
                    "str #129, r3", "str #130, r4", "ldad.bpcache r5, [r2,#1++], drc0",
                    "str #129, r5")
    ev = trace(lines, seeds={"r1": ("cmd_ta", 0)})
    assert texts(ev) == [
        "ld cmd_ta.te_aa, CMDTA+0x23c",                # glossary term, else the offset
        "W CR_TE_AA <- cmd_ta.te_aa",
        "W CR_TE_MTILE_1 <- CMDTA+0x23c",
        "ld CMDTA+0x240",                              # post-increment moved r2 by 2
        "W CR_TE_AA <- CMDTA+0x240",
    ]


def test_memory_stores_name_both_sides():
    lines = listing("ldad.bpcache r2, [r0,+#7], drc1", "stad.bpcache [r1,+#53], r2",
                    "stad.bpcache [r1,+#52], #0")
    ev = trace(lines, seeds={"r0": ("cmd_ta", 0), "r1": ("hw_render_details", 0)})
    assert texts(ev) == ["ld cmd_ta.frag_flags",
                         "st hw_render_details.frag_flags <- cmd_ta.frag_flags",
                         "st HWRENDERDETAILS+0x0d0 <- 0x0"]


def test_pointer_fields_of_kick3d_type_what_is_loaded_through_them():
    # cmd_ta dword 14 is the render details' address (kick3d.py, E159)
    lines = listing("ldad.bpcache r4, [r1,+#14], drc0", "ldad.bpcache r5, [r4,+#53], drc0")
    ev = trace(lines, seeds={"r1": ("cmd_ta", 0)})
    assert texts(ev) == ["ld cmd_ta.hw_render_details_dev_vaddr",
                         "ld hw_render_details.frag_flags"]


def test_a_loaded_pointer_prints_as_the_word_it_came_from():
    lines = listing("ldad.bpcache r4, [r1,+#14], drc0", "stad.bpcache [r14,+#1], r4")
    ev = trace(lines, seeds={"r1": ("cmd_ta", 0), "r14": ("hw_rt_data", 0)})
    assert texts(ev)[-1] == ("st hw_rt_data.hw_render_details_dev_vaddr <- "
                             "cmd_ta.hw_render_details_dev_vaddr")


def test_pointers_chain_through_several_structures():
    # context dword 6 -> PB descriptor, its dword 14 -> the first PB block, whose dword 3 ->
    # the next block (kick3d.py, E200, E201)
    lines = listing("ldad.bpcache r3, [r0,+#6], drc0", "ldad.bpcache r4, [r3,+#14], drc0",
                    "ldad.bpcache r5, [r4,+#3], drc0", "ldad.bpcache r6, [r5,+#0], drc0")
    ev = trace(lines, seeds={"r0": ("hw_render_context", 0)})
    assert texts(ev) == ["ld HWRENDERCONTEXT+0x018", "ld HWPBDESC+0x038",
                         "ld PB_BLOCK+0x00c", "ld PB_BLOCK+0x000"]


def test_a_nested_layout_is_named_by_its_own_structure():
    # the RT data set holds the RT data at byte 0x18: its dword 19 is RT data dword 13
    lines = listing("ldad.bpcache r2, [r1,+#19], drc0", "ldad.bpcache r3, [r1,+#7], drc0",
                    "ldad.bpcache r4, [r3,+#53], drc0")
    ev = trace(lines, seeds={"r1": ("hw_rt_data_set", 0)})
    assert texts(ev) == ["ld hw_rt_data.state", "ld hw_rt_data.hw_render_details_dev_vaddr",
                         "ld hw_render_details.frag_flags"]


def test_array_elements_are_named_after_their_array():
    # pds_bgnd: three words from CMDTA+0x008; src_syncs: eight 4-dword syncs from 0x16c
    lines = listing("ldad.bpcache.fetch3 r2, [r1,+#1], drc0",
                    "ldad.bpcache r5, [r6,+#96], drc0")
    ev = trace(lines, seeds={"r1": ("cmd_ta", 0), "r6": ("hw_render_details", 0)})
    assert texts(ev) == ["ld cmd_ta.pds_bgnd, cmd_ta.pds_bgnd[1], cmd_ta.pds_bgnd[2]",
                         "ld hw_render_details.src_syncs[1]+1"]


def test_every_dword_of_a_wide_field_is_named_after_it():
    # patches_3d: one field of two dwords at CMDTA+0x2a8; its second dword is +1, no index
    lines = listing("ldad.bpcache.fetch2 r2, [r1,#170++], drc0")
    ev = trace(lines, seeds={"r1": ("cmd_ta", 0)})
    assert texts(ev) == ["ld cmd_ta.patches_3d, cmd_ta.patches_3d+1"]


def test_a_structure_without_a_layout_is_traced_by_offset():
    # no layout: the loaded word is a plain field, and nothing is typed through it
    lines = listing("ldad.bpcache r4, [r1,+#14], drc0", "ldad.bpcache r5, [r4,+#53], drc0",
                    "str #128, r4")
    ev = trace(lines, seeds={"r1": ("TA3DCtl", 0)})
    assert "TA3DCtl" not in edmtrace.kick3d.STRUCTS
    assert texts(ev) == ["ld TA3DCtl+0x038", "W CR_VDM_START <- TA3DCtl+0x038"]


def test_unknown_structs_print_dword_indices():
    ev = trace(listing("ldad.bpcache r2, [sa0,+#25], drc0", "stad.bpcache [sa0,+#20], r2"),
               seeds={"sa0": ("TA3DCtl", 0)})
    assert texts(ev) == ["ld TA3DCtl+0x064", "st TA3DCtl+0x050 <- TA3DCtl+0x064"]


def test_seeds_accept_glossary_structure_prefixes():
    ev = trace(listing("ldad.bpcache r2, [r1,+#7], drc0"), seeds={"r1": ("CMDTA", 0)})
    assert texts(ev) == ["ld cmd_ta.frag_flags"]


def test_only_glossary_names_or_offsets_are_printed():
    # kick3d's names serve for typing; a word prints as its glossary term or STRUCT+0xOFF
    lines = listing("ldad.bpcache r4, [r1,+#14], drc0", "ldad.bpcache r5, [r4,+#52], drc0",
                    "ldad.bpcache r6, [r1,+#6], drc0", "str #128, r6")
    out = texts(trace(lines, seeds={"r1": ("cmd_ta", 0)}))
    assert out == ["ld cmd_ta.hw_render_details_dev_vaddr", "ld HWRENDERDETAILS+0x0d0",
                   "ld CMDTA+0x018", "W CR_VDM_START <- CMDTA+0x018"]


# --- the tables, from kick3d.py --------------------------------------------------------------

def test_every_kick3d_structure_has_a_prefix_or_lies_in_one_that_has():
    inside = {edmtrace.named_layout(f[1]) for fields in edmtrace.kick3d.STRUCTS.values()
              for f in fields if isinstance(f[1], list)}
    top = set(edmtrace.kick3d.STRUCTS) - set(edmtrace.PREFIX)
    assert top <= inside
    assert set(edmtrace.PREFIX) <= set(edmtrace.kick3d.STRUCTS)
    assert all(edmtrace.KICK3D[p] == s for s, p in edmtrace.PREFIX.items())


def test_the_transfer_structures_take_the_dataflows_prefixes():
    # edm_dataflow.py types the transfer context and its commands as HWTRANSFERCONTEXT and
    # TRANSFERCMD; the glossary locates the shared block's words at TRANSFERCMD_SHARED too
    assert edmtrace.PREFIX["transfer_cmd"] == "TRANSFERCMD"
    assert edmtrace.PREFIX["hw_transfer_context"] == "HWTRANSFERCONTEXT"
    assert edmtrace.PREFIX["SGXMKIF_TRANSFERCMD_SHARED"] == "TRANSFERCMD_SHARED"
    assert edmtrace.KICK3D["TRANSFERCMD"] == "transfer_cmd"


def test_prefixes_are_the_glossarys():
    # a structure's words are located in the glossary as PREFIX+0xOFF (the sgx545 column)
    rows = edmtrace.glossary.load(edmtrace.GLOSSARY)
    for struct, prefix in edmtrace.PREFIX.items():
        locs = {m.group(1) for r in rows if r["kind"] == "field"
                and r["name"].startswith(struct + ".")
                for m in [edmtrace._FIELD_LOC.search(r["sgx545"])] if m}
        assert locs <= {prefix}, (struct, locs)


def test_pointer_fields_are_kick3ds():
    assert edmtrace.POINTS_AT == {
        "hw_render_details_dev_vaddr": "hw_render_details",
        "hw_rt_data_dev_vaddr": "hw_rt_data",
        "hw_rt_data_set_dev_vaddr": "hw_rt_data_set",
        "hw_render_context_dev_vaddr": "hw_render_context",
        "hw_pb_desc_dev_vaddr": "hw_pb_desc",
        "dst_sync_list_dev_vaddr": "SGXMKIF_HWDEVICE_SYNC_LIST",
        "first_block_dev_vaddr": "pb_block",
        "next_block_dev_vaddr": "pb_block",
        # the TA/3D control block: its own address (E002) and the kicks' job words
        "ta3d_ctl_dev_vaddr": "ta3d_ctl",
        "dpm_slot0_rt_data_dev_vaddr": "hw_rt_data",
        "dpm_slot1_rt_data_dev_vaddr": "hw_rt_data",
        "cmd_ta_dev_vaddr": "cmd_ta",
        "hw_rt_data_ta": "hw_rt_data",
        "hw_render_details_ta": "hw_render_details",
        "hw_render_context_ta": "hw_render_context",
        "hw_rt_data_3d": "hw_rt_data",
        "hw_render_details_3d": "hw_render_details",
        "hw_pb_desc_ta": "hw_pb_desc",
        "hw_pb_desc_3d": "hw_pb_desc",
    }


def test_a_new_pointer_field_in_kick3d_types_without_a_table_change():
    structs = dict(edmtrace.kick3d.STRUCTS)
    structs["hw_rt_data"] = [("pad_0x00", 1), ("hw_pb_desc_dev_vaddr", 1),
                             ("bgobj_dev_vaddr", 1), ("parent_rt_data_dev_vaddr", 1),
                             ("ccb_ctl_dev_vaddr", 1)]
    got = edmtrace.points_at(structs)
    assert got["hw_pb_desc_dev_vaddr"] == "hw_pb_desc"        # the structure's own name
    assert "bgobj_dev_vaddr" not in got                       # no structure of that name
    assert "ccb_ctl_dev_vaddr" not in got                     # no layout of that name
    assert got["parent_rt_data_dev_vaddr"] == "hw_rt_data"    # its name without hw_


def test_other_writes_and_predicated_writes_forget_values():
    lines = listing("mov r3, #0x00000001", "shl r3, r3, #0x00000004", "str #128, r3",
                    "mov r4, #0x00000002", "p0 mov r4, #0x00000003", "str #128, r4")
    assert texts(trace(lines)) == ["W CR_VDM_START <- r3", "W CR_VDM_START <- r4"]


def test_calls_are_listed_with_labels():
    lines = listing("mov r23, pclink", "ba.savelink #0x00000004", "mov pclink, r23", "nop",
                    "lapc")
    ev = trace(lines, labels={4: "edm.helper"})
    assert texts(ev) == ["call 0x4 edm.helper"]


def test_range_limits_the_events():
    lines = listing("str #128, #1", "str #128, #2", "str #128, #3")
    assert [e.index for e in trace(lines, start=1, end=1)] == [1]


def test_format_has_the_index_and_text():
    ev = trace(listing("str #128, #1", start=0x95E))
    assert edmtrace.format_events(ev) == "0x095e  W CR_VDM_START <- 0x1"


# --- names from the glossary ----------------------------------------------------------------

def _row(group, name, kind, loc, tier):
    return dict(group=group, name=name, status="named", term="X", kind=kind, sgx545=loc,
                meaning="m", tier=tier, source="s", citation="c", licence="l", evidence="e")


def test_glossary_loader_takes_the_best_tier_term_per_location(tmp_path):
    rows = [_row("registers", "CR_ROGUE_NAME", "register", "0x0204", "3"),
            _row("registers", "CR_TE_AA", "register", "0x0204", "1"),
            _row("registers", "CR_TE_AA.FIELD", "bitfield", "0x0204[3:0]", "1"),
            _row("registers", "CR_GONE", "register", "- (no 2D core)", "1"),
            _row("structs", "cmd_ta.flags", "field", "CMDTA+0x004", "3"),
            _row("structs", "cmd_ta_shared.ctrl_flags", "field",
                 "CMDTA_SHARED+0x000 (CMDTA+0x058)", "1"),
            _row("structs", "misc_info_features.core_rev", "field",
                 "MISCINFO_FEATURES+0x00 (=MISC+0x04)", "1"),
            _row("structs", "GEOM_FLAGS.FIRST_KICK", "flag", "CMDTA+0x004 bit0 (0x1)", "3"),
            _row("structs", "CONTEXT_FLAGS.NEW", "flag",
                 "HWRENDERCONTEXT/HWTRANSFERCONTEXT+0x000 bit0 (0x1)", "ours"),
            _row("structs", "FRAG_FLAGS.NO_RENDER", "flag", "render flags bit0 (0x1)", "3"),
            _row("structs", "cmd_ta.frag_flags", "field", "CMDTA+0x01c", "3"),
            _row("structs", "pb_block.page_count", "field", "-", "ours"),
            _row("structs", "cmd_ta.not_in_kick3d", "field", "-", "ours")]
    edmtrace.glossary.write(rows, tmp_path)
    g = edmtrace.load_glossary(tmp_path)
    assert g.registers == {0x204: "CR_TE_AA"}
    assert g.fields[("CMDTA", 0x004)] == "cmd_ta.flags"
    assert g.fields[("CMDTA", 0x058)] == "cmd_ta_shared.ctrl_flags"
    assert g.fields[("CMDTA_SHARED", 0x000)] == "cmd_ta_shared.ctrl_flags"
    assert g.fields[("MISC", 0x004)] == "misc_info_features.core_rev"
    assert g.flags[("CMDTA", 0x004)] == {0: "GEOM_FLAGS.FIRST_KICK"}
    assert g.flags[("HWRENDERCONTEXT", 0x000)] == {0: "CONTEXT_FLAGS.NEW"}
    assert g.flags[("HWTRANSFERCONTEXT", 0x000)] == {0: "CONTEXT_FLAGS.NEW"}
    assert g.flags[("CMDTA", 0x01C)] == {0: "FRAG_FLAGS.NO_RENDER"}   # the frag_flags words
    # a row with no location is placed by kick3d's field of the same name
    assert g.fields[("PB_BLOCK", 0x000)] == "pb_block.page_count"
    assert "cmd_ta.not_in_kick3d" not in g.fields.values()


def test_the_repository_glossary_loads():
    g = edmtrace.load_glossary()
    assert g.registers[0x0AC8].startswith("CR_EVENT_KICK")
    assert g.fields[("HOST_CTL", 0x038)] == "host_ctl.assert_fail"


# --- the real ukernel (optional, gitignored) -----------------------------------------------

NEEDS_UKERNEL = pytest.mark.skipif(
    not UKERNEL.exists() or not USSE_DIS.exists(),
    reason="needs the cut ukernel ($RESGX545_UKERNEL) and a built usse-dis")


@pytest.fixture(scope="module")
def ukernel():
    assert UKERNEL.read_bytes()[:8] != b"SGX545FW", \
        "$RESGX545_UKERNEL is the .fw container; give the cut image (00_ukernel.bin)"
    out = subprocess.run([str(USSE_DIS), str(UKERNEL)], capture_output=True, text=True,
                         check=True).stdout.splitlines()
    return edmtrace.parse(out), edmtrace.load_glossary()


def typed_words(events) -> list[str]:
    """The structure words the events load or store by name or by STRUCT+0xOFF (a store
    through an untyped base, [rN+#k] or *WORD+k, is not typed)."""
    out = []
    for e in events:
        if e.text.startswith("ld "):
            out += e.text[3:].split(", ")
        elif e.text.startswith("st ") and not e.text.startswith(("st [", "st *")):
            out.append(e.text[3:].split(" <- ")[0])
    return out


@NEEDS_UKERNEL
def test_ta_handler_loads_the_ta_registers_from_the_command(ukernel):
    insns, g = ukernel
    ev = edmtrace.trace(insns, 0x95A, 0x985, names=g.registers, labels={}, fields=g.fields,
                        seeds={"r1": ("CMDTA", 0)})
    got = set(texts(ev))
    for reg, off in ((0x204, 0x238), (0x238, 0x250), (0xC90, 0x274)):
        # the TA registers' and words' terms arrive with the TA unit; until then, offsets
        name = g.registers.get(reg, f"{reg:#06x}")
        field = g.fields.get(("CMDTA", off), f"CMDTA+{off:#05x}")
        assert f"W {name} <- {field}" in got


@NEEDS_UKERNEL
def test_the_copy_routine_types_the_render_details_through_the_command(ukernel, monkeypatch):
    # 0x7b1 copies TA command words into the render details command dword 14 points at (E158);
    # seeded with the command alone, every word it stores lands in the render details
    insns, g = ukernel

    def run():
        return edmtrace.trace(insns, 0x7B1, 0x7FB, names=g.registers, labels={},
                              fields=g.fields, seeds={"r0": ("cmd_ta", 0)})
    ev = run()
    rd = {e.text.split(" <- ")[0][3:] for e in ev if e.text.startswith("st ")} - {"[sa0+#41]"}
    loc = edmtrace._loc
    assert {loc("hw_render_details", d, g.fields) for d in (53, 80, 70, 71, 76, 90, 91)} <= rd
    # the one store through a loaded word: the 3D patch pairs are memory writes (E158)
    assert [w for w in rd if w.startswith(("*", "["))] == [f"*{loc('cmd_ta', 170, g.fields)}"]
    assert f"st {loc('hw_render_details', 53, g.fields)} <- {loc('cmd_ta', 7, g.fields)}" \
        in texts(ev)
    # the landed tables matched no kick3d field: the same trace typed none of these stores
    monkeypatch.setattr(edmtrace, "POINTS_AT", {})
    before = typed_words(run())
    assert len(typed_words(ev)) - len(before) >= 20
    assert not [w for w in before if w.startswith(("hw_render_details", "HWRENDERDETAILS"))]


@NEEDS_UKERNEL
def test_the_labelled_routines_type_the_structures_the_control_block_points_at(
        ukernel, monkeypatch):
    # every labelled routine, from its label to the next, with sa0 the TA/3D control block
    # (E002): the job words the kicks record (E158, E159, E163, E200) type what the routines
    # read and write through them
    insns, g = ukernel
    labels = edmtrace.load_labels((HERE / "sgx545_labels.r2").read_text().splitlines())
    starts = sorted(labels)

    def outside():
        n = 0
        for a, b in zip(starts, starts[1:] + [insns[-1].index + 1]):
            ev = edmtrace.trace(insns, a, b - 1, names=g.registers, labels=labels,
                                fields=g.fields, seeds={"sa0": ("ta3d_ctl", 0)})
            n += sum(not w.startswith(("TA3D_CTL", "ta3d_ctl")) for w in typed_words(ev))
        return n
    after = outside()
    monkeypatch.setattr(edmtrace, "POINTS_AT", {})
    assert outside() == 0 and after >= 130


def test_cli_rejects_unknown_flags_and_a_trailing_seed(capsys):
    for extra in (["--bogus"], ["--seed"], ["--labels"], ["--seed", "r1=X", "--glossary"]):
        assert edmtrace.main(["none.txt", "0", "1", *extra]) == 2
    assert "unknown flag" in capsys.readouterr().err
