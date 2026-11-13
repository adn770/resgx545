# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The USSE tutorial (doc/specs/usse_tutorial.md) is generated from doc/isa/books/
usse-tutorial.book; its quotes and its runs may not drift from the files and the tools.

- A code block after "From `PATH`:" is an excerpt of the file PATH (from the repository
  root): contiguous lines of it, its licence lines aside.
- A code block of shell lines replays them: `$ cat NAME` defines the file NAME as the lines
  up to the next command; `$ sgx-sim ...` must print the lines that follow it (standard
  output, then standard error), and `$ usse-asm ...` or `$ pds-asm ...` likewise. A program
  named without a path is looked up where doc/isa/build.py looks. Other commands are not
  replayed here.
"""
import pathlib
import re
import subprocess
import sys

import pytest

from conftest import HERE

ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "crates" / "pysgx"))
import load  # noqa: E402

TUTORIAL = ROOT / "doc" / "specs" / "usse_tutorial.md"
BLOCK = re.compile(r"(?:^From `([^`]+)`:\n\n)?^```\n(.*?)^```\n", re.M | re.S)
# where a program named without a path is found, as doc/isa/build.py looks
PROGS = [ROOT / "asm" / "transfer", ROOT / "asm" / "tri", ROOT / "asm",
         ROOT / "probes" / "usse" / "templates"]


def blocks():
    """(source path or None, block text) of every code block."""
    return [(m.group(1), m.group(2)) for m in BLOCK.finditer(TUTORIAL.read_text())]


def sections():
    """{section number: its text} of the numbered sections."""
    parts = re.split(r"^## (\d+)\. ", TUTORIAL.read_text(), flags=re.M)[1:]
    return {int(n): text for n, text in zip(parts[::2], parts[1::2])}


def without_licence(text):
    return [ln for ln in text.splitlines() if not re.match(r"\s*(?:[;#]|//)\s*SPDX-", ln)]


def contiguous(part, whole):
    n = len(part)
    # an excerpt is at least two lines, so that it cannot match anywhere by being a blank line
    return (n >= 2 and any(ln.strip() for ln in part)
            and any(whole[i:i + n] == part for i in range(len(whole) - n + 1)))


def program(name):
    for d in PROGS:
        if (d / name).is_file():
            return d / name
    return None


@pytest.fixture(scope="module")
def sim():
    r = subprocess.run(["cargo", "build", "-q", "--release", "-p", "sgx-tools", "--bin",
                        "sgx-sim"], cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return load.cargo_target_dir() / "release" / "sgx-sim"


def test_the_tutorial_quotes_sources_and_runs():
    got = blocks()
    assert sum(path is not None for path, _ in got) >= 5
    assert sum(text.startswith("$ ") for _, text in got) >= 4


def test_quoted_sources_are_excerpts_of_the_files():
    quoted = [(path, text) for path, text in blocks() if path is not None]
    assert quoted
    for path, text in quoted:
        assert (ROOT / path).is_file(), path
        part = without_licence(text)
        assert contiguous(part, without_licence((ROOT / path).read_text())), path


def test_every_run_block_replays_commands():
    for _, text in blocks():
        if text.startswith("$ "):
            cmd = text[2:].split(None, 1)[0]
            # cargo is shown (the vectors run), not replayed here
            assert cmd in ("cat", "sgx-sim", "usse-asm", "pds-asm", "cargo"), text


def test_the_simulator_runs_of_the_main_sections_are_present():
    for n in (1, 2, 3, 6):
        assert re.search(r"^\$ sgx-sim ", sections()[n], re.M), f"section {n} has no run"


def replay(text, tool, tmp_path):
    """Replay the commands of a shell block that `tool` prints; return how many ran."""
    ran = 0
    files: dict[str, str] = {}
    for step in re.split(r"^\$ ", text, flags=re.M)[1:]:
        cmd, _, out = step.partition("\n")
        argv = cmd.split()
        if argv[0] == "cat":
            files[argv[1]] = out
            continue
        if argv[0] not in tool:
            continue
        for name, body in files.items():
            (tmp_path / name).write_text(body)
        args = [str(program(a)) if a not in files and program(a) else a for a in argv[1:]]
        r = subprocess.run([str(tool[argv[0]]), *args], cwd=tmp_path, capture_output=True,
                           text=True)
        # a run the tutorial shows stopping as unsupported exits with status 1, the others 0
        want = 1 if out.rstrip("\n").split("\n")[-1].startswith("unsupported") else 0
        assert r.returncode == want, f"{cmd}: exit status {r.returncode}: {r.stderr}"
        got = r.stdout.rstrip("\n").split("\n") + [ln for ln in r.stderr.split("\n") if ln]
        assert got == out.rstrip("\n").split("\n"), cmd
        ran += 1
    return ran


def test_simulator_runs_are_what_the_tool_prints(sim, tmp_path):
    ran = sum(replay(text, {"sgx-sim": sim}, tmp_path) for _, text in blocks()
              if text.startswith("$ "))
    assert ran >= 6
