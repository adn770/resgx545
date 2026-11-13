+++
id = "Q071"
question = "what do the bits of the ZLS control word that change nothing seen (12, 15, 16, 20 to 23, 27 to 31) do, alone and set together, what does bit 0 store with a control other than 0x0017100c, and how does the ISP use the control in a render with a stencil test?"
unit = "isp"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E057", "E169", "E216", "E228", "E284", "E337", "E411", "E465", "E466", "E467", "E665", "E989"]
terms = ["CR_ISP_ZLSCTL", "CR_ISP_BGOBJVALS.STENCIL", "ISP2"]
+++

ISP word 2 is answered (E284): its compare (27:25) with the eight relations, the compare mask
(15:8), the write mask (7:0) and the operations on stencil fail (24:22), depth fail (21:19) and
pass (18:16), each 0 keep, 1 zero, 2 replace, 3 and 4 increment and decrement clamped, 5 invert, 6
and 7 increment and decrement wrapping; bits 31:28 change nothing.

The control word is now read bit by bit (§11.5 of 3d.md): bit 0 completes the job with no pixel
(E057), bit 1 turns the load on with bits 13 (stencil) and 14 (depth) choosing what (E467), bit 2
the stores, bits 17 and 18 the stencil and depth stores, bits 11:3 the tile pitch minus one
(E465), bit 19 the negated float and bits 26:24 the stored format (E466). E411's pages changed by
bits 3 and 4 and its faults with bits 5 to 11 set fit the pitch running out of the scratch buffer
(E465's derivation by hand; no fault was reproduced) [infer].

What is open: bits 12, 15, 16, 20 to 23 and 27 to 31 change nothing seen in the stores of E411
(one flip each of 0x17100c, two runs, on a 64 x 64 target: bits 12, 16 and 20 cleared, bits 15, 21
to 23 and 27 to 31 set; not tried with bit 1, a stencil test, formats 1 to 7, a larger target or a
partial render; E466 varies only bits 26:24, 19, 2, 17 and 18, E467 bits 1, 13 and 14). Bit 12 and
bit 16 are set in the window-surface controls of the closed driver (0x0017100c, 0x0017700e), so
they may matter to a stage this setup does not reach; E337's control for a texture's depth
attachment, 0x00140008, has both clear. Also open: the stencil test against a stencil the render
loaded (Q121). The stored formats 3 to 7 are Q120 and bit 19 with the integer formats is Q101. To
settle it: the same ramp stores with each of those bits flipped in a render with a stencil test
and a loaded stencil, the pitch and format fields set so that the stored dwords are readable.

Folded here 2026-11-12 (round 6 housekeeping, decision R6-1 a): Q244 asked the same control bits
(12, 15, 16, 20 to 23, 27 to 31) set in combination, and bit 0 under another control; both fit
this question, and its evidence (E665) moves here. E411 flipped each bit of 0x0017100c once: bits
1, 12 to 16, 20 to 23 and 27 to 31 left the image and the stored pages as the control's; the closed
driver sets 12, 16 and 20 in every value (E337). The pipeline simulator (E665) ignores those bits
as the single flips showed and models bit 0 as E411's raw output shows it: with 0x0017100d (two
runs) the colour image is not written (4096 of 4096 pixels keep the sentinel) and the stored pages
are the control's (page 4 and pages 12 to 15, 5120 dwords, the same first values); the image and
the depth and stencil store are different things. Bit 0 with any other control was not run and
refuses. To settle it, besides the runs above: the control with several of these bits set
together, and bit 0 with other controls (the formats, the load bits, another pitch), with the
depth and stencil dumps kept and the image counted.

Narrowed 2026-11-13 (E989, with E988's stencil test). Under a stencil test against a loaded stencil
(control 0x0017300e, E988), flipping bits 15, 21 to 23 and 27 to 31 (set) and 12, 16 and 20
(cleared) together makes the test read 0, not the loaded byte: every EQUAL-to-0 test passed and its
invert stored 0xff at every byte, while the depth dump and the loaded buffer stayed the base rows'.
So these bits are not all inert. Open: which of them does it (a flip of each under the same test),
and what they do to the depth path.
