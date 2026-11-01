+++
id = "Q045"
question = "what sets the fields of register 0x0740 that the TA kick turns into DPM store and load tasks, and what do those tasks move?"
unit = "dpm"
phase = 11
evidence = ["E158", "E256"]
terms = ["CR_DPM_TASK_STATE", "CR_DPM_TASK_CONTROL", "CR_DPM_STATE_CONTEXT_ID"]
+++

On a first kick, or with command flag 0x8, the TA kick clears the DPM state of its context slot,
then issues a store task (code 1) with an index taken from a 9-bit field of register 0x0740,
the field chosen by the DPM context slot, and a load task (code 4), each only if that field is
not zero (E158).

0x0740 reads 0 in every sample of every job run so far: fills, copies, single and double renders
in one context, two render contexts, partial renders in a 0x30-page buffer and the triangle at
eight sizes up to 4096x4096 (E256). So none of these jobs issued the store or the load task, and
what would set the fields is still not seen; `contexts -n 2` renders nothing, so two contexts that
each render were not among them.

To settle it: sample 0x0740 around kicks of two render contexts that each render, alternating, and
around a context switch in the middle of a TA (a two-context mode the linux fork does not have yet).
If a field is ever non-zero at a first kick, dump the DPM state and control pages before and after
that kick: the entries the store and the load change name what the index counts. Then write chosen
values into the register before a first kick (a kernel poke) and compare the dumps.
