+++
id = "Q018"
question = "where does the 0xff00ff00 colour left in the opaque pass and the punch-through phase scene come from, and why does its pixel count vary from run to run?"
unit = "usse"
phase = 6
evidence = ["E077", "E082", "E373"]
terms = ["ISP0.PASS_TYPE"]
+++

Answered (E373): 0xff00ff00 is the colour of the campaign's baseline triangle, left in the output
registers. An output register a job does not write reads what the job before left there for the
same instance: a fill that never writes o0 reads the triangle's 0xff00ff00 on 616 pixels and its
background 0xff203040 on the rest, the same positions in ten runs, the triangle's image in pieces
laid out by tile; after a fill that writes 0x11223344, the next fill's unwritten o0 and o1 read
0x11223344 everywhere. The counts vary with what ran before. E082's colour phase counts are taken
to be of the same kind where the pass did not write o0.

What is left: why o1 reads what o0 held, and the slot mapping for other job sizes.
