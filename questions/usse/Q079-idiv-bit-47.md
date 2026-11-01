+++
id = "Q079"
question = "what does idiv's enc[47], a bit outside every field of the form, select?"
unit = "usse"
phase = 11
evidence = ["E295"]
terms = []
+++

Flipped alone on `idiv r10, r1, r2, drc0`, enc[47] changed every destination r10 to r17 (0, 0,
0x80, 0, 0, 0xa, 0, 0x8923 where the base wrote the quotient 0 and the remainder 0x3fc01234 to
r10 and r11); 0x80 is r3 divided by r4, the others fit no plain quotient or remainder of the
inputs (E295). The other 18 unmapped bits of the form change nothing. The simulator stops on the
bit.

To settle it: on the laptop, idiv with enc[47] over a grid of inputs in r1 to r8 (small
quotients and remainders, a zero divisor in each pair), with and without .repeat flags and
other destinations, every register r10 to r25 stored, two runs.
