# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""deliver-module.sh and build-module.sh on toy repositories: the "build host" is the same
machine (`sh -c` in place of ssh, HOME a temporary directory holding its clone), and docker
and systemd-nspawn are one fake that acts out kbuild's part: a full build writes
Module.symvers, modules_prepare writes kernel.release (with the '+' of a git tree unless
LOCALVERSION is set empty), the M= build writes a gma500_gfx.ko whose .modinfo carries that
release. Nothing here touches a real fork, host or laptop."""
from __future__ import annotations

import hashlib
import os
import pathlib
import subprocess

import pytest

HERE = pathlib.Path(__file__).resolve().parent
DELIVER = HERE / "deliver-module.sh"
BUILD = HERE / "build-module.sh"
KREL = "7.3.0-resgx545"
VERMAGIC = f"{KREL} SMP preempt mod_unload 686"
GMA = "drivers/gpu/drm/gma500"

# The fake runner: docker run ... -v SRC:/k:ro -v B:/b ... sh -c CMD, or
# sudo systemd-nspawn ... --bind-ro=SRC:/k --bind=B:/b ... sh -c CMD.
FAKE = r"""#!/bin/bash
echo "$(basename "$0") $*" >> "$HOME/runner.log"
args=("$@")
k= b=
for a in "${args[@]}"; do
    case $a in
    *:/k:ro) k=${a%:/k:ro} ;;
    --bind-ro=*:/k) k=${a#--bind-ro=}; k=${k%:/k} ;;
    --bind=*:/b) b=${a#--bind=}; b=${b%:/b} ;;
    *:/b) b=${a%:/b} ;;
    esac
done
cmd=${args[${#args[@]}-1]}
[ -n "$k" ] && [ -n "$b" ] || { echo "fake runner: no /k or /b mount" >&2; exit 1; }
if [[ $cmd == *" vmlinux modules"* ]]; then
    echo full >> "$HOME/builds.log"
    : > "$b/Module.symvers"
fi
if [[ $cmd == *modules_prepare* ]]; then
    mkdir -p "$b/include/config"
    if [[ $cmd =~ LOCALVERSION=\  ]]; then r=$FAKE_RELEASE; else r=$FAKE_RELEASE+; fi
    echo "$r" > "$b/include/config/kernel.release"
fi
if [[ $cmd == *"M=/k/drivers/gpu/drm/gma500 "* ]]; then
    echo "module git=$([ -e "$k/.git" ] && echo yes || echo no) $(cat "$k/drivers/gpu/drm/gma500/a.c")" >> "$HOME/builds.log"
    [ -f "$b/Module.symvers" ] || { echo "no Module.symvers" >&2; exit 1; }
    mkdir -p "$b/drivers/gpu/drm/gma500"
    src=$(cksum < "$k/drivers/gpu/drm/gma500/a.c" | cut -c1-8)
    printf '\177ELF\0srcversion=%s\0depends=video\0vermagic=%s SMP preempt mod_unload 686%s \0' \
        "$src" "$(cat "$b/include/config/kernel.release")" "${FAKE_SUFFIX:-}" \
        > "$b/drivers/gpu/drm/gma500/gma500_gfx.ko"
fi
exit 0
"""
SUDO = """#!/bin/bash
[ "$1" = systemd-nspawn ] || { echo "fake sudo: $*" >&2; exit 1; }
exec "$(dirname "$0")/systemd-nspawn" "${@:2}"
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


def write_exec(path, text):
    path.write_text(text)
    path.chmod(0o755)


@pytest.fixture
def world(tmp_path):
    """home: the fork clone (base, c1 changes gma500 only, c2 changes something else, c3
    gma500 again); hosthome: the build host's $HOME with its clone of it and the config."""
    home = tmp_path / "home"
    home.mkdir()
    git(home, "init", "-q", "-b", "main")
    base = commit(home, "Linux 7.3", {f"{GMA}/a.c": "int a;\n", "mm/m.c": "int m;\n"})
    c1 = commit(home, "drm/gma500: one", {f"{GMA}/a.c": "int a1;\n"})
    c2 = commit(home, "mm: elsewhere", {"mm/m.c": "int m2;\n"})
    c3 = commit(home, "drm/gma500: three", {f"{GMA}/a.c": "int a3;\n"})
    hosthome = tmp_path / "hosthome"
    hosthome.mkdir()
    subprocess.run(["git", "clone", "-q", str(home), str(hosthome / "clone")], check=True)
    (hosthome / "laptop.config").write_text("CONFIG_LOCALVERSION=\"-resgx545\"\n")
    bindir = tmp_path / "bin"
    bindir.mkdir()
    for name in ("docker", "systemd-nspawn"):
        write_exec(bindir / name, FAKE)
    write_exec(bindir / "sudo", SUDO)
    env = {**{k: v for k, v in os.environ.items()
              if not k.startswith(("SGX_", "FORK_", "DELIVER_"))},
           "PATH": f"{bindir}:{os.environ['PATH']}", "HOME": str(hosthome),
           "SGX_LOCAL_ENV": os.devnull, "FORK_CHECK_SSH": "sh -c",
           "FORK_CHECK_CLONE": "clone", "FORK_PASS_FILE": str(tmp_path / "pass"),
           "FORK_DELIVER_WORK": "deliver", "FORK_DELIVER_CONFIG": "laptop.config",
           "FORK_DELIVER_OUT": str(tmp_path / "out"), "SGX_KERNEL_RELEASE": KREL,
           "SGX_BUILD_JOBS": "4", "FAKE_RELEASE": KREL}
    return dict(home=home, host=hosthome, base=base, c1=c1, c2=c2, c3=c3, env=env,
                tmp=tmp_path)


def deliver(w, tip, passed=True, **extra):
    if passed:
        (w["tmp"] / "pass").write_text(tip + "\n")
    return subprocess.run([str(DELIVER), tip], cwd=w["home"], env={**w["env"], **extra},
                          capture_output=True, text=True, timeout=60)


def manifest(w, tip):
    text = (w["tmp"] / "out" / tip[:12] / "manifest").read_text()
    return dict(line.split("=", 1) for line in text.splitlines() if "=" in line)


def builds(w):
    p = w["host"] / "builds.log"
    return p.read_text().splitlines() if p.exists() else []


def runner_log(w):
    p = w["host"] / "runner.log"
    return p.read_text() if p.exists() else ""


def test_scripts_are_valid_bash_and_executable():
    for p in (DELIVER, BUILD):
        assert os.access(p, os.X_OK), p
        subprocess.run(["bash", "-n", str(p)], check=True)


def test_delivers_the_module_of_a_checked_tip(world):
    w = world
    r = deliver(w, w["c1"])
    assert r.returncode == 0, r.stdout + r.stderr
    ko = w["tmp"] / "out" / w["c1"][:12] / "gma500_gfx.ko"
    m = manifest(w, w["c1"])
    assert m["tip"] == w["c1"]
    assert m["checked"] == "pass-file"
    assert m["vermagic"] == VERMAGIC
    assert m["release"] == KREL
    assert m["srcversion"] and m["depends"] == "video"
    assert m["sha256"] == hashlib.sha256(ko.read_bytes()).hexdigest()
    assert m["sha256"] in r.stdout and m["srcversion"] in r.stdout
    assert f"push-gma500.sh --ko {ko}" in r.stdout


def test_refuses_a_tip_the_series_check_has_not_passed(world):
    w = world
    (w["tmp"] / "pass").write_text(w["base"] + "\n")
    r = deliver(w, w["c1"], passed=False)
    assert r.returncode != 0
    assert "recheck.sh" in r.stderr and "FORK_DELIVER_FORCE" in r.stderr
    assert not list(w["host"].glob("deliver-*.sh")) and runner_log(w) == ""


def test_a_forced_delivery_says_so_in_the_manifest(world):
    w = world
    r = deliver(w, w["c1"], passed=False, FORK_DELIVER_FORCE="1")
    assert r.returncode == 0, r.stdout + r.stderr
    assert manifest(w, w["c1"])["checked"] == "forced"
    assert "not passed" in r.stderr


def test_every_make_runs_in_the_image_from_a_plain_source_archive(world):
    w = world
    assert deliver(w, w["c1"]).returncode == 0
    log = runner_log(w)
    makes = [l for l in log.splitlines() if "make " in l]
    assert makes and all(l.startswith("docker run ") for l in makes)
    assert all("resgx545/arch32:kernel" in l for l in makes)
    assert "LOCALVERSION= modules_prepare" in log
    assert f"M=/k/{GMA} MO=/b/{GMA}" in log and "-j4 " in log
    assert "olddefconfig" in log
    # the source is the tip's tree without .git (setlocalversion adds no '+'), read-only
    assert "module git=no int a1;" in builds(w)
    assert f"/deliver/src-{w['c1'][:12]}:/k:ro" in log


def test_a_new_build_directory_is_built_in_full_once(world):
    w = world
    assert deliver(w, w["c1"]).returncode == 0
    assert builds(w).count("full") == 1
    work = w["host"] / "deliver"
    [bdir] = [p for p in work.glob("build-*") if p.is_dir()]
    assert (bdir / ".config").read_text() == (w["host"] / "laptop.config").read_text()
    assert pathlib.Path(f"{bdir}.built").read_text().strip() == w["c1"]


def test_a_gma500_only_tip_reuses_the_build_and_another_rebuilds_it(world):
    w = world
    assert deliver(w, w["c1"]).returncode == 0
    r = deliver(w, w["c3"])          # c1..c3 touches mm/: Module.symvers may be stale
    assert r.returncode == 0, r.stdout + r.stderr
    assert builds(w).count("full") == 2
    assert manifest(w, w["c3"])["full_build"] == "yes"
    (w["host"] / "builds.log").unlink()
    r = deliver(w, w["c3"])          # same tip: module only
    assert r.returncode == 0
    assert builds(w) == ["module git=no int a3;"]
    assert manifest(w, w["c3"])["full_build"] == "no"


def test_a_wrong_vermagic_is_refused_and_nothing_delivered(world):
    w = world
    r = deliver(w, w["c1"], FAKE_SUFFIX=" modversions")
    assert r.returncode != 0
    assert "vermagic" in r.stdout + r.stderr
    assert not (w["tmp"] / "out" / w["c1"][:12] / "gma500_gfx.ko").exists()


def test_a_plus_in_the_release_is_refused(world):
    w = world
    r = deliver(w, w["c1"], FAKE_RELEASE=KREL + "x")
    assert r.returncode != 0
    assert "kernel.release" in r.stdout + r.stderr


def test_a_tip_missing_on_the_host_is_refused(world):
    w = world
    tip = commit(w["home"], "drm/gma500: local only", {f"{GMA}/a.c": "int z;\n"})
    r = deliver(w, tip)
    assert r.returncode != 0
    assert "recheck.sh" in r.stderr
    assert runner_log(w) == ""


def test_dry_run_prints_the_commands_and_builds_nothing(world):
    w = world
    r = deliver(w, w["c1"], SGX_DRY_RUN="1")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "docker run" in r.stdout and "modules_prepare" in r.stdout
    assert "vmlinux modules" in r.stdout
    assert runner_log(w) == ""
    assert not (w["tmp"] / "out" / w["c1"][:12] / "gma500_gfx.ko").exists()


# --- traveling: the laptop builds in its sgx-build root -----------------------------------

def test_chroot_refuses_a_full_build_unless_allowed(world):
    w = world
    r = deliver(w, w["c1"], FORK_CHECK_RUNNER="chroot")
    assert r.returncode != 0
    assert "FORK_DELIVER_SEED" in r.stderr and "FORK_DELIVER_FULL" in r.stderr
    assert runner_log(w) == ""


def seed_dir(w, built):
    seed = w["host"] / "check" / "build-on"
    seed.mkdir(parents=True)
    (seed / ".config").write_text("seeded\n")
    (seed / "Module.symvers").write_text("symbols\n")
    (seed / "vmlinux.o").write_text("objects\n")
    (w["host"] / "check" / "build-on.built").write_text(built + "\n")
    return seed


def test_chroot_starts_from_a_seed_build_directory(world):
    w = world
    seed = seed_dir(w, w["base"])
    r = deliver(w, w["c1"], FORK_CHECK_RUNNER="chroot", FORK_DELIVER_SEED="check/build-on")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "full" not in builds(w)
    log = runner_log(w)
    assert "systemd-nspawn" in log and "docker" not in log
    assert "-D /var/lib/machines/arch32-build" in log
    assert f"--bind-ro={w['host']}/deliver/src-{w['c1'][:12]}:/k" in log
    [bdir] = [p for p in (w["host"] / "deliver").glob("build-*") if p.is_dir()]
    assert (bdir / "vmlinux.o").exists()                       # copied, not built
    assert (seed / ".config").read_text() == "seeded\n"        # the seed is not touched
    assert manifest(w, w["c1"])["vermagic"] == VERMAGIC


def test_a_seed_without_its_record_is_refused(world):
    w = world
    seed_dir(w, w["base"])
    (w["host"] / "check" / "build-on.built").unlink()
    r = deliver(w, w["c1"], FORK_CHECK_RUNNER="chroot", FORK_DELIVER_SEED="check/build-on")
    assert r.returncode != 0 and "build-on.built" in r.stderr


def test_chroot_with_full_builds_allowed_goes_ahead(world):
    w = world
    r = deliver(w, w["c1"], FORK_CHECK_RUNNER="chroot", FORK_DELIVER_FULL="1")
    assert r.returncode == 0, r.stdout + r.stderr
    assert builds(w).count("full") == 1


def test_reads_the_example_settings(world):
    w = world
    env = {k: v for k, v in w["env"].items()
           if k not in ("FORK_CHECK_CLONE", "FORK_DELIVER_WORK", "FORK_DELIVER_CONFIG")}
    env["SGX_LOCAL_ENV"] = str(HERE.parent / "bringup" / "local.env.example")
    (w["tmp"] / "pass").write_text(w["c1"] + "\n")
    r = subprocess.run([str(DELIVER), w["c1"]], cwd=w["home"], env=env, capture_output=True,
                       text=True, timeout=60)
    assert r.returncode != 0                      # the example's clone is not on this host
    assert "(src/linux-sgx-check)" in r.stderr
