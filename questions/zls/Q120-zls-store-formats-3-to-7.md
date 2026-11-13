+++
id = "Q120"
question = "what do the stored depth formats 3 to 7 (CR_ISP_ZLSCTL bits 26:24) hold and how are they laid out, given that they store depth and stencil packed or nothing?"
unit = "zls"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E466", "E490", "E978", "E985", "E986"]
terms = ["CR_ISP_ZLSCTL"]
+++

E466: of the eight values of bits 26:24 only 0 (float32), 1 (24-bit) and 2 (16-bit) store plain
depth. At 1024 x 768 with G = 33 and no stencil buffer, 3 stores 965120 scrambled dwords in 1885
slots of 512, 5 stores 96580 and 6 stores 86084, and 4 and 7 store nothing. With a stencil buffer,
3 stores 965120 depth dwords and 17920 stencil dwords, 4 stores 245760 depth dwords and no stencil,
5 96580 and 1792, 6 86084 and none, 7 18432 and none. E490 repeated the counts without a stencil
buffer from stored dumps, in the x ramp (965120, 96580 and 86084 dwords for 3, 5 and 6, none for 4
and 7; the y ramp stores 965120, 84480 and 73760, so for 5 and 6 the count depends on the stored
data, and format 3 reaches the last dword of the 1000-page buffer, so 965120 is a lower bound) and
decoded none of the layouts.

What is open: the layout of each (bytes a pixel, the in-tile order, whether the stencil is inside
the depth words, whether 5 and 6 are compressed and by what), and what the hardware does with 4 and
7 when no stencil is present. To settle it: a depth ramp and a stencil pattern (a stencil buffer
with a known value per pixel, through the loads of E467 or a stencil operation) stored in each
format, the dwords decoded against the pixels, at several sizes.

Note 2026-11-13 (E978). With a loaded index stencil (bits 1 and 13) and bit 17, at 64 x 32 and 96 x
48: format 4 stores 160 depth dwords a tile (E466 scaled, held), formats 3 and 5 640, 6 512, 7 196 a
tile at 64 x 32 and not a whole number at 96 x 48; none of 3 to 7 writes the stencil store. The
dumps are kept; no layout is decoded.

Narrowed 2026-11-13 (round 10 offline, decision R10-1 a; E985, SEMI). E978's kept dumps decode for
formats 3, 4, 5 and 6 at both sizes, every changed dword: 3 and 5 the same bytes, a 5-byte record a
pixel (the float with its sign bit set, then the stencil byte) in 160-byte chunks a row at fitted
addresses; 4 the stencil alone, a 0xf0 byte before each quad's four; 6 the float with its sign bit
set, one dword a pixel; tiles in blocks of 640, 256 and 512 dwords, two tile rows a macro row. The
rules were fitted at 64 x 32 and frozen before 96 x 48 was scored, after a coverage look at 96 x
48. Open: held-out rows (a y ramp, the whole depth range, other stencil fills, edge tiles: the seeds
plan's stage zst2, closing10/seeds/exp-seeds-r10.md section 5), what parts 3 from 5, what the 0xf0
encodes, format 7's layout, and the formats without a stencil buffer.

Narrowed 2026-11-13 (E986). E985's offline layouts held out byte for byte: formats 3 and 4 on
every plane that ran (an x ramp under three constant stencil fills, a y ramp, a plane over 0 to 1,
40 x 20's edge tiles), formats 5 and 6 where every pixel of a tile row has its own depth. Where a
tile row repeats one depth (the y ramp) or a tile holds the constant background past an edge
target, formats 5 and 6 store fewer dwords, in another layout [infer: compressed]; format 7 stores
48 dwords under a constant stencil and 784 under the index one. None of 3 to 7 writes the stencil
store. Open: the layouts of formats 5 and 6 when they store less, and format 7's.
