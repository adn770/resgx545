+++
id = "Q126"
question = "which extension of a source 1 above 0x7fff does the test of iaddu32 read, and does the value it writes zero-extend source 1 with a repeat, an immediate or a constant in source 2, or with other destinations"
unit = "usse"
kind = "hw"
value = "low"
phase = 11
evidence = ["E472", "E498", "E521"]
terms = ["Universal Scalable Shader Engine (USSE)"]
+++

E472: `iadd32` n and p read the sign of the true sum sext16(r1) + r2 (twelve pairs); `iaddu32`
nonzero reads the sum with its carry (eight pairs). E498 ran 16 pairs, five of them with r1 below
0x8000: `iadd32` n and p read the true signed sum (16 of 16; the wrapped sum fits 15, one pair
separating), `iadd32` z and nz read the zero of the sum with r1 sign-extended (16 of 16; a
zero-extended r1 fits 11), with r2 signed the sum of a 16-bit and a 32-bit value stays within
+-2^32, so the zero test of an `iadd32` sum agrees between the true and the wrapped sum (16 of 16
pairs; (1, 0xffffffff) reads zero); `iaddu32` p is always true and n never (16 of 16 each) and its z
is true for (0, 0) only, which the sum with its carry fits under either extension of r1 and the
wrapped sum under neither (so does 'zero if both operands are zero', which the 16 pairs do not
separate from it).

E521 answers what the question first asked: the value `iaddu32` writes zero-extends source 1 (16
distinct pairs in two datasets run before, seven of which a sign extension writes otherwise, such as
(0x8000, 0x8000) giving 0x10000), where `iadd32` sign-extends. It came from readbacks that were
already in the data, found when the simulator was replayed on the vectors, not from a table for it.

What is open is smaller. Which extension the test reads is not told by a test: the carry-counted sum
is zero for no pair under either extension but (0, 0), and the sign tests read nothing of an
`iaddu32` sum (E498). The value was seen with `chan0` and two destinations (a register, `o0` or
scratch dword 0) only: with a repeat, an immediate or a constant in source 2 or other destinations
it was not run (the `chan` fields other than `chan0` are Q150). To settle it: the same pairs with
r1 of 0x8000 to 0xffff in those forms, the value read back.
