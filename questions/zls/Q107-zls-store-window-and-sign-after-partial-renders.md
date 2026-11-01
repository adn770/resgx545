+++
id = "Q107"
question = "why does the final render of a job that overflows store zeros for the first row of macrotiles and the depth with its sign bit set for the rest, and in what order are the tiles stored?"
unit = "zls"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E058", "E411", "E461", "E465", "E468", "E489", "E628", "E629"]
terms = ["CR_ISP_ZLSCTL", "CR_ISP_ZSTORE_BASE"]
+++

The window of the store (64512 dwords at 1024x768, 326656 at 4096x4096) is answered (E465): the
tile (tx, ty) of 32 x 16 pixels is stored at dword 512 * (ty * (G + 1) + tx), G being bits 11:3 of
the control, and the library's control has G = 1, so the tiles of a row overlap and the last one
written keeps the address. The window is (th - 1) * (G + 1) + tw tiles. The in-tile order is the
bits y0 x0 y1 x1 y2 x2 y3 x3 x4 of the pixel offsets. In 16 of 18 cases on 13 sizes every stored
dword is at that address; the two overflowed 4096 x 4096 jobs have 80640 and 48000 stored dwords
that are not (E465): they are 0x00000000 in both ramp dumps of a rerun that kept them (E489), so the
zeros are measured; that they are the zeros of a parameter-buffer overflow stays E468's inference.

What E461 called the leading zero dwords and the sign flip of a job that overflows is the same
store (E468): with no two tiles at one address (G = 33) the 336 tiles of tile rows 0 to 11 (the
first row of macrotiles) hold zeros, 48 more are half zeros, and the other tiles hold the depth
with the sign bit set, at the address of the rule (E468 also counts 11264 stored dwords beyond the
rows' tiles). The aliased job equals those tiles written in raster order with the first macrotile
last (an order chosen after the zeros were seen), except 512 dwords (1536 at 0x30 pages).

What is open: why the first row of macrotiles stores zeros (a macrotile the partial renders stored
without a depth, or a depth the final render did not load), what sets the sign bit (bit 19 and bit
1 are clear in the controls of these jobs, 0x0017110c and 0x0017100c, so it is something the
control does not show, probably the partial-render path [infer], E468; a load clears the sign,
E467), why the ramp job at 0x30 pages negates (E468) while E461's z = 0.5 job at 0x30 keeps the
positive whole-buffer values behind its zeros (the number of partial renders of each is not
known), the exact order of the tile stores (the 512 dwords the two orders tried leave different),
and the extra stored dwords in the two slots each tile row has beyond its tiles. To settle it: the
same ramp job at a pitch with no overlap and three controls, with and without bits 1 and 14 (the
final render's load) and bit 19 (E466), and a scene whose first macrotile row holds geometry after
the last partial render.

Narrowed in 11.38 (E628, E629). The first row of macrotiles stores zeros, and the load buffer's
own dump is zeroed in the same region (E628). At 1024x768 with no overlap (G = 33; 34 slots a tile
row for 32 tiles) the 195584 zero dwords are 336 whole target tiles and 48 half-zero tiles (360
tile-equivalents of the 384 in tile rows 0 to 11, so the first row is 24 tile-equivalents, 6.25
percent, short; the half-zero tiles sit at tx 6, 14, 23 and 31 of every row) and 22 zero slots of
the padding at tx 32 and 33 (11264 dwords); 184320 in a job that loads. At 4096x4096 (G = 127, no
padding) the 4193152 zero dwords are a prefix of 8189.75 of the first row's 8192 tile slots, 2.25
tiles short (the band of a first row hit 2 of 2 and that of a first macrotile missed 2 of 2). The
zero rows are not one rule across the sizes. The sign bit is set in exactly the 26 of 44
overflowing jobs whose first abort's threshold was raised (E625), not by P, the pitch (5 of 5
cells identical at G = 1 and 33) or the number of partial renders; within the z = 0.5 scene the
raise is the same as P below 0x2d, and the one pair that separates them is E461's z = 0.5 job at
0x30 (positive, not raised) against E468's ramp job (signed, raised, its page need being larger)
[infer: the ramp's need]. The loaded-buffer jobs do not test the sign (their store is the index
buffer). Open: the tile order of the store, the shortfall of the first row at both sizes, what the
11264 extra zero dwords at 1024x768 are, and what negates (the partial render's store or the final
render's load).
