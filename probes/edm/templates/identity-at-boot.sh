# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
# render_uapi.md section 4 and Q005, on the linux fork's commit 32: the firmware's identity in
# DEV_QUERY before the firmware runs, after its load and after a reset. Works with and without
# the debug option: the reset is debugfs reset when the debug files exist, else a render that
# faults on its unmapped stream page (tri --fault), which the fault watchdog recovers.
# Each step prints the query's identity lines (core_sw, ddk) and the driver's identity lines
# ("SGX firmware: core ...", one per boot of the firmware) of the kernel log.
# Root through sudo -n.
set -u
T=${SGXFIVE_TEST:-$HOME/sgxfive-test-1110}
[ -x "$T" ] || { echo "no $T: build userspace/libsgxfive (11.10) for the laptop first"; exit 1; }
# the debug files exist only with the debug option (the sgx directory is there in any build)
D=$(sudo -n sh -c 'ls -d /sys/kernel/debug/dri/*/sgx 2>/dev/null' | head -n 1)
{ [ -n "$D" ] && sudo -n test -e "$D/reset"; } || D=''

echo "## uname"; uname -r
echo "## firmware"; sha256sum /lib/firmware/sgx545_ukernel.fw
echo "## module"; modinfo -F srcversion gma500_gfx 2>/dev/null
echo "## tool"; sha256sum "$T"
echo "## debug option: $([ -n "$D" ] && echo yes || echo no)"
ident() {
	echo "## identity $1"
	sudo -n "$T" query 2>&1 | grep -E "^(core_sw|ddk|fw_state)" | sed 's/^/query: /'
	echo "query: core_sw lines $(sudo -n "$T" query 2>&1 | grep -c '^core_sw')"
	sudo -n dmesg | grep "SGX firmware:" | sed 's/^\[[ 0-9.]*\] //' | sed 's/^/kline: /'
	echo "firmware boots logged: $(sudo -n dmesg | grep -c 'SGX firmware:')"
}
health() {
	echo "## health"
	sudo -n "$T" fill 2>&1 | grep -E "^job|^diff"
	sudo -n "$T" tri 2>&1 | grep -E "^diff|^tri 64x64 #1: [0-9]+ tri"
}
# GPU_INFO read in a tight loop on the render node while the debugfs reset restarts the firmware
# (written 0.5 s in, from a thread): the time of each change of SW_VALID and core_id_sw, the
# reset's own start and end, and how many reads fell in its window. FW_INFO is not read: it takes
# the device lock, which the reset holds, so it waits for the reset to end
during_reset() {
	sudo -n python3 - "$D/reset" <<'PY'
import ctypes, fcntl, os, struct, sys, threading, time

IOCTL = 0xC0106440      # DRM_IOWR(DRM_COMMAND_BASE + DEV_QUERY, struct dev_query_args): 16 bytes
fd = os.open("/dev/dri/renderD128", os.O_RDWR)
gpu = ctypes.create_string_buffer(32)       # struct drm_sgxfive_dev_query_gpu_info
arg = ctypes.create_string_buffer(struct.pack("<IIQ", 0, len(gpu), ctypes.addressof(gpu)))
res = {}


def reset():
    time.sleep(0.5)
    res["start"] = time.monotonic()
    with open(sys.argv[1], "w") as f:
        f.write("1")
    res["end"] = time.monotonic()


t = threading.Thread(target=reset)
t0 = time.monotonic()
t.start()
last = None
n = n_in = invalid_in = 0
changes = []
while time.monotonic() - t0 < 3.0:
    fcntl.ioctl(fd, IOCTL, arg)
    now = time.monotonic()
    valid = struct.unpack_from("<I", gpu.raw, 28)[0] & 1
    ddk = struct.unpack_from("<I", gpu.raw, 8)[0]
    n += 1
    if "start" in res and ("end" not in res):
        n_in += 1
        invalid_in += not valid
    if (valid, ddk) != last:
        changes.append((now - t0, valid, ddk))
        last = (valid, ddk)
t.join()
print("during: %d reads, reset written at %.0f ms, returned at %.0f ms"
      % (n, (res["start"] - t0) * 1e3, (res["end"] - t0) * 1e3))
for when, valid, ddk in changes:
    print("during: %.1f ms: SW_VALID %d core_id_sw %d" % (when * 1e3, valid, ddk))
print("during: %d reads while the reset ran, %d of them with SW_VALID clear" % (n_in, invalid_in))
PY
}
W=$(mktemp)
ident before-load
echo "## load (the first context: a fill)"
sudo -n "$T" fill 2>&1 | grep -E "^job|^diff"
ident after-load
echo "## reset"
if [ -n "$D" ]; then
	s=$(date +%s%N)
	echo 1 | sudo -n tee "$D/reset" >/dev/null
	echo "debugfs reset: ret $?, $(( ($(date +%s%N) - s) / 1000 )) us"
else
	echo "no debugfs: a faulting render, recovered by the fault watchdog"
	sudo -n "$T" tri --fault --wait-ms 3000 2>&1 | grep -E "^job|FAILED|failed|diff" | head -3
	sleep 2
fi
sudo -n dmesg | grep -E "SGX (stop|boot|reset)|recover|resetting" | tail -6 | sed 's/^\[[ 0-9.]*\] //; s/^/kline: /'
ident after-reset
if [ -n "$D" ]; then
	echo "## query during a reset"
	during_reset
	ident after-second-reset
fi
rm -f "$W"
health
