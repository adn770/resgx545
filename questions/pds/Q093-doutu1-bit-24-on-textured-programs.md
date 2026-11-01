+++
id = "Q093"
question = "why does the closed driver add DOUTU1 bit 24 (wait for iterations) to some textured primary pixel programs, all GLES1 ones but GL_REPLACE and GLES2's two-texture and half-float luminance ones, and not to the other textured programs whose douti and doutt counts are the same?"
unit = "pds"
phase = 11
evidence = ["E345", "E364"]
terms = ["DOUTU1.WAIT_ITER", "DOUTU1.WAIT_FETCH"]
+++

The main part is answered (E364, the 114 captured primaries with a fetch): the closed driver sets
DOUTU1 bit 24 exactly when a douti of the primary iterates an attribute into the primary attribute
registers (the vertex colour or a coordinate set, DOUTI0 source below 36), 21 of 21, and every
program it starts reads that register; the 93 without it iterate only fetch coordinates (source
36) and their programs read only texels. GLES2's tex2, tex2_mip and fmt_lf16 iterate a coordinate
set or the colour into the attribute registers, so they follow the same rule.

What is open: whether the bit is needed: a program reading an iterated register without it might
read it stale.

To settle it: on the laptop clear bit 24 in our textured triangle whose shader also reads an
iterated colour, and compare the image.
