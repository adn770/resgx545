+++
id = "Q028"
question = "which of the recovery's reset steps does a later job need after a fault, now that a held fault is seen to stop the EDM's command processing?"
unit = "transfer"
phase = 9
evidence = ["E024", "E317", "E318", "E319", "E354", "E355"]
terms = ["CR_BIF_INT_STAT", "CR_BIF_FAULT", "misc_info"]
+++

On a fault the kernel stops and resets the core, boots the firmware again in place and later jobs
run exactly (E024). Held without recovery (debugfs `hold_recovery`), a faulted or hung job wedges
the EDM: GETMISCINFO is not answered, other contexts' jobs do not run and the tick's count stays
still (E317-E319). A debugfs reset written while the hold is set now recovers the held job with
blame, once, the held job failing with its detector's error and not running again (E354, linux fork
commit 31), and a cleanup that fails while held keeps the hold (E355).

Open: which of the reset's steps a later job needs (the core reset, the firmware boot, rebuilding
the firmware's buffers, restoring the contexts' rings); that the EDM's task is stalled on the
faulted bus is a reading of the still count (E317) [infer].

To settle it: kernel switches that leave out one reset step at a time, each followed by a job on
another context and GETMISCINFO.
