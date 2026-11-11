# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The tests that read the linux fork read the pinned commit, whatever the fork home has checked
out (KB-T5): a home on another branch, or on a newer commit, changes nothing."""
import pathlib
import subprocess
import sys

import pytest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import forkpin  # noqa: E402

SG = "drivers/gpu/drm/gma500/sgxfive"


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t",
                           *args], check=True, capture_output=True, text=True).stdout.strip()


@pytest.fixture
def home(tmp_path, monkeypatch):
    """A fork home with the pinned commit, then a newer one, checked out on another branch."""
    h = tmp_path / "linux"
    (h / SG).mkdir(parents=True)
    git(h, "init", "-q", "-b", "resgx545")
    (h / SG / "a.h").write_text("pinned\n")
    git(h, "add", "-A")
    git(h, "commit", "-q", "-m", "pinned")
    pin = git(h, "rev-parse", "HEAD")
    git(h, "checkout", "-q", "-b", "sgx545")
    (h / SG / "a.h").write_text("newer\n")
    (h / SG / "b.h").write_text("only later\n")
    git(h, "add", "-A")
    git(h, "commit", "-q", "-m", "newer")
    monkeypatch.setenv("RESGX545_LINUX", str(h))
    monkeypatch.setenv("RESGX545_FORK_PIN", pin)
    return h


def test_show_reads_the_pinned_commit_not_the_checkout(home):
    assert (home / SG / "a.h").read_text() == "newer\n"
    assert forkpin.show(f"{SG}/a.h") == "pinned\n"


def test_sgxfive_dir_is_the_pinned_tree(home):
    d = forkpin.sgxfive_dir()
    assert (d / "a.h").read_text() == "pinned\n"
    assert not (d / "b.h").exists()


def test_no_fork_or_no_pin_gives_none(tmp_path, monkeypatch):
    monkeypatch.setenv("RESGX545_LINUX", str(tmp_path / "nothing"))
    assert forkpin.sgxfive_dir() is None
    assert forkpin.show(f"{SG}/a.h") is None
