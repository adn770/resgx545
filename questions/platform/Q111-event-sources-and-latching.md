+++
id = "Q111"
question = "which hardware event sets which bit of CR_EVENT_STATUS and CR_EVENT_STATUS2 in an ordinary TA, 3D, DPM or transfer job, how long does each stay set, and what does a write to CR_EVENT_HOST_CLEAR do to it?"
unit = "platform"
kind = "hw"
value = "high"
phase = 11
evidence = ["E006", "E154", "E155", "E357", "E431", "E435", "E444", "E547", "E548"]
terms = ["CR_EVENT_STATUS", "CR_EVENT_STATUS2", "CR_EVENT_HOST_CLEAR", "CR_EVENT_HOST_ENABLE"]
+++

The bit names of CR_EVENT_STATUS (TA_FINISHED 13, PIXELBE_END_RENDER 18, ISP_END_TILE 23, the DPM
out-of-memory and state bits, and so on) come from the driver headers (doc/specs/hw_spec.md section
6.4), and the firmware's handlers test and acknowledge them (E154, E155). The host enables only
SW_EVENT (E006).

Seen on the hardware: the idle bits (TIMER 29 and DCU_INVAL_COMPLETE of STATUS2), SW_EVENT 14 which
the firmware raises itself, TRIG_TA 7 and TRIG_3D 6 of STATUS2 which latch on a hang or a long loop
until a reset (E357, E431), and bit 11 gained by a held render with render flag bit 0, with 0x0748
ending at 0x1d (E435). A bus-interface fault sets no bit of its own: the STATUS2 bits 7 and 6 that
follow a TA or a background program's fetch fault are the hang latches (E357, E444), and the EDM's
write fault sets none. Q082 holds bits 6 and 7 and Q003 what a fault raises.

Open: which hardware event sets each of the other bits in a job that runs to its end (the TA's end,
the 3D's tiles and render, the DPM's page and state tasks, an out-of-memory overflow, a transfer),
whether a bit is a pulse or a level, for how long it stays when nothing acknowledges it, in which
order the bits of one job set, and what a write to CR_EVENT_HOST_CLEAR clears (the bits written, or
others). [infer] The firmware takes its work from these bits, so a simulator that runs it needs
them.

To settle it: sample CR_EVENT_STATUS and CR_EVENT_STATUS2 at the finest sampling (`--regs` with
regtimeline as in E435) through a fill, a copy, a triangle, a partial render and an overflowing
scene, and count the host interrupts per enabled bit with the enable written through debugfs kregnow
one bit per run (the method of E444); the firmware acknowledges the bits it handles, so a sample can
miss one, and the order of the bits needs a firmware build that stores each status word it reads
(the run Q033 names).

Narrowed in 11.31 (E547, 66 timeline jobs; E548, 160 jobs of the host-interrupt matrix and its
repeats), with the existing debugfs (`regs` for the registers, `kregnow` for the two host enables;
`kreg` not used): in ordinary jobs the short pulses of PIXELBE_END_RENDER, DPM_3D_MEM_FREE and
TA_FINISHED in the 64 x 64, 256-pixel and partial jobs are 4.2 to 6.1 microseconds, at most a few
samples wide (sampling intervals averaging 1.06 to 5.58 microseconds a job), [infer] the time to the
firmware's acknowledgement (longer pulses, to 136 microseconds, are in E547); the bits a 64 x 64
triangle, a fill, a copy, a 256-pixel triple, a depth store and a partial render show are tabled in
E547 (PIXELBE_END_RENDER, DPM_3D_MEM_FREE and MADD_CACHE_INVALCOMPLETE in the triangle, TA_FINISHED,
TPC_FLUSH and the DPM state and control bits in the larger jobs, OTPM_MEM_CLEARED and
DPM_TA_FREE_LOAD of STATUS2 in some), SW_EVENT always with MASTER_INTERRUPT; armed one at a time, 7
bits raised a host interrupt of their own in a triangle and 1 in a fill and the answer reproduces
(21 of 24 case-runs of the bits that raise one, 30 of 30 of those that do not); which armed bit
raised it is inferred from the enable written, not read, and a no is only that the host saw no extra
interrupt (E548). Open: the order of the bits within a job (the firmware-task work of p1130 and a
stored status word), the events whose pulses are under a sample (bits 6, 9, 20 of a triangle), the
events of a transfer other than the fill's, an out-of-memory overflow with the DPM bits in the
larger jobs, and what a write to CR_EVENT_HOST_CLEAR clears (moved to Q166: it needs a kernel
change). Status: narrowed.