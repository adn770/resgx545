# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""regen_generated.py and the merge driver: the generated files (the evidence log, the open
questions, the cited-scratch manifests, the USSE books) are rebuilt from their sources after a
merge, and a generated file that differs from its regeneration is reported."""
from __future__ import annotations

import os
import pathlib
import subprocess
import sys

import pytest

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import regen_generated as rg      # noqa: E402


def manifest(tmp_path, files=0, size=0, sha="x"):
    root, data = tmp_path / "root", tmp_path / "data"
    (root / "datasets").mkdir(parents=True)
    (data / "cited").mkdir(parents=True)
    (data / "cited" / "a.out").write_text("hello\n")
    (root / "datasets" / "cited-scratch.toml").write_text(
        f'title = "t"\nrepo = "data"\npaths = ["cited/"]\nmethod = "m"\ndate = "2026-11-12"\n'
        f'files = {files}\nsize = {size}\nsha256 = "{sha}"\nrecipe = "r"\n')
    return root, {"data": data}


def test_a_stale_manifest_is_reported_and_refreshed_keeping_the_date(tmp_path):
    root, repos = manifest(tmp_path)
    assert [p for p in rg.manifest_problems(root, repos)] == ["datasets/cited-scratch.toml"]
    rg.refresh_manifests(root, repos)
    assert rg.manifest_problems(root, repos) == []
    text = (root / "datasets" / "cited-scratch.toml").read_text()
    assert "files = 1\nsize = 6\n" in text and 'date = "2026-11-12"' in text


def test_a_manifest_of_an_absent_repository_is_left_alone(tmp_path):
    root, _ = manifest(tmp_path)
    before = (root / "datasets" / "cited-scratch.toml").read_text()
    assert rg.manifest_problems(root, {}) == []
    rg.refresh_manifests(root, {})
    assert (root / "datasets" / "cited-scratch.toml").read_text() == before


def test_each_generated_file_that_differs_from_its_regeneration_is_named(tmp_path):
    root, repos = manifest(tmp_path)
    rg.refresh_manifests(root, repos)
    seen = []

    def run(cmd, cwd):
        seen.append(cmd[1:])
        return 1 if cmd[1].endswith(("evidence_log.py", "build.py")) else 0
    bad = rg.problems(root, repos, run)
    assert bad == ["doc/evidence_log.md", "doc/isa books"]
    assert all("--check" in c for c in seen)


def test_regeneration_runs_every_generator(tmp_path):
    root, repos = manifest(tmp_path)
    seen = []
    rg.regen(root, repos, lambda cmd, cwd: seen.append(" ".join(cmd[1:])) or 0)
    joined = "\n".join(seen)
    for tool in ("evidence_log.py", "questions.py", "build.py"):
        assert tool in joined
    assert "--check" not in joined


def test_the_real_tree_is_generated_from_its_sources():
    """No generated file of the tree was edited by hand (the data repositories, when present,
    are not needed here: a manifest of an absent repository is skipped)."""
    assert rg.problems(ROOT, rg.datasets.repos(ROOT)) == []


def test_gitattributes_gives_every_generated_file_the_regen_driver():
    attrs = {}
    for line in (ROOT / ".gitattributes").read_text().splitlines():
        if line.strip() and not line.startswith("#"):
            path, *rest = line.split()
            attrs[path] = rest
    for path in rg.GENERATED:
        assert "merge=regen" in attrs.get(path, []), path


def git(cwd, *args):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=cwd,
                          check=True, capture_output=True, text=True,
                          env={**os.environ, "GIT_CONFIG_GLOBAL": "/dev/null"}).stdout


def test_the_merge_driver_keeps_our_side_and_leaves_no_conflict(tmp_path):
    repo = tmp_path / "r"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    (repo / ".gitattributes").write_text("gen.md merge=regen\n")
    git(repo, "config", "merge.regen.driver", f"{HERE}/merge-regen.sh %O %A %B %L %P")
    (repo / "gen.md").write_text("a\nb\nc\n")
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "base")
    git(repo, "checkout", "-qb", "side")
    (repo / "gen.md").write_text("a\nside\nc\n")
    git(repo, "commit", "-qam", "side")
    git(repo, "checkout", "-q", "main")
    (repo / "gen.md").write_text("a\nmain\nc\n")
    git(repo, "commit", "-qam", "main")
    git(repo, "merge", "-q", "--no-commit", "side")
    assert git(repo, "diff", "--name-only", "--diff-filter=U") == ""
    assert (repo / "gen.md").read_text() == "a\nmain\nc\n"


def test_check_sh_runs_the_generated_guard_in_quick_mode():
    text = (HERE / "check.sh").read_text()
    quick = text.split('if [ "$mode" = quick ]')[1].split("\nelse\n")[0]
    assert "regen_generated.py" in quick and "--check" in quick
