+++
id = "Q060"
question = "what do mr01, mr23, ir1 and the .h specials read in the vertex-side programs?"
unit = "pds"
phase = 11
evidence = ["E128", "E130", "E262", "E263", "E390"]
terms = []
+++

In a fill's secondary program ir1 reads 0 in any case, bit 9 of a special source makes a mov16 read
0, and ir0 is the tile position (E128). In the primary pixel program, per pixel of a 64x64 and a
128x128 triangle, ir0 is the 16x16 tile position, the ALU's ir1 and mov32's ir1.0 read 0, and mr01
and mr23 read 0 (E262). In the pixel-event program every path to ir1 read reads the event bits: on a
one-tile render the ALU, shl, abs, mov32's ir1.0 and ir1.1 and mov16's ir1.0, and on every tile of a
128x128 render whose slot word names its tile the ALU and mov32's ir1.0 and ir1.1; mr01, mr23 and
ir2.l read 0, ir2.h on the one tile, and .h reads 0 for ir0, ir1 and tim (E263). A test's source 65,
which the decoder names ir1, tests zero exactly where ir0 is 0 in the primary pixel and the
pixel-event programs, so that it reads ir0 [infer]; tstn of it was not measured (E262, E263).

Narrowed in 11.14 (E390): the planned route does not work: a douta from the vertex PDS program does
not reach the vertex task's sa (34 of 36 jobs stored the same vertex data in sa4-sa6 whatever the
read, as the earlier douta probe did), so no special was read this way. The reads need another route
out of the vertex program (a store to memory, or a vertex output).

What is open (pds_isa.md §7, items 4 and 9): the same reads in the vertex-side programs (the
vertex index is ir0; ir1 is Rogue's instance ID), and what mr01 and mr23 hold in any task, since
they read 0 in every one tried, also after a movs to mr.

To settle it: on the laptop, each special read with .l and .h, through the ALU, mov32 and a test,
stored per vertex by the vertex shader (vtx_dump.s), over 3 and 64 vertices, three runs.
