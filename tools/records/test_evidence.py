# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""evidence.py: the evidence records' format."""
import pytest

import evidence

GOOD = '''+++
id = "E001"
claim = "an example claim"
unit = "dpm"
method = "an example method"
tiers = ["HW", "RE"]
date = "2026-10-28"
data = ["dpm-example"]
terms = ["CR_X"]
+++

What was seen.
'''


def record(tmp_path, text=GOOD, unit="dpm", name="E001-example.md"):
    p = tmp_path / unit / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)
    return p


def test_a_well_formed_record_passes(tmp_path):
    assert evidence.problems(record(tmp_path), {"CR_X"}) == []


def test_a_draft_id_passes_only_in_draft_mode(tmp_path):
    p = record(tmp_path, GOOD.replace('"E001"', '"E???"'), name="E???-example.md")
    assert evidence.problems(p, {"CR_X"}, draft=True) == []
    assert evidence.problems(p, {"CR_X"})


def test_the_record_agrees_with_its_place(tmp_path):
    p = record(tmp_path, unit="isp")
    assert "unit does not match the directory" in evidence.problems(p, {"CR_X"})
    p = record(tmp_path, name="E002-example.md")
    assert "id does not match the file name" in evidence.problems(p, {"CR_X"})
    p = record(tmp_path, unit="misc")
    assert "directory misc is not a unit" in evidence.problems(p, {"CR_X"})


def test_terms_tiers_and_line_citations_are_checked(tmp_path):
    p = record(tmp_path, GOOD.replace('"HW", "RE"', '"GUESS"').replace(
        "What was seen.", "See doc/specs/example.md:12."))
    msgs = " ".join(evidence.problems(p, set()))
    assert "tiers" in msgs and "not in the glossary" in msgs and "line number" in msgs


def test_missing_front_matter_is_reported(tmp_path):
    assert evidence.problems(record(tmp_path, "just prose\n"), set())


@pytest.mark.parametrize("old, new, msg", [
    ('tiers = ["HW", "RE"]', 'tiers = "HW"', "tiers is not a list of strings"),
    ('tiers = ["HW", "RE"]', 'tiers = [["HW"]]', "tiers is not a list of strings"),
    ('terms = ["CR_X"]', "terms = [1]", "terms is not a list of strings"),
    ('data = ["dpm-example"]', 'data = "dpm-example"', "data is not a list of strings"),
    ('id = "E001"', "id = 1", "id is not a string"),
    ('unit = "dpm"', "unit = 3", "unit is not a string"),
    ('date = "2026-10-28"', "date = 2026-10-28", "date is not a string"),
    ('claim = "an example claim"', "claim = 1", "claim empty"),
])
def test_malformed_types_are_reported_not_a_crash(tmp_path, old, new, msg):
    p = record(tmp_path, GOOD.replace(old, new))
    assert msg in evidence.problems(p, {"CR_X"})


@pytest.mark.parametrize("date", ["2026-99-99", "2026-02-30", "20261028", "2026-10-28T00:00"])
def test_the_date_is_a_calendar_date(tmp_path, date):
    p = record(tmp_path, GOOD.replace("2026-10-28", date))
    assert "date is not YYYY-MM-DD" in evidence.problems(p, {"CR_X"})


def test_only_unit_directories_of_records_live_under_evidence(tmp_path):
    record(tmp_path)
    record(tmp_path, name="notes.txt")
    record(tmp_path, unit="dpm/deeper")
    (tmp_path / "E003-top.md").write_text(GOOD)
    (tmp_path / "dpm" / ".DS_Store").write_text("")
    assert [p.relative_to(tmp_path).as_posix() for p in evidence.misplaced(tmp_path)] == [
        "E003-top.md", "dpm/deeper/E001-example.md", "dpm/notes.txt"]


def test_main_reports_misplaced_files(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(evidence, "ROOT", tmp_path)
    monkeypatch.setattr(evidence, "DIR", tmp_path / "evidence")
    monkeypatch.setattr(evidence, "glossary_terms", lambda: {"CR_X"})
    record(tmp_path / "evidence")
    assert evidence.main([]) == 0
    record(tmp_path / "evidence", unit="dpm/deeper")
    assert evidence.main([]) == 1
    assert "evidence/dpm/deeper/E001-example.md: not evidence/<unit>/<name>.md" in \
        capsys.readouterr().out


# --- the repository's records ----------------------------------------------------------------

import re  # noqa: E402

E_REF = re.compile(r"\bE\d{3,}\b")


def _records():
    return sorted(evidence.DIR.glob("*/*.md"))


def test_the_records_are_well_formed():
    terms = evidence.glossary_terms()
    bad = {p.name: m for p in _records() if (m := evidence.problems(p, terms))}
    assert not bad, bad
    assert not evidence.misplaced(), evidence.misplaced()


def test_a_retired_id_is_not_reused(tmp_path, monkeypatch):
    monkeypatch.setattr(evidence, "RETIRED", {"E001": "refuted"})
    assert "id is retired" in "".join(evidence.problems(record(tmp_path), {"CR_X"}))


def test_ids_are_unique():
    ids = [p.name.split("-")[0] for p in _records()]
    assert len(ids) == len(set(ids))


def test_references_between_records_resolve():
    """A record names another as E<nnn>; no placeholder for a document section is left, since
    nothing cites a spec."""
    ids = {p.name.split("-")[0] for p in _records()}
    for p in _records():
        body = evidence.parse(p)[1]
        assert "{{ref:" not in body, p
        assert set(E_REF.findall(body)) <= ids, p


def test_the_glossary_cites_records_not_documents():
    """References run glossary -> evidence -> specs: a glossary row cites a record (E<nnn>) or
    an external source, never a design document or a spec page."""
    import sys
    sys.path.insert(0, str(evidence.ROOT / "tools" / "clean-room"))
    import glossary
    ids = {p.name.split("-")[0] for p in _records()}
    for r in glossary.load():
        for col in ("citation", "evidence", "meaning"):
            assert not re.search(r"\bdoc/[\w./-]+\.md|§", r[col]), \
                (r["name"], col)
            assert set(E_REF.findall(r[col])) <= ids, (r["name"], col)


def test_a_corrected_claim_needs_a_correction_of_its_date(tmp_path):
    marked = GOOD.replace('"an example claim"',
                          '"a corrected claim [corrected 2026-11-11, see Correction]"')
    assert evidence.problems(record(tmp_path, marked), {"CR_X"}) == \
        ["claim marked corrected 2026-11-11 but no **Correction 2026-11-11:** in the prose"]
    fixed = marked + "\n**Correction 2026-11-11:** The claim said X; it is Y.\n"
    assert evidence.problems(record(tmp_path, fixed), {"CR_X"}) == []


def test_a_claim_edited_after_landing_carries_the_corrected_mark():
    """A landed record's claim changes only with a dated mark (HACKING.md, Evidence records).

    The rule holds from 2026-11-11; earlier claim edits (the 2026-11-01 rewrite, a retired
    question's id taken out on 2026-11-10) predate it."""
    import subprocess
    root = evidence.ROOT
    try:
        log = subprocess.run(["git", "-C", str(root), "log", "--diff-filter=M", "-p",
                              "--since=2026-11-11T00:00", "--format=@@commit %h", "--",
                               "evidence"],
                             capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        pytest.skip("no git history")
    edited, path = set(), None
    for line in log.splitlines():
        if line.startswith("+++ b/"):
            path = line[6:]
        elif line.startswith("+claim = ") and path:
            edited.add(path)
    bad = [p for p in sorted(edited) if (root / p).exists()
           and "[corrected " not in evidence.parse(root / p)[0]["claim"]]
    assert not bad, bad


def test_record_numbers_past_e999_are_accepted(tmp_path):
    p = record(tmp_path, GOOD.replace('"E001"', '"E1000"'), name="E1000-example.md")
    assert evidence.problems(p, {"CR_X"}) == []
    p = record(tmp_path, GOOD.replace('"E001"', '"E12345"'), name="E12345-example.md")
    assert evidence.problems(p, {"CR_X"}) == []
    assert evidence.num("E1000") > evidence.num("E999") > evidence.num("E099")
    assert sorted(["E1000", "E999", "E100"], key=evidence.num) == ["E100", "E999", "E1000"]
    p = record(tmp_path, name="E01-example.md")      # too few digits stays refused
    assert evidence.problems(p, {"CR_X"})
