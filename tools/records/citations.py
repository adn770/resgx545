#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Citation records: citations/<source>/C<nnnn>-<slug>.md, one per distinct external citation.

A glossary row that rests on an external source (cites/<source>.toml, any kind but "project")
cites a record by its id; the record says where in the source the fact is, in a form a reader
without our local copies can follow. Markdown with TOML front matter between `+++` lines:

    +++
    id = "C0001"
    source = "example-tree"
    locator = "src/example/regs.h:12"
    link = "https://github.com/<owner>/<repo>/blob/<pin>/src/example/regs.h#L12"
    quote = "#define EXAMPLE_CR_CTL 0x0000"
    terms = ["CR_CTL"]
    +++

    A short abstract in our own words: what the source says there, and which term it backs.

`locator` depends on the source's kind: a tree's `path:line` relative to the upstream
repository root at the pin; a document's `page N` of the PDF the pin names by hash; a granted
patent's `col C:line L` (else `page N`), an application's `[para NNNN]` (else `page N`); a
package's `string@<lib>` or `export@<lib>`, the quote being the string or symbol itself.
`link` is a deep link at the pin (a tree's blob and line, a document's PDF and page, the
patent's Google Patents page, a package's upstream). `quote` is one verbatim line of at most 200
characters, the one that carries the fact. `terms` are the glossary names that cite the record.
Ids are given once and never reused: a record that is dropped is retired in RETIRED. A tree
without citations/ or without glossary terms yet has nothing to check.

    python3 tools/records/citations.py
        check every record, and the glossary's references to them
"""
from __future__ import annotations

import collections
import pathlib
import re
import sys
import tomllib
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parents[2]
DIR = ROOT / "citations"
KEYS = ["id", "source", "locator", "link", "quote", "terms"]
RETIRED: dict[str, str] = {}
NAME = re.compile(r"C\d{4}-[a-z0-9]+(-[a-z0-9]+)*\.md")
ID = re.compile(r"C\d{4}")
MAX_QUOTE = 200
LIB = r"lib\w+\.so\.1\.7\.862890"
LOCATORS = {
    "tree": re.compile(r"(?P<path>[^\s:]+):(?P<line>[1-9]\d*)"),
    "document": re.compile(r"page (?P<page>[1-9]\d*)"),
    "patent": re.compile(r"col [1-9]\d*:line [1-9]\d*|\[para \d{4}\]|page (?P<page>[1-9]\d*)"),
    "package": re.compile(rf"(string|export)@{LIB}"),
}


def parse(path: pathlib.Path) -> tuple[dict, str]:
    """(front matter, body) of a record."""
    text = path.read_text()
    if not text.startswith("+++\n"):
        raise ValueError(f"{path}: no front matter")
    head, sep, body = text[4:].partition("\n+++\n")
    if not sep:
        raise ValueError(f"{path}: front matter not closed")
    return tomllib.loads(head), body


def tree_link(upstream: str, pin: str, path: str, line: int) -> str:
    """The permalink to a line of a file at the pin, in the form the upstream's host serves."""
    q = urllib.parse.quote(path)
    if "googlesource.com" in upstream:                         # gitiles
        return f"{upstream}/+/{pin}/{q}#{line}"
    if "git.kernel.org" in upstream:                            # cgit
        return f"{upstream}/tree/{q}?id={pin}#n{line}"
    if "gitlab" in upstream:
        return f"{upstream}/-/blob/{pin}/{q}#L{line}"
    return f"{upstream}/blob/{pin}/{q}#L{line}"                # GitHub


def url(upstream: str) -> str:
    """The URL of a source's upstream, without the note that may follow it."""
    return upstream.split()[0]


def _link_problems(fm: dict, cite: dict) -> list[str]:
    kind, m = cite["kind"], LOCATORS[cite["kind"]].fullmatch(fm["locator"])
    if kind == "tree":
        want = tree_link(cite["upstream"], cite["pin"], m["path"], int(m["line"]))
    elif kind == "document":
        want = f"{url(cite['upstream'])}#page={m['page']}"
    else:
        want = url(cite["upstream"])
    return [] if fm["link"] == want else [f"link {fm['link']} != {want}"]


def problems(path: pathlib.Path, cites: dict[str, dict], terms: set[str]) -> list[str]:
    """What is wrong with one record (empty when it is well formed)."""
    out = []
    if not NAME.fullmatch(path.name):
        out.append("file name is not C<nnnn>-<slug>.md")
    try:
        fm, body = parse(path)
    except (ValueError, tomllib.TOMLDecodeError) as e:
        return out + [str(e)]
    if list(fm) != KEYS:
        return out + [f"keys {list(fm)} != {KEYS}"]
    if not all(isinstance(fm[k], str) for k in KEYS[:-1]):
        return out + ["a key other than terms is not a string"]
    if fm["id"] in RETIRED:
        out.append(f"id is retired: {RETIRED[fm['id']]}")
    if not ID.fullmatch(fm["id"]) or fm["id"] != path.name.split("-")[0]:
        out.append("id does not match the file name")
    if fm["source"] != path.parent.name:
        out.append("source does not match the directory")
    cite = cites.get(fm["source"])
    if cite is None:
        return out + [f"source {fm['source']} is not a cites record"]
    if cite["kind"] == "project":
        return out + ["a project source is our own evidence, cited directly"]
    if not LOCATORS[cite["kind"]].fullmatch(fm["locator"]):
        out.append(f"locator {fm['locator']!r} is not a {cite['kind']} locator")
    else:
        out += _link_problems(fm, cite)
    q = fm["quote"]
    if "\n" in q or "\r" in q:
        out.append("quote is not one line")
    if len(q) > MAX_QUOTE:
        out.append(f"quote is longer than {MAX_QUOTE} characters ({len(q)})")
    if not q.strip():
        out.append("quote empty")
    if not isinstance(fm["terms"], list) or not all(isinstance(t, str) for t in fm["terms"]):
        out.append("terms is not a list of strings")
    elif not fm["terms"]:
        out.append("terms empty")
    else:
        unknown = [t for t in fm["terms"] if t not in terms]
        if unknown:
            out.append(f"terms not in the glossary: {unknown}")
    if not body.strip():
        out.append("no prose")
    return out


def load(path: pathlib.Path | None = None) -> dict[str, dict]:
    """The records' front matter by id."""
    files = sorted(pathlib.Path(path or DIR).glob("*/C*.md"))
    return {fm["id"]: fm for fm in (parse(p)[0] for p in files)}


def crossref(records: dict[str, dict], rows: list[dict], external: set[str]) -> list[str]:
    """Where the glossary and the records disagree: a row of an external source that cites no
    record, a record no row cites, or a record whose source or terms are not its rows'."""
    out, cited = [], {}
    for r in rows:
        if r["source"] not in external:
            continue
        rec = records.get(r["citation"])
        if rec is None:
            out.append(f"{r['name']} ({r['source']}): citation {r['citation']} does not resolve")
            continue
        if rec["source"] != r["source"]:
            out.append(f"{r['citation']}: source {rec['source']} != the row's {r['source']} "
                       f"({r['name']})")
        cited.setdefault(r["citation"], set()).add(r["name"])
    for cid, rec in sorted(records.items()):
        if cid not in cited:
            out.append(f"{cid}: cited by no glossary row")
        elif sorted(rec["terms"]) != sorted(cited[cid]):
            out.append(f"{cid}: terms {sorted(rec['terms'])} != the citing rows' "
                       f"{sorted(cited[cid])}")
    return out


def _glossary():
    sys.path.insert(0, str(ROOT / "tools" / "clean-room"))
    import glossary
    return glossary


def main(argv: list[str] | None = None) -> int:
    g = _glossary()
    cites, rows = g.cites(), g.load()
    terms, bad = {r["name"] for r in rows}, 0
    for p in sorted(DIR.glob("*/*.md")):
        for msg in problems(p, cites, terms):
            print(f"{p.relative_to(ROOT)}: {msg}")
            bad += 1
    ids = [p.name.split("-")[0] for p in DIR.glob("*/*.md")]
    for i in sorted(i for i, n in collections.Counter(ids).items() if n > 1):
        print(f"{i}: id given twice")
        bad += 1
    external = {k for k, c in cites.items() if c["kind"] != "project"}
    for msg in crossref(load(), rows, external):
        print(msg)
        bad += 1
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
