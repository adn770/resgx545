#!/bin/bash
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
# usage: health.sh TOOL
#
# A quick look at the laptop: a fill and the triangle through TOOL (the sgxfive-test binary in
# the target's home, e.g. sgxfive-test-1138), the driver's debug switches, the first kpoke
# lines and the last kernel messages. Host and ssh options are those of push-gma500.sh
# (SGX_TARGET_HOST, SGX_TARGET_SSH_OPTS; tools/bringup/local.env). SGX_DRY_RUN=1 prints the
# ssh command instead of running it.
set -u
cd "$(dirname "$0")/../.."
LOCAL_ENV=${SGX_LOCAL_ENV:-tools/bringup/local.env}
[ -f "$LOCAL_ENV" ] && . "$LOCAL_ENV"
[ $# -eq 1 ] || { echo "usage: health.sh TOOL" >&2; exit 2; }
TOOL=$1
T=${SGX_TARGET_HOST:-user@sgx-target}
OPTS=${SGX_TARGET_SSH_OPTS:-}
remote="D=/sys/kernel/debug/dri/0/sgx;
 sudo -n ~/$TOOL fill 2>&1 | grep -E \"^diff|^job|ok|FAIL\" | head -3;
 sudo -n ~/$TOOL tri 2>&1 | grep -E \"^tri|^diff|FAIL\" | head -3;
 for s in hold_recovery rtds_keep alias_ta3d_ro render_pb_pages render_ctx_flags; do
    printf \"%s=%s \" \$s \"\$(sudo -n cat \$D/\$s)\"; done; echo;
 sudo -n cat \$D/kpoke | head -3;
 sudo -n dmesg | tail -3"
if [ -n "${SGX_DRY_RUN:-}" ]; then
    echo "ssh -o BatchMode=yes -o ConnectTimeout=10 $OPTS $T '$remote'"
    exit 0
fi
# shellcheck disable=SC2086
exec ssh -o BatchMode=yes -o ConnectTimeout=10 $OPTS "$T" "$remote"
