#!/bin/bash
# Build gma500 on the build host, install it on the laptop's test kernel and boot that
# kernel once with the crash safety net armed; returns when the new module is up. Runs on
# the workstation, which relays the files between the two hosts over ssh. With
# SGX_BUILD_HOST=target the laptop builds the module itself, in its own kernel tree through
# sgx-build (the toolchain root the kernel was built with), and installs it from there.
#
#   usage: [SGX_RENDER=0] [SGX_DRY_RUN=1] tools/bringup/push-gma500.sh [--ko FILE] [--no-reboot]
#
# --ko FILE installs that module instead of building one: a module delivered from a checked
# fork tip (tools/fork/deliver-module.sh), checked against the sha256 of the manifest beside
# it when there is one. The install is install-module.sh on the laptop (old module and
# initramfs kept under the old srcversion, vermagic checked, initramfs verified); --no-reboot
# stops there.
# The test kernel boots with gma500_gfx.sgx_render=1 (the render node the tests use) unless
# SGX_RENDER=0 asks for the gate-off boot (no render node, card0 answers only DEV_QUERY).
# The installed kernel is 7.3.0-sgx with LOCALVERSION_AUTO off, so a module built with an
# empty LOCALVERSION keeps matching it. gma500 loads from the initramfs, hence mkinitcpio.
# SGX_DRY_RUN=1 prints the commands instead of running them.
#
# Settings (environment, or tools/bringup/local.env; see local.env.example):
#   SGX_BUILD_HOST       ssh destination of the build host, or target (sgx-build)
#   SGX_TARGET_HOST      ssh destination of the test laptop           (sgx-target)
#   SGX_TARGET_SSH_OPTS  extra ssh/scp options for the laptop         (none)
#   SGX_KERNEL_TREE      kernel tree on the build host, from $HOME    (src/linux-sgx)
#   SGX_KERNEL_RELEASE   release of the installed test kernel         (7.3.0-sgx)
#   SGX_KERNEL_PKGBASE   package of the installed test kernel         (linux-sgx)
#   SGX_BUILD_JOBS       make -j on the build host                    ($(nproc) there)
#   SGX_BUILD_PATH       directories prepended to PATH on the build host (none)
#   SGX_NETCONSOLE_HOST  where the laptop sends its kernel log        (the build host;
#                        required when the laptop builds)
#   SGX_NETCONSOLE_PORT  UDP port of netconsole-listen.py             (6666)
# The remote build command is wrapped in bash -c, so any login shell works on the build host.
set -euo pipefail
SCRIPTS=$(dirname "$0")
LOCAL_ENV=${SGX_LOCAL_ENV:-$SCRIPTS/local.env}
# shellcheck source=/dev/null
[ -f "$LOCAL_ENV" ] && . "$LOCAL_ENV"
BUILD=${SGX_BUILD_HOST:-sgx-build}
TARGET=${SGX_TARGET_HOST:-sgx-target}
read -ra TOPTS <<< "${SGX_TARGET_SSH_OPTS:-}"
KTREE=${SGX_KERNEL_TREE:-src/linux-sgx}
KREL=${SGX_KERNEL_RELEASE:-7.3.0-sgx}
KPKG=${SGX_KERNEL_PKGBASE:-linux-sgx}
JOBS=${SGX_BUILD_JOBS:-'$(nproc)'}
BPATH=${SGX_BUILD_PATH:+export PATH=$SGX_BUILD_PATH:\$PATH; }
if [ "$BUILD" = target ]; then
	NC_HOST=${SGX_NETCONSOLE_HOST:-}
	[ -n "$NC_HOST" ] || { echo "push-gma500.sh: the laptop builds: set SGX_NETCONSOLE_HOST" \
		"to an address of this machine the laptop reaches" >&2; exit 1; }
else
	NC_HOST=${SGX_NETCONSOLE_HOST:-$(ssh -G "$BUILD" 2>/dev/null | awk '$1 == "hostname" { print $2; exit }')}
fi
NC_PORT=${SGX_NETCONSOLE_PORT:-6666}
MOD=drivers/gpu/drm/gma500/gma500_gfx.ko
usage() { echo "usage: push-gma500.sh [--ko FILE] [--no-reboot]" >&2; exit 2; }
KO_FILE= REBOOT=1
while [ $# -gt 0 ]; do
	case $1 in
	--no-reboot) REBOOT= ;;
	--ko) [ $# -ge 2 ] || usage; KO_FILE=$2; shift ;;
	*) usage ;;
	esac
	shift
done
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

run() {
	if [ -n "${SGX_DRY_RUN:-}" ]; then
		printf '%s\n' "$*"
	else
		"$@"
	fi
}
on_target() { run ssh ${TOPTS[@]+"${TOPTS[@]}"} "$TARGET" "$@"; }

SHA=
if [ -n "$KO_FILE" ]; then
	manifest=$(dirname "$KO_FILE")/manifest
	[ -f "$manifest" ] && SHA=$(sed -n 's/^sha256=//p' "$manifest")
	run scp -q ${TOPTS[@]+"${TOPTS[@]}"} "$KO_FILE" "$TARGET:/tmp/gma500_gfx.ko"
	KO=/tmp/gma500_gfx.ko
elif [ "$BUILD" = target ]; then
	on_target "SGX_KERNEL_TREE=$KTREE sgx-build kernel make ARCH=i386 -j$JOBS \
		M=drivers/gpu/drm/gma500 >/dev/null &&
		strings $KTREE/$MOD | grep -q \"^vermagic=$KREL \""
	KO=$KTREE/$MOD
else
	run ssh "$BUILD" "bash -c '${BPATH}cd $KTREE &&
		LOCALVERSION= make ARCH=i386 -j$JOBS M=drivers/gpu/drm/gma500 >/dev/null &&
		strings $MOD | grep -q \"^vermagic=$KREL \"'"
	run scp -q "$BUILD:$KTREE/$MOD" "$tmp/"
	run scp -q ${TOPTS[@]+"${TOPTS[@]}"} "$tmp/gma500_gfx.ko" "$TARGET:/tmp/"
	KO=/tmp/gma500_gfx.ko
fi
run scp -q ${TOPTS[@]+"${TOPTS[@]}"} "$SCRIPTS/boot-test-kernel.sh" "$SCRIPTS/test-session.sh" \
	"$SCRIPTS/install-module.sh" "$TARGET:"
on_target "sudo ./install-module.sh $KO $KREL $KPKG${SHA:+ $SHA}"
[ -n "$REBOOT" ] || exit 0

on_target "sudo ./boot-test-kernel.sh ${SGX_RENDER:-1} $KPKG >/dev/null" || true
run sleep 15
until on_target -o ConnectTimeout=4 -o BatchMode=yes \
	"test \"\$(uname -r)\" = $KREL && test \"\$(cut -d. -f1 /proc/uptime)\" -lt 300 &&
	 sudo test -e /sys/kernel/debug/dri/0/sgx/load" 2>/dev/null; do
	sleep 5
done
# Every test boot runs with the safety net armed: panic and lockup reboots,
# netconsole to the listener (tools/bringup/test-session.sh, netconsole-listen.py).
on_target "sudo ./test-session.sh $NC_HOST $NC_PORT >/dev/null"
on_target 'sudo dmesg | grep -E "# gma500_[a-z_]+: pass|^\[[ 0-9.]+\] (not )?ok [0-9]+ gma500"'
