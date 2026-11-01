#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The open rows: every glossary term whose meaning is an inferred reading, grouped by unit,
with the records behind it, rendered as doc/open_rows.md
(python3 tools/records/open_rows.py [--check])."""
from __future__ import annotations

import re
import sys
import textwrap

import evidence

sys.path.insert(0, str(evidence.ROOT / "tools" / "clean-room"))
import glossary  # noqa: E402
import glossary_coverage  # noqa: E402

DOC = evidence.ROOT / "doc" / "open_rows.md"


def rows() -> list[dict]:
    return [r for r in glossary.load() if r["status"] == "inferred"]


def render(rs: list[dict]) -> str:
    out = ["<!-- SPDX-" "License-Identifier: MIT -->",
           "<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->",
           "# SGX545 open glossary rows", "",
           "*Generated from `glossary/` by `tools/records/open_rows.py`; do not edit.*", ""]
    out += textwrap.wrap(
        "The glossary terms whose meaning our evidence has not established: each has the status "
        "`inferred`, and its meaning is our best reading, a hypothesis to test, never a name. "
        "Names stay neutral (`REG_xxxx`, `BITSn_m`) until a test settles them. Each entry gives "
        "the term's glossary id, where it sits, the reading, and the evidence records it rests "
        "on.", 100)
    out.append("")
    terms: dict[str, list[dict]] = {}
    for r in rs:
        terms.setdefault(r["id"], []).append(r)
    units: dict[str, list[str]] = {}
    for gid, trs in terms.items():
        units.setdefault(glossary_coverage.unit_of(trs[0]) if trs[0]["group"] != "units"
                         else "units", []).append(gid)
    for unit in sorted(units):
        out += [f"## {unit}", ""]
        for gid in sorted(units[unit], key=lambda g: terms[g][0]["name"]):
            trs = sorted(terms[gid], key=lambda r: glossary.ORDER[r["tier"]])
            r = trs[0]
            loc = f" ({r['sgx545']})" if r["sgx545"] != "-" else ""
            ids = sorted({e for t in trs for c in ("citation", "evidence")
                          for e in re.findall(r"\bE\d{3}\b", t[c])})
            text = f"- `{gid}` `{r['name']}`{loc}: {r['meaning']}."
            if ids:
                text += f" Evidence: {', '.join(ids)}."
            out += textwrap.wrap(text, 100, subsequent_indent="  ", break_on_hyphens=False,
                                 break_long_words=False)
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    a = sys.argv[1:] if argv is None else argv
    text = render(rows())
    if "--check" in a:
        return 0 if DOC.is_file() and DOC.read_text() == text else 1
    DOC.parent.mkdir(parents=True, exist_ok=True)
    DOC.write_text(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
