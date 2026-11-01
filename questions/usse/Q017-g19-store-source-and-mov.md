+++
id = "Q017"
question = "why does g19 read 0x1a as a store's source but 0 through a mov and as the pixel?"
unit = "usse"
phase = 6
evidence = ["E085", "E086"]
terms = ["REGTYPE.FPCONSTANT", "USE.NUM_HW_SPECIAL_CONSTS"]
+++

The g bank of the fill shader (E085, E086) reads small per-pixel and per-tile values. g19 is
the odd one. The probes `usse-constant-banks-gbank` store g16 to g31 (the third dword of the
second set is g18, the fourth g19) as the store's own source and again after a `mov` to r1-r16:

- as the store's source: g19 reads 0x0000001a in both runs (the second of the four sets of 16
  registers).
- through `mov r4, g19` and a store of r4: 0x00000000 (the same set, both runs).
- as the pixel (`gbank-pixels`, `mov o0, g19` over the 2048 pixels of the fill): 0 in all
  pixels, in both runs.

The other registers of the set agree between the two stores except where they depend on the
instance: g18 reads 0x10 as the store's source in both runs and 0x16 (first run) or 0x10 (follow-up
run) through the `mov`; g21 and g23 take other values in the follow-up run. So the store sees one
instance's values (an inference from these differences).

Open: which of the three readings is the register. The store reading is 0x1a and the others zero;
a value that is 0 for the 2048 pixels but 0x1a for the instance that stores would be a
property of the stored instance (for example a register nonzero only for an instance outside the
fill's 2048 pixels, or the instance that ran last), and a read path that differs by operand
position would be a property of the instruction.

To settle it: store g19 from the pixel program as source 1 and as source 2 of other
instructions (or, and), with the instance's tile x and y (g23, g24) stored next to it so each
reading is tied to a pixel, over the whole fill rather than the one instance; and change the
fill's size and position to see whether 0x1a moves.
