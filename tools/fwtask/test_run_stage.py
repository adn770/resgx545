# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The host side of the laptop runs: the job list of the matrix, the evaluation of a record, the
freeze of the predictions (no str before it), the stop rules."""
import pathlib
import sys

import pytest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import classify  # noqa: E402
import classify1129  # noqa: E402
import classify_b2  # noqa: E402
import layout as L  # noqa: E402
import run_stage  # noqa: E402


@pytest.fixture
def frozen(tmp_path, monkeypatch):
    # the 9b evaluation of phase 11.29 reads the 11.29 table
    p = tmp_path / "predictions.toml"
    p.write_text(classify1129.render())
    f = tmp_path / "predictions.sha256"
    f.write_text(classify1129.sha256(p) + "\n")
    monkeypatch.setattr(run_stage, "classify", classify1129)
    monkeypatch.setattr(run_stage, "PRED", p)
    monkeypatch.setattr(run_stage, "FROZEN", f)
    return p, f


def test_jobs_cover_every_case_pair_and_repeat_in_a_fixed_shuffled_order():
    j1 = run_stage.jobs_9b("R1", sorted(L.X9B), 2, 3, 5)
    j2 = run_stage.jobs_9b("R1", sorted(L.X9B), 2, 3, 5)
    assert j1 == j2
    assert len(j1) == len(L.X9B) * 2 * 3
    assert j1 != sorted(j1, key=lambda j: (j["rep"], j["pair"], j["n"]))       # shuffled
    assert run_stage.jobs_9b("R1", sorted(L.X9B), 2, 3, 6) != j1               # by the seed


def test_second_value_pair_swaps_b_and_c_and_never_equals_the_start_value():
    """B ^ mask equals A for both registers (A and B are complements), so a second pair made that
    way would be a store of the held value: the second pair is (C, B) instead."""
    for reg, rr in (("R1", L.R1), ("R2", L.R2)):
        assert L.B[rr] ^ L.MASK[rr] == L.A[rr]          # why the first design was vacuous
        for j in run_stage.jobs_9b(reg, [3], 2, 1, 1):
            b, c = (L.C[rr], L.B[rr]) if j["pair"] else (L.B[rr], L.C[rr])
            assert (j["params"]["8"], j["params"]["9"]) == (b, c) and j["A"] == L.A[rr]
            assert j["params"]["8"] != j["A"] and j["params"]["9"] != j["A"]


def test_every_value_fits_the_register_width():
    for reg, rr in (("R1", L.R1), ("R2", L.R2)):
        for j in run_stage.jobs_9b(reg, sorted(L.X9B), 2, 1, 1):
            assert j["params"]["8"] <= L.MASK[rr] and j["params"]["9"] <= L.MASK[rr]


def rec(reg, n, L_, H, A, B, C, other_H=None, slot=None, done=True):
    rr = {"R1": L.R1, "R2": L.R2}[reg]
    other = L.R2 if rr == L.R1 else L.R1
    return {"job": {"n": n, "A": A, "A_other": L.A[other], "params": {"8": B, "9": C}},
            "slot": slot or [L_, 0, 0, 0], "done": done,
            "H": {hex(rr): H, hex(other): L.A[other] if other_H is None else other_H}}


def test_evaluate_predicted_and_falsified_records(frozen):
    A, B, C = L.A[L.R1], L.B[L.R1], L.C[L.R1]
    ok, _ = run_stage.evaluate_9b(rec("R1", 3, B, B, A, B, C), "R1")
    assert ok
    ok, _ = run_stage.evaluate_9b(rec("R1", 3, A, B, A, B, C), "R1")
    assert not ok                       # the ldr overtook
    ok, _ = run_stage.evaluate_9b(rec("R1", 3, A, A, A, B, C), "R1")
    assert not ok                       # the str did not land
    ok, _ = run_stage.evaluate_9b(rec("R1", 14, L.A[L.R2], B, A, B, C), "R1")
    assert ok                           # X8: R2 unchanged
    ok, _ = run_stage.evaluate_9b(rec("R1", 14, L.A[L.R2], B, A, B, C, other_H=7), "R1")
    assert not ok                       # the registers alias
    ok, _ = run_stage.evaluate_9b(rec("R1", 15, B, B, A, B, C, slot=[B, 0xdeadc0de, 0, 0]), "R1")
    assert ok
    ok, _ = run_stage.evaluate_9b(rec("R1", 15, 0xdeadc0de, B, A, B, C), "R1")
    assert not ok                       # X9: a result never landed


def test_no_str_before_the_predictions_are_frozen(tmp_path, monkeypatch):
    monkeypatch.setattr(run_stage, "PRED", tmp_path / "p.toml")
    monkeypatch.setattr(run_stage, "FROZEN", tmp_path / "p.sha256")
    (tmp_path / "p.toml").write_text(classify.render())
    with pytest.raises(run_stage.StageStop):
        run_stage.check_frozen_predictions()


def test_a_changed_prediction_after_the_freeze_is_refused(frozen):
    p, f = frozen
    run_stage.check_frozen_predictions()
    p.write_text(p.read_text().replace('expect = "L == B and H == B"', 'expect = "L == 1"', 1))
    with pytest.raises(run_stage.StageStop):
        run_stage.check_frozen_predictions()


def test_the_remote_runner_only_writes_the_two_registers_and_names_no_clock_gate():
    src = (HERE / "fwtask_run.py").read_text()
    assert "REGS_WRITABLE = {0x0814: " in src and "0x0a78: " in src
    # the only register write is kreg_write, which refuses anything else; the clock-gate names
    # appear as a deny list only
    assert src.count('wr("kreg"') == 1
    assert "DENY_NAMES" in src
    import fwtask_run
    with pytest.raises(fwtask_run.Stop):
        fwtask_run.kreg_write(0x0004, 0)        # CR_CLKGATECTL2
    for off in (0x0000, 0x0004, 0x0008, 0x000c, 0x0810, 0x0818, 0x0520):
        with pytest.raises(fwtask_run.Stop):
            fwtask_run.kreg_write(off, 0)


def test_b_entry_reads_the_reader_slots_and_judge_b_separates_stage_from_predictions(tmp_path, monkeypatch):
    """Stage B's evaluation, from a synthetic run: the markers kept or not decide the rows, the stage
    passes when the pair ran and the tick went on, whatever the rows say."""
    p = tmp_path / "predictions-1130.toml"
    p.write_text(classify.render())
    monkeypatch.setattr(run_stage, "PRED", p)

    def rd(kind, k, pclink, p4, r20, r21, i0, i1, sa, rate=1000.0, **kw):
        s = {"10": [pclink, *p4[:3]], "11": [p4[3], r20, r21, i0], "12": list(sa[:4]),
             "13": [sa[4], i1, L.INITFILL, L.INITFILL]}
        d = {"kind": kind, "k": k, "slots": s, "alive": {"advancing": True}, "rate_hz": rate, "reader_cleared": True}
        d.update(kw)
        return d

    m = [0x80000001 + i for i in range(9)]
    pat = [0, 0, 1, 1]
    ctl = {"rounds": [rd("control", 0, 0x98, (1, 1, 0, 0), 0, 0x1000, 7, 8, (2, 3, 4, 0, 0))] * 2}
    keep = rd("write", 0, 6, (1, 0, 1, 1), m[5], m[6], m[7], m[8], (2, m[1], m[2], m[3], m[4]), writer_ms=0.4)
    gap = rd("gap", 1, 0x98, (1, 1, 1, 1), m[5], m[6], m[7], m[8], (2, m[1], m[2], m[3], m[4]))
    fill = rd("fill", 2, 0x98, (1, 1, 0, 1), 0, 0x1000, m[7], m[8], (2, m[1], m[2], m[3], m[4]))
    out = {"rounds": [keep, gap, fill] * 3}
    saved = {}

    class Run:
        def save(self, f, o):
            saved[f] = o
    run_stage.judge_b(Run(), ctl, out, [m, m, m], pat)
    v = saved["b-verdicts.json"]
    r = v["rounds"][0]
    assert r["B_sa_low_next"] and r["B_i_kept"] and not r["B_r_gone"]     # r20, r21 were kept: the row fails
    assert not r["B_sa_high_next"]                                       # sa64 reads 2, not the marker
    assert v["summary"]["B_alive"] and not v["summary"]["B_pclink_const"]
    # a pair that did not run stops the stage
    bad = {"rounds": [dict(keep, reader_cleared=False), gap, fill] * 3}
    with pytest.raises(run_stage.StageStop):
        run_stage.judge_b(Run(), ctl, bad, [m, m, m], pat)


def test_b2_predictions_are_frozen_by_hash_and_can_fail(tmp_path):
    p = tmp_path / "b2.toml"
    p.write_text(classify_b2.render())
    ok = dict(pcl_next=[6, 6, 6], p1_next=[0, 0, 0])
    assert classify.evaluate(p, "B2_ponly", **ok)
    assert not classify.evaluate(p, "B2_ponly", pcl_next=[6, 0x98, 6], p1_next=[0, 0, 0])
    assert not classify.evaluate(p, "B2_sa64", sa64_next=[2, 0x80000000])
    assert classify.evaluate(p, "B2_armonly", pcl_next=[0x98] * 3, pcl_ctl=[0x98] * 3, p1_next=[1] * 3, p1_ctl=[1] * 3)
    assert not classify.evaluate(p, "B2_armonly", pcl_next=[6] * 3, pcl_ctl=[0x98] * 3, p1_next=[1] * 3, p1_ctl=[1] * 3)


def test_freeze_writes_both_11_30_tables_and_their_hashes(tmp_path, monkeypatch):
    """--freeze: predictions-1130.toml and predictions-1130-b2.toml with their sha256 files, and
    the hashes are those check_frozen_predictions accepts."""
    for name, f in (("PRED", "p.toml"), ("FROZEN", "p.sha256"), ("PRED_B2", "b2.toml"), ("FROZEN_B2", "b2.sha256")):
        monkeypatch.setattr(run_stage, name, tmp_path / f)
    run_stage.freeze_predictions()
    assert (tmp_path / "p.toml").read_text() == classify.render()
    assert (tmp_path / "b2.toml").read_text() == classify_b2.render()
    assert (tmp_path / "p.sha256").read_text().strip() == classify.sha256(tmp_path / "p.toml")
    run_stage.check_frozen_predictions()
    run_stage.check_frozen_predictions(run_stage.PRED_B2, run_stage.FROZEN_B2, classify)


def test_trc_32_and_up_is_never_armed_without_the_explicit_hazard_flag(monkeypatch):
    """The arm of a TRC of 32 or more needs the hazard word; the tool gives it only when asked
    for (--trc-hazard, off by default), and refuses before arming anything otherwise. The words
    are the only difference between the lines."""
    assert run_stage.trc_arm_line(31, False) == "slots=0x1 entry=0 trc=31"
    assert run_stage.trc_arm_line(8, True) == "slots=0x1 entry=0 trc=8"
    for t in (32, 40, 48, 49, 64):
        with pytest.raises(run_stage.StageStop):
            run_stage.trc_arm_line(t, False)
        assert run_stage.trc_arm_line(t, True) == f"slots=0x1 entry=0 trc={t} trc_hazard=1"
    armed = []
    monkeypatch.setattr(run_stage, "arm", lambda *a, **k: armed.append(a))
    monkeypatch.setattr(run_stage, "srcversions", lambda: {})
    monkeypatch.setattr(run_stage, "check_frozen_predictions", lambda *a, **k: None)

    class R:
        def env(self, x):
            pass

    ns = type("A", (), {"trc": [8, 32], "trc_hazard": False})()
    with pytest.raises(run_stage.StageStop):
        run_stage.stage_s13(R(), ns)
    assert armed == []                           # not even the T = 8 before it
