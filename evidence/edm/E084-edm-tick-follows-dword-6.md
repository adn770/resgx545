+++
id = "E084"
claim = "The EDM tick lasts HostCtl dword 6 cycles of a 399.0 MHz clock: with dword 6 at 200000, 400000 and 800000 the tick runs at 1995.00, 997.48 and 498.76 Hz, 399.00 MHz to within 0.01 MHz each time, while TIMER counts 1/16 of that clock whatever dword 6 holds"
unit = "edm"
method = "probes/edm/tick-rate.toml on the laptop, linux fork with the debug option on: for each dword 6 value, written through the debug group's timer_clock file, the firmware stopped, loaded and booted, then 200 snapshots of sgx/regs over 41 s, each stamped with the laptop's clock before and after; rates by least squares against the stamps' midpoints"
tiers = ["HW"]
date = "2026-11-01"
data = ["edm-tick-rate"]
terms = ["CR_TIMER", "host_ctl.edm_ticks", "host_ctl.ukernel_timer_clock"]
+++

**What runs.** The kernel writes the `timer_clock` file's value into HostCtl dword 6 when it
boots the firmware. The script sets it to 400000 (the firmware's own value), 200000 and 800000
in turn, boots the firmware each time, and samples the registers as E009 did. The tick is the
rate of HostCtl dword 12, which advances once a tick (E009); `TIMER` is `0x144`.

**Results.** Each run has 200 snapshots over 40.8 to 41.0 s.

| dword 6 | tick (Hz) | tick x dword 6 | `TIMER` (per s) | `TIMER` x 16 |
|---|---|---|---|---|
| 400000 | 997.482 ± 0.010 | 398.993 MHz | 24937122 ± 229 | 398.994 MHz |
| 200000 | 1995.004 ± 0.013 | 399.001 MHz | 24937664 ± 156 | 399.003 MHz |
| 800000 | 498.758 ± 0.004 | 399.006 MHz | 24938041 ± 201 | 399.009 MHz |

Halving dword 6 doubles the tick and doubling it halves the tick, to within 0.004%. `TIMER`
does not move with dword 6. The rates are against the laptop's clock, which E009 found 30 ±
17 ppm slow and which was not checked again; corrected by that, every figure would rise by
about 0.012 MHz, the same for all three runs.

So the EDM timer counts down dword 6 cycles of one clock, and that clock and `TIMER` x 16
agree at 399.0 MHz in all three runs. This closes the first half of Q002: the tick is dword 6
clocks of a 399.0 MHz reference. It does not show that this reference is the clock the USSE
runs from.
