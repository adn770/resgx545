+++
id = "Q135"
question = "what does the high-word form of ima32, ima32 d, iK, a, b, c, do with immediates and constants other than c56, with cie on the same instruction, with .neg, in the dual-issue form and with the selector 3, and what does bit 46 of an ima32 word do to r14?"
unit = "usse"
kind = "hw"
value = "low"
phase = 11
evidence = ["E493", "E494", "E495", "E501", "E525", "E526", "E528", "E597"]
terms = ["Universal Scalable Shader Engine (USSE)", "REGTYPE.FPINTERNAL"]
+++

E493: `ima32.u d, iK, a, b, c` writes the low 32 bits of a * b + c to d and the high 32 bits to iK
(15 of 15 cases of five register triples, K = 0 to 2, `.u` only); E501 uses it for a borrow, b *
0xffffffff + a over eight values of b (75 of 75), and an unsigned compare (64 of 64 pairs of eight
values, not padded). Eight raw words that differ from the plain `ima32.u` word in the fields
enc[38:36] and in the bits 46, 45, 44 and 35 left the result and i0 to i2 as the plain word's (24 of
24); with bit 46 set r14 read 0x2255 instead of its preset in 3 of 3 jobs; the registers read were
r10 to r17, r1 to r8 and i0 to i2.

Narrowed in 11.27: the high word on generic register operands is shown for `.u` (E525: 282 of 282
jobs, 42 corner triples and 200 random triples, K = 0 to 2, bits 63:32 of the exact 64-bit a * b +
c) and for `.s` (E526: 282 of 282, the signed 64-bit a * b + c with c sign-extended), and a signed
compare is two instructions through it (E528, 164 of 164 pairs).

What is open: the high word for immediates and constants other than c56, the extra operand together
with `cie` or `.neg` (the assembler writes both), the dual-issue secondary (two 16-bit lanes), the
selector 3 (an i3 that no `mov` of the assembler reads), an iK that is also a source or the
destination, a destination other than r10, what bit 46 does (it changed r14, a register the
instruction does not name: an unnamed destination, a second result or a write mask are all
possible), and whether the other unmapped bits do anything outside r10 and i0 to i2, which were the
registers read.

To settle it: the generic-value tables of E525 over each of those forms, with the i registers and
r10 to r17 read after; and the raw word with bit 46 set over operands that show where 0x2255 comes
from.

Round 12 cites: E597 (the high word of ima32 in client fills over every operand partition).
