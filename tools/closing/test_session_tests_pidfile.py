# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""session_tests.sh names a pidfile in its output, holding its own PID while it runs, so a
waiter (tools/waitfor.py --pidfile) has something exact; the file is gone when it exits."""
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "session_tests.sh")


def test_pidfile_named_and_removed(tmp_path):
    data = tmp_path / "data"
    data.mkdir()
    target = tmp_path / "target"
    env = dict(os.environ, RESGX545_DATA=str(data), RESGX545_SESSION_TARGET=str(target))
    r = subprocess.run(["bash", SCRIPT, "area/closing-nosuch"], capture_output=True, text=True,
                       env=env)
    assert r.returncode == 2
    m = re.search(r"session_tests: pidfile (\S+) \(pid (\d+)\)", r.stdout)
    assert m, r.stdout + r.stderr
    assert m.group(1) == str(target / "session_tests.pid")
    assert not os.path.exists(m.group(1))


def test_usage_error_writes_no_pidfile(tmp_path):
    target = tmp_path / "target"
    env = dict(os.environ, RESGX545_SESSION_TARGET=str(target))
    r = subprocess.run(["bash", SCRIPT], capture_output=True, text=True, env=env)
    assert r.returncode == 2
    assert "pidfile" not in r.stdout
