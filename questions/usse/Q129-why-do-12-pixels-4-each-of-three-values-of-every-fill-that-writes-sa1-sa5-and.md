+++
id = "Q129"
question = "why do exactly 4 pixels of a fill that writes sa_n show the written value instead of the colour, and what rule places them (E1144: the same 4 per n in every run, one per 16 x 8 block of the top-left 32 x 16, not a constant step in pixel index)"
unit = "usse"
kind = "hw"
value = "low"
phase = 11
evidence = ["E484", "E1140", "E1144"]
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

Note 2026-11-18 (narrowed by E1144, r35-sa stage a). Clause (b), how long an sa lasts, is
answered [HW]: an sa5 write read after a job that wrote sa1 read that job's output (H-ONEJOB 2 of
2, E484's form reproduced), so an sa lasts one job whatever the job between writes; with E1140
for sa0. Clause (a): every sa_n writer (n = 0 to 15) showed its value at exactly 4 pixels, the same
in both replicates, and sa1, sa5 and sa7 together the union (E484's 12) [HW]; the frozen position
rules (the same 4 for every n, a step of n d in pixel index) failed. Post hoc [infer]: (x, y) =
((n & 1) + 2 (n >> 2) + {0, 16}, ((n >> 1) & 1) + {0, 8}), 29 of 29 sets, not frozen. Open: that
rule held out (sa16 and up, other sizes), and why those instances show the write (R35-3a: the
mechanism with Q098's "pa_n naming sa_n").
