+++
id = "Q144"
question = "how many registers does a phase get from a phas request above 256 (a request runs when it is 4 to 192 modulo 256 and hangs the job when it is 0 or 196 to 252), and what bounds it"
unit = "usse"
kind = "hw"
value = "low"
phase = 11
evidence = ["E519"]
terms = []
+++

E519: the requests run are 8 to 192 and 260 to 448; those that hung are 196 to 256 and 452 to 512
and every one of 708, 764, 768, 964, 1000, 1016 and 1020 (E487): the rule "T mod 256 in 4 to 192"
predicted 15 of 15 requests from 512 up.

What is open: the allocation of a request above 256 (every E519 job wrote the marker 0x7E57007B to
r123, which earlier jobs wrote too, and temporaries persist from job to job (E484), so the read-back
of r123 in 2048 of 2048 pixels at 260 to 376 does not show that the write landed under a small
allocation; where a write past an allocation goes is Q132), the quantity that bounds the request at
192 ([infer] the register file divided by the instances in flight: Q133), whether a firmware task's
request follows the same rule. To settle it: a request of 260 and of 516 with a distinct marker
written to each of r0 to r7 and r123 (the way E486 did), read back, and a smaller target.
