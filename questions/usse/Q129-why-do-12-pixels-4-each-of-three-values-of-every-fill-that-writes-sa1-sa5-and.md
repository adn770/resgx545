+++
id = "Q129"
question = "why do 12 pixels (4 each of three values) of every fill that writes sa1, sa5 and sa7 show those sa values as their output, and how long does an sa written by one job stay readable (one job, or until the next job that writes it)"
unit = "usse"
kind = "hw"
value = "low"
phase = 11
evidence = ["E484"]
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
