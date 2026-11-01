# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""probe.py: the hardware probe tables (probes/<unit>/<feature>.toml), their programs, the parser of
sgxfive-test's probe output and the verdicts. The hardware runs are not tested here; an
end-to-end run goes through sgxfive-test --mock."""
from __future__ import annotations

import os
import pathlib
import shutil
import subprocess

import pytest

import probe

HERE = pathlib.Path(__file__).resolve().parent
TOOL = HERE.parent.parent / "userspace" / "libsgxfive" / "build" / "sgxfive-test"
PROBES = probe.PROBES
# the tables that hold probes (the others hold sweeps or scripts), each with its templates
TABLES = sorted(t for t in PROBES.glob("*/*.toml") if "[[probe]]" in t.read_text())


def _src(t):
    return t.parent / "templates"


@pytest.fixture(scope="module")
def table():
    return probe.load()


def test_table_loads(table):
    assert len(table) >= 10
    names = [p.name for p in table]
    assert len(names) == len(set(names))
    for p in table:
        assert probe.NAME_RE.fullmatch(p.name), p.name
        assert p.cases, p.name
        assert p.question, p.name


def test_every_table_is_loaded(table):
    assert len(table) == sum(len(probe.load(t)) for t in TABLES) > 100


def test_hypotheses_cover_every_case_and_differ(table):
    for p in table:
        vecs = list(p.hypotheses.values())
        for name, v in p.hypotheses.items():
            assert len(v) == len(p.cases), (p.name, name)
        # Two hypotheses with the same predictions could never be told apart.
        assert len({repr(v) for v in vecs}) == len(vecs), p.name


SPDX = "SPDX-" + "License-Identifier: MIT"   # split, so that reuse does not parse it


def test_sources_carry_spdx():
    sources = list(PROBES.glob("*/templates/*.s"))
    assert len(sources) > 50
    for s in sources:
        assert SPDX in s.read_text(), s


@pytest.mark.parametrize("path", TABLES, ids=lambda t: f"{t.parent.name}/{t.stem}")
def test_every_case_assembles(path, tmp_path):
    for p in probe.load(path):
        if p.host == "tri":         # a slot of a render: the host patches it, no fill to build
            continue
        files = probe.build(p, tmp_path, _src(path))
        assert len(files) == len(p.cases)
        width = 4 if p.isa == "pds" else 8
        for f in files:
            data = f.read_bytes()
            assert data and len(data) % width == 0 and len(data) <= 256 * 8, f
            assert probe.FILE_RE.fullmatch(f.stem), f


def test_render_substitutes_params_and_inputs():
    p = probe.Probe(name="x", question="q", source="pred.s", params={"OP": "nop"},
                    inputs=["A", "B"], cases=[[1, 0x80000000]], hypotheses={})
    text = probe.render(p, p.cases[0], "mov.skipinv r1, #{A}\n{OP}\nmov r2, #{B}\n")
    assert text == "mov.skipinv r1, #0x00000001\nnop\nmov r2, #0x80000000\n"


def test_render_rejects_an_unfilled_placeholder():
    p = probe.Probe(name="x", question="q", source="pred.s", params={}, inputs=["A"],
                    cases=[[1]], hypotheses={})
    with pytest.raises(probe.ProbeError):
        probe.render(p, p.cases[0], "mov r1, #{A}\n{OP}\n")


OUTPUT = """programs asm
probe a__0: scratch at 0x3e003000
probe a__0: o0 0x00000001 (2048 of 2048)
probe a__1: scratch at 0x3e003000
probe a__1: o0 mixed 0x00000001 x1024 0x00000000 x1024
probe a__2: scratch at 0x3e003000
probe a__2: failed: Connection timed out
probe a__3: scratch at 0x3e003000
probe a__3: o0 0x00000000 (2048 of 2048)
probe a__3: scratch +0x104 0x11111111
"""


def test_parse():
    obs = probe.parse(OUTPUT)
    assert obs["a__0"] == probe.Obs(o0=1)
    assert obs["a__1"] == probe.Obs(o0=None, mixed=((1, 1024), (0, 1024)))
    assert obs["a__2"] == probe.Obs(failed="Connection timed out")
    assert obs["a__3"] == probe.Obs(o0=0, scratch=((0x104, 0x11111111),))



def test_a_failed_job_keeps_its_scratch():
    # what ran before a render hung stored to the scratch: the host still reports it
    obs = probe.parse("probe a__0: failed: job faulted, context lost (Input/output error)\n"
                      "probe a__0: scratch +0x008 0x7e570002\n"
                      "probe b__0: failed: job faulted\n"
                      "probe b__0: scratch unchanged\n")
    assert obs["a__0"] == probe.Obs(failed="job faulted, context lost (Input/output error)",
                                    scratch=((8, 0x7E570002),))
    assert obs["b__0"] == probe.Obs(failed="job faulted")
    assert probe.describe(obs["a__0"]) == \
        "failed (job faulted, context lost (Input/output error)) scratch +0x008=0x7e570002"
    # {fail = true}: the job failed; "dwords" (the list form) and "scratch" still apply
    a = obs["a__0"]
    assert probe.matches({"fail": True}, a)
    assert probe.matches({"fail": True, "dwords": [0xD0000000, 0xD0000001, 0x7E570002]}, a)
    assert not probe.matches({"fail": True, "dwords": [0x7E570002]}, a)
    assert probe.matches({"fail": True, "scratch": {"0x8": 0x7E570002}}, a)
    assert not probe.matches({"fail": True, "scratch": {}}, a)
    assert probe.matches({"fail": True, "scratch": {}}, obs["b__0"])
    assert not probe.matches({"fail": True}, probe.Obs(o0=1))
    # without it a table still wants a job that completed; "dwords" is the list form
    assert not probe.matches({"dwords": [0xD0000000]}, a)
    assert probe.matches({"dwords": [5]}, probe.Obs(o0=0, scratch=((0, 5),)))
    assert probe.matches([5], probe.Obs(o0=0, scratch=((0, 5),)))

def test_expect_forms():
    assert probe.matches(1, probe.Obs(o0=1))
    assert not probe.matches(1, probe.Obs(o0=0))
    assert not probe.matches(1, probe.Obs(failed="x"))
    assert probe.matches("fail", probe.Obs(failed="x"))
    assert probe.matches({"scratch": {"0x104": 0x11111111}},
                         probe.Obs(o0=0, scratch=((0x104, 0x11111111),)))
    # the scratch set is exact: no changed dword may be missing or extra
    assert not probe.matches({"scratch": {}}, probe.Obs(o0=0, scratch=((0x104, 1),)))
    assert probe.matches({"o0": 0, "scratch": {}}, probe.Obs(o0=0))
    assert not probe.matches(1, probe.Obs(o0=None, mixed=((1, 1024), (0, 1024))))
    # most: o0, or the value of at least 90% of the pixels when they differ
    assert probe.matches({"most": 1}, probe.Obs(o0=1))
    assert probe.matches({"most": 1}, probe.Obs(mixed=((1, 2020), (0, 28))))
    assert not probe.matches({"most": 1}, probe.Obs(mixed=((1, 1024), (0, 1024))))
    assert not probe.matches({"most": 0}, probe.Obs(mixed=((1, 2020), (0, 28))))
    # o0_not: anything but that value, a failed job excluded
    assert probe.matches({"o0_not": 1}, probe.Obs(o0=2))
    assert not probe.matches({"o0_not": 1}, probe.Obs(o0=1))
    assert not probe.matches({"o0_not": 1}, probe.Obs(failed="x"))


def test_expect_dump_list():
    # a list: the first scratch dwords in order (dump.s stores its registers there); a value
    # equal to the dword's fill shows as unchanged, the dwords after the list are not checked
    obs = probe.Obs(o0=0, scratch=((0x0, 5), (0x8, 7), (0x40, 9)))
    assert probe.matches([5, 0xD0000001, 7], obs)
    assert probe.matches([5], obs)
    assert not probe.matches([5, 6, 7], obs)
    assert not probe.matches([5, 0xD0000001, 8], obs)
    assert not probe.matches([5, 0xD0000001, 7, 1], obs)
    assert not probe.matches([5], probe.Obs(failed="x"))
    assert probe.matches([0xffffffff], probe.Obs(o0=0, scratch=((0x0, 0xffffffff),)))
    assert probe.matches([-1], probe.Obs(o0=0, scratch=((0x0, 0xffffffff),)))


def test_expect_dump_list_near():
    # a list element may be a tolerance: {near = x, ulp = n, abs = e} matches a dword whose
    # binary32 value is within the larger of n units in the last place of x and e of x
    one, two = 0x3F800000, 0x40000000
    obs = probe.Obs(o0=0, scratch=((0x0, one + 1), (0x4, two)))
    assert probe.matches([{"near": 1.0, "ulp": 1}, two], obs)
    assert not probe.matches([{"near": 1.0, "ulp": 0}, two], obs)
    assert probe.matches([{"near": 1.0, "abs": 2.0 ** -20}], obs)
    assert not probe.matches([{"near": 1.0, "abs": 2.0 ** -30}], obs)
    assert probe.matches([one + 1, {"near": 2.0, "ulp": 0}], obs)
    # either bound suffices; an infinite or NaN dword is never near
    assert probe.matches([{"near": 1.0, "ulp": 0, "abs": 1e-6}], obs)
    assert not probe.matches([{"near": 1.0, "ulp": 4}],
                             probe.Obs(o0=0, scratch=((0x0, 0x7FFFFFFF),)))
    # the unit in the last place of 0 is that of the smallest normal
    assert probe.matches([{"near": 0.0, "ulp": 1}],
                         probe.Obs(o0=0, scratch=((0x0, 0x00000001),)))
    assert not probe.matches([{"near": 0.0, "ulp": 1}],
                             probe.Obs(o0=0, scratch=((0x0, 0x00000002),)))
    assert not probe.matches([{"near": 1.0, "ulp": 1}], probe.Obs(failed="x"))


def test_expect_o0_near():
    # a table with "near" (and "ulp"/"abs") is a tolerance on o0, for value.s probes
    one = 0x3F800000
    assert probe.matches({"near": 1.0, "ulp": 1}, probe.Obs(o0=one + 1))
    assert probe.matches({"near": 1.0, "ulp": 1}, probe.Obs(o0=one - 1))
    assert not probe.matches({"near": 1.0, "ulp": 1}, probe.Obs(o0=one + 2))
    assert probe.matches({"near": 1.0, "abs": 1e-6}, probe.Obs(o0=one + 2))
    # o0 must be uniform and the job must have run
    assert not probe.matches({"near": 1.0, "ulp": 1}, probe.Obs(mixed=((one, 1024),)))
    assert not probe.matches({"near": 1.0, "ulp": 1}, probe.Obs(failed="x"))


def test_dump_template_stores_its_registers(tmp_path):
    params = {"OP": "nop", "OUT": "r10", **{k: 0 for k in "ABCDEFGH"}}
    p = probe.Probe(name="d", question="q", source="dump.s", params=params,
                    inputs=[], cases=[[]], hypotheses={})
    text = probe.render(p, [], (PROBES / "usse" / "templates" / "dump.s").read_text())
    for i, r in enumerate([*range(10, 18), *range(1, 9)]):
        assert f"stad [r29,+#{i}], r{r}" in text


def test_verdicts():
    p = probe.Probe(name="a", question="q", source="pred.s", params={}, inputs=["A"],
                    cases=[[0], [1]], hypotheses={"h1": [1, 1], "h2": [0, 1]})
    v = probe.verdict(p, [probe.Obs(o0=0), probe.Obs(o0=1)])
    assert v.settled == "h2" and v.consistent == ["h2"]
    v = probe.verdict(p, [probe.Obs(o0=2), probe.Obs(o0=1)])
    assert v.settled is None and v.consistent == []
    q = probe.Probe(name="b", question="q", source="pred.s", params={}, inputs=["A"],
                    cases=[[0]], hypotheses={"h1": [0], "h2": [0]})
    v = probe.verdict(q, [probe.Obs(o0=0)])
    assert v.settled is None and v.consistent == ["h1", "h2"]
    r = probe.Probe(name="c", question="q", source="pred.s", params={}, inputs=["A"],
                    cases=[[0]], hypotheses={})
    v = probe.verdict(r, [probe.Obs(o0=5)])
    assert v.settled is None and "record" in v.text


ROWS = "".join(f"probe p__0: row {y}: " + " ".join(f"{(y << 16) | x:08x}" for x in range(64))
               + "\n" for y in range(32))


def test_parse_pixels():
    # --pixels: every pixel, row by row, kept as a tuple of 2048 values in raster order
    obs = probe.parse("probe p__0: o0 mixed 0x00000000 x1 other x2047\n" + ROWS)
    assert obs["p__0"].pixels == tuple((i // 64) << 16 | i % 64 for i in range(2048))
    assert probe.parse(OUTPUT)["a__0"].pixels is None


def test_expect_pixels():
    px = tuple(range(2048))
    obs = probe.Obs(mixed=((0, 1),), pixels=px)
    assert probe.matches({"pixels": list(px)}, obs)
    assert not probe.matches({"pixels": [0] * 2048}, obs)
    # no pixels printed: never matches
    assert not probe.matches({"pixels": list(px)}, probe.Obs(o0=0))


def test_expect_quad_marks():
    # "quad": coords.s marks, per quad position TL, TR, BL, BR: [k, n] = the pixel holds mark k
    # (0x45000000 + k * 0x06000000 | q << 12) of the pixel q at position n of its own quad
    def mark(k, q):
        return (0x45000000 + k * 0x06000000) | q << 12

    def at(p, n):
        return ((p // 64) & ~1) * 64 + (n // 2) * 64 + ((p % 64) & ~1) + n % 2

    own = tuple(mark(0, p) for p in range(2048))
    assert probe.matches({"quad": [[0, 0], [0, 1], [0, 2], [0, 3]]}, probe.Obs(pixels=own))
    rot = tuple(mark(2, at(p, ((p % 2) + 2 * ((p // 64) % 2) + 1) % 4)) for p in range(2048))
    assert probe.matches({"quad": [[2, 1], [2, 2], [2, 3], [2, 0]]}, probe.Obs(pixels=rot))
    assert not probe.matches({"quad": [[2, 0], [2, 1], [2, 2], [2, 3]]}, probe.Obs(pixels=rot))
    assert not probe.matches({"quad": [[0, 0], [0, 1], [0, 2], [0, 3]]}, probe.Obs(o0=0))
    assert probe.quad_pixels([[0, 0], [0, 1], [0, 2], [0, 3]]) == list(own)


def test_flags_select_the_sgxfive_test_options():
    p = probe.Probe(name="x", question="q", source="pred.s", params={}, inputs=[], cases=[[]],
                    hypotheses={}, coords=True, pixels=True)
    assert probe.tool_args(p) == ["--temps", "32", "--coords", "--pixels"]
    q = probe.Probe(name="y", question="q", source="pred.s", params={}, inputs=[], cases=[[]],
                    hypotheses={}, temps=8)
    assert probe.tool_args(q) == ["--temps", "8"]


ALU = PROBES / "pds" / "alu.toml"


def test_pds_probes_run_their_program_as_the_pds_secondary():
    (p,) = [q for q in probe.load(ALU) if q.name == "pds-alu-readback"]
    assert p.isa == "pds" and probe.pds_data(p, _src(ALU)) == 36
    assert probe.tool_args(p, use="w/sa_dump.bin", src_dir=_src(ALU)) == \
        ["--temps", "32", "--pds", "36", "--use", "w/sa_dump.bin"]


def test_pds_build_writes_the_use_program_too(tmp_path):
    (p,) = [q for q in probe.load(ALU) if q.name == "pds-alu-readback"]
    files = probe.build(p, tmp_path, _src(ALU))
    # 36 data dwords, 16 mov32 into the temporaries, 16 douta, the doutu, halt (and the OP)
    assert all(f.stat().st_size == 4 * (36 + 16 + 1 + 16 + 2) for f in files)
    use = probe.build_use(tmp_path, probe.USE_DUMP, _src(ALU))
    assert use.name == "sa_dump.bin" and use.stat().st_size % 8 == 0


def test_a_pds_probe_may_name_its_use_program(tmp_path):
    t = tmp_path / "t.toml"
    t.write_text('[[probe]]\nname = "u"\nquestion = "q"\nsource = "pds_dump.s"\nisa = "pds"\n'
                 'use = "sa_pixel.s"\npixels = true\nparams = { OP = "nop" }\n'
                 'inputs = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", '
                 '"N", "O", "P"]\ncases = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]\n')
    (p,) = probe.load(t)
    assert p.use == "sa_pixel.s"
    assert probe.tool_args(p, src_dir=_src(ALU))[-4:] == \
        ["--pds", "36", "--use", "sa_pixel.bin"]
    assert probe.build_use(tmp_path, p.use, _src(ALU)).name == "sa_pixel.bin"


PDS_TEMPS = 48     # ds0/ds1[48..63]: the only PDS data registers a program can write


def _pds_written(op: str) -> list:
    """The data registers OP's lines write: (mnemonic, destination) of each ALU op and move."""
    keep = {"movs", "movsa", "tstz", "tstn", "bra", "call", "rtn", "halt", "nop", "alum",
            "store", "rwfence", "load"}
    out = []
    for ln in op.split("\n"):
        ln = ln.split(";")[0].strip()
        ln = ln.split(":", 1)[1].strip() if ":" in ln.split(" ")[0] else ln
        ln = ln[ln.index(")") + 1:].strip() if ln.startswith("(") else ln
        if not ln or ln.split()[0] in keep:
            continue
        if ln.startswith(".word") and "/*ds" not in ln:     # a raw word that writes no register
            continue
        out.append((ln.split()[0], ln.split()[1].rstrip(",")))
    return out


def test_pds_probes_write_only_the_temporaries():
    """Writes to ds0/ds1[0..47] (the constants) are dropped [HW]: every PDS probe's OP
    writes ds[48..63] only, so its results reach the readback."""
    tables = [PROBES / "pds" / "alu.toml", PROBES / "pds" / "moves.toml"]
    probes = [q for t in tables for q in probe.load(t) if q.isa == "pds" and q.host == "fill"]
    assert "pds-alu-constants" in {p.name for p in probes}
    for p in probes:
        if p.name in ("pds-alu-constants", "pds-moves-mov16-constants"):     # on purpose
            continue
        ops = [p.params["OP"]] if "OP" in p.params else [c[0] for c in p.cases]
        for op in ops:
            for mn, r in _pds_written(op):
                n = int(r[r.index("[") + 1:r.index("]")])
                n = n >> 1 if mn == "mov16" else n      # mov16 names a 16-bit half
                assert n >= PDS_TEMPS, (p.name, op, r)


def test_pds_template_copies_its_inputs_to_the_temporaries():
    src = (PROBES / "pds" / "templates" / "pds_dump.s").read_text()
    for k in range(8):
        assert f"mov32 ds0[{48 + k}], ds0[{2 + k}]" in src
        assert f"mov32 ds1[{48 + k}], ds1[{2 + k}]" in src
        assert f"movs douta, ds0[{48 + k}]," in src and f"movs douta, ds1[{48 + k}]," in src


def test_table_flags_load(tmp_path):
    t = tmp_path / "t.toml"
    t.write_text('[[probe]]\nname = "c"\nquestion = "q"\nsource = "pred.s"\n'
                 'coords = true\npixels = true\ncases = [[]]\n')
    (p,) = probe.load(t)
    assert p.coords and p.pixels


def test_target_from_env(monkeypatch):
    monkeypatch.setenv("SGX_TARGET_HOST", "u@h")
    monkeypatch.setenv("SGX_TARGET_SSH_OPTS", "-o HostKeyAlias=x")
    assert probe.target() == ("u@h", ["-o", "HostKeyAlias=x"])


@pytest.mark.skipif(not TOOL.exists(), reason="sgxfive-test not built")
def test_end_to_end_on_the_mock(tmp_path):
    # The mock colours a fill with its program's second instruction's immediate.
    (tmp_path / "imm.s").write_text(f"; {SPDX}\n"
                                    "phas #0, #0, pixel, end, parallel\n"
                                    "mov.skipinv.end o0, #{A}\n")
    p = probe.Probe(name="mock-imm", question="q", source="imm.s", params={}, inputs=["A"],
                    cases=[[3], [0x5CAF0010]], hypotheses={"same": [3, 0x5CAF0010],
                                                         "other": [3, 4]})
    out = probe.run_local([p], [str(TOOL), "--mock"], tmp_path / "work", src_dir=tmp_path)
    obs = probe.parse(out)
    assert obs["mock-imm__0"].o0 == 3
    # the scratch immediate was patched to the scratch page's address + 0x10
    assert obs["mock-imm__1"].o0 != 0x5CAF0010 and obs["mock-imm__1"].o0 & 0xfff == 0x10
    v = probe.verdict(p, [obs["mock-imm__0"], obs["mock-imm__1"]])
    assert v.consistent == []


@pytest.mark.skipif(not TOOL.exists(), reason="sgxfive-test not built")
def test_end_to_end_coords_on_the_mock(tmp_path):
    # --coords --pixels: the mock runs the copy shader itself, so pa0 = (y << 16) | x
    (tmp_path / "cp.s").write_text(f"; {SPDX}\n"
                                   "phas #0, #0, pixel, end, parallel\n"
                                   "mov.skipinv.end o0, pa0\n")
    want = [(i // 64) << 16 | i % 64 for i in range(2048)]
    p = probe.Probe(name="mock-cp", question="q", source="cp.s", params={}, inputs=[],
                    cases=[[]], hypotheses={"coords": [{"pixels": want}]}, coords=True,
                    pixels=True, temps=8)
    out = probe.run_local([p], [str(TOOL), "--mock"], tmp_path / "work", src_dir=tmp_path)
    v = probe.verdict(p, [probe.parse(out)["mock-cp__0"]])
    assert v.settled == "coords", v.text


@pytest.mark.skipif(not TOOL.exists(), reason="sgxfive-test not built")
def test_end_to_end_pds_on_the_mock(tmp_path):
    # The mock colours the fill with its USE program's second immediate (sa_dump's scratch
    # address): the PDS probe gets through the plumbing; its program itself is not run.
    (p,) = [q for q in probe.load(ALU) if q.name == "pds-alu-readback"]
    out = probe.run_local([p], [str(TOOL), "--mock"], tmp_path / "work", src_dir=_src(ALU))
    obs = probe.parse(out)
    assert obs["pds-alu-readback__0"].failed is None, out
    assert obs["pds-alu-readback__0"].o0 is not None, out


def test_each_probe_names_its_table(table):
    tables = {p.name: p.table for p in table}
    assert tables["usse-tests-sign-p-shl"] == "tests.toml"
    assert all(t.endswith(".toml") for t in tables.values())


def test_save_bins_keeps_the_programs_sent(tmp_path):
    work, out = tmp_path / "work", tmp_path / "out"
    work.mkdir()
    (work / "a__0.bin").write_bytes(b"\x01" * 8)
    (work / "a__1.bin").write_bytes(b"\x02" * 8)
    (work / "notes.txt").write_text("x")
    probe.save_bins(work, out)
    assert sorted(f.name for f in (out / "bins").iterdir()) == ["a__0.bin", "a__1.bin"]
    assert (out / "bins" / "a__1.bin").read_bytes() == b"\x02" * 8


def test_table_option_picks_one_table(tmp_path, capsys):
    t = tmp_path / "own.toml"
    t.write_text('[[probe]]\nname = "own-one"\nquestion = "q?"\nsource = "dump.s"\n'
                 'params = { OP = "and r10, r1, r2", OUT = "r10", C = 0, D = 0, E = 0, '
                 'F = 0, G = 0, H = 0 }\ninputs = ["A", "B"]\ncases = [[1, 2]]\n')
    (tmp_path / "templates").mkdir()
    shutil.copy(PROBES / "usse" / "templates" / "dump.s", tmp_path / "templates")
    assert probe.main(["--table", str(t), "list"]) == 0
    out = capsys.readouterr().out
    assert out.startswith("own-one") and len(out.splitlines()) == 1
    assert probe.main(["--table", str(t), "build", str(tmp_path / "b")]) == 0
    assert (tmp_path / "b" / "own-one__0.bin").exists()


def test_low_becomes_the_low_option(tmp_path):
    """A fill probe's low address (the scratch mapped again in the first MiB, for the PDS's
    load and store) runs as --low; it is a fill option only."""
    p = probe.Probe(name="x", question="q", source="pred.s", params={}, inputs=[], cases=[[]],
                    hypotheses={}, low=0x10000)
    assert probe.tool_args(p) == ["--temps", "32", "--low", "0x10000"]
    t = tmp_path / "t.toml"
    base = '[[probe]]\nname = "p"\nquestion = "q"\nsource = "pred.s"\ncases = [[]]\n'
    t.write_text(base + "low = 0x10000\n")
    (q,) = probe.load(t)
    assert q.low == 0x10000
    t.write_text(base + 'low = 0x10000\nhost = "tri"\nslot = "pixel"\n')
    with pytest.raises(probe.ProbeError):
        probe.load(t)


def test_late_becomes_the_late_option(tmp_path):
    """A fill probe's late write (the host writes V to scratch dword K once dword R leaves
    its fill, while the job runs) runs as --late R:K=V; it is a fill option only."""
    p = probe.Probe(name="x", question="q", source="pred.s", params={}, inputs=[], cases=[[]],
                    hypotheses={}, late="128:64=0x12345678")
    assert probe.tool_args(p) == ["--temps", "32", "--late", "128:64=0x12345678"]
    t = tmp_path / "t.toml"
    base = '[[probe]]\nname = "p"\nquestion = "q"\nsource = "pred.s"\ncases = [[]]\n'
    t.write_text(base + 'late = "128:64=0x12345678"\n')
    (q,) = probe.load(t)
    assert q.late == "128:64=0x12345678"
    for bad in ('late = "128:64"\n', 'late = "128:64=0x12345678"\nhost = "tri"\nslot = "pixel"\n'):
        t.write_text(base + bad)
        with pytest.raises(probe.ProbeError):
            probe.load(t)


def test_pokes_become_poke_options(tmp_path):
    """A fill probe's pokes (words of its transfer command) run as --poke options."""
    p = probe.Probe(name="x", question="q", source="pred.s", params={}, inputs=[], cases=[[]],
                    hypotheses={}, pokes=["xfer:17^=0x4", "xfer:33=0x66"])
    assert probe.tool_args(p) == ["--temps", "32", "--poke", "xfer:17^=0x4",
                                  "--poke", "xfer:33=0x66"]
    t = tmp_path / "t.toml"
    t.write_text('[[probe]]\nname = "p"\nquestion = "q"\nsource = "pred.s"\ncases = [[]]\n'
                 'pokes = ["xfer:17^=0x4"]\n')
    (q,) = probe.load(t)
    assert q.pokes == ["xfer:17^=0x4"]
    t.write_text('[[probe]]\nname = "p"\nquestion = "q"\nsource = "pred.s"\ncases = [[]]\n'
                 'pokes = ["cmd:0=1"]\n')
    with pytest.raises(probe.ProbeError):
        probe.load(t)


def test_case_set_runs_each_case_with_its_own_words(tmp_path):
    """A probe whose cases differ in the words they poke (a folded bit scan) runs one process
    per case: its pokes after the probe's, its cmd words over the probe's."""
    t = tmp_path / "t.toml"
    t.write_text('[[probe]]\nname = "p"\nquestion = "q"\nsource = "value.s"\ncases = [[], []]\n'
                 'params = { OP = "mov r4, #0", OUT = "r4", A = 0, B = 0, C = 0, D = 0 }\n'
                 'pokes = ["xfer:17^=0x4"]\n'
                 'case_set = [{ pokes = ["xfer:33=0x40"] }, '
                 '{ pokes = ["xfer:34=0x40", "xfer:35=1"] }]\n')
    (p,) = probe.load(t)
    groups = probe._groups([p])
    assert [(args[2:], [v.first for v in ps]) for args, ps in groups.items()] == [
        (("--poke", "xfer:17^=0x4", "--poke", "xfer:33=0x40"), [0]),
        (("--poke", "xfer:17^=0x4", "--poke", "xfer:34=0x40", "--poke", "xfer:35=1"), [1])]
    names = [f.name for ps in groups.values() for v in ps
             for f in probe.build(v, tmp_path / "b", PROBES / "usse" / "templates")]
    assert names == ["p__0.bin", "p__1.bin"]


def test_case_set_replaces_a_triangle_probes_words_per_case(tmp_path):
    t = tmp_path / "t.toml"
    t.write_text('[[probe]]\nname = "p"\nquestion = "q"\nsource = "pred.s"\nhost = "tri"\n'
                 'slot = "pixel"\ncases = [[], []]\ncmd = { 1 = 5, 2 = 6 }\n'
                 'case_set = [{ cmd = { 1 = 7 } }, { cmd = { 2 = 8 } }]\n')
    (p,) = probe.load(t)
    views = [probe._view(p, i) for i in range(2)]
    assert [v.cmd for v in views] == [{1: 7, 2: 6}, {1: 5, 2: 8}]


@pytest.mark.parametrize("extra", ['case_set = [{}]\n',                        # one per case
                                   'case_set = [{ frob = 1 }, {}]\n',
                                   'case_set = [{ pokes = ["frob"] }, {}]\n',
                                   'case_set = [{ cmd = { 99 = 1 } }, {}]\n'])
def test_case_set_is_checked(tmp_path, extra):
    t = tmp_path / "t.toml"
    t.write_text('[[probe]]\nname = "p"\nquestion = "q"\nsource = "pred.s"\nhost = "tri"\n'
                 'slot = "pixel"\ncases = [[], []]\n' + extra)
    with pytest.raises(probe.ProbeError):
        probe.load(t)
