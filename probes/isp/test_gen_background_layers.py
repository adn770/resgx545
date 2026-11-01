# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""gen_background_layers.py: the two-layer background object of background-layers.toml."""
from __future__ import annotations

import pathlib
import subprocess
import tomllib

import gen_background_layers as g

HERE = pathlib.Path(__file__).resolve().parent
ONE = 0x3f800000


def _bg(pokes: list) -> dict:
    return {int(p.split(":")[1].split("=")[0]): int(p.split("=")[1], 16)
            for p in pokes if p.startswith("bg:")}


def test_vertex_major_object():
    """Dwords 3-14 the coordinates, each vertex's layer A (identity) then B (mirrored in u),
    15 zero, 16 the format word, 17-20 zero, 21-28 the 8x4 copy's vertices."""
    bg = _bg(g.pokes("vertex", 0x404, 2))
    assert [bg[i] for i in range(3, 15)] == [0, 0, ONE, 0, ONE, 0, 0, 0, 0, ONE, ONE, ONE]
    assert bg[15] == 0 and bg[16] == 0x404 and all(bg[i] == 0 for i in range(17, 21))
    assert [bg[i] for i in range(21, 29)] == g.VERTS
    assert sorted(bg) == list(range(3, 29))


def test_layer_major_object():
    bg = _bg(g.pokes("layer", 0x404, 1))
    assert [bg[i] for i in range(3, 15)] == [0, 0, ONE, 0, 0, ONE, ONE, 0, 0, 0, ONE, ONE]


def test_tag_and_fetch_set():
    p = g.pokes("vertex", 0x404, 2)
    assert "xfer:0^=0x06000000" in p and "pds:prim:4=0x40012002" in p
    p = g.pokes("vertex", 0x404, 1, tag=False)
    assert not any(x.startswith("xfer:") for x in p) and "pds:prim:4=0x40012001" in p


def test_cases_cover_the_set():
    names = [c.name for c in g.RUNS]
    assert len(names) == len(set(names))
    assert "vertex-404-set2" in names and "layer-202-set1" in names
    assert "vertex-404-set2-tag2" in names and "vertex-ffffffff-set2" in names


def test_the_script_is_current_and_parses():
    script = HERE / "templates" / "background-layers.sh"
    assert script.read_text() == g.script(), "run probes/isp/gen_background_layers.py"
    assert subprocess.run(["sh", "-n", str(script)], capture_output=True).returncode == 0
    assert script.read_text().count("\nrun ") == len(g.RUNS)


def test_the_table_names_its_script():
    spec = tomllib.loads((HERE / "background-layers.toml").read_text())
    assert spec["name"] == "isp-background-layers" and spec["script"] == "background-layers.sh"


def test_a_failing_case_does_not_fail_the_script(tmp_path):
    # nothing is judged here: each case's status is kept in the output and the run goes on
    fake = tmp_path / "sgxfive-test"
    fake.write_text("#!/bin/sh\necho row 1: 0xa5000000\nexit 1\n")
    fake.chmod(0o755)
    r = subprocess.run(["sh", "-c", g.script()], capture_output=True, text=True,
                       env={"SGXFIVE_TEST": str(fake), "PATH": "/usr/bin:/bin"})
    assert r.returncode == 0
    assert r.stdout.count("status 1") == len(g.RUNS)
