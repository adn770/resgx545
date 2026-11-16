+++
id = "Q111"
question = "which hardware event sets which bit of CR_EVENT_STATUS and CR_EVENT_STATUS2 in an ordinary TA, 3D, DPM or transfer job, and how long does each stay set, and what does a host write of a bit other than 15 and 18 to CR_EVENT_HOST_CLEAR clear?"
unit = "platform"
kind = "hw"
value = "high"
phase = 11
evidence = ["E006", "E154", "E155", "E357", "E431", "E435", "E444", "E547", "E548", "E747", "E764",
            "E765", "E766", "E823", "E837", "E855", "E857", "E890", "E902", "E921",
            "E1115", "E1116"]
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
order the bits of one job set (what a write to CR_EVENT_HOST_CLEAR clears was a question of its
own, answered by E857 for bits 15 and 18). [infer] The firmware takes its work from these bits,
so a simulator that runs it needs them.

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
larger jobs, and what a write to CR_EVENT_HOST_CLEAR clears (moved to a question of its own: it
needs a kernel change; answered by E857). Status: narrowed.

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
(then a question of its own, answered by E857) stay open.

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
is the CLEAR question's alone and is cut from this question's line; that question is retyped from
kernel to hw (low). E821
and E822 answer `CR_EVENT_HOST_CLEAR2` (the bits written are the bits cleared, 3 of 3 rounds by the
host and by a task's `str`).

Narrowed 2026-11-11 (round 4 session r4-events, stage e3p, E837; not retired, and the line is not
reworded: round 4's rule rewords it only when the CLEAR question's clears hold in 3 of 3 jobs, and
one ran). With
the slot 3 end-of-render handler skipped and the watch started at the slot 3 entry, bit 18
(`PIXELBE_END_RENDER`) read set in 7 of 7 reads over 54 ms and two seconds later (H-LEVEL held out,
1 job; E823's 8 of 9 the other), and never in the control fill without the skip (9 of 9 clear):
bit 18 is a level until cleared, and its 4 to 6 us pulses in ordinary jobs are the closed
handler's acknowledgement [infer]. Open as before: the other bits' level or pulse, which event sets
each, and their order within a job.

Narrowed 2026-11-12 (round 5 session r5-events, E855 to E857; the question line is reworded, the
question is not retired; user decision R5-7 a). The line asked "... how long does each stay set
(what a write to CR_EVENT_HOST_CLEAR clears is Q166)?". The CLEAR question is answered by E857 and
retired: a host write to `CR_EVENT_HOST_CLEAR` clears the bits written and no others that are set,
bit 15 leaving bit 18 and `TIMER`, bit 18 clearing bit 18 alone, 3 of 3 with the EDM stopped
(E855) and 3 of 3 with it running (E857), held out (H-W; H-ALL and H-NONE refuted), and bit 18
(`PIXELBE_END_RENDER`) is a level from the slot 3 entry to the stop whenever the closed handler is
skipped (E855, E856: 7 of 7 jobs, every watch read). Its other bits move here, as R5-7 (a)
decided: what a write of any bit other than 15 and 18 clears, and a write against a status with
other bits set (only `TIMER` and bit 18 were ever set when a CLEAR was written). Open as before:
the other bits' level or pulse, which event sets each, their order within a job, and the clears
of the other bits.

Note 2026-11-12 (round 6 session r6-held part P, E890; 0x0694, not retired). The r6 kernel's
debugfs `peek` reads `CR_DPM_TASK_STATE` (0x0694), which the regs file skips. At E855's lockup stop
(2 of 2, the marks and clears replicated) it read 0 at the arm, at the stop, after the clears and
after the recovery, and 0 in every other read of the session (before, during and after six held
TA faults, E891 and E892): H-R6, the store of 2 that the firmware reading R-6 places before the
lockup's poll of `CR_EVENT_STATUS` bit 6, is refuted as a register read, and E855 has a correction.
Bit 6 (`DPM_STATE_CLEAR`) read clear at every stop. Whether the store is made and does not read
back, goes elsewhere, or is never reached is open; no read has shown 0x0694 other than 0.

Note 2026-11-12 (round 7 offline fold, E902; 0x0694, not retired). The six held TA jobs of r6-held
were each the first render of a new context, so their kicks carried TA flag 0x1 and the firmware's
Clear wrote `(index << 3) | 2` to `CR_DPM_TASK_STATE` before the fault [RE]; the peek read 0 before
each job, during each hold and after each reset, 18 of 18. The register does not read back what the
TA kick writes [infer], so a host read of 0x0694 cannot tell whether the lockup path's store is
reached: the peek is exhausted and no more peek rows are planned. Open: whether the store is reached
(the plan's stage L, `lock #0` twice in a pixel program, or the kernel option K1), and the rest of
this question as before.

Note 2026-11-12 (round 7 session r7-faults stage L, E921; the lockup stop's `lock #0` twice, not
retired). In a pixel program a second `lock #0` by the quad that holds mutex 0 blocks that quad: the
counter fill hung with no update stored, with two releases after it or one (H-SELF 4 of 4 rows held
out; H-REFLAG and H-RECOUNT refuted; `lock #0`, `lock #1` ran to 512). Read with R-6, the EDM's
lockup routine would then stop at its second `lock #0`, before its store to `CR_DPM_TASK_STATE` and
before the poll of bit 6 (`DPM_STATE_CLEAR`), which fits every reading of the stop (E855, E890,
E902) [infer]: the transfer from a pixel program to an EDM task is not measured, and neither is
whether mutex 0 is free on entry or anything releases it. If it holds, the stop's bit 6 reading
clear says nothing of the DPM's state-clear event, and this question's open part (which event sets
each bit, a pulse or a level, their order, the other bits' clears) is unchanged. The direct test, an
own EDM task taking `lock #0` twice (kernel option K2), was not run.

Narrowed 2026-11-16 (round 30 session r30-evst, E1115; E1116 readings only; not retired). Plain
64 x 64 triangles with CR_EVENT_STATUS sampled alone at 541 ns: outside the job it reads
0x20000000 (14 of 14), bit 26 (MADD_CACHE_INVALCOMPLETE) whenever set reads 0x24000000 and in a
one-render job rises 88 to 119 us before the first rise of bit 18 or 0 and falls before it (8 of
8: the order of bit 26 against the render end), it is not seen in every job (8 of 14) and its
episodes are 4 to 93 us; bits 6, 9 and 20 stay under 541 ns (14 of 14). Post hoc (E1116, its
frozen controls failed on a wrong frozen value): CR_CACHE_CTRL bit 28 sets about 35 us before bit
26 and stays until a reset, and with that register sampled bit 26 shows 5 to 13 us wide. Open as
before: which event sets each bit, a pulse or a level, the other bits' order and clears.
