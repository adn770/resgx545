# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Parallel runs (pytest -n N, tools/check.sh): the tests of several files build the same tool
directories and cargo targets, and make or cargo racing on one output corrupts it. The
controller builds them once before the workers start; the builds the tests make themselves
are then no-ops."""
import pathlib
import shutil
import sys
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent
PREBUILD = [
    ["make", "-s", "-C", "tools/usse-dis", "usse-dis", "pds-dis", "pingen"],
    ["make", "-s", "-C", "tools/usse-asm"],
    ["cargo", "build", "-q", "-p", "sgx-tools"],
    ["cargo", "build", "-q", "--release", "-p", "sgx-tools", "--bin", "sgx-sim"],
]
# Modules whose warning classes a worker reports: the controller imports them to show the warning
# (xdist fails with ModuleNotFoundError otherwise).
WARNING_PATHS = ["tools/fwtask"]


def wants_prebuild(numprocesses, workerinput) -> bool:
    """True on the controller of a parallel run, not on a worker and not in a serial run."""
    return bool(numprocesses) and workerinput is None


def pytest_configure(config):
    if wants_prebuild(getattr(config.option, "numprocesses", None),
                      getattr(config, "workerinput", None)):
        sys.path += [str(ROOT / p) for p in WARNING_PATHS]
        for cmd in PREBUILD:
            if shutil.which(cmd[0]):
                subprocess.run(cmd, cwd=ROOT, check=False)
