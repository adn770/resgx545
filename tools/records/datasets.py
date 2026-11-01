#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Dataset manifests: datasets/<id>.toml, one per body of data the evidence rests on. The
bytes live in one of two companion repositories: resgx545-data (public, our own runs) or
resgx545-data-private (private: captures of the closed driver and anything derived from
its firmware). The campaign runner (tools/campaign, a later unit) writes both the data and
its manifest.

    title = "probe table usse/branch"
    repo = "data"                       # data | data-private
    paths = ["usse/branch/"]            # relative, within that repository
    method = "campaign runner on the laptop target (tools/campaign)"
    date = "2026-11-01"                 # of the run, a string
    files = 12                          # at least 1
    size = 34567                        # bytes
    sha256 = "..."                      # 64 lower-case hex digits: see digest()
    recipe = "probes/usse/branch.toml"  # the table, or the script, that made it

Evidence names a dataset by id (`data = ["usse-branch"]`) or a part of one
(`"usse-branch:usse-branch-quad/"`); tracked repository files are named by path.

A repository is found in $RESGX545_DATA / $RESGX545_DATA_PRIVATE, else beside this checkout
(../resgx545-data, ../resgx545-data-private). Manifests of a repository that is not present
are checked for form only.

    python3 tools/records/datasets.py   check the records against the data checked out
"""
from __future__ import annotations

import datetime
import hashlib
import os
import pathlib
import re
import sys
import tomllib

ROOT = pathlib.Path(__file__).resolve().parents[2]
DIR = ROOT / "datasets"
KEYS = ["title", "repo", "paths", "method", "date", "files", "size", "sha256", "recipe"]
REPOS = {"data": ("RESGX545_DATA", "resgx545-data"),
         "data-private": ("RESGX545_DATA_PRIVATE", "resgx545-data-private")}


def repos(root: pathlib.Path = ROOT) -> dict[str, pathlib.Path]:
    """{repo: path} of the data repositories present. A variable that is set but names no
    directory is a mistake, not an absent repository: it is warned about on stderr."""
    out = {}
    for repo, (var, name) in REPOS.items():
        p = pathlib.Path(os.environ[var]) if os.environ.get(var) else root.parent / name
        if p.is_dir():
            out[repo] = p
        elif os.environ.get(var):
            print(f"datasets.py: ${var} is set to {p}, which is not a directory; "
                  f"the {repo} repository is skipped", file=sys.stderr)
    return out


def files_of(paths: list[str], root: pathlib.Path) -> list[pathlib.Path]:
    out = []
    for p in paths:
        q = root / p
        out += [q] if q.is_file() else sorted(x for x in q.rglob("*") if x.is_file())
    return sorted(set(out))


def digest(paths: list[str], root: pathlib.Path) -> tuple[int, int, str]:
    """(files, size, sha256) of a dataset's files. The sha256 is of the 'sha256  path' lines
    of the files in path order (component by component), paths relative to the repository
    root, each line ended by a newline."""
    lines, size = [], 0
    fs = files_of(paths, root)
    for f in fs:
        data = f.read_bytes()
        size += len(data)
        lines.append(f"{hashlib.sha256(data).hexdigest()}  {f.relative_to(root).as_posix()}\n")
    return len(fs), size, hashlib.sha256("".join(lines).encode()).hexdigest()


def load(path: pathlib.Path = DIR) -> dict[str, dict]:
    return {p.stem: tomllib.loads(p.read_text()) for p in sorted(pathlib.Path(path).glob("*.toml"))}


def _path_problem(p: object) -> str | None:
    """Why a manifest path is not a relative path within its repository (None if it is)."""
    if not isinstance(p, str):
        return f"path {p!r} is not a string"
    q = pathlib.PurePosixPath(p)
    if q.is_absolute() or p.startswith("\\") or re.match(r"[A-Za-z]:", p):
        return f"path {p!r} is absolute"
    if ".." in q.parts:
        return f"path {p!r} has a '..' component"
    if not q.parts:
        return f"path {p!r} names the whole repository"
    return None


def _date_ok(v: str) -> bool:
    try:
        datetime.date.fromisoformat(v)
    except ValueError:
        return False
    return bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", v))


def _form(d: dict) -> list[str]:
    """What is wrong with the form of a record whose keys are right."""
    out = []
    if not isinstance(d["repo"], str) or d["repo"] not in REPOS:
        out.append(f"repo {d['repo']!r} not in {sorted(REPOS)}")
    for k in ("title", "method", "recipe"):
        if not isinstance(d[k], str) or not d[k].strip():
            out.append(f"{k} is not a non-empty string")
    if not isinstance(d["paths"], list) or not d["paths"]:
        out.append("paths is not a non-empty list")
    else:
        out += [m for m in map(_path_problem, d["paths"]) if m]
    if not isinstance(d["date"], str):
        out.append("date is not a string")
    elif not _date_ok(d["date"]):
        out.append(f"date {d['date']!r} is not YYYY-MM-DD")
    for k, least in (("files", 1), ("size", 0)):
        if type(d[k]) is not int or d[k] < least:
            out.append(f"{k} {d[k]!r} is not an integer >= {least}")
    if not isinstance(d["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", d["sha256"]):
        out.append(f"sha256 {d['sha256']!r} is not 64 lower-case hex digits")
    return out


def problems(ident: str, d: dict, present: dict[str, pathlib.Path]) -> list[str]:
    """What is wrong with one record: its form always, its bytes when its repo is present."""
    if list(d) != KEYS:
        return [f"{ident}: keys {list(d)} != {KEYS}"]
    bad = _form(d)
    if bad:
        return [f"{ident}: {m}" for m in bad]
    root = present.get(d["repo"])
    if root is None:
        return []
    if not all((root / p).exists() for p in d["paths"]):
        return [f"{ident}: missing from {d['repo']}"]
    top = root.resolve()
    outside = [p for p in d["paths"] if not (root / p).resolve().is_relative_to(top)]
    if not outside:               # a path that leaves the repository is not walked
        outside = [f.relative_to(root).as_posix() for f in files_of(d["paths"], root)
                   if not f.resolve().is_relative_to(top)]
    if outside:
        return [f"{ident}: {p} resolves outside the repository" for p in outside]
    n, size, sha = digest(d["paths"], root)
    if (n, size, sha) != (d["files"], d["size"], d["sha256"]):
        return [f"{ident}: contents changed ({n} files, {size} bytes)"]
    return []


def main() -> int:
    present = repos()
    bad = [m for i, d in load(DIR).items() for m in problems(i, d, present)]
    if bad:
        print("\n".join(bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
