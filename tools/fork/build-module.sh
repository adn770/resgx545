#!/bin/bash
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
# usage: build-module.sh TIP     (on the build host, in its clone of the fork)
#
# Build the gma500 module of one fork commit for the laptop's installed test kernel; the host
# side of deliver-module.sh, which sends this script and runs it. All in DELIVER_WORK:
#
#   src-<tip>/          git archive of TIP: a plain tree, so setlocalversion adds no '+'
#   build-<config>/     O= build directory of the config (named by the first 12 hex digits of
#                       its sha256), with <dir>.built naming the commit it was last built at
#   out-<tip>/          gma500_gfx.ko and its manifest; log-<tip>.txt, the build's output
#
# Every make runs in the toolchain root, never on the host: the build directory's Makefile
# includes /k/Makefile, which exists only there. docker (DELIVER_RUNNER=docker, the image
# resgx545/arch32:kernel) or the laptop's sgx-build nspawn root (chroot), the source at /k
# read-only and the build directory at /b, as fork-check.sh mounts them. Each make passes
# LOCALVERSION= so kernel.release is the config's own (no '+', also in a directory copied from
# a git-tree build); modules_prepare rewrites it before the module is built.
#
# The module needs a fully built directory (Module.symvers for modpost's depends). A new
# build directory is copied from DELIVER_SEED when given (an O= directory built from this
# config, with its <seed>.built record, e.g. a series check's build-on, never changed here),
# otherwise built in full (vmlinux modules). A full build is redone when TIP changes anything
# but gma500's sources and its UAPI header since the recorded commit. Under the chroot runner a
# full build (most of a day on the laptop) is refused unless DELIVER_FULL=1.
#
# The module's gma500 objects are always rebuilt (the MO directory is removed first). It is
# delivered only if kernel.release is the release of DELIVER_VERMAGIC and its vermagic equals
# DELIVER_VERMAGIC exactly; the manifest records tip, vermagic, srcversion, depends, sha256.
#
# Environment: DELIVER_WORK, DELIVER_CONFIG (paths from $HOME, or absolute), DELIVER_VERMAGIC
# (required); DELIVER_RUNNER (docker), DELIVER_IMAGE (resgx545/arch32:kernel), DELIVER_ROOT
# (/var/lib/machines/arch32-build), DELIVER_JOBS (the CPU count), DELIVER_SEED, DELIVER_FULL,
# DELIVER_CHECKED (recorded in the manifest), DELIVER_DRY_RUN=1 (print the commands).
set -euo pipefail
die() { echo "build-module.sh: $*" >&2; exit 1; }
[ $# -eq 1 ] || { echo "usage: build-module.sh TIP" >&2; exit 2; }
abs() { case $1 in /*) printf '%s' "$1" ;; *) printf '%s' "$HOME/$1" ;; esac; }
sha() { if command -v sha256sum >/dev/null; then sha256sum "$1"; else shasum -a 256 "$1"; fi | cut -d' ' -f1; }
field() { tr '\0' '\n' < "$2" | sed -n "s/^$1=//p" | head -n 1 | sed 's/ *$//'; }

: "${DELIVER_WORK:?}" "${DELIVER_CONFIG:?}" "${DELIVER_VERMAGIC:?}"
dry=${DELIVER_DRY_RUN:-}
work=$(abs "$DELIVER_WORK")
config=$(abs "$DELIVER_CONFIG")
want=$DELIVER_VERMAGIC
rel=${want%% *}
runner=${DELIVER_RUNNER:-docker}
image=${DELIVER_IMAGE:-resgx545/arch32:kernel}
root=${DELIVER_ROOT:-/var/lib/machines/arch32-build}
jobs=${DELIVER_JOBS:-$(getconf _NPROCESSORS_ONLN 2>/dev/null || echo 8)}
seed=
[ -n "${DELIVER_SEED:-}" ] && seed=$(abs "$DELIVER_SEED")
case $runner in
docker | chroot) ;;
*) die "DELIVER_RUNNER is docker or chroot, not $runner" ;;
esac
clone=$(pwd)
tip=$(git rev-parse --verify -q "$1^{commit}") || die "no commit $1 in $clone"
t=${tip:0:12}
[ -f "$config" ] || die "no config $config"
csha=$(sha "$config")
b=$work/build-${csha:0:12}
src=$work/src-$t
out=$work/out-$t
log=$work/log-$t.txt

run() {
	if [ -n "$dry" ]; then
		printf '$ %s\n' "$1"
	else
		bash -c "$1"
	fi
}
in_root() {   # COMMAND: the command in the toolchain root, /k the source, /b the build
	if [ "$runner" = docker ]; then
		echo "docker run --rm -u $(id -u):$(id -g) -v $src:/k:ro -v $b:/b -w /k $image sh -c '$1'"
	else
		echo "sudo systemd-nspawn -q -D $root --user=$(id -un) -E HOME=/tmp --bind-ro=$src:/k --bind=$b:/b --chdir=/k sh -c '$1'"
	fi
}
only_gma500() {   # FROM TO: TO changes nothing but gma500's sources and UAPI header since FROM
	[ -n "$1" ] || return 1
	git cat-file -e "$1^{commit}" 2>/dev/null || return 1
	git diff --name-only "$1" "$2" -- | awk '
		$0 == "drivers/gpu/drm/gma500/Kconfig" { bad = 1; next }
		/^drivers\/gpu\/drm\/gma500\// || $0 == "include/uapi/drm/sgxfive_drm.h" { next }
		{ bad = 1 }
		END { exit bad }'
}

# Where the build directory comes from, and whether it needs a full build.
seeding=
if [ ! -e "$b/.config" ] && [ -n "$seed" ]; then
	[ -f "$seed/Module.symvers" ] || die "the seed $seed is not a built build directory (no Module.symvers)"
	[ -f "$seed.built" ] || die "the seed has no record $seed.built: which commit it was built at is unknown"
	seeding=1
	built=$(cat "$seed.built")
	symvers=$seed/Module.symvers
else
	built=$(cat "$b.built" 2>/dev/null || true)
	symvers=$b/Module.symvers
fi
full=no
if [ ! -f "$symvers" ] || ! only_gma500 "$built" "$tip"; then
	full=yes
fi
if [ "$full" = yes ] && [ "$runner" = chroot ] && [ "${DELIVER_FULL:-}" != 1 ]; then
	echo "build-module.sh: $b needs a full kernel build (most of a day on the laptop): give" \
		"FORK_DELIVER_SEED (an O= directory built from this config, with its .built record," \
		"e.g. a series check's build-on) or allow it with FORK_DELIVER_FULL=1" >&2
	exit 2
fi

echo "build-module.sh: tip $t, build directory $b (full build: $full), log $log"
run "rm -rf $src $out && mkdir -p $src $b $out && git -C $clone archive $tip | tar -x -C $src"
if [ -n "$seeding" ]; then
	run "cp -a $seed/. $b/ && cp $seed.built $b.built"
fi
run "cp $config $b/.config"
mk="make O=/b ARCH=i386 LOCALVERSION="
run "$(in_root "$mk olddefconfig") > $log 2>&1" || die "olddefconfig failed (see $log)"
if [ "$full" = yes ]; then
	run "rm -f $b.built"
	run "$(in_root "$mk -j$jobs vmlinux modules") >> $log 2>&1" ||
		die "the full build failed (see $log)"
	run "echo $tip > $b.built"
fi
run "$(in_root "rm -rf /b/drivers/gpu/drm/gma500 && $mk modules_prepare && $mk -j$jobs M=/k/drivers/gpu/drm/gma500 MO=/b/drivers/gpu/drm/gma500") > $log.module 2>&1" ||
	die "the module build failed (see $log.module)"
ko=$b/drivers/gpu/drm/gma500/gma500_gfx.ko
if [ -n "$dry" ]; then
	echo "# checks: kernel.release = $rel, vermagic = '$want'; then $out/{gma500_gfx.ko,manifest}"
	exit 0
fi
cat "$log.module" >> "$log"
kr=$(cat "$b/include/config/kernel.release")
[ "$kr" = "$rel" ] || die "kernel.release is '$kr', not '$rel': not delivered"
[ -f "$ko" ] || die "no $ko"
vm=$(field vermagic "$ko")
[ "$vm" = "$want" ] || die "vermagic '$vm' is not the target's '$want': not delivered"
warnings=$(grep -c -E '(warning|error):' "$log.module" || true)
cp "$ko" "$out/gma500_gfx.ko"
{
	echo "tip=$tip"
	echo "subject=$(git log -1 --format=%s "$tip")"
	echo "checked=${DELIVER_CHECKED:-unknown}"
	echo "release=$kr"
	echo "vermagic=$vm"
	echo "srcversion=$(field srcversion "$ko")"
	echo "depends=$(field depends "$ko")"
	echo "sha256=$(sha "$out/gma500_gfx.ko")"
	echo "warnings=$warnings"
	echo "config=$config"
	echo "config_sha256=$csha"
	echo "runner=$runner"
	if [ "$runner" = docker ]; then echo "image=$image"; else echo "root=$root"; fi
	echo "build_dir=$b"
	echo "full_build=$full"
	echo "host=$(hostname)"
	echo "built=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > "$out/manifest"
cat "$out/manifest"
