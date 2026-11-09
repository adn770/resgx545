#!/bin/sh
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
#
# The linux fork's series check: every commit builds and passes KUnit. For each commit in
# BASE..HEAD of the clone it runs in (the current directory), with DRM_GMA500_SGXFIVE_DEBUG off
# and, from the commit whose Kconfig adds it, on:
#
#   - build gma500 for i686 in the laptop's toolchain image with the laptop's config and the
#     KUnit option: W=1 over drivers/gpu/drm/gma500/ (no warning or error there), then the
#     whole kernel and its modules (modpost: no undefined symbol). Each config has its own
#     build directory (flipping the option in one would change the embedded .config and
#     relink vmlinux every time). A commit that changes only gma500's sources or its UAPI
#     header since the directory's last build (not its Kconfig) builds gma500 alone, W=1 with
#     its own modpost against the directory's Module.symvers: minutes instead of the full
#     build's half hour on the laptop. The last built commit is recorded per config
#     (<work>/build-<config>.built), so a later run continues incrementally, and an empty
#     directory starts as a copy of the other config's;
#   - run the gma500 KUnit suites under qemu-system-i386 (tools/testing/kunit/kunit.py) in a
#     container that has qemu (built here from archlinux:latest when missing).
#
# One PASS/FAIL line per commit and config; the exit status is 1 if any failed. Run it on the
# build host in a scratch clone of the fork: it checks out each commit (detached) in that clone
# and goes back to where it was at the end. The first build of a config's directory is a full
# kernel build; later ones are incremental.
#
#   fork-check.sh BASE [HEAD]               check BASE..HEAD (HEAD defaults to HEAD)
#   CHECK_DRY_RUN=1 fork-check.sh BASE ...  print the commands instead of running them
#   fork-check.sh --kunit-summary LOG       summarise a kunit.py log (exit 1 unless all passed)
#   fork-check.sh --gma500-warnings LOG     count warnings and errors in gma500 (exit 1 if any)
#   fork-check.sh --gma500-warnings LOG all  count every one (a gma500-only build's log)
#
# Environment: CHECK_CONFIG, the laptop's kernel config (default
# ~/src/linux-sgx-travel/.config); CHECK_WORK, the build and log directory (default
# <clone>-check); CHECK_BUILD_IMAGE (default resgx545/arch32:kernel, gcc 15 for i686; tag the
# build host's existing image with that name once: docker tag OLD resgx545/arch32:kernel);
# CHECK_KUNIT_IMAGE (default resgx545/arch32:kunit, the build image plus qemu); CHECK_JOBS
# (default the CPU count). CHECK_RUNNER=chroot runs both steps in the laptop's build root
# (CHECK_ROOT, default /var/lib/machines/arch32-build, with qemu-system-x86 installed) instead
# of docker, so the laptop checks the series alone (KUnit under TCG: slow); it requires CHECK_WORK, since
# the default directory would mean a from-scratch kernel build, and is refused without it.
set -u

kunit_summary() {
	log=$1
	ran=$(sed -n 's/.*Testing complete\. Ran \([0-9]*\) tests\{0,1\}: passed: \([0-9]*\).*/\1/p' "$log" | tail -n 1)
	passed=$(sed -n 's/.*Testing complete\. Ran \([0-9]*\) tests\{0,1\}: passed: \([0-9]*\).*/\2/p' "$log" | tail -n 1)
	suites=$(sed -n 's/.*=\{1,\} \(gma500_[A-Za-z0-9_]*\) (\([0-9]*\) subtests\{0,1\}) =\{1,\}.*/\1:\2/p' "$log" | tr '\n' ' ' | sed 's/ $//')
	if [ -z "$ran" ]; then
		echo "kunit: no result"
		return 1
	fi
	echo "kunit $passed/$ran ($suites)"
	[ "$ran" -gt 0 ] && [ "$passed" = "$ran" ] && [ -n "$suites" ]
}

gma500_warnings() {   # LOG [all]: all, a gma500-only build, whose paths may be relative
	if [ "${2:-}" = all ]; then
		n=$(grep -c -E '[^ :]+:[0-9]+(:[0-9]+)?: (warning|error):' "$1")
	else
		n=$(grep -c -E 'drivers/gpu/drm/gma500/[^ :]*:[0-9]+(:[0-9]+)?: (warning|error):' "$1")
	fi
	echo "$n"
	[ "$n" -eq 0 ]
}

case "${1:-}" in
--kunit-summary) kunit_summary "$2"; exit $? ;;
--gma500-warnings) gma500_warnings "$2" "${3:-}"; exit $? ;;
esac

if [ $# -lt 1 ] || [ $# -gt 2 ]; then
	echo "usage: fork-check.sh BASE [HEAD] | --kunit-summary LOG | --gma500-warnings LOG" >&2
	exit 2
fi

base=$1
head=${2:-HEAD}
dry=${CHECK_DRY_RUN:-}
repo=$(git rev-parse --show-toplevel) || exit 2
config=${CHECK_CONFIG:-$HOME/src/linux-sgx-travel/.config}
work=${CHECK_WORK:-$repo-check}
bimg=${CHECK_BUILD_IMAGE:-resgx545/arch32:kernel}
kimg=${CHECK_KUNIT_IMAGE:-resgx545/arch32:kunit}
runner=${CHECK_RUNNER:-docker}
root=${CHECK_ROOT:-/var/lib/machines/arch32-build}
case $runner in
docker | chroot) ;;
*) echo "fork-check.sh: CHECK_RUNNER is docker or chroot, not $runner" >&2; exit 2 ;;
esac
if [ "$runner" = chroot ] && [ -z "${CHECK_WORK:-}" ]; then
	echo "fork-check.sh: CHECK_RUNNER=chroot needs CHECK_WORK (an existing build directory," \
		"e.g. \$HOME/src/linux-sgx-checkout-check): without it the laptop would start a" \
		"from-scratch kernel build" >&2
	exit 2
fi
jobs=${CHECK_JOBS:-$(getconf _NPROCESSORS_ONLN 2>/dev/null || echo 8)}
ug="$(id -u):$(id -g)"
orig=$(git symbolic-ref -q --short HEAD || git rev-parse HEAD)
commits=$(git rev-list --reverse "$base..$head") || exit 2

run() {
	if [ -n "$dry" ]; then
		printf '$ %s\n' "$1"
	else
		sh -c "$1"
	fi
}

kunitconfig() {
	opts="CONFIG_KUNIT=y CONFIG_PCI=y CONFIG_DRM=y CONFIG_DRM_GMA500=y CONFIG_DRM_GMA500_KUNIT_TEST=y"
	[ "$1" = on ] && opts="$opts CONFIG_DEBUG_FS=y CONFIG_DRM_GMA500_SGXFIVE_DEBUG=y"
	echo "$opts"
}

# The same mount points under both runners (/k the tree, /b the build, /kb the KUnit build,
# /kc its configs): a work directory one runner built stays incremental under the other.
# Both compile with the build image's gcc (the laptop's), KUnit included.
in_root() {   # in_root IMAGE MOUNTS COMMAND
	if [ "$runner" = docker ]; then
		echo "docker run --rm -u $ug $2 -w /k $1 sh -c '$3'"
	else
		echo "sudo systemd-nspawn -q -D $root --user=$(id -un) -E HOME=/tmp $(echo "$2" |
			sed -e 's/-v \([^ ]*\):ro/--bind-ro=\1/g' -e 's/-v /--bind=/g') --chdir=/k sh -c '$3'"
	fi
}
if [ "$runner" = docker ]; then
	run "docker image inspect $kimg >/dev/null 2>&1 || printf 'FROM $bimg\\nRUN pacman -Sy --noconfirm --needed qemu-system-x86 && pacman -Scc --noconfirm\\n' | docker build -q -t $kimg -" || exit 1
else
	# /var/lib/machines is mode 0700: look inside as root
	run "sudo -n test -x $root/usr/bin/qemu-system-i386 || { echo 'no qemu in $root: install qemu-system-x86 there' >&2; exit 1; }" || exit 1
fi
run "mkdir -p $work/build-off $work/build-on $work/log $work/kc $work/kunit-off $work/kunit-on"

# The commit each config's directory last built (empty: none, build it all).
built_off=$(cat "$work/build-off.built" 2>/dev/null || true)
built_on=$(cat "$work/build-on.built" 2>/dev/null || true)

# only_gma500 FROM TO: TO changes nothing but gma500's sources and its UAPI header since FROM
only_gma500() {
	[ -n "$1" ] || return 1
	git diff --name-only "$1" "$2" -- | awk '
		$0 == "drivers/gpu/drm/gma500/Kconfig" { bad = 1; next }
		/^drivers\/gpu\/drm\/gma500\// || $0 == "include/uapi/drm/sgxfive_drm.h" { next }
		{ bad = 1 }
		END { exit bad }'
}

fail=0
n=0
for c in $commits; do
	n=$((n + 1))
	h=$(echo "$c" | cut -c1-12)
	subject=$(git log -1 --format=%s "$c")
	cfgs=off
	if git show "$c:drivers/gpu/drm/gma500/Kconfig" 2>/dev/null |
	   grep -q '^config DRM_GMA500_SGXFIVE_DEBUG$'; then
		cfgs="off on"
	fi
	run "git checkout -q --detach $c"
	for cfg in $cfgs; do
		if [ "$cfg" = on ]; then flag=-e; else flag=-d; fi
		blog=$work/log/$(printf %02d "$n")-$h-$cfg-build.log
		klog=$work/log/$(printf %02d "$n")-$h-$cfg-kunit.log
		[ -n "$dry" ] && echo "# $h debug=$cfg"
		eval "last=\$built_$cfg"
		if only_gma500 "$last" "$c"; then
			scope=all
			run "$(in_root "$bimg" "-v $repo:/k:ro -v $work/build-$cfg:/b" "make O=/b ARCH=i386 -j$jobs W=1 M=/k/drivers/gpu/drm/gma500 MO=/b/drivers/gpu/drm/gma500 && echo build done") > $blog 2>&1"
		else
			scope=
			# an empty directory starts from the other config's (not its record): the debug flip is
			# incremental, a build from scratch takes most of a day on the laptop
			if [ "$cfg" = on ]; then other=off; else other=on; fi
			run "[ -e $work/build-$cfg/.config ] || [ ! -e $work/build-$other/.config ] || cp -a $work/build-$other/. $work/build-$cfg/"
			run "cp $config $work/build-$cfg/.config"
			run "$(in_root "$bimg" "-v $repo:/k:ro -v $work/build-$cfg:/b" "scripts/config --file /b/.config -e DRM_GMA500_KUNIT_TEST $flag DRM_GMA500_SGXFIVE_DEBUG -d X86_DECODER_SELFTEST && make O=/b ARCH=i386 olddefconfig && make O=/b ARCH=i386 -j$jobs W=1 drivers/gpu/drm/gma500/ && make O=/b ARCH=i386 ZSTD=zstd-kernel -j$jobs && echo build done") > $blog 2>&1"
		fi
		brc=$?
		run "printf '%s\\n' $(kunitconfig "$cfg") > $work/kc/$cfg.kunitconfig"
		run "$(in_root "$kimg" "-v $repo:/k:ro -v $work/kunit-$cfg:/kb -v $work/kc:/kc:ro" "python3 tools/testing/kunit/kunit.py run --arch=i386 --build_dir=/kb --kunitconfig=/kc/$cfg.kunitconfig --jobs=$jobs") > $klog 2>&1"
		if [ -n "$dry" ]; then
			run "echo $c > $work/build-$cfg.built"
			eval "built_$cfg=$c"
			echo "DRY $h debug=$cfg $subject"
			continue
		fi
		if [ "$brc" -eq 0 ]; then
			echo "$c" > "$work/build-$cfg.built"
			eval "built_$cfg=$c"
		else              # a failed build may leave the directory half built: rebuild all
			rm -f "$work/build-$cfg.built"
			eval "built_$cfg="
		fi
		if [ "$brc" -ne 0 ]; then
			build="build FAILED ($blog)"
		elif ! w=$(gma500_warnings "$blog" "$scope"); then
			build="build: $w gma500 warnings ($blog)"
			brc=1
		else
			build="build W=1 clean"
		fi
		if k=$(kunit_summary "$klog"); then krc=0; else krc=1; k="$k ($klog)"; fi
		if [ "$brc" -eq 0 ] && [ "$krc" -eq 0 ]; then
			echo "PASS $h debug=$cfg $build, $k | $subject"
		else
			echo "FAIL $h debug=$cfg $build, $k | $subject"
			fail=1
		fi
	done
done
run "git checkout -q $orig"
exit $fail
