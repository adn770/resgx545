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
import make_vectors1130  # noqa: E402


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


# ---- phase 11.30: the vectors with task state ------------------------------------------------
def test_slow_vector_has_the_loop_count_the_overlap_flag_and_no_time(tmp_path):
    d = tmp_path / "p1130-d-slow"
    d.mkdir()
    rec = {"H": {}, "cmd_after": 0, "done": True, "echo": 3, "ms": 0.8, "overlap": 0, "restored": True,
           "slot": [L.INITFILL] * 4, "job": {"n": 1, "params": {"10": 10000}}}
    (d / "s11.jsonl").write_text(json.dumps(rec) + "\n")
    (v,) = make_vectors1130.slow_vectors(tmp_path)
    assert v["init"]["mem"]["0x00a"] == "0x00002710" and v["init"]["mem"]["0x001"] == "0x00000001"
    assert v["readback"]["mem"]["0x004"] == "0x00000000"           # overlap
    assert v["readback"]["mem"]["0x002"] == f"0x{L.DONE:08x}" and v["readback"]["mem"]["0x005"] == "0x00000003"
    assert "ms" in v["provenance"] and not any("ms" in k for k in v["readback"])


def test_events_vector_logs_what_the_stub_was_given_and_the_tick_logs_nothing(tmp_path):
    for run in ("p1130-c-events", "p1130-c2-events", "p1130-c3-events"):
        d = tmp_path / run
        d.mkdir()
        (d / "q033-q1.json").write_text(json.dumps({"log": [1, 2, 0x03000000, 0x01061a70] + [0] * 12,
                                                    "quiet_log": [0] * 16}))
    vs = make_vectors1130.events_vectors(tmp_path)
    assert len(vs) == 6
    kick, tick = vs[0], vs[1]
    assert kick["init"]["state"]["pa"] == {"0": "0x00000002", "1": "0x03000000", "2": "0x01061a70"}
    assert tick["init"]["state"]["pa"]["1"] == "0x02000000"
    assert kick["program"]["entry"] == 0 and kick["init"]["task"] == "firmware"
    log = {k: v for k, v in kick["readback"]["mem"].items() if int(k, 16) >= L.LOG}
    assert list(log.values())[:4] == ["0x00000001", "0x00000002", "0x03000000", "0x01061a70"]
    assert set(v for k, v in tick["readback"]["mem"].items() if int(k, 16) >= L.LOG) == {"0x00000000"}


def test_a_writer_vector_lists_only_what_the_next_event_read_of_the_state(tmp_path):
    """readback.state of a writer: sa100, sa127, sa20, sa24, r20, r21, i0, i1 and p1 to p3; never sa64,
    p0 or pclink, which the closed task changes (E536)."""
    def rd(k, pclink, p, r20, r21, i0, i1, sa):
        s = {"10": [pclink, *p[:3]], "11": [p[3], r20, r21, i0], "12": list(sa[:4]),
             "13": [sa[4], i1, L.INITFILL, L.INITFILL]}
        return {"k": k, "slots": s, "kind": "x"}
    ctl = {"rounds": [rd(0, 0x98, (1, 1, 0, 0), 0, 0x1000, 5, 6, (2, 7, 8, 0, 0)),
                      rd(1, 0x98, (1, 1, 0, 0), 0, 0x1000, 5, 6, (2, 7, 8, 0, 0))], "stop": None}
    m = [0x80000000 + i for i in range(9)]
    w = rd(2, 6, (1, 0, 1, 1), m[5], m[6], m[7], m[8], (2, m[1], m[2], m[3], m[4]))
    g = rd(3, 0x98, (1, 1, 1, 1), m[5], m[6], m[7], m[8], (2, m[1], m[2], m[3], m[4]))
    f = rd(4, 0x98, (1, 1, 0, 1), 0, 0x1000, m[7], m[8], (2, m[1], m[2], m[3], m[4]))
    d = tmp_path / "p1130-b-tailpair"
    d.mkdir()
    (d / "b-controls.json").write_text(json.dumps(ctl))
    (d / "b-rounds.json").write_text(json.dumps({"rounds": [w, g, f] * 3, "stop": None}))
    (d / "b-markers.json").write_text(json.dumps({"markers": [m, m, m], "p_pattern": [0, 0, 1, 1]}))
    vs = make_vectors1130.state_vectors(tmp_path)
    assert len(vs) == 14 and sum("writer" in v["id"] for v in vs) == 3
    st = next(v for v in vs if "writer" in v["id"])["readback"]["state"]
    assert set(st) == {"sa", "r", "i", "p"}
    assert set(st["sa"]) == {"100", "127", "20", "24"} and set(st["p"]) == {"1"}   # only p1 is shown to persist
    assert st["p"]["1"] == "0x00000000" and st["r"]["20"] == f"0x{m[5]:08x}"


@pytest.mark.parametrize("sub", ["fwtask-state", "fwtask-events", "fwtask-slow", "fwtask-trc"])
def test_the_11_30_vectors_of_the_data_repository_are_the_conversion_of_the_raw_runs(sub, tmp_path):
    """vectors/nokernel/usse/<sub>/ is make_vectors1130's output for the raw runs, apart from the
    time it was converted."""
    have = DATA / "vectors/nokernel/usse" / sub if DATA else None
    if have is None or not have.is_dir():
        pytest.skip("SKIPPED, NOT PASSED: the 11.30 vectors are not in RESGX545_DATA")
    make_vectors1130.main(["x", str(DATA / "firmware-tasks"), str(tmp_path)])
    for want_file in sorted(have.glob("*.vec.json")):
        got = json.loads((tmp_path / sub / want_file.name).read_text())
        want = json.loads(want_file.read_text())
        got["run"].pop("converted"), want["run"].pop("converted")
        assert got == want, want_file.name
