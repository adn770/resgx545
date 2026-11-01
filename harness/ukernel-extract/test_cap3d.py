# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""cap3d.py: a 3D capture table's data (one <run>.tar.xz per run, capture3d_host.sh) unpacked
into the var/ layout capture3d.sh leaves, which diff3d.py, state3d.py and tiling3d.py read."""
import io
import pathlib
import tarfile

import pytest

import cap3d


def archive(path: pathlib.Path, files: dict[str, bytes]) -> None:
    with tarfile.open(path, "w:xz") as t:
        for name, data in files.items():
            info = tarfile.TarInfo(name)
            info.size = len(data)
            t.addfile(info, io.BytesIO(data))


def table(tmp_path) -> pathlib.Path:
    d = tmp_path / "render" / "draws-frames-pb"
    d.mkdir(parents=True)
    archive(d / "base.tar.xz", {"tri.out": b"done\n", "dump3d/kick00_in.bin": b"\0" * 8,
                                "dump3d/kick00/objects.txt": b""})
    archive(d / "pb_64k.tar.xz", {"tri.out": b"failed\n"})
    (d / "runs.txt").write_text("base: ok, 1 kicks\npb_64k: FAILED (1), 0 kicks\n")
    return d


def test_unpack_gives_one_directory_per_run(tmp_path):
    runs = cap3d.unpack(table(tmp_path), tmp_path / "var")
    assert [p.name for p in runs] == ["base", "pb_64k"]
    assert (tmp_path / "var/base/dump3d/kick00_in.bin").read_bytes() == b"\0" * 8
    assert (tmp_path / "var/pb_64k/tri.out").read_text() == "failed\n"


def test_unpack_again_keeps_what_is_unchanged(tmp_path):
    d = table(tmp_path)
    cap3d.unpack(d, tmp_path / "var")
    extra = tmp_path / "var/base/mine.txt"
    extra.write_text("kept")
    cap3d.unpack(d, tmp_path / "var")
    assert extra.exists()                       # same archive: not unpacked again
    archive(d / "base.tar.xz", {"tri.out": b"new\n"})
    cap3d.unpack(d, tmp_path / "var")
    assert not extra.exists() and (tmp_path / "var/base/tri.out").read_text() == "new\n"


def test_unpack_removes_the_run_of_a_vanished_archive(tmp_path):
    d = table(tmp_path)
    cap3d.unpack(d, tmp_path / "var")
    other = tmp_path / "var/not-a-run"
    other.mkdir()                               # no stamp: not ours, left alone
    (d / "pb_64k.tar.xz").unlink()
    runs = cap3d.unpack(d, tmp_path / "var")
    assert [p.name for p in runs] == ["base"]
    assert not (tmp_path / "var/pb_64k").exists() and other.exists()


def test_unpack_refuses_a_member_outside_its_run(tmp_path):
    d = tmp_path / "t"
    d.mkdir()
    archive(d / "bad.tar.xz", {"../escape.txt": b"x"})
    with pytest.raises(Exception):
        cap3d.unpack(d, tmp_path / "var")
    assert not (tmp_path / "escape.txt").exists()


def test_status_reads_the_host_lines(tmp_path):
    st = cap3d.status(table(tmp_path))
    assert st == {"base": ("ok", 1), "pb_64k": ("FAILED (1)", 0)}


def test_main_unpacks_and_lists(tmp_path, capsys):
    assert cap3d.main(["unpack", str(table(tmp_path)), str(tmp_path / "v")]) == 0
    assert "base" in capsys.readouterr().out and (tmp_path / "v/base").is_dir()
