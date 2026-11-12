#!/bin/bash
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
# usage: build-igt.sh COMMIT
#
# Build the IGT fork's sgxfive tests at COMMIT for i686 on the build host and smoke them there,
# with no laptop (deliver-module.sh is the model):
#   - COMMIT must be on the fork's sgxfive branch in the local clone (IGT_FORCE=1 builds another
#     commit, recorded as branch=forced in the manifest);
#   - a git archive of COMMIT (no .git) is unpacked on the host and build-igt-host.sh, sent with
#     it, runs meson and ninja in the toolchain image (SGX_TOOLS_IMAGE) for libigt and every
#     program of tests/sgxfive, then each binary's --list-subtests in the same image;
#   - the binaries, libigt.so.0, the subtest lists and the manifest (commit, branch, image,
#     binaries, sha256 per file, smoke per binary) come back to IGT_OUT/<commit12>/, each file
#     checked against the manifest's sha256 and for an i686 ELF header.
# Exits 1 when the build, the copy, a check or the smoke fails (the manifest is kept on a
# failed smoke). push-tools.sh copies IGT binaries to the laptop; this script does not.
#
# Environment (tools/bringup/local.env is sourced when present; SGX_LOCAL_ENV names another):
#   IGT_CLONE        the local IGT fork clone (default ~/src/igt-gpu-tools)
#   IGT_BRANCH       the branch COMMIT must be on (sgxfive); IGT_FORCE=1 to build another
#   IGT_BUILD_HOST, IGT_BUILD_SSH   the host (default SGX_BUILD_HOST) or the whole ssh command
#   IGT_BUILD_WORK   the host's work directory, from its $HOME (src/igt-build), per commit
#   SGX_TOOLS_IMAGE  the image (sgxhumation/arch32:igt); IGT_MESON_OPTIONS, meson's options
#   IGT_OUT          where the files land here (default <clone git dir>/igt-deliver)
set -u -o pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
LOCAL=${SGX_LOCAL_ENV:-$HERE/local.env}
# shellcheck source=/dev/null
[ -f "$LOCAL" ] && . "$LOCAL"
die() { echo "build-igt.sh: $*" >&2; exit 1; }
sha() { if command -v sha256sum >/dev/null; then sha256sum "$1"; else shasum -a 256 "$1"; fi | cut -d' ' -f1; }
byte() { od -An -tu1 -j "$2" -N1 "$1" | tr -d ' '; }
[ $# -eq 1 ] || { echo "usage: build-igt.sh COMMIT" >&2; exit 2; }
CLONE=${IGT_CLONE:-$HOME/src/igt-gpu-tools}
BR=${IGT_BRANCH:-sgxfive}
C=$(git -C "$CLONE" rev-parse --verify -q "$1^{commit}") || die "no such commit $1 in $CLONE"
if git -C "$CLONE" merge-base --is-ancestor "$C" "$BR" 2>/dev/null; then
	BRANCH=$BR
elif [ -n "${IGT_FORCE:-}" ]; then
	BRANCH=forced
	echo "build-igt.sh: $C is not on $BR; building it anyway (IGT_FORCE)" >&2
else
	die "$C is not on the $BR branch of $CLONE; set IGT_FORCE=1 to build it anyway"
fi
T=${C:0:12}
GITDIR=$(git -C "$CLONE" rev-parse --path-format=absolute --git-common-dir)
OUT=${IGT_OUT:-$GITDIR/igt-deliver}/$T
WORK=${IGT_BUILD_WORK:-src/igt-build}/$T
IMG=${SGX_TOOLS_IMAGE:-sgxhumation/arch32:igt}
SSH=${IGT_BUILD_SSH:-ssh -o BatchMode=yes ${IGT_BUILD_HOST:-${SGX_BUILD_HOST:-sgx-build}}}
REMOTE=build-igt-$T.sh
# every remote command goes through bash -c: the host's login shell may be another one
on_host() { $SSH "bash -c '$1'"; }

$SSH "bash -c 'cd && cat > $REMOTE'" < "$HERE/build-igt-host.sh" || die "cannot send the build script"
git -C "$CLONE" archive --format=tar "$C" |
	$SSH "bash -c 'cd && rm -rf $WORK/src && mkdir -p $WORK/src && tar -x -C $WORK/src'" ||
	die "cannot send the source of $C"
envs="IGT_WORK=\"$WORK\" IGT_IMAGE=\"$IMG\" IGT_BRANCH_STATE=$BRANCH"
[ -n "${IGT_MESON_OPTIONS:-}" ] && envs="$envs IGT_MESON_OPTIONS=\"$IGT_MESON_OPTIONS\""
on_host "cd && $envs bash ~/$REMOTE $C" || die "the build on the host failed"

rm -rf "$OUT.part"
mkdir -p "$OUT.part"
on_host "cd && cd $WORK/out && tar -c ." | tar -x -C "$OUT.part" || die "cannot copy the build back"
M=$OUT.part/manifest
[ -f "$M" ] || die "no manifest came back"
while IFS='=' read -r key want; do
	f=$OUT.part/${key#sha256.}
	[ -f "$f" ] || die "the manifest names ${key#sha256.}, which did not come back"
	got=$(sha "$f")
	[ "$got" = "$want" ] || die "${key#sha256.} has sha256 $got, not $want"
	[ "$(byte "$f" 4)" = 1 ] && [ "$(byte "$f" 18)" = 3 ] ||
		die "${key#sha256.} is not an i686 (32-bit x86) ELF file"
done < <(grep '^sha256\.' "$M")
rm -rf "$OUT"
mv "$OUT.part" "$OUT"
smoke=$(sed -n 's/^smoke=//p' "$OUT/manifest")
echo "built:    $C ($BRANCH) in $IMG"
echo "manifest: $OUT/manifest"
if [ "$smoke" != pass ]; then
	grep '^smoke\.' "$OUT/manifest" | grep -v '=ok ' >&2
	die "the smoke failed (--list-subtests in $IMG)"
fi
echo "smoke:    pass ($(grep -c '^smoke\.' "$OUT/manifest") binaries list their subtests)"
