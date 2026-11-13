#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Evidence records: evidence/<unit>/E<nnn>-<slug>.md, one finding per file.

A record is Markdown with TOML front matter between `+++` lines:

    +++
    id = "E001"
    claim = "an example claim"
    unit = "dpm"
    method = "an example method"
    tiers = ["HW", "RE"]
    date = "2026-10-28"                 # a string
    data = ["dpm-example"]
    terms = ["CR_X"]
    +++

    Prose: what was done, what was seen, what it shows and what it does not.

`tiers` uses the project's provenance tags: HW (our hardware), CAP (captures of the closed
stack, black box), RE (our reading of the firmware's code), DDK (the GPL kernel sources),
infer (an inference). `terms` are glossary names; `data` names datasets (datasets/<id>.toml,
or `<id>:<part>`) or tracked repository files. Nothing but records lives under evidence/, each
exactly at evidence/<unit>/<name>.md. A record that turned out wrong is removed (git keeps it)
and its id is retired in RETIRED, never to be given again.

    python3 tools/records/evidence.py [--draft]
        check every record (--draft: ids may still be "E???")
"""
from __future__ import annotations

import datetime
import pathlib
import re
import sys
import tomllib

ROOT = pathlib.Path(__file__).resolve().parents[2]
DIR = ROOT / "evidence"
KEYS = ["id", "claim", "unit", "method", "tiers", "date", "data", "terms"]
UNITS = {"platform", "firmware", "bif", "edm", "dpm", "vdm", "ta", "mte", "isp", "tsp", "pds",
         "usse", "texture", "pbe", "zls", "transfer", "render"}
TIERS = {"HW", "CAP", "RE", "DDK", "infer"}
RETIRED: dict[str, str] = {}    # id -> why it was withdrawn
NAME = re.compile(r"(E\d{3,}|E\?\?\?)-[a-z0-9]+(-[a-z0-9]+)*\.md")
# a record id in a text: E followed by at least three digits (E1000 and up are ids too)
ID_REF = r"\bE\d{3,}\b"


def num(rid: str) -> int:
    """The number of a record id, for ordering (E999 comes before E1000)."""
    return int(rid[1:])


def parse(path: pathlib.Path) -> tuple[dict, str]:
    """(front matter, body) of a record."""
    text = path.read_text()
    if not text.startswith("+++\n"):
        raise ValueError(f"{path}: no front matter")
    head, sep, body = text[4:].partition("\n+++\n")
    if not sep:
        raise ValueError(f"{path}: front matter not closed")
    return tomllib.loads(head), body


def problems(path: pathlib.Path, terms: set[str], draft: bool = False) -> list[str]:
    """What is wrong with one record (empty when it is well formed)."""
    out = []
    if not NAME.fullmatch(path.name) or (not draft and "???" in path.name):
        out.append("file name is not E<nnn>-<slug>.md")
    if path.parent.name not in UNITS:
        out.append(f"directory {path.parent.name} is not a unit")
    try:
        fm, body = parse(path)
    except (ValueError, tomllib.TOMLDecodeError) as e:
        return out + [str(e)]
    if list(fm) != KEYS:
        return out + [f"keys {list(fm)} != {KEYS}"]
    typed = [f"{k} is not a string" for k in ("id", "unit", "date") if not isinstance(fm[k], str)]
    typed += [f"{k} empty" for k in ("claim", "method")
              if not isinstance(fm[k], str) or not fm[k].strip()]
    typed += [f"{k} is not a list of strings" for k in ("tiers", "data", "terms")
              if not isinstance(fm[k], list) or not all(isinstance(x, str) for x in fm[k])]
    if typed:
        return out + typed
    if fm["id"] in RETIRED:
        out.append(f"id is retired: {RETIRED[fm['id']]}")
    if fm["id"] != path.name.split("-")[0]:
        out.append("id does not match the file name")
    if fm["unit"] != path.parent.name:
        out.append("unit does not match the directory")
    if not _date_ok(fm["date"]):
        out.append("date is not YYYY-MM-DD")
    if not fm["tiers"] or set(fm["tiers"]) - TIERS:
        out.append(f"tiers {fm['tiers']} not in {sorted(TIERS)}")
    unknown = [t for t in fm["terms"] if t not in terms]
    if unknown:
        out.append(f"terms not in the glossary: {unknown}")
    if not body.strip():
        out.append("no prose")
    if re.search(r"\.md:\d+", body):
        out.append("cites a line number")
    for d in re.findall(r"\[corrected (\d{4}-\d{2}-\d{2})", fm["claim"]):
        if f"**Correction {d}:**" not in body:
            out.append(f"claim marked corrected {d} but no **Correction {d}:** in the prose")
    return out


def _date_ok(v: str) -> bool:
    """A calendar date written YYYY-MM-DD."""
    try:
        datetime.date.fromisoformat(v)
    except ValueError:
        return False
    return bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", v))


def misplaced(path: pathlib.Path | None = None) -> list[pathlib.Path]:
    """Files under evidence/ that are not at <unit>/<name>.md: misplaced or nested records and
    anything else (hidden files, such as a desktop's metadata, are ignored)."""
    d = DIR if path is None else pathlib.Path(path)
    return sorted(p for p in d.rglob("*") if p.is_file() and not p.name.startswith(".")
                  and (len(p.relative_to(d).parts) != 2 or p.suffix != ".md"))


def glossary_terms() -> set[str]:
    sys.path.insert(0, str(ROOT / "tools" / "clean-room"))
    import glossary
    return {r["name"] for r in glossary.load()}


def main(argv: list[str] | None = None) -> int:
    a = sys.argv[1:] if argv is None else argv
    terms, bad = glossary_terms(), 0
    for p in sorted(DIR.glob("*/*.md")):
        for msg in problems(p, terms, draft="--draft" in a):
            print(f"{p.relative_to(ROOT)}: {msg}")
            bad += 1
    for p in misplaced():
        print(f"{p.relative_to(ROOT)}: not evidence/<unit>/<name>.md")
        bad += 1
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
