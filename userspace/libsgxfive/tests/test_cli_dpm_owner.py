# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""sgxfive-test tri options of the 11.38 DPM and partial-render batch, against the mock:

  --keep-overflow --ctx2 [--close-first-early]: an overflowed first render does not stop the
      second context, and an overflowed second render is counted;
  --tadata-fill-render N:PAGE:VALUE[:ramp]: debugfs tadata_fill written just before render N, so
      that a page of the TA data can be changed between a geometry kick and the final render;
  --kept-copy DIR (tri --ctx2): debugfs render_kept copied to DIR/kept.N.bin after the second
      context's render N and before any close.
Run through `make check`, which builds the binary and sets SGXFIVE_TEST."""
from __future__ import annotations

import os
import pathlib
import subprocess

import pytest

HERE = pathlib.Path(__file__).resolve().parent
TOOL = os.environ.get("SGXFIVE_TEST", str(HERE.parent / "build" / "sgxfive-test"))


def run(*args: str, dbg: pathlib.Path | None = None) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    if dbg is not None:
        env["SGXFIVE_DEBUGFS"] = str(dbg)
    return subprocess.run([TOOL, *args], capture_output=True, text=True, timeout=60, env=env)


@pytest.fixture(scope="module", autouse=True)
def tool_exists():
    if not pathlib.Path(TOOL).exists():
        pytest.skip(f"{TOOL} not built (run make -C userspace/libsgxfive check)")


def test_keep_overflow_alone_still_counts():
    r = run("--mock", "--mock-pb-pages=0x28", "tri", "--width", "1024", "--height", "768", "--keep-overflow")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "1 overflowed" in r.stdout


def test_t2_second_context_after_an_overflowed_first_render():
    r = run("--mock", "--mock-pb-pages=0x28", "tri", "--width", "1024", "--height", "768",
            "--keep-overflow", "--ctx2", "--close-first-early")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "tri2 1024x768 #1: overflowed" in r.stdout, r.stdout


def test_t3_tadata_fill_before_render_n(tmp_path):
    (tmp_path / "tadata_fill").write_text("")
    r = run("--mock", "tri", "--width", "64", "--height", "64", "-n", "2", "--geometry", "1",
            "--tadata-fill-render", "2:6:0xa5000000:ramp", dbg=tmp_path)
    assert "tri: tadata_fill before render 2: 6 0xa5000000 ramp" in r.stdout, r.stdout + r.stderr
    assert (tmp_path / "tadata_fill").read_text() == "6 0xa5000000 ramp\n"


def test_t3_rejects_a_bad_spec():
    r = run("--mock", "tri", "--tadata-fill-render", "x")
    assert r.returncode != 0
    assert "bad --tadata-fill-render" in r.stderr


def test_t4_kept_copy_after_the_second_render(tmp_path):
    (tmp_path / "render_kept").write_bytes(bytes(range(256)) * 4)
    out = tmp_path / "out"
    out.mkdir()
    r = run("--mock", "tri", "--width", "64", "--height", "64", "--ctx2", "--close-first-early",
            "--kept-copy", str(out), dbg=tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    assert (out / "kept.1.bin").read_bytes() == bytes(range(256)) * 4


def test_t4_needs_ctx2():
    r = run("--mock", "tri", "--kept-copy", "/tmp")
    assert r.returncode == 2
    assert "--kept-copy is for tri --ctx2" in r.stderr
