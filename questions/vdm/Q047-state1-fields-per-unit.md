+++
id = "Q047"
question = "what do VDM_STATE1 bit 8, bits 11:9 and bits 15:13 select for a state task, when on the one-triangle job bit 8 changes nothing, bits 11:9 at 0 stop the triangle before tiling and bits 15:13 at 0, 5 or 6 hang it?"
unit = "vdm"
phase = 11
evidence = ["E060", "E185", "E186", "E187"]
terms = ["VDM_STATE1.BIT8", "VDM_STATE1.BITS11_9", "VDM_STATE1.BITS15_13"]
+++

The triangle's VDM stream has one state task, and its second word holds the three fields. Bits 11:9
(2 in the job) at 0 make the TA write no object and leave every region header empty, byte for byte
the render memory of a culled triangle; at 1, 6 and 7 the render memory is the drawn triangle's
(E185, E060). Bits 15:13 (1 in the job) at 0, 5 or 6 hang the job (E060), and the memory a hung job
leaves does not show how far it got (E186). Bit 8 set leaves the TA's output byte for byte as it is
(E187).

Q015 asks why bits 11:9 = 7 hang one job and not another, and Q037 what a hung job's memory shows.
Neither asks what the fields select. The glossary reads bit 8 as marking a state block that loads
constants or does nothing, a hypothesis; for bits 11:9 and 15:13 it holds only the measurements.
This question's own hypotheses are that bits 11:9 give the size or kind of the work the state task
does for the MTE, and that bits 15:13 name the units its results go to. One state task in a
one-triangle job cannot separate these, since every unit downstream sees the same block.

To settle it: build a stream of two state blocks, one whose PDS program writes the MTE state and one
whose program loads constants for the pixel side, and vary each field on one block at a time with
the other block as the job builds it, two runs each. Read the TA's output (the parameter buffer and
the TA data), the effect of the MTE state (a cull or viewport change) and the pixels separately: a
field that names units moves only the unit it names, a size of the MTE work shows in the MTE state
the TA applies.
