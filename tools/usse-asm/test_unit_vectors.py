# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""unit_vectors.py against the data repository: the unit vectors of 12.0 (zls-store, te-region,
ta-object, isp-tile) carry the counts their records state. Skips (with the reason) when the data
repository is absent."""
import json
import os
import pathlib

import pytest

import unit_vectors as uv

ROOT = pathlib.Path(__file__).resolve().parents[2]
DATA = pathlib.Path(os.environ.get("RESGX545_DATA") or ROOT.parent / "resgx545-data")

pytestmark = pytest.mark.skipif(not (DATA / "zls/store-layout-dumps/recompute.txt").is_file(),
                                reason="no resgx545-data (set RESGX545_DATA)")


def vectors(fn):
    return fn(DATA)


def test_zls_store_has_the_18_cases_and_the_counts_of_e489():
    vs = vectors(uv.zls_store)
    assert len(vs) == 18
    assert sum(v["expect"]["stored"] for v in vs) == 3415552
    # 3279132 dwords at the rule's address: 3225000 for pixels of the target, 54132 past it (Q122)
    assert sum(v["expect"]["matched"] for v in vs) == 3225000
    assert sum(v["expect"]["refused"].get("Q107", 0) for v in vs) == 128640 + 6656
    assert sum(v["expect"]["refused"].get("Q122", 0) for v in vs) == 54132 + 1124
    assert all(v["init"]["task"] == "zls-store" and len(v["init"]["x"]["sha256"]) == 64 for v in vs)


def test_te_region_has_the_35_jobs_and_14656_pairs_with_no_mismatch():
    vs = vectors(uv.te_region)
    assert len(vs) == 35
    assert sum(v["expect"]["matched"] for v in vs) == 14656
    assert all(v["init"]["prims"] for v in vs)


def test_ta_object_has_the_completed_jobs_and_the_three_that_did_not():
    vs = vectors(uv.ta_object)
    done = [v for v in vs if "stored" in v["expect"]]
    failed = [v for v in vs if v["expect"].get("outcome") in ("hang", "fault")]
    assert (len(vs), len(done), len(failed)) == (59, 56, 3)
    assert sorted(v["expect"]["outcome"] for v in failed) == ["fault", "hang", "hang"]
    assert sum(1 for v in done if v["id"].startswith("ta-object__f2-")) == 12


def test_isp_tile_has_the_48_runs_and_the_786_tiles_of_e503():
    vs = vectors(uv.isp_tile)
    assert len(vs) == 48
    assert sum(v["expect"]["tiles"] for v in vs) == 786
    assert sum(v["expect"]["matched"] for v in vs) == 773
    assert sum(v["expect"]["refused"].get("Q141", 0) for v in vs) == 13


def test_written_files_are_the_vector_container_and_deterministic(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    uv.write_all(DATA, a)
    uv.write_all(DATA, b)
    fa = sorted(p.relative_to(a) for p in a.rglob("*.vec.json"))
    assert len(fa) >= 4
    for p in fa:
        assert (a / p).read_bytes() == (b / p).read_bytes()
        d = json.loads((a / p).read_text())
        assert d["format"] == "sgx545-vectors" and d["version"] == 1 and d["vectors"]
