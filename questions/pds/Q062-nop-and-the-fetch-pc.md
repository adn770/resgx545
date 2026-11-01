+++
id = "Q062"
question = "does a PDS nop do anything beyond taking an instruction slot, and why does pc.0 read the instruction index plus 1 or 2, not 3, at some places?"
unit = "pds"
phase = 11
evidence = ["E128", "E142", "E143"]
terms = []
+++

rfence and rwfence leave the data-segment registers as they are in a program with no load or store
(E142); a load's dwords arrive at the next fence (E143). pc.0 reads 3 ahead of the instruction at
most places (E128).

What is open (pds_isa.md §7, items 8 and 13): nop is stated only by name, and where pc.0 reads 1 or
2 ahead a model of the PDS fetch would say why.

To settle it: on the laptop, pc.0 read after 0 to 8 nops, after each kind of instruction and across
a branch, and a load followed by nops instead of a fence, every value stored through the USE task.
