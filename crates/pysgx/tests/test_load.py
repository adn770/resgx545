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
