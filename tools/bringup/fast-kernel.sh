#!/bin/bash
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
# The laptop's quick kernel loop: build the test kernel incrementally in its tree, in the
# laptop's sgx-build nspawn root, and install it over the installed test kernel package,
# without packaging.
#
#   usage (on the laptop): ./fast-kernel.sh      then boot it one-shot (boot-test-kernel.sh)
#
# The packaged route (build-kernel.sh, install-test-kernel.sh) takes about 50 minutes on the
# laptop: pacman-pkg strips and signs every module, splits a debug package and builds a
# headers package. This one makes bzImage and modules only, compresses the image at zstd -3
# (the kernel asks for -22 --ultra; boot-time decompression is not affected), and copies the
# image and only the modules rebuilt since the last fast install (or since the package's
# install) as they are, unsigned, as the module loop (push-gma500.sh) does. It needs the
# package of the same kernel release installed once; the package route stays for clean
# installs.
#
# Settings: SGX_KERNEL_TREE, the kernel tree relative to $HOME or absolute (default
# src/linux-sgx); SGX_KERNEL_PKGBASE, the installed package's name (default linux-sgx);
# SGX_BUILD_JOBS, make jobs (default: the CPU count). SGX_DRY_RUN=1 prints the commands
# instead of running them, with SGX_KERNEL_RELEASE standing in for the release the build
# would write.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
abs() { case $1 in /*) printf '%s' "$1" ;; *) printf '%s' "$HOME/$1" ;; esac; }
REL_TREE=${SGX_KERNEL_TREE:-src/linux-sgx}
TREE=$(abs "$REL_TREE")
PKG=${SGX_KERNEL_PKGBASE:-linux-sgx}
JOBS=${SGX_BUILD_JOBS:-$(nproc)}
STAMP=$TREE/.fast-kernel.stamp
run() {
	if [ -n "${SGX_DRY_RUN:-}" ]; then
		printf '%s\n' "$*"
	else
		bash -c "$*"
	fi
}
run "SGX_KERNEL_TREE=$REL_TREE SGX_DRY_RUN= $HERE/sgx-build kernel make ARCH=i386 -j$JOBS \"ZSTD=sh -c 'exec zstd -3 -q' zstd-fast\" bzImage modules"
if [ -n "${SGX_DRY_RUN:-}" ]; then
	rel=${SGX_KERNEL_RELEASE:-RELEASE}
else
	rel=$(cat "$TREE/include/config/kernel.release")
fi
mods=/usr/lib/modules/$rel
run "test -d $mods || { echo 'fast-kernel.sh: install the $PKG package of $rel first' >&2; exit 1; }"
# One failed install fails the copy, and so the script, before the stamp.
run "set -o pipefail; cd $TREE && ref=$STAMP && { test -e \$ref || ref=$mods/modules.dep; } &&
	find . -name '*.ko' -newer \$ref | while read -r m; do
		sudo install -D -m644 \"\$m\" \"$mods/kernel/\${m#./}\" || exit 1; done"
run "cd $TREE && sudo install -m644 arch/x86/boot/bzImage /boot/vmlinuz-$PKG"
run "sudo depmod $rel"
run "sudo mkinitcpio -p $PKG >/dev/null"
run "touch $STAMP"
