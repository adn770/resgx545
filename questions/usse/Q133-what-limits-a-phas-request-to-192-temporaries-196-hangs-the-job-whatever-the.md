+++
id = "Q133"
question = "what bounds a phas request (it runs when T mod 256 is 4 to 192 and hangs the job when it is 0 or 196 to 252, whatever the task was started with: E519), how many registers does a phase get from a request above 256, and is the limit the same for a firmware task"
unit = "usse"
kind = "hw"
value = "low"
phase = 11
evidence = ["E487", "E519", "E540", "E535", "E594"]
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
above 124 allocates is not shown, and the merged question below asks it.

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

**Correction 2026-11-10:** Q144 is merged into this question (retired as folded into Q133; a fold is not an answer), and its question is now a clause of the one above. Its question was: how many registers does a phase get from a phas request above 256 (a request runs when it is 4 to 192 modulo 256 and hangs the job when it is 0 or 196 to 252), and what bounds it.

E519: the requests run are 8 to 192 and 260 to 448; those that hung are 196 to 256 and 452 to 512
and every one of 708, 764, 768, 964, 1000, 1016 and 1020 (E487): the rule "T mod 256 in 4 to 192"
predicted 15 of 15 requests from 512 up.

Narrowed in 11.30 (not retired). With a marker of its own in every job (E535), a write to r123
landed under the requests 260, 264, 300, 316 and 376 (10 of 10 jobs) and under 448, 124, 128 and
192, and was not seen under 4 to 100 (0 of 12 jobs; all pixels of run a's six, the pixels listed in
run b's report): the read-back of r123 at 260 to 376 in E519 was a write that landed and not a stale
read, and [infer] a request of 260 to 376 allocates at least 124 registers, not the 4 to 120 that
its value modulo 256 would give. The modulo rule still fits which requests run and hang (E519). What
is open: T = 101 to 123 (no case ran), what a request above 255 allocates (at least 124 at the five
values run; no other value above 255 was run with a marker of its own), the quantity that bounds the
request at 192 ([infer] the register file divided by the instances in flight: Q133), where a write
past an allocation goes (Q132), and whether a firmware task's request follows the same rule
(E540 has the TRC up to 31 only). To settle it: a request of 260 and of 516 with a distinct marker
written to each of r0 to r7 and r123 (the way E486 did), read back, and a smaller target.

Round 12 cites: E594 (E487's jobs T = 132 to 192 read their own marker back, 8 of 8).
