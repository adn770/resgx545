+++
id = "Q101"
question = "what does bit 19 (the negated float) do with the integer stored formats (CR_ISP_ZLSCTL bits 26:24 = 1 and 2)?"
unit = "zls"
kind = "hw"
value = "low"
phase = 11
evidence = ["E057", "E284", "E411", "E465", "E466", "E490"]
terms = ["CR_ISP_ZLSCTL"]
+++

E411 found that flipping a bit of 0x17100c changes what is stored; E465 and E466 read the bits with
a depth ramp. Answered: bits 11:3 are the tile pitch minus one in tiles (E465: a dword 512 * (ty *
(G + 1) + tx) + the in-tile order, in 18 cases on 13 target sizes, the sizes that are not multiples
of the tile and G from 0 to 511 included). Bits 26:24 are the stored format (E466): 0 float32, 1
the 24-bit unsigned integer round(z * 0xffffff), 2 the 16-bit integer round(z * 0xffffff) >> 8 with
two rows in a dword (256 dwords a tile); bit 19 stores the float negated (-z at 786432 of 786432
pixels, a recompute of a second run from stored dumps, E490). That E411's earlier "region" bits 3
and 4 and its faults with bits 5 to 11 were this pitch is [infer] (E465).

With a positive depth ramp bit 19 changes no dword of formats 1 and 2: the dumps are byte-identical
to the dumps without it (same sha256 in both ramps, E490), and in format 0 it flips bit 31 at every
one of the 786432 dwords.

What is open: what bit 19 does with the integer formats when the depth is negative before the
conversion (the ramps are positive). The formats 3 to 7 are Q120's,
and bit 12 and the pitch beyond bits 11:3 are Q071's. To settle it: store the integer formats with
a depth that is negative before the conversion (a depth test greater with a negative ramp) with and
without bit 19, and compare the whole buffers.
