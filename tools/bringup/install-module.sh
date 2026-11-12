#!/bin/bash
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
# Install a gma500 module into the laptop's test kernel without booting it: the install step
# that push-gma500.sh runs before its boot step, and the one for a module delivered from a
# checked fork tip (tools/fork/deliver-module.sh).
#
#   usage (on the laptop): sudo ./install-module.sh KO RELEASE PKGBASE [SHA256]
#
# - KO must hash to SHA256 when it is given (the manifest's), and its vermagic must equal the
#   installed gma500's exactly (the module that loads on that kernel): a '+' or a different
#   SMP/preempt/686 suffix is refused before anything changes.
# - The installed module and the initramfs are kept beside themselves with the first eight
#   characters of the old module's srcversion as a suffix (gma500_gfx.ko.B21FDA82,
#   initramfs-PKGBASE.img.B21FDA82); an existing backup is never overwritten.
# - depmod, mkinitcpio -p PKGBASE (gma500 loads from the initramfs), then the new initramfs is
#   unpacked (lsinitcpio -x) and must hold a gma500_gfx.ko with KO's sha256.
#
# SGX_DRY_RUN=1 prints the commands that change something instead of running them.
# SGX_MODULES_DIR (/usr/lib/modules) and SGX_BOOT_DIR (/boot) exist for the tests.
set -euo pipefail
[ $# -ge 3 ] && [ $# -le 4 ] || { echo "usage: install-module.sh KO RELEASE PKGBASE [SHA256]" >&2; exit 2; }
ko=$1 rel=$2 pkg=$3 want=${4:-}
die() { echo "install-module.sh: $*" >&2; exit 1; }
run() {
	if [ -n "${SGX_DRY_RUN:-}" ]; then
		printf '%s\n' "$*"
	else
		"$@"
	fi
}
sha() { sha256sum "$1" | cut -d' ' -f1; }
modinfo_field() {   # FIELD KO: one .modinfo value, as it is (vermagic ends in a space)
	tr '\0' '\n' < "$2" | sed -n "s/^$1=//p" | head -n 1
}
dst=${SGX_MODULES_DIR:-/usr/lib/modules}/$rel/kernel/drivers/gpu/drm/gma500/gma500_gfx.ko
img=${SGX_BOOT_DIR:-/boot}/initramfs-$pkg.img

[ -f "$ko" ] || die "no module $ko"
[ -f "$dst" ] || die "no gma500 installed for $rel ($dst): install the $pkg package first"
new_sha=$(sha "$ko")
[ -z "$want" ] || [ "$new_sha" = "$want" ] || die "$ko has sha256 $new_sha, not $want"
new_vm=$(modinfo_field vermagic "$ko")
old_vm=$(modinfo_field vermagic "$dst")
[ "$new_vm" = "$old_vm" ] ||
	die "vermagic '$new_vm' is not the installed kernel's '$old_vm': refused"
new_src=$(modinfo_field srcversion "$ko")
old_src=$(modinfo_field srcversion "$dst")
[ -n "$old_src" ] || die "the installed $dst has no srcversion"
suffix=${old_src:0:8}

if [ "$(sha "$dst")" = "$new_sha" ]; then
	echo "install-module.sh: srcversion $new_src is already installed"
else
	[ -e "$dst.$suffix" ] || run cp -p "$dst" "$dst.$suffix"
	[ ! -e "$img" ] || [ -e "$img.$suffix" ] || run cp -p "$img" "$img.$suffix"
	run install -m644 "$ko" "$dst"
fi
run depmod "$rel"
if [ -n "${SGX_DRY_RUN:-}" ]; then
	echo "mkinitcpio -p $pkg"
else
	mkinitcpio -p "$pkg" >/dev/null
fi
if [ -n "${SGX_DRY_RUN:-}" ]; then
	echo "lsinitcpio -x $img  # must hold gma500_gfx.ko with sha256 $new_sha"
	exit 0
fi
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
(cd "$tmp" && lsinitcpio -x "$img") >/dev/null 2>&1 || die "cannot unpack $img"
got=$(find "$tmp" -name gma500_gfx.ko -type f | head -n 1)
[ -n "$got" ] || die "the initramfs $img holds no gma500_gfx.ko"
[ "$(sha "$got")" = "$new_sha" ] || die "the initramfs $img holds a gma500_gfx.ko with sha256 $(sha "$got"), not $new_sha"
echo "installed srcversion $new_src (sha256 $new_sha) for $rel; old srcversion $old_src kept as $dst.$suffix and $img.$suffix; initramfs holds it"
