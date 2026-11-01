+++
id = "E005"
claim = "HostCtl is 17 dwords; before the first kick the host writes only PowerStatus, HWRecoverySampleRate = 10, uKernelTimerClock = 400000, ActivePowManSampleRate = 0, HostClock and InitStatus = 0, and on the laptop dword 12 then advances once per EDM tick"
unit = "firmware"
method = "reading of the GPL Cedarview kernel module (sgxinit.c, sgxpower.c, sgxutils.c); srvinit's HostCtl at the hand-over under the extraction harness; HostCtl read through the phase-3 kernel's debugfs after each of 20 boots and in 200 snapshots of the running firmware"
tiers = ["DDK", "CAP", "HW"]
date = "2026-10-30"
data = ["firmware-init-payload", "platform-boot", "platform-edm-tick"]
terms = ["host_ctl", "host_ctl.init_status", "host_ctl.power_status", "host_ctl.cleanup_status", "host_ctl.ukernel_detected_lockups", "host_ctl.host_detected_lockups", "host_ctl.hw_recovery_sample_rate", "host_ctl.ukernel_timer_clock", "host_ctl.active_powman_sample_rate", "host_ctl.interrupt_flags", "host_ctl.interrupt_clear_flags", "host_ctl.bp_set_clear_signal", "host_ctl.num_active_power_events", "host_ctl.edm_ticks", "host_ctl.host_clock", "host_ctl.assert_fail", "host_ctl.perf_group", "host_ctl.opencl_delay_count"]
+++

**The layout and the host's writes (DDK).** `SGXMKIF_HOST_CTL`
(`src/services4/include/sgx_mkif_km.h`) has 17 dwords, `0x44` bytes, with `SUPPORT_HW_RECOVERY`
on and EDM breakpoints off, the size srvinit reports (E001). The host writes, in the whole
module: dword 0 (`ui32InitStatus`) = 0 just before the kick; dword 1 (`ui32PowerStatus`) `|=
0x20` in `DevInitSGXPart2KM` and 0 at power-on; dword 2 `&= ~1` after a cleanup command; dword 4
`++` on a lockup the host timer sees; dwords 5, 6 and 7 = 10, `400000000 / 1000` and 0
(`SGXPostPowerState` through `SGXUpdateTimingInfo`); dword 9 `|=` / `&= ~` for recovery and
active power; dword 10 = 0 on the breakpoint path; dword 11 `++` after an active power-down;
dword 13 = `OSClockus()` before every kick; dword 14 = 0 after the debug dump logs it; dword 15
from the HWPerf status request; dword 16 from the host timer. Dwords 3, 8 and 12 have no host
write. Before the first kick, then, only dwords 0, 1, 5, 6, 7 and 13 have been written.

**At the hand-over (CAP).** In the REV1 run of firmware-init-payload, the HostCtl allocation
srvinit hands the kernel is all zero.

**On the laptop (HW).** After each of the 20 boots of platform-boot, dwords 0-11 read `1, 0, 0,
0, 0, 10, 400000, 0, 0, 0, 0, 0` and dword 14 (`ui32AssertFail`) reads 0; dword 13 holds the
host clock written before the kick. Dword 12 is non-zero after every boot. In platform-edm-tick
it takes 200 distinct values in 200 snapshots over 40 s and rises by 997.49 a second, in step
with `USE0_SERV_EVENT` (E009): it counts the EDM's timer ticks. No other HostCtl dword changes
while the firmware runs alone.

The DDK calls dword 12 `ui32TimeWraps`; nothing in the module writes or reads it. The
glossary's `host_ctl.edm_ticks` names it after what it does.

This does not show which EDM code writes dword 12, nor what dwords 3, 8 and 9 do on a hardware
recovery, which no run caused.
