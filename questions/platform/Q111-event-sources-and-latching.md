+++
id = "Q111"
question = "which hardware event sets which bit of CR_EVENT_STATUS and CR_EVENT_STATUS2 in an ordinary TA, 3D, DPM or transfer job, and how long does each stay set (what a write to CR_EVENT_HOST_CLEAR clears is Q166)?"
unit = "platform"
kind = "hw"
value = "high"
phase = 11
evidence = ["E006", "E154", "E155", "E357", "E431", "E435", "E444", "E547", "E548", "E747", "E764",
            "E765", "E766", "E823", "E837"]
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
order the bits of one job set (what a write to CR_EVENT_HOST_CLEAR clears is Q166). [infer] The firmware takes its work from these bits, so a simulator that runs it needs
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

Offline reading of the timelines, 2026-11-09 (the dataset's `events-timelines.txt`, which lists
the first-rise order of the bits per job; an analysis of existing data, not a new measurement). In
the 42 non-empty orders of the file the order of the bits of one job kind is not the same from job
to job: a 64 x 64 triangle at the 1.22 us sampling shows 26 18 14 31 (twice), 14 31, 26 0 18 14 31
and 26 14 31 0 18, and the partial render's jobs 26 18 13 0 12, 1 0 18 13 14 31 26, 18 14 31 0 26
and 26 1 0 18 5 13 14 31. What does repeat is that bit 14 (SW_EVENT) is followed at once by bit 31
(MASTER_INTERRUPT) in every order that holds either. The orders are the order of first sampling at
1 to 5 us, so bits that rise within one sample (above: bits 6, 9 and 20 of a triangle) have no
order here, and a bit the firmware acknowledges within a sample can be missed. The within-job
order Q111 asks for is therefore not given by the timelines; the arrival order at the EDM (Q033's
event log) is the measurement that would give it.

Narrowed 2026-11-10 (S2, E747). The arrival order at the EDM that the offline reading of 2026-11-09
asked for was measured: in 14 client jobs the events reach the EDM one status bit at a time, in an
order identical in every replicate of a kind (fill and copy: a kick entry of the kernel's buffer,
the end of render, a later kick entry; a 64x64 triangle: kick entry, TA finished (pa1 bit 9), end of
render (bit 4), the status bit that pa1 bit 22 stands for, then five kick entries; the partial
render, per render: kick entry, bits 21 and 10, bits 4 and 22, bit 9, bits 4 and 22), with the
status bits read through the reversed order of E155 (pa1 bit = 22 minus the status bit, E747). That
is the order of arrival at the EDM, not the order in which the registers rose; no status register
was read in those jobs, whether a bit is a pulse or a level is not shown, bits 26, 14 and 31 of E547
never reached the EDM, and which event sets the other bits and what CR_EVENT_HOST_CLEAR clears
(Q166) stay open.

Post hoc note, S3 (2026-11-10, dataset render-closing-s3; timeline rows read after the scoring, 1
run each). For a BIF fault the status bit that follows it, `CR_EVENT_STATUS2` bit 7 or 6, sets 121
to 124 us after the fault word is visible in `CR_BIF_INT_STAT`, in the TA's read fault, a
background program's fetch fault, a texture fetch fault and a transfer's write fault (E764, E765,
E766), so for these jobs the order of the bits is the fault word first and the bit about 122 us
later; the EDM's write fault sets none (E444). In the background-fetch job the TA's end shows first
(bit 26, then SW_EVENT with bit 31, cleared 12 us later by the kernel's handler) and the fault 31
us after that (E764, [infer]).

Narrowed 2026-11-10 (K1 stage e3b, E823; not retired). With our task skipping the slot-3
end-of-render pass once, the fill never completed, the tick stopped (E537's signature, 1 job) and
`CR_EVENT_STATUS` bit 18 stayed set from 7.3 ms to the end of the 50 ms watch (8 of 9 reads; the
first read preceded the render's end; the frozen scorer therefore says 'mixed': post hoc), cleared
by a host write of bit 18 and not by one of bit 15: with no acknowledgement the bit is a level, so
the 4 to 6 microseconds of E547 are the firmware's acknowledgement [infer, one job]. Open: the other
bits' pulse or level, the firmware route (B2 not run), the order of bits.

Note 2026-11-11 (round 4, decision R4-3): the clause on what a write to `CR_EVENT_HOST_CLEAR` clears
is Q166's alone and is cut from this question's line; Q166 is retyped from kernel to hw (low). E821
and E822 answer `CR_EVENT_HOST_CLEAR2` (the bits written are the bits cleared, 3 of 3 rounds by the
host and by a task's `str`).

Narrowed 2026-11-11 (round 4 session r4-events, stage e3p, E837; not retired, and the line is not
reworded: round 4's rule rewords it only when Q166's clears hold in 3 of 3 jobs, and one ran). With
the slot 3 end-of-render handler skipped and the watch started at the slot 3 entry, bit 18
(`PIXELBE_END_RENDER`) read set in 7 of 7 reads over 54 ms and two seconds later (H-LEVEL held out,
1 job; E823's 8 of 9 the other), and never in the control fill without the skip (9 of 9 clear):
bit 18 is a level until cleared, and its 4 to 6 us pulses in ordinary jobs are the closed
handler's acknowledgement [infer]. Open as before: the other bits' level or pulse, which event sets
each, and their order within a job.
