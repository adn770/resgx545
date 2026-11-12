# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""regen_generated.py and the merge driver: the generated files (the evidence log, the open
questions, the cited-scratch manifests, the USSE books, the state digest) are rebuilt from their
sources after a merge, and a generated file that differs from its regeneration is reported."""
from __future__ import annotations

import importlib.util
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
    for tool in ("evidence_log.py", "questions.py", "build.py", "digest.py"):
        assert tool in joined
    assert "--check" not in joined
    assert seen[-1].endswith("digest.py")      # the digest reads the other generated files


def test_the_state_digest_is_a_generated_file(tmp_path):
    root, repos = manifest(tmp_path)
    rg.refresh_manifests(root, repos)
    bad = rg.problems(root, repos, lambda cmd, cwd: 1 if cmd[1].endswith("digest.py") else 0)
    assert bad == ["doc/state_digest.md"]
    assert "doc/state_digest.md" in rg.GENERATED


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


def test_check_sh_checks_the_state_digest_in_both_modes():
    text = (HERE / "check.sh").read_text()
    quick, full = text.split('if [ "$mode" = quick ]')[1].split("\nelse\n")[:2]
    for part in (quick, full):
        loop = part.split("for t in ")[1].split("; do")[0]
        assert "digest" in loop.split()


def test_check_sh_runs_pytest_in_parallel_and_the_venv_has_xdist():
    assert "-n \"${CHECK_JOBS:-auto}\"" in (HERE / "check.sh").read_text()
    assert "pytest-xdist" in (ROOT / "requirements-dev.txt").read_text()


def root_conftest():
    """The conftest.py of the tree root (several others are called conftest)."""
    spec = importlib.util.spec_from_file_location("root_conftest", ROOT / "conftest.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_parallel_runs_build_the_shared_tools_once_before_the_workers_start():
    """Tests of several files make the same tool directories and cargo targets; with xdist the
    controller builds them first, so no two workers write the same binary."""
    top = root_conftest()
    dirs = {c[c.index("-C") + 1] for c in top.PREBUILD if c[0] == "make"}
    assert {"tools/usse-dis", "tools/usse-asm"} <= dirs
    assert all((ROOT / d).is_dir() for d in dirs)
    assert any(c[0] == "cargo" for c in top.PREBUILD)
    assert top.wants_prebuild(4, None) and not top.wants_prebuild(0, None)
    assert not top.wants_prebuild(4, {"workerid": "gw0"})


def test_the_controller_can_import_the_modules_that_define_warning_classes():
    top = root_conftest()
    assert all((ROOT / p / "fwtask.py").is_file() for p in top.WARNING_PATHS[:1])
