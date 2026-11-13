# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""sgxfive-test tri / probe --tri --bg-layer against the mock (Q190's layered background).

The kernel builds the render's background object from the tag's one layer when debugfs
render_bg_layer is on, and checks render_bg_src, the source the user's PDS primary samples. The
tool never writes either knob (the session kit writes and restores them as `dbg:` row words);
it reads them (SGXFIVE_DEBUGFS, or --mock-knob NAME=V on the mock), maps a W x H source at
render_bg_src in the render's VM, gives the background the copy's primary and one attribute row,
and checks every background pixel against the texel of its own position. It refuses, exit 2
before any device call, whatever would make a row unreadable: the option with the knob off, the
knob on without the option, an unusable source address, and the options the layer does not
combine with. Run through `make check`, which builds the binary and sets SGXFIVE_TEST."""
from __future__ import annotations

import os
import pathlib
import re
import subprocess
import sys

import pytest

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent
TOOL = os.environ.get("SGXFIVE_TEST", str(HERE.parent / "build" / "sgxfive-test"))
SRC = "0x3e800000"
KNOBS = ["--mock-knob", "render_bg_layer=1", "--mock-knob", f"render_bg_src={SRC}"]
PHAS = "phas #0, #0, pixel, end, parallel\n"


def run(*args: str, env: dict | None = None) -> subprocess.CompletedProcess[str]:
    e = {**os.environ, **(env or {})}
    return subprocess.run([TOOL, *args], capture_output=True, text=True, timeout=60, env=e)


@pytest.fixture(scope="module", autouse=True)
def tool_exists():
    if not pathlib.Path(TOOL).exists():
        pytest.skip(f"{TOOL} not built (run make -C userspace/libsgxfive check)")


def assemble(tmp_path: pathlib.Path, name: str, source: str, isa: str = "usse") -> pathlib.Path:
    sys.path.insert(0, str(ROOT / "tools" / "fwcutter"))
    import ours  # builds the assemblers on demand
    out = tmp_path / f"{name}.bin"
    subprocess.run([str(ours._tool(isa)), "-o", str(out), "-"], input=source.encode(),
                   capture_output=True, check=True)
    return out


def test_tri_bg_layer_every_background_pixel_is_its_texel():
    r = run("--mock", *KNOBS, "tri", "--bg-layer", "--pixels")
    assert r.returncode == 0, r.stdout + r.stderr
    assert f"bg-layer: source {SRC} 64x64 RGBA8888, knob Y\n" in r.stdout, r.stdout
    m = re.search(r"^tri 64x64 #1: (\d+) triangle, (\d+) background, 0 other; wrong 0 inside, "
                  r"0 outside, 0 at edges; \d+ if flipped; guard 0; (\d+) layer texels in place, "
                  r"0 elsewhere, 0 not a texel$", r.stdout, re.M)
    assert m, r.stdout
    assert int(m[1]) + int(m[2]) == 4096 and m[2] == m[3]
    assert "diff: 0 of 4096 pixels" in r.stdout
    # a background pixel is the texel of its own position: check byte, y, x
    rows = {int(a): b.split() for a, b in re.findall(r"^row (\d+):(.*)$", r.stdout, re.M)}
    x, y = 0, 0
    assert rows[y][x] == f"0x{((x ^ y ^ 0xa5) & 0xff) << 24 | y << 12 | x:08x}"
    x, y = 60, 63
    assert rows[y][x] == f"0x{((x ^ y ^ 0xa5) & 0xff) << 24 | y << 12 | x:08x}"


@pytest.mark.parametrize("size", [(128, 64), (100, 60), (32, 16)])
def test_tri_bg_layer_sizes(size):
    w, h = size
    r = run("--mock", *KNOBS, "tri", "--bg-layer", "--width", str(w), "--height", str(h))
    assert r.returncode == 0, r.stdout + r.stderr
    assert f"{w}x{h} RGBA8888, knob Y" in r.stdout
    assert "0 elsewhere, 0 not a texel" in r.stdout


def test_without_the_option_nothing_changes():
    r = run("--mock", "tri")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "bg-layer" not in r.stdout and "layer texels" not in r.stdout
    assert "tri 64x64 #1: 1098 triangle, 2998 background, 0 other" in r.stdout


def test_option_with_the_knob_off_is_refused():
    r = run("--mock", "tri", "--bg-layer")
    assert r.returncode == 2, r.stdout + r.stderr
    assert "usage:" in r.stderr and "render_bg_layer" in r.stderr
    assert r.stdout == ""
    r = run("--mock", "--mock-knob", "render_bg_layer=0", "--mock-knob", f"render_bg_src={SRC}",
            "tri", "--bg-layer")
    assert r.returncode == 2 and "render_bg_layer" in r.stderr


def test_knob_on_without_the_option_is_refused():
    r = run("--mock", *KNOBS, "tri")
    assert r.returncode == 2, r.stdout + r.stderr
    assert "usage:" in r.stderr and "--bg-layer" in r.stderr
    assert r.stdout == ""


@pytest.mark.parametrize("src", ["0", "0x3e800004", "0x3e800800", "0x100000", "0x1ffffff000",
                                 "0xfffff000"])
def test_bad_source_address_is_refused(src):
    r = run("--mock", "--mock-knob", "render_bg_layer=1", "--mock-knob", f"render_bg_src={src}",
            "tri", "--bg-layer")
    assert r.returncode == 2, (src, r.stdout + r.stderr)
    assert "usage:" in r.stderr and "render_bg_src" in r.stderr, r.stderr
    assert r.stdout == ""


@pytest.mark.parametrize("args", [["--tri-full"], ["--aa4"], ["--ctx2"], ["--geometry", "1", "-n", "2"],
                                  ["--fault"], ["-n", "2"], ["--width", "4096"],
                                  ["--height", "4096"]])
def test_refused_combinations(args):
    r = run("--mock", *KNOBS, "tri", "--bg-layer", *args)
    assert r.returncode == 2, (args, r.stdout + r.stderr)
    assert "usage:" in r.stderr and "--bg-layer" in r.stderr, r.stderr
    assert r.stdout == ""


def test_source_past_the_heap_end_is_refused():
    # the general heap ends at 0xf0000000 - 0x1000 (rev1): a 4095 x 4095 source at 0xef000000
    # needs 64 MiB
    r = run("--mock", "--mock-knob", "render_bg_layer=1", "--mock-knob",
            "render_bg_src=0xef000000", "tri", "--bg-layer", "--width", "4095", "--height",
            "4095")
    assert r.returncode == 2, r.stdout + r.stderr
    assert "render_bg_src" in r.stderr


def test_source_over_the_renders_own_pages_is_rc_1():
    # the tool maps the source first, at the knob's address; the render's first pages are the
    # general heap's first, so a source there overlaps them: a VM_MAP failure, rc 1, no image
    r = run("--mock", "--mock-knob", "render_bg_layer=1", "--mock-knob",
            "render_bg_src=0x3e000000", "tri", "--bg-layer")
    assert r.returncode == 1, r.stdout + r.stderr
    assert "File exists" in r.stderr and "layer texels" not in r.stdout


def test_mock_knob_needs_the_mock():
    r = run("--mock-knob", "render_bg_layer=1", "tri")
    assert r.returncode == 2, r.stdout + r.stderr
    r = run("--mock", "--mock-knob", "render_bg_layer", "tri")        # no value
    assert r.returncode == 2, r.stdout + r.stderr
    r = run("--mock", "--mock-knob", "render_bg_layer=maybe", "tri")
    assert r.returncode == 2, r.stdout + r.stderr


def test_unknown_mock_knob_is_accepted_with_a_line():
    r = run("--mock", "--mock-knob", "render_tail_room=0x100", "tri")
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stderr.count("mock: debugfs render_tail_room not modelled") == 1, r.stderr


def test_the_knobs_are_read_from_debugfs_files(tmp_path):
    (tmp_path / "render_bg_layer").write_text("Y\n")
    (tmp_path / "render_bg_src").write_text(f"{SRC}\n")
    env = {"SGXFIVE_DEBUGFS": str(tmp_path)}
    r = run("--mock", "tri", "--bg-layer", env=env)
    assert r.returncode == 0, r.stdout + r.stderr
    assert f"bg-layer: source {SRC} 64x64 RGBA8888, knob Y" in r.stdout
    assert run("--mock", "tri", env=env).returncode == 2            # knob Y, no option
    (tmp_path / "render_bg_layer").write_text("N\n")
    assert run("--mock", "tri", "--bg-layer", env=env).returncode == 2
    assert run("--mock", "tri", env=env).returncode == 0
    # an older module has neither file: N and 0
    empty = tmp_path / "old"
    empty.mkdir()
    r = run("--mock", "tri", "--bg-layer", env={"SGXFIVE_DEBUGFS": str(empty)})
    assert r.returncode == 2 and "render_bg_layer" in r.stderr
    assert run("--mock", "tri", env={"SGXFIVE_DEBUGFS": str(empty)}).returncode == 0


def test_the_tool_never_writes_the_knobs(tmp_path):
    (tmp_path / "render_bg_layer").write_text("Y\n")
    (tmp_path / "render_bg_src").write_text(f"{SRC}\n")
    before = {p.name: p.read_text() for p in tmp_path.iterdir()}
    run("--mock", "tri", "--bg-layer", env={"SGXFIVE_DEBUGFS": str(tmp_path)})
    assert {p.name: p.read_text() for p in tmp_path.iterdir()} == before


def test_probe_tri_bg_layer(tmp_path):
    pix = assemble(tmp_path, "pix", PHAS + "mov.skipinv.end o0, pa0\n")
    r = run("--mock", *KNOBS, "probe", "--tri", "pixel", "--bg-layer", str(pix))
    assert r.returncode == 0, r.stdout + r.stderr
    assert f"bg-layer: source {SRC} 64x64 RGBA8888, knob Y\n" in r.stdout, r.stdout
    # the same refusals
    r = run("--mock", "probe", "--tri", "pixel", "--bg-layer", str(pix))
    assert r.returncode == 2 and "render_bg_layer" in r.stderr
    r = run("--mock", *KNOBS, "probe", "--tri", "pixel", str(pix))
    assert r.returncode == 2 and "--bg-layer" in r.stderr
    r = run("--mock", *KNOBS, "probe", "--tri", "pixel", "--bg-layer", "--tri-full", str(pix))
    assert r.returncode == 2 and "usage:" in r.stderr
    r = run("--mock", *KNOBS, "probe", "--bg-layer", str(pix))      # no --tri
    assert r.returncode == 2
    # a bgpixel slot without a bgpds one would not run: refused
    r = run("--mock", *KNOBS, "probe", "--tri", "bgpixel", "--bg-layer", str(pix))
    assert r.returncode == 2 and "bgpds" in r.stderr


def test_probe_tri_bg_layer_with_a_bgpds_slot_keeps_its_own_primary(tmp_path):
    pds = tmp_path / "bgpds.bin"
    pds.write_bytes(bytes(16 * 4))
    pix = assemble(tmp_path, "pix", PHAS + "mov.skipinv.end o0, pa0\n")
    r = run("--mock", *KNOBS, "probe", "--tri", "bgpds:4", "--slot", f"bgpixel={pix}",
            "--bg-layer", str(pds))
    # the zero program of the slot faults the mock (rc 3, a failed job); not a refusal
    assert r.returncode in (0, 3), r.stdout + r.stderr
    assert f"bg-layer: source {SRC} 64x64 RGBA8888, knob Y\n" in r.stdout, r.stdout
    assert "usage:" not in r.stderr


# ---- the layer-sampling programs ----------------------------------------------------------

PROBES = ROOT / "probes"
TEMPLATES = {
    "bgl_raw": PROBES / "isp" / "templates" / "pds_bgl_raw.s",      # L-RAW: u in pa0, v in pa1
    "bg_pos": PROBES / "dpm" / "templates" / "pds_bg_pos.s",        # POS: x + 0.5, y + 0.5
}


def words(path: pathlib.Path) -> list[int]:
    raw = path.read_bytes()
    return [int.from_bytes(raw[i:i + 4], "little") for i in range(0, len(raw), 4)]


def test_bgl_raw_program_words(tmp_path):
    # 12 data dwords as the copy's primary has them (dwords 3-9 stated by the plan), then
    # doutu, douti, doutt and halt
    w = words(assemble(tmp_path, "raw", TEMPLATES["bgl_raw"].read_text(), "pds"))
    assert len(w) == 16
    assert w[3] == 0x02000004                       # U1: wait for the fetch
    assert w[4] == 0x40400801 and w[5] == 0          # DOUTI: set 1, two components, fetch bit
    assert w[6] == 0x5CAF0000                       # T2: the probe's scratch (patched)
    assert w[7:10] == [0x00800800, 0x07fe0000, 0x0d00f00f]
    assert w[0] == w[1] == w[2] == 0 and w[10] == w[11] == 0
    # the program is E709's pds_iter_xy (measured on a triangle's coordinate set), word for word
    xy = words(assemble(tmp_path, "xy", (PROBES / "usse" / "templates" /
                                         "pds_iter_xy.s").read_text(), "pds"))
    assert w == xy


def test_bg_pos_program_words(tmp_path):
    w = words(assemble(tmp_path, "pos", TEMPLATES["bg_pos"].read_text(), "pds"))
    assert len(w) == 15
    assert w[3] == 0x01000004 and w[4] == 0x20400000 and w[5] == 0


@pytest.mark.parametrize("pa", ["pix_pa0", "pix_pa1"])
def test_bgl_raw_rows_run_on_the_mock(tmp_path, pa):
    # L-RAW-U and -V: the bgpds primary, a pa0 or pa1 background shader, the layer on
    pds = assemble(tmp_path, "raw", TEMPLATES["bgl_raw"].read_text(), "pds")
    shader = assemble(tmp_path, pa, (PROBES / "dpm" / "templates" / f"{pa}.s").read_text())
    r = run("--mock", *KNOBS, "probe", "--tri", "bgpds:12", "--slot", f"bgpixel={shader}",
            "--bg-layer", str(pds))
    assert r.returncode in (0, 3), r.stdout + r.stderr
    assert f"bg-layer: source {SRC} 64x64 RGBA8888, knob Y\n" in r.stdout
    assert re.search(r"^probe raw: tri 64x64, bgpds bgpixel replaced$", r.stdout, re.M), r.stdout


def test_bg_pos_row_runs_on_the_mock(tmp_path):
    pds = assemble(tmp_path, "pos", TEMPLATES["bg_pos"].read_text(), "pds")
    shader = assemble(tmp_path, "pix_pa0", (PROBES / "dpm" / "templates" /
                                            "pix_pa0.s").read_text())
    r = run("--mock", *KNOBS, "probe", "--tri", "bgpds:12", "--slot", f"bgpixel={shader}",
            "--bg-layer", str(pds))
    assert r.returncode in (0, 3), r.stdout + r.stderr
    assert re.search(r"^probe pos: tri 64x64, bgpds bgpixel replaced$", r.stdout, re.M), r.stdout
