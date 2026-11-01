+++
id = "Q162"
question = "what do OUTSEL bits 10, 11 and 15 select, which fault (bits 8 without a size row, 10, 11, 15 on the plain triangle) or hang (10 and 15 with the size program) the job, and why does a two-output size program hang the points job with and without bit 8"
unit = "ta"
kind = "hw"
value = "low"
phase = 11
evidence = ["E544"]
terms = ["OUTSEL", "OUTSEL.VTX_SIZE", "ISP0.OBJ_TYPE"]
+++

E544 flipped each of the OUTSEL bits 8 to 15 and 20 to 31 on the plain triangle (20 jobs): bit 8
(the point size, with a vertex program that writes the size row) faults without the row; bits 10, 11
and 15 fault (declared complete), bit 12 clears the format word to 0x00000000 (the 1/w dword and bit
18 gone, one vertex dword fewer than declared), bits 20, 21 and 22 complete with no object, and bits
9, 13, 14 and 23 to 31 change nothing in the object. With the one-output size program and points,
bits 10 and 15 hang (4 of 4). The two-output size program (o4 = A, o5 = B) hung the points job in 4
of 4 jobs: with OUTSEL bit 8 at both orders of (A, B) and in a repeat (3 of 3) and without bit 8 (1
of 1).

Open: what bits 10, 11 and 15 and the 20 to 22 select (E286's presence-word bits are a different
word), why bit 8 faults without the row, and what the two-output hang is: the program, the
coordinate size for two outputs with points, or the second output.

To settle it: each bit with a vertex program that writes the rows it may need (colour, size, 1/w),
the same bits with `--vtx-coords` 1 to 4, and the two-output program as plain triangles. No kernel
change.
