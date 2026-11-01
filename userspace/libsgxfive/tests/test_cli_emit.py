# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""sgxfive-test --emit-scene on fill and copy, against the mock: the words of the built job
(after any pokes) as JSON for the pipeline simulator's scene vectors."""
from __future__ import annotations

import json
import os
import pathlib
import subprocess

import pytest

HERE = pathlib.Path(__file__).resolve().parent
TOOL = os.environ.get("SGXFIVE_TEST", str(HERE.parent / "build" / "sgxfive-test"))


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([TOOL, "--mock", *args], capture_output=True, text=True, timeout=30)


@pytest.fixture(scope="module", autouse=True)
def tool_exists():
    if not pathlib.Path(TOOL).exists():
        pytest.skip(f"{TOOL} not built (run make -C userspace/libsgxfive check)")


def emit(tmp_path, *args: str) -> dict:
    out = tmp_path / "scene.json"
    r = run(*args, "--emit-scene", str(out))
    assert r.returncode == 0, r.stdout + r.stderr
    return json.loads(out.read_text())


def words(seg: dict) -> list[int]:
    return [int(w, 16) for w in seg["dwords"]]


def test_a_fill_emits_its_command_pages_and_target(tmp_path):
    s = emit(tmp_path, "fill")
    assert s["kind"] == "fill"
    assert s["target"] == {"w": 64, "h": 32, "base": s["target"]["base"], "stride": 256, "pages": 3}
    x = [int(w, 16) for w in s["xfer"]]
    assert x[1] == 0x200 and x[2] == 0x3F800000 and x[3] == 3      # ISPBgObj, depth, ISPRender
    assert x[13] == 0x10001                                        # last tile (1, 1)
    assert x[14] == 0x80 and x[15] == 0x2E000000                   # PIXELBE, PDS_EXEC_BASE
    assert len(s["memory"]) == 3                                   # PDS, USE, stream pages
    assert all(len(m["dwords"]) == 1024 and m["source"] == "rebuilt" for m in s["memory"])
    lay = s["layout"]
    assert [m["base"] for m in s["memory"]] == [lay["pds_page"], lay["use_page"], lay["stream_page"]]
    bg = words(s["memory"][2])
    assert bg[1] >> 16 & 3 == 3                                    # the primary's attrs, 3 in [17:16]


def test_the_colour_reaches_the_fill_shader_in_the_use_page(tmp_path):
    use = words(emit(tmp_path, "fill", "--colour", "0x12345678")["memory"][1])
    other = words(emit(tmp_path, "fill", "--colour", "0xff336699")["memory"][1])
    assert use != other and use.count(0) > 900


def test_a_copy_emits_the_source_pattern_and_a_layer(tmp_path):
    s = emit(tmp_path, "copy")
    assert s["kind"] == "copy" and len(s["memory"]) == 4
    src = s["memory"][3]
    assert len(src["dwords"]) % 1024 == 0 and len(src["dwords"]) >= 2048
    assert src["base"] != s["target"]["base"]
    w = words(src)
    assert w[0] == 0xA5000000 and w[1] == 0xA5000101           # 0xa5 y x (x ^ y)
    assert int(s["xfer"][0], 16) >> 25 & 63 == 1               # one layer in the tag
    assert len(words(s["memory"][2])) == 1024


def test_pokes_are_applied_before_the_words_are_written(tmp_path):
    base = emit(tmp_path, "fill")
    s = emit(tmp_path, "fill", "--poke", "xfer:7^=0x2", "--poke", "bg:3=0x55")
    assert int(s["xfer"][7], 16) == int(base["xfer"][7], 16) ^ 2
    assert words(s["memory"][2])[3] == 0x55 and words(base["memory"][2])[3] == 0


def test_the_job_still_runs_and_the_option_is_refused_on_other_commands(tmp_path):
    r = run("fill", "--emit-scene", str(tmp_path / "s.json"))
    assert "job: ok" in r.stdout and "fill: ok" in r.stdout
    r = run("query", "--emit-scene", str(tmp_path / "t.json"))
    assert r.returncode != 0
