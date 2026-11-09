# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The commit hooks and tools/check.sh: the message rules, the correction warning, and the
hooks and the quick check run in a synthetic repository with a synthetic guard directory (a
fake confidential tree, a planted token), so no real data is involved."""
import os
import pathlib
import subprocess

import pytest

import corrections
import msgcheck

HERE = pathlib.Path(__file__).resolve().parent
TOOLS = HERE.parent
SECRET = "zorptokalpha"
OLD = "ancientnamegamma"
TRAILER = "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"


def msg(subject="topic: add the thing", body="Why it changed, in a sentence.", trailer=TRAILER):
    return f"{subject}\n\n{body}\n\n{trailer}\n"


# --- msgcheck ----------------------------------------------------------------------------

def test_a_good_message_passes():
    assert msgcheck.check(msg()) == []


def test_subject_over_70_characters_fails():
    (p,) = msgcheck.check(msg("topic: " + "x" * 70))
    assert "70" in p


def test_subject_needs_a_topic_and_lowercase():
    assert msgcheck.check(msg("no topic here"))
    assert msgcheck.check(msg("topic: Capitalised"))


def test_subject_has_no_final_period():
    assert msgcheck.check(msg("topic: ends with a period."))


def test_body_wraps_at_80():
    assert msgcheck.check(msg(body="word " * 20))
    assert msgcheck.check(msg(body=("word " * 15).strip())) == []


def test_a_long_unbroken_line_is_allowed():
    assert msgcheck.check(msg(body="https://example.invalid/" + "a" * 90)) == []


def test_missing_blank_line_after_the_subject_fails():
    assert msgcheck.check("topic: x\nbody directly\n\n" + TRAILER + "\n")


def test_trailer_is_required_and_last():
    assert msgcheck.check(msg(trailer=""))
    assert msgcheck.check(msg() + "Signed-off-by: x\n")
    assert msgcheck.check(msg(trailer="Assisted-by: LLM")) == []


def test_merge_and_fixup_subjects_are_exempt_from_the_topic_rule():
    assert msgcheck.check("Merge branch 'x'\n\n" + TRAILER + "\n") == []
    assert msgcheck.check("fixup! topic: x\n\n" + TRAILER + "\n") == []


def test_comment_lines_are_ignored():
    assert msgcheck.check(msg() + "# Please enter the commit message\n" + "# " + "x" * 90) == []


# --- corrections -------------------------------------------------------------------------

REC = "+++\nid = \"E1\"\n+++\n\nBody.\n"


def test_an_appended_correction_is_fine():
    new = REC + "\nCorrection 2026-11-09: the digest was wrong.\n"
    assert corrections.warning("evidence/x/E1.md", REC, new) is None


def test_an_appended_correction_heading_is_fine():
    new = REC + "\n## Correction 2026-11-09: the digest was wrong.\n"
    assert corrections.warning("evidence/x/E1.md", REC, new) is None


def test_a_rewrite_warns():
    w = corrections.warning("evidence/x/E1.md", REC, REC.replace("Body", "Changed"))
    assert w and "Correction YYYY-MM-DD:" in w


def test_an_append_without_the_dated_form_warns():
    assert corrections.warning("evidence/x/E1.md", REC, REC + "\nmore text\n")


def test_a_new_record_is_not_a_correction():
    assert corrections.warning("evidence/x/E1.md", None, REC) is None


def test_other_paths_are_not_landed_records():
    assert corrections.warning("tools/x.py", REC, "other") is None


# --- the hooks, in a synthetic repository ------------------------------------------------

def git(path, *args, env=None, check=True):
    return subprocess.run(["git", "-C", str(path), *args], capture_output=True, text=True,
                          check=check, env=env)


@pytest.fixture
def world(tmp_path):
    conf = tmp_path / "conf"
    conf.mkdir()
    (conf / "a.c").write_text(f"int {SECRET}; int commonname;")
    g = tmp_path / "guard"
    g.mkdir()
    (g / "allowed.txt").write_text("# none\n")
    (g / "patterns.txt").write_text("d1\tforbiddenwordd\n")
    (g / "oldnames.toml").write_text(f'[rename]\n{OLD} = "newname"\n')
    (g / "glossary-reviewed.txt").write_text("")
    (g / "refs.local.toml").write_text(f'confidential = "{conf}"\n')
    r = tmp_path / "r"
    r.mkdir()
    git(r, "init", "-q")
    git(r, "config", "user.name", "t")
    git(r, "config", "user.email", "t@example.com")
    git(r, "config", "core.hooksPath", str(HERE))
    return r


def env(world, **extra):
    e = {**os.environ, "RESGX545_GUARD_DIR": str(world.parent / "guard")}
    e.pop("RESGX545_REQUIRE_GUARD", None)
    e.update(extra)
    return e


def commit(world, text, message=None, **extra):
    (world / "f.md").write_text(text)
    git(world, "add", "f.md")
    return git(world, "commit", "-q", "-m", message or msg(), env=env(world, **extra),
               check=False)


def test_pre_commit_refuses_a_planted_token(world):
    r = commit(world, f"we use {SECRET}\n")
    assert r.returncode != 0
    assert SECRET not in r.stdout + r.stderr
    assert git(world, "rev-list", "--all", "--count", check=False).stdout.strip() in ("", "0")


def test_pre_commit_passes_a_clean_commit(world):
    r = commit(world, "fine\n")
    assert r.returncode == 0, r.stdout + r.stderr
    assert git(world, "rev-list", "--count", "HEAD").stdout.strip() == "1"


def test_pre_commit_refuses_trailing_whitespace(world):
    assert commit(world, "fine \n").returncode != 0


def test_pre_commit_refuses_numpy_in_a_tracked_py(world):
    (world / "m.py").write_text("import " + "numpy as np\n")      # not whole here
    git(world, "add", "m.py")
    r = git(world, "commit", "-q", "-m", msg(), env=env(world), check=False)
    assert r.returncode != 0 and "numpy" in r.stdout + r.stderr


def test_absent_guard_fails_by_default(world, tmp_path):
    r = commit(world, "fine\n", RESGX545_GUARD_DIR=str(tmp_path / "nowhere"))
    assert r.returncode != 0 and "ABSENT" in r.stdout + r.stderr


def test_absent_guard_is_reported_when_not_required(world, tmp_path):
    r = commit(world, "fine\n", RESGX545_GUARD_DIR=str(tmp_path / "nowhere"),
               RESGX545_REQUIRE_GUARD="0")
    assert r.returncode == 0 and "NOT CHECKED" in r.stdout + r.stderr


def test_commit_msg_refuses_a_bad_subject(world):
    assert commit(world, "fine\n", "Bad subject\n").returncode != 0


def test_commit_msg_refuses_a_missing_trailer(world):
    assert commit(world, "fine\n", msg(trailer="")).returncode != 0


def test_commit_msg_refuses_an_old_spelling(world):
    r = commit(world, "fine\n", msg(body=f"mentions {OLD} here"))
    assert r.returncode != 0 and OLD not in r.stdout + r.stderr


def test_commit_msg_refuses_a_private_pattern(world):
    assert commit(world, "fine\n", msg(body="has forbiddenwordd inside")).returncode != 0


# --- check.sh ----------------------------------------------------------------------------

def test_check_script_is_valid_bash_and_executable():
    for p in (TOOLS / "check.sh", HERE / "pre-commit", HERE / "commit-msg"):
        assert os.access(p, os.X_OK), p
        subprocess.run(["bash", "-n", str(p)], check=True)


def test_quick_check_runs_on_the_repository_it_is_in(world):
    (world / "f.md").write_text("fine\n")
    git(world, "add", "f.md")
    r = subprocess.run([str(TOOLS / "check.sh"), "--quick"], cwd=world, env=env(world),
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    (world / "f.md").write_text(f"{SECRET}\n")
    git(world, "add", "f.md")
    r = subprocess.run([str(TOOLS / "check.sh"), "--quick"], cwd=world, env=env(world),
                       capture_output=True, text=True)
    assert r.returncode != 0 and SECRET not in r.stdout + r.stderr


def test_check_script_says_what_it_ran():
    out = subprocess.run([str(TOOLS / "check.sh"), "--list"], capture_output=True, text=True,
                         check=True).stdout
    for word in ("cargo test", "cargo fmt", "reuse lint", "guard.py", "check_refs", "numpy"):
        assert word in out


def test_check_only_runs_the_steps_that_match():
    out = subprocess.run([str(TOOLS / "check.sh"), "--list"], capture_output=True, text=True,
                         check=True, env={**os.environ, "CHECK_ONLY": "cargo fmt|reuse"}).stdout
    assert out.strip().splitlines() == ["cargo fmt --check", "reuse lint"]
