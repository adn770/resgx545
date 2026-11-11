+++
id = "Q030"
question = "does the sample layout of E281 hold in the tiles and windows past the first (what CR_TE_AA bits 31 and 30 do when bit 29 is clear is answered by E728 and E829; why the TA inserts the zero dword that leaves the image empty is Q293)?"
unit = "isp"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E210", "E211", "E219", "E220", "E281", "E415", "E502", "E503", "E504", "E728", "E829"]
terms = ["CR_ISP_MSAA", "CR_ISP_MSAA.MODE", "CR_ISP_MSAA.ENABLE", "CR_ISP_MULTISAMPLECTL", "CR_TE_AA", "programmable sample positions"]
+++

What each value of `CR_ISP_MSAA.MODE` stores is answered (E281): mode 1 stores two samples of each
pixel side by side in x and mode 2 four in a 2x2 block, the samples of `CR_ISP_MULTISAMPLECTL` in
byte order, fitted with no pixel missed over eight positions of a known edge, one run each (that
mode 1 takes its samples from `CR_ISP_MULTISAMPLECTL` and not the MTE's word is read from mode 2);
mode 3 hangs (E210). A clear bit 31 still tiles the triangle: the parameter buffer and TA data are
the same as with it set, and only the stored image loses the triangle, in modes 1 and 2.

Where the tiles land is answered by a rule read post hoc (E503, 48 runs of the identity maps of
E502): the stored 32 x 16 tile (tx, ty) holds the pixels of a half window of its own area, from x =
32 tx + 16 b31 and y = 16 ty + 8 b30 (b30 in mode 2 only), each stored twice in x and, in mode 2,
in y; the rule was read from the 64 x 64 runs after the declared test decoded nothing, and agrees
with all 634 tiles of the sizes declared held out (an agreement found after the rule was written).
E415's constant displacement of 4 pixels was the doubling of an in-tile offset. With `CR_TE_AA` bit
29 set, bits 31 and 30 change 76 and 132 dwords of the parameter buffer and TA data (E504; what
they hold is Q142), and bit 29 alone changes nothing (E281; byte-identical to a clear word in 10 of
10 pairs of configurations, E502).

What is open, which keeps Q030 open and is not the 13 tiles with background pixels (Q141): what
bits 31 and 30 do when bit 29 is clear, where the triangle is not stored (E281; 6 of 6 jobs of
E504, modes 0 and 2; the tool wrote no dump for them, so the TA's output was not compared), and
what bit 29 gates; and whether the sample positions of E281, fitted inside the target's first 16 x
16 tile, are the same in the tiles past the first and in each window, which the identity maps
cannot show because every sample slot of a pixel held the same iterated position (E502).

To settle it: the jobs of E504 with bit 29 clear and bits 31 or 30 set, with the render dumps kept
whatever the image check says, compared with the parameter buffer of 0x20000000; and the small
triangle moved tile by tile across a 64x64 target in mode 2 under the four windows, fitted per tile
with isp_words.py layout --joint.

Narrowed in 11.15 (E415, one run of four tables, three triangle phases and three rows each): a
small triangle in each tile of a 64x64 target under modes 1 and 2 is drawn only in the first and
third tile columns with the TE anti-aliasing bits clear and only in the middle column with them
set; every drawn triangle lands at its tile's place plus a constant. Corrected in 11.26 [infer]: by
E503's rule that is the doubling and the window, and the TE bits choose a window of each tile, not
tile columns.

Narrowed in 11.26 (E502 to E504; the tile placement and the window of each TE bit are answered, not
the clear-bit-29 case or the per-tile sample layout). Status: narrowed, not answered.

Run in 11.39 (E728): with bit 29 clear, bits 31 and 30 do act in the TA's output: TE 0x40, 0x80 and
0xc0 differ from TE 0x00 in 89 to 818 parameter and 132 to 367 TA data dwords (0 of 9 equal), and
equal the bit-29-set job in the TA data (6 of 6); the parameter buffer differs from it in 13 dwords,
a one-dword displacement of dwords 11 to 26 (Q285). The image is empty without bit 29 in 9 of 9
jobs. Point 1 ("what bits 31 and 30 do when bit 29 is clear, where the triangle is gone") is only
partly answered: bits 31 and 30 act in the TA output the same as with bit 29 set, but "where the
triangle is gone" is not answered. Landed te 0x20 equals te 0x00 (0 dwords differ in the parameter
buffer and the TA data), so bit 29 alone changes nothing and acts only with bit 30 or 31 set. "What
bit 29 gates" stays open (Q285).

Note 2026-11-11 (round 4, stale text overtaken by E829). The "what bit 29 gates stays open (Q285)"
of the paragraph above is answered: Q285 is retired as answered by E829, which shows the 3D reads
the object in the bit-29-set layout, so with bit 29 clear and bit 30 or 31 set the zero the TA
inserts at dword 11 is read as the format word and the image is empty. "Where the triangle is gone"
is therefore answered, and what is left of the TA side (why the TA inserts the dword) is Q293. What
stays here is the sample layout in the tiles and windows past the first (every sample slot held the
same iterated position in E502's identity maps, which cannot show it).
