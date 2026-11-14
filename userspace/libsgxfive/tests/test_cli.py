# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""sgxfive-test against the in-process mock (--mock): every subcommand, its output and exit
status. Run through `make check`, which builds the binary and sets SGXFIVE_TEST."""
from __future__ import annotations

import os
import pathlib
import re
import subprocess

import pytest

HERE = pathlib.Path(__file__).resolve().parent
TOOL = os.environ.get("SGXFIVE_TEST", str(HERE.parent / "build" / "sgxfive-test"))


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([TOOL, *args], capture_output=True, text=True, timeout=30)


@pytest.fixture(scope="module", autouse=True)
def tool_exists():
    if not pathlib.Path(TOOL).exists():
        pytest.skip(f"{TOOL} not built (run make -C userspace/libsgxfive check)")


def test_usage_without_command():
    r = run()
    assert r.returncode == 2
    assert "usage" in r.stderr


def test_unknown_command():
    r = run("--mock", "frobnicate")
    assert r.returncode == 2
    assert run("--mock", "q4").returncode == 2      # the register-access probe is regaccess


def test_usage_names_every_command():
    usage = run().stderr
    for cmd in ("query", "dummy", "fill", "copy", "isolation", "tri", "contexts", "regaccess",
                "probe"):
        assert re.search(rf"\b{cmd}\b", usage), cmd
    for opt in ("--every-value", "--poke", "--pixels", "--regs", "--low", "--late", "--isp2",
                "--blk-add", "--vtx-coords", "--obj2", "--pbe", "--ramp", "--print-addrs",
                "--page-before", "--place", "bgpixel", "N^=V", "--tri-full", "--tri-z",
                "--depth-store", "--stencil", "--stencil-store", "--stencil-fill",
                "--depth-store-fill", "--stencil-store-fill", "--refill"):
        assert opt in usage, opt


def test_query_rev1():
    r = run("--mock", "query")
    assert r.returncode == 0, r.stderr
    out = r.stdout
    assert re.search(r"^device\s+/dev/dri/renderD128$", out, re.M)
    assert re.search(r"^core_id\s+0x01150000$", out, re.M)
    assert re.search(r"^quirks\s+0x1 SAMPLE_CACHE$", out, re.M)
    assert re.search(r"^max_updates\s+0$", out, re.M)
    assert re.search(r"^heap GENERAL\s+base 0x3e000000 size 0xb1fff000$", out, re.M)
    assert re.search(r"^heap KERNEL_CODE\s+base 0x30000000 size 0x0007f000 RESERVED$",
                     out, re.M)
    assert re.search(r"^heap USSE_PIXEL\s+base 0x37000000 size 0x00500000 FIXED_WINDOWS$",
                     out, re.M)


def test_query_harness_layout():
    r = run("--mock=harness", "query")
    assert r.returncode == 0, r.stderr
    assert re.search(r"^heap PDS_PIXEL\s+base 0xe4000000 ", r.stdout, re.M)
    assert re.search(r"^heap TEXTURE\s+absent$", r.stdout, re.M)


def test_no_device_found():
    r = run("--mock=none", "query")
    assert r.returncode == 1
    assert "no sgxfive render node" in r.stderr


def test_dummy_chain():
    r = run("--mock", "dummy", "-n", "16")
    assert r.returncode == 0, r.stderr
    assert "dummy: 16 jobs ok" in r.stdout


@pytest.mark.parametrize("args", [
    [],
    ["--width", "32", "--height", "16", "--x", "8", "--y", "4", "--stride", "320"],
    ["--width", "33", "--height", "16", "--x", "8", "--y", "4", "--stride", "320"],
    ["--width", "1", "--height", "1", "--x", "5", "--y", "7"],
])
@pytest.mark.parametrize("layout", ["rev1", "harness"])
def test_fill(layout, args):
    r = run(f"--mock={layout}", "fill", *args)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "fill: ok" in r.stdout


def test_fill_rejects_odd_stride():
    r = run("--mock", "fill", "--stride", "260")
    assert r.returncode == 1
    assert "Invalid argument" in r.stderr


@pytest.mark.parametrize("args", [
    [],
    ["--width", "32", "--height", "16", "--sx", "5", "--sy", "3", "--src-stride", "320",
     "--dx", "8", "--dy", "4", "--dst-stride", "288"],
    ["--width", "33", "--height", "16"],
])
def test_copy(args):
    r = run("--mock", "copy", *args)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "copy: ok" in r.stdout


def test_isolation():
    r = run("--mock", "isolation")
    assert r.returncode == 0, r.stdout + r.stderr
    checks = re.findall(r"^(PASS|FAIL) (\S+)$", r.stdout, re.M)
    assert [c for c, _ in checks] == ["PASS"] * 9
    assert {n for _, n in checks} == {
        "kernel-heap-unmappable", "same-address-separate-vms", "other-vm-address-faults",
        "lost-context-cancelled", "other-context-survives", "read-only-faults",
        "queued-innocent-job-reruns", "fault-recovered-quickly",
        "faulting-file-banned",
    }


@pytest.mark.parametrize("cmd", ["fill", "copy", "isolation"])
def test_fake_programs_still_run_on_the_mock(cmd):
    r = run("--mock", "--programs=fake", cmd)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "programs fake" in r.stdout


@pytest.mark.parametrize("cmd", ["fill", "copy"])
def test_assembled_programs_by_default(cmd):
    r = run("--mock", cmd)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "programs asm" in r.stdout


def test_fake_programs_refused_on_hardware():
    # Without --mock the tool would use the real backend; the fake program source must
    # never be sent to the GPU, so it is refused before opening anything.
    r = run("--device", "/nonexistent", "--programs=fake", "fill")
    assert r.returncode == 2
    assert "fake program source" in r.stderr


def test_hardware_fill_needs_no_mock():
    # The assembled programs are real: without --mock, fill goes to the device.
    r = run("--device", "/nonexistent", "fill")
    assert r.returncode == 1
    assert "/nonexistent" in r.stderr and "program" not in r.stderr


def test_unknown_program_source():
    assert run("--mock", "--programs=fw", "fill").returncode == 2


def test_regaccess_probe_words_are_their_source():
    """Each regaccess probe word is usse-asm's encoding of the source in its comment."""
    import sys
    sys.path.insert(0, str(HERE.parent.parent.parent / "tools" / "fwcutter"))
    import ours  # builds usse-asm on demand
    src = (HERE.parent / "tools" / "sgxfive-test.c").read_text()
    lines = re.findall(r"0x([0-9A-F]{16})ull,\s*/\* ([^(*]+?)\s*(?:\([^)]*\))? \*/", src)
    assert len(lines) == 25
    asm = "\n".join(text for _, text in lines) + "\n"
    r = subprocess.run([str(ours._tool("usse")), "-o", "/dev/stdout", "-"], input=asm.encode(),
                       capture_output=True, check=True)
    words = [int.from_bytes(r.stdout[i:i + 8], "little") for i in range(0, len(r.stdout), 8)]
    assert words == [int(w, 16) for w, _ in lines]


def test_regaccess_runs_on_the_mock():
    r = run("--mock", "regaccess")
    assert r.returncode == 0, r.stdout + r.stderr
    assert re.search(r"^ldr-core-id: ", r.stdout, re.M)
    assert re.search(r"^str-use-g0: ", r.stdout, re.M)


def test_query_render():
    r = run("--mock", "query")
    assert r.returncode == 0, r.stderr
    assert re.search(r"^job_types\s+0x3$", r.stdout, re.M)
    assert re.search(r"^render_cmd\s+0x68 pb 0x422 pages max 4096x4096$", r.stdout, re.M)
    assert re.search(r"^heap PARAMETERS\s+base 0x10000000 size 0x10000000 RESERVED$",
                     r.stdout, re.M)
    assert re.search(r"^heap TA_DATA\s+base 0x20000000 size 0x0d000000 RESERVED$",
                     r.stdout, re.M)


@pytest.mark.parametrize("size", [None, ("64", "64"), ("256", "128"), ("128", "32"),
                                  ("256", "256"), ("100", "60"), ("1024", "768")])
def test_tri(size):
    args = ["--mock", "tri", "-n", "2"]
    if size:
        args += ["--width", size[0], "--height", size[1]]
    r = run(*args)
    assert r.returncode == 0, r.stdout + r.stderr
    w, h = size or ("64", "64")
    assert re.search(rf"^tri {w}x{h} #1: \d+ triangle, \d+ background, 0 other; "
                     r"wrong 0 inside, 0 outside, 0 at edges; \d+ if flipped; guard 0$",
                     r.stdout, re.M), r.stdout
    assert "tri: 2 renders ok" in r.stdout


@pytest.mark.parametrize("overlap", [False, True])
def test_tri_second_context(overlap):
    # a second render context in the VM, the same scene in its own colours, each render checked
    # against its own triangle; --overlap submits both before waiting for either
    r = run("--mock", "tri", "-n", "2", "--ctx2", *(["--overlap"] if overlap else []))
    assert r.returncode == 0, r.stdout + r.stderr
    assert "tri: second render context" in r.stdout
    for i in (1, 2):
        assert re.search(rf"^tri2 64x64 #{i}: \d+ triangle, \d+ background, 0 other; "
                         r"wrong 0 inside, 0 outside, 0 at edges; \d+ if flipped; guard 0$",
                         r.stdout, re.M), r.stdout
    assert "tri: 2 renders ok" in r.stdout


def test_tri_share_pb_asks_the_kernel_before_the_second_context(tmp_path, monkeypatch):
    (tmp_path / "render_share_pb").write_text("N\n")
    monkeypatch.setenv("SGXFIVE_DEBUGFS", str(tmp_path))
    r = run("--mock", "tri", "--ctx2", "--share-pb")
    assert r.returncode == 0, r.stdout + r.stderr
    assert (tmp_path / "render_share_pb").read_text().strip() == "Y"
    assert "tri: second render context shares the first's parameter buffer" in r.stdout


def test_tri_share_pb_needs_the_second_context():
    r = run("--mock", "tri", "--share-pb")
    assert r.returncode == 2
    r = run("--mock", "tri", "--overlap")
    assert r.returncode == 2
    r = run("--mock", "fill", "--ctx2")
    assert r.returncode == 2


def test_tri_share_pb_without_debugfs_fails(tmp_path, monkeypatch):
    monkeypatch.setenv("SGXFIVE_DEBUGFS", str(tmp_path / "none"))
    r = run("--mock", "tri", "--ctx2", "--share-pb")
    assert r.returncode == 1
    assert "render_share_pb" in r.stderr


FINAL_ARGS = ("tri", "--width", "1024", "--height", "768", "-n", "2", "--geometry", "1")


def test_tri_final_pb_pages_writes_the_knob_before_the_context_and_the_final_render_fits(
        tmp_path, monkeypatch):
    # the kernel's PB is read once, at the context's creation: --final-pb-pages writes debugfs
    # render_final_pb_pages before it, and the context's final render after the geometry kick
    # has that PB (0x23 pages overflow 1024 x 768 in the mock, 0x40 take it)
    (tmp_path / "render_final_pb_pages").write_text("0x0\n")
    monkeypatch.setenv("SGXFIVE_DEBUGFS", str(tmp_path))
    r = run("--mock-pb-pages=0x23", "--mock", *FINAL_ARGS, "--final-pb-pages", "0x40")
    assert r.returncode == 0, r.stdout + r.stderr
    assert (tmp_path / "render_final_pb_pages").read_text().strip() == "0x40"
    assert "tri: final renders' PB 0x40 pages (debugfs render_final_pb_pages)" in r.stdout
    assert "tri: 2 renders ok" in r.stdout
    (tmp_path / "render_final_pb_pages").write_text("0x0\n")
    r = run("--mock-pb-pages=0x23", "--mock", *FINAL_ARGS)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "overflowed" in r.stdout + r.stderr
    assert (tmp_path / "render_final_pb_pages").read_text().strip() == "0x0"


def test_tri_final_pb_pages_without_debugfs_fails(tmp_path, monkeypatch):
    monkeypatch.setenv("SGXFIVE_DEBUGFS", str(tmp_path / "none"))
    r = run("--mock", *FINAL_ARGS, "--final-pb-pages", "0x40")
    assert r.returncode == 1
    assert "render_final_pb_pages" in r.stderr


@pytest.mark.parametrize("args", [
    ("tri", "-n", "2", "--final-pb-pages", "0x40"),                  # no geometry kick
    ("tri", "--final-pb-pages", "0x40"),
    (*FINAL_ARGS, "--final-pb-pages", "0x22"),                        # the kernel's range
    (*FINAL_ARGS, "--final-pb-pages", "0x423"),
    (*FINAL_ARGS, "--final-pb-pages", "0"),
    (*FINAL_ARGS, "--final-pb-pages", "64x"),
    (*FINAL_ARGS, "--final-pb-pages", "0x40", "--final-pb-pages", "0x41"),
    ("fill", "--final-pb-pages", "0x40"),
])
def test_tri_final_pb_pages_is_refused_strictly(args):
    r = run("--mock", *args)
    assert r.returncode == 2, (args, r.stdout + r.stderr)


@pytest.mark.parametrize("overlap", [[], ["--overlap"]])
def test_tri_second_context_kpoke(tmp_path, monkeypatch, overlap):
    # --kpoke-render2 writes its poke just before the second context's render N, so that the
    # kernel applies it to that context's kick, not the first's
    kp = tmp_path / "kpoke"
    kp.write_text("")
    monkeypatch.setenv("SGXFIVE_KPOKE", str(kp))
    r = run("--mock", "tri", "-n", "2", "--ctx2", *overlap,
            "--kpoke-render2", "2:ctx:7=0xdeadbeef")
    assert r.returncode == 0, r.stdout + r.stderr
    assert kp.read_text() == "ctx:7=0xdeadbeef\n"
    assert "tri: kpoke before second-context render 2: ctx:7=0xdeadbeef" in r.stdout
    assert "tri: kpoke before render" not in r.stdout


@pytest.mark.parametrize("args", [["--kpoke-render2", "1:ctx:7=1"],
                                  ["--ctx2", "--kpoke-render2", "3:ctx:7=1", "-n", "2"],
                                  ["--ctx2", "--kpoke-render2", "x"]])
def test_tri_kpoke_render2_bounds(args):
    r = run("--mock", "tri", *args)
    assert r.returncode in (1, 2)
    assert r.returncode == 2 or "bad --kpoke-render2" in r.stderr


def test_tri_default_is_the_first_triangle():
    r = run("--mock", "tri", "-n", "1")
    assert r.returncode == 0, r.stdout + r.stderr
    m = re.search(r"^tri 64x64 #1: (\d+) triangle, (\d+) background", r.stdout, re.M)
    assert m and int(m.group(1)) + int(m.group(2)) == 4096
    assert 1000 < int(m.group(1)) < 1100       # 1062 on the hardware


def test_tri_rejects_sizes_the_kernel_refuses():
    r = run("--mock", "tri", "--width", "4098")
    assert r.returncode == 1
    assert "Invalid argument" in r.stderr


def test_tri_needs_render_heaps():
    r = run("--mock=harness", "tri")
    assert r.returncode == 1


def test_tri_context_maximum_is_the_target_by_default():
    r = run("--mock", "tri", "--width", "128", "--height", "32")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "tri: render context for targets up to 128x32" in r.stdout


def test_tri_within_a_larger_maximum():
    r = run("--mock", "tri", "--width", "64", "--height", "64",
            "--max-width", "1024", "--max-height", "600")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "tri: render context for targets up to 1024x600" in r.stdout
    assert "tri: 1 renders ok" in r.stdout


@pytest.mark.parametrize("args", [
    ["--width", "128", "--max-width", "64"],        # wider than the context's maximum
    ["--height", "66", "--max-height", "64"],       # taller
])
def test_tri_beyond_the_context_maximum(args):
    r = run("--mock", "tri", *args)
    assert r.returncode == 1
    assert "render: Invalid argument" in r.stderr


@pytest.mark.parametrize("args", [["--max-width", "4097"], ["--max-height", "0"]])
def test_tri_context_maximum_bounds(args):
    r = run("--mock", "tri", *args)
    assert r.returncode == 1
    assert "render context: Invalid argument" in r.stderr


def test_tri_scene_overflowing_the_parameter_buffer():
    # The mock's PB as debugfs render_pb_pages sets the kernel's: 0x62 pages take 1024x768
    # but not 4096x4096, whose job fails with -ENOSPC; the context is not lost.
    r = run("--mock", "--mock-pb-pages=0x62", "query")
    assert r.returncode == 0, r.stdout + r.stderr
    assert re.search(r"^render_cmd +0x[0-9a-f]+ pb 0x62 pages", r.stdout, re.M), r.stdout
    r = run("--mock", "--mock-pb-pages=0x62", "tri", "--width", "1024", "--height", "768")
    assert r.returncode == 0, r.stdout + r.stderr
    r = run("--mock", "--mock-pb-pages=0x62", "tri", "--width", "4096", "--height", "4096")
    assert r.returncode == 1
    assert ("sgxfive-test: render: scene overflowed the parameter buffer, context kept "
            "(No space left on device)") in r.stderr, r.stderr
    assert "tri: FAILED after 0 renders" in r.stdout


@pytest.mark.parametrize("args", [["--mock-pb-pages=0x22", "--mock"],
                                  ["--mock-pb-pages=0x423", "--mock"],
                                  ["--mock-pb-pages=x", "--mock"],
                                  ["--mock-pb-pages=0x62"]])     # the mock's only
def test_mock_pb_pages_bounds(args):
    r = run(*args, "query")
    assert r.returncode == 2


def test_contexts_reports_memory_per_context():
    r = run("--mock", "contexts", "-n", "32", "--width", "64", "--height", "64")
    assert r.returncode == 0, r.stdout + r.stderr
    assert re.search(r"^contexts: 32 render contexts for targets up to 64x64: ", r.stdout,
                     re.M), r.stdout
    assert "contexts: destroyed" in r.stdout


def test_contexts_stops_at_the_vm_limit():
    r = run("--mock", "contexts", "-n", "33")
    assert r.returncode == 1
    assert "render context 33: No space left on device" in r.stderr


# ---- probe: run our own assembled programs as the fill shader ---------------------------

def assemble(tmp_path, name: str, source: str) -> pathlib.Path:
    """Assemble USSE source with tools/usse-asm into tmp_path/name.bin."""
    import sys
    sys.path.insert(0, str(HERE.parent.parent.parent / "tools" / "fwcutter"))
    import ours  # builds usse-asm on demand
    out = tmp_path / f"{name}.bin"
    subprocess.run([str(ours._tool("usse")), "-o", str(out), "-"], input=source.encode(),
                   capture_output=True, check=True)
    return out


PHAS = "phas #0, #0, pixel, end, parallel\n"


def test_probe_reports_the_uniform_result(tmp_path):
    # The mock's interpreter takes the colour from the second instruction's immediate.
    f = assemble(tmp_path, "colour", PHAS + "mov.skipinv.end o0, #0x12345678\n")
    r = run("--mock", "probe", str(f))
    assert r.returncode == 0, r.stdout + r.stderr
    assert re.search(r"^probe colour: o0 0x12345678 \(2048 of 2048\)$", r.stdout, re.M), r.stdout


def test_probe_runs_every_file_in_its_own_fill(tmp_path):
    a = assemble(tmp_path, "a", PHAS + "mov.skipinv.end o0, #0x0000000A\n")
    b = assemble(tmp_path, "b", PHAS + "mov.skipinv.end o0, #0x0000000B\n")
    r = run("--mock", "probe", "--temps", "16", str(a), str(b))
    assert r.returncode == 0, r.stdout + r.stderr
    assert re.findall(r"^probe (\w+): o0 (0x\w+) ", r.stdout, re.M) == [
        ("a", "0x0000000a"), ("b", "0x0000000b")]


@pytest.mark.parametrize("k", [0x10, 0x8000, 0xfffc])
def test_probe_patches_scratch_immediates(tmp_path, k):
    # An immediate 0x5CAFnnnn is replaced by the 64 KiB scratch buffer's address + nnnn.
    f = assemble(tmp_path, "scr", PHAS + f"mov.skipinv.end o0, #0x{0x5CAF0000 | k:08X}\n")
    r = run("--mock", "probe", str(f))
    assert r.returncode == 0, r.stdout + r.stderr
    m = re.search(r"^probe scr: scratch at (0x\w+) \(64 KiB\)$", r.stdout, re.M)
    assert m, r.stdout
    o0 = re.search(r"^probe scr: o0 (0x\w+) ", r.stdout, re.M)
    assert int(o0.group(1), 16) == int(m.group(1), 16) + k


def pds_secondary(out: str, name: str) -> tuple[int, int]:
    """(address, offset in the pixel PDS heap) of the PDS secondary the probe printed."""
    m = re.search(rf"^probe {name}: PDS secondary at (0x[0-9a-f]+) \(pixel PDS heap base \+ "
                  rf"(0x[0-9a-f]+)\)$", out, re.M)
    assert m, out
    return int(m.group(1), 16), int(m.group(2), 16)


@pytest.mark.parametrize("k", [0, 0x10, 0xfff0])
def test_probe_patches_pds_references(tmp_path, k):
    # An immediate 0x5CB0nnnn is replaced by the PDS secondary's offset in the pixel PDS heap
    # shifted right by four, plus nnnn: the s1 an emitpds names that program with. 0x5CB1nnnn is
    # the same from the program's GPU address. The printed line says where the program is.
    rel = assemble(tmp_path, "rel", PHAS + f"mov.skipinv.end o0, #0x{0x5CB00000 | k:08X}\n")
    ab = assemble(tmp_path, "ab", PHAS + f"mov.skipinv.end o0, #0x{0x5CB10000 | k:08X}\n")
    r = run("--mock", "probe", str(rel), str(ab))
    assert r.returncode == 0, r.stdout + r.stderr
    for name, want in (("rel", lambda a, o: (o >> 4) + k), ("ab", lambda a, o: (a >> 4) + k)):
        addr, off = pds_secondary(r.stdout, name)
        assert addr % 16 == 0 and off % 16 == 0 and off > 0 and addr >= off
        o0 = re.search(rf"^probe {name}: o0 (0x\w+) ", r.stdout, re.M)
        assert int(o0.group(1), 16) == want(addr, off) & 0xffffffff, r.stdout


def test_probe_leaves_other_pds_immediates_alone(tmp_path):
    # only 0x5CB0nnnn and 0x5CB1nnnn are references; 0x5CB2nnnn and 0x5CAFnnnn keep their meaning
    f = assemble(tmp_path, "other", PHAS + "mov.skipinv.end o0, #0x5CB20010\n")
    r = run("--mock", "probe", str(f))
    assert r.returncode == 0, r.stdout + r.stderr
    assert re.search(r"^probe other: o0 0x5cb20010 ", r.stdout, re.M), r.stdout


def test_probe_patches_pds_references_in_a_placed_program(tmp_path):
    # the program --place maps is patched too, whatever order the programs are built in
    base = assemble(tmp_path, "base", PHAS + "mov.skipinv.end o0, #0x0000BA5E\n")
    use = assemble(tmp_path, "use", PHAS + "mov.skipinv.end o0, #0x5CB00020\n")
    r = run("--mock", "probe", "--place", f"0x100000={use}", "--place-form", "cbase", str(base))
    assert r.returncode == 0, r.stdout + r.stderr
    _, off = pds_secondary(r.stdout, "base")
    o0 = re.search(r"^probe base: o0 (0x\w+) ", r.stdout, re.M)
    assert int(o0.group(1), 16) == (off >> 4) + 0x20, r.stdout


def test_probe_pds_takes_coords(tmp_path):
    # --pds N --use USE with --coords: the PDS secondary of a copy, whose shader reads the texel
    # coordinates in pa0 (a probe that lets one instance act, such as an emitpds, tests pa0);
    # the mock does not run PDS programs: the options are accepted and the probe names the copy's
    # PDS secondary (at pixel PDS heap base + 0x40, the s1 of 4 an emitpds uses, E488)
    import sys
    sys.path.insert(0, str(HERE.parent.parent.parent / "tools" / "fwcutter"))
    import ours
    pds = tmp_path / "pds.bin"
    subprocess.run([str(ours._tool("pds")), "-o", str(pds), "-"],
                   input=b".word 0, 0, 0, 0\n.word 0, 0, 0, 0\nhalt\n", capture_output=True,
                   check=True)
    use = assemble(tmp_path, "use", PHAS + "mov.skipinv.end o0, #0x5CB00020\n")
    r = run("--mock", "probe", "--pds", "8", "--use", str(use), "--coords", str(pds))
    assert r.returncode == 3, r.stdout + r.stderr
    assert "usage" not in r.stderr
    _, off = pds_secondary(r.stdout, "pds")
    assert off == 0x40, r.stdout
    assert run("--mock", "probe", "--pds", "8", "--coords", str(pds)).returncode == 2  # no --use


def test_probe_scratch_pages(tmp_path):
    # --scratch-pages N (16 to 256): a larger scratch buffer, for a texture chain that does not
    # fit 64 KiB; the immediates 0x5CAFnnnn still add nnnn (up to 64 KiB) to its address
    f = assemble(tmp_path, "big", PHAS + "mov.skipinv.end o0, #0x5CAF0010\n")
    r = run("--mock", "probe", "--scratch-pages", "24", str(f))
    assert r.returncode == 0, r.stdout + r.stderr
    m = re.search(r"^probe big: scratch at (0x\w+) \(96 KiB\)$", r.stdout, re.M)
    assert m, r.stdout
    o0 = re.search(r"^probe big: o0 (0x\w+) ", r.stdout, re.M)
    assert int(o0.group(1), 16) == int(m.group(1), 16) + 0x10
    for bad in ("15", "257", "x"):
        assert run("--mock", "probe", "--scratch-pages", bad, str(f)).returncode == 2, bad
    # 256 pages (1 MiB): E1033's second fault page, scratch + 0x40000, lies inside
    r = run("--mock", "probe", "--scratch-pages", "256", str(f))
    assert r.returncode == 0, r.stdout + r.stderr
    assert re.search(r"^probe big: scratch at 0x\w+ \(1024 KiB\)$", r.stdout, re.M), r.stdout


@pytest.mark.parametrize("order", ["low-first", "pages-first"])
def test_probe_low_and_scratch_pages_are_checked_together(tmp_path, order):
    # --low maps the whole scratch buffer, so low + pages x 4 KiB must stay within 1 MiB
    # whichever option comes first on the command line
    f = assemble(tmp_path, "lp", PHAS + "mov.skipinv.end o0, #1\n")

    def probe(low, pages):
        a, b = ["--low", low], ["--scratch-pages", pages]
        return run("--mock", "probe", *(a + b if order == "low-first" else b + a), str(f))

    assert probe("0xf0000", "64").returncode == 2           # 16 pages at parse time, 64 in all
    # ends exactly at 1 MiB; the mock's job fails there (3), the check passed
    assert probe("0xf0000", "16").returncode == 3
    assert probe("0xc0000", "64").returncode == 3           # 64 pages end at 0x100000
    assert probe("0x1000", "256").returncode == 2           # 1 MiB never fits past page 0
    assert probe("0x1000", "255").returncode == 3           # 255 pages end at 0x100000


@pytest.mark.parametrize("order", ["late-first", "pages-first"])
def test_probe_late_is_checked_against_the_scratch_pages(tmp_path, order):
    # --late's dwords lie in the scratch buffer, whose size --scratch-pages sets, whichever
    # option comes first: dword 20000 is past 16 pages (16384 dwords) but within 24 (24576)
    f = assemble(tmp_path, "lq", PHAS + "mov.skipinv.end o0, #1\n")

    def probe(late, pages):
        a, b = ["--late", late], ["--scratch-pages", pages]
        return run("--mock", "probe", *(a + b if order == "late-first" else b + a), str(f))

    assert probe("0:20000=1", "24").returncode == 0
    assert probe("0:20000=1", "16").returncode == 2
    assert probe("0:24576=1", "24").returncode == 2
    assert probe("0:262143=1", "256").returncode == 0       # the last dword of 1 MiB
    assert probe("0:262144=1", "256").returncode == 2


def pixel_rows(out: str, name: str) -> dict:
    """--pixels output: {y: [64 values]}."""
    rows = {}
    for y, vals in re.findall(rf"^probe {name}: row (\d+): ([0-9a-f ]+)$", out, re.M):
        rows[int(y)] = [int(v, 16) for v in vals.split()]
    return rows


def test_probe_pixels_prints_every_pixel(tmp_path):
    f = assemble(tmp_path, "px", PHAS + "mov.skipinv.end o0, #0x12345678\n")
    r = run("--mock", "probe", "--pixels", str(f))
    assert r.returncode == 0, r.stdout + r.stderr
    rows = pixel_rows(r.stdout, "px")
    assert sorted(rows) == list(range(32)), r.stdout
    assert all(v == [0x12345678] * 64 for v in rows.values())
    # the summary line is still there
    assert re.search(r"^probe px: o0 0x12345678 \(2048 of 2048\)$", r.stdout, re.M)


def test_probe_without_pixels_prints_no_rows(tmp_path):
    f = assemble(tmp_path, "px", PHAS + "mov.skipinv.end o0, #0x12345678\n")
    r = run("--mock", "probe", str(f))
    assert not pixel_rows(r.stdout, "px")


def test_probe_coords_runs_the_program_as_a_copy_of_the_coordinates(tmp_path):
    # --coords: the program is the copy shader of a 64x32 copy whose source texel (x, y)
    # is (y << 16) | x, so pa0 holds the pixel's coordinates (on the mock: the copy shader
    # itself, the only one its interpreter runs).
    f = assemble(tmp_path, "xy", PHAS + "mov.skipinv.end o0, pa0\n")
    r = run("--mock", "probe", "--temps", "8", "--coords", "--pixels", str(f))
    assert r.returncode == 0, r.stdout + r.stderr
    rows = pixel_rows(r.stdout, "xy")
    assert sorted(rows) == list(range(32)), r.stdout
    for y, vals in rows.items():
        assert vals == [(y << 16) | x for x in range(64)], y
    assert re.search(r"^probe xy: o0 mixed ", r.stdout, re.M)


def test_probe_coords_reports_other_programs_as_failed_on_the_mock(tmp_path):
    # The mock knows no other copy shader: a hang, the job fails, as a fill's would.
    f = assemble(tmp_path, "other", PHAS + "mov.skipinv.end o0, #1\n")
    r = run("--mock", "probe", "--coords", str(f))
    assert r.returncode == 3, r.stdout + r.stderr
    assert re.search(r"^probe other: failed: job faulted", r.stdout, re.M), r.stdout


@pytest.mark.parametrize("args", [["--pixels"], ["--coords"], ["--temps", "8", "--coords"]])
def test_probe_options_need_a_file(args):
    r = run("--mock", "probe", *args)
    assert r.returncode == 2


@pytest.mark.parametrize("args", [[], ["--temps", "0"], ["--temps", "200"]])
def test_probe_usage(tmp_path, args):
    f = assemble(tmp_path, "x", PHAS + "mov.skipinv.end o0, #1\n")
    r = run("--mock", "probe", *args, *([str(f)] if args else []))
    assert r.returncode == 2


@pytest.mark.parametrize("v", ["0", "0x800", "0x100000", "0x200000", "x"])
def test_probe_low_takes_a_page_in_the_first_mib(tmp_path, v):
    # --low ADDR: the scratch buffer mapped again at ADDR, a page of the first MiB but page 0
    f = assemble(tmp_path, "x", PHAS + "mov.skipinv.end o0, #1\n")
    r = run("--mock", "probe", "--low", v, str(f))
    assert r.returncode == 2, r.stdout + r.stderr


def test_probe_low_is_refused_without_the_kernels_vm_low(tmp_path):
    # the mock checks VM_MAP against the heaps, as the kernel does with debugfs vm_low off
    f = assemble(tmp_path, "lo", PHAS + "mov.skipinv.end o0, #1\n")
    r = run("--mock", "probe", "--low", "0x10000", str(f))
    assert r.returncode == 3, r.stdout + r.stderr
    assert re.search(r"^probe lo: failed: scratch at 0x00010000: Invalid argument$", r.stdout,
                     re.M), r.stdout


@pytest.mark.parametrize("v", ["1:2", "1=2", "16384:0=1", "0:16384=1", "1:2=0x100000000",
                               "x:2=3", "1:2=3:4", "5:5=1"])
def test_probe_late_takes_ready_dword_and_value(tmp_path, v):
    # --late R:K=V: once scratch dword R leaves its fill, the host writes V to dword K
    f = assemble(tmp_path, "x", PHAS + "mov.skipinv.end o0, #1\n")
    r = run("--mock", "probe", "--late", v, str(f))
    assert r.returncode == 2, r.stdout + r.stderr


def test_probe_late_writes_the_dword_while_the_job_runs(tmp_path):
    # the mock's shader never sets the ready dword: the host writes after its wait, says so,
    # and the readback shows the dword it wrote
    f = assemble(tmp_path, "lt", PHAS + "mov.skipinv.end o0, #1\n")
    r = run("--mock", "probe", "--late", "128:64=0x12345678", str(f))
    assert r.returncode == 0, r.stdout + r.stderr
    assert re.search(r"^probe lt: late: ready \(scratch \+0x200\) not seen in \d+ us; "
                     r"scratch \+0x100 = 0x12345678 written$", r.stdout, re.M), r.stdout
    assert re.search(r"^probe lt: scratch \+0x100 0x12345678$", r.stdout, re.M), r.stdout


def test_probe_rejects_a_bad_file(tmp_path):
    odd = tmp_path / "odd.bin"
    odd.write_bytes(b"\0" * 12)
    r = run("--mock", "probe", str(odd))
    assert r.returncode == 1
    assert "odd.bin" in r.stderr
    r = run("--mock", "probe", str(tmp_path / "missing.bin"))
    assert r.returncode == 1


def test_probe_reports_a_surface_left_untouched(tmp_path):
    # A probe whose job completes without writing a pixel leaves the surface's 0xdeadbeef
    # sentinel (on the mock: a program colouring with it).
    f = assemble(tmp_path, "nopix", PHAS + "mov.skipinv.end o0, #0xDEADBEEF\n")
    r = run("--mock", "probe", str(f))
    assert r.returncode == 3, r.stdout + r.stderr
    assert re.search(r"^probe nopix: failed: no pixel written$", r.stdout, re.M), r.stdout


def test_probe_reports_a_failed_job(tmp_path):
    # A probe that faults or hangs is recovered and its job fails, which the wait reports
    # (on the mock a fill shader that is not a limm mov is an unknown program: a hang that
    # loses the context, its job's fence failing with -EIO).
    f = assemble(tmp_path, "hang", PHAS + "nop.end\n")
    g = assemble(tmp_path, "good", PHAS + "mov.skipinv.end o0, #0x0000000A\n")
    r = run("--mock", "probe", str(f), str(g))
    assert r.returncode == 3, r.stdout + r.stderr
    assert re.search(r"^probe hang: failed: job faulted, context lost \(Input/output error\)$",
                     r.stdout, re.M), r.stdout
    assert re.search(r"^probe hang: scratch unchanged$", r.stdout, re.M), r.stdout
    # The next probe runs in a context of its own.
    assert re.search(r"^probe good: o0 0x0000000a ", r.stdout, re.M), r.stdout


def test_regaccess_reports_failed_jobs():
    # On the mock the regaccess programs other than fills are unknown programs, so their jobs
    # fail and the file is banned after three; each probe says so.
    r = run("--mock", "regaccess")
    assert r.returncode == 0, r.stdout + r.stderr
    assert re.search(r"^ldr-core-id: job failed: job faulted, context lost "
                     r"\(Input/output error\)$", r.stdout, re.M), r.stdout
    assert re.search(r"^kick-code-base-15: failed: Operation canceled$", r.stdout, re.M), \
        r.stdout


def test_tri_reports_a_failed_render():
    # --fault unmaps the scene's stream page before the render: the job faults and the
    # wait reports it.
    r = run("--mock", "tri", "--fault")
    assert r.returncode == 1, r.stdout + r.stderr
    assert "sgxfive-test: render: job faulted, context lost (Input/output error)" in r.stderr


def test_copy_ramp_counts_one_channel(tmp_path):
    # --ramp CH=START [--ramp-base V]: channel CH is START + the pixel's index (modulo 256), the
    # other channels V's; the copy is checked against that source
    r = run("--mock", "copy", "--ramp", "g=100", "--ramp-base", "0xff0000ff", "--width", "32",
            "--height", "2", "--src-stride", "256", "--pixels")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "copy: ok" in r.stdout and "diff: 0 of 64 pixels" in r.stdout, r.stdout
    row0 = re.search(r"^row 0: (.*)$", r.stdout, re.M).group(1).split()
    assert row0[:3] == ["0xff0064ff", "0xff0065ff", "0xff0066ff"], row0
    row1 = re.search(r"^row 1: (.*)$", r.stdout, re.M).group(1).split()
    assert row1[0] == "0xff00a4ff", row1       # 64 pixels (stride 256 bytes) on: 100 + 64
    for ch, shift in (("a", 24), ("r", 16), ("b", 0)):
        r = run("--mock", "copy", "--ramp", f"{ch}=255", "--width", "4", "--height", "1",
                "--pixels")
        row0 = re.search(r"^row 0: (.*)$", r.stdout, re.M).group(1).split()
        assert row0[:2] == [f"0x{0xff << shift:08x}", f"0x{0:08x}"], (ch, row0)


@pytest.mark.parametrize("args", [
    ["--ramp", "x=1"], ["--ramp", "g=256"], ["--ramp", "g"], ["--ramp", "g=1", "--every-value"],
    ["--ramp-base", "0xff"], ["--ramp", "g=1", "--ramp", "r=2"],
])
def test_copy_ramp_usage(args):
    assert run("--mock", "copy", *args).returncode == 2


def test_copy_ramp_is_for_copy():
    for cmd in ("fill", "tri"):
        r = run("--mock", cmd, "--ramp", "g=1")
        assert r.returncode == 2, (cmd, r.stdout + r.stderr)


def test_copy_prints_addresses_and_a_counting_page_before():
    # --print-addrs: where the source and destination lie; --page-before: the source's buffer
    # has a counting page before it, so the source starts one page into its buffer
    r = run("--mock", "copy", "--print-addrs")
    assert r.returncode == 0, r.stdout + r.stderr
    a = re.search(r"^copy: source at (0x\w+), destination at (0x\w+)$", r.stdout, re.M)
    assert a, r.stdout
    r = run("--mock", "copy", "--print-addrs", "--page-before")
    assert r.returncode == 0, r.stdout + r.stderr
    b = re.search(r"^copy: source at (0x\w+), destination at (0x\w+), a counting page before "
                  r"the source$", r.stdout, re.M)
    assert b, r.stdout
    assert int(b.group(1), 16) - int(a.group(1), 16) == 4096 or int(b.group(1), 16) % 4096 == 0
    assert "copy: ok" in r.stdout
    assert run("--mock", "fill", "--page-before").returncode == 2


def test_probe_places_a_program_in_the_code_heap(tmp_path):
    # --place OFFSET=FILE --place-form cbase|exe18: FILE mapped at the USSE pixel heap's base +
    # OFFSET and started in place of the fill shader by a primary DOUTU with the offset's bits in
    # EXE and CBASE (cbase) or in an 18-bit EXE (exe18); the mock runs the placed program
    base = assemble(tmp_path, "base", PHAS + "mov.skipinv.end o0, #0x0000BA5E\n")
    use = assemble(tmp_path, "use", PHAS + "mov.skipinv.end o0, #0x61\n")
    # (offset, form, bits 21:0 of the DOUTU)
    for off, form, bits in ((0x100000, "cbase", 0x000002), (0x100000, "exe18", 0x200000),
                            (0x400000, "cbase", 0x000008), (0x400000, "exe18", 0x000000),
                            (0x10008, "cbase", 0x020010), (0x10008, "exe18", 0x020010)):
        r = run("--mock", "probe", "--place", f"0x{off:x}={use}", "--place-form", form, str(base))
        assert r.returncode == 0, r.stdout + r.stderr
        kind = "EXE and CBASE" if form == "cbase" else "an 18-bit EXE"
        assert (f"probe base: program placed at 0x{0x37000000 + off:08x} (code heap base + "
                f"0x{off:x}), started as {kind}: DOUTU bits 21:0 0x{bits:06x}") in r.stdout, r.stdout
    for args in (["--place", f"0x400000={use}"],                        # no form
                 ["--place-form", "cbase"],                              # no program
                 ["--place", f"0x400004={use}", "--place-form", "cbase"],
                 ["--place", f"0x500000={use}", "--place-form", "cbase"],
                 ["--place", f"8={use}", "--place", f"16={use}", "--place-form", "cbase"],
                 ["--place", f"8={use}", "--place-form", "bogus"],
                 ["--tri", "pixel", "--place", f"8={use}", "--place-form", "cbase"]):
        r = run("--mock", "probe", *args, str(base))
        assert r.returncode == 2, (args, r.stdout + r.stderr)


def test_probe_scratch_in_the_texture_heap(tmp_path):
    # --scratch-heap texture: the scratch buffer is allocated in the texture heap (0xf0000000 and
    # up on the mock), the program's scratch immediates pointing there; only texture is a heap
    f = assemble(tmp_path, "tx", PHAS + "mov.skipinv.end o0, #0x5CAF0010\n")
    r = run("--mock", "probe", "--scratch-heap", "texture", str(f))
    assert r.returncode == 0, r.stdout + r.stderr
    m = re.search(r"^probe tx: scratch at (0x\w+) \(64 KiB\)$", r.stdout, re.M)
    assert m and 0xf0000000 <= int(m.group(1), 16) < 0x100000000, r.stdout
    assert f"0x{int(m.group(1), 16) + 0x10:08x}" in r.stdout, r.stdout
    for args in (["--scratch-heap", "general"], ["--scratch-heap"], ["--tri", "pixel",
                                                                         "--scratch-heap", "texture"]):
        assert run("--mock", "probe", *args, str(f)).returncode == 2, args


def test_tri_scratch_at_maps_the_pages_where_asked():
    # --scratch-at ADDR: the --scratch pages mapped at ADDR (a heap's second page, where a unit
    # of the render fetches from) instead of allocated in the general heap
    r = run("--mock", "tri", "--scratch", "1", "--scratch-at", "0x2e001000", "--scratch-fill",
            "0xd1d1d1d1")
    assert r.returncode == 0, r.stdout + r.stderr
    assert re.search(r"^scratch: 0x2e001000 1 pages, fill 0xd1d1d1d1$", r.stdout, re.M), r.stdout
    r = run("--mock", "tri", "--scratch", "1", "--scratch-at", "0x2e001")      # not page-aligned
    assert r.returncode != 0, r.stdout + r.stderr
    assert "--scratch-at" in run().stderr


def test_tri_scratch_file_fills_the_scratch_pages_from_a_file(tmp_path):
    # --scratch-file FILE: the first dwords of the --scratch pages are the file's (a table the host
    # built), the rest --scratch-fill; the report counts the dwords a render changed against that
    f = tmp_path / "table.bin"
    f.write_bytes(bytes.fromhex("11111111" "22222222"))
    r = run("--mock", "tri", "--scratch", "1", "--scratch-fill", "0x5a5a5a5a", "--scratch-file",
            str(f))
    assert r.returncode == 0, r.stdout + r.stderr
    assert re.search(r"^scratch: 0x[0-9a-f]{8} 1 pages, fill 0x5a5a5a5a, file 2 dwords$", r.stdout,
                     re.M), r.stdout
    assert re.search(r"^scratch: 0 dwords changed$", r.stdout, re.M), r.stdout


@pytest.mark.parametrize("size", [3, 4098 * 2, 0])
def test_tri_scratch_file_is_checked(tmp_path, size):
    # a multiple of 4 bytes, not empty, no longer than the scratch pages
    f = tmp_path / "bad.bin"
    f.write_bytes(bytes(size))
    r = run("--mock", "tri", "--scratch", "1", "--scratch-file", str(f))
    assert r.returncode == 2, r.stdout + r.stderr
    assert "--scratch-file" in r.stderr


def test_tri_scratch_file_needs_scratch_pages_and_a_readable_file(tmp_path):
    f = tmp_path / "t.bin"
    f.write_bytes(bytes(8))
    assert run("--mock", "tri", "--scratch-file", str(f)).returncode == 2
    r = run("--mock", "tri", "--scratch", "1", "--scratch-file", str(tmp_path / "none.bin"))
    assert r.returncode == 2
    assert "--scratch-file" in r.stderr


def test_tri_close_first_closes_the_first_context_before_the_second(tmp_path, monkeypatch):
    # --close-first: the first context (the donor, with --share-pb) is closed before the second;
    # the default closes the second first
    (tmp_path / "render_share_pb").write_text("N\n")
    monkeypatch.setenv("SGXFIVE_DEBUGFS", str(tmp_path))
    r = run("--mock", "tri", "-n", "1", "--ctx2", "--share-pb", "--close-first")
    assert r.returncode == 0, r.stdout + r.stderr
    assert re.search(r"^tri: closing the first context before the second$", r.stdout, re.M)
    r = run("--mock", "tri", "-n", "1", "--ctx2", "--share-pb")
    assert r.returncode == 0, r.stdout + r.stderr
    assert re.search(r"^tri: closing the second context before the first$", r.stdout, re.M)


def test_tri_close_first_needs_the_second_context():
    assert run("--mock", "tri", "--close-first").returncode == 2
    assert run("--mock", "fill", "--ctx2", "--close-first").returncode == 2


def test_tri_close_trace_prints_the_kernel_trace_after_each_close(tmp_path, monkeypatch):
    # --close-trace: after each context is closed, the debugfs render_cleanup lines and dwords 32,
    # 46 and 47 of the TA/3D control block (debugfs buf09), so that the cleanup of each is seen
    (tmp_path / "render_share_pb").write_text("N\n")
    (tmp_path / "render_cleanup").write_text("rtds 0x1 ctx 0x2 pbdesc 0x3 flags 0x0 ret 0\n"
                                             "pb ta 0x00000000 3d 0x00000000\n")
    words = [0] * 64
    words[32], words[46], words[47] = 0x32411380, 0x11, 0x22
    (tmp_path / "buf09").write_bytes(b"".join(w.to_bytes(4, "little") for w in words))
    monkeypatch.setenv("SGXFIVE_DEBUGFS", str(tmp_path))
    for first, second in (("second", "first"), ("first", "second")):
        args = ["--close-first"] if first == "first" else []
        r = run("--mock", "tri", "-n", "1", "--ctx2", "--share-pb", "--close-trace", *args)
        assert r.returncode == 0, r.stdout + r.stderr
        for which in (first, second):
            assert (f"cleanup after closing the {which} context: "
                    "rtds 0x1 ctx 0x2 pbdesc 0x3 flags 0x0 ret 0") in r.stdout
            assert (f"cleanup after closing the {which} context: "
                    "pb ta 0x00000000 3d 0x00000000") in r.stdout
            assert (f"ta3dctl after closing the {which} context: dword 32 0x32411380, "
                    "dword 46 0x00000011, dword 47 0x00000022") in r.stdout
        # and again 500 ms after both are closed (a deferred release may run the donor's cleanup)
        assert ("cleanup 500 ms after both are closed: "
                "rtds 0x1 ctx 0x2 pbdesc 0x3 flags 0x0 ret 0") in r.stdout
        assert ("ta3dctl 500 ms after both are closed: dword 32 0x32411380, "
                "dword 46 0x00000011, dword 47 0x00000022") in r.stdout
        assert r.stdout.index(f"closing the {first} context") < r.stdout.index(
            f"cleanup after closing the {first} context")
        assert r.stdout.index(f"cleanup after closing the {first} context") < r.stdout.index(
            f"cleanup after closing the {second} context")


def test_tri_close_trace_needs_the_second_context():
    assert run("--mock", "tri", "--close-trace").returncode == 2
    assert run("--mock", "fill", "--ctx2", "--close-trace").returncode == 2


def test_tri_wait_second_waits_for_the_second_job_first():
    # --wait-second (with --overlap): the second context's job is waited for before the first's,
    # so that a first job that never ends does not hide whether the second ran
    r = run("--mock", "tri", "-n", "2", "--ctx2", "--overlap", "--wait-second")
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stdout.count("tri: waiting for the second context's job first") == 2
    assert r.stdout.count("job: ok") == 4
    assert "tri: 2 renders ok" in r.stdout
    assert re.search(r"^tri2 64x64 #2: .*wrong 0 inside, 0 outside, 0 at edges; .*guard 0$",
                     r.stdout, re.M), r.stdout


def test_tri_wait_second_needs_overlap():
    assert run("--mock", "tri", "--ctx2", "--wait-second").returncode == 2
    assert run("--mock", "tri", "--wait-second").returncode == 2
    assert run("--mock", "fill", "--ctx2", "--overlap", "--wait-second").returncode == 2


def test_probe_stamp_prints_the_jobs_wall_clock_window(tmp_path):
    # probe --stamp: the job's start and end in CLOCK_REALTIME ns (the time of the submission and of
    # the wait's return), to place a write from another process inside the job
    import time
    f = assemble(tmp_path, "stm", PHAS + "mov.skipinv.end o0, #0x1\n")
    before = time.time_ns()
    r = run("--mock", "probe", "--stamp", str(f))
    after = time.time_ns()
    assert r.returncode == 0, r.stdout + r.stderr
    m = re.search(r"^probe stm: job window (\d+) (\d+) ns$", r.stdout, re.M)
    assert m, r.stdout
    start, end = int(m.group(1)), int(m.group(2))
    assert before <= start <= end <= after
    assert "job window" not in run("--mock", "probe", str(f)).stdout


def test_probe_stamp_is_a_flag_of_probe_only(tmp_path):
    assert run("--mock", "tri", "--stamp").returncode == 2


def test_dummy_kpoke_job_writes_before_its_job(tmp_path, monkeypatch):
    # dummy --kpoke-job N:SPEC writes SPEC to debugfs kpoke just before job N is submitted, so
    # that the kernel applies it to that job (th:N, a transfer context's HW context, is taken
    # at the next transfer submitted, a dummy too)
    kp = tmp_path / "kpoke"
    kp.write_text("")
    monkeypatch.setenv("SGXFIVE_KPOKE", str(kp))
    r = run("--mock", "dummy", "-n", "3", "--kpoke-job", "2:th:0=0x10", "--wait-ms", "1000")
    assert r.returncode == 0, r.stdout + r.stderr
    assert kp.read_text() == "th:0=0x10\n"
    assert "dummy: kpoke before job 2: th:0=0x10" in r.stdout
    assert "dummy: 3 jobs ok" in r.stdout


@pytest.mark.parametrize("args", [
    ["dummy", "-n", "3", "--kpoke-job", "4:th:0=1"],
    ["dummy", "-n", "3", "--kpoke-job", "0:th:0=1"],
    ["dummy", "--kpoke-job", "x"],
    ["tri", "--kpoke-job", "1:th:0=1"],
    ["fill", "--kpoke-job", "2:th:0=1"],
    ["copy", "--kpoke-job", "1:th:0=1"],
    ["fill", "--wait-ms", "100"],
    ["dummy", "--wait-ms", "0"],
])
def test_dummy_options_are_checked(args):
    r = run("--mock", *args)
    assert r.returncode == 2, r.stdout + r.stderr


def test_dummy_without_kpoke_file_fails(tmp_path, monkeypatch):
    monkeypatch.setenv("SGXFIVE_KPOKE", str(tmp_path / "none"))
    r = run("--mock", "dummy", "--kpoke-job", "1:th:1=1")
    assert r.returncode == 1


def test_tri_kreg_render_writes_before_its_render(tmp_path, monkeypatch):
    # --kreg-render N:OFF=V writes the register to debugfs kregnow just before render N of the
    # first context, --kreg-render2 before the second context's (a write the host does not usually make
    # holds until the SGX is reset)
    (tmp_path / "kregnow").write_text("")
    monkeypatch.setenv("SGXFIVE_DEBUGFS", str(tmp_path))
    r = run("--mock", "tri", "-n", "2", "--kreg-render", "2:0x0740=0x200")
    assert r.returncode == 0, r.stdout + r.stderr
    assert (tmp_path / "kregnow").read_text() == "0x0740=0x200\n"
    assert "tri: kregnow before render 2: 0x0740=0x200" in r.stdout
    (tmp_path / "kregnow").write_text("")
    r = run("--mock", "tri", "-n", "1", "--ctx2", "--kreg-render2", "1:0x0740^=0x1000")
    assert r.returncode == 0, r.stdout + r.stderr
    assert (tmp_path / "kregnow").read_text() == "0x0740^=0x1000\n"
    assert "tri: kregnow before second-context render 1: 0x0740^=0x1000" in r.stdout
    assert "tri: kregnow before render" not in r.stdout


@pytest.mark.parametrize("args", [["--kreg-render2", "1:0x0740=1"],
                                  ["--kreg-render", "3:0x0740=1", "-n", "2"],
                                  ["--kreg-render", "x"],
                                  ["--kreg-render", "0:0x0740=1"]])
def test_tri_kreg_render_bounds(args):
    r = run("--mock", "tri", *args)
    assert r.returncode == 2, r.stdout + r.stderr


def test_tri_kreg_render_without_debugfs_fails(tmp_path, monkeypatch):
    monkeypatch.setenv("SGXFIVE_DEBUGFS", str(tmp_path / "none"))
    r = run("--mock", "tri", "--kreg-render", "1:0x0740=1")
    assert r.returncode == 1


def test_tri_close_first_early(tmp_path, monkeypatch):
    # --close-first-early: in the last iteration the first context is closed after its render and
    # before the second context's, with --words a snapshot before the close (N = 100 + the render) and one after it (200 +)
    dbg, out = tmp_path / "dbg", tmp_path / "w"
    dbg.mkdir()
    out.mkdir()
    (dbg / "render_words").write_text("ctx:0=0x00000011\n")
    (dbg / "buf09").write_bytes(bytes(256))
    monkeypatch.setenv("SGXFIVE_DEBUGFS", str(dbg))
    r = run("--mock", "tri", "-n", "2", "--ctx2", "--close-first-early", "--words", str(out))
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stdout.count("tri: closed the first context before the second context's render 2") == 1
    assert "render 1:" not in r.stdout
    for n in (0, 1, 2, 102, 202):
        assert (out / f"words.{n}.txt").exists(), n
        assert (out / f"ta3d.{n}.bin").exists(), n
    assert not (out / "words.101.txt").exists()
    assert not (out / "words.201.txt").exists()
    assert re.search(r"^tri2 64x64 #2: ", r.stdout, re.M)
    assert "tri: 2 renders ok" in r.stdout
    assert "tri: closing the second context before the first" not in r.stdout


@pytest.mark.parametrize("args", [["tri", "--close-first-early"],
                                  ["tri", "--ctx2", "--close-first-early", "--close-first"],
                                  ["tri", "--ctx2", "--close-first-early", "--overlap"],
                                  ["fill", "--ctx2", "--close-first-early"]])
def test_tri_close_first_early_is_checked(args):
    r = run("--mock", *args)
    assert r.returncode == 2, r.stdout + r.stderr


def test_fill_kpoke_job_writes_before_its_job(tmp_path, monkeypatch):
    # fill has one job: --kpoke-job 1:SPEC is written to debugfs kpoke just before it
    kp = tmp_path / "kpoke"
    kp.write_text("")
    monkeypatch.setenv("SGXFIVE_KPOKE", str(kp))
    r = run("--mock", "fill", "--kpoke-job", "1:th:0=0x2")
    assert r.returncode == 0, r.stdout + r.stderr
    assert kp.read_text() == "th:0=0x2\n"
    assert "fill: kpoke before job 1: th:0=0x2" in r.stdout
    assert "fill: ok" in r.stdout


def test_tri_words_between_saves_a_snapshot_before_the_second_contexts_render(tmp_path,
                                                                             monkeypatch):
    # --words-between: with --ctx2 and --words, before the second context's render N the words
    # are saved again as N = 100 + the render, the first context still open
    dbg, out = tmp_path / "dbg", tmp_path / "w"
    dbg.mkdir()
    out.mkdir()
    (dbg / "render_words").write_text("ctx:0=0x00000011\n")
    (dbg / "buf09").write_bytes(bytes(256))
    monkeypatch.setenv("SGXFIVE_DEBUGFS", str(dbg))
    r = run("--mock", "tri", "-n", "2", "--ctx2", "--words-between", "--words", str(out))
    assert r.returncode == 0, r.stdout + r.stderr
    for n in (0, 1, 2, 101, 102):
        assert (out / f"words.{n}.txt").exists(), n
        assert (out / f"ta3d.{n}.bin").exists(), n
    assert not (out / "words.201.txt").exists()
    assert "tri: closed the first context" not in r.stdout
    assert "tri: 2 renders ok" in r.stdout


@pytest.mark.parametrize("args", [["tri", "--words-between"],
                                  ["tri", "--ctx2", "--words-between"],
                                  ["tri", "--ctx2", "--words-between", "--overlap",
                                   "--words", "/tmp"],
                                  ["fill", "--ctx2", "--words-between"]])
def test_tri_words_between_is_checked(args):
    r = run("--mock", *args)
    assert r.returncode == 2, r.stdout + r.stderr


def test_tri_keep_overflow_reports_the_overflowed_render_and_goes_on(tmp_path):
    # An overflowing scene fails the run by default; --keep-overflow counts it, prints its
    # target's colours as a render's line (the mock draws nothing) and goes on to the next
    # render, exiting 0 when no render failed otherwise
    args = ("--mock", "--mock-pb-pages=0x62", "tri", "--width", "4096", "--height", "4096",
            "-n", "2")
    r = run(*args)
    assert r.returncode == 1 and "#2:" not in r.stdout, r.stdout
    r = run(*args, "--keep-overflow")
    assert r.returncode == 0, r.stdout + r.stderr
    lines = re.findall(r"^tri 4096x4096 #(\d): overflowed, (\d+) triangle, (\d+) background",
                       r.stdout, re.M)
    assert [n for n, _, _ in lines] == ["1", "2"], r.stdout
    assert r.stdout.count("job: failed: scene overflowed the parameter buffer") == 2
    assert "tri: 0 of 2 renders ok, 2 overflowed" in r.stdout


def test_tri_keep_overflow_does_not_hide_other_failures():
    # a render that fits still checks as before; the mock's fitting 1024x768 job is ok
    r = run("--mock", "--mock-pb-pages=0x62", "tri", "--width", "1024", "--height", "768",
            "--keep-overflow")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "tri: 1 renders ok" in r.stdout and "overflowed," not in r.stdout
    r = run("--mock", "--mock-pb-pages=0x62", "tri", "-n", "2", "--poke", "blk:5^=2",
            "--keep-overflow")
    assert r.returncode == 1, r.stdout + r.stderr


def test_tri_dump_each_dumps_after_every_render_even_an_overflowed_one(tmp_path, monkeypatch):
    # --dump-each: the kernel's render_param and render_tadata after every render N as
    # DIR/tri.N.*.bin, for an overflowed render too (its context is kept, the state page
    # holds the lists a partial render stored); needs --dump-render DIR
    dbg, out = tmp_path / "dbg", tmp_path / "out"
    dbg.mkdir()
    out.mkdir()
    (dbg / "render_param").write_bytes(b"\x11" * 64)
    (dbg / "render_tadata").write_bytes(b"\x22" * 32)
    monkeypatch.setenv("SGXFIVE_DEBUGFS", str(dbg))
    r = run("--mock", "--mock-pb-pages=0x62", "tri", "--width", "4096", "--height", "4096",
            "-n", "2", "--keep-overflow", "--dump-render", str(out), "--dump-each")
    assert r.returncode == 0, r.stdout + r.stderr
    for n in (1, 2):
        assert (out / f"tri.{n}.param.bin").read_bytes() == b"\x11" * 64, n
        assert (out / f"tri.{n}.tadata.bin").read_bytes() == b"\x22" * 32, n
    assert (out / "tri.tadata.bin").exists()
    assert re.search(r"^probe tri\.1: render memory to .* after the failure$", r.stdout, re.M), \
        r.stdout


@pytest.mark.parametrize("args", [["tri", "--dump-each"],
                                  ["tri", "--dump-each", "--keep-overflow"],
                                  ["fill", "--keep-overflow"],
                                  ["copy", "--dump-each", "--dump-render", "/tmp"]])
def test_tri_keep_overflow_and_dump_each_are_checked(args):
    r = run("--mock", *args)
    assert r.returncode == 2, (args, r.stdout + r.stderr)
    assert "bad option" not in r.stderr and \
        ("--keep-overflow" in r.stderr or "--dump-each" in r.stderr), r.stderr


def depth_args(*extra):
    return ("--mock", "tri", "--depth", *extra)


def test_tri_depth_arms_the_zls_pokes_and_reports_the_buffer(tmp_path, monkeypatch):
    # --depth maps a depth buffer for the target (width x height dwords and sixteen pages),
    # fills it (--depth-fill, 1.0f) and before each render arms the render-flag, ZLS-clear,
    # control and both base pokes at it; after the render it reports the dwords it changed
    # and the most frequent values (the mock stores no depth: nothing changes)
    kp = tmp_path / "kpoke"
    kp.write_text("")
    monkeypatch.setenv("SGXFIVE_KPOKE", str(kp))
    r = run(*depth_args("-n", "2"))
    assert r.returncode == 0, r.stdout + r.stderr
    head = re.search(r"^depth: (0x[0-9a-f]{8}) (\d+) pages, fill 0x3f800000, base 0x3e000000, "
                     r"control 0x0017100c$", r.stdout, re.M)
    assert head, r.stdout
    addr, pages = int(head.group(1), 16), int(head.group(2))
    assert addr % 4096 == 0 and pages == 4 + 16
    lines = kp.read_text().split()
    off = addr - 0x3E000000     # the bases are offsets from the ZLS base (rd:1)
    assert lines == ["ta:7^=0x80", "rd:1=0x3e000000", "rd:11=0x0017100c", f"rd:12={off:#x}",
                     f"rd:13={off:#x}"] * 2, lines
    for n in (1, 2):
        assert re.search(rf"^depth #{n}: {pages * 1024} dwords, 0 changed, 1 distinct; 0x3f800000 x "
                         rf"{pages * 1024}$", r.stdout, re.M), r.stdout


def test_tri_depth_options_set_the_words(tmp_path, monkeypatch):
    # --depth-ctl V, --depth-base V, --depth-fill V, --depth-pages N; --depth-ctl-next V for
    # renders 2 on, the buffer then filled before render 1 only (render 2 loads what 1 stored)
    kp = tmp_path / "kpoke"
    kp.write_text("")
    monkeypatch.setenv("SGXFIVE_KPOKE", str(kp))
    r = run(*depth_args("-n", "2", "--depth-ctl", "0x17700e", "--depth-base", "0x3dfff000",
                        "--depth-fill", "0x12345678", "--depth-pages", "6",
                        "--depth-ctl-next", "0x11700a"))
    assert r.returncode == 0, r.stdout + r.stderr
    assert re.search(r"^depth: 0x[0-9a-f]{8} 6 pages, fill 0x12345678, base 0x3dfff000, "
                     r"control 0x0017700e, then 0x0011700a$", r.stdout, re.M), r.stdout
    lines = kp.read_text().split()
    addr = int(re.search(r"^depth: (0x[0-9a-f]{8}) ", r.stdout, re.M).group(1), 16)
    assert "rd:1=0x3dfff000" in lines and f"rd:12={addr - 0x3DFFF000:#x}" in lines, lines
    assert [x for x in lines if x.startswith("rd:11")] == ["rd:11=0x0017700e",
                                                            "rd:11=0x0011700a"], lines
    assert "depth #2: 6144 dwords, 0 changed, 1 distinct; 0x12345678 x 6144" in r.stdout


def test_tri_depth_fill_value_is_counted(tmp_path, monkeypatch):
    # the report's most frequent value is the fill when nothing was stored
    kp = tmp_path / "kpoke"
    kp.write_text("")
    monkeypatch.setenv("SGXFIVE_KPOKE", str(kp))
    r = run(*depth_args("--depth-fill", "0"))
    assert re.search(r"^depth #1: 20480 dwords, 0 changed, 1 distinct; 0x00000000 x 20480$", r.stdout, re.M), \
        r.stdout


@pytest.mark.parametrize("args", [["tri", "--depth-ctl", "1"],
                                  ["tri", "--depth", "--depth-ctl-next", "1"],
                                  ["tri", "--depth", "--depth-pages", "0"],
                                  ["tri", "--depth", "--depth-pages", "4", "--width", "128",
                                   "--height", "128"],
                                  ["fill", "--depth"],
                                  ["tri", "--depth", "--ctx2"]])
def test_tri_depth_is_checked(args):
    r = run("--mock", *args)
    assert r.returncode == 2, (args, r.stdout + r.stderr)
    assert "--depth" in r.stderr and "bad option" not in r.stderr, r.stderr


def test_tri_depth_dump_writes_the_buffer_after_each_render(tmp_path, monkeypatch):
    # --depth-dump DIR: the buffer's bytes after render N as DIR/depth.N.bin, for a layout read
    # on the host (the mock stores no depth: the fill is all there is)
    kp = tmp_path / "kpoke"
    kp.write_text("")
    monkeypatch.setenv("SGXFIVE_KPOKE", str(kp))
    r = run(*depth_args("-n", "2", "--depth-fill", "0x01020304", "--depth-pages", "5",
                        "--depth-dump", str(tmp_path)))
    assert r.returncode == 0, r.stdout + r.stderr
    for n in (1, 2):
        assert (tmp_path / f"depth.{n}.bin").read_bytes() == bytes([4, 3, 2, 1]) * (5 * 1024), n
    r = run(*depth_args("--depth-dump", "/nonexistent/dir"))
    assert "--depth-dump" in r.stdout, r.stdout


def words(path):
    import array
    a = array.array("I")
    a.frombytes(path.read_bytes())
    return a


def test_tri_depth_fill_index_and_bit_patterns(tmp_path, monkeypatch):
    # --depth-fill index: dword i holds i (the address in the value); --depth-fill bit:K: dword i
    # holds 0.75f when bit K of i is set, else 0.25f (a load shows through the pixels' depth
    # test, one bit of the loaded address a render); the report counts a dword that left its
    # pattern value as changed
    kp = tmp_path / "kpoke"
    kp.write_text("")
    monkeypatch.setenv("SGXFIVE_KPOKE", str(kp))
    for fill, want in (("index", lambda i: i),
                       ("bit:3", lambda i: 0x3f400000 if i >> 3 & 1 else 0x3e800000)):
        r = run(*depth_args("--depth-fill", fill, "--depth-pages", "4",
                            "--depth-dump", str(tmp_path)))
        assert r.returncode == 0, r.stdout + r.stderr
        assert re.search(rf"^depth: 0x[0-9a-f]{{8}} 4 pages, fill {fill.replace(':', ' ')}, ",
                         r.stdout, re.M), r.stdout
        assert "depth #1: 4096 dwords, 0 changed," in r.stdout, r.stdout
        w = words(tmp_path / "depth.1.bin")
        assert all(w[i] == want(i) for i in range(4096)), fill


@pytest.mark.parametrize("fill", ["bit", "bit:", "bit:32", "bit:x", "indexed", ""])
def test_tri_depth_fill_is_checked(fill):
    r = run("--mock", "tri", "--depth", "--depth-fill", fill)
    assert r.returncode == 2, (fill, r.stdout + r.stderr)
    assert "--depth-fill" in r.stderr, r.stderr


def test_tri_stencil_and_store_buffers_are_armed_and_dumped(tmp_path, monkeypatch):
    # --depth-store: the store base (rd:13) on a buffer of its own; --stencil: the stencil flag
    # (ta:7 bit 8 too) and both stencil bases (rd:14, rd:15, bit 31 set) on a stencil buffer,
    # --stencil-store: the store base on another; each filled (--depth-store-fill,
    # --stencil-fill, --stencil-store-fill) and dumped
    kp = tmp_path / "kpoke"
    kp.write_text("")
    monkeypatch.setenv("SGXFIVE_KPOKE", str(kp))
    r = run(*depth_args("--depth-pages", "4", "--depth-store", "--stencil", "--stencil-store",
                        "--depth-fill", "1", "--depth-store-fill", "2", "--stencil-fill", "3",
                        "--stencil-store-fill", "4", "--depth-dump", str(tmp_path)))
    assert r.returncode == 0, r.stdout + r.stderr
    addrs = {m[1]: int(m[2], 16) for m in re.finditer(
        r"^(depth|depth store|stencil|stencil store): (0x[0-9a-f]{8}) 4 pages, fill (0x\w+)",
        r.stdout, re.M)}
    assert len(addrs) == 4 and len(set(addrs.values())) == 4, r.stdout
    off = {k: v - 0x3E000000 for k, v in addrs.items()}
    assert kp.read_text().split() == [
        "ta:7^=0x180", "rd:1=0x3e000000", "rd:11=0x0017100c", f"rd:12={off['depth']:#x}",
        f"rd:13={off['depth store']:#x}", f"rd:14={0x80000000 | off['stencil']:#x}",
        f"rd:15={0x80000000 | off['stencil store']:#x}"], kp.read_text()
    for name, v in (("depth", 1), ("depth-store", 2), ("stencil", 3), ("stencil-store", 4)):
        assert (tmp_path / f"{name}.1.bin").read_bytes() == v.to_bytes(4, "little") * 4096, name
    for what in ("depth", "depth store", "stencil", "stencil store"):
        assert re.search(rf"^{what} #1: 4096 dwords, 0 changed", r.stdout, re.M), what


def test_tri_stencil_without_store_buffer_uses_one_buffer_for_both_bases(tmp_path, monkeypatch):
    kp = tmp_path / "kpoke"
    kp.write_text("")
    monkeypatch.setenv("SGXFIVE_KPOKE", str(kp))
    r = run(*depth_args("--stencil"))
    assert r.returncode == 0, r.stdout + r.stderr
    lines = kp.read_text().split()
    assert lines[0] == "ta:7^=0x180", lines
    assert lines[3][5:] == lines[4][5:], lines          # depth: one buffer for both bases
    assert lines[5][5:] == lines[6][5:] and lines[5].startswith("rd:14=0x8"), lines
    assert "stencil #1:" in r.stdout and "store #1" not in r.stdout, r.stdout


@pytest.mark.parametrize("args", [["tri", "--stencil"], ["tri", "--depth-store"],
                                  ["tri", "--stencil-store", "--depth"],
                                  ["tri", "--depth", "--stencil-fill", "1"],
                                  ["tri", "--depth", "--depth-store-fill", "1"],
                                  ["tri", "--depth", "--stencil", "--stencil-store-fill", "1"]])
def test_tri_stencil_options_are_checked(args):
    r = run("--mock", *args)
    assert r.returncode == 2, (args, r.stdout + r.stderr)
    assert "bad option" not in r.stderr and ("--depth" in r.stderr or "--stencil" in r.stderr), \
        r.stderr


def test_tri_full_and_z_set_the_triangle():
    # --tri-full: the triangle (0,0), (3W,0), (0,3H) covers the target; --tri-z A,B,C: the
    # screen depth at each vertex (clip z 2z - 1), so 0.25,0.75,0.25 is a ramp across x
    r = run("--mock", "tri", "--tri-full", "--tri-z", "0.25,0.75,0.25", "--width", "64",
            "--height", "32")
    assert r.returncode == 0, r.stdout + r.stderr
    assert re.search(r"^tri: triangle \(0,0\) \(192,0\) \(0,96\), depth 0.25 0.75 0.25$",
                     r.stdout, re.M), r.stdout
    assert re.search(r"^tri 64x32 #1: 2048 triangle, 0 background", r.stdout, re.M), r.stdout


def test_tri_odd_width_prints_every_pixel():
    # the row pitch is rounded up to even pixels (the PBE line stride's unit); the image
    # read back skips the pad pixel: 18 rows of 19 values, every one the triangle's
    r = run("--mock", "tri", "--width", "19", "--height", "18", "--tri-full", "--pixels")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "diff: 0 of 342 pixels" in r.stdout, r.stdout
    assert "outside: 0 dwords" in r.stdout, r.stdout
    rows = re.findall(r"^row \d+:(.*)$", r.stdout, re.M)
    assert len(rows) == 18
    assert all(row.split() == ["0xff00ff00"] * 19 for row in rows), rows
    assert re.search(r"^tri 19x18 #1: 342 triangle, 0 background", r.stdout, re.M), r.stdout


@pytest.mark.parametrize("z", ["1", "1,2", "a,b,c", "0.1,0.2,0.3,0.4", "-1.5,0,0", "0,0,2.5",
                               "nan,0,0", "inf,0,0", ""])
def test_tri_z_is_checked(z):
    r = run("--mock", "tri", "--tri-z", z)
    assert r.returncode == 2, (z, r.stdout + r.stderr)
    assert "--tri-z" in r.stderr and "unknown" not in r.stderr, r.stderr
    assert "three screen depths" in r.stderr, r.stderr


def test_tri_z_accepts_minus_one_to_two():
    # Q101: a vertex depth outside [0, 1] reaches the render (clip z 2z - 1 in [-3, 3]), the
    # range is [-1, 2] and the line prints the depths as given
    for z in ("-1,0.5,2", "-0.5,0,1.5"):
        r = run("--mock", "tri", "--tri-full", "--tri-z", z)
        assert r.returncode == 0, (z, r.stdout + r.stderr)
        want = " ".join(f"{float(x):g}" for x in z.split(","))
        assert f"depth {want}\n" in r.stdout, r.stdout


def test_tri_full_and_z_are_for_tri():
    for opt in (["--tri-full"], ["--tri-z", "0,0,0"]):
        r = run("--mock", "fill", *opt)
        assert r.returncode == 2 and "are for tri" in r.stderr, (opt, r.stderr)


def test_tri_isp2_puts_the_stencil_word_in_the_state_block(tmp_path, monkeypatch):
    # --isp2 V (Q121): ISP word 2 V in place of the wrap word, as probe --tri --isp2 does; the
    # mock still finds the viewport and draws the triangle, with or without the stencil buffers
    kp = tmp_path / "kpoke"
    kp.write_text("")
    monkeypatch.setenv("SGXFIVE_KPOKE", str(kp))
    for extra in ([], ["--depth", "--stencil", "--stencil-store"]):
        r = run("--mock", "tri", "--isp2", "0x0e0200ff", "--tri-full", "--width", "64",
                "--height", "32", *extra)
        assert r.returncode == 0, (extra, r.stdout + r.stderr)
        assert re.search(r"^tri: isp2 0x0e0200ff$", r.stdout, re.M), r.stdout
        assert re.search(r"^tri 64x32 #1: 2048 triangle, 0 background", r.stdout, re.M), r.stdout
    r = run("--mock", "tri", "--width", "64", "--height", "32")
    assert "isp2" not in r.stdout, r.stdout


@pytest.mark.parametrize("v", ["x", "", "0x1ffffffff", "-1", "1,2"])
def test_tri_isp2_is_checked(v):
    r = run("--mock", "tri", "--isp2", v)
    assert r.returncode == 2, (v, r.stdout + r.stderr)
    assert "--isp2" in r.stderr and "unknown" not in r.stderr, r.stderr


def test_isp2_is_for_tri_and_probe_tri():
    r = run("--mock", "fill", "--isp2", "0")
    assert r.returncode == 2 and "--isp2 is for tri" in r.stderr, r.stderr


def test_tri_v_sets_the_vertices_in_256ths():
    # --tri-v X0,Y0,X1,Y1,X2,Y2: window coordinates in 1/256 pixel (integers), in place of the
    # default triangle; the line printed says what was drawn
    r = run("--mock", "tri", "--tri-v", "2048,2048,12288,5120,5120,14336", "--tri-z",
            "0.25,0.5,0.75")
    assert r.returncode == 0, r.stdout + r.stderr
    assert re.search(r"^tri: vertices256 2048 2048 12288 5120 5120 14336, depth 0.25 0.5 0.75$",
                     r.stdout, re.M), r.stdout


@pytest.mark.parametrize("v", ["1,2,3,4,5", "1,2,3,4,5,6,7", "a,b,c,d,e,f", "", "1,2,3,4,5,99999999999",
                               "1,2,3,4,5,6,"])
def test_tri_v_is_checked(v):
    r = run("--mock", "tri", "--tri-v", v)
    assert r.returncode == 2, (v, r.stdout + r.stderr)
    assert "--tri-v" in r.stderr and "six integers" in r.stderr, r.stderr


def test_tri_v_refuses_tri_full_and_other_commands():
    r = run("--mock", "tri", "--tri-v", "0,0,256,0,0,256", "--tri-full")
    assert r.returncode == 2 and "--tri-v" in r.stderr and "--tri-full" in r.stderr, r.stderr
    r = run("--mock", "fill", "--tri-v", "0,0,256,0,0,256")
    assert r.returncode == 2 and "are for tri" in r.stderr, r.stderr


def test_tri_words_with_regs_reads_the_registers_at_every_snapshot(tmp_path, monkeypatch):
    # --words DIR with --regs LO-HI: each snapshot N (before the first render, after each one, and
    # the 100 + N and 200 + N of --ctx2) is followed by the register range, so the registers can
    # be read where the words are (the mock has no registers: its line says so)
    dbg, out = tmp_path / "dbg", tmp_path / "w"
    dbg.mkdir()
    out.mkdir()
    (dbg / "render_words").write_text("ctx:0=0x00000011\n")
    (dbg / "buf09").write_bytes(bytes(256))
    monkeypatch.setenv("SGXFIVE_DEBUGFS", str(dbg))
    r = run("--mock", "tri", "-n", "2", "--ctx2", "--words-between", "--words", str(out),
            "--regs", "0x600-0x750")
    assert r.returncode == 0, r.stdout + r.stderr
    snaps = re.findall(r"^tri: registers at snapshot (\d+)$", r.stdout, re.M)
    assert snaps == ["0", "101", "1", "102", "2"], (snaps, r.stdout)
    r = run("--mock", "tri", "-n", "1", "--words", str(out))
    assert "registers at snapshot" not in r.stdout


def test_stderr_message_lands_after_the_stdout_lines_before_it():
    # stdout redirected is block-buffered unless the tool flushes it: the failure message the
    # tool writes to stderr then landed at the last 4096-byte boundary of the stdout stream
    # (inside a dump's rows, or before every line of a short output). It is now in the order
    # the program wrote: after "layout:", before the closing "tri: FAILED" line.
    r = subprocess.run([TOOL, "--mock", "tri", "--fault"], stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, text=True, timeout=30)
    lines = r.stdout.splitlines()
    i = [n for n, ln in enumerate(lines) if ln.startswith("sgxfive-test: render:")]
    assert len(i) == 1, r.stdout
    assert lines[i[0] - 1].startswith("layout: fb "), r.stdout
    assert lines[i[0] + 1].startswith("tri: FAILED"), r.stdout


def test_stderr_message_is_not_inside_a_long_dump():
    # a dump that crosses many 4096-byte boundaries: every row is whole, the message is a line
    # of its own between "layout:" and the closing line, after all of the rows
    r = subprocess.run([TOOL, "--mock", "tri", "--fault", "--pixels"], stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, text=True, timeout=30)
    assert len(r.stdout) > 4096 * 4, len(r.stdout)
    lines = r.stdout.splitlines()
    rows = [ln for ln in lines if ln.startswith("row ")]
    assert len(rows) == 64 and all(len(ln.split()) == 66 for ln in rows), len(rows)
    i = [n for n, ln in enumerate(lines) if ln.startswith("sgxfive-test: render:")]
    assert len(i) == 1 and lines[i[0] - 1].startswith("layout: fb "), r.stdout[-300:]


def test_probe_exits_3_on_a_failed_job(tmp_path):
    # a probe whose job faulted or hung, or wrote no pixel, ends the run with status 3 (the
    # output is complete and still says which); a run with no failed job ends with 0
    f = assemble(tmp_path, "hang", PHAS + "nop.end\n")
    g = assemble(tmp_path, "good", PHAS + "mov.skipinv.end o0, #0x0000000A\n")
    h = assemble(tmp_path, "nopix", PHAS + "mov.skipinv.end o0, #0xDEADBEEF\n")
    bad = run("--mock", "probe", str(f), str(g))
    assert bad.returncode == 3, bad.stdout + bad.stderr
    assert re.search(r"^probe hang: failed: job faulted", bad.stdout, re.M), bad.stdout
    assert re.search(r"^probe good: o0 0x0000000a ", bad.stdout, re.M), bad.stdout
    assert run("--mock", "probe", str(h)).returncode == 3
    assert run("--mock", "probe", str(g)).returncode == 0


def test_probe_exit_status_is_the_check_failure_before_a_failed_job(tmp_path):
    # a usage or call error keeps its own status (1 and 2); 3 is only a failed job
    assert run("--mock", "probe").returncode == 2


def test_tri_unit_sets_the_vertex_unit():
    # --tri-unit K: --tri-v values are in 1/2^K pixel (K 5 to 20, default 8)
    r = run("--mock", "tri", "--tri-unit", "12", "--tri-v", "32768,32768,196608,81920,81920,229376")
    assert r.returncode == 0, r.stdout + r.stderr
    assert re.search(r"^tri: vertices4096 32768 32768 196608 81920 81920 229376$", r.stdout, re.M), r.stdout


@pytest.mark.parametrize("k", ["21", "x", "", "-1", "100"])
def test_tri_unit_is_checked(k):
    r = run("--mock", "tri", "--tri-unit", k, "--tri-v", "0,0,256,0,0,256")
    assert r.returncode == 2 and "--tri-unit" in r.stderr, (k, r.stderr)


@pytest.mark.parametrize("k", [0, 1, 4, 5, 20])
def test_tri_unit_takes_0_to_20(k):
    # Q199 past 2^25 px: units from a whole pixel (K 0) to 1/2^20; 0 is a unit, not "default"
    v = "0,0,64,0,0,64"
    r = run("--mock", "tri", "--tri-unit", str(k), "--tri-v", v)
    # accepted and drawn (the reference may or may not agree with the mock at a tiny unit)
    assert r.returncode in (0, 1) and "bad option" not in r.stderr, (k, r.stdout + r.stderr)
    assert re.search(rf"^tri: vertices{1 << k} 0 0 64 0 0 64$", r.stdout, re.M), r.stdout


def test_tri_v_takes_the_int32_range():
    for v in ("-2147483648,2147483647,0,0,5,5", "2147483647,0,0,-2147483648,0,0"):
        r = run("--mock", "tri", "--tri-unit", "0", "--tri-v", v)
        assert r.returncode in (0, 1) and "bad option" not in r.stderr, (v, r.stdout + r.stderr)
        assert f"vertices1 {v.replace(',', ' ')}" in r.stdout, r.stdout
    for v in ("2147483648,0,0,0,0,0", "-2147483649,0,0,0,0,0"):
        r = run("--mock", "tri", "--tri-v", v)
        assert r.returncode == 2 and "six integers" in r.stderr, (v, r.stderr)


def test_tri_unit_needs_tri_v():
    r = run("--mock", "tri", "--tri-unit", "12")
    assert r.returncode == 2 and "--tri-unit" in r.stderr and "--tri-v" in r.stderr, r.stderr


def test_tri_stencil_fill_bytes_numbers_the_bytes(tmp_path, monkeypatch):
    # Q121's lane 1: a fill `bytes` holds byte j = j & 0xff (a stencil byte names its own pixel),
    # `bytes:S` starts the count at S (a shifted fill); the dump is the buffer as written
    kp = tmp_path / "kpoke"
    kp.write_text("")
    monkeypatch.setenv("SGXFIVE_KPOKE", str(kp))
    for fill, first in (("bytes", 0), ("bytes:3", 3), ("bytes:255", 255)):
        d = tmp_path / fill.replace(":", "_")
        d.mkdir()
        r = run(*depth_args("--depth-pages", "4", "--stencil", "--stencil-fill", fill,
                            "--isp2", "0x0e0200ff", "--depth-dump", str(d)))
        assert r.returncode == 0, (fill, r.stdout + r.stderr)
        assert re.search(rf"^stencil: 0x[0-9a-f]{{8}} 4 pages, fill {fill}$", r.stdout, re.M), \
            r.stdout
        assert (d / "stencil.1.bin").read_bytes() == bytes(
            (first + j) & 0xff for j in range(16384)), fill


@pytest.mark.parametrize("fill", ["bytes:", "bytes:256", "bytes:x", "bytes:-1", "byte"])
def test_tri_fill_bytes_is_checked(fill):
    r = run(*depth_args("--stencil", "--stencil-fill", fill))
    assert r.returncode == 2 and "bad option --stencil-fill" in r.stderr, (fill, r.stderr)
    assert "bytes" in r.stderr


def _all(path, value):
    w = words(path)
    return len(w) > 0 and all(x == value for x in w)


def test_tri_refill_writes_the_depth_buffer_between_the_renders(tmp_path, monkeypatch):
    # Q108's stale-data rows: --refill K:depth=V writes V to every dword of the depth buffer
    # after render K - 1 is done and read back and before render K's kick. With
    # --depth-ctl-next the buffer is filled before render 1 only, so render 3 sees what render 2
    # left (the mock stores no depth: V); the report counts against what the host wrote last
    kp = tmp_path / "kpoke"
    kp.write_text("")
    monkeypatch.setenv("SGXFIVE_KPOKE", str(kp))
    r = run(*depth_args("-n", "3", "--depth-pages", "4", "--depth-ctl-next", "0x11700a",
                        "--refill", "2:depth=0x3f000000", "--depth-dump", str(tmp_path)))
    assert r.returncode == 0, r.stdout + r.stderr
    lines = r.stdout.splitlines()
    at = lines.index("refill: render 2 buf depth value 0x3f000000")
    jobs = [i for i, ln in enumerate(lines) if ln == "job: ok"]
    assert len(jobs) == 3 and jobs[0] < at < jobs[1], r.stdout
    assert any(ln.startswith("depth #1: ") for ln in lines[jobs[0]:at]), r.stdout
    assert _all(tmp_path / "depth.1.bin", 0x3F800000)
    assert _all(tmp_path / "depth.2.bin", 0x3F000000)
    assert _all(tmp_path / "depth.3.bin", 0x3F000000)
    for n in (2, 3):
        assert f"depth #{n}: 4096 dwords, 0 changed, 1 distinct; 0x3f000000 x 4096" in r.stdout
    assert r.stdout.count("refill: ") == 1


def test_tri_refill_once_then_the_fill_again(tmp_path, monkeypatch):
    # without --depth-ctl-next the fill goes in before every render: the refill wins at render
    # K only (written after it), and render K + 1 has the fill again
    kp = tmp_path / "kpoke"
    kp.write_text("")
    monkeypatch.setenv("SGXFIVE_KPOKE", str(kp))
    r = run(*depth_args("-n", "3", "--depth-pages", "4", "--depth-fill", "1",
                        "--refill", "2:depth=2", "--depth-dump", str(tmp_path)))
    assert r.returncode == 0, r.stdout + r.stderr
    assert [_all(tmp_path / f"depth.{n}.bin", v) for n, v in ((1, 1), (2, 2), (3, 1))] == \
        [True] * 3
    assert "depth #2: 4096 dwords, 0 changed, 1 distinct; 0x00000002 x 4096" in r.stdout
    assert "depth #3: 4096 dwords, 0 changed, 1 distinct; 0x00000001 x 4096" in r.stdout


def test_tri_refill_stencil_leaves_the_depth_buffer(tmp_path, monkeypatch):
    kp = tmp_path / "kpoke"
    kp.write_text("")
    monkeypatch.setenv("SGXFIVE_KPOKE", str(kp))
    r = run(*depth_args("-n", "2", "--depth-pages", "4", "--depth-fill", "5", "--stencil",
                        "--stencil-fill", "6", "--refill", "2:stencil=0x07070707",
                        "--depth-dump", str(tmp_path)))
    assert r.returncode == 0, r.stdout + r.stderr
    assert "refill: render 2 buf stencil value 0x07070707" in r.stdout
    assert _all(tmp_path / "stencil.1.bin", 6) and _all(tmp_path / "stencil.2.bin", 0x07070707)
    assert _all(tmp_path / "depth.2.bin", 5)


def test_tri_refill_fb_goes_in_before_the_kick():
    # fb: the colour buffer's target rows hold V in place of the sentinel the library writes
    # before each kick (render.c), the guard page the sentinel still; the mock draws every
    # pixel, so the render checks as ever
    r = run("--mock", "tri", "-n", "2", "--refill", "2:fb=0x12345678")
    assert r.returncode == 0, r.stdout + r.stderr
    lines = r.stdout.splitlines()
    at = lines.index("refill: render 2 buf fb value 0x12345678")
    jobs = [i for i, ln in enumerate(lines) if ln == "job: ok"]
    assert len(jobs) == 2 and jobs[0] < at < jobs[1], r.stdout
    assert "tri: 2 renders ok" in r.stdout


@pytest.mark.parametrize("args", [
    ["tri", "-n", "2", "--refill", "1:fb=0"],               # K from 2
    ["tri", "-n", "2", "--refill", "3:fb=0"],               # K up to -n
    ["tri", "--refill", "2:fb=0"],                          # -n 1
    ["tri", "-n", "2", "--refill", "2:depth=0"],            # no depth buffer mapped
    ["tri", "-n", "2", "--depth", "--refill", "2:stencil=0"],
    ["tri", "-n", "2", "--refill", "2:texture=0"],
    ["tri", "-n", "2", "--refill", "2:fb"],
    ["tri", "-n", "2", "--refill", "2:fb=x"],
    ["tri", "-n", "2", "--refill", "x:fb=1"],
    ["tri", "-n", "2", "--refill", "2fb=1"],
    ["fill", "--refill", "2:fb=0"],
])
def test_tri_refill_is_checked(args):
    r = run("--mock", *args)
    assert r.returncode == 2, (args, r.stdout + r.stderr)
    assert "--refill" in r.stderr, r.stderr
