# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""sgxfive-test fill, copy and probe print the time of their job (submission to the wait's
return), as tri does, against the mock. The 11.15 register-limits runs read it."""
from __future__ import annotations

import os
import pathlib
import re
import subprocess
import sys

import pytest

HERE = pathlib.Path(__file__).resolve().parent
TOOL = os.environ.get("SGXFIVE_TEST", str(HERE.parent / "build" / "sgxfive-test"))


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([TOOL, *args], capture_output=True, text=True, timeout=60)


@pytest.fixture(scope="module", autouse=True)
def tool_exists():
    if not pathlib.Path(TOOL).exists():
        pytest.skip(f"{TOOL} not built (run make -C userspace/libsgxfive check)")


@pytest.mark.parametrize("cmd", ["fill", "copy"])
def test_the_job_time_follows_the_job_line(cmd):
    r = run("--mock", cmd)
    assert r.returncode == 0, r.stdout + r.stderr
    lines = r.stdout.splitlines()
    i = lines.index("job: ok")
    assert re.fullmatch(r"job time: \d+ us", lines[i + 1]), lines[i:i + 2]


def test_a_rejected_job_has_no_time():
    r = run("--mock", "copy", "--width", "1024", "--height", "1024")
    assert "job: rejected" in r.stdout
    assert "job time" not in r.stdout


def test_probe_prints_its_job_time(tmp_path):
    sys.path.insert(0, str(HERE.parent.parent.parent / "tools" / "fwcutter"))
    import ours  # builds usse-asm on demand
    out = tmp_path / "colour.bin"
    src = "phas #0, #0, pixel, end, parallel\nmov.skipinv.end o0, #0x12345678\n"
    subprocess.run([str(ours._tool("usse")), "-o", str(out), "-"], input=src.encode(),
                   capture_output=True, check=True)
    r = run("--mock", "probe", str(out))
    assert r.returncode == 0, r.stdout + r.stderr
    assert re.search(r"^probe colour: job time: \d+ us$", r.stdout, re.M), r.stdout
