# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The session kit (tools/closing/kit, HACKING.md "Session kit"): a closing session declares its
tables, predictions, scorer and env, and the kit supplies the laptop runner, the Mac driver, the
staging list, the freeze pinned by commit, the static guard and the argv-driven mock. Each case
is one of the slips of rounds 5-7 made impossible: an unstaged lib, a dump directory never made,
a control that could not be read, /tmp, a mock that leaned on milliseconds, a freeze that broke
when main moved."""
import hashlib
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
                assert re.search(r'sleep "\$\{(RESET_WAIT|HEALTH_WAIT|TEE_GRACE):-[0-9]+\}"',
                                 ln), ln
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
