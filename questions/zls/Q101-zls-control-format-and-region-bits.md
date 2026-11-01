+++
id = "Q101"
question = "what does bit 19 (the negated float) do with the integer stored formats (CR_ISP_ZLSCTL bits 26:24 = 1 and 2)?"
unit = "zls"
kind = "hw"
value = "low"
phase = 11
evidence = ["E057", "E284", "E411", "E465", "E466"]
terms = ["CR_ISP_ZLSCTL"]
+++

E411 found that flipping a bit of 0x17100c changes what is stored; E465 and E466 read the bits
with a depth ramp. Answered: bits 11:3 are the tile pitch minus one in tiles (E465: a dword 512 *
(ty * (G + 1) + tx) + the in-tile order, in 18 cases on 13 target sizes, the sizes that are not
multiples of the tile and G from 0 to 511 included). Bits 26:24 are the stored format (E466): 0
float32, 1 the 24-bit unsigned integer round(z * 0xffffff), 2 the 16-bit integer round(z *
0xffffff) >> 8 with two rows in a dword (256 dwords a tile); bit 19 stores the float negated (the
three most frequent dwords only). That E411's earlier "region" bits 3 and 4 and its faults with
bits 5 to 11 were this pitch is [infer] (E465).

What is open: what bit 19 does with the integer formats (the three most frequent stored dwords are
the same as without it; the buffers were not compared). The formats 3 to 7 are Q120's, and bit 12
and the pitch beyond bits 11:3 are Q071's. To settle it: store the integer formats with a depth
that is negative before the conversion (a depth test greater with a negative ramp) with and
without bit 19, and compare the whole buffers.
