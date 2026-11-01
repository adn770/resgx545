+++
id = "Q105"
question = "what does the base-only fault over a zeroed table leave, which a debugfs GPU reset does not clear, that makes the next two jobs fault whatever they are (E453, E463)?"
unit = "dpm"
phase = 11
evidence = ["E446", "E453", "E463"]
terms = ["hw_pb_desc.page_table_base", "hw_pb_desc.pb_flags"]
+++

With the page-table base at zeroed scratch pages and flag bit 0 set, the render wrote 1058 scratch
dwords in every run (E446, E453), and rendered exactly in 3 of 3 runs of E446 and in 2 of 2 runs of
E453 that followed a run that had not faulted; it faulted in 5 of 5 runs of E453 that followed a
run that had (a debugfs reset between every pair of runs). With a host-filled table in the kernel's
layout the render did not fault in any of the 3 of its 12 runs that came right after a run that
faulted (K1 after H3, and flag-then-base-K-2 and -3 after base-then-flag-zero-2 and -3); the other
9 followed a run that rendered. Those 3 exact K renders followed faults of other kinds than a
base-only fault: an H-table fault (K1 after H3) and faults of the runs named base-then-flag, which
poked the flag as well as the base (K-2 and K-3); E463's base-only fault is followed by K faulting
(4 of 4), so the two do not contradict each other, but E453's 3 of 3 show no follow-on fault of K
after those other kinds [HW], and why a flagged zero-table run faulted after a flagged one (5 of 5)
while K did not is not shown.

The health check at the end of the flag-order run of E453, a plain triangle with no pokes after the
reset that follows a faulted run, faulted too (4096 of 4096 pixels differ; BIF faults at 0x10000052
and 0x10000051 in its kernel log), and the 7 lines "SGX recovery failed: -110" of the two runs (5 in
the flag-order log, 2 in the host-filled one) do not line up with the runs that were followed by a
fault. The fault address was 0x3e140081 for the H table and 0x10000051 for every zero table, also
for the flagged H run CH1 that came right after a zero-table fault.

Narrowed by E463 (two scripts, 148 steps, two runs of every sequence): the effect is that of the
base-only fault, not of faults in general. The plain triangle that faulted after the last faulted
run in E453, a base-only run over zeros (flag clear), is probably the same effect [infer]; E463's
plain triangles after a base-only fault faulted in 8 of 8 [HW]. After the base alone over zeros
(kernel poke pb:4, the flag clear) faults, exactly the next two jobs fault, whatever they are: the
flagged build over zeros (20 of 20), the plain triangle (8 of 8) and the base over the kernel's
table (4 of 4); the third completes (8 of 8). It is the same with a debugfs GPU reset before each
job and with none (16 sequences). A fault from an unmapped scene stream leaves nothing (16 of 16
followed by an exact job), and the flagged build over zeros is exact whenever no base-only fault
came before (40 of 40). The kernel log has 48 BIF faults for the 16 sequences (all BIF fault status
`0x90004`, 44 at 0x10000051) and 31 "SGX recovery failed: -110"; in the sequences with a reset the
base-only job's recovery failed, the next job's recovered and the second job's failed again (8 of
8).

What is open: what the base-only fault leaves for two jobs that the debugfs reset does not clear (a
state of the driver, the page directory's list, the bus interface), why the first job after it
recovers and the second does not, and whether a base-only job whose recovery succeeds leaves it.

To settle it: the base-only job followed by two jobs with the BIF registers (0x0c00 to 0x0cff) and
the driver's page directory list read between the jobs, then the sequence with a recovery that
succeeds (a job that faults at another address), and the context page's table compared before and
after the fault.
