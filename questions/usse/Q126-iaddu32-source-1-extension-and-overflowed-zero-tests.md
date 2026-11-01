+++
id = "Q126"
question = "how does iaddu32 extend a source 1 above 0x7fff?"
unit = "usse"
kind = "hw"
value = "low"
phase = 11
evidence = ["E472", "E498"]
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

What is open: the extension of source 1 in `iaddu32` (sign or zero for a source 1 above 0x7fff). No
zero test tells it, since the carry-counted sum is zero for no pair under either extension but (0,
0), and the sign tests read nothing of an `iaddu32` sum. To settle it: read the value `iaddu32`
writes to a register (a test form that keeps its result, since the assembler refuses `iaddu32` with
no test: E469) with r1 of 0x8000 to 0xffff and a small r2, which the tests of 11.23 to 11.25 did not
do (whether the 2026-10-22 value probes of `iaddu32` reached such an r1 was not checked here), and
the chan fields other than chan0.
