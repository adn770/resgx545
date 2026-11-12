#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""waitfor.py: wait for work to finish, with a timeout (HACKING.md, "Waiting on work").

  waitfor.py --timeout SECONDS (--pid N)... [--pidfile F]... [--file F]...

Waits until every named PID (or the PID in each pidfile) has exited and every named file exists.
A PID is polled with os.kill(pid, 0) (a non-child cannot be wait()ed on; EPERM means alive).
Nothing is matched by name or command line: a name pattern also matches the waiting shell
itself and never ends. Prints one line: what it waited on, how long, why it stopped.
Exit 0 when met, 124 on timeout (as timeout(1)), 2 on a usage error. Standard library only.
"""
import argparse
import errno
import os
import sys
import time

POLL = 0.2


def alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError as e:
        return e.errno == errno.EPERM
    return True


def read_pidfile(path):
    try:
        with open(path) as f:
            text = f.read().split()
        pid = int(text[0])
    except (OSError, ValueError, IndexError):
        raise ValueError(f"pidfile {path} does not hold a PID")
    if pid <= 0:
        raise ValueError(f"pidfile {path} does not hold a PID")
    return pid


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], add_help=True)
    ap.add_argument("--pid", type=int, action="append", default=[], metavar="N")
    ap.add_argument("--pidfile", action="append", default=[], metavar="F")
    ap.add_argument("--file", action="append", default=[], metavar="F")
    ap.add_argument("--timeout", type=float, required=True, metavar="SECONDS")
    try:
        a = ap.parse_args(argv)
    except SystemExit as e:
        return 2 if e.code else 0
    if a.timeout < 0 or not (a.pid or a.pidfile or a.file) or any(p <= 0 for p in a.pid):
        print("waitfor: need --timeout >= 0 and a --pid, --pidfile or --file", file=sys.stderr)
        return 2
    pids = list(a.pid)
    try:
        pids += [read_pidfile(f) for f in a.pidfile]
    except ValueError as e:
        print(f"waitfor: {e}", file=sys.stderr)
        return 2
    what = ([f"pid {p}" for p in pids] + [f"file {f}" for f in a.file])
    what = ", ".join(what)
    start = time.monotonic()
    while True:
        waiting = [p for p in pids if alive(p)] + [f for f in a.file if not os.path.exists(f)]
        took = time.monotonic() - start
        if not waiting:
            print(f"waitfor: {what}: {took:.1f}s: met")
            return 0
        if took >= a.timeout:
            print(f"waitfor: {what}: {took:.1f}s: timeout after {a.timeout:g}s")
            return 124
        time.sleep(min(POLL, max(0.0, a.timeout - took)))


if __name__ == "__main__":
    sys.exit(main())
