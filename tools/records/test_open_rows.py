# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""open_rows.py: the open rows are generated from the glossary's inferred terms."""
import pytest

import open_rows


def test_the_view_is_current():
    """With no inferred terms and no document there is nothing to compare; otherwise the
    document must be the rendering, even an empty one."""
    rows = open_rows.rows()
    if not rows and not open_rows.DOC.exists():
        pytest.skip("no inferred terms and no document yet")
    assert open_rows.DOC.exists() and open_rows.DOC.read_text() == open_rows.render(rows)


def test_every_inferred_term_is_listed_once():
    rows = open_rows.rows()
    if not rows:
        pytest.skip("no inferred terms yet")
    text = open_rows.render(rows)
    terms = {(r["group"], r["name"]) for r in rows}
    assert terms and all(r["status"] == "inferred" for r in rows)
    assert sum(text.count(f"`{r['id']}`") for r in {r["id"]: r for r in rows}.values()) == \
        len({r["id"] for r in rows})


ROW = dict(group="registers", id="G0001", name="CR_UNIT_REG_0000", status="inferred",
           term="CR_UNIT_REG_0000", kind="register", sgx545="0x0000", meaning="a reading",
           tier="ours", source="resgx545", citation="E002", licence="MIT",
           evidence="[HW] E001")


def test_an_entry_gives_its_reading_and_records():
    text = open_rows.render([ROW])
    assert "`G0001` `CR_UNIT_REG_0000` (0x0000): a reading." in text
    assert "E001, E002" in text


def test_main_writes_the_document_where_doc_does_not_exist(tmp_path, monkeypatch):
    monkeypatch.setattr(open_rows, "DOC", tmp_path / "doc" / "open_rows.md")
    monkeypatch.setattr(open_rows, "rows", lambda: [ROW])
    assert open_rows.main(["--check"]) == 1          # a missing document is stale
    assert open_rows.main([]) == 0
    assert open_rows.DOC.read_text() == open_rows.render([ROW])
    assert open_rows.main(["--check"]) == 0


def test_records_past_e999_are_listed_in_numeric_order():
    row = dict(ROW, evidence="E1000 E999 E002", citation="")
    text = open_rows.render([row])
    assert "Evidence: E002, E999, E1000." in text
