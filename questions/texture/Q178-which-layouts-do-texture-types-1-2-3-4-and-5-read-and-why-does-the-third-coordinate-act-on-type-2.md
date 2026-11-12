+++
id = "Q178"
question = "what does TEXTYPE 5 compute from the texture memory it reads (two values, 0 and 0x0000ffff, that follow the stored dwords, a 16-column step at 16 to 64 texels and a 2-row alternation at 8 under E725's map fill, E911), the one texture type of the eight whose reading no record states"
unit = "texture"
kind = "hw"
value = "low"
phase = 11
evidence = ["E567", "E342", "E725", "E726", "E894", "E911"]
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

Note 2026-11-12 (round 7 offline, E894; post hoc, the question stays open, the line unchanged).
E567's three type 5 jobs stored no texel tag in any of their 2048 pixels: 0 at x mod 16 = 0 to 7
and 0x0000ffff at 8 to 15 in every row, under smp2d and smp3d alike, where types 1, 3, 4 and 7
return tags. [infer] Type 5 does not read the 32-bit texels as a layout, so the map texture of the
"to settle it" above would read no offset at other sizes either; what decides is whether the image
follows the texture memory (the same job on a zeroed and an all-ones texture) and whether the step
stays at half the width at 8 x 8 to 64 x 64.

Narrowed 2026-11-12 (round 7, R7-geo stage tx, E911; decision 5 of the ranking does not apply:
its retirement needed H-STEP to hold and the memory rows to show no read). Type 5 reads the
texture memory: the program storing 0 over the texture's first 112 dwords made the 16 x 16 image
0 in every pixel, storing 0xffffffff made it 0x0000ffff in every pixel (H-STEP's premise refuted 2
of 2). The step at half the width is refuted (0 of 3): at 32 x 32 and 64 x 64 the image repeats
E567's 16-column step (H-FIX16, frozen as a rival), at 8 x 8 it alternates by row. So the note
above (E894's [infer]) is withdrawn: type 5 is not a step of its own; what remains open is which
bits of which texels it reads and how it turns them into one of two values. To settle it: type 5
on textures whose dwords vary in one bit field at a time (the high and low halves of the map fill
are constant and counting), at 8 x 8 and 16 x 16, and with the format and the filter changed.
