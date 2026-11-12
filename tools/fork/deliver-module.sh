#!/bin/bash
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
# usage: deliver-module.sh TIP     (run in the fork clone that holds TIP, as recheck.sh)
#
# Deliver the gma500 module of a checked fork commit for the laptop's installed test kernel:
#   - refuse TIP unless the series check passed for exactly it (the pass file recheck.sh
#     writes, as fork-land.sh reads it); FORK_DELIVER_FORCE=1 delivers anyway and the
#     manifest says checked=forced;
#   - the build host's clone must hold TIP (recheck.sh sends the series there);
#   - send build-module.sh and run it there: a git archive of TIP, a build directory from the
#     laptop's config, every make in the toolchain root (docker on the build host, the
#     sgx-build nspawn root when the laptop builds), vermagic checked against the target's;
#   - copy gma500_gfx.ko and its manifest (tip, vermagic, srcversion, depends, sha256) back to
#     FORK_DELIVER_OUT/<tip12>/ and check the copy's sha256.
# Installing is a separate step: tools/bringup/push-gma500.sh --ko FILE [--no-reboot] (through
# install-module.sh on the laptop).
#
# Environment (tools/bringup/local.env is sourced when present; SGX_LOCAL_ENV names another):
#   FORK_CHECK_HOST, FORK_CHECK_SSH, FORK_CHECK_CLONE   the host and its clone, as recheck.sh
#   FORK_CHECK_RUNNER    docker (default) or chroot (the laptop's build root)
#   FORK_PASS_FILE       the series check's pass file (default <git dir>/fork-check.pass)
#   FORK_DELIVER_WORK    the host's delivery directory, from its $HOME (src/linux-sgx-deliver)
#   FORK_DELIVER_CONFIG  the installed kernel's config on the host (src/linux-sgx-travel/.config)
#   FORK_DELIVER_SEED    a built O= directory of that config to start a new build directory from
#   FORK_DELIVER_FULL=1  allow a full kernel build under the chroot runner (refused otherwise)
#   FORK_DELIVER_IMAGE   docker image (resgx545/arch32:kernel); FORK_DELIVER_ROOT, nspawn root
#   FORK_DELIVER_OUT     where the module lands here (default <git dir>/deliver)
#   FORK_DELIVER_VERMAGIC  the target's vermagic (default "$SGX_KERNEL_RELEASE SMP preempt
#                        mod_unload 686"); SGX_KERNEL_RELEASE (7.3.0-sgx), SGX_BUILD_JOBS
#   SGX_DRY_RUN=1        print the host's commands; nothing is built or copied
set -u -o pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
LOCAL=${SGX_LOCAL_ENV:-$HERE/../bringup/local.env}
# shellcheck source=/dev/null
[ -f "$LOCAL" ] && . "$LOCAL"
die() { echo "deliver-module.sh: $*" >&2; exit 1; }
sha() { if command -v sha256sum >/dev/null; then sha256sum "$1"; else shasum -a 256 "$1"; fi | cut -d' ' -f1; }
[ $# -eq 1 ] || { echo "usage: deliver-module.sh TIP" >&2; exit 2; }
CLONE=${FORK_CHECK_CLONE:-}
[ -n "$CLONE" ] || { echo "deliver-module.sh: FORK_CHECK_CLONE is not set" >&2; exit 2; }
TIP=$(git rev-parse --verify -q "$1^{commit}") || die "no such tip $1"
T=${TIP:0:12}
GITDIR=$(git rev-parse --path-format=absolute --git-common-dir)
PASSFILE=${FORK_PASS_FILE:-$GITDIR/fork-check.pass}
tested=$(cat "$PASSFILE" 2>/dev/null || true)
if [ "$tested" = "$TIP" ]; then
	CHECKED=pass-file
elif [ -n "${FORK_DELIVER_FORCE:-}" ]; then
	CHECKED=forced
	echo "deliver-module.sh: the series check has not passed for $TIP; delivering it anyway" \
		"(FORK_DELIVER_FORCE)" >&2
else
	die "the series check has not passed for $TIP (the pass file names ${tested:-nothing}):" \
		"run tools/fork/recheck.sh BASE $TIP first, or set FORK_DELIVER_FORCE=1"
fi
SSH=${FORK_CHECK_SSH:-ssh -o BatchMode=yes ${FORK_CHECK_HOST:-${SGX_BUILD_HOST:-sgx-build}}}
RUNNER=${FORK_CHECK_RUNNER:-docker}
WORK=${FORK_DELIVER_WORK:-src/linux-sgx-deliver}
CONFIG=${FORK_DELIVER_CONFIG:-src/linux-sgx-travel/.config}
VERMAGIC=${FORK_DELIVER_VERMAGIC:-${SGX_KERNEL_RELEASE:-7.3.0-sgx} SMP preempt mod_unload 686}
OUT=${FORK_DELIVER_OUT:-$GITDIR/deliver}/$T
REMOTE=deliver-$T.sh
# every remote command goes through bash -c: the host's login shell may be another one
on_host() { $SSH "bash -c '$1'"; }

on_host "cd && cd $CLONE && git rev-parse --verify -q $TIP^{commit} >/dev/null" ||
	die "the host's clone ($CLONE) does not hold $TIP: tools/fork/recheck.sh sends the series"
$SSH "bash -c 'cd && cat > $REMOTE'" < "$HERE/build-module.sh" || die "cannot send the build script"
envs="DELIVER_WORK=\"$WORK\" DELIVER_CONFIG=\"$CONFIG\" DELIVER_VERMAGIC=\"$VERMAGIC\""
envs="$envs DELIVER_RUNNER=$RUNNER DELIVER_CHECKED=$CHECKED DELIVER_DRY_RUN=${SGX_DRY_RUN:-}"
envs="$envs DELIVER_SEED=\"${FORK_DELIVER_SEED:-}\" DELIVER_FULL=${FORK_DELIVER_FULL:-}"
[ -n "${FORK_DELIVER_IMAGE:-}" ] && envs="$envs DELIVER_IMAGE=$FORK_DELIVER_IMAGE"
[ -n "${FORK_DELIVER_ROOT:-}" ] && envs="$envs DELIVER_ROOT=$FORK_DELIVER_ROOT"
[ -n "${SGX_BUILD_JOBS:-}" ] && envs="$envs DELIVER_JOBS=$SGX_BUILD_JOBS"
on_host "cd && cd $CLONE && $envs bash ~/$REMOTE $TIP" || die "the build on the host failed"
[ -n "${SGX_DRY_RUN:-}" ] && exit 0

mkdir -p "$OUT"
rm -f "$OUT/gma500_gfx.ko" "$OUT/manifest"
on_host "cd && cd $WORK && cat out-$T/manifest" > "$OUT/manifest.part" &&
	on_host "cd && cd $WORK && cat out-$T/gma500_gfx.ko" > "$OUT/gma500_gfx.ko.part" ||
	die "cannot copy the module back"
want=$(sed -n 's/^sha256=//p' "$OUT/manifest.part")
got=$(sha "$OUT/gma500_gfx.ko.part")
[ -n "$want" ] && [ "$got" = "$want" ] || die "the copied module has sha256 $got, not $want"
mv "$OUT/manifest.part" "$OUT/manifest"
mv "$OUT/gma500_gfx.ko.part" "$OUT/gma500_gfx.ko"
src=$(sed -n 's/^srcversion=//p' "$OUT/manifest")
echo "delivered: $OUT/gma500_gfx.ko (srcversion $src, sha256 $got, checked=$CHECKED)"
echo "install:   tools/bringup/push-gma500.sh --ko $OUT/gma500_gfx.ko [--no-reboot]"
