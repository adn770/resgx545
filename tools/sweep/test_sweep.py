# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The sweep runner: tables, case generation, classification, raw.txt and resuming, the
stop on driver errors, the report and its kernel annotations (kernel_masks.toml), a mock
end-to-end run of a tiny table, the tables of the first round, and regtimeline against a
file standing in for /dev/mem."""
from __future__ import annotations

import collections
import pathlib
import re
import shutil
import struct
import subprocess
import textwrap

import pytest

import sweep

HERE = pathlib.Path(__file__).resolve().parent
TOOL = sweep.DEFAULT_TOOL

SIZES = {"xfer": 42, "bg": 17, "pds:prim": 4, "cmd": 26}


def size_of(host, space):
    return SIZES[space]


def table(tmp_path, text: str) -> sweep.Sweep:
    p = tmp_path / "t.toml"
    p.write_text(textwrap.dedent(text))
    return sweep.load(p)


# ---- tables and cases --------------------------------------------------------------------

def test_load_defaults(tmp_path):
    s = table(tmp_path, """
        name = "t"
        about = "a test"
        host = "fill"
        [[range]]
        space = "xfer"
    """)
    assert s.name == "t" and s.host == "fill" and s.options == []
    assert s.bits == list(range(32))
    assert s.values == ["=0", "=0xffffffff"]
    assert s.repeat == 1
    assert s.ranges == [sweep.Range("xfer", None, None)]


def test_load_all_of_a_table_with_one_sweep_and_other_parts(tmp_path):
    # the fields a table of several kinds adds are not the sweep's, and are not errors
    p = tmp_path / "t.toml"
    p.write_text(textwrap.dedent("""
        needs = ["render"]
        open = ["unit-t-x"]
        name = "unit-t"
        host = "fill"
        [[range]]
        space = "xfer"
        [[probe]]
        name = "unit-t-x"
    """))
    (s,) = sweep.load_all(p)
    assert s.name == "unit-t" and s.ranges == [sweep.Range("xfer", None, None)]
    assert sweep.load(p).name == "unit-t"


def test_load_all_of_a_table_with_several_sweeps(tmp_path):
    p = tmp_path / "t.toml"
    p.write_text(textwrap.dedent("""
        name = "unit-t"
        [[sweep]]
        name = "unit-t-copy"
        host = "copy"
        options = ["--every-value"]
        [[sweep.range]]
        space = "xfer"
        [[sweep]]
        name = "unit-t-fill"
        host = "fill"
        [[sweep.range]]
        space = "bg"
        indices = [1, 2]
    """))
    a, b = sweep.load_all(p)
    assert (a.name, a.host, a.options) == ("unit-t-copy", "copy", ["--every-value"])
    assert (b.name, b.ranges) == ("unit-t-fill", [sweep.Range("bg", 1, 2)])


@pytest.mark.parametrize("text", [
    'name = "t"\n[[range]]\nspace = "xfer"\n[[sweep]]\nname = "a"\nhost = "fill"',
    'name = "t"\n[[sweep]]\nhost = "fill"\n[[sweep.range]]\nspace = "xfer"',
    'name = "t"\n[[sweep]]\nname = "a"\nhost = "fill"\n[[sweep.range]]\nspace = "xfer"\n'
    '[[sweep]]\nname = "a"\nhost = "fill"\n[[sweep.range]]\nspace = "xfer"',
    'name = "t"\n[[sweep]]\nname = "a"\nhost = "fill"\nneeds = ["x"]\n'
    '[[sweep.range]]\nspace = "xfer"',
])
def test_load_all_rejects(tmp_path, text):
    p = tmp_path / "t.toml"
    p.write_text(text)
    with pytest.raises(sweep.SweepError):
        sweep.load_all(p)


def test_load_all_of_a_table_without_sweeps(tmp_path):
    p = tmp_path / "t.toml"
    p.write_text('name = "t"\n[[probe]]\nname = "t-x"\n')
    assert sweep.load_all(p) == []


@pytest.mark.parametrize("bad", [
    'host = "frob"\n[[range]]\nspace = "xfer"',
    'host = "fill"\n[[range]]\nspace = "frob"',
    'host = "fill"\n[[range]]\nspace = "xfer"\nindices = [3, 1]',
    'host = "fill"\nbits = [32]\n[[range]]\nspace = "xfer"',
    'host = "fill"\nvalues = ["0"]\n[[range]]\nspace = "xfer"',
    'host = "fill"\nrepeat = 0\n[[range]]\nspace = "xfer"',
    'host = "fill"\nfrob = 1\n[[range]]\nspace = "xfer"',
    'host = "fill"',                                  # nothing to sweep, no pb list
])
def test_load_rejects(tmp_path, bad):
    with pytest.raises(sweep.SweepError):
        table(tmp_path, 'name = "t"\nabout = "x"\n' + bad)


def test_cases_baseline_first_then_every_bit_and_value(tmp_path):
    s = table(tmp_path, """
        name = "t"
        about = "x"
        host = "fill"
        bits = [0, 31]
        [[range]]
        space = "xfer"
        indices = [3, 4]
    """)
    cs = sweep.cases(s, size_of)
    assert [c.id for c in cs] == [
        "baseline",
        "xfer:3^=0x1", "xfer:3^=0x80000000", "xfer:3=0", "xfer:3=0xffffffff",
        "xfer:4^=0x1", "xfer:4^=0x80000000", "xfer:4=0", "xfer:4=0xffffffff",
    ]
    assert cs[0].pokes == [] and cs[1].pokes == ["xfer:3^=0x1"]


def test_cases_whole_space_by_default(tmp_path):
    s = table(tmp_path, """
        name = "t"
        about = "x"
        host = "fill"
        [[range]]
        space = "xfer"
        [[range]]
        space = "pds:prim"
    """)
    cs = sweep.cases(s, size_of)
    assert len(cs) == 1 + (42 + 4) * 34
    assert cs[-1].id == "pds:prim:3=0xffffffff"


def test_cases_repeat(tmp_path):
    s = table(tmp_path, """
        name = "t"
        about = "x"
        host = "tri"
        bits = [5]
        values = []
        repeat = 2
        [[range]]
        space = "cmd"
        indices = [0, 0]
    """)
    assert [c.id for c in sweep.cases(s, size_of)] == [
        "baseline", "baseline#1", "cmd:0^=0x20", "cmd:0^=0x20#1"]


def test_cases_pb_pages(tmp_path):
    s = table(tmp_path, """
        name = "t"
        about = "x"
        host = "tri"
        options = ["--width", "1024", "--height", "768"]
        pb_pages = [0x23, 0x422]
    """)
    cs = sweep.cases(s, size_of)
    assert [(c.id, c.pb) for c in cs] == [("pb=0x23:baseline", 0x23),
                                          ("pb=0x422:baseline", 0x422)]


def test_tool_args(tmp_path):
    s = table(tmp_path, """
        name = "t"
        about = "x"
        host = "copy"
        options = ["--width", "16"]
        mock_options = ["--mock=rev1"]
        bits = [0]
        values = []
        [[range]]
        space = "tex"
        indices = [2, 2]
    """)
    c = sweep.cases(s, lambda h, sp: 4)[1]
    assert sweep.tool_args(s, c) == ["copy", "--width", "16", "--poke", "tex:2^=0x1"]
    assert sweep.local_argv(s, c, "T", mock=True) == [
        "T", "--mock", "--mock=rev1", "copy", "--width", "16", "--poke", "tex:2^=0x1"]
    assert sweep.local_argv(s, c, "T", mock=False) == [
        "T", "copy", "--width", "16", "--poke", "tex:2^=0x1"]
    pb = sweep.Case("pb=0x30:baseline", [], 0x30)
    assert sweep.local_argv(s, pb, "T", mock=True)[:4] == [
        "T", "--mock", "--mock=rev1", "--mock-pb-pages=0x30"]


# ---- classification ----------------------------------------------------------------------

def out(job="ok", h="0x00000000000000aa", diff=0, outside=0, first=""):
    return (f"job: {job}\ntarget: 64x32 hash {h}\ndiff: {diff} of 2048 pixels{first}\n"
            f"outside: {outside} dwords\n")


BASE = sweep.parse_result(out())


@pytest.mark.parametrize("rc,stdout,cls,detail", [
    (0, out(), "unchanged", ""),
    (1, out(h="0x00000000000000bb", diff=12,
            first=", first (1, 0) 0x0 expected 0x1"), "changed", "12 pixels"),
    (1, out(h="0x00000000000000bb", diff=0), "changed", "0 pixels"),
    (1, out(outside=3), "outside", "3 dwords"),
    (1, out(h="0x00000000000000bb", diff=5, outside=3), "changed", "5 pixels, 3 outside"),
    (1, out() + "scratch page 2: 5 changed, first +0x0 0x00000001\n"
     "scratch page 4: 1 changed, first +0x8 0x00000002\nscratch: 6 dwords changed\n",
     "scratch", "pages 2, 4 (6 dwords)"),
    (1, out(h="0x00000000000000bb", diff=5) + "scratch page 2: 5 changed, first +0x0 0x1\n"
     "scratch: 5 dwords changed\n", "changed", "5 pixels, scratch pages 2 (5 dwords)"),
    (1, out() + "scratch: 0 dwords changed\n", "unchanged", ""),
    (1, out(job="failed: job faulted, context lost (Input/output error)"), "fault", ""),
    (1, out(job="failed: job hung, context lost (Connection timed out)"), "hang", ""),
    (1, out(job="failed: job cancelled, context lost (Operation canceled)"),
     "cancelled", ""),
    (1, out(job="failed: scene overflowed the parameter buffer, context kept "
                "(No space left on device)"), "overflow", ""),
    (1, out(job="rejected (Invalid argument)"), "rejected", "Invalid argument"),
    (1, out(job="failed: Timer expired"), "error", "failed: Timer expired"),
    (2, "", "usage", ""),
    (1, "", "error", "rc 1, no job line"),
    (255, "", "error", "rc 255, no job line"),
    (-9, out(), "error", "rc -9"),
])
def test_classify(rc, stdout, cls, detail):
    r = sweep.classify(rc, stdout, BASE)
    assert (r.cls, r.detail) == (cls, detail)


# ---- raw.txt, running, resuming ----------------------------------------------------------

class FakeExec:
    """Runs cases from a script: {case id: (rc, stdout)}, default ok; records the calls."""

    def __init__(self, script=None, default=(0, out())):
        self.script, self.default, self.calls = script or {}, default, []

    def __call__(self, s, case):
        self.calls.append(case.id)
        rc, so = self.script.get(case.id, self.default)
        return sweep.Record(case.id, "tool " + " ".join(sweep.tool_args(s, case)), rc, so,
                            "", 0.01)


def small(tmp_path):
    return table(tmp_path, """
        name = "small"
        about = "x"
        host = "fill"
        bits = [0, 1]
        values = ["=0"]
        [[range]]
        space = "xfer"
        indices = [0, 1]
    """)


def test_raw_round_trip():
    recs = [sweep.Record("baseline", "tool fill", 0, out(), "", 0.25),
            sweep.Record("xfer:0^=0x1", "tool fill --poke xfer:0^=0x1", 1,
                         out(h="0x00000000000000bb", diff=3), "sgxfive-test: x\n", 0.5)]
    text = "".join(sweep.format_record(r) for r in recs)
    assert sweep.parse_raw(text) == {r.id: r for r in recs}


def test_raw_ignores_an_unfinished_case():
    text = sweep.format_record(sweep.Record("baseline", "c", 0, out(), "", 0.1))
    text += "=== case xfer:0^=0x1\n$ c\njob: ok\n"
    assert list(sweep.parse_raw(text)) == ["baseline"]


def test_run_writes_raw_and_report(tmp_path):
    s = small(tmp_path)
    ex = FakeExec({"xfer:0^=0x2": (1, out(h="0x00000000000000cc", diff=7)),
                   "xfer:1=0": (1, out(job="failed: job faulted, context lost (x)"))})
    d = tmp_path / "o"
    res = sweep.run(s, ex, d, size_of)
    assert res.done == 7 and res.stopped is None
    raw = sweep.parse_raw((d / "raw.txt").read_text())
    assert list(raw) == [c.id for c in sweep.cases(s, size_of)]
    rep = (d / "report.txt").read_text()
    assert "unchanged 4" in rep and "changed 1" in rep and "fault 1" in rep
    assert "xfer:0" in rep and "^=0x2 changed (7 pixels)" in rep
    assert "=0 fault" in rep


def test_run_resumes(tmp_path):
    s = small(tmp_path)
    d = tmp_path / "o"
    sweep.run(s, FakeExec(), d, size_of, limit=3)
    ex = FakeExec()
    res = sweep.run(s, ex, d, size_of)
    assert ex.calls == [c.id for c in sweep.cases(s, size_of)][3:]
    assert res.done == 7
    assert len(sweep.parse_raw((d / "raw.txt").read_text())) == 7


def test_run_stops_after_consecutive_errors(tmp_path):
    s = small(tmp_path)
    err = (255, "")
    ex = FakeExec({"xfer:0^=0x1": err, "xfer:0^=0x2": err, "xfer:0=0": err,
                   "xfer:1^=0x1": (0, out()), "xfer:1^=0x2": err, "xfer:1=0": err})
    res = sweep.run(s, ex, tmp_path / "o", size_of, max_errors=3)
    assert res.stopped and "3 errors in a row" in res.stopped
    assert ex.calls == ["baseline", "xfer:0^=0x1", "xfer:0^=0x2", "xfer:0=0"]
    # job errors do not count
    ex = FakeExec(default=(1, out(job="failed: job hung, context lost (x)")))
    ex.script["baseline"] = (0, out())
    res = sweep.run(s, ex, tmp_path / "o2", size_of, max_errors=3)
    assert res.stopped is None and res.done == 7


def test_run_needs_a_good_baseline(tmp_path):
    s = small(tmp_path)
    ex = FakeExec({"baseline": (1, out(job="failed: job faulted, context lost (x)"))})
    with pytest.raises(sweep.SweepError, match="baseline"):
        sweep.run(s, ex, tmp_path / "o", size_of)


def test_pb_sweep_takes_its_first_size_as_the_reference(tmp_path):
    # A sweep of PB sizes alone has no poke: an overflowing first size is a result too.
    s = table(tmp_path, """
        name = "t"
        about = "x"
        host = "tri"
        pb_pages = [0x23, 0x422]
    """)
    ex = FakeExec({"pb=0x23:baseline": (1, out(job="failed: scene overflowed the parameter "
                                                   "buffer, context kept (x)"))})
    setups = []
    ex.setup = lambda s, pb: setups.append(pb)
    res = sweep.run(s, ex, tmp_path / "o", size_of)
    assert res.done == 2 and setups == [0x23, 0x422, 0x422]
    rep = (tmp_path / "o" / "report.txt").read_text()
    assert "baseline: ('failed: scene overflowed" in rep
    assert "pb=0x422:baseline: all unchanged" in rep


def test_report_marks_unstable_repeats(tmp_path):
    s = table(tmp_path, """
        name = "t"
        about = "x"
        host = "fill"
        bits = [0]
        values = []
        repeat = 2
        [[range]]
        space = "xfer"
        indices = [0, 0]
    """)
    ex = FakeExec({"xfer:0^=0x1#1": (1, out(job="failed: job hung, context lost (x)"))})
    sweep.run(s, ex, tmp_path / "o", size_of)
    assert "^=0x1 unchanged/hang" in (tmp_path / "o" / "report.txt").read_text()


# ---- what the kernel does with each word (kernel_masks.toml) ----------------------------

VALIDATED = ["xfer:4", "xfer:6", "xfer:9", "xfer:15", "xfer:16", "xfer:17",
             "cmd:0", "cmd:2", "cmd:3", "cmd:4", "cmd:5", "cmd:9", "cmd:15", "cmd:18"]


def test_kernel_masks_cover_both_commands():
    m = sweep.load_masks()
    assert set(m) == {f"xfer:{i}" for i in range(42)} | {f"cmd:{i}" for i in range(26)}
    assert collections.Counter(w.action for w in m.values()) == {"pass": 54, "validate": 14}
    assert [k for k, w in m.items() if w.action == "validate"] == VALIDATED
    assert m["xfer:17"].lands == ["tq:98", "tq:99", "tq:100"] and m["xfer:17"].mask == 7
    assert m["xfer:16"].lands == ["tq:16"] and m["xfer:18"].lands == ["tq:17"]
    assert m["xfer:41"].lands == ["tq:40"]
    assert m["cmd:0"].lands == ["ta:148"] and m["cmd:9"].lands == ["ta:154"]
    assert m["cmd:11"].lands == ["rd:2"] and m["cmd:22"].lands == ["rd:51"]
    assert [m[f"cmd:{i}"].lands for i in (23, 24, 25)] == [["ta:2"], ["ta:3"], ["ta:4"]]
    lands = [x for w in m.values() for x in w.lands]
    assert len(lands) == len(set(lands))        # no two words land on the same word
    assert all(re.fullmatch(r"[a-z_]+\.c:\d+", w.ref) for w in m.values())


@pytest.mark.parametrize("bad", [
    'word = "xfer:0"\naction = "frob"\nlands = ["tq:0"]\nref = "a.c:1"',
    'word = "xfer:0"\naction = "mask"\nlands = ["tq:0"]\nref = "a.c:1"',   # no mask
    'word = "xfer:0"\naction = "pass"\nlands = ["zz:0"]\nref = "a.c:1"',
    'word = "frob:0"\naction = "pass"\nlands = ["tq:0"]\nref = "a.c:1"',
    'word = "xfer:0"\naction = "pass"\nlands = ["tq:0"]\nref = "a.c"',
    'word = "xfer:0"\naction = "pass"\nlands = ["tq:0"]\nref = "a.c:1"\nfrob = 1',
    'word = "xfer:0"\naction = "pass"\nlands = ["tq:0"]\nref = "a.c:1"\n'
    '[[word]]\nword = "xfer:0"\naction = "pass"\nlands = ["tq:1"]\nref = "a.c:1"',
])
def test_load_masks_rejects(tmp_path, bad):
    p = tmp_path / "m.toml"
    p.write_text('fork = "x"\n[[word]]\n' + bad + "\n")
    with pytest.raises(sweep.SweepError):
        sweep.load_masks(p)


@pytest.mark.parametrize("action,mask,op,cls,want", [
    ("pass", None, "^=0x1", "changed", None),
    ("pass", None, "^=0x1", "rejected", None),
    ("validate", None, "^=0x1", "rejected", "never reached the GPU"),
    ("validate", None, "^=0x1", "unchanged", "reached"),
    ("validate", None, "=0", "hang", "reached"),
    ("validate", None, "^=0x1", "error", None),
    ("validate", None, "^=0x1", "usage", None),
    ("override", None, "^=0x1", "unchanged", "never reached the GPU"),
    ("mask", 0xff, "^=0x100", "unchanged", "never reached the GPU"),
    ("mask", 0xff, "^=0x101", "changed", "reached"),
    ("mask", 0xff, "=0", "unchanged", "reached, bits 0xff only"),
    ("mask", 0xff, "^=0x1", "rejected", "never reached the GPU"),
])
def test_reach(action, mask, op, cls, want):
    w = sweep.Mask(action, ["tq:0"], "a.c:1", mask=mask)
    assert sweep.reach(w, op, cls) == want
    assert sweep.reach(None, op, cls) is None


def test_report_annotates_kernel_checked_words(tmp_path):
    s = small(tmp_path)
    masks = {"xfer:0": sweep.Mask("validate", ["tq:0"], "c.c:9", note="zero"),
             "xfer:1": sweep.Mask("pass", ["tq:1"], "c.c:1")}
    rej = (1, out(job="rejected (Invalid argument)"))
    ex = FakeExec({"xfer:0^=0x1": rej, "xfer:0^=0x2": (1, out(h="0x00000000000000cc", diff=7)),
                   "xfer:1^=0x1": rej})
    d = tmp_path / "o"
    sweep.run(s, ex, d, size_of, masks=masks)
    lines = {ln.split(":")[0] + ":" + ln.split(":")[1]: ln
             for ln in (d / "report.txt").read_text().splitlines() if ln.startswith("xfer:")}
    w0, w1 = lines["xfer:0"], lines["xfer:1"]
    assert "^=0x1 rejected (Invalid argument) [never reached the GPU]" in w0
    assert "^=0x2 changed (7 pixels) [reached]" in w0
    assert w0.endswith("[kernel: validate (zero), lands tq:0, c.c:9; "
                       "reached the GPU in 2 of 3]")
    assert w1 == "xfer:1: ^=0x1 rejected (Invalid argument)"     # pass: no annotation
    # the default is the kernel's own list: xfer:1 is passed on unchanged
    assert sweep.report(s, sweep.cases(s, size_of),
                        sweep.parse_raw((d / "raw.txt").read_text())).count("[kernel:") == 0


def test_report_annotates_masked_and_overridden_words(tmp_path):
    s = table(tmp_path, """
        name = "t"
        about = "x"
        host = "fill"
        bits = [0, 8]
        values = []
        [[range]]
        space = "xfer"
        indices = [0, 1]
    """)
    masks = {"xfer:0": sweep.Mask("mask", ["tq:0"], "c.c:2", mask=0xff),
             "xfer:1": sweep.Mask("override", ["tq:1"], "c.c:3")}
    d = tmp_path / "o"
    sweep.run(s, FakeExec(), d, size_of, masks=masks)
    rep = (d / "report.txt").read_text()
    assert ("xfer:0: all unchanged [kernel: mask 0xff, lands tq:0, c.c:2; "
            "reached the GPU in 1 of 2]") in rep
    assert ("xfer:1: all unchanged [kernel: override, lands tq:1, c.c:3; "
            "reached the GPU in 0 of 2]") in rep


# ---- against the mock --------------------------------------------------------------------

@pytest.fixture(scope="module")
def tool():
    if not TOOL.exists():
        pytest.skip(f"{TOOL} not built (make -C userspace/libsgxfive)")
    return TOOL


def test_tool_sizes(tool):
    assert sweep.tool_size_of(tool)("fill", "xfer") == 42
    assert sweep.tool_size_of(tool)("copy", "tex") == 4
    assert sweep.tool_size_of(tool)("tri", "pds:pixev") == 20
    with pytest.raises(sweep.SweepError):
        sweep.tool_size_of(tool)("fill", "cmd")


def test_mock_end_to_end(tool, tmp_path):
    s = table(tmp_path, """
        name = "tiny"
        about = "x"
        host = "fill"
        bits = [0]
        [[range]]
        space = "xfer"
        indices = [12, 13]
    """)
    d = tmp_path / "o"
    res = sweep.run(s, sweep.LocalExec(tool, mock=True), d, sweep.tool_size_of(tool))
    assert res.done == 7 and res.stopped is None
    raw = sweep.parse_raw((d / "raw.txt").read_text())
    assert raw["baseline"].rc == 0 and "job: ok" in raw["baseline"].out
    rep = (d / "report.txt").read_text()
    # xfer:13 = 0: the mock clips to the first tile
    assert "=0 changed (1536 pixels)" in rep
    assert sweep.main(["report", str(d), "--table", str(tmp_path / "t.toml")]) == 0


# ---- regtimeline -------------------------------------------------------------------------

@pytest.fixture(scope="module")
def regtimeline(tmp_path_factory):
    cc = shutil.which("cc")
    if not cc:
        pytest.skip("no cc")
    exe = tmp_path_factory.mktemp("rt") / "regtimeline"
    subprocess.run([cc, "-O2", "-Wall", "-Werror", "-o", str(exe), str(HERE / "regtimeline.c")],
                   check=True)
    return exe


def test_regtimeline_samples_a_file(regtimeline, tmp_path):
    mem = tmp_path / "mem"
    mem.write_bytes(b"".join(struct.pack("<I", 0x1000 + i) for i in range(0x1000)))
    r = subprocess.run([str(regtimeline), "0.05", "0.01", "0x10-0x18,0x740", "--", "echo", "hi"],
                       capture_output=True, text=True, timeout=10,
                       env={"REGTIMELINE_MEM": str(mem), "REGTIMELINE_BASE": "0",
                            "PATH": "/usr/bin:/bin"})
    assert r.returncode == 0, r.stderr
    lines = r.stdout.splitlines()
    assert lines[0] == "hi"
    head = [ln for ln in lines if ln.startswith("timeline: ")]
    assert len(head) == 1 and "regs 0x0010 0x0014 0x0018 0x0740" in head[0]
    assert " rc 0" in head[0]
    tl = [ln.split() for ln in lines if ln.startswith("tl ")]
    assert len(tl) == 1        # the file does not change: one sample line
    assert tl[0][2:] == ["00001004", "00001005", "00001006", "000011d0"]


def test_regtimeline_exits_with_the_commands_status(regtimeline, tmp_path):
    """A wrapped command keeps its exit status (the probe and sweep runs depend on it)."""
    mem = tmp_path / "mem"
    mem.write_bytes(bytes(0x1000))
    r = subprocess.run([str(regtimeline), "0", "0", "0x10", "--", "sh", "-c", "exit 3"],
                       capture_output=True, text=True, timeout=10,
                       env={"REGTIMELINE_MEM": str(mem), "REGTIMELINE_BASE": "0",
                            "PATH": "/usr/bin:/bin"})
    assert r.returncode == 3, r.stderr
    assert " rc 3" in r.stdout


def test_regtimeline_total_0_samples_until_the_command_exits(regtimeline, tmp_path):
    mem = tmp_path / "mem"
    mem.write_bytes(bytes(0x1000))
    r = subprocess.run([str(regtimeline), "0", "0", "0x10", "--", "sleep", "0.05"],
                       capture_output=True, text=True, timeout=10,
                       env={"REGTIMELINE_MEM": str(mem), "REGTIMELINE_BASE": "0",
                            "PATH": "/usr/bin:/bin"})
    m = re.search(r" samples (\d+) ", r.stdout)
    assert m and int(m.group(1)) > 100, r.stdout


@pytest.mark.parametrize("args", [[], ["1", "0", "0x10", "true"], ["1", "0", "0x3-0x8", "--",
                                                                 "true"],
                                  ["1", "0", "0x10-0x4", "--", "true"],
                                  ["1", "0", "0x0-0x4000", "--", "true"]])
def test_regtimeline_usage(regtimeline, args):
    r = subprocess.run([str(regtimeline), *args], capture_output=True, text=True, timeout=10)
    assert r.returncode == 2


# ---- kernel pokes (debugfs kpoke) and registers (debugfs kreg) ----------------------------

def no_size(host, space):
    raise AssertionError(f"asked the tool for {space}")


@pytest.mark.parametrize("host,space", [("tri", "ta"), ("tri", "rd"), ("fill", "tq"),
                                        ("copy", "tq"), ("fill", "kreg"), ("tri", "kreg")])
def test_load_kernel_spaces(tmp_path, host, space):
    s = table(tmp_path, f'name = "t"\nabout = "x"\nhost = "{host}"\n'
                        f'[[range]]\nspace = "{space}"\n')
    assert s.kernel


@pytest.mark.parametrize("host,space", [("tri", "tq"), ("fill", "ta"), ("copy", "rd"),
                                        ("fill", "ta:1"), ("fill", "kreg:0")])
def test_load_rejects_kernel_spaces_of_the_other_kind(tmp_path, host, space):
    with pytest.raises(sweep.SweepError):
        table(tmp_path, f'name = "t"\nabout = "x"\nhost = "{host}"\n'
                        f'[[range]]\nspace = "{space}"\n')


def test_kernel_space_sizes_are_the_kernels():
    # sgxfive_kpoke_words() in the kernel fork
    assert sweep.KSPACES == {"ta": 176, "rd": 123, "tq": 306}
    assert sweep.KREGS == (0x0810, 0x0814, 0x0818, 0x0a78, 0x0abc)
    # sgxfive_kreg_allowed's others: written only by a 3D render's details, so they hold
    # through a transfer job (fill, copy)
    assert sweep.KREGS_3D == (0x0418, 0x04dc, 0x04e8, 0x0520, 0x0800)


def test_kreg_ranges_reach_the_render_only_registers(tmp_path):
    t = tmp_path / "k.toml"
    t.write_text('name = "k"\nabout = "a"\nhost = "copy"\n[[range]]\nspace = "kreg"\n'
                 'indices = [0x0400, 0x0900]\n')
    got = sweep.resolve(sweep.load(t), lambda h, sp: 0)
    assert [o for _, o, _ in got] == [0x0418, 0x04dc, 0x04e8, 0x0520, 0x0800, 0x0810, 0x0814,
                                      0x0818]


def test_cases_kernel_words(tmp_path):
    s = table(tmp_path, """
        name = "t"
        about = "x"
        host = "tri"
        [[range]]
        space = "ta"
        [[range]]
        space = "rd"
        indices = [120, 122]
    """)
    cs = sweep.cases(s, no_size)
    assert len(cs) == 1 + (176 + 3) * 34
    assert cs[1].id == "ta:0^=0x1" and cs[-1].id == "rd:122=0xffffffff"
    with pytest.raises(sweep.SweepError):
        sweep.cases(table(tmp_path, 'name = "t"\nabout = "x"\nhost = "fill"\n'
                                    '[[range]]\nspace = "tq"\nindices = [0, 306]\n'), no_size)


def test_cases_kernel_registers(tmp_path):
    s = table(tmp_path, """
        name = "t"
        about = "x"
        host = "fill"
        bits = [0]
        values = []
        [[range]]
        space = "kreg"
    """)
    assert [c.id for c in sweep.cases(s, no_size)] == [
        "baseline", "kreg:0x0810^=0x1", "kreg:0x0814^=0x1", "kreg:0x0818^=0x1",
        "kreg:0x0a78^=0x1", "kreg:0x0abc^=0x1"]
    s = table(tmp_path, 'name = "t"\nabout = "x"\nhost = "fill"\nbits = [0]\nvalues = []\n'
                        '[[range]]\nspace = "kreg"\nindices = [0x0814, 0x0a78]\n')
    assert [c.id for c in sweep.cases(s, no_size)][1:] == [
        "kreg:0x0814^=0x1", "kreg:0x0818^=0x1", "kreg:0x0a78^=0x1"]


def test_tool_args_leave_kernel_pokes_out(tmp_path):
    s = table(tmp_path, 'name = "t"\nabout = "x"\nhost = "tri"\n[[range]]\nspace = "ta"\n')
    c = sweep.Case("ta:3^=0x1", ["ta:3^=0x1"])
    assert sweep.tool_args(s, c) == ["tri"]
    assert sweep.local_argv(s, c, "T", mock=True) == ["T", "--mock", "tri"]


FAKE_SUDO = r'''#!/usr/bin/env python3
# Stands in for sudo and the kernel's kpoke and kreg debugfs files.
import os, pathlib, re, sys
a = sys.argv[1:]
if a[:1] == ["-n"]:
    a = a[1:]
if a[0] == "tee" and pathlib.Path(a[1]).name in ("kpoke", "kreg"):
    p, data = pathlib.Path(a[1]), sys.stdin.read()
    if not p.exists():
        sys.exit(1)
    if p.name == "kpoke":
        cur = [x for x in p.read_text().splitlines() if x]
        for line in data.split():
            cur = [] if line == "clear" else cur + [line]
        p.write_text("".join(x + "\n" for x in cur))
        sys.exit(0)
    m = re.fullmatch(r"(0x[0-9a-f]+)(\^?)=(0x[0-9a-f]+|\d+)", data.strip())
    regs = dict(x.split() for x in p.read_text().splitlines())
    if not m or m[1] not in regs:
        sys.exit(1)
    v = int(m[3], 0)
    new = (int(regs[m[1]], 16) ^ v) if m[2] else v
    keep = int(os.environ.get("FAKE_KREG_BITS", "0xffffffff"), 0)
    regs[m[1]] = f"0x{new & keep:08x}"
    p.write_text("".join(f"{k} {x}\n" for k, x in regs.items()))
    sys.exit(0)
os.execvp(a[0], a)
'''

FAKE_TOOL = r'''#!/bin/sh
# Stands in for sgxfive-test: shows what is armed, then (FAKE_APPLY=1) takes it, as a job.
echo "armed: $(tr '\n' ' ' < "$FAKE_DBG/kpoke")"
[ "$FAKE_APPLY" = 1 ] && : > "$FAKE_DBG/kpoke"
r=$(awk '$1 == "0x0810" { print $2 }' "$FAKE_DBG/kreg")
echo "tool sees 0x0810 $r"
echo "job: ok"
exit "${FAKE_RC:-0}"
'''


@pytest.fixture
def fake_target(tmp_path):
    """A debugfs directory, sudo and the tool, as the laptop's, for kernel_script."""
    bin_ = tmp_path / "bin"
    bin_.mkdir()
    for name, text in (("sudo", FAKE_SUDO), ("tool", FAKE_TOOL)):
        (bin_ / name).write_text(text)
        (bin_ / name).chmod(0o755)
    dbg = tmp_path / "dbg"
    dbg.mkdir()
    (dbg / "kpoke").write_text("tq:1=0x00000002\n")         # left over: cleared first
    (dbg / "kreg").write_text("".join(f"{r:#06x} 0x{0x50 + i:08x}\n"
                                      for i, r in enumerate(sweep.KREGS)))
    env = {"PATH": f"{bin_}:/usr/bin:/bin", "FAKE_DBG": str(dbg)}

    def run(s, c, base=None, **extra):
        cmd = sweep.target_cmd(s, c, "tool", "./regtimeline", str(dbg), base)
        r = subprocess.run(["sh", "-c", cmd], capture_output=True, text=True, timeout=30,
                           env={**env, **extra})
        return r.returncode, r.stdout, r.stderr
    return dbg, run


def test_target_cmd_without_kernel_pokes_is_the_tool(tmp_path):
    s = small(tmp_path)
    assert sweep.target_cmd(s, sweep.Case("xfer:0^=0x1", ["xfer:0^=0x1"]), "./t", "./rt",
                            "/d") == "./t fill --poke 'xfer:0^=0x1'"


def test_target_cmd_records_the_counters(tmp_path):
    """counters: the tool runs inside regtimeline over the visibility counters, as root."""
    s = small(tmp_path)
    c = sweep.Case("xfer:0^=0x1", ["xfer:0^=0x1"])
    assert sweep.target_cmd(s, c, "./t", "./rt", "/d", counters=True) == \
        "sudo -n ./rt 0 0 0x0494-0x04b4 -- ./t fill --poke 'xfer:0^=0x1'"


def test_target_cmd_adds_the_counters_to_a_timeline(tmp_path):
    s = table(tmp_path, 'name = "t"\nabout = "x"\nhost = "fill"\n'
              'timeline = { regs = "0x0484-0x0490", total = 1.0, lead = 0.1 }\n'
              '[[range]]\nspace = "xfer"\n')
    c = sweep.Case("xfer:0^=0x1", ["xfer:0^=0x1"])
    cmd = sweep.target_cmd(s, c, "./t", "./rt", "/d", counters=True)
    assert "./rt 1.0 0.1 0x0484-0x0490,0x0494-0x04b4 --" in cmd
    assert sweep.target_cmd(s, c, "./t", "./rt", "/d").count("0x0494") == 0


def test_report_lists_the_cases_that_counted(tmp_path):
    s = small(tmp_path)
    cs = sweep.cases(s, size_of)
    tl0 = "timeline: regs " + " ".join(f"{o:#06x}" for o in range(0x494, 0x4b8, 4)) + \
        " samples 9 seconds 0 start 0 end 9 rc 0\n"
    zero = tl0 + "tl 0" + " 00000000" * 9 + "\n"
    hot = zero + "tl 5" + " 00000000" * 8 + " 0000000e\n"
    done = {c.id: sweep.Record(c.id, "x", 0, "job: ok\ntarget: 4x4 hash 0x1\n" +
                               (hot if i == 2 else zero), "", 0.1)
            for i, c in enumerate(cs[:4])}
    rep = sweep.report(s, cs, done, masks={})
    line = next(ln for ln in rep.splitlines() if ln.startswith("counters:"))
    assert line == f"counters: 4 recorded, 1 counted: {cs[2].id} (0x04b4 0x0..0xe)"


def test_kernel_script_kpoke_applied(tmp_path, fake_target):
    dbg, run = fake_target
    s = table(tmp_path, 'name = "t"\nabout = "x"\nhost = "tri"\n[[range]]\nspace = "ta"\n')
    c = sweep.Case("ta:3^=0x1", ["ta:3^=0x1"])
    cmd = sweep.target_cmd(s, c, "tool", "./rt", str(dbg))
    rec = sweep.Record(c.id, cmd, 0, "job: ok\n", "", 0.1)
    assert sweep.parse_raw(sweep.format_record(rec)) == {c.id: rec}     # one line in raw.txt
    rc, so, se = run(s, c, FAKE_APPLY="1", FAKE_RC="1")
    assert rc == 1, se
    assert "armed: ta:3^=0x1 \n" in so and "job: ok\n" in so
    assert so.endswith("kpoke left: none\n")
    assert sweep.kpoke_left(so) == []
    assert (dbg / "kpoke").read_text() == ""


def test_kernel_script_kpoke_left_armed(tmp_path, fake_target):
    dbg, run = fake_target
    s = table(tmp_path, 'name = "t"\nabout = "x"\nhost = "fill"\n[[range]]\nspace = "tq"\n')
    rc, so, _ = run(s, sweep.Case("tq:305=0xffffffff", ["tq:305=0xffffffff"]))
    assert rc == 0 and "kpoke left: tq:305=0xffffffff" in so
    assert sweep.kpoke_left(so) == [("tq", 305, False, 0xffffffff)]
    assert (dbg / "kpoke").read_text() == ""               # cleared after the case
    # the baseline of a kernel table arms nothing, clears what was left
    (dbg / "kpoke").write_text("tq:1=0x00000002\n")
    rc, so, _ = run(s, sweep.Case("baseline", []))
    assert "armed:  \n" in so or "armed: \n" in so
    assert sweep.kpoke_left(so) == []


def test_kernel_script_kpoke_not_armed_is_an_error(tmp_path, fake_target):
    dbg, run = fake_target
    (dbg / "kpoke").unlink()
    s = table(tmp_path, 'name = "t"\nabout = "x"\nhost = "tri"\n[[range]]\nspace = "rd"\n')
    rc, so, se = run(s, sweep.Case("rd:0=0", ["rd:0=0"]))
    assert rc == 3 and "job:" not in so and "kpoke" in se
    assert sweep.classify(rc, so, BASE).cls == "error"


def test_kernel_script_kreg(tmp_path, fake_target):
    dbg, run = fake_target
    s = table(tmp_path, 'name = "t"\nabout = "x"\nhost = "fill"\n[[range]]\nspace = "kreg"\n')
    rc, so, se = run(s, sweep.Case("baseline", []))
    assert rc == 0, se
    base = sweep.kreg_values(so)
    assert base == {r: 0x50 + i for i, r in enumerate(sweep.KREGS)}
    # a register a killed case left poked is set back to the baseline's value first
    (dbg / "kreg").write_text((dbg / "kreg").read_text().replace("0x00000050", "0x00000777"))
    rc, so, se = run(s, sweep.Case("kreg:0x0810^=0x100", ["kreg:0x0810^=0x100"]), base,
                     FAKE_KREG_BITS="0xff")
    assert rc == 0, se
    assert "kreg 0x0810: was 0x00000050 reads 0x00000050\n" in so    # bit 8 does not take
    assert "tool sees 0x0810 0x00000050" in so
    assert "kreg 0x0810: after the job 0x00000050\n" in so
    rc, so, se = run(s, sweep.Case("kreg:0x0810^=0x1", ["kreg:0x0810^=0x1"]), base)
    assert "kreg 0x0810: was 0x00000050 reads 0x00000051\n" in so
    assert "tool sees 0x0810 0x00000051" in so
    assert sweep.kreg_results(so) == {0x0810: (0x50, 0x51, 0x51)}
    assert "0x0810 0x00000050\n" in (dbg / "kreg").read_text()        # restored


def test_run_hands_the_baseline_registers_to_the_executor(tmp_path):
    s = table(tmp_path, 'name = "t"\nabout = "x"\nhost = "fill"\nbits = [0]\nvalues = []\n'
                        '[[range]]\nspace = "kreg"\nindices = [0x0810, 0x0814]\n')

    class RegExec(FakeExec):
        kreg_base = None

        def __call__(self, s, case):
            self.seen.append((case.id, self.kreg_base))
            return super().__call__(s, case)
    ex = RegExec({"baseline": (0, "kreg: 0x0810=0x00000050 0x0814=0x00000000\n" + out())})
    ex.seen = []
    sweep.run(s, ex, tmp_path / "o", no_size, limit=2)
    want = {0x0810: 0x50, 0x0814: 0}
    assert ex.seen == [("baseline", None), ("kreg:0x0810^=0x1", want)]
    ex.kreg_base, ex.seen = None, []                    # a resumed run: from raw.txt
    sweep.run(s, ex, tmp_path / "o", no_size)
    assert ex.seen == [("kreg:0x0814^=0x1", want)]


def kout(left="none", **kw):
    return out(**kw) + f"kpoke left: {left}\n"


def test_report_kernel_words(tmp_path):
    s = table(tmp_path, """
        name = "t"
        about = "x"
        host = "tri"
        bits = [0, 1]
        values = []
        [[range]]
        space = "ta"
        indices = [148, 149]
    """)
    masks = {"cmd:0": sweep.Mask("validate", ["ta:148"], "c.c:9")}
    ex = FakeExec({"baseline": (0, kout()),
                   "ta:148^=0x1": (1, kout("ta:148^=0x00000001",
                                           job="rejected (Invalid argument)")),
                   "ta:148^=0x2": (1, kout(job="failed: job hung, context lost (x)")),
                   "ta:149^=0x1": (1, kout(h="0x00000000000000cc", diff=4)),
                   "ta:149^=0x2": (0, kout())})
    d = tmp_path / "o"
    sweep.run(s, ex, d, no_size, masks=masks)
    lines = {ln.split(": ")[0]: ln for ln in (d / "report.txt").read_text().splitlines()}
    assert lines["ta:148"] == ("ta:148: ^=0x1 rejected (Invalid argument) [never reached the "
                               "GPU]; ^=0x2 hang [kpoke applied in 1 of 2; carries cmd:0]")
    assert lines["ta:149"] == "ta:149: ^=0x1 changed (4 pixels) [kpoke applied in 2 of 2]"


def test_report_kernel_registers(tmp_path):
    s = table(tmp_path, """
        name = "t"
        about = "x"
        host = "fill"
        bits = [0, 8]
        values = ["=0"]
        [[range]]
        space = "kreg"
        indices = [0x0810, 0x0810]
    """)

    def k(was, reads, after, **kw):
        return (f"kreg: 0x0810={was:#010x}\nkreg 0x0810: was {was:#010x} reads {reads:#010x}\n"
                + out(**kw) + f"kreg 0x0810: after the job {after:#010x}\n")
    ex = FakeExec({"baseline": (0, "kreg: 0x0810=0x00000050\n" + out()),
                   "kreg:0x0810^=0x1": (0, k(0x50, 0x51, 0x51)),
                   "kreg:0x0810^=0x100": (1, k(0x50, 0x50, 0x50, h="0x00000000000000cc",
                                               diff=1)),
                   "kreg:0x0810=0": (0, k(0x50, 0x0, 0x40))})
    d = tmp_path / "o"
    sweep.run(s, ex, d, no_size)
    line = [ln for ln in (d / "report.txt").read_text().splitlines()
            if ln.startswith("kreg:0x0810")][0]
    assert line == ("kreg:0x0810: ^=0x100 changed (1 pixels) [register: was 0x00000050; "
                    "flips that took 0x00000001, did not 0x00000100; the job changed it in "
                    "1 of 3]")


def test_mock_end_to_end_kernel_table(tool, tmp_path):
    # the mock has no kernel: the host job runs without the kernel poke
    s = table(tmp_path, 'name = "k"\nabout = "x"\nhost = "fill"\nbits = [0]\nvalues = []\n'
                        '[[range]]\nspace = "tq"\nindices = [0, 1]\n')
    res = sweep.run(s, sweep.LocalExec(tool, mock=True), tmp_path / "o",
                    sweep.tool_size_of(tool))
    assert res.done == 3 and res.stopped is None


def test_ssh_control_socket_fits_a_unix_socket_path(monkeypatch):
    """ssh appends ".<16 random chars>" to the ControlPath while it sets the socket up, and the
    expanded %C is 40 hex digits; macOS's long $TMPDIR pushed that past the 104 bytes a Unix
    socket path may have, and every case failed with rc 255."""
    monkeypatch.setenv("SGX_TARGET_HOST", "user@host")
    monkeypatch.setenv("TMPDIR", "/var/folders/86/hx7sqkhd1rn400k9693sghnw0000gn/T/")
    e = sweep.SshExec()
    ctl = next(a.split("=", 1)[1] for a in e.ssh if a.startswith("ControlPath="))
    assert len(ctl.replace("%C", "x" * 40)) + 17 < 104


# ---- rerun: the changed cases again, every pixel against the baseline's ------------------

PIX = "job: ok\ntarget: 2x2 hash 0x1\ndiff: 0 of 4 pixels\noutside: 0 dwords\n" \
      "row 0: 0x00000001 0x00000002\nrow 1: 0x00000003 0x00000004\n"


def test_parse_pixels():
    assert sweep.parse_pixels(PIX) == [[1, 2], [3, 4]]
    assert sweep.parse_pixels("job: ok\n") is None


def test_pixel_diff_counts_boxes_and_values():
    d = sweep.pixel_diff([[1, 2], [3, 4]], [[1, 9], [3, 9]])
    assert d.count == 2 and d.box == (1, 0, 1, 1) and d.values == [(9, 2)]
    assert sweep.pixel_diff([[1]], [[1]]).count == 0
    assert sweep.pixel_diff([[1, 2]], [[1]]).count is None      # sizes differ


def test_changed_cases_put_the_baseline_first(tmp_path):
    s = table(tmp_path, """
        name = "t"
        about = "x"
        host = "fill"
        bits = [0, 1]
        [[range]]
        space = "xfer"
        indices = [3, 3]
    """)
    cs = sweep.cases(s, lambda h, sp: 42)
    rec = lambda cid, h: sweep.Record(cid, "c", 0, f"job: ok\ntarget: 2x2 hash {h}\n"
                                      "diff: 0 of 4 pixels\noutside: 0 dwords\n", "", 0.1)
    done = {c.id: rec(c.id, "0x1") for c in cs}
    done[cs[2].id] = rec(cs[2].id, "0x2")
    assert [c.id for c in sweep.changed_cases(s, cs, done)] == [cs[0].id, cs[2].id]


def test_mock_rerun_reports_pixels_against_the_baseline(tool, tmp_path):
    s = table(tmp_path, """
        name = "tiny"
        about = "x"
        host = "fill"
        bits = [0]
        [[range]]
        space = "xfer"
        indices = [12, 13]
    """)
    d = tmp_path / "o"
    sweep.run(s, sweep.LocalExec(tool, mock=True), d, sweep.tool_size_of(tool))
    res = sweep.rerun(s, sweep.LocalExec(tool, mock=True), d, sweep.tool_size_of(tool))
    assert res.total == 1 + sum(1 for line in (d / "report.txt").read_text().splitlines()
                                for _ in re.findall(r"changed \(", line))
    px = (d / "pixels" / "report.txt").read_text()
    assert "xfer:13=0: 1536 pixels differ from the baseline" in px
    raw = sweep.parse_raw((d / "pixels" / "raw.txt").read_text())
    assert "--pixels" in raw["baseline"].cmd


def test_the_kernel_default_pb_comes_back_when_a_run_dies(tmp_path):
    s = table(tmp_path, """
        name = "t"
        about = "x"
        host = "tri"
        pb_pages = [0x422, 0x23]
    """)

    class Dies(FakeExec):
        def __call__(self, s, c):
            if c.pb == 0x23:
                raise KeyboardInterrupt
            return super().__call__(s, c)
    ex = Dies()
    setups = []
    ex.setup = lambda s, pb: setups.append(pb)
    with pytest.raises(KeyboardInterrupt):
        sweep.run(s, ex, tmp_path / "o", size_of)
    assert setups == [0x422, 0x23, sweep.DEFAULT_PB_PAGES]
    assert sweep.DEFAULT_PB_PAGES == 0x422
