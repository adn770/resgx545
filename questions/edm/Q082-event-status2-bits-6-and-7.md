+++
id = "Q082"
question = "what do CR_EVENT_STATUS2 bits 6 and 7 mean, bit 6 set while a job hangs in its pixel task and bit 7 while a TA job hangs or faults?"
unit = "edm"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E317", "E318", "E319", "E357", "E431", "E764", "E765", "E766", "E769", "E770", "E784"]
terms = ["CR_EVENT_STATUS2"]
+++

Narrowed by E357 (timelines of every change from 50 ms before each job): the timing is answered,
the meaning is not. `CR_EVENT_STATUS2` bit 7 (`TRIG_TA` in the GPL header) sets 0.1 to 0.2 ms
after the TA kick's PB load in a TA that hangs and in one that faults on its stream page; bit 6
(`TRIG_3D`) about 0.1 ms after the pixel units start in a fill whose pixel program loops 128 or
more times, not 16. Neither sets through renders from 64x64 to 4096x4096, partial renders, fills
or copies. Once set, each stays through later jobs until a reset, which puts the register back to
0x400; the kernel neither enables nor clears them [DDK: linux fork, source reading]. That explains
E317-E319's readings: 0x480 after a TA fault or hang, 0x440 after the pixel hang, 0x400 when the
EDM's own write faulted before any TA ran.

What is open: the condition itself. A task running or stalled past a short time is the reading
that fits both bits [infer]; the threshold between 16 and 128 loop iterations is not placed, nor
whether a long but progressing TA sets bit 7.

To settle it: loop fills of 16 to 128 iterations in small steps after a reset, and a TA job whose
vertex program loops a known count, each with the register sampled.

Narrowed in 11.16 (E431, 75 jobs): the latch is a threshold in the loop's length: after a reset
bit 6 sets for fills of 55 and 56 iterations (3 of 3 runs), 54 (2 of 3) and 56 to 136, never for
53 or fewer (3 of 3 runs each, 16 to 53). What it measures (a time, an instruction count) and bit
7 (the TA, a vertex program that loops a known count) are not placed. Status: narrowed, not
answered.

Post hoc note, S3 (2026-11-10, dataset render-closing-s3; nothing was predicted about it, 1 run
each, sampling about every 4.3 us). Sampled from the launch, the bit follows a BIF fault word and
is not set with it: after the TA's read fault bit 7 sets 121.2 us after `CR_BIF_INT_STAT` and
`CR_BIF_FAULT` show the fault (E764), after a background program's fetch fault bit 6 sets 121.1
us after (E764), after a texture fetch fault 122.5 us after (E765) and after a transfer's write
fault 124.1 us after (E766), `CR_EVENT_STATUS2` reading 0x400 in between. The EDM's write fault
sets neither (E444). [infer] The near-equal delay for the two bits points to a time since the
fault, or to the firmware's reaction to a stalled pipeline, rather than to the fault word; that
reading is not tested (a threshold of E431 is in loop iterations, and a delay in time here is of
a different kind).

Note 2026-11-10 (offline readings of E357 and E431 before the round 2 runs; not new measurements;
see the notes of both). E357's renders, long but not looping, never set bit 6, so "time since the
pixel units started" is not supported [data for the renders, infer for the reading]. E431's job
times (single runs, steps of 8) rise from 797 us at 16 iterations to 1917 us at 136, about 9.3 us
per iteration [data]; with the threshold at 53 against 55 iterations, that is about 1.1 to 1.3 ms
of job time [infer: interpolated between the single runs].
[infer] The latch watches something per instance of the pixel program, with the loop length
as the knob; occupancy (the target's size) is the untried second knob. The 121 us of E764 to E766
between a fault and the bit is a different condition and is not tested. An estimate of resident
instances and of instructions per clock from 440 instructions in 121 us was proposed offline and is
not recorded here: it rests on a clock not read from the repository.

Narrowed 2026-11-10 (R1-events stage t, E769 and E770; not retired). The latch is not a threshold
in loop iterations and not one in all instructions an instance executes: with a 16-instruction body
of our own bit 6 was clear at 20 and set at 26 to 30 and at 56 iterations (1 run each), while a
4-instruction body stayed clear to 120 iterations (480 instructions) and an 8-instruction body with
a load and a wait to 56 (448), and E431's 8-instruction body reproduced its 53 clear and 56 set
(the control, 2 of 2 each). The frozen scorer read the hypotheses of time or instruction count per
instance and of 54 to 55 iterations as refuted by these ladders, and ended that the ladders are
'cannot tell' because its job-time control (time grows with the loop length) failed for the
8-instruction and 4-instruction ladders (single runs). Post hoc, a count of multiply-adds executed
between about 318 and 336 fits every point of the stage and of E431 (a one-parameter fit to the
same points; the 4-instruction and load ladders never reached it, so it is untested, and it is not
a mechanism). The triangle jobs meant to vary occupancy (T3) and the load latency on 8x8 (T4) are
void: our loops as a triangle's pixel program wrote o0 in a fraction of the pixels or none (E770),
so occupancy is still untried. A stock vertex program read 0x400 and a held TA fault 0x480 as
predicted; bit 7's condition (a vertex loop, T5) was not run. Open: the quantity the latch counts,
a body-4 ladder past about 165 iterations and a body of another mix to test the fit, occupancy
through fills of other sizes, bit 7, and the 121 us after a fault word of E764 to E766.

Narrowed 2026-11-10 (R2-geo stage g-t5v, E784; bit 7 only, not retired). A vertex program of our own
that loops on a backward `br` (8 instructions an iteration, the count carried into the stored depth
as the loop proof) ran on every vertex at 1, 3, 28, 53, 55, 110, 220, 440, 880 and 1760 iterations
(the controls with no loop, 1 and 3 iterations passed: a backward `br` loop works on this core).
Bit 7 was clear after every job up to 880 iterations and set after 1760 (STATUS2 0x400 before each
job, 0x480 after the last): the frozen H-ITER and H-INSTR (set from 55 as the pixel latch, clear at
53) and H-NEVER are refuted, H-TIME (a monotone dependence on the length) is consistent, the point
is somewhere in (880, 1760] and 3520 and 7040 were skipped by the sweep's stop. So the TA side's
condition is not the pixel latch's: [infer] it fits a quantity of the whole job (time, or the three
vertices' instructions together) better than one of an instance, which is untested. Open: the point
between 880 and 1760 iterations, whether it is time or instructions (a second body length), whether
it depends on the number of vertices, bit 6's quantity as before (the multiply-add count fit, the
body-4 ladder, occupancy), and the 121 us after a fault word.
