+++
id = "Q026"
question = "why do the per-tile stores of the grid pixel-event probes leave empty slots and mixed copies, different ones per run?"
unit = "pds"
phase = 7
evidence = ["E130", "E394"]
terms = ["PIXEL_EVENT.END_OF_TILE"]
+++

On a 128x128 render of 8 x 8 tiles the pixel-event program passes `ir0` and other words to the
end-of-tile task, which stores them in a slot of 16 dwords per tile (E130). 60 of the 64 slots
hold data. In 59 of them `ir0.l` is `tile_y << 10 | tile_x` of the slot; the slot of tile (5,7)
holds the value of tile (7,7), and the slots of tiles (0,0), (1,0), (4,2) and (1,3) are empty. In
11 of the 60 slots the second copy of `ir0`, which went through the ALU, is another tile's
position. In 20 of the 60 slots the slot word stored in dword 15, which the end-of-tile task
addresses its stores by, is the slot's own number plus 2 (slot 2 holds 0x00400004), and the 11
slots with a differing copy are among them. The grid probe, the same render with 32 slots shared
by two tiles each, fills 33 slots (32 of its layout and one at slot 768), and the 32x4096 one 211
slots for 512 tile positions.

The follow-up run has the same pattern with different gaps: 59 slots, 58 right, empty slots 0, 1,
25, 37 and 51, 9 slots with a differing second copy, 21 with the slot word 2 above their own number;
the grid probe 32 slots (31 of its layout and one at slot 64); the tall probe 221 slots. Which
tiles are lost differs from run to run. Slots 0 and 1 are empty in both runs of the grid16 probe;
slot 0 holds data in both runs of the grid probe.

Narrowed in 11.14 (E394): five more runs of the grid16 probe: slots 0 and 1 are empty in all five, 1
to 5 others differ per run (13, 20, 22, 25, 33, 46, 51, 52), and slots 64 and 768 hold only colour
words, except slot 768 in the first run (data).
The unique tag word and the fence were not run.

Open: whether the empty slots are tiles whose event never ran, ran but stored nowhere, or stored
into another tile's slot (the mixed copies suggest the last); whether the tile-to-slot mapping or
the end-of-tile task's timing is the cause; why the first slots are often empty; why the slot word
in dword 15 is two above the slot in a third of the slots, when the stores are addressed by it.

To settle it: give each tile's store a unique tag word that does not come from `ir0` (a counter
the task increments, and the timer) and a second copy that does not go through the ALU; run the
128x128 job ten times, and count per run the slots with zero, one and two writers. Repeat with the
end-of-tile task stored to a slot per tile and a fence after the store.
