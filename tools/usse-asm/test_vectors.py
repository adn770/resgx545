# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""vectors.py: probe readbacks (sgxfive-test probe output) into instruction-vector files."""
import json
import pathlib
import sys

import pytest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import probe  # noqa: E402
import vectors  # noqa: E402

PROBES = probe.PROBES

TEMPLATE = """phas #0, #0, pixel, end, parallel
mov.skipinv r1, #{A}
mov.skipinv r10, #0xA0A1A2A3
{OP}
mov.skipinv.end o0, r1
"""

RAW = """programs asm
probe t-add__0: scratch at 0x3e003000 (64 KiB)
probe t-add__0: o0 0x00000002 (2048 of 2048)
programs asm
probe t-add__1: scratch at 0x3e003000 (64 KiB)
probe t-add__1: o0 mixed 0x00000001 x2000 0x00000000 x48
probe t-add__1: scratch +0x004 0x12345678
probe gone__0: scratch at 0x3e003000 (64 KiB)
probe gone__0: o0 0x00000000 (2048 of 2048)
probe t-add__2: scratch at 0x3e003000 (64 KiB)
probe t-add__2: failed: job failed: -5
"""


def table():
    return [probe.Probe(name="t-add", question="add one?", source="t.s",
                        params={"OP": "iadd32 r1, r1, #1"}, inputs=["A"],
                        cases=[[1], [0xffffffff], [7]], hypotheses={}, temps=8)]


def fake_words(p, i, text):
    assert "iadd32 r1, r1, #1" in text            # the rendered case
    return [0x1000 + i, 0x2000]


def convert(raw=RAW, **kw):
    return vectors.convert(raw, table(), templates={"t.s": TEMPLATE}, words_for=fake_words,
                           raw_name="runs/x/raw.txt", **kw)


def test_one_vector_per_case_in_order():
    batch = convert()
    assert batch["format"] == "sgx545-vectors" and batch["version"] == 1
    assert [v["id"] for v in batch["vectors"]] == ["t-add__0", "t-add__1", "t-add__2"]
    assert batch["orphans"] == ["gone__0"]
    assert batch["run"]["raw"] == "runs/x/raw.txt"
    assert len(batch["run"]["raw_sha256"]) == 64


def test_program_and_init():
    v = convert()["vectors"][0]
    assert v["program"] == {"isa": "usse", "entry": 0, "source": "rebuilt",
                            "words": ["0x0000000000001000", "0x0000000000002000"]}
    assert v["init"]["temps"] == 8
    assert v["init"]["pa0"] == "fill"
    assert v["init"]["instances"] == 2048
    assert v["init"]["scratch"] == {"base": "0x3e003000", "bytes": 65536,
                                    "fill": "0xd0000000|i"}
    # the registers the program presets, before the instruction under test
    assert v["init"]["regs"] == {"r1": "0x00000001", "r10": "0xa0a1a2a3"}


def test_a_low_mapping_of_the_scratch_is_recorded():
    """--low: the scratch mapped again in the first MiB (for the PDS's load and store)."""
    raw = RAW.replace("probe t-add__0: scratch at 0x3e003000 (64 KiB)\n",
                      "probe t-add__0: scratch at 0x3e003000 (64 KiB)\n"
                      "probe t-add__0: scratch also at 0x00010000\n")
    vs = convert(raw)["vectors"]
    assert vs[0]["init"]["scratch"]["low"] == "0x00010000"
    assert "low" not in vs[1]["init"]["scratch"]


def test_readbacks():
    vs = convert()["vectors"]
    assert vs[0]["readback"] == {"failed": None, "o0": "0x00000002", "mixed": [],
                                 "scratch": {}, "pixels": None}
    assert vs[1]["readback"]["o0"] is None
    assert vs[1]["readback"]["mixed"] == [["0x00000001", 2000], ["0x00000000", 48]]
    assert vs[1]["readback"]["scratch"] == {"0x004": "0x12345678"}
    assert vs[2]["readback"]["failed"] == "job failed: -5"


def test_provenance():
    p = convert()["vectors"][1]["provenance"]
    assert p["probe"] == "t-add" and p["case"] == 1
    assert p["inputs"] == {"A": "0xffffffff"}
    assert p["params"] == {"OP": "iadd32 r1, r1, #1"}
    assert p["template"] == "t.s" and len(p["template_sha256"]) == 64
    assert p["options"] == ["--temps", "8"]
    assert p["question"] == "add one?"


def test_recorded_words_win(tmp_path):
    (tmp_path / "t-add__0.bin").write_bytes((0xdead).to_bytes(8, "little"))
    batch = convert(bins=tmp_path)
    assert batch["vectors"][0]["program"]["source"] == "recorded"
    assert batch["vectors"][0]["program"]["words"] == ["0x000000000000dead"]
    assert batch["vectors"][1]["program"]["source"] == "rebuilt"


def test_coords_and_pixels_options():
    t = table()
    t[0].coords, t[0].pixels = True, True
    raw = RAW + "probe t-add__0: row 0: " + " ".join(["00000003"] * 64) + "\n"
    batch = vectors.convert(raw, t, templates={"t.s": TEMPLATE}, words_for=fake_words,
                            raw_name="r")
    v = batch["vectors"][0]
    assert v["init"]["pa0"] == "coords"
    assert v["readback"]["pixels"][:2] == ["0x00000003", "0x00000003"]


def test_validate_round_trip(tmp_path):
    path = tmp_path / "x.vec.json"
    vectors.dump(path, convert())
    again = vectors.load(path)
    assert again == json.loads(path.read_text())
    assert again["vectors"][0]["id"] == "t-add__0"


@pytest.mark.parametrize("mutate", [
    lambda b: b.update(version=2),
    lambda b: b.update(format="other"),
    lambda b: b["vectors"][0]["program"].update(isa="arm"),
    lambda b: b["vectors"][0]["program"].update(words=[3]),          # not a hex string
    lambda b: b["vectors"][0]["readback"].update(o0=5),
    lambda b: b["vectors"][0].pop("provenance"),
])
def test_validate_rejects(mutate):
    b = convert()
    mutate(b)
    with pytest.raises(ValueError):
        vectors.validate(b)


def test_converts_a_real_case_with_the_assembler(tmp_path):
    """The default words_for assembles with usse-asm (built by conftest)."""
    t = [p for p in probe.load(PROBES / "usse" / "tests.toml") if p.name == "usse-tests-sign-p-shl"]
    raw = "probe usse-tests-sign-p-shl__1: scratch at 0x3e003000 (64 KiB)\n" \
          "probe usse-tests-sign-p-shl__1: o0 0x00000001 (2048 of 2048)\n"
    batch = vectors.convert(raw, t, raw_name="r")
    v = batch["vectors"][0]
    assert v["program"]["source"] == "rebuilt"
    assert v["provenance"]["table"] == "tests.toml"
    assert len(v["program"]["words"]) > 2
    assert all(len(w) == 18 for w in v["program"]["words"])
    vectors.validate(batch)


def test_converts_a_pds_probe(tmp_path):
    """A PDS probe's vector: the PDS program (32-bit words, its data segment) and the USE
    program its douta results go through, recorded from the run's bins when there."""
    t = [p for p in probe.load(PROBES / "pds" / "alu.toml") if p.name == "pds-alu-readback"]
    raw = "probe pds-alu-readback__0: scratch at 0x3e003000 (64 KiB)\n" \
          "probe pds-alu-readback__0: o0 0x0da7a000 (2048 of 2048)\n" \
          "probe pds-alu-readback__0: scratch +0x000 0x11111111\n"
    v = vectors.convert(raw, t, raw_name="r")["vectors"][0]
    assert v["program"]["isa"] == "pds" and v["program"]["data"] == 36
    assert all(len(w) == 10 for w in v["program"]["words"])
    assert v["init"]["task"] == "pds-secondary" and v["init"]["attrs"] == 16
    use = v["init"]["use"]
    assert use["source"] == "sa_dump.s" and all(len(w) == 18 for w in use["words"])
    assert v["provenance"]["options"][-4:] == ["--pds", "36", "--use", "sa_dump.bin"]
    vectors.validate({"format": vectors.FORMAT, "version": vectors.VERSION, "vectors": [v]})
    # recorded: the bytes sent, PDS and USE
    src = PROBES / "pds" / "templates"
    probe.build(t[0], tmp_path, src)
    probe.build_use(tmp_path, probe.USE_DUMP, src)
    w = vectors.convert(raw, t, raw_name="r", bins=tmp_path)["vectors"][0]
    assert w["program"]["source"] == "recorded" and w["program"]["words"] == v["program"]["words"]
    assert w["init"]["use"]["words"] == use["words"]


def test_pds_attrs_follow_the_run_s_print_up_to_64():
    """A PDS probe's secondary attributes are what its run could show: 16 (sa0-sa15, the
    tool's PROBE_PDS_ATTRS and sa_dump.s) unless the probe prints more scratch dwords
    (--scratch-show N), up to the 64 E1104 read at their own sa."""
    assert vectors.pds_attrs(0) == 16
    assert vectors.pds_attrs(8) == 16
    assert vectors.pds_attrs(32) == 32
    assert vectors.pds_attrs(64) == 64
    with pytest.raises(ValueError):
        vectors.pds_attrs(65)


def test_a_pds_probe_with_scratch_show_64_gets_64_attributes(tmp_path):
    """E1104's form: attribute-room's probe printing all 64 dwords gives a vector with attrs 64,
    so a douta to sa32-sa63 replays instead of stopping at sa16."""
    text = (PROBES / "pds" / "attribute-room.toml").read_text()
    assert "\ntemps = 0x20\n" in text
    (tmp_path / "attribute-room.toml").write_text(
        text.replace("\ntemps = 0x20\n", "\ntemps = 0x20\nscratch_show = 64\n"))
    t = probe.load(tmp_path / "attribute-room.toml")
    raw = "probe pds-attribute-room-rows__3: scratch at 0x3e003000 (64 KiB)\n" \
          "probe pds-attribute-room-rows__3: o0 0x0da7a000 (2048 of 2048)\n" \
          "probe pds-attribute-room-rows__3: scratch +0x0c0 0xa1000030\n"
    v = vectors.convert(raw, t, raw_name="r")["vectors"][0]
    assert v["init"]["attrs"] == 64 and v["init"]["use"]["source"] == "sa64_dump.s"
    assert "--scratch-show" in v["provenance"]["options"]


def test_run_id():
    root = pathlib.Path("/c")
    assert vectors.run_id(pathlib.Path("/c/data/usse/integer/usse-integer-x/raw.txt"), root) == \
        "data_usse_integer_usse-integer-x"


def test_a_run_s_own_table_comes_first(tmp_path):
    """Exploratory runs keep their table next to the run directory (q3.toml for
    q3/raw.txt); its probes win over the repo tables, its templates are found next to
    it or among the tables'."""
    (tmp_path / "q3").mkdir()
    (tmp_path / "own.s").write_text(TEMPLATE)
    (tmp_path / "q3.toml").write_text(
        '[[probe]]\nname = "x-own"\nquestion = "q"\nsource = "own.s"\n'
        'params = { OP = "iadd32 r1, r1, #1" }\ninputs = ["A"]\ncases = [[2]]\n'
        '[[probe]]\nname = "x-repo"\nquestion = "q"\nsource = "dump.s"\n'
        'params = {}\ninputs = []\ncases = [[]]\n')
    tbl, dirs = vectors.tables_for(tmp_path / "q3" / "raw.txt", table())
    assert [p.name for p in tbl][:2] == ["x-own", "x-repo"]
    assert tbl[0].table == "q3.toml"
    assert dirs == [tmp_path, *vectors.template_dirs()]
    assert vectors.template_text(tbl[0], dirs) == TEMPLATE
    assert vectors.template_text(tbl[1], dirs).startswith("; SPDX")
    # a run without its own table: the repo tables only
    t2, d2 = vectors.tables_for(tmp_path / "other" / "raw.txt", table())
    assert [p.name for p in t2] == ["t-add"] and d2 == vectors.template_dirs()


def test_a_campaign_run_finds_its_table_and_templates(tmp_path):
    """A run of probes/<unit>/<feature>.toml under DATA/<unit>/<feature>/<probe>/ finds its
    table and the templates beside it, with no copy beside the run."""
    probes = tmp_path / "probes"
    (probes / "usse" / "templates").mkdir(parents=True)
    (probes / "usse" / "x.toml").write_text(
        '[[probe]]\nname = "usse-x-expl"\nquestion = "q"\nsource = "dump.s"\n'
        'params = {}\ninputs = []\ncases = [[]]\n')
    tbl, dirs = vectors.tables_for(tmp_path / "data/usse/x/usse-x-expl/raw.txt", table(), probes)
    assert [p.name for p in tbl] == ["usse-x-expl", "t-add"]
    assert tbl[0].table == "x.toml"
    assert dirs[0] == probes / "usse" / "templates"
    # another feature's runs do not see it
    tbl, _ = vectors.tables_for(tmp_path / "data/usse/y/usse-y-z/raw.txt", table(), probes)
    assert [p.name for p in tbl] == ["t-add"]


def test_converts_a_pds_probe_whose_table_sits_beside_the_run(tmp_path):
    """An exploration run's own table (<run>.toml) is looked up first, but the PDS template
    it names is still the repo's: the data size comes from the template found."""
    t = [p for p in probe.load(PROBES / "pds" / "alu.toml") if p.name == "pds-alu-readback"]
    raw = "probe pds-alu-readback__0: o0 0x0da7a000 (2048 of 2048)\n"
    v = vectors.convert(raw, t, raw_name="r", dirs=[tmp_path, *vectors.template_dirs()])["vectors"][0]
    assert v["program"]["data"] == 36


# ---- the job a fill ran in: its transfer command's pokes and the USE coefficients (11.7) ----

def filter_table():
    """A fill probe that loads the filter block (xfer:17 bit 2) with mode 3, each case its own
    first coefficient word (case_set), as probes/usse/filter-taps.toml does."""
    d = {"name": "t-firh", "question": "q", "source": "t.s", "params": {"OP": "nop"},
         "inputs": ["A"], "cases": [[1], [2]], "pokes": ["xfer:17^=0x4", "xfer:32=0x3"],
         "case_set": [{"pokes": ["xfer:33=0x4"]}, {"pokes": ["xfer:33=0x8", "xfer:41=0x10"]}]}
    return [probe._probe(d, "t.toml")]


FILTER_RAW = """probe t-firh__0: scratch at 0x3e003000 (64 KiB)
probe t-firh__0: pokes xfer:17^=0x4 xfer:32=0x3 xfer:33=0x4
probe t-firh__0: o0 0x00000002 (2048 of 2048)
probe t-firh__1: scratch at 0x3e003000 (64 KiB)
probe t-firh__1: pokes xfer:17^=0x4 xfer:32=0x3 xfer:33=0x8 xfer:41=0x10
probe t-firh__1: o0 0x00000003 (2048 of 2048)
"""


def test_use_coeffs_follow_the_transfer_words():
    """The transfer command starts zeroed (sgxfive_transfer_cmd); the firmware loads the filter
    block only with load_flags bit 2 (transfer.md 3.2), then 0x0a9c from word 32 and the
    three groups from words 33-41."""
    assert vectors.use_coeffs([]) == {"load": False}
    got = vectors.use_coeffs(["xfer:17^=0x4", "xfer:32=0x3", "xfer:33=0x4", "xfer:41=16"])
    assert got == {"load": True, "mode": "0x00000003",
                   "words": ["0x00000004"] + ["0x00000000"] * 7 + ["0x00000010"]}
    # a flip twice is no load; other words do not matter
    assert vectors.use_coeffs(["xfer:17^=0x4", "xfer:17^=0x4", "bg:3=1"]) == {"load": False}


def test_a_case_set_s_pokes_reach_the_options_and_the_job():
    """The options are the case's own (the probe's pokes, then its case_set's): the first
    conversion recorded the probe's only, so a case's coefficient words were lost."""
    batch = vectors.convert(FILTER_RAW, filter_table(), templates={"t.s": TEMPLATE},
                            words_for=lambda p, i, t: [0], raw_name="r")
    v0, v1 = batch["vectors"]
    assert v0["provenance"]["options"] == ["--temps", "32", "--poke", "xfer:17^=0x4",
                                           "--poke", "xfer:32=0x3", "--poke", "xfer:33=0x4"]
    assert v1["init"]["job"]["pokes"] == ["xfer:17^=0x4", "xfer:32=0x3", "xfer:33=0x8",
                                          "xfer:41=0x10"]
    assert v1["init"]["job"]["use_coeffs"]["words"][0] == "0x00000008"
    assert v1["init"]["job"]["use_coeffs"]["words"][8] == "0x00000010"


def test_a_fill_without_pokes_loads_no_coefficients():
    v = convert()["vectors"][0]
    assert v["init"]["job"] == {"pokes": [], "use_coeffs": {"load": False}}


def test_a_case_whose_run_printed_no_pokes_carries_no_job():
    """As jobs(): a case whose table has pokes but whose run printed none ran with pokes not
    known, so its vector carries no job (not the table's pokes)."""
    no_lines = "\n".join(x for x in FILTER_RAW.splitlines() if ": pokes" not in x) + "\n"
    batch = vectors.convert(no_lines, filter_table(), templates={"t.s": TEMPLATE},
                            words_for=lambda p, i, t: [0], raw_name="r")
    assert [("job" in v["init"]) for v in batch["vectors"]] == [False, False]
    assert vectors.jobs(no_lines, filter_table()) == {}


def test_jobs_come_from_the_run_s_pokes_lines():
    """jobs(): the job of each case as the run printed it; a case whose table has pokes but
    whose run printed none is left out (not known)."""
    j = vectors.jobs(FILTER_RAW, filter_table())
    assert j["t-firh__1"]["use_coeffs"]["mode"] == "0x00000003"
    assert j["t-firh__0"]["pokes"] == ["xfer:17^=0x4", "xfer:32=0x3", "xfer:33=0x4"]
    no_lines = "\n".join(x for x in FILTER_RAW.splitlines() if ": pokes" not in x) + "\n"
    assert vectors.jobs(no_lines, filter_table()) == {}
    # a probe without pokes: none printed, none needed
    assert vectors.jobs(RAW, table())["t-add__0"] == {"pokes": [], "use_coeffs": {"load": False}}
    # the run's line wins over the table (what ran)
    other = FILTER_RAW.replace("xfer:33=0x4\n", "xfer:33=0x5\n")
    assert vectors.jobs(other, filter_table())["t-firh__0"]["pokes"][-1] == "xfer:33=0x5"


def test_the_jobs_command_writes_a_sidecar(tmp_path):
    """jobs VEC...: the jobs of existing vector files, beside them under the data repository's
    vectors/jobs/ (the vector files themselves stay as converted)."""
    data = tmp_path / "data"
    run = data / "usse" / "t" / "t-firh"
    run.mkdir(parents=True)
    (run / "raw.txt").write_text(FILTER_RAW)
    vec = data / "vectors" / "usse" / "t" / "t-firh.vec.json"
    vec.parent.mkdir(parents=True)
    vec.write_text(json.dumps({"format": "sgx545-vectors", "version": 1,
                               "run": {"raw": "usse/t/t-firh/raw.txt"}, "vectors": []}))
    out = vectors.write_jobs(vec, data, filter_table())
    assert out == data / "vectors" / "jobs" / "usse" / "t" / "t-firh.job.json"
    side = json.loads(out.read_text())
    assert side["format"] == "sgx545-vector-jobs" and "vectors" not in side
    assert side["run"]["raw"] == "usse/t/t-firh/raw.txt"
    assert sorted(side["jobs"]) == ["t-firh__0", "t-firh__1"]
