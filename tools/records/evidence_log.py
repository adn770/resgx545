#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The evidence log: every evidence record's claim, unit, provenance tiers and data, in the
order the records were made and again by unit, rendered as doc/evidence_log.md
(python3 tools/records/evidence_log.py [--check])."""
from __future__ import annotations

import sys
import textwrap

import evidence

DOC = evidence.ROOT / "doc" / "evidence_log.md"
WIDTH = 100


def records() -> list[dict]:
    """The front matter of every record, in date then id order."""
    return sorted((evidence.parse(p)[0] for p in evidence.DIR.glob("*/E*.md")),
                  key=lambda fm: (fm["date"], evidence.num(fm["id"])))


def _wrap(text: str, indent: str = "") -> list[str]:
    return textwrap.wrap(text, WIDTH, subsequent_indent=indent, break_on_hyphens=False,
                         break_long_words=False)


def _entry(fm: dict) -> list[str]:
    data = ", ".join(f"`{d}`" for d in fm["data"]) or "none"
    out = _wrap(f"- `{fm['id']}` {fm['claim']}.", "  ")
    return out + _wrap(f"  *{fm['unit']}; {', '.join(fm['tiers'])}; data: {data}.*", "  ")


def render(recs: list[dict]) -> str:
    recs = sorted(recs, key=lambda fm: (fm["date"], evidence.num(fm["id"])))
    out = ["<!-- SPDX-" "License-Identifier: MIT -->",
           "<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->",
           "# SGX545 evidence log", "",
           "*Generated from `evidence/` by `tools/records/evidence_log.py`; do not edit.*", ""]
    out += _wrap("Every evidence record, by the day it was made and again by unit: its claim, "
                 "the unit it belongs to, its provenance tiers (HW our hardware, CAP captures "
                 "of the closed stack, RE our reading of the firmware, DDK the GPL kernel "
                 "sources, infer an inference) and the datasets or files it rests on. The "
                 "record itself, in `evidence/<unit>/`, gives the method and what it does "
                 "and does not show.")
    out.append("")
    if not recs:
        return "\n".join(out + ["No evidence records yet."]) + "\n"
    out += ["## Chronology", ""]
    for date in sorted({fm["date"] for fm in recs}):
        out += [f"### {date}", ""]
        for fm in recs:
            if fm["date"] == date:
                out += _entry(fm)
        out.append("")
    out += ["## By unit", ""]
    for unit in sorted({fm["unit"] for fm in recs}):
        ids = ", ".join(fm["id"] for fm in recs if fm["unit"] == unit)
        out += [f"### {unit}", ""] + _wrap(f"Records: {ids}.") + [""]
    return "\n".join(out).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    a = sys.argv[1:] if argv is None else argv
    text = render(records())
    if "--check" in a:
        return 0 if DOC.is_file() and DOC.read_text() == text else 1
    DOC.parent.mkdir(parents=True, exist_ok=True)
    DOC.write_text(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
