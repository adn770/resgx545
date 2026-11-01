#!/bin/sh
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
# Gate between sweep tables: on the laptop (SGX_TARGET_HOST, tools/bringup/local.env) a plain
# fill must pass and the kernel log must hold no oops, BUG, lockdep report or call trace.
# Prints what it saw; exit 0 healthy, 1 not.
cd "$(dirname "$0")/../.." || exit 1
[ -f tools/bringup/local.env ] && . tools/bringup/local.env
# shellcheck disable=SC2086
out=$(ssh ${SGX_TARGET_SSH_OPTS:-} "${SGX_TARGET_HOST:?set SGX_TARGET_HOST}" \
	'~/sgxfive-test fill 2>&1 | grep -E "^job|^diff"; echo "bad $(sudo -n dmesg | grep -ciE "oops|BUG:|lockdep|call trace")"')
echo "$out" | tr '\n' ' '; echo
echo "$out" | grep -q "^job: ok" && echo "$out" | grep -q "^diff: 0 of" && echo "$out" | grep -q "^bad 0$"
