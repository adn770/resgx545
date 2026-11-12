# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""install-module.sh on a fake laptop: a modules directory and a /boot in a temporary
directory, depmod, mkinitcpio and lsinitcpio replaced by stubs (the initramfs is a plain tar
of the modules directory). The script runs on the laptop only; nothing here needs one."""
from __future__ import annotations

import hashlib
import os
import pathlib
import subprocess

import pytest

HERE = pathlib.Path(__file__).resolve().parent
INSTALL = HERE / "install-module.sh"
KREL = "7.3.0-resgx545"
PKG = "linux-resgx545"
REL = "kernel/drivers/gpu/drm/gma500/gma500_gfx.ko"
VERMAGIC = f"{KREL} SMP preempt mod_unload 686 "


def ko(srcversion: str, vermagic: str = VERMAGIC, body: str = "code") -> bytes:
    """A stand-in for a module: its .modinfo strings, NUL separated, as in a real .ko."""
    return (f"\x7fELF{body}\0license=GPL\0srcversion={srcversion}\0depends=video\0"
            f"vermagic={vermagic}\0").encode()


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@pytest.fixture
def laptop(tmp_path):
    mods = tmp_path / "modules"
    boot = tmp_path / "boot"
    bindir = tmp_path / "bin"
    for d in (mods / KREL / "kernel/drivers/gpu/drm/gma500", boot, bindir):
        d.mkdir(parents=True)
    old = ko("B21FDA82C0FFEE0000000AA")
    (mods / KREL / REL).write_bytes(old)
    (boot / f"initramfs-{PKG}.img").write_bytes(b"old initramfs")
    calls = tmp_path / "calls"
    stubs = {
        "depmod": f'echo "depmod $*" >> "{calls}"',
        # the image holds the modules directory as it is now (or stays stale: FAKE_STALE)
        "mkinitcpio": (f'echo "mkinitcpio $*" >> "{calls}"\n'
                       f'[ -n "${{FAKE_STALE:-}}" ] && exit 0\n'
                       f'tar -cf "{boot}/initramfs-$2.img" -C "{mods}/.." modules'),
        "lsinitcpio": f'echo "lsinitcpio $*" >> "{calls}"\n[ "$1" = -x ] && tar -xf "$2"',
    }
    for name, text in stubs.items():
        (bindir / name).write_text(f"#!/bin/bash\n{text}\n")
        (bindir / name).chmod(0o755)
    env = {**{k: v for k, v in os.environ.items() if not k.startswith("SGX_")},
           "PATH": f"{bindir}:{os.environ['PATH']}", "SGX_MODULES_DIR": str(mods),
           "SGX_BOOT_DIR": str(boot)}
    return dict(tmp=tmp_path, mods=mods, boot=boot, calls=calls, env=env, old=old)


def install(laptop, data: bytes | None, *extra_args: str, **env: str):
    new = laptop["tmp"] / "new" / "gma500_gfx.ko"
    if data is not None:
        new.parent.mkdir(exist_ok=True)
        new.write_bytes(data)
    return subprocess.run(["bash", str(INSTALL), str(new), KREL, PKG, *extra_args],
                          env={**laptop["env"], **env}, capture_output=True, text=True,
                          timeout=30)


def test_script_is_valid_bash_and_executable():
    assert os.access(INSTALL, os.X_OK)
    subprocess.run(["bash", "-n", str(INSTALL)], check=True)


def test_installs_and_keeps_the_old_module_and_initramfs_by_srcversion(laptop):
    new = ko("41E2F5C756F96D20F7109A4")
    r = install(laptop, new, sha(new))
    assert r.returncode == 0, r.stdout + r.stderr
    dst = laptop["mods"] / KREL / REL
    assert dst.read_bytes() == new
    assert (dst.parent / "gma500_gfx.ko.B21FDA82").read_bytes() == laptop["old"]
    assert (laptop["boot"] / f"initramfs-{PKG}.img.B21FDA82").read_bytes() == b"old initramfs"
    calls = laptop["calls"].read_text()
    assert f"depmod {KREL}" in calls and f"mkinitcpio -p {PKG}" in calls
    assert "41E2F5C756F96D20F7109A4" in r.stdout and sha(new) in r.stdout
    assert "initramfs holds" in r.stdout


def test_the_expected_sha256_is_optional(laptop):
    r = install(laptop, ko("41E2F5C756F96D20F7109A4"))
    assert r.returncode == 0, r.stdout + r.stderr


@pytest.mark.parametrize("vermagic", [f"{KREL}+ SMP preempt mod_unload 686 ",
                                      f"{KREL} SMP mod_unload 686 "])
def test_refuses_a_module_whose_vermagic_differs_from_the_installed_one(laptop, vermagic):
    r = install(laptop, ko("41E2F5C756F96D20F7109A4", vermagic))
    assert r.returncode != 0
    assert "vermagic" in r.stderr
    assert (laptop["mods"] / KREL / REL).read_bytes() == laptop["old"]
    assert not laptop["calls"].exists()


def test_refuses_a_module_whose_sha256_is_not_the_expected_one(laptop):
    r = install(laptop, ko("41E2F5C756F96D20F7109A4"), "0" * 64)
    assert r.returncode != 0 and "sha256" in r.stderr
    assert (laptop["mods"] / KREL / REL).read_bytes() == laptop["old"]


def test_fails_when_the_initramfs_does_not_hold_the_new_module(laptop):
    (laptop["boot"] / f"initramfs-{PKG}.img").write_bytes(b"")
    r = install(laptop, ko("41E2F5C756F96D20F7109A4"), FAKE_STALE="1")
    assert r.returncode != 0
    assert "initramfs" in r.stderr


def test_an_existing_backup_is_never_overwritten(laptop):
    dst = laptop["mods"] / KREL / REL
    (dst.parent / "gma500_gfx.ko.B21FDA82").write_bytes(b"first backup")
    r = install(laptop, ko("41E2F5C756F96D20F7109A4"))
    assert r.returncode == 0, r.stdout + r.stderr
    assert (dst.parent / "gma500_gfx.ko.B21FDA82").read_bytes() == b"first backup"


def test_refuses_without_an_installed_module(laptop):
    (laptop["mods"] / KREL / REL).unlink()
    r = install(laptop, ko("41E2F5C756F96D20F7109A4"))
    assert r.returncode != 0 and KREL in r.stderr


def test_dry_run_prints_and_changes_nothing(laptop):
    new = ko("41E2F5C756F96D20F7109A4")
    r = install(laptop, new, sha(new), SGX_DRY_RUN="1")
    assert r.returncode == 0, r.stderr
    dst = laptop["mods"] / KREL / REL
    assert dst.read_bytes() == laptop["old"]
    assert not laptop["calls"].exists()
    assert f"install -m644 {laptop['tmp']}/new/gma500_gfx.ko {dst}" in r.stdout
    assert f"mkinitcpio -p {PKG}" in r.stdout and f"depmod {KREL}" in r.stdout
    assert "gma500_gfx.ko.B21FDA82" in r.stdout
