# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""session_tests.sh's pass cache: a pass is recorded under $RESGX545_SESSION_TARGET/passes/,
keyed by the session's path and files, the runner's own digest, the commits the session pins
(the tool tree's HEAD when it pins none) and PY; --cached skips a run whose key passed."""
import os
import pathlib
import subprocess

import passcache
from test_session_tests import SCRIPT, git, world  # noqa: F401  (the toy world fixture)


def run(world, *args, **extra):
    tool, data, py = world
    env = {**os.environ, "RESGX545_TOOL": str(tool), "RESGX545_DATA": str(data), "PY": str(py),
           "RESGX545_SESSION_TARGET": str(tool.parent / "session-target")}
    env.update(extra)
    return subprocess.run(["bash", str(SCRIPT), *args], env=env, capture_output=True,
                          text=True, timeout=120)


def passes(world):
    d = world[0].parent / "session-target" / "passes"
    return sorted(d.iterdir()) if d.is_dir() else []


def test_a_pass_is_recorded_and_the_default_still_runs(world):
    r = run(world, "edm/closing-demo")
    assert r.returncode == 0, r.stdout + r.stderr
    assert len(passes(world)) == 1
    assert "edm/closing-demo" in passes(world)[0].read_text()
    r = run(world, "edm/closing-demo")
    assert "RUN_ALL PASSED" in r.stdout and "CACHED" not in r.stdout
    assert len(passes(world)) == 1


def test_cached_skips_a_run_whose_key_passed(world):
    r = run(world, "--cached", "edm/closing-demo")
    assert r.returncode == 0 and "RUN_ALL PASSED" in r.stdout    # nothing cached yet
    r = run(world, "--cached", "edm/closing-demo")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "RUN_ALL PASSED" not in r.stdout
    assert "session_tests: edm/closing-demo CACHED PASS" in r.stdout


def test_a_failure_records_nothing(world):
    r = run(world, "edm/closing-demo", DEMO_RC="3")
    assert r.returncode == 3 and passes(world) == []
    r = run(world, "--cached", "edm/closing-demo", DEMO_RC="3")
    assert r.returncode == 3 and "CACHED" not in r.stdout


def test_a_changed_session_file_or_python_runs_again(world, tmp_path):
    tool, data, py = world
    assert run(world, "edm/closing-demo").returncode == 0
    (data / "edm/closing-demo/README.md").write_text("changed\n")
    r = run(world, "--cached", "edm/closing-demo")
    assert "RUN_ALL PASSED" in r.stdout
    py2 = tmp_path / "py2"
    py2.write_text(py.read_text())
    py2.chmod(0o755)
    r = run(world, "--cached", "edm/closing-demo", PY=str(py2))
    assert "RUN_ALL PASSED" in r.stdout
    assert len(passes(world)) == 3


def test_cached_alone_is_a_usage_error(world):
    assert run(world, "--cached").returncode == 2


def test_the_key_follows_the_pins_and_the_runner(world, tmp_path):
    tool, data, py = world
    s = data / "edm/closing-demo"
    runner = tmp_path / "runner.sh"
    runner.write_text("a\n")
    k = passcache.key(s, tool, str(py), [runner])
    assert k == passcache.key(s, tool, str(py), [runner])
    (tool / "tools/y.py").write_text("y\n")         # a new tool commit: the pins hold
    git(tool, "add", ".")
    git(tool, "commit", "-qm", "y")
    assert passcache.key(s, tool, str(py), [runner]) == k
    runner.write_text("b\n")
    assert passcache.key(s, tool, str(py), [runner]) != k
    (s / "FROZEN.commits").unlink()                 # no pins: the tool tree's HEAD counts
    k2 = passcache.key(s, tool, str(py), [runner])
    (tool / "tools/z.py").write_text("z\n")
    git(tool, "add", ".")
    git(tool, "commit", "-qm", "z")
    assert passcache.key(s, tool, str(py), [runner]) != k2


def test_the_key_names_its_parts():
    parts = passcache.parts(pathlib.Path(__file__).parent, pathlib.Path(__file__).parents[2],
                            "python3", [pathlib.Path(__file__)])
    assert [p.split(" ", 1)[0] for p in parts] == ["session", "files", "runner", "commits",
                                                    "py"]


def test_the_cli_prints_the_key(world):
    tool, data, py = world
    out = subprocess.run(
        ["python3", str(pathlib.Path(passcache.__file__)), "key", str(data / "edm/closing-demo"),
         str(tool), str(py), __file__], capture_output=True, text=True, check=True).stdout
    assert out.strip() == passcache.key(data / "edm/closing-demo", tool, str(py),
                                        [pathlib.Path(__file__)])
