# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""questions.py: the open questions, one per file, removed and retired once answered."""
import pytest

import questions

GOOD = '''+++
id = "Q001"
question = "what does the example bit do?"
unit = "isp"
kind = "hw"
value = "medium"
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
    ('kind = "hw"', 'kind = "driver"', "kind"),
    ('value = "medium"', 'value = "huge"', "value"),
    ('kind = "hw"\nvalue = "medium"', 'kind = "fw"\nvalue = "medium"', "value"),
    ('kind = "hw"\nvalue = "medium"', 'kind = "kernel"\nvalue = "low"', "value"),
    ('kind = "hw"\n', '', "kind"),
    ('kind = "hw"\nvalue = "medium"\n', 'value = "medium"\nkind = "hw"\n', "keys"),
])
def test_fields_are_checked(tmp_path, old, new, msg):
    p = record(tmp_path, GOOD.replace(old, new))
    assert any(msg in m for m in questions.problems(p, {"E001"}, {"CR_X"}))


@pytest.mark.parametrize("old, new", [
    ('kind = "hw"\nvalue = "medium"\n', 'kind = "hw"\n'),
    ('kind = "hw"\nvalue = "medium"\n', 'kind = "fw"\n'),
    ('kind = "hw"\nvalue = "medium"\n', 'kind = "kernel"\n'),
    ('value = "medium"', 'value = "high"'),
    ('value = "medium"', 'value = "low"'),
])
def test_kinds_and_values_that_are_allowed(tmp_path, old, new):
    p = record(tmp_path, GOOD.replace(old, new))
    assert questions.problems(p, {"E001"}, {"CR_X"}) == []


def test_a_missing_kind_is_named(tmp_path):
    p = record(tmp_path, GOOD.replace('kind = "hw"\n', ""))
    assert any("kind" in m and "missing" in m for m in questions.problems(p, {"E001"}, {"CR_X"}))


def test_the_record_agrees_with_its_place(tmp_path):
    assert questions.problems(record(tmp_path, name="Q002-example-bit.md"), {"E001"}, {"CR_X"})
    assert questions.problems(record(tmp_path, unit="dpm"), {"E001"}, {"CR_X"})
    assert questions.problems(record(tmp_path, name="example.md"), {"E001"}, {"CR_X"})


def test_malformed_fields_are_reported_not_raised(tmp_path):
    p = record(tmp_path, GOOD.replace('evidence = ["E001"]', 'evidence = 3'))
    assert any("evidence" in m for m in questions.problems(p, {"E001"}, {"CR_X"}))


def test_a_folded_question_is_retired_and_cited_as_its_target(monkeypatch):
    monkeypatch.setattr(questions, "RETIRED", {"Q002": "folded into Q001"})
    assert questions.reference_problems("see Q001 and Q002", {"Q001"}) == \
        ["Q002 was folded into Q001: cite Q001"]
    questions.check_retired({"Q002": "folded into Q001", "Q003": "answered by E004"})
    for why in ("folded into Q1", "folded into E001", "folded", "merged into Q001"):
        with pytest.raises(ValueError):
            questions.check_retired({"Q002": why})


def test_a_fold_names_an_open_question():
    assert questions.fold_problems({"Q002": "folded into Q001"}, {"Q001"}) == []
    assert questions.fold_problems({"Q002": "answered by E003"}, {"Q001"}) == []
    assert questions.fold_problems({"Q002": "folded into Q009"}, {"Q001"}) == \
        ["Q002 folded into Q009, which is not an open question"]
    assert questions.fold_problems({"Q002": "folded into Q003", "Q003": "folded into Q001"},
                                   {"Q001"}) == \
        ["Q002 folded into Q003, which is not an open question"]


@pytest.fixture
def tree(tmp_path, monkeypatch):
    """A kit tree of one open question, Q001, that the checker reads in place of the real one."""
    import evidence
    for name, val in (("ROOT", tmp_path), ("DIR", tmp_path / "questions"),
                      ("DOC", tmp_path / "doc" / "open_questions.md")):
        monkeypatch.setattr(questions, name, val)
    monkeypatch.setattr(evidence, "DIR", tmp_path / "evidence")
    monkeypatch.setattr(evidence, "glossary_terms", lambda: {"CR_X"})
    (tmp_path / "evidence" / "isp").mkdir(parents=True)
    (tmp_path / "evidence" / "isp" / "E001-x.md").write_text("x")
    record(tmp_path / "questions")
    monkeypatch.setattr(questions, "RETIRED", {})
    assert questions.main([]) == 0
    return tmp_path


def test_main_passes_a_consistent_tree(tree):
    assert questions.main(["--check"]) == 0


def test_main_fails_on_a_fold_to_a_retired_target(tree, monkeypatch):
    monkeypatch.setattr(questions, "RETIRED", {"Q002": "folded into Q009"})
    assert questions.main(["--check"]) == 1
    monkeypatch.setattr(questions, "RETIRED", {"Q002": "folded into Q001"})
    assert questions.main(["--check"]) == 0


def test_main_fails_on_a_malformed_retirement(tree, monkeypatch):
    monkeypatch.setattr(questions, "RETIRED", {"Q002": "it was hard"})
    assert questions.main(["--check"]) == 1


def test_main_fails_on_a_citation_of_a_folded_question(tree, monkeypatch):
    monkeypatch.setattr(questions, "RETIRED", {"Q002": "folded into Q001"})
    note = tree / "doc" / "note.md"
    note.write_text("Q001 holds what Q002 asked.\n")
    assert questions.main(["--check"]) == 1
    note.write_text("Q001 holds what the former Q00x asked.\n")
    assert questions.main(["--check"]) == 0
    (tree / "evidence" / "isp" / "E001-x.md").write_text("see Q002")
    assert questions.main(["--check"]) == 1


def test_an_answered_question_is_retired_and_cited_only_as_answered(monkeypatch):
    monkeypatch.setattr(questions, "RETIRED", {"Q002": "answered by E003"})
    assert questions.reference_problems("see Q001 and Q002", {"Q001"}) == \
        ["Q002 is answered (answered by E003): cite the answer"]
    assert questions.reference_problems("Q009", {"Q001"}) == ["Q009: no such question"]
    with pytest.raises(ValueError):
        questions.check_retired({"Q002": "it was hard"})


def test_records_up_to_the_answer_may_cite_an_answered_question(monkeypatch):
    """A record written before or with the answer keeps its citation (landed records change
    only by corrections); a later record, a doc or a glossary term cites the answer."""
    monkeypatch.setattr(questions, "RETIRED", {"Q002": "answered by E003"})
    assert questions.reference_problems("Q002", {"Q001"}, record="E001") == []
    assert questions.reference_problems("Q002", {"Q001"}, record="E003") == []
    assert questions.reference_problems("Q002", {"Q001"}, record="E004") == \
        ["Q002 is answered (answered by E003): cite the answer"]
    assert questions.reference_problems("Q002", {"Q001"}) == \
        ["Q002 is answered (answered by E003): cite the answer"]


def test_main_lets_earlier_records_cite_an_answered_question(tree, monkeypatch):
    monkeypatch.setattr(questions, "RETIRED", {"Q002": "answered by E003"})
    (tree / "evidence" / "isp" / "E002-x.md").write_text("see Q002")
    assert questions.main(["--check"]) == 0
    (tree / "evidence" / "isp" / "E004-x.md").write_text("see Q002")
    assert questions.main(["--check"]) == 1


def test_main_leaves_the_generated_evidence_log_to_the_records(tree, monkeypatch):
    """doc/evidence_log.md copies the records' claims; their citations are checked in the
    records themselves."""
    monkeypatch.setattr(questions, "RETIRED", {"Q002": "answered by E003"})
    (tree / "evidence" / "isp" / "E002-x.md").write_text("see Q002")
    (tree / "doc" / "evidence_log.md").write_text("- `E002` see Q002\n")
    assert questions.main(["--check"]) == 0
    (tree / "doc" / "other.md").write_text("see Q002\n")
    assert questions.main(["--check"]) == 1


def test_records_up_to_a_late_fold_may_cite_the_folded_question(monkeypatch):
    """A fold made after records cited the question ("folded into Q<nnn> after E<nnn>") lets
    the records up to that one keep their citation; a later record or a doc cites the target."""
    monkeypatch.setattr(questions, "RETIRED", {"Q002": "folded into Q001 after E003"})
    assert questions.reference_problems("Q002", {"Q001"}, record="E002") == []
    assert questions.reference_problems("Q002", {"Q001"}, record="E003") == []
    assert questions.reference_problems("Q002", {"Q001"}, record="E004") == \
        ["Q002 was folded into Q001 after E003: cite Q001"]
    assert questions.reference_problems("Q002", {"Q001"}) == \
        ["Q002 was folded into Q001 after E003: cite Q001"]


def test_a_plain_fold_is_still_never_citable(monkeypatch):
    monkeypatch.setattr(questions, "RETIRED", {"Q002": "folded into Q001"})
    assert questions.reference_problems("Q002", {"Q001"}, record="E001") == \
        ["Q002 was folded into Q001: cite Q001"]


def test_a_late_fold_names_an_open_target_and_a_record(monkeypatch):
    questions.check_retired({"Q002": "folded into Q001 after E003"})
    with pytest.raises(ValueError):
        questions.check_retired({"Q002": "folded into Q001 after Q003"})
    assert questions.fold_problems({"Q002": "folded into Q001 after E003"}, {"Q001"}) == []
    assert questions.fold_problems({"Q002": "folded into Q009 after E003"}, {"Q001"}) == \
        ["Q002 folded into Q009 after E003, which is not an open question"]


def test_main_lets_earlier_records_cite_a_late_fold(tree, monkeypatch):
    monkeypatch.setattr(questions, "RETIRED", {"Q002": "folded into Q001 after E003"})
    (tree / "evidence" / "isp" / "E002-x.md").write_text("see Q002")
    assert questions.main(["--check"]) == 0
    (tree / "evidence" / "isp" / "E004-x.md").write_text("see Q002")
    assert questions.main(["--check"]) == 1


def test_a_decided_question_is_retired_and_stays_citable(monkeypatch):
    monkeypatch.setattr(questions, "RETIRED", {"Q002": "decided in doc/specs/x.md"})
    assert questions.reference_problems("see Q001 and Q002", {"Q001"}) == []
    questions.check_retired({"Q002": "decided in doc/specs/x.md"})
    for why in ("decided in x", "decided", "decided in doc/x.md and more"):
        with pytest.raises(ValueError):
            questions.check_retired({"Q002": why})


def test_main_fails_when_the_decision_does_not_name_the_question(tree, monkeypatch):
    monkeypatch.setattr(questions, "RETIRED", {"Q002": "decided in doc/specs/x.md"})
    assert questions.main(["--check"]) == 1          # no such file
    (tree / "doc" / "specs").mkdir(parents=True)
    (tree / "doc" / "specs" / "x.md").write_text("A decision about nothing.\n")
    assert questions.main(["--check"]) == 1          # does not name Q002
    (tree / "doc" / "specs" / "x.md").write_text("Decision (Q002): accept what fits.\n")
    assert questions.main(["--check"]) == 0
    (tree / "evidence" / "isp" / "E001-x.md").write_text("see Q002")
    assert questions.main(["--check"]) == 0          # a decided question is still cited


def test_the_view_lists_every_question_by_unit(tmp_path):
    p = record(tmp_path)
    text = questions.render([questions.parse(p)])
    assert "\n### isp\n" in text and "`Q001`" in text and "what does the example bit do?" in text


def test_the_view_separates_the_work_queue_from_the_parked_questions(tmp_path):
    def one(i, kind, value=None):
        v = f'value = "{value}"\n' if value else ""
        return questions.parse(record(tmp_path, GOOD.replace(
            'id = "Q001"', f'id = "{i}"').replace('kind = "hw"\nvalue = "medium"\n',
                                                   f'kind = "{kind}"\n{v}'),
            name=f"{i}-example-bit.md"))
    text = questions.render([one("Q001", "hw", "high"), one("Q002", "hw"), one("Q003", "fw"),
                             one("Q004", "kernel"), one("Q005", "hw", "low")])
    queue, _, parked = text.partition("## Parked")
    assert "## Work queue" in queue and "## Parked" in text
    assert "`Q001` (phase 10, hw, high)" in queue and "`Q005` (phase 10, hw, low)" in queue
    assert "`Q002` (phase 10, hw)" in queue
    assert "`Q003`" not in queue and "`Q004`" not in queue and "`Q001`" not in parked
    assert "`Q003` (phase 10, fw)" in parked and "`Q004` (phase 10, kernel)" in parked
    assert "5 open: 3 hw (high 1, medium 0, low 1, unrated 1), 1 fw, 1 kernel" in text
    assert text.index("### closed firmware") < text.index("### kernel")


# --- the repository's questions ---------------------------------------------------------------

def test_the_questions_are_well_formed():
    import evidence
    ids = {p.name[:4] for p in evidence.DIR.glob("*/E*.md")}
    terms = evidence.glossary_terms()
    bad = {p.name: m for p in questions.files() if (m := questions.problems(p, ids, terms))}
    assert not bad, bad
    assert not questions.misplaced()
    questions.check_retired(questions.RETIRED)
    assert not questions.fold_problems(questions.RETIRED,
                                       {p.name[:4] for p in questions.files()})
    qs = [questions.parse(p) for p in questions.files()]
    assert not [q["id"] for q in qs if q["kind"] == "hw" and "value" not in q]


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
            rec = p.name[:4] if d == "evidence" else None
            gen = (questions.DOC, questions.ROOT / "doc" / "evidence_log.md")
            if p not in gen and (m := questions.reference_problems(p.read_text(),
                                                                         open_ids, rec)):
                bad[str(p.relative_to(questions.ROOT))] = m
    assert not bad, bad
