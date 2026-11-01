# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""sgxfive-test probe --tri ... --tri-full against the mock: the first triangle of a probe's
render covers the whole target, as `tri --tri-full` does (the vertices (0,0), (3W,0), (0,3H)), so
that every tile of the render has pixels. The 11.26 identity maps need a position-coded image of
every stored pixel of the target; the default triangle covers about a quarter of it."""
from __future__ import annotations

import os
import pathlib
import re
import subprocess
import sys

import pytest

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent
TOOL = os.environ.get("SGXFIVE_TEST", str(HERE.parent / "build" / "sgxfive-test"))
PHAS = "phas #0, #0, pixel, end, parallel\n"
BG = 0xff203040                 # the first triangle's background (sgxfive_tri_default)
GREEN = 0xff00ff00


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([TOOL, *args], capture_output=True, text=True, timeout=60)


@pytest.fixture(scope="module", autouse=True)
def tool_exists():
    if not pathlib.Path(TOOL).exists():
        pytest.skip(f"{TOOL} not built (run make -C userspace/libsgxfive check)")


def assemble(tmp_path: pathlib.Path, name: str, source: str) -> pathlib.Path:
    sys.path.insert(0, str(ROOT / "tools" / "fwcutter"))
    import ours  # builds the assemblers on demand
    out = tmp_path / f"{name}.bin"
    subprocess.run([str(ours._tool("usse")), "-o", str(out), "-"], input=source.encode(),
                   capture_output=True, check=True)
    return out


def summary(out: str, name: str) -> dict:
    # a mixed target prints "o0 mixed 0xV xN ...", a uniform one "o0 0xV (N of N)"
    m = re.search(rf"^probe {name}: o0 mixed (.*)$", out, re.M)
    if m:
        return {int(v, 16): int(c) for v, c in re.findall(r"(0x[0-9a-f]+) x(\d+)", m.group(1))}
    m = re.search(rf"^probe {name}: o0 (0x[0-9a-f]+) \((\d+) of \d+\)", out, re.M)
    assert m, out
    return {int(m.group(1), 16): int(m.group(2))}


def test_probe_tri_full_covers_the_target(tmp_path):
    f = assemble(tmp_path, "pix", PHAS + "mov.skipinv.end o0, #0xFF00FF00\n")
    r = run("--mock", "probe", "--tri", "pixel", "--tri-full", "--temps", "8", str(f))
    assert r.returncode == 0, r.stdout + r.stderr
    # the same line `tri --tri-full` prints, so a run's output says which triangle it drew
    assert re.search(r"^probe pix: triangle \(0,0\) \(192,0\) \(0,192\)$", r.stdout, re.M), r.stdout
    vals = summary(r.stdout, "pix")
    assert vals.get(GREEN, 0) == 64 * 64 and BG not in vals, vals


def test_probe_tri_full_follows_the_size(tmp_path):
    f = assemble(tmp_path, "pix", PHAS + "mov.skipinv.end o0, #0xFF00FF00\n")
    r = run("--mock", "probe", "--tri", "pixel", "--tri-full", "--width", "128", "--height", "64",
            "--temps", "8", str(f))
    assert r.returncode == 0, r.stdout + r.stderr
    assert re.search(r"triangle \(0,0\) \(384,0\) \(0,192\)", r.stdout), r.stdout
    assert summary(r.stdout, "pix").get(GREEN, 0) == 128 * 64


def test_probe_tri_without_the_option_keeps_the_default_triangle(tmp_path):
    f = assemble(tmp_path, "pix", PHAS + "mov.skipinv.end o0, #0xFF00FF00\n")
    r = run("--mock", "probe", "--tri", "pixel", "--temps", "8", str(f))
    assert r.returncode == 0, r.stdout + r.stderr
    vals = summary(r.stdout, "pix")
    assert vals.get(BG, 0) > 0 and "triangle (" not in r.stdout, r.stdout


@pytest.mark.parametrize("args", [["probe", "--tri-full"], ["probe", "--coords", "--tri-full"]])
def test_tri_full_needs_probe_tri(args, tmp_path):
    # a fill probe has no triangle: a usage error, as `fill --tri-full` is
    f = assemble(tmp_path, "pix", PHAS + "mov.skipinv.end o0, #0\n")
    r = run("--mock", *args, str(f))
    assert r.returncode == 2 and re.search(r"^sgxfive-test: .*--tri-full", r.stderr, re.M), (
        r.returncode, r.stderr)
