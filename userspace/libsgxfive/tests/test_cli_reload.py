# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""sgxfive-test tri options of round 22 (P2), against the mock:

  --bg-pds FILE:N --bg-pixel FILE: the background object's primary PDS program (N data dwords)
      and pixel shader, put into every render's scene as probe --tri's bgpds and bgpixel slots
      are (patched the same way, the shader with 32 temporaries), so that E442's reload
      (probes/dpm/templates/bg_reload_1024.s and pds_bg_pos.s) runs in a geometry final (Q038);
      accepted with -n, --geometry, --final-pb-pages, --depth and --refill, refused with
      --bg-layer;
  --keep-target K (2 <= K <= -n): the library writes no sentinel (and no --refill K:fb) before
      render K, whose report counts against render K - 1's readback, not the CPU reference:
      `tri WxH #K: target kept, X pixels changed, colours ...`;
  --ctx2-geometry N (with --ctx2): the second context's render N is a geometry kick, followed in
      the same iteration by the second context's closing render; with --kept-copy DIR,
      DIR/kept.geo.N.bin is copied between the two (Q191).
Run through `make check`, which builds the binary and sets SGXFIVE_TEST."""
from __future__ import annotations

import json
import os
import pathlib
import re
import subprocess
import sys

import pytest

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent
TOOL = os.environ.get("SGXFIVE_TEST", str(HERE.parent / "build" / "sgxfive-test"))
DPM = ROOT / "probes" / "dpm" / "templates"
PHAS = "phas #0, #0, pixel, end, parallel\n"


def run(*args: str, dbg: pathlib.Path | None = None) -> subprocess.CompletedProcess[str]:
    """The tool; with dbg, its debugfs there (render_final_pb_pages, kpoke made for it)."""
    env = dict(os.environ)
    if dbg is not None:
        env["SGXFIVE_DEBUGFS"] = str(dbg)
        env["SGXFIVE_KPOKE"] = str(dbg / "kpoke")
        for k in ("render_final_pb_pages", "kpoke"):
            if not (dbg / k).exists():
                (dbg / k).write_text("0x0\n" if k != "kpoke" else "")
    return subprocess.run([TOOL, *args], capture_output=True, text=True, timeout=120, env=env)


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


@pytest.fixture
def e442(tmp_path):
    """E442's reload programs: (pds_bg_pos.bin:12, bg_reload_1024.bin)."""
    pds = assemble(tmp_path, "pds_bg_pos", (DPM / "pds_bg_pos.s").read_text(), "pds")
    pix = assemble(tmp_path, "bg_reload_1024", (DPM / "bg_reload_1024.s").read_text())
    return f"{pds}:12", str(pix)


def fill_shader(tmp_path, colour: int) -> pathlib.Path:
    return assemble(tmp_path, f"fill{colour:08x}", PHAS + f"mov.skipinv.end o0, #0x{colour:08X}\n")


ZL = ("tri", "--width", "1024", "--height", "768", "-n", "2", "--geometry", "1",
      "--final-pb-pages", "0x100")


def test_e442_reload_in_a_geometry_final_with_the_target_kept(tmp_path, e442):
    """r21's zl form with E442's reload and --keep-target 2: the programs are put in, render 1
    is a geometry kick, render 2 closes the scene on the kept target and is counted against
    render 1's readback (the mock draws nothing for a geometry kick: every pixel changed)."""
    pds, pix = e442
    r = run("--mock", *ZL, "--bg-pds", pds, "--bg-pixel", pix, "--keep-target", "2",
            dbg=tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    out = r.stdout
    assert ("tri: background object's programs: primary pds_bg_pos (12 data dwords), pixel "
            "shader bg_reload_1024 (32 temporaries)\n") in out, out
    assert "tri: render 2 on the target as render 1 left it (--keep-target)\n" in out, out
    assert "tri 1024x768 #1: geometry only, the scene left open\n" in out, out
    m = re.search(r"^tri 1024x768 #2: target kept, (\d+) pixels changed, colours (.*); "
                  r"guard (\d+)$", out, re.M)
    assert m and m[1] == str(1024 * 768) and m[3] == "0", out
    cols = re.findall(r"0x([0-9a-f]{8}) (\d+)", m[2])
    assert sum(int(n) for _, n in cols) == 1024 * 768, m[2]
    assert "tri: 2 renders ok" in out, out


def test_the_keep_report_counts_against_the_last_readback():
    """Without a geometry kick: render 1 draws green on 0xff203040, render 2 red on 0xff000080
    over it, every pixel changed; the colours are render 2's, most first."""
    r = run("--mock", "tri", "--width", "64", "--height", "64", "-n", "2", "--keep-target", "2")
    assert r.returncode == 0, r.stdout + r.stderr
    m = re.search(r"^tri 64x64 #2: target kept, (\d+) pixels changed, colours "
                  r"0xff000080 (\d+), 0xffff0000 (\d+); guard 0$", r.stdout, re.M)
    assert m and m[1] == "4096" and int(m[2]) + int(m[3]) == 4096, r.stdout
    assert re.search(r"^diff: 4096 of 4096 pixels, first \(0, 0\) 0xff000080 expected "
                     r"0xff203040 \(render 1's\)$", r.stdout, re.M), r.stdout
    # render 1 is checked against the CPU reference as ever
    assert re.search(r"^tri 64x64 #1: \d+ triangle, \d+ background, 0 other; wrong 0 inside",
                     r.stdout, re.M), r.stdout


def test_an_unchanged_kept_render_counts_zero():
    """Render 3 repeats render 1's colours over render 2: every pixel changed back; with -n 3
    --keep-target 3 only render 3 is kept."""
    r = run("--mock", "tri", "--width", "64", "--height", "64", "-n", "3", "--keep-target", "3")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "tri 64x64 #3: target kept, 4096 pixels changed" in r.stdout, r.stdout
    assert "#2: target kept" not in r.stdout


def test_the_background_shader_reaches_the_scene_of_every_render(tmp_path):
    """A limm fill as the background's pixel shader: the mock paints the background with it in
    both renders (the scene hook runs on each), with and without a bgpds of ours in front."""
    pix = fill_shader(tmp_path, 0xff102030)
    pds = assemble(tmp_path, "pos", (DPM / "pds_bg_pos.s").read_text(), "pds")
    for extra in ([], ["--bg-pds", f"{pds}:12"]):
        r = run("--mock", "tri", "--width", "64", "--height", "64", "-n", "2", "--keep-going",
                "--bg-pixel", str(pix), *extra, "--pixels")
        rows = re.findall(r"^row \d+:(.*)$", r.stdout, re.M)
        assert len(rows) == 128, r.stdout + r.stderr
        for k in (0, 64):
            px = " ".join(rows[k:k + 64]).split()
            assert "0xff102030" in px and "0xff203040" not in px and "0xff000080" not in px, extra


@pytest.mark.parametrize("extra", [
    ["--depth"],
    ["--refill", "2:fb=0x11223344"],
    ["--depth", "--refill", "2:depth=0x3f000000"],
])
def test_accepted_with(tmp_path, e442, extra):
    """Every render with our background is checked on its triangle only (the background is the
    programs', not the reference's): `; background ours, not checked`."""
    pds, pix = e442
    r = run("--mock", "tri", "--width", "64", "--height", "64", "-n", "2", "--geometry", "1",
            "--bg-pds", pds, "--bg-pixel", pix, *extra, dbg=tmp_path)
    assert r.returncode == 0, (extra, r.stdout + r.stderr)
    assert re.search(r"^tri 64x64 #2: \d+ triangle, \d+ background, \d+ other; wrong 0 inside, "
                     r"\d+ outside, \d+ at edges; \d+ if flipped; guard 0; background ours, not "
                     r"checked$", r.stdout, re.M), r.stdout


def test_refill_of_the_target_before_a_kept_render_is_refused(e442):
    r = run("--mock", "tri", "--width", "64", "--height", "64", "-n", "2", "--keep-target", "2",
            "--refill", "2:fb=0x11223344")
    assert r.returncode == 2 and "--keep-target" in r.stderr, r.stdout + r.stderr
    r = run("--mock", "tri", "--width", "64", "--height", "64", "-n", "3", "--keep-target", "3",
            "--refill", "2:fb=0x11223344")
    assert r.returncode == 0, r.stdout + r.stderr


@pytest.mark.parametrize("args", [
    ["--keep-target", "1", "-n", "2"],
    ["--keep-target", "3", "-n", "2"],
    ["--keep-target", "0", "-n", "2"],
    ["--keep-target", "x", "-n", "2"],
    ["--keep-target", "2", "--keep-target", "2", "-n", "2"],
    ["--keep-target", "2", "-n", "2", "--ctx2"],
])
def test_keep_target_refusals(args):
    r = run("--mock", "tri", "--width", "64", "--height", "64", *args)
    assert r.returncode == 2, (args, r.stdout + r.stderr)
    assert r.stdout == "" and "keep-target" in r.stderr, (args, r.stderr)


def test_options_are_for_tri(e442):
    pds, pix = e442
    for args in (["--keep-target", "2"], ["--bg-pds", pds], ["--bg-pixel", pix],
                 ["--ctx2-geometry", "1"]):
        r = run("--mock", "fill", *args)
        assert r.returncode == 2, (args, r.stdout + r.stderr)


@pytest.mark.parametrize("spec", ["", ":12", "{pds}", "{pds}:0", "{pds}:3", "{pds}:132",
                                  "{pds}:x"])
def test_bg_pds_needs_its_data_dwords(e442, spec):
    pds = e442[0].rsplit(":", 1)[0]
    r = run("--mock", "tri", "--bg-pds", spec.format(pds=pds))
    assert r.returncode != 0 and r.stdout == "", (spec, r.stdout + r.stderr)


def test_bg_pixel_takes_no_data_and_one_file(e442):
    pds, pix = e442
    for args in (["--bg-pixel", f"{pix}:4"], ["--bg-pixel", pix, "--bg-pixel", pix],
                 ["--bg-pds", pds, "--bg-pds", pds], ["--bg-pixel", "/nonexistent.bin"]):
        r = run("--mock", "tri", *args)
        assert r.returncode != 0 and r.stdout == "", (args, r.stdout + r.stderr)


def test_a_program_that_does_not_fit_is_refused_before_any_device_call(tmp_path):
    """The programs are checked as sgxfive_tri_probe_apply would put them (exit 2, before the
    device): a bgpixel past its page's end, and a ba (a branch from the code base)."""
    long_pix = tmp_path / "long.bin"
    long_pix.write_bytes(fill_shader(tmp_path, 0xff102030).read_bytes() * 100)  # 200 > 128
    ba = assemble(tmp_path, "ba", PHAS + "ba #0\nmov.skipinv.end o0, #0x1\n")
    for f in (long_pix, ba):
        r = run("--mock", "tri", "--bg-pixel", str(f))
        assert r.returncode == 2 and r.stdout == "", (f.name, r.stdout + r.stderr)
        assert "--bg-pixel" in r.stderr, r.stderr


def test_refused_with_the_layered_background(e442):
    pds, pix = e442
    r = run("--mock", "--mock-knob", "render_bg_layer=1", "--mock-knob",
            "render_bg_src=0x3e800000", "tri", "--bg-layer", "--bg-pds", pds, "--bg-pixel", pix)
    assert r.returncode == 2 and r.stdout == "", r.stdout + r.stderr
    assert "--bg-layer" in r.stderr and "--bg-pds" in r.stderr, r.stderr


def test_refused_with_the_layer_knob_on(e442):
    """The knob render_bg_layer on would make the kernel build the layer over our programs."""
    pds, pix = e442
    r = run("--mock", "--mock-knob", "render_bg_layer=1", "--mock-knob",
            "render_bg_src=0x3e800000", "tri", "--bg-pds", pds, "--bg-pixel", pix)
    assert r.returncode == 2 and r.stdout == "", r.stdout + r.stderr
    assert "render_bg_layer" in r.stderr


def test_probe_tri_still_emits_the_background_slots(tmp_path, e442):
    """probe --tri --slot bgpds/bgpixel --emit-scene: the slot programs in the pages, as before."""
    pds, pix = e442
    pdsf, _ = pds.rsplit(":", 1)
    prog = assemble(tmp_path, "pixel", PHAS + "mov.skipinv.end o0, #0xFF00FF00\n")
    out = tmp_path / "tri.json"
    r = run("--mock", "probe", "--tri", "pixel", "--slot", f"bgpixel={pix}", "--slot",
            f"bgpds={pds}", "--emit-scene", str(out), str(prog))
    assert r.returncode == 0, r.stdout + r.stderr
    s = json.loads(out.read_text())
    mem = {m["role"]: m["dwords"] for m in s["memory"]}

    def dw(v):
        return int(v, 16) if isinstance(v, str) else v

    want = pathlib.Path(pdsf).read_bytes()
    got = b"".join(dw(v).to_bytes(4, "little") for v in mem["pdsp"][0xc00 // 4 + 2:
                                                                    0xc00 // 4 + len(want) // 4])
    assert got == want[8:], "the bgpds program is not at 0xc00 of the pixel PDS page"
    first = b"".join(dw(v).to_bytes(4, "little") for v in mem["usep"][0xc00 // 4 + 2:0xc00 // 4 + 4])
    assert first == pathlib.Path(pix).read_bytes()[8:16]


# ---- --ctx2-geometry N (Q191) ------------------------------------------------------------

def kept_pages(n: int) -> bytes:
    return b"".join(i.to_bytes(4, "little") * 1024 for i in range(n))


def test_ctx2_geometry_kick_then_its_closing_render(tmp_path):
    """The second context's render 1 is a geometry kick that leaves its scene open (the mock as
    for the first context's), then its closing render in the same iteration, checked as ever;
    kept.geo.1.bin between the two, kept.1.bin after the closing render."""
    (tmp_path / "render_kept").write_bytes(kept_pages(3))
    out = tmp_path / "out"
    out.mkdir()
    r = run("--mock", "tri", "--width", "64", "--height", "64", "-n", "1", "--ctx2",
            "--close-first-early", "--ctx2-geometry", "1", "--kept-copy", str(out),
            dbg=tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    assert (out / "kept.geo.1.bin").read_bytes() == kept_pages(3)
    assert (out / "kept.1.bin").read_bytes() == kept_pages(3)
    lines = r.stdout.splitlines()
    order = ["tri: closed the first context",
             "tri2 64x64 #1: geometry only, the scene left open",
             "tri: render_kept after the second context's geometry kick, before its closing "
             f"render 1: {out}/kept.geo.1.bin (12288 bytes)",
             "tri2 64x64 #1: closing render",
             "tri2 64x64 #1: ",
             "tri: render_kept after the second context's render 1:"]
    at = []
    for k in order:
        at.append(next(i for i, ln in enumerate(lines) if ln.startswith(k) and i not in at))
    assert at == sorted(at), r.stdout
    assert re.search(r"^tri2 64x64 #1: \d+ triangle, \d+ background, 0 other; wrong 0 inside",
                     r.stdout, re.M), r.stdout
    assert sum(ln == "job: ok" for ln in lines) == 3, r.stdout


def test_ctx2_geometry_copy_reads_again_while_parking(tmp_path):
    """The park race of t20 (E1085): right after the early close the kept copy can read empty;
    the geometry kick's copy reads again while it is empty, as the copy after the close does.

    The race is a window: the copy must start after the close and before the 150 ms park ends.
    On a machine under heavy load the tool can be descheduled past the park, the first read
    then finds the bytes and says nothing about reading again, with no code change. So the
    window is tried up to 5 times, each in a fresh directory, and what it checks is unchanged:
    every attempt must succeed and copy the whole kept data, and at least one must have read
    again and say so. A real failure (the copy never reads again) fails every attempt."""
    pat = re.compile(r"^tri: render_kept read \d+ times after the second context's geometry "
                     r"kick, before its closing render 1 \(empty \d+, 10 ms apart\): "
                     r"8192 bytes$", re.M)
    last = ""
    for attempt in range(5):
        d = tmp_path / f"a{attempt}"
        d.mkdir()
        (d / "render_kept").write_bytes(kept_pages(2))
        out = d / "out"
        out.mkdir()
        r = run("--mock", "--mock-park-ms=150", "tri", "--width", "64", "--height", "64", "-n",
                "1", "--ctx2", "--close-first-early", "--ctx2-geometry", "1", "--kept-copy",
                str(out), dbg=d)
        assert r.returncode == 0, r.stdout + r.stderr
        assert (out / "kept.geo.1.bin").read_bytes() == kept_pages(2)
        last = r.stdout
        if pat.search(r.stdout):
            return
    assert pat.search(last), last


def test_ctx2_geometry_only_in_its_iteration(tmp_path):
    """-n 2 --ctx2-geometry 2: the second context's render 1 is a whole render, render 2 the
    geometry kick and its closing render."""
    r = run("--mock", "tri", "--width", "64", "--height", "64", "-n", "2", "--ctx2",
            "--ctx2-geometry", "2")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "tri2 64x64 #1: geometry only" not in r.stdout
    assert "tri2 64x64 #2: geometry only, the scene left open" in r.stdout, r.stdout
    assert "tri: 2 renders ok" in r.stdout, r.stdout


@pytest.mark.parametrize("args", [
    ["--ctx2-geometry", "1"],                                   # no --ctx2
    ["--ctx2", "--ctx2-geometry", "2"],                         # N > n
    ["--ctx2", "--ctx2-geometry", "0"],
    ["--ctx2", "--ctx2-geometry", "x"],
    ["--ctx2", "--ctx2-geometry", "1", "--ctx2-geometry", "1"],
    ["--ctx2", "--ctx2-geometry", "1", "--final-pb-pages", "0x100"],
    ["--ctx2", "--ctx2-geometry", "1", "--overlap"],
])
def test_ctx2_geometry_refusals(args):
    r = run("--mock", "tri", "--width", "64", "--height", "64", "-n", "1", *args)
    assert r.returncode == 2, (args, r.stdout + r.stderr)
    assert r.stdout == "", (args, r.stdout)
