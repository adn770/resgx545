# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Our own task sources (asm/fwtask): generated, mapped by sha256, verified, with no closed index
and the predictions frozen as they were before the first `str` (phase 11.29). None of these needs
the closed firmware."""
import hashlib
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import classify  # noqa: E402
import fwtask  # noqa: E402
import gen_blobs  # noqa: E402

FROZEN_SHA256 = "38e364de9a46535b82cf9f045eab84d19d2b112f7907ffd2cd38bf4514f67183"


def test_the_sources_are_the_generator_s_output():
    gen = gen_blobs.all_sources()
    assert sorted(gen) == sorted(p.stem for p in fwtask.sources())
    for name, text in gen.items():
        assert (fwtask.ASM / f"{name}.s").read_text() == text, name


def test_the_sha256_map_is_the_sources_and_the_blobs_they_assemble_to():
    committed = json.loads((fwtask.ASM / "fwtask.map").read_text())
    now = fwtask.current_map()
    assert committed == now
    for name, row in committed.items():
        assert row["source_sha256"] == hashlib.sha256((fwtask.ASM / row["source"]).read_bytes()).hexdigest()


def test_every_source_passes_the_default_deny_verifier():
    regs = fwtask.load_regs()
    for p in fwtask.sources():
        assert not fwtask.verify_blob(fwtask.blob_of(p.stem), regs), p.name


def test_no_source_holds_an_index_of_the_closed_code():
    """The four start indices of PDS #13 (E146) are not in any source: the continue index is a
    patched immediate, taken by the loader from the record being replaced."""
    closed = {1434, 2766, 3594}
    for p in fwtask.sources():
        for line in p.read_text().splitlines():
            for m in re.finditer(r"#?(0x[0-9a-fA-F]+|\b\d+\b)", line.split(";")[0]):
                assert int(m.group(1), 0) not in closed, (p.name, line)
        assert "@patch cont" in p.read_text()


def test_the_predictions_are_the_frozen_file():
    pred = HERE / "predictions.toml"
    assert hashlib.sha256(pred.read_bytes()).hexdigest() == FROZEN_SHA256
    assert (HERE / "predictions.sha256").read_text().strip() == FROZEN_SHA256
    assert classify.render() == pred.read_text()
