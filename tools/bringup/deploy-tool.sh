#!/bin/bash
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
# usage: deploy-tool.sh NAME
#
# Build sgxfive-test on the laptop as ~/sgxfive-test-NAME from this checkout's
# userspace/libsgxfive, include/uapi and tools/gen_tri_progs.py (the userspace compile only; no
# git on the laptop) and print the sha256 of the source file here and there and of the binary,
# to record in the dataset's env.toml. Name the tool after the phase or the run. Host and ssh
# options: SGX_TARGET_HOST, SGX_TARGET_SSH_OPTS (tools/bringup/local.env). SGX_DRY_RUN=1 prints
# the commands.
set -u
cd "$(dirname "$0")/../.."
LOCAL_ENV=${SGX_LOCAL_ENV:-tools/bringup/local.env}
[ -f "$LOCAL_ENV" ] && . "$LOCAL_ENV"
[ $# -eq 1 ] && [[ $1 =~ ^[A-Za-z0-9._-]+$ ]] || { echo "usage: deploy-tool.sh NAME" >&2; exit 2; }
NAME=$1
T=${SGX_TARGET_HOST:-user@sgx-target}
OPTS=${SGX_TARGET_SSH_OPTS:-}
SRC=userspace/libsgxfive/tools/sgxfive-test.c
tar_cmd="tar cf - --exclude=build userspace/libsgxfive include/uapi tools/gen_tri_progs.py"
remote="rm -rf ~/libsgxfive-$NAME && mkdir ~/libsgxfive-$NAME && cd ~/libsgxfive-$NAME && tar xf - 2>/dev/null; sha256sum $SRC; cd userspace/libsgxfive && make -j2 build/sgxfive-test 2>&1 | grep -E ' error |warning:'; cp build/sgxfive-test ~/sgxfive-test-$NAME; sha256sum ~/sgxfive-test-$NAME; ls -l ~/sgxfive-test-$NAME"
if [ -n "${SGX_DRY_RUN:-}" ]; then
    echo "sha256sum $SRC"
    echo "$tar_cmd | ssh $OPTS $T '$remote'"
    exit 0
fi
sha256sum "$SRC"
# shellcheck disable=SC2086
$tar_cmd 2>/dev/null | ssh $OPTS "$T" "$remote"
