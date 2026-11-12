# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""sgxfive-test --emit-scene on fill and copy, against the mock: the words of the built job
(after any pokes) as JSON for the pipeline simulator's scene vectors."""
from __future__ import annotations

import json
import os
import pathlib
import re
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


def probe_scene(tmp_path, *extra: str) -> dict:
    """`probe --tri pixel` (the pixel program a placeholder: it is not part of the TA's input)."""
    prog = tmp_path / "pix.bin"
    prog.write_bytes(bytes(8))
    out = tmp_path / "tri.json"
    r = run("probe", "--tri", "pixel", "--width", "128", "--height", "128", *extra,
            "--emit-scene", str(out), str(prog))
    assert r.returncode == 0, r.stdout + r.stderr
    return json.loads(out.read_text())


def test_a_triangle_probe_emits_the_pages_the_vdm_reads(tmp_path):
    s = probe_scene(tmp_path, "--vertices", "15")
    assert s["kind"] == "render" and s["target"]["w"] == 128 and s["target"]["h"] == 128
    assert [m["role"] for m in s["memory"]] == ["pdsv", "usev", "pdsp", "usep", "gen"]
    assert all(m["source"] == "rebuilt" for m in s["memory"])
    assert all(len(m["dwords"]) == 1024 for m in s["memory"][:4])
    assert len(s["memory"][4]["dwords"]) % 1024 == 0     # the gen region: one or more pages
    lay = s["layout"]
    assert [m["base"] for m in s["memory"]] == [lay[k] for k in ("pdsv", "usev", "pdsp", "usep", "gen")]
    assert len(s["cmd"]) == 26                       # the render command's words, version 1
    vdm = words(s["memory"][4])[:11]
    assert vdm[2] >> 30 == 2 and vdm[10] >> 30 == 3  # triangles; terminate
    assert vdm[4] == 0xF0000000 and vdm[5] == 0x3FFFFF


def test_an_odd_width_probe_emits_the_even_row_pitch(tmp_path):
    prog = tmp_path / "pix.bin"
    prog.write_bytes(bytes(8))
    out = tmp_path / "tri.json"
    r = run("probe", "--tri", "pixel", "--width", "33", "--height", "17", "--emit-scene",
            str(out), str(prog))
    assert r.returncode == 0, r.stdout + r.stderr
    t = json.loads(out.read_text())["target"]
    assert (t["w"], t["h"], t["stride"]) == (33, 17, 4 * 34)


def test_the_triangle_probe_words_follow_the_pokes(tmp_path):
    base = probe_scene(tmp_path)
    s = probe_scene(tmp_path, "--blk", "6=0x427f8000", "--vdm", "4=0x0")
    blk = lambda sc: words(sc["memory"][0])[0x100 // 4:0x100 // 4 + 18]
    assert blk(s)[6] == 0x427F8000 and blk(base)[6] != 0x427F8000
    assert words(s["memory"][4])[4] == 0 and words(base["memory"][4])[4] == 0xF0000000


def test_index_width_32_writes_word_indices_and_header_bit_25(tmp_path):
    """--index-width 32: the index list 0..N-1 as 32-bit words at the list's place (gen 0x200)
    and VDM word 2 bit 25 set; --vdm 2^=0x02000000 clears the bit again over the same list
    (the negative of the g-e4 positive test); 16 is the default list."""
    base = probe_scene(tmp_path, "--vertices", "15")
    s = probe_scene(tmp_path, "--vertices", "15", "--index-width", "32")
    g, g0 = words(s["memory"][4]), words(base["memory"][4])
    assert g[0x200 // 4:0x200 // 4 + 15] == list(range(15))
    assert g[2] == g0[2] | 0x02000000 and g[2] & 0x3FFFFF == 15
    assert g[0x100 // 4:0x100 // 4 + 60] == g0[0x100 // 4:0x100 // 4 + 60]
    n = probe_scene(tmp_path, "--vertices", "15", "--index-width", "32", "--vdm", "2^=0x02000000")
    gn = words(n["memory"][4])
    assert gn[2] == g0[2] and gn[0x200 // 4:0x200 // 4 + 15] == list(range(15))
    assert words(probe_scene(tmp_path, "--vertices", "15", "--index-width", "16")["memory"][4]) == g0


def test_index_width_is_checked(tmp_path):
    prog = tmp_path / "pix.bin"
    prog.write_bytes(bytes(8))
    for args in (["--tri", "pixel", "--index-width", "8"], ["--tri", "pixel", "--index-width", "x"],
                 ["--index-width", "32"],
                 ["--tri", "pixel", "--vertices", "12", "--obj2", "6", "--index-width", "32"],
                 ["--tri", "pixel", "--vertices", "129", "--index-width", "32"]):
        r = run("probe", *args, str(prog))
        assert r.returncode == 2, (args, r.stdout + r.stderr)
    r = run("probe", "--tri", "pixel", "--vertices", "15", "--index-width", "32", str(prog))
    assert re.search(r"^probe pix: tri 64x64 \(15 vertices, 32-bit indices\)", r.stdout, re.M), \
        r.stdout


def test_emit_scene_on_a_probe_without_a_triangle_is_refused(tmp_path):
    prog = tmp_path / "p.bin"
    prog.write_bytes(bytes(8))
    r = run("probe", str(prog), "--emit-scene", str(tmp_path / "x.json"))
    assert r.returncode != 0
