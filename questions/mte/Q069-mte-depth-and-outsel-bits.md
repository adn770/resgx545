+++
id = "Q069"
question = "what do OUTSEL bit 13 and the state block's presence bits 16-31 select?"
unit = "mte"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E061", "E066", "E192", "E193", "E198", "E286", "E287", "E419"]
terms = ["OUTSEL", "VIEWPORT.Z_OFFSET", "VIEWPORT.Z_SCALE", "PRESENCE"]
+++

The depth question is answered (E287): the MTE clips at clip z = -w and w, cutting a triangle
along them, and the viewport's depth is not clipped; against a clear depth a depth above 1
compares as itself and a negative one as 0. OUTSEL bit 12 puts each vertex's 1/w into the TA's
object (E286): clear, the object loses the 1/w dwords and the format word bit 18.

What is open: OUTSEL bit 13 changes neither the object nor the image with zero, one and two
coordinate sets (E286). Of the presence word's bits 16-31, set one at a time, 17, 18 and 22 to 25
remove the triangle and 27 hangs (one run); which words they announce is not shown. What the
missing 1/w costs a perspective triangle is not run.

To settle it: OUTSEL bit 13 with point sprites and with the vertex colour present; each removing
presence bit with words appended to the block (--blk-add-like growth) and the render memory
dumped; OUTSEL bit 12 clear on vtx_persp.s with a perspective iteration.

Narrowed in 11.15 (E419, two runs): with a perspective triangle (w = x + 2, two coordinate sets) and
an iterating pixel program, OUTSEL with bit 12 set puts the 1/w in the object and with it clear
leaves two dwords a vertex, and bit 13 changes neither the object nor the image; all four values
give the same image, an affine interpolation on all 1062 pixels, so the missing 1/w costs this
iteration nothing (the DOUTI perspective flag was not set). Not run: bit 13 with point sprites or
the vertex colour, and the presence bits 16 to 31 with appended words (the tool grows the block only
for presence bits 2 to 5 and 7). Status: narrowed, not answered.
