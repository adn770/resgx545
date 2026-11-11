# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""spec_coverage.py: every hardware record from E600 is cited by a spec or listed, with a reason,
in doc/specs/UNCITED.toml, a baseline that may only shrink."""
import pytest

import spec_coverage


def record(tree, rid, tiers='["HW"]', unit="isp"):
    d = tree / "evidence" / unit
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{rid}-x.md").write_text(f'+++\nid = "{rid}"\ntiers = {tiers}\n+++\nbody\n')


@pytest.fixture
def tree(tmp_path, monkeypatch):
    (tmp_path / "doc" / "specs").mkdir(parents=True)
    monkeypatch.setattr(spec_coverage, "ROOT", tmp_path)
    return tmp_path


def test_cited_tokens_and_ranges():
    assert spec_coverage.cited("E601, E700 and E804-E806; E810 to E811 (E820..E821)") == {
        "E601", "E700", "E804", "E805", "E806", "E810", "E811", "E820", "E821"}
    assert spec_coverage.cited("E8040 xE601") == set()


def test_only_hardware_records_from_e600_must_be_cited(tree):
    record(tree, "E599")
    record(tree, "E600")
    record(tree, "E601", tiers='["CAP"]')
    record(tree, "E602", tiers='["infer"]')
    assert spec_coverage.required() == {"E600", "E601"}


def test_a_record_neither_cited_nor_listed_is_a_problem(tree):
    record(tree, "E600")
    record(tree, "E601")
    (tree / "doc" / "specs" / "a.md").write_text("see E600\n")
    assert spec_coverage.problems(baseline={}) == [
        "E601: cited by no doc/specs file and not in doc/specs/UNCITED.toml"]
    assert spec_coverage.problems(baseline={"E601": "not yet"}) == []


def test_a_listed_record_that_is_cited_must_leave_the_baseline(tree):
    record(tree, "E600")
    (tree / "doc" / "specs" / "a.md").write_text("see E600\n")
    assert spec_coverage.problems(baseline={"E600": "not yet"}) == [
        "E600: cited by a spec, remove it from doc/specs/UNCITED.toml"]


def test_a_listed_id_that_needs_no_citation_is_a_problem(tree):
    record(tree, "E602", tiers='["infer"]')
    assert spec_coverage.problems(baseline={"E602": "x", "E999": "x"}) == [
        "E602: not a hardware record from E600, remove it from doc/specs/UNCITED.toml",
        "E999: not a hardware record from E600, remove it from doc/specs/UNCITED.toml"]


def test_every_listed_record_has_a_reason(tree):
    record(tree, "E600")
    assert spec_coverage.problems(baseline={"E600": ""}) == ["E600: listed without a reason"]


def test_main_reads_the_baseline_and_checks(tree):
    record(tree, "E600")
    assert spec_coverage.main(["--check"]) == 1
    (tree / "doc" / "specs" / "UNCITED.toml").write_text('E600 = "not yet in a spec"\n')
    assert spec_coverage.main(["--check"]) == 0
