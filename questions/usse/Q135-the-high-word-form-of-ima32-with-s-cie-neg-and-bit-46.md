+++
id = "Q135"
question = "what does the high-word form of ima32, ima32 d, iK, a, b, c, do with .s, with cie on the same instruction, with .neg, in the dual-issue form and with the selector 3, and what does bit 46 of an ima32 word do to r14?"
unit = "usse"
kind = "hw"
value = "low"
phase = 11
evidence = ["E493", "E494", "E495", "E501"]
terms = ["Universal Scalable Shader Engine (USSE)", "REGTYPE.FPINTERNAL"]
+++

E493: `ima32.u d, iK, a, b, c` writes the low 32 bits of a * b + c to d and the high 32 bits to iK
(15 of 15 cases of five register triples, K = 0 to 2, `.u` only); E501 uses it for a borrow, b *
0xffffffff + a over eight values of b (75 of 75), and an unsigned compare (64 of 64 pairs of eight
values, not padded). Eight raw words that differ from the plain `ima32.u` word in the fields
enc[38:36] and in the bits 46, 45, 44 and 35 left the result and i0 to i2 as the plain word's (24 of
24); with bit 46 set r14 read 0x2255 instead of its preset in 3 of 3 jobs; the registers read were
r10 to r17, r1 to r8 and i0 to i2.

What is open: the high word for operands other than those run (two generic multi-limb register
values, immediates, constants other than c56), `.s` (a signed high word, the sign extension of the
product), the extra operand together with `cie` or `.neg` (the assembler writes both), the
dual-issue secondary (two 16-bit lanes), the selector 3 (an i3 that no `mov` of the assembler
reads), an iK that is also a source or the destination, what bit 46 does (it changed r14, a register
the instruction does not name: an unnamed destination, a second result or a write mask are all
possible), and whether the other unmapped bits do anything outside r10 and i0 to i2, which were the
registers read.

To settle it: the corner-value tables of E469 over each form, with the i registers and r10 to r17
read after; and the raw word with bit 46 set over operands that show where 0x2255 comes from.
