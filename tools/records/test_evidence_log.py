# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""evidence_log.py: the evidence log is generated from the evidence records' front matter."""
import evidence_log

A = dict(id="E001", claim="a first claim", unit="dpm", method="a method", tiers=["HW", "RE"],
         date="2026-10-28", data=["dpm-example", "dpm-other:part"], terms=["CR_X"])
B = dict(id="E002", claim="a second claim", unit="firmware", method="another", tiers=["CAP"],
         date="2026-10-27", data=[], terms=[])
C = dict(id="E003", claim="a third claim", unit="dpm", method="third", tiers=["HW"],
         date="2026-10-28", data=["dpm-example"], terms=[])


def test_the_view_is_current():
    """The document, when the tree has records, is exactly the rendering."""
    recs = evidence_log.records()
    if not recs and not evidence_log.DOC.exists():
        return
    assert evidence_log.DOC.read_text() == evidence_log.render(recs)


def test_chronology_is_by_date_then_id():
    text = evidence_log.render([A, B, C])
    chrono = text.split("## By unit")[0]
    assert chrono.index("### 2026-10-27") < chrono.index("### 2026-10-28")
    assert chrono.index("E001") < chrono.index("E003")


def test_each_entry_gives_claim_unit_tiers_and_data():
    text = evidence_log.render([A, B])
    assert "`E001` a first claim." in text
    assert "dpm; HW, RE; data: `dpm-example`, `dpm-other:part`" in text
    assert "firmware; CAP; data: none" in text


def test_by_unit_groups_in_unit_order():
    text = evidence_log.render([A, B, C]).split("## By unit")[1]
    assert text.index("### dpm") < text.index("### firmware")
    assert "E001, E003" in text


def test_the_rendering_is_deterministic_and_input_order_free():
    assert evidence_log.render([A, B, C]) == evidence_log.render([C, B, A])


def test_lines_are_wrapped_and_clean():
    long = dict(A, claim="word " * 60)
    for line in evidence_log.render([long]).splitlines():
        assert len(line) <= 100 and line == line.rstrip()


def test_no_records_renders_an_empty_log():
    assert "No evidence records yet." in evidence_log.render([])


def test_chronology_and_units_order_e1000_after_e999():
    a = dict(A, id="E999", date="2026-11-13")
    b = dict(B, id="E1000", date="2026-11-13", unit="dpm")
    text = evidence_log.render([b, a])
    assert text.index("E999") < text.index("E1000")
    assert "E999, E1000" in text.split("## By unit")[1]
