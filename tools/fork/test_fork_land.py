# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""recheck.sh and fork-land.sh on toy repositories: the series is sent to the "build host"
(here the same machine, through `sh -c` in place of ssh), checked by a fake check script that
prints PASS and FAIL lines, and the branch moves only for the tip that passed. Nothing here
touches a real fork or a real host."""
import os
import pathlib
import subprocess

import pytest

HERE = pathlib.Path(__file__).resolve().parent
RECHECK = HERE / "recheck.sh"
LAND = HERE / "fork-land.sh"
SECRET = "zorptokalpha"


def git(repo, *args, check=True):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
                          check=check).stdout.strip()


def commit(repo, subject, files=None):
    files = files or {f"{subject.split()[0]}.c": "int a;\n"}
    for path, text in files.items():
        (repo / path).write_text(text)
    git(repo, "add", "-A")
    git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", subject)
    return git(repo, "rev-parse", "HEAD")


FAKE_PASS = """#!/bin/sh
# a fake series check: one PASS line per commit of BASE..HEAD
for c in $(git rev-list --reverse "$1..${2:-HEAD}"); do
    echo "PASS $(echo $c | cut -c1-12) debug=off built, kunit 1/1 | $(git log -1 --format=%s $c)"
done
"""
FAKE_FAIL = FAKE_PASS.replace("echo \"PASS", "echo \"FAIL")


@pytest.fixture
def world(tmp_path):
    """home: a fork clone with branch fork at the base; the series of two commits on `work`;
    a build host that is another clone of it; a guard directory with a planted token."""
    home = tmp_path / "home"
    home.mkdir()
    git(home, "init", "-q", "-b", "main")
    base = commit(home, "base commit")
    git(home, "branch", "fork")
    git(home, "checkout", "-q", "-b", "work")
    c1 = commit(home, "first change")
    c2 = commit(home, "second change")
    git(home, "checkout", "-q", "main")
    hosthome = tmp_path / "hosthome"
    hosthome.mkdir()
    subprocess.run(["git", "clone", "-q", str(home), str(hosthome / "clone")], check=True)
    conf = tmp_path / "conf"
    conf.mkdir()
    (conf / "a.c").write_text(f"int {SECRET};")
    g = tmp_path / "guard"
    g.mkdir()
    (g / "allowed.txt").write_text("")
    (g / "patterns.txt").write_text("fork\tforkonlyword\n")
    (g / "oldnames.toml").write_text("[rename]\n")
    (g / "glossary-reviewed.txt").write_text("")
    (g / "refs.local.toml").write_text(f'confidential = "{conf}"\n')
    env = {**os.environ, "HOME": str(hosthome), "FORK_CHECK_SSH": "sh -c",
           "FORK_CHECK_CLONE": "clone", "RESGX545_GUARD_DIR": str(g),
           "RESGX545_REQUIRE_GUARD": "1", "FORK_PASS_FILE": str(tmp_path / "pass")}
    return dict(home=home, base=base, c1=c1, c2=c2, env=env, tmp=tmp_path,
                fake=lambda text: write_exec(tmp_path / "fakecheck.sh", text))


def write_exec(path, text):
    path.write_text(text)
    path.chmod(0o755)
    return path


def recheck(w, script=None, **extra):
    env = {**w["env"], **extra}
    if script:
        env["FORK_CHECK_SCRIPT"] = str(script)
    return subprocess.run([str(RECHECK), w["base"], w["c2"]], cwd=w["home"], env=env,
                          capture_output=True, text=True)


def land(w, branch="fork", tip=None, **extra):
    env = {**w["env"], **extra}
    return subprocess.run([str(LAND), str(w["home"]), branch, w["base"], tip or w["c2"]],
                          env=env, capture_output=True, text=True)


def test_scripts_are_valid_bash_and_executable():
    for p in (RECHECK, LAND):
        assert os.access(p, os.X_OK), p
        subprocess.run(["bash", "-n", str(p)], check=True)


# --- recheck.sh --------------------------------------------------------------------------

def test_recheck_passes_and_records_the_tested_tip(world):
    w = world
    r = recheck(w, w["fake"](FAKE_PASS))
    assert r.returncode == 0, r.stdout + r.stderr
    assert pathlib.Path(w["env"]["FORK_PASS_FILE"]).read_text().strip() == w["c2"]
    assert "2 PASS" in r.stdout
    assert git(w["home"], "for-each-ref", "refs/fork-recheck") == ""     # the temporary ref


def test_recheck_sends_the_series_to_the_host(world):
    w = world
    recheck(w, w["fake"](FAKE_PASS))
    host = w["tmp"] / "hosthome" / "clone"
    assert git(host, "cat-file", "-t", w["c2"]) == "commit"


def test_recheck_fails_on_a_fail_line_and_records_nothing(world):
    w = world
    r = recheck(w, w["fake"](FAKE_FAIL))
    assert r.returncode != 0
    assert not pathlib.Path(w["env"]["FORK_PASS_FILE"]).exists()


def test_recheck_fails_when_a_commit_has_no_pass_line(world):
    w = world
    one = """#!/bin/sh
c=$(git rev-list --reverse "$1..${2:-HEAD}" | head -1)
echo "PASS $(echo $c | cut -c1-12) debug=off built | $(git log -1 --format=%s $c)"
"""
    r = recheck(w, w["fake"](one))
    assert r.returncode != 0
    assert not pathlib.Path(w["env"]["FORK_PASS_FILE"]).exists()


def test_recheck_removes_a_stale_pass_file(world):
    w = world
    pathlib.Path(w["env"]["FORK_PASS_FILE"]).write_text(w["c2"] + "\n")
    assert recheck(w, w["fake"](FAKE_FAIL)).returncode != 0
    assert not pathlib.Path(w["env"]["FORK_PASS_FILE"]).exists()


def test_recheck_dry_run_runs_the_real_script_and_records_nothing(world):
    w = world
    r = recheck(w, None, CHECK_DRY_RUN="1")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "DRY " in r.stdout
    assert not pathlib.Path(w["env"]["FORK_PASS_FILE"]).exists()


def test_recheck_refuses_an_unknown_tip(world):
    w = world
    r = subprocess.run([str(RECHECK), w["base"], "0" * 40], cwd=w["home"], env=w["env"],
                       capture_output=True, text=True)
    assert r.returncode != 0


# --- fork-land.sh ------------------------------------------------------------------------

def test_land_checks_then_moves_the_branch(world):
    w = world
    r = land(w, FORK_CHECK_SCRIPT=str(w["fake"](FAKE_PASS)))
    assert r.returncode == 0, r.stdout + r.stderr
    assert git(w["home"], "rev-parse", "fork") == w["c2"]


def test_land_uses_a_pass_file_that_names_the_tip(world):
    w = world
    pathlib.Path(w["env"]["FORK_PASS_FILE"]).write_text(w["c2"] + "\n")
    boom = write_exec(w["tmp"] / "boom.sh", "#!/bin/sh\necho ran >&2\nexit 9\n")
    r = land(w, FORK_CHECK_CMD=str(boom))
    assert r.returncode == 0, r.stdout + r.stderr
    assert git(w["home"], "rev-parse", "fork") == w["c2"]


def test_land_refuses_a_pass_file_for_another_tip(world):
    w = world
    pathlib.Path(w["env"]["FORK_PASS_FILE"]).write_text(w["c1"] + "\n")
    r = land(w, FORK_CHECK_CMD="true")                  # does not rewrite the pass file
    assert r.returncode != 0
    assert git(w["home"], "rev-parse", "fork") == w["base"]


def test_land_refuses_when_the_check_fails(world):
    w = world
    r = land(w, FORK_CHECK_SCRIPT=str(w["fake"](FAKE_FAIL)))
    assert r.returncode != 0
    assert git(w["home"], "rev-parse", "fork") == w["base"]


def test_land_never_rewrites_landed_commits(world):
    w = world
    git(w["home"], "branch", "-f", "fork", w["c2"])
    git(w["home"], "checkout", "-q", "-b", "other", w["base"])
    other = commit(w["home"], "diverging change")
    git(w["home"], "checkout", "-q", "main")
    pathlib.Path(w["env"]["FORK_PASS_FILE"]).write_text(other + "\n")
    r = land(w, tip=other, FORK_CHECK_CMD="true")
    assert r.returncode != 0
    assert git(w["home"], "rev-parse", "fork") == w["c2"]


def test_land_refuses_a_branch_checked_out_in_a_worktree(world):
    w = world
    git(w["home"], "checkout", "-q", "fork")
    pathlib.Path(w["env"]["FORK_PASS_FILE"]).write_text(w["c2"] + "\n")
    r = land(w, FORK_CHECK_CMD="true")
    assert r.returncode != 0
    assert git(w["home"], "rev-parse", "fork") == w["base"]


def test_land_refuses_a_planted_token_in_the_series(world):
    w = world
    git(w["home"], "checkout", "-q", "work")
    tip = commit(w["home"], "third change", {"third.c": f"int {SECRET};\n"})
    git(w["home"], "checkout", "-q", "main")
    pathlib.Path(w["env"]["FORK_PASS_FILE"]).write_text(tip + "\n")
    r = land(w, tip=tip, FORK_CHECK_CMD="true")
    assert r.returncode != 0
    assert SECRET not in r.stdout + r.stderr
    assert git(w["home"], "rev-parse", "fork") == w["base"]


def test_land_refuses_a_fork_pattern_in_a_message(world):
    w = world
    git(w["home"], "checkout", "-q", "work")
    tip = commit(w["home"], "third forkonlyword change")
    git(w["home"], "checkout", "-q", "main")
    pathlib.Path(w["env"]["FORK_PASS_FILE"]).write_text(tip + "\n")
    assert land(w, tip=tip, FORK_CHECK_CMD="true").returncode != 0


def test_land_fails_without_the_guard_data(world, tmp_path):
    w = world
    pathlib.Path(w["env"]["FORK_PASS_FILE"]).write_text(w["c2"] + "\n")
    r = land(w, FORK_CHECK_CMD="true", RESGX545_GUARD_DIR=str(tmp_path / "nowhere"))
    assert r.returncode != 0 and "ABSENT" in r.stdout + r.stderr
    assert git(w["home"], "rev-parse", "fork") == w["base"]


def test_land_dry_run_moves_nothing(world):
    w = world
    pathlib.Path(w["env"]["FORK_PASS_FILE"]).write_text(w["c2"] + "\n")
    r = land(w, FORK_CHECK_CMD="true", FORK_LAND_DRY_RUN="1")
    assert r.returncode == 0
    assert git(w["home"], "rev-parse", "fork") == w["base"]


def test_land_usage(world):
    r = subprocess.run([str(LAND)], capture_output=True, text=True)
    assert r.returncode == 2 and "usage" in r.stderr
