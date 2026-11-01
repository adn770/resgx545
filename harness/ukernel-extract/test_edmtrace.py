# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Tests for edmtrace.py — a linear value tracer over usse-dis listings of the EDM.

Synthetic listings only: the encodings are zeros and the instructions are text we wrote,
in the format usse-dis prints. One check runs on the gitignored ukernel when it is present."""
import pathlib
import shutil
import subprocess

import pytest

import os

import edmtrace

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
UKERNEL = pathlib.Path(os.environ.get("RESGX545_UKERNEL", "/nonexistent"))
USSE_DIS = ROOT / "tools" / "usse-dis" / "usse-dis"

# Register and field names as the glossary gives them (our terms; not every offset has one).
NAMES = {0x204: "CR_TE_AA", 0x208: "CR_TE_MTILE_1", 0x200: "CR_VDM_START",
         0x12C: "CR_EVENT_STATUS"}
FIELDS = {("CMDTA", 0x238): "cmd_ta.te_aa", ("CMDTA", 0x01C): "cmd_ta.frag_flags",
          ("HWRENDERDETAILS", 0x0D4): "hw_render_details.frag_flags"}


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
    ev = trace(lines, seeds={"r1": ("SGXMKIF_CMDTA", 0)})
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
    ev = trace(lines, seeds={"r0": ("SGXMKIF_CMDTA", 0), "r1": ("hw_render_details", 0)})
    assert texts(ev) == ["ld cmd_ta.frag_flags",
                         "st hw_render_details.frag_flags <- cmd_ta.frag_flags",
                         "st HWRENDERDETAILS+0x0d0 <- 0x0"]


def test_pointer_fields_can_be_followed_with_typed_seeds(monkeypatch):
    # a layout whose dword 14 is a render-details pointer (a stand-in: the TA command has no
    # layout in kick3d.py) types what is loaded through it
    monkeypatch.setitem(edmtrace.kick3d.STRUCTS, "SGXMKIF_CMDTA",
                        [("words", 1, 14), ("hw_render_details_dev_addr", 1)])
    lines = listing("ldad.bpcache r4, [r1,+#14], drc0", "ldad.bpcache r5, [r4,+#53], drc0")
    ev = trace(lines, seeds={"r1": ("SGXMKIF_CMDTA", 0)})
    assert texts(ev)[1] == "ld hw_render_details.frag_flags"


def test_a_structure_without_a_layout_is_traced_by_offset():
    # no layout: the loaded word is a plain field, and nothing is typed through it
    lines = listing("ldad.bpcache r4, [r1,+#14], drc0", "ldad.bpcache r5, [r4,+#53], drc0",
                    "str #128, r4")
    ev = trace(lines, seeds={"r1": ("SGXMKIF_CMDTA", 0)})
    assert "SGXMKIF_CMDTA" not in edmtrace.kick3d.STRUCTS
    assert texts(ev)[0] == "ld CMDTA+0x038"
    assert texts(ev)[-1] == "W CR_VDM_START <- CMDTA+0x038"
    assert not any("hw_render_details" in x for x in texts(ev))


def test_unknown_structs_print_dword_indices():
    ev = trace(listing("ldad.bpcache r2, [sa0,+#25], drc0", "stad.bpcache [sa0,+#20], r2"),
               seeds={"sa0": ("TA3DCtl", 0)})
    assert texts(ev) == ["ld TA3DCtl+0x064", "st TA3DCtl+0x050 <- TA3DCtl+0x064"]


def test_seeds_accept_glossary_structure_prefixes():
    ev = trace(listing("ldad.bpcache r2, [r1,+#7], drc0"), seeds={"r1": ("CMDTA", 0)})
    assert texts(ev) == ["ld cmd_ta.frag_flags"]


def test_no_kick3d_names_are_printed():
    lines = listing("ldad.bpcache r4, [r1,+#14], drc0", "ldad.bpcache r5, [r4,+#52], drc0",
                    "ldad.bpcache r6, [r1,+#3], drc0", "str #128, r6")
    out = " ".join(texts(trace(lines, seeds={"r1": ("SGXMKIF_CMDTA", 0)})))
    leaves = {path.rsplit(".", 1)[-1] for fields in edmtrace.kick3d.STRUCTS.values()
              for path, *_ in edmtrace.kick3d._layout(fields)}
    assert "SGXMKIF" not in out and not any(leaf in out.split() for leaf in leaves)


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
            _row("structs", "cmd_ta.frag_flags", "field", "CMDTA+0x01c", "3")]
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


def test_the_repository_glossary_loads():
    g = edmtrace.load_glossary()
    assert g.registers[0x0AC8].startswith("CR_EVENT_KICK")
    assert g.fields[("HOST_CTL", 0x038)] == "host_ctl.assert_fail"


# --- the real ukernel (optional, gitignored) -----------------------------------------------

@pytest.mark.skipif(not UKERNEL.exists() or not USSE_DIS.exists(),
                    reason="needs the cut ukernel ($RESGX545_UKERNEL) and a built usse-dis")
def test_ta_handler_loads_the_ta_registers_from_the_command():
    assert UKERNEL.read_bytes()[:8] != b"SGX545FW", \
        "$RESGX545_UKERNEL is the .fw container; give the cut image (00_ukernel.bin)"
    out = subprocess.run([str(USSE_DIS), str(UKERNEL)], capture_output=True, text=True,
                         check=True).stdout.splitlines()
    insns = edmtrace.parse(out)
    g = edmtrace.load_glossary()
    ev = edmtrace.trace(insns, 0x95A, 0x985, names=g.registers, labels={}, fields=g.fields,
                        seeds={"r1": ("CMDTA", 0)})
    got = set(texts(ev))
    for reg, off in ((0x204, 0x238), (0x238, 0x250), (0xC90, 0x274)):
        # the TA registers' and words' terms arrive with the TA unit; until then, offsets
        name = g.registers.get(reg, f"{reg:#06x}")
        field = g.fields.get(("CMDTA", off), f"CMDTA+{off:#05x}")
        assert f"W {name} <- {field}" in got


def test_cli_rejects_unknown_flags_and_a_trailing_seed(capsys):
    for extra in (["--bogus"], ["--seed"], ["--labels"], ["--seed", "r1=X", "--glossary"]):
        assert edmtrace.main(["none.txt", "0", "1", *extra]) == 2
    assert "unknown flag" in capsys.readouterr().err
