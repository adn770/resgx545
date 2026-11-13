# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""load.install: the built library is put in place as a new file, never rewritten in place.

macOS caches a Mach-O's code signature per file: a library overwritten in place while (or
after) a process mapped it kills the next process that loads it (SIGKILL, Code Signature
Invalid). A new file renamed over the old name is safe."""
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import load  # noqa: E402


def test_install_creates_the_library(tmp_path):
    lib = tmp_path / "libpysgx.dylib"
    lib.write_bytes(b"new")
    dest = tmp_path / "out" / "pysgx.abi3.so"
    load.install(lib, dest)
    assert dest.read_bytes() == b"new"


def test_install_replaces_an_older_library_with_a_new_file(tmp_path):
    dest = tmp_path / "pysgx.abi3.so"
    dest.write_bytes(b"old")
    os.utime(dest, (1, 1))
    old_inode = dest.stat().st_ino
    keep = tmp_path / "keep"
    os.link(dest, keep)                # holds the old inode so it cannot be reused
    lib = tmp_path / "libpysgx.dylib"
    lib.write_bytes(b"new")
    load.install(lib, dest)
    assert dest.read_bytes() == b"new"
    assert dest.stat().st_ino != old_inode
    assert keep.read_bytes() == b"old"     # the old file was not written to
    assert sorted(p.name for p in tmp_path.iterdir()) == ["keep", "libpysgx.dylib",
                                                          "pysgx.abi3.so"]


def test_install_leaves_a_current_library_alone(tmp_path):
    lib = tmp_path / "libpysgx.dylib"
    lib.write_bytes(b"new")
    os.utime(lib, (1, 1))
    dest = tmp_path / "pysgx.abi3.so"
    dest.write_bytes(b"current")
    inode = dest.stat().st_ino
    load.install(lib, dest)
    assert dest.read_bytes() == b"current" and dest.stat().st_ino == inode


# load.cargo_target_dir: where cargo puts its builds, for every Python caller that runs a
# built tool or library (a worktree with its own CARGO_TARGET_DIR needs no target symlink).

def test_target_dir_is_the_repo_target_without_cargo_target_dir(monkeypatch):
    monkeypatch.delenv("CARGO_TARGET_DIR", raising=False)
    assert load.cargo_target_dir() == load.REPO / "target"


def test_target_dir_is_the_repo_target_when_cargo_target_dir_is_empty(monkeypatch):
    monkeypatch.setenv("CARGO_TARGET_DIR", "")
    assert load.cargo_target_dir() == load.REPO / "target"


def test_target_dir_is_an_absolute_cargo_target_dir(monkeypatch, tmp_path):
    monkeypatch.setenv("CARGO_TARGET_DIR", str(tmp_path / "build"))
    assert load.cargo_target_dir() == tmp_path / "build"


def test_target_dir_takes_a_relative_cargo_target_dir_from_the_repo_root(monkeypatch, tmp_path):
    """cargo runs with cwd = the repo root here, so it resolves a relative path from there."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("CARGO_TARGET_DIR", "build/mine")
    assert load.cargo_target_dir() == load.REPO / "build" / "mine"


def test_build_installs_from_and_into_the_target_dir(monkeypatch, tmp_path):
    """build() looks for the library and puts the module under cargo_target_dir()."""
    monkeypatch.setenv("CARGO_TARGET_DIR", str(tmp_path))
    (tmp_path / "debug").mkdir()
    (tmp_path / "debug" / "libpysgx.so").write_bytes(b"lib")
    ran = []

    class Done:
        returncode = 0
        stderr = ""

    monkeypatch.setattr(load.shutil, "which", lambda name: "/bin/" + name)
    monkeypatch.setattr(load.subprocess, "run", lambda *a, **k: ran.append(a) or Done())
    assert load.build() == tmp_path / "pysgx"
    assert (tmp_path / "pysgx" / "pysgx.abi3.so").read_bytes() == b"lib"
    assert ran


# the callers that run built tools ask cargo_target_dir(); none spells <repo>/target itself
CALLERS = ["tools/fwcutter/asmmap.py", "crates/pysgx/tests/test_pysgx.py",
           "tools/usse-dis/r2/pds_esil_check.py", "tools/usse-asm/test_tutorial.py",
           "tools/texture/test_tx_tool_assumptions.py", "crates/pysgx/load.py"]


def test_callers_take_the_target_dir_from_load():
    for rel in CALLERS:
        text = (load.REPO / rel).read_text()
        assert "cargo_target_dir()" in text, rel
        for spelled in ('"target" /', '"target/', "'target' /"):
            assert spelled not in text, (rel, spelled)


def test_asmmap_runs_sgx_asm_from_the_target_dir(monkeypatch, tmp_path):
    sys.path.insert(0, str(load.REPO / "tools" / "fwcutter"))
    import asmmap

    class Done:
        returncode = 0
        stderr = ""

    monkeypatch.setenv("CARGO_TARGET_DIR", str(tmp_path))
    monkeypatch.setattr(asmmap.subprocess, "run", lambda *a, **k: Done())
    assert asmmap.sgx_asm() == tmp_path / "debug" / "sgx-asm"
