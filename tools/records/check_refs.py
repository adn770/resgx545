#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Section references: a reference (`doc.md §N`, or a spec's short name before §) must name a
document the tree holds and, when that document numbers its headings, sections it has. A landed
document never points at one that is not there. Reads the tracked text files.

    python3 tools/records/check_refs.py --check [ROOT]
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]

# Short names the specs use for each other in section references ("transfer §4.2").
SPEC_NAMES = {"format": "doc/specs/fw_format.md", "transfer": "doc/specs/transfer.md",
              "hardware spec": "doc/specs/hw_spec.md", "hw spec": "doc/specs/hw_spec.md",
              "boot sequence": "doc/specs/boot_sequence.md",
              "edm dataflow": "doc/specs/edm_dataflow.md"}
SECTION_REF = re.compile(r"([\w./-]+\.md)[`)'\"]*\s*§|\b(" +
                         "|".join(sorted(SPEC_NAMES, key=len, reverse=True)) + r")(?:'s)?\s+§",
                         re.IGNORECASE)
# The sections a reference names after its document: "§9.4, §10.4", "§9-§11", "§4.2–§4.3".
SECTION_LIST = re.compile(r"§[\d.§,\s–-]*")
SECTION_NUM = re.compile(r"(?:§|[-–]\s*§?)(\d+(?:\.\d+)*)")
NUMBERED = re.compile(r"^#+\s+§?(\d+(?:\.\d+)*)\.?\s", re.MULTILINE)


def tracked(root: pathlib.Path) -> list[pathlib.Path]:
    out = subprocess.run(["git", "-C", str(root), "ls-files", "-z"], capture_output=True,
                         check=True).stdout.decode().split("\0")
    return [root / f for f in out if f and (root / f).is_file()]


def check(root: pathlib.Path, files: list[pathlib.Path]) -> list[str]:
    """The problems, one line each: file:line and what is wrong."""
    paths: dict[str, pathlib.Path] = {}
    for f in files:
        if f.suffix == ".md":
            paths.setdefault(f.name, f)
    sections: dict[pathlib.Path, set[str]] = {}
    problems = []
    for f in sorted(files):
        data = f.read_bytes()
        if b"\0" in data[:8192]:
            continue
        rel = f.relative_to(root)
        for n, line in enumerate(data.decode("utf-8", errors="replace").splitlines(), 1):
            for m in SECTION_REF.finditer(line):
                doc = m.group(1) or SPEC_NAMES[m.group(2).lower()]
                target = next((p for p in (root / doc, f.parent / doc) if p.is_file()),
                              paths.get(doc) if "/" not in doc else None)
                if target is None:
                    problems.append(f"{rel}:{n}: {m.group(0)!r}: reference into an absent "
                                    "document")
                    continue
                if target not in sections:
                    sections[target] = set(NUMBERED.findall(target.read_text(errors="replace")))
                have = sections[target]
                tail = SECTION_LIST.match(line, m.end() - 1)
                for s in SECTION_NUM.findall(tail.group(0) if tail else ""):
                    if have and s not in have:
                        problems.append(f"{rel}:{n}: {doc} §{s}: reference into an absent "
                                        "section")
    return problems


def main(argv: list[str]) -> int:
    args = [a for a in argv if a != "--check"]
    root = pathlib.Path(args[0]).resolve() if args else ROOT
    problems = check(root, tracked(root))
    print("\n".join(problems))
    print(f"check_refs: {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
