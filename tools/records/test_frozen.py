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


def test_a_pin_of_a_worktree_under_scratch_is_named_by_its_commits_line(tmp_path):
    """Round 4 froze against an integration worktree under scratch/resgx545/ (closing4/lead/wt):
    the first resgx545 component of such a path is the scratch tree, not the tool tree. A line
    of FROZEN.commits whose hash is the pin's and whose path ends the pin's path names it."""
    repo, c = history(tmp_path)
    wt = "/home/u/src/scratch/resgx545/closing4/lead/wt"
    s = session(tmp_path, [f"{sha('x')}  {wt}/tools/a.py", f"{sha('q')}  score/score_x.py"])
    (s / "FROZEN.commits").write_text(f"# h\n{sha('x')}  {c['03']}  tools/a.py\n")
    assert frozen.session_pins(s) == [(sha("x"), "tools/a.py")]
    assert frozen.check(tmp_path / "data", repo) == []
    (s / "FROZEN.commits").write_text(f"# h\n{sha('y')}  {c['02']}  tools/a.py\n")
    bad = frozen.check(tmp_path / "data", repo)
    assert any("has no line" in b and "closing4/lead/wt/tools/a.py" in b for b in bad)


def test_inputs_read_from_scratch_are_checked_against_their_published_copies(tmp_path):
    """Round 5's r5-events froze the plan, the decisions and a reading of the firmware by
    absolute paths under scratch/resgx545/ that no FROZEN.commits line names: they are no files
    of the tool tree but inputs published as cited/<path> of resgx545-data or, derived from the
    firmware, of resgx545-data-private. Each must have a copy with the frozen hash; without the
    private repository a copy found in neither is not reported."""
    repo, c = history(tmp_path)
    sc = "/home/u/src/scratch/resgx545"
    r5 = "closing" + "5"   # not a scratch cite of this file (scratch_cites.py)
    s = session(tmp_path, [f"{sha('x')}  {TREE}/tools/a.py",
                           f"{sha('P')}  {sc}/{r5}/events/plan.md",
                           f"{sha('R')}  {sc}/{r5}/r6/reading.md"])
    (s / "FROZEN.commits").write_text(f"# h\n{sha('x')}  {c['03']}  tools/a.py\n")
    data, priv = tmp_path / "data", tmp_path / "priv"
    assert frozen.session_pins(s) == [(sha("x"), "tools/a.py")]
    assert frozen.scratch_inputs(s) == [(sha("P"), f"{r5}/events/plan.md"),
                                        (sha("R"), f"{r5}/r6/reading.md")]
    (data / f"cited/{r5}/events").mkdir(parents=True)
    (data / f"cited/{r5}/events/plan.md").write_text("P")
    assert frozen.check(data, repo) == []
    priv.mkdir()
    bad = frozen.check(data, repo, priv)
    assert len(bad) == 1 and f"{r5}/r6/reading.md" in bad[0] and "not published" in bad[0]
    (priv / f"cited/{r5}/r6").mkdir(parents=True)
    (priv / f"cited/{r5}/r6/reading.md").write_text("R")
    assert frozen.check(data, repo, priv) == []
    (data / f"cited/{r5}/events/plan.md").write_text("changed")
    bad = frozen.check(data, repo, priv)
    assert len(bad) == 1 and "plan.md" in bad[0] and sha("changed") in bad[0]


def test_a_line_may_name_its_repository(tmp_path):
    """Round 5's R5-dpm wrote `<sha256>  <commit>  <repo>:<path>` for every outside file its
    freeze pins or its checks read: resgx545:PATH is a file of this tree, verified at its commit
    as a bare path is, and may be one the freeze does not pin (a file its checks read); a line of
    another repository (linux:, data:) is the session's own check and not this tree's."""
    repo, c = history(tmp_path)
    s = session(tmp_path, [f"{sha('x')}  {TREE}/tools/a.py", f"{sha('q')}  score/score_x.py"])
    (s / "FROZEN.commits").write_text(
        f"# h\n{sha('x')}  {c['03']}  resgx545:tools/a.py\n"
        f"{sha('b')}  {c['01']}  resgx545:tools/b.c\n"
        f"{sha('k')}  {'a' * 40}  linux:drivers/k.c\n"
        f"{sha('d')}  {'b' * 40}  data:render/closing-y/bins/p.bin\n"
        f"{sha('e')}  untracked  resgx545:tools/bin/e\n")
    assert frozen.check(tmp_path / "data", repo) == []
    (s / "FROZEN.commits").write_text(f"# h\n{sha('x')}  {c['02']}  resgx545:tools/a.py\n"
                                      f"{sha('w')}  {c['01']}  resgx545:tools/b.c\n")
    bad = frozen.check(tmp_path / "data", repo)
    assert len(bad) == 2 and c["02"] in bad[0] and "tools/b.c" in bad[1]
    (s / "FROZEN.commits").write_text(f"# h\n{sha('b')}  {c['01']}  resgx545:tools/b.c\n")
    bad = frozen.check(tmp_path / "data", repo)
    assert len(bad) == 1 and "tools/a.py" in bad[0] and "has no line" in bad[0]


def test_a_data_line_is_checked_at_its_commit_when_the_data_history_is_there(tmp_path):
    """A `data:PATH` line pins a file of the data repository by commit, as the session kit's
    freeze writes it (tools/closing/kit): once the data checkout has a history, the line is
    verified against the blob at its commit, never against the working tree, so the data
    repository may move after the freeze."""
    repo, c = history(tmp_path)
    s = session(tmp_path, [f"{sha('q')}  score/score_x.py"])
    data = tmp_path / "data"
    git(data, "init", "-q")
    d1 = commit(data, {"render/closing-y/p.bin": "p1"}, "2026-11-01")
    commit(data, {"render/closing-y/p.bin": "p2"}, "2026-11-02")
    (s / "FROZEN.commits").write_text(f"# h\n{sha('p1')}  {d1}  data:render/closing-y/p.bin\n")
    assert frozen.check(data, repo) == []
    (s / "FROZEN.commits").write_text(f"# h\n{sha('p2')}  {d1}  data:render/closing-y/p.bin\n"
                                      f"{sha('p1')}  {'b' * 40}  data:render/closing-y/p.bin\n"
                                      f"{sha('k')}  {'a' * 40}  linux:drivers/k.c\n")
    bad = frozen.check(data, repo)
    assert len(bad) == 2 and "data:render/closing-y/p.bin" in bad[0] and "b" * 40 in bad[1]


def built_session(tmp_path, recipe="data:render/closing-r/lead/build.sh"):
    """A session that froze a binary it ran (bin/t/tool, by relative path, not published) and
    binds it to its source: tools/b.c at the 11-01 commit, built by a recipe published in the
    data repository."""
    repo, c = history(tmp_path)
    s = session(tmp_path, [f"{sha('x')}  {TREE}/tools/a.py", f"{sha('BIN')}  bin/t/tool"])
    r = tmp_path / "data" / "render" / "closing-r" / "lead"
    r.mkdir(parents=True)
    (r / "build.sh").write_text("make\n")
    (s / "FROZEN.commits").write_text(
        f"# h\n{sha('x')}  {c['03']}  tools/a.py\n"
        f"{sha('BIN')}  built  {c['01']}  tools/b.c  {sha('b')}  {recipe}\n")
    return repo, c, s


def test_a_built_binary_is_checked_by_its_source_not_its_bytes(tmp_path):
    """`<binary-sha256>  built  <commit>  <source-path>  <source-sha256>  <recipe>` binds a
    binary the freeze names to the source it was built from: the source blob at the commit has
    the source hash and the recipe is at its pinned place (data:PATH in the data repository, a
    bare or resgx545:PATH in this tree at the commit). The binary itself is never needed."""
    repo, c, s = built_session(tmp_path)
    assert not (s / "bin").exists()
    assert frozen.check(tmp_path / "data", repo) == []
    text = (s / "FROZEN.commits").read_text()
    (s / "FROZEN.commits").write_text(text.replace("closing-r/lead/build.sh", "tools/b.c")
                                      .replace("data:render/", ""))
    assert frozen.check(tmp_path / "data", repo) == []     # a recipe of this tree at the commit


def test_a_built_line_with_the_wrong_source_hash_is_reported(tmp_path):
    repo, c, s = built_session(tmp_path)
    text = (s / "FROZEN.commits").read_text()
    (s / "FROZEN.commits").write_text(text.replace(f"tools/b.c  {sha('b')}",
                                                   f"tools/b.c  {sha('w')}"))
    bad = frozen.check(tmp_path / "data", repo)
    assert len(bad) == 1 and "tools/b.c" in bad[0] and sha("w") in bad[0]


def test_a_built_line_whose_recipe_is_missing_is_reported(tmp_path):
    repo, _, _ = built_session(tmp_path, recipe="data:render/closing-r/lead/gone.sh")
    bad = frozen.check(tmp_path / "data", repo)
    assert len(bad) == 1 and "gone.sh" in bad[0] and "recipe" in bad[0]
    (tmp_path / "t2").mkdir()
    repo2, _, _ = built_session(tmp_path / "t2", recipe="tools/gone.sh")
    bad = frozen.check(tmp_path / "t2" / "data", repo2)
    assert len(bad) == 1 and "tools/gone.sh" in bad[0] and "recipe" in bad[0]


def test_a_built_line_for_a_binary_no_freeze_names_is_reported(tmp_path):
    repo, c, s = built_session(tmp_path)
    text = (s / "FROZEN.commits").read_text()
    (s / "FROZEN.commits").write_text(text.replace(sha("BIN"), sha("OTHER")))
    bad = frozen.check(tmp_path / "data", repo)
    assert len(bad) == 1 and sha("OTHER") in bad[0] and "no freeze" in bad[0]


def test_a_malformed_built_line_is_reported(tmp_path):
    repo, c, s = built_session(tmp_path)
    (s / "FROZEN.commits").write_text(f"# h\n{sha('x')}  {c['03']}  tools/a.py\n"
                                      f"{sha('BIN')}  built  {c['01']}  tools/b.c\n")
    bad = frozen.check(tmp_path / "data", repo)
    assert len(bad) == 1 and "built" in bad[0]


def test_a_scratch_input_of_a_published_session_is_checked_in_that_session(tmp_path):
    """R7-rp froze inputs of round 6's sessions by their scratch paths (closingN/r6-misc/...):
    those sessions are published as <area>/closing-<name>/ of a data repository, so the input
    resolves there as scratch_cites.py resolves a cite (its aliases included), before cited/."""
    repo, c = history(tmp_path)
    sc = "/home/u/src/scratch/resgx545"
    r6 = "closing" + "6"   # not a scratch cite of this file (scratch_cites.py)
    s = session(tmp_path, [f"{sha('x')}  {TREE}/tools/a.py",
                           f"{sha('M')}  {sc}/{r6}/r6-misc/gen/models.py",
                           f"{sha('V')}  {sc}/{r6}/s1b-v2/README.md"])
    (s / "FROZEN.commits").write_text(f"# h\n{sha('x')}  {c['03']}  tools/a.py\n")
    data, priv = tmp_path / "data", tmp_path / "priv"
    priv.mkdir()
    bad = frozen.check(data, repo, priv)
    assert len(bad) == 2 and all("not published" in b for b in bad)
    (data / "render/closing-r6-misc/gen").mkdir(parents=True)
    (data / "render/closing-r6-misc/gen/models.py").write_text("M")
    (priv / "edm/closing-s1b").mkdir(parents=True)
    (priv / "edm/closing-s1b/README.md").write_text("V")
    assert frozen.check(data, repo, priv) == []
    (data / "render/closing-r6-misc/gen/models.py").write_text("changed")
    bad = frozen.check(data, repo, priv)
    assert len(bad) == 1 and "render/closing-r6-misc/gen/models.py" in bad[0] \
        and sha("changed") in bad[0]
