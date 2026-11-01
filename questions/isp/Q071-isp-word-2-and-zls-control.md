+++
id = "Q071"
question = "what do the bits of the ZLS control word that change nothing seen (12, 15, 16, 20 to 23, 27 to 31) do, and how does the ISP use the control in a render with a stencil test?"
unit = "isp"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E057", "E169", "E216", "E228", "E284", "E337", "E411", "E465", "E466", "E467"]
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
