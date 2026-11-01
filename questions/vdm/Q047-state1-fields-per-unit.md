+++
id = "Q047"
question = "what do VDM_STATE1 bit 8, bits 11:9 and bits 15:13 select for a state task, when on the one-triangle job bit 8 changes nothing, bits 11:9 at 0 stop the triangle before tiling and bits 15:13 at 0, 5 or 6 hang it?"
unit = "vdm"
kind = "hw"
value = "high"
phase = 11
evidence = ["E060", "E185", "E186", "E187", "E299", "E414", "E427", "E440", "E545"]
terms = ["VDM_STATE1.BIT8", "VDM_STATE1.BITS11_9", "VDM_STATE1.BITS15_13"]
+++

The triangle's VDM stream has one state task, and its second word holds the three fields. Bits 11:9
(2 in the job) at 0 make the TA write no object and leave every region header empty, byte for byte
the render memory of a culled triangle; at 1, 6 and 7 the render memory is the drawn triangle's
(E185, E060). Bits 15:13 (1 in the job) at 0, 5 or 6 hang the job (E060), and the memory a hung job
leaves does not show how far it got (E186). Bit 8 set leaves the TA's output byte for byte as it is
(E187).

Bits 11:9 = 7 hang every second job and complete the others, tiling as 2 when they complete (E299,
E413; Q163 asks what state a completed job leaves), and Q037 asks what a hung job's memory shows.
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

Narrowed in 11.15 (E414, one run each, no two-block stream): on the five-copy job the state word's
fields do what they do on the one-triangle job: bit 8 flipped changes nothing, bits 11:9 at 3, 4, 5
and 7 and bits 15:13 at 2, 3, 4 and 7 give the control's object and image, bits 11:9 at 0 give no
object, at 1 and 6 and bits 15:13 at 0, 5 and 6 hang the job. More geometry does not separate the
units the fields name. The two-block stream of the settle plan needs a VDM stream with a second
state block, which the tool cannot build (its stream is a fixed 11 words, vdm:N pokes only); not
run. Status: narrowed, not answered; the missing piece is a tool option for a second state block.

Narrowed in 11.16 (E427, 62 jobs): the tool builds a stream of two objects with a state block each
(probe --tri --obj2, with --vdm words 0 to 18 set after the second object). Flipping the fields of
the second block's state word gives the same completions and hangs as the first block's for bits
15:13 (0, 5, 6, 7 hang, 2, 3, 4 complete, 28 of 28 jobs) and bits 11:9 at 3 and 4, and bits 11:9
at 0 in the second block removes the second object alone (2 of 2); bit 8 changes nothing in
either. The fields act per state task; with both blocks the same MTE state the units they name are
not separated, and a block that loads pixel-side constants is not built. Status: narrowed.

Narrowed again in 11.16 (E440, 51 jobs, three runs each): the tool builds a second block whose
primary pixel program writes a constant to a secondary attribute (probe --tri --obj2-pixpds) for a
shader that writes it as the colour. The constant reaches only 24 to 270 of the controls' 978
non-background pixels, the rest reading leftovers (2, 6, 0xbf3f0000), and no field flip (bit 8,
bits 11:9 at 1, 3 and 4, bits 15:13 at 2, 3 and 4, in either block) moves it beyond that spread;
bits 11:9 at 0 still removes the second block's object (3 of 3) and bits 11:9 at 1 hang in the
second block (3 of 3), bits 11:9 at 4 in one of three runs of each block. So the fields still do
not separate units. Status: narrowed, not answered; missing: a constant load that reaches every
pixel (E381 found a douta in a primary program reaching sa in one job of thirteen; Q020 asks of
it).

Narrowed in 11.31 (E545, 133 jobs, the two-block stream built in 11.16 with all three marks,
viewport x, ISP word 1 in the object and the block's own pixel shader): each field flipped in either
block's state word (bit 8, bits 11:9, bits 15:13, bit 17, bit 25, the closed driver's two word
forms, and in the grids bits 7:0) moves all the block's marks together or none (86 completed jobs:
77 all marks, 8 the object absent, 1 other); bit 8, bit 25 and bits 15:13 = 2, 3, 4 change nothing,
bits 11:9 = 0 remove the block's object, bits 15:13 = 0, 5, 6, 7, bit 17 and the closed driver's
state-word forms hang. The marks are one object's own state, so what the data show is that they move
together under every field flipped; bits 0 to 7 outside the grid, 12, 16, 18 to 24 and 26 to 31 were
never flipped. The hangs of bits 11:9 = 1, 6 (7 of the 14 jobs at 6 hung) and 7 (and singly 4 and 5)
are not a function of the word: the word 0x0a022205 hung twice and completed once; two readings of
the dependence on the attribute rows (bits 7:0) were wrong (4 of 10 and 5 of 10). That hang question
is Q163. Open: a block that loads pixel-side constants reaching every pixel (Q020), and what each
field selects. Status: narrowed, not answered.
