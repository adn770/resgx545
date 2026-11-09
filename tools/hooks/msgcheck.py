#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The commit message rules (the commit-msg hook): subject `topic: summary` of at most 70
characters, lowercase after the colon, no final period; a blank line; body lines of at most 80
columns; the trailer (Co-Authored-By, or Assisted-by in the forks) as the last line.

    python3 tools/hooks/msgcheck.py MESSAGE_FILE
"""
from __future__ import annotations

import pathlib
import re
import sys

SUBJECT = re.compile(r"^[^\s:][^:]*: (?=\S)(?![A-Z])")
EXEMPT = ("Merge ", "Revert ", "fixup! ", "squash! ", "amend! ")
TRAILER = re.compile(r"^(Co-Authored-By: .+ <.+>|Assisted-by: .+)$")


def check(text: str) -> list[str]:
    lines = [l for l in text.splitlines() if not l.startswith("#")]
    while lines and not lines[-1].strip():
        lines.pop()
    if not lines:
        return ["empty message"]
    problems = []
    subject = lines[0]
    if len(subject) > 70:
        problems.append(f"subject is {len(subject)} characters, at most 70")
    if not subject.startswith(EXEMPT):
        if not SUBJECT.match(subject):
            problems.append("subject must be `topic: summary`, lowercase after the colon")
        if subject.endswith("."):
            problems.append("subject ends with a period")
    if len(lines) > 1 and lines[1].strip():
        problems.append("a blank line must follow the subject")
    for n, line in enumerate(lines[1:], 2):
        if len(line) > 80 and " " in line.strip():
            problems.append(f"line {n} is {len(line)} columns, body wraps at 80")
    if not TRAILER.match(lines[-1]):
        problems.append("the last line must be the trailer (Co-Authored-By or Assisted-by)")
    return problems


def main(argv: list[str]) -> int:
    problems = check(pathlib.Path(argv[0]).read_text())
    for p in problems:
        print(f"commit-msg: {p}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
