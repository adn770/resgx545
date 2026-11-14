+++
id = "Q126"
question = "which extension of a source 1 above 0x7fff does the test of iaddu32 read (no test tells it, E498), and what value does iaddu32 write into sa0 for one instance (the fill's instances share sa0: E1061's sa0 row read other pairs' values, post hoc)"
unit = "usse"
kind = "hw"
value = "low"
phase = 11
evidence = ["E472", "E498", "E521", "E1061"]
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

Narrowed 2026-11-14 (round 16, session r16-usse, decisions R16-5 a and R16-6 a; E1061; the question
line is rewritten to what stays, the question is not retired). Held out and holding, with E521's
pairs and E498's tests replicated as controls: the value iaddu32 writes zero-extends source 1 with
source 2 #1, #127 and c56 (0xffffffff) and into i0 (8 of 8 pairs each, seven of which the sign
extension writes otherwise), and a write mask `.xy` or `.xyzw` on its test repeats it, component k
writing d + k from the sources advanced by k (2 of 2 rows, against the mask ignored and every
component the first's value). The row into sa0 FAILED its frozen prediction: two of eight dwords
read later pairs' values and its pixels mixed four values; post hoc [infer], sa0 is one register
shared by the fill's instances, every value read being a zero-extended sum of some pair. What
stays: the extension the test reads, which no test tells (the sum counted with its carry is zero
for (0, 0) only under both, the sign tests read nothing: [infer] not observable, as Q276's
predicate clause), and sa0 written by one instance alone. sgx-sim models the mask on the iaddu32
test and refuses the masks of the other tests, naming E1061.
