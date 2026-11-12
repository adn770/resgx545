#!/bin/bash
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
# usage: build-igt-host.sh COMMIT     (on the build host; the host side of build-igt.sh)
#
# Build the IGT fork's sgxfive tests and libigt for i686 in the toolchain image, from the plain
# tree build-igt.sh unpacked (a git archive of COMMIT, no .git) in IGT_WORK/src, then smoke them
# in the same image: each binary's --list-subtests must exit 0 and name at least one subtest.
# Nothing runs on the host itself but docker. All in IGT_WORK (a path from $HOME, or absolute):
#
#   src/        the tree of COMMIT;  build/  the meson build directory, made afresh
#   log.txt     meson's and ninja's output
#   out/        the binaries, libigt.so.0, <name>.subtests/.stderr, the manifest: commit, branch,
#               image and its id, meson options, the binaries, a sha256 per file, the smoke
#               result per binary (ok <subtests> or FAILED rc=<rc>) and overall (pass or fail)
#
# A failed build exits 1 with the log's tail; a failed smoke is recorded in the manifest (the
# caller fails on it after copying it back).
# Environment: IGT_WORK (required), IGT_IMAGE (sgxhumation/arch32:igt), IGT_BRANCH_STATE (the
# manifest's branch line, from build-igt.sh), IGT_MESON_OPTIONS (those of the earlier build32).
set -euo pipefail
die() { echo "build-igt-host.sh: $*" >&2; exit 1; }
[ $# -eq 1 ] || { echo "usage: build-igt-host.sh COMMIT" >&2; exit 2; }
abs() { case $1 in /*) printf '%s' "$1" ;; *) printf '%s' "$HOME/$1" ;; esac; }
sha() { if command -v sha256sum >/dev/null; then sha256sum "$1"; else shasum -a 256 "$1"; fi | cut -d' ' -f1; }
COMMIT=$1
W=$(abs "${IGT_WORK:?IGT_WORK is not set}")
IMG=${IGT_IMAGE:-sgxhumation/arch32:igt}
OPTS=${IGT_MESON_OPTIONS:--Doverlay=disabled -Dchamelium=disabled -Dvalgrind=disabled \
-Dman=disabled -Ddocs=disabled -Dtestplan=disabled -Dsphinx=disabled -Dxe_driver=disabled \
-Dvmtb=disabled -Dlibdrm_drivers= -Drunner=enabled -Dlibunwind=enabled -Doping=disabled}
cd "$W" || die "no work directory $W"
[ -f src/tests/sgxfive/meson.build ] || die "the tree of $COMMIT has no tests/sgxfive"
names=$(grep -oE "'sgxfive_[a-z0-9_]+'" src/tests/sgxfive/meson.build | tr -d "'" | tr '\n' ' ')
names=${names% }
[ -n "$names" ] || die "tests/sgxfive/meson.build lists no programs"
targets="lib/libigt.so.0"
for n in $names; do targets="$targets tests/sgxfive/$n"; done
rm -rf build out
mkdir -p out
user="$(id -u):$(id -g)"
if ! docker run --rm --user "$user" -e HOME=/tmp -v "$W:/w" -w /w/src "$IMG" \
	bash -c "meson setup /w/build $OPTS && ninja -C /w/build $targets" > log.txt 2>&1; then
	tail -n 40 log.txt
	die "the build of $COMMIT failed (log: $W/log.txt)"
fi
cp build/lib/libigt.so.0 out/
{
	echo "commit=$COMMIT"
	echo "branch=${IGT_BRANCH_STATE:-unknown}"
	echo "image=$IMG"
	echo "image_id=$(docker image inspect -f '{{.Id}}' "$IMG")"
	echo "meson_options=$OPTS"
	echo "built=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
	echo "binaries=$names"
	echo "sha256.libigt.so.0=$(sha out/libigt.so.0)"
} > out/manifest.part
smoke=pass
for n in $names; do
	cp "build/tests/sgxfive/$n" out/
	echo "sha256.$n=$(sha "out/$n")" >> out/manifest.part
	rc=0
	docker run --rm --user "$user" -e HOME=/tmp -e LD_LIBRARY_PATH=/w/build/lib -v "$W:/w" \
		"$IMG" "/w/build/tests/sgxfive/$n" --list-subtests > "out/$n.subtests" 2> "out/$n.stderr" || rc=$?
	count=$(grep -c . "out/$n.subtests" || true)
	if [ "$rc" -eq 0 ] && [ "$count" -gt 0 ]; then
		echo "smoke.$n=ok $count" >> out/manifest.part
	else
		echo "smoke.$n=FAILED rc=$rc lines=$count" >> out/manifest.part
		smoke=fail
	fi
done
echo "smoke=$smoke" >> out/manifest.part
mv out/manifest.part out/manifest
cat out/manifest
