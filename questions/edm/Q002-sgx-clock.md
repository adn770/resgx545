+++
id = "Q002"
question = "is the 399.0 MHz reference that times the EDM tick and TIMER the clock the USSE runs from?"
unit = "edm"
kind = "hw"
value = "low"
phase = 3
evidence = ["E009", "E084", "E124", "E377", "E1131", "E1133"]
terms = ["CR_TIMER", "host_ctl.edm_ticks"]
+++

The DDK assumes a constant 400 MHz (`SYS_SGX_CLOCK_SPEED`, sgx545-ce `sysconfig.c:48`) and
sets the EDM tick to 400000 core clocks (HostCtl dword 6). Against an NTP-checked clock the
tick runs at 997.46 Hz and `TIMER` at 24.9366 MHz (E009).

With dword 6 at 200000, 400000 and 800000 the tick scales as 1/dword 6 and gives 399.00 MHz to
within 0.01 MHz each time, while `TIMER` stays at 1/16 of the same clock (E084). So the EDM tick is
dword 6 cycles of one 399.0 MHz reference, and `TIMER` counts that reference divided by 16.

Narrowed by E377: below 65536 iterations a fill's loop is linear in its count (E124's loop ran
its count modulo 65536), and loops of 8 and 16 instructions give 0.3203 µs per instruction over
the fill's 2048 instances: 127.8 cycles of the 399.0 MHz reference, 16.03 instances a cycle. That
is a whole number within 0.2 percent, as the reference being the USSE's clock with 16 instances
issued a cycle would give; it cannot tell 399 MHz from 400, nor exclude k x 399 MHz with 16/k
instances a cycle, since the issue rate is not measured.

What is open: the USSE's issue rate, which would turn the rate into a clock.

To settle it: the same loop on a fill of a quarter and of four times the instances, and with
dual-issue pairs in place of the nops; a counter the USSE itself reads (a timer register through
`ldr`) before and after a loop of known length.

The only consequence for the driver so far is the length of the EDM tick (1.0025 ms instead of
1 ms) and of the DDK's `SGXWaitClocks` delays.

Note 2026-11-11 (round 4, an offline reading of 702 consecutive plain-tick gaps of the kept rings
of round 3; [data] for the count, [infer] for the clock). The gaps average 25000.2 `CR_TIMER` units
(431 of the first 513 exactly 25000, the rest within 4): 400000 timer clocks a tick at 16.000 clocks
a unit, so one clock times both `CR_TIMER` and the event timer (`CR_EVENT_TIMER` bits 23:0 count
down 400000 and reload by themselves, E751). The USSE clause stays open: the issue rate, not the
timer, turns the rate into the USSE's clock.

Note 2026-11-16 (r33-tim, E1131, post-hoc readings, no verdict: its controls failed on the sample
interval). `CR_EVENT_TIMER` sampled by the host through /dev/mem over 40 to 60 ms in 15 jobs counts
down 398.96 to 399.01 a us with a period of 1002.497 to 1002.535 us against the laptop's monotonic
clock, which agrees with the 399.0 MHz above. The USSE clause stays open.

Narrowed 2026-11-16 (r33-tim2, E1133, frozen and held out): `CR_EVENT_TIMER` counts down 398.9 to
399.1 a us with a period of 1002.40 to 1002.65 us in 15 of 15 jobs (H-TIM-399 30 of 30 clauses,
H-TIM-400 refuted), so the clock that times the event timer is 399.0 MHz against the laptop's
monotonic clock, not the DDK's 400 MHz. The USSE clause stays open: the issue rate, not the timer,
turns the rate into the USSE's clock.
