# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""build-igt.sh and build-igt-host.sh on a toy IGT clone: the "build host" is this machine
(`sh -c` in place of ssh, HOME a temporary directory), and docker is a fake that acts out meson
and ninja (each requested ninja target becomes a small i686 ELF file) and answers a binary's
`--list-subtests`. Nothing here touches the real IGT fork, the build host or the laptop."""
from __future__ import annotations

import hashlib
import os
import pathlib
import subprocess

import pytest

HERE = pathlib.Path(__file__).resolve().parent
BUILD = HERE / "build-igt.sh"
HOST = HERE / "build-igt-host.sh"
IMG = "sgxhumation/arch32:igt"
MESON = """sgxfive_progs = [
\t'sgxfive_ctx',
\t'sgxfive_gem',
]
"""

# docker run ... -v X:/w ... IMG bash -c CMD | docker run ... IMG /w/.../NAME --list-subtests
# | docker image inspect -f ... IMG
FAKE = r"""#!/bin/bash
echo "docker $*" >> "$HOME/docker.log"
if [ "$1 $2" = "image inspect" ]; then echo "sha256:fakeimage"; exit 0; fi
args=("$@")
w=
for a in "${args[@]}"; do case $a in *:/w) w=${a%:/w} ;; esac; done
[ -n "$w" ] || { echo "fake docker: no /w mount" >&2; exit 1; }
last=${args[${#args[@]}-1]}
if [ "$last" = --list-subtests ]; then
    bin=${args[${#args[@]}-2]}
    name=$(basename "$bin")
    [ -f "$w/${bin#/w/}" ] || { echo "no such binary $bin" >&2; exit 127; }
    [ "$name" = "${FAKE_SMOKE_FAIL:-}" ] && { echo "IGT-Version: x" ; exit 79; }
    printf '%s-basic\n%s-other\n' "$name" "$name"
    exit 0
fi
cmd=$last
[[ $cmd == *"meson setup /w/build"* ]] || { echo "fake docker: no meson setup" >&2; exit 1; }
[ -f "$w/src/tests/sgxfive/meson.build" ] || { echo "fake docker: no source" >&2; exit 1; }
[ -e "$w/src/.git" ] && { echo "fake docker: a .git in the source" >&2; exit 1; }
mkdir -p "$w/build"
[ -n "${FAKE_BUILD_FAIL:-}" ] && { echo "ninja: build stopped: subcommand failed." ; exit 1; }
for t in $(grep -oE '(tests/sgxfive/[a-z_]+|lib/libigt\.so\.0)' <<< "${cmd#*ninja}"); do
    mkdir -p "$w/build/$(dirname "$t")"
    printf '\177ELF\001\001\001\000\000\000\000\000\000\000\000\000\002\000%b\000%s' \
        "${FAKE_MACHINE:-\\003}" "$t $(cat "$w/src/tests/sgxfive/a.c")" > "$w/build/$t"
done
"""


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
                          check=True).stdout.strip()


def commit(repo, subject, files):
    for path, text in files.items():
        (repo / path).parent.mkdir(parents=True, exist_ok=True)
        (repo / path).write_text(text)
    git(repo, "add", "-A")
    git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", subject)
    return git(repo, "rev-parse", "HEAD")


@pytest.fixture
def world(tmp_path):
    clone = tmp_path / "igt"
    clone.mkdir()
    git(clone, "init", "-q", "-b", "master")
    base = commit(clone, "igt", {"meson.build": "project('igt')\n",
                                 "tests/sgxfive/meson.build": MESON,
                                 "tests/sgxfive/a.c": "one\n"})
    git(clone, "checkout", "-q", "-b", "sgxfive")
    c1 = commit(clone, "tests/sgxfive: two", {"tests/sgxfive/a.c": "two\n"})
    git(clone, "checkout", "-q", "master")
    other = commit(clone, "elsewhere", {"x.c": "x\n"})
    host = tmp_path / "hosthome"
    host.mkdir()
    bindir = tmp_path / "bin"
    bindir.mkdir()
    (bindir / "docker").write_text(FAKE)
    (bindir / "docker").chmod(0o755)
    env = {**{k: v for k, v in os.environ.items() if not k.startswith(("SGX_", "IGT_"))},
           "PATH": f"{bindir}:{os.environ['PATH']}", "HOME": str(host),
           "SGX_LOCAL_ENV": os.devnull, "IGT_BUILD_SSH": "sh -c", "IGT_CLONE": str(clone),
           "IGT_BUILD_WORK": "igtw", "IGT_OUT": str(tmp_path / "out")}
    return dict(clone=clone, host=host, base=base, c1=c1, other=other, env=env, tmp=tmp_path)


def run(w, rev, **extra):
    return subprocess.run([str(BUILD), rev], env={**w["env"], **extra}, capture_output=True,
                          text=True, timeout=60)


def manifest(w, rev):
    text = (w["tmp"] / "out" / rev[:12] / "manifest").read_text()
    return dict(line.split("=", 1) for line in text.splitlines() if "=" in line)


def docker_log(w):
    p = w["host"] / "docker.log"
    return p.read_text() if p.exists() else ""


def test_scripts_are_valid_bash_and_executable():
    for p in (BUILD, HOST):
        assert os.access(p, os.X_OK), p
        subprocess.run(["bash", "-n", str(p)], check=True)


def test_builds_the_sgxfive_tests_and_writes_the_manifest(world):
    w = world
    r = run(w, "sgxfive")
    assert r.returncode == 0, r.stdout + r.stderr
    out = w["tmp"] / "out" / w["c1"][:12]
    m = manifest(w, w["c1"])
    assert m["commit"] == w["c1"]
    assert m["image"] == IMG and m["image_id"] == "sha256:fakeimage"
    assert m["binaries"] == "sgxfive_ctx sgxfive_gem"
    for name in ("sgxfive_ctx", "sgxfive_gem", "libigt.so.0"):
        assert m[f"sha256.{name}"] == hashlib.sha256((out / name).read_bytes()).hexdigest()
    assert m["smoke.sgxfive_ctx"] == "ok 2" and m["smoke.sgxfive_gem"] == "ok 2"
    assert m["smoke"] == "pass"
    assert "two" in (out / "sgxfive_ctx").read_text(errors="replace")
    assert str(out / "manifest") in r.stdout


def test_every_build_and_smoke_runs_in_the_image_from_a_plain_archive(world):
    w = world
    assert run(w, w["c1"]).returncode == 0
    log = docker_log(w).splitlines()
    runs = [l for l in log if l.startswith("docker run")]
    assert runs and all(IMG in l for l in runs)
    [build] = [l for l in runs if "meson setup" in l]
    assert "ninja -C /w/build" in build and "tests/sgxfive/sgxfive_ctx" in build
    assert "lib/libigt.so.0" in build and "-Drunner=enabled" in build
    smokes = [l for l in runs if l.endswith("--list-subtests")]
    assert len(smokes) == 2 and all("LD_LIBRARY_PATH=/w/build/lib" in l for l in smokes)


def test_a_smoke_failure_is_recorded_and_fails(world):
    w = world
    r = run(w, w["c1"], FAKE_SMOKE_FAIL="sgxfive_gem")
    assert r.returncode != 0
    m = manifest(w, w["c1"])
    assert m["smoke"] == "fail" and m["smoke.sgxfive_gem"].startswith("FAILED rc=79")
    assert "smoke" in r.stderr


def test_a_failed_build_reports_the_log_and_delivers_nothing(world):
    w = world
    r = run(w, w["c1"], FAKE_BUILD_FAIL="1")
    assert r.returncode != 0
    assert "subcommand failed" in r.stdout + r.stderr
    assert not (w["tmp"] / "out" / w["c1"][:12] / "manifest").exists()


def test_a_binary_that_is_not_i686_is_refused(world):
    w = world
    r = run(w, w["c1"], FAKE_MACHINE="\\076")
    assert r.returncode != 0
    assert "i686" in r.stderr
    assert not (w["tmp"] / "out" / w["c1"][:12] / "manifest").exists()


def test_a_commit_off_the_sgxfive_branch_is_refused(world):
    w = world
    r = run(w, w["other"])
    assert r.returncode != 0
    assert "sgxfive" in r.stderr and "IGT_FORCE" in r.stderr
    assert docker_log(w) == ""
    r = run(w, w["other"], IGT_FORCE="1")
    assert r.returncode == 0, r.stdout + r.stderr
    assert manifest(w, w["other"])["branch"] == "forced"
    assert run(w, w["base"]).returncode == 0                   # an ancestor is on the branch
    assert manifest(w, w["base"])["branch"] == "sgxfive"
