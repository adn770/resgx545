+++
id = "Q054"
question = "what do #incp, .cut and .tasks/.taske do on the emits, and what do sideband bits 11 and 12 select, beyond the pack mode, bits 8:6, 9, 10 and 13 that the end-of-tile emit reads?"
unit = "usse"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E030", "E102", "E106", "E239", "E269", "E376"]
terms = ["SIDEBAND.PACKMODE", "SIDEBAND.BIT9", "SIDEBAND.BITS8_6", "SIDEBAND.DITHER"]
+++

Bit 42 (.twopart) is needed on emitvcbvtx and not on emitmtevtx (E102), and on the state task's
emits it changes nothing (E106). In the end-of-tile emit's sideband the pack mode selects the
stored format (E030), bit 9 (`TILERELATIVE` in the specs) clear hangs the job, on a one-tile
target too (E239), bits 8:6 select the channel of a one-channel mode, bit 10 dithers the modes
that drop colour bits, bit 11 faults the job and bit 12 stores values of no colour (E269). The
emitpix2 instruction carries sideband bits 13:0 only.

Narrowed by E376: on the triangle's vertex program, incp 1 to 3 on emitvcbvtx or emitmtevtx draws
the triangle as with 0, and .cut on emitmtevtx hangs the job (two runs).

What is open (usse_isa.md §8, item 5): what incp counts, .cut on a program that emits more than
one primitive, .tasks/.taske (emitpds); what bits 11 and 12 select (Q046); bit 9 is Q074.

To settle it: a vertex program that emits two primitives with .cut between them, and emitpds with
.tasks/.taske in the state task, the parameter buffer dumped.
