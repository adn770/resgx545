+++
id = "Q093"
question = "why does the closed driver add DOUTU1 bit 24 (wait for iterations) to some textured primary pixel programs, all GLES1 ones but GL_REPLACE and GLES2's two-texture and half-float luminance ones, and not to the other textured programs whose douti and doutt counts are the same?"
unit = "pds"
phase = 11
evidence = ["E345"]
terms = ["DOUTU1.WAIT_ITER", "DOUTU1.WAIT_FETCH"]
+++

Every captured primary with a doutt carries `DOUTU1.WAIT_FETCH`, and every one that iterates
without fetching carries `DOUTU1.WAIT_ITER`; with a fetch, bit 24 is added in 21 programs and
left out in 93, and the douti and doutt counts do not tell the two groups apart (E345). The
GLES1 programs that mix in the vertex colour fit a program that reads an iterated value itself;
GLES2's tex2, tex2_mip and fmt_lf16 do not obviously.

To settle it: read which primary attribute registers the USSE program of each group reads (its
first instructions' sources, with tools/usse-dis, privately), and on the laptop clear bit 24 in
our textured triangle whose shader also reads an iterated colour, to see whether the image
changes.
