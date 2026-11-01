+++
id = "Q136"
question = "how long does a value written to sa0 last across jobs, why is pa0 not written by ima32 or mov, and is the 0xff00ff00 and 0xff203040 mixture that pa0 reads in the first jobs of a table the colour left by the job before it?"
unit = "usse"
kind = "hw"
value = "low"
phase = 11
evidence = ["E496", "E484"]
terms = ["Universal Scalable Shader Engine (USSE)"]
+++

E496: `ima32.u sa0, ...` and `mov r10, sa0` read the result back in the same job; a pa0 destination
of `ima32.u` (2 jobs) or `mov` (1 job) left pa0 as it was (3 of 3); the job after the sa0 writer
read the sa0 value (job 8 of usse-pa-dest, 2048 of 2048 pixels), which is also the colour the writer
(job 7) output, and the job after that read it in pa0 (job 9, the same count), which is also the
colour job 8 output: E484 and Q098 have an unwritten pa or sa read the colour the job before output,
and every job of the table outputs what it read, so neither job 8 nor job 9 separates the
persistence of the sa0 value from the colour rule. The same reading explains the pa0 left-over of
0xff00ff00 (1536 pixels) and 0xff203040 (512) of the first seven jobs (each job outputs the mixture
it read) and the 0x02dadf6f that the pa0 destination jobs of the dest probe read (the colour the r0
job before them output); the mixture's first value came from the job before the table, not checked.

What is open: how long an sa0 write by `ima32` lasts, and whether it persists at all (job 8 is
confounded with the colour rule), whether another fill or the kernel's jobs clear it, the colours of
the job before the first job of a table (the runner's baseline job), why the `ima32` and `mov`
destination of pa0 is lost while sa0, o0, i1 and i2 take it, whether a pa1 to pa4 or an o
destination, and a value other than the left-over colour held in pa, sa, o or g as an operand,
behave the same way. To settle it: the pa-dest order with a writer whose colour differs from its sa0
value and a job that outputs a known colour before each reader, with waiting times and with a
triangle job between, and one job per register of the banks.
