# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""sgxfive-test probe --tri against the mock: probe programs in the first triangle's render
(sgxfive_tri_probe.h). The mock draws the scene from the programs' first words and does not
run them, so these check the plumbing: the options, the placement and patching the mock can
see, and the output probe.py parses."""
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
PROBES = ROOT / "probes" / "pds" / "templates"
PHAS = "phas #0, #0, pixel, end, parallel\n"
BG = 0xff203040                 # the first triangle's background (sgxfive_tri_default)
SENTINEL = 0xdeadbeef           # SGXFIVE_TRI_SENTINEL: a pixel no render wrote


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([TOOL, *args], capture_output=True, text=True, timeout=60)


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


def pixev(tmp_path: pathlib.Path, name: str = "pixev") -> pathlib.Path:
    """pixev_dump.s with sixteen markers passed on: 60 data dwords."""
    op = "\n".join(f"movs douta, ds0[{10 + k}], ds1[{10 + k}], ds0[{10 + k}], ds0[{10 + k}]"
                   for k in range(16))
    return assemble(tmp_path, name, (PROBES / "pixev_dump.s").read_text().replace("{OP}", op),
                    "pds")


def summary(out: str, name: str) -> dict:
    m = re.search(rf"^probe {name}: o0 mixed (.*)$", out, re.M)
    assert m, out
    return {int(v, 16): int(c) for v, c in re.findall(r"(0x[0-9a-f]+) x(\d+)", m.group(1))}


def test_tri_pixel_shader_with_scratch_immediate(tmp_path):
    # The mock colours the triangle with its pixel shader's second immediate: here the
    # scratch buffer's address + 0x10.
    f = assemble(tmp_path, "pix", PHAS + "mov.skipinv.end o0, #0x5CAF0010\n")
    r = run("--mock", "probe", "--tri", "pixel", "--temps", "8", str(f))
    assert r.returncode == 0, r.stdout + r.stderr
    m = re.search(r"^probe pix: scratch at (0x\w+) \(64 KiB\)$", r.stdout, re.M)
    assert m, r.stdout
    assert re.search(r"^probe pix: tri 64x64, pixel replaced$", r.stdout, re.M), r.stdout
    vals = summary(r.stdout, "pix")
    assert vals.get(int(m.group(1), 16) + 0x10, 0) > 0, r.stdout
    assert vals.get(BG, 0) > 0
    assert sum(vals.values()) == 64 * 64


def test_tri_pixel_event_and_end_of_tile(tmp_path):
    # pixev_dump.s as the pixel-event program and eot_dump.s as the end-of-tile task: the
    # mock finds the target's PBE words in the replacement, so the image is drawn.
    p = pixev(tmp_path)
    e = assemble(tmp_path, "eot", (PROBES / "eot_dump.s").read_text())
    r = run("--mock", "probe", "--tri", "pixev:60", "--slot", f"eot={e}", "--temps", "8",
            "--width", "32", "--height", "16", str(p))
    assert r.returncode == 0, r.stdout + r.stderr
    assert re.search(r"^probe pixev: tri 32x16, pixev eot replaced$", r.stdout, re.M), r.stdout
    assert "failed" not in r.stdout
    vals = summary(r.stdout, "pixev")
    assert vals.get(BG, 0) > 0 and sum(vals.values()) == 32 * 16


def test_tri_odd_height_and_odd_width_run(tmp_path):
    f = assemble(tmp_path, "x", PHAS + "mov.skipinv.end o0, #0x12345678\n")
    r = run("--mock", "probe", "--tri", "pixel", "--pixels", "--width", "32", "--height", "17",
            str(f))
    assert r.returncode == 0, r.stdout + r.stderr
    assert re.search(r"^probe x: tri 32x17,", r.stdout, re.M), r.stdout
    assert len(re.findall(r"^probe x: row \d+:", r.stdout, re.M)) == 17
    # an odd width: the row pitch is rounded up to 34 pixels, the readback skips the pad pixel
    r = run("--mock", "probe", "--tri", "pixel", "--pixels", "--width", "33", "--height", "17",
            str(f))
    assert r.returncode == 0, r.stdout + r.stderr
    assert re.search(r"^probe x: tri 33x17,", r.stdout, re.M), r.stdout
    rows = re.findall(r"^probe x: row \d+:(.*)$", r.stdout, re.M)
    assert len(rows) == 17
    assert all(len(row.split()) == 33 for row in rows), rows
    vals = summary(r.stdout, "x")
    assert sum(vals.values()) == 33 * 17 and vals.get(BG, 0) > 0, vals
    assert "%08x" % SENTINEL not in r.stdout, r.stdout


def test_tri_every_file_runs_in_its_own_render(tmp_path):
    a = pixev(tmp_path, "a")
    b = pixev(tmp_path, "b")
    e = assemble(tmp_path, "tile", (PROBES / "eot_tile.s").read_text())
    r = run("--mock", "probe", "--tri", "pixev:60", "--slot", f"eot={e}", "--temps", "8",
            "--width", "32", "--height", "4096", "--max-height", "4096", str(a), str(b))
    assert r.returncode == 0, r.stdout + r.stderr
    assert re.findall(r"^probe (\w+): tri 32x4096,", r.stdout, re.M) == ["a", "b"], r.stdout


def test_tri_vertex_programs(tmp_path):
    # Copies of the default vertex programs (pds_vtx.s, use_vtx.s) as replacements: the
    # mock reads the vertex buffer through the replaced PDS program and faults on a vertex
    # shader that is not mapped, so the triangle is drawn only if both are placed right.
    vp = assemble(tmp_path, "vp", (ROOT / "asm" / "tri" / "pds_vtx.s").read_text(), "pds")
    vu = assemble(tmp_path, "vu", (ROOT / "asm" / "tri" / "use_vtx.s").read_text())
    r = run("--mock", "probe", "--tri", "vtxpds:8", "--slot", f"vtxuse={vu}", str(vp))
    assert r.returncode == 0, r.stdout + r.stderr
    assert re.search(r"^probe vp: tri 64x64, vtxpds vtxuse replaced$", r.stdout, re.M)
    vals = summary(r.stdout, "vp")
    assert vals.get(0xff00ff00, 0) > 0 and vals.get(BG, 0) > 0, r.stdout


def test_tri_pixels_prints_every_row(tmp_path):
    f = assemble(tmp_path, "px", PHAS + "mov.skipinv.end o0, #0x12345678\n")
    r = run("--mock", "probe", "--tri", "pixel", "--pixels", "--width", "32", "--height",
            "16", str(f))
    assert r.returncode == 0, r.stdout + r.stderr
    rows = re.findall(r"^probe px: row (\d+): ([0-9a-f ]+)$", r.stdout, re.M)
    assert [int(y) for y, _ in rows] == list(range(16))
    assert all(len(v.split()) == 32 for _, v in rows)
    flat = [int(v, 16) for _, vs in rows for v in vs.split()]
    assert 0x12345678 in flat and BG in flat


@pytest.mark.parametrize("args", [
    ["--tri", "bogus"],
    ["--tri", "pixev"],                         # a PDS slot needs its data dwords
    ["--tri", "pixev:18"],                      # not whole rows
    ["--tri", "eot:8"],                         # a USE slot has none
    ["--tri", "pixel", "--coords"],
    ["--tri", "pixel", "--pds", "8"],
    ["--slot", "eot=x.bin"],                    # --slot needs --tri
    ["--tri", "pixel", "--slot", "pixel=x.bin"],  # the case's own slot
    ["--tri", "pixel", "--slot", "bogus=x.bin"],
    ["--tri", "pixel", "--slot", "eot"],
    ["--tri", "pixel", "--width", "64", "--max-width", "32"],
    ["--width", "32"],                          # --width needs --tri
])
def test_tri_usage(tmp_path, args):
    f = assemble(tmp_path, "x", PHAS + "mov.skipinv.end o0, #1\n")
    args = [a.replace("x.bin", str(f)) for a in args]
    r = run("--mock", "probe", *args, str(f))
    assert r.returncode == 2, r.stdout + r.stderr


def test_tri_rejects_bad_files(tmp_path):
    f = assemble(tmp_path, "x", PHAS + "mov.skipinv.end o0, #1\n")
    # a PDS case no longer than its data segment
    short = tmp_path / "short.bin"
    short.write_bytes(b"\0" * 4 * 20)
    r = run("--mock", "probe", "--tri", "pixev:20", str(short))
    assert r.returncode == 1
    r = run("--mock", "probe", "--tri", "pixel", "--slot",
            f"eot={tmp_path / 'missing.bin'}", str(f))
    assert r.returncode == 1
    assert "missing.bin" in r.stderr
    # an end-of-tile program too short for the PBE words and the emit: the scene refuses it
    r = run("--mock", "probe", "--tri", "eot", str(f))
    assert r.returncode == 3, r.stdout + r.stderr
    assert re.search(r"^probe x: failed: Invalid argument$", r.stdout, re.M), r.stdout


def test_tri_reports_a_failed_render(tmp_path):
    # A render that fails is reported as the probe's failure (on the mock: a scene
    # too large for a parameter buffer of 0x23 pages, -ENOSPC).
    f = assemble(tmp_path, "pix", PHAS + "mov.skipinv.end o0, #1\n")
    r = run("--mock", "--mock-pb-pages=0x23", "probe", "--tri", "pixel", str(f))
    assert r.returncode == 3, r.stdout + r.stderr
    assert re.search(r"^probe pix: failed: scene overflowed the parameter buffer", r.stdout,
                     re.M), r.stdout
    # what the scratch holds is still reported: what ran before the failure stored there
    # (on the mock nothing ran)
    assert re.search(r"^probe pix: scratch unchanged$", r.stdout, re.M), r.stdout
    # the target is read after an overflow (the render's partial renders stored into it, its
    # context kept): its colours follow the failure, and every row with --pixels
    assert re.search(r"^probe pix: o0 ", r.stdout, re.M), r.stdout
    assert r.stdout.index("failed: scene overflowed") < r.stdout.index("probe pix: o0 ")
    assert not re.search(r"^probe pix: row ", r.stdout, re.M), r.stdout
    r = run("--mock", "--mock-pb-pages=0x23", "probe", "--tri", "pixel", "--pixels", str(f))
    assert r.returncode == 3, r.stdout + r.stderr
    rows = re.findall(r"^probe pix: row (\d+):((?: [0-9a-f]{8})+)$", r.stdout, re.M)
    assert [int(y) for y, _ in rows] == list(range(64)) and len(rows[0][1].split()) == 64, r.stdout
    assert r.stdout.index("failed: scene overflowed") < r.stdout.index("probe pix: row 0:")


def test_tri_vertices_failed_render_prints_no_time(tmp_path):
    # an overflowed render did not complete: no timing line
    f = assemble(tmp_path, "pix", PHAS + "mov.skipinv.end o0, #1\n")
    r = run("--mock", "--mock-pb-pages=0x23", "probe", "--tri", "pixel", "--vertices", "6",
            str(f))
    assert r.returncode == 3 and "failed: scene overflowed" in r.stdout, r.stdout + r.stderr
    assert not re.search(r"^tri 64x64 #1:", r.stdout, re.M), r.stdout


def test_tri_vertices(tmp_path):
    # --vertices N: copies of the triangle after it (sgxfive_tri_probe.h), so that the vertex
    # programs run for more vertices than one task's; the mock draws them all.
    f = assemble(tmp_path, "pix", PHAS + "mov.skipinv.end o0, #0x0000000A\n")
    r = run("--mock", "probe", "--tri", "pixel", "--vertices", "15", str(f))
    assert r.returncode == 0, r.stdout + r.stderr
    assert re.search(r"^probe pix: tri 64x64 \(15 vertices\), pixel replaced$", r.stdout,
                     re.M), r.stdout
    assert summary(r.stdout, "pix").get(0xA, 0) > 0, r.stdout
    # the same per-render timing line the plain tri form prints (kit timing scorers read it)
    assert re.search(r"^tri 64x64 #1: \d+ us$", r.stdout, re.M), r.stdout
    # 126: the vertex buffer moved to the scene page's spare room, still drawn
    r = run("--mock", "probe", "--tri", "pixel", "--vertices", "126", str(f))
    assert r.returncode == 0 and summary(r.stdout, "pix").get(0xA, 0) > 0, r.stdout + r.stderr
    # 300 and 1500: the wide scenes (the rig's gen region of extra pages), still drawn
    for n in ("129", "300", "1500"):
        r = run("--mock", "probe", "--tri", "pixel", "--vertices", n, str(f))
        assert r.returncode == 0 and summary(r.stdout, "pix").get(0xA, 0) > 0, (n, r.stdout)
        assert f"({n} vertices)" in r.stdout, r.stdout
    # not whole triangles, more than the wide scene holds, or not a --tri probe
    for args in (["--tri", "pixel", "--vertices", "4"], ["--tri", "pixel", "--vertices", "1503"],
                 ["--tri", "pixel", "--vertices", "x"], ["--vertices", "6"]):
        r = run("--mock", "probe", *args, str(f))
        assert r.returncode == 2, (args, r.stdout + r.stderr)   # usage


def test_tri_vtx_coords(tmp_path):
    # --vtx-coords N: N more output dwords per vertex, a texture coordinate set
    # (sgxfive_tri_probe.h, coords), for a vtxuse program that writes o4 on
    f = assemble(tmp_path, "pix", PHAS + "mov.skipinv.end o0, #0x0000000A\n")
    r = run("--mock", "probe", "--tri", "pixel", "--vtx-coords", "2", str(f))
    assert r.returncode == 0, r.stdout + r.stderr
    assert re.search(r"^probe pix: tri 64x64 \(2 coordinates\), pixel replaced$", r.stdout,
                     re.M), r.stdout
    # more than the vertex size holds, not a number, or not a --tri probe
    for args in (["--tri", "pixel", "--vtx-coords", "12"], ["--tri", "pixel", "--vtx-coords",
                 "x"], ["--vtx-coords", "2"]):
        r = run("--mock", "probe", *args, str(f))
        assert r.returncode == 2, (args, r.stdout + r.stderr)   # usage


def test_tri_isp2(tmp_path):
    # --isp2 V: the state block carries ISP word 2 (stencil) V in place of the wrap word
    # (sgxfive_tri_probe.h, isp2); the mock still finds the viewport and draws the triangle
    f = assemble(tmp_path, "pix", PHAS + "mov.skipinv.end o0, #0x0000000A\n")
    r = run("--mock", "probe", "--tri", "pixel", "--pixels", "--isp2", "0x0e0200ff", str(f))
    assert r.returncode == 0, r.stdout + r.stderr
    assert re.search(r"^probe pix: tri 64x64 \(isp2 0x0e0200ff\), pixel replaced$", r.stdout,
                     re.M), r.stdout
    assert summary(r.stdout, "pix").get(0xA, 0) > 0, r.stdout
    # not a number, or not a --tri probe
    for args in (["--tri", "pixel", "--isp2", "x"], ["--isp2", "0"]):
        r = run("--mock", "probe", *args, str(f))
        assert r.returncode == 2, (args, r.stdout + r.stderr)   # usage


def test_tri_blk_add(tmp_path):
    # --blk-add BIT=V[,V]: presence bit BIT added to the state block with its words, the block
    # and its copy grown (sgxfive_tri_probe.h, add_mask); the mock still draws the triangle
    f = assemble(tmp_path, "pix", PHAS + "mov.skipinv.end o0, #0x0000000A\n")
    r = run("--mock", "probe", "--tri", "pixel", "--pixels", "--isp2", "0x0e0200ff",
            "--blk-add", "3=0x0e0200ff", "--blk-add", "7=0x0000ffff,0x0000ffff", str(f))
    assert r.returncode == 0, r.stdout + r.stderr
    assert re.search(r"^probe pix: tri 64x64 \(isp2 0x0e0200ff\) \(blk-add 0x88\), pixel "
                     r"replaced$", r.stdout, re.M), r.stdout
    assert summary(r.stdout, "pix").get(0xA, 0) > 0, r.stdout
    # a bit it cannot add, a missing or extra word, not a number, not a --tri probe
    for args in (["--tri", "pixel", "--blk-add", "0=1"], ["--tri", "pixel", "--blk-add", "7=1"],
                 ["--tri", "pixel", "--blk-add", "3=1,2"], ["--tri", "pixel", "--blk-add", "3=x"],
                 ["--blk-add", "3=1"]):
        r = run("--mock", "probe", *args, str(f))
        assert r.returncode == 2, (args, r.stdout + r.stderr)   # usage


def test_tri_copy_depth_and_blk(tmp_path):
    # --copy-depth: the copies at clip z = c / 16; --blk N=V: state block word N set to V
    f = assemble(tmp_path, "pix", PHAS + "mov.skipinv.end o0, #0x0000000A\n")
    r = run("--mock", "probe", "--tri", "pixel", "--vertices", "6", "--copy-depth",
            "--blk", "1=0x00400200", "--blk", "10=0x3e99999a", str(f))
    assert r.returncode == 0, r.stdout + r.stderr
    assert re.search(r"^probe pix: tri 64x64 \(6 vertices, at depths\) \(block words 1 10\), "
                     r"pixel replaced$", r.stdout, re.M), r.stdout
    for args in (["--tri", "pixel", "--blk", "18=1"], ["--tri", "pixel", "--blk", "x"],
                 ["--tri", "pixel", "--blk", "1="], ["--tri", "pixel", "--copy-depth"],
                 ["--blk", "1=2"]):
        r = run("--mock", "probe", *args, str(f))
        assert r.returncode == 2, (args, r.stdout + r.stderr)   # usage



def test_tri_obj2(tmp_path):
    # --obj2 FIRST: the copies from vertex FIRST on as a second object, with its own state
    # block (--obj2-blk N=V words set in the first's) and pixel shader (--obj2-pixel FILE)
    f = assemble(tmp_path, "pix", PHAS + "mov.skipinv.end o0, #0x0000000A\n")
    g = assemble(tmp_path, "pix2", PHAS + "mov.skipinv.end o0, #0x0000000B\n")
    r = run("--mock", "probe", "--tri", "pixel", "--vertices", "6", "--obj2", "3",
            "--obj2-blk", "1=0x00400200", "--obj2-pixel", str(g), str(f))
    assert r.returncode == 0, r.stdout + r.stderr
    assert re.search(r"^probe pix: tri 64x64 \(6 vertices\) \(obj2 from 3: block words 1, "
                     r"pixel\), pixel replaced$", r.stdout, re.M), r.stdout
    for args in (["--tri", "pixel", "--obj2", "3"],                       # no copies
                 ["--tri", "pixel", "--vertices", "6", "--obj2", "4"],    # not a triangle's
                 ["--tri", "pixel", "--vertices", "6", "--obj2", "6"],    # past the copies
                 ["--tri", "pixel", "--vertices", "6", "--obj2", "3", "--obj2-blk", "32=1"],
                 ["--tri", "pixel", "--vertices", "6", "--obj2-blk", "1=1"],
                 ["--tri", "pixel", "--vertices", "6", "--obj2-pixel", str(g)],
                 ["--obj2", "3"]):
        r = run("--mock", "probe", *args, str(f))
        assert r.returncode == 2, (args, r.stdout + r.stderr)   # usage


def test_tri_obj2_pixpds(tmp_path):
    # --obj2-pixpds FILE:N: the second object's primary pixel PDS program with N data dwords, as
    # --tri pixpds:N is the first's, which may load the pixel side's constants (douta)
    f = assemble(tmp_path, "pix", PHAS + "mov.skipinv.end o0, #0x0000000A\n")
    g = assemble(tmp_path, "pix2", PHAS + "mov.skipinv.end o0, #0x0000000B\n")
    pds = assemble(tmp_path, "pp", ".word 0\n.word 0\n.word 0\n.word 4\n"
                   "movs doutu, ds0[0], ds1[1], ds1[0], ds0[0]\nhalt\n", isa="pds")
    r = run("--mock", "probe", "--tri", "pixel", "--vertices", "6", "--obj2", "3",
            "--obj2-pixel", str(g), "--obj2-pixpds", f"{pds}:4", str(f))
    assert r.returncode == 0, r.stdout + r.stderr
    assert re.search(r"^probe pix: tri 64x64 \(6 vertices\) \(obj2 from 3: pixel, primary\), "
                     r"pixel replaced$", r.stdout, re.M), r.stdout
    r = run("--mock", "probe", "--tri", "pixel", "--vertices", "6", "--obj2", "3",
            "--obj2-blk", "4=0x130004", "--obj2-pixpds", f"{pds}:4", str(f))
    assert r.returncode == 0, r.stdout + r.stderr
    assert "(obj2 from 3: block words 4, primary)" in r.stdout, r.stdout
    for args in (["--tri", "pixel", "--vertices", "6", "--obj2-pixpds", f"{pds}:4"],  # no obj2
                 ["--tri", "pixel", "--vertices", "6", "--obj2", "3", "--obj2-pixpds", str(pds)],
                 ["--tri", "pixel", "--vertices", "6", "--obj2", "3", "--obj2-pixpds",
                  f"{pds}:3"],                                     # not whole rows
                 ["--tri", "pixel", "--vertices", "6", "--obj2", "3", "--obj2-pixpds",
                  f"{pds}:8"]):                                    # no code after the data
        r = run("--mock", "probe", *args, str(f))
        assert r.returncode in (1, 2), (args, r.stdout + r.stderr)


def test_tri_sideband(tmp_path):
    # --sideband V: the replaced end-of-tile program's emitpix2 sideband; needs that slot
    f = assemble(tmp_path, "pix", PHAS + "mov.skipinv.end o0, #0x0000000A\n")
    eot = assemble(tmp_path, "eot", (PROBES / "eot_dump.s").read_text())
    r = run("--mock", "probe", "--tri", "pixel", "--slot", f"eot={eot}", "--temps", "8",
            "--sideband", "0x2240", str(f))
    assert r.returncode == 0, r.stdout + r.stderr
    assert re.search(r"^probe pix: tri 64x64 \(sideband 0x00002240\), eot pixel replaced$",
                     r.stdout, re.M), r.stdout
    for args in (["--tri", "pixel", "--sideband", "0x200"], ["--tri", "pixel", "--slot",
                 f"eot={eot}", "--sideband", "x"], ["--sideband", "0x200"]):
        r = run("--mock", "probe", *args, str(f))
        assert r.returncode == 2, (args, r.stdout + r.stderr)   # usage


def test_tri_cmd_words(tmp_path):
    # --cmd N=V: the render command's word N set to V (after the other options)
    f = assemble(tmp_path, "pix", PHAS + "mov.skipinv.end o0, #0x0000000A\n")
    r = run("--mock", "probe", "--tri", "pixel", "--cmd", "13=0x80000002", "--cmd",
            "16=0xeaa26e26", str(f))
    assert r.returncode == 0, r.stdout + r.stderr
    assert re.search(r"^probe pix: tri 64x64 \(command words 13 16\), pixel replaced$",
                     r.stdout, re.M), r.stdout
    for args in (["--tri", "pixel", "--cmd", "26=1"], ["--tri", "pixel", "--cmd", "x"],
                 ["--cmd", "1=2"]):
        r = run("--mock", "probe", *args, str(f))
        assert r.returncode == 2, (args, r.stdout + r.stderr)


def test_tri_vdm_words(tmp_path):
    # --vdm N=V: the VDM stream's word N set to V (after the other options)
    f = assemble(tmp_path, "pix", PHAS + "mov.skipinv.end o0, #0x0000000A\n")
    r = run("--mock", "probe", "--tri", "pixel", "--vdm", "4=0xf4000000", "--vdm",
            "7=0x01c00083", str(f))
    assert r.returncode == 0, r.stdout + r.stderr
    assert re.search(r"^probe pix: tri 64x64 \(VDM words 4 7\), pixel replaced$",
                     r.stdout, re.M), r.stdout
    for args in (["--tri", "pixel", "--vdm", "11=1"], ["--tri", "pixel", "--vdm", "x"],
                 ["--vdm", "1=2"]):
        r = run("--mock", "probe", *args, str(f))
        assert r.returncode == 2, (args, r.stdout + r.stderr)


def test_tri_dump_render(tmp_path):
    # --dump-render DIR: after the render, the kernel's debugfs render_param and
    # render_tadata (SGXFIVE_DEBUGFS overrides their directory) copied to DIR/NAME.*.bin
    f = assemble(tmp_path, "pix", PHAS + "mov.skipinv.end o0, #0x0000000A\n")
    dbg = tmp_path / "debugfs"
    dbg.mkdir()
    param, tadata = bytes(range(256)) * 300, b"\x5a" * 5000
    (dbg / "render_param").write_bytes(param)
    (dbg / "render_tadata").write_bytes(tadata)
    out = tmp_path / "out"
    out.mkdir()
    r = subprocess.run([TOOL, "--mock", "probe", "--tri", "pixel", "--dump-render", str(out),
                        str(f)], capture_output=True, text=True, timeout=60,
                       env={**os.environ, "SGXFIVE_DEBUGFS": str(dbg)})
    assert r.returncode == 0, r.stdout + r.stderr
    assert (out / "pix.param.bin").read_bytes() == param
    assert (out / "pix.tadata.bin").read_bytes() == tadata
    assert re.search(rf"^probe pix: render memory to {re.escape(str(out))}/pix\.\{{param,tadata\}}"
                     rf"\.bin \(76800, 5000 bytes\)$", r.stdout, re.M), r.stdout
    r = run("--mock", "probe", "--dump-render", str(out), str(f))   # not a --tri probe
    assert r.returncode == 2, r.stdout + r.stderr


def test_tri_dump_render_after_a_failed_job(tmp_path):
    # --dump-render also after a job that faulted or hung: recovery keeps the PB pages (the
    # TA's objects and streams), so the dump shows how far the TA got; the job still fails
    # (the mock faults on an index list that is not of triangles)
    vp = assemble(tmp_path, "vp", PHAS + "mov.skipinv.end o0, #0x0000000A\n")
    dbg = tmp_path / "debugfs"
    dbg.mkdir()
    (dbg / "render_param").write_bytes(b"\x33" * 4096)
    (dbg / "render_tadata").write_bytes(b"\x44" * 4096)
    out = tmp_path / "out"
    out.mkdir()
    r = subprocess.run([TOOL, "--mock", "probe", "--tri", "pixel", "--vdm", "2=0x88c00003",
                        "--dump-render", str(out), str(vp)], capture_output=True, text=True,
                       timeout=60, env={**os.environ, "SGXFIVE_DEBUGFS": str(dbg)})
    assert re.search(r"^probe vp: failed: ", r.stdout, re.M), r.stdout
    assert re.search(r"^probe vp: render memory to .*/vp\.\{param,tadata\}\.bin "
                     r"\(4096, 4096 bytes\) after the failure$", r.stdout, re.M), r.stdout
    assert (out / "vp.param.bin").read_bytes() == b"\x33" * 4096


def test_tri_kpoke(tmp_path):
    # --kpoke SPEC (repeatable): written to the kernel's debugfs kpoke (SGXFIVE_KPOKE overrides
    # the path) before each case's render, in order, so a probe can set kernel-built words
    f = assemble(tmp_path, "pix", PHAS + "mov.skipinv.end o0, #0x0000000A\n")
    k = tmp_path / "kpoke"
    k.write_text("")
    r = subprocess.run([TOOL, "--mock", "probe", "--tri", "pixel", "--kpoke", "ta:152=0x40000000",
                        "--kpoke", "ta:153=0x3e800000", str(f)], capture_output=True, text=True,
                       timeout=60, env={**os.environ, "SGXFIVE_KPOKE": str(k)})
    assert r.returncode == 0, r.stdout + r.stderr
    assert k.read_text() == "ta:152=0x40000000\nta:153=0x3e800000\n"
    assert re.search(r"^probe pix: kpoke ta:152=0x40000000 ta:153=0x3e800000$", r.stdout, re.M)
    r = run("--mock", "probe", "--kpoke", "ta:1=1", str(f))          # not a --tri probe
    assert r.returncode == 2, r.stdout + r.stderr


def test_tri_vdm_flip(tmp_path):
    # --vdm N^=V: the VDM stream's word N flipped by V (the words hold addresses we do not set)
    f = assemble(tmp_path, "pix", PHAS + "mov.skipinv.end o0, #0x0000000A\n")
    r = run("--mock", "probe", "--tri", "pixel", "--vdm", "1^=0x100", str(f))
    assert r.returncode == 0, r.stdout + r.stderr
    assert re.search(r"^probe pix: tri 64x64 \(VDM words \^1\), pixel replaced$", r.stdout,
                     re.M), r.stdout
    r = run("--mock", "probe", "--tri", "pixel", "--vdm", "11^=1", str(f))
    assert r.returncode == 2, r.stdout + r.stderr


def test_tri_blk_and_cmd_flip(tmp_path):
    # --blk N^=V and --cmd N^=V: the state block's word and the render command's word flipped
    # by V, listed after the set words in the probe's line; out-of-range words are usage errors
    f = assemble(tmp_path, "pix", PHAS + "mov.skipinv.end o0, #0x0000000A\n")
    r = run("--mock", "probe", "--tri", "pixel", "--blk", "4^=0x8000", "--blk", "1=0x400200",
            "--cmd", "10^=1", "--cmd", "11=2", str(f))
    assert r.returncode == 0, r.stdout + r.stderr
    assert re.search(r"^probe pix: tri 64x64 \(block words 1 \^4\) \(command words \^10 11\), "
                     r"pixel replaced$", r.stdout, re.M), r.stdout
    for args in (["--tri", "pixel", "--blk", "18^=1"], ["--tri", "pixel", "--cmd", "26^=1"],
                 ["--tri", "pixel", "--blk", "1^1"], ["--blk", "1^=2"], ["--cmd", "1^=2"]):
        r = run("--mock", "probe", *args, str(f))
        assert r.returncode == 2, (args, r.stdout + r.stderr)


def test_tri_vdm_words_of_the_second_object(tmp_path):
    # with --obj2 the stream's words 11 to 18 are the second object's, flipped as built (word 9
    # is the second state block's); without it only 0 to 10 exist
    f = assemble(tmp_path, "pix", PHAS + "mov.skipinv.end o0, #0x0000000A\n")
    r = run("--mock", "probe", "--tri", "pixel", "--vertices", "12", "--obj2", "6", "--vdm",
            "9^=0x200", "--vdm", "18=0xc0000000", str(f))
    assert r.returncode == 0, r.stdout + r.stderr
    assert re.search(r"\(VDM words \^9 18\)", r.stdout), r.stdout
    for args in (["--vdm", "11^=0x200"], ["--vdm", "18=1"]):
        r = run("--mock", "probe", "--tri", "pixel", *args, str(f))
        assert r.returncode == 2, (args, r.stdout + r.stderr)
    r = run("--mock", "probe", "--tri", "pixel", "--vertices", "12", "--obj2", "6", "--vdm",
            "19=1", str(f))
    assert r.returncode == 2, r.stdout + r.stderr


def test_tri_pbe_words(tmp_path):
    # --pbe N=V: the end-of-tile task's PBE word N (0 to 3) as given, with the default end-of-tile
    # task too; word 4 is --sideband's and a flip is not offered
    f = assemble(tmp_path, "pix", PHAS + "mov.skipinv.end o0, #0x0000000A\n")
    r = run("--mock", "probe", "--tri", "pixel", "--pbe", "1=0x003f003f", "--pbe", "3=0x3e004000",
            str(f))
    assert r.returncode == 3, r.stdout + r.stderr
    assert re.search(r"^probe pix: tri 64x64 \(PBE words 1 3\), pixel replaced$", r.stdout,
                     re.M), r.stdout
    for args in (["--tri", "pixel", "--pbe", "4=1"], ["--tri", "pixel", "--pbe", "1^=1"],
                 ["--tri", "pixel", "--pbe", "x"], ["--pbe", "1=2"]):
        r = run("--mock", "probe", *args, str(f))
        assert r.returncode == 2, (args, r.stdout + r.stderr)


def test_tri_background_slots(tmp_path):
    # bgpixel and bgpds: the background object's pixel shader and primary PDS program
    f = assemble(tmp_path, "bg", PHAS + "mov.skipinv.end o0, #0x0000000B\n")
    r = run("--mock", "probe", "--tri", "bgpixel", str(f))
    assert r.returncode == 0, r.stdout + r.stderr
    assert re.search(r"^probe bg: tri 64x64, bgpixel replaced$", r.stdout, re.M), r.stdout
    p = pixev(tmp_path, "bgp")          # a PDS program with 60 data dwords
    r = run("--mock", "probe", "--tri", "bgpds:60", "--slot", f"bgpixel={f}", str(p))
    assert r.returncode == 0, r.stdout + r.stderr
    assert re.search(r"^probe bgp: tri 64x64, bgpds bgpixel replaced$", r.stdout, re.M), r.stdout
    r = run("--mock", "probe", "--tri", "bgpds", str(p))               # no data dword count
    assert r.returncode == 2, r.stdout + r.stderr


def test_tri_probe_vertices_in_256ths_and_depths(tmp_path):
    # probe --tri takes --tri-v and --tri-z as tri does; the case's line says the triangle
    pix = assemble(tmp_path, "pix", PHAS + "mov.skipinv.end o0, pa0\n")
    r = run("--mock", "probe", "--tri", "pixel", "--tri-v", "2048,2048,12288,5120,5120,14336",
            "--tri-z", "0.25,0.5,0.75", str(pix))
    assert r.returncode == 0, r.stdout + r.stderr
    assert re.search(r"^probe pix: vertices256 2048 2048 12288 5120 5120 14336, depth 0.25 0.5 0.75$",
                     r.stdout, re.M), r.stdout


def test_tri_probe_depths_range_minus_one_to_two(tmp_path):
    pix = assemble(tmp_path, "pix", PHAS + "mov.skipinv.end o0, pa0\n")
    r = run("--mock", "probe", "--tri", "pixel", "--tri-z", "-1,0.5,2", str(pix))
    assert r.returncode == 0, r.stdout + r.stderr
    assert "depth -1 0.5 2\n" in r.stdout, r.stdout
    r = run("--mock", "probe", "--tri", "pixel", "--tri-z", "-1.5,0.5,2", str(pix))
    assert r.returncode == 2, r.stdout + r.stderr


def test_tri_probe_v_is_checked(tmp_path):
    pix = assemble(tmp_path, "pix", PHAS + "mov.skipinv.end o0, pa0\n")
    for args in (["--tri-v", "1,2,3"], ["--tri-v", "0,0,256,0,0,256", "--tri-full"],
                 ["--tri-v", "0,0,256,0,0,256", "--vertices", "6"], ["--tri-z", "0.1,0.2"]):
        r = run("--mock", "probe", "--tri", "pixel", *args, str(pix))
        assert r.returncode == 2, (args, r.stdout + r.stderr)
    r = run("--mock", "probe", "--tri-v", "0,0,256,0,0,256", str(pix))
    assert r.returncode == 2, r.stdout + r.stderr


def test_tri_probe_unit(tmp_path):
    pix = assemble(tmp_path, "pix", PHAS + "mov.skipinv.end o0, pa0\n")
    r = run("--mock", "probe", "--tri", "pixel", "--tri-unit", "12", "--tri-v", "32768,32768,196608,81920,81920,229376", str(pix))
    assert r.returncode == 0, r.stdout + r.stderr
    assert re.search(r"^probe pix: vertices4096 32768 32768 196608 81920 81920 229376$", r.stdout, re.M), r.stdout
    r = run("--mock", "probe", "--tri", "pixel", "--tri-unit", "12", str(pix))
    assert r.returncode == 2, r.stdout + r.stderr


@pytest.mark.parametrize("slot", ["pixel", "vtxuse"])
def test_tri_refuses_an_absolute_branch(tmp_path, slot):
    # A ba counts from the code base, but the slot is not at it (record E770): refused, a br
    # (relative) branch is accepted.
    loop = "mov.skipinv r0, #1\n{BR}\nmov.skipinv.end o0, #1\n"
    ba = assemble(tmp_path, "ba", PHAS + loop.replace("{BR}", "p0 ba #4"))
    br = assemble(tmp_path, "br", PHAS + loop.replace("{BR}", "p0 br #1"))
    vp = assemble(tmp_path, "vp", (ROOT / "asm" / "tri" / "pds_vtx.s").read_text(), "pds")

    def probe(prog):
        if slot == "vtxuse":
            return run("--mock", "probe", "--tri", "vtxpds:8", "--slot", f"vtxuse={prog}", str(vp))
        return run("--mock", "probe", "--tri", slot, str(prog))

    r = probe(ba)
    assert r.returncode == 3, r.stdout + r.stderr
    assert f"a ba in the --tri {slot} slot counts from the code base: use br" in r.stderr
    r = probe(br)
    assert r.returncode == 0, r.stdout + r.stderr


def test_tri_probe_unit_0_and_int32_vertices(tmp_path):
    pix = assemble(tmp_path, "pix", PHAS + "mov.skipinv.end o0, pa0\n")
    r = run("--mock", "probe", "--tri", "pixel", "--tri-unit", "0", "--tri-v",
            "-2147483648,2147483647,0,0,5,5", str(pix))
    assert r.returncode == 0, r.stdout + r.stderr
    assert re.search(r"^probe pix: vertices1 -2147483648 2147483647 0 0 5 5$", r.stdout,
                     re.M), r.stdout
    r = run("--mock", "probe", "--tri", "pixel", "--tri-unit", "21", "--tri-v",
            "0,0,1,1,2,2", str(pix))
    assert r.returncode == 2, r.stdout + r.stderr
