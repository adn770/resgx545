+++
id = "Q178"
question = "what layout does TEXTYPE 5 read (one image under smp2d and smp3d at 16 x 16, E567), the one texture type of the eight whose layout no record reads"
unit = "texture"
kind = "hw"
value = "low"
phase = 11
evidence = ["E567", "E342", "E725", "E726"]
terms = ["TEXTYPE"]
+++

E567: type 7 is the twiddled image; 3 and 1 are one image of 256 values; 4 and 5 one image each
under smp2d and smp3d; type 2 depends on w (9, 12 and 25 distinct values). Q114 asks the volume
layout that type 2 may be; the cube layout is answered (E725, E726, E844). The next step
is the plan's follow-up (gen_p1132.py --follow) on TEXTYPE 2: six cube directions (the major axis
+-1) and two slice sweeps, the faces'
dword offsets read from the names. Types 1, 2, 4 and 5 are each at 16x16 only; other sizes would
say whether they are layouts or formats.

Run in 11.39 (E725, E726): types 3 and 1 read a raster of w dwords per row (8 jobs held out,
8 x 8 to 32 x 32); E567's "fixed 16" was the 16 x 16 case. Type 4 reads 32 dwords per row at 8,
16 and 32 wide [fitted, Q283]. TEXTYPE 2 with smp3d is a cube: six faces of 256 dwords (a 16 x 16
face), face = +x, -x, +y, -y, +z, -z along the dominant axis (exploratory: the plan predicted only
faces 1, 3, 5 for the negative axes; the mapping and the dominant-axis rule are post hoc [infer],
checked on cu-w02). Open: the faces' (s, t), the edges, other sizes (Q284); type 5 not run.

Narrowed 2026-11-12 (round 6 housekeeping, decision R6-1 a) to TEXTYPE 5. Types 3 and 1 read a
raster of w dwords per row and type 4 32 dwords per row (E725; the strides at other widths are
Q283), type 2 with smp3d is the cube, its face chosen by the dominant coordinate and its sign
(E725, E726, held out by E844; the faces' coordinates, edges and sizes are Q284). Type 5 was run
once, at 16 x 16 (E567: one image under smp2d and smp3d), and nothing else. To settle it: type 5
at 8 x 8 to 64 x 64 with a texture whose dwords name their own offsets, as E725 read types 1, 3
and 4.
