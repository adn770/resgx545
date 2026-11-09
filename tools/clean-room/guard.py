#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The clean-room guard (HACKING.md, "Workflow"): nothing found only in the confidential
sources, and none of the private patterns or renamed-away spellings, may be in this
repository's files, commit messages or history.

The forbidden set is derived on each run: the identifiers of the confidential tree, minus those
of the public reference trees, the open GPU driver code and the closed libraries' strings. No
token list is stored anywhere. The data that decides lives in a private directory, never in a
public repository: `RESGX545_GUARD_DIR` (default `../resgx545-data-private/clean-room/` beside
this checkout) holds

    allowed.txt          reviewed exceptions, whitespace separated words, `#` comments
    patterns.txt         `scope<TAB>regex` per line; scope d1 (everywhere) or fork
    oldnames.toml        [rename] old spelling = settled spelling
    glossary-reviewed.txt  sha256 of each confidential-only token that was reviewed and may
                         stay; a glossary term allows nothing by existing
    refs.local.toml      the machine-local paths of the trees (untracked; see
                         refs.local.toml.example)

    python3 tools/clean-room/guard.py [--tree [PATH] | --staged | --history REPO
              [--base REV] [--fork] | --message FILE | --accept-glossary] [--show] [--no-glossary]

Output names a file, a line and a category; the matched text is shown only as a short hash,
unless --show. Exit 0 clean, 1 findings, 2 data absent with RESGX545_REQUIRE_GUARD=1. With the
data absent and no REQUIRE the run says loudly that nothing was checked and exits 0."""
from __future__ import annotations

import argparse
import dataclasses
import hashlib
import os
import pathlib
import re
import subprocess
import sys
import threading
import tomllib

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TOKEN = re.compile(rb"(?<![A-Za-z0-9_])[A-Za-z_][A-Za-z0-9_]{3,}")
MAX_FILE = 20_000_000


class GuardMissing(Exception):
    """The private data, or a tree it names, is not there."""


def required() -> bool:
    return os.environ.get("RESGX545_REQUIRE_GUARD") == "1"


def guard_dir() -> pathlib.Path:
    env = os.environ.get("RESGX545_GUARD_DIR")
    return pathlib.Path(env) if env else ROOT.parent / "resgx545-data-private" / "clean-room"


def sha(word: str | bytes) -> str:
    return hashlib.sha256(word if isinstance(word, bytes) else word.encode()).hexdigest()


@dataclasses.dataclass
class Rules:
    forbidden: set[bytes]
    allowed: set[str]
    patterns: list[tuple[str, re.Pattern]]
    oldnames: re.Pattern | None
    oldkey: dict[str, str]
    unreviewed: set[str]            # sha256 of glossary tokens that are forbidden and not reviewed
    reviewed: set[str] = dataclasses.field(default_factory=set)   # sha256 of reviewed tokens


@dataclasses.dataclass
class Finding:
    category: str                   # token, pattern-d1, pattern-fork, oldname
    where: str                      # a path, or "message"
    line: int = 0
    digest: str = ""                # sha256 of the matched text
    match: str = ""
    commit: str = ""

    def render(self, show: bool = False) -> str:
        at = f"{self.where}:{self.line}" if self.line else self.where
        pre = f"{self.commit[:10]} " if self.commit else ""
        what = self.match if show else self.digest[:8]
        return f"{pre}{at}: {self.category} [{what}]"


# --- the data ----------------------------------------------------------------------------

def tokens(root: pathlib.Path) -> set[bytes]:
    out: set[bytes] = set()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for f in filenames:
            p = os.path.join(dirpath, f)
            try:
                if os.path.getsize(p) <= MAX_FILE:
                    with open(p, "rb") as fh:
                        out.update(TOKEN.findall(fh.read()))
            except OSError:
                pass
    return out


def glossary_tokens(rows) -> set[str]:
    """The identifier-like words the glossary's terms and source spellings are made of."""
    out: set[str] = set()
    for r in rows:
        out |= {r["term"], *r["name"].split(".")}
    return out


def _words(text: str) -> set[str]:
    return {w for line in text.splitlines() if not line.startswith("#") for w in line.split()}


def _read(path: pathlib.Path) -> str:
    try:
        return path.read_text()
    except OSError as e:
        raise GuardMissing(f"{path}: {e.strerror}") from e


def _oldnames(names) -> tuple[re.Pattern | None, dict[str, str]]:
    names = list(names)
    if not names:
        return None, {}
    alts = sorted({n.lstrip(".") for n in names}, key=len, reverse=True)
    pat = re.compile(r"(?:(?<=\\n)|(?<![A-Za-z0-9]))(" + "|".join(map(re.escape, alts))
                     + r")(?![A-Za-z0-9])")
    return pat, {n.lstrip("."): n for n in names}


def load_rules(gdir: pathlib.Path, terms=None) -> Rules:
    """The rules from the private directory. terms: the glossary's tokens (None: read this
    repository's glossary; an empty tuple: none)."""
    gdir = pathlib.Path(gdir)
    if not gdir.is_dir():
        raise GuardMissing(f"{gdir}: no such directory (RESGX545_GUARD_DIR)")
    refs = tomllib.loads(_read(gdir / "refs.local.toml"))
    conf = pathlib.Path(refs["confidential"])
    if not conf.is_dir():
        raise GuardMissing("the confidential tree named in refs.local.toml is not there")
    only = tokens(conf)
    public_root = pathlib.Path(refs.get("public_root", "."))
    others = [public_root / p for p in refs.get("public", [])]
    others += [pathlib.Path(p) for p in refs.get("rogue", []) + refs.get("libs", [])]
    for d in others:
        if d.is_dir():
            only -= tokens(d)
    allowed = _words(_read(gdir / "allowed.txt"))
    patterns = []
    for line in _read(gdir / "patterns.txt").splitlines():
        if line and not line.startswith("#"):
            scope, rx = line.split("\t", 1)
            patterns.append((scope, re.compile(rx, re.I)))
    old = tomllib.loads(_read(gdir / "oldnames.toml")).get("rename", {})
    oldpat, oldkey = _oldnames(old)
    reviewed = {w for w in _words(_read(gdir / "glossary-reviewed.txt"))}
    if terms is None:
        import glossary
        terms = glossary_tokens(glossary.load())
    forbidden_terms = {t for t in terms if t.encode() in only and t not in allowed}
    unreviewed = {sha(t) for t in forbidden_terms} - reviewed
    return Rules(only, allowed, patterns, oldpat, oldkey, unreviewed, reviewed)


# --- scanning ----------------------------------------------------------------------------

def _is_text(data: bytes) -> bool:
    return b"\0" not in data[:8192]


def _lines(text: str, rx: re.Pattern):
    for i, line in enumerate(text.splitlines(), 1):
        for m in rx.finditer(line):
            yield i, m


def _text_rules(text: str, where: str, rules: Rules, fork: bool) -> list[Finding]:
    out = []
    for scope, rx in rules.patterns:
        if scope == "d1" or (scope == "fork" and fork):
            out += [Finding(f"pattern-{scope}", where, i, sha(m.group(0).lower()), m.group(0))
                    for i, m in _lines(text, rx)]
    if rules.oldnames:
        out += [Finding("oldname", where, i, sha(m.group(1)), m.group(1))
                for i, m in _lines(text, rules.oldnames)]
    return out


def scan_blob(where: str, data: bytes, rules: Rules, fork: bool = False) -> list[Finding]:
    out = []
    if rules.forbidden:
        for t in sorted(set(TOKEN.findall(data)) & rules.forbidden):
            if t.decode("latin-1") in rules.allowed or sha(t) in rules.reviewed:
                continue
            line = data[:data.find(t)].count(b"\n") + 1 if _is_text(data) else 0
            out.append(Finding("token", where, line, sha(t), t.decode("latin-1")))
    if _is_text(data):
        out += _text_rules(data.decode("utf-8", errors="replace"), where, rules, fork)
    return out


def scan_message(text: str, rules: Rules, fork: bool = False) -> list[Finding]:
    return _text_rules(text, "message", rules, fork)


def _git(repo, *args, check=True) -> bytes:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                          check=check).stdout


def scan_tree(repo: pathlib.Path, rules: Rules, fork: bool = False) -> list[Finding]:
    """Every tracked file, as it is in the working tree."""
    out = []
    for f in _git(repo, "ls-files", "-z").decode().split("\0"):
        p = pathlib.Path(repo) / f
        if f and p.is_file():
            out += scan_blob(f, p.read_bytes(), rules, fork)
    return out


def scan_staged(repo: pathlib.Path, rules: Rules, fork: bool = False) -> list[Finding]:
    """The index's version of every added or changed file."""
    names = _git(repo, "diff", "--cached", "--no-renames", "--name-only", "--diff-filter=ACMR",
                 "-z").decode().split("\0")
    out = []
    for f in filter(None, names):
        out += scan_blob(f, _git(repo, "show", f":{f}"), rules, fork)
    return out


def _blobs(repo, spec: list[str]):
    """(sha, path, size, data) of every blob reachable in spec, once each."""
    listing = _git(repo, "rev-list", "--objects", *spec).decode(errors="replace").splitlines()
    paths = {}
    for line in listing:
        sha_, _, path = line.partition(" ")
        if path:
            paths.setdefault(sha_, path)
    proc = subprocess.Popen(["git", "-C", str(repo), "cat-file", "--batch"],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    def feed():
        proc.stdin.write("".join(s + "\n" for s in paths).encode())
        proc.stdin.close()

    threading.Thread(target=feed, daemon=True).start()
    while True:
        head = proc.stdout.readline()
        if not head:
            break
        sha_, kind, size = head.split()
        data = proc.stdout.read(int(size))
        proc.stdout.read(1)
        if kind == b"blob":
            yield sha_.decode(), paths[sha_.decode()], int(size), data
    proc.wait()


def scan_history(repo: pathlib.Path, rules: Rules, base: str | None = None,
                 fork: bool = False) -> list[Finding]:
    """Every message and every blob of every commit reachable from any ref (and not from
    base)."""
    spec = ["--all"] + ([f"^{base}"] if base else [])
    out = []
    log = _git(repo, "log", *spec, "--format=%H%x00%B%x01").decode(errors="replace")
    for rec in log.split("\x01"):
        if rec.strip():
            commit, _, body = rec.strip("\n").partition("\x00")
            for f in scan_message(body, rules, fork):
                f.commit = commit
                out.append(f)
    for blob, path, size, data in _blobs(repo, spec):
        if size > MAX_FILE:
            continue
        found = scan_blob(path, data, rules, fork)
        if found:
            first = _git(repo, "log", *spec, "--format=%H", f"--find-object={blob}"
                         ).decode().split()
            for f in found:
                f.commit = first[-1] if first else blob
            out += found
    return out


# --- command line ------------------------------------------------------------------------

def accept_glossary(gdir: pathlib.Path, rules: Rules) -> int:
    path = pathlib.Path(gdir) / "glossary-reviewed.txt"
    have = _words(path.read_text())
    new = sorted(rules.unreviewed - have)
    with path.open("a") as fh:
        fh.write("".join(h + "\n" for h in new))
    return len(new)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--tree", nargs="?", const=str(ROOT), metavar="PATH")
    mode.add_argument("--staged", nargs="?", const=str(ROOT), metavar="PATH")
    mode.add_argument("--history", metavar="REPO")
    mode.add_argument("--message", metavar="FILE")
    mode.add_argument("--accept-glossary", action="store_true")
    ap.add_argument("--base", help="with --history: leave out what this revision reaches")
    ap.add_argument("--fork", action="store_true", help="apply the fork-scope patterns")
    ap.add_argument("--show", action="store_true", help="print the matched text")
    ap.add_argument("--no-glossary", action="store_true", help="ignore this repo's glossary")
    a = ap.parse_args(argv)
    gdir = guard_dir()
    try:
        rules = load_rules(gdir, terms=() if a.no_glossary else None)
    except GuardMissing as e:
        print(f"guard: private data ABSENT ({e})", file=sys.stderr)
        if required():
            print("guard: RESGX545_REQUIRE_GUARD=1, failing", file=sys.stderr)
            return 2
        print("guard: NOT CHECKED (set RESGX545_GUARD_DIR; RESGX545_REQUIRE_GUARD=1 fails)",
              file=sys.stderr)
        return 0
    if a.accept_glossary:
        print(f"guard: {accept_glossary(gdir, rules)} glossary tokens marked reviewed")
        return 0
    if a.staged is not None:
        found = scan_staged(pathlib.Path(a.staged), rules, a.fork)
    elif a.history:
        found = scan_history(pathlib.Path(a.history), rules, a.base, a.fork)
    elif a.message:
        found = scan_message(pathlib.Path(a.message).read_text(), rules, a.fork)
    else:
        found = scan_tree(pathlib.Path(a.tree or ROOT), rules, a.fork)
    for f in found:
        print(f.render(a.show))
    print(f"guard: {len(found)} findings")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
