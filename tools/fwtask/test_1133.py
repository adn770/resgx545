# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Phase 11.33 part 1: the TRC 32 to 48 temporaries run (item 13, Q133)."""
import pathlib
import sys

import pytest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fwtask  # noqa: E402
import gen_blobs  # noqa: E402
import layout as L  # noqa: E402
import t1133  # noqa: E402


def test_the_five_sources_exist_assemble_and_verify():
    for t in t1133.TS:
        src = (fwtask.ASM / f"trcp_{t}.s").read_text()
        assert src == gen_blobs.gen_trcp(t)
        assert fwtask.blob_of(f"trcp_{t}")
        assert "ldad.bypassl1 r10, [r1,+#8], drc0" in src      # the marker comes from the job
        assert "mov r123, r10" in src
        assert "#0x7a11" not in src                              # no marker constant in the blob


def test_arm_line_only_32_to_48_with_the_hazard_word():
    for t in (32, 36, 40, 44, 48):
        assert t1133.arm_line(t) == f"slots=0x1 entry=0 trc={t} trc_hazard=1"
    for t in (0, 8, 31, 49, 50, 64):
        with pytest.raises(ValueError):
            t1133.arm_line(t)


def test_every_job_has_its_own_marker():
    jobs = t1133.make_jobs(t1133.TS, 2, seed=1133)
    assert len(jobs) == 10
    ms = [j["marker"] for j in jobs]
    assert len(set(ms)) == len(ms)
    assert all(m & 0x80000000 and m != L.INITFILL for m in ms)
    assert all(j["params"] == {"8": j["marker"]} for j in jobs)
    assert [j["T"] for j in jobs[:5]] == list(t1133.TS)         # first pass: one job per T
    assert t1133.make_jobs(t1133.TS, 2, seed=1133) == jobs
    assert t1133.make_jobs(t1133.TS, 2, seed=1134) != jobs


def test_judge_is_able_to_fail():
    ok = {"done": True, "slot": [0x81234567, 0, 0, 0xdeadc0de]}
    assert t1133.judge(0x81234567, ok)["marker_back"] is True
    assert t1133.judge(0x81234568, ok)["marker_back"] is False
    stale = {"done": True, "slot": [L.INITFILL, L.INITFILL, L.INITFILL, L.INITFILL]}
    assert t1133.judge(0x81234567, stale)["marker_back"] is False
    assert t1133.judge(0x81234567, {"done": False, "slot": ok["slot"]})["done"] is False
    r0 = {"done": True, "slot": [0x81234567, 0, 5, 0]}
    assert t1133.judge(0x81234567, r0)["r0_zero"] is False


def test_the_predictions_are_frozen_and_can_fail(tmp_path):
    p = tmp_path / "p.toml"
    p.write_text(t1133.render_predictions())
    sha = t1133.sha256(p)
    assert t1133.check_frozen(p, sha)
    assert not t1133.check_frozen(p, "0" * 64)
    rows = t1133.load_predictions(p)
    for t in t1133.TS:
        assert f"P33_T{t}" in rows and "marker_back" in rows[f"P33_T{t}"]["expect"]
    assert "P33_PAST" in rows
