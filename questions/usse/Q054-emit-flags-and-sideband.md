+++
id = "Q054"
question = "what do #incp, .cut and .tasks/.taske do on the emits, and which sideband bits beyond the pack mode and bit 9 does the end-of-tile emit read?"
unit = "usse"
phase = 11
evidence = ["E030", "E102", "E106", "E239"]
terms = ["SIDEBAND.PACKMODE", "SIDEBAND.BIT9"]
+++

Bit 42 (.twopart) is needed on emitvcbvtx and not on emitmtevtx (E102), and on the state task's
emits it changes nothing (E106). In the end-of-tile emit's sideband the pack mode selects the stored
format (E030) and bit 9 (`TILERELATIVE` in the specs) clear hangs the job, on a one-tile target
too (E239).

What is open (usse_isa.md §8, item 5): #incp, .cut and .tasks/.taske on the emits, and the sideband
bits beyond the pack mode and bit 9; bit 9 is Q074. Q046 asks about bits 8:6 and Q040 about EMIT2
bits 15:8.

To settle it: on the laptop, the triangle job's vertex emits with each flag flipped alone, with
several vertex tasks per job and the parameter buffer dumped; the end-of-tile emit's other sideband
bits flipped one at a time on the fill, the copy and the triangle, every pixel read back.
