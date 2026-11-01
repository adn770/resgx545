+++
id = "Q126"
question = "how do iaddu32 and iadd32 extend a source 1 above 0x7fff, and what do their zero tests do when the sum overflows?"
unit = "usse"
kind = "hw"
value = "low"
phase = 11
evidence = ["E472"]
terms = ["Universal Scalable Shader Engine (USSE)"]
+++

E472: `iadd32` n and p read the sign of the true sum sext16(r1) + r2 (twelve pairs); `iaddu32`
nonzero reads the sum with its carry (eight pairs). The pairs that would tell zero- from
sign-extension of a source 1 of 0x8000 or more for `iaddu32` read nonzero either way, and the
zero test of a sum that overflows has no pair that separates the readings (the sum is zero only
without overflow in the pairs run).

What is open: the extension of source 1 in `iaddu32` (the `iaddu32` nonzero result of E472 rests on
one decisive pair, (1, 0xffffffff); two more with a wrapped sum of zero separate the readings only
if source 1 is zero-extended), `testtaz` of an overflowed `iadd32` sum (`testpat` is separated: the
true sum, 12 of 12), and `testtaz` and `testpat` of `iaddu32`. To settle it: pairs where sext16(r1)
+ r2 is exactly 0 or 2^32 with r1 of 0x8000 to 0xffff, for iaddu32 testtaz and testtanz, iadd32
testtaz.
