# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Tests for bufclass.h: the buffer-class device fakedrm.c offers, so the closed GLES2 stack
can stream a YUV texture (IMG_texture_stream2) under the fake kernel.

The layouts are the GPL DDK's (services4/include/pvr_bridge.h, include4/servicesext.h:
BUFFER_INFO, PVRSRV_PIXEL_FORMAT); they are checked here through a small host program."""
import pathlib
import shutil
import subprocess

import pytest

HERE = pathlib.Path(__file__).resolve().parent
CC = shutil.which("cc") or shutil.which("gcc")

PROBE = r"""
#include <stdio.h>
#include <stdlib.h>
#include "bufclass.h"
int main(int argc, char **argv) {
    struct bc_config c;
    if (bc_parse(&c, argc > 1 ? argv[1] : 0)) { printf("error\n"); return 1; }
    uint32_t o[32] = { 0 };
    bc_info(o, &c);
    printf("info");
    for (int k = 1; k < 8; k++) printf(" %u", o[k]);
    printf(" name=%s\n", (const char *)(o + 8));
    uint32_t n = bc_size(&c);
    unsigned char *b = malloc(n);
    bc_pattern(&c, b);
    printf("size %u\nbytes", n);
    for (int k = 0; k < 8; k++) printf(" %02x", b[k]);
    printf("\nrow1");
    for (int k = 0; k < 4; k++) printf(" %02x", b[c.stride + k]);
    printf("\nlast %02x\n", b[n - 1]);
    return 0;
}
"""


@pytest.fixture(scope="module")
def probe(tmp_path_factory):
    if not CC:
        pytest.skip("no C compiler")
    d = tmp_path_factory.mktemp("bufclass")
    (d / "probe.c").write_text(PROBE)
    exe = d / "probe"
    subprocess.run([CC, "-Wall", "-Werror", "-I", str(HERE), str(d / "probe.c"), "-o", str(exe)],
                   check=True)
    return exe


def run(probe, arg=None):
    r = subprocess.run([str(probe)] + ([arg] if arg else []), capture_output=True, text=True)
    return dict(l.split(" ", 1) for l in r.stdout.strip().splitlines() if " " in l) | (
        {"error": "1"} if r.returncode else {})


def test_default_is_uyvy_64x64(probe):
    # BUFFER_INFO: count 1, device id, PVRSRV_PIXEL_FORMAT_UYVY (71), stride, w, h, flags
    o = run(probe)
    assert o["info"].split()[:7] == ["1", "0", "71", "128", "64", "64", "0"]
    assert o["info"].endswith("name=fakebc")
    assert o["size"] == str(128 * 64)


def test_packed_pattern(probe):
    # Y = 4x, U = 8y, V = 255 - 8y; UYVY bytes U Y0 V Y1, YUYV Y0 U Y1 V
    assert run(probe, "uyvy,64x64")["bytes"] == "00 00 ff 04 00 08 ff 0c"
    assert run(probe, "uyvy,64x64")["row1"] == "08 00 f7 04"
    assert run(probe, "yuyv,64x64")["bytes"] == "00 00 04 ff 08 00 0c ff"
    assert run(probe, "yuyv,32x16")["info"].split()[2:6] == ["69", "64", "32", "16"]


def test_nv12_planes(probe):
    # NV12 (64): the Y plane, then interleaved U, V at half resolution; stride = width
    o = run(probe, "nv12,16x8")
    assert o["info"].split()[2:6] == ["64", "16", "16", "8"]
    assert o["size"] == str(16 * 8 * 3 // 2)
    assert o["bytes"] == "00 04 08 0c 10 14 18 1c"
    assert o["last"] == "%02x" % (255 - 8 * 6)      # V of the last chroma row (y = 6)


def test_packed_code_variants(probe):
    # the GPL enum's other packed codes (include4/servicesext.h), same layouts: 73, 74
    # (PVRSRV_PIXEL_FORMAT_FOURCC_ORG_UYVY, _YUYV), 195, 196 (PVRSRV_PIXEL_FORMAT_C0_YUYV,
    # PVRSRV_PIXEL_FORMAT_C0_UYVY), 199, 200 (the C1 pair)
    for name, code, first in (("fuyvy", 73, "00 00 ff 04"), ("fyuyv", 74, "00 00 04 ff"),
                              ("c0yuyv", 195, "00 00 04 ff"), ("c0uyvy", 196, "00 00 ff 04"),
                              ("c1yuyv", 199, "00 00 04 ff"), ("c1uyvy", 200, "00 00 ff 04")):
        o = run(probe, f"{name},16x8")
        assert o["info"].split()[2] == str(code), name
        assert o["bytes"].startswith(first), name


def test_bad_configs(probe):
    for bad in ("rgb565,64x64", "uyvy,0x64", "uyvy,63x64", "nv12,16x7", "uyvy"):
        assert "error" in run(probe, bad), bad
