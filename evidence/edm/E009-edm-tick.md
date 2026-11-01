+++
id = "E009"
claim = "Left alone, the running firmware moves exactly four values: TIMER, EVENT_TIMER, USE0_SERV_EVENT and HostCtl dword 12; the last two advance at 997.46 Hz, and TIMER at 1/16 of the same 399.0 MHz"
unit = "edm"
method = "200 snapshots of the phase-3 kernel's sgx/regs over 40 s of a running firmware on the laptop, each read stamped with the laptop's clock before and after; rates by least squares against the stamps' midpoints; the laptop's clock compared with an NTP-synchronised clock over the direct cable before and after the run"
tiers = ["HW", "infer"]
date = "2026-10-30"
data = ["platform-edm-tick"]
terms = ["CR_TIMER", "CR_EVENT_TIMER", "CR_USE0_SERV_EVENT", "CR_USE1_SERV_EVENT", "host_ctl.edm_ticks", "host_ctl.ukernel_timer_clock"]
+++

**What moves.** Of the 269 values in each snapshot (the registers `sgx/regs` reads, HostCtl,
TA3DCtl and the CCB control words), four differ between snapshots: `TIMER` (`0x144`),
`EVENT_TIMER` (`0xacc`), `USE0_SERV_EVENT` (`0xb14`) and HostCtl dword 12. `CLKGATESTATUS`
reads `0x20` in all 200; `USE1_SERV_EVENT` stays `0x00010000`.

**Rates (against the laptop's clock).** HostCtl dword 12: 997.494 ± 0.008 per second.
`USE0_SERV_EVENT`: bit 16 always set, bits 15:0 counting at 997.491 ± 0.008 per second, 3
(186 snapshots) or 4 (14) counts ahead of dword 12. `TIMER`: 24937355 ± 195 per second.
`EVENT_TIMER`: bits 31:24 always `0x01`, bits 23:0 between `0x289` and `0x615eb`, below
`0x61a80` (400000, HostCtl dword 6).

**The laptop's clock.** It is not NTP-synchronised (no network but the cable). Compared with the
Mac's NTP-synchronised clock over one ssh session (round trips 9-14 ms), over 696 s, it runs
30 ± 17 ppm slow. Corrected, the tick is 997.46 Hz and `TIMER` 24.9366 MHz.

**[infer]** With HostCtl dword 6 = 400000 core clocks a tick, 997.46 Hz is a core clock of
398.99 MHz; `TIMER` x 16 gives 398.99 MHz too. Two counters agree on a clock 0.25% below the
DDK's `SYS_SGX_CLOCK_SPEED` constant of 400 MHz (`sysconfig.c:48`). `EVENT_TIMER`'s bit 24 and
its count staying below dword 6 fit a down-counter reloaded from dword 6 each tick. Bit 16 of
`USE0_SERV_EVENT` is the event queue's `EMPTY` flag and bits 15:0 its `COUNT` in Intel's SGX535
register list (emgd-psb_regs).

This does not show which clock feeds `TIMER` or the EDM timer (Q002), nor which EDM code
increments dword 12.
