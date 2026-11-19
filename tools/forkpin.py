# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The linux fork at the commit the tests are pinned to, read with `git`, so that the check does
not depend on which branch or commit the fork home (RESGX545_LINUX, default ../linux) has out.
RESGX545_FORK_PIN overrides PIN while a newer fork commit is under test."""
import os
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
PIN = "f9453424bf71"        # the linux fork's resgx545 branch the tests read
SGXFIVE = "drivers/gpu/drm/gma500/sgxfive"
_cache: dict = {}


def pin() -> str:
    return os.environ.get("RESGX545_FORK_PIN", PIN)


def home() -> pathlib.Path:
    return pathlib.Path(os.environ.get("RESGX545_LINUX", ROOT.parent / "linux"))


def show(path: str) -> str | None:
    """The text of `path` at the pinned commit, or None without the fork or the commit."""
    r = subprocess.run(["git", "-C", str(home()), "show", f"{pin()}:{path}"],
                       capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def sgxfive_dir() -> pathlib.Path | None:
    """A directory with the fork's sgxfive sources at the pinned commit (extracted once per
    process and pin), or None without the fork or the commit."""
    key = (str(home()), pin())
    if key not in _cache:
        d = pathlib.Path(tempfile.mkdtemp(prefix="forkpin_"))
        arch = subprocess.run(["git", "-C", str(home()), "archive", pin(), f"{SGXFIVE}/"],
                              capture_output=True)
        ok = arch.returncode == 0 and subprocess.run(
            ["tar", "-x", "-C", str(d)], input=arch.stdout).returncode == 0
        _cache[key] = d / SGXFIVE if ok else None
    return _cache[key]
