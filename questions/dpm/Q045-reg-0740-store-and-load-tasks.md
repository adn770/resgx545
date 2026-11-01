+++
id = "Q045"
question = "what sets the fields of register 0x0740 that the TA kick turns into DPM store and load tasks, and does a load task read back the macrotile lists a partial render stores in the RT data's state page?"
unit = "dpm"
phase = 11
evidence = ["E158", "E256", "E310", "E312"]
terms = ["CR_DPM_TASK_STATE", "CR_DPM_TASK_CONTROL", "CR_DPM_STATE_CONTEXT_ID"]
+++

On a first kick, or with command flag 0x8, the TA kick clears the DPM state of its context slot,
then issues a store task (code 1) with an index taken from a 9-bit field of register 0x0740,
the field chosen by the DPM context slot, and a load task (code 4), each only if that field is
not zero (E158).

0x0740 reads 0 in every sample of every job run (E256), the twelve partial renders of the 11.9
timelines included (E312). What a DPM store writes is now seen in another path: a partial render,
under DPM context slot 2, leaves the RT data's state page (`CR_DPM_STATE_BASE0`) holding sixteen
macrotile page lists and the global list (E310); every job without one leaves that page, the control
page and the OTPM page zero. So the store writes per-macrotile page lists; what the 0x0740 index
counts, and whether a load reads these lists back, is not seen.

To settle it: sample 0x0740 around kicks of two render contexts that each render, alternating, and
around a context switch in the middle of a TA (a two-context mode the linux fork does not have
yet). Write chosen values into 0x0740 before a first kick (a kernel poke target the fork needs,
11.10) and compare the state page of the RT data before and after; or poke a stored list into the
state page before a kick with flag 0x8 clear.
