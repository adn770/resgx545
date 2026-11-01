+++
id = "Q082"
question = "what do CR_EVENT_STATUS2 bits 6 and 7 mean, bit 6 set while a job hangs in its pixel task and bit 7 while a TA job hangs or faults?"
unit = "edm"
phase = 11
evidence = ["E317", "E318", "E319", "E357", "E431"]
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
