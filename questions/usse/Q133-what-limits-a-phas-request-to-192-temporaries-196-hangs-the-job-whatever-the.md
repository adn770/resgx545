+++
id = "Q133"
question = "what bounds a phas request (it runs when T mod 256 is 4 to 192 and hangs the job when it is 0 or 196 to 252, whatever the task was started with: E519) and is the limit the same for a firmware task"
unit = "usse"
kind = "hw"
value = "low"
phase = 11
evidence = ["E487", "E519", "E540"]
terms = []
+++

E487: requests of 8, 16, 32, 64, 96, 124, 128, 132, 136, 144, 160 and 192 ran (15 of 15 jobs,
started with 8; 192 also started with 32, 64 and 128) and 196, 200, 204, 208, 212, 216, 220, 224,
252, 256, 508 and 1020 hung the job (15 of 15; 196 also started with 32, 64 and 128): 12 values
each, not an interval (228 to 248 and 260 to 504 were not run); every request from 124 up wrote
r123 only, since r124 and up cannot be named, so a request above 124 exercised r123 and not the
registers past it; the field itself takes up to 1020 and counts in fours.

Narrowed in 11.27 (E519): the 12 and 12 values are not an interval. Requests 100 to 120, 148 to 156,
164 to 188 and 260 to 448 (64 requests, every multiple of four) ran, 228 to 248 and 452 to 504 (20)
hung, and of 15 requests from 512 to 1016 chosen by the rule 'T mod 256 in 4 to 192 runs, 0 and 196
to 252 hang' all 15 behaved as predicted (8 ran, 7 hung); the rule was written after the first 84
and tested on the 15. A job that ran wrote r123 only (or, from 512 up, r3, r63 or r123), and E519
does not show whether a write reaches a register under a small allocation (Q132), so what a request
above 124 allocates is not shown, and Q144 asks it.

Narrowed in 11.30 (not retired). For a firmware task the allocation is the TRC it is started with:
TRC 8, 9, 12, 16, 24 and 31 (32 to 124 temporaries) gave real storage up to the top register, r(4T
- 1), 6 of 6 (r123 for 31), and the register past the allocation did not hold a marker written to it
(0 of 5, E540), as in a client fill (E535). TRC 32 and above, and the hang predicted for 49 and up,
were not run (the arm of 32 failed with its error cut off, [infer] at the fork's hazard gate, and
arming with the hazard word was not made), so
whether a firmware task's request follows the same limit is open above 31.

What is open: the quantity that bounds a phas request ([infer] the register file divided by the
instances in flight), the request between 192 and 196 (the field counts in fours, so none is
encodable), whether the microkernel's tasks request the same, and TRC 32 and above in a firmware
task. To settle it: the limit against the number of instances (a smaller target, a render with
fewer pixels) and the firmware tasks with the hazard word (phase 12's tasks).

Noted 2026-11-09: near duplicate of Q144, not merged (both ask what bounds a phas request and what
a request above 256 allocates (E519)). A merge or a fold decides which text survives.
