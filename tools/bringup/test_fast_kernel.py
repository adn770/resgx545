# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""fast-kernel.sh: the laptop's quick kernel loop, checked in dry-run mode (SGX_DRY_RUN=1).

The packaged route (build-kernel.sh, then install-test-kernel.sh) takes about 50 minutes on
the laptop: pacman-pkg strips and signs every module, splits a debug package and builds a
headers package. The fast route builds bzImage and modules incrementally, compresses the
image at zstd -3, and installs the image and only the modules rebuilt since the last fast
install over the installed test kernel package."""
import os
import subprocess

import pytest

from test_scripts import HERE, clean_env

FAST = HERE / "fast-kernel.sh"


def fast(**extra):
    out = subprocess.run(["bash", str(FAST)], capture_output=True, text=True, timeout=30,
                         env=clean_env(**{"SGX_DRY_RUN": "1",
                                          "SGX_KERNEL_RELEASE": "7.3.0-resgx545",
                                          "SGX_KERNEL_TREE": "src/linux-sgx",
                                          "SGX_KERNEL_PKGBASE": "linux-resgx545",
                                          "SGX_BUILD_JOBS": "4", **extra}))
    assert out.returncode == 0, out.stderr
    return out.stdout.splitlines()


def test_one_incremental_make_of_the_image_and_modules_without_packaging():
    lines = fast()
    makes = [l for l in lines if " make " in l]
    assert len(makes) == 1
    assert "ARCH=i386 -j4" in makes[0] and makes[0].rstrip().endswith("bzImage modules")
    assert not any("pacman" in l for l in lines)


def test_the_image_is_compressed_cheaply():
    make = next(l for l in fast() if " make " in l)
    # the kernel runs $(ZSTD) -22 --ultra: the wrapper drops those and compresses at -3
    assert "ZSTD=sh -c 'exec zstd -3 -q' zstd-fast" in make
    assert "zstd-kernel" not in make


def test_it_refuses_without_the_installed_package():
    lines = fast()
    guard = next(i for i, l in enumerate(lines) if "test -d /usr/lib/modules/7.3.0-resgx545" in l)
    first_install = next(i for i, l in enumerate(lines) if "sudo install" in l)
    assert guard < first_install


def test_only_modules_newer_than_the_last_install_are_copied():
    text = "\n".join(fast())
    home = os.path.expanduser("~")
    tree = f"{home}/src/linux-sgx"
    # the stamp of the last fast install, else the package's depmod (its install time)
    assert f"ref={tree}/.fast-kernel.stamp" in text and "-newer $ref" in text
    assert "/usr/lib/modules/7.3.0-resgx545/modules.dep" in text
    assert "find . -name '*.ko'" in text
    assert "sudo install -D -m644" in text and "/usr/lib/modules/7.3.0-resgx545/kernel/" in text


def test_the_image_initramfs_and_module_index_follow():
    lines = fast()
    text = "\n".join(lines)
    assert "sudo install -m644 arch/x86/boot/bzImage /boot/vmlinuz-linux-resgx545" in text
    assert "sudo depmod 7.3.0-resgx545" in text
    assert "sudo mkinitcpio -p linux-resgx545" in text
    assert lines[-1] == f"touch {os.path.expanduser('~')}/src/linux-sgx/.fast-kernel.stamp"
    assert text.index("depmod") < text.index("mkinitcpio")


def test_a_failed_module_install_stops_before_the_stamp(tmp_path):
    """The module copy fails as a whole when one install fails, so the script stops (set -e)
    before depmod and the stamp: a module that failed stays newer than the stamp."""
    tree = tmp_path / "tree"
    (tree / "drivers").mkdir(parents=True)
    stamp = tree / ".fast-kernel.stamp"
    stamp.touch()
    os.utime(stamp, (1, 1))
    for name in ("a.ko", "b.ko", "c.ko"):
        (tree / "drivers" / name).touch()
    lines = fast(SGX_KERNEL_TREE=str(tree))
    first = next(i for i, l in enumerate(lines) if "ref=" in l)
    last = next(i for i in range(first, len(lines)) if lines[i].rstrip().endswith("done"))
    copy = "\n".join(lines[first:last + 1])
    stub = tmp_path / "bin"
    stub.mkdir()
    calls = tmp_path / "calls"
    # sudo fails on its first call only: the loop's last install succeeds
    (stub / "sudo").write_text(f'#!/bin/bash\necho x >> "{calls}"\n'
                               f'[ "$(wc -l < "{calls}")" -gt 1 ]\n')
    (stub / "sudo").chmod(0o755)
    env = clean_env(PATH=f"{stub}:{os.environ['PATH']}")
    out = subprocess.run(["bash", "-c", copy], capture_output=True, text=True, timeout=30,
                         env=env)
    assert out.returncode != 0, out.stdout + out.stderr
    assert calls.read_text().count("x") == 1      # nothing after the failed install
