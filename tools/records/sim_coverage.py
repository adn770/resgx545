#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Sim coverage: a hardware fact a record settles belongs in the simulators, as a model or as a
refusal. Every evidence record from E600 whose tiers include HW or CAP is cited (an `E<nnn>`
token or a range, read as spec_coverage.py reads them) by a file of crates/sgx-sim, crates/sgx-pipe
or crates/pysgx (sources, tests, examples; a test replaying a vectors table counts), or it is
listed in crates/SIM_UNMODELLED.toml with a one-line reason. The list may only shrink: a listed
record that the code cites is a problem until it is removed, and so is a listed id that needs no
citation.

    python3 tools/records/sim_coverage.py --check
    python3 tools/records/sim_coverage.py --write-baseline

--write-baseline starts the list when there is none (every uncited record, its unit in the
reason); once it exists it only removes the records the code now cites, it never adds one.
"""
from __future__ import annotations

import pathlib
import sys
import tomllib

import evidence
from spec_coverage import FIRST, cited

ROOT = pathlib.Path(__file__).resolve().parents[2]
CRATES = ("sgx-sim", "sgx-pipe", "pysgx")
SKIP = {"target", "__pycache__", ".pytest_cache"}
BASELINE = "crates/SIM_UNMODELLED.toml"
HEADER = """\
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
# Hardware records (tier HW or CAP) from E600 that neither sgx-sim, sgx-pipe nor pysgx cites yet,
# as a model or a refusal, each with the reason. tools/records/sim_coverage.py --check; this list
# only shrinks (HACKING.md).
"""


def _records() -> dict[str, dict]:
    out = {}
    for p in (ROOT / "evidence").glob("*/E*.md"):
        fm, _ = evidence.parse(p)
        if int(fm["id"][1:]) >= FIRST and {"HW", "CAP"} & set(fm.get("tiers", [])):
            out[fm["id"]] = fm | {"unit": fm.get("unit") or p.parent.name}
    return out


def required() -> set[str]:
    """The hardware records from E600: tiers with HW or CAP."""
    return set(_records())


def sim_citations() -> set[str]:
    out = set()
    for c in CRATES:
        for p in (ROOT / "crates" / c).rglob("*"):
            if p.is_file() and not SKIP & set(p.relative_to(ROOT).parts):
                out |= cited(p.read_text(errors="replace"))
    return out


def load_baseline() -> dict[str, str]:
    p = ROOT / BASELINE
    return tomllib.loads(p.read_text()) if p.is_file() else {}


def problems(baseline: dict[str, str]) -> list[str]:
    need, have = required(), sim_citations()
    out = []
    for rid in sorted(need - have - set(baseline)):
        out.append(f"{rid}: cited by no sgx-sim, sgx-pipe or pysgx file and not in {BASELINE}")
    for rid in sorted(baseline):
        if rid not in need:
            out.append(f"{rid}: not a hardware record from E{FIRST}, remove it from {BASELINE}")
        elif rid in have:
            out.append(f"{rid}: cited by the simulator code, remove it from {BASELINE}")
        elif not str(baseline[rid]).strip():
            out.append(f"{rid}: listed without a reason")
    return out


def write_baseline() -> int:
    p = ROOT / BASELINE
    recs, have = _records(), sim_citations()
    if p.is_file():
        old = load_baseline()
        keep = {r: why for r, why in old.items() if r in recs and r not in have}
    else:
        keep = {r: f"{recs[r]['unit']}: not modelled or refused by sgx-sim or sgx-pipe yet"
                for r in recs if r not in have}
    lines = [f"{r} = {_quote(keep[r])}" for r in sorted(keep)]
    p.write_text(HEADER + "".join(f"{x}\n" for x in lines))
    print(f"{BASELINE}: {len(keep)} records")
    return 0


def _quote(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv == ["--write-baseline"]:
        return write_baseline()
    if argv not in ([], ["--check"]):
        print(__doc__, file=sys.stderr)
        return 2
    found = problems(load_baseline())
    for msg in found:
        print(msg)
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
