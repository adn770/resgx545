+++
id = "Q092"
question = "what do bits 31:28 of the index list's first trailing word count, which the closed driver writes as 0xf on 1886 captured lists and 0xd on a draw of eight vertex attributes?"
unit = "vdm"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E346", "E348", "E414"]
terms = ["VDM_INDEX2.WORD", "MTECTL.FLAT_VERTEX"]
+++

Of 1888 captured index lists the first trailing word is `0xf0000000` in 1886, `0xf4000000` in
GLES1's vcolor_flat, a flat-shaded vertex colour, and `0xd0000000` in vs_many_attrs, whose
vertex task takes 14 vertices (`VDM_TASK0.MAX_VERTICES` 13) where most take 16 (E346, E348, one
capture each). Bits 31:28 equal MAX_VERTICES there and in the GLES2 draws (15), not in GLES1's
(9) or the clears' (7). The difference between 0xf4 and 0xf0 is in bits 27:24 (bit 26), which
Q042 holds, with the flat-shaded draw's 0xf4 as a further value for it; the draw whose MTE
control word sets `MTECTL.FLAT_VERTEX` to 3 with no smoothed attribute is that same draw (E348).
Q042 also records that bits 31:28 changed nothing seen on our own jobs, at 0xf, 0x0, 0x8,
0x1 and 0x7.

What is open here: what bits 31:28 count, and whether they are tied to MAX_VERTICES or to the
attribute count.

To settle it: on the laptop, run our triangle with a vertex task of 16 and of 14 vertices and the
word at 0xf0000000, 0xd0000000 and 0x70000000, with eight vertex attributes and with one, reading
whether the object and the image change; the flat-shading question (bits 27:24) belongs with
Q042: capture GLES1's glShadeModel(GL_FLAT) over lines, strips and fans (GLSL ES 1.00 has no flat
varying, so GLES2 cannot ask for it).

Narrowed in 11.15 (E414, one run each): on our job the top nibble of the first trailing word at 0xf,
0xd and 0x7 against a vertex task of 16 and of 14 vertices (VDM_TASK0.MAX_VERTICES 15 and 13), with
15 and with 12 vertices, gives the object and the image of the control in all 12 cases, so the
nibble is not tied to the vertex task's maximum in anything our job shows. The attribute count was
not varied (the tool has no option for it), and the GLES1 flat-shading capture was not made. Status:
narrowed, not answered.
