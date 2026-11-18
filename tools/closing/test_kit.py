# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The session kit (tools/closing/kit, HACKING.md "Session kit"): a closing session declares its
tables, predictions, scorer and env, and the kit supplies the laptop runner, the Mac driver, the
staging list, the freeze pinned by commit, the static guard and the argv-driven mock. Each case
is one of the slips of rounds 5-7 made impossible: an unstaged lib, a dump directory never made,
a control that could not be read, /tmp, a mock that leaned on milliseconds, a freeze that broke
when main moved."""
import hashlib
import importlib.util
import os
import pathlib
import re
import subprocess
import sys

import pytest

HERE = pathlib.Path(__file__).resolve().parent
KIT = HERE / "kit"
sys.path.insert(0, str(KIT))
sys.path.insert(0, str(HERE.parent / "records"))

import frozen  # noqa: E402
import session as S  # noqa: E402

NEW = HERE / "new_session.py"
PY = sys.executable
SRCV = "41E2F5C756F96D20F7109A4"
TOOL_SHA = "e" * 64


def git(repo, *args):
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
               GIT_COMMITTER_EMAIL="t@t")
    return subprocess.run(["git", "-C", str(repo), *args], env=env, check=True,
                          capture_output=True, text=True).stdout.strip()


def commit_all(repo, msg="c"):
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", msg)
    return git(repo, "rev-parse", "HEAD")


@pytest.fixture
def repos(tmp_path):
    """A resgx545 holding this kit at a commit, and a data repository with one kept record."""
    main = tmp_path / "src" / "resgx545"
    for rel in S.KIT_SOURCES.values():
        (main / rel).parent.mkdir(parents=True, exist_ok=True)
        (main / rel).write_bytes((HERE.parent.parent / rel).read_bytes())
    (main / "tools/bringup").mkdir(parents=True)
    (main / "tools/bringup/health.sh").write_text("echo health\n")
    git(main, "init", "-q")
    c1 = commit_all(main)
    data = tmp_path / "src" / "resgx545-data"
    (data / "render/closing-r6-x").mkdir(parents=True)
    (data / "render/closing-r6-x/cases.tsv").write_text("name\trc\nj1\t0\n")
    git(data, "init", "-q")
    d1 = commit_all(data)
    return dict(main=main, c1=c1, data=data, d1=d1, tmp=tmp_path)


def scaffold(repos, name="r8-t", extra=()):
    kp = repos["tmp"] / "scratch" / name
    extra = list(extra)
    bound = [extra[i + 1].split("=")[0] for i, x in enumerate(extra) if x == "--tool-src"]
    names = ["t4"] + [extra[i + 1].split("=")[0] for i, x in enumerate(extra) if x == "--tool"]
    extra = [*extra, *(a for n in names if n not in bound
                       for a in ("--no-source", f"{n}=a test fixture with no library mock"))]
    r = subprocess.run([PY, str(NEW), str(kp), "--name", name, "--prefix", "r8t",
                        "--srcversion", SRCV, "--tool", f"t4=sgxfive-test-rgn4:{TOOL_SHA}",
                        "--resgx545", str(repos["main"]), "--commit", repos["c1"],
                        "--data", str(repos["data"]), "--data-commit", repos["d1"], *extra],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    return kp


def env_for(repos):
    return dict(os.environ, RESGX545=str(repos["main"]), RESGX545_DATA=str(repos["data"]))


def kit(kp, repos, *args):
    return subprocess.run([PY, str(kp / "kit" / "session.py"), *args, str(kp)],
                          capture_output=True, text=True, env=env_for(repos), timeout=600)


# ---- the scaffold ----------------------------------------------------------------------------
def test_the_scaffold_copies_the_kit_from_the_named_commit_not_the_working_tree(repos):
    (repos["main"] / "tools/closing/kit/lib_kit.sh").write_text("# moved on\n")
    kp = scaffold(repos)
    assert (kp / "kit/lib_kit.sh").read_bytes() == (KIT / "lib_kit.sh").read_bytes()
    for f in ("session.toml", "tables/s0.txt", "predictions/s0.tsv", "score/score.py",
              "mock/world.py", "run/hooks.sh", "tests/run_all.sh"):
        assert (kp / f).is_file(), f
    assert (kp / "kit/scorekit.py").read_bytes() == (HERE / "scorekit.py").read_bytes()


def test_the_scaffold_names_the_repo_venv_as_the_python_never_a_scratch_one(repos):
    """The interpreter with pytest and numpy is the repo's .venv, not a session's scratch
   : the generated README and tests/run_all.sh say so."""
    kp = scaffold(repos)
    readme, run_all = (kp / "README.md").read_text(), (kp / "tests/run_all.sh").read_text()
    assert "resgx545/.venv/bin/python" in readme and "resgx545/.venv/bin/python" in run_all
    for f in kp.rglob("*"):
        if f.is_file() and "kit" not in f.relative_to(kp).parts:
            assert b"pixel-faults" not in f.read_bytes(), f


def test_the_scaffold_passes_its_guard_its_mock_and_its_freeze(repos):
    kp = scaffold(repos)
    g = kit(kp, repos, "guard")
    assert g.returncode == 0, g.stdout
    m = kit(kp, repos, "mock")
    assert m.returncode == 0, m.stdout + m.stderr
    assert "FAIL" not in m.stdout
    assert re.search(r"^ok +world model: driver 0", m.stdout, re.M), m.stdout
    assert re.search(r"^ok +world nodiff: driver 25", m.stdout, re.M), m.stdout
    f = kit(kp, repos, "freeze")
    assert f.returncode == 0, f.stdout + f.stderr
    v = kit(kp, repos, "verify")
    assert v.returncode == 0, v.stdout


# ---- B: the freeze, pinned by commit -----------------------------------------------------------
def frozen_session(repos):
    kp = scaffold(repos)
    toml = (kp / "session.toml").read_text().replace(
        "pins = []", 'pins = ["resgx545:tools/bringup/health.sh", '
        '"data:render/closing-r6-x/cases.tsv"]')
    (kp / "session.toml").write_text(toml)
    f = kit(kp, repos, "freeze")
    assert f.returncode == 0, f.stdout + f.stderr
    return kp


def test_the_freeze_pins_the_kit_copies_and_the_inputs_by_commit(repos):
    kp = frozen_session(repos)
    lines = (kp / "FROZEN.commits").read_text().splitlines()
    body = [x for x in lines if not x.startswith("#")]
    sha = hashlib.sha256((KIT / "lib_kit.sh").read_bytes()).hexdigest()
    assert f"{sha}  {repos['c1']}  resgx545:tools/closing/kit/lib_kit.sh" in body
    assert any(x.endswith(f"{repos['d1']}  data:render/closing-r6-x/cases.tsv") for x in body)
    assert any(x.endswith(f"{repos['c1']}  resgx545:tools/bringup/health.sh") for x in body)
    fz = (kp / "FROZEN.sha256").read_text()
    assert f"  {repos['main']}/tools/bringup/health.sh\n" in fz
    assert "  tables/s0.txt\n" in fz and "  kit/run_stage.sh\n" in fz
    assert "out/" not in fz and "debug/" not in fz


def test_tools_records_frozen_accepts_the_kit_freeze(repos):
    kp = frozen_session(repos)
    pub = repos["data"] / "render" / "closing-r8-t"
    pub.mkdir(parents=True)
    for f in ("FROZEN.sha256", "FROZEN.commits"):
        (pub / f).write_bytes((kp / f).read_bytes())
    commit_all(repos["data"], "publish")
    assert frozen.check(repos["data"], repos["main"]) == []
    (pub / "FROZEN.commits").write_text((kp / "FROZEN.commits").read_text().replace(
        repos["d1"], repos["c1"]))
    assert frozen.check(repos["data"], repos["main"]) != []


def test_a_declared_tool_source_is_bound_by_toolsrc_and_a_built_line(repos):
    """new_session.py --tool-src NAME=COMMIT:PATH@RECIPE writes the TOOLSRC.sha256 pin and, at
    the freeze, the `built` line and the binary's freeze line frozen.py and session_tests.sh
    verify; nobody writes them by hand."""
    src = hashlib.sha256((repos["main"] / "tools/bringup/health.sh").read_bytes()).hexdigest()
    kp = scaffold(repos, extra=("--tool-src",
                                f"t4={repos['c1'][:9]}:tools/bringup/health.sh@"
                                "tools/bringup/health.sh"))
    assert (kp / "TOOLSRC.sha256").read_text() == \
        f"{src}  {repos['c1']}:tools/bringup/health.sh\n"
    f = kit(kp, repos, "freeze")
    assert f.returncode == 0, f.stdout + f.stderr
    built = f"{TOOL_SHA}  built  {repos['c1']}  tools/bringup/health.sh  {src}  " \
            "tools/bringup/health.sh\n"
    assert built in (kp / "FROZEN.commits").read_text()
    assert f"{TOOL_SHA}  bin/t4\n" in (kp / "FROZEN.sha256").read_text()
    v = kit(kp, repos, "verify")
    assert v.returncode == 0, v.stdout
    pub = repos["data"] / "render" / "closing-r8-t"
    pub.mkdir(parents=True)
    for n in ("FROZEN.sha256", "FROZEN.commits"):
        (pub / n).write_bytes((kp / n).read_bytes())
    commit_all(repos["data"], "publish")
    assert frozen.check(repos["data"], repos["main"]) == []


def test_a_tool_src_that_names_no_blob_or_a_wrong_tool_is_refused(repos):
    for spec in (f"t4={repos['c1']}:tools/nope.sh@tools/bringup/health.sh",
                 f"t9={repos['c1']}:tools/bringup/health.sh@tools/bringup/health.sh",
                 "t4=tools/bringup/health.sh"):
        kp = repos["tmp"] / "scratch" / "bad"
        r = subprocess.run([PY, str(NEW), str(kp), "--name", "r8-t", "--prefix", "r8t",
                            "--srcversion", SRCV, "--tool", f"t4=sgxfive-test-rgn4:{TOOL_SHA}",
                            "--tool-src", spec, "--resgx545", str(repos["main"]),
                            "--commit", repos["c1"], "--data", str(repos["data"]),
                            "--data-commit", repos["d1"]], capture_output=True, text=True)
        assert r.returncode != 0 and not (kp / "TOOLSRC.sha256").exists(), spec


def test_verify_reads_each_pin_at_its_commit_so_main_and_data_may_move(repos):
    kp = frozen_session(repos)
    (repos["main"] / "tools/bringup/health.sh").write_text("echo moved\n")
    (repos["main"] / "tools/closing/kit/lib_kit.sh").write_text("# moved\n")
    commit_all(repos["main"], "main moves")
    (repos["data"] / "render/closing-r6-x/cases.tsv").write_text("changed\n")
    v = kit(kp, repos, "verify")
    assert v.returncode == 0, v.stdout


def test_verify_finds_a_changed_session_file_a_new_file_and_a_wrong_commit(repos):
    kp = frozen_session(repos)
    (kp / "tables/s0.txt").write_text((kp / "tables/s0.txt").read_text() + "# edit\n")
    assert "tables/s0.txt" in kit(kp, repos, "verify").stdout
    kp = frozen_session(dict(repos, tmp=repos["tmp"] / "b"))
    (kp / "gen").mkdir()
    (kp / "gen/late.py").write_text("x = 1\n")
    v = kit(kp, repos, "verify")
    assert v.returncode != 0 and "gen/late.py" in v.stdout
    kp = frozen_session(dict(repos, tmp=repos["tmp"] / "c"))
    text = (kp / "FROZEN.commits").read_text()
    (kp / "FROZEN.commits").write_text(text.replace(repos["d1"], repos["c1"]))
    v = kit(kp, repos, "verify")
    assert v.returncode != 0 and "data:render/closing-r6-x/cases.tsv" in v.stdout


def test_the_freeze_refuses_a_kit_copy_that_is_not_the_commits_blob(repos):
    kp = scaffold(repos)
    with open(kp / "kit/lib_kit.sh", "a") as f:
        f.write("# local edit\n")
    f = kit(kp, repos, "freeze")
    assert f.returncode != 0 and "kit/lib_kit.sh" in f.stdout
    assert not (kp / "FROZEN.sha256").exists()


def test_a_freeze_is_never_rewritten(repos):
    kp = frozen_session(repos)
    f = kit(kp, repos, "freeze")
    assert f.returncode != 0 and "never rewritten" in f.stdout


# ---- the static guard ------------------------------------------------------------------------
@pytest.mark.parametrize("line,word", [
    ("t=/tmp/x", "/tmp"),
    ("export TMPDIR=$HOME", "TMPDIR"),
    ("while true; do :; done", "wait loop"),
    ("sudo -n timeout 5 cat \"$D/regs\"", "-k"),
    ("cat \"$D/regs\"", "sudo -n"),
    ("rm -rf \"$JW\"", "rm"),
    ("dbg_write render_pb_pages 0x422", "debugfs write"),
    ("sudo -n reboot", "forbidden"),
])
def test_the_guard_refuses_the_laptop_slips_in_a_hook(repos, line, word):
    kp = scaffold(repos)
    with open(kp / "run/hooks.sh", "a") as f:
        f.write(f"hook_extra() {{ {line}; }}\n")
    g = kit(kp, repos, "guard")
    assert g.returncode != 0 and word in g.stdout, g.stdout


def test_the_guard_refuses_a_knob_tool_or_option_the_session_does_not_allow(repos):
    kp = scaffold(repos)
    t = kp / "tables/s0.txt"
    base = t.read_text()
    for row, word in [("x|fit|safe|bogus|t4|fill", "bogus"),
                      ("x|fit|safe|-|t9|fill", "t9"),
                      ("x|fit|safe|dbg:render_pb_pages=1|t4|fill", "render_pb_pages"),
                      ("x|control|safe|-|t4|fill", "reads:"),
                      ("x|fit|safe|-|t4|fill --kpoke 0x1=2", "--kpoke")]:
        t.write_text(base + row + "\n")
        g = kit(kp, repos, "guard")
        assert g.returncode != 0 and word in g.stdout, (row, g.stdout)


def test_the_guard_allows_a_probe_kpoke_and_keeps_the_dangerous_forms_refused(repos):
    kp = scaffold(repos)
    t = kp / "tables/s0.txt"
    base = t.read_text()
    for row, ok in [("x|fit|safe|-|t4|probe --tri --kpoke 1:bg:N=1", True),
                    ("x|fit|safe|-|t4|probe --tri --kpoke=1:bg:N=1", True),
                    ("x|fit|safe|-|t4|tri --kpoke-render 1:bg:N=1", True),
                    ("x|fit|safe|-|t4|tri -n 2 --depth --refill 2:depth=0x3f000000", True),
                    ("x|fit|safe|-|t4|probe --scratch-pages 256 x.bin", True),
                    ("x|fit|safe|-|t4|fill --kpoke 0x1=2", False),
                    ("x|fit|safe|-|t4|tri --kpoke 0x1=2", False),
                    ("x|fit|safe|-|t4|probe --tri --kpoke 1:bg:N=1 --kreg 0x1=2", False),
                    ("x|fit|safe|-|t4|probe --tri --clkgate", False),
                    ("x|fit|safe|-|t4|probe --tri --trc-hazard", False)]:
        t.write_text(base + row + "\n")
        g = kit(kp, repos, "guard")
        assert (g.returncode == 0) == ok, (row, g.stdout)


FINAL_KNOB = 'render_final_pb_pages = { default = "0", values = ["0"] }\n'
FINAL_ROW = "f1|fit|safe|-|t4|tri -n 2 --geometry 1 --final-pb-pages 0x40\n"


def test_the_guard_wants_the_final_pb_knob_declared_for_a_row_that_writes_it(repos):
    """`tri --final-pb-pages N` writes debugfs render_final_pb_pages itself, which the kernel's
    next render context takes once: a row with it needs the knob in session.toml [knobs] at
    default 0, so the preflight checks the loaded module has the file and the exit trap puts
    the knob back should a tool die before its context took it."""
    kp = scaffold(repos)
    t = kp / "tables/s0.txt"
    t.write_text(t.read_text() + FINAL_ROW)
    g = kit(kp, repos, "guard")
    assert g.returncode != 0 and "render_final_pb_pages" in g.stdout, g.stdout
    toml = kp / "session.toml"
    toml.write_text(toml.read_text().replace(
        "[knobs]\n", '[knobs]\nrender_final_pb_pages = { default = "0x40", values = ["0x40"] }\n',
        1))
    g = kit(kp, repos, "guard")
    assert g.returncode != 0 and "render_final_pb_pages" in g.stdout, g.stdout
    kp = scaffold(repos, name="r8-u")
    t = kp / "tables/s0.txt"
    t.write_text(t.read_text() + FINAL_ROW)
    toml = kp / "session.toml"
    toml.write_text(toml.read_text().replace("[knobs]\n", "[knobs]\n" + FINAL_KNOB, 1))
    g = kit(kp, repos, "guard")
    assert g.returncode == 0, g.stdout


def same_value(a, b):
    lib = (KIT / "lib_kit.sh").read_text()
    fn = re.search(r"^same_value\(\).*?^}\n", lib, re.M | re.S).group(0)
    return subprocess.run(["bash", "-c", fn + 'same_value "$1" "$2"', "x", a, b]).returncode == 0


@pytest.mark.parametrize("a,b,eq", [
    ("Y", "1", True), ("y", "1", True), ("1", "Y", True), ("N", "0", True), ("n", "0", True),
    ("0", "N", True), ("Y", "Y", True), ("N", "N", True),
    ("Y", "0", False), ("N", "1", False), ("Y", "N", False), ("", "0", False),
    ("0x00000003", "3", True), ("0x00000003", "4", False), ("abc", "abc", True),
])
def test_a_knob_reads_back_by_value_a_bool_as_1_or_y_and_0_or_n(a, b, eq):
    assert same_value(a, b) == eq


def test_the_driver_bounds_every_command_and_names_the_host_key():
    src = (KIT / "session.py").read_text()
    calls = [m.start() for m in re.finditer(r"subprocess\.(run|Popen|call|check_output)\(",
                                            src)]
    assert len(calls) == 1, "every command goes through bounded()"
    assert "BatchMode=yes" in src and "HostKeyAlias=" in src and "ConnectTimeout=" in src


# ---- the mock: the staged tree under env -i, answered by argv -----------------------------------
def write_world(kp, body, expect):
    (kp / "mock/world.py").write_text(
        "import os\n" + f"EXPECT = {expect!r}\n" + body)


HEALTH = '''
def health(argv):
    if argv == ["fill"]:
        return dict(out="diff: 0 of 2048 pixels\\n")
    if argv == ["tri"]:
        return dict(out="diff: 0 of 4096 pixels\\n")
'''


def test_a_file_the_scorer_requires_that_no_job_writes_stops_the_runner(repos):
    kp = scaffold(repos)
    s = (kp / "score/score.py").read_text()
    (kp / "score/score.py").write_text(s.replace('".txt", "cases.tsv"',
                                                 '".txt", ".dump.bin", "cases.tsv"'))
    m = kit(kp, repos, "mock")
    assert m.returncode != 0
    assert re.search(r"^FAIL +world model: driver 23", m.stdout, re.M), m.stdout


def test_an_output_directory_is_made_only_when_declared(repos):
    kp = scaffold(repos)
    t = kp / "tables/s0.txt"
    t.write_text(t.read_text() + "d0|fit|safe|-|t4|fill --dump $W/dump/d.bin\n")
    with open(kp / "mock/world.py", "a") as f:
        f.write("\nDUMP_OPT = '--dump'\n")
    m = kit(kp, repos, "mock")
    assert m.returncode != 0 and "No such file" in m.stdout, m.stdout
    toml = (kp / "session.toml").read_text().replace("outdir_opts = []",
                                                    'outdir_opts = ["--dump"]')
    (kp / "session.toml").write_text(toml)
    m = kit(kp, repos, "mock")
    assert m.returncode == 0, m.stdout


def test_a_hook_that_calls_a_missing_command_fails_the_mock(repos):
    kp = scaffold(repos)
    with open(kp / "run/hooks.sh", "a") as f:
        f.write("hook_check() { num_eq 1 1; }\n")
    m = kit(kp, repos, "mock")
    assert m.returncode != 0 and "command not found" in m.stdout, m.stdout


def test_a_knob_is_restored_when_the_stage_stops(repos):
    kp = scaffold(repos)
    toml = (kp / "session.toml").read_text().replace(
        "[knobs]", '[knobs]\nrender_rgn_arrays = { default = "0", values = ["0", "1"] }')
    (kp / "session.toml").write_text(toml)
    t = kp / "tables/s0.txt"
    t.write_text(t.read_text() + "k1|fit|safe|dbg:render_rgn_arrays=1|t4|fill --fault\n")
    w = (kp / "mock/world.py").read_text()
    w = w.replace('EXPECT = {', 'EXPECT = {"fault": (4, {"s0": 4}), ')
    w += ('\n\ndef _fault(argv, world):\n'
          '    if "--fault" in argv and "fault" in world:\n'
          '        return dict(rc=3, out="job: failed\\n", kmsg=["sgxfive: BIF fault 0x90004 '
          'at 0x10000016 stalls job 9"], latch=(4, 0x10000016))\n')
    w = w.replace("def answer(tool, argv, world):\n",
                  "def answer(tool, argv, world):\n    f = _fault(argv, world)\n"
                  "    if f:\n        return f\n")
    (kp / "mock/world.py").write_text(w)
    m = kit(kp, repos, "mock")
    assert m.returncode == 0, m.stdout
    assert re.search(r"^ok +world fault: driver 4", m.stdout, re.M), m.stdout
    assert "knobs back at their defaults" in m.stdout


def test_the_mock_waits_on_no_clock():
    """r5-events' fake laptop had 16 ms to start a fill and failed on a loaded Mac: every sleep of
    the laptop runner is a *_WAIT the mock sets to 0 (or the tee's grace, which fires only if tee
    hangs), and the fake commands answer synchronously."""
    for f in ("lib_kit.sh", "run_stage.sh"):
        for ln in (KIT / f).read_text().splitlines():
            if re.search(r"(^|[;(\s])sleep ", ln) and not ln.lstrip().startswith("#"):
                assert re.search(r'sleep "\$\{(RESET_WAIT|HEALTH_WAIT|TEE_GRACE):-[0-9]+\}"'
                                 r'|sleep "\$\{IDLE_WAIT:-\$idle\}"', ln), ln
    src = (KIT / "session.py").read_text()
    assert 'RESET_WAIT="0"' in src and 'HEALTH_WAIT="0"' in src
    for f in (KIT / "fake").iterdir():
        assert "sleep" not in f.read_text(), f.name


def test_every_command_the_readme_gives_names_its_interpreter_and_runs_at_mode_644(repos):
    """r7-geo's run/stage_g.sh had mode 644: the lead's `run/stage_g.sh` got "permission
    denied", nothing was staged and the first stage exited 127 on the laptop. The kit runs its
    scripts through their interpreter, the guard refuses a README command that leans on the
    exec bit, and the documented offline command passes with every file at mode 644."""
    kp = scaffold(repos)
    for p in kp.rglob("*"):
        if p.is_file():
            p.chmod(0o644)
    cmds = re.findall(r"`((?:bash|python3|kit/|tests/|run/)[^`]*)`", (kp / "README.md").read_text())
    assert cmds and all(c.startswith(("bash ", "python3 ")) for c in cmds), cmds
    r = subprocess.run(["bash", "tests/run_all.sh"], cwd=kp, capture_output=True, text=True,
                       env=dict(env_for(repos), PY=PY), timeout=600)
    assert r.returncode == 0 and "RUN_ALL PASSED" in r.stdout, r.stdout + r.stderr
    with open(kp / "README.md", "a") as f:
        f.write("\nThen `kit/session.py run .` again.\n")
    g = kit(kp, repos, "guard")
    assert g.returncode != 0 and "README.md" in g.stdout and "interpreter" in g.stdout, g.stdout


def test_a_scaffolded_sessions_run_all_leaves_no_cache_directory(repos):
    """Builders cannot delete a __pycache__ or .pytest_cache inside a scratch session and folds
    must exclude them: run_all.sh and the kit write no bytecode and no pytest cache, even when
    the caller's environment would allow them."""
    kp = scaffold(repos)
    env = {k: v for k, v in dict(env_for(repos), PY=PY).items() if k != "PYTHONDONTWRITEBYTECODE"}
    r = subprocess.run(["bash", "tests/run_all.sh"], cwd=kp, capture_output=True, text=True,
                       env=env, timeout=600)
    assert r.returncode == 0 and "RUN_ALL PASSED" in r.stdout, r.stdout + r.stderr
    assert "PYTHONDONTWRITEBYTECODE=1" in (kp / "tests/run_all.sh").read_text()
    left = [str(p.relative_to(kp)) for p in kp.rglob("*")
            if p.name in ("__pycache__", ".pytest_cache") or p.suffix == ".pyc"]
    assert left == [], left


def test_a_hook_keeps_its_count_across_rows(repos):
    """r7-geo's needhash: the SECOND row without a hash stops the stage, so hook_check runs in
    the runner's shell (a count survives from row to row), and its reason stops the stage with
    24, after which the driver goes on (the session's status stays 0)."""
    kp = scaffold(repos)
    with open(kp / "run/hooks.sh", "a") as f:
        f.write('NSEEN=0\nhook_check() { NSEEN=$((NSEEN + 1)); [ "$NSEEN" -lt 2 ] '
                '|| echo "the second row"; return 0; }\n')
    w = (kp / "mock/world.py").read_text()
    (kp / "mock/world.py").write_text(w.replace(
        'EXPECT = {"model": (0, {"s0": 0}), "nodiff": (25, {"s0": 25})}',
        'EXPECT = {"model": (0, {"s0": 24})}'))
    m = kit(kp, repos, "mock")
    assert m.returncode == 0, m.stdout
    assert re.search(r"^ok +world model: driver 0 \(s0 24\)", m.stdout, re.M), m.stdout


# ---- expected outcomes: a declared end of a job that is not rc 0 ---------------------------
OVERFLOW = ("job: failed: scene overflowed the parameter buffer, context kept (No space left on "
            "device)\n")


def overflow_world(kp, expect):
    """A world whose `probe` cells end as the real DPM cells do: rc 3 with the overflow line
    (world `model`), or rc 3 with another failure (world `other`)."""
    w = (kp / "mock/world.py").read_text()
    w = w.replace('EXPECT = {"model": (0, {"s0": 0}), "nodiff": (25, {"s0": 25})}',
                  f"EXPECT = {expect!r}")
    w = w.replace("def answer(tool, argv, world):\n",
                  "def answer(tool, argv, world):\n"
                  "    if argv[:1] == ['probe']:\n"
                  "        if 'other' in world:\n"
                  "            return dict(rc=3, out='job: failed: cancelled\\n')\n"
                  f"        return dict(rc=3, out={OVERFLOW!r})\n")
    (kp / "mock/world.py").write_text(w)


def test_a_declared_overflow_is_a_completed_job_for_the_runner_and_the_scorer(repos):
    """r8-ldpm's `probe` DPM cells end rc 3 "scene overflowed the parameter buffer": the normal
    end of the cell, which R7-dpm's own runner accepted and the kit's classifier called a
    failure (rc 4, the stage stopped). A row that declares `expect:rc3-overflow` takes it as a
    completed job (class ok, kept in cases.tsv, kitscore.completed); any other rc 3 still stops
    the stage, and so does the overflow on a row that does not declare it."""
    kp = scaffold(repos)
    t = kp / "tables/s0.txt"
    base, world = t.read_text(), (kp / "mock/world.py").read_text()
    t.write_text(base + "o1|fit|safe|expect:rc3-overflow|t4|probe --tri pixel\n")
    overflow_world(kp, {"model": (0, {"s0": 0}), "other": (4, {"s0": 4})})
    g = kit(kp, repos, "guard")
    assert g.returncode == 0, g.stdout
    m = kit(kp, repos, "mock")
    assert m.returncode == 0, m.stdout + m.stderr
    assert re.search(r"^ok +world model: driver 0 \(s0 0\)", m.stdout, re.M), m.stdout
    assert re.search(r"^ok +world other: driver 4 \(s0 4\)", m.stdout, re.M), m.stdout
    kept = next(kp.glob("debug/mock.*/model/out/model/s0"))
    sys.path.insert(0, str(kp / "kit"))
    import kitscore
    row = kitscore.rows(str(kept))["o1"]
    assert (row["rc"], row["class"]) == (3, "ok")
    assert kitscore.completed(row)
    assert not kitscore.completed(dict(row, knobs="-"))
    assert not kitscore.completed(dict(row, rc=4))
    t.write_text(base + "o1|fit|safe|-|t4|probe --tri pixel\n")
    (kp / "mock/world.py").write_text(world)
    overflow_world(kp, {"model": (4, {"s0": 4})})
    m = kit(kp, repos, "mock")
    assert m.returncode == 0, m.stdout + m.stderr


OVERFLOW0 = "tri: 0 of 1 renders ok, 1 overflowed\n"


def overflow0_world(kp, expect):
    """A world whose `tri` rows end rc 0 with --keep-overflow's summary (world `model`), or rc 0
    with a render that did not overflow (world `other`)."""
    w = (kp / "mock/world.py").read_text()
    w = w.replace('EXPECT = {"model": (0, {"s0": 0}), "nodiff": (25, {"s0": 25})}',
                  f"EXPECT = {expect!r}")
    w = w.replace("def answer(tool, argv, world):\n",
                  "def answer(tool, argv, world):\n"
                  "    if argv[:1] == ['tri'] and '--keep-overflow' in argv:\n"
                  "        if 'other' in world:\n"
                  "            return dict(rc=0, out='tri: 1 renders ok\\n')\n"
                  f"        return dict(rc=0, out={OVERFLOW0!r})\n")
    (kp / "mock/world.py").write_text(w)


def test_a_declared_rc0_overflow_needs_the_overflow_the_row_declares(repos):
    """Q024's many-small-triangles renders end rc 0 whether or not the scene overflowed the
    parameter buffer (`tri --keep-overflow` counts it and goes on). A row that declares
    `expect:rc0-overflow` is a completed job only when the summary says `N overflowed`; a render
    that did not overflow (rc 0, no such line) is a failure that stops the stage, as the
    premise of the row is gone. A row without the knob takes either end."""
    kp = scaffold(repos)
    t = kp / "tables/s0.txt"
    base, world = t.read_text(), (kp / "mock/world.py").read_text()
    t.write_text(base + "o1|fit|safe|expect:rc0-overflow|t4|tri --keep-overflow\n")
    overflow0_world(kp, {"model": (0, {"s0": 0}), "other": (4, {"s0": 4})})
    g = kit(kp, repos, "guard")
    assert g.returncode == 0, g.stdout
    m = kit(kp, repos, "mock")
    assert m.returncode == 0, m.stdout + m.stderr
    assert re.search(r"^ok +world model: driver 0 \(s0 0\)", m.stdout, re.M), m.stdout
    assert re.search(r"^ok +world other: driver 4 \(s0 4\)", m.stdout, re.M), m.stdout
    kept = next(kp.glob("debug/mock.*/model/out/model/s0"))
    sys.path.insert(0, str(kp / "kit"))
    import kitscore
    row = kitscore.rows(str(kept))["o1"]
    assert (row["rc"], row["class"]) == (0, "ok") and kitscore.completed(row)
    t.write_text(base + "o1|fit|safe|-|t4|tri --keep-overflow\n")
    (kp / "mock/world.py").write_text(world)
    overflow0_world(kp, {"model": (0, {"s0": 0}), "other": (0, {"s0": 0})})
    m = kit(kp, repos, "mock")
    assert m.returncode == 0, m.stdout + m.stderr


def test_the_replay_of_an_rc0_overflow_row_needs_the_overflow(repos):
    kp = scaffold(repos)
    bind_source(repos, kp, src=REPLAY_SRC)
    base = (kp / "tables/s0.txt").read_text()
    m, bad = replay_findings(repos, kp, base,
                             "o1|fit|safe|expect:rc0-overflow|t4|tri --overflow0\n")
    assert not bad, (bad, m.stdout)
    m, bad = replay_findings(repos, kp, base,
                             "o2|fit|safe|expect:rc0-overflow|t4|tri --fine\n")
    assert len(bad) == 1 and "tables/s0.txt o2" in bad[0] and "did not overflow" in bad[0], \
        (bad, m.stdout)


def test_an_unknown_expected_outcome_is_refused(repos):
    kp = scaffold(repos)
    t = kp / "tables/s0.txt"
    t.write_text(t.read_text() + "o1|fit|safe|expect:rc5-anything|t4|probe\n")
    g = kit(kp, repos, "guard")
    assert g.returncode != 0 and "expect:rc5-anything" in g.stdout, g.stdout


def test_the_runner_and_kitscore_know_the_same_outcomes():
    sys.path.insert(0, str(KIT))
    import kitscore
    run = (KIT / "run_stage.sh").read_text()
    lib = (KIT / "lib_kit.sh").read_text()
    for name, (rc, line) in kitscore.OUTCOMES.items():
        assert f"expect:{name}" in run and f'{name}) [ "$rc" -eq {rc} ] && grep -q "{line}"' in lib
        assert S.BASE_KNOBS.match(f"expect:{name}")
    assert not S.BASE_KNOBS.match("expect:rc5-anything")


# ---- a tool run under regtimeline: a wrapper tool -----------------------------------------
RT_SHA = "d" * 64


def rt_session(repos, row):
    kp = scaffold(repos, extra=("--tool", f"rt=regtimeline:{RT_SHA}"))
    toml = (kp / "session.toml").read_text().replace(
        f'[tools.rt]\npath = "regtimeline"\nsha256 = "{RT_SHA}"\n',
        f'[tools.rt]\npath = "regtimeline"\nsha256 = "{RT_SHA}"\nwraps = true\n')
    assert "wraps = true" in toml
    (kp / "session.toml").write_text(toml)
    t = kp / "tables/s0.txt"
    t.write_text(t.read_text() + row + "\n")
    return kp


def test_a_tool_run_under_regtimeline_is_mocked_with_its_timeline(repos):
    """r8-ldpm runs `probe` under regtimeline (`rt`, args `0 LEAD REGS -- "$HOME/TOOL" ...`):
    the kit's mock runs the wrapped tool's fake (the world answers it as the tool it is) and
    prints a timeline after its output, with the wrapped tool's status, as regtimeline does; the
    declared overflow holds through the wrapper."""
    kp = rt_session(repos, 'o1|fit|safe|expect:rc3-overflow|rt|0 1 0x0c04,0x0700-0x0708 -- '
                           '"$HOME/sgxfive-test-rgn4" probe --tri pixel')
    overflow_world(kp, {"model": (0, {"s0": 0}), "other": (4, {"s0": 4})})
    g = kit(kp, repos, "guard")
    assert g.returncode == 0, g.stdout
    m = kit(kp, repos, "mock")
    assert m.returncode == 0, m.stdout + m.stderr
    kept = next(kp.glob("debug/mock.*/model/out/model/s0"))
    sys.path.insert(0, str(kp / "kit"))
    import kitscore
    out = kitscore.text(str(kept), "o1.txt")
    assert out.startswith(OVERFLOW), out
    assert re.search(r"^timeline: regs 0x0c04 0x0700 0x0704 0x0708 samples \d+ .* rc 3$", out,
                     re.M), out
    assert re.search(r"^tl \d+( [0-9a-f]{8}){4}$", out, re.M), out


def _fake_tool():
    spec = importlib.util.spec_from_file_location("fake_tool", KIT / "fake/tool.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.parametrize("nregs, ns", [(1, 541), (4, 1450), (27, 9000)])
def test_the_fake_regtimeline_spaces_its_samples_as_the_laptop_does(nregs, ns):
    """r31-cc and r32-misc: an m2-style control that premises `ivl` (the mean sample spacing,
    seconds / samples) failed on the mock, whose timeline said 0 seconds. The fake's header now
    carries the laptop's measured spacing (E1120, E1122: ~541 ns for 1 register, ~1.45 us for 4,
    ~9 us for 27), so a correct session's controls pass on the mock."""
    tool = _fake_tool()
    assert abs(tool.interval_ns(nregs) - ns) < 1
    assert tool.interval_ns(2) < tool.interval_ns(3) < tool.interval_ns(40)


def test_a_world_may_set_the_fake_regtimeline_spacing_and_the_header_follows(capsys, monkeypatch):
    tool = _fake_tool()

    class World:
        @staticmethod
        def interval_ns(*a):
            return 2000

    monkeypatch.setattr(subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(a, 0))
    for world, want in ((World, 2000), (object, tool.interval_ns(2))):
        tool.wrap(world, "rt", ["1.5", "0.5", "0x0804,0x0b14", "--", "x"], "model")
        head = capsys.readouterr().out.splitlines()[0]
        m = re.search(r"samples (\d+) seconds ([\d.]+) ", head)
        assert m, head
        ivl = float(m.group(2)) * 1e9 / int(m.group(1))
        assert abs(ivl - want) / want < 0.01, (head, ivl)


def test_a_mocked_timeline_header_gives_the_laptops_spacing_for_its_register_count(repos):
    """End to end through the kit's mock: 4 registers give an ivl near the laptop's 1.45 us."""
    kp = rt_session(repos, 'o1|fit|safe|expect:rc3-overflow|rt|1.5 0.5 0x0c04,0x0700-0x0708 -- '
                           '"$HOME/sgxfive-test-rgn4" probe --tri pixel')
    overflow_world(kp, {"model": (0, {"s0": 0}), "other": (4, {"s0": 4})})
    m = kit(kp, repos, "mock")
    assert m.returncode == 0, m.stdout + m.stderr
    kept = next(kp.glob("debug/mock.*/model/out/model/s0"))
    sys.path.insert(0, str(kp / "kit"))
    import kitscore
    out = kitscore.text(str(kept), "o1.txt")
    h = re.search(r"^timeline: .* samples (\d+) seconds ([\d.]+) ", out, re.M)
    assert h, out
    assert 1300 < float(h.group(2)) * 1e9 / int(h.group(1)) < 1600, h.group(0)


def test_the_guard_refuses_a_wrapped_command_that_is_not_a_pinned_tool(repos):
    """The preflight checks the sha256 of the tools of session.toml only, so the command a
    wrapper runs must be one of them, named by its laptop path."""
    cases = [('0 1 0x0c04 -- "$HOME/other-tool" probe', "$HOME/other-tool"),
             ("0 1 0x0c04 -- probe", "--"),
             ('0 1 0x0c04 "$HOME/sgxfive-test-rgn4" probe', "--"),
             ('0 1 0x0c04 -- "$HOME/regtimeline" probe', "wrapper")]
    for i, (args, word) in enumerate(cases):
        kp = rt_session(dict(repos, tmp=repos["tmp"] / f"w{i}"),
                        f"o1|fit|safe|-|rt|{args}")
        g = kit(kp, repos, "guard")
        assert g.returncode != 0 and word in g.stdout, (args, g.stdout)
    kp = rt_session(dict(repos, tmp=repos["tmp"] / "plain"),
                    'o1|fit|safe|-|t4|probe "$HOME/other-tool"')
    g = kit(kp, repos, "guard")
    assert g.returncode != 0 and "$HOME/other-tool" in g.stdout, g.stdout


# ---- expectdiff: a reading only when the job ran ---------------------------------------------
def diff_world(kp, expect):
    """A world whose `fill --odd` job ends rc 1 with a diff line: `job: ok` (world `model`) or
    `job: rejected` (world `rejected`, as the real tool prints a kernel refusal and still compares
    the untouched target)."""
    w = (kp / "mock/world.py").read_text()
    w = w.replace('EXPECT = {"model": (0, {"s0": 0}), "nodiff": (25, {"s0": 25})}',
                  f"EXPECT = {expect!r}")
    w = w.replace("def answer(tool, argv, world):\n",
                  "def answer(tool, argv, world):\n"
                  "    if '--odd' in argv:\n"
                  "        job = 'job: rejected (Invalid argument)' if 'rejected' in world "
                  "else 'job: ok'\n"
                  "        return dict(rc=1, out=job + '\\ndiff: 7 of 2048 pixels\\n')\n")
    (kp / "mock/world.py").write_text(w)


def test_an_expectdiff_row_is_a_reading_only_when_the_job_ran(repos):
    """r8-geo's E934: `job: rejected` with a diff line under expectdiff was taken as a reading,
    and 23 rows were refusals. An expectdiff row is a reading when it ends rc 1 with the tool's
    `job: ok` and a diff line; a rejected job is a failure that stops the stage."""
    kp = scaffold(repos)
    t = kp / "tables/s0.txt"
    t.write_text(t.read_text() + "d1|fit|safe|expectdiff|t4|fill --odd\n")
    diff_world(kp, {"model": (0, {"s0": 0}), "rejected": (4, {"s0": 4})})
    m = kit(kp, repos, "mock")
    assert m.returncode == 0, m.stdout + m.stderr
    assert re.search(r"^ok +world rejected: driver 4 \(s0 4\)", m.stdout, re.M), m.stdout
    kept = next(kp.glob("debug/mock.*/model/out/model/s0"))
    sys.path.insert(0, str(kp / "kit"))
    import kitscore
    assert kitscore.rows(str(kept))["d1"]["class"] == "ok"


def test_an_expectdiff_reading_is_a_completed_job(repos):
    """r8-ldpm's k calibrations (expectdiff rows that ended rc 1 with `job: ok` and a diff line)
    were read as cannot tell: kitscore.completed takes them as completed jobs, and only them."""
    kp = scaffold(repos)
    t = kp / "tables/s0.txt"
    t.write_text(t.read_text() + "d1|fit|safe|expectdiff|t4|fill --odd\n")
    diff_world(kp, {"model": (0, {"s0": 0})})
    m = kit(kp, repos, "mock")
    assert m.returncode == 0, m.stdout + m.stderr
    kept = next(kp.glob("debug/mock.*/model/out/model/s0"))
    sys.path.insert(0, str(kp / "kit"))
    import kitscore
    row = kitscore.rows(str(kept))["d1"]
    assert (row["rc"], row["class"]) == (1, "ok")
    assert kitscore.completed(row)
    assert not kitscore.completed(dict(row, knobs="-"))
    assert not kitscore.completed(dict(row, rc=2))
    assert not kitscore.completed(dict(row, **{"class": "fail"}))


# ---- the laptop's host key: SGX_TARGET_HOST_KEY_ALIAS or the older SGX_TARGET_SSH_OPTS -------
def opts_with(c, **env):
    S.ENV = {k: v for k, v in os.environ.items()
             if k not in ("SGX_TARGET_HOST_KEY_ALIAS", "SGX_TARGET_SSH_OPTS")} | env
    try:
        return S.ssh_opts(c)
    finally:
        S.ENV = None


def alias_of(opts):
    return [o.split("=", 1)[1] for o in opts if o.startswith("HostKeyAlias=")][0]


def test_the_host_key_alias_comes_from_either_variable():
    """The lead's environment named the laptop's host key in SGX_TARGET_SSH_OPTS (the bringup
    tools' variable) and the kit read only SGX_TARGET_HOST_KEY_ALIAS: r8-geo's first staging
    used session.toml's alias and ssh exited 255. The kit takes SGX_TARGET_SSH_OPTS's options
    too; ssh keeps the first HostKeyAlias it is given, so the alias variable comes first, the
    options' own alias next, session.toml's last and only when neither names one."""
    c = {"host_key_alias": "sgx-target"}
    assert alias_of(opts_with(c)) == "sgx-target"
    o = opts_with(c, SGX_TARGET_SSH_OPTS="-o HostKeyAlias=box -o Port=2222")
    assert alias_of(o) == "box" and "Port=2222" in o and "HostKeyAlias=sgx-target" not in o
    o = opts_with(c, SGX_TARGET_HOST_KEY_ALIAS="cedar",
                  SGX_TARGET_SSH_OPTS="-o HostKeyAlias=box")
    assert alias_of(o) == "cedar"
    o = opts_with(c, SGX_TARGET_SSH_OPTS="-o Port=2222")
    assert alias_of(o) == "sgx-target" and "Port=2222" in o
    assert opts_with(c, SGX_TARGET_SSH_OPTS="-o BatchMode=no")[:2] == ["-o", "BatchMode=yes"]


def test_a_staging_that_ssh_refuses_names_the_variables(repos):
    """ssh's 255 (a host key it does not know, an unreachable host) stops the staging with its
    own message and the variables that choose the host and its key, never silently."""
    kp = frozen_session(repos)
    S.ENV = dict(env_for(repos), SGX_TARGET_HOST="u@laptop")
    S.ENV.pop("SGX_TARGET_HOST_KEY_ALIAS", None)
    S.ENV.pop("SGX_TARGET_SSH_OPTS", None)
    S.SSH = [PY, "-c", "import sys; sys.stderr.write('Host key verification failed.\\n'); "
                       "sys.exit(255)"]
    try:
        with pytest.raises(S.Stop) as e:
            S.stage(kp, say=lambda *a: None)
    finally:
        S.ENV, S.SSH = None, ["ssh"]
    msg = str(e.value)
    for word in ("255", "Host key verification failed", "SGX_TARGET_HOST", "u@laptop",
                 "SGX_TARGET_HOST_KEY_ALIAS", "SGX_TARGET_SSH_OPTS", "sgx-target"):
        assert word in msg, (word, msg)


# ---- the library mock: every row's argv through the tool's own source ----------------------
FAKE_SRC = """#!/bin/sh
[ "$1" = --mock ] || { echo "usage: not the library mock" >&2; exit 2; }
shift
case "$*" in *--refused*) echo "job: rejected (Invalid argument)"; echo "diff: 9 of 2048 pixels"
    exit 1 ;; esac
case "$1" in fill|tri) echo "job: ok"; echo "diff: 0 of 2048 pixels" ;;
    *) echo "usage: sgxfive-test COMMAND" >&2; exit 2 ;; esac
"""
FAKE_MAKE = ("build/sgxfive-test: tools/sgxfive-test.c\n"
             "\tmkdir -p build && cp tools/sgxfive-test.c build/sgxfive-test "
             "&& chmod +x build/sgxfive-test\n")
SRC_PATH = "userspace/libsgxfive/tools/sgxfive-test.c"


def bind_source(repos, kp, src=FAKE_SRC, sha=None):
    """The tool's source at a commit of the fake resgx545 (a script its Makefile copies, which
    answers as the library mock does), bound in session.toml [tools.t4]."""
    main = repos["main"]
    (main / "userspace/libsgxfive/tools").mkdir(parents=True, exist_ok=True)
    (main / "include/uapi").mkdir(parents=True, exist_ok=True)
    (main / SRC_PATH).write_text(src)
    (main / "userspace/libsgxfive/Makefile").write_text(FAKE_MAKE)
    (main / "include/uapi/sgxfive.h").write_text("/* uapi */\n")
    c2 = commit_all(main, "tool")
    sha = sha or hashlib.sha256(src.encode()).hexdigest()
    toml = (kp / "session.toml").read_text().replace(
        f'[tools.t4]\npath = "sgxfive-test-rgn4"\nsha256 = "{TOOL_SHA}"\n',
        f'[tools.t4]\npath = "sgxfive-test-rgn4"\nsha256 = "{TOOL_SHA}"\n'
        f'source = "{c2}:{SRC_PATH}"\nsource_sha256 = "{sha}"\n')
    assert "source_sha256" in toml
    (kp / "session.toml").write_text(toml)
    return c2


def test_the_mock_replays_every_row_on_the_library_mock_and_stops_on_a_refusal(repos):
    """r8-geo lost 23 rows to `job: rejected`: its mock's world answered them `job: ok`, so the
    dry run passed. With the tool's source bound in session.toml (`source`, `source_sha256`) the
    mock builds the library mock from that commit (never the working tree) and runs every row's
    argv through it first; a `job: rejected` or a usage refusal stops the mock before any world
    runs, naming the row."""
    kp = scaffold(repos)
    bind_source(repos, kp)
    assert kit(kp, repos, "guard").returncode == 0
    m = kit(kp, repos, "mock")
    assert m.returncode == 0, m.stdout + m.stderr
    assert re.search(r"^ok +libmock: 2 rows of t4 replayed", m.stdout, re.M), m.stdout
    t = kp / "tables/s0.txt"
    base = t.read_text()
    for row, word in [("r1|fit|safe|-|t4|fill --refused", "job: rejected"),
                      ("r1|fit|safe|-|t4|bogus", "usage")]:
        t.write_text(base + row + "\n")
        m = kit(kp, repos, "mock")
        assert m.returncode != 0, m.stdout
        assert re.search(rf"^FAIL libmock: tables/s0.txt r1: .*{word}", m.stdout, re.M), m.stdout
        assert "world model" not in m.stdout, m.stdout


KNOB_SRC = """#!/bin/sh
[ "$1" = --mock ] || { echo "usage: sgxfive-test [--mock [--mock-knob NAME=V]...] COMMAND" >&2
    exit 2; }
shift
bgl=0; src=0
while [ "$1" = --mock-knob ]; do
    case "$2" in render_bg_layer=1) bgl=1 ;; render_bg_src=0x*) src=1 ;; esac; shift 2; done
case " $* " in *" --bg-layer "*)
    [ $bgl = 1 ] && [ $src = 1 ] \\
        || { echo "usage: --bg-layer needs both knobs set" >&2; exit 2; } ;; esac
echo "job: ok"; echo "diff: 0 of 2048 pixels"
"""


def knob_session(repos, src):
    kp = scaffold(repos)
    toml = (kp / "session.toml").read_text().replace(
        "[knobs]\n", '[knobs]\nrender_bg_layer = { default = "0", values = ["0", "1"] }\n'
        'render_bg_src = { default = "0x0", values = ["0x0", "0x3e800000"] }\n', 1)
    (kp / "session.toml").write_text(toml)
    bind_source(repos, kp, src=src)
    return kp


def test_the_library_mock_replays_a_row_with_the_knob_state_its_dbg_words_set(repos):
    """E934's twin: a row whose premise needs a debugfs knob replayed `job: ok` with no knob
    state. A library mock that lists --mock-knob gets each of the row's `dbg:NAME=V` words as
    `--mock-knob NAME=V`; a row with the wrong knob state is then the tool's refusal, a finding."""
    kp = knob_session(repos, KNOB_SRC)
    t = kp / "tables/s0.txt"
    base = t.read_text()
    both = "dbg:render_bg_layer=1 dbg:render_bg_src=0x3e800000"
    t.write_text(base + f"k1|fit|safe|{both}|t4|fill --bg-layer\n")
    m = kit(kp, repos, "mock")
    assert m.returncode == 0, m.stdout + m.stderr
    for words in ("-", "dbg:render_bg_layer=1", "dbg:render_bg_src=0x3e800000"):
        t.write_text(base + f"k2|fit|safe|{words}|t4|fill --bg-layer\n")
        m = kit(kp, repos, "mock")
        assert m.returncode != 0, (words, m.stdout)
        assert re.search(r"^FAIL libmock: tables/s0.txt k2: .*both knobs", m.stdout, re.M), \
            m.stdout


REPLAY_SRC = """#!/bin/sh
[ "$1" = --mock ] || { echo "usage: not the library mock" >&2; exit 2; }
shift
case "$*" in
*--kpoke-render*) [ -f "${SGXFIVE_KPOKE:-/nonexistent}" ] \\
    || { echo "sgxfive-test: kpoke: No such file or directory" >&2; exit 1; } ;;
*--probefail*) echo "probe p: failed: program at 0x1: Invalid argument"; exit 0 ;;
*--silent1*) exit 1 ;;
*--overflow0*) echo "tri: 0 of 1 renders ok, 1 overflowed"; exit 0 ;;
*--overflow*) echo "job: failed: scene overflowed the parameter buffer, context kept"; exit 3 ;;
esac
echo "job: ok"; echo "diff: 0 of 2048 pixels"
"""


def replay_findings(repos, kp, base, rows):
    (kp / "tables/s0.txt").write_text(base + rows)
    m = kit(kp, repos, "mock")
    return m, re.findall(r"^FAIL libmock: (.*)$", m.stdout, re.M)


def test_the_replay_has_a_kpoke_file_and_counts_every_unexpected_end_as_a_refusal(repos):
    """round 10's x session: the replay ran without SGXFIVE_KPOKE, so every `--depth` tri row ended
    `kpoke: No such file` (rc 1) and the replay still said none was refused. It now has a kpoke
    file as the real runner does, and any rc other than 0, or a `failed:` or `rejected` line, is
    a refusal; a declared `expect:NAME` end is not."""
    kp = scaffold(repos)
    bind_source(repos, kp, src=REPLAY_SRC)
    base = (kp / "tables/s0.txt").read_text()
    m, bad = replay_findings(repos, kp, base, "k1|fit|safe|-|t4|tri --kpoke-render 1:rd:1=2\n")
    assert not bad, (bad, m.stdout)
    assert re.search(r"^ok +libmock: 3 rows of t4 replayed", m.stdout, re.M), m.stdout
    for arg, word in [("--silent1", "status 1"), ("--probefail", "failed:")]:
        m, bad = replay_findings(repos, kp, base, f"x1|fit|safe|-|t4|tri {arg}\n")
        assert m.returncode != 0 and len(bad) == 1 and "tables/s0.txt x1" in bad[0] \
            and word in bad[0], (arg, bad, m.stdout)
    m, bad = replay_findings(repos, kp, base,
                             "o1|fit|safe|expect:rc3-overflow|t4|probe --overflow\n")
    assert not bad, (bad, m.stdout)
    m, bad = replay_findings(repos, kp, base, "o2|fit|safe|-|t4|probe --overflow\n")
    assert len(bad) == 1 and "status 3" in bad[0], (bad, m.stdout)


FINAL_SRC = """#!/bin/sh
[ "$1" = --mock ] || { echo "usage: not the library mock" >&2; exit 2; }
shift
case "$*" in
*--final-pb-pages*) [ -f "${SGXFIVE_DEBUGFS:-/nonexistent}/render_final_pb_pages" ] \\
    && printf 0x40 > "$SGXFIVE_DEBUGFS/render_final_pb_pages" \\
    || { echo "sgxfive-test: render_final_pb_pages: No such file or directory" >&2; exit 1; } ;;
esac
echo "job: ok"; echo "diff: 0 of 2048 pixels"
"""


def test_the_replay_has_the_declared_knob_files_for_a_tool_that_writes_one(repos):
    """The tool writes debugfs render_final_pb_pages itself (tri --final-pb-pages), which needs
    the file: the replay's debugfs directory holds every knob session.toml declares, at its
    default, beside the dumps; a knob's state still comes only from a row's dbg: words."""
    kp = scaffold(repos)
    bind_source(repos, kp, src=FINAL_SRC)
    toml = kp / "session.toml"
    toml.write_text(toml.read_text().replace("[knobs]\n", "[knobs]\n" + FINAL_KNOB, 1))
    base = (kp / "tables/s0.txt").read_text()
    m, bad = replay_findings(repos, kp, base, FINAL_ROW)
    assert not bad, (bad, m.stdout)
    assert re.search(r"^ok +libmock: 3 rows of t4 replayed", m.stdout, re.M), m.stdout


FILL_SRC = """#!/bin/sh
[ "$1" = --mock ] || { echo "usage: not the library mock" >&2; exit 2; }
shift
case "$*" in
*--use-fill*) [ -f "${SGXFIVE_DEBUGFS:-/nonexistent}/tadata_fill" ] \\
    || { echo "sgxfive-test: tadata_fill: No such file or directory" >&2; exit 1; } ;;
esac
echo "job: ok"; echo "diff: 0 of 2048 pixels"
"""


def test_the_replay_creates_every_debugfs_file_the_session_declares_and_no_other(repos):
    """`tri --tadata-fill-render` needs debugfs tadata_fill, which session.toml declares in
    `debugfs = [...]` and the worlds' fake laptop creates; the replay made only the dumps and the
    knobs, so the row failed `tadata_fill: No such file`. It creates each declared file, empty;
    a file not declared stays absent, so an undeclared use still fails."""
    kp = scaffold(repos)
    bind_source(repos, kp, src=FILL_SRC)
    base = (kp / "tables/s0.txt").read_text()
    row = "d1|fit|safe|-|t4|tri --use-fill\n"
    m, bad = replay_findings(repos, kp, base, row)
    assert len(bad) == 1 and "tadata_fill" in bad[0], (bad, m.stdout)
    toml = kp / "session.toml"
    toml.write_text(toml.read_text().replace("debugfs = []", 'debugfs = ["tadata_fill"]', 1))
    m, bad = replay_findings(repos, kp, base, row)
    assert not bad, (bad, m.stdout)



LARGE_KNOBS = ('vm_pde_addr = { default = "0", values = ["0", "0x60000000"] }\n'
               'vm_pde_size = { default = "0", values = ["0", "3"] }\n'
               'vm_pde_layout = { default = "0", values = ["0", "1"] }\n')
LARGE_SRC = """#!/bin/sh
[ "$1" = --mock ] || { echo "usage: sgxfive-test [--mock [--mock-knob NAME=V]...] COMMAND" >&2
    exit 2; }
shift
addr=0; size=0
while [ "$1" = --mock-knob ]; do
    case "$2" in vm_pde_addr=*) addr=${2#*=} ;; vm_pde_size=*) size=${2#*=} ;; esac; shift 2; done
dir=$(printf '%s\\n' "$@" | sed -n '/^--large-copy$/{n;p;}')
[ -z "$dir" ] || { mkdir -p "$dir" && echo "mock: vm_large not modelled: vm_pde_addr $addr \\
vm_pde_size $size" > "$dir/vm_large.txt"; } || exit 1
[ -f "${SGXFIVE_DEBUGFS:-/nonexistent}/vm_large" ] || { echo "no vm_large" >&2; exit 1; }
echo "job: ok"; echo "diff: 0 of 4096 pixels"
"""


def test_a_large_page_row_replays_with_its_knobs_and_its_read_out(repos):
    """Q109's rows (the linux fork's debugfs vm_pde_*): the three knobs declared in [knobs] at
    default 0, debugfs vm_large in debugfs, --large-copy in outdir_opts. The guard takes them, the
    replay gives the tool the row's knob words and vm_large's file, and the read-out's directory
    is the tool's to make."""
    kp = scaffold(repos)
    bind_source(repos, kp, src=LARGE_SRC)
    toml = kp / "session.toml"
    toml.write_text(toml.read_text().replace("[knobs]\n", "[knobs]\n" + LARGE_KNOBS, 1)
                    .replace("debugfs = []", 'debugfs = ["vm_large"]', 1)
                    .replace("outdir_opts = []", 'outdir_opts = ["--large-copy"]', 1))
    row = ("l1|fit|safe|dbg:vm_pde_addr=0x60000000 dbg:vm_pde_size=3 dbg:vm_pde_layout=1|t4|"
           "copy --width 1024 --height 4 --src-addr 0x603fc000 --large-copy $W/large\n")
    g = kit(kp, repos, "guard")
    assert g.returncode == 0, g.stdout
    base = (kp / "tables/s0.txt").read_text()
    m, bad = replay_findings(repos, kp, base, row)
    assert not bad, (bad, m.stdout)
    assert re.search(r"^ok +libmock: 3 rows of t4 replayed", m.stdout, re.M), m.stdout


UNKNOWN_SRC = """#!/bin/sh
[ "$1" = --mock ] || { echo "usage: not the library mock" >&2; exit 2; }
shift
[ "$1" = probe ] || { echo "job: ok"; echo "diff: 0 of 2048 pixels"; exit 0; }
for a; do last=$a; done
n=$(basename "$last" .bin)
case "$*" in
*--usage*) echo "usage: sgxfive-test probe: --usage" >&2; exit 2 ;;
*--rejected*) echo "job: rejected (Invalid argument)"; exit 3 ;;
esac
echo "programs asm"
case "$*" in *--noscratch*) ;; *) echo "probe $n: scratch at 0x3e003000 (64 KiB)" ;; esac
case "$*" in
*--hung*) echo "probe $n: failed: job hung, context lost (Timer expired)" ;;
*) echo "probe $n: failed: job faulted, context lost (Input/output error)" ;;
esac
echo "probe $n: scratch unchanged"
exit 3
"""
# libsgxfive src/mock.c runs a fill's or a copy's program only when its qword 1 is a limm
# `mov o0, #imm` (a fill) or its own copy shader's instruction (a copy, probe --coords)
LIMM_MOV_Q = 0xfc << 56 | 1 << 53 | 0x1234
COPY_Q = 0x28851001 << 32 | 0xa0000000


def program_bins(kp):
    (kp / "bins").mkdir(exist_ok=True)
    for name, q1 in (("own", LIMM_MOV_Q), ("own0", 0x1), ("copy", COPY_Q)):
        (kp / "bins" / f"{name}.bin").write_bytes(
            (0x5).to_bytes(8, "little") + q1.to_bytes(8, "little") + bytes(8))
    toml = (kp / "session.toml").read_text()
    (kp / "session.toml").write_text(toml.replace("[files]\nlaptop = []",
                                                  '[files]\nlaptop = ["bins/*.bin"]'))


def test_the_replay_runs_a_probe_of_our_program_as_not_simulated_and_stays_strict(repos):
    """r13-tex and r13-flag named their probe fills t10p, a second name for t10 with no_source:
    libsgxfive's mock runs only its own copy and fill programs, so every probe of a program of
    ours faults there ("an unknown program") and 287031c's replay refused it. That end is now
    the expected end of such a row (a `probe` of program files the mock would not run), said as
    "program not simulated"; a usage refusal, `job: rejected`, another failure, a failure with
    no scratch line (the job never submitted), a program the mock would run, or a --tri probe
    still fail."""
    kp = scaffold(repos)
    bind_source(repos, kp, src=UNKNOWN_SRC)
    program_bins(kp)
    base = (kp / "tables/s0.txt").read_text()
    ok_rows = ('n1|fit|safe|-|t4|probe --temps 32 --coords --pixels "$S/bins/own.bin"\n'
               'n2|fit|safe|-|t4|probe --temps 32 "$S/bins/own0.bin"\n'
               'n3|fit|risky|expectfault|t4|probe --temps 32 --coords "$S/bins/own.bin"\n')
    m, bad = replay_findings(repos, kp, base, ok_rows)
    assert not bad, (bad, m.stdout)
    assert re.search(r"^ok +libmock: 5 rows of t4 replayed on \S+, none refused; 3 of them "
                     r"program not simulated", m.stdout, re.M), m.stdout
    assert re.search(r"^note libmock: program not simulated .*: tables/s0.txt n1, "
                     r"tables/s0.txt n2, tables/s0.txt n3$", m.stdout, re.M), m.stdout
    for row, word in [
            ('x1|fit|safe|-|t4|probe --usage --coords "$S/bins/own.bin"', "usage"),
            ('x1|fit|safe|-|t4|probe --rejected --coords "$S/bins/own.bin"', "job: rejected"),
            ('x1|fit|safe|-|t4|probe --hung --coords "$S/bins/own.bin"', "status 3"),
            ('x1|fit|safe|-|t4|probe --noscratch --coords "$S/bins/own.bin"', "status 3"),
            ('x1|fit|safe|-|t4|probe --coords "$S/bins/copy.bin"', "status 3"),
            ('x1|fit|safe|-|t4|probe --temps 32 "$S/bins/own.bin"', "status 3"),
            ('x1|fit|safe|-|t4|probe --tri pixel --coords "$S/bins/own.bin"', "status 3"),
            ('x1|fit|safe|-|t4|probe --coords --pixels', "status 3")]:
        m, bad = replay_findings(repos, kp, base, row + "\n")
        assert m.returncode != 0 and len(bad) == 1 and "tables/s0.txt x1" in bad[0] \
            and word in bad[0] and "not simulated" not in m.stdout, (row, bad, m.stdout)


PLACE_SRC = """#!/bin/sh
[ "$1" = --mock ] || { echo "usage: not the library mock" >&2; exit 2; }
shift
[ "$1" = probe ] || { echo "job: ok"; echo "diff: 0 of 2048 pixels"; exit 0; }
place=; prev=; q=
for a; do [ "$prev" = --place ] && place=${a#*=}; prev=$a; last=$a; done
n=$(basename "$last" .bin)
case "$*" in *--usage*) echo "usage: sgxfive-test probe: --usage" >&2; exit 2 ;; esac
echo "programs asm"
if [ -n "$place" ]; then
	q=$(od -An -v -t x8 -j 8 -N 8 "$place" | tr -d ' ')
	echo "probe $n: program placed at 0x3707fe00..0x370810c0 (3 pages), crosses code step 0x80000 at word 64"
	echo "probe $n: program placed at 0x3707fe00 (code heap base + 0x7fe00), started as EXE and CBASE: DOUTU bits 21:0 0x0ffc00"
fi
echo "probe $n: scratch at 0x3e003000 (64 KiB)"
case "$*" in *--hung*)
	echo "probe $n: failed: job hung, context lost (Timer expired)"
	exit 3 ;;
esac
case "$q" in fc[26ae]*)
	echo "probe $n: o0 0x00001234 (2048 of 2048)"
	echo "probe $n: placed words read back: 600 of 600 as built, hash 0xfe5a956d5e27d72e"
	exit 0 ;;
esac
echo "probe $n: failed: job faulted, context lost (Input/output error)"
echo "probe $n: scratch unchanged"
[ -n "$place" ] && echo "probe $n: placed words read back: 600 of 600 as built, hash 0x0a53a52fcf43f0a1"
exit 3
"""


def test_the_replay_runs_a_placed_program_of_ours_as_not_simulated(repos):
    """r23-pk's q123 rows: `probe --place OFFSET=FILE --place-form F BASE`, FILE a program of
    ours of more than 256 words (P1's --place takes up to 8192, across pages and code steps).
    The library mock starts the placed program in place of the fill shader, so it is FILE, not
    BASE, that the mock runs or not: a FILE the mock would not run (qword 1 not a limm mov) ends
    as its unknown program after the place lines and the scratch line, and is "program not
    simulated", the read-back line after the fault included; a FILE it runs ends ok. A usage
    refusal, another failure, or the fault of a FILE the mock would run still fail."""
    kp = scaffold(repos)
    bind_source(repos, kp, src=PLACE_SRC)
    program_bins(kp)
    (kp / "bins" / "long.bin").write_bytes((0x5).to_bytes(8, "little") +
                                           (0x1).to_bytes(8, "little") * 599)
    (kp / "bins" / "longmov.bin").write_bytes((0x5).to_bytes(8, "little") +
                                              LIMM_MOV_Q.to_bytes(8, "little") * 599)
    base = (kp / "tables/s0.txt").read_text()
    pl = 'probe --place 0x7fe00="$S/bins/{}.bin" --place-form cbase {}"$S/bins/{}.bin"'
    ok_rows = (f'p1|fit|safe|-|t4|{pl.format("long", "", "own")}\n'
               f'p2|fit|safe|-|t4|{pl.format("long", "--temps 32 ", "own0")}\n'
               f'p3|fit|safe|-|t4|{pl.format("longmov", "", "own")}\n')
    m, bad = replay_findings(repos, kp, base, ok_rows)
    assert not bad, (bad, m.stdout)
    assert re.search(r"^ok +libmock: 5 rows of t4 replayed on \S+, none refused; 2 of them "
                     r"program not simulated", m.stdout, re.M), m.stdout
    assert re.search(r"^note libmock: program not simulated .*: tables/s0.txt p1, "
                     r"tables/s0.txt p2$", m.stdout, re.M), m.stdout
    for row, word in [
            ('x1|fit|safe|-|t4|' + pl.format("long", "--usage ", "own"), "usage"),
            ('x1|fit|safe|-|t4|' + pl.format("long", "--hung ", "own"), "status 3"),
            ('x1|fit|safe|-|t4|' + pl.format("longmov", "--hung ", "own"), "status 3"),
            ('x1|fit|safe|-|t4|probe --tri pixel --place 0x7fe00="$S/bins/long.bin" '
             '--place-form cbase "$S/bins/own.bin"', "status 3")]:
        m, bad = replay_findings(repos, kp, base, row + "\n")
        assert m.returncode != 0 and len(bad) == 1 and "tables/s0.txt x1" in bad[0] \
            and word in bad[0] and "not simulated" not in m.stdout, (row, bad, m.stdout)


def test_a_library_mock_without_mock_knob_replays_as_before(repos):
    kp = knob_session(repos, FAKE_SRC)
    t = kp / "tables/s0.txt"
    t.write_text(t.read_text() + "k1|fit|safe|dbg:render_bg_layer=1|t4|fill\n")
    m = kit(kp, repos, "mock")
    assert m.returncode == 0, m.stdout + m.stderr


def test_the_library_mock_runs_the_tool_a_wrapper_runs(repos):
    kp = rt_session(repos, 'o1|fit|safe|-|rt|0 1 0x0c04 -- "$HOME/sgxfive-test-rgn4" fill '
                           '--refused')
    bind_source(repos, kp)
    m = kit(kp, repos, "mock")
    assert m.returncode != 0 and re.search(r"^FAIL libmock: tables/s0.txt o1: .*job: rejected",
                                           m.stdout, re.M), m.stdout


def test_the_library_mock_is_built_only_from_the_bound_source(repos):
    kp = scaffold(repos)
    bind_source(repos, kp, sha="0" * 64)
    m = kit(kp, repos, "mock")
    assert m.returncode != 0 and re.search(r"^FAIL libmock: .*not 0{12}", m.stdout, re.M), m.stdout
    toml = (kp / "session.toml").read_text().replace('source = "', 'source = "nocommit')
    (kp / "session.toml").write_text(toml)
    g = kit(kp, repos, "guard")
    assert g.returncode != 0 and "source" in g.stdout, g.stdout


def test_a_tool_without_a_source_or_a_reason_fails_the_guard_loudly(repos):
    """Round 8's sessions declared no `source`, so no row went through the library mock and the
    E934 fix did nothing for them, silently. A tool needs `source` (+ `source_sha256`) or a
    `no_source` reason of its own; a wrapper is the tool it wraps."""
    kp = scaffold(repos)
    m = kit(kp, repos, "mock")
    assert m.returncode == 0, m.stdout
    assert re.search(r"^note libmock: t4 has no source in session.toml \(a test fixture", m.stdout, re.M), \
        m.stdout
    toml = (kp / "session.toml").read_text()
    for bad in ("", 'no_source = "  "\n', 'no_source = "TODO"\n'):
        (kp / "session.toml").write_text(
            re.sub(r'no_source = ".*"\n', bad, toml))
        g = kit(kp, repos, "guard")
        assert g.returncode != 0 and re.search(r"tool t4: no `source`.*no_source", g.stdout), \
            (bad, g.stdout)
        assert kit(kp, repos, "mock").returncode != 0
        assert kit(kp, repos, "freeze").returncode != 0


def test_the_scaffold_demands_a_source_or_a_reason_for_every_tool(repos):
    kp = repos["tmp"] / "scratch" / "none"
    r = subprocess.run([PY, str(NEW), str(kp), "--name", "r8-t", "--prefix", "r8t",
                        "--srcversion", SRCV, "--tool", f"t4=sgxfive-test-rgn4:{TOOL_SHA}",
                        "--resgx545", str(repos["main"]), "--commit", repos["c1"],
                        "--data", str(repos["data"]), "--data-commit", repos["d1"]],
                       capture_output=True, text=True)
    assert r.returncode != 0 and "--tool-src or --no-source" in r.stdout and not kp.exists()


def test_tool_src_of_the_tool_source_declares_it_for_the_library_mock(repos):
    (repos["main"] / "userspace/libsgxfive/tools").mkdir(parents=True)
    (repos["main"] / SRC_PATH).write_text(FAKE_SRC)
    c2 = commit_all(repos["main"], "tool")
    kp = scaffold(repos, extra=("--tool-src", f"t4={c2}:{SRC_PATH}@tools/bringup/health.sh"))
    toml = (kp / "session.toml").read_text()
    sha = hashlib.sha256(FAKE_SRC.encode()).hexdigest()
    assert f'source = "{c2}:{SRC_PATH}"' in toml and f'source_sha256 = "{sha}"' in toml
    assert "no_source" not in toml
    assert kit(kp, repos, "guard").returncode == 0


# ---- #limit: the faults a control expects are not the stage's ------------------------------
def fault_limit_session(repos, iso_set):
    kp = scaffold(repos)
    t = kp / "tables/s0.txt"
    t.write_text(t.read_text().replace("#limit 0", "#limit 1")
                 + f"c1-iso|{iso_set}|safe|expectfault reads:diff|t4|fill --fault\n"
                 + "f1-fill|fit|safe|-|t4|fill --width 32 --height 32\n")
    w = (kp / "mock/world.py").read_text()
    w = w.replace("def answer(tool, argv, world):\n",
                  "def answer(tool, argv, world):\n"
                  "    if '--fault' in argv:\n"
                  "        return dict(rc=3, out='job: failed\\ndiff: 0 of 2048 pixels\\n', "
                  "kmsg=['sgxfive: BIF fault 0x80020 at 0x3e200002 stalls job 9'], "
                  "latch=(4, 0x3e200002))\n")
    if iso_set != "control":
        w = w.replace('EXPECT = {"model": (0, {"s0": 0}), "nodiff": (25, {"s0": 25})}',
                      'EXPECT = {"model": (0, {"s0": 24})}')
    else:
        w = w.replace('EXPECT = {"model": (0, {"s0": 0}), "nodiff": (25, {"s0": 25})}',
                      'EXPECT = {"model": (0, {"s0": 0})}')
    (kp / "mock/world.py").write_text(w)
    return kp


def test_a_control_that_expects_its_fault_does_not_count_against_the_limit(repos):
    """r8-k2's xf stage stopped before its end control: the isolation control's own READONLY
    fault, the reading it exists for, was counted against `#limit`, which bounds the faults of
    the rows under test. A control's expected fault is not counted; a fit row's still is."""
    kp = fault_limit_session(repos, "control")
    m = kit(kp, repos, "mock")
    assert m.returncode == 0, m.stdout + m.stderr
    assert re.search(r"^ok +world model: driver 0 \(s0 0\)", m.stdout, re.M), m.stdout
    kp = fault_limit_session(dict(repos, tmp=repos["tmp"] / "fit"), "fit")
    m = kit(kp, repos, "mock")
    assert m.returncode == 0, m.stdout + m.stderr
    assert re.search(r"^ok +world model: driver 0 \(s0 24\)", m.stdout, re.M), m.stdout


def test_a_stage_stopped_by_its_limit_names_the_rows_it_did_not_run(repos):
    """`#limit` is a budget of planned faults and hangs, not a row count: the stage stops (rc 24)
    when the limit is reached with rows left, and the runner log says which rows were not run
    (limit), so a summary never reads them as run or as refused. A stage that reaches the end
    names none."""
    kp = fault_limit_session(repos, "fit")
    m = kit(kp, repos, "mock")
    assert m.returncode == 0, m.stdout + m.stderr
    mm = next(kp.glob("debug/mock.*/model"))
    log = (mm / "out/model/s0/runner.log").read_text()
    assert re.search(r"^## not run \(limit\): f1-fill *$", log, re.M), log
    kp = fault_limit_session(dict(repos, tmp=repos["tmp"] / "ctl"), "control")
    m = kit(kp, repos, "mock")
    assert m.returncode == 0, m.stdout + m.stderr
    mm = next(kp.glob("debug/mock.*/model"))
    assert "not run (limit)" not in (mm / "out/model/s0/runner.log").read_text()


def test_a_hook_runs_after_a_fault_row_and_its_reason_stops_the_stage(repos):
    """r9-faults: the runner called no hook after a fault row, so a stage rule on the fault's own
    kernel lines (two `SGX recovery failed: -110` in a row) was read only at the next ok row.
    hook_fault NAME runs after the fault row's reset and strict health, in the runner's shell, and
    its reason stops the stage with 24; without a reason the stage goes on."""
    kp = fault_limit_session(repos, "fit")
    t = kp / "tables/s0.txt"
    t.write_text(t.read_text().replace("#limit 1", "#limit 5"))
    w = (kp / "mock/world.py").read_text()
    (kp / "mock/world.py").write_text(w.replace('(0, {"s0": 24})', '(0, {"s0": 0})'))
    m = kit(kp, repos, "mock")
    assert m.returncode == 0, m.stdout + m.stderr
    for body, status in [('NF=0\nhook_fault() { NF=$((NF + 1)); [ "$NF" -lt 1 ] || echo "a -110"; }',
                          24), ("hook_fault() { return 0; }", 0)]:
        k2 = fault_limit_session(dict(repos, tmp=repos["tmp"] / f"h{status}"), "fit")
        t = k2 / "tables/s0.txt"
        t.write_text(t.read_text().replace("#limit 1", "#limit 5"))
        with open(k2 / "run/hooks.sh", "a") as f:
            f.write(body + "\n")
        w = (k2 / "mock/world.py").read_text()
        (k2 / "mock/world.py").write_text(w.replace('(0, {"s0": 24})', f'(0, {{"s0": {status}}})'))
        m = kit(k2, repos, "mock")
        assert m.returncode == 0, (status, m.stdout + m.stderr)
        assert re.search(rf"^ok +world model: driver 0 \(s0 {status}\)", m.stdout, re.M), m.stdout


def two_stage_session(repos, on_stop=None, expect='(0, {"s0": 24, "s1": 0})'):
    """fault_limit_session's s0, which its #limit stops with 24, then s1, a copy of the
    template's stage; `on_stop` set on s0 when given."""
    kp = fault_limit_session(repos, "fit")
    t0 = (kp / "tables/s0.txt").read_text()
    (kp / "tables/s1.txt").write_text(
        "".join(ln for ln in t0.replace("#stage s0", "#stage s1").splitlines(keepends=True)
                if not ln.startswith("c1-iso")))
    (kp / "predictions/s1.tsv").write_text((kp / "predictions/s0.tsv").read_text())
    sc = (kp / "score/score.py").read_text()
    (kp / "score/score.py").write_text(sc.replace(
        'REQUIRED = {"s0": (".txt", "cases.tsv", "void.tsv", "readings.tsv")}',
        'REQUIRED = {s: (".txt", "cases.tsv", "void.tsv", "readings.tsv") for s in ("s0", "s1")}'))
    st = "s0 = { alarm = 1800" + (f', on_stop = "{on_stop}"' if on_stop else "") + " }\n"
    toml = (kp / "session.toml").read_text().replace(
        "s0 = { alarm = 1800 }\n", st + "s1 = { alarm = 1800 }\n")
    (kp / "session.toml").write_text(toml)
    w = (kp / "mock/world.py").read_text()
    (kp / "mock/world.py").write_text(w.replace('EXPECT = {"model": (0, {"s0": 24})}',
                                                f'EXPECT = {{"model": {expect}}}'))
    return kp


def test_a_stage_stopped_by_its_rule_goes_on_unless_it_declares_on_stop_end(repos):
    """r13-tex and r13-flag: a stage that stops by its rule (runner status 24) lets the driver go
    on to the next stage, so a session whose later stages make no sense after that stop leaned
    on gates. A stage may declare `on_stop = "end"`: its rc 24 then ends the session there (the
    driver's status 24, no later stage runs). The default, and `on_stop = "next"`, go on."""
    for sub, on_stop, expect, detail in [
            ("d", None, '(0, {"s0": 24, "s1": 0})', r"driver 0 \(s0 24, s1 0\)"),
            ("n", "next", '(0, {"s0": 24, "s1": 0})', r"driver 0 \(s0 24, s1 0\)"),
            ("e", "end", '(24, {"s0": 24})', r"driver 24 \(s0 24\);")]:
        kp = two_stage_session(dict(repos, tmp=repos["tmp"] / sub), on_stop, expect)
        assert kit(kp, repos, "guard").returncode == 0, kit(kp, repos, "guard").stdout
        m = kit(kp, repos, "mock")
        assert m.returncode == 0, (on_stop, m.stdout + m.stderr)
        assert re.search(rf"^ok +world model: {detail}", m.stdout, re.M), (on_stop, m.stdout)


def test_the_guard_refuses_an_unknown_on_stop(repos):
    kp = two_stage_session(repos, "skip")
    g = kit(kp, repos, "guard")
    assert g.returncode != 0 and re.search(r"session.toml: stage s0: on_stop", g.stdout), g.stdout


# ---- post-run files: fold/ and out/ ----------------------------------------------------------
def test_verify_lets_a_fold_add_its_files_under_fold_and_out(repos):
    """r8-lgeo's fold had to put its files under out/fold/: verify took any new file of a frozen
    session as a change. The session's fold/ subtree (post-run fold notes, tables) and out/ (the
    kept records, lead logs) are not frozen, and every frozen file stays checked; no laptop
    file may come from them."""
    kp = frozen_session(repos)
    (kp / "fold/tables").mkdir(parents=True)
    (kp / "fold/FOLD.md").write_text("notes\n")
    (kp / "fold/tables/t.json").write_text("{}\n")
    (kp / "out").mkdir(exist_ok=True)
    (kp / "out/lead-run.log").write_text("log\n")
    v = kit(kp, repos, "verify")
    assert v.returncode == 0, v.stdout
    (kp / "FOLD.md").write_text("notes\n")
    v = kit(kp, repos, "verify")
    assert v.returncode != 0 and "FOLD.md" in v.stdout, v.stdout
    (kp / "FOLD.md").unlink()
    (kp / "tables/s0.txt").write_text((kp / "tables/s0.txt").read_text() + "# edit\n")
    v = kit(kp, repos, "verify")
    assert v.returncode != 0 and "tables/s0.txt" in v.stdout, v.stdout
    kp = scaffold(dict(repos, tmp=repos["tmp"] / "g"))
    toml = (kp / "session.toml").read_text().replace("laptop = []", 'laptop = ["fold/*.bin"]')
    (kp / "session.toml").write_text(toml)
    g = kit(kp, repos, "guard")
    assert g.returncode != 0 and "fold/*.bin" in g.stdout, g.stdout


def test_the_template_runs_pytest_without_a_cache_and_the_freeze_ignores_one(repos):
    """A pytest run from the session directory left .pytest_cache/ in it, which verify took for a
    new file and the freeze pinned. The template's runner passes -p no:cacheprovider, and a cache
    (or a __pycache__) anywhere in the session is no session file."""
    run_all = (KIT / "templates/tests/run_all.sh").read_text()
    assert re.search(r'-m pytest .*-p no:cacheprovider', run_all), run_all
    kp = frozen_session(repos)
    (kp / ".pytest_cache").mkdir()
    (kp / ".pytest_cache/README.md").write_text("cache\n")
    (kp / "tests/.pytest_cache").mkdir()
    (kp / "tests/.pytest_cache/v").write_text("cache\n")
    v = kit(kp, repos, "verify")
    assert v.returncode == 0, v.stdout
    assert not [f for f in S.freeze_files(kp) if ".pytest_cache" in f]
    (kp / "tests/new_test.py").write_text("x = 1\n")      # a real new file is still refused
    v = kit(kp, repos, "verify")
    assert v.returncode != 0 and "new_test.py" in v.stdout, v.stdout


# ---- noreset and idle:S: a row that keeps the GPU state of the row before it -------------------
NR_ROWS = ("n1|fit|safe|noreset|t4|fill --width 8 --height 8\n"
           "h1|fit|safe|expectfault|t4|fill --hang\n"
           "n2|fit|safe|noreset idle:120|t4|fill --width 8 --height 4\n"
           "p1|fit|safe|-|t4|fill --width 4 --height 4\n")
NR_ANSWER = ("def answer(tool, argv, world):\n"
             "    if '--hang' in argv:\n"
             "        return dict(rc=3, out='job: failed: timed out\\n', "
             "kmsg=['sgxfive: job 9 hung'])\n"
             "    if '--softfail' in argv:\n"
             "        return dict(rc=1, out='job: failed: cancelled\\n')\n")


def noreset_session(repos, rows, limit=2):
    """The template's control row first, then ROWS; the world hangs `--hang` (rc 3, `job 9 hung`
    in the kernel log) and fails `--softfail` (rc 1)."""
    kp = scaffold(repos)
    t = kp / "tables/s0.txt"
    head = [ln for ln in t.read_text().splitlines(keepends=True) if not ln.startswith("f0-fill")]
    t.write_text("".join(head).replace("#limit 0", f"#limit {limit}") + rows)
    w = (kp / "mock/world.py").read_text()
    (kp / "mock/world.py").write_text(w.replace("def answer(tool, argv, world):\n", NR_ANSWER))
    return kp


def resets_between(kmsg, names):
    """The fake reset lines of the kernel log between each pair of consecutive case markers."""
    after, cur = {}, None
    for ln in kmsg.splitlines():
        m = re.match(r"resgx545 case (\S+) ", ln)
        if m:
            cur = m.group(1)
        elif "SGX reset:" in ln and cur:
            after[cur] = after.get(cur, 0) + 1
    return {b: after.get(a, 0) for a, b in zip(names, names[1:])}


def test_a_noreset_row_runs_without_the_reset_before_it(repos):
    """Q163's hang sequences (r13-flag F3) need the GPU state of the row before: `noreset` skips
    the runner's reset before its row, after a row that ended ok (no reset at all between the
    two) or after an expected hang (only the runner's own reset after the hang); a plain row
    still takes its reset. `idle:S` sleeps S seconds before the job, IDLE_WAIT in the mock."""
    kp = noreset_session(repos, NR_ROWS)
    g = kit(kp, repos, "guard")
    assert g.returncode == 0, g.stdout
    m = kit(kp, repos, "mock", "--world", "model")
    assert m.returncode == 0, m.stdout + m.stderr
    assert re.search(r"^ok +world model: driver 0 \(s0 0\)", m.stdout, re.M), m.stdout
    mm = next(kp.glob("debug/mock.*/model"))
    kmsg = (mm / "kmsg").read_text()
    assert resets_between(kmsg, ["c0-tri", "n1", "h1", "n2", "p1"]) == \
        {"n1": 0, "h1": 1, "n2": 1, "p1": 1}, kmsg
    assert re.search(r"resgx545 r8t noreset n1 ok ", kmsg), kmsg
    assert re.search(r"resgx545 r8t noreset n2 hang ", kmsg), kmsg
    assert re.search(r"resgx545 r8t idle n2 120 ", kmsg), kmsg
    log = (mm / "out/model/s0/runner.log").read_text()
    assert "idle 120 s before n2" in log, log
    sys.path.insert(0, str(kp / "kit"))
    import kitscore
    rows = kitscore.rows(str(mm / "out/model/s0"))
    assert {n: rows[n]["class"] for n in ("n1", "h1", "n2", "p1")} == \
        {"n1": "ok", "h1": "hang", "n2": "ok", "p1": "ok"}


def test_a_noreset_row_after_a_row_that_did_not_end_ok_is_skipped(repos):
    """A row before that failed (a soft failure, a gate refusal) or was skipped leaves no state a
    `noreset` row may build on: the row is skipped (never run, not in cases.tsv), and so is a
    `noreset` row after it; the next plain row runs with its reset."""
    kp = noreset_session(repos, "s1|fit|safe|soft|t4|fill --softfail\n"
                                "n3|fit|safe|noreset|t4|fill --width 8 --height 8\n"
                                "n4|fit|safe|noreset|t4|fill --width 8 --height 4\n"
                                "p2|fit|safe|-|t4|fill --width 4 --height 4\n")
    m = kit(kp, repos, "mock", "--world", "model")
    assert m.returncode == 0, m.stdout + m.stderr
    assert re.search(r"^ok +world model: driver 0 \(s0 0\)", m.stdout, re.M), m.stdout
    mm = next(kp.glob("debug/mock.*/model"))
    log = (mm / "out/model/s0/runner.log").read_text()
    assert "== n3 skipped: noreset after s1, which ended fail" in log, log
    assert "== n4 skipped: noreset after n3, which ended skipped" in log, log
    sys.path.insert(0, str(kp / "kit"))
    import kitscore
    kept = mm / "out/model/s0"
    assert set(kitscore.rows(str(kept))) == {"c0-tri", "p2"}
    assert set(kitscore.rows(str(kept), "void.tsv")) == {"s1"}
    assert "resgx545 case n3" not in (mm / "kmsg").read_text()


def runner_tree(tmp, rows):
    """The runner's own table check alone: a staged tree with run_stage.sh, its table and env, and
    no lib_kit.sh, so a table that passes stops at the frozen-file check (rc 1), never on sudo."""
    st = tmp / "staged"
    (st / "kit").mkdir(parents=True)
    (st / "run").mkdir()
    (st / "tables").mkdir()
    (st / "kit/run_stage.sh").write_bytes((KIT / "run_stage.sh").read_bytes())
    (st / "tables/s0.txt").write_text("#stage s0\n#limit 0\n" + rows)
    (st / "run/session.env").write_text('PREFIX=r8t\nTOOLS="t4"\nEXTRA_KNOBS=""\nKNOBS=""\n')
    (st / "FROZEN.sha256").write_text("x\n")
    fz = hashlib.sha256(b"x\n").hexdigest()
    return subprocess.run(["bash", str(st / "kit/run_stage.sh"), "s0", fz, "a1"],
                          capture_output=True, text=True, timeout=60,
                          env=dict(PATH=os.environ["PATH"], HOME=str(tmp)))


@pytest.mark.parametrize("rows,word", [
    ("n0|fit|safe|noreset|t4|fill\nb|fit|safe|-|t4|fill\n", "first row"),
    ("a|fit|safe|-|t4|fill\nb|fit|safe|idle:0|t4|fill\n", "idle:0"),
    ("a|fit|safe|-|t4|fill\nb|fit|safe|idle:121|t4|fill\n", "idle:121"),
    ("a|fit|safe|-|t4|fill\nb|fit|safe|idle:01|t4|fill\n", "idle:01"),
    ("a|fit|safe|-|t4|fill\nb|fit|safe|idle:x|t4|fill\n", "idle:x"),
    ("a|fit|safe|-|t4|fill\nb|fit|safe|idle:5 idle:6|t4|fill\n", "idle"),
])
def test_the_runner_refuses_a_first_noreset_row_and_an_idle_out_of_range(tmp_path, rows, word):
    r = runner_tree(tmp_path, rows)
    assert r.returncode == 7 and word in r.stdout, (r.returncode, r.stdout + r.stderr)


def test_the_runner_accepts_noreset_after_the_first_row_and_idle_1_to_120(tmp_path):
    r = runner_tree(tmp_path, "a|fit|safe|-|t4|fill\nb|fit|safe|noreset idle:1|t4|fill\n"
                              "c|fit|safe|idle:120 noreset|t4|fill\n")
    assert r.returncode == 1 and "is not the frozen one" in r.stdout, (r.returncode, r.stdout)


def test_the_guard_refuses_a_first_noreset_row_and_an_idle_out_of_range(repos):
    kp = scaffold(repos)
    t = kp / "tables/s0.txt"
    base = t.read_text()
    g = kit(kp, repos, "guard")
    assert g.returncode == 0, g.stdout
    t.write_text(base + "x|fit|safe|noreset idle:1|t4|fill\ny|fit|safe|idle:120|t4|fill\n")
    g = kit(kp, repos, "guard")
    assert g.returncode == 0, g.stdout
    for row, word in [("x|fit|safe|idle:0|t4|fill", "idle:0"),
                      ("x|fit|safe|idle:121|t4|fill", "idle:121"),
                      ("x|fit|safe|idle:5 idle:6|t4|fill", "one idle:")]:
        t.write_text(base + row + "\n")
        g = kit(kp, repos, "guard")
        assert g.returncode != 0 and word in g.stdout, (row, g.stdout)
    first = base.replace("|reads:diff|", "|reads:diff noreset|", 1)
    assert first != base
    t.write_text(first)
    g = kit(kp, repos, "guard")
    assert g.returncode != 0 and "first row" in g.stdout and "noreset" in g.stdout, g.stdout


def test_the_header_the_runner_and_the_guard_know_the_same_words():
    run = (KIT / "run_stage.sh").read_text()
    header = run.split("trap '' PIPE HUP")[0]
    for w in ("noreset", "idle:S"):
        assert re.search(rf"^#\s+{re.escape(w)}\s", header, re.M), w
    for w in ("noreset", "idle:1", "idle:9", "idle:10", "idle:99", "idle:100", "idle:120"):
        assert S.BASE_KNOBS.match(w), w
    for w in ("idle:0", "idle:121", "idle:01", "idle:", "idle:x", "noreset:1"):
        assert not S.BASE_KNOBS.match(w), w


def test_the_mock_sets_the_idle_sleep_to_zero_and_the_fake_ssh_passes_it():
    src = (KIT / "session.py").read_text()
    assert 'IDLE_WAIT="0"' in src
    assert "IDLE_WAIT" in (KIT / "fake/ssh.py").read_text()
    run = (KIT / "run_stage.sh").read_text()
    assert re.search(r'sleep "\$\{IDLE_WAIT:-\$idle\}"', run), "idle's one sleep"


def test_the_library_mock_replays_noreset_and_idle_rows_and_says_it_has_no_state(repos):
    """The library mock starts every row from a fresh mock: a `noreset` row replays without the
    state of the row before it, which the replay says; `idle:S` is no option of the tool."""
    kp = scaffold(repos)
    bind_source(repos, kp)
    t = kp / "tables/s0.txt"
    t.write_text(t.read_text() + "n1|fit|safe|noreset idle:60|t4|fill --width 8 --height 8\n")
    m = kit(kp, repos, "mock", "--world", "model")
    assert m.returncode == 0, m.stdout + m.stderr
    assert re.search(r"^ok +libmock: 3 rows of t4 replayed", m.stdout, re.M), m.stdout
    assert re.search(r"^note libmock: 1 noreset row\(s\) replayed without the state of the row "
                     r"before", m.stdout, re.M), m.stdout


# ---- round 18: REQUIRED per row class, the replay's debugfs dumps, the driver's logs ----------
def kept_dir_with(tmp_path, rows, files):
    """A kept directory: cases.tsv rows (name, class) in the runner's columns and the files."""
    k = tmp_path / "kept"
    k.mkdir()
    (k / "cases.tsv").write_text("".join(
        f"{n}\ts0\tfit\tsafe\t-\tt4\tfill\t{0 if c == 'ok' else 3}\t{c}\t-\t-\t-\n"
        for n, c in rows))
    for f in files:
        (k / f).write_text("x")
    return k


def test_required_per_row_class_spares_a_planned_fault_the_dumps_of_an_ok_row(tmp_path):
    """r14-flag and r18-flag: a row that ends in a planned fault or hang keeps no dump, and the
    driver's kept check asked every row for the per-row files of REQUIRED (the runner asked only
    the rows that ended ok), so f2's stores were scored outside the kit. A plain ".suffix" is now
    the ok rows' (as the runner reads it); "fault:", "hang:" and "any:" name the files of the
    rows that ended so, or of every row."""
    import sessioncheck
    k = kept_dir_with(tmp_path, [("a", "ok"), ("f", "fault"), ("h", "hang")],
                      ["a.txt.gz", "a.dump.gz", "f.txt.gz", "h.txt.gz", "f.dmesg.gz"])
    rows = sessioncheck.kept_classes(str(k))
    assert rows == {"a": "ok", "f": "fault", "h": "hang"}
    assert sessioncheck.kept_problems(str(k), (".txt", ".dump", "any:.txt", "fault:.dmesg"),
                                      rows) == []
    assert sessioncheck.kept_problems(str(k), ("any:.dump",), rows) == [
        "the scorer reads f.dump, which is not kept", "the scorer reads h.dump, which is not kept"]
    assert sessioncheck.kept_problems(str(k), ("hang:.dmesg", "ok:.dmesg"), rows) == [
        "the scorer reads a.dmesg, which is not kept", "the scorer reads h.dmesg, which is not kept"]
    # a list of names (no classes): every row is an ok row, as before
    assert sessioncheck.kept_problems(str(k), (".dump",), ["a", "f"]) == [
        "the scorer reads f.dump, which is not kept"]


def test_the_kept_check_declares_every_class_s_files_for_every_row(tmp_path):
    """Declaring is about what the scorer reads, not what must be kept: a file a REQUIRED entry
    of any class names, for any row, is declared."""
    import sessioncheck
    k = kept_dir_with(tmp_path, [("a", "ok"), ("f", "fault")], ["a.dump.gz", "f.dmesg.gz"])

    def reads():
        for f in ("a.dump.gz", "f.dmesg.gz"):
            open(k / f).read()
    assert sessioncheck.kept_problems(str(k), (".dump", "fault:.dmesg"),
                                      sessioncheck.kept_classes(str(k)), reads) == []


def test_the_kept_cli_reads_the_row_classes_from_cases_tsv(tmp_path):
    k = kept_dir_with(tmp_path, [("a", "ok"), ("f", "fault")], ["a.dump"])
    sc = tmp_path / "score.py"
    sc.write_text('REQUIRED = {"s0": (".dump", "cases.tsv")}\n')
    r = subprocess.run([PY, str(HERE / "sessioncheck.py"), "kept", str(sc), "s0", str(k)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    sc.write_text('REQUIRED = {"s0": ("any:.dump", "cases.tsv")}\n')
    r = subprocess.run([PY, str(HERE / "sessioncheck.py"), "kept", str(sc), "s0", str(k)],
                       capture_output=True, text=True)
    assert r.returncode == 1 and "f.dump" in r.stdout, r.stdout


def required_missing(tmp_path, entries, name="", cls=""):
    """The runner's required_missing NAME CLASS over a required.tsv of entries (stage s0)."""
    lib = (KIT / "lib_kit.sh").read_text()
    fns = "".join(re.search(rf"^{f}\(\).*?^}}\n", lib, re.M | re.S).group(0)
                  for f in ("has_kept", "required_missing"))
    (tmp_path / "run").mkdir(exist_ok=True)
    (tmp_path / "run/required.tsv").write_text("".join(f"s0\t{e}\n" for e in entries))
    keep = tmp_path / "keep"
    keep.mkdir(exist_ok=True)
    (keep / "a.txt.gz").write_text("x")
    r = subprocess.run(["bash", "-c", fns + 'required_missing "$1" "$2"', "x", name, cls],
                       capture_output=True, text=True,
                       env=dict(os.environ, STAGE="s0", STAGED=str(tmp_path), KEEP=str(keep)))
    assert r.returncode == 0, r.stderr
    return r.stdout.split()


def test_the_runner_asks_each_row_for_the_files_of_its_class(tmp_path):
    entries = (".txt", ".dump", "any:.err", "fault:.dmesg", "hang:.snap", "cases.tsv")
    assert required_missing(tmp_path, entries, "a", "ok") == ["a.dump", "a.err"]
    assert required_missing(tmp_path, entries, "a") == ["a.dump", "a.err"]     # ok by default
    assert required_missing(tmp_path, entries, "a", "fault") == ["a.err", "a.dmesg"]
    assert required_missing(tmp_path, entries, "a", "hang") == ["a.err", "a.snap"]
    assert required_missing(tmp_path, entries) == ["cases.tsv"]


def test_the_runner_checks_a_fault_or_hang_row_s_files_after_its_recovery():
    run = (KIT / "run_stage.sh").read_text()
    fh = run[run.index("\tfault|hang)"):run.index("\tfail)")]
    assert re.search(r'required_missing "\$name" "\$class"', fh), fh
    assert "exit 23" in fh


def test_the_guard_refuses_a_required_entry_of_no_class(repos):
    kp = scaffold(repos)
    sc = kp / "score/score.py"
    text = sc.read_text()
    sc.write_text(text.replace('REQUIRED = {"s0": (".txt",', 'REQUIRED = {"s0": ("fualt:.txt",'))
    g = kit(kp, repos, "guard")
    assert g.returncode != 0 and "fualt:.txt" in g.stdout, g.stdout
    sc.write_text(text.replace('REQUIRED = {"s0": (".txt",',
                               'REQUIRED = {"s0": ("any:.txt", "fault:.dmesg",'))
    g = kit(kp, repos, "guard")
    assert g.returncode == 0, g.stdout


DUMP_SRC = """#!/bin/sh
[ "$1" = --mock ] || { echo "usage: not the library mock" >&2; exit 2; }
shift
case "$*" in *--dump-render*)
    for f in render_param render_tadata; do
        [ -f "${SGXFIVE_DEBUGFS:-/sys/kernel/debug/dri/0/sgx}/$f" ] || {
            echo "probe p: failed: --dump-render: No such file or directory"; exit 3; }
    done ;;
esac
case "$*" in *--words*)
    for f in render_words buf09; do
        [ -f "${SGXFIVE_DEBUGFS:-/sys/kernel/debug/dri/0/sgx}/$f" ] || {
            echo "sgxfive-test: --words: No such file or directory" >&2; exit 1; }
    done ;;
esac
[ -e "${SGXFIVE_DEBUGFS:-/nonexistent}/render_bg_layer" ] && { echo "a knob file" >&2; exit 1; }
echo "job: ok"; echo "diff: 0 of 2048 pixels"
"""


def test_the_replay_gives_the_tool_the_debugfs_dumps_it_copies(repos):
    """r18-flag dropped `--dump-render` from h1's and ix32-n's `probe --tri` rows (E756 had it):
    the library mock has no debugfs, so the dump's copy failed and the replay refused the row.
    The replay now gives the tool a debugfs directory (SGXFIVE_DEBUGFS) holding the files it
    copies (render_param, render_tadata, render_kept, render_words, buf09), empty, and no knob:
    a knob still comes only from the row's dbg: words."""
    kp = scaffold(repos)
    bind_source(repos, kp, src=DUMP_SRC)
    base = (kp / "tables/s0.txt").read_text()
    m, bad = replay_findings(repos, kp, base,
                             'd1|fit|safe|-|t4|probe --tri pixel --dump-render "$W" x.bin\n'
                             'd2|fit|safe|-|t4|tri --dump-render "$W" --words "$W"\n')
    assert not bad, (bad, m.stdout)
    assert re.search(r"^ok +libmock: 4 rows of t4 replayed", m.stdout, re.M), m.stdout


def test_the_driver_keeps_its_logs_under_out_never_at_the_session_s_top(repos):
    """r9-x, r13-flag, r17-zls and r18-flag: the driver's output was teed to run.log and
    stage.log at the session's top, where verify reports them "not frozen". The driver now
    writes them itself: stage to out/stage.log, run to out/ATTEMPT/run.log."""
    kp = scaffold(repos)
    m = kit(kp, repos, "mock", "--world", "model")
    assert m.returncode == 0, m.stdout + m.stderr
    top = next((kp / "debug").glob("mock.*"))
    stage_log = top / "tree/out/stage.log"
    assert "staged " in stage_log.read_text()
    run_log = (top / "model/out/model/run.log").read_text()
    assert run_log.startswith("attempt model: ") and "SUMMARY: s0" in run_log, run_log
    assert not (top / "tree/run.log").exists() and not (top / "tree/stage.log").exists()


def test_verify_takes_a_published_session_with_its_logs_at_the_top(repos):
    """Older published sessions keep their teed run.log and stage.log at the top (they are never
    touched): verify passes them, and still refuses any other new file."""
    kp = frozen_session(repos)
    (kp / "run.log").write_text("attempt 1\n")
    (kp / "stage.log").write_text("staged 3 files\n")
    v = kit(kp, repos, "verify")
    assert v.returncode == 0, v.stdout
    (kp / "notes.txt").write_text("new\n")
    v = kit(kp, repos, "verify")
    assert v.returncode != 0 and "notes.txt: not frozen" in v.stdout, v.stdout
    for d in ("tables", "score"):
        (kp / d / "run.log").write_text("x\n")
    v = kit(kp, repos, "verify")
    assert "tables/run.log: not frozen" in v.stdout, v.stdout


# ---- stream-bounded param hash (round 21) ----------------------------------------------------
#
# r19-k0 stopped at a whole-buffer param hash that differed in 4 dwords past a stream's end only
# (stale terminate words, E1077's session r19-k0b); kitscore.param_hash and lib_kit.sh's
# param_hash hash each stream up to its terminate word.

DATA = pathlib.Path(os.environ.get("RESGX545_DATA", str(pathlib.Path.home() / "src/resgx545-data")))
E1077_PMASK = "ed097a084afcb70a2220ba82f4a8f085a6be53c18d19308b088501b6bafc27e3"
E1077_DUMPS = (
    "render/closing-r10-dpm/out/20261113-102513/s6rep/a0-cal-2048.p1139-green.param.bin.gz",
    "render/closing-r19-k0/out/20261114-223342/k0/k0-a0.p1139-green.param.bin.gz",
    "render/closing-r19-k0b/out/20261114-224248/k0/k0-a0.p1139-green.param.bin.gz",
)


def dwords(*ws):
    return b"".join(w.to_bytes(4, "little") for w in ws)


def shell_param_hash(path):
    lib = (KIT / "lib_kit.sh").read_text()
    fns = re.search(r"^sha\(\) \{.*?\}\n", lib, re.M).group(0)
    fns += re.search(r"^param_hash\(\) \{\n.*?^\}\n", lib, re.M | re.S).group(0)
    r = subprocess.run(["bash", "-c", fns + 'param_hash "$1"', "x", str(path)],
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


def test_param_hash_ignores_what_follows_a_stream_s_terminate_word(tmp_path):
    import kitscore
    T = 0xC0000000
    a = dwords(1, 2, T, T, T, 7, T, T)
    b = dwords(1, 2, T, 0, 0, 7, T, 0)
    assert kitscore.param_hash(a) == kitscore.param_hash(b)
    # what precedes a terminate word still counts, as does a stream's own terminate word
    assert kitscore.param_hash(a) != kitscore.param_hash(dwords(1, 3, T, T, T, 7, T, T))
    assert kitscore.param_hash(a) != kitscore.param_hash(dwords(1, 2, 0, T, T, 7, T, T))
    assert kitscore.param_hash(a) != kitscore.param_hash(dwords(1, 2, T, T, T, 8, T, T))
    # the hash is the sha256 of the masked dwords as "%08x\n" lines
    want = hashlib.sha256(b"".join(b"%08x\n" % w for w in (1, 2, T, 0, 0, 7, T, 0)))
    assert kitscore.param_hash(a) == want.hexdigest()
    assert kitscore.param_hash(None) is None
    for name, buf in (("a", a), ("b", b)):
        (tmp_path / name).write_bytes(buf)
        assert shell_param_hash(tmp_path / name) == kitscore.param_hash(buf)


@pytest.mark.parametrize("rel", E1077_DUMPS)
def test_param_hash_holds_on_e1077_s_kept_dumps(rel, tmp_path):
    """r10-dpm's kept a0-cal-2048, r19-k0's stopped k0-a0 and r19-k0b's k0-a0 (E1077): one
    stream-bounded hash, ed097a08..., where r19-k0's whole-buffer sha256 differed."""
    import gzip
    import kitscore
    p = DATA / rel
    if not p.exists():
        pytest.skip(f"{p} is not here (RESGX545_DATA)")
    b = gzip.decompress(p.read_bytes())
    assert kitscore.param_hash(b) == E1077_PMASK
    raw = tmp_path / "param.bin"
    raw.write_bytes(b)
    assert shell_param_hash(raw) == E1077_PMASK


def test_whole_buffer_sha256_differs_on_r19_k0_s_dump():
    import gzip
    old, new = (DATA / E1077_DUMPS[0], DATA / E1077_DUMPS[1])
    if not (old.exists() and new.exists()):
        pytest.skip("E1077's kept dumps are not here (RESGX545_DATA)")
    a, b = gzip.decompress(old.read_bytes()), gzip.decompress(new.read_bytes())
    assert hashlib.sha256(a).hexdigest() != hashlib.sha256(b).hexdigest()


# ---- kreg:OFF=V, a register write of ours (Q024, round 29) ------------------------------------
KREG_TOML = '[kregs]\n"0x0a78" = { values = ["0x00", "0x01", "0x2c", "0x3f"] }\n\n'
KREG_ROWS = ("k1|fit|flagged|kreg:0x0a78=0x01|t4|tri --width 64 --height 64\n"
             "k2|fit|flagged|kreg:0x0a78=0x3f|t4|tri --width 32 --height 32\n")
KREG_ANSWER = ("def answer(tool, argv, world):\n"
               "    if 'kregfreeze' in world and argv[:1] == ['tri'] and '32' in argv:\n"
               "        return dict(rc=124, out='')\n")


def kreg_session(repos, cls="flagged", rows=KREG_ROWS, toml=KREG_TOML, expect=None):
    """The template's stage s0 declared `class = CLS`, session.toml's [kregs] TOML, and ROWS
    after the template's rows; the world freezes k2 (rc 124) in world kregfreeze."""
    kp = scaffold(repos)
    t = kp / "tables/s0.txt"
    t.write_text(t.read_text() + rows)
    st = (kp / "session.toml").read_text()
    st = st.replace("s0 = { alarm = 1800 }", f's0 = {{ alarm = 1800, class = "{cls}" }}')
    st = st.replace("\n[kregs]\n", "\n")        # the template's empty table
    st = st.replace("# a debugfs knob a row may write", toml + "# a debugfs knob a row may write")
    (kp / "session.toml").write_text(st)
    w = (kp / "mock/world.py").read_text().replace("def answer(tool, argv, world):\n",
                                                   KREG_ANSWER)
    if expect:
        w = re.sub(r"^EXPECT = .*$", f"EXPECT = {expect!r}", w, count=1, flags=re.M)
    (kp / "mock/world.py").write_text(w)
    return kp


def lib_kregs():
    """lib_kit.sh's and run_stage.sh's frozen allow-list: {offset: (default, max)}."""
    run = (KIT / "run_stage.sh").read_text()
    m = re.search(r'^KIT_KREGS="([^"]*)"', run, re.M)
    assert m, "run_stage.sh freezes KIT_KREGS"
    out = {}
    for e in m.group(1).split():
        off, _, rest = e.partition("=")
        d, _, mx = rest.partition("/")
        out[off] = (d, int(mx, 0))
    return out


def test_the_kreg_allow_list_is_0x0a78_alone_and_the_same_on_both_sides():
    """Round 29 (Q024): the kit writes one register, CR_PDS_REG_0A78, to 0x00-0x3f (E045's 64
    values), back to the firmware's 0x2c; the Mac guard and the laptop runner freeze one list."""
    assert S.KREG_ALLOWED == {"0x0a78": ("0x2c", 0x3f)}
    assert lib_kregs() == S.KREG_ALLOWED


def test_the_guard_allows_a_kreg_word_only_in_a_flagged_stage(repos):
    kp = kreg_session(repos)
    g = kit(kp, repos, "guard")
    assert g.returncode == 0, g.stdout
    kp = kreg_session(dict(repos, tmp=repos["tmp"] / "safe"), cls="safe")
    g = kit(kp, repos, "guard")
    assert g.returncode != 0 and "flagged" in g.stdout and "kreg:0x0a78=0x01" in g.stdout, g.stdout
    kp = kreg_session(dict(repos, tmp=repos["tmp"] / "none"))
    st = (kp / "session.toml").read_text().replace(', class = "flagged"', "")
    (kp / "session.toml").write_text(st)
    g = kit(kp, repos, "guard")
    assert g.returncode != 0 and "flagged" in g.stdout, g.stdout


@pytest.mark.parametrize("toml,rows,word", [
    ('[kregs]\n"0x0abc" = { values = ["0x00"] }\n\n',
     "k1|fit|flagged|kreg:0x0abc=0x00|t4|tri\n", "0x0abc"),
    ('[kregs]\n"0x0a78" = { values = ["0x40"] }\n\n',
     "k1|fit|flagged|kreg:0x0a78=0x40|t4|tri\n", "0x40"),
    ('[kregs]\n"0x0a78" = { values = ["0x01"], default = "0x00" }\n\n',
     "k1|fit|flagged|kreg:0x0a78=0x01|t4|tri\n", "default"),
    ('[kregs]\n"0x0a78" = { values = ["1"] }\n\n',
     "k1|fit|flagged|kreg:0x0a78=1|t4|tri\n", "0x"),
    (KREG_TOML, "k1|fit|flagged|kreg:0x0a78=0x08|t4|tri\n", "kreg:0x0a78=0x08"),
    (KREG_TOML, "k1|fit|flagged|kreg:0x0a78^=0x01|t4|tri\n", "kreg:0x0a78^=0x01"),
    (KREG_TOML, "k1|fit|flagged|kreg:0x0A78=0x01|t4|tri\n", "kreg:0x0A78=0x01"),
    (KREG_TOML, "k1|fit|flagged|kreg:0x0a78=0x01 expectfault|t4|tri\n", "expectfault"),
    (KREG_TOML, "k1|fit|flagged|kreg:0x0a78=0x01 kreg:0x0a78=0x00|t4|tri\n", "one kreg"),
    ("", "k1|fit|flagged|kreg:0x0a78=0x01|t4|tri\n", "kreg:0x0a78=0x01"),
])
def test_the_guard_refuses_a_register_or_value_off_the_allow_list(repos, toml, rows, word):
    kp = kreg_session(repos, rows=rows, toml=toml)
    g = kit(kp, repos, "guard")
    assert g.returncode != 0 and word in g.stdout, g.stdout


def test_the_guard_wants_every_flagged_stage_after_every_safe_one(repos):
    kp = kreg_session(repos)
    (kp / "tables/s1.txt").write_text((kp / "tables/s0.txt").read_text()
                                      .replace("#stage s0", "#stage s1")
                                      .replace(KREG_ROWS, ""))
    st = (kp / "session.toml").read_text()
    (kp / "session.toml").write_text(st.replace(
        's0 = { alarm = 1800, class = "flagged" }',
        's0 = { alarm = 1800, class = "flagged" }\ns1 = { alarm = 1800 }'))
    g = kit(kp, repos, "guard")
    assert g.returncode != 0 and "after every safe stage" in g.stdout, g.stdout
    (kp / "session.toml").write_text(st.replace(
        's0 = { alarm = 1800, class = "flagged" }',
        's0 = { alarm = 1800, class = "unsafe" }'))
    g = kit(kp, repos, "guard")
    assert g.returncode != 0 and "class" in g.stdout, g.stdout


@pytest.mark.parametrize("line", ["kreg_set 0x0a78 0x01", "kregs_restore",
                                  "printf '0x0a78=1\\n' | sudo -n timeout -k 5 20 tee \"$D/kreg\""])
def test_the_guard_refuses_a_register_write_in_a_hook(repos, line):
    kp = kreg_session(repos)
    with open(kp / "run/hooks.sh", "a") as f:
        f.write(f"hook_extra() {{ {line}; }}\n")
    g = kit(kp, repos, "guard")
    assert g.returncode != 0 and "hooks.sh" in g.stdout, g.stdout


def test_a_kreg_row_writes_before_its_job_reads_back_and_restores_after_it(repos):
    kp = kreg_session(repos)
    m = kit(kp, repos, "mock", "--world", "model")
    assert m.returncode == 0, m.stdout + m.stderr
    assert re.search(r"^ok +world model: driver 0 \(s0 0\)", m.stdout, re.M), m.stdout
    mm = next(kp.glob("debug/mock.*/model"))
    writes = (mm / "fake/writes").read_text().splitlines()
    kw = [x for x in writes if x.startswith("kreg ")]
    # each row's write and the restore after its job, then the exit trap's restore
    assert kw == ["kreg 0x0a78=0x01", "kreg 0x0a78=0x2c", "kreg 0x0a78=0x3f",
                  "kreg 0x0a78=0x2c", "kreg 0x0a78=0x2c"], writes
    kmsg = (mm / "kmsg").read_text()
    order = [kmsg.index(s) for s in ("resgx545 r8t kreg k1 0x0a78=0x01 ", "resgx545 case k1 ",
                                     "resgx545 r8t kreg-restored k1 ", "resgx545 case k2 ",
                                     "resgx545 r8t kreg-restored k2 ",
                                     "resgx545 r8t exit kregs restored ")]
    assert order == sorted(order), kmsg
    assert re.search(r"^0x0a78 0x0000002c$", (mm / "dbgreal/kreg").read_text(), re.M)
    log = (mm / "out/model/s0/runner.log").read_text()
    assert "kreg 0x0a78: 0x0000002c -> 0x01, reads 0x00000001" in log, log


def test_a_kreg_that_does_not_read_back_stops_before_the_job(repos):
    kp = kreg_session(repos, expect={"kregstuck": (19, {"s0": 19})})
    m = kit(kp, repos, "mock", "--world", "kregstuck")
    assert m.returncode == 0, m.stdout + m.stderr
    mm = next(kp.glob("debug/mock.*/kregstuck"))
    kmsg = (mm / "kmsg").read_text()
    assert "resgx545 case k1 " not in kmsg, kmsg
    log = (mm / "out/kregstuck/s0/runner.log").read_text()
    assert "## STOP: kreg 0x0a78 does not read back 0x01 before k1" in log, log


def test_a_kreg_is_restored_by_the_exit_trap_when_its_job_does_not_return(repos):
    kp = kreg_session(repos, expect={"kregfreeze": (6, {"s0": 6})})
    m = kit(kp, repos, "mock", "--world", "kregfreeze")
    assert m.returncode == 0, m.stdout + m.stderr
    mm = next(kp.glob("debug/mock.*/kregfreeze"))
    kmsg = (mm / "kmsg").read_text()
    assert "resgx545 r8t kreg-restored k2 " not in kmsg, kmsg
    assert re.search(r"resgx545 r8t exit kregs restored", kmsg), kmsg
    assert kmsg.index("resgx545 case k2 ") < kmsg.index("exit kregs restored")
    writes = [x for x in (mm / "fake/writes").read_text().splitlines() if x.startswith("kreg ")]
    assert writes[-2:] == ["kreg 0x0a78=0x3f", "kreg 0x0a78=0x2c"], writes
    assert re.search(r"^0x0a78 0x0000002c$", (mm / "dbgreal/kreg").read_text(), re.M)


def test_a_safe_stage_never_writes_a_declared_register(repos):
    """A session that declares [kregs] but whose stage is safe and has no kreg row: the runner
    reads the register (preflight: at its default) and writes it never, not even in its trap."""
    kp = kreg_session(repos, cls="safe", rows="")
    assert kit(kp, repos, "guard").returncode == 0
    m = kit(kp, repos, "mock", "--world", "model")
    assert m.returncode == 0, m.stdout + m.stderr
    mm = next(kp.glob("debug/mock.*/model"))
    assert not [x for x in (mm / "fake/writes").read_text().splitlines()
                if x.startswith("kreg")]


def runner_env_tree(tmp, rows, env):
    """runner_tree with session.env ENV: the runner's table check alone (rc 7 or the frozen-file
    check's rc 1)."""
    st = tmp / "staged"
    (st / "kit").mkdir(parents=True)
    (st / "run").mkdir()
    (st / "tables").mkdir()
    (st / "kit/run_stage.sh").write_bytes((KIT / "run_stage.sh").read_bytes())
    (st / "tables/s0.txt").write_text("#stage s0\n#limit 0\n" + rows)
    (st / "run/session.env").write_text('PREFIX=r8t\nTOOLS="t4"\nEXTRA_KNOBS=""\nKNOBS=""\n' + env)
    (st / "FROZEN.sha256").write_text("x\n")
    fz = hashlib.sha256(b"x\n").hexdigest()
    return subprocess.run(["bash", str(st / "kit/run_stage.sh"), "s0", fz, "a1"],
                          capture_output=True, text=True, timeout=60,
                          env=dict(PATH=os.environ["PATH"], HOME=str(tmp)))


KREG_ENV = 'KREGS="0x0a78"\nKREG_0x0a78_VALUES="0x00 0x01"\n'


@pytest.mark.parametrize("env,row,ok", [
    (KREG_ENV + 'FLAGGED_STAGES="s0"\n', "k|fit|flagged|kreg:0x0a78=0x01|t4|tri\n", True),
    (KREG_ENV + 'FLAGGED_STAGES="s1"\n', "k|fit|flagged|kreg:0x0a78=0x01|t4|tri\n", False),
    (KREG_ENV, "k|fit|flagged|kreg:0x0a78=0x01|t4|tri\n", False),
    (KREG_ENV + 'FLAGGED_STAGES="s0"\n', "k|fit|flagged|kreg:0x0a78=0x08|t4|tri\n", False),
    (KREG_ENV + 'FLAGGED_STAGES="s0"\n',
     "k|fit|flagged|kreg:0x0a78=0x01 expectfault|t4|tri\n", False),
    ('KREGS="0x0abc"\nKREG_0x0abc_VALUES="0x00"\nFLAGGED_STAGES="s0"\n',
     "k|fit|flagged|kreg:0x0abc=0x00|t4|tri\n", False),
    ('KREGS="0x0a78"\nKREG_0x0a78_VALUES="0x40"\nFLAGGED_STAGES="s0"\n',
     "k|fit|flagged|kreg:0x0a78=0x40|t4|tri\n", False),
])
def test_the_runner_refuses_a_kreg_outside_a_flagged_stage_or_its_allow_list(tmp_path, env, row,
                                                                            ok):
    r = runner_env_tree(tmp_path, "a|fit|safe|-|t4|fill\n" + row, env)
    if ok:
        assert r.returncode == 1 and "is not the frozen one" in r.stdout, (r.returncode, r.stdout)
    else:
        assert r.returncode == 7 and "kreg" in r.stdout, (r.returncode, r.stdout)


# ---- pre:miscinfo, a debugfs miscinfo read before snap0 (Q111, round 32) ---------------------
MISC_ROWS = ("m1|fit|safe|pre:miscinfo|t4|tri --width 64 --height 64\n"
             "m2|fit|safe|-|t4|tri --width 32 --height 32\n")


def misc_session(repos, rows=MISC_ROWS, expect=None):
    """The template's safe stage s0 with ROWS after its rows."""
    kp = scaffold(repos)
    t = kp / "tables/s0.txt"
    t.write_text(t.read_text() + rows)
    if expect:
        w = (kp / "mock/world.py").read_text()
        w = re.sub(r"^EXPECT = .*$", f"EXPECT = {expect!r}", w, count=1, flags=re.M)
        (kp / "mock/world.py").write_text(w)
    return kp


def test_the_guard_allows_pre_miscinfo_in_a_safe_stage(repos):
    kp = misc_session(repos)
    g = kit(kp, repos, "guard")
    assert g.returncode == 0, g.stdout


@pytest.mark.parametrize("rows,word", [
    ("m0|fit|safe|-|t4|tri\nm1|fit|safe|pre:miscinfo noreset|t4|tri\n", "noreset"),
    ("m1|fit|safe|pre:miscinfo pre:miscinfo|t4|tri\n", "one pre:miscinfo"),
    ("m1|fit|safe|pre:misc|t4|tri\n", "pre:misc"),
])
def test_the_guard_refuses_pre_miscinfo_with_noreset_or_twice(repos, rows, word):
    kp = misc_session(repos, rows=rows)
    g = kit(kp, repos, "guard")
    assert g.returncode != 0 and word in g.stdout, g.stdout


@pytest.mark.parametrize("line", ['sudo -n timeout -k 5 10 cat "$D/miscinfo"',
                                  "dbg_cat miscinfo", "miscinfo_read x"])
def test_the_guard_refuses_a_miscinfo_read_in_a_hook(repos, line):
    """The miscinfo read sends a firmware command (GETMISCINFO): the kit's word only."""
    kp = misc_session(repos)
    with open(kp / "run/hooks.sh", "a") as f:
        f.write(f"hook_extra() {{ {line}; }}\n")
    g = kit(kp, repos, "guard")
    assert g.returncode != 0 and "hooks.sh" in g.stdout, g.stdout


def test_the_preflight_needs_debugfs_miscinfo_only_when_a_row_reads_it(repos):
    kp = misc_session(repos)
    env = S.generated(kp)["run/session.env"]
    assert re.search(r'^DEBUGFS_NEED="[^"]*\bmiscinfo\b', env, re.M), env
    kp = misc_session(dict(repos, tmp=repos["tmp"] / "none"), rows="")
    env = S.generated(kp)["run/session.env"]
    assert not re.search(r'^DEBUGFS_NEED="[^"]*\bmiscinfo\b', env, re.M), env


def test_a_pre_miscinfo_row_reads_after_the_reset_and_before_snap0_and_keeps_it(repos):
    kp = misc_session(repos)
    m = kit(kp, repos, "mock", "--world", "model")
    assert m.returncode == 0, m.stdout + m.stderr
    assert re.search(r"^ok +world model: driver 0 \(s0 0\)", m.stdout, re.M), m.stdout
    mm = next(kp.glob("debug/mock.*/model"))
    kmsg = (mm / "kmsg").read_text()
    mark = kmsg.index("resgx545 r8t miscinfo m1 ")
    answer = kmsg.index("SGX firmware: core 545", mark)
    assert mark < answer < kmsg.index("resgx545 r8t snap m1 0 ") < kmsg.index("resgx545 case m1 "), \
        kmsg
    # the reset before m1 comes before its read: the last reset line before the read's mark
    before = kmsg[:kmsg.index("resgx545 r8t miscinfo m1 ")]
    assert before.rindex("SGX reset") > before.rindex("resgx545 case f0-fill "), kmsg
    assert "resgx545 r8t miscinfo m2 " not in kmsg, kmsg
    # a read, not a write: the only debugfs writes are the resets
    assert set((mm / "fake/writes").read_text().splitlines()) == {"reset 1"}
    kept = mm / "out/model/s0"
    import kitscore
    assert kitscore.miscinfo(str(kept), "m1")["served"] is True
    assert kitscore.miscinfo(str(kept), "m2") is None
    log = (kept / "runner.log").read_text()
    assert re.search(r"miscinfo before m1: served", log), log


def test_a_miscinfo_read_with_a_mismatch_stops_before_the_job(repos):
    kp = misc_session(repos, expect={"miscinfobad": (19, {"s0": 19})})
    m = kit(kp, repos, "mock", "--world", "miscinfobad")
    assert m.returncode == 0, m.stdout + m.stderr
    mm = next(kp.glob("debug/mock.*/miscinfobad"))
    kmsg = (mm / "kmsg").read_text()
    assert "resgx545 case m1 " not in kmsg, kmsg
    log = (mm / "out/miscinfobad/s0/runner.log").read_text()
    assert "## STOP: the miscinfo read before m1 was not served" in log, log
    assert (mm / "out/miscinfobad/s0/m1.miscinfo.gz").exists()


def test_a_miscinfo_read_that_fails_stops_before_the_job(repos):
    kp = misc_session(repos, expect={"miscinfofail": (19, {"s0": 19})})
    m = kit(kp, repos, "mock", "--world", "miscinfofail")
    assert m.returncode == 0, m.stdout + m.stderr
    mm = next(kp.glob("debug/mock.*/miscinfofail"))
    log = (mm / "out/miscinfofail/s0/runner.log").read_text()
    assert "## STOP: the miscinfo read before m1 was not served (status 1" in log, log


@pytest.mark.parametrize("row,ok", [
    ("k|fit|safe|pre:miscinfo|t4|tri\n", True),
    ("k|fit|safe|pre:miscinfo noreset|t4|tri\n", False),
    ("k|fit|safe|pre:miscinfo pre:miscinfo|t4|tri\n", False),
])
def test_the_runner_refuses_pre_miscinfo_with_noreset_or_twice(tmp_path, row, ok):
    r = runner_env_tree(tmp_path, "a|fit|safe|-|t4|fill\n" + row, "")
    if ok:
        assert r.returncode == 1 and "is not the frozen one" in r.stdout, (r.returncode, r.stdout)
    else:
        assert r.returncode == 7 and "miscinfo" in r.stdout, (r.returncode, r.stdout)


MISC_OK = ("GETMISCINFO answered after 142 us\ncore rev         0x0001000d ok\n"
           "all values match\n")
MISC_BAD = ("GETMISCINFO answered after 142 us\ncore rev         0x0001000c MISMATCH\n"
            "                 expected 0x0001000d\nMISMATCHES\n")


def misc_kept(tmp, text=MISC_OK, knobs="pre:miscinfo"):
    import gzip
    d = tmp / "kept"
    d.mkdir()
    cols = "name\tstage\tset\trisk\tknobs\ttool\targs\trc\tclass\tfault_int\tfault_word\tfree_kb\n"
    (d / "cases.tsv").write_text(cols + f"m1\ts0\tfit\tsafe\t{knobs}\tt4\ttri\t0\tok\t-\t-\t1\n")
    (d / "m1.txt.gz").write_bytes(gzip.compress(b"job: ok\n"))
    if text is not None:
        (d / "m1.miscinfo.gz").write_bytes(gzip.compress(text.encode()))
    return d


@pytest.mark.parametrize("text,served,us", [(MISC_OK, True, 142), (MISC_BAD, False, 142),
                                            ("cat: miscinfo: Connection timed out\n", False,
                                             None)])
def test_kitscore_reads_whether_the_miscinfo_kick_was_served(tmp_path, text, served, us):
    import kitscore
    d = misc_kept(tmp_path, text)
    got = kitscore.miscinfo(str(d), "m1")
    assert got["served"] is served and got["us"] == us, got


def test_the_kept_check_wants_the_miscinfo_of_a_row_with_the_word(tmp_path):
    import sessioncheck
    d = misc_kept(tmp_path, text=None)
    probs = sessioncheck.kept_problems(str(d), (".txt",), sessioncheck.kept_classes(str(d)))
    assert any("m1.miscinfo" in p for p in probs), probs
    (d / "m1.miscinfo").write_text(MISC_OK)
    assert sessioncheck.kept_problems(str(d), (".txt",), sessioncheck.kept_classes(str(d))) == []


def test_a_scorer_may_read_the_miscinfo_of_a_row_with_the_word(tmp_path):
    import kitscore
    import sessioncheck
    d = misc_kept(tmp_path)
    probs = sessioncheck.kept_problems(str(d), (".txt",), sessioncheck.kept_classes(str(d)),
                                       lambda: kitscore.miscinfo(str(d), "m1"))
    assert probs == [], probs


def test_the_header_the_runner_and_the_guard_know_pre_miscinfo():
    header = (KIT / "run_stage.sh").read_text().split("trap '' PIPE HUP")[0]
    assert re.search(r"^#\s+pre:miscinfo\s", header, re.M)
    assert S.BASE_KNOBS.match("pre:miscinfo")
    for w in ("pre:", "pre:miscinfo2", "miscinfo"):
        assert not S.BASE_KNOBS.match(w), w
    lib = (KIT / "lib_kit.sh").read_text()
    assert [ln.strip() for ln in lib.splitlines() if "$D/miscinfo" in ln] == [S.MISCINFO_LINE]


def test_the_library_mock_replays_a_pre_miscinfo_row_and_says_it_sends_no_command(repos):
    kp = scaffold(repos)
    bind_source(repos, kp)
    t = kp / "tables/s0.txt"
    t.write_text(t.read_text() + "m1|fit|safe|pre:miscinfo|t4|fill --width 8 --height 8\n")
    m = kit(kp, repos, "mock", "--world", "model")
    assert m.returncode == 0, m.stdout + m.stderr
    assert re.search(r"^ok +libmock: 3 rows of t4 replayed", m.stdout, re.M), m.stdout
    assert re.search(r"^note libmock: 1 pre:miscinfo row\(s\) replayed without the miscinfo "
                     r"read", m.stdout, re.M), m.stdout


def test_the_fake_reset_ends_in_the_boot_s_own_getmiscinfo_as_the_kernel_s_does(repos):
    """The fork's boot after every reset asks GETMISCINFO (sgxfive_ident_ask) and logs its
    answer; a row's pre:miscinfo is a second command, so the fake log has one answer a reset."""
    kp = misc_session(repos)
    m = kit(kp, repos, "mock", "--world", "model")
    assert m.returncode == 0, m.stdout + m.stderr
    kmsg = (next(kp.glob("debug/mock.*/model")) / "kmsg").read_text()
    resets = kmsg.count("SGX reset: BIF_FAULT")
    assert resets and kmsg.count("SGX boot: kicking the EDM") == resets
    assert kmsg.count("SGX firmware: core 545") == resets + 1, kmsg
    m1 = kmsg[:kmsg.index("resgx545 r8t snap m1 0 ")]
    tail = m1[m1.rindex("SGX reset: BIF_FAULT"):]
    assert tail.count("SGX firmware: core 545") == 2, tail


def test_the_fake_regs_show_cache_ctrl_set_by_a_job_and_cleared_by_a_reset(repos):
    """The fake laptop's CR_CACHE_CTRL (0x0804) reads as r31-cc's snapshots do (E1122): the
    reset word 0x0000ffff after a reset and the miscinfo read, 0x1000ffff after a tool's job."""
    import gzip
    kp = misc_session(repos)
    m = kit(kp, repos, "mock", "--world", "model")
    assert m.returncode == 0, m.stdout + m.stderr
    kept = next(kp.glob("debug/mock.*/model")) / "out/model/s0"
    for n in ("m1", "m2"):
        s0 = gzip.decompress((kept / f"{n}.snap0.regs.gz").read_bytes()).decode()
        s9 = gzip.decompress((kept / f"{n}.snap9.regs.gz").read_bytes()).decode()
        assert "reg 0x0804 0x0000ffff" in s0.splitlines(), s0
        assert "reg 0x0804 0x1000ffff" in s9.splitlines(), s9


# ---- round 34 (T1): premises read from the session's own snap0, intervals from a calibration --
def kept_dir(tmp_path, rows, snaps=None, readings=None):
    """A kept stage directory: cases.tsv for `rows`, NAME.snap0.regs.gz where `snaps` has one
    ({name: {offset: value}}), readings.tsv of `readings` ({name: 'k=v ...'})."""
    import gzip
    d = tmp_path / "kept"
    d.mkdir()
    (d / "cases.tsv").write_text(
        "\t".join(("name", "stage", "set", "risk", "knobs", "tool", "args", "rc", "class",
                   "fault_int", "fault_word", "free_kb")) + "\n"
        + "".join(f"{n}\ts\tcontrol\tsafe\t-\trt\ta\t0\tok\t-\t-\t1\n" for n in rows))
    for n, regs in (snaps or {}).items():
        body = "sgxfive regs 1\nstate loaded 1\n" + "".join(
            f"reg {o:#06x} {v:#010x}\n" for o, v in regs.items()) + "dwords 0x00 0x00000001\n"
        with gzip.open(d / f"{n}.snap0.regs.gz", "wb") as f:
            f.write(body.encode())
    if readings:
        (d / "readings.tsv").write_text("name\treads\treading\n" + "".join(
            f"{n}\tdiff,ivl\t{r}\n" for n, r in readings.items()))
    return d


def test_kitscore_reads_a_kept_snap0_register_table(tmp_path):
    sys.path.insert(0, str(KIT))
    import kitscore
    d = kept_dir(tmp_path, ["r1", "r2"], snaps={"r1": {0x0A60: 0x5, 0x0ACC: 0x01003574}})
    assert kitscore.snap_regs(str(d), "r1") == {0x0A60: 0x5, 0x0ACC: 0x01003574}
    assert kitscore.snap_regs(str(d), "r2") == {}
    # the debugfs file also lists dword tables after the regs: only `reg` lines are registers
    assert kitscore.snaps0(str(d)) == {"r1": {0x0A60: 0x5, 0x0ACC: 0x01003574}}


def test_kitscore_snaps_feed_scorekit_reg_control(tmp_path):
    sys.path.insert(0, str(KIT))
    import kitscore
    import scorekit
    d = kept_dir(tmp_path, ["r1"], snaps={"r1": {0x0A60: 0x0000FFFF}})
    snaps = kitscore.snaps0(str(d))
    assert scorekit.reg_control(0x0000FFFF, "@snap0", "0x0a60", "r1", snaps) is True
    assert scorekit.reg_control(0x1000FFFF, "@snap0", "0x0a60", "r1", snaps) is False


def test_kitscore_calibration_is_the_readings_ivl_of_the_stages_rows(tmp_path):
    sys.path.insert(0, str(KIT))
    import kitscore
    d = kept_dir(tmp_path, ["k1", "k2", "k3"],
                 readings={"k1": "diff=0 ivl=4897", "k2": "diff=0 ivl=3696", "k3": "diff=0"})
    c = kitscore.calibration(str(d))
    assert c.rows == 2 and c.ns == (4897 + 3696) / 2 and c.window is not None
    c = kitscore.calibration(str(d), names=["k1"])
    assert c.window is None and c.problems


def test_kitscore_calibration_of_a_stage_that_has_not_run_is_empty(tmp_path):
    sys.path.insert(0, str(KIT))
    import kitscore
    c = kitscore.calibration(str(tmp_path / "none"))
    assert c.rows == 0 and c.window is None


def lint_session(repos, tables, preds):
    kp = scaffold(repos)
    (kp / "tables/s0.txt").write_text(tables)
    (kp / "predictions/s0.tsv").write_text(
        "case\tquantity\tvalue\tmodel\tset\tsource\n" + preds)
    return kp


T_REG = ("#stage s0\n#limit 0\n"
         "ref|control|safe|reads:diff|t4|tri --width 64 --height 64\n"
         "c1|control|safe|reads:diff|t4|tri --width 64 --height 64\n")


def test_the_lint_command_and_the_freeze_warn_on_a_constant_for_a_snapshotted_register(repos):
    kp = lint_session(repos, T_REG, "c1\treg:0x0a60\t0x1000ffff\tH\tcontrol\tE258\n")
    li = kit(kp, repos, "lint")
    assert li.returncode == 0 and "WARN" in li.stdout and "0x0a60" in li.stdout, li.stdout
    f = kit(kp, repos, "freeze")
    assert f.returncode == 0 and "WARN" in f.stdout and "@snap0" in f.stdout, f.stdout


def test_the_freeze_is_quiet_on_the_snap0_form(repos):
    kp = lint_session(repos, T_REG, "c1\treg:0x0a60\t@snap0:ref\tH\tcontrol\tthe row's snap0\n")
    f = kit(kp, repos, "freeze")
    assert f.returncode == 0 and "WARN" not in f.stdout, f.stdout


def test_the_freeze_refuses_a_snap0_reference_to_an_unknown_row(repos):
    kp = lint_session(repos, T_REG, "c1\treg:0x0a60\t@snap0:nope\tH\tcontrol\tx\n")
    li = kit(kp, repos, "lint")
    assert li.returncode == 1 and "nope" in li.stdout
    f = kit(kp, repos, "freeze")
    assert f.returncode != 0 and "nope" in f.stdout and not (kp / "FROZEN.sha256").exists()


# ---- owntask: one of our own firmware tasks as a kit stage (round 36, kernel33 design §5) ----
OWN_BLOB = b"\x01own-task blob fixture\x00" * 4
OWN_STAGE = ('own = { alarm = 1800, class = "flagged", owntask = { blob = "emitsa", '
             'arm = "slots=0x1 entry=0" } }')
OWN_ROWS = ('o1|fit|flagged|-|owntask|{"cmd": 1, "params": {}, "timeout_ms": 100}\n'
            'o2|fit|flagged|-|owntask|{"cmd": 1, "params": {"32": 7}, "timeout_ms": 100}\n')
OWN_REQUIRED = ('"own": (".txt", ".own_res.json", ".gate.json", "cases.tsv", "void.tsv", '
                '"readings.tsv", "owntask.arm.json", "owntask.reset.json")')
OWN_WORLD = ("def own_res(cmd, params, world):\n"
             "    return {0x44: 0x5a5a3301, 0x45: 1, 0x50: 0x5a5a3302}\n\n\n")


def own_repos(repos, blob=OWN_BLOB, name="emitsa"):
    """repos with asm/fwtask/fwtask.map at a new commit (c1): NAME's blob sha256 is BLOB's."""
    import json
    m = repos["main"]
    (m / "asm/fwtask").mkdir(parents=True, exist_ok=True)
    old = (m / "asm/fwtask/fwtask.map").read_text() if (m / "asm/fwtask/fwtask.map").exists() \
        else None
    (m / "asm/fwtask/fwtask.map").write_text(json.dumps(
        {name: {"bytes": len(blob), "insns": 1, "sha256": hashlib.sha256(blob).hexdigest(),
                "source": f"{name}.s", "source_sha256": "0" * 64}},
        indent=1, sort_keys=True) + "\n")
    if (m / "asm/fwtask/fwtask.map").read_text() == old:
        return dict(repos, c1=git(m, "rev-parse", "HEAD"))
    return dict(repos, c1=commit_all(m, "map"))


def own_session(repos, stage=OWN_STAGE, rows=OWN_ROWS, blob=OWN_BLOB, preds="", expect=None):
    """The scaffold's safe s0, then the flagged owntask stage `own` (STAGE) with ROWS, its blob
    file owntask/emitsa.blob (BLOB; None: none) and the map of the fixture blob."""
    r = own_repos(repos)
    kp = scaffold(r)
    st = (kp / "session.toml").read_text()
    (kp / "session.toml").write_text(st.replace("s0 = { alarm = 1800 }",
                                                "s0 = { alarm = 1800 }\n" + stage))
    (kp / "tables/own.txt").write_text("#stage own\n#limit 0\n" + rows)
    (kp / "predictions/own.tsv").write_text("case\tquantity\tvalue\tmodel\tset\tsource\n" + preds)
    if blob is not None:
        (kp / "owntask").mkdir()
        (kp / "owntask/emitsa.blob").write_bytes(blob)
    sc = (kp / "score/score.py").read_text()
    sc = sc.replace('REQUIRED = {"s0": (".txt", "cases.tsv", "void.tsv", "readings.tsv")}',
                    'REQUIRED = {"s0": (".txt", "cases.tsv", "void.tsv", "readings.tsv"), '
                    + OWN_REQUIRED + "}")
    (kp / "score/score.py").write_text(sc)
    w = (kp / "mock/world.py").read_text().replace("def answer(tool, argv, world):\n",
                                                   OWN_WORLD + "def answer(tool, argv, world):\n")
    expect = expect or {"model": (0, {"s0": 0, "own": 0}), "nodiff": (25, {"s0": 25})}
    w = re.sub(r"^EXPECT = .*$", f"EXPECT = {expect!r}", w, count=1, flags=re.M)
    (kp / "mock/world.py").write_text(w)
    return kp, r


def test_the_kit_copies_fwtask_run_and_stages_it_with_the_blob_and_the_job_table(repos):
    assert S.KIT_SOURCES["kit/fwtask_run.py"] == "tools/fwtask/fwtask_run.py"
    assert "kit/fake/fwtask.py" in S.KIT_SOURCES
    kp, r = own_session(repos)
    assert (kp / "kit/fwtask_run.py").read_bytes() == \
        (HERE.parent / "fwtask/fwtask_run.py").read_bytes()
    lap = S.laptop_files(kp)
    for f in ("kit/fwtask_run.py", "owntask/emitsa.blob", "run/owntask.tsv"):
        assert f in lap, lap


def test_lint_and_guard_accept_a_valid_owntask_session(repos):
    kp, r = own_session(repos)
    li = kit(kp, r, "lint")
    assert li.returncode == 0, li.stdout + li.stderr
    g = kit(kp, r, "guard")
    assert g.returncode == 0, g.stdout + g.stderr


OWN_DEBUGFS = ("own_code", "own_arm", "own_res", "load", "boot", "status", "miscinfo", "kreg")


def test_the_preflight_needs_the_debugfs_files_fwtask_run_uses_only_in_an_owntask_session(repos):
    kp, r = own_session(repos)
    S.ENV = env_for(r)
    try:
        env = S.generated(kp)["run/session.env"]
    finally:
        S.ENV = None
    need = re.search(r'^DEBUGFS_NEED="([^"]*)"', env, re.M).group(1).split()
    assert set(OWN_DEBUGFS) <= set(need) and len(need) == len(set(need)), need
    env = S.generated(scaffold(dict(repos, tmp=repos["tmp"] / "plain")))["run/session.env"]
    need = re.search(r'^DEBUGFS_NEED="([^"]*)"', env, re.M).group(1).split()
    assert not set(OWN_DEBUGFS) & set(need), need


def test_prepare_writes_the_arm_and_each_job_for_the_runner(repos):
    import json
    kp, r = own_session(repos)
    S.ENV = env_for(r)
    try:
        tsv = S.generated(kp)["run/owntask.tsv"]
    finally:
        S.ENV = None
    lines = [ln.split("\t") for ln in tsv.splitlines() if ln and not ln.startswith("#")]
    assert lines[0] == ["arm", "own", "emitsa", hashlib.sha256(OWN_BLOB).hexdigest(),
                        "slots=0x1 entry=0"], lines
    jobs = {ln[2]: json.loads(ln[3]) for ln in lines if ln[0] == "job"}
    assert jobs == {"o1": {"n": 1, "params": {}, "runid": 1, "timeout_ms": 100},
                    "o2": {"n": 1, "params": {"32": 7}, "runid": 2, "timeout_ms": 100}}, jobs
    assert all(ln[1] == "own" for ln in lines)


def test_a_session_without_owntask_has_an_empty_job_table(repos):
    kp = scaffold(repos)
    tsv = S.generated(kp)["run/owntask.tsv"]
    assert not [ln for ln in tsv.splitlines() if ln and not ln.startswith("#")], tsv


BAD_ARMS = ["slots=0x1", "slots=0x0 entry=0", "slots=0x1 entry=0 trc_hazard=1",
            "slots=0x3 entry=0", "entry=0 slots=0x1", "slots=0x1 entry=0 trc=32",
            "slots=0x1 entry=0;reboot", "slots=1 entry=0"]


@pytest.mark.parametrize("arm", BAD_ARMS)
def test_lint_refuses_a_bad_arm_string(repos, arm):
    kp, r = own_session(repos, stage=OWN_STAGE.replace("slots=0x1 entry=0", arm))
    li = kit(kp, r, "lint")
    assert li.returncode == 1 and "arm" in li.stdout, li.stdout
    assert kit(kp, r, "guard").returncode != 0


def test_lint_accepts_the_arm_forms_of_the_runner(repos):
    for arm in ("slots=0xf entry=0,1,2,3", "slots=0x1 entry=0 trc=31"):
        kp, r = own_session(dict(repos, tmp=repos["tmp"] / arm.replace(" ", "_")),
                            stage=OWN_STAGE.replace("slots=0x1 entry=0", arm))
        li = kit(kp, r, "lint")
        assert li.returncode == 0, (arm, li.stdout)


def test_lint_refuses_a_missing_blob(repos):
    kp, r = own_session(repos, blob=None)
    li = kit(kp, r, "lint")
    assert li.returncode == 1 and "owntask/emitsa.blob" in li.stdout, li.stdout


def test_lint_refuses_a_blob_that_is_not_the_maps(repos):
    kp, r = own_session(repos, blob=OWN_BLOB + b"\x00")
    li = kit(kp, r, "lint")
    assert li.returncode == 1 and "fwtask.map" in li.stdout and "sha256" in li.stdout, li.stdout


def test_lint_refuses_a_blob_name_the_map_does_not_hold(repos):
    kp, r = own_session(repos, stage=OWN_STAGE.replace('"emitsa"', '"nosuch"'))
    li = kit(kp, r, "lint")
    assert li.returncode == 1 and "nosuch" in li.stdout, li.stdout


def test_lint_refuses_an_owntask_stage_without_a_blob_key(repos):
    kp, r = own_session(repos, stage=OWN_STAGE.replace('blob = "emitsa", ', ""))
    li = kit(kp, r, "lint")
    assert li.returncode == 1 and "blob" in li.stdout, li.stdout


def test_an_owntask_stage_must_be_flagged(repos):
    kp, r = own_session(repos, stage=OWN_STAGE.replace('class = "flagged", ', ""))
    li = kit(kp, r, "lint")
    assert li.returncode == 1 and "flagged" in li.stdout, li.stdout
    g = kit(kp, r, "guard")
    assert g.returncode != 0 and "flagged" in g.stdout, g.stdout


@pytest.mark.parametrize("row,word", [
    ('o3|fit|flagged|-|owntask|{"params": {}, "timeout_ms": 100}', "cmd"),
    ('o3|fit|flagged|-|owntask|{"cmd": 0, "params": {}, "timeout_ms": 100}', "cmd"),
    ('o3|fit|flagged|-|owntask|{"cmd": 1, "params": {"1": 5}, "timeout_ms": 100}', "params"),
    ('o3|fit|flagged|-|owntask|{"cmd": 1, "params": {"1024": 5}, "timeout_ms": 100}', "params"),
    ('o3|fit|flagged|-|owntask|{"cmd": 1, "params": {"x": 5}, "timeout_ms": 100}', "params"),
    ('o3|fit|flagged|-|owntask|{"cmd": 1, "params": {"40": -1}, "timeout_ms": 100}', "params"),
    ('o3|fit|flagged|-|owntask|{"cmd": 1, "params": {}}', "timeout_ms"),
    ('o3|fit|flagged|-|owntask|{"cmd": 1, "params": {}, "timeout_ms": 999999}', "timeout_ms"),
    ('o3|fit|flagged|-|owntask|{"cmd": 1, "params": {}, "timeout_ms": 100, "regs": {}}', "regs"),
    ('o3|fit|flagged|-|owntask|cmd=1', "JSON"),
    ('o3|fit|flagged|kreg:0x0a78=0x01|owntask|{"cmd": 1, "params": {}, "timeout_ms": 100}',
     "kreg"),
    ('o3|fit|flagged|expectfault|owntask|{"cmd": 1, "params": {}, "timeout_ms": 100}',
     "expectfault"),
    ('o3|fit|flagged|noreset|owntask|{"cmd": 1, "params": {}, "timeout_ms": 100}', "noreset"),
    ("o3|fit|flagged|-|t4|tri --width 64 --height 64", "owntask rows only"),
])
def test_lint_refuses_a_malformed_owntask_row(repos, row, word):
    kp, r = own_session(repos, rows=OWN_ROWS + row + "\n")
    li = kit(kp, r, "lint")
    assert li.returncode == 1 and word in li.stdout, li.stdout


def test_an_owntask_row_outside_an_owntask_stage_is_refused(repos):
    kp, r = own_session(repos)
    t = kp / "tables/s0.txt"
    t.write_text(t.read_text() + 'x|fit|safe|-|owntask|{"cmd": 1, "params": {}, '
                 '"timeout_ms": 100}\n')
    li = kit(kp, r, "lint")
    assert li.returncode == 1 and "not an owntask stage" in li.stdout, li.stdout
    g = kit(kp, r, "guard")
    assert g.returncode != 0 and "not an owntask stage" in g.stdout, g.stdout


def test_a_tool_may_not_be_named_owntask(repos):
    kp, r = own_session(repos)
    st = (kp / "session.toml").read_text().replace("[tools.t4]", "[tools.owntask]")
    st = st.replace('health_tool = "t4"', 'health_tool = "owntask"')
    (kp / "session.toml").write_text(st)
    li = kit(kp, r, "lint")
    assert li.returncode == 1 and "owntask" in li.stdout and "reserved" in li.stdout, li.stdout


@pytest.mark.parametrize("qty,ok", [("res:0x44", True), ("res:80", True), ("res:0x400", False),
                                    ("res:x", False)])
def test_lint_reads_a_result_dword_quantity_by_index(repos, qty, ok):
    kp, r = own_session(repos, preds=f"o1\t{qty}\t0x5a5a3301\tH-PA\tfit\tdesign §3\n")
    li = kit(kp, r, "lint")
    assert (li.returncode == 0) is ok, li.stdout
    if not ok:
        assert qty in li.stdout, li.stdout


def test_the_freeze_pins_the_map_the_blob_was_checked_against(repos):
    kp, r = own_session(repos)
    f = kit(kp, r, "freeze")
    assert f.returncode == 0, f.stdout + f.stderr
    commits = (kp / "FROZEN.commits").read_text()
    assert re.search(rf"  {r['c1']}  resgx545:asm/fwtask/fwtask.map$", commits, re.M), commits
    assert "  owntask/emitsa.blob" in (kp / "FROZEN.sha256").read_text()
    v = kit(kp, r, "verify")
    assert v.returncode == 0, v.stdout


def own_log(mm):
    return (mm / "fake/own.log").read_text().splitlines()


def test_an_owntask_stage_arms_once_runs_each_job_without_a_reset_and_disarms(repos):
    import gzip
    import json
    kp, r = own_session(repos)
    m = kit(kp, r, "mock", "--world", "model")
    assert m.returncode == 0, m.stdout + m.stderr
    assert re.search(r"^ok +world model: driver 0 \(s0 0, own 0\)", m.stdout, re.M), m.stdout
    mm = next(kp.glob("debug/mock.*/model"))
    log = own_log(mm)
    own = log[next(i for i, x in enumerate(log) if x.startswith("arm ")):]
    # the gate runs the session's pinned health tool (t4), never the runner's default
    gates = [x for x in own[:8] if x.startswith("gate")]
    assert len(gates) == 2 and all(re.fullmatch(r"gate /\S+/sgxfive-test-rgn4", g)
                                   for g in gates), log
    own = ["gate" if x.startswith("gate") else x for x in own]
    assert own[:8] == ["arm slots=0x1 entry=0", "run o1 n=1 runid=1", "page", "gate",
                       "run o2 n=1 runid=2", "page", "gate", "reset"], log
    kept = mm / "out/model/own"
    page = json.loads(gzip.decompress((kept / "o2.own_res.json.gz").read_bytes()))
    page = page["page"] if isinstance(page, dict) else page
    assert page[0x44] == 0x5a5a3301 and page[32] == 7 and page[3] == 2, page[:64]
    for f in ("owntask.arm.json.gz", "owntask.reset.json.gz", "o1.gate.json.gz", "o1.txt.gz"):
        assert (kept / f).exists(), f
    runner = (kept / "runner.log").read_text()
    assert "## end: 2 jobs of own" in runner, runner
    kmsg = (mm / "kmsg").read_text()
    order = [kmsg.index(s) for s in ("resgx545 r8t owntask-arm own emitsa ", "resgx545 case o1 ",
                                     "resgx545 case o2 ", "resgx545 r8t owntask-disarm own ")]
    assert order == sorted(order), kmsg


@pytest.mark.parametrize("world,rc,word", [
    ("ownarmbad", 26, "## STOP: the own-task arm of emitsa"),
    ("ownstop", 4, "## STOP: unexplained failure in o1"),
    ("owngatebad", 16, "## STOP: the gate after o1 failed"),
])
def test_an_owntask_stage_stops_on_a_bad_arm_a_runner_stop_or_a_failed_gate(repos, world, rc,
                                                                           word):
    kp, r = own_session(repos, expect={world: (rc, {"s0": 0, "own": rc})})
    m = kit(kp, r, "mock", "--world", world)
    assert m.returncode == 0, m.stdout + m.stderr
    mm = next(kp.glob(f"debug/mock.*/{world}"))
    runner = (mm / f"out/{world}/own/runner.log").read_text()
    assert word in runner, runner
    if world == "ownstop":
        assert (mm / f"out/{world}/own/o1.stop0-own_res.json.gz").exists()


def test_the_scorer_reads_a_result_slot_by_dword_index(tmp_path):
    import gzip
    import json
    import kitscore
    d = tmp_path / "kept"
    d.mkdir()
    page = [0] * 1024
    page[0x44], page[0x50] = 0x5a5a3301, 0x5a5a3302
    (d / "o1.own_res.json.gz").write_bytes(gzip.compress(json.dumps({"page": page}).encode()))
    (d / "o2.own_res.json").write_text(json.dumps(page))        # a runner stop dump's form
    assert kitscore.own_res(str(d), "o1") == page
    assert kitscore.own_dword(str(d), "o1", 0x44) == 0x5a5a3301
    assert kitscore.own_dword(str(d), "o2", kitscore.res_index("res:0x50")) == 0x5a5a3302
    assert kitscore.own_slot(str(d), "o1", 1) == [0x5a5a3301, 0, 0, 0]
    assert kitscore.own_dword(str(d), "none", 0x44) is None
    assert kitscore.res_index("diff") is None
    for bad in ("res:0x400", "res:x", "res:-1"):
        with pytest.raises(ValueError):
            kitscore.res_index(bad)


def test_the_kept_check_wants_the_own_res_dump_of_every_owntask_row(tmp_path):
    import sessioncheck
    d = tmp_path / "kept"
    d.mkdir()
    cols = "name\tstage\tset\trisk\tknobs\ttool\targs\trc\tclass\tfault_int\tfault_word\tfree_kb\n"
    (d / "cases.tsv").write_text(cols + "o1\town\tfit\tflagged\t-\towntask\t{}\t0\tok\t-\t-\t1\n")
    (d / "o1.txt").write_text("{}\n")
    probs = sessioncheck.kept_problems(str(d), (".txt",), sessioncheck.kept_classes(str(d)))
    assert any("o1.own_res.json" in p for p in probs), probs
    (d / "o1.own_res.json").write_text("[]\n")
    assert sessioncheck.kept_problems(str(d), (".txt",), sessioncheck.kept_classes(str(d))) == []


@pytest.mark.parametrize("obj,ok", [
    ('{"health": {"ok": true}, "ok": false}', False),
    ('{"fill": "x", "ok": true, "tri": "y"}', True),
    ('{"ok": "true"}', False), ("[true]", False), ("not json", False), ("", False),
    ('{"alive": {}, "ok": true}\n{"ok": false}', False),
])
def test_the_runner_reads_ok_only_at_the_top_of_the_runners_object(tmp_path, obj, ok):
    """fwtask_run.py's arm and reset nest a health object with its own ok: the runner's check
    is the top level's (sessioncheck.py ownok, the laptop's one JSON reader)."""
    f = tmp_path / "o.json"
    f.write_text(obj)
    r = subprocess.run([PY, str(HERE / "sessioncheck.py"), "ownok", str(f)], capture_output=True,
                       text=True)
    assert (r.returncode == 0) is ok, (obj, r.stdout + r.stderr)
    lib = (KIT / "lib_kit.sh").read_text()
    assert 'json_ok() { python3 "$KIT/sessioncheck.py" ownok "$1"; }' in lib


@pytest.mark.parametrize("line", ['owntask_call gate "{}" "$JW/g" "$JW/e" 60',
                                  'sudo -n timeout -k 5 20 python3 "$KIT/fwtask_run.py" page "{}"'])
def test_the_guard_refuses_an_own_task_call_in_a_hook(repos, line):
    kp, r = own_session(repos)
    with open(kp / "run/hooks.sh", "a") as f:
        f.write(f"hook_extra() {{ {line}; }}\n")
    g = kit(kp, r, "guard")
    assert g.returncode != 0 and "hooks.sh" in g.stdout, g.stdout


OWN_TSV = ("arm\town\temitsa\t" + "a" * 64 + "\tslots=0x1 entry=0\n"
           'job\town\to1\t{"n": 1, "params": {}, "runid": 1, "timeout_ms": 100}\n')


def own_runner_tree(tmp, rows, env='FLAGGED_STAGES="own"\n', tsv=OWN_TSV, stage="own"):
    st = tmp / "staged"
    (st / "kit").mkdir(parents=True)
    (st / "run").mkdir()
    (st / "tables").mkdir()
    (st / "kit/run_stage.sh").write_bytes((KIT / "run_stage.sh").read_bytes())
    (st / f"tables/{stage}.txt").write_text(f"#stage {stage}\n#limit 0\n" + rows)
    (st / "run/session.env").write_text('PREFIX=r8t\nTOOLS="t4"\nEXTRA_KNOBS=""\nKNOBS=""\n' + env)
    (st / "run/owntask.tsv").write_text(tsv)
    (st / "FROZEN.sha256").write_text("x\n")
    fz = hashlib.sha256(b"x\n").hexdigest()
    return subprocess.run(["bash", str(st / "kit/run_stage.sh"), stage, fz, "a1"],
                          capture_output=True, text=True, timeout=60,
                          env=dict(PATH=os.environ["PATH"], HOME=str(tmp)))


OWN_ROW = 'o1|fit|flagged|-|owntask|{"cmd": 1, "params": {}, "timeout_ms": 100}\n'


@pytest.mark.parametrize("rows,env,tsv,stage,word", [
    (OWN_ROW, 'FLAGGED_STAGES=""\n', OWN_TSV, "own", "flagged"),
    (OWN_ROW + "t|fit|flagged|-|t4|tri\n", 'FLAGGED_STAGES="own"\n', OWN_TSV, "own",
     "owntask rows only"),
    (OWN_ROW.replace("|-|", "|kreg:0x0a78=0x01|"), 'FLAGGED_STAGES="own"\n', OWN_TSV, "own",
     "kreg"),
    (OWN_ROW, 'FLAGGED_STAGES="own"\n', OWN_TSV.replace("slots=0x1 entry=0", "slots=0x1"),
     "own", "arm"),
    (OWN_ROW, 'FLAGGED_STAGES="own"\n', OWN_TSV.split("job")[0], "own", "no job"),
    (OWN_ROW, 'FLAGGED_STAGES="s0"\n', "", "s0", "not an owntask stage"),
])
def test_the_runner_refuses_an_owntask_table_that_breaks_the_rules(tmp_path, rows, env, tsv,
                                                                   stage, word):
    r = own_runner_tree(tmp_path, rows, env, tsv, stage)
    assert r.returncode == 7 and word in r.stdout, (r.returncode, r.stdout + r.stderr)


def test_the_runner_takes_a_valid_owntask_table(tmp_path):
    r = own_runner_tree(tmp_path, OWN_ROW)
    assert r.returncode == 1 and "is not the frozen one" in r.stdout, (r.returncode, r.stdout)
