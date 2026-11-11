#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Spec coverage: a hardware fact a record settles belongs in the specs. Every evidence record from
E600 whose tiers include HW or CAP is cited by a file under doc/specs (an `E<nnn>` token, or a
range such as `E804-E808`, `E804 to E808` or `E804..E808`), or it is listed in
doc/specs/UNCITED.toml with the reason it is not yet. The list may only shrink: a listed record
that a spec cites is a problem until it is removed, and so is a listed id that needs no citation.

    python3 tools/records/spec_coverage.py --check
"""
from __future__ import annotations

import pathlib
import re
import sys
import tomllib

import evidence

ROOT = pathlib.Path(__file__).resolve().parents[2]
FIRST = 600
TOKEN = re.compile(r"(?<![\w])E(\d{3})(?:\s*(?:-|to|\.\.)\s*E(\d{3}))?(?![\w])")
BASELINE = "doc/specs/UNCITED.toml"


def cited(text: str) -> set[str]:
    """The record ids a text cites, ranges expanded."""
    out = set()
    for a, b in TOKEN.findall(text):
        lo, hi = int(a), int(b or a)
        out |= {f"E{n:03d}" for n in range(lo, hi + 1)} if lo <= hi else {f"E{lo:03d}"}
    return out


def required() -> set[str]:
    """The hardware records from E600: tiers with HW or CAP."""
    out = set()
    for p in (ROOT / "evidence").glob("*/E*.md"):
        fm, _ = evidence.parse(p)
        if int(fm["id"][1:]) >= FIRST and {"HW", "CAP"} & set(fm.get("tiers", [])):
            out.add(fm["id"])
    return out


def spec_citations() -> set[str]:
    out = set()
    for p in (ROOT / "doc" / "specs").rglob("*.md"):
        out |= cited(p.read_text(errors="replace"))
    return out


def load_baseline() -> dict[str, str]:
    p = ROOT / BASELINE
    return tomllib.loads(p.read_text()) if p.is_file() else {}


def problems(baseline: dict[str, str]) -> list[str]:
    need, have = required(), spec_citations()
    out = []
    for rid in sorted(need - have - set(baseline)):
        out.append(f"{rid}: cited by no doc/specs file and not in {BASELINE}")
    for rid in sorted(baseline):
        if rid not in need:
            out.append(f"{rid}: not a hardware record from E{FIRST}, remove it from {BASELINE}")
        elif rid in have:
            out.append(f"{rid}: cited by a spec, remove it from {BASELINE}")
        elif not str(baseline[rid]).strip():
            out.append(f"{rid}: listed without a reason")
    return out


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv not in ([], ["--check"]):
        print(__doc__, file=sys.stderr)
        return 2
    found = problems(load_baseline())
    for msg in found:
        print(msg)
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
