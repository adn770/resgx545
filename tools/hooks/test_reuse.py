# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The tree is REUSE compliant. reuse reads an SPDX tag wherever it sees one, so a string literal
that holds the tag and ends the line makes it parse an invalid expression: a literal that
needs the text splits it so the tag is not whole in the source."""
import pathlib
import shutil
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]


def test_reuse_lint_passes():
    exe = shutil.which("reuse", path=str(pathlib.Path(sys.executable).parent))
    if exe is None:
        pytest.skip("reuse is not installed (requirements-dev.txt)")
    r = subprocess.run([exe, "lint"], cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout[-1500:]
