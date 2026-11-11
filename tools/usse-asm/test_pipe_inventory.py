# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""pipe_inventory.py: the classification rules on synthetic inputs, and the scans of the data
repository checked against each other and the report (no count is pinned: the repository grows)."""
import os
import pathlib

import pytest

import pipe_inventory as inv

ROOT = pathlib.Path(__file__).resolve().parents[2]
DATA = pathlib.Path(os.environ.get("RESGX545_DATA") or ROOT.parent / "resgx545-data")
needs_data = pytest.mark.skipif(not (DATA / "vectors").is_dir(), reason="no resgx545-data")


def vec(**rb):
    return {"readback": dict({"failed": None, "pixels": None, "mixed": None, "o0": None}, **rb)}


def test_a_hung_job_is_a_hang_vector_and_a_faulted_one_a_fault_vector():
    assert inv.classify_vector(vec(failed="job hung, context lost (Connection timed out)"), False)[0] == "hang"
    assert inv.classify_vector(vec(failed="job faulted, context lost (Input/output error)"), False)[0] == "fault"


def test_no_pixel_written_is_excluded_with_its_reason():
    st, why = inv.classify_vector(vec(failed="no pixel written"), False)
    assert st == "excluded" and "no pixel" in why


def test_an_image_is_a_scene_by_pixels_or_mixed_counts_and_notes_the_dump():
    assert inv.classify_vector(vec(pixels=["0x1"]), False) == ("scene-pixels", "")
    assert inv.classify_vector(vec(mixed=[["0x1", 4]]), True) == ("scene-mixed+pb", "")
    assert inv.classify_vector(vec(pixels=["0x1"]), True)[0] == "scene-pixels+pb"


def test_a_vector_with_no_result_at_all_is_excluded():
    assert inv.classify_vector(vec(), False)[0] == "excluded"


def test_dump_directories_classify_by_the_first_matching_rule():
    r = inv.classify_dir("zls/store-layout-dumps/dumps")
    assert (r.kind, r.status) == ("zls-store", "built")
    r = inv.classify_dir("followup/vdm/state1/vdm-state1-lines3/dumps")
    assert r.kind == "vdm-stream"
    # a directory no rule matches is reported as unclassified, never an exception of the suite
    assert inv.classify_dir("nowhere/at-all/dumps") is inv.UNCLASSIFIED
    assert inv.UNCLASSIFIED.status == "unclassified"


def fake_data(tmp_path, dirs):
    for d in dirs:
        (tmp_path / d).mkdir(parents=True)
        (tmp_path / d / "f.bin").write_bytes(b"x")
    (tmp_path / "vectors").mkdir(exist_ok=True)
    return tmp_path


def test_a_new_dump_directory_is_listed_as_unclassified_and_only_the_generator_fails(tmp_path, capsys):
    data = fake_data(tmp_path, ["zls/store-layout-dumps/dumps", "brand/new-dataset/dumps"])
    dumps = inv.scan_dumps(data)
    assert [d["rule"].status for d in dumps] == ["unclassified", "built"]
    text = inv.report(data)
    assert "unclassified" in text and "brand/new-dataset/dumps" in text
    assert inv.main(["--data", str(data)]) == 0, "printing the report is not a failure"
    out = tmp_path / "out.md"
    assert inv.main(["--data", str(data), "--out", str(out)]) == 1
    assert not out.exists(), "the generator does not write an inventory with an unclassified directory"
    assert inv.main(["--data", str(fake_data(tmp_path / "ok", ["zls/store-layout-dumps/dumps"])),
                     "--out", str(out)]) == 0
    assert out.exists()


@needs_data
def test_the_scans_are_consistent_with_each_other_and_with_the_report_not_with_fixed_counts():
    # the counts grow with the data repository: nothing here pins them, the report must state
    # exactly what the two scans found, and every directory has a rule or says it has none
    t = inv.scan_vectors(DATA)
    d = inv.scan_dumps(DATA)
    assert t["vectors"] > 0 and t["files"] > 0 and len(d) > 0
    assert sum(sum(v for k, v in c.items() if not k.startswith("_")) for c in t["by"].values()) == t["vectors"]
    assert all(x["rule"] for x in d)
    text = inv.report(DATA)
    assert "%d vectors in %d files" % (t["vectors"], t["files"]) in text
    assert "%d directories named `dumps`" % len(d) in text


@needs_data
def test_the_report_fits_100_columns_and_has_no_trailing_space():
    text = inv.report(DATA)
    assert all(len(l) <= 100 for l in text.splitlines()), [l for l in text.splitlines() if len(l) > 100][:2]
    assert all(l == l.rstrip() for l in text.splitlines())


def test_the_zls_store_rule_cites_the_band_of_e831_and_no_retired_question():
    r = next(r for r in inv.RULES if r.pattern == r"zls/store-layout-dumps/")
    assert "E831" in r.records.split() and r.blockers.split() == ["Q107"]
    assert "Q122" not in inv.TAIL and "E831" in inv.TAIL
