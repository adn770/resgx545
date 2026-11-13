# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""datasets.py: the dataset manifests, the repositories that hold their bytes, and the
evidence's references to them."""
import hashlib
import re
import subprocess

import pytest

import datasets
import evidence

EMPTY = hashlib.sha256(b"").hexdigest()


def record(**kw):
    d = dict(title="t", repo="data", paths=["usse/x/"], method="m", date="2026-11-01",
             files=1, size=0, sha256=EMPTY, recipe="probes/usse/x.toml")
    d.update(kw)
    return d


def test_a_record_matches_its_files(tmp_path):
    (tmp_path / "usse" / "x").mkdir(parents=True)
    (tmp_path / "usse" / "x" / "a.txt").write_text("x")
    n, size, sha = datasets.digest(["usse/x/"], tmp_path)
    assert (n, size) == (1, 1)
    repos = {"data": tmp_path}
    assert datasets.problems("x", record(files=n, size=size, sha256=sha), repos) == []
    (tmp_path / "usse" / "x" / "a.txt").write_text("y")
    msgs = datasets.problems("x", record(files=n, size=size, sha256=sha), repos)
    assert "contents changed" in msgs[0]


def test_the_digest_lists_files_in_path_order(tmp_path):
    """The hash is over the "sha256  path" lines in path order, component by component:
    a/b/y sorts before a-b/x (as a string, "-" would sort before "/")."""
    for rel, text in (("a-b/x", "x"), ("a/b/y", "y"), ("a/c", "c")):
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text(text)
    listing = "".join(f"{hashlib.sha256(t.encode()).hexdigest()}  {p}\n"
                      for p, t in (("a/b/y", "y"), ("a/c", "c"), ("a-b/x", "x")))
    sha = "3ce9d9a236e00c7cae86eca25e16a26b5935e0899fc9f303ab906ebcea6321d7"
    assert hashlib.sha256(listing.encode()).hexdigest() == sha
    assert datasets.digest(["a/", "a-b/"], tmp_path) == (3, 3, sha)
    assert datasets.digest(["a-b/", "a/"], tmp_path) == (3, 3, sha)


def test_the_digest_skips_python_caches(tmp_path):
    """A published script run in place leaves __pycache__/ in the data repository; it is
    gitignored and never data, so it changes no dataset's count, size or hash."""
    (tmp_path / "s" / "tool").mkdir(parents=True)
    (tmp_path / "s" / "tool" / "gen.py").write_text("g")
    before = datasets.digest(["s/"], tmp_path)
    (tmp_path / "s" / "tool" / "__pycache__").mkdir()
    (tmp_path / "s" / "tool" / "__pycache__" / "gen.cpython-313.pyc").write_bytes(b"c")
    assert datasets.files_of(["s/"], tmp_path) == [tmp_path / "s" / "tool" / "gen.py"]
    assert datasets.digest(["s/"], tmp_path) == before


def test_the_digest_skips_pytest_caches_outside_git(tmp_path):
    (tmp_path / "s" / ".pytest_cache").mkdir(parents=True)
    (tmp_path / "s" / "a.txt").write_text("a")
    before = datasets.digest(["s/"], tmp_path)
    (tmp_path / "s" / ".pytest_cache" / "README.md").write_text("c")
    assert datasets.digest(["s/"], tmp_path) == before


def test_in_a_git_checkout_the_digest_covers_the_tracked_files_only(tmp_path):
    """The folds' data worktrees held an untracked .pytest_cache/ that the walk counted: a git
    checkout is digested from `git ls-files`, what the repository publishes."""
    def git(*a):
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=tmp_path,
                       check=True, capture_output=True)
    git("init", "-q")
    (tmp_path / "s").mkdir()
    (tmp_path / "s" / "a.txt").write_text("a")
    (tmp_path / "s" / "gone.txt").write_text("g")
    git("add", ".")
    git("commit", "-qm", "c")
    before = datasets.digest(["s/"], tmp_path)
    assert before[0] == 2
    (tmp_path / "s" / "scratch.log").write_text("untracked")
    (tmp_path / "s" / "cache").mkdir()
    (tmp_path / "s" / "cache" / "x").write_text("untracked")
    assert datasets.digest(["s/"], tmp_path) == before
    (tmp_path / "s" / "gone.txt").unlink()           # tracked but deleted: not a file
    assert datasets.digest(["s/"], tmp_path)[0] == 1
    assert datasets.files_of(["s/a.txt"], tmp_path) == [tmp_path / "s" / "a.txt"]


def test_a_record_names_a_known_repo_and_its_keys_in_order(tmp_path):
    assert any("repo" in m for m in datasets.problems("x", record(repo="elsewhere"), {}))
    assert any("repo" in m for m in datasets.problems("x", record(repo=["data"]), {}))
    d = record()
    d.pop("recipe")
    assert any("keys" in m for m in datasets.problems("x", d, {}))


def test_a_record_may_end_with_the_tables_needs_and_open_probes():
    # the campaign appends the table's needs and its open probes (campaign.run_table)
    assert datasets.problems("x", record(needs=["render", "kpoke"]), {}) == []
    assert datasets.problems("x", record(needs=["render"], open=["usse-x-a"]), {}) == []
    assert datasets.problems("x", record(open=["usse-x-a"]), {}) == []
    assert any("keys" in m for m in datasets.problems("x", record(other=1), {}))
    d = record(needs=["render"])
    assert any("needs" in m for m in datasets.problems("x", {**d, "needs": "render"}, {}))


def test_needs_and_open_agree_with_the_recipe_when_it_is_there(tmp_path):
    (tmp_path / "probes" / "usse").mkdir(parents=True)
    recipe = tmp_path / "probes" / "usse" / "x.toml"
    recipe.write_text('needs = ["render"]\nopen = ["usse-x-a"]\n')
    ok = record(needs=["render"], open=["usse-x-a"])
    assert datasets.problems("x", ok, {}, tmp_path) == []
    bad = datasets.problems("x", record(needs=["kpoke"], open=["usse-x-a"]), {}, tmp_path)
    assert len(bad) == 1 and "needs" in bad[0] and "recipe" in bad[0]
    assert any("open" in m for m in datasets.problems("x", record(needs=["render"]), {},
                                                         tmp_path))
    recipe.write_text("")
    assert any("needs" in m for m in datasets.problems("x", ok, {}, tmp_path))
    assert datasets.problems("x", record(), {}, tmp_path) == []
    assert datasets.problems("x", ok, {}, tmp_path / "elsewhere") == []     # no recipe, no check


@pytest.mark.parametrize("paths", [["/usse/x/"], ["usse/../x"], [".."], ["../x"], [""], ["."],
                                   ["./"], [], "usse/x/", [3]])
def test_paths_stay_inside_their_repository(paths):
    msgs = datasets.problems("x", record(paths=paths), {})
    assert any("path" in m for m in msgs), msgs


def test_a_path_may_not_escape_through_a_symlink(tmp_path):
    repo, outside = tmp_path / "repo", tmp_path / "outside"
    (outside / "d").mkdir(parents=True)
    (outside / "d" / "f").write_text("f")
    repo.mkdir()
    (repo / "link").symlink_to(outside / "d")
    (repo / "in").mkdir()
    (repo / "in" / "f").symlink_to(outside / "d" / "f")
    for p in ("link/", "in/"):
        msgs = datasets.problems("x", record(paths=[p]), {"data": repo})
        assert any("outside the repository" in m for m in msgs), (p, msgs)


@pytest.mark.parametrize("key, value", [
    ("date", "2026-99-99"), ("date", "20261101"), ("files", "1"), ("files", True),
    ("files", 0), ("size", -1), ("size", 1.0), ("sha256", ""), ("sha256", "..."),
    ("sha256", "A" * 64), ("title", ""), ("method", 3), ("recipe", "")])
def test_the_form_of_each_field_is_checked(key, value):
    msgs = datasets.problems("x", record(**{key: value}), {})
    assert any(key in m for m in msgs), msgs


def test_a_toml_date_is_reported_not_a_crash():
    import datetime
    msgs = datasets.problems("x", record(date=datetime.date(2026, 11, 1)), {})
    assert any("date is not a string" in m for m in msgs), msgs


def test_a_repo_not_checked_out_is_skipped(tmp_path):
    # the private repo is often absent: its records are checked only where it is present
    assert datasets.problems("x", record(repo="data-private", files=3), {}) == []


def test_repos_are_found_beside_the_checkout_or_from_the_environment(tmp_path, monkeypatch):
    (tmp_path / "resgx545-data").mkdir()
    monkeypatch.delenv("RESGX545_DATA", raising=False)
    monkeypatch.delenv("RESGX545_DATA_PRIVATE", raising=False)
    assert datasets.repos(tmp_path / "resgx545") == {"data": tmp_path / "resgx545-data"}
    monkeypatch.setenv("RESGX545_DATA_PRIVATE", str(tmp_path / "elsewhere"))
    (tmp_path / "elsewhere").mkdir()
    assert datasets.repos(tmp_path / "resgx545")["data-private"] == tmp_path / "elsewhere"


def test_a_variable_naming_no_directory_is_warned_about(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("RESGX545_DATA", str(tmp_path / "missing"))
    monkeypatch.delenv("RESGX545_DATA_PRIVATE", raising=False)
    assert "data" not in datasets.repos(tmp_path / "resgx545")
    err = capsys.readouterr().err
    assert "RESGX545_DATA" in err and str(tmp_path / "missing") in err


def test_main_is_silent_when_all_is_well(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(datasets, "DIR", tmp_path)
    monkeypatch.setattr(datasets, "repos", lambda: {})
    assert datasets.main() == 0
    assert capsys.readouterr().out == ""
    (tmp_path / "x.toml").write_text('title = "t"\n')
    assert datasets.main() == 1
    assert "x: keys" in capsys.readouterr().out


def test_the_records_are_well_formed():
    for i, d in datasets.load().items():
        assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", i), i
        assert datasets.problems(i, d, {}) == [], i


def test_the_records_match_the_data_where_it_is_checked_out():
    repos = datasets.repos()
    if not repos:
        pytest.skip("no data repository checked out")
    bad = [m for i, d in datasets.load().items() for m in datasets.problems(i, d, repos)]
    assert not bad, bad


def test_evidence_names_datasets_or_tracked_files():
    recs = datasets.load()
    tracked = set(subprocess.run(["git", "ls-files"], cwd=evidence.ROOT, capture_output=True,
                                 text=True, check=True).stdout.split("\n"))
    for p in evidence.DIR.glob("*/*.md"):
        for d in evidence.parse(p)[0]["data"]:
            ident = d.split(":")[0]
            assert ident in recs or d in tracked, (p.name, d)


def test_every_record_is_cited():
    """A dataset is recorded because a finding rests on it. The copies of cited scratch files
    (recipe scratch_cites.py) are named by the cites in the records' text, which
    scratch_cites.py --check resolves, not by a record's data list."""
    used = {d.split(":")[0] for p in evidence.DIR.glob("*/*.md")
            for d in evidence.parse(p)[0]["data"]}
    cited = {i for i, d in datasets.load().items()
             if d["recipe"] == "tools/records/scratch_cites.py"}
    assert cited == {"cited-scratch", "cited-scratch-private"}
    assert set(datasets.load()) - cited <= used


def test_the_git_listing_ignores_the_callers_git_environment(tmp_path, monkeypatch):
    """Run from a commit hook of another repository, GIT_INDEX_FILE and GIT_DIR name that
    repository's index: the listing of this one must not read them."""
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / "s").mkdir()
    (tmp_path / "s" / "a.txt").write_text("a")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    (tmp_path / "s" / "untracked.txt").write_text("u")
    monkeypatch.setenv("GIT_INDEX_FILE", str(tmp_path / "other-index"))
    monkeypatch.setenv("GIT_DIR", str(tmp_path / "nowhere"))
    assert datasets.files_of(["s/"], tmp_path) == [tmp_path / "s" / "a.txt"]


def test_the_git_listing_does_not_go_through_a_patched_subprocess_run(tmp_path, monkeypatch):
    """campaign's tests replace subprocess.run (the one module object every tool shares) to
    record their ssh calls; the digest's own git calls must not land there."""
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / "s").mkdir()
    (tmp_path / "s" / "a.txt").write_text("a")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    (tmp_path / "s" / "untracked.txt").write_text("u")
    seen = []
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: seen.append(a))
    assert datasets.files_of(["s/"], tmp_path) == [tmp_path / "s" / "a.txt"]
    assert seen == []
