# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Tests for pds_esil_check.py: the random programs stay inside what the simulator models, and
the fork's PDS ESIL computes what the simulator does. The checks against the fork need its
install (R2_PREFIX, or its prefix beside the repository) and are skipped without it."""
import os
import pathlib
import random
import shutil
import subprocess
import tempfile

import pytest

import pds_esil_check as pc

needs_tools = pytest.mark.skipif(
    shutil.which("cargo") is None, reason="needs cargo (the Rust pds-asm and sgx-sim)")


@pytest.fixture(scope="module", autouse=True)
def tools():
    if shutil.which("cargo"):
        subprocess.run(["cargo", "build", "-q", "-p", "sgx-tools"], cwd=pc.ROOT, check=True)


def _fork_pds_esil():
    prefix = pc.PREFIX
    if not (prefix / "bin" / "r2").exists():
        return False
    try:
        out = subprocess.run([str(pathlib.Path(prefix) / "bin" / "r2"), "-q", "-a", "pds", "-b",
                              "32", "-c", "wx 60000017; aoj 1", "malloc://8"],
                             capture_output=True, text=True).stdout
    except OSError:
        return False
    return '"esil":"ds0_0,ds0_48,="' in out          # mov32 ds0[48], ds0[0]


@needs_tools
def test_random_programs_run_to_their_halt_in_the_simulator():
    """Every generated program is one the simulator models end to end (it would raise)."""
    with tempfile.TemporaryDirectory() as t:
        for i in range(40):
            want = pc.simulate(pc.random_program(random.Random(i)), pathlib.Path(t))
            assert len([r for r in want if r.startswith("ds")]) >= 8


@needs_tools
def test_the_fixed_program_writes_what_the_reference_says():
    """A few of its results, worked out from doc/specs/pds_isa.md by hand."""
    with tempfile.TemporaryDirectory() as t:
        want = pc.simulate(pc.FIXED, pathlib.Path(t))
    assert want["ds0_49"] == 5 + 2 + 1 + 3      # adc after a carry, then the loop's 3 adds
    assert want["ds0_51"] == 5 - 2 - 1         # sbc after a borrow
    assert want["ds1_49"] == 0xAAAA2222        # mov16 into the high half
    assert want["ds0_52"] == 0xAAAABBBB        # mov128 with its pairs swapped
    assert want["ds1_56"] == 0x7FFFFFF0        # abs under alum signed
    assert want["ds1_55"] == 0xFFFFFFFE        # mul of -1 by 2 under alum signed


@needs_tools
@pytest.mark.skipif(not _fork_pds_esil(), reason="no install of the radare2 fork")
def test_the_fork_emulates_as_the_simulator():
    assert pc.check(pc.FIXED) == []
    for i in range(60):
        assert pc.check(pc.random_program(random.Random(1000 + i))) == [], i
