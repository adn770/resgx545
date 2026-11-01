+++
id = "Q277"
question = "what sets the fields of register 0x0740 that the TA kick turns into DPM store and load tasks (a host write reads back 0: E456; 0 in every snapshot taken)"
unit = "dpm"
kind = "fw"
phase = 11
evidence = ["E158", "E256", "E312", "E456", "E574"]
terms = ["CR_DPM_TASK_STATE", "CR_DPM_TASK_CONTROL"]
+++
Split in 11.39 from Q045 (merge 6, part (a)); Q045 keeps the state page. On a first kick, or with
command flag 0x8, the TA kick clears the DPM state of its context slot, then issues a store task
(code 1) with an index taken from a 9-bit field of register 0x0740, the field chosen by the DPM
context slot, and a load task (code 4), each only if that field is not zero (E158).

0x0740 reads 0 in every sample of every job run (E256), the twelve partial renders of the 11.9
timelines included (E312), in 36 more jobs (E574) and in 607 register snapshots of 171 jobs and 225
reads after the jobs of the 11.38 batch. A host write does not stay: the register read 0 right after
each of 156 writes (E456). What sets the fields is the firmware's route (the DPM unit, a register
the
host writes elsewhere, a value from the firmware's own state), so the question is about the closed
firmware's behaviour and is parked. There is no instruction to stop sampling the register: the zero
readings stay the evidence, and a nonzero value anywhere would reopen it as a hardware question.
