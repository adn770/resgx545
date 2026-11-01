# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The PDS probes of the movs tim counter and of the special source indices: which word of
movs tim loads the counter (probes/pds/timer.toml), and the special indices of each datapath,
swept with hand-encoded words (probes/pds/moves.toml)."""
from __future__ import annotations

import re

import pytest

import pds_tables as T
import probe

TIM = "pds-timer-tim-words"
PDS_TEMPLATES = probe.PROBES / "pds" / "templates"
# sweep -> (the source field's lo bit and width, the special values, results per program,
# how many of them the decoder names)
SWEEPS = {
    "pds-moves-index-mov32": (9, 8, range(128, 256), 16, 8),    # ir0, ir1, pc, tim, each .0 and .1
    "pds-moves-index-alu": (17, 7, range(64, 128), 16, 3),      # ir0, ir1, tim
    "pds-moves-index-mov16": (8, 9, range(256, 512), 32, 16),   # the eight above, .l and .h
    "pds-moves-index-mul": (16, 8, range(128, 256), 16, 6),     # ir0, ir1, tim, .l and .h
    "pds-moves-index-shl": (16, 8, range(128, 256), 16, 2),     # ir0, ir1
}
MNEMONIC = {"pds-moves-index-mov32": "mov32", "pds-moves-index-alu": "or",
            "pds-moves-index-mov16": "mov16", "pds-moves-index-mul": "mul",
            "pds-moves-index-shl": "shl"}
RAW = re.compile(r"^\.word /\*ds([01])\[(\d+)\]\*/ 0x([0-9a-f]{8})$")


@pytest.fixture(scope="module")
def sweeps():
    ps = probe.load(probe.PROBES / "pds" / "timer.toml") + \
        probe.load(probe.PROBES / "pds" / "moves.toml")
    return {p.name: p for p in ps if p.name == TIM or p.name in SWEEPS}


def raw_words(p) -> list:
    """Each case's hand-encoded words: (bank, register named by the comment, word)."""
    out = []
    for case in p.cases:
        lines = [RAW.match(ln) for ln in case[0].split("\n")]
        out.append([(int(m.group(1)), int(m.group(2)), int(m.group(3), 16)) for m in lines if m])
    return out


def dst_of(name: str, w: int) -> tuple:
    """The (bank, register) a word writes: mov32 bank w[7] and dst
    w[6:1]; mov16 bank w[7] and a half index w[6:0]; the ALU, mul and shl DST7 w[6:0]."""
    if name == "pds-moves-index-mov32":
        return w >> 7 & 1, w >> 1 & 63
    if name == "pds-moves-index-mov16":
        return w >> 7 & 1, (w & 0x7F) >> 1
    return w >> 6 & 1, w & 63


def test_sweeps_probes_exist(sweeps):
    assert set(sweeps) == {TIM, *SWEEPS}


def test_sweeps_cases_assemble(sweeps, tmp_path):
    for p in sweeps.values():
        files = probe.build(p, tmp_path, PDS_TEMPLATES)
        assert len(files) == len(p.cases), p.name
        for f, words in zip(files, raw_words(p)):
            data = f.read_bytes()
            assert data and len(data) % 4 == 0 and len(data) <= 256 * 8, f
            for *_, w in words:          # the hand-encoded words reach the binary as written
                assert w.to_bytes(4, "little") in data, (p.name, hex(w))


def test_tim_words_is_judged_and_its_hypotheses_differ(sweeps):
    p = sweeps[TIM]
    assert len(p.hypotheses) == 5
    vecs = [repr(v) for v in p.hypotheses.values()]
    assert len(set(vecs)) == len(vecs)
    for v in p.hypotheses.values():
        assert len(v) == len(p.cases)
    # the four "word k" readings differ in the first case (four nonzero words); the 25-bit
    # reading of word a differs from the 32-bit one in the cases with word a's top bits set
    words = list(p.hypotheses.values())[:4]
    for a in words:
        for b in words:
            assert a is b or a[0] != b[0]
    full, low25 = list(p.hypotheses.values())[0], list(p.hypotheses.values())[4]
    assert full[0] != low25[0] and full[-1] != low25[-1]


def test_tim_words_predicts_the_loaded_word(sweeps):
    p = sweeps[TIM]
    op, ins = p.cases[0][0], p.cases[0][1:]
    load = next(ln for ln in op.split("\n") if ln.startswith("movs tim"))
    words = [w.strip() for w in load.split(",")[1:]]
    regs = {f"ds0[{48 + k}]": ins[k] for k in range(8)} | \
        {f"ds1[{48 + k}]": ins[8 + k] for k in range(8)}
    assert len({regs[w] for w in words}) == 4         # four distinct values
    for k, (h, pred) in enumerate(p.hypotheses.items()):
        got = pred[0]
        # the eight reads (ds0[50..53], ds1[50..53]) all give word k (the fifth reading:
        # word a's bits 24-0); the rest is the input
        reads = got[2:6] + got[10:14]
        want = regs[words[k]] if k < 4 else regs[words[0]] & 0x01FFFFFF
        assert reads == [want] * 8, h
        assert got[:2] + got[6:10] + got[14:] == ins[:2] + ins[6:10] + ins[14:], h
    assert sum(ln.startswith("or ") and "tim" in ln for ln in op.split("\n")) == 8


def test_sweeps_are_recorded(sweeps):
    for name in SWEEPS:
        assert not sweeps[name].hypotheses, name


def test_raw_words_pass_through_in_temps():
    for line in [".word /*ds0[48]*/ 0x17010060", ".word /*ds1[55]*/ 0xc7840477"]:
        assert T.in_temps(line) == line


def test_sweeps_cover_every_index_once(sweeps):
    for name, (lo, bits, values, per, _) in SWEEPS.items():
        mask = ((1 << bits) - 1) << lo
        progs = raw_words(sweeps[name])
        assert [len(ws) for ws in progs] == [per] * (len(values) // per), name
        idx = [w >> lo & ((1 << bits) - 1) for ws in progs for *_, w in ws]
        assert idx == list(values), name
        for ws in progs:
            # only the index and the destination vary within a sweep
            dmask = 0xFF if name in ("pds-moves-index-mov32", "pds-moves-index-mov16") else 0x7F
            base = {w & ~(mask | dmask) & 0xFFFFFFFF for *_, w in ws}
            assert len(base) == 1, name


def test_sweep_destinations_are_the_temporaries_the_comments_name(sweeps):
    for name, (*_, per, _) in SWEEPS.items():
        for ws in raw_words(sweeps[name]):
            dsts = [dst_of(name, w) for *_, w in ws]
            assert dsts == [(b, r) for b, r, _ in ws], name
            assert all(48 <= r <= 55 for _, r in dsts), name
            # each result has its own temporary (mov16: its own half)
            halves = [w & 0xFF for *_, w in ws] if name == "pds-moves-index-mov16" else dsts
            assert len(set(halves)) == per, name


def test_sweep_named_indices_match_the_disassembler_and_assembler(sweeps, pds_dis, pds_asm):
    for name, (*_, named) in SWEEPS.items():
        words = [w for ws in raw_words(sweeps[name]) for *_, w in ws]
        texts = pds_dis(words)
        decoded = [(w, t) for w, t in zip(words, texts) if not t.startswith(".word")]
        assert len(decoded) == named, (name, decoded)
        for w, t in decoded:
            b, r = dst_of(name, w)
            assert t.startswith(f"{MNEMONIC[name]} ds{b}["), (name, t)
            assert pds_asm(t) == [w], (name, t)


def test_sweeps_writes_only_the_temporaries(sweeps):
    """As the probe tests' check, with the hand-encoded words' destinations decoded."""
    for name in SWEEPS:
        for case in sweeps[name].cases:
            for ln in case[0].split("\n"):
                m = re.match(r"^(mov32|mov16|mul|or|shl) ds([01])\[(\d+)\]", ln)
                if m:
                    n = int(m.group(3))
                    assert (n >> 1 if m.group(1) == "mov16" else n) >= 48, ln
