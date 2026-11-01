# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The 3D capture tables written from the variation lists (cap3d_tables.py), and the host
script they run (capture3d_host.sh)."""
import pathlib
import re
import subprocess
import sys
import tomllib

import pytest

import cap3d_tables as ct

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tools" / "campaign"))


def test_every_variation_list_has_one_table():
    lists = {p.name for p in HERE.glob("*3d.txt")}
    assert sorted(t[2] for t in ct.TABLES) == sorted(lists)
    names = [(u, f) for u, f, *_ in ct.TABLES]
    assert len(set(names)) == len(names)


def test_a_table_is_a_private_capture_named_after_its_path():
    import campaign
    for rel, text in ct.render().items():
        if not rel.endswith(".toml"):
            continue
        spec = tomllib.loads(text)
        m = re.fullmatch(r"captures/([^/]+)/([^/]+)\.toml", rel)
        assert m and m.group(1) in campaign.UNITS
        assert spec["kind"] == "capture" and spec["name"] == f"{m.group(1)}-{m.group(2)}"
        assert spec["script"] == f"{m.group(2)}.sh" and spec["host"] == "build"
        assert all(len(ln) <= 100 for ln in text.splitlines())


def test_a_tables_files_exist_and_cover_every_include():
    for _, _, lst, *_ in ct.TABLES:
        fs = ct.files(lst)
        assert all((ROOT / f).is_file() for f in fs), [f for f in fs if not (ROOT / f).is_file()]
        names = {pathlib.Path(f).name for f in fs}
        for src in [n for n in names if n.endswith((".c", ".h"))]:
            for inc in re.findall(r'#include "([^"]+)"', (HERE / src).read_text()):
                assert inc in names, (src, inc)


def test_every_list_naming_shader_files_brings_their_generator():
    gen = f"{ct.HARNESS}/gen_shaders3d.py"
    for _, _, lst, *_ in ct.TABLES:
        assert (gen in ct.files(lst)) == ("shaders/" in (HERE / lst).read_text()), lst
    assert gen in ct.files("isp3d.txt") and gen in ct.files("inputs3d.txt")
    assert gen not in ct.files("track3d.txt")
    assert gen in ct.files("x.txt", "a fsfile=shaders/a.frag\n")


def test_the_template_runs_the_host_script_with_its_list():
    sh = ct.render()["captures/render/templates/draws-frames-pb.sh"]
    assert sh.rstrip().splitlines()[-1] == "exec sh ./capture3d_host.sh track3d.txt"


def test_open_lists_the_never_captured_runs_of_track3d_only():
    out = ct.render()
    spec = tomllib.loads(out["captures/render/draws-frames-pb.toml"])
    assert len(spec["open"]) == 28 and "base" not in spec["open"]
    assert spec["open"][0] == "draws2" and spec["open"][-1] == "pbmax_512k"
    assert "open" not in tomllib.loads(out["captures/render/state-variations.toml"])


def test_runs_skip_comments_and_blank_lines():
    assert ct.runs("# c\n\nbase\nx  a=1 b\n  # d\n") == ["base", "x"]


def test_check_finds_a_stale_table(tmp_path):
    (tmp_path / ct.HARNESS).mkdir(parents=True)
    for _, _, lst, *_ in ct.TABLES:
        (tmp_path / ct.HARNESS / lst).write_text((HERE / lst).read_text())
    assert ct.main([str(tmp_path)]) == 0 and ct.main(["--check", str(tmp_path)]) == 0
    p = tmp_path / "captures/ta/target-sizes.toml"
    p.write_text(p.read_text() + "# edited\n")
    assert ct.main(["--check", str(tmp_path)]) == 1


@pytest.mark.skipif(not (ROOT / "captures" / "render").is_dir(), reason="no 3D tables here")
def test_the_tree_holds_the_tables_as_written():
    assert ct.main(["--check", str(ROOT)]) == 0


def test_the_host_script_parses_and_builds_what_capture3d_runs():
    sh = HERE / "capture3d_host.sh"
    subprocess.run(["sh", "-n", str(sh)], check=True)
    text = sh.read_text()
    for out in ("fakedrm.so", "libpvrFAKEWSEGL.so", "-o loader", "-o tri ", "-o tri1 "):
        assert out in text
    assert "-lm" in text                     # tri.c rounds with lroundf
    assert "sh ./capture3d.sh" in text and ".tar.xz" in text
    assert '[ -n "$keep" ]' in text           # no archive of an empty keep list
