+++
id = "Q178"
question = "what do TEXTYPE 1, 2, 3 (the same image as 1), 4 and 5 read, and why is type 2 the only one of the eight run on which the third coordinate of smp3d changes the image (three images for smp2d, smp3d at 0.5 and smp3d at 1.5)"
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
