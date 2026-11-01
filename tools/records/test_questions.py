# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""questions.py: the open questions, one per file, removed and retired once answered."""
import pytest

import questions

GOOD = '''+++
id = "Q001"
question = "what does the example bit do?"
unit = "isp"
phase = 10
evidence = ["E001"]
terms = ["CR_X"]
+++

What is known, what was tried, and what experiment would settle it.
'''


def record(tmp_path, text=GOOD, unit="isp", name="Q001-example-bit.md"):
    p = tmp_path / unit / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)
    return p


def test_a_well_formed_question_passes(tmp_path):
    assert questions.problems(record(tmp_path), {"E001"}, {"CR_X"}) == []


@pytest.mark.parametrize("old, new, msg", [
    ('question = "what does the example bit do?"', 'question = "a\\nb"', "one line"),
    ('phase = 10', 'phase = 13', "phase"),
    ('evidence = ["E001"]', 'evidence = ["E404"]', "E404"),
    ('terms = ["CR_X"]', 'terms = ["CR_Y"]', "CR_Y"),
    ('unit = "isp"', 'unit = "misc"', "unit"),
])
def test_fields_are_checked(tmp_path, old, new, msg):
    p = record(tmp_path, GOOD.replace(old, new))
    assert any(msg in m for m in questions.problems(p, {"E001"}, {"CR_X"}))


def test_the_record_agrees_with_its_place(tmp_path):
    assert questions.problems(record(tmp_path, name="Q002-example-bit.md"), {"E001"}, {"CR_X"})
    assert questions.problems(record(tmp_path, unit="dpm"), {"E001"}, {"CR_X"})
    assert questions.problems(record(tmp_path, name="example.md"), {"E001"}, {"CR_X"})


def test_malformed_fields_are_reported_not_raised(tmp_path):
    p = record(tmp_path, GOOD.replace('evidence = ["E001"]', 'evidence = 3'))
    assert any("evidence" in m for m in questions.problems(p, {"E001"}, {"CR_X"}))


def test_an_answered_question_is_retired_and_cited_only_as_answered(monkeypatch):
    monkeypatch.setattr(questions, "RETIRED", {"Q002": "answered by E003"})
    assert questions.reference_problems("see Q001 and Q002", {"Q001"}) == \
        ["Q002 is answered (answered by E003): cite the answer"]
    assert questions.reference_problems("Q009", {"Q001"}) == ["Q009: no such question"]
    with pytest.raises(ValueError):
        questions.check_retired({"Q002": "it was hard"})


def test_the_view_lists_every_question_by_unit(tmp_path):
    p = record(tmp_path)
    text = questions.render([questions.parse(p)])
    assert "## isp" in text and "`Q001`" in text and "what does the example bit do?" in text


# --- the repository's questions ---------------------------------------------------------------

def test_the_questions_are_well_formed():
    import evidence
    ids = {p.name[:4] for p in evidence.DIR.glob("*/E*.md")}
    terms = evidence.glossary_terms()
    bad = {p.name: m for p in questions.files() if (m := questions.problems(p, ids, terms))}
    assert not bad, bad
    assert not questions.misplaced()
    questions.check_retired(questions.RETIRED)


def test_the_view_is_current():
    qs = [questions.parse(p) for p in questions.files()]
    if not qs and not questions.DOC.exists():
        pytest.skip("no open questions yet")
    assert questions.DOC.exists() and questions.DOC.read_text() == questions.render(qs)


def test_references_name_open_questions():
    """Specs, evidence records and glossary terms cite only open questions."""
    open_ids = {p.name[:4] for p in questions.files()}
    bad = {}
    for d, pat in (("evidence", "*/*.md"), ("glossary", "*/*.toml"), ("doc", "**/*.md")):
        for p in sorted((questions.ROOT / d).glob(pat)):
            if p != questions.DOC and (m := questions.reference_problems(p.read_text(),
                                                                         open_ids)):
                bad[str(p.relative_to(questions.ROOT))] = m
    assert not bad, bad
