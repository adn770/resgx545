+++
id = "E130"
claim = "In the pixel-event program of triangle jobs, input word ir0 reads 0 on a one-tile render and tile_y << 10 | tile_x for the 16x16 tiles of larger renders (59 of the 60 tiles that stored anything on a 128x128 render, tile_y up to 255 on a 32x4096 one), ir1 reads 2 and, on the last tiles, 6; the vertex-index reading of ir0 is not in this data"
unit = "pds"
method = "probes pds-pixel-event-pixev-inputs, -pixev-grid16, -pixev-grid and -pixev-tall of probes/pds/pixel-event.toml (pixev_dump.s passes ir0, ir1, tim and copies of them to the end-of-tile task with douta; eot_dump.s or eot_tile.s stores the task's attributes to scratch, each tile to its own 16 dwords in the tall, grid and grid16 probes) on the laptop, linux fork with the debug option on: triangle jobs of 32x16, 128x128 and 32x4096, one run of each, fresh context each; the table ran twice (the second is the follow-up run)"
tiers = ["HW"]
date = "2026-11-01"
data = ["pds-pixel-event", "pds-pixel-event-followup"]
terms = ["PIXEL_EVENT.END_OF_TILE", "PIXEL_EVENT.LAST_TILE"]
+++

**What runs.** On the end-of-tile event the probe's pixel-event program reads its inputs and passes
them to the end-of-tile task as `douta` attributes: `ir0.l`, `ir1.l`, `tim.l`, the `.h` halves,
`ir0` and `ir1` through the ALU (OR with 0), a `mov32` of `ir0.0` and `ir0.1`, and `pc.0`. The task
stores them. The grid and tall probes use a per-tile store, each tile at 16 dwords of its own,
indexed by a slot word the program builds from `ir0`. The 128x128 render has 8 x 8 tiles of 16x16 in
both of its probes: grid16 builds the slot as 8 x tile_y + tile_x, 64 slots, and grid uses the
program's default slot word, which gave the 32 slots 8 x tile_y + (tile_x & 3) (slots 0 to 3, 8 to
11, ... 56 to 59), so two tiles share each slot. The tall probe is 32x4096 with the default slot
word. A slot counts below as holding data when its `ir1` word is 2 or 6; slots that hold only colour
values (0xff203040 or 0xff00ff00, as pixels do) are not counted.

**Results.**

- One tile (32x16): `ir0.l`, `ir0.h`, `ir0` through the ALU and `mov32` of `ir0.0` and `ir0.1`
  all read 0; `ir1.l` and `ir1` read 6 (bits 1 and 2) and `ir1.h` reads 0; `pc.0` reads 0x1a;
  `tim.l` passes the whole timer (0x0102c890) and `tim.h` reads 0.
- 128x128 (grid16): 60 of the 64 slots hold data. In 59 of them `ir0.l` is `tile_y << 10 |
  tile_x` of the slot (slot 8 x tile_y + tile_x, both from 0 to 7); the slot of tile
  (5,7) holds the value of tile (7,7), 0x1c07, and slots 0, 1, 20 and 25, the tiles (0,0), (1,0),
  (4,2) and (1,3), hold nothing. `ir1` is 2 in 57 slots and 6 in the three slots whose `ir0`
  is that of (6,7) or (7,7), the last two tiles. In 11 of the 60 slots the second copy of
  `ir0`, which went through the ALU, is another tile's position (slot 5 holds 0x5 and 0x7).
  In 20 of the 60 slots the slot word stored in dword 15 is the slot's own number plus 2 (slot 2
  holds 0x00400004, slot 3 0x00400005) and in the other 40 it is the slot's own number; the 11
  slots with a differing second copy are among the 20.
- 128x128 with the default slot word (grid): 33 slots hold data, 32 of them the 32 slots of the
  layout and one at slot 768, with `ir1` 2 in 30 and 6 in 3.
- 32x4096 (tall): 211 slots hold data. Their `ir0.l` values are all of the form `tile_y << 10 |
  tile_x` with tile_x 0 or 1 and tile_y up to 255; 210 distinct positions of the 512, the largest
  261121 = 255 << 10 | 1. So `.l` passes the whole of `ir0` past bit 16, not 16 bits. `ir1.l`
  is 2 in 209 slots and 6 in 2.

**Second run.** The follow-up run repeats the one-tile values (`ir0` 0, `ir1` 6, `pc.0` 0x1a, a
different timer count) and the pattern of the larger renders, with different gaps. grid16 has 59
slots, 58 with `ir0.l` as the formula, empty slots 0, 1, 25, 37 and 51, 9 slots with a differing
second copy, `ir1` 2 in 56 and 6 in 3, and the slot word 2 above the slot's own number in 21 of
the 59 (the 9 with a differing copy among them). grid has 32 slots, 31 of the layout (slot 48 is
empty) and one at slot 64 (`ir1` 2 in 29, 6 in 3). tall has 221 slots, 218 distinct positions, the
largest again 261121, and `ir1.l` 2 in 217 and 6 in 4.
Which tiles are lost differs from run to run.

**Not shown.** The 16 x 16 tile size is read from the probe labels and the render: 128 pixels wide
with `tile_x` from 0 to 7 is 16 pixels per tile. The grid probe's label, 32 tiles, counts its slots
(two tiles share one), not tiles. `ir0` as the vertex index of a vertex program is not in this data
(no vertex-program probe was assigned here). The gaps (4 empty slots of 64 in the first run and 5 in
the follow-up, 211 and 221 slots for 512 tile positions in the tall probe) and the second copies and
slot words that differ from the expected mean these probes do not recover every tile's attributes;
why was not examined. One run of each probe in each run.
