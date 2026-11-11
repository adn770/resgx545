# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""sgxfive-test tri --aa4 against the mock: the render context (and the --ctx2 one) is created
with DRM_SGXFIVE_CTX_RENDER_AA_4X, the flag for 4x targets, which the kernel gives four arrays
of region headers and lets a job set TE_AA bits 31:30. The option sets only the flag: the job's
words stay what the pokes make them (the runs' --poke cmd:1=0xe0000000 and their cmd:10, 13 and
16 words), so a 1x job on a 4x context can still be run. Without it nothing changes. The mock
refuses a multisampled TE_AA on a context made without the flag, as the kernel does.
Run through `make check`, which builds the binary and sets SGXFIVE_TEST."""
from __future__ import annotations

import os
import pathlib
import subprocess

import pytest

HERE = pathlib.Path(__file__).resolve().parent
TOOL = os.environ.get("SGXFIVE_TEST", str(HERE.parent / "build" / "sgxfive-test"))
AA4_LINE = "tri: render context made for 4x targets (DRM_SGXFIVE_CTX_RENDER_AA_4X)"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([TOOL, *args], capture_output=True, text=True, timeout=60)


@pytest.fixture(scope="module", autouse=True)
def tool_exists():
    if not pathlib.Path(TOOL).exists():
        pytest.skip(f"{TOOL} not built (run make -C userspace/libsgxfive check)")


def test_without_the_option_nothing_changes():
    r = run("--mock", "tri", "--width", "64", "--height", "64")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "tri: render context for targets up to 64x64\n" in r.stdout
    assert "made for 4x" not in r.stdout
    assert "tri: 1 renders ok" in r.stdout


def test_aa4_creates_the_context_with_the_flag():
    r = run("--mock", "tri", "--width", "64", "--height", "64", "--aa4")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "tri: render context for targets up to 64x64\n" in r.stdout
    assert AA4_LINE in r.stdout
    # the flag only: the job keeps the library's single-sampled TE_AA, every pixel right
    assert "wrong 0 inside, 0 outside, 0 at edges" in r.stdout
    assert "tri: 1 renders ok" in r.stdout


def test_a_4x_job_needs_the_flag():
    poke = ["--poke", "cmd:1=0xe0000000"]
    r = run("--mock", "tri", "--width", "64", "--height", "64", *poke)
    assert r.returncode != 0
    assert "-22" in r.stdout + r.stderr or "Invalid argument" in r.stdout + r.stderr
    r = run("--mock", "tri", "--width", "64", "--height", "64", "--aa4", *poke)
    assert r.returncode == 0, r.stdout + r.stderr
    assert AA4_LINE in r.stdout


def test_aa4_with_ctx2_flags_both_contexts():
    r = run("--mock", "tri", "--width", "64", "--height", "64", "--aa4", "--ctx2",
            "--poke", "cmd:1=0xe0000000")
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stdout.count(AA4_LINE) == 1
    assert "tri: second render context made for 4x targets" in r.stdout


@pytest.mark.parametrize("cmd", [["fill"], ["dummy"], ["copy"]])
def test_aa4_is_for_tri(cmd):
    r = run("--mock", *cmd, "--aa4")
    assert r.returncode == 2
    assert "--aa4 is for tri" in r.stderr
