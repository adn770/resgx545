# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Our own task sources (asm/fwtask): generated, mapped by sha256, verified, with no closed index
and the predictions frozen as they were before the first `str` (phase 11.29) and before the first
run of stage B (phase 11.30). None of these needs the closed firmware."""
import hashlib
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import classify  # noqa: E402
import classify1129  # noqa: E402
import classify_b2  # noqa: E402
import fwtask  # noqa: E402
import gen_blobs  # noqa: E402

FROZEN_SHA256 = "38e364de9a46535b82cf9f045eab84d19d2b112f7907ffd2cd38bf4514f67183"
FROZEN_1130 = "d8c677cd520c8304aa60c5f10a1743cab132a032c60671d85306644836827197"
FROZEN_1130_B2 = "35b326d7a56799c18c164e13f519f7e8402f02c49d9ee9832f562f666e743c58"


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
    assert classify1129.render() == pred.read_text()


def test_the_11_30_predictions_are_the_frozen_files():
    """predictions-1130.toml was frozen before stage B (22:31) and predictions-1130-b2.toml before
    stage B2, after stage B's results were read (so its rows are not blind to them)."""
    for name, sha, render in (("predictions-1130", FROZEN_1130, classify.render),
                              ("predictions-1130-b2", FROZEN_1130_B2, classify_b2.render)):
        pred = HERE / f"{name}.toml"
        assert hashlib.sha256(pred.read_bytes()).hexdigest() == sha
        assert (HERE / f"{name}.sha256").read_text().strip() == sha
        assert render() == pred.read_text()


def test_the_sources_that_ran_in_11_30_are_the_blobs_the_runs_uploaded():
    """The blob hashes of env.toml in resgx545-data (firmware-tasks/p1130-*): the map's."""
    ran = {"state2": "df82c85410feee7019e067ab3e98aada7c65b4faa3e1a1aaa2f8d1f0771d7ebc",
           "state3": "4465620910e7f895ba6c903c17a1a76097ef650ace10cc6c2ecf6bf4140c7480",
           "events_m": "9b9ddac0182bce6a2c6a0729423221b9402e7758261f0366f7055ec6266fe194",
           "slow": "683dd70ddf06243a6603ab6cc323ee9e0f156c8650165a771138c1de2dac7a1b",
           "trc_08": "cbb1de22af31", "trc_09": "4ae3305e793c", "trc_12": "4060637c3208",
           "trc_16": "e6072dd9564c", "trc_24": "008953fa3be2", "trc_31": "0fbf908f392d"}
    m = json.loads((fwtask.ASM / "fwtask.map").read_text())
    for name, sha in ran.items():
        assert m[name]["sha256"].startswith(sha), name


def test_oomring2_is_the_blob_r7_dpm_ran_and_reads_the_two_page_counts_only():
    """oomring2 (round 7, R7-4 a): R5-dpm's oomring with two read-only loads, CR_DPM_PAGE_STATUS
    (#457) and CR_DPM_GLOBAL_PAGE_STATUS (#459), stored in each rung's words 6 and 7. It lands as
    the blob R7-dpm's set B armed on module 37EC97AB (resgx545-data render/closing-r7-dpm,
    bins/blobs.json; E918), accepted by the Python verifier; no str."""
    blob = fwtask.blob_of("oomring2")
    assert hashlib.sha256(blob).hexdigest() == "c855818ec4334a0826be4361f0c0c1ae6819fba681e7b9f3a4f9dab028399676"
    assert fwtask.refusal(blob, fwtask.load_regs()) is None
    text = (fwtask.ASM / "oomring2.s").read_text()
    code = [ln.split(";")[0].split() for ln in text.splitlines()]
    assert sorted({w[2] for w in code if w and w[0] == "ldr"}) == ["#457,", "#459,", "#81,"]
    assert not [w for w in code if w and w[0] == "str"]
