# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The sim chain of phase 11.29: our wrapper and variants in sgx-sim (pysgx) with our own stand-in
for the closed task. The simulator proves encodings, control flow, patching and the results
layout. It proves nothing of hardware: its `ldr` returns the register when it is issued and a
`str` lands at once (no hardware vector replays either), so "ordered" here is the model's."""
import pathlib
import sys

import pytest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fwtask  # noqa: E402
import layout as L  # noqa: E402
import simrun  # noqa: E402

pytestmark = pytest.mark.skipif(not simrun.available(), reason="pysgx does not build here (cargo)")


def test_limm_patch_matches_the_assembler():
    base = fwtask.assemble_text("mov r5, #0x00000000")[0]
    for v in (0, 1, 0x4000, 0x32140000, 0xdeadbeef, 0xffffffff, 0x12345678):
        assert fwtask.limm_set(base, v) == fwtask.assemble_text(f"mov r5, #0x{v:08x}")[0], hex(v)
        assert fwtask.limm_get(fwtask.limm_set(base, v)) == v


def test_null_wrapper_only_tail_calls():
    r = simrun.run("null")
    assert r.stub_hit and not r.stores and not r.reg_reads and not r.reg_writes


def test_zero_command_goes_to_the_closed_task_untouched():
    for name in ("mem", "ldr", "x9b_r1", "x9b_r2", "state", "slow", "trc_08"):
        r = simrun.run(name, cmd=0, entry_state=(name == "state"))
        assert r.stub_hit, name
        assert r.reg_writes == [], name
        assert r.stores == [] or name == "slow", name      # slow: busy state is 0, no overlap


def test_unknown_command_is_treated_as_zero():
    r = simrun.run("x9b_r1", cmd=99)
    assert r.stub_hit and r.reg_writes == [] and r.stores == []


def test_mem_stores_pa_and_marker_then_done():
    r = simrun.run("mem", cmd=1, pa=(7, 0, 0x1234), runid=77)
    assert r.slot(1) == [7, 0, 0x1234, 0x5a5a1129]
    assert r.mem[L.STATE] == L.DONE and r.mem[L.CMD] == 0 and r.mem[L.RUNID_ECHO] == 77
    assert r.stub_hit
    assert r.order_ok          # results and cmd are stored before state = done


def test_ldr_reads_the_three_registers():
    r = simrun.run("ldr", cmd=1, regs={7: 0x01150000, 8: 0x0001000d, 81: 0x123456})
    assert r.slot(1)[:3] == [0x01150000, 0x0001000d, 0x123456]
    assert r.reg_writes == []


@pytest.mark.parametrize("reg", ["R1", "R2"])
def test_9b_sequential_model_gives_the_predicted_rows(reg):
    for n, (name, kind, d) in L.X9B.items():
        r = simrun.run_9b(reg, n)
        assert r.ok, (reg, name, r.explain)


def test_registers_written_are_a_subset_of_the_allow_list():
    allowed = {0x0814 // 4, 0x0a78 // 4}
    for reg in ("R1", "R2"):
        for n in L.X9B:
            r = simrun.run_9b(reg, n)
            assert {i for i, v in r.reg_writes} <= allowed
            assert {i for i, v in r.reg_reads} <= allowed | {7, 8, 81}


def test_x8_leaves_the_other_register_alone():
    r = simrun.run_9b("R1", 14)
    assert r.final_regs[0x0a78 // 4] == L.A[L.R2]


def test_x9_has_no_idf_before_done():
    r = simrun.run_9b("R1", 15)
    assert not r.idf_before_done


@pytest.mark.parametrize("model", ["late4", "late20", "drop", "ldr_overtakes4"])
def test_what_if_buses_each_give_the_row_the_plan_says(model):
    """Every prediction can fail: the classifier reports the row of 4.2 for each model."""
    exp = simrun.WHAT_IF_EXPECT[model]
    for reg in ("R1", "R2"):
        for n, want in exp.items():
            r = simrun.run_9b(reg, n, model=model)
            assert r.reading == want, (model, reg, L.X9B[n][0], r.reading, want)


def test_state_two_tasks_in_the_sim():
    w = simrun.run("state", cmd=1, entry_state=True)
    assert w.mem[L.STATE] == L.DONE and w.mem[L.CMD] == 2
    assert not w.stub_hit                      # no tail call: the closed task is skipped
    assert w.final_sa[64] == 0xa5000040 and w.final_pred == (1, 0, 1, 0)
    assert w.final_pclink == 0      # task 1 cannot write pclink (R1): nothing of ours is left in it
    rd = simrun.run("state", cmd=2, entry_state=True, carry=w)
    assert rd.slot(2)[:4] == [0, 1, 0, 1] and rd.slot(3)[0] == 0
    assert rd.slot(4)[:3] == [0xa5000040, 0xa5000064, 0xa500007f]


def test_events_log_only_when_pa1_nonzero():
    r = simrun.run("events", entry=2, pa=(0, 0, 5))
    assert r.mem[L.LOG + 8] == 0 and r.stub_hit and r.stub_slot == 2
    r = simrun.run("events", entry=1, pa=(0, 0x100, 5))
    assert r.mem[L.LOG + 4:L.LOG + 8] == [1, 0, 0x100, 5] and r.stub_slot == 1


def test_slow_overlap_flag():
    r = simrun.run("slow", cmd=1, params={L.PARAM_N: 50})
    assert r.mem[L.STATE] == L.DONE and r.mem[L.OVERLAP] == 0
    r = simrun.run("slow", cmd=0, mem_extra={L.STATE: L.BUSY})
    assert r.mem[L.OVERLAP] == 1


def test_trc_marker_and_readback():
    r = simrun.run("trc_16", cmd=1, r0=0xc0ffee)
    assert r.slot(1)[:3] == [0x7a110010, 0x7b220010, r.slot(1)[2]]
    r = simrun.run("trc_31", cmd=1, r0=0xc0ffee)
    assert r.slot(1)[0] == 0x7a11001f and r.slot(1)[1] == 0
