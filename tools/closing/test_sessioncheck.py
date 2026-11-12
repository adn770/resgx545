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
