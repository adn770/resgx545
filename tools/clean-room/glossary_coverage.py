#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Glossary coverage per unit: for each unit, its terms; how many carry a functional name; how
many are neutral (REG_xxxx, BITSn…), unset or inferred (best guesses, not established); how many
have hardware or capture evidence; and the count per source tier.

    python3 tools/clean-room/glossary_coverage.py [GLOSSARY_DIR]
"""
from __future__ import annotations

import collections
import pathlib
import re
import sys

import glossary

NEUTRAL = re.compile(r"(REG_[0-9A-F]{4}|(^|[._])(word|WORD)_?[0-9a-f]{3}\b|BITS?\d|\.B\d+$"
                     r"|_reg_[0-9a-f]{4})")

TEXTURE = {"T0", "T1", "T2", "T3", "TEXTYPE", "TEXFORMAT"}
ISP = {"ISP0", "ISP1", "ISP2", "PASS_TYPE", "CMP_MODE", "STENCIL_OP"}
PIXEL_TASK = {"PIXEL_EVENT", "PRIMARY_FRAG", "SECONDARY_FRAG", "PDS_PRIMARY", "PDS_SECONDARY",
              "PDS_SIZE", "PDS_PTR", "PDS_OP", "PDS_REG"}
MTE_STATE = {"PRESENCE", "VIEWPORT", "WCLAMP", "OUTSEL", "MTECTL", "CLIP0", "CLIP1", "TERM", "BG",
             "SIDEBAND", "EMPTY_TILE", "PORT", "COORDSIZE", "COORDFMT"}
ENCODINGS = {"REGTYPE", "USE", "FDUAL", "ARGFLAGS", "TEST_MASK", "USE_OP", "INTSRCSEL", "FILTER",
             "ADDRMODE", "PACKMODE", "MEMLAYOUT", "MIPMAPS_PRESENT", "DOUTI", "DOUTT"}
TA_MEMORY = {"PB_OBJ", "REGION_HDR", "CSTREAM"}


def _word_family(top: str) -> str:
    if top.startswith("DOUT") and top not in ENCODINGS:
        return "PDS DOUT words"
    for prefix, fam in (("VDM", "VDM stream words"), ("EMIT", "PDS/pixel task words"),
                        ("CR_", "register field words")):
        if top.startswith(prefix):
            return fam
    for names, fam in ((PIXEL_TASK, "PDS/pixel task words"), (MTE_STATE, "MTE state block words"),
                       (TEXTURE, "texture words T0-T3"), (ISP, "ISP state words"),
                       (ENCODINGS, "USSE/PDS instruction encodings"),
                       (TA_MEMORY, "the TA's parameter buffer and TA data"),
                       ({"FEATURE", "HEAP"}, "feature/heap ids")):
        if top in names:
            return fam
    return top


def unit_of(r: dict) -> str:
    """The unit a glossary row belongs to: its group and a family of names."""
    g, name = r["group"], r["name"]
    if g == "registers":
        m = re.match(r"CR_([A-Z]+)[0-9]?_", name)
        u = m.group(1) if m else ("CLKGATE" if name.startswith("CR_CLKGATE") else
                                  "PDS" if name.startswith("CR_PDS") else
                                  "TIMER" if name.startswith("CR_TIMER") else "init values")
        unit = "registers: " + ("(no unit)" if u == "REG" else u)
    elif g == "structs":
        top = name.split(".")[0]
        if "." not in name and re.match(r"(SGX|PVRSRV|DevInit)", top):
            top = "(services API entry points)"
        elif "." not in name:
            top = "(standalone fields)"
        elif re.match(r"[A-Z_]+$", top) and top not in ("FRAG_FLAGS", "GEOM_FLAGS", "TQ_FLAGS"):
            top = "(other flag/enum sets)"
        unit = "structs: " + top
    else:
        unit = "words: " + _word_family(name.split(".")[0])
    return unit


def units(rows: list[dict]) -> dict[str, collections.Counter]:
    """{unit: counts} of rows, named, neutral, unset, hw/cap, and per tier."""
    stat: dict = collections.defaultdict(collections.Counter)
    for r in rows:
        if r["group"] == "units":
            continue
        s = stat[unit_of(r)]
        s["rows"] += 1
        neutral = bool(NEUTRAL.search(r["name"]))
        unset, inferred = r["status"] == "unset", r["status"] == "inferred"
        s["neutral"] += neutral
        s["unset"] += unset
        s["inferred"] += inferred
        s["named"] += not neutral and not unset and not inferred
        if re.search(r"[\[(](HW|CAP)", r["evidence"]):
            s["hw/cap"] += 1
        s["tier " + r["tier"]] += 1
    return stat


def report(stat: dict) -> str:
    out = [f"{'unit':34} {'rows':>5} {'named':>6} {'cov%':>5} {'unset':>6} {'inferred':>8} "
           f"{'neutral':>8} {'hw/cap':>7}  tiers"]
    tot: collections.Counter = collections.Counter()
    last = None
    for u in sorted(stat, key=lambda u: (u.split(":")[0], -stat[u]["rows"])):
        s = stat[u]
        tot.update(s)
        grp = u.split(":")[0]
        if grp != last:
            out.append(f"-- {grp}")
            last = grp
        tiers = " ".join(f"{k[5:]}:{v}" for k, v in sorted(s.items()) if k.startswith("tier "))
        out.append(f"  {u.split(': ', 1)[1]:32} {s['rows']:5} {s['named']:6} "
                   f"{100 * s['named'] // s['rows']:5} {s['unset']:6} {s['inferred']:8} "
                   f"{s['neutral']:8} {s['hw/cap']:7}  {tiers}")
    out.append(f"{'TOTAL':34} {tot['rows']:5} {tot['named']:6} "
               f"{100 * tot['named'] // max(tot['rows'], 1):5} {tot['unset']:6} "
               f"{tot['inferred']:8} {tot['neutral']:8} {tot['hw/cap']:7}")
    return "\n".join(out) + "\n"


def main(argv: list[str] | None = None) -> int:
    a = sys.argv[1:] if argv is None else argv
    path = pathlib.Path(a[0]) if a else glossary.DIR
    print(report(units(glossary.load(path))), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
