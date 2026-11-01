# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
import pathlib
import sys

import pytest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import classify  # noqa: E402
import classify1129  # noqa: E402
import layout as L  # noqa: E402

A, B, C = 0x15a5a, 0x0a5a5, 0x0f0f0


@pytest.fixture
def pred(tmp_path):
    p = tmp_path / "predictions.toml"
    p.write_text(classify.render())
    return p


@pytest.fixture
def pred1129(tmp_path):
    p = tmp_path / "predictions1129.toml"
    p.write_text(classify1129.render())
    return p


def test_every_9b_command_has_a_row_in_the_11_29_table():
    ids = {r["id"] for r in classify1129.table()}
    for n, (name, kind, d) in L.X9B.items():
        assert name in ids or name.split("_")[0] in ids, name


def test_every_row_has_a_declared_prediction_and_a_falsifier():
    for r in classify.table() + classify1129.table():
        assert r["declared"] and r["falsifier"] and r["expect"]


def test_11_29_rows_pass_for_the_predicted_values_and_fail_otherwise(pred1129):
    v = dict(A=A, B=B, C=C, A2=0x15, R2H=0x15, landed=True)
    assert classify1129.evaluate(pred1129, "X2_d0", L=B, H=B, **v)
    assert not classify1129.evaluate(pred1129, "X2_d0", L=A, H=B, **v)        # the ldr overtook
    assert not classify1129.evaluate(pred1129, "X2_d0", L=A, H=A, **v)        # the str did not land
    assert classify1129.evaluate(pred1129, "X6_d0", L=A, H=B, **v)
    assert not classify1129.evaluate(pred1129, "X6_d0", L=B, H=B, **v)
    assert classify1129.evaluate(pred1129, "X7", L=C, H=C, **v)
    assert not classify1129.evaluate(pred1129, "X7", L=B, H=C, **v)
    assert not classify1129.evaluate(pred1129, "X9", L=B, H=B, A=A, B=B, C=C, landed=False)
    assert classify1129.evaluate(pred1129, "X11", t0=100, t1=300, **v)
    assert not classify1129.evaluate(pred1129, "X11", t0=100, t1=2000, **v)


def test_11_30_rows_pass_for_the_predicted_values_and_fail_otherwise(pred):
    m = (1, 2, 3)
    assert classify.evaluate(pred, "B_sa_high_next", sa_high=m, markers_high=m)
    assert not classify.evaluate(pred, "B_sa_high_next", sa_high=(2, 2, 3), markers_high=m)      # sa64 = 2
    assert classify.evaluate(pred, "B_r_gone", r_vals=(0, 1), markers_r=(5, 6))
    assert not classify.evaluate(pred, "B_r_gone", r_vals=(5, 6), markers_r=(5, 6))
    assert classify.evaluate(pred, "B_r_gone", r_vals=(5, 1), markers_r=(5, 6))        # a partial match passes: the row is a tuple compare
    assert classify.evaluate(pred, "B_i_kept", i_vals=(7, 8), markers_i=(7, 8))
    assert not classify.evaluate(pred, "B_i_kept", i_vals=(7, 9), markers_i=(7, 8))
    # the row's expression passes when p0 alone differs: the weakness recorded in E536
    assert classify.evaluate(pred, "B_p_gone", p_vals=(1, 0, 1, 1), p_pattern=(0, 0, 1, 1))
    assert classify.evaluate(pred, "B_pclink_const", pclinks=[0x98] * 5)
    assert not classify.evaluate(pred, "B_pclink_const", pclinks=[0x98, 0x98, 6, 6, 6])
    assert classify.evaluate(pred, "Q033_q1m", hit_slots=[0], pa1=0x02000100)
    assert not classify.evaluate(pred, "Q033_q1m", hit_slots=[0], pa1=0x03000000)
    assert not classify.evaluate(pred, "Q033_q1m", hit_slots=[1], pa1=0x100)
    assert classify.evaluate(pred, "Q033_quiet", quiet_hits=[])
    assert not classify.evaluate(pred, "Q033_quiet", quiet_hits=[0])
    assert classify.evaluate(pred, "I11_overlap", overlap_runs=0, lost_ticks=0)
    assert not classify.evaluate(pred, "I11_overlap", overlap_runs=1, lost_ticks=0)
    assert classify.evaluate(pred, "I13_P09", past_back=0)
    assert not classify.evaluate(pred, "I13_P09", past_back=0x7b220009)
    assert classify.evaluate(pred, "I13_T49", hang=True)
    assert not classify.evaluate(pred, "I13_T49", hang=False)


def test_reading_rows():
    assert classify1129.reading(B, B, A, B).startswith("(B,B)")
    assert classify1129.reading(A, B, A, B).startswith("(A,B)")
    assert classify1129.reading(A, A, A, B).startswith("(A,A)")
    assert classify1129.reading(B, A, A, B).startswith("(B,A)")
    assert classify1129.reading(7, B, A, B).startswith("other")


def test_the_classifier_reads_only_the_file(pred, tmp_path):
    text = pred.read_text().replace('expect = "sa_high == markers_high"', 'expect = "sa_high == 1"', 1)
    q = tmp_path / "other.toml"
    q.write_text(text)
    v = dict(sa_high=(1, 2, 3), markers_high=(1, 2, 3))
    assert classify.evaluate(pred, "B_sa_high_next", **v) is True
    assert classify.evaluate(q, "B_sa_high_next", **v) is False


def test_render_is_deterministic():
    assert classify.render() == classify.render()
