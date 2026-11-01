# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The IGT checkout's copy of libsgxfive is current.

The IGT tests live on the IGT fork, a separate repository. They build our ioctl layer,
transfer and render engines and assembled programs from a copy of these files in the fork's
lib/sgxfive/ directory. A change here without a re-sync would test stale code on the hardware.

Set RESGX545_IGT to an IGT checkout to run the check; without it the test is skipped. To
re-sync a stale file, copy it from userspace/libsgxfive/ (the paths in FILES) into the fork's
lib/sgxfive/ directory, flat (each file by its base name), and commit that on the fork.
"""
import os
import pathlib

import pytest

HERE = pathlib.Path(__file__).resolve().parent.parent
FILES = ["include/sgxfive.h", "include/sgxfive_xfer.h", "include/sgxfive_render.h",
         "include/sgxfive_poke.h", "src/dev.c", "src/xfer.c", "src/xfer_job.c", "src/render.c",
         "src/prog_asm.c", "src/prog_asm_gen.h", "src/tri_progs_gen.h"]


def stale_files(copy, src=HERE):
    """The files of FILES whose copy in `copy` is missing or differs from `src`."""
    stale = []
    for f in FILES:
        theirs = pathlib.Path(copy) / pathlib.Path(f).name
        if not theirs.is_file() or theirs.read_bytes() != (pathlib.Path(src) / f).read_bytes():
            stale.append(f)
    return stale


def test_igt_copy_is_current():
    igt = os.environ.get("RESGX545_IGT")
    if not igt:
        pytest.skip("RESGX545_IGT is not set: point it at the IGT checkout to check "
                    "its lib/sgxfive/ copy")
    copy = pathlib.Path(igt).expanduser() / "lib" / "sgxfive"
    stale = stale_files(copy)
    assert not stale, (f"{copy} is stale for {stale}: copy those files from "
                       f"{HERE} flat into lib/sgxfive/ of the IGT checkout and commit "
                       f"them there")


def _mirror(dst):
    dst.mkdir(parents=True, exist_ok=True)
    for f in FILES:
        (dst / pathlib.Path(f).name).write_bytes((HERE / f).read_bytes())


def test_copy_equal_is_not_stale(tmp_path):
    _mirror(tmp_path)
    assert stale_files(tmp_path) == []


def test_changed_file_is_named(tmp_path):
    _mirror(tmp_path)
    with open(tmp_path / "render.c", "ab") as fh:
        fh.write(b"/* edit */\n")
    assert stale_files(tmp_path) == ["src/render.c"]


def test_missing_file_is_named(tmp_path):
    _mirror(tmp_path)
    (tmp_path / "dev.c").unlink()
    assert stale_files(tmp_path) == ["src/dev.c"]
