#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The key of a session_tests.sh pass (standard library only).

    python3 tools/closing/passcache.py key SESSION_DIR TOOL PY RUNNER...

prints the sha256 of the parts a pass depends on: the session's path, a digest of its files
(path and content of each, links by their target), the runner's own digest (RUNNER files:
session_tests.sh and this file), the commits the session pins in its FROZEN.commits (the
session's and those of its parts; data: and resgx545: lines alike; the tool tree's HEAD when
no line pins the tool tree, since the run then checks out HEAD), and PY (as given and resolved).
session_tests.sh records a pass as $RESGX545_SESSION_TARGET/passes/<key> and, with --cached,
skips a run whose key is there.
"""
from __future__ import annotations

import hashlib
import os
import pathlib
import subprocess
import sys


def _files_digest(session: pathlib.Path) -> str:
    h = hashlib.sha256()
    for p in sorted(session.rglob("*")):
        rel = p.relative_to(session).as_posix()
        if p.is_symlink():
            h.update(f"L {rel} {os.readlink(p)}\n".encode())
        elif p.is_file():
            h.update(f"F {rel} {hashlib.sha256(p.read_bytes()).hexdigest()}\n".encode())
    return h.hexdigest()


def _pins(session: pathlib.Path) -> tuple[list[str], bool]:
    """(pinned commits, whether any line pins the tool tree)."""
    commits, tool = set(), False
    for cm in [session / "FROZEN.commits", *sorted(session.glob("*/FROZEN.commits"))]:
        if not cm.is_file():
            continue
        for line in cm.read_text().splitlines():
            f = line.split()
            if line.startswith("#") or len(f) < 3 or f[1] == "untracked":
                continue
            commits.add(f[1])
            prefix = f[2].split(":", 1)[0] if ":" in f[2] else None
            tool |= prefix in (None, "resgx545")
    return sorted(commits), tool


def parts(session: pathlib.Path, tool: pathlib.Path, py: str,
          runner: list[pathlib.Path]) -> list[str]:
    session = pathlib.Path(session).resolve()
    rh = hashlib.sha256()
    for r in runner:
        rh.update(hashlib.sha256(pathlib.Path(r).read_bytes()).digest())
    commits, pins_tool = _pins(session)
    if not pins_tool:
        head = subprocess.run(["git", "-C", str(tool), "rev-parse", "HEAD"],
                              capture_output=True, text=True).stdout.strip()
        commits.append(f"HEAD={head}")
    return [f"session {session}", f"files {_files_digest(session)}", f"runner {rh.hexdigest()}",
            f"commits {' '.join(commits)}", f"py {py} {os.path.realpath(py)}"]


def key(session: pathlib.Path, tool: pathlib.Path, py: str, runner: list[pathlib.Path]) -> str:
    return hashlib.sha256("\n".join(parts(session, tool, py, runner)).encode()).hexdigest()


def main(argv: list[str]) -> int:
    if len(argv) < 5 or argv[0] != "key":
        print(__doc__.strip().splitlines()[2].strip(), file=sys.stderr)
        return 2
    print(key(pathlib.Path(argv[1]), pathlib.Path(argv[2]), argv[3],
              [pathlib.Path(r) for r in argv[4:]]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
