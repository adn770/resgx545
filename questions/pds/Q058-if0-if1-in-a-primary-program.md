+++
id = "Q058"
question = "what sets the input flags if0 and if1 outside a vertex program, since neither tests true in any primary pixel or pixel-event task tried, and (moved from Q207) do if0 and if1 test true in the primary and pixel-event PDS programs of a transfer (a fill or a copy)?"
unit = "pds"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E128", "E130", "E262", "E263", "E389", "E620"]
terms = []
+++

In the pixel-event program ir0 reads the tile position and ir1 reads 2, or 6 on the last tiles
(E130); in a fill's secondary program ir0 is the tile position and neither flag tests true (E128).

In the primary pixel program neither if0 nor if1 tests true on any pixel of a 64x64 and a 128x128
triangle (E262), and in the pixel-event program on no tile of a one-tile and a 128x128 render, the
last tiles (ir1 6) included (E263). So Rogue's pixel readings, end of tile and end of render, do not
hold for these tasks; in a vertex program if0 holds on the last vertex (pds_isa.md §8.11).

Narrowed in 11.14 (E389): with the triangle drawn twice and five times over itself neither if0 nor
if1 tests true on any pixel of the primary pixel program, three runs each. The secondary pixel
program and the vertex-side flags were not run.

What is open (pds_isa.md §7, item 2): whether anything sets them in a pixel task (the secondary
program of a render, an end-of-render event, a render with several objects or primitives per tile),
and what if1 is in a vertex program (an (if1) kick alone works as (if0) does).

To settle it: the same per-pixel probe (pds_iter_if.s) with two triangles overlapping in one tile
and with the render's secondary pixel program in place of the primary; in a vertex program, if0 and
if1 passed to the vertex shader per vertex over 3, 4 and 64 vertices.

**Correction 2026-11-16 (round 31, with the user):** Q207's `if0`/`if1` clause moves here (Q207
keeps `ir2`, the `movs` specials and the programs that are not templates): whether `if0` and `if1`
test true in the primary and pixel-event programs of a transfer (a fill or a copy). The line above
says so and the list gains E620, the transfer model that refuses any PDS input no record measured:
none of the three template programs it runs reads the flags. To settle it (Q207's plan for the
flags): a primary-program probe that branches on `if0` and `if1`, run on the laptop with a fill
and a copy.
