# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Tests for the capture templates captures/firmware/templates/."""
import pathlib
import subprocess

TEMPLATES = (pathlib.Path(__file__).resolve().parents[2] / "captures" / "firmware"
             / "templates")


def run(script, cwd, **env):
    import os
    return subprocess.run(["sh", str(TEMPLATES / script)], cwd=cwd, capture_output=True,
                          text=True, env=dict(os.environ, **env))


def test_templates_parse():
    for name in ("layout.sh", "images.sh"):
        assert subprocess.run(["sh", "-n", str(TEMPLATES / name)]).returncode == 0


def test_layout_names_its_host_requirements_and_clears_its_stage():
    text = (TEMPLATES / "layout.sh").read_text()
    assert "gcc -m32" in text.split("set -eu")[0]          # said in the header comment
    assert 'rm -rf "$stage"' in text


def test_layout_fails_clearly_without_the_libraries(tmp_path):
    r = run("layout.sh", tmp_path, RESGX545_CDV_LIBS=str(tmp_path / "none"), OUT=str(tmp_path))
    assert r.returncode == 1 and "libsrv_um.so.1.7.862890 not found" in r.stderr


def test_images_fails_clearly_without_fwcutter(tmp_path):
    r = run("images.sh", tmp_path, RESGX545_CDV_LIBS=str(tmp_path), OUT=str(tmp_path))
    assert r.returncode == 1 and "fwcutter.py is not in the work directory" in r.stderr


def test_images_tolerates_an_existing_output_directory():
    assert "out.mkdir(exist_ok=True)" in (TEMPLATES / "images.sh").read_text()
