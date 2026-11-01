#!/bin/bash
# install1135.sh: install the series-checked module on the laptop and reload it. Only after 6 or more PASS of
# the series check (recheck.pass). Keeps ~/gma500_gfx.ko.34729eb8 (the module that was installed); prints the
# installed and the loaded srcversion; unbinds vtcon1 first, binds it again, then writes 9 and 10 to the
# backlight; keeps the kernel log of the load (the module's KUnit output) in ~/p1134b-modload-kernel.txt.
set -u
H=$(cd "$(dirname "$0")" && pwd)
TIP=$(cut -d' ' -f3 "$H/commits.txt")
[ "$(cat "$H/recheck.pass" 2>/dev/null)" = "$TIP" ] || { echo "the series check has not passed for the tip: nothing installed"; exit 1; }
SSH="ssh -o HostKeyAlias=cedar -o BatchMode=yes jtorra@10.42.0.2"
$SSH 'bash -s' <<'REMOTE'
set -u
KO=$HOME/src/linux-sgx/drivers/gpu/drm/gma500/gma500_gfx.ko
DST=/lib/modules/7.3.0-resgx545/kernel/drivers/gpu/drm/gma500/gma500_gfx.ko
[ -f ~/gma500_gfx.ko.34729eb8 ] || cp $DST ~/gma500_gfx.ko.34729eb8
echo "kept previous: $(modinfo -F srcversion ~/gma500_gfx.ko.34729eb8)"
echo "built:     $(modinfo -F srcversion $KO) vermagic $(modinfo -F vermagic $KO)"
echo "installed: $(modinfo -F srcversion $DST) vermagic $(modinfo -F vermagic $DST)"
[ "$(modinfo -F vermagic $KO)" = "$(modinfo -F vermagic $DST)" ] || { echo "vermagic differs: stop"; exit 1; }
sudo install -m644 $KO $DST && sudo depmod 7.3.0-resgx545 || exit 1
echo "after install: $(modinfo -F srcversion gma500_gfx)"
echo 0 | sudo tee /sys/class/vtconsole/vtcon1/bind >/dev/null
sudo rmmod gma500_gfx 2>&1 || { echo "rmmod failed"; echo 1 | sudo tee /sys/class/vtconsole/vtcon1/bind >/dev/null; exit 2; }
T0=$(date '+%Y-%m-%d %H:%M:%S')
sudo modprobe gma500_gfx sgx_render=1 2>&1 || { echo "modprobe failed"; exit 3; }
echo 1 | sudo tee /sys/class/vtconsole/vtcon1/bind >/dev/null
sleep 2
echo 9 | sudo tee /sys/class/backlight/acpi_video0/brightness >/dev/null
echo 10 | sudo tee /sys/class/backlight/acpi_video0/brightness >/dev/null
sudo journalctl -k --since "$T0" --no-pager > ~/p1134b-modload-kernel.txt 2>&1
echo "load log: $(wc -l < ~/p1134b-modload-kernel.txt) lines, KUnit: $(grep -c 'ok [0-9]* gma500' ~/p1134b-modload-kernel.txt) suites ok, $(grep -c 'not ok' ~/p1134b-modload-kernel.txt) not ok"
echo "installed: $(modinfo -F srcversion gma500_gfx)"
echo "loaded:    $(sudo cat /sys/module/gma500_gfx/srcversion)"
sudo ls /sys/kernel/debug/dri/0/sgx/ | tr '\n' ' ' | grep -o "render_k[a-z]*" | tr '\n' ' '; echo
sudo cat /sys/kernel/debug/dri/0/sgx/status | head -1
REMOTE
mkdir -p "$H/logs"
scp -q -o HostKeyAlias=cedar jtorra@10.42.0.2:p1134b-modload-kernel.txt "$H/logs/modload-kernel-1134b.txt"
