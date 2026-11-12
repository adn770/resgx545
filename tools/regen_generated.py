#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The generated files of the tree, rebuilt from their sources or compared with the rebuild.

    python3 tools/regen_generated.py            rebuild them all (after a merge, see HACKING.md)
    python3 tools/regen_generated.py --check    name each that differs from its rebuild

They are doc/evidence_log.md (tools/records/evidence_log.py), doc/open_questions.md
(tools/records/questions.py), the digests of datasets/cited-scratch{,-private}.toml over the
cited/ directory of the data repositories (a manifest whose repository is absent is left alone),
and the books of doc/isa/build.py (doc/specs/usse_isa.md, usse_guide.md, usse_tutorial.md,
pds_isa.md). Edit the sources; a hand edit of a generated file is what --check reports.
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys
from typing import Callable

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE / "records"))
import datasets                  # noqa: E402

GENERATED = ["doc/evidence_log.md", "doc/open_questions.md",
             "datasets/cited-scratch.toml", "datasets/cited-scratch-private.toml",
             "doc/specs/usse_isa.md", "doc/specs/usse_guide.md", "doc/specs/usse_tutorial.md",
             "doc/specs/pds_isa.md"]
MANIFESTS = {"cited-scratch": "data", "cited-scratch-private": "data-private"}
Runner = Callable[[list[str], pathlib.Path], int]


def run(cmd: list[str], cwd: pathlib.Path) -> int:
    return subprocess.run(cmd, cwd=cwd, stdout=subprocess.DEVNULL).returncode


def _digest(root: pathlib.Path, name: str, repos: dict) -> tuple[pathlib.Path, dict] | None:
    repo = repos.get(MANIFESTS[name])
    path = root / "datasets" / f"{name}.toml"
    if repo is None or not path.is_file():
        return None
    files, size, sha = datasets.digest(["cited/"], repo)
    return path, {"files": str(files), "size": str(size), "sha256": f'"{sha}"'}


def _fields(path: pathlib.Path, keys) -> dict:
    text = path.read_text()
    return {k: m.group(1) for k in keys if (m := re.search(rf"(?m)^{k} = (.*)$", text))}


def manifest_problems(root: pathlib.Path, repos: dict) -> list[str]:
    out = []
    for name in MANIFESTS:
        got = _digest(root, name, repos)
        if got and _fields(got[0], got[1]) != got[1]:
            out.append(got[0].relative_to(root).as_posix())
    return out


def refresh_manifests(root: pathlib.Path, repos: dict) -> None:
    """Rewrite files, size and sha256 of each manifest whose repository is present; the title,
    the method and the date are the author's and stay."""
    for name in MANIFESTS:
        got = _digest(root, name, repos)
        if got:
            text = got[0].read_text()
            for key, val in got[1].items():
                text = re.sub(rf"(?m)^{key} = .*$", f"{key} = {val}", text, count=1)
            got[0].write_text(text)


def _py(root: pathlib.Path, rel: str, *args: str) -> list[str]:
    return [sys.executable, str(root / rel), *args]


def problems(root: pathlib.Path = ROOT, repos: dict | None = None,
             runner: Runner = run) -> list[str]:
    repos = datasets.repos(root) if repos is None else repos
    bad = []
    for label, rel in (("doc/evidence_log.md", "tools/records/evidence_log.py"),
                       ("doc/open_questions.md", "tools/records/questions.py"),
                       ("doc/isa books", "doc/isa/build.py")):
        if runner(_py(root, rel, "--check"), root):
            bad.append(label)
    return bad + manifest_problems(root, repos)


def regen(root: pathlib.Path = ROOT, repos: dict | None = None, runner: Runner = run) -> int:
    repos = datasets.repos(root) if repos is None else repos
    rc = 0
    for rel in ("tools/records/evidence_log.py", "tools/records/questions.py",
                "doc/isa/build.py"):
        rc |= runner(_py(root, rel), root)
    refresh_manifests(root, repos)
    return rc


def main(argv: list[str] | None = None) -> int:
    a = sys.argv[1:] if argv is None else argv
    if "--check" in a:
        bad = problems()
        for b in bad:
            print(f"{b}: differs from its regeneration (edit the sources, run "
                  f"tools/regen_generated.py)")
        return 1 if bad else 0
    return regen()


if __name__ == "__main__":
    sys.exit(main())
