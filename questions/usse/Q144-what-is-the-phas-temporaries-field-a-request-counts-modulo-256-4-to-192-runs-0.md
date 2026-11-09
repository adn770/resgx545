+++
id = "Q144"
question = "how many registers does a phase get from a phas request above 256 (a request runs when it is 4 to 192 modulo 256 and hangs the job when it is 0 or 196 to 252), and what bounds it"
unit = "usse"
kind = "hw"
value = "low"
phase = 11
evidence = ["E519", "E535"]
terms = []
+++

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
past an allocation goes (Q132, Q147), and whether a firmware task's request follows the same rule
(E540 has the TRC up to 31 only). To settle it: a request of 260 and of 516 with a distinct marker
written to each of r0 to r7 and r123 (the way E486 did), read back, and a smaller target.

Noted 2026-11-09: near duplicate of Q133, not merged (both ask what bounds a phas request and what
a request above 256 allocates (E519)). A merge or a fold decides which text survives.
