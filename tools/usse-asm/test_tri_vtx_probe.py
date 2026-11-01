# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The vertex PDS probes of the triangle host (probes/pds/vertex-programs.toml): what if0 and if1
mean in a vertex PDS program. The table loads and assembles, its helpers keep use_vtx.s's
shape, its hypotheses are what the slot model of vtx_dump.s predicts, and the plumbing
runs end to end on the mock."""
from __future__ import annotations

import pathlib
import re
import struct

import pytest

import probe

HERE = pathlib.Path(__file__).resolve().parent
TOOL = HERE.parent.parent / "userspace" / "libsgxfive" / "build" / "sgxfive-test"
TABLE = probe.PROBES / "pds" / "vertex-programs.toml"
SRC = TABLE.parent / "templates"
SAFE = ("pds-vertex-programs-if0", "pds-vertex-programs-if1-if0",
        "pds-vertex-programs-always", "pds-vertex-programs-douta")
RISKY = ("pds-vertex-programs-if1", "pds-vertex-programs-not-if0")
# the mov16 flag as a select on if0: T = 0, then the move into T's low
# half, then the kick only where T is nonzero (all hang unless the kick is the last vertex's)
FLAG = ("pds-vertex-programs-flag-pc", "pds-vertex-programs-plain-pc",
        "pds-vertex-programs-zero")
FLAG_MOVE = {"pds-vertex-programs-flag-pc": 0x0F010A60,
             "pds-vertex-programs-plain-pc": 0x0F010860, "pds-vertex-programs-zero": None}
KICK = "movs doutu, ds0[2], ds0[3], ds1[1], ds1[1]"


def f32(x: float) -> int:
    return struct.unpack("<I", struct.pack("<f", x))[0]


# The default triangle (sgxfive_tri_default): (8, 8), (56, 20), (20, 56) of 64 x 64, in clip
# space ndc = px / 32 - 1 whatever the size (render.c's ndc()).
VERTICES = [(8, 8), (56, 20), (20, 56)]
CLIP = [(v[0] / 32 - 1, v[1] / 32 - 1) for v in VERTICES]
SENTINEL = f32(1.0)


def slot(x_bits: int) -> int:
    """vtx_dump.s's slot of a vertex: (x >> 30 & 2) | (x >> 23 & 1)."""
    return ((x_bits >> 30) & 2) | ((x_bits >> 23) & 1)


def model(tasks: list, sa: list | None = None) -> list:
    """Scratch dwords 0-63 after vtx_dump.s (vtx_dump_sa.s with sa) ran for the tasks given
    as lists of vertices, instance j of a task holding its j-th vertex."""
    d = [probe.SCRATCH_FILL | i for i in range(64)]
    for t in tasks:
        xs = [f32(CLIP[v][0]) for v in t]
        for j, v in enumerate(t):
            x, y = CLIP[v]
            s = slot(f32(x))
            others = [xs[(j + k) % 4] if (j + k) % 4 < len(t) else SENTINEL for k in (1, 2, 3)]
            words = [0x7E570000 | s, f32(x), f32(y), 0, f32(1.0)] + others + (sa or [])
            d[16 * s:16 * s + len(words)] = words
    return d


@pytest.fixture(scope="module")
def vtx():
    return {p.name: p for p in probe.load(TABLE)}


def test_slots_separate_the_vertices():
    slots = [slot(f32(x)) for x, _ in CLIP]
    assert slots == [2, 0, 3]
    assert slot(SENTINEL) == 1 and 1 not in slots   # the sentinel's slot stays unwritten


def test_table_loads(vtx):
    assert list(vtx) == list(SAFE[:3]) + [SAFE[3]] + list(RISKY) + list(FLAG)
    for p in vtx.values():
        assert p.host == "tri" and p.slot == "vtxpds" and p.isa == "pds", p.name
        assert p.table == "vertex-programs.toml" and p.size == (64, 64) and p.temps == 16
        assert p.slots == {"vtxuse": "vtx_dump_sa.s" if p.name == "pds-vertex-programs-douta"
                           else "vtx_dump.s"}
        assert len(p.cases) == 1 and p.hypotheses


def test_table_assembles(vtx, tmp_path):
    for p in vtx.values():
        (f,) = probe.build(p, tmp_path, SRC)
        assert f.stat().st_size % 4 == 0
        assert probe.pds_data(p, SRC) == (12 if p.name == "pds-vertex-programs-douta" else 8), p.name
        (h,) = probe.build_helpers([p], tmp_path, SRC)
        assert h.stat().st_size % 8 == 0


def test_tool_args(vtx):
    assert probe.tool_args(vtx["pds-vertex-programs-if0"], src_dir=SRC) == [
        "--temps", "16", "--tri", "vtxpds:8", "--width", "64", "--height", "64",
        "--slot", "vtxuse=vtx_dump.bin"]
    assert probe.tool_args(vtx["pds-vertex-programs-douta"], src_dir=SRC)[3:4] == ["vtxpds:12"]


def test_kicks(vtx):
    def kicks(p):
        return [ln.strip() for ln in p.params["KICK"].splitlines() if ln.strip()]

    assert kicks(vtx["pds-vertex-programs-if0"]) == [f"(if0) {KICK}"]      # the default's
    assert kicks(vtx["pds-vertex-programs-if1-if0"]) == [f"(if1) {KICK}", f"(if0) {KICK}"]
    assert kicks(vtx["pds-vertex-programs-always"]) == [KICK]
    assert kicks(vtx["pds-vertex-programs-if1"]) == [f"(if1) {KICK}"]
    assert kicks(vtx["pds-vertex-programs-not-if0"]) == ["(if0) bra skip", KICK, "skip:"]
    for name, word in FLAG_MOVE.items():
        move = [] if word is None else [f".word 0x{word:08x}"]
        got = [ln.split(";")[0].strip() for ln in kicks(vtx[name])]
        assert got == ["mov32 ds0[48], ds1[1]", *move, "tstz p0, ds0[48]",
                       "(p0) bra skip", KICK, "skip:"], name


def test_flag_moves_are_the_fields_they_name(pds_dis):
    """mov16 into the low half of ds0[48] (half index 96) from special field 266 (pc.l
    with the flag: pc.1.l) and 264 (pc.0.l)."""
    flag, plain = FLAG_MOVE["pds-vertex-programs-flag-pc"], FLAG_MOVE["pds-vertex-programs-plain-pc"]
    for w, fld in ((flag, 266), (plain, 264)):
        assert w >> 27 == 1 and w >> 24 & 7 == 7 and w >> 8 & 0x1FF == fld
        assert w >> 7 & 1 == 0 and w & 0x7F == 96
    assert pds_dis([plain, flag]) == ["mov16 ds0[96], pc.0.l", "mov16 ds0[96], pc.1.l"]


def test_kick_template_is_the_default_but_its_kick():
    """vtx_kick.s with the default's kick is asm/tri/pds_vtx.s, word for word."""
    p = probe.Probe(name="x", question="q", source="vtx_kick.s", params={
        "KICK": f"        (if0) {KICK}"}, inputs=[], cases=[[]], hypotheses={}, isa="pds")
    text = probe.render(p, [], (SRC / "vtx_kick.s").read_text())
    ours = probe._assemble(text, pathlib.Path("/dev/null"), "pds")
    default = probe._assemble((HERE.parent.parent / "asm" / "tri" / "pds_vtx.s").read_text(),
                              pathlib.Path("/dev/null"), "pds")

    def words(listing):
        return [ln.split("\t")[0].split(":")[1].strip() for ln in listing.splitlines() if ln]

    assert words(ours) == words(default)


@pytest.mark.parametrize("name", ["vtx_dump.s", "vtx_dump_sa.s"])
def test_helper_keeps_use_vtx_shape(name):
    """As use_vtx.s: a phas whose next phase is the second phas (the host relocates it), the
    vertex emitted to the VCB at the end of phase 0 and to the MTE in phase 1; scratch
    immediates only within the slot (64 bytes, the register offset adds 64 x slot)."""
    listing = probe._assemble((SRC / name).read_text(),
                              pathlib.Path("/dev/null"))
    code = [ln.split("\t", 1)[1].strip() for ln in listing.splitlines() if "\t" in ln]
    phases = [i for i, c in enumerate(code) if c.startswith("phas")]
    assert phases[0] == 0 and len(phases) == 2
    assert code[0].startswith(f"phas #{phases[1]}, #0, pixel, vcull")
    assert code[phases[1] - 1].startswith("emitvcbvtx.end")
    assert code[-1].startswith("emitmtevtx.end")
    imms = [int(m, 16) for m in re.findall(r"#0x5CAF([0-9A-F]{4})", "\n".join(code))]
    words = 16 if name == "vtx_dump_sa.s" else 8
    assert imms == [4 * j for j in range(words)]
    stores = [c for c in code if c.startswith("stad")]
    assert len(stores) == words and all(c.startswith("stad.skipinv [r8,+r1]") for c in stores)
    assert "or.skipinv r1, r1, #0x00400000" in code      # 64 bytes per slot


def test_no_template_writes_tim(vtx):
    writes_tim = re.compile(r"^\s*(\(\w+\)\s*)?movsa?\s+tim\b", re.M)
    for name in ("vtx_kick.s", "vtx_douta.s"):
        text = (SRC / name).read_text()
        assert not writes_tim.search("\n".join(ln.split(";")[0] for ln in text.splitlines()))
    for p in vtx.values():
        assert not writes_tim.search(p.params.get("KICK", "")), p.name


def test_hypotheses_are_the_model(vtx):
    one, single = [[0, 1, 2]], [[0], [1], [2]]
    sa = [0x7E570000, 0x7E570001, 0x7E570002, 0x7E57FFFF,
          0x7E570000, 0x7E570000, 0x7E570000, 0x7E57FFFF]
    want = {
        "pds-vertex-programs-if0": [model(one), model(single)],
        "pds-vertex-programs-if1-if0": [model([[0], [1, 2]]), model(one)],
        "pds-vertex-programs-always": [model(single), "fail"],
        "pds-vertex-programs-douta": [model(one, sa)],
        # a hang still reports what the vertices that ran stored
        "pds-vertex-programs-if1": [model(one), model(single), {"fail": True, "dwords": model([[0]])}],
        "pds-vertex-programs-not-if0": [model(single), {"fail": True, "dwords": model([[0], [1]])}],
        # a kick before the last vertex hangs after one task's stores (pds-vertex-programs-always and
        # -not-if0 on the hardware); no kick at all hangs with nothing stored
        "pds-vertex-programs-flag-pc": [model(one), {"fail": True, "dwords": model([])},
                            {"fail": True, "dwords": model(one)}],
        "pds-vertex-programs-plain-pc": [model(one), {"fail": True, "dwords": model(one)}],
        "pds-vertex-programs-zero": [model(one), {"fail": True, "dwords": model([])}],
    }
    for name, exps in want.items():
        assert [e for (e,) in vtx[name].hypotheses.values()] == exps, name


def test_hypotheses_tell_the_readings_apart(vtx):
    """Each probe's hypotheses are told apart by its readback (no two predict the same), and
    the readback of one fits only its own hypothesis."""
    for p in vtx.values():
        exps = [e for (e,) in p.hypotheses.values()]
        assert len({repr(e) for e in exps}) == len(exps), p.name
        for h, (e,) in p.hypotheses.items():
            dwords = e["dwords"] if isinstance(e, dict) else e
            stored = () if e == "fail" else tuple(
                (4 * i, v) for i, v in enumerate(dwords) if v != probe.SCRATCH_FILL | i)
            if e == "fail" or isinstance(e, dict):
                obs = probe.Obs(failed="hung", scratch=stored)
            else:
                obs = probe.Obs(mixed=((1, 3000), (2, 1096)), scratch=stored)
            assert probe.verdict(p, [obs]).settled == h, (p.name, h)


def test_the_last_vertex_reading_settles_the_default(vtx):
    """Rogue's reading: one task of all three; each vertex sees the other two's x."""
    (exp,) = vtx["pds-vertex-programs-if0"].hypotheses["if0 = last vertex in task: one task of 0, 1, 2"]
    s0 = exp[16 * 2:16 * 2 + 8]          # vertex 0, instance 0
    assert s0 == [0x7E570002, f32(-0.75), f32(-0.75), 0, f32(1.0),
                  f32(0.75), f32(-0.375), SENTINEL]


@pytest.mark.skipif(not TOOL.exists(), reason="sgxfive-test not built")
def test_end_to_end_on_the_mock(vtx, tmp_path):
    # The mock runs none of the programs: the probes get through the plumbing (the helper
    # built, the options right, the render done) and store nothing.
    sel = list(vtx.values())
    out = probe.run_local(sel, [str(TOOL), "--mock"], tmp_path / "work", src_dir=SRC)
    obs = probe.parse(out)
    for p in sel:
        o = obs[f"{p.name}__0"]
        assert o.failed is None, out
        assert o.mixed and not o.scratch, out
    assert "pds-vertex-programs-if0: NONE of the hypotheses fits" in probe.report(sel, out)


@pytest.mark.skipif(not TOOL.exists(), reason="sgxfive-test not built")
def test_main_local_mock(capsys):
    assert probe.main(["--table", str(TABLE), "local", "--tool", str(TOOL), "--mock",
                       "pds-vertex-programs-if0"]) == 0
    assert "pds-vertex-programs-if0: NONE of the hypotheses fits" in capsys.readouterr().out
