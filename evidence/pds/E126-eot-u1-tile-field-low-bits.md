+++
id = "E126"
claim = "On a 128x128 triangle render of 64 tiles of 16x16, flipping bit 3 of the end-of-tile task's DOUTU1 or bit 12 gives one and the same whole picture, flipping bits 4 and 5 or bits 13 to 15 writes every pixel but exchanges tiles, and flipping bits 6 to 11 or 16 to 21 writes no pixel"
unit = "pds"
method = "probes pds-pixel-event-eot-u1-tile-x-flip and -tile-y-flip of probes/pds/pixel-event.toml (pixev_u1_flip.s: the pixel-event program XORs one mask into the tile_x field, bits 11:3, or the tile_y field, bits 21:12, of the end-of-tile task's DOUTU1) on the laptop, linux fork with the debug option on: 128x128 triangle job, one run of each case, fresh context each, every pixel read back; the table ran twice (the second is the follow-up run)"
tiers = ["HW"]
date = "2026-11-01"
data = ["pds-pixel-event", "pds-pixel-event-followup"]
terms = ["DOUTU1.BITS11_3", "DOUTU1.BITS21_12", "PIXEL_EVENT.END_OF_TILE"]
+++

**What runs.** The probe replaces the triangle job's pixel-event program with one that builds
the end-of-tile task's DOUTU1 as the job's own program does, from the tile position in `ir0`,
and XORs a mask into the x field (9 cases, bits 3 to 11) or the y field (10 cases, bits 12 to
21). The target is 128x128, 8 x 8 tiles of 16x16; the unflipped picture has 12100 background
pixels and 4284 triangle pixels. The default end-of-tile program writes each tile's pixels to
the place its DOUTU1 names, so where a tile's pixels land shows where each event's task went.
The table has no case with a mask of 0. The target is filled with the sentinel 0xdeadbeef before
each job, so a pixel no task wrote still reads that value.

**Results.**

| bits flipped | pixels written | picture |
|---|---|---|
| x bit 3, y bit 12 | 16384 of 16384 | one picture, identical in the two cases |
| x bit 4 | 16384 | columns exchanged in pairs 2 apart (6520 pixels differ from bit 3's) |
| x bit 5 | 16384 | columns exchanged 4 apart (7168 pixels differ) |
| y bit 13 | 16384 | rows exchanged in pairs 1 apart (2452 pixels differ) |
| y bit 14 | 16384 | rows exchanged 2 apart (6520 differ) |
| y bit 15 | 16384 | rows exchanged 4 apart (7168 differ) |
| x bits 6 to 11, y bits 16 to 21 | 0 | no pixel written, the target keeps the sentinel 0xdeadbeef |

Every written picture holds 12100 background and 4284 triangle pixels, so the tiles are whole and
only their places change. Of the blocks whose content is unique in the picture (11 of them), each
one in the bit 4 case shows the content that the bit 3 picture has two columns away, in the bit 5
case four columns away, in the bit 13 case one row away, in the bit 14 case two rows and in the
bit 15 case four. The 12 cases with bits 6 to 11 or 16 to 21 write nothing at all, not even the
background.

The unflipped job is not in this table. That the bit 3 and bit 12 pictures are the unflipped one
rests on E043 and E044, where bit 3 and bit 12 (x or y = 1) change nothing in the fill, the copy
and the 64x64 triangle.

This corrects a sentence of E046, which says that flipping bits 3 to 5 of the end-of-tile word gives
that same image, and bits 12 to 15 likewise, on the 128x128 render: with every pixel read back, only
bit 3 and bit 12 give the unflipped picture, and bits 4, 5, 13, 14 and 15 exchange tiles.

**Second run.** In the follow-up run all 19 cases give the same classes (written with 12100
background and 4284 triangle pixels, or no pixel written) and every picture identical, pixel for
pixel, to the first run's.

**Not shown.** The 64x64 triangle of E043 is not repeated here, and on this target bit 5 (and 14,
15) still write every pixel while E043 reports bits 5 to 11 writing none on the 64x64 target,
so how far each field reaches depends on the target. One run of each case in each run.
