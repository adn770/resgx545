+++
id = "Q142"
question = "which control-stream form does the TA write in a region of the grid that CR_TE_AA bits 30 and 31 halve (16 x 16, 32 x 8 and 16 x 8 regions), and what are the five parameter-buffer dwords outside the stream blocks that change at 128 x 128 with 0xe0000000 (the region headers and the blocks are answered, E893)"
unit = "ta"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E504", "E893"]
terms = ["CR_TE_AA"]
+++

E504: against CR_TE_AA 0x20000000, 0x60000000 and 0xa0000000 each change 76 parameter dwords and 132
TA-data dwords (0xe0000000: 204 and 279 in mode 2 at 64 x 64; the 76 and 132 of 0x60000000 and
0xa0000000 are the same in modes 0 and 2, and mode 0 with 0xe0000000 failed its image check and has
no dump), the first parameter dwords at 1056, 1058, 1120 and 1122 (0x4688000f, 0x00030001,
0x4690ffff, 0xc0000000 becoming 0x46880007, 0x00010001 and so on).

What is open: the layout of those dwords (the parameter buffer's block headers or the region-header
fields of §6.4) and what they say about the window. To settle it: decode the changed dwords against
the region header and primitive block layouts of the specification, with the dumps of E504.

Narrowed 2026-11-12 (round 7 offline fold, E893; the question line is reworded, the question stays
open). The line read "what do the 76 parameter-buffer and 132 TA-data dwords that change with
CR_TE_AA bits 30 and 31 hold, and why do 0x60000000 and 0xa0000000 change the same number of dwords
by different values". With bit 29, bit 31 halves the region's width and bit 30 its height, a
macrotile keeping its pixel area; the TA data is the region-header array of that grid (positions
in 16 x 8 pixel units, 4 x 4-region sub-blocks, streams in the writer's walk, a second page past 32
streams): H-GRID, frozen on the 64 x 64 dumps, predicted te-m2-e0-128x128's 6144 TA-data dwords
with 0 off and its 128 stream blocks exactly [held out, one job]. The equal counts of 0x60000000
and 0xa0000000 are the same doubling along y and along x. The parameter-buffer change is the
stream blocks of the added regions, in the five forms the library's grid uses (post hoc), plus
five dwords from parameter dword 1083393 on at 128 x 128. Open: which form a halved region takes
(the tile test of a region narrower or shorter than two 16 x 16 tiles), those five dwords, and
macrotiles of other than 4 x 4 regions. To settle the forms: read E504's kept blocks against a
tile test of the finer region, fitted on 64 x 64 and frozen before the 128 x 128 blocks are scored
(they are now seen: a new size, or triangles that miss part of a region, is the held-out set).
sgx-pipe gives the headers (`ta::region_data`) and still refuses a render with such a word.
