+++
id = "Q042"
question = "what do bits 31:24 of the index list's first trailing word (VDM_INDEX2) do: bits 27:24, when its low bits move the list's first index and 0x0f000000 drops two of five triangles, and (folded from Q092) what do bits 31:28 count, which the closed driver writes as 0xf on 1886 captured lists and 0xd on a draw of eight vertex attributes?"
unit = "vdm"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E188", "E300", "E307", "E308", "E414", "E346", "E348", "E546"]
terms = ["VDM_INDEX2.WORD", "VDM_INDEX0.WORDS_PRESENT", "VDM_INDEX3.INDEX_WRAP", "MTECTL.FLAT_VERTEX"]
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
27 change nothing. Bits 31:28 at 0xf, 0xd and 0x7 change nothing (see below).

Still open: what bit 24 does besides the drop and the winding mark on two entries; the offset's
width beyond 4096 and whether k counts indices (the fit says indices, one past the list counted);
what decides which two entries get bit 15. Status: narrowed, not answered.

**Correction 2026-11-16 (round 31, with the user):** Q092 is folded into this question (retired as
folded into Q042 after E1125; a fold is not an answer): it asked what bits 31:28 of the same word
count, this question bits 27:24, so the two are one question on bits 31:24. Its clauses are
appended to the line above, its evidence (E346, E348, E546) to this list and its term
`MTECTL.FLAT_VERTEX` to the terms; the reference to Q092 in the 11.15 paragraph above now points
here. Q112 (the header's bits 25:24 and the index width) stays separate. Q092's text, kept here: of
1888 captured index lists the first trailing word is `0xf0000000` in 1886, `0xf4000000` in GLES1's
vcolor_flat, a flat-shaded vertex colour, and `0xd0000000` in vs_many_attrs, whose vertex task
takes 14 vertices (`VDM_TASK0.MAX_VERTICES` 13) where most take 16 (E346, E348, one capture each).
Bits 31:28 equal MAX_VERTICES there and in the GLES2 draws (15), not in GLES1's (9) or the clears'
(7). The difference between 0xf4 and 0xf0 is in bits 27:24 (bit 26), the flat-shaded draw's 0xf4
a further value for them; the draw whose MTE control word sets `MTECTL.FLAT_VERTEX` to 3 with no
smoothed attribute is that same draw (E348). Narrowed in 11.15 (E414, one run each): on our job
the top nibble at 0xf, 0xd and 0x7 against a vertex task of 16 and of 14 vertices (MAX_VERTICES 15
and 13), with 15 and with 12 vertices, gives the object and the image of the control in all 12
cases, so the nibble is not tied to the vertex task's maximum in anything our job shows. Narrowed
in 11.31 (E546, 9 jobs): with five copies of the triangle the top nibble at 0xf, 0xd and 0x7 and
the task's attribute rows (VDM_TASK1 bits 14:7) at 1, 2 and 4 leave the object's PDS words, first
vertex, format word and primitive list equal to the control's in 9 of 9 jobs, so the nibble is
neither the task's maximum (E414) nor the attribute count in anything our jobs show.

Open from Q092: what bits 31:28 count. To settle it (Q092's plan): the GLES1 capture of
glShadeModel(GL_FLAT) over lines, strips and fans (GLSL ES 1.00 has no flat varying, so GLES2
cannot ask for it), which also bears on bit 26 above, and our triangle with the word's top nibble
varied against what the closed driver's lists vary with it.
