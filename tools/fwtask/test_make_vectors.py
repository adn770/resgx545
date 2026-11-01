# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""make_vectors.py: the 9b runs as hardware vectors of the firmware task (doc/specs/vectors.md,
kind firmware): one vector per run, the program as patched and run, what went in, what came out."""
import json
import os
import pathlib
import sys

import pytest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fwtask  # noqa: E402
import layout as L  # noqa: E402
import make_vectors  # noqa: E402


def fake_run(tmp_path):
    rec = {"H": {"0x814": 0xa5a5, "0xa78": 0x15}, "cmd_after": 0, "done": True, "echo": 7, "ms": 0.5,
           "overlap": 0, "restored": True, "slot": [0xa5a5, 0xdeadc0de, 0xdeadc0de, 0xdeadc0de],
           "job": {"A": 0x15a5a, "A_other": 0x15, "n": 3, "pair": 0, "params": {"8": 0xa5a5, "9": 0xf0f0},
                   "reg": "R1", "rep": 0, "regs": {"2068": 0x15a5a, "2680": 0x15}}}
    p = tmp_path / "t.jsonl"
    p.write_text(json.dumps(rec) + "\n")
    return p


def test_vector_has_the_patched_program_the_inputs_and_the_readback(tmp_path):
    f = make_vectors.convert(fake_run(tmp_path), "x9b_r1", "p1129-test")
    v = f["vectors"][0]
    assert f["format"] == "sgx545-vectors" and f["version"] == 1
    blob = fwtask.parse_blob(fwtask.blob_of("x9b_r1"))
    words = fwtask.apply_patches(blob.words, blob.patches, 0x32140000, {0: 6})
    assert v["program"]["words"] == [f"0x{w:016x}" for w in words]
    assert v["program"]["entry"] == 0 and v["init"]["task"] == "firmware"
    assert v["init"]["regs"] == {"0x0814": "0x00015a5a", "0x0a78": "0x00000015"}
    assert v["init"]["mem"]["0x001"] == "0x00000003"                       # cmd
    assert v["init"]["mem"][f"0x{L.slot(3):03x}"] == "0xdeadc0de"          # the initial fill value
    assert v["init"]["mem"]["0x008"] == "0x0000a5a5"
    assert v["readback"]["mem"][f"0x{L.slot(3):03x}"] == "0x0000a5a5"
    assert v["readback"]["regs"] == {"0x0814": "0x0000a5a5", "0x0a78": "0x00000015"}
    assert v["readback"]["failed"] is None


def test_every_hex_value_is_a_string_so_no_reader_loses_bits(tmp_path):
    f = make_vectors.convert(fake_run(tmp_path), "x9b_r1", "p1129-test")
    s = json.dumps(f)
    assert "deadc0de" in s and isinstance(f["vectors"][0]["init"]["mem"]["0x001"], str)


def test_a_run_that_did_not_finish_gives_no_vector(tmp_path):
    rec = json.loads(fake_run(tmp_path).read_text())
    rec["done"] = False
    p = tmp_path / "bad.jsonl"
    p.write_text(json.dumps(rec) + "\n")
    assert make_vectors.convert(p, "x9b_r1", "x")["vectors"] == []


def test_x11_keeps_only_the_ldr_result_and_seeds_the_timer(tmp_path):
    """CR_TIMER counts are not reproducible: X11's vector seeds the register with the recorded t0
    and compares only L."""
    rec = json.loads(fake_run(tmp_path).read_text())
    rec["job"]["n"] = 17
    rec["slot"] = [0xa5a5, 1000, 1040, 0xdeadc0de]
    p = tmp_path / "x11.jsonl"
    p.write_text(json.dumps(rec) + "\n")
    v = make_vectors.convert(p, "x9b_r1", "x")["vectors"][0]
    assert v["init"]["regs"]["0x0144"] == "0x000003e8"
    assert list(k for k in v["readback"]["mem"] if int(k, 16) >= L.RESULTS) == [f"0x{L.slot(17):03x}"]


DATA = pathlib.Path(os.environ["RESGX545_DATA"]) if os.environ.get("RESGX545_DATA") else None
RUNS = {"p1129-s5c-x0x1-r1": ("s5", "x9b_r1"), "p1129-s6r1": ("s6r1", "x9b_r1"),
        "p1129-s6r1b": ("s6r1", "x9b_r1"), "p1129-s6r2": ("s6r2", "x9b_r2")}


@pytest.mark.parametrize("run", sorted(RUNS))
def test_the_vectors_of_the_data_repository_are_the_conversion_of_the_raw_runs(run):
    """vectors/nokernel/usse/fwtask-9b/<run>.vec.json is make_vectors' output for the run's raw
    jsonl, apart from the time it was converted."""
    vec = DATA / "vectors/nokernel/usse/fwtask-9b" / f"{run}.vec.json" if DATA else None
    if vec is None or not vec.is_file():
        pytest.skip("SKIPPED, NOT PASSED: the 11.29 vectors are not in RESGX545_DATA")
    stem, blob = RUNS[run]
    got = make_vectors.convert(DATA / "firmware-tasks" / run / f"{stem}.jsonl", blob, run)
    want = json.loads(vec.read_text())
    got["run"].pop("converted"), want["run"].pop("converted")
    assert got == want
