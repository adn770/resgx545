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


def test_a_record_names_a_known_repo_and_its_keys_in_order(tmp_path):
    assert any("repo" in m for m in datasets.problems("x", record(repo="elsewhere"), {}))
    assert any("repo" in m for m in datasets.problems("x", record(repo=["data"]), {}))
    d = record()
    d.pop("recipe")
    assert any("keys" in m for m in datasets.problems("x", d, {}))


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
    """A dataset is recorded because a finding rests on it."""
    used = {d.split(":")[0] for p in evidence.DIR.glob("*/*.md")
            for d in evidence.parse(p)[0]["data"]}
    assert set(datasets.load()) <= used
