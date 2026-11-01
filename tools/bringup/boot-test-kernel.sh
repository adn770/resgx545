#!/bin/bash
# Reboot the laptop once into a test kernel; the next reboot returns to the default
# (distro) entry.   usage (on the laptop): sudo ./boot-test-kernel.sh [sgx_render [pkgbase]]
#
# sgx_render (1 by default) becomes gma500_gfx.sgx_render on the test kernel's command line:
# 1 creates the sgxfive render node the tests use, 0 boots with the gate off (no render
# node, card0 answers only DEV_QUERY); a kernel without the parameter ignores it. pkgbase
# (linux-sgx by default) names the test kernel's package, so two test kernels can be
# installed side by side (one the fallback of the other). The test kernels' entries read
# the parameter from grubenv (sgx_cmdline), so the distro kernels never see it;
# grub-mkconfig drops that hook, so it is put back here on every run.
set -euo pipefail
render=${1:-1}
pkg=${2:-linux-sgx}
[ "$render" = 0 ] || [ "$render" = 1 ] || { echo "sgx_render must be 0 or 1" >&2; exit 1; }
cfg=${SGX_GRUB_CFG:-/boot/grub/grub.cfg}
adv=$(grep -o "submenu 'Advanced options for Arch Linux' \$menuentry_id_option '[^']*'" \
	"$cfg" | grep -o "gnulinux-advanced-[^']*")
sgx=$(grep -o "gnulinux-$pkg-advanced-[^']*" "$cfg" | head -1)
[ -n "$adv" ] && [ -n "$sgx" ] || { echo "no $pkg entry in grub.cfg" >&2; exit 1; }
hook='load_env -f /boot/grub/grubenv sgx_cmdline'
re="^([[:space:]]*)linux([[:space:]]+/boot/vmlinuz-$pkg .*)\$"
if ! grep -qE "/boot/vmlinuz-$pkg .*\\\$sgx_cmdline" "$cfg"; then
	tmp=$(mktemp)
	sed -E "s|$re|\\1$hook\\n\\1linux\\2 \$sgx_cmdline|" "$cfg" > "$tmp"
	cat "$tmp" > "$cfg"
	rm -f "$tmp"
	grub-script-check "$cfg"
fi
grub-editenv - set "sgx_cmdline=gma500_gfx.sgx_render=$render"
grub-reboot "$adv>$sgx"
grub-editenv list
systemctl reboot
