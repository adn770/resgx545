# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""probe.py's triangle host (host = "tri"): probes whose programs run in the first triangle's
render (sgxfive-test probe --tri), the table fields, the options they run with, their fixed
helper programs, and the plumbing end to end on the mock."""
from __future__ import annotations

import atexit
import pathlib
import re
import shutil
import subprocess
import tempfile

import pytest

import probe

HERE = pathlib.Path(__file__).resolve().parent
TOOL = HERE.parent.parent / "userspace" / "libsgxfive" / "build" / "sgxfive-test"
PIXEL_EVENT = probe.PROBES / "pds" / "pixel-event.toml"
TABLES = sorted(t for t in probe.PROBES.glob("*/*.toml") if "[[probe]]" in t.read_text())
_MERGED = tempfile.TemporaryDirectory()
atexit.register(_MERGED.cleanup)
SRC = pathlib.Path(_MERGED.name)         # the tables' templates in one directory
for _f in sorted(probe.PROBES.glob("*/templates/*.s")):
    shutil.copy(_f, SRC / _f.name)


def tri_probes() -> list:
    """Every probe that runs inside the triangle's render, over all the tables."""
    return [p for t in TABLES for p in probe.load(t) if p.host == "tri"]


def dump_probes() -> list:
    return [p for t in TABLES for p in probe.load(t) if p.dump_render]


def by_name() -> dict:
    return {p.name: p for p in tri_probes()}
SPDX = "SPDX-" + "License-Identifier: MIT"   # split, so that reuse does not parse it


def table(tmp_path: pathlib.Path, body: str) -> list:
    t = tmp_path / "t.toml"
    t.write_text('[[probe]]\nname = "t"\nquestion = "q"\ncases = [[]]\n' + body)
    return probe.load(t)


def test_tri_fields(tmp_path):
    (p,) = table(tmp_path, 'source = "pixev_dump.s"\nhost = "tri"\nslot = "pixev"\n'
                           'slots = { eot = "eot_dump.s" }\nsize = [32, 16]\ntemps = 8\n')
    assert p.host == "tri" and p.slot == "pixev" and p.slots == {"eot": "eot_dump.s"}
    assert p.size == (32, 16) and p.max_size is None
    assert p.isa == "pds"                       # the slot's
    (q,) = table(tmp_path, 'source = "pred.s"\nhost = "tri"\nslot = "pixel"\n'
                           'max_size = [64, 4096]\n')
    assert q.isa == "usse" and q.size == (64, 64) and q.max_size == (64, 4096)
    (f,) = table(tmp_path, 'source = "pred.s"\n')
    assert f.host == "fill" and f.slot == "" and f.slots == {}


@pytest.mark.parametrize("body", [
    'host = "tri"\n',                                   # no slot
    'host = "tri"\nslot = "bogus"\n',
    'host = "tri"\nslot = "pixel"\nslots = { pixel = "pred.s" }\n',   # its own slot
    'host = "tri"\nslot = "pixel"\nslots = { bogus = "pred.s" }\n',
    'host = "tri"\nslot = "pixel"\nsize = [33, 16]\n',
    'host = "tri"\nslot = "pixel"\nsize = [64, 64]\nmax_size = [32, 64]\n',
    'host = "tri"\nslot = "pixel"\ncoords = true\n',
    'host = "tri"\nslot = "pixel"\nvertices = 4\n',            # not whole triangles
    'host = "tri"\nslot = "pixel"\nvertices = 129\n',          # beyond the vertex buffer
    'host = "tri"\nslot = "pixel"\nvertices = 0\n',
    'vertices = 6\n',                                   # on a fill probe
    'host = "copy"\n',
    'slot = "pixel"\n',                                  # tri fields on a fill probe
])
def test_tri_fields_refused(tmp_path, body):
    with pytest.raises(probe.ProbeError):
        table(tmp_path, 'source = "pred.s"\n' + body)


def test_tri_tool_args(tmp_path):
    (p,) = table(tmp_path, 'source = "pixev_dump.s"\nhost = "tri"\nslot = "pixev"\n'
                           'params = { OP = "" }\nslots = { eot = "eot_dump.s" }\n'
                           'size = [32, 4096]\nmax_size = [32, 4096]\ntemps = 8\n'
                           'pixels = true\n')
    assert probe.tool_args(p, src_dir=SRC) == [
        "--temps", "8", "--pixels", "--tri", "pixev:60", "--width", "32", "--height", "4096",
        "--max-width", "32", "--max-height", "4096", "--slot", "eot=eot_dump.bin"]
    (q,) = table(tmp_path, 'source = "pred.s"\nhost = "tri"\nslot = "pixel"\n')
    assert probe.tool_args(q, src_dir=SRC) == ["--temps", "32", "--tri", "pixel", "--width", "64",
                                  "--height", "64"]



def test_tri_vertices(tmp_path):
    # copies of the triangle after it, for the vertex programs to run for more vertices
    (p,) = table(tmp_path, 'source = "pred.s"\nhost = "tri"\nslot = "pixel"\nvertices = 15\n')
    assert p.vertices == 15
    assert probe.tool_args(p, src_dir=SRC)[-2:] == ["--vertices", "15"]
    (q,) = table(tmp_path, 'source = "pred.s"\nhost = "tri"\nslot = "pixel"\n')
    assert q.vertices == 0 and "--vertices" not in probe.tool_args(q, src_dir=SRC)

def test_tri_pds_helper_gets_its_data_dwords(tmp_path):
    # a fixed PDS program (here the default pixel-event program as the helper) names its
    # data dwords after the file
    src = tmp_path / "pixev.s"
    src.write_text((HERE.parent.parent / "asm" / "transfer" / "pds_pixevent.s").read_text())
    (p,) = table(tmp_path, 'source = "eot_dump.s"\nhost = "tri"\nslot = "eot"\n'
                           f'slots = {{ pixev = "{src}" }}\n')
    assert probe.tool_args(p, src_dir=SRC)[-2:] == ["--slot", "pixev=pixev.bin:20"]


def test_helpers_are_built_and_found(tmp_path):
    (p,) = table(tmp_path, 'source = "pixev_dump.s"\nhost = "tri"\nslot = "pixev"\n'
                           'params = { OP = "" }\nslots = { eot = "eot_tile.s" }\n')
    built = probe.build_helpers([p], tmp_path / "w", SRC)
    assert [f.name for f in built] == ["eot_tile.bin"]
    assert built[0].stat().st_size % 8 == 0
    args = probe._with_use(tuple(probe.tool_args(p, src_dir=SRC)), "dir")
    assert args[-2:] == ["--slot", "eot=dir/eot_tile.bin"]
    # a fill PDS probe's USE program is still a helper
    (q,) = [x for x in probe.load(probe.PROBES / "pds" / "alu.toml") if x.name == "pds-alu-readback"]
    assert [f.name for f in probe.build_helpers([q], tmp_path / "w", SRC)] == ["sa_dump.bin"]


@pytest.fixture(scope="module")
def tri():
    return tri_probes()


def test_tri_table(tri):
    names = [p.name for p in tri]
    assert "pds-pixel-event-readback" in names
    assert "pds-pixel-event-pixev-inputs" in names and "pds-pixel-event-pixev-tall" in names
    for p in tri:
        assert p.host == "tri" and p.slot in probe.TRI_SLOTS, p.name


# The data dwords of each PDS probe source (and of the pixev slot's default), tri probes.
PDS_DATA = {"pixev": 60, "pds_iter.s": 8, "pds_tex.s": 12, "pds_tex_iter.s": 12,
            "pds_tex_t3.s": 12, "pds_tex2.s": 16, "pds_iter_nofetch.s": 12,
            "pds_iter_done.s": 12, "pixev_u1_flip.s": 64}


def test_tri_table_assembles(tri, tmp_path):
    for p in tri:
        for f in probe.build(p, tmp_path, SRC):
            assert f.stat().st_size % 4 == 0
        if p.slot in probe.TRI_PDS:
            want = PDS_DATA.get(p.source, PDS_DATA["pixev"] if p.slot == "pixev" else None)
            assert want is None or probe.pds_data(p, SRC) == want, p.name
        assert probe.build_helpers([p], tmp_path, SRC) or not p.slots, p.name   # helpers, if any


def test_tri_readback_hypothesis(tri):
    (p,) = [q for q in tri if q.name == "pds-pixel-event-readback"]
    assert p.size == (32, 16)                   # one tile: one end-of-tile task
    assert p.slots == {"pixtask": "task_dump.s"}  # the end-of-tile task's sa are the tile's
    # starts the pixtask through the PTOFF program, which the host turns into a br to it
    assert "movs doutu, ds0[0], ds0[1], ds0[0], ds0[0]" in p.params["OP"]
    assert p.hypotheses == {"douta writes the sa0-sa15 of the task started next":
                            [[0x7E570000 | k for k in range(16)]]}
    obs = probe.Obs(mixed=((1, 300), (2, 212)),
                    scratch=tuple((4 * k, 0x7E570000 | k) for k in range(16)))
    assert probe.verdict(p, [obs]).settled


def test_tri_templates_never_write_tim():
    # a movs to tim stops the counter until the GPU is reset
    writes_tim = re.compile(r"^\s*(\(\w+\)\s*)?movsa?\s+tim\b", re.M)

    def code(text: str) -> str:
        return "\n".join(ln.split(";", 1)[0] for ln in text.splitlines())

    text = (SRC / "pixev_dump.s").read_text()
    assert SPDX in text
    assert not writes_tim.search(code(text))
    assert writes_tim.search("        (p0) movs tim, ds0[0], ds0[1], ds0[0], ds0[0]")
    for p in tri_probes():
        assert not writes_tim.search(code(p.params.get("OP", ""))), p.name


def test_tri_mock_output_parses(tmp_path):
    out = ("probe a__0: scratch at 0x3e003000 (64 KiB)\n"
           "probe a__0: tri 32x16, pixev eot replaced\n"
           "probe a__0: o0 mixed 0xff203040 x377 0xff00ff00 x135\n"
           "probe a__0: scratch +0x000 0x7e570000\n")
    obs = probe.parse(out)["a__0"]
    assert obs.failed is None and obs.scratch == ((0, 0x7E570000),)


@pytest.mark.skipif(not TOOL.exists(), reason="sgxfive-test not built")
def test_end_to_end_tri_on_the_mock(tri, tmp_path):
    # The mock draws the triangle from the replaced programs' first words but runs none of
    # them: the probe gets through the plumbing (helpers built, options right, the render
    # done), and stores nothing.
    sel = [p for p in tri if p.name in ("pds-pixel-event-readback", "pds-pixel-event-pixev-tall")]
    out = probe.run_local(sel, [str(TOOL), "--mock"], tmp_path / "work", src_dir=SRC)
    obs = probe.parse(out)
    for p in sel:
        o = obs[f"{p.name}__0"]
        assert o.failed is None, out
        assert o.mixed and not o.scratch, out
    assert "pds-pixel-event-readback: NONE of the hypotheses fits" in probe.report(sel, out)


@pytest.mark.skipif(not TOOL.exists(), reason="sgxfive-test not built")
def test_main_local_mock_with_the_tri_table(capsys):
    assert probe.main(["--table", str(PIXEL_EVENT), "local", "--tool", str(TOOL), "--mock",
                       "pds-pixel-event-readback"]) == 0
    assert "pds-pixel-event-readback: NONE of the hypotheses fits" in capsys.readouterr().out


def test_run_remote_sends_the_helpers(tri, tmp_path, monkeypatch):
    calls = []
    real_run = subprocess.run

    def fake_run(cmd, **kw):
        if cmd[0] not in ("ssh", "scp"):
            return real_run(cmd, **kw)          # the assemblers
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr(probe, "target", lambda: ("u@h", []))
    monkeypatch.setattr(probe.subprocess, "run", fake_run)
    sel = [p for p in tri if p.name == "pds-pixel-event-readback"]
    probe.run_remote(sel, tmp_path, SRC)
    scp = next(c for c in calls if c[0] == "scp")
    assert any(a.endswith("/task_dump.bin") for a in scp)
    loop = calls[-1][-1]
    assert "--slot pixtask=sgxprobes/task_dump.bin" in loop and "--tri pixev:60" in loop


def _remote_loop(tri, tmp_path, monkeypatch):
    calls = []
    real_run = subprocess.run

    def fake_run(cmd, **kw):
        if cmd[0] not in ("ssh", "scp"):
            return real_run(cmd, **kw)
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr(probe, "target", lambda: ("u@h", []))
    monkeypatch.setattr(probe.subprocess, "run", fake_run)
    probe.run_remote([p for p in tri if p.name == "pds-pixel-event-readback"], tmp_path, SRC)
    return calls[-1][-1]


def test_run_remote_records_the_counters(tri, tmp_path, monkeypatch):
    """Every case runs inside regtimeline over the visibility counters, after a line that
    names it (probe-case), so a scan finds the case that counted and the one before it."""
    monkeypatch.delenv("SGX_PROBE_COUNTERS", raising=False)
    loop = _remote_loop(tri, tmp_path, monkeypatch)
    assert 'echo "probe-case $(basename $f .bin)"' in loop
    assert "sudo -n ./regtimeline 0 0 0x0494-0x04b4 -- ./sgxfive-test probe" in loop


def test_run_remote_counters_off(tri, tmp_path, monkeypatch):
    monkeypatch.setenv("SGX_PROBE_COUNTERS", "0")
    loop = _remote_loop(tri, tmp_path, monkeypatch)
    assert "regtimeline" not in loop and "probe-case" not in loop


def test_report_says_which_cases_counted(tri):
    p = next(p for p in tri if p.name == "pds-pixel-event-readback")
    regs = " ".join(f"{o:#06x}" for o in range(0x494, 0x4b8, 4))
    out = ""
    for i in range(len(p.cases)):
        out += f"probe-case {p.name}__{i}\nprobe {p.name}__{i}: o0 0x00000000\n" \
            f"timeline: regs {regs} samples 9 seconds 0 start 0 end 9 rc 0\n" \
            "tl 0" + " 00000000" * 9 + "\n"
        if i == 0:
            out += "tl 7" + " 00000000" * 8 + " 00000004\n"
    rep = probe.report([p], out)
    assert "  counters: [0] 0x04b4 0x0..0x4" in rep
    assert probe.report([p], out.replace(" 00000004", " 00000000")).count("counters") == 0


def test_eot_helpers_do_not_skip_invalid_instances():
    """An end-of-tile task's instance counts as invalid: a .skipinv instruction there did not
    run (the scratch mov), so the helpers' own instructions carry none. The four
    PBE movs stay as use_eot.s has them (the host patches them in place)."""
    for name in ("eot_dump.s", "eot_tile.s"):
        lines = [ln.split(";")[0].strip() for ln in (SRC / name).read_text().splitlines()]
        code = [ln for ln in lines if ln and not ln.startswith(".")]
        own = code[5:]                     # past the phas and the four PBE movs
        assert own and not any(".skipinv" in ln for ln in own), name


def test_a_pixtask_helper_loads(tmp_path):
    """The pixel-event program's own plain task: the pixtask slot takes a helper."""
    t = tmp_path / "t.toml"
    t.write_text('[[probe]]\nname = "x"\nquestion = "q"\nsource = "pixev_dump.s"\n'
                 'host = "tri"\nslot = "pixev"\nslots = { pixtask = "task_dump.s" }\n'
                 'params = { OP = "nop" }\ncases = [[]]\n')
    (p,) = probe.load(t)
    assert p.slots == {"pixtask": "task_dump.s"}


def test_task_dump_is_a_plain_task():
    """task_dump.s stores sa0-sa15 to scratch dwords 0-15 with no .skipinv and no emit."""
    text = (SRC / "task_dump.s").read_text()
    code = [ln.split(";")[0].strip() for ln in text.splitlines()]
    code = [ln for ln in code if ln]
    assert not any(".skipinv" in ln or "emitpix" in ln for ln in code)
    for k in range(16):
        assert f"stad [r0,+#{k}], sa{k}" in code
    assert code[-1].split()[0].endswith(".end")


# the event bits of the end-of-tile event: a tile whose event
# has the bit runs the end-of-render task instead, which writes no pixels, so that tile keeps
# the sentinel; the ds1 word holding each mask is in the data segment of pixev_dump.s
EVENT_BITS = {2: "ds1[4]", 3: "ds1[2]", 8: "ds1[11]", 9: "ds1[12]", 10: "ds1[14]", 11: "ds1[18]"}


def test_tri_event_bit_probes():
    probes = by_name()
    for bit, mask in EVENT_BITS.items():
        for size in ((128, 128),) + (((64, 64),) if bit == 2 else ()):
            name = f"pds-pixel-event-pixev-event-bit{bit}" + ("-64" if size == (64, 64) else "")
            p = probes[name]
            assert p.host == "tri" and p.slot == "pixev" and p.slots == {} and p.size == size
            assert p.pixels, name
            op = p.params["OP"]
            assert f"and ds1[56], ir1, {mask}" in op and "movs doutu, ds0[2], ds0[3]" in op


def test_pixpds_is_a_pds_slot(tmp_path):
    """pixpds, the triangle's primary pixel PDS program, is a PDS slot like pixev and vtxpds."""
    assert "pixpds" in probe.TRI_SLOTS and "pixpds" in probe.TRI_PDS
    (p,) = table(tmp_path, 'source = "pds_prim.s"\nhost = "tri"\nslot = "pixpds"\n')
    assert p.isa == "pds" and p.slot == "pixpds"


def test_state_is_a_usse_slot(tmp_path):
    """state, the triangle's state task (use_mtest18.s), is a USSE slot."""
    assert "state" in probe.TRI_SLOTS and "state" not in probe.TRI_PDS
    (p,) = table(tmp_path, 'source = "pix_op.s"\nhost = "tri"\nslot = "state"\n')
    assert p.isa == "usse" and p.slot == "state"


def test_tri_iteration_sources_probe():
    """tri-iter-sources: the triangle's pixel PDS iterates DOUTI0.ATTR_SOURCE 0-63 (bit 30
    set, no texture fetch) into pa0, which pix_pa0.s writes out."""
    p = by_name()["pds-iteration-sources-iter-sources"]
    assert p.slot == "pixpds" and p.slots == {"pixel": "pix_pa0.s"} and p.pixels
    assert p.inputs == ["A"]
    assert [c[0] for c in p.cases] == [0x40000000 | s << 11 for s in range(64)]


def test_tri_vtx_coords_field(tmp_path):
    """vtx_coords = N: N more output dwords per vertex (sgxfive-test --vtx-coords N)."""
    (p,) = table(tmp_path, 'source = "pix.s"\nhost = "tri"\nslot = "pixel"\nvtx_coords = 2\n')
    assert p.vtx_coords == 2 and probe._tri_args(p)[-2:] == ["--vtx-coords", "2"]
    for bad in ("0", "12"):
        with pytest.raises(probe.ProbeError):
            table(tmp_path, f'source = "pix.s"\nhost = "tri"\nslot = "pixel"\nvtx_coords = {bad}\n')
    with pytest.raises(probe.ProbeError):
        table(tmp_path, 'source = "pix.s"\nvtx_coords = 2\n')      # not host = "tri"


def test_tri_texture_probes():
    """tri-tex-fetch: the triangle samples the scratch buffer (pds_tex.s, the closed driver's
    DOUTI0 and texture state, coordinates from vtx_coords.s); tri-tex-sources: the same fetch
    with DOUTI0.ATTR_SOURCE 0-63, what each puts in pa0 when the task waits for the fetch."""
    ps = by_name()
    for name in ("texture-fetch-tex-fetch", "texture-fetch-tex-sources"):
        p = ps[name]
        assert p.slot == "pixpds" and p.source == "pds_tex.s" and p.vtx_coords == 2, name
        assert p.slots == {"pixel": "pix_pa0.s", "vtxuse": "vtx_coords.s"} and p.pixels, name
    assert [c[0] for c in ps["texture-fetch-tex-fetch"].cases] == [0x46012201]
    assert [c[0] for c in ps["texture-fetch-tex-sources"].cases] == [0x40000001 | s << 11
                                                           for s in range(64)]


def test_tri_copy_depth_and_blk_fields(tmp_path):
    """copy_depth = true and blk = { N = V }: sgxfive-test --copy-depth and --blk N=V."""
    (p,) = table(tmp_path, 'source = "pix.s"\nhost = "tri"\nslot = "pixel"\nvertices = 6\n'
                           'copy_depth = true\nblk = { 1 = 0x00400200, 10 = 0x3e99999a }\n')
    assert p.copy_depth and p.blk == {1: 0x00400200, 10: 0x3e99999a}
    args = probe._tri_args(p)
    assert "--copy-depth" in args
    assert args[args.index("--blk") + 1] == "1=0x00400200"
    assert args[len(args) - 1 - args[::-1].index("--blk") + 1] == "10=0x3e99999a"
    for bad in ('vertices = 6\nblk = { 18 = 1 }\n', 'copy_depth = true\n',
                'vertices = 6\nblk = { x = 1 }\n'):
        with pytest.raises(probe.ProbeError):
            table(tmp_path, 'source = "pix.s"\nhost = "tri"\nslot = "pixel"\n' + bad)


def test_tri_blk_add_field(tmp_path):
    """blk_add = { BIT = V, 7 = [V, V] }: sgxfive-test --blk-add BIT=V[,V], presence bits 2-5
    (one word) and 7 (two) added to the state block."""
    (p,) = table(tmp_path, 'source = "pix.s"\nhost = "tri"\nslot = "pixel"\n'
                           'blk_add = { 3 = 0x0e0200ff, 7 = [0x0000ffff, 0x00000001] }\n')
    assert p.blk_add == {3: (0x0e0200ff,), 7: (0x0000ffff, 0x00000001)}
    args = probe._tri_args(p)
    assert args[args.index("--blk-add") + 1] == "3=0x0e0200ff"
    assert args[len(args) - 1 - args[::-1].index("--blk-add") + 1] == "7=0x0000ffff,0x00000001"
    for bad in ('blk_add = { 0 = 1 }\n', 'blk_add = { 7 = 1 }\n', 'blk_add = { 3 = [1, 2] }\n',
                'blk_add = { x = 1 }\n'):
        with pytest.raises(probe.ProbeError):
            table(tmp_path, 'source = "pix.s"\nhost = "tri"\nslot = "pixel"\n' + bad)



def test_tri_obj2_field(tmp_path):
    """obj2 = { first = N, blk = { W = V }, pixel = "file.s" }: sgxfive-test --obj2 N,
    --obj2-blk W=V and --obj2-pixel FILE; the pixel shader is a helper built with the rest."""
    (p,) = table(tmp_path, 'source = "pix.s"\nhost = "tri"\nslot = "pixel"\nvertices = 6\n'
                           'obj2 = { first = 3, blk = { 1 = 0x00400200 }, pixel = "pix_op.s" }\n')
    assert p.obj2 == {"first": 3, "blk": {1: 0x00400200}, "pixel": "pix_op.s"}
    args = probe._tri_args(p)
    assert args[args.index("--obj2") + 1] == "3"
    assert args[args.index("--obj2-blk") + 1] == "1=0x00400200"
    assert args[args.index("--obj2-pixel") + 1] == "pix_op.bin"
    assert ("pix_op.s", "usse") in probe._helpers(p)
    assert probe._with_use(tuple(args), "dir")[args.index("--obj2-pixel") + 1] == "dir/pix_op.bin"
    for bad in ('vertices = 6\nobj2 = { first = 4 }\n', 'vertices = 6\nobj2 = { first = 6 }\n',
                'obj2 = { first = 3 }\n', 'vertices = 6\nobj2 = { first = 3, blk = { 32 = 1 } }\n',
                'vertices = 6\nobj2 = { first = 3, colour = 1 }\n'):
        with pytest.raises(probe.ProbeError):
            table(tmp_path, 'source = "pix.s"\nhost = "tri"\nslot = "pixel"\n' + bad)


def test_tri_vdm_field(tmp_path):
    """vdm = { N = V }: sgxfive-test --vdm N=V, VDM stream words 0-10."""
    (p,) = table(tmp_path, 'source = "pix.s"\nhost = "tri"\nslot = "pixel"\n'
                           'vdm = { 4 = 0xf4000000, 7 = 0x01c00083 }\n')
    assert p.vdm == {4: 0xf4000000, 7: 0x01c00083}
    args = probe._tri_args(p)
    assert args[args.index("--vdm") + 1] == "4=0xf4000000"
    assert args[len(args) - 1 - args[::-1].index("--vdm") + 1] == "7=0x01c00083"
    for bad in ('vdm = { 11 = 1 }\n', 'vdm = { x = 1 }\n'):
        with pytest.raises(probe.ProbeError):
            table(tmp_path, 'source = "pix.s"\nhost = "tri"\nslot = "pixel"\n' + bad)

DEPTH_SCENES = {"always": 0x01D00200, "less": 0x00400200, "translucent": 0x02400200,
                "translucent-nowrite": 0x03D00200, "punch": 0x08400200}


def test_tri_depth_scenes():
    """tri-depth-*: five copies of the triangle at clip z = 0, 1/16 .. 4/16 (copy_depth), each
    pixel coloured with the z of the copy that won it (vtx_z.s, pds_tex.s source 1), under the
    ISP0 word (blk 1) of each scene."""
    ps = by_name()
    for scene, isp0 in DEPTH_SCENES.items():
        p = ps[f"isp-depth-test-{scene}"]
        assert p.vertices == 15 and p.copy_depth and p.blk == {1: isp0}, scene
        assert p.slots == {"pixel": "pix_pa0.s", "vtxuse": "vtx_z.s"} and p.vtx_coords == 2
        assert [c[0] for c in p.cases] == [0x40000801], scene


def test_tri_douti_probes():
    """tri-douti-bits: DOUTI0 bits 17-29 and 31 flipped on the textured triangle's source 1;
    tri-douti-pa0..pa3: each primary attribute under the bits that resize the iteration."""
    ps = by_name()
    base = 0x40000801
    assert [c[0] for c in ps["pds-iteration-sources-douti-bits"].cases][:15] == [base] + [
        base ^ (1 << k) for k in list(range(17, 30)) + [31]]
    for k in range(4):
        p = ps[f"pds-iteration-sources-douti-pa{k}"]
        assert p.slots["pixel"] == f"pix_pa{k}.s" and len(p.cases) == 7


def test_tri_depth_slope_probes():
    """tri-depth-slope: the triangle with z = clip x (vtx_zx.s), depth less against the
    background's 1.0 with the viewport's z offset 0.75 (blk 10): where the depth passes 1.0;
    tri-src34-pa0/pa2: source 34's first and third dwords on it."""
    ps = by_name()
    p = ps["isp-depth-test-slope"]
    assert p.slots["vtxuse"] == "vtx_zx.s" and p.blk == {1: 0x00400200, 10: 0x3F400000}
    for k in (0, 2):
        q = ps[f"pds-iteration-sources-src34-pa{k}"]
        assert q.slots["pixel"] == f"pix_pa{k}.s" and [c[0] for c in q.cases] == [0x40811001]


def test_tri_framebuffer_fetch_probes():
    """tri-fbf-opaque/translucent: a pixel shader that reads o0 (pix_op.s), in the opaque pass
    and in a translucent one (blk 1, pass type 1): whether o0 holds the destination colour."""
    ps = by_name()
    assert ps["usse-output-registers-fbf-opaque"].blk == {}
    assert ps["usse-output-registers-fbf-translucent"].blk == {1: 0x03D00200}
    for name in ("usse-output-registers-fbf-opaque", "usse-output-registers-fbf-translucent"):
        p = ps[name]
        assert p.slot == "pixel" and p.source == "pix_op.s" and p.inputs == ["OP"]
        assert [c[0] for c in p.cases][0] == "mov.skipinv.end o0, o0"


def test_tri_w_probe():
    """tri-w-scan: the vertex shader's w (vtx_w.s) from 2 down to 0 and below: how the
    triangle's size follows 1/w and what happens below the state block's WCLAMP (1e-5)."""
    p = by_name()["mte-clipping-w-scan"]
    assert p.slot == "vtxuse" and p.source == "vtx_w.s" and p.inputs == ["W"]
    assert len(p.cases) == 12 and p.cases[0] == [0x3F800000]


def test_tri_isp2_field(tmp_path):
    """isp2 = V: ISP word 2 (stencil) in the state block (sgxfive-test --isp2 V)."""
    (p,) = table(tmp_path, 'source = "pix.s"\nhost = "tri"\nslot = "pixel"\nisp2 = 0x0e0200ff\n')
    assert p.isp2 == 0x0e0200ff
    args = probe._tri_args(p)
    assert args[args.index("--isp2") + 1] == "0x0e0200ff"
    (p,) = table(tmp_path, 'source = "pix.s"\nhost = "tri"\nslot = "pixel"\n')
    assert p.isp2 is None and "--isp2" not in probe._tri_args(p)
    for bad in ("-1", "0x100000000"):
        with pytest.raises(probe.ProbeError):
            table(tmp_path, f'source = "pix.s"\nhost = "tri"\nslot = "pixel"\nisp2 = {bad}\n')


def test_tri_sideband_field(tmp_path):
    """sideband = V (with an eot slot): sgxfive-test --sideband V."""
    (p,) = table(tmp_path, 'source = "pix.s"\nhost = "tri"\nslot = "pixel"\n'
                           'slots = { eot = "eot_tile.s" }\nsideband = 0x2240\n')
    assert p.sideband == 0x2240
    args = probe._tri_args(p)
    assert args[args.index("--sideband") + 1] == "0x00002240"
    for bad in ('sideband = 0x200\n', 'slots = { eot = "eot_tile.s" }\nsideband = -1\n'):
        with pytest.raises(probe.ProbeError):
            table(tmp_path, 'source = "pix.s"\nhost = "tri"\nslot = "pixel"\n' + bad)


def test_tri_cmd_field(tmp_path):
    """cmd = { N = V }: sgxfive-test --cmd N=V, render command words 0-25."""
    (p,) = table(tmp_path, 'source = "pix.s"\nhost = "tri"\nslot = "pixel"\n'
                           'cmd = { 13 = 0x80000002, 16 = 0xeaa26e26 }\n')
    assert p.cmd == {13: 0x80000002, 16: 0xeaa26e26}
    args = probe._tri_args(p)
    assert args[args.index("--cmd") + 1] == "13=0x80000002"
    assert args[len(args) - 1 - args[::-1].index("--cmd") + 1] == "16=0xeaa26e26"
    for bad in ('cmd = { 26 = 1 }\n', 'cmd = { x = 1 }\n'):
        with pytest.raises(probe.ProbeError):
            table(tmp_path, 'source = "pix.s"\nhost = "tri"\nslot = "pixel"\n' + bad)


def test_tri_dump_render_field(tmp_path):
    """dump_render = true: sgxfive-test --dump-render into the run's dumps directory (under
    the helpers' directory remotely); tri probes only."""
    (p,) = table(tmp_path, 'source = "pix.s"\nhost = "tri"\nslot = "pixel"\ndump_render = true\n')
    assert p.dump_render
    args = probe._tri_args(p)
    assert args[args.index("--dump-render") + 1] == probe.DUMPS
    moved = probe._with_use(tuple(args), "sgxprobes")
    assert moved[moved.index("--dump-render") + 1] == "sgxprobes/" + probe.DUMPS
    (q,) = table(tmp_path, 'source = "pix.s"\nhost = "tri"\nslot = "pixel"\n')
    assert not q.dump_render and "--dump-render" not in probe._tri_args(q)
    with pytest.raises(probe.ProbeError):
        table(tmp_path, 'source = "x.s"\ndump_render = true\n')


def _remote_calls(sel, tmp_path, monkeypatch):
    calls = []
    real_run = subprocess.run

    def fake_run(cmd, **kw):
        if cmd[0] not in ("ssh", "scp"):
            return real_run(cmd, **kw)
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr(probe, "target", lambda: ("u@h", []))
    monkeypatch.setattr(probe.subprocess, "run", fake_run)
    probe.run_remote(sel, tmp_path, SRC)
    return calls


def test_run_remote_fetches_the_dumps(tmp_path, monkeypatch):
    """A dump_render probe's dumps land in sgxprobes/dumps on the target, which the run
    makes first and copies back to the work directory's dumps/ after the cases; the tool
    runs as root to read debugfs even without the counters."""
    monkeypatch.setenv("SGX_PROBE_COUNTERS", "0")
    (p,) = table(tmp_path, 'source = "pix_pa0.s"\nhost = "tri"\nslot = "pixel"\n'
                           'dump_render = true\n')
    calls = _remote_calls([p], tmp_path / "w", monkeypatch)
    assert "mkdir -p sgxprobes/" + probe.DUMPS in calls[0][-1]
    loop = next(c[-1] for c in calls if c[0] == "ssh" and "sgxfive-test" in c[-1])
    assert "sudo -n ./sgxfive-test probe" in loop
    assert "--dump-render sgxprobes/" + probe.DUMPS in loop
    back = calls[-1]
    assert back[0] == "scp" and "-r" in back and back[-2] == "u@h:sgxprobes/" + probe.DUMPS
    assert back[-1] == str(tmp_path / "w")


def test_save_dumps(tmp_path):
    """The dumps the run fetched are kept with it (out/dumps)."""
    work, out = tmp_path / "w", tmp_path / "o"
    (work / probe.DUMPS).mkdir(parents=True)
    (work / probe.DUMPS / "t__0.param.bin").write_bytes(b"\1\2")
    probe.save_dumps(work, out)
    assert (out / probe.DUMPS / "t__0.param.bin").read_bytes() == b"\1\2"
    probe.save_dumps(tmp_path / "none", out)                  # no dumps: nothing to do


def test_dump_table():
    """The render dumps: one case each, every one a dump_render tri probe."""
    ps = dump_probes()
    assert ps and all(p.host == "tri" and p.dump_render for p in ps)
    assert {"mte-mtectl-mte-bit6", "ta-zero-words-cull-culled"} <= {p.name for p in ps}


def test_tri_kpoke_field(tmp_path, monkeypatch):
    """kpoke = ["ta:N=V", ...]: sgxfive-test --kpoke SPEC each (the kernel-built words of the
    case's render), run as root on the target; tri probes only, specs as debugfs kpoke takes."""
    (p,) = table(tmp_path, 'source = "pix_pa0.s"\nhost = "tri"\nslot = "pixel"\n'
                           'kpoke = ["ta:152=0x40000000", "rd:5^=0x1"]\n')
    assert p.kpoke == ["ta:152=0x40000000", "rd:5^=0x1"]
    args = probe._tri_args(p)
    assert [args[i + 1] for i, a in enumerate(args) if a == "--kpoke"] == p.kpoke
    for bad in ('kpoke = ["ta:x=1"]\n', 'kpoke = ["xx:1=1"]\n', 'kpoke = "ta:1=1"\n'):
        with pytest.raises(probe.ProbeError):
            table(tmp_path, 'source = "pix_pa0.s"\nhost = "tri"\nslot = "pixel"\n' + bad)
    monkeypatch.setenv("SGX_PROBE_COUNTERS", "0")
    calls = _remote_calls([p], tmp_path / "w", monkeypatch)
    loop = next(c[-1] for c in calls if c[0] == "ssh" and "sgxfive-test" in c[-1])
    assert "sudo -n ./sgxfive-test probe" in loop and "--kpoke ta:152=0x40000000" in loop


def test_tri_vdm_xor_field(tmp_path):
    """vdm_xor = { N = V }: sgxfive-test --vdm N^=V, VDM stream words 0-10 flipped by V."""
    (p,) = table(tmp_path, 'source = "pix.s"\nhost = "tri"\nslot = "pixel"\n'
                           'vdm_xor = { 6 = 0x80000000 }\n')
    assert p.vdm_xor == {6: 0x80000000}
    args = probe._tri_args(p)
    assert args[args.index("--vdm") + 1] == "6^=0x80000000"
    with pytest.raises(probe.ProbeError):
        table(tmp_path, 'source = "pix.s"\nhost = "tri"\nslot = "pixel"\nvdm_xor = { 11 = 1 }\n')
