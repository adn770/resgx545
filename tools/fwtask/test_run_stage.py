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
import layout as L  # noqa: E402
import run_stage  # noqa: E402


@pytest.fixture
def frozen(tmp_path, monkeypatch):
    p = tmp_path / "predictions.toml"
    p.write_text(classify.render())
    f = tmp_path / "predictions.sha256"
    f.write_text(classify.sha256(p) + "\n")
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
