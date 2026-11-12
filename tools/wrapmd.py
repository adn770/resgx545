#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Wrap over-long Markdown prose lines to 100 columns.

    python3 tools/wrapmd.py [--check] [--fix] FILE...

Only prose lines longer than the limit change: they break at spaces, keep their indentation (a
list item's continuation lines are indented to its text) and never gain a list marker or heading.
Fenced and indented code, tables, headings, front matter, HTML, link reference definitions and
single words longer than the limit are left alone. `--check` lists the lines that would change
and exits 1; `--fix` rewrites the files in place.
"""
from __future__ import annotations

import re
import sys

LIMIT = 100
LIST_RE = re.compile(r"^(\s*)((?:[-*+]|\d{1,9}[.)])\s+)")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
REF_RE = re.compile(r"^\s{0,3}\[[^\]]+\]:\s")
MARKER_RE = re.compile(r"^(?:[-*+]|\d{1,9}[.)]|#{1,6}|>|\||```|~~~|\[[^\]]*\]:)$")


def _prefix(line: str) -> tuple[str, str]:
    """Split a prose line into (continuation prefix, text)."""
    m = LIST_RE.match(line)
    if m:
        return " " * len(m.group(0)), line[len(m.group(0)):]
    m = re.match(r"^(\s*(?:>\s?)+)", line)
    if m:
        return m.group(1), line[len(m.group(1)):]
    m = re.match(r"^\s*", line)
    return m.group(0), line[m.end():]


def _break(line: str, limit: int) -> list[str]:
    cont, _ = _prefix(line)
    out = []
    first = True
    while len(line) > limit:
        floor = len(cont) if not first else len(_head(line))
        cut = None
        for i in range(min(limit, len(line) - 1), floor, -1):
            if line[i] == " " and line[:i].strip() and _ok_next(line[i + 1:]):
                cut = i
                break
        if cut is None:  # one word wider than the limit: break after it
            for i in range(max(limit, floor + 1), len(line) - 1):
                if line[i] == " " and _ok_next(line[i + 1:]):
                    cut = i
                    break
        if cut is None:
            break
        out.append(line[:cut].rstrip())
        line = cont + line[cut + 1:].lstrip()
        first = False
    out.append(line)
    return out


def _head(line: str) -> str:
    return line[: len(line) - len(_prefix(line)[1])]


def _ok_next(rest: str) -> bool:
    word = rest.split(" ", 1)[0]
    return bool(word) and not MARKER_RE.match(word)


def wrap_lines(lines: list[str], limit: int = LIMIT) -> list[str]:
    out: list[str] = []
    fence = None
    front = None
    in_list = False
    prev_blank = True
    for n, line in enumerate(lines):
        stripped = line.strip()
        if n == 0 and stripped in ("+++", "---"):
            front = stripped
            out.append(line)
            continue
        if front is not None:
            out.append(line)
            if stripped == front:
                front = None
            continue
        m = FENCE_RE.match(line)
        if fence is not None:
            out.append(line)
            if m and m.group(1) == fence:
                fence = None
            continue
        if m:
            fence = m.group(1)
            out.append(line)
            prev_blank = False
            continue
        if not stripped:
            out.append(line)
            prev_blank = True
            continue
        indent = len(line) - len(line.lstrip(" "))
        is_item = bool(LIST_RE.match(line))
        if is_item:
            in_list = True
        elif indent == 0 and not line.startswith(">"):
            in_list = False
        skip = (
            len(line) <= limit
            or stripped.startswith(("|", "#", "<"))
            or REF_RE.match(line)
            or (indent >= 4 and prev_blank and not in_list)
        )
        prev_blank = False
        out.extend([line] if skip else _break(line, limit))
    return out


def wrap_text(text: str, limit: int = LIMIT) -> str:
    return "\n".join(wrap_lines(text.split("\n"), limit))


def main(argv: list[str]) -> int:
    check = "--check" in argv
    fix = "--fix" in argv
    files = [a for a in argv if not a.startswith("--")]
    if not files or check == fix and not check:
        print(__doc__, file=sys.stderr)
        return 2
    bad = 0
    for name in files:
        with open(name, encoding="utf-8") as f:
            text = f.read()
        new = wrap_text(text)
        if new == text:
            continue
        if fix:
            with open(name, "w", encoding="utf-8") as f:
                f.write(new)
        else:
            old = text.split("\n")
            for n, l in enumerate(old, 1):
                if len(l) > LIMIT and l not in new.split("\n"):
                    print(f"{name}:{n}: {len(l)} columns (run tools/wrapmd.py --fix {name})")
            bad = 1
    return bad


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
