#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Scratch citations: the scratch area (~/src/scratch/resgx545) is disposable, so a path in it
that the tree cites must also be published. A cite is a path rooted in a scratch directory of
the closing pass (`closing/`, `closing2/`, `closing3/`, `closing4/`, ...), written bare or after
`scratch/resgx545/`, in a tracked text file; a path broken over two lines is joined. It resolves
to one of:

- a published session: `closingN/<name>/rest` is `<area>/closing-<name>/rest` of a data
  repository (the names the sessions had in scratch, as tools/closing/session_tests.sh maps them);
- a published copy: `cited/<cite>` of resgx545-data, or of resgx545-data-private when the file
  derives from the closed firmware (a reading of its disassembly).

The copies are datasets: datasets/cited-scratch.toml (data) and cited-scratch-private.toml
(data-private), `paths = ["cited/"]`, refreshed by --publish. Landed records keep their text; the
cite resolves through the rule above.

    python3 tools/records/scratch_cites.py --check          every cite resolves
    python3 tools/records/scratch_cites.py --list           the cites and where they resolve
    python3 tools/records/scratch_cites.py --publish [--private] CITE...
                                                            copy from scratch into cited/
"""
from __future__ import annotations

import datetime
import os
import pathlib
import re
import shutil
import subprocess
import sys

import datasets

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRATCH = (pathlib.Path(os.environ["RESGX545_SCRATCH"]) if os.environ.get("RESGX545_SCRATCH")
           else ROOT.parent / "scratch" / "resgx545")
TEXT = {".md", ".toml", ".py", ".rs", ".sh", ".txt", ".json"}
# Files whose closing paths are the mechanics of rebuilding the scratch layout, not citations.
MECHANICS = {"tools/closing/session_tests.sh", "tools/closing/test_session_tests.py",
             "tools/records/scratch_cites.py", "tools/records/test_scratch_cites.py"}
# Cite prefixes that name no file to publish, with the reason.
NOT_FILES = {"closing4/lead/wt": "round 4's integration worktree; FROZEN.commits pins its files "
                                 "to resgx545 commits"}
# Names a session had in scratch before it was published under another one.
ALIASES = {"s1b-v2": "s1b"}
SKIP = {"debug", "__pycache__", ".venv", ".pytest_cache"}
MANIFEST = {False: "cited-scratch", True: "cited-scratch-private"}

_PREFIX = re.compile(r"(?:(?:~|/Users/[^/\s]+|/home/[^/\s]+)/src/)?scratch/resgx545/")
_JOIN = re.compile(r"/[ \t]*\n[ \t]*(?:(?://[!/]?|#|\*)[ \t]*)?(?=[\w.-])")
_CITE = re.compile(r"(?<![\w./~-])(closing\d*/[\w.{}*-][\w./{}*-]*)")


def cites_in(text: str) -> list[str]:
    """The scratch cites of a text, in order, trailing punctuation dropped."""
    text = _JOIN.sub("/", _PREFIX.sub("", text))
    return [m.group(1).rstrip(".,") for m in _CITE.finditer(text)]


def tracked(root: pathlib.Path) -> list[str]:
    out = subprocess.run(["git", "-C", str(root), "ls-files", "-z"], capture_output=True,
                         check=True).stdout.decode()
    return [p for p in out.split("\0") if p]


def repos() -> dict[str, pathlib.Path]:
    return datasets.repos(ROOT)


def cites() -> dict[str, list[str]]:
    """{cite: [citing files]} over the tracked text files."""
    out: dict[str, list[str]] = {}
    for rel in tracked(ROOT):
        if rel in MECHANICS or pathlib.PurePath(rel).suffix not in TEXT:
            continue
        p = ROOT / rel
        if not p.is_file():
            continue
        for c in cites_in(p.read_text(errors="replace")):
            if any(c == n or c.startswith(n + "/") for n in NOT_FILES):
                continue
            out.setdefault(c, [])
            if rel not in out[c]:
                out[c].append(rel)
    return out


def resolve(cite: str) -> str | None:
    """'<repo>:<path>' where the cite is published, or None."""
    present = repos()
    parts = cite.split("/", 2)
    name = ALIASES.get(parts[1], parts[1]) if len(parts) > 1 else ""
    rest = parts[2] if len(parts) > 2 else ""
    for repo, base in present.items():
        if not name:
            break
        for s in sorted(base.glob(f"*/closing-{name}")):
            if s.is_dir() and (not rest or (s / rest).exists()):
                rel = s.relative_to(base).as_posix()
                return f"{repo}:{rel}/{rest}" if rest or cite.endswith("/") else f"{repo}:{rel}/"
    for repo, base in present.items():
        if (base / "cited" / cite).exists():
            return f"{repo}:cited/{cite}"
    return None


def problems() -> list[str]:
    return [f"{c}: not published (cited by {', '.join(who)})"
            for c, who in sorted(cites().items()) if resolve(c) is None]


def _copy(src: pathlib.Path, dst: pathlib.Path) -> None:
    if src.is_dir():
        shutil.copytree(src, dst, ignore=lambda d, names: [n for n in names if n in SKIP])
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def _manifest(private: bool, base: pathlib.Path) -> None:
    files, size, sha = datasets.digest(["cited/"], base)
    path = ROOT / "datasets" / f"{MANIFEST[private]}.toml"
    today = datetime.date.today().isoformat()
    if path.is_file():
        text = path.read_text()
        for key, val in (("files", str(files)), ("size", str(size)), ("sha256", f'"{sha}"'),
                         ("date", f'"{today}"')):
            text = re.sub(rf"(?m)^{key} = .*$", f"{key} = {val}", text, count=1)
    else:
        repo = "data-private" if private else "data"
        what = ("readings of the closed firmware's disassembly and other files derived from it"
                if private else "notes, scorers and outputs of the closing pass")
        text = (f'title = "files of the scratch area that the records cite: {what}"\n'
                f'repo = "{repo}"\npaths = ["cited/"]\n'
                f'method = "copied byte for byte from ~/src/scratch/resgx545/<cite> to '
                f'cited/<cite> by tools/records/scratch_cites.py --publish; a cite in a record '
                f'resolves to the copy"\n'
                f'date = "{today}"\nfiles = {files}\nsize = {size}\nsha256 = "{sha}"\n'
                f'recipe = "tools/records/scratch_cites.py"\n')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def publish(names: list[str], private: bool) -> None:
    """Copy each cite from scratch to cited/ of data (or data-private) and refresh its manifest."""
    repo = "data-private" if private else "data"
    base = repos().get(repo)
    if base is None:
        raise SystemExit(f"scratch_cites: the {repo} repository is not present")
    for c in names:
        src, dst = SCRATCH / c, base / "cited" / c
        if not src.exists():
            raise SystemExit(f"scratch_cites: {c} is not in the scratch area ({SCRATCH})")
        if dst.exists():
            raise SystemExit(f"scratch_cites: {c} is already published ({repo}:cited/{c})")
    for c in names:
        _copy(SCRATCH / c, base / "cited" / c)
    _manifest(private, base)


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if args[:1] == ["--publish"]:
        private = "--private" in args
        publish([a for a in args[1:] if a != "--private"], private)
        return 0
    if not repos():
        print("scratch_cites: no data repository present; cites not checked", file=sys.stderr)
        return 0
    if args[:1] == ["--list"]:
        for c, who in sorted(cites().items()):
            print(f"{c}\t{resolve(c) or 'UNPUBLISHED'}\t{', '.join(who)}")
        return 0
    bad = problems()
    for b in bad:
        print(b)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
