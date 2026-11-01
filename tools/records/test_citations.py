# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""citations.py: the citation records' format, and the glossary's references to them."""
import re
import sys

import pytest

import citations

CITES = {
    "example-tree": {"kind": "tree", "upstream": "https://github.com/o/example-tree",
                  "pin": "0123456789abcdef0123456789abcdef01234567"},
    "example-doc": {"kind": "document", "upstream": "https://example.org/doc.pdf", "pin": "p"},
    "patent-US1": {"kind": "patent", "upstream": "https://patents.google.com/patent/US1B2/en",
                   "pin": "US1B2"},
    "example-pkg": {"kind": "package", "upstream": "https://example.org/pkg (pkg.tar)",
                   "pin": "p"},
    "resgx545": {"kind": "project", "upstream": "-", "pin": "-"},
}

LINK = ("https://github.com/o/example-tree/blob/0123456789abcdef0123456789abcdef01234567/"
        "src/example/regs.h#L12")
GOOD = f'''+++
id = "C0001"
source = "example-tree"
locator = "src/example/regs.h:12"
link = "{LINK}"
quote = "#define EXAMPLE_CR_CTL 0x0000"
terms = ["CR_CTL"]
+++

`regs.h` defines the register's offset.
'''


def record(tmp_path, text=GOOD, source="example-tree", name="C0001-cr-ctl.md"):
    p = tmp_path / source / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)
    return p


def problems(p, terms=("CR_CTL",)):
    return citations.problems(p, CITES, set(terms))


def test_a_well_formed_record_passes(tmp_path):
    assert problems(record(tmp_path)) == []


def test_the_keys_come_in_order(tmp_path):
    text = GOOD.replace('terms = ["CR_CTL"]\n', "").replace(
        'source = "example-tree"\n', 'source = "example-tree"\nterms = ["CR_CTL"]\n')
    assert any("keys" in m for m in problems(record(tmp_path, text)))


def test_missing_front_matter_is_reported(tmp_path):
    assert problems(record(tmp_path, "just prose\n"))


def test_the_record_agrees_with_its_place(tmp_path):
    p = record(tmp_path, name="C0002-cr-ctl.md")
    assert "id does not match the file name" in problems(p)
    p = record(tmp_path, source="other-tree")
    assert "source does not match the directory" in problems(p)
    p = record(tmp_path, name="c1-ctl.md")
    assert "file name is not C<nnnn>-<slug>.md" in problems(p)


def test_the_source_is_an_external_record(tmp_path):
    p = record(tmp_path, GOOD.replace('"example-tree"', '"nowhere"'), source="nowhere")
    assert any("not a cites record" in m for m in problems(p))
    p = record(tmp_path, GOOD.replace('"example-tree"', '"resgx545"'), source="resgx545")
    assert any("our own evidence" in m for m in problems(p))


def test_the_quote_is_one_short_line(tmp_path):
    p = record(tmp_path, GOOD.replace("0x0000", "0x0000\\nmore"))
    assert "quote is not one line" in problems(p)
    p = record(tmp_path, GOOD.replace("0x0000", "0" * 200))
    assert any("quote is longer than 200" in m for m in problems(p))
    p = record(tmp_path, GOOD.replace('"#define EXAMPLE_CR_CTL 0x0000"', '""'))
    assert "quote empty" in problems(p)


def test_a_tree_locator_is_a_path_and_line_and_the_link_points_there(tmp_path):
    p = record(tmp_path, GOOD.replace("regs.h:12", "regs.h"))
    assert any("locator" in m for m in problems(p))
    p = record(tmp_path, GOOD.replace("#L12", "#L13"))
    assert any("link" in m for m in problems(p))
    p = record(tmp_path, GOOD.replace("0123456789abcdef0123456789abcdef01234567/", "main/"))
    assert any("link" in m for m in problems(p))
    p = record(tmp_path, GOOD.replace('"src/example', '"example-tree/src/example'))
    assert any("link" in m for m in problems(p))


def test_document_patent_and_package_locators(tmp_path):
    doc = GOOD.replace('"example-tree"', '"example-doc"').replace(
        "src/example/regs.h:12", "page 14").replace(
        f'"{LINK}"', '"https://example.org/doc.pdf#page=14"')
    assert problems(record(tmp_path, doc, source="example-doc")) == []
    bad = doc.replace("#page=14", "#page=15")
    assert any("link" in m for m in problems(record(tmp_path, bad, source="example-doc")))
    pat = doc.replace('"example-doc"', '"patent-US1"').replace(
        "https://example.org/doc.pdf#page=14", "https://patents.google.com/patent/US1B2/en")
    for loc in ("col 3:line 12", "[para 0020]", "page 4"):
        p = record(tmp_path, pat.replace("page 14", loc), source="patent-US1")
        assert problems(p) == [], loc
    p = record(tmp_path, pat.replace("page 14", "US1B2.txt:504"), source="patent-US1")
    assert any("locator" in m for m in problems(p))
    pkg = doc.replace('"example-doc"', '"example-pkg"').replace(
        "https://example.org/doc.pdf#page=14", "https://example.org/pkg").replace(
        "page 14", "string@libexample.so.1.7.862890")
    assert problems(record(tmp_path, pkg, source="example-pkg")) == []
    p = record(tmp_path, pkg.replace("string@", "strings in "), source="example-pkg")
    assert any("locator" in m for m in problems(p))


def test_terms_must_be_glossary_names_and_prose_is_required(tmp_path):
    assert any("not in the glossary" in m for m in problems(record(tmp_path), terms=()))
    p = record(tmp_path, GOOD.split("+++\n\n")[0] + "+++\n")
    assert "no prose" in problems(p)
    p = record(tmp_path, GOOD.replace('["CR_CTL"]', "[]"))
    assert "terms empty" in problems(p)


def test_a_retired_id_is_not_reused(tmp_path, monkeypatch):
    monkeypatch.setitem(citations.RETIRED, "C0001", "a test")
    assert any("id is retired" in m for m in problems(record(tmp_path)))


def test_cross_references_with_the_glossary():
    recs = {"C0001": {"source": "s", "terms": ["A", "B"]},
            "C0002": {"source": "s", "terms": ["C"]}}
    rows = [dict(name="A", source="s", citation="C0001"),
            dict(name="B", source="s", citation="C0001"),
            dict(name="C", source="t", citation="C0002"),
            dict(name="D", source="s", citation="C0003"),
            dict(name="E", source="resgx545", citation="E001")]
    msgs = " ".join(citations.crossref(recs, rows, external={"s", "t"}))
    assert "C0003" in msgs and "does not resolve" in msgs
    assert "C0002" in msgs and "source" in msgs
    assert "E001" not in msgs
    recs["C0004"] = {"source": "s", "terms": ["A"]}
    assert any("C0004" in m and "cited by no glossary row" in m
               for m in citations.crossref(recs, rows[:2], external={"s"}))
    recs = {"C0001": {"source": "s", "terms": ["A"]}}
    assert any("terms" in m for m in citations.crossref(recs, rows[:2], external={"s"}))


# --- the repository's records ----------------------------------------------------------------

def _glossary():
    sys.path.insert(0, str(citations.ROOT / "tools" / "clean-room"))
    import glossary
    return glossary


def _records():
    paths = sorted(citations.DIR.glob("*/*.md"))
    if not paths:
        pytest.skip("no citation records yet")
    return paths


def test_the_records_are_well_formed():
    g = _glossary()
    cites, terms = g.cites(), {r["name"] for r in g.load()}
    paths = _records()
    bad = {p.name: m for p in paths if (m := citations.problems(p, cites, terms))}
    assert not bad, bad


def test_ids_are_unique():
    ids = [p.name.split("-")[0] for p in _records()]
    assert len(ids) == len(set(ids))


def test_every_external_row_cites_a_record_and_every_record_is_cited():
    g = _glossary()
    cites, rows = g.cites(), g.load()
    if not rows:
        pytest.skip("no glossary terms yet")
    external = {k for k, c in cites.items() if c["kind"] != "project"}
    msgs = citations.crossref(citations.load(), rows, external)
    assert not msgs, msgs[:20]


def test_external_rows_cite_by_id():
    g = _glossary()
    cites, rows = g.cites(), g.load()
    if not rows:
        pytest.skip("no glossary terms yet")
    for r in rows:
        if cites[r["source"]]["kind"] != "project":
            assert re.fullmatch(r"C\d{4}", r["citation"]), r


def test_main_reports_nothing():
    assert citations.main([]) == 0


def test_a_tree_without_records_or_terms_passes(tmp_path, monkeypatch):
    class NoGlossary:          # a tree before any phase names a term
        @staticmethod
        def cites():
            return {}

        @staticmethod
        def load():
            return []
    monkeypatch.setattr(citations, "DIR", tmp_path / "no-citations")
    monkeypatch.setattr(citations, "_glossary", lambda: NoGlossary)
    assert citations.load() == {}
    assert citations.main([]) == 0
