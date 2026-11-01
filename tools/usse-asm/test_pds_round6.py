# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The PDS probes of the flagged special moves (probes/pds/moves.toml): what the low bit of
the mov16/mov32 special index (the "flag": special k is selector k >> 1, flag k & 1) does,
what the count at selector 2 is, and how mov64 sees the specials."""
from __future__ import annotations

import re

import pytest

import pds_tables as T
import probe

WRITE, FLAGS, PC, SWEEP64 = ("pds-moves-mov-flag-write", "pds-moves-mov-flag-flags",
                             "pds-moves-mov-pc", "pds-moves-index-mov64")
SIDE = "pds-moves-mov-flag-side"
COND = "pds-moves-mov-flag-cond"
PIPES = "pds-moves-mov-flag-pipes"
SPARE32, SPAREM = "pds-moves-mov32-spare", "pds-alu-alum-spare"
SPARE_BITS = [0, 8, *range(17, 24)]
PDS_TEMPLATES = probe.PROBES / "pds" / "templates"
RAW = re.compile(r"^(?:\w+:\s*)?\.word /\*ds([01])\[(\d+)\]\*/ 0x([0-9a-f]{8})$")
H = T.MARK


@pytest.fixture(scope="module")
def moves():
    ps = probe.load(probe.PROBES / "pds" / "moves.toml") + \
        probe.load(probe.PROBES / "pds" / "alu.toml")
    return {p.name: p for p in ps
            if p.name in (WRITE, FLAGS, PC, SWEEP64, SIDE, COND, PIPES, SPARE32, SPAREM)}


def raw_words(op: str) -> list:
    """OP's hand-encoded words: (line index, bank, register named by the comment, word)."""
    out = []
    for i, ln in enumerate(op.split("\n")):
        m = RAW.match(ln)
        if m:
            out.append((i, int(m.group(1)), int(m.group(2)), int(m.group(3), 16)))
    return out


def field(w: int, lo: int, bits: int) -> int:
    return w >> lo & ((1 << bits) - 1)


def test_moves_probes_exist(moves):
    assert set(moves) == {WRITE, FLAGS, PC, SWEEP64, SIDE, COND, PIPES, SPARE32, SPAREM}


def test_mov32_spare_bits_probe(moves):
    """mov32's unused bits (0, 8, 23:17) as its pipe select: plain and with the bit, ir0,
    pc, tim; mov16 ir0.l with the bit where mov16 leaves it unused; flagged mov16 last."""
    p = moves[SPARE32]
    assert not p.hypotheses and len(p.cases) == len(SPARE_BITS)
    assert p.labels == [f"bit {b}" for b in SPARE_BITS]
    for case, bit in zip(p.cases, SPARE_BITS):
        op, ins = case[0], case[1:]
        assert all(v >> 16 == 0x5EED for v in ins) and len(set(ins)) == 16
        words = raw_words(op)
        assert [(b, r) for _, b, r, _ in words] == [(0, 48 + k) for k in range(8)]
        ws = [w for *_, w in words]
        for k, fld in enumerate((128, 132, 134)):
            assert ws[2 * k] == T.mov32_raw(fld, 0, 48 + 2 * k)
            assert ws[2 * k + 1] == T.mov32_raw(fld, 0, 49 + 2 * k) | 1 << bit
        m16 = T.mov16_raw(256, 0, 54, hi=False)
        assert ws[6] == (m16 | 1 << bit if bit >= 17 else m16)
        assert ws[7] == T.mov16_raw(258, 0, 55, hi=False)


def test_alum_spare_bits_probe(moves):
    """alum with one unused bit set, then plain reads; alum unsigned restores the mode."""
    p = moves[SPAREM]
    assert not p.hypotheses and len(p.cases) == 24
    assert p.labels == ["alum unsigned (control)"] + [f"alum bit {b}" for b in range(1, 24)]
    for k, case in enumerate(p.cases):
        lines = case[0].split("\n")
        word = 0xBF000000 | (1 << k if k else 0)
        assert lines[0] == (f".word 0x{word:08x}" if k else "alum unsigned")
        assert lines[-1] == "alum unsigned"
        reads = raw_words(case[0])
        assert [(b, r) for _, b, r, _ in reads] == [(0, 48 + j) for j in range(5)]
        assert [w for *_, w in reads] == [
            T.mov32_raw(128, 0, 48), T.mov32_raw(132, 0, 49), T.mov32_raw(134, 0, 50),
            T.mov16_raw(256, 0, 51, hi=False), T.mov16_raw(264, 0, 52, hi=False)]
        assert lines[6:8] == ["or ds0[53], ir0, ds1[1]", "add ds0[54], ds0[54], ds1[54]"]


def test_pipes_probe_samples_in_a_long_loop_per_tile(moves):
    """The flag as the other PDS pipe's register (the SGX545 has two PDS pipes): each tile's
    secondary ORs 200 samples of a move into ds0[48], which sa_pixel.s paints as the pixel,
    so a nonzero sample in any tile shows."""
    p = moves[PIPES]
    assert p.use == "sa_pixel.s" and p.pixels and not p.hypotheses
    fields = [266, 258, 270, None, 264]          # flagged pc.l, ir0.l, tim.l; ir0; pc.l
    assert len(p.cases) == len(fields)
    for case, fld in zip(p.cases, fields):
        op, ins = case[0], case[1:]
        lines = op.split("\n")
        if fld is None:
            assert lines == ["mov32 ds0[48], ir0.0"]
            continue
        assert ins[0] == 0 and ins[1] == 200 and ins[15] == 1
        assert lines[0] == "loop: mov32 ds1[50], ds1[1]"
        (i, b, r, w), = raw_words(op)
        assert (i, b, r) == (1, 1, 50)
        assert field(w, 27, 5) == 1 and field(w, 8, 9) == fld
        assert field(w, 7, 1) == 1 and field(w, 0, 7) == 100          # ds1[50]'s low half
        assert lines[2:] == ["or ds0[48], ds0[48], ds1[50]", "sub ds0[49], ds0[49], ds1[55]",
                             "tstz p0, ds0[49]", "(p0) bra out", "bra loop", "out: nop"]


# pds-mov-flag-cond: the setup lines of each case, and its (A, I)
COND_SETUPS = [
    ([], (0, 0)),
    (["sub ds0[48], ds0[48], ds1[48]"], (5, 5)),
    (["add ds0[48], ds0[48], ds1[48]"], (T.M, 1)),
    (["sub ds0[48], ds0[48], ds1[48]"], (0, 1)),
    (["alum signed", "sub ds0[48], ds0[48], ds1[48]"], (3, 5)),
    ([f"tstz p{k}, ds0[48]" for k in range(3)], (0, 0)),
    ([f"tstz p{k}, ds0[48]" for k in range(3)], (5, 0)),
]
# the moves after it: (destination bank, register, mnemonic, source field, high half?)
COND_MOVES = [(0, 49, "mov16", 258, False), (0, 50, "mov16", 256, False),
              (0, 51, "mov16", 270, False), (0, 52, "mov16", 271, True),
              (0, 53, "mov16", 266, False), (0, 54, "mov16", 264, False),
              (0, 55, "mov32", 129, None), (1, 49, "mov32", 135, None)]
COND_MARKS = ["(aluz) mov32 ds1[50], ds1[55]", "(alun) mov32 ds1[51], ds1[55]",
              "(p0) mov32 ds1[52], ds1[55]", "(p1) mov32 ds1[53], ds1[55]",
              "(p2) mov32 ds1[54], ds1[55]"]


def test_cond_probe_sets_each_state_then_keeps_every_moved_value(moves):
    p = moves[COND]
    assert not p.hypotheses and len(p.cases) == len(COND_SETUPS)
    for case, (setup, (a, i)) in zip(p.cases, COND_SETUPS):
        op, ins = case[0], case[1:]
        lines = op.split("\n")
        n = len(setup)
        assert lines[:n] == setup
        assert lines[n + len(COND_MOVES):] == COND_MARKS
        assert (ins[0], ins[8]) == (a, i) and ins[15] == H
        # every result temporary is marked with distinct halves (a half write keeps one)
        assert all(ins[k] >> 16 == 0x5EED for k in [*range(1, 8), *range(9, 15)])
        words = raw_words(op)
        assert [li for li, *_ in words] == list(range(n, n + len(COND_MOVES)))
        for (_, b, r, w), (wb, wr, mn, fld, hi) in zip(words, COND_MOVES):
            assert (b, r) == (wb, wr)
            if mn == "mov16":
                assert field(w, 27, 5) == 1 and field(w, 8, 9) == fld
                assert field(w, 7, 1) == b and field(w, 0, 7) == 2 * r + hi
            else:
                assert field(w, 27, 5) == 2 and field(w, 9, 8) == fld
                assert field(w, 7, 1) == b and field(w, 1, 6) == r


def test_side_effect_probe_rereads_each_register_after_its_flagged_reads(moves):
    """An auto-decrement (or any change) of the register a flagged move reads would show
    as the plain reads before and after the flagged ones differing."""
    p = moves[SIDE]
    assert not p.hypotheses and len(p.cases) == 2
    for case, mn in zip(p.cases, ("mov32", "mov16")):
        words = raw_words(case[0])
        assert [(b, r) for _, b, r, _ in words] == [(b, 48 + k) for b in (0, 1)
                                                   for k in range(8)]
        assert sorted(i for i, *_ in words) == list(range(16))   # nothing else in between
        got = []
        for _, b, r, w in words:
            if field(w, 27, 5) == 2:
                got.append(("mov32", field(w, 9, 8)))
            else:
                assert field(w, 27, 5) == 1 and field(w, 0, 7) == 2 * r     # the low half
                got.append(("mov16", field(w, 8, 9)))
        # per register (ir0, ir1, tim): plain, flagged, flagged, plain; then tim plain x4
        flagged = {"mov32": (129, 131, 135), "mov16": (258, 262, 270)}[mn]
        plain = (128, 130, 134)
        want = []
        for pl, fl in zip(plain, flagged):
            want += [("mov32", pl), (mn, fl), (mn, fl), ("mov32", pl)]
        want += [("mov32", 134)] * 4
        assert got == want, mn


def test_moves_cases_assemble(moves, tmp_path):
    for p in moves.values():
        files = probe.build(p, tmp_path, PDS_TEMPLATES)
        assert len(files) == len(p.cases), p.name
        for f, case in zip(files, p.cases):
            data = f.read_bytes()
            for *_, w in raw_words(case[0]):
                assert w.to_bytes(4, "little") in data, (p.name, hex(w))


# The encoders: mov32 special field 128 + 2 * selector + flag (w[16:9]); mov16 256 + 4 *
# selector + 2 * flag + half (w[16:8]), its destination a half index (w[6:0]); mov64 source
# w[16:10], its destination a pair (w[6:2]).
def test_encoders_match_the_assembler(pds_asm):
    assert T.mov32_raw(128, 1, 48) == pds_asm("mov32 ds1[48], ir0.0")[0]
    assert T.mov32_raw(130, 0, 51) == pds_asm("mov32 ds0[51], ir1.0")[0]
    assert T.mov16_raw(256, 0, 48, hi=False) == pds_asm("mov16 ds0[96], ir0.0.l")[0]
    assert T.mov16_raw(263, 1, 55, hi=True) == pds_asm("mov16 ds1[111], ir1.1.h")[0]
    assert T.mov64_raw(64, 0, 48) == pds_asm("mov64 ds0[48], mr01")[0]
    assert T.mov64_raw(65, 1, 54) == pds_asm("mov64 ds1[54], mr23")[0]
    assert T.mov32_field(2, 1) == 133 and T.mov16_field(3, 1, hi=True) == 271


def test_flag_write_writes_each_temporary_once_with_the_fields_it_names(moves):
    p = moves[WRITE]
    assert not p.hypotheses and len(p.cases) == 1
    op, ins = p.cases[0][0], p.cases[0][1:]
    # the marks have distinct halves, so a half write keeps the other half's 0x5eed
    assert all(v >> 16 == 0x5EED for v in ins) and len(set(ins)) == 16
    words = raw_words(op)
    dsts = [(b, r) for _, b, r, _ in words]
    assert sorted(dsts) == [(b, 48 + k) for b in (0, 1) for k in range(8)
                            if (b, 48 + k) != (0, 55)]      # ds0[55]: the ALU's tim
    assert "or ds0[55], tim, ds1[1]" in op.split("\n")[0]   # read just before the mov16s
    mov16 = {r: w for _, b, r, w in words if b == 0}
    mov32 = {r: w for _, b, r, w in words if b == 1}
    assert {r: field(w, 8, 9) for r, w in mov16.items()} == \
        {48: 268, 49: 269, 50: 270, 51: 271, 52: 258, 53: 264, 54: 266}
    assert {r: field(w, 0, 7) & 1 for r, w in mov16.items()} == \
        {48: 0, 49: 1, 50: 0, 51: 1, 52: 0, 53: 0, 54: 0}   # .l low half, .h high half
    assert all(field(w, 27, 5) == 1 and field(w, 0, 7) >> 1 == r for r, w in mov16.items())
    assert {r: field(w, 9, 8) for r, w in mov32.items()} == \
        {48: 128, 49: 129, 50: 134, 51: 135, 52: 132, 53: 133, 54: 130, 55: 131}
    assert all(field(w, 27, 5) == 2 and field(w, 1, 6) == r for r, w in mov32.items())


# pds-mov-flag-flags: (setup, the move's field, hypothesis -> (aluz, alun, carry) after it)
FLAG_CASES = [
    ("sub 5 - 5: aluz", "mov32", 129, {"keep": (1, 0, 0), "set": (0, 0, 0), "setc": (0, 0, 0)}),
    ("sub 5 - 3", "mov32", 131, {"keep": (0, 0, 0), "set": (1, 0, 0), "setc": (1, 0, 0)}),
    ("sub 5 - 3", "mov16", 258, {"keep": (0, 0, 0), "set": (1, 0, 0), "setc": (1, 0, 0)}),
    ("sub 5 - 5: aluz", "mov32", 128, {"keep": (1, 0, 0), "set": (1, 0, 0), "setc": (1, 0, 0)}),
    ("add -1 + 1: aluz, carry", "mov32", 129,
     {"keep": (1, 0, 1), "set": (0, 0, 1), "setc": (0, 0, 0)}),
    ("signed sub 3 - 5: alun", "mov32", 131,
     {"keep": (0, 1, None), "set": (1, 0, None), "setc": (1, 0, None)}),
]


def test_flag_flags_cases_and_predictions(moves):
    p = moves[FLAGS]
    assert len(p.cases) == len(FLAG_CASES)
    hyps = list(p.hypotheses.values())
    assert len(hyps) == 3
    for c, (case, (_, mn, fld, want)) in enumerate(zip(p.cases, FLAG_CASES)):
        op, ins = case[0], case[1:]
        (_, b, r, w), = raw_words(op)
        assert (b, r) == (0, 48)
        if mn == "mov32":
            assert field(w, 27, 5) == 2 and field(w, 9, 8) == fld
        else:
            assert field(w, 27, 5) == 1 and field(w, 8, 9) == fld
        lines = op.split("\n")
        assert lines[-1] == "mov32 ds0[48], ds1[1]"        # the moved value cleared
        assert ("adc ds0[51], ds0[51], ds1[51]" in lines) == (want["keep"][2] is not None)
        for h, key in zip(hyps, ("keep", "set", "setc")):
            z, n, carry = want[key]
            got = h[c]
            assert got[0] == 0
            assert got[1] == (H if z else ins[1]), (c, key)
            assert got[2] == (H if n else ins[2]), (c, key)
            assert got[3] == (ins[3] + ins[11] + (carry or 0)) & T.M, (c, key)
            assert got[4:] == ins[4:], (c, key)
    assert len({repr(h) for h in hyps}) == 3


def template_prefix() -> int:
    """The instructions pds_dump.s runs before OP."""
    src = (PDS_TEMPLATES / "pds_dump.s").read_text()
    head = src[:src.index("{OP}")]
    return sum(1 for ln in head.split("\n")
               if ln.strip() and not ln.strip().startswith((";", ".word")))


def test_pc_probe_predicts_the_reading_instructions_index_plus_3(moves):
    p = moves[PC]
    assert template_prefix() == 16
    (hyp,) = p.hypotheses.values()
    loops = 0
    for case, pred in zip(p.cases, hyp):
        op, ins = case[0], case[1:]
        words = raw_words(op)
        assert words and all(field(w, 27, 5) == 2 and field(w, 9, 8) in (132, 133)
                             for *_, w in words)
        if op.startswith("loop:"):
            loops += 1
            (i, b, r, _), = words
            # read twice in the loop: once kept in ds0[50], once in ds0[49]
            assert (b, r) == (0, 49) and pred[1] == pred[2] == 16 + i + 3 and pred[0] == 0
            continue
        for i, b, r, _ in words:
            assert pred[8 * b + r - 48] == 16 + i + 3, (op, r)
        untouched = set(range(16)) - {8 * b + r - 48 for _, b, r, _ in words}
        for k in untouched:         # (the muls multiply zero inputs: they keep them too)
            assert pred[k] == ins[k], (op, k)
    assert loops == 1
    assert len(p.cases) == 4


def test_mov64_sweep_covers_the_special_sources_once(moves):
    p = moves[SWEEP64]
    assert not p.hypotheses
    progs = [raw_words(c[0]) for c in p.cases]
    assert [len(ws) for ws in progs] == [8] * 8
    assert [field(w, 10, 7) for ws in progs for *_, w in ws] == list(range(64, 128))
    for ws in progs:
        # pairs ds0[48], [50], [52], [54], then ds1's, as the comments name
        assert [(b, r) for _, b, r, _ in ws] == [(b, 48 + 2 * k) for b in (0, 1)
                                                 for k in range(4)]
        assert all(field(w, 27, 5) == 3 and field(w, 7, 1) == b and field(w, 2, 5) * 2 == r
                   for _, b, r, w in ws)


def test_mov64_sweep_names_only_mr01_and_mr23(moves, pds_dis):
    words = [w for c in moves[SWEEP64].cases for *_, w in raw_words(c[0])]
    named = [t for t in pds_dis(words) if not t.startswith(".word")]
    assert [t.split(", ")[1] for t in named] == ["mr01", "mr23"]
