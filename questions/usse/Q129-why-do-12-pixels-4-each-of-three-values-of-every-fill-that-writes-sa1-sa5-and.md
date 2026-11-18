+++
id = "Q129"
question = "why do 12 pixels (4 each of three values) of every fill that writes sa1, sa5 and sa7 show those sa values as their output, and how long does an sa written by one job stay readable (one job, or until the next job that writes it)"
unit = "usse"
kind = "hw"
value = "low"
phase = 11
evidence = ["E484", "E1140"]
terms = []
+++

E484: all 18 writer jobs that wrote sa1, sa5 and sa7 (and then a colour to o0) read back 2036
pixels at the colour and 12 at 0x5A5A0001, 0x5A5A0005 and 0x5A5A0007, 4 each; the writers that
wrote no sa read back the colour in all 2048. And an sa is read by the next job (9 of 9) but after
a job that wrote no sa the reader read that job's output instead (3 of 3).

What is open: which instances show the sa value (the positions were not kept) and why (the sa
written by instances of one task sharing a bank that the output of the last instances overwrites?),
and whether an sa survives a job that writes only other registers (the gap job wrote nothing). To
settle it: the pixel positions of the odd 12 kept (probe --pixels), sa written by 1 to 16
instances, and a gap job that writes an sa other than the probed one.

Note 2026-11-17 (Q136 retired, answered by E1140). An sa0 written by every instance of a fill is
read by the next job in 2048 of 2048 pixels, and a job between that writes no sa (a fill, the
health fill or triangle) replaces it with that job's colour. That answers this body's "whether an
sa survives a job that writes only other registers" for sa0 [HW]. Kept here as notes from Q136's
rule, not new clauses:
- which instance reads which slot, and why the health triangle's 64 x 64 render reads as 1536 and
  512 pixels of a 64 x 32 fill;
- E1139 [infer]: a reader's later instances read what its earlier ones wrote to o0.

An o destination, other operands and the other registers of the banks were not run.
