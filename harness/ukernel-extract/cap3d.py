#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""A 3D capture table's data, as the campaign runner keeps it (capture3d_host.sh: one
<run>.tar.xz per run of the list, runs.txt with capture3d.sh's line per run), unpacked into
the var/ layout capture3d.sh leaves (<dest>/<run>/dump3d/, tri.out, drm.log, powervr.ini), the
layout diff3d.py, state3d.py, tiling3d.py and kickwalk.py read. A run is unpacked again only
when its archive changed (a stamp file holds the archive's sha256).

    cap3d.py unpack DATA DEST     unpack every run of DATA (resgx545-data-private/<unit>/
                                  <feature>/) into DEST, one line per run
    cap3d.py status DATA          each run's status and kick count (runs.txt)
"""
from __future__ import annotations

import hashlib
import pathlib
import re
import shutil
import sys
import tarfile

STAMP = ".cap3d-sha256"


def _sha(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def unpack(data: pathlib.Path, dest: pathlib.Path) -> list[pathlib.Path]:
    """Unpack each <run>.tar.xz of data into dest/<run>/, dropping the stamped run directories
    whose archive is gone; the run directories, by name."""
    data, dest = pathlib.Path(data), pathlib.Path(dest)
    out = []
    archives = sorted(data.glob("*.tar.xz"))
    have = {a.name.removesuffix(".tar.xz") for a in archives}
    if dest.is_dir():                    # a run directory of ours (stamped) without an archive
        for old in dest.iterdir():
            if old.is_dir() and (old / STAMP).exists() and old.name not in have:
                shutil.rmtree(old)
    for a in archives:
        run = dest / a.name.removesuffix(".tar.xz")
        sha = _sha(a)
        stamp = run / STAMP
        if not (stamp.exists() and stamp.read_text().strip() == sha):
            if run.exists():
                shutil.rmtree(run)
            run.mkdir(parents=True)
            with tarfile.open(a, "r:xz") as t:
                t.extractall(run, filter="data")     # refuses members outside run/
            stamp.write_text(sha + "\n")
        out.append(run)
    return out


def status(data: pathlib.Path) -> dict[str, tuple[str, int]]:
    """{run: (status, kicks)} from runs.txt ("name: ok, 2 kicks")."""
    out = {}
    for ln in (pathlib.Path(data) / "runs.txt").read_text().splitlines():
        m = re.fullmatch(r"(\S+): (.+), (\d+) kicks", ln.strip())
        if m:
            out[m.group(1)] = (m.group(2), int(m.group(3)))
    return out


def main(argv: list[str]) -> int:
    if len(argv) == 3 and argv[0] == "unpack":
        for run in unpack(pathlib.Path(argv[1]), pathlib.Path(argv[2])):
            print(run.name)
        return 0
    if len(argv) == 2 and argv[0] == "status":
        for name, (st, kicks) in status(pathlib.Path(argv[1])).items():
            print(f"{name}\t{st}\t{kicks}")
        return 0
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
