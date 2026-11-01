# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
import pathlib
import sys

import pytest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import classify  # noqa: E402
import layout as L  # noqa: E402

A, B, C = 0x15a5a, 0x0a5a5, 0x0f0f0


@pytest.fixture
def pred(tmp_path):
    p = tmp_path / "predictions.toml"
    p.write_text(classify.render())
    return p


def test_every_9b_command_has_a_row():
    ids = {r["id"] for r in classify.table()}
    for n, (name, kind, d) in L.X9B.items():
        assert name in ids or name.split("_")[0] in ids, name


def test_every_row_has_a_declared_prediction_and_a_falsifier():
    for r in classify.table():
        assert r["declared"] and r["falsifier"] and r["expect"]


def test_rows_pass_for_the_predicted_values_and_fail_otherwise(pred):
    v = dict(A=A, B=B, C=C, A2=0x15, R2H=0x15, landed=True)
    assert classify.evaluate(pred, "X2_d0", L=B, H=B, **v)
    assert not classify.evaluate(pred, "X2_d0", L=A, H=B, **v)        # the ldr overtook
    assert not classify.evaluate(pred, "X2_d0", L=A, H=A, **v)        # the str did not land
    assert classify.evaluate(pred, "X6_d0", L=A, H=B, **v)
    assert not classify.evaluate(pred, "X6_d0", L=B, H=B, **v)
    assert classify.evaluate(pred, "X7", L=C, H=C, **v)
    assert not classify.evaluate(pred, "X7", L=B, H=C, **v)
    assert not classify.evaluate(pred, "X9", L=B, H=B, A=A, B=B, C=C, landed=False)
    assert classify.evaluate(pred, "X11", t0=100, t1=300, **v)
    assert not classify.evaluate(pred, "X11", t0=100, t1=2000, **v)
    assert classify.evaluate(pred, "I13_T49", hang=True)
    assert not classify.evaluate(pred, "I13_T49", hang=False)


def test_reading_rows():
    assert classify.reading(B, B, A, B).startswith("(B,B)")
    assert classify.reading(A, B, A, B).startswith("(A,B)")
    assert classify.reading(A, A, A, B).startswith("(A,A)")
    assert classify.reading(B, A, A, B).startswith("(B,A)")
    assert classify.reading(7, B, A, B).startswith("other")


def test_the_classifier_reads_only_the_file(pred, tmp_path):
    text = pred.read_text().replace('expect = "L == B and H == B"', 'expect = "L == 1"', 1)
    q = tmp_path / "other.toml"
    q.write_text(text)
    v = dict(A=A, B=B, C=C, A2=0x15, R2H=0x15, landed=True, L=B, H=B)
    assert classify.evaluate(pred, "X2_d0", **v) is True
    assert classify.evaluate(q, "X2_d0", **v) is False


def test_render_is_deterministic():
    assert classify.render() == classify.render()
