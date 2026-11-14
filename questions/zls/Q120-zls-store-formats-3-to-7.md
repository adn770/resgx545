+++
id = "Q120"
question = "what do the stored depth formats 3 to 7 (CR_ISP_ZLSCTL bits 26:24) hold and how are they laid out, given that they store depth and stencil packed or nothing?"
unit = "zls"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E466", "E490", "E978", "E985", "E986", "E1015", "E1031", "E1043"]
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

Narrowed 2026-11-13 (round 11 offline, decision R11-10 a; E1015). Two of the "store less" layouts
decode byte for byte from E986's kept dumps: format 7 under a constant stencil fill writes a 48-byte
template of 0x3f, 0x1f and the fill byte at the start of each 256-dword tile block (fitted on 0xa5,
held out blind on 0x00 and 0xff), and format 6 where four tile rows each hold one depth writes a
12-dword group of records (0x9e, the float with its sign clear, 0x00) and mask words 0x3f000000
(fitted on one block, two more blocks SEMI). sgx-pipe now models formats 3 and 4 as E986 held them
(a loaded and stored stencil, G + 1 the tiles across, format 3's edge tiles at an even size). Open:
format 7 under a varying stencil, format 5 under constant rows, format 6's edge tiles and its
variable-length runs, the template at fills equal to its markers and at other sizes, what parts the
pitch from the tiles across, and every packed format without a stencil buffer.

Narrowed 2026-11-13 (r13-zls, E1031). E1015's F7K held out at the fills 0x3f and 0x1f, equal to its
markers (48 of 48 each, no other dword), and F6C on a 48 x 32 y ramp of another origin (8 of 8
groups of its full tiles); on a flat 0.5, where every row of every tile is one depth, F6C failed 0
of 16: each block holds the same 44 dwords, another form (post hoc, no rule). Open: that flat
form, format 7 under a varying stencil, format 5 under constant rows, format 6's edge tiles and
variable-length runs, what parts the pitch from the tiles across, and every packed format without a
stencil buffer.

Narrowed 2026-11-14 (r14-zls, E1043). A flat format-6 tile at 0.25, 0.75, 1.0 and 0.0 stores
E1031's 44 dwords a block, its first 16 bytes E1015's F6C group 0 for the depth (FL-HEAD, FL-SHAPE 4
of 5); post hoc every block is E1031's with row 0's record carrying the depth, while 0.1234 stores
another form of 52 to 60 dwords. Format 7 under the index stencil keeps on a flat 0.5 the 771 dwords
E986's two ramps share (F7I-COMMON, F7I-COUNT); format 5 on the flat 0.5 is not format 6's block.
Open: the flat form's rule and why 0.1234 differs, format 7's depth-dependent dwords, format 5's
layout, format 6's edge tiles and variable runs, the pitch against the tiles across, and every
packed format without a stencil buffer.
