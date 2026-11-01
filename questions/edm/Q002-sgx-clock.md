+++
id = "Q002"
question = "is the 399.0 MHz reference that times the EDM tick and TIMER the clock the USSE runs from?"
unit = "edm"
kind = "hw"
value = "low"
phase = 3
evidence = ["E009", "E084", "E124", "E377"]
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
