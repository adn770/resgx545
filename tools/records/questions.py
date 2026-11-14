#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Open questions: questions/<unit>/Q<nnn>-<slug>.md, one per file.

A question is Markdown with TOML front matter between `+++` lines:

    +++
    id = "Q001"
    question = "what does the example bit do?"   # one line
    unit = "isp"
    kind = "hw"                         # hw, fw or kernel (see below)
    value = "medium"                    # hw only, optional: high, medium or low
    phase = 10                          # the roadmap phase it arose in
    evidence = ["E001"]                 # the records that bear on it so far
    terms = ["CR_X"]                    # glossary terms waiting on it
    +++

    Prose: what is known, what was tried, and what experiment would settle it.

The kind says whose behaviour the open part asks about. The work is hardware knowledge, so
only an hw question is in the work queue: what the SGX545 does, read from registers, memory and
images. An fw question asks about the closed firmware's or the closed driver's own behaviour,
a kernel question about the design of our kernel driver; both stay open, parked. A question
that mixes them is narrowed to its hardware part, or folded into the hardware question that
holds it. The value (high, medium, low) says how much a simulator of the hardware loses
without the answer; only an hw question has one.

When a question is answered, its file is removed in the commit that adds the evidence record
answering it, and its id is retired in RETIRED ("answered by E<nnn>"), never to be given
again. A question folded into another (its hardware open part moved into that question's text,
its evidence into that question's list) is retired as "folded into Q<nnn>": a fold is not an
answer. A question closed by a decision and not by a measurement is retired as "decided in
<doc>.md", a document that names it and states the decision: an answer is not claimed, and the id
stays citable as the name of the decision. Specs, evidence records and glossary terms cite a
question as Q<nnn>; an answered or folded one may not be cited, its answer or the question it was
folded into is, except that the records up to the answering one keep their citations (a landed
record changes only by corrections). A fold made after records cited the question is retired as
"folded into Q<nnn> after E<nnn>", the last record then landed; the records up to it keep their
citations in the same way. doc/open_questions.md is
generated from the files: the work queue (hw), then the parked fw and kernel questions.

    python3 tools/records/questions.py [--check]
        check every question, the retirements (a fold needs an open target) and the Q<nnn>
        citations of evidence, glossary and doc, and write (--check: compare) doc/open_questions.md
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
KEYS = ["id", "question", "unit", "kind", "phase", "evidence", "terms"]
KEYS_HW = KEYS[:4] + ["value"] + KEYS[4:]       # an hw question may carry a value
KINDS = ("hw", "fw", "kernel")
VALUES = ("high", "medium", "low")
PARKED = {"fw": "closed firmware", "kernel": "kernel"}
# id -> "answered by E<nnn>", "folded into Q<nnn>" or "decided in <doc>.md" (a decision, not
# a measurement: the id stays citable and the named document states the decision)
RETIRED: dict[str, str] = {
    "Q015": "answered by E413", "Q018": "answered by E373", "Q022": "answered by E392",
    "Q035": "answered by E407", "Q056": "answered by E366", "Q077": "answered by E379",
    "Q079": "answered by E367", "Q097": "answered by E380", "Q007": "answered by E425",
    "Q061": "answered by E428", "Q009": "answered by E441", "Q041": "answered by E458",
    "Q006": "folded into Q076", "Q083": "folded into Q076", "Q028": "folded into Q003",
    "Q067": "folded into Q036", "Q105": "folded into Q036", "Q106": "folded into Q036",
    "Q117": "folded into Q161", "Q102": "folded into Q163", "Q131": "answered by E752",
    "Q155": "folded into Q294", "Q156": "folded into Q294",
    "Q094": "decided in doc/specs/3d.md",
    "Q153": "answered by E746", "Q157": "answered by E746", "Q197": "answered by E752",
    "Q281": "answered by E787", "Q286": "answered by E788",
    "Q278": "decided in doc/specs/3d.md", "Q005": "answered by E402",
    "Q147": "folded into Q132", "Q144": "folded into Q133", "Q270": "folded into Q163",
    "Q138": "folded into Q089", "Q150": "answered by E1062", "Q151": "answered by E1062",
    "Q037": "answered by E422", "Q198": "decided in HACKING.md", "Q285": "answered by E829",
    "Q273": "answered by E803", "Q124": "answered by E809", "Q175": "answered by E721",
    "Q085": "answered by E408", "Q167": "answered by E828", "Q176": "folded into Q078", "Q103": "folded into Q211 after E968",
    "Q145": "folded into Q128 after E830", "Q140": "folded into Q003 after E830",
    "Q122": "answered by E831", "Q113": "answered by E844",
    "Q021": "folded into Q180 after E830",
    "Q152": "answered by E836", "Q166": "answered by E857", "Q295": "answered by E857",
    "Q274": "folded into Q183 after E869", "Q244": "folded into Q071 after E869",
    "Q289": "answered by E884",
    "Q292": "answered by E889",
    "Q287": "answered by E903", "Q291": "answered by E904", "Q293": "answered by E906", "Q271": "answered by E933",
    "Q141": "answered by E953",
    "Q178": "answered by E942",
    "Q283": "answered by E958",
    "Q190": "answered by E971",
    "Q121": "answered by E988",
    "Q205": "folded into Q200 after E992",
    "Q030": "answered by E1010",
    "Q101": "folded into Q069 after E1010",
    "Q201": "answered by E1022",
    "Q137": "answered by E1062",
    "Q282": "answered by E1038",
    "Q261": "answered by E1036",
    "Q199": "answered by E1037",
    "Q243": "answered by E1040",
    "Q298": "answered by E1051",
    "Q242": "answered by E1041",
    "Q104": "answered by E1052",
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
    if "kind" not in fm:
        return out + ["kind is missing (hw, fw or kernel)"]
    if list(fm) not in (KEYS, KEYS_HW):
        return out + [f"keys {list(fm)} != {KEYS} (hw: {KEYS_HW})"]
    for k in ("id", "question", "unit"):
        if not isinstance(fm[k], str) or not fm[k].strip():
            out.append(f"{k} is not a string")
    for k in ("evidence", "terms"):
        if not isinstance(fm[k], list) or not all(isinstance(x, str) for x in fm[k]):
            out.append(f"{k} is not a list of strings")
    if fm["kind"] not in KINDS:
        out.append(f"kind {fm['kind']!r} is not one of {', '.join(KINDS)}")
    elif "value" in fm and fm["kind"] != "hw":
        out.append(f"value on a {fm['kind']} question: only an hw question has a value")
    elif "value" in fm and fm["value"] not in VALUES:
        out.append(f"value {fm['value']!r} is not one of {', '.join(VALUES)}")
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
    """A retired question names the record that answered it, the question it folded into or
    the document that states the decision that closed it."""
    for q, why in retired.items():
        if not re.fullmatch(r"Q\d{3}", q) or not re.fullmatch(
                r"answered by E\d{3,}|folded into Q\d{3}( after E\d{3,})?|decided in [\w./-]+\.md",
                why):
            raise ValueError(f"{q}: retired as {why!r}, not 'answered by E<nnn>', "
                             "'folded into Q<nnn>[ after E<nnn>]' or 'decided in <doc>.md'")


def decision_problems(retired: dict[str, str], root: pathlib.Path) -> list[str]:
    """The decisions whose document is absent or does not name the question it closes."""
    out = []
    for q, why in retired.items():
        if why.startswith("decided in "):
            doc = root / why[len("decided in "):]
            if not doc.is_file():
                out.append(f"{q} {why}: no such file")
            elif q not in doc.read_text(errors="replace"):
                out.append(f"{q} {why}: the document does not name {q}")
    return out


def fold_problems(retired: dict[str, str], open_ids: set[str]) -> list[str]:
    """The folds whose target is not an open question."""
    return [f"{q} {why}, which is not an open question" for q, why in retired.items()
            if why.startswith("folded into ") and fold_target(why) not in open_ids]


def fold_target(why: str) -> str:
    """The question a fold moved into: "folded into Q<nnn>[ after E<nnn>]"."""
    return why.split()[2]


def reference_problems(text: str, open_ids: set[str], record: str | None = None) -> list[str]:
    """The Q<nnn> references of a text that do not name an open question. `record` is the id of
    the evidence record the text is: a record up to the one that answered a question keeps
    citing it (it was written before or with the answer, and changes only by corrections)."""
    out = []
    for q in dict.fromkeys(REF.findall(text)):
        if q in RETIRED and RETIRED[q].startswith("folded into ") and record \
                and " after E" in RETIRED[q] and evidence.num(record) <= evidence.num(RETIRED[q].split()[-1]):
            continue
        elif q in RETIRED and RETIRED[q].startswith("folded into "):
            out.append(f"{q} was {RETIRED[q]}: cite {fold_target(RETIRED[q])}")
        elif q in RETIRED and RETIRED[q].startswith("decided in "):
            continue
        elif q in RETIRED and record and RETIRED[q].startswith("answered by ") \
                and evidence.num(record) <= evidence.num(RETIRED[q].split()[-1]):
            continue
        elif q in RETIRED:
            out.append(f"{q} is answered ({RETIRED[q]}): cite the answer")
        elif q not in open_ids:
            out.append(f"{q}: no such question")
    return out


def line(q: dict) -> str:
    tag = ", ".join([f"phase {q['phase']}"] + ([q["kind"], q["value"]] if q["kind"] == "hw"
                                                  and "value" in q else [q["kind"]]))
    refs = ", ".join(q["evidence"])
    return f"- `{q['id']}` ({tag}): {q['question']}" + (f" ({refs})" if refs else "")


def render(qs: list[dict]) -> str:
    hw = [q for q in qs if q["kind"] == "hw"]
    by = {v: sum(q.get("value") == v for q in hw) for v in VALUES}
    out = ["<!-- SPDX-" "License-Identifier: MIT -->",
           "<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->",
           "# Open questions", "",
           "*Generated from `questions/` by `tools/records/questions.py`; do not edit.*", "",
           f"{len(qs)} open: {len(hw)} hw (high {by['high']}, medium {by['medium']}, "
           f"low {by['low']}, unrated {sum('value' not in q for q in hw)}), "
           + ", ".join(f"{sum(q['kind'] == k for q in qs)} {k}" for k in PARKED) + ".", "",
           "## Work queue: hardware", ""]
    for unit in sorted({q["unit"] for q in hw}):
        out += [f"### {unit}", ""]
        out += [line(q) for q in sorted((q for q in hw if q["unit"] == unit),
                                        key=lambda q: q["id"])] + [""]
    out += ["## Parked: not hardware knowledge", ""]
    for kind, name in PARKED.items():
        rows = [q for q in qs if q["kind"] == kind]
        out += [f"### {name}", ""]
        for unit in sorted({q["unit"] for q in rows}):
            out += [f"#### {unit}", ""]
            out += [line(q) for q in sorted((q for q in rows if q["unit"] == unit),
                                            key=lambda q: q["id"])] + [""]
    return "\n".join(out).rstrip() + "\n"


def generated() -> tuple[pathlib.Path, ...]:
    """The generated documents that copy the records' text (their citations are checked in
    the records themselves)."""
    return DOC, ROOT / "doc" / "evidence_log.md", ROOT / "doc" / "state_digest.md"


def main(argv: list[str] | None = None) -> int:
    a = sys.argv[1:] if argv is None else argv
    ids = {p.name.split("-")[0] for p in evidence.DIR.glob("*/E*.md")}
    terms, bad = evidence.glossary_terms(), 0
    for p in files():
        for msg in problems(p, ids, terms):
            print(f"{p.relative_to(ROOT)}: {msg}")
            bad += 1
    for p in misplaced():
        print(f"{p.relative_to(ROOT)}: not questions/<unit>/<name>.md")
        bad += 1
    try:
        check_retired(RETIRED)
    except ValueError as e:
        print(f"RETIRED: {e}")
        bad += 1
    open_ids = {p.name.split("-")[0] for p in files()}
    for msg in fold_problems(RETIRED, open_ids) + decision_problems(RETIRED, ROOT):
        print(f"RETIRED: {msg}")
        bad += 1
    for d, pat in (("evidence", "*/*.md"), ("glossary", "*/*.toml"), ("doc", "**/*.md")):
        for p in sorted((ROOT / d).glob(pat)):
            if p not in generated():
                rec = p.name.split("-")[0] if d == "evidence" else None
                for msg in reference_problems(p.read_text(), open_ids, rec):
                    print(f"{p.relative_to(ROOT)}: {msg}")
                    bad += 1
    text = render([parse(p) for p in files()])
    if "--check" in a:
        return 1 if bad or not DOC.exists() or DOC.read_text() != text else 0
    DOC.parent.mkdir(parents=True, exist_ok=True)
    DOC.write_text(text)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
