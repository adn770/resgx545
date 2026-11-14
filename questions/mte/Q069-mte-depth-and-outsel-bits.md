+++
id = "Q069"
question = "what do OUTSEL bit 13 and the state block's presence bits 16-31 select, and why does the viewport's z offset (state-block word 10) scale the depth plane when it is below 0.5?"
unit = "mte"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E057", "E061", "E066", "E192", "E193", "E198", "E284", "E286", "E287", "E411", "E419",
            "E465", "E466", "E490", "E981", "E987", "E1066"]
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

Folded here 2026-11-13 (round 11, decision R11-7 a): the question of bit 19 of CR_ISP_ZLSCTL with
the integer stored formats, with its evidence. Bit 19 negates the stored float (E466, E490) and
changes no dword of formats 1 and 2 over every depth that reached them: E490's ramp, E981's 0 to
0.3, E987's background; and no route that ran brings a negative depth to the integer conversion (a
depth below 0 after the clip is stored as 0, E981; the background depth is stored with its sign
cleared, E987; --tri-z outside 0 to 1 is clipped, E287), so the bit-19 clause is answered as no
observable effect [infer: on every route that ran]. What stays is the MTE's depth: the viewport's
z offset, word 10, is an offset at 0.5 to 1.0 (z = t + w - 0.5 at every dword, E987) but at 0.25
gave 0.6 t (E981) and at 0.125 0.4 t (E987) [infer: two points], not t + w - 0.5. Open: why a
low offset turns into a scale (a sweep of word 10 from 0 to 0.5 with the plane over 0 to 1, and
the viewport's z scale beside it).

Narrowed 2026-11-14 (r16-zls, E1066; the offline gate OQ069 first). On E987's ramp a z offset w
below 0.5 does not cut the plane at z = 0 (E1056's polygon cut failed 7 of 8): the plane is (1.6 w
+ 0.4 s) t, the near vertices at 0 and the far one at w + s + 0.6 (w - s), at w from 0 to 7/16 and
the z scale s at 0.25 and 0.75 (8 of 8 held out), except 912 pixels by the far edge that bend the
same way at every offset with a negative vertex [post hoc]. sgx-pipe's `mte::triangle` refuses a
viewport depth below 0. Open: why 0.6 and the bend, another triangle, OUTSEL bit 13 and the
presence bits 16 to 31.

Carried here 2026-11-14 with Q297's retirement (answered by E1059): a ZLS load pass over a plane
whose depth leaves 0 to 1, which only the z offset brings (E1051 stored 1.25 in format 0), did not
run; sgx-pipe's `zls::pass_plane` refuses it naming Q069.
