+++
id = "Q002"
question = "is the 399.0 MHz reference that times the EDM tick and TIMER the clock the USSE runs from?"
unit = "edm"
phase = 3
evidence = ["E009", "E084", "E124"]
terms = ["CR_TIMER", "host_ctl.edm_ticks"]
+++

The DDK assumes a constant 400 MHz (`SYS_SGX_CLOCK_SPEED`, sgx545-ce `sysconfig.c:48`) and
sets the EDM tick to 400000 core clocks (HostCtl dword 6). Against an NTP-checked clock the
tick runs at 997.46 Hz and `TIMER` at 24.9366 MHz (E009).

With dword 6 at 200000, 400000 and 800000 the tick scales as 1/dword 6 and gives 399.00 MHz to
within 0.01 MHz each time, while `TIMER` stays at 1/16 of the same clock (E084). So the EDM tick is
dword 6 cycles of one 399.0 MHz reference, and `TIMER` counts that reference divided by 16. What is
not shown is that this reference is the core clock the USSE and the other units run from, rather
than a separate timer clock of about the same rate.

A third view needs a workload whose cycle count is known. A loop timed by the host
(`probes/usse/loop-timing.toml`, E124: a fill whose shader runs a loop of 8 instructions 12500 to
1250000 times, timed by the host) did not give one. The host-measured time grows linearly with
the iteration count taken modulo 65536 (3.03 µs an iteration, 0.95 ms rms over 100 runs), not
with the count itself, although every run ends with the counter at 0 and the full 32-bit
immediate loads correctly elsewhere. Why is open; until it is understood the loop cannot time
the core. A loop kept below 65536 iterations, with the number of instances and the USSE's
issue rate known, would give the cycle count to set against the host clock.

The only consequence for the driver so far is the length of the EDM tick (1.0025 ms instead of
1 ms) and of the DDK's `SGXWaitClocks` delays.
