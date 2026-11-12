#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Freezes pinned by commit: FROZEN.commits beside a published session's FROZEN*.sha256.

A session of the closing pass (render/closing-*, edm/closing-* in resgx545-data) freezes its
inputs before the first job in FROZEN.sha256 ("sha256  path" lines). Some lines pin files of
this tree by absolute path (a path with a component named resgx545, e.g.
/Users/.../src/resgx545/tools/fwtask/fwtask.py). When the tree changes those files, the freeze
no longer verifies standalone. FROZEN.commits names, for each such pin, a resgx545 commit whose
blob at that path has exactly the pinned sha256:

    # (header comments)
    <sha256>  <commit>  <path relative to the resgx545 tree>

one line per pinned file and hash, over every FROZEN*.sha256 of the session. A pinned file the
history never tracked (a build product, such as the ignored tools/usse-asm/usse-asm) has no
commit: its line says `untracked` in the commit's place, and that pin still verifies only against
the file itself. A pin of a worktree that sat under scratch/resgx545/ (round 4 froze against
closing4/lead/wt, listed in scratch_cites.NOT_FILES) is named by the FROZEN.commits line with its
hash whose path ends it. Any other line under scratch/resgx545/ is an input the session read from
scratch (round 5's r5-events froze its plan, the decisions and a reading of the firmware): no file
of the tool tree but a cite, published as cited/<path> of resgx545-data or of
resgx545-data-private, and checked against that copy. The published freeze bytes are never
rewritten: FROZEN.commits is a new file beside them.

--write finds, for each session whose freezes pin resgx545 files and that has no
FROZEN.commits, the commits in this tree's history (`git log -- <path>`): the newest commit at
or before the session's date (the date of the dataset manifest holding the session) whose blob
has the pinned hash, else the oldest after it. A pin of a tracked path that no commit holds is
reported, never guessed, and the session gets no file. An existing FROZEN.commits is never
replaced (one that differs from what would be written is reported).

--check verifies every FROZEN.commits: each resgx545 pin of the session's freezes has a line,
each line is a pin, `git show <commit>:<path>` hashes to the pinned sha256, and an untracked
line names a path the history has never tracked; each scratch input has a published copy with its
hash (one found in neither repository is reported only when the private one is present). Once any session has a FROZEN.commits, a
session whose freezes pin resgx545 files without one is a problem. It skips quietly when the
data repository (found as datasets.py finds it) or this tree's git history is absent.

    python3 tools/records/frozen.py [--check]   check the FROZEN.commits of the data
    python3 tools/records/frozen.py --write     write the missing ones
"""
from __future__ import annotations

import hashlib
import pathlib
import re
import subprocess
import sys

import datasets
import scratch_cites

ROOT = datasets.ROOT
NAME = "FROZEN.commits"
UNTRACKED = "untracked"
TREE = "resgx545"
SCRATCH = "/scratch/resgx545/"
HEADER = """\
# FROZEN.commits: the resgx545 commit that holds each file of the resgx545 tree this session's
# FROZEN*.sha256 pin by absolute path. One line per pinned file and hash: the sha256, the
# commit, the path relative to the resgx545 tree. Verify a pin with
# `git -C resgx545 show <commit>:<path> | sha256sum`. "untracked" in the commit's place: a file
# resgx545 never tracked (a build product), verifiable only against the file itself. Written by
# tools/records/frozen.py --write; the freezes themselves are never rewritten.
"""
LINE = re.compile(r"([0-9a-f]{64})  ([0-9a-f]{7,40}|" + UNTRACKED + r")  (\S.*)")


def pins(freeze: pathlib.Path) -> list[tuple[str, str]]:
    """(sha256, path in the resgx545 tree) of a freeze's absolute lines under the tree: the
    path after the first component named resgx545. Other lines are not pins."""
    out = []
    for line in freeze.read_text().splitlines():
        m = re.fullmatch(r"([0-9a-f]{64}) [ *](.+)", line)
        if not m or not m[2].startswith("/"):
            continue
        parts = pathlib.PurePosixPath(m[2]).parts
        if TREE in parts[1:]:
            i = parts.index(TREE)
            if i + 1 < len(parts):
                out.append((m[1], "/".join(parts[i + 1:])))
    return out


def freezes(session: pathlib.Path) -> list[pathlib.Path]:
    return sorted(session.glob("FROZEN*.sha256"))


def committed(session: pathlib.Path) -> dict[str, set[str]]:
    """{sha256: paths} of the session's FROZEN.commits lines (empty without one)."""
    out: dict[str, set[str]] = {}
    f = session / NAME
    for line in f.read_text().splitlines() if f.exists() else []:
        m = LINE.fullmatch(line)
        if m:
            out.setdefault(m[1], set()).add(m[3])
    return out


def scratch_inputs(session: pathlib.Path) -> list[tuple[str, str]]:
    """(sha256, path below scratch/resgx545/) of the freezes' lines under the scratch tree outside
    the worktrees whose files FROZEN.commits pins (scratch_cites.NOT_FILES): inputs read from
    scratch, not pins of the tool tree."""
    out = set()
    for f in freezes(session):
        for line in f.read_text().splitlines():
            m = re.fullmatch(r"([0-9a-f]{64}) [ *](/.+)", line)
            if not m or SCRATCH not in m[2]:
                continue
            rel = m[2].split(SCRATCH, 1)[1]
            if not any(rel.startswith(n + "/") for n in scratch_cites.NOT_FILES):
                out.add((m[1], rel))
    return sorted(out, key=lambda p: (p[1], p[0]))


def session_pins(session: pathlib.Path) -> list[tuple[str, str]]:
    """The distinct pins of all the session's freezes, in path then hash order. A pin of a
    worktree that sat under scratch/resgx545/ (round 4 froze against closing4/lead/wt) reads
    as the path below scratch's resgx545; a FROZEN.commits line with the pin's hash whose path
    ends that path names it."""
    known = committed(session)
    inputs = set(scratch_inputs(session))
    out = set()
    for f in freezes(session):
        for sha256, path in pins(f):
            if (sha256, path) in inputs:
                continue
            named = [p for p in known.get(sha256, ()) if path.endswith("/" + p)]
            out.add((sha256, named[0] if len(named) == 1 and path not in known[sha256]
                     else path))
    return sorted(out, key=lambda p: (p[1], p[0]))


def sessions(data: pathlib.Path) -> list[pathlib.Path]:
    """The directories of the data repository that hold a FROZEN*.sha256."""
    return sorted({f.parent for f in data.rglob("FROZEN*.sha256")
                   if ".git" not in f.relative_to(data).parts})


def has_history(repo: pathlib.Path) -> bool:
    r = subprocess.run(["git", "-C", str(repo), "rev-parse", "--verify", "-q", "HEAD"],
                       capture_output=True)
    return r.returncode == 0


class Finder:
    """The resgx545 history of a path, and the hash of its blob at a commit."""

    def __init__(self, repo: pathlib.Path):
        self.repo = repo
        self._log: dict[str, list[tuple[str, str]]] = {}
        self._sha: dict[str, str | None] = {}

    def _git(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(["git", "-C", str(self.repo), *args], capture_output=True)

    def log(self, path: str) -> list[tuple[str, str]]:
        """(commit, committer date) of the commits that touch the path, newest first."""
        if path not in self._log:
            r = self._git("log", "--full-history", "--format=%H %cs", "--", path)
            self._log[path] = [tuple(x.split()) for x in r.stdout.decode().splitlines()]
        return self._log[path]

    def sha(self, commit: str, path: str) -> str | None:
        """sha256 of the path's blob at the commit, None when there is none."""
        key = f"{commit}:{path}"
        if key not in self._sha:
            r = self._git("cat-file", "blob", key)
            self._sha[key] = hashlib.sha256(r.stdout).hexdigest() if r.returncode == 0 else None
        return self._sha[key]

    def commit(self, path: str, sha256: str, date: str) -> str | None:
        """The newest commit at or before the date whose blob of path hashes to sha256, else the
        oldest after the date, else None."""
        hits = [(c, d) for c, d in self.log(path) if self.sha(c, path) == sha256]
        before = [c for c, d in hits if d <= date]
        if before:
            return before[0]
        return hits[-1][0] if hits else None


def commits_for(session: pathlib.Path, find: Finder, date: str) -> tuple[str, list[str]]:
    """(the FROZEN.commits text, the pins no commit holds) of a session."""
    lines, bad = [], []
    for sha256, path in session_pins(session):
        c = find.commit(path, sha256, date)
        if c is None and not find.log(path):
            lines.append(f"{sha256}  {UNTRACKED}  {path}\n")
        elif c is None:
            bad.append(f"{path} {sha256}: no resgx545 commit holds this hash")
        else:
            lines.append(f"{sha256}  {c}  {path}\n")
    return HEADER + "".join(lines), bad


def session_dates(manifests: dict[str, dict], names: list[str]) -> dict[str, str]:
    """{session: date} of the sessions (paths relative to the data repository) that a manifest
    of the data repository holds: a manifest path is the session, under it, or above it."""
    out = {}
    for name in names:
        for d in manifests.values():
            if d.get("repo") != "data":
                continue
            for p in d.get("paths", []):
                p = p.rstrip("/")
                if p == name or p.startswith(name + "/") or name.startswith(p + "/"):
                    out.setdefault(name, d["date"])
    return out


def write(data: pathlib.Path, repo: pathlib.Path, dates: dict[str, str]) -> list[str]:
    """Write the missing FROZEN.commits of the data repository; return the problems."""
    find, bad = Finder(repo), []
    for s in sessions(data):
        name = s.relative_to(data).as_posix()
        if not session_pins(s):
            continue
        if name not in dates:
            bad.append(f"{name}: no dataset manifest gives the session's date")
            continue
        text, missing = commits_for(s, find, dates[name])
        if (s / NAME).exists():
            if missing or (s / NAME).read_text() != text:
                bad.append(f"{name}: {NAME} exists and differs from what would be written; "
                           "not replaced")
            continue
        if missing:
            bad += [f"{name}: {m}" for m in missing]
            continue
        (s / NAME).write_text(text)
        n = text.count("\n") - HEADER.count("\n")
        loose = text.count(f"  {UNTRACKED}  ")
        print(f"{name}/{NAME}: {n} pins" + (f", {loose} untracked" if loose else ""))
    return bad


def check(data: pathlib.Path, repo: pathlib.Path,
          private: pathlib.Path | None = None) -> list[str]:
    """What is wrong with the FROZEN.commits of the data repository (and the published copies of
    the scratch inputs, in it or in the private one)."""
    find, bad = Finder(repo), []
    all_sessions = sessions(data)
    adopted = any((s / NAME).exists() for s in all_sessions)
    for s in all_sessions:
        name = s.relative_to(data).as_posix()
        want = set(session_pins(s))
        if not (s / NAME).exists():
            if adopted and want:
                bad.append(f"{name}: pins {len(want)} resgx545 files and has no {NAME}")
            continue
        have = set()
        for line in (s / NAME).read_text().splitlines():
            if not line.strip() or line.startswith("#"):
                continue
            m = LINE.fullmatch(line)
            if not m:
                bad.append(f"{name}/{NAME}: not '<sha256>  <commit>  <path>': {line!r}")
                continue
            sha256, c, path = m.groups()
            have.add((sha256, path))
            if (sha256, path) not in want:
                bad.append(f"{name}/{NAME}: {path} {sha256} is pinned by no freeze")
            if c == UNTRACKED:
                if find.log(path):
                    bad.append(f"{name}/{NAME}: {path} is tracked in resgx545: pin it by commit")
                continue
            got = find.sha(c, path)
            if got is None:
                bad.append(f"{name}/{NAME}: {c}:{path} is not in the resgx545 history")
            elif got != sha256:
                bad.append(f"{name}/{NAME}: {c}:{path} hashes to {got}, not {sha256}")
        bad += [f"{name}: {path} {sha256} has no line in {NAME}"
                for sha256, path in sorted(want - have, key=lambda p: p[1])]
        for sha256, path in scratch_inputs(s):
            copies = [b / "cited" / path for b in (data, private) if b is not None]
            copies = [p for p in copies if p.is_file()]
            if not copies:
                if private is not None:
                    bad.append(f"{name}: scratch input {path} is not published (cited/{path})")
                continue
            got = hashlib.sha256(copies[0].read_bytes()).hexdigest()
            if got != sha256:
                bad.append(f"{name}: cited/{path} hashes to {got}, not {sha256}")
    return bad


def main(argv: list[str] | None = None) -> int:
    a = sys.argv[1:] if argv is None else argv
    if any(x not in ("--check", "--write") for x in a) or len(a) > 1:
        print("usage: frozen.py [--check | --write]", file=sys.stderr)
        return 2
    data = datasets.repos().get("data")
    if data is None or not has_history(ROOT):
        return 0
    if "--write" in a:
        names = [s.relative_to(data).as_posix() for s in sessions(data)]
        bad = write(data, ROOT, session_dates(datasets.load(datasets.DIR), names))
    else:
        bad = check(data, ROOT, datasets.repos().get("data-private"))
    if bad:
        print("\n".join(bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
