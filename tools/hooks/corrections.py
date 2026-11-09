#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Landed records get dated corrections only: a staged change to an existing evidence record
should append a `Correction YYYY-MM-DD: ...` section and leave the rest as it was. This only
warns (it never blocks): the pre-commit hook prints each record that was changed otherwise.

    python3 tools/hooks/corrections.py [REPO]     the staged changes of REPO (default: .)
"""
from __future__ import annotations

import re
import subprocess
import sys

LANDED = re.compile(r"^evidence/.+\.md$")
CORRECTION = re.compile(r"^(?:#+\s+|\*\*)?Correction \d{4}-\d{2}-\d{2}:", re.MULTILINE)


def warning(path: str, old: str | None, new: str) -> str | None:
    if old is None or not LANDED.match(path) or old == new:
        return None
    head = old.rstrip("\n")
    if new.startswith(head) and CORRECTION.search(new[len(head):]):
        return None
    return (f"{path}: a landed record changed other than by an appended "
            "`Correction YYYY-MM-DD:` section (warning only)")


def _git(repo: str, *args: str) -> bytes:
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, check=True).stdout


def main(argv: list[str]) -> int:
    repo = argv[0] if argv else "."
    status = _git(repo, "diff", "--cached", "--no-renames", "--name-status", "-z"
                  ).decode().split("\0")
    for st, path in zip(status[0::2], status[1::2]):
        if st == "M" and LANDED.match(path):
            old = _git(repo, "show", f"HEAD:{path}").decode(errors="replace")
            new = _git(repo, "show", f":{path}").decode(errors="replace")
            w = warning(path, old, new)
            if w:
                print(f"corrections: warning: {w}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
