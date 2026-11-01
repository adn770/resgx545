# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""isp_scenes.py: render scenes with an image to reproduce (12.3)."""
from __future__ import annotations

import json
import os
import pathlib

import pytest

import isp_scenes as isc

HERE = pathlib.Path(__file__).resolve().parent
TOOL = os.environ.get("SGXFIVE_TEST", str(HERE.parent.parent / "userspace/libsgxfive/build/sgxfive-test"))


def test_a_size_is_inside_when_it_is_one_of_the_three_e606_ran():
    for w, h in [(64, 64), (128, 128), (256, 128)]:
        assert isc.open_questions(w, h) == [], (w, h)
    for w, h in [(64, 128), (128, 64), (256, 64), (32, 16), (512, 128), (512, 64), (128, 96), (64, 144),
                 (256, 256), (1024, 768), (4096, 4096), (100, 64)]:
        assert "Q240" in isc.open_questions(w, h), (w, h)


def test_four_macrotiles_a_row_from_640_by_480_add_the_tas_questions():
    assert isc.open_questions(1024, 768) == ["Q240", "Q100", "Q139", "Q086"]
    assert "Q139" not in isc.open_questions(256, 128)


def test_a_triangle_with_no_area_or_a_steep_depth_plane_names_its_question_from_its_vertices():
    flat = [(0, 0), (2560, 0), (0, 2560)]
    assert isc.plane_questions(flat, [0.5, 0.5, 0.5]) == []
    assert isc.plane_questions(flat, [0.0, 1.0, 0.0]) == ["Q200"], "gradient 0.1 per pixel"
    assert isc.plane_questions([(0, 0), (256, 256), (512, 512)], [0.1, 0.2, 0.3]) == ["Q230"]
    # 0.03 is the limit: a gradient just under it is unrefused (0.025 per pixel)
    assert isc.plane_questions(flat, [0.0, 0.25, 0.0]) == []


def test_a_vertex_depth_outside_zero_to_one_names_the_clamp_question():
    flat = [(0, 0), (2560, 0), (0, 2560)]
    assert isc.plane_questions(flat, [0.0, 0.0, 0.0]) == [] and isc.plane_questions(flat, [1.0] * 3) == []
    assert isc.plane_questions(flat, [-0.5] * 3) == ["Q241"]
    assert isc.plane_questions(flat, [1.5] * 3) == ["Q241"]


def test_the_fnv_of_the_first_triangle_image_is_the_hash_e148_recorded():
    # the 64 x 64 first triangle (8, 8), (56, 20), (20, 56), centre samples, top and left edges own the
    # tie: its image hashes to the first render of E148's 64 x 64 run
    v = [(8 * 256, 8 * 256), (56 * 256, 20 * 256), (20 * 256, 56 * 256)]
    px = []
    for y in range(64):
        for x in range(64):
            p = (256 * x + 128, 256 * y + 128)
            inside = True
            for i in range(3):
                a, b = v[i], v[(i + 1) % 3]
                dx, dy = b[0] - a[0], b[1] - a[1]
                e = dx * (p[1] - a[1]) - dy * (p[0] - a[0])
                if not (e > 0 or (e == 0 and (dy < 0 or (dy == 0 and dx > 0)))):
                    inside = False
            px.append("0xff00ff00" if inside else "0xff203040")
    assert px.count("0xff00ff00") == 1062
    assert isc.fnv64(px) == "0x99385a04ee01c585"
    assert isc.fnv64([]) == "0xcbf29ce484222325"


def test_the_hashes_of_a_target_sizes_output_come_in_render_order():
    import tempfile
    t = "#### 64x64\ntarget: 64x64 hash 0x1\ndiff: 0\ntarget: 64x64 hash 0x2\n#### 64x128\ntarget: 64x128 hash 0x3\n"
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write(t)
    try:
        assert isc.hashes(f.name) == {(64, 64): ["0x1", "0x2"], (64, 128): ["0x3"]}
    finally:
        os.unlink(f.name)


@pytest.mark.skipif(not os.path.exists(TOOL), reason="build userspace/libsgxfive first")
def test_a_first_triangle_scene_is_rebuilt_with_its_words_layout_and_no_dump_option(tmp_path):
    prog = tmp_path / "p.bin"
    prog.write_bytes(bytes(8))
    s = isc.ta_scenes.emit([TOOL], ["probe", "--tri", "pixel", "--width", "64", "--height", "64", str(prog)])
    sc = isc.scene_words(s, regs={"0x0480": "0x17100c"})
    assert sc["kind"] == "render" and sc["target"]["w"] == 64 and len(sc["cmd"]) == 26
    assert {m["role"] for m in sc["memory"]} == {"pdsv", "usev", "pdsp", "usep", "gen"}
    assert all(m["source"] == "rebuilt" for m in sc["memory"])
    assert sc["regs"] == {"0x0480": "0x17100c"}
    json.dumps(sc)
