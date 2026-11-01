# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""sgxfive-test tri --words and --wait-ms, against the mock: the kernel's debugfs render_words
and TA/3D control block (buf09) saved before the first render and after each, while the
context lives, and the time each render is waited for."""
from __future__ import annotations

import os
import pathlib
import re
import subprocess

import pytest

HERE = pathlib.Path(__file__).resolve().parent
TOOL = os.environ.get("SGXFIVE_TEST", str(HERE.parent / "build" / "sgxfive-test"))


def run(*args: str, env: dict | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run([TOOL, *args], capture_output=True, text=True, timeout=60,
                          env={**os.environ, **(env or {})})


@pytest.fixture(scope="module", autouse=True)
def tool_exists():
    if not pathlib.Path(TOOL).exists():
        pytest.skip(f"{TOOL} not built (run make -C userspace/libsgxfive check)")


@pytest.fixture
def debugfs(tmp_path):
    """A stand-in for the kernel's dri/N/sgx directory (SGXFIVE_DEBUGFS)."""
    d = tmp_path / "debugfs"
    d.mkdir()
    (d / "render_words").write_text("ctx:0=0x00000001\nkw:1=0x00000002\n")
    (d / "buf09").write_bytes(bytes(range(16)) * 4)
    return d


def test_words_before_the_first_render_and_after_each(tmp_path, debugfs):
    out = tmp_path / "out"
    out.mkdir()
    r = run("--mock", "tri", "-n", "3", "--geometry", "1", "--geometry", "2", "--words",
            str(out), env={"SGXFIVE_DEBUGFS": str(debugfs)})
    assert r.returncode == 0, r.stdout + r.stderr
    for n in range(4):
        assert (out / f"words.{n}.txt").read_text() == "ctx:0=0x00000001\nkw:1=0x00000002\n"
        assert (out / f"ta3d.{n}.bin").read_bytes() == bytes(range(16)) * 4
        assert re.search(rf"^tri: words {n} to .*/words\.{n}\.txt \(33 bytes\), "
                         rf".*/ta3d\.{n}\.bin \(64 bytes\)$", r.stdout, re.M), r.stdout
    assert not (out / "words.4.txt").exists()
    # the words after render n follow its job line
    lines = r.stdout.splitlines()
    jobs = [i for i, ln in enumerate(lines) if ln.startswith("job:")]
    words = [i for i, ln in enumerate(lines) if ln.startswith("tri: words ")]
    assert len(jobs) == 3 and words[0] < jobs[0]
    assert all(j < w for j, w in zip(jobs, words[1:])), r.stdout


def test_words_after_a_failed_render(tmp_path, debugfs):
    """A render that faults is waited for, its words saved, then the command fails."""
    out = tmp_path / "out"
    out.mkdir()
    r = run("--mock", "tri", "--fault", "--words", str(out),
            env={"SGXFIVE_DEBUGFS": str(debugfs)})
    assert r.returncode == 1, r.stdout + r.stderr
    assert (out / "words.0.txt").exists() and (out / "words.1.txt").exists()


def test_words_missing_debugfs_fails(tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    r = run("--mock", "tri", "--words", str(out),
            env={"SGXFIVE_DEBUGFS": str(tmp_path / "none")})
    assert r.returncode == 1, r.stdout + r.stderr
    assert "--words" in r.stdout + r.stderr


def test_words_only_for_tri(tmp_path):
    r = run("--mock", "fill", "--words", str(tmp_path))
    assert r.returncode == 2, r.stdout + r.stderr


def test_wait_ms():
    r = run("--mock", "tri", "--wait-ms", "20000")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "tri: 1 renders ok" in r.stdout
    for args in (["--wait-ms", "0"], ["--wait-ms", "x"], ["--wait-ms", "600001"]):
        r = run("--mock", "tri", *args)
        assert r.returncode == 2, (args, r.stdout + r.stderr)
    r = run("--mock", "fill", "--wait-ms", "100")
    assert r.returncode == 2, r.stdout + r.stderr


def test_options_after_dump_render_are_read(tmp_path, debugfs):
    """--dump-render DIR takes one value: the option after it is still read."""
    (debugfs / "render_param").write_bytes(b"\x11" * 64)
    (debugfs / "render_tadata").write_bytes(b"\x22" * 64)
    r = run("--mock", "tri", "--dump-render", str(tmp_path), "-n", "2",
            env={"SGXFIVE_DEBUGFS": str(debugfs)})
    assert r.returncode == 0, r.stdout + r.stderr
    assert "tri: 2 renders ok" in r.stdout
