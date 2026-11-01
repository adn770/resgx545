+++
id = "Q042"
question = "what do bits 27:24 of the index list's first trailing word (VDM_INDEX2) do, when its low bits move the list's first index and 0x0f000000 drops two of five triangles?"
unit = "vdm"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E188", "E300", "E307", "E308", "E414"]
terms = ["VDM_INDEX2.WORD", "VDM_INDEX0.WORDS_PRESENT", "VDM_INDEX3.INDEX_WRAP"]
+++

What the word does with small values is answered (E300). In the five-copy job, two runs with the
same bytes in the eight cases both ran (the job's own value hung in the first), the low values
change the TA's object: at 1 it keeps five triangles but its last vertex is read past the list (1/w
100000.0, a vertex whose w meets the clamp), at 2 and 3 four triangles remain, at 5 three, at 0xff
none. An offset of the list's first index fits these: the last triangles read past the 15 indices
and are dropped. The job's own value, 0xf0000000, and 0 and 0x80000000 give the job's object, so
bits 31:28 change nothing seen; the earlier values of E188 (0x10000000, 0x70000000) agree. The
images do not change, because the copies overlap.

What is open: 0x0f000000 drops two of the five triangles, which an offset in bits 7:0 does not
explain, and its object is not that of 5: bit 15 is set in both entries of the primitive list's
first dword (0xd693ca30 for 0x56934a30) and the packed vertices differ; bit 15 marks one winding in
the random triangles of E307 (E308), so a winding flip would fit [infer]; which triangles an offset
drops, since the copies are identical; whether the offset counts indices or bytes, and its width.

To settle it: the five-copy job with copies at distinct positions (`copy_depth` or moved copies)
so that the dropped triangles show in the image and the object, at the offsets 1 to 6, 0x10,
0x100, 0x1000, and at each of bits 24 to 27 alone; with 16-bit and 32-bit indices if the header
selects the size.

Narrowed in 11.15 (E414, five copies at distinct depths, the object's primitive list read, two runs
each): the low bits are an offset in indices. With 0xf0000000 | k the object keeps the leading
floor((16 - k) / 3) of the five triangles for k = 0 to 6 (five, five, four, four, four, three,
three) and none for k = 0x10, 0x100 and 0x1000, the same in both runs. Of bits 27:24 only bit 24
acts: alone or with 0xf0000000 it keeps three triangles and sets bit 15 in the first two primitive-
list entries (the drop of E300's 0x0f000000); bits 25, 26 (the closed driver's flat-shading bit) and
27 change nothing. Bits 31:28 at 0xf, 0xd and 0x7 change nothing (see Q092).

Still open: what bit 24 does besides the drop and the winding mark on two entries; the offset's
width beyond 4096 and whether k counts indices (the fit says indices, one past the list counted);
what decides which two entries get bit 15. Status: narrowed, not answered.
