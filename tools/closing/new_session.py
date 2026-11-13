#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""new_session.py: scaffold a closing session on the session kit (HACKING.md, "Session kit").

  new_session.py DIR --name r8-x --prefix r8x --srcversion SRCV --tool t4=PATH:SHA256 [--tool ...]
                 [--tool-src NAME=COMMIT:PATH@RECIPE]
                 [--no-source NAME=REASON] [--resgx545 REPO] [--commit REV] [--data REPO] [--data-commit REV]

DIR must not exist or be empty. The kit (tools/closing/kit, scorekit.py, sessioncheck.py) is
copied into DIR/kit from the blobs of resgx545 REV (default: its HEAD), never from a working tree,
and session.toml freezes against REV and the data repository's REV, so main and data may move
while the session is built and run. Then: session.toml (the env), tables/s0.txt, predictions/,
score/score.py (scorekit-based), mock/world.py (answers by argv), run/hooks.sh, tests/run_all.sh
and README.md, each a working example to replace. A tool's PATH is under the laptop's home.

--tool-src binds a tool's binary to its source: the source file PATH of resgx545 at COMMIT and the
RECIPE that built it (data:PATH, or PATH of the resgx545 tree). It writes TOOLSRC.sha256
(`<sha256>  <commit>:<path>`) and the tool's built_from, built_sha256 and recipe into session.toml;
the freeze then writes the `built` line of FROZEN.commits and the binary's freeze line.
"""
import argparse
import hashlib
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


def library_mock(name, src):
    """The `source` pair the kit's library-mock replay builds from, for the tool whose source it
    can build (libsgxfive's sgxfive-test); any other tool has no library mock."""
    commit, path, sha, _ = src
    if path == "userspace/libsgxfive/tools/sgxfive-test.c":
        return f'source = "{commit}:{path}"\nsource_sha256 = "{sha}"\n'
    return f'no_source = "built from {path}: not a library-mock tool"\n'


def main(argv=None):
    home = pathlib.Path.home()
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("dir")
    ap.add_argument("--name", required=True)
    ap.add_argument("--prefix", required=True)
    ap.add_argument("--srcversion", required=True)
    ap.add_argument("--tool", action="append", required=True, metavar="NAME=PATH:SHA256")
    ap.add_argument("--tool-src", action="append", default=[], metavar="NAME=COMMIT:PATH@RECIPE")
    ap.add_argument("--no-source", action="append", default=[], metavar="NAME=REASON")
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
    srcs = {}
    for s in a.tool_src:
        m = re.fullmatch(r"([a-z][a-z0-9]*)=([^:@]+):([^:@]+)@(\S+)", s)
        if not m or m[1] not in {n for n, _, _ in tools} or m[1] in srcs:
            print(f"--tool-src {s!r} is not NAME=COMMIT:PATH@RECIPE of a --tool, once")
            return 1
        full = git(a.resgx545, "rev-parse", "--verify", f"{m[2]}^{{commit}}")
        blob = git(a.resgx545, "show", f"{full}:{m[3]}", binary=True)
        srcs[m[1]] = (full, m[3], hashlib.sha256(blob).hexdigest(), m[4])
    data_commit = git(a.data, "rev-parse", "--verify", f"{a.data_commit}^{{commit}}")
    nosrc = {}
    for s in a.no_source:
        n, _, why = s.partition("=")
        if n not in {x for x, _, _ in tools} or n in srcs or n in nosrc or not why.strip():
            print(f"--no-source {s!r} is not NAME=REASON of a --tool without a --tool-src")
            return 1
        nosrc[n] = why.strip().replace('"', "'")
    for n, _, _ in tools:
        if n not in srcs and n not in nosrc:
            print(f"tool {n}: give --tool-src or --no-source (a reason it has no library mock): "
                  "a tool with neither is never replayed on the library mock")
            return 1
    for rel, src in S.KIT_SOURCES.items():
        p = kp / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(git(a.resgx545, "show", f"{commit}:{src}", binary=True))
        if rel.endswith((".sh", ".py")) or "/fake/" in rel:
            p.chmod(0o755)
    toolspec = "\n".join(
        f'[tools.{n}]\npath = "{p}"\nsha256 = "{h}"\n' + (
            f'built_from = "{srcs[n][0]}:{srcs[n][1]}"\nbuilt_sha256 = "{srcs[n][2]}"\n'
            f'recipe = "{srcs[n][3]}"\n' + library_mock(n, srcs[n])
            if n in srcs else f'no_source = "{nosrc[n]}"\n') for n, p, h in tools)
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
    if srcs:
        (kp / "TOOLSRC.sha256").write_text("".join(
            f"{sh}  {cm}:{path}\n" for cm, path, sh, _ in srcs.values()))
    S.prepare(kp)
    print(f"{kp}: kit from resgx545 {commit[:12]}, data {data_commit[:12]}; next: edit the "
          "tables, predictions, scorer and world, then tests/run_all.sh")
    return 0


if __name__ == "__main__":
    sys.exit(main())
