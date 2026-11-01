# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Source-level checks of fakedrm.c and loader.c.

Both are 32-bit Linux LD_PRELOAD/dlopen programs that need the closed libraries, so they
cannot run in the test suite; these tests pin the fixes of the review findings in the text.
"""
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
FAKEDRM = (HERE / "fakedrm.c").read_text()
LOADER = (HERE / "loader.c").read_text()


def body(src: str, signature: str) -> str:
    start = src.index(signature)
    return src[start:src.index("\n}\n", start)]


def test_register_context_bounds_check_cannot_overflow():
    fn = body(FAKEDRM, "static void register_context")
    assert "pdoff + 4" not in fn
    assert "size >= 4 && pdoff <= size - 4" in fn


def test_devdata_file_is_not_used_after_fclose():
    fn = body(FAKEDRM, "static void load_devdata")
    after = fn[fn.index("fclose(f)"):]
    assert not re.search(r"\bf\b\s*\?", after)


def test_real_mmap_result_is_checked():
    fn = body(FAKEDRM, "static int new_obj")
    assert "MAP_FAILED" in fn


def test_directory_and_write_failures_are_reported():
    assert FAKEDRM.count("mkdir(") == 1       # only inside make_dir
    assert "strerror(errno)" in body(FAKEDRM, "static void make_dir")
    assert "strerror(errno)" in body(FAKEDRM, "static void write_file")


def test_fault_handler_uses_only_write():
    fn = body(LOADER, "static void on_fault")
    for banned in ("printf", "fputs", "backtrace", "dump_lib_maps", "malloc"):
        assert banned not in fn
    assert "put(" in fn and "_exit" in fn
    assert "write(2" in body(LOADER, "static void put(")


def test_getmiscinfo_reply_is_selected_by_one_knob():
    fn = body(FAKEDRM, "static void miscinfo_fill")
    assert 'getenv("MISC_REPLY")' in fn
    for reply in ('"zero"', '"plausible"', '"mismatched"', '"untouched"'):
        assert reply in fn
    assert 'getenv("MISC_ZERO")' in fn               # the older spelling of untouched
    assert "memset(&mi[2], 0" in fn                   # zero: every feature word written 0
    assert "~0x60218u" in fn                         # mismatched: every build option flipped
    assert re.search(r"unknown MISC_REPLY", fn)       # a typo is reported, not ignored
