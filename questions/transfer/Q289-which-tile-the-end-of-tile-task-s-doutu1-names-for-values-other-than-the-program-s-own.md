+++
id = "Q289"
question = "which tile does the end-of-tile task's DOUTU1 x field (bits 11:3) and y field (bits 21:12) name when they differ from the pixel-event program's own, on a fill, a copy and a larger target, and do the two fields combine as a tile (x, y)"
unit = "transfer"
kind = "hw"
value = "medium"
phase = 12
evidence = ["E043", "E044", "E126", "E620"]
terms = ["PIXEL_EVENT.END_OF_TILE", "DOUTU1.BITS11_3", "DOUTU1.BITS21_12"]
+++

Split off Q074 on 2026-11-09: the transfer model (E620) refuses a U1 that differs from the
program's own, because the tile written is the loop's and not decoded from U1, and the 1534
scenes of the x and y sweeps (511 and 1023 values on the fill) were filed under Q074, a question
about a double emit. The records already say, per value, what the fill does: x or y = 1 changes
nothing, 2 or 3 leaves half of the 2048 pixels unwritten, and every x or y from 4 up leaves the
whole target unwritten (E044); on a 128x128 triangle render bits 4 and 5 or 13 to 15 exchange
tiles and bits 6 to 11 or 16 to 21 write no pixel (E126); and the right column's task has x = 2
in the copy as in the fill (E620, read with E043 and E044). x counts in steps of 16 pixels (2
for a 32-pixel tile) and, ir0's high field being tile_y << 10, y has a field of 2 for each 16
rows [infer, E620].

Open: whether one rule, "the loop's tile is stored at the tile U1 names and nothing is stored
when that lies outside the target", gives every recorded value on the copy and the larger target
as it does on the fill (no such rule has been fitted: a first test would fit it on the fill's x
sweep and hold it out on the y sweep, the copy's pokes and E126's exchanges), what the x and y
fields name together, and the data-word pokes of the pixel-event program that only move U1
against those that change the masks' meaning (the tile_x mask, dword 9, E620). The 12 hangs among
the 1813 refusals (E620) are Q003's, not an image.
