# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Tests for tools/waitfor.py: exit 0 met, 124 timeout, 2 usage; no name matching."""
import os
import subprocess
import sys
import time

TOOL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "waitfor.py")


def run(*args):
    return subprocess.run([sys.executable, TOOL, *args], capture_output=True, text=True,
                          timeout=30)


def test_usage_errors():
    assert run().returncode == 2                       # nothing to wait on
    assert run("--file", "/x").returncode == 2         # no timeout
    assert run("--timeout", "1").returncode == 2       # no condition
    assert run("--pid", "abc", "--timeout", "1").returncode == 2
    assert run("--pid", "1", "--timeout", "-1").returncode == 2


def test_pid_exits():
    p = subprocess.Popen(["sleep", "0.5"])
    t = time.time()
    # reap in the background so the pid really disappears
    import threading
    threading.Thread(target=p.wait, daemon=True).start()
    r = run("--pid", str(p.pid), "--timeout", "10")
    assert r.returncode == 0, r.stdout + r.stderr
    assert time.time() - t < 8
    assert len(r.stdout.strip().splitlines()) == 1
    assert str(p.pid) in r.stdout


def test_pid_timeout():
    p = subprocess.Popen(["sleep", "30"])
    try:
        r = run("--pid", str(p.pid), "--timeout", "1")
        assert r.returncode == 124
        assert "timeout" in r.stdout
        assert len(r.stdout.strip().splitlines()) == 1
    finally:
        p.kill()
        p.wait()


def test_already_dead_pid_is_met():
    p = subprocess.Popen(["true"])
    p.wait()
    assert run("--pid", str(p.pid), "--timeout", "5").returncode == 0


def test_eperm_is_alive():
    # pid 1 belongs to another user: EPERM must count as alive
    r = run("--pid", "1", "--timeout", "1")
    assert r.returncode == 124


def test_multiple_pids_all_must_exit():
    p = subprocess.Popen(["sleep", "30"])
    try:
        q = subprocess.Popen(["true"])
        q.wait()
        assert run("--pid", str(q.pid), "--pid", str(p.pid), "--timeout", "1").returncode == 124
    finally:
        p.kill()
        p.wait()


def test_pidfile(tmp_path):
    f = tmp_path / "x.pid"
    p = subprocess.Popen(["sleep", "30"])
    f.write_text(f"{p.pid}\n")
    try:
        assert run("--pidfile", str(f), "--timeout", "1").returncode == 124
    finally:
        p.kill()
        p.wait()
    assert run("--pidfile", str(f), "--timeout", "5").returncode == 0


def test_pidfile_bad(tmp_path):
    f = tmp_path / "bad.pid"
    f.write_text("nonsense\n")
    assert run("--pidfile", str(f), "--timeout", "1").returncode == 2
    assert run("--pidfile", str(tmp_path / "missing"), "--timeout", "1").returncode == 2


def test_file(tmp_path):
    f = tmp_path / "done"
    assert run("--file", str(f), "--timeout", "1").returncode == 124
    p = subprocess.Popen([sys.executable, "-c",
                          f"import time;time.sleep(0.5);open({str(f)!r},'w').close()"])
    r = run("--file", str(f), "--timeout", "10")
    p.wait()
    assert r.returncode == 0
    assert "met" in r.stdout
