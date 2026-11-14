# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""transfer_scenes.py: the raw.txt of a fill or copy sweep as scene vectors."""
from __future__ import annotations

import json
import pathlib
import subprocess

import pytest

import transfer_scenes as ts

RAW = """=== case baseline
$ sudo -n ./regtimeline 0 0 0x0494-0x04b4 -- ./sgxfive-test fill
programs asm
job: ok
target: 64x32 hash 0xb60c6095080bd325
diff: 0 of 2048 pixels
outside: 0 dwords
fill: ok, 64x32 at (0, 0), stride 256, colour 0xff336699
--- rc 0 0.276 s
=== case xfer:0^=0x2
$ sudo -n ./regtimeline 0 0 0x0494-0x04b4 -- ./sgxfive-test fill --poke 'xfer:0^=0x2'
programs asm
job: failed: job faulted, context lost (Input/output error)
target: 64x32 hash 0xfc8ce806207f8325
diff: 2048 of 2048 pixels, first (0, 0) 0xdeadbeef expected 0xff336699
outside: 0 dwords
--- rc 1 0.493 s
=== case xfer:4^=0x1
$ sudo -n ./regtimeline 0 0 0x0494-0x04b4 -- ./sgxfive-test fill --poke 'xfer:4^=0x1'
programs asm
job: rejected (Invalid argument)
--- rc 1 0.1 s
=== case xfer:7^=0x1
$ sudo -n ./regtimeline 0 0 0x0494-0x04b4 -- ./sgxfive-test fill --poke 'xfer:7^=0x1' --poke 'bg:3=0x5'
programs asm
job: ok
target: 64x32 hash 0x1111111111111111
diff: 1024 of 2048 pixels, first (0, 0) 0xdeadbeef expected 0xff336699
outside: 3 dwords
--- rc 1 0.3 s
=== case xfer:9^=0x10
$ sudo -n ./regtimeline 0 0 0x0494-0x04b4 -- ./sgxfive-test fill --poke 'xfer:9^=0x10'
programs asm
job: failed: job hung, context lost (Connection timed out)
target: 64x32 hash 0xfc8ce806207f8325
diff: 2048 of 2048 pixels, first (0, 0) 0xdeadbeef expected 0xff336699
outside: 0 dwords
--- rc 1 0.5 s
"""


def test_fnv_hash_of_the_fill_and_copy_references_is_the_recorded_baseline():
    assert ts.fnv64([0xFF336699] * 2048) == 0xB60C6095080BD325
    assert ts.fnv64(ts.copy_reference(64, 32, 64, 0, 0, plain=True)) == 0x9B1C0BE484AC0D25


def test_parse_raw_reads_the_command_the_outcome_and_the_result_lines():
    cs = ts.parse_raw(RAW)
    assert [c.name for c in cs] == ["baseline", "xfer:0^=0x2", "xfer:4^=0x1", "xfer:7^=0x1", "xfer:9^=0x10"]
    b = cs[0]
    assert (b.cmd, b.args, b.job, b.hash, b.diff, b.outside) == ("fill", [], "ok", 0xB60C6095080BD325, 0, 0)
    assert cs[1].job == "fault" and cs[1].args == ["--poke", "xfer:0^=0x2"]
    assert cs[2].job == "rejected" and cs[2].hash is None
    assert cs[3].args == ["--poke", "xfer:7^=0x1", "--poke", "bg:3=0x5"]
    assert cs[3].diff == 1024 and cs[3].outside == 3
    assert cs[4].job == "hang"


def test_expect_is_the_image_hash_for_a_completed_job_and_the_outcome_for_a_failed_one():
    cs = ts.parse_raw(RAW)
    assert ts.expect_of(cs[3]) == {"image": {"hash": "0x1111111111111111"}, "outside": 3}
    assert ts.expect_of(cs[1]) == {"outcome": "fault"}
    assert ts.expect_of(cs[4]) == {"outcome": "hang"}
    assert ts.expect_of(cs[2]) is None  # never reached the GPU: not a hardware result


def test_the_baseline_expect_is_the_whole_reference_image_because_its_hash_is_recomputed():
    cs = ts.parse_raw(RAW)
    e = ts.expect_of(cs[0], reference=[0xFF336699] * 2048)
    assert e["image"]["hash"] == "0xb60c6095080bd325" and e["image"]["o0"] == "0xff336699"
    with pytest.raises(ValueError):
        ts.expect_of(cs[0], reference=[0] * 2048)  # a reference that is not the recorded image


def test_split_pokes_separates_the_poke_arguments_from_the_job_options():
    base, pokes = ts.split_pokes(["--every-value", "--poke", "xfer:7^=0x1", "--poke", "bg:3=0x5"])
    assert base == ["--every-value"] and pokes == ["xfer:7^=0x1", "bg:3=0x5"]


def test_delta_keeps_the_changed_command_words_and_memory_dwords_only():
    base = {"xfer": ["0x0", "0x200", "0x3"], "memory": [{"base": "0x1000", "dwords": ["0x1", "0x2", "0x3"]}]}
    scene = {"xfer": ["0x0", "0x201", "0x3"], "memory": [{"base": "0x1000", "dwords": ["0x1", "0x2", "0x9"]}]}
    d = ts.delta(base, scene)
    assert d == {"xfer": {"1": "0x201"}, "memory": [{"base": "0x1000", "at": {"2": "0x9"}}]}
    assert ts.delta(base, base) == {}


def test_repeated_cases_that_differ_become_an_either_expectation():
    raw = RAW.replace("=== case xfer:9^=0x10", "=== case xfer:9^=0x10").rstrip() + "\n" + (
        "=== case xfer:9^=0x10\n$ sudo -n ./x -- ./sgxfive-test fill --poke 'xfer:9^=0x10'\n"
        "programs asm\njob: ok\ntarget: 64x32 hash 0xb60c6095080bd325\ndiff: 0 of 2048 pixels\n"
        "outside: 0 dwords\n--- rc 0 0.2 s\n")
    cs = [c for c in ts.parse_raw(raw) if c.name == "xfer:9^=0x10"]
    e = ts.expect_many(cs)
    assert e["outcome"] == "either" and len(e["either"]) == 2
    assert {"outcome": "hang"} in e["either"]
    # the same result twice is just that result
    assert ts.expect_many([cs[0], cs[0]]) == {"outcome": "hang"}


def test_the_generator_runs_the_tool_per_case_and_writes_a_base_with_deltas(tmp_path):
    tool = tmp_path / "tool.py"
    tool.write_text(
        "#!/usr/bin/env python3\nimport json, sys\na = sys.argv[1:]\nout = a[a.index('--emit-scene') + 1]\n"
        "x = ['0x0', '0x200']\nif any(p == 'xfer:1^=0x1' for p in a):\n    x[1] = '0x201'\n"
        "json.dump({'kind': a[1], 'target': {'w': 64, 'h': 32}, 'xfer': x, 'layout': {}, "
        "'memory': [{'base': '0x10', 'dwords': ['0x0', '0x0']}]}, open(out, 'w'))\n")
    tool.chmod(0o755)
    raw = RAW.replace("xfer:0^=0x2", "xfer:1^=0x1")
    f = ts.build_file(raw, [str(tool), "--mock"], "demo", "transfer/x/y", "raw.txt", "00")
    assert f["format"] == "sgx545-scene-vectors" and len(f["bases"]) == 1
    ids = [s["id"] for s in f["scenes"]]
    assert ids[0] == "demo:baseline" and "demo:xfer:1^=0x1" in ids
    assert not any("xfer:4" in i for i in ids), "rejected cases are excluded"
    assert [e["case"] for e in f["excluded"]] == ["xfer:4^=0x1"]
    s1 = next(s for s in f["scenes"] if s["id"] == "demo:xfer:1^=0x1")
    assert s1["delta"] == {"xfer": {"1": "0x201"}} and s1["expect"] == {
        "outcome": "fault", "refuse": ["Q003", "Q011", "Q076", "Q206", "Q207"]}


def test_a_poked_scene_names_the_questions_its_poked_words_are_open_under(tmp_path):
    assert ts.refuse_of(["xfer:4^=0x1"]) == ["Q003", "Q011", "Q076", "Q206", "Q207"]
    assert ts.refuse_of(["bg:3=0x5", "xfer:7^=0x1"]) == [
        "Q003", "Q011", "Q066", "Q076", "Q200", "Q206", "Q207"]
    assert ts.refuse_of(["pds:pixev:7=0"]) == ["Q003", "Q074", "Q206", "Q207"]
    assert ts.refuse_of(["pds:prim:6^=0x2000"]) == ["Q003", "Q076", "Q180", "Q206", "Q207", "Q300"]
    assert ts.refuse_of(["tex:1^=0x20"]) == ["Q003", "Q076", "Q206", "Q300"]
    assert ts.refuse_of([]) == [], "an unpoked job is not one a question keeps open"
    # a word of a space the table does not know is not refused under a guess
    assert ts.refuse_of(["kreg:5=1"]) == ["Q206"]


def test_the_scene_of_a_poked_case_carries_the_refusal_in_its_expect(tmp_path):
    tool = tmp_path / "tool.py"
    tool.write_text(
        "#!/usr/bin/env python3\nimport json, sys\na = sys.argv[1:]\nout = a[a.index('--emit-scene') + 1]\n"
        "json.dump({'kind': a[1], 'target': {'w': 64, 'h': 32}, 'xfer': ['0x0'], 'layout': {}, "
        "'memory': [{'base': '0x10', 'dwords': ['0x0']}]}, open(out, 'w'))\n")
    tool.chmod(0o755)
    f = ts.build_file(RAW, [str(tool), "--mock"], "demo", "transfer/x/y", "raw.txt", "00")
    s = {x["id"]: x for x in f["scenes"]}
    assert "refuse" not in s["demo:baseline"]["expect"]
    assert s["demo:xfer:9^=0x10"]["expect"]["refuse"] == ["Q003", "Q011", "Q076", "Q206", "Q207"]


KREG_RAW = """=== case baseline
$ d=/sys/kernel/debug/dri/0/sgx; put() { f=$1; shift; echo "$@"; }; sudo -n ./regtimeline 0 0 0x0494-0x04b4 -- ./sgxfive-test copy --ramp 3; rc=$?; exit "$rc"
job: ok
target: 64x32 hash 0xb60c6095080bd325
diff: 0 of 2048 pixels
outside: 0 dwords
=== case kreg:0x0810^=0x1
$ d=/sys/kernel/debug/dri/0/sgx; put() { f=$1; shift; echo "$@"; }; put kreg '0x0810^=0x1' || die 'x'; sudo -n ./regtimeline 0 0 0x0494-0x04b4 -- ./sgxfive-test copy --ramp 3; rc=$?; put kreg "0x0810=$was" || echo x >&2; exit "$rc"
job: ok
target: 64x32 hash 0xb60c6095080bd325
diff: 0 of 2048 pixels
outside: 0 dwords
"""


def test_a_kreg_case_wraps_the_job_in_a_shell_tail_that_is_not_part_of_its_arguments():
    base, kreg = ts.parse_raw(KREG_RAW)
    assert (base.cmd, base.args, base.kreg) == ("copy", ["--ramp", "3"], False)
    assert (kreg.cmd, kreg.args, kreg.kreg) == ("copy", ["--ramp", "3"], True)
