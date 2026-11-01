+++
id = "Q004"
question = "can a transfer context whose flag bit 4 is set be released, which agent but the host sets flag bits 1 and 4, and which priorities above 0 have queue slots of their own (a priority 1 or 2 hangs a job and 3 faults it: E455)?"
unit = "transfer"
kind = "fw"
phase = 4
evidence = ["E015", "E455"]
terms = ["hw_transfer_context.fw_com_ctx_flags", "hw_transfer_context.priority"]
+++

The dataflow (E015) shows the pick routine skipping a context whose flag bit 4 is set and, for flag
bit 1, clearing the bit and taking the dummy path; the handler indexes the queue's head and tail by
the context's priority (secondary attributes 13 + priority, 14 + priority). Every run on the laptop
before E455 used flags 0 and priority 0 (E018-E021).

Answered by E455 (kernel poke `th:W=V` on a new context's HW context, two runs of each case): with
flag bit 1 set a fill completes and writes nothing, a dummy completes (2 of 2 each); with bit 4 set
(0x10, 0x12) a dummy and a fill never complete (6 of 6 jobs; the fills were given up after 1.02 to
1.04 s); a priority of 1 or 2 hangs a dummy (4 of 4) and a priority of 1 a fill (2 of 2), and a
priority of 3 faults a dummy through the EDM's own directory (2 of 2).

Open: whether the hang of a bit-4 context is a job left queued (the pick routine's skip) or lost,
and so whether clearing the bit and sending PROCESS_QUEUES releases it (the two-job chain whose
second poke cleared word 0 completed, 2 of 2, but that poke is applied at the second submission,
perhaps before the firmware picked the first job); whether anything but the host sets bit 1 or bit
4 (a CONTEXTSUSPEND command is the candidate); and the queue slots behind priorities 1 to 3 (which
attributes 13 + p and 14 + p alias), a hang for 1 and 2 and a fault for 3 not telling them apart.

To settle it: read the context's flags back after each job (a readable view of the transfer HW
context), clear word 0 only after the firmware has picked the first job (a delay between the
submissions with the hang watchdog stretched), send a CONTEXTSUSPEND from the host between the two,
and read which attributes 13 + p and 14 + p alias in the firmware's queue code before more
priorities.
