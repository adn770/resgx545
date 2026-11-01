#!/bin/sh
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
# Build sgxfive-test for i686 in the resgx545/arch32:igt image on the build host and copy it
# to the laptop's home directory. If the build host has also built the IGT fork's sgxfive
# tests (libigt in $SGX_IGT_TREE/build32), copy them and libigt to ~/igtpkg/ on the laptop.
# Settings are those of push-gma500.sh (tools/bringup/local.env): SGX_BUILD_HOST,
# SGX_TARGET_HOST, SGX_TARGET_SSH_OPTS; SGX_IGT_TREE locates the IGT tree.
set -e
cd "$(dirname "$0")/../.."
[ -f tools/bringup/local.env ] && . tools/bringup/local.env
B=${SGX_BUILD_HOST:-sgx-build}
T=${SGX_TARGET_HOST:-sgx-target}
I=${SGX_IGT_TREE:-src/igt-gpu-tools}
ssh "$B" "bash -c 'rm -rf ~/sgxt/userspace/libsgxfive ~/sgxt/include/uapi && mkdir -p ~/sgxt/userspace ~/sgxt/include'"
scp -qr userspace/libsgxfive "$B:sgxt/userspace/"
scp -qr include/uapi "$B:sgxt/include/"
ssh "$B" "bash -c 'cd ~/sgxt/userspace/libsgxfive && rm -rf build && docker run --rm --user \$(id -u):\$(id -g) -e HOME=/tmp -v ~/sgxt:/s -w /s/userspace/libsgxfive resgx545/arch32:igt make -s CC=gcc build/sgxfive-test'"
S=$(mktemp -d)
scp -q "$B:sgxt/userspace/libsgxfive/build/sgxfive-test" "$S/"
# shellcheck disable=SC2086
scp -q ${SGX_TARGET_SSH_OPTS:-} "$S/sgxfive-test" "$T:"
if scp -q "$B:$I/build32/lib/libigt.so.0" "$S/" 2>/dev/null; then
	scp -q "$B:$I/build32/tests/sgxfive/sgxfive_*" "$S/" 2>/dev/null || true
	rm -rf "$S"/*.p
	# shellcheck disable=SC2086
	ssh ${SGX_TARGET_SSH_OPTS:-} "$T" 'mkdir -p igtpkg'
	# shellcheck disable=SC2086
	scp -q ${SGX_TARGET_SSH_OPTS:-} "$S"/sgxfive_* "$S/libigt.so.0" "$T:igtpkg/"
fi
rm -rf "$S"
