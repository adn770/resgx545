+++
id = "Q079"
question = "what does idiv's enc[47], a bit outside every field of the form, select?"
unit = "usse"
phase = 11
evidence = ["E295", "E367"]
terms = []
+++

Answered (E367): enc[47] is the high bit of idiv's repeat count, enc[47:44] + 1 (1 to 16).
Iteration k divides src1 + k by src2 + k, writes the quotient to dst + k and the remainder to
dst + k + 1, which the next quotient overwrites; E295's eight changed destinations are nine
iterations over its inputs. 21 cases match this exactly; in nine more an iteration reads a
register an earlier one writes, and every such read saw what an iteration ten or more before
wrote and the old value otherwise. The ISA table gives idiv the four-bit count, the decoder prints
`.repeat9` to `.repeat16` and the simulator runs it, stopping where an iteration reads an earlier
one's destination.

What is left: whether the ten-iteration distance holds for other task sizes and a `pa`
destination.
