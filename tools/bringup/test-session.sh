#!/bin/bash
# Arm the crash safety net for one SGX test session on the laptop (nothing persists across
# reboots): reboot 10 s after a panic, panic on oops, soft lockup and hung tasks, and send
# the kernel log with netconsole to HOST:PORT (listener there: netconsole-listen.py).
#   usage (on the laptop): sudo ./test-session.sh HOST [PORT [EPOCH]]
# HOST is an IPv4 address or a name the laptop resolves; PORT defaults to 6666.
# EPOCH is the host's clock (date +%s): the laptop's CMOS battery is flat, so its clock
# restarts in 2011 after a power-off and has no time server on the travel cable; a clock
# more than 5 s off EPOCH is set from it (and the RTC from that), and the change is logged.
# push-gma500.sh passes all three (SGX_NETCONSOLE_HOST, SGX_NETCONSOLE_PORT, its clock).
set -euo pipefail
host=${1:-}
port=${2:-6666}
epoch=${3:-}
[ -n "$host" ] || { echo "usage: test-session.sh HOST [PORT [EPOCH]]" >&2; exit 2; }
[[ -z $epoch || $epoch =~ ^[0-9]+$ ]] ||
	{ echo "test-session.sh: EPOCH must be seconds since 1970, not '$epoch'" >&2; exit 2; }
if [ -n "$epoch" ]; then
	now=$(date +%s)
	off=$((now - epoch))
	if [ "${off#-}" -gt 5 ]; then
		date -u -s "@$epoch" >/dev/null
		hwclock --systohc
		echo "clock set: was $now, off by ${off} s; now $epoch (RTC written)"
	fi
fi
if [[ $host =~ ^[0-9]+(\.[0-9]+){3}$ ]]; then
	ip=$host
else
	ip=$(getent ahostsv4 "$host" | awk 'NR == 1 { print $1 }')
	[ -n "$ip" ] || { echo "cannot resolve $host" >&2; exit 1; }
fi
sysctl -w kernel.panic=10 kernel.panic_on_oops=1 kernel.softlockup_panic=1 \
	kernel.hung_task_panic=1
dev=$(ip -o route get "$ip" | grep -o 'dev [^ ]*' | cut -d' ' -f2)
src=$(ip -o route get "$ip" | grep -o 'src [^ ]*' | cut -d' ' -f2)
# Without a MAC netconsole sends to ff:ff:ff:ff:ff:ff, which macOS drops: use the next
# hop's (the gateway's, or the listener's on a direct link), broadcast if it is unknown.
hop=$(ip -o route get "$ip" | grep -o 'via [^ ]*' | cut -d' ' -f2 || true)
hop=${hop:-$ip}
ping -c1 -W1 "$hop" >/dev/null 2>&1 || true
mac=$(ip neigh show "$hop" dev "$dev" | grep -o 'lladdr [^ ]*' | cut -d' ' -f2 || true)
modprobe netconsole netconsole="6665@$src/$dev,$port@$ip/$mac"
dmesg -n 8
echo "netconsole armed on $dev ($src) -> $ip:$port"
