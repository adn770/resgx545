# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The glossary (glossary/<group>/<NAME>.toml, rendered as doc/glossary.md): every name the
project may use for an SGX545 register, structure field, state-word field, flag, function, unit
or concept, each with the open sources that support it (HACKING.md, "Sources"). Only legal
sources count: open SGX code, the strings and exported symbols of our own Cedarview package,
Imagination's open Rogue code (as an analogue), Imagination's public documents and patents.
Nothing read from inside a closed binary is a source of a name; a string or exported symbol seen
from outside, as a black box, may back one (tier 2)."""
import os
import pathlib
import re
import tomllib

import pytest

import glossary

ROOT = pathlib.Path(__file__).resolve().parents[2]


@pytest.fixture
def rows():
    """The glossary's rows; the terms enter phase by phase, so a tree may have none yet."""
    rs = glossary.load()
    if not rs:
        pytest.skip("no glossary terms yet")
    return rs


def test_rows_are_well_formed(rows):
    for r in rows:
        assert list(r) == glossary.COLUMNS, r
        assert r["status"] in glossary.STATUSES, r
        assert all(v and v == v.strip() for v in r.values()), r     # "-" for nothing
        assert r["term"] and r["meaning"] and r["citation"], r
        assert r["kind"] in glossary.KINDS, r
        assert r["tier"] in glossary.TIERS, r
        assert r["licence"] in glossary.LICENCES, r
        assert r["source"] in glossary.SOURCES, r


def test_tiers_match_their_sources():
    for r in glossary.load():
        assert glossary.SOURCES[r["source"]] == r["tier"] or \
            (r["tier"] == "1c" and glossary.SOURCES[r["source"]] == "1"), r


def test_our_own_terms_point_at_our_evidence():
    """Tier "ours": a thing no open source names, named by us after what we measured; the
    citation names the evidence records that show it (E<nnn>), or a file of this repository
    (a probe, a label file, a capture tool)."""
    records = {p.name[:4] for p in (ROOT / "evidence").glob("*/E*.md")}
    for r in glossary.load():
        if r["tier"] == "ours":
            assert r["source"] == "resgx545" and r["licence"] == "MIT", r
            ids = re.findall(r"\bE\d{3}\b", r["citation"])
            if ids:
                assert set(ids) <= records, r
            else:
                path = r["citation"].split(":")[0].split(" ")[0].split("#")[0]
                assert (ROOT / path).exists(), r
            assert "[infer]" in r["meaning"] or "[infer]" in r["evidence"], r


def test_rows_cite_a_recorded_source():
    """Every row's source is a record under cites/: a closed binary backs a name only as a
    string or exported symbol of our own package, seen as a black box (tier 2)."""
    cites = glossary.cites()
    for r in glossary.load():
        assert r["source"] in cites, r


def test_every_row_says_where_it_applies():
    for r in glossary.load():
        assert r["sgx545"], r          # "-" for a concept
        if r["kind"] == "register" and r["tier"] in ("1", "1c") and r["sgx545"][:2] == "0x":
            assert re.fullmatch(r"0x[0-9a-f]{4}", r["sgx545"]), r


SOURCE_PREFIX = re.compile(r"(?i:(^|[._])(EUR|EURASIA|PSB|ROGUE|SGXMKIF|PVRSRV))(_|[A-Z]|$)"
                           r"|(^|[._])(ui64|ui32|ui16|ui8|psz)"
                           r"(_|[A-Z]|$)")


def test_our_terms_carry_no_source_prefix():
    for r in glossary.load():
        if r["kind"] != "function":           # exported symbols keep their exact spelling
            assert not SOURCE_PREFIX.search(r["name"]), r


def test_our_terms_follow_the_case_of_their_kind():
    upper = re.compile(r"[A-Z0-9_]+(\.[A-Z0-9_]+)?")
    lower = re.compile(r"[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)?")
    for r in glossary.load():
        if r["kind"] in ("unit", "concept", "function"):
            continue
        if r["group"] in ("structs", "registers") and r["kind"] in ("struct", "field"):  # C structs
            assert lower.fullmatch(r["name"]), r
        else:
            assert upper.fullmatch(r["name"]), r


def test_registers_and_their_fields_are_control_registers():
    for r in glossary.load():
        if r["kind"] == "register" or (r["group"] == "registers" and r["kind"] in ("bitfield",
                                                                                 "flag")):
            assert re.fullmatch(r"CR_[A-Z0-9_]+(\.[A-Z0-9_]+)?", r["name"]), r


def test_one_term_per_register_and_structure_field():
    seen = {}
    for r in glossary.load():
        key = None
        if r["group"] == "registers" and r["kind"] == "register" and r["sgx545"].startswith("0x"):
            key = r["sgx545"]
        elif r["group"] == "structs" and r["kind"] == "field" and "+0x" in r["sgx545"]:
            key = r["sgx545"]
        if key:
            assert seen.setdefault(key, r["name"]) == r["name"], r


def test_the_document_is_rendered_from_the_records():
    """With no terms and no document there is nothing to compare; otherwise the document must
    be the rendering (a missing document, or one left over from removed terms, is stale)."""
    rows, doc = glossary.load(), glossary.DOC
    if not rows and not doc.exists():
        pytest.skip("no glossary terms and no document yet")
    assert doc.exists() and doc.read_text() == glossary.render(rows)


def test_the_document_is_written_where_doc_does_not_exist(tmp_path, monkeypatch):
    monkeypatch.setattr(glossary, "DOC", tmp_path / "doc" / "glossary.md")
    assert glossary.main(["--check"]) == 1          # a missing document is stale
    assert glossary.main([]) == 0
    assert glossary.DOC.read_text() == glossary.render(glossary.load())
    assert glossary.main(["--check"]) == 0


def test_the_render_says_what_a_closed_binary_may_back():
    text = " ".join(glossary.render([]).split())
    assert "Nothing read from inside a closed binary is a source of a name; a string or " \
        "exported symbol seen from outside, as a black box, may back one (tier 2; " \
        "HACKING.md, \"Sources\")." in text
    assert "- **2**: a string or exported symbol of our own Cedarview package, observed as a " \
        "black box." in text
    assert "2o" not in glossary.TIERS and "2o" not in glossary.ORDER


def test_the_document_lines_fit_100_columns():
    for n, line in enumerate(glossary.render(glossary.load()).splitlines(), 1):
        assert len(line) <= 100, (n, line)


# --- the records: one file per term and its fields --------------------------------------------

def _files():
    return sorted(glossary.DIR.glob("*/*.toml"))


def test_one_file_per_term_and_its_fields():
    """glossary/<group>/<NAME>.toml holds the term NAME and its fields NAME.FIELD; a unit or
    concept, named in words, has a file of its own. Names that differ only in case share a
    file, so the layout works on case-insensitive file systems."""
    stems: dict[tuple[str, str], str] = {}
    for f in _files():
        group = f.parent.name
        assert group in dict(glossary.GROUPS), f
        assert stems.setdefault((group, f.stem.lower()), f.stem) == f.stem, f
        terms = tomllib.loads(f.read_text())["term"]
        assert terms, f
        for t in terms:
            assert glossary.stem(group, t["name"]).lower() == f.stem.lower(), (f, t["name"])


def test_a_term_lists_its_sources():
    for f in _files():
        for t in tomllib.loads(f.read_text())["term"]:
            assert list(t) == ["id", "name", "status", "source"], (f, t)
            assert t["source"], (f, t["name"])
            for s in t["source"]:
                assert list(s) == glossary.SOURCE_KEYS, (f, t["name"], s)


def test_status_says_how_far_a_meaning_is_established():
    """named: the meaning is established; inferred: our best reading, not confirmed (the
    rendered glossary marks it); unset: no reading yet. A neutral name (REG_xxxx, BITSn) is a
    property of the name, not a status."""
    for r in glossary.load():
        assert not r["meaning"].startswith("inferred reading"), r
        unset = bool(glossary.UNSET.search(r["meaning"]))
        assert unset == (r["status"] == "unset"), r


def test_write_then_load_gives_the_rows_back(tmp_path):
    def row(group, name, status="named", tier="1", meaning="m", kind="register"):
        return dict(group=group, name=name, status=status, term="T_" + name, kind=kind,
                    sgx545="-", meaning=meaning, tier=tier, source="sgx545-ce",
                    citation="c", licence="GPL-2.0", evidence="e \\ \"q\"")
    rows = [row("registers", "CR_A"), row("registers", "CR_A.F", kind="bitfield"),
            row("registers", "CR_A", tier="3"),
            row("structs", "misc_info", kind="struct"),
            row("structs", "MISC_INFO.REQUEST", kind="enum"),
            row("units", "Bus Interface (BIF)", kind="unit"),
            row("units", "sub-ISP/TSP", status="inferred", kind="unit")]
    glossary.assign_ids(rows)
    glossary.write(rows, tmp_path)
    assert sorted(p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob("*.toml")) == [
        "registers/CR_A.toml", "structs/misc_info.toml", "units/Bus-Interface-BIF.toml",
        "units/sub-ISP-TSP.toml"]
    key = lambda r: tuple(r[k] for k in glossary.COLUMNS)
    assert sorted(glossary.load(tmp_path), key=key) == sorted(rows, key=key)


def test_an_inferred_reading_renders_as_one():
    rows = [dict(group="words", id="G0007", name="DOUTU1.BIT2", status="inferred",
                 term="DOUTU1.BIT2",
                 kind="bitfield", sgx545="-", meaning="a hint", tier="ours",
                 source="resgx545", citation="c", licence="MIT", evidence="e")]
    assert "`DOUTU1.BIT2` G0007: inferred reading (unconfirmed): a hint." in glossary.render(rows)


# --- the sources: one record per external source under cites/ ----------------------------------

CITE_KEYS = ["title", "tier", "kind", "licences", "root", "upstream", "pin", "locator"]


def test_every_source_has_a_record():
    used = {r["source"] for r in glossary.load()}
    if not used:
        pytest.skip("no glossary terms yet")
    have = {p.stem for p in glossary.CITES.glob("*.toml")}
    assert used <= have, sorted(used - have)
    assert have <= used | {"resgx545"}, sorted(have - used)   # no source nobody cites


def test_a_source_record_says_what_it_is_and_how_to_find_it():
    for p in sorted(glossary.CITES.glob("*.toml")):
        c = tomllib.loads(p.read_text())
        assert list(c) == CITE_KEYS, p
        assert c["tier"] in glossary.TIERS - {"1c"}, p
        assert c["kind"] in {"tree", "document", "patent", "package", "project"}, p
        assert c["licences"] and set(c["licences"]) <= glossary.LICENCES, p
        assert all(isinstance(c[k], str) and c[k] for k in CITE_KEYS if k != "licences"), p


def test_a_source_record_points_upstream_not_at_our_local_copies():
    """Readers have none of our local copies: a source's root names the part of the upstream
    it covers (or the PDF), and its locator the portable form its citation records use."""
    for p in sorted(glossary.CITES.glob("*.toml")):
        c = tomllib.loads(p.read_text())
        if c["kind"] == "project":
            continue
        assert c["root"] not in ("linux", "mesa") and not c["root"].startswith("/"), p
        assert ".txt:" not in c["locator"] and not c["locator"].startswith("/"), p
        assert c["upstream"].startswith("https://"), p


def test_external_rows_cite_a_citation_record():
    """A row of an external source cites its citation record (citations/<source>/C<nnnn>-*.md);
    our own rows cite evidence records or repository files directly."""
    recs = _citations()
    for r in glossary.load():
        if glossary.cites()[r["source"]]["kind"] != "project":
            assert re.fullmatch(r"C\d{4}", r["citation"]) and r["citation"] in recs, r
            assert recs[r["citation"]]["source"] == r["source"], r


def test_rows_agree_with_their_source_record():
    cites = glossary.cites()
    for r in glossary.load():
        c = cites[r["source"]]
        assert r["licence"] in c["licences"], r
        assert r["tier"] == c["tier"] or (r["tier"] == "1c" and c["tier"] == "1"), r


# The Cedarview package's libraries stay outside every repository: name their directory.
CDV_LIBS = pathlib.Path(os.environ.get("RESGX545_CDV_LIBS", "/nonexistent"))


def _citations():
    import sys
    sys.path.insert(0, str(ROOT / "tools" / "records"))
    import citations
    return citations.load()


def test_cedarview_rows_cite_a_string_or_export_of_a_library():
    """Tier 2: the term is a string or exported symbol of one of our Cedarview package's
    libraries; the row's citation record names which, as string@<lib> or export@<lib>, and
    quotes the term itself."""
    recs = _citations()
    for r in glossary.load():
        if r["tier"] == "2":
            c = recs[r["citation"]]
            assert re.fullmatch(r"(string|export)@lib\w+\.so\.1\.7\.862890", c["locator"]), r
            assert c["quote"] == r["term"], r


def test_cedarview_terms_occur_in_their_library():
    """Black-box check of the bytes: the term occurs in the cited library (skips without the
    package, which stays outside the repository)."""
    if not CDV_LIBS.is_dir():
        pytest.skip("no Cedarview libraries (RESGX545_CDV_LIBS)")
    recs = _citations()
    data: dict[str, bytes] = {}
    for r in glossary.load():
        if r["tier"] == "2":
            lib = recs[r["citation"]]["locator"].split("@")[1]
            data.setdefault(lib, (CDV_LIBS / lib).read_bytes())
            assert r["term"].encode() in data[lib], r


# --- numbered ids: G<nnnn> per term, assigned once ------------------------------------------------

def test_every_term_has_one_id_of_its_own():
    """Specs cite glossary entries as G<nnnn>; the id is per term (one file holds a term and
    its fields), shared by all its sources, never reused."""
    ids: dict[str, tuple[str, str]] = {}
    for r in glossary.load():
        assert re.fullmatch(r"G\d{4}", r["id"]), r
        assert ids.setdefault(r["id"], (r["group"], r["name"])) == (r["group"], r["name"]), r


def test_new_terms_get_the_next_ids_and_old_ones_keep_theirs():
    rows = [dict(group="words", id="G0005", name="A"), dict(group="words", id="", name="B"),
            dict(group="words", id="", name="B"), dict(group="units", id="", name="c")]
    glossary.assign_ids(rows)
    assert [r["id"] for r in rows] == ["G0005", "G0006", "G0006", "G0007"]


# --- the scripts ----------------------------------------------------------------------------------

def test_scripts_say_how_to_run_them():
    """A script has a shebang and its docstring's usage runs it as python3 tools/<dir>/<name>."""
    for d in ("records", "clean-room"):
        for p in sorted((ROOT / "tools" / d).glob("*.py")):
            text = p.read_text()
            if p.name.startswith("test_") or "__main__" not in text:
                continue
            assert text.startswith("#!/usr/bin/env python3\n"), p
            assert f"python3 tools/{d}/{p.name}" in text, p
