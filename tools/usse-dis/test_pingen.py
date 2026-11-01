# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""pinned.tsv is pingen's output: regenerating it (make pinned) gives the committed file, so a
pinned word is never edited by hand and a form changed on purpose is re-pinned in one step."""
import pathlib
import subprocess

HERE = pathlib.Path(__file__).resolve().parent


def test_pingen_writes_the_committed_pinned_words():
    subprocess.run(["make", "-s", "-C", str(HERE), "pingen"], check=True)
    out = subprocess.run([str(HERE / "pingen")], capture_output=True, text=True, check=True)
    assert out.stdout == (HERE / "pinned.tsv").read_text()
