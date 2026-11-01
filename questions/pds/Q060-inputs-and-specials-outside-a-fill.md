+++
id = "Q060"
question = "what do mr01, mr23 and ir1 hold outside a fill, and do the .h specials read 0 in every task and the per-tile inputs follow the tile in a multi-tile render?"
unit = "pds"
phase = 11
evidence = ["E128", "E130"]
terms = []
+++

In a fill's secondary program ir1 reads 0 in any case, bit 9 of a special source makes a mov16 read
0, and ir0 is the tile position (E128). In the pixel-event program ir1.l reads what the ALU's ir1
does, and .h reads 0 for ir0, ir1 and tim; ir0 reads the tile position in 16x16 tiles (E130).

What is open (pds_isa.md §7, items 4 and 9): mr01, mr23 and ir1 outside a fill, whether .h reads 0
in every kind of task, and the per-tile inputs of a multi-tile render in tasks other than the
pixel-event program.

To settle it: on the laptop, each special read with .l and .h and stored through the USE task from
the primary, secondary and pixel-event programs of a 128x128 triangle render and from the
vertex-side programs, three runs.
