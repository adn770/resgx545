# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""sim_coverage.py: every hardware record from E600 is cited by sgx-sim, sgx-pipe or pysgx (source
or tests, as a model or a refusal) or listed, with a reason, in crates/SIM_UNMODELLED.toml, a
baseline that may only shrink."""
import pytest

import sim_coverage

BASE = "crates/SIM_UNMODELLED.toml"


def record(tree, rid, tiers='["HW"]', unit="isp"):
    d = tree / "evidence" / unit
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{rid}-x.md").write_text(f'+++\nid = "{rid}"\ntiers = {tiers}\n+++\nbody\n')


def source(tree, rel, text):
    p = tree / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


@pytest.fixture
def tree(tmp_path, monkeypatch):
    for c in ("sgx-sim", "sgx-pipe", "pysgx"):
        (tmp_path / "crates" / c).mkdir(parents=True)
    monkeypatch.setattr(sim_coverage, "ROOT", tmp_path)
    return tmp_path


def test_cited_tokens_and_ranges_are_spec_coverages():
    assert sim_coverage.cited("E601 and E804-E806; E810 to E811 (E820..E821)") == {
        "E601", "E804", "E805", "E806", "E810", "E811", "E820", "E821"}
    assert sim_coverage.cited("E12 xE601 0xE601 E601x") == set()


def test_only_hardware_records_from_e600_must_be_cited(tree):
    record(tree, "E599")
    record(tree, "E600")
    record(tree, "E601", tiers='["CAP"]')
    record(tree, "E602", tiers='["infer"]')
    record(tree, "E603", tiers='["RE"]')
    assert sim_coverage.required() == {"E600", "E601"}


def test_sources_and_tests_of_the_three_crates_cite(tree):
    source(tree, "crates/sgx-sim/src/edm.rs", "// refused: 0x0728 (E700)\n")
    source(tree, "crates/sgx-pipe/tests/zls.rs", "//! E831, E885\n")
    source(tree, "crates/pysgx/tests/test_x.py", "# E702-E703\n")
    source(tree, "crates/sgx-sim/examples/a.rs", "// E704\n")
    source(tree, "crates/pds-isa/src/lib.rs", "// E705: not a simulator\n")
    source(tree, "crates/sgx-sim/target/release/build.rs", "// E706: a build product\n")
    source(tree, "doc/specs/a.md", "E707\n")
    assert sim_coverage.sim_citations() == {"E700", "E831", "E885", "E702", "E703", "E704"}


def test_a_record_neither_cited_nor_listed_is_a_problem(tree):
    record(tree, "E600")
    record(tree, "E601")
    source(tree, "crates/sgx-sim/src/a.rs", "// E600\n")
    assert sim_coverage.problems(baseline={}) == [
        f"E601: cited by no sgx-sim, sgx-pipe or pysgx file and not in {BASE}"]
    assert sim_coverage.problems(baseline={"E601": "not modelled yet"}) == []


def test_a_listed_record_that_the_code_cites_must_leave_the_baseline(tree):
    record(tree, "E600")
    source(tree, "crates/sgx-pipe/src/a.rs", "// E600\n")
    assert sim_coverage.problems(baseline={"E600": "not yet"}) == [
        f"E600: cited by the simulator code, remove it from {BASE}"]


def test_a_listed_id_that_needs_no_citation_is_a_problem(tree):
    record(tree, "E602", tiers='["infer"]')
    assert sim_coverage.problems(baseline={"E602": "x", "E999": "x"}) == [
        f"E602: not a hardware record from E600, remove it from {BASE}",
        f"E999: not a hardware record from E600, remove it from {BASE}"]


def test_every_listed_record_has_a_reason(tree):
    record(tree, "E600")
    assert sim_coverage.problems(baseline={"E600": " "}) == ["E600: listed without a reason"]


def test_main_reads_the_baseline_and_checks(tree):
    record(tree, "E600")
    assert sim_coverage.main(["--check"]) == 1
    source(tree, BASE, 'E600 = "not modelled by sgx-sim or sgx-pipe yet"\n')
    assert sim_coverage.main(["--check"]) == 0
    assert sim_coverage.main(["--bogus"]) == 2


def test_write_baseline_starts_the_list_and_after_that_only_shrinks_it(tree):
    record(tree, "E600")
    record(tree, "E601", unit="dpm")
    record(tree, "E602")
    source(tree, "crates/sgx-sim/src/a.rs", "// E600\n")
    assert sim_coverage.main(["--write-baseline"]) == 0
    listed = sim_coverage.load_baseline()
    assert sorted(listed) == ["E601", "E602"] and listed["E601"].startswith("dpm: ")
    assert sim_coverage.main(["--check"]) == 0
    source(tree, "crates/sgx-pipe/src/b.rs", "// E602\n")
    record(tree, "E603")
    assert sim_coverage.main(["--write-baseline"]) == 0
    assert sorted(sim_coverage.load_baseline()) == ["E601"]
    assert sim_coverage.problems(sim_coverage.load_baseline()) == [
        f"E603: cited by no sgx-sim, sgx-pipe or pysgx file and not in {BASE}"]
