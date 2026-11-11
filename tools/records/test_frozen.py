# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""frozen.py: the resgx545 files a published session's freeze pins by absolute path are pinned
by commit in FROZEN.commits, found in the history and checked against it."""
import hashlib
import os
import subprocess

import frozen

TREE = "/home/u/src/resgx545"


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def git(repo, *args, date=None):
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
               GIT_COMMITTER_EMAIL="t@t")
    if date:
        env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = f"{date}T12:00:00+00:00"
    return subprocess.run(["git", "-C", str(repo), *args], env=env, check=True,
                          capture_output=True, text=True).stdout.strip()


def commit(repo, files: dict[str, str], date: str) -> str:
    for rel, text in files.items():
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
        (repo / rel).write_text(text)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", f"c {date}", date=date)
    return git(repo, "rev-parse", "HEAD")


def history(tmp_path):
    """A resgx545 history: tools/a.py is "x" on 11-01, "y" on 11-02, "x" again on 11-03 and
    "z" on 11-05; tools/b.c is "b" from 11-01."""
    repo = tmp_path / "resgx545"
    repo.mkdir()
    git(repo, "init", "-q")
    c = {"01": commit(repo, {"tools/a.py": "x", "tools/b.c": "b"}, "2026-11-01"),
         "02": commit(repo, {"tools/a.py": "y"}, "2026-11-02"),
         "03": commit(repo, {"tools/a.py": "x"}, "2026-11-03"),
         "05": commit(repo, {"tools/a.py": "z"}, "2026-11-05")}
    return repo, c


def session(tmp_path, lines: list[str], name="FROZEN.sha256"):
    s = tmp_path / "data" / "render" / "closing-x"
    s.mkdir(parents=True, exist_ok=True)
    (s / name).write_text("".join(f"{x}\n" for x in lines))
    return s


def test_only_absolute_lines_under_the_resgx545_tree_are_pins(tmp_path):
    s = session(tmp_path, [f"{sha('x')}  {TREE}/tools/a.py",
                           f"{sha('q')}  score/score_x.py",
                           f"{sha('r')}  /home/u/src/resgx545-data/texture/p/t.py",
                           f"{sha('b')}  {TREE}/tools/b.c"])
    assert frozen.pins(s / "FROZEN.sha256") == [(sha("x"), "tools/a.py"), (sha("b"), "tools/b.c")]


def test_the_newest_commit_at_or_before_the_date_is_chosen(tmp_path):
    repo, c = history(tmp_path)
    find = frozen.Finder(repo)
    assert find.commit("tools/a.py", sha("x"), "2026-11-04") == c["03"]
    assert find.commit("tools/a.py", sha("x"), "2026-11-03") == c["03"]
    assert find.commit("tools/a.py", sha("x"), "2026-11-02") == c["01"]
    assert find.commit("tools/a.py", sha("y"), "2026-11-10") == c["02"]
    assert find.commit("tools/b.c", sha("b"), "2026-11-10") == c["01"]


def test_a_commit_after_the_date_is_taken_only_when_none_is_before(tmp_path):
    repo, c = history(tmp_path)
    assert frozen.Finder(repo).commit("tools/a.py", sha("z"), "2026-11-04") == c["05"]


def test_a_hash_the_path_never_had_is_not_guessed(tmp_path):
    repo, _ = history(tmp_path)
    find = frozen.Finder(repo)
    assert find.commit("tools/a.py", sha("never"), "2026-11-10") is None
    assert find.commit("tools/gone.py", sha("x"), "2026-11-10") is None


def test_write_pins_each_resgx545_file_by_commit(tmp_path):
    repo, c = history(tmp_path)
    s = session(tmp_path, [f"{sha('q')}  score/score_x.py", f"{sha('x')}  {TREE}/tools/a.py"])
    session(tmp_path, [f"{sha('y')}  {TREE}/tools/a.py", f"{sha('b')}  {TREE}/tools/b.c"],
            "FROZEN.pre-reword.sha256")
    before = {p.name: p.read_bytes() for p in s.iterdir()}
    text, bad = frozen.commits_for(s, frozen.Finder(repo), "2026-11-04")
    assert bad == []
    body = [x for x in text.splitlines() if not x.startswith("#")]
    want = [f"{sha('x')}  {c['03']}  tools/a.py", f"{sha('y')}  {c['02']}  tools/a.py",
            f"{sha('b')}  {c['01']}  tools/b.c"]
    assert body == sorted(want, key=lambda x: (x.split()[2], x.split()[0]))
    assert text.startswith("# ")
    frozen.write(tmp_path / "data", repo, {"render/closing-x": "2026-11-04"})
    assert (s / "FROZEN.commits").read_text() == text
    assert {p.name: p.read_bytes() for p in s.iterdir() if p.name != "FROZEN.commits"} == before


def test_write_reports_an_unresolved_pin_and_writes_nothing(tmp_path):
    repo, _ = history(tmp_path)
    s = session(tmp_path, [f"{sha('x')}  {TREE}/tools/a.py", f"{sha('w')}  {TREE}/tools/b.c"])
    bad = frozen.write(tmp_path / "data", repo, {"render/closing-x": "2026-11-04"})
    assert len(bad) == 1 and "tools/b.c" in bad[0] and sha("w") in bad[0]
    assert not (s / "FROZEN.commits").exists()


def test_write_never_replaces_a_commits_file(tmp_path):
    repo, _ = history(tmp_path)
    s = session(tmp_path, [f"{sha('x')}  {TREE}/tools/a.py"])
    (s / "FROZEN.commits").write_text("# kept\n")
    bad = frozen.write(tmp_path / "data", repo, {"render/closing-x": "2026-11-04"})
    assert (s / "FROZEN.commits").read_text() == "# kept\n"
    assert any("exists" in m for m in bad)


def test_a_session_without_a_date_is_reported(tmp_path):
    repo, _ = history(tmp_path)
    s = session(tmp_path, [f"{sha('x')}  {TREE}/tools/a.py"])
    bad = frozen.write(tmp_path / "data", repo, {})
    assert any("date" in m for m in bad) and not (s / "FROZEN.commits").exists()


def test_check_passes_on_matching_pins(tmp_path):
    repo, _ = history(tmp_path)
    session(tmp_path, [f"{sha('x')}  {TREE}/tools/a.py", f"{sha('q')}  score/score_x.py"])
    assert frozen.write(tmp_path / "data", repo, {"render/closing-x": "2026-11-04"}) == []
    assert frozen.check(tmp_path / "data", repo) == []


def test_check_finds_a_missing_pin(tmp_path):
    repo, c = history(tmp_path)
    s = session(tmp_path, [f"{sha('x')}  {TREE}/tools/a.py", f"{sha('b')}  {TREE}/tools/b.c"])
    (s / "FROZEN.commits").write_text(f"# h\n{sha('x')}  {c['03']}  tools/a.py\n")
    bad = frozen.check(tmp_path / "data", repo)
    assert len(bad) == 1 and "tools/b.c" in bad[0] and "render/closing-x" in bad[0]


def test_check_finds_a_wrong_hash(tmp_path):
    repo, c = history(tmp_path)
    s = session(tmp_path, [f"{sha('x')}  {TREE}/tools/a.py"])
    (s / "FROZEN.commits").write_text(f"# h\n{sha('x')}  {c['02']}  tools/a.py\n")
    bad = frozen.check(tmp_path / "data", repo)
    assert len(bad) == 1 and c["02"] in bad[0] and "tools/a.py" in bad[0]


def test_check_finds_an_unknown_commit_and_a_bad_line(tmp_path):
    repo, _ = history(tmp_path)
    s = session(tmp_path, [f"{sha('x')}  {TREE}/tools/a.py"])
    (s / "FROZEN.commits").write_text(f"{sha('x')}  {'0' * 40}  tools/a.py\nnot a line\n")
    bad = frozen.check(tmp_path / "data", repo)
    assert any("0" * 40 in m for m in bad) and any("not a line" in m for m in bad)


def test_check_finds_a_line_no_freeze_pins(tmp_path):
    repo, c = history(tmp_path)
    s = session(tmp_path, [f"{sha('x')}  {TREE}/tools/a.py"])
    (s / "FROZEN.commits").write_text(f"{sha('x')}  {c['03']}  tools/a.py\n"
                                      f"{sha('b')}  {c['01']}  tools/b.c\n")
    bad = frozen.check(tmp_path / "data", repo)
    assert len(bad) == 1 and "tools/b.c" in bad[0]


def test_check_ignores_lines_off_the_resgx545_tree(tmp_path):
    repo, _ = history(tmp_path)
    session(tmp_path, [f"{sha('x')}  {TREE}/tools/a.py", f"{sha('q')}  score/score_x.py",
                       f"{sha('r')}  /home/u/src/resgx545-data/texture/p/t.py"])
    assert frozen.write(tmp_path / "data", repo, {"render/closing-x": "2026-11-04"}) == []
    assert frozen.check(tmp_path / "data", repo) == []


def test_once_a_session_has_commits_every_pinning_session_needs_them(tmp_path):
    repo, _ = history(tmp_path)
    session(tmp_path, [f"{sha('x')}  {TREE}/tools/a.py"])
    other = tmp_path / "data" / "edm" / "closing-y"
    other.mkdir(parents=True)
    (other / "FROZEN.sha256").write_text(f"{sha('b')}  {TREE}/tools/b.c\n")
    plain = tmp_path / "data" / "edm" / "closing-z"
    plain.mkdir(parents=True)
    (plain / "FROZEN.sha256").write_text(f"{sha('q')}  score/score_z.py\n")
    assert frozen.check(tmp_path / "data", repo) == []      # no FROZEN.commits yet
    frozen.write(tmp_path / "data", repo, {"render/closing-x": "2026-11-04"})
    bad = frozen.check(tmp_path / "data", repo)
    assert len(bad) == 1 and "edm/closing-y" in bad[0] and "FROZEN.commits" in bad[0]


def test_session_dates_come_from_the_data_manifests():
    manifests = {"a": dict(repo="data", paths=["render/closing-x/"], date="2026-11-04"),
                 "b": dict(repo="data", paths=["edm/closing-y/FROZEN.sha256",
                                               "edm/closing-y/run/"], date="2026-11-09"),
                 "c": dict(repo="data-private", paths=["edm/closing-z/"], date="2026-11-01")}
    dates = frozen.session_dates(manifests, ["render/closing-x", "edm/closing-y",
                                             "edm/closing-z"])
    assert dates == {"render/closing-x": "2026-11-04", "edm/closing-y": "2026-11-09"}


def test_main_skips_without_a_data_repository(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(frozen.datasets, "repos", lambda: {})
    assert frozen.main(["--check"]) == 0
    assert capsys.readouterr().out == ""


def test_the_published_sessions_verify():
    """The data checked out beside this one, when there is one, passes the check."""
    data = frozen.datasets.repos().get("data")
    if data is None or not frozen.has_history(frozen.ROOT):
        return
    assert frozen.check(data, frozen.ROOT) == []


def test_a_pin_of_a_file_never_tracked_is_written_as_untracked(tmp_path):
    """A build product (an ignored file such as tools/usse-asm/usse-asm) has no commit: its line
    says so, and the check refuses it once the path is tracked."""
    repo, c = history(tmp_path)
    s = session(tmp_path, [f"{sha('x')}  {TREE}/tools/a.py", f"{sha('e')}  {TREE}/tools/bin/e"])
    assert frozen.write(tmp_path / "data", repo, {"render/closing-x": "2026-11-04"}) == []
    body = [x for x in (s / "FROZEN.commits").read_text().splitlines() if not x.startswith("#")]
    assert body == [f"{sha('x')}  {c['03']}  tools/a.py", f"{sha('e')}  untracked  tools/bin/e"]
    assert frozen.check(tmp_path / "data", repo) == []
    commit(repo, {"tools/bin/e": "e"}, "2026-11-06")
    bad = frozen.check(tmp_path / "data", repo)
    assert len(bad) == 1 and "tools/bin/e" in bad[0] and "is tracked" in bad[0]


def test_a_tracked_path_without_the_hash_is_not_written_as_untracked(tmp_path):
    repo, _ = history(tmp_path)
    s = session(tmp_path, [f"{sha('w')}  {TREE}/tools/a.py"])
    (s / "FROZEN.commits").write_text(f"{sha('w')}  untracked  tools/a.py\n")
    bad = frozen.check(tmp_path / "data", repo)
    assert len(bad) == 1 and "tools/a.py" in bad[0] and "is tracked" in bad[0]
