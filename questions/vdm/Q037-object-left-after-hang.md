+++
id = "Q037"
question = "why did one of E186's runs find no object after the job hung in its pixel task, when a dump taken before recovery always holds it?"
unit = "vdm"
phase = 10
evidence = ["E186", "E318"]
terms = ["VDM_STATE1.BITS15_13", "Parameter Buffer (PB)"]
+++

The main part is answered (E318, one run; the pixel-task control held twice and not held once).
Saved before the kernel recovers (debugfs `hold_recovery`), the job hung in its pixel task holds
its object in the parameter buffer and the region headers and control streams a finished TA
leaves, byte for byte those of the one-kick triangle (E288), in both held runs. Saved after the
recovery, the same job holds the same object and an all-zero TA data: the recovery zeroes the TA
data and keeps the parameter buffer's pages. The job with VDM state word 1 bits 15:13 = 0 holds
neither object nor control stream before any recovery, so its TA stopped before writing them.

What is open: E186's run in which the pixel-task control left no object is not reproduced here;
whether it came from the kernel of that run (its recovery, its page table) or from the hang
itself is not shown.

To settle it: the pixel-task control held on fresh boots, a few times, with the parameter
buffer's page table read before the job.
