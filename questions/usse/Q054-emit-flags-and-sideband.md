+++
id = "Q054"
question = "what do #incp, .cut and .tasks/.taske do on the emits, and what do sideband bits 11 and 12 select, beyond the pack mode, bits 8:6, 9, 10 and 13 that the end-of-tile emit reads?"
unit = "usse"
phase = 11
evidence = ["E030", "E102", "E106", "E239", "E269"]
terms = ["SIDEBAND.PACKMODE", "SIDEBAND.BIT9", "SIDEBAND.BITS8_6", "SIDEBAND.DITHER"]
+++

Bit 42 (.twopart) is needed on emitvcbvtx and not on emitmtevtx (E102), and on the state task's
emits it changes nothing (E106). In the end-of-tile emit's sideband the pack mode selects the
stored format (E030), bit 9 (`TILERELATIVE` in the specs) clear hangs the job, on a one-tile
target too (E239), bits 8:6 select the channel of a one-channel mode, bit 10 dithers the modes
that drop colour bits, bit 11 faults the job and bit 12 stores values of no colour (E269). The
emitpix2 instruction carries sideband bits 13:0 only.

What is open (usse_isa.md §8, item 5): #incp, .cut and .tasks/.taske on the emits; what bits 11
and 12 select (Q046); bit 9 is Q074.

To settle it: on the laptop, the triangle job's vertex emits with each flag flipped alone, with
several vertex tasks per job and the parameter buffer dumped; the end-of-tile emit's flags
flipped one at a time on the triangle, every pixel read back.
