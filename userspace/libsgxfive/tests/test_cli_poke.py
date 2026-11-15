# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""sgxfive-test --poke, --pixels and --regs on fill, copy and tri, against the mock: the
result lines a sweep reads (job, target hash, difference from the CPU reference, writes
outside the target), the usage errors, and a poke that changes the mock's image."""
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


def result(out: str) -> dict:
    """The result lines of one job."""
    job = re.search(r"^job: (.*)$", out, re.M)
    tgt = re.search(r"^target: (\d+)x(\d+) hash (0x[0-9a-f]{16})$", out, re.M)
    diff = re.search(r"^diff: (\d+) of (\d+) pixels(?:, first \((\d+), (\d+)\) "
                     r"(0x[0-9a-f]{8}) expected (0x[0-9a-f]{8}))?$", out, re.M)
    outside = re.search(r"^outside: (\d+) dwords$", out, re.M)
    assert job and tgt and diff and outside, out
    return {"job": job.group(1), "size": (int(tgt.group(1)), int(tgt.group(2))),
            "hash": tgt.group(3), "diff": int(diff.group(1)), "of": int(diff.group(2)),
            "first": diff.group(3) and (int(diff.group(3)), int(diff.group(4)),
                                        int(diff.group(5), 16), int(diff.group(6), 16)),
            "outside": int(outside.group(1))}


@pytest.mark.parametrize("cmd,size", [("fill", (64, 32)), ("copy", (64, 32)),
                                      ("tri", (64, 64))])
def test_result_lines(cmd, size):
    r = run("--mock", cmd)
    assert r.returncode == 0, r.stdout + r.stderr
    res = result(r.stdout)
    assert res["job"] == "ok"
    assert res["size"] == size
    assert res["diff"] == 0 and res["of"] == size[0] * size[1] and res["first"] is None
    assert res["outside"] == 0
    assert result(run("--mock", cmd).stdout)["hash"] == res["hash"]


def test_hash_is_of_the_target():
    a = result(run("--mock", "fill", "--colour", "0xff000000").stdout)
    b = result(run("--mock", "fill", "--colour", "0xff000001").stdout)
    assert a["hash"] != b["hash"]


@pytest.mark.parametrize("args", [
    ["fill", "--poke", "xfer:42=1"],         # past the transfer command's 42 dwords
    ["fill", "--poke", "cmd:0=1"],           # a fill has no render command
    ["fill", "--poke", "tex:0=1"],           # nor texture words
    ["fill", "--poke", "bg:17=1"],           # 17 background-object words
    ["fill", "--poke", "pds:prim:4=1"],
    ["fill", "--poke", "pds:frob:0=1"],
    ["copy", "--poke", "tex:4=1"],
    ["copy", "--poke", "bg:29=1"],          # room for a two-layer object
    ["copy", "--poke", "pds:prim:12=1"],
    ["tri", "--poke", "cmd:26=1"],
    ["tri", "--poke", "xfer:0=1"],
    ["tri", "--poke", "bg:0=1"],
    ["tri", "--poke", "vdm:11=1"],
    ["tri", "--poke", "eos:2=1"],
    ["tri", "--poke", "blk:18=1"],
    ["tri", "--poke", "pds:pixev:20=1"],
    ["tri", "--poke", "pds:prim:4=1"],
    ["fill", "--poke", "xfer:1"],            # syntax
    ["fill", "--poke", "xfer:1~=1"],
    ["fill", "--poke"],
    ["dummy", "--poke", "xfer:0=1"],         # only fill, copy and tri take pokes
    ["contexts", "--poke", "cmd:0=1"],
    ["dummy", "--pixels"],
    ["fill", "--regs", "0x10"],
    ["fill", "--regs", "0x10-0x8"],
    ["fill", "--regs", "0x2-0x8"],
    ["fill", "--regs", "0x0-0x4000"],
])
def test_poke_usage_errors(args):
    r = run("--mock", *args)
    assert r.returncode == 2, r.stdout + r.stderr
    assert "job:" not in r.stdout


@pytest.mark.parametrize("args", [
    ["fill", "--poke", "xfer:41=1"], ["fill", "--poke", "bg:16^=1"],
    ["fill", "--poke", "pds:pixev:19=0"], ["fill", "--poke", "pds:sec:3=0"],
    ["copy", "--poke", "tex:3^=0x80000000"], ["copy", "--poke", "bg:22=0"],
    ["copy", "--poke", "pds:prim:11=0"],
    ["tri", "--poke", "cmd:25^=0"], ["tri", "--poke", "vdm:10^=0"],
    ["tri", "--poke", "eos:1^=0"], ["tri", "--poke", "blk:17^=0"],
    ["tri", "--poke", "pds:vtx:7^=0"], ["tri", "--poke", "pds:state:7^=0"],
    ["tri", "--poke", "pds:eos:7^=0"], ["tri", "--poke", "pds:bgprim:3^=0"],
    ["tri", "--poke", "pds:sec:3^=0"], ["tri", "--poke", "pds:pixev:19^=0"],
])
def test_last_word_of_every_space_runs(args):
    r = run("--mock", *args)
    assert r.returncode in (0, 1), r.stdout + r.stderr
    result(r.stdout)


def test_a_null_flip_changes_nothing():
    base = result(run("--mock", "tri").stdout)
    r = run("--mock", "tri", "--poke", "cmd:0^=0", "--poke", "blk:3^=0")
    assert r.returncode == 0, r.stdout + r.stderr
    assert result(r.stdout) == base


def test_fill_poke_render_box_shrinks_the_image():
    # The mock clips the rectangle to the render box: xfer:13 is ISP_RENDBOX2, the last
    # tile; tile (0, 0) leaves the 32 x 16 pixels of the first tile.
    r = run("--mock", "fill", "--poke", "xfer:13=0")
    assert r.returncode == 1, r.stdout + r.stderr
    res = result(r.stdout)
    assert res["job"] == "ok"
    assert res["diff"] == 64 * 32 - 32 * 16
    assert res["first"] == (32, 0, 0xdeadbeef, 0xff336699)


def test_copy_poke_texture_address_moves_the_source():
    # T2 is the source address: one row (256 bytes) on.
    base = result(run("--mock", "copy").stdout)
    r = run("--mock", "copy", "--poke", "tex:2^=0x100")
    assert r.returncode == 1, r.stdout + r.stderr
    res = result(r.stdout)
    assert res["job"] == "ok" and res["hash"] != base["hash"]
    assert res["diff"] == 64 * 32
    assert res["first"][:2] == (0, 0)


def test_tri_poke_primary_pointer_paints_the_background_colour():
    # blk:5 is the triangle's pixel primary (in 16-byte units from PDS_EXEC_BASE); the
    # background primary is two units on.
    base = result(run("--mock", "tri").stdout)
    r = run("--mock", "tri", "--poke", "blk:5^=2")
    assert r.returncode == 1, r.stdout + r.stderr
    res = result(r.stdout)
    assert res["job"] == "ok" and res["hash"] != base["hash"]
    assert res["diff"] > 0
    # no image dump with pokes: --pixels has the image
    assert not re.search(r"^[#.?s]+$", r.stdout, re.M)


def test_tri_poke_fault_still_reports():
    r = run("--mock", "tri", "--poke", "cmd:0=0x3e800000")
    assert r.returncode == 1, r.stdout + r.stderr
    res = result(r.stdout)
    assert res["job"].startswith("failed: job faulted"), res


def test_rejected_job():
    # The kernel refuses tiling words that are not the target's layout.
    r = run("--mock", "tri", "--poke", "cmd:4^=1")
    assert r.returncode == 1, r.stdout + r.stderr
    assert result(r.stdout)["job"] == "rejected (Invalid argument)"


@pytest.mark.parametrize("cmd,w,h", [("fill", 64, 32), ("copy", 64, 32), ("tri", 64, 64)])
def test_pixels(cmd, w, h):
    r = run("--mock", cmd, "--pixels")
    assert r.returncode == 0, r.stdout + r.stderr
    rows = re.findall(r"^row (\d+): ((?:0x[0-9a-f]{8} ?)+)$", r.stdout, re.M)
    assert [int(y) for y, _ in rows] == list(range(h))
    assert all(len(v.split()) == w for _, v in rows)


def test_copy_every_value_source():
    # --every-value: the copy's source holds every value of every channel in each run of 256
    # pixels, each channel through its own permutation; the copy still checks out.
    r = run("--mock", "copy", "--every-value", "--pixels")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "copy: ok" in r.stdout
    px = [int(v, 16) for _, row in re.findall(r"^row (\d+): ((?:0x[0-9a-f]{8} ?)+)$",
                                                r.stdout, re.M) for v in row.split()]
    run0 = px[:256]
    for shift in (0, 8, 16, 24):
        assert {v >> shift & 0xff for v in run0} == set(range(256)), shift
    assert len({(v >> 24, v & 0xff) for v in run0}) == 256    # channels not in lockstep...
    assert any(v >> 24 != v & 0xff for v in run0)             # ...and not equal


def test_every_value_only_for_copy():
    r = run("--mock", "fill", "--every-value")
    assert r.returncode != 0


def test_regs_not_on_the_mock():
    r = run("--mock", "fill", "--regs", "0x700-0x740")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "regs: not available on the mock" in r.stdout


def _probe_file(tmp_path):
    # the shader of test_cli.py's probes: one move into o0, assembled by the probe host
    import sys
    sys.path.insert(0, str(HERE))
    from test_cli import PHAS, assemble
    return assemble(tmp_path, "pk", PHAS + "mov.skipinv.end o0, #0x12345678\n")


def test_probe_takes_transfer_pokes(tmp_path):
    """probe --poke xfer:N...: the pokes apply to the probe's fill (its transfer command),
    listed on the probe's lines; a poke the kernel rejects fails the probe."""
    f = _probe_file(tmp_path)
    r = run("--mock", "probe", "--poke", "xfer:17^=0x4", "--poke", "xfer:33=0x66", str(f))
    assert r.returncode == 0, r.stdout + r.stderr
    assert re.search(r"^probe pk: pokes xfer:17\^=0x4 xfer:33=0x66$", r.stdout, re.M), r.stdout
    assert re.search(r"^probe pk: o0 0x12345678", r.stdout, re.M), r.stdout
    r = run("--mock", "probe", "--poke", "xfer:4^=0x1", str(f))
    assert re.search(r"^probe pk: failed", r.stdout, re.M), r.stdout


def test_probe_takes_background_object_pokes(tmp_path):
    """probe --poke bg:N...: words of the fill's background object, where the PDS state's
    secondary attribute rows are (bits 24:18 of dword 1)."""
    f = _probe_file(tmp_path)
    r = run("--mock", "probe", "--poke", "bg:1=0x130000", str(f))
    assert r.returncode == 0, r.stdout + r.stderr
    assert re.search(r"^probe pk: pokes bg:1=0x130000$", r.stdout, re.M), r.stdout


@pytest.mark.parametrize("poke", ["cmd:0=1", "tex:0=1", "xfer:42=1", "bg:17=1"])
def test_probe_rejects_other_pokes(tmp_path, poke):
    r = run("--mock", "probe", "--poke", poke, str(_probe_file(tmp_path)))
    assert r.returncode == 2, r.stdout


def test_tri_prints_the_target_address():
    """tri prints its colour buffer's GPU address, the same in every run: a kernel poke can
    point another unit's base at it (the ZLS bases, say)."""
    outs = [run("--mock", "tri").stdout for _ in range(2)]
    addrs = [re.findall(r"^layout: fb (0x[0-9a-f]{8})$", o, re.M) for o in outs]
    assert addrs[0] and addrs[0] == addrs[1], outs[0]
    assert int(addrs[0][0], 16) % 4096 == 0


def scratch(out: str) -> dict:
    head = re.search(r"^scratch: (0x[0-9a-f]{8}) (\d+) pages, fill (0x[0-9a-f]{8})$", out, re.M)
    total = re.search(r"^scratch: (\d+) dwords changed$", out, re.M)
    assert head and total, out
    pages = {int(p): int(n) for p, n in re.findall(r"^scratch page (\d+): (\d+) changed", out,
                                                    re.M)}
    return {"addr": int(head.group(1), 16), "pages": int(head.group(2)),
            "fill": int(head.group(3), 16), "changed": int(total.group(1)), "per_page": pages}


def test_tri_scratch_buffer():
    """tri --scratch N maps N pages for a kernel poke to point a unit at, fills them before
    each render (--scratch-fill, default 0.25f) and reports what the render changed in
    them, page by page."""
    r = run("--mock", "tri", "--scratch", "4")
    assert r.returncode == 0, r.stdout + r.stderr
    s = scratch(r.stdout)
    fb = int(re.search(r"^layout: fb (0x[0-9a-f]{8})$", r.stdout, re.M).group(1), 16)
    assert s["pages"] == 4 and s["addr"] % 4096 == 0 and s["fill"] == 0x3E800000
    assert not (s["addr"] <= fb < s["addr"] + 4 * 4096)
    assert s["changed"] == 0 and s["per_page"] == {}
    s = scratch(run("--mock", "tri", "--scratch", "2", "--scratch-fill", "0x12345678").stdout)
    assert s["pages"] == 2 and s["fill"] == 0x12345678
    assert "scratch:" not in run("--mock", "tri").stdout


def test_tri_kpoke_per_render(tmp_path):
    """tri --kpoke-render N:SPEC writes SPEC to the kernel's debugfs kpoke (SGXFIVE_KPOKE
    overrides the path) just before render N, one line, so each render of one context can
    carry its own kernel pokes; several are written in order."""
    f = tmp_path / "kpoke"
    f.write_text("")
    r = subprocess.run([TOOL, "--mock", "tri", "-n", "2", "--kpoke-render", "2:ta:1=0x2",
                        "--kpoke-render", "1:rd:3^=0x4", "--kpoke-render", "2:ta:7^=0x8"],
                       capture_output=True, text=True, timeout=30,
                       env={**os.environ, "SGXFIVE_KPOKE": str(f)})
    assert r.returncode == 0, r.stdout + r.stderr
    assert f.read_text() == "rd:3^=0x4\nta:1=0x2\nta:7^=0x8\n"
    assert re.search(r"^tri: kpoke before render 2: ta:1=0x2$", r.stdout, re.M), r.stdout
    for args in (["--kpoke-render", "0:ta:1=1"], ["--kpoke-render", "3:ta:1=1"],
                 ["--kpoke-render", "1"], ["--kpoke-render", "x:ta:1=1"]):
        r = run("--mock", "tri", "-n", "2", *args)
        assert r.returncode == 2, (args, r.stdout + r.stderr)


def test_tri_move_per_render():
    """tri --move N:DX,DY draws render N's triangle DX, DY pixels away; the CPU reference
    moves with it, so the mock's image still checks."""
    r = run("--mock", "tri", "-n", "2", "--move", "2:8,-4")
    assert r.returncode == 0, r.stdout + r.stderr
    assert re.search(r"^tri: render 2 moved by 8,-4$", r.stdout, re.M), r.stdout
    assert "tri: 2 renders ok" in r.stdout
    for args in (["--move", "3:1,1"], ["--move", "1:1"], ["--move", "1:x,1"]):
        r = run("--mock", "tri", "-n", "2", *args)
        assert r.returncode == 2, (args, r.stdout + r.stderr)


@pytest.mark.parametrize("unit", [[], ["--tri-unit", "10"], ["--tri-unit", "5"]])
def test_tri_move_moves_fine_vertices(unit):
    """With --tri-v the render draws the fine vertices (1/2^unit pixel): --move moves those,
    not only the 1/16-pixel ones the CPU reference reads, so the moved render still checks."""
    s = 1 << int(unit[1]) if unit else 256
    v = ",".join(str(c * s) for c in (8, 8, 48, 20, 20, 56))
    r = run("--mock", "tri", "-n", "2", "--tri-v", v, *unit, "--move", "2:8,4")
    assert r.returncode == 0, r.stdout + r.stderr
    assert re.search(r"^tri: render 2 moved by 8,4$", r.stdout, re.M), r.stdout
    assert "tri: 2 renders ok" in r.stdout, r.stdout


def test_tri_geometry_render():
    """tri --geometry N submits render N as a geometry job (DRM_SGXFIVE_SUBMIT_JOB_RENDER_GEOMETRY):
    it tiles into the context's scene and leaves it open, so nothing is drawn and its image
    is not checked; the next render closes the scene. The last render cannot be one."""
    r = run("--mock", "tri", "-n", "2", "--geometry", "1", "--move", "2:12,12")
    assert r.returncode == 0, r.stdout + r.stderr
    assert re.search(r"^tri 64x64 #1: geometry only, the scene left open$", r.stdout, re.M), \
        r.stdout
    assert re.search(r"^tri 64x64 #2: \d+ triangle", r.stdout, re.M), r.stdout
    assert "tri: 2 renders ok" in r.stdout
    for args in (["-n", "2", "--geometry", "2"], ["-n", "2", "--geometry", "0"],
                 ["-n", "2", "--geometry", "x"]):
        r = run("--mock", "tri", *args)
        assert r.returncode == 2, (args, r.stdout + r.stderr)


def test_tri_dump_render(tmp_path):
    """tri --dump-render DIR: after the last render, the kernel's debugfs render_param and
    render_tadata (SGXFIVE_DEBUGFS overrides their directory) copied to DIR/tri.*.bin, so a
    scene built over several renders can be read; only for tri."""
    dbg = tmp_path / "debugfs"
    dbg.mkdir()
    (dbg / "render_param").write_bytes(b"\x11" * 8192)
    (dbg / "render_tadata").write_bytes(b"\x22" * 4096)
    out = tmp_path / "out"
    out.mkdir()
    r = subprocess.run([TOOL, "--mock", "tri", "-n", "2", "--geometry", "1", "--dump-render",
                        str(out)], capture_output=True, text=True, timeout=60,
                       env={**os.environ, "SGXFIVE_DEBUGFS": str(dbg)})
    assert r.returncode == 0, r.stdout + r.stderr
    assert (out / "tri.param.bin").read_bytes() == b"\x11" * 8192
    assert (out / "tri.tadata.bin").read_bytes() == b"\x22" * 4096
    assert re.search(r"^probe tri: render memory to .*/tri\.\{param,tadata\}\.bin "
                     r"\(8192, 4096 bytes\)$", r.stdout, re.M), r.stdout
    r = run("--mock", "fill", "--dump-render", str(out))
    assert r.returncode == 2, r.stdout + r.stderr

def test_tri_keep_going():
    """tri --keep-going reports every render even when one's image differs from its
    reference (a scene over several kicks holds the earlier renders' triangles too), and
    still fails at the end."""
    r = run("--mock", "tri", "-n", "2", "--poke", "blk:5^=2")
    assert r.returncode == 1 and "#2:" not in r.stdout, r.stdout
    r = run("--mock", "tri", "-n", "2", "--poke", "blk:5^=2", "--keep-going")
    assert r.returncode == 1, r.stdout + r.stderr
    assert re.search(r"^tri 64x64 #1: ", r.stdout, re.M) and \
        re.search(r"^tri 64x64 #2: ", r.stdout, re.M), r.stdout
    assert "tri: 0 of 2 renders ok" in r.stdout


def test_job_hooks_get_no_compound_literal():
    """A job hook runs when the job is built, after the call that set it: its argument must
    outlive that call. A compound literal made in a block ends with the block, and gcc reuses
    its slot (probe --poke died of SIGSEGV in the laptop's i686 build, round 22), so no
    `sgxfive_*_set_hook(..., &(struct ...){ ... })` in the tool."""
    src = (HERE.parent / "tools" / "sgxfive-test.c").read_text()
    calls = re.findall(r"sgxfive_\w+_set_hook\([^;]*;", src, re.S)
    assert calls, "no set_hook call found"
    bad = [c for c in calls if re.search(r"&\s*\(\s*(const\s+)?struct\b", c)]
    assert not bad, bad


POKED = re.compile(r"^probe (\w+): poked ([a-z]+(?::\w+)?:\d+) (0x[0-9a-f]{8}) -> "
                   r"(0x[0-9a-f]{8})$", re.M)


@pytest.mark.parametrize("coords", [[], ["--coords"]])
def test_probe_poke_echo(tmp_path, coords):
    """probe --poke echoes every poke the hook applied to the built job, once the job was
    submitted: `probe NAME: poked SPACE:N 0xOLD -> 0xNEW`, OLD the word the job was built
    with and NEW what went to the kernel. (The mock runs no program of ours as a copy shader:
    the copy faults there, after its submit, so --coords ends in rc 3 with its echo.)"""
    f = _probe_file(tmp_path)
    rc = 3 if coords else 0
    r = run("--mock", "probe", *coords, "--poke", "bg:1^=0", "--poke", "xfer:17^=0", str(f))
    assert r.returncode == rc, r.stdout + r.stderr
    built = {s: (o, n) for _, s, o, n in POKED.findall(r.stdout)}
    assert set(built) == {"bg:1", "xfer:17"}, r.stdout
    assert all(o == n for o, n in built.values()), built
    r = run("--mock", "probe", *coords, "--poke", "bg:1=0x130000", "--poke", "xfer:17^=0x4",
            str(f))
    assert r.returncode == rc, r.stdout + r.stderr
    got = POKED.findall(r.stdout)
    assert [(n, s) for n, s, _, _ in got] == [("pk", "bg:1"), ("pk", "xfer:17")], r.stdout
    assert got[0][2:] == (built["bg:1"][0], "0x00130000"), got
    old = int(built["xfer:17"][0], 16)
    assert got[1][2:] == (f"0x{old:08x}", f"0x{old ^ 4:08x}"), got
    assert r.stdout.index("poked bg:1") > r.stdout.index("pokes bg:1"), r.stdout


def test_probe_poke_echo_in_order_on_one_word(tmp_path):
    """Two pokes of one word: each echo shows the word as the poke before it left it."""
    f = _probe_file(tmp_path)
    r = run("--mock", "probe", "--poke", "xfer:33=0x10", "--poke", "xfer:33^=0x3", str(f))
    assert r.returncode == 0, r.stdout + r.stderr
    got = POKED.findall(r.stdout)
    assert [g[1:] for g in got][1] == ("xfer:33", "0x00000010", "0x00000013"), got
    assert got[0][3] == "0x00000010", got


def test_probe_poke_echo_not_for_a_job_not_run(tmp_path):
    """No echo for a job the kernel rejected: its words never reached the GPU."""
    f = _probe_file(tmp_path)
    r = run("--mock", "probe", "--poke", "xfer:4^=0x1", str(f))
    assert re.search(r"^probe pk: failed", r.stdout, re.M), r.stdout
    assert "poked" not in r.stdout, r.stdout
