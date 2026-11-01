+++
id = "Q045"
question = "what do the DPM store and load tasks that the TA kick issues from the fields of register 0x0740 move, and what sets those fields?"
unit = "dpm"
phase = 11
evidence = ["E158"]
terms = ["CR_DPM_TASK_STATE", "CR_DPM_TASK_CONTROL", "CR_DPM_STATE_CONTEXT_ID"]
+++

On a first kick, or with command flag 0x8, the TA kick clears the DPM state of its context slot: it
writes the slot's state and control bases, then a clear task (code 2) for each render target to both
DPM task registers. It then issues a store task (code 1) with an index taken from a 9-bit field of
register 0x0740, the field chosen by the DPM context slot, and a load task (code 4), each only if
that field is not zero, before it sets up the OTPM (E158). The firmware's reading of the register is
all the record shows: what sets the fields, whose index they hold, and why a store comes before a
load are not shown.

Reading the two fields as a DPM task's position in the page tables is a hypothesis from the code
alone; no run has read the register.

To settle it: read 0x0740 with the debug option's register snapshot before and after TA kicks of one
and of two render contexts, after a scene of several kicks and after partial renders, two runs each.
If a field is ever non-zero at a first kick, dump the DPM state and control pages before and after
that kick: the entries the store and the load change name what the index counts. Then write chosen
values into the register before a first kick (a kernel poke) and compare the dumps the same way.
