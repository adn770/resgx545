# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""One made-up word per form, with its pinned decoder text (pinned.tsv).

Each line of pinned.tsv names an instruction set (usse or pds), a form index (its line in
`--forms`), a word and the text the decoder prints for it. The words are made up: the fields
of each form are set to values of our choosing, distinct from each other and from the
form's defaults where the form allows it, so that a field moved, resized or swapped changes
the text. Every form of both tables must be hit by a pinned word, and every pinned word must
decode with its form to its text. The Rust decoders read the same file
(crates/usse-isa/tests/pinned.rs, crates/pds-isa/tests/pinned.rs).
"""
import pathlib
import struct
import subprocess

import pytest

HERE = pathlib.Path(__file__).resolve().parent
PINNED = HERE / "pinned.tsv"
TOOLS = {"usse": ("usse-dis", "Q", ()), "pds": ("pds-dis", "I", ("0",))}


def pinned(isa: str) -> list[tuple[int, int, str]]:
    """(form index, word, text) of the pinned words of one instruction set."""
    rows = []
    for line in PINNED.read_text().splitlines():
        if line and not line.startswith("#"):
            which, form, word, text = line.split("\t")
            if which == isa:
                rows.append((int(form), int(word, 16), text))
    return rows


@pytest.fixture(scope="module", autouse=True)
def build():
    subprocess.run(["make", "-s", "-C", str(HERE), "usse-dis", "pds-dis"], check=True)


def forms(isa: str) -> int:
    out = subprocess.run([str(HERE / TOOLS[isa][0]), "--forms"], capture_output=True,
                         text=True, check=True).stdout
    return len(out.splitlines())


def which(isa: str, words: list[int], tmp_path: pathlib.Path) -> list[tuple[str, int]]:
    """(text, form index) the decoder gives each word."""
    tool, fmt, extra = TOOLS[isa]
    blob = tmp_path / f"{isa}.bin"
    blob.write_bytes(struct.pack(f"<{len(words)}{fmt}", *words))
    out = subprocess.run([str(HERE / tool), "--which", str(blob), *extra], capture_output=True,
                         text=True, check=True).stdout
    rows = []
    for line in out.splitlines():
        _, text, form = line.split("\t")
        rows.append((text, int(form.lstrip("#"))))
    return rows


@pytest.mark.parametrize("isa", TOOLS)
def test_pinned_words_decode_with_their_form_to_their_text(isa, tmp_path):
    rows = pinned(isa)
    assert rows
    got = which(isa, [w for _, w, _ in rows], tmp_path)
    bad = [f"{w:X}: form {f}, {t!r}; decoded as form {gf}, {gt!r}"
           for (f, w, t), (gt, gf) in zip(rows, got) if (gt, gf) != (t, f)]
    assert len(got) == len(rows)
    assert not bad, "\n".join(bad)


@pytest.mark.parametrize("isa", TOOLS)
def test_every_form_is_hit_by_a_pinned_word(isa, tmp_path):
    hit = {f for _, f in which(isa, [w for _, w, _ in pinned(isa)], tmp_path)}
    missing = sorted(set(range(forms(isa))) - hit)
    assert not missing, f"{isa} forms without a pinned word: {missing}"
