#!/bin/bash
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
# Build the whole test kernel on the laptop, in its kernel tree through sgx-build, and
# package it for pacman under its own package base, so it installs beside the distro
# kernels and beside another test kernel (install-test-kernel.sh installs the package).
#
#   usage (on the laptop): ./build-kernel.sh
#
# SGX_KERNEL_TREE (src/linux-sgx), SGX_KERNEL_PKGBASE (linux-sgx), SGX_BUILD_JOBS
# (the CPU count). The tree's .config sets the release (CONFIG_LOCALVERSION); the build
# adds no local version of its own. One make: pacman-pkg builds the kernel before it packages
# it. On the laptop an incremental run takes most of an hour (the vmlinux link, compressing
# the image, and stripping and signing every module); the module loop (push-gma500.sh with
# SGX_BUILD_HOST=target) takes minutes. SGX_DRY_RUN=1 prints the command.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
TREE=${SGX_KERNEL_TREE:-src/linux-sgx}
PKG=${SGX_KERNEL_PKGBASE:-linux-sgx}
JOBS=${SGX_BUILD_JOBS:-$(nproc)}
run() {
	if [ -n "${SGX_DRY_RUN:-}" ]; then
		printf '%s\n' "$*"
	else
		"$@"
	fi
}
run env SGX_KERNEL_TREE="$TREE" "$HERE/sgx-build" kernel make ARCH=i386 ZSTD=zstd-kernel -j"$JOBS" \
	pacman-pkg PACMAN_PKGBASE="$PKG"
