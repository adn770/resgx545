#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The glossary: every name the project may use for SGX545 hardware and firmware, with the
open sources that support it. The records are glossary/<group>/<NAME>.toml, one file per term
and its fields (NAME, NAME.FIELD); each term has a status and lists its sources, each source
with its own spelling, location, meaning, tier, citation (an external source's citation record,
C<nnnn> under citations/; for our own terms, evidence records or repository files), licence
and evidence. This module loads the records as rows (one per term and source), writes rows
back as records, and renders doc/glossary.md (python3 tools/clean-room/glossary.py
[--check])."""
import collections
import json
import pathlib
import re
import sys
import textwrap
import tomllib

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DIR = ROOT / "glossary"
DOC = ROOT / "doc" / "glossary.md"

SOURCE_KEYS = ["term", "kind", "sgx545", "meaning", "tier", "source", "citation", "licence",
               "evidence"]
COLUMNS = ["group", "id", "name", "status"] + SOURCE_KEYS
# named: the meaning is established; inferred: our best reading, unconfirmed; unset: none yet
STATUSES = {"named", "inferred", "unset"}
UNSET = re.compile(r"not established|unknown", re.I)
INFERRED = "inferred reading (unconfirmed)"
KINDS = {"register", "field", "struct", "bitfield", "flag", "enum", "function", "unit", "concept"}
TIERS = {"1", "1c", "2", "3", "4", "ours"}
LICENCES = {"GPL-2.0", "GPL-2.0 OR MIT", "GPL-2.0-only OR MIT", "MIT", "Intel-binary (ours)",
            "public-doc", "patent"}

CITES = ROOT / "cites"


def cites(path: pathlib.Path = CITES) -> dict[str, dict]:
    """The sources, one record per source under cites/: {id: record}."""
    return {p.stem: tomllib.loads(p.read_text()) for p in sorted(pathlib.Path(path).glob("*.toml"))}


SOURCES = {k: c["tier"] for k, c in cites().items()}

TIER_TEXT = {
    "1": "the original spelling in open SGX code (GPL or MIT kernel sources, Intel's register "
         "list), applying to SGX545 directly or at the same offset",
    "1c": "as 1, from another SGX core: the evidence says which, and whether the offset matches",
    "2": "a string or exported symbol of our own Cedarview package, observed as a black box",
    "3": "Imagination's open Rogue code (Linux, Mesa): the same function on the descendant core; "
         "an analogy, not SGX545's own spelling",
    "4": "Imagination's public SGX documents and patents: unit and concept names",
    "ours": "our own term for a thing no open source names, after what we measured (the "
            "citation points into this repository); an inference, marked [infer]",
}
GROUPS = [("units", "Units and concepts"), ("registers", "Registers and their fields"),
          ("structs", "Firmware-interface structures, flags and functions"),
          ("words", "State words, ports and instruction-level terms")]


def stem(group: str, name: str) -> str:
    """The record file a term lives in: its first component (CR_X for CR_X and CR_X.F); a unit
    or concept, named in words, by its name with the punctuation turned into dashes."""
    if group == "units":
        return re.sub(r"[^A-Za-z0-9_.]+", "-", name).strip("-")
    return name.split(".")[0]


def load(path: pathlib.Path = DIR) -> list[dict]:
    """Rows, one per term and source, in file order."""
    rows = []
    for f in sorted(pathlib.Path(path).glob("*/*.toml")):
        for t in tomllib.loads(f.read_text())["term"]:
            for s in t["source"]:
                rows.append({"group": f.parent.name, "id": t["id"], "name": t["name"],
                             "status": t["status"], **{k: s[k] for k in SOURCE_KEYS}})
    return rows


def _str(v: str) -> str:
    return json.dumps(v, ensure_ascii=False)      # a TOML basic string


def assign_ids(rows: list[dict]) -> None:
    """Give each term without an id the next free G<nnnn>, in row order; ids are never
    reused or renumbered, so a term keeps the id specs cite it by."""
    have = {(r["group"], r["name"]): r["id"] for r in rows if r.get("id")}
    top = max((int(i[1:]) for i in have.values()), default=0)
    for r in rows:
        key = (r["group"], r["name"])
        if key not in have:
            top += 1
            have[key] = f"G{top:04d}"
        r["id"] = have[key]


def write(rows: list[dict], path: pathlib.Path = DIR) -> None:
    """Rows back as records: one file per group and term family, names that differ only in
    case in one file (spelled as the family's own term, else its first name)."""
    assign_ids(rows)
    files: dict[tuple[str, str], dict[str, list[dict]]] = collections.defaultdict(dict)
    for r in rows:
        key = (r["group"], stem(r["group"], r["name"]).lower())
        files[key].setdefault(r["name"], []).append(r)
    for (group, _), terms in files.items():
        stems = sorted({stem(group, n) for n in terms})
        name = next((s for s in stems if s in terms), stems[0])
        out = []
        for n in sorted(terms, key=lambda n: (n.lower(), n)):
            status = {r["status"] for r in terms[n]}
            assert len(status) == 1, (n, status)
            out += ["[[term]]", f"id = {_str(terms[n][0]['id'])}", f"name = {_str(n)}",
                    f"status = {_str(status.pop())}", ""]
            for r in terms[n]:
                out += ["[[term.source]]"] + [f"{k} = {_str(r[k])}" for k in SOURCE_KEYS] + [""]
        d = pathlib.Path(path) / group
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{name}.toml").write_text("\n".join(out).rstrip() + "\n")


ORDER = {"1": 0, "1c": 1, "2": 2, "3": 3, "4": 4, "ours": 5}


def _entry(name: str, rs: list[dict]) -> list[str]:
    """One term: where it applies, what it is, and every source spelling that supports it."""
    rs = sorted(rs, key=lambda r: (ORDER[r["tier"]], r["source"], r["term"]))
    locs = sorted({r["sgx545"] for r in rs if r["sgx545"] != "-"})
    more = ", ..." if len(locs) > 3 else ""
    head = f"- `{name}` {rs[0]['id']}" + (f" ({', '.join(locs[:3])}{more})"
                           if locs else "")
    srcs, seen = [], set()
    for r in rs:
        key = (r["term"], r["tier"], r["source"])
        if key not in seen:
            seen.add(key)
            srcs.append(f"`{r['term']}` ({r['tier']}, {r['source']})")
    meaning = rs[0]["meaning"]
    if rs[0]["status"] == "inferred":
        meaning = f"{INFERRED}: {meaning}"
    text = f"{head}: {meaning}. From {'; '.join(srcs)}."
    return textwrap.wrap(text, 100, subsequent_indent="  ", break_on_hyphens=False,
                         break_long_words=False)


def render(rows: list[dict]) -> str:
    out = ["<!-- SPDX-" "License-Identifier: MIT -->",
           "<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->",
           "# SGX545 glossary: names and where they come from", "",
           "*Generated from `glossary/` by `tools/clean-room/glossary.py`; do not edit.*", ""]
    out += textwrap.wrap(
        "Every name this project uses for an SGX545 register, firmware structure or field, "
        "state-word field, flag, function, unit or concept must have an open source. This is "
        "the list of names that do, each with the source spellings that support it; its record "
        "(`glossary/<group>/<NAME>.toml`) also gives the citation, the licence and the evidence "
        "that ties a name from another core or from Rogue to SGX545. An external source is "
        "cited by a citation record (`citations/<source>/C<nnnn>-*.md`: the place in the "
        "upstream source, a link to it at the pinned version and the line quoted); our own "
        "terms cite our evidence records. "
        "Nothing read from inside a closed binary is a source of a name; a string or exported "
        "symbol seen from outside, as a black box, may back one (tier 2; HACKING.md, "
        "\"Sources\"). A thing with no name here gets a descriptive name of our own.", 100)
    out += ["", "Tiers:", ""]
    for t in ("1", "1c", "2", "3", "4", "ours"):
        out += textwrap.wrap(f"- **{t}**: {TIER_TEXT[t]}.", 100, subsequent_indent="  ")
    out += [""]
    out += textwrap.wrap(
        "Our terms have one form per kind: registers `UNIT_NAME` and their fields `REG.FIELD`; "
        "firmware structures and their fields `lower_snake`, as `struct.field`; state-word "
        "fields `WORD.FIELD`; flags and enums `FAMILY.VALUE`; units and concepts in words. "
        "Source prefixes (`EUR_CR_`, `PSB_CR_`, `ROGUE_CR_`, `SGXMKIF_`, `ui32`...) are never "
        "part of our term; exported functions keep their exact symbol. Each entry lists the "
        "source spellings behind it, best tier first.", 100)
    out += [""]
    for n, (g, title) in enumerate(GROUPS, 1):
        sel = [r for r in rows if r["group"] == g]
        out += [f"## {n}. {title}", ""]
        for kind in sorted({r["kind"] for r in sel}):
            out += [f"### {kind}", ""]
            by: dict[str, list[dict]] = {}
            for r in sel:
                if r["kind"] == kind:
                    by.setdefault(r["name"], []).append(r)
            for name in sorted(by, key=lambda n: (min(r["sgx545"] for r in by[n]), n)):
                out += _entry(name, by[name])
            out.append("")
    out += [f"## {len(GROUPS) + 1}. Sources", ""]
    used = {r["source"] for r in rows}
    recs = cites()
    for s in sorted(used & set(recs), key=lambda s: (ORDER[recs[s]["tier"]], s)):
        out += textwrap.wrap(f"- `{s}` (tier {recs[s]['tier']}): {recs[s]['title']}.", 100,
                             subsequent_indent="  ")
    return "\n".join(out).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    a = sys.argv[1:] if argv is None else argv
    text = render(load())
    if "--check" in a:
        return 0 if DOC.is_file() and DOC.read_text() == text else 1
    DOC.parent.mkdir(parents=True, exist_ok=True)
    DOC.write_text(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
