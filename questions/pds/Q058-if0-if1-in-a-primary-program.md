+++
id = "Q058"
question = "what do the input flags if0 and if1 read in a primary pixel program: the first and last task of a tile, or the end of a tile and of a render?"
unit = "pds"
phase = 11
evidence = ["E128", "E130"]
terms = []
+++

In the pixel-event program ir0 reads the tile position and ir1 reads 2, or 6 on the last tiles
(E130); in a fill's secondary program ir0 is the tile position (E128).

What is open (pds_isa.md §7, item 2): if0 and if1 in a primary program. Rogue's reading is last or
first in task and end of tile or end of render.

To settle it: on the laptop, a primary program that branches on if0 and on if1 and hands the outcome
to the USE task as an attribute, on one-tile and many-tile triangle renders, every pixel read back,
three runs.
