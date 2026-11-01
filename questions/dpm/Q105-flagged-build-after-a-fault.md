+++
id = "Q105"
question = "what does a faulted job leave that makes the next job fault, with a GPU reset between (seen with flag bit 0 set over a zeroed table, and with a plain triangle)?"
unit = "dpm"
phase = 11
evidence = ["E446", "E453"]
terms = ["hw_pb_desc.page_table_base", "hw_pb_desc.pb_flags"]
+++

With the page-table base at zeroed scratch pages and flag bit 0 set, the render wrote 1058 scratch
dwords in every run (E446, E453), and rendered exactly in 3 of 3 runs of E446 and in 2 of 2 runs of
E453 that followed a run that had not faulted; it faulted in 5 of 5 runs of E453 that followed a
run that had (a debugfs reset between every pair of runs). With a host-filled table in the kernel's
layout the render did not fault in any of the 3 of its 12 runs that came right after a run
that faulted (K1 after H3, and flag-then-base-K-2 and -3 after base-then-flag-zero-2 and -3); the
other 9 followed a run that rendered.

The effect is probably not specific to the flagged build over zeros [infer]. The health check at
the end of the flag-order run of E453, a plain triangle with no pokes after the reset that follows
a faulted run, faulted too (4096 of 4096 pixels differ; BIF faults at 0x10000052 and 0x10000051 in
its kernel log), and the 7 lines "SGX recovery failed: -110" of the two runs (5 in the flag-order
log, 2 in the host-filled one) do not line up with the runs that were followed by a fault. The
fault address was 0x3e140081 for the H table and 0x10000051 for every zero table, also for the
flagged H run CH1 that came right after a zero-table fault.

What is open: what a faulted job leaves that a GPU reset does not clear, whether the builder
or the render reads the table through a state that survives it, and whether a failed recovery
has a part in it.

To settle it: the same runs in the order fault, ok, fault, ok, with the kernel's log and the BIF
registers read before the reset, then with the context page's table compared before and after a
faulted run, and a plain triangle after a fault that recovered and after one whose recovery
failed.
