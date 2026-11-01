+++
id = "Q028"
question = "which of the recovery's reset steps does a later job need after a fault, now that a held fault is seen to stop the EDM's command processing?"
unit = "transfer"
phase = 9
evidence = ["E024", "E317", "E318", "E319"]
terms = ["CR_BIF_INT_STAT", "CR_BIF_FAULT", "misc_info"]
+++

On a fault the kernel stops and resets the core, boots the firmware again in place, and later jobs
run exactly (E024). Held without recovery (debugfs `hold_recovery`, E317, one run), a render that
faulted on its unmapped stream page wedges more than its own job: the EDM answers no GETMISCINFO
(the kernel's 500 ms wait ends the query, about 0.65 s from the shell), a fill on another context
does not run, and the EDM tick's count in `CR_USE0_SERV_EVENT` stays still between two reads 19 s
apart, while the bus interface keeps the fault in `CR_BIF_INT_STAT` (0x90008) and `CR_BIF_FAULT`
(the page) and the kernel counts no interrupt. Jobs hung without a fault, in a pixel task or in
the TA (E318, one run), and a fault of the EDM's own write to the control block (E319, one run)
leave GETMISCINFO unanswered too. A debugfs reset (halt, the firmware's buffers rebuilt, boot in
place) recovers each case, and the jobs a client had given up on run after it. It blames no job,
so the held job runs again and is recovered once more with blame (E318; E317's log does not tell
the order; render_uapi.md §10, §13).

Open: which of the reset's steps a later job needs (the core reset, the firmware boot, rebuilding
the firmware's buffers, restoring the contexts' rings); that the EDM's task is stalled on the
faulted bus is a reading of the still count (E317) [infer].

To settle it: kernel switches that leave out one reset step at a time, each followed by a job on
another context and GETMISCINFO.
