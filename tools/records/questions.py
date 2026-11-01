#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Open questions: questions/<unit>/Q<nnn>-<slug>.md, one per file.

A question is Markdown with TOML front matter between `+++` lines:

    +++
    id = "Q001"
    question = "what does the example bit do?"   # one line
    unit = "isp"
    phase = 10                          # the roadmap phase it arose in
    evidence = ["E001"]                 # the records that bear on it so far
    terms = ["CR_X"]                    # glossary terms waiting on it
    +++

    Prose: what is known, what was tried, and what experiment would settle it.

When a question is answered, its file is removed in the commit that adds the evidence record
answering it, and its id is retired in RETIRED ("answered by E<nnn>"), never to be given
again. Specs, evidence records and glossary terms cite a question as Q<nnn>; a retired one may
not be cited, its answer is. doc/open_questions.md is generated from the files.

    python3 tools/records/questions.py [--check]
        check every question and write (--check: compare) doc/open_questions.md
"""
from __future__ import annotations

import pathlib
import re
import sys
import tomllib

import evidence

ROOT = evidence.ROOT
DIR = ROOT / "questions"
DOC = ROOT / "doc" / "open_questions.md"
KEYS = ["id", "question", "unit", "phase", "evidence", "terms"]
RETIRED: dict[str, str] = {     # id -> "answered by E<nnn>"
    "Q015": "answered by E413", "Q018": "answered by E373", "Q022": "answered by E392",
    "Q035": "answered by E407", "Q056": "answered by E366", "Q077": "answered by E379",
    "Q079": "answered by E367", "Q097": "answered by E380", "Q007": "answered by E425",
    "Q061": "answered by E428", "Q009": "answered by E441",
}
NAME = re.compile(r"Q\d{3}-[a-z0-9]+(-[a-z0-9]+)*\.md")
REF = re.compile(r"\bQ\d{3}\b")


def parse(path: pathlib.Path) -> dict:
    """The front matter, with the prose as "body"."""
    fm, body = evidence.parse(path)
    return {**fm, "body": body}


def files() -> list[pathlib.Path]:
    return sorted(DIR.glob("*/Q*.md"))


def misplaced(path: pathlib.Path | None = None) -> list[pathlib.Path]:
    """Files under questions/ that are not questions/<unit>/<name>.md."""
    root = path or DIR
    if not root.is_dir():
        return []
    return [p for p in sorted(root.rglob("*")) if p.is_file() and not p.name.startswith(".")
            and (p.parent.parent != root or p.suffix != ".md")]


def problems(path: pathlib.Path, evidence_ids: set[str], terms: set[str]) -> list[str]:
    """What is wrong with one question (empty when it is well formed)."""
    out = []
    if not NAME.fullmatch(path.name):
        out.append("file name is not Q<nnn>-<slug>.md")
    if path.parent.name not in evidence.UNITS:
        out.append(f"directory {path.parent.name} is not a unit")
    try:
        fm, body = evidence.parse(path)
    except (ValueError, tomllib.TOMLDecodeError) as e:
        return out + [str(e)]
    if list(fm) != KEYS:
        return out + [f"keys {list(fm)} != {KEYS}"]
    for k in ("id", "question", "unit"):
        if not isinstance(fm[k], str) or not fm[k].strip():
            out.append(f"{k} is not a string")
    for k in ("evidence", "terms"):
        if not isinstance(fm[k], list) or not all(isinstance(x, str) for x in fm[k]):
            out.append(f"{k} is not a list of strings")
    if not isinstance(fm["phase"], int) or isinstance(fm["phase"], bool) \
            or not 0 <= fm["phase"] <= 12:
        out.append(f"phase {fm['phase']!r} is not a roadmap phase (0-12)")
    if out:
        return out
    if "\n" in fm["question"]:
        out.append("the question is not one line")
    if fm["id"] != path.name.split("-")[0]:
        out.append("id does not match the file name")
    if fm["id"] in RETIRED:
        out.append(f"id is retired: {RETIRED[fm['id']]}")
    if fm["unit"] != path.parent.name:
        out.append("unit does not match the directory")
    out += [f"evidence {e} does not exist" for e in fm["evidence"] if e not in evidence_ids]
    out += [f"term {t} is not in the glossary" for t in fm["terms"] if t not in terms]
    if not body.strip():
        out.append("no prose")
    return out


def check_retired(retired: dict[str, str]) -> None:
    """A retired question names the record that answered it."""
    for q, why in retired.items():
        if not re.fullmatch(r"Q\d{3}", q) or not re.fullmatch(r"answered by E\d{3}", why):
            raise ValueError(f"{q}: retired as {why!r}, not 'answered by E<nnn>'")


def reference_problems(text: str, open_ids: set[str]) -> list[str]:
    """The Q<nnn> references of a text that do not name an open question."""
    out = []
    for q in dict.fromkeys(REF.findall(text)):
        if q in RETIRED:
            out.append(f"{q} is answered ({RETIRED[q]}): cite the answer")
        elif q not in open_ids:
            out.append(f"{q}: no such question")
    return out


def render(qs: list[dict]) -> str:
    out = ["<!-- SPDX-" "License-Identifier: MIT -->",
           "<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->",
           "# Open questions", "",
           "*Generated from `questions/` by `tools/records/questions.py`; do not edit.*", ""]
    for unit in sorted({q["unit"] for q in qs}):
        out += [f"## {unit}", ""]
        for q in sorted((q for q in qs if q["unit"] == unit), key=lambda q: q["id"]):
            refs = ", ".join(q["evidence"])
            out.append(f"- `{q['id']}` (phase {q['phase']}): {q['question']}"
                       + (f" ({refs})" if refs else ""))
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    a = sys.argv[1:] if argv is None else argv
    ids = {p.name[:4] for p in evidence.DIR.glob("*/E*.md")}
    terms, bad = evidence.glossary_terms(), 0
    for p in files():
        for msg in problems(p, ids, terms):
            print(f"{p.relative_to(ROOT)}: {msg}")
            bad += 1
    for p in misplaced():
        print(f"{p.relative_to(ROOT)}: not questions/<unit>/<name>.md")
        bad += 1
    text = render([parse(p) for p in files()])
    if "--check" in a:
        return 1 if bad or not DOC.exists() or DOC.read_text() != text else 0
    DOC.parent.mkdir(parents=True, exist_ok=True)
    DOC.write_text(text)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
