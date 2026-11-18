# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""sessioncheck.py: the build checks of a closing session, one case per round-6 slip. r6-dpm's
staged tree lacked lib_check.sh (num_eq "command not found" at a control on the laptop); r6-misc's
runner gave --depth-dump a directory it had not made, so no dump was kept for its scorer."""
import gzip
import pathlib
import subprocess
import sys

import pytest

import sessioncheck as C

SCRIPT = pathlib.Path(__file__).resolve().parent / "sessioncheck.py"

RUN_STAGE = """#!/bin/bash
# run_stage.sh STAGE: the toy runner (num_eq in this comment is not a call)
DIR=$(cd "$(dirname "$0")" && pwd)
. "$DIR/lib.sh"
for f in $DIR/../tables/*.txt; do :; done
num_eq 1 1 || exit 9
"$PY" "$DIR/reader.py" || exit 8   # reader.py prints ok
echo "## end"
"""
LIB = """HERE_LIB=$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)
. "$HERE_LIB/lib_check.sh"
"""
LIB_CHECK = """is_num() { case "$1" in 0x*|[0-9]*) return 0 ;; *) return 1 ;; esac; }
num_eq() { is_num "$1" && is_num "$2" && [ $(($1)) -eq $(($2)) ]; }
"""
STAGE = """#!/bin/bash
push() { scp -q "$@"; }
push run_stage.sh lib.sh reader.py
"""


@pytest.fixture
def src(tmp_path):
    d = tmp_path / "run"
    d.mkdir()
    for name, text in [("run_stage.sh", RUN_STAGE), ("lib.sh", LIB), ("lib_check.sh", LIB_CHECK),
                       ("reader.py", "print('ok')\n"), ("stage.sh", STAGE)]:
        (d / name).write_text(text)
    return d


def stage_tree(src, dest, names):
    dest.mkdir(parents=True)
    for n in names:
        (dest / n).write_text((src / n).read_text())
    return dest


A1 = ["run_stage.sh", "lib.sh", "reader.py"]           # attempt a1's list: lib_check.sh left out
FULL = A1 + ["lib_check.sh"]


# ---- the staged tree, statically -----------------------------------------------------------
def test_staged_finds_the_unstaged_file_and_its_function(src):
    assert C.staged_problems(src, A1) == [
        "lib.sh sources or runs lib_check.sh, which is not staged",
        "run_stage.sh calls num_eq, defined in lib_check.sh, which is not staged"]


def test_staged_complete_tree_passes(src):
    assert C.staged_problems(src, FULL) == []


def test_staged_a_file_that_is_nowhere(src):
    (src / "lib.sh").write_text(LIB + '. "$HERE_LIB/gone.env"\n')
    assert C.staged_problems(src, FULL) == [
        "lib.sh sources or runs gone.env, which is not staged (and not in the source either)"]


def test_staged_a_function_of_a_mac_side_script(src):
    # push is defined in stage.sh, which runs on the Mac: a staged script may not call it
    (src / "run_stage.sh").write_text(RUN_STAGE + "push out\n")
    assert C.staged_problems(src, FULL) == [
        "run_stage.sh calls push, defined in stage.sh, which is not staged"]


def test_staged_only_entries_and_what_they_reach(src):
    # a staged file nothing sources is not analysed; one the entry sources is
    (src / "spare.sh").write_text('D=$(dirname "$0")\n. "$D/nothing.sh"\n')
    assert C.staged_problems(src, FULL + ["spare.sh"], entries=["run_stage.sh"]) == []


def test_staged_a_python_module_the_runner_imports(src):
    # reader.py imports kit.py beside it: run on the laptop, kit.py must be staged too
    (src / "reader.py").write_text("import sys\nimport kit\nfrom kit import x\n")
    (src / "kit.py").write_text("x = 1\n")
    assert C.staged_problems(src, FULL) == ["reader.py imports kit, which is not staged"]
    assert C.staged_problems(src, FULL + ["kit.py"]) == []


def test_staged_cli(src):
    r = subprocess.run([sys.executable, SCRIPT, "staged", src, *A1], capture_output=True,
                       text=True)
    assert r.returncode == 1
    assert "FAIL lib.sh sources or runs lib_check.sh, which is not staged" in r.stdout
    r = subprocess.run([sys.executable, SCRIPT, "staged", src, *FULL], capture_output=True,
                       text=True)
    assert r.returncode == 0, r.stdout


# ---- the staged tree, run under env -i -----------------------------------------------------
def test_envi_reproduces_the_missing_function(src, tmp_path):
    t = stage_tree(src, tmp_path / "a1", A1)
    rc, out, probs = C.run_env_i(["bash", str(t / "run_stage.sh")], {"PY": sys.executable})
    assert rc != 0
    assert any("No such file or directory" in p for p in probs)
    assert any("num_eq: command not found" in p for p in probs)


def test_envi_complete_tree_runs(src, tmp_path):
    t = stage_tree(src, tmp_path / "a2", FULL)
    rc, out, probs = C.run_env_i(["bash", str(t / "run_stage.sh")], {"PY": sys.executable})
    assert (rc, probs) == (0, [])
    assert "ok\n## end" in out


def test_envi_hides_the_callers_environment(tmp_path, monkeypatch):
    monkeypatch.setenv("SESSIONCHECK_LEAK", "1")
    s = tmp_path / "s.sh"
    s.write_text('[ -z "$SESSIONCHECK_LEAK" ] || { echo leaked; exit 1; }; echo "home=$HOME"\n')
    rc, out, probs = C.run_env_i(["bash", str(s)], {"HOME": "/nowhere"})
    assert (rc, out.strip(), probs) == (0, "home=/nowhere", [])


def test_envi_cli(src, tmp_path):
    t = stage_tree(src, tmp_path / "a1", A1)
    r = subprocess.run([sys.executable, SCRIPT, "envi", "--set", f"PY={sys.executable}", "--",
                        "bash", t / "run_stage.sh"], capture_output=True, text=True)
    assert r.returncode == 1
    assert "FAIL" in r.stdout and "num_eq: command not found" in r.stdout


# ---- kept files: declared, present and the only ones read -----------------------------------
def kept_dir(tmp_path, names):
    d = tmp_path / "kept"
    d.mkdir()
    (d / "cases.tsv").write_text("# name\tset\n" + "".join(f"{n}\tx\n" for n in names))
    for n in names:
        with gzip.open(d / f"{n}.txt.gz", "wt") as f:
            f.write("out\n")
    return d


def test_kept_missing_and_undeclared(tmp_path):
    d = kept_dir(tmp_path, ["a", "b"])
    (d / "a.extra").write_text("x")

    def scorer():
        for n in ("a", "b"):
            gzip.open(d / f"{n}.txt.gz", "rt").read()
        open(d / "a.extra").read()

    probs = C.kept_problems(d, ("cases.tsv", ".txt", ".depth.1.bin"), ["a", "b"], scorer)
    assert probs == ["the scorer reads a.depth.1.bin, which is not kept",
                     "the scorer reads b.depth.1.bin, which is not kept",
                     "the scorer read a.extra, which REQUIRED does not declare"]


def test_kept_complete(tmp_path):
    d = kept_dir(tmp_path, ["a"])
    assert C.kept_problems(d, ("cases.tsv", ".txt"), ["a"],
                           lambda: gzip.open(d / "a.txt.gz").read()) == []


def test_kept_rows_from_cases(tmp_path):
    d = kept_dir(tmp_path, ["a", "b"])
    assert C.kept_rows(d) == ["a", "b"]
    # the runners' cases.tsv starts with a plain header line, `name` first
    (d / "cases.tsv").write_text("name\tstage\na\tq287\n")
    assert C.kept_rows(d) == ["a"]


SCORER = '''
import gzip, os
REQUIRED = {"q287": ("cases.tsv", ".txt", ".depth.1.bin")}
def check_read(stage, d):
    for n in ("a",):
        gzip.open(os.path.join(d, n + ".txt.gz")).read()
'''


def test_kept_cli(tmp_path):
    d = kept_dir(tmp_path, ["a"])
    s = tmp_path / "score_x.py"
    s.write_text(SCORER)
    cmd = [sys.executable, SCRIPT, "kept", s, "q287", d, "--call", "check_read"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    assert r.returncode == 1
    assert "FAIL the scorer reads a.depth.1.bin, which is not kept" in r.stdout
    (d / "a.depth.1.bin.gz").write_text("x")
    r = subprocess.run(cmd, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


# ---- output directories: made before a tool writes into them ---------------------------------
def test_outdirs_missing(tmp_path):
    argv = ["tri", "--depth-dump", str(tmp_path / "depth"), f"--out={tmp_path}/o/x.txt", "-q"]
    assert C.missing_outdirs(argv, dir_opts=["--depth-dump"], file_opts=["--out"]) == [
        f"--depth-dump {tmp_path}/depth: no such directory",
        f"--out {tmp_path}/o/x.txt: no directory {tmp_path}/o"]
    (tmp_path / "depth").mkdir()
    (tmp_path / "o").mkdir()
    assert C.missing_outdirs(argv, dir_opts=["--depth-dump"], file_opts=["--out"]) == []


def test_outdirs_option_without_argument():
    assert C.missing_outdirs(["tri", "--depth-dump"], dir_opts=["--depth-dump"]) == [
        "--depth-dump: no argument"]


def test_outdirs_cli(tmp_path):
    cmd = [sys.executable, SCRIPT, "outdirs", "--dir-opt=--depth-dump", "--",
           "tri", "--depth-dump", tmp_path / "depth"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    assert r.returncode == 1 and "no such directory" in r.stdout
    (tmp_path / "depth").mkdir()
    assert subprocess.run(cmd, capture_output=True).returncode == 0


# ---- the premise stage, from the runner -------------------------------------------------------
def test_premise_cli(tmp_path):
    f = tmp_path / "a0.read"
    f.write_text("void=0 cls=R knob=0x96 gps_left=- nparts=0\n")
    r = subprocess.run([sys.executable, SCRIPT, "premise", "a0-t-s3m7", "knob gps_left", f],
                       capture_output=True, text=True)
    assert r.returncode == 1
    assert r.stdout.strip() == "STOP: premise: control a0-t-s3m7 has no reading of gps_left"
    r = subprocess.run([sys.executable, SCRIPT, "premise", "a0-t-s3m7", "knob cls", "-"],
                       input=f.read_text(), capture_output=True, text=True)
    assert (r.returncode, r.stdout) == (0, "")


def test_premise_cli_no_reading_declared(tmp_path):
    r = subprocess.run([sys.executable, SCRIPT, "premise", "c", "", "-"], input="x=1\n",
                       capture_output=True, text=True)
    assert r.returncode == 2


# ---- the freeze lint: constants for registers the kit snapshots, calibrated intervals --------
# r30-evst (E1116) and r33-tim (E1131) froze premises from a mid-session reading and from idle
# spacing; each voided whole stages.
def row(name, sset="control", knobs="reads:diff", args="tri --width 64 --height 64", tool="t10"):
    return dict(name=name, set=sset, knobs=knobs.split(), args=args, tool=tool,
                reads=tuple(k[6:].split(",") for k in knobs.split() if k.startswith("reads:"))[0]
                if "reads:" in knobs else ())


def pred(**q):
    """{case: {quantity: {model: value}}} from case=(quantity, value) pairs."""
    out = {}
    for case, (qty, val) in q.items():
        out.setdefault(case, {}).setdefault(qty, {})["H"] = val
    return out


def lint(tables, preds, order=None):
    return C.lint_predictions(tables, preds, order or list(tables))


def test_the_kit_snapshot_register_list_holds_the_registers_of_a_real_snap0():
    assert {0x0A60, 0x0ACC, 0x0C04, 0x0804, 0x012C} <= C.SNAP_REGS
    assert 0x0748 not in C.SNAP_REGS


def test_a_control_constant_for_a_snapshotted_register_warns():
    warns, errs = lint({"s0": [row("c1", knobs="reads:reg")]},
                       {"s0": pred(c1=("reg:0x0a60", "0x1000ffff"))})
    assert not errs
    assert len(warns) == 1 and "c1" in warns[0] and "0x0a60" in warns[0]
    assert "@snap0" in warns[0]


def test_a_snap0_form_control_does_not_warn():
    for v in ("@snap0", "@snap0:ref", "@snap0&0xffff"):
        tables = {"s0": [row("ref"), row("c1", knobs="reads:reg")]}
        assert lint(tables, {"s0": pred(c1=("reg:0x0a60", v))}) == ([], [])


def test_a_constant_for_a_register_the_kit_does_not_snapshot_is_not_warned():
    tables = {"s0": [row("c1", knobs="reads:reg")]}
    assert lint(tables, {"s0": pred(c1=("reg:0x0748", "0x1"))}) == ([], [])


def test_a_held_row_constant_is_not_a_control_premise():
    tables = {"s0": [row("h1", sset="held", knobs="-")]}
    assert lint(tables, {"s0": pred(h1=("reg:0x0a60", "0x5"))}) == ([], [])


def test_a_snap0_reference_to_an_unknown_row_is_an_error():
    tables = {"s0": [row("c1", knobs="reads:reg")]}
    _, errs = lint(tables, {"s0": pred(c1=("reg:0x0a60", "@snap0:nope"))})
    assert len(errs) == 1 and "nope" in errs[0]


def test_a_snap0_form_that_is_no_form_is_an_error():
    tables = {"s0": [row("c1", knobs="reads:reg")]}
    _, errs = lint(tables, {"s0": pred(c1=("reg:0x0a60", "@snap9"))})
    assert len(errs) == 1 and "@snap9" in errs[0]


RT = 'rt'


def rt(name, regs, sset="control", knobs="reads:diff,ivl"):
    return row(name, sset=sset, knobs=knobs, tool=RT,
               args=f'0.06 0.005 {regs} -- "$HOME/sgxfive-test-t10" tri --width 64 --height 64')


def test_a_control_interval_constant_warns_to_calibrate():
    tables = {"t1": [rt("c1", "0x012c,0x0acc")]}
    warns, errs = lint(tables, {"t1": pred(c1=("ivl", "1100..1500"))})
    assert not errs and len(warns) == 1 and "calibrat" in warns[0] and "c1" in warns[0]


def test_a_calibrated_interval_control_is_clean():
    tables = {"cal": [rt("k1", "0x012c,0x0acc"), rt("k2", "0x012c,0x0acc")],
              "t1": [rt("c1", "0x012c,0x0acc")]}
    assert lint(tables, {"t1": pred(c1=("ivl", "@cal:cal"))}, ["cal", "t1"]) == ([], [])


def test_a_calibration_stage_must_come_first():
    tables = {"cal": [rt("k1", "0x0acc"), rt("k2", "0x0acc")], "t1": [rt("c1", "0x0acc")]}
    _, errs = lint(tables, {"t1": pred(c1=("ivl", "@cal:cal"))}, ["t1", "cal"])
    assert len(errs) == 1 and "before" in errs[0]


def test_a_calibration_of_another_register_set_is_an_error():
    tables = {"cal": [rt("k1", "0x012c"), rt("k2", "0x012c")], "t1": [rt("c1", "0x012c,0x0acc")]}
    _, errs = lint(tables, {"t1": pred(c1=("ivl", "@cal:cal"))}, ["cal", "t1"])
    assert len(errs) == 1 and "register set" in errs[0]


def test_a_register_set_is_compared_as_a_set_not_as_text():
    tables = {"cal": [rt("k1", "0x0acc,0x012c"), rt("k2", "0x012c,0x0acc")],
              "t1": [rt("c1", "0x012c,0x0acc")]}
    assert lint(tables, {"t1": pred(c1=("ivl", "@cal:cal"))}, ["cal", "t1"]) == ([], [])


def test_a_calibration_stage_that_reads_no_interval_or_has_one_row_is_an_error():
    tables = {"cal": [rt("k1", "0x0acc", knobs="reads:diff")], "t1": [rt("c1", "0x0acc")]}
    _, errs = lint(tables, {"t1": pred(c1=("ivl", "@cal:cal"))}, ["cal", "t1"])
    assert any("ivl" in e for e in errs)
    tables["cal"] = [rt("k1", "0x0acc")]
    _, errs = lint(tables, {"t1": pred(c1=("ivl", "@cal:cal"))}, ["cal", "t1"])
    assert any("two" in e for e in errs)


def test_a_calibration_of_an_unknown_stage_is_an_error():
    tables = {"t1": [rt("c1", "0x0acc")]}
    _, errs = lint(tables, {"t1": pred(c1=("ivl", "@cal:zz"))})
    assert len(errs) == 1 and "zz" in errs[0]


def test_regtimeline_register_sets_are_parsed_from_the_args():
    assert C.timeline_regs('0.06 0.005 0x012c,0x0acc -- "$HOME/t" tri') == {0x012C, 0x0ACC}
    assert C.timeline_regs("tri --width 64") is None
