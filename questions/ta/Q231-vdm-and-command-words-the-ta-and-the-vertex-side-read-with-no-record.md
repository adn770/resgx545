+++
id = "Q231"
question = "what do the words of a render job that the vertex side and the TA read or ignore and no record explains do: the command's CR_MTE_CTRL (0xa2) and MTE screen words, the command words 10 to 25, the MTE state block's WCLAMP, the attribute rows of a VDM state block (VDM_STATE1 bits 7:0), the end-of-scene block's two terminate halves (E059 only shows that clearing a half leaves part of the target unwritten), and the stream's forms of a region (the primitive word and the further dword) for an object of more than five triangles?"
unit = "ta"
kind = "hw"
value = "low"
phase = 12
evidence = ["E059", "E060", "E177", "E180", "E650", "E652"]
terms = ["CSTREAM.PRIM_TILES", "TERM.CLIP_RIGHT", "TERM.CLIP_BOTTOM"]
+++

The model (E650) accepts the library's CR_MTE_CTRL (0xa2) and CR_MTE_SCREEN ((w - 1) | (h - 1) <<
16), the library's value in each of the render command words 10 to 25 (all 355 dumped scenes carry
the same value in each, and nothing in the model reads them), WCLAMP of the library's or of 1e-3
(ta-objects-wclamp: the object did not change at w = 1; a w other than 1 refuses under Q230), the
attribute rows 5 of a draw and 1 of the end of scene (VDM_STATE1 bits 7:0, refused under Q047 when
they differ), and an end-of-scene term word of the target's last 32 x 32 block, and refuses any
other value here: no record reads those words through an object or a stream, so a scene that
varies one is not fitted by ignoring it. It also refuses a stream for an
object of more than five triangles (the five-bit vertex numbers 16 to 31 hold 15 vertices; the
splitting of a longer index list into objects is E546's, Q094 and Q070).

What would settle it: command words flipped one bit at a time with the objects dumped, the way
E407 did the macrotile words.

Status: open.
