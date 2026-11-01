+++
id = "Q107"
question = "why does the final render of a job that overflows store zeros for the first row of macrotiles and the depth with its sign bit set for the rest, and in what order are the tiles stored?"
unit = "zls"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E461", "E058", "E411", "E465", "E468"]
terms = ["CR_ISP_ZLSCTL", "CR_ISP_ZSTORE_BASE"]
+++

The window of the store (64512 dwords at 1024x768, 326656 at 4096x4096) is answered (E465): the
tile (tx, ty) of 32 x 16 pixels is stored at dword 512 * (ty * (G + 1) + tx), G being bits 11:3 of
the control, and the library's control has G = 1, so the tiles of a row overlap and the last one
written keeps the address. The window is (th - 1) * (G + 1) + tw tiles. The in-tile order is the
bits y0 x0 y1 x1 y2 x2 y3 x3 x4 of the pixel offsets. In 16 of 18 cases on 13 sizes every stored
dword is at that address; the two overflowed 4096 x 4096 jobs have 80640 and 48000 stored dwords
that are not (E465).

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
