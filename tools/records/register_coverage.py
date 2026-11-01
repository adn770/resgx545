#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Register coverage: every glossary register by offset, with the implemented bits an evidence
record measured, its field rows and the bits no field covers, and the records behind them,
rendered as doc/register_coverage.md (python3 tools/records/register_coverage.py [--check]).

A measured width is the mask of the bits that took a write, read from an evidence record: a
table with a "bits that took a write" column, or a sentence on the implemented bits giving
`0xNNNN 0xMMMMMMMM` pairs after the words "implemented bits" (a pair before them, or in
another sentence, is not a width). Where no record measured one, 32 bits are assumed."""
from __future__ import annotations

import dataclasses
import re
import sys
import textwrap

import evidence

sys.path.insert(0, str(evidence.ROOT / "tools" / "clean-room"))
import glossary  # noqa: E402
import glossary_coverage  # noqa: E402

DOC = evidence.ROOT / "doc" / "register_coverage.md"

REG_LOC = re.compile(r"0x([0-9a-fA-F]{4})")
FIELD_LOC = re.compile(r"0x([0-9a-fA-F]{4})\[(\d+)(?::(\d+))?\]")
E_ID = re.compile(r"\bE\d{3}\b")
TABLE_HEAD = re.compile(r"^\|(.+)\|\s*$")
WRITE_COLUMN = "bits that took a write"
REG_AND_MASK = re.compile(r"\b0x([0-9a-fA-F]{4}) 0x([0-9a-fA-F]{8})\b")
SENTENCE_END = re.compile(r"(?<=[.;])\s+(?=[A-Z0-9`(])")
ALL = 0xFFFFFFFF


@dataclasses.dataclass
class Register:
    offset: int
    name: str
    fields: dict[str, int]            # field leaf -> mask of its bits
    width: int | None                 # implemented bits a record measured, or None
    width_records: list[str]
    records: list[str]                # the records of its rows, its fields' and its width's

    def covered(self) -> int:
        out = 0
        for mask in self.fields.values():
            out |= mask
        return out

    def uncovered(self) -> int | None:
        """The implemented bits (all 32 when unmeasured) no field covers; None with no
        field rows, the register's meaning then being the whole word."""
        if not self.fields:
            return None
        return (ALL if self.width is None else self.width) & ~self.covered()


def _bits(hi: str, lo: str | None) -> int:
    hi_, lo_ = int(hi), int(lo if lo is not None else hi)
    return ((1 << (hi_ + 1)) - 1) & ~((1 << lo_) - 1)


def _mask(text: str) -> int | None:
    """A mask written as 0x..., or as bits and ranges (16:0, 5:0, 0)."""
    text = text.strip().strip("`")
    if re.fullmatch(r"0x[0-9a-fA-F]+", text):
        return int(text, 16)
    out = 0
    for part in text.split(","):
        m = re.fullmatch(r"\s*(\d+)(?::(\d+))?\s*", part)
        if not m:
            return None
        out |= _bits(m.group(1), m.group(2))
    return out


def widths_in(body: str) -> dict[int, int]:
    """{register offset: implemented bits} a record's text measures."""
    out: dict[int, int] = {}
    column = None
    for line in body.splitlines():
        m = TABLE_HEAD.match(line.strip())
        if not m:
            column = None
            continue
        cells = [c.strip() for c in m.group(1).split("|")]
        if column is None:
            column = next((i for i, c in enumerate(cells) if c.lower() == WRITE_COLUMN), -1)
            continue
        if column < 0 or column >= len(cells) or set(cells[0]) <= set("-: "):
            continue
        reg = re.fullmatch(r"`?0x([0-9a-fA-F]{4})`?", cells[0])
        mask = _mask(cells[column])
        if reg and mask is not None:
            out[int(reg.group(1), 16)] = mask
    for para in re.split(r"\n\s*\n", body):
        for sentence in SENTENCE_END.split(" ".join(para.split())):
            _, said, rest = sentence.partition("implemented bits")
            if said:
                for m in REG_AND_MASK.finditer(rest):
                    out[int(m.group(1), 16)] = int(m.group(2), 16)
    return out


def measured() -> dict[int, tuple[int, list[str]]]:
    """{register offset: (implemented bits, the records that measured them)}."""
    out: dict[int, tuple[int, list[str]]] = {}
    for path in sorted(evidence.DIR.glob("*/E*.md")):
        fm, body = evidence.parse(path)
        for reg, mask in widths_in(body).items():
            old, ids = out.get(reg, (0, []))
            out[reg] = (old | mask, ids + [fm["id"]])
    return out


def registers(rows: list[dict] | None = None,
              widths: dict[int, tuple[int, list[str]]] | None = None) -> list[Register]:
    """The glossary's registers in offset order, each with its fields and measured width."""
    rows = glossary.load() if rows is None else rows
    widths = measured() if widths is None else widths
    regs: dict[str, Register] = {}
    for r in rows:
        if r["group"] != "registers" or "." in r["name"] or r["kind"] != "register":
            continue
        m = REG_LOC.fullmatch(r["sgx545"].strip())
        if m and r["name"] not in regs:
            off = int(m.group(1), 16)
            mask, ids = widths.get(off, (None, []))
            regs[r["name"]] = Register(off, r["name"], {}, mask, list(ids), [])
    ids: dict[str, set[str]] = {n: set(reg.width_records) for n, reg in regs.items()}
    for r in rows:
        top, _, leaf = r["name"].partition(".")
        reg = regs.get(top)
        if reg is None:
            continue
        ids[top] |= {e for k in ("citation", "evidence", "meaning") for e in E_ID.findall(r[k])}
        if not leaf:
            continue
        m = FIELD_LOC.match(r["sgx545"].strip())
        if m and int(m.group(1), 16) == reg.offset:
            reg.fields[leaf] = reg.fields.get(leaf, 0) | _bits(m.group(2), m.group(3))
    for name, reg in regs.items():
        reg.records = sorted(ids[name])
    return sorted(regs.values(), key=lambda g: (g.offset, g.name))


def ranges(mask: int) -> str:
    """The set bits of a mask as ranges, high first: 31, 27:24, 2."""
    out, bit = [], 31
    while bit >= 0:
        if mask >> bit & 1:
            lo = bit
            while lo > 0 and mask >> (lo - 1) & 1:
                lo -= 1
            out.append(f"{bit}:{lo}" if lo != bit else str(bit))
            bit = lo - 1
        else:
            bit -= 1
    return ", ".join(out) or "-"


def _field_bits(mask: int) -> str:
    return "[" + ranges(mask).replace(", ", "][") + "]"


def entry(reg: Register) -> list[str]:
    if reg.width is None:
        width = "width 32 bits assumed"
    else:
        width = (f"width {bin(reg.width).count('1')} bits ({ranges(reg.width)}, "
                 f"{', '.join(reg.width_records)})")
    parts = [width]
    if reg.fields:
        n = len(reg.fields)
        fields = ", ".join(f"{k} {_field_bits(v)}" for k, v in
                           sorted(reg.fields.items(), key=lambda kv: (-kv[1].bit_length(), kv[0])))
        parts.append(f"{n} field{'s' if n != 1 else ''}: {fields}")
        un = reg.uncovered()
        parts.append(f"uncovered {ranges(un)} ({bin(un).count('1')} bits)")
        if reg.width is not None and reg.covered() & ~reg.width:
            parts.append(f"fields on bits that took no write: {ranges(reg.covered() & ~reg.width)}")
    else:
        parts.append("no field rows")
    text = f"- `0x{reg.offset:04x}` `{reg.name}`: " + "; ".join(parts) + "."
    if reg.records:
        text += f" Records: {', '.join(reg.records)}."
    return textwrap.wrap(text, 100, subsequent_indent="  ", break_on_hyphens=False,
                         break_long_words=False)


def _unit(reg: Register) -> str:
    unit = glossary_coverage.unit_of({"group": "registers", "name": reg.name})
    return unit.split(": ", 1)[1]


def summary(regs: list[Register]) -> list[list]:
    """[unit, registers, with fields, measured width, uncovered bits, uncovered on a measured
    width] per unit, then the total."""
    units: dict[str, list[Register]] = {}
    for r in regs:
        units.setdefault(_unit(r), []).append(r)
    out = []
    for name in sorted(units) + ["total"]:
        rs = regs if name == "total" else units[name]
        withf = [r for r in rs if r.fields]
        out.append([name, len(rs), len(withf), sum(r.width is not None for r in rs),
                    sum(bin(r.uncovered()).count("1") for r in withf),
                    sum(bin(r.uncovered()).count("1") for r in withf if r.width is not None)])
    return out


def render(regs: list[Register]) -> str:
    out = ["<!-- SPDX-" "License-Identifier: MIT -->",
           "<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->",
           "# SGX545 register coverage", "",
           "*Generated from `glossary/` and `evidence/` by `tools/records/register_coverage.py`; "
           "do not edit.*", ""]
    out += textwrap.wrap(
        "Every register the glossary places at an offset, with the bits a record measured as "
        "implemented (the bits that took a write), the field rows that name its bits, and the "
        "bits no field covers. Where no record measured the register, all 32 bits are assumed; "
        "a register with no field rows carries its meaning at register level (an address, a "
        "count) or has fields still to name. Records are the evidence records its rows, its "
        "fields' rows and its measured width cite.", 100)
    out += ["", "## Summary", "",
            "| unit | registers | with fields | measured width | uncovered bits | "
            "on a measured width |",
            "|---|---|---|---|---|---|"]
    out += ["| " + " | ".join(str(c) for c in line) + " |" for line in summary(regs)]
    out.append("")
    units: dict[str, list[Register]] = {}
    for r in regs:
        units.setdefault(_unit(r), []).append(r)
    for name in sorted(units):
        out += [f"## {name}", ""]
        for r in units[name]:
            out += entry(r)
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    a = sys.argv[1:] if argv is None else argv
    text = render(registers())
    if "--check" in a:
        return 0 if DOC.is_file() and DOC.read_text() == text else 1
    DOC.parent.mkdir(parents=True, exist_ok=True)
    DOC.write_text(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
