# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
# render_uapi.md section 10 and the linux fork's commit 35: a job whose client gave up while a
# recovery was held. debugfs hold_recovery is set and a render that faults on its unmapped stream
# page (tri --fault, 20 s wait, in the background) is held. A fill on another context is
# submitted behind it and its client is killed 2 s later: the file closes, the job stays in the
# firmware. hold_recovery is cleared and debugfs reset written: with commit 35 the kernel logs
# that it cancelled the closed context's job; before it, the job ran again after the reset.
# Each step prints the status counters (events, bus faults, deferred commands) and the driver's
# new kernel lines; a fill and a triangle at the end show the GPU works. Root through sudo -n.
set -u
T=${SGXFIVE_TEST:-$HOME/sgxfive-test-1110}
D=$(sudo -n sh -c 'ls -d /sys/kernel/debug/dri/*/sgx' | head -n 1)
[ -x "$T" ] || { echo "no $T: build userspace/libsgxfive (11.10) for the laptop first"; exit 1; }
echo "## uname"; uname -r
echo "## module"; modinfo -F srcversion gma500_gfx 2>/dev/null
echo "## tool"; sha256sum "$T"
mark() { sudo -n dmesg | wc -l; }
since() {   # the driver's lines after line $1
	sudo -n dmesg | tail -n +"$(( $1 + 1 ))" |
		grep -E "sgxfive|SGX (stop|boot|reset)|BIF|fault|recover|hung|cancel" |
		sed 's/^\[[ 0-9.]*\] //; s/^/klog: /'
}
status() { echo "status $1: $(sudo -n head -n 1 "$D/status")"; }
echo 1 | sudo -n tee "$D/reset" >/dev/null
sleep 1
N=$(mark)
echo "## hold and fault"
echo Y | sudo -n tee "$D/hold_recovery" >/dev/null
sudo -n "$T" tri --fault --wait-ms 20000 > /tmp/cc-tri.out 2>&1 &
sleep 2
status held
echo "## a fill behind it, its client killed after 2 s"
sudo -n timeout -s KILL 2 "$T" fill > /tmp/cc-fill.out 2>&1
echo "fill client exit: $?"
sleep 1
status closed
echo "## hold cleared, reset"
echo N | sudo -n tee "$D/hold_recovery" >/dev/null
s=$(date +%s%N)
echo 1 | sudo -n tee "$D/reset" >/dev/null
echo "reset: ret $?, $(( ($(date +%s%N) - s) / 1000000 )) ms"
wait
sleep 3
status after-reset
since "$N"
echo "## tri client"; grep -E "^job|FAILED|failed|diff" /tmp/cc-tri.out | head -3
echo "## health"
sudo -n "$T" fill 2>&1 | grep -E "^job|^diff"
sudo -n "$T" tri 2>&1 | grep -E "^diff|^tri 64x64 #1: [0-9]+ tri"
status end
