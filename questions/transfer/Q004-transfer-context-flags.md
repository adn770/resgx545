+++
id = "Q004"
question = "what do a transfer context's flag bits 1 and 4 and a priority other than 0 do on the hardware?"
unit = "transfer"
phase = 4
evidence = ["E015"]
terms = ["hw_transfer_context.fw_com_ctx_flags", "hw_transfer_context.priority"]
+++

The dataflow (E015) shows the pick routine skipping a context whose flag bit 4 is set and,
for flag bit 1, clearing the bit and taking the dummy path; the handler indexes the queue's
head and tail by the context's priority (secondary attributes 13 + priority, 14 + priority).
Every run on the laptop uses flags 0 and priority 0 (E018-E021).

Open: whether bit 4 is a suspend the host sets (and CONTEXTSUSPEND clears), whether bit 1
is set by anyone but the host, and which priorities have queue slots of their own rather
than reaching attributes another queue uses. A run: a dummy on a context with bit 4 set
(expected to stay queued until cleared and PROCESS_QUEUES), one with bit 1 set (expected to
complete with the bit cleared), and, only after reading which attributes 13 + p and 14 + p
alias, a context of priority 1.
