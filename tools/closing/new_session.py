#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""new_session.py: scaffold a closing session on the session kit (HACKING.md, "Session kit").

  new_session.py DIR --name r8-x --prefix r8x --srcversion SRCV --tool t4=PATH:SHA256 [--tool ...]
                 [--resgx545 REPO] [--commit REV] [--data REPO] [--data-commit REV]

DIR must not exist or be empty. The kit (tools/closing/kit, scorekit.py, sessioncheck.py) is
copied into DIR/kit from the blobs of resgx545 REV (default: its HEAD), never from a working tree,
and session.toml freezes against REV and the data repository's REV, so main and data may move
while the session is built and run. Then: session.toml (the env), tables/s0.txt, predictions/,
score/score.py (scorekit-based), mock/world.py (answers by argv), run/hooks.sh, tests/run_all.sh
and README.md, each a working example to replace. A tool's PATH is under the laptop's home.
"""
import argparse
import os
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "kit"))
import session as S  # noqa: E402

TEMPLATES = HERE / "kit" / "templates"


def git(repo, *args, binary=False):
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, timeout=60)
    if r.returncode:
        raise SystemExit(f"git -C {repo} {' '.join(args)}: {r.stderr.decode().strip()}")
    return r.stdout if binary else r.stdout.decode().strip()


def main(argv=None):
    home = pathlib.Path.home()
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("dir")
    ap.add_argument("--name", required=True)
    ap.add_argument("--prefix", required=True)
    ap.add_argument("--srcversion", required=True)
    ap.add_argument("--tool", action="append", required=True, metavar="NAME=PATH:SHA256")
    ap.add_argument("--resgx545", default=str(home / "src/resgx545"))
    ap.add_argument("--commit", default="HEAD")
    ap.add_argument("--data", default=str(home / "src/resgx545-data"))
    ap.add_argument("--data-commit", default="HEAD")
    a = ap.parse_args(argv)
    kp = pathlib.Path(a.dir)
    if kp.exists() and any(kp.iterdir()):
        print(f"{kp} exists and is not empty")
        return 1
    if not re.fullmatch(r"[a-z][a-z0-9]{1,15}", a.prefix):
        print(f"prefix {a.prefix!r} is not a short lower-case name")
        return 1
    tools = []
    for t in a.tool:
        m = re.fullmatch(r"([a-z][a-z0-9]*)=([^:/][^:]*):([0-9a-f]{64})", t)
        if not m:
            print(f"--tool {t!r} is not NAME=PATH:SHA256 (PATH under the laptop's home)")
            return 1
        tools.append(m.groups())
    commit = git(a.resgx545, "rev-parse", "--verify", f"{a.commit}^{{commit}}")
    data_commit = git(a.data, "rev-parse", "--verify", f"{a.data_commit}^{{commit}}")
    for rel, src in S.KIT_SOURCES.items():
        p = kp / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(git(a.resgx545, "show", f"{commit}:{src}", binary=True))
        if rel.endswith((".sh", ".py")) or "/fake/" in rel:
            p.chmod(0o755)
    toolspec = "\n".join(f'[tools.{n}]\npath = "{p}"\nsha256 = "{h}"\n' for n, p, h in tools)
    subst = {"@NAME@": a.name, "@PREFIX@": a.prefix, "@SRCV@": a.srcversion,
             "@HEALTH@": tools[0][0], "@COMMIT@": commit, "@COMMIT12@": commit[:12],
             "@DATA_COMMIT@": data_commit, "@TOOLS@": toolspec}
    for t in sorted(TEMPLATES.rglob("*")):
        if not t.is_file():
            continue
        text = t.read_text()
        for k, v in subst.items():
            text = text.replace(k, v)
        out = kp / t.relative_to(TEMPLATES)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text)
        out.chmod(t.stat().st_mode & 0o777)
    S.prepare(kp)
    print(f"{kp}: kit from resgx545 {commit[:12]}, data {data_commit[:12]}; next: edit the "
          "tables, predictions, scorer and world, then tests/run_all.sh")
    return 0


if __name__ == "__main__":
    sys.exit(main())
