+++
id = "Q178"
question = "what do TEXTYPE 1, 2, 3 (the same image as 1), 4 and 5 read, and why is type 2 the only one of the eight run on which the third coordinate of smp3d changes the image (three images for smp2d, smp3d at 0.5 and smp3d at 1.5)"
unit = "texture"
kind = "hw"
value = "low"
phase = 11
evidence = ["E567", "E342"]
terms = ["TEXTYPE"]
+++

E567: type 7 is the twiddled image; 3 and 1 are one image of 256 values; 4 and 5 one image each
under smp2d and smp3d; type 2 depends on w (9, 12 and 25 distinct values). Q113 and Q114 ask the
cube and volume layouts that type 2 may be. The next step is the plan's follow-up (gen_p1132.py
--follow) on TEXTYPE 2: six cube directions (the major axis +-1) and two slice sweeps, the faces'
dword offsets read from the names. Types 1, 2, 4 and 5 are each at 16x16 only; other sizes would
say whether they are layouts or formats.
