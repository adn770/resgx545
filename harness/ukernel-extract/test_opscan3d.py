# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""opscan3d.py: which instruction forms still open the closed compiler uses, over every USSE
program the captures hold; names and counts only."""
import json

import opscan3d as op

FORMS = """0\tFF\t00\tFF\t{0}mov{1}{2} {3}, #{4}
8\tFF\t01\tFF\tphas{0} #{1}, #{2}, {3}
145\tFF\t02\tFF\t{0}ldr {1}, {2}
200\tFF\t03\tFF\t{0}smoa {1}
"""


def test_a_form_is_named_by_its_first_word():
    assert op.mnemonic("{0}mov{1}{2} {3}, #{4}") == "mov"
    assert op.mnemonic("mov pclink, {0}") == "mov"
    assert op.mnemonic("phas{0} #{1}") == "phas"
    assert op.mnemonic("{0}{1} #{2}") == "?"


def test_forms_reads_the_disassemblers_listing():
    assert op.forms(FORMS) == {0: "mov", 8: "phas", 145: "ldr", 200: "smoa"}


def test_programs_are_grouped_by_path_and_deduplicated():
    words = {"k0.eor.usse0.i0": 1, "k0.eor.usse0.i1": 2, "k1.eor.usse0.i0": 1,
             "k1.eor.usse0.i1": 2, "k0.eot.i0": 3, "k0.vdm.b0.pds.usse0.i0": 4,
             "k0.cmd.size": 0x2c0}
    progs = op.programs(words)
    assert progs == {(1, 2): ["k0.eor.usse0", "k1.eor.usse0"], (3,): ["k0.eot"],
                     (4,): ["k0.vdm.b0.pds.usse0"]}


def test_open_forms_are_those_no_vector_passes_and_the_named_ones(tmp_path):
    cov = {"forms": [{"form": 0, "op": "mov", "probes": {"p": [3, 0, 0]}},
                     {"form": 8, "op": "phas", "probes": {}},
                     {"form": 145, "op": "ldr", "probes": {"q": [0, 2, 0]}},
                     {"form": 200, "op": "smoa", "probes": {"r": [1, 0, 0]}}]}
    p = tmp_path / "cov.json"
    p.write_text(json.dumps(cov))
    names = op.forms(FORMS)
    assert op.open_forms(p, names) == {8: "no passing vector", 145: "no passing vector",
                                       200: "no semantics in the simulator"}


def test_scan_counts_programs_and_runs_without_words():
    names = op.forms(FORMS)
    which = {1: 0, 2: 145, 3: 8, 4: 0, 5: 200}

    def dis(words):
        return [which[w] for w in words]
    runs = {"t/a": {"k0.eor.usse0.i0": 1, "k0.eor.usse0.i1": 2},
            "t/b": {"k0.eor.usse0.i0": 1, "k0.eor.usse0.i1": 2, "k0.eot.i0": 3},
            "t/c": {"k0.eot.i0": 4}}
    rep = op.scan(runs, dis, {8: "x", 145: "y", 200: "z"})
    assert rep[145] == {"programs": 1, "uses": 1, "runs": ["t/a", "t/b"]}
    assert rep[8] == {"programs": 1, "uses": 1, "runs": ["t/b"]}
    assert 200 not in rep
    text = op.report(rep, names, {8: "x", 145: "y", 200: "z"}, total_programs=3)
    assert "ldr" in text and "smoa" in text and "0x" not in text


def test_the_which_column_is_parsed():
    line = "     0: 0xFA4C070000000000\tphas.end #0, #0, pixel, end, parallel\t#8"
    assert op.which_of([line]) == [8]


def test_a_form_named_by_a_field_takes_the_coverage_op(tmp_path):
    p = tmp_path / "cov.json"
    p.write_text(json.dumps({"forms": [{"form": 64, "op": "dual", "probes": {}},
                                       {"form": 0, "op": "mov_imm", "probes": {}}]}))
    assert op.fill_names({64: "?", 0: "mov"}, p) == {64: "dual", 0: "mov"}


GUARDED = ["phas #7, #0, pixel, vcull, parallel", "nop.nosched",
           "and.skipinv.testtanz.chan0 !r0, p0, #0x00000000, #0",
           "p0 ldad.skipinv.fetch4 pa0, [pa0,+#0], drc0", "wdf drc0",
           "mov.skipinv.repeat4 o0, pa0"]


def test_a_program_opens_with_the_never_taken_load_and_its_wait():
    assert op.guarded(GUARDED)
    assert op.guarded(GUARDED[2:])                          # no phas or nop before it
    assert not op.guarded(GUARDED[:2] + GUARDED[3:])        # no and
    assert not op.guarded(GUARDED[:4] + GUARDED[5:])        # no wdf
    one = GUARDED[:2] + ["and.skipinv.testtanz.chan0 !r0, p0, #0x00000001, #0"] + GUARDED[3:]
    assert not op.guarded(one)                              # p0 could be true
    other = GUARDED[:3] + ["p1 ldad.skipinv.fetch4 pa0, [pa0,+#0], drc0"] + GUARDED[4:]
    assert not op.guarded(other)                            # another predicate
    late = GUARDED[:2] + ["mov.skipinv o0, pa0"] + GUARDED[2:]
    assert not op.guarded(late)                             # not at the start


def test_a_program_is_kinded_by_the_path_that_reaches_it():
    assert op.kind("k0.vdm.b1.vtx.usse0") == "vertex"
    assert op.kind("k0.vdm.b0.pds.usse0") == "state copy"
    assert op.kind("k0.vdm.b0.mte.sec.usse0") == "secondary"
    assert op.kind("k1.spec.sec.usse0") == "secondary"
    assert op.kind("k0.vdm.b2.mte.pri.usse1") == "primary"
    assert op.kind("k0.eot") == "end of tile"
    assert op.kind("k0.eor.usse2") == "end of render"


def test_guards_counts_programs_by_kind_without_words():
    text = {1: GUARDED, 2: GUARDED[:2] + GUARDED[5:], 3: GUARDED[2:]}
    runs = {"t/a": {"k0.vdm.b1.vtx.usse0.i0": 1, "k0.vdm.b0.mte.sec.usse0.i0": 2},
            "t/b": {"k0.vdm.b1.vtx.usse0.i0": 1, "k0.vdm.b3.vtx.usse0.i0": 3,
                    "k0.vdm.b0.pds.usse0.i0": 2}}
    rep = op.guards(runs, lambda ins: text[ins[0]])
    assert rep == {"vertex": {"programs": 2, "guarded": 2, "runs": 2},
                   "secondary": {"programs": 1, "guarded": 0, "runs": 1},
                   "state copy": {"programs": 1, "guarded": 0, "runs": 1}}
    out = op.guard_report(rep)
    assert "vertex: 2 of 2 programs" in out and "0x" not in out
