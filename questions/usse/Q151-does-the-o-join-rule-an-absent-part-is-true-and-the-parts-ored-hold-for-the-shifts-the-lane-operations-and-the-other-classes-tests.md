+++
id = "Q151"
question = "does the o join rule of E529 (enc[39] = 0: the two parts of the test field ORed, an absent part true) hold for the shifts, the 8-bit and 16-bit lane operations and the other classes' tests, and with a chan other than chan0, and does any compiler output need it?"
unit = "usse"
kind = "hw"
value = "low"
phase = 11
evidence = ["E529", "E499"]
terms = ["Universal Scalable Shader Engine (USSE)"]
+++

E529: with enc[39] = 0 the rule (an absent part true, the parts ORed) fits the 90 cases of the first
run, read after the run, and predicted 270 of 270 on or, xor and and #7 over other pairs; a one-part
field is always true under the o join. E499's AND is the a join.

What is open: the shifts, the lane operations, the other classes' tests (iadd32 and the like), the o
join with chan fields other than 0, the field value 0, and result classes that the pairs did not
give (the and #7 probe has no negative result). A compiler needs the o join only for a test of two
conditions, 'x is zero or negative', which the o join writes as one instruction (taz with nat, which
the assembler writes as `.testnoz`), a case E529's field 5 reads as predicted by the rule: 1 for the
results 0, 0x80000000 and 0xffffffff. To settle it: the same 15 values over those forms, with the
rule as the hypothesis.
