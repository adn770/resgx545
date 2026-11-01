# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The USSE tutorial (doc/specs/usse_tutorial.md) quotes our sources and the assembler's
output; neither may drift.

- A code block after "From `PATH`:" is the file PATH (from the repository root) without
  its licence header.
- A code block of shell lines replays them: `$ cat NAME` defines the file NAME as the lines
  up to the next command, and `$ usse-asm ...` or `$ pds-asm ...` must print the lines that
  follow it. Other commands are not replayed here.
"""
import pathlib
import re
import subprocess

from conftest import HERE

ROOT = HERE.parents[1]
TUTORIAL = ROOT / "doc" / "specs" / "usse_tutorial.md"
BLOCK = re.compile(r"(?:^From `([^`]+)`:\n\n)?^```\n(.*?)^```\n", re.M | re.S)


def blocks():
    """(source path or None, block text) of every code block."""
    return [(m.group(1), m.group(2)) for m in BLOCK.finditer(TUTORIAL.read_text())]


def without_licence(text):
    lines = text.splitlines(keepends=True)
    while lines and "SPDX-" in lines[0]:
        lines.pop(0)
    return "".join(lines)


def test_the_tutorial_quotes_sources_and_listings():
    got = blocks()
    assert sum(path is not None for path, _ in got) >= 5
    assert sum(text.startswith("$ ") for _, text in got) >= 2


def test_quoted_sources_are_the_files():
    for path, text in blocks():
        if path is not None:
            assert text == without_licence((ROOT / path).read_text()), path


def test_listings_are_what_the_assembler_prints(tmp_path):
    ran = 0
    for _, text in blocks():
        if not text.startswith("$ "):
            continue
        files: dict[str, str] = {}
        steps = re.split(r"^\$ ", text, flags=re.M)[1:]
        for step in steps:
            cmd, _, out = step.partition("\n")
            argv = cmd.split()
            if argv[0] == "cat":
                files[argv[1]] = out
                continue
            if argv[0] not in ("usse-asm", "pds-asm"):
                continue
            for name, body in files.items():
                (tmp_path / name).write_text(body)
            args = [a if a in files or a.startswith("-") or a == argv[argv.index("-o") + 1]
                    else str(ROOT / a) for a in argv[1:]]
            r = subprocess.run([str(HERE / argv[0]), *args], cwd=tmp_path, capture_output=True,
                               text=True)
            assert (r.returncode, r.stderr) == (0, ""), cmd
            assert r.stdout == out, cmd
            ran += 1
    assert ran >= 2
