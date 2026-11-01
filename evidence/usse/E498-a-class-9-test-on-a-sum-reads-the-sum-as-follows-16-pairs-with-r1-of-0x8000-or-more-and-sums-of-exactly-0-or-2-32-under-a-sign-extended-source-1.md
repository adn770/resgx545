+++
id = "E498"
claim = "On the 16 pairs (r1, r2) = (0x8000, 0x8000), (0xffff, 1), (0x8000, 0xffff8000), (0x8001, 0xffff7fff), (0xffff, 0xffffffff), (0x9000, 0xffff7000), (1, 0xffffffff), (0x7fff, 0xffff8001), (0, 0), (0, 0xffffffff), (0x8000, 0), (0xffff, 0), (0x8000, 0x7fff0000), (0xffff, 0x80000000), (5, 0xfffffffb) and (0x8000, 0x7fff8000), the class 9 tests of a sum read it as follows: iadd32 testnat and testpat read the sign of the true signed sum sext16(r1) + r2 (16 of 16; the wrapped 32-bit sum fits 15, the one pair (0xffff, 0x80000000) separating the two readings), iadd32 testtaz and testtanz read the zero of that sum with r1 sign-extended from 16 bits (16 of 16: the pairs (0x8000, 0x8000) and (0xffff, 1) read zero, which a zero-extended r1 does not give, 11 of 16; the true and the wrapped sum give the same zero test on every pair, 16 of 16), iaddu32 testpat is true and testnat false for all 16 pairs, and iaddu32 testtaz is true for (0, 0) only (1 of 16) and testtanz for the other 15, the five pairs whose sign-extended sum wraps to zero and the six whose zero-extended sum wraps to zero (besides (0, 0)) included: the sum with its carry out of bit 31 fits 16 of 16 under either extension and the wrapped 32-bit sum under neither, and no pair separates a zero-extended from a sign-extended source 1 for iaddu32"
unit = "usse"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1124 (sha256 58907b06a8e9030472a809cd669d2c3823946fd67aaf4775f942704a90f6a5ae): probes/usse/iaddu32-pairs.toml (dump.s, 8 probes of 16 pairs each, 128 cases: iadd32 and iaddu32 with testtaz, testtanz, testnat and testpat); the campaign runner once for the table, no probe.py first run. The runner's verdicts: testtaz and testtanz of iadd32 SETTLED on the wrapped sum with a sign-extended source 1 (the true sum fits as well, so the verdict does not separate them), iaddu32 testtaz and testtanz UNDECIDED between the true sums with either extension, and the four sign tests NONE: my table wrote the same expectation for the true and the wrapped sums in the sign tests and its hypotheses read the sign wrongly. The counts above are mine, recomputed from the readbacks by a script written after the run (not kept in the tree)"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["usse-iaddu32-pairs"]
terms = ["Universal Scalable Shader Engine (USSE)"]
+++

**What runs.** `iaddu32.testtaz.chan0 !c0, p0, r1, r2` (and testtanz, testnat, testpat) and the same
for iadd32, then `mov r10, #0; p0 mov r10, #1`, over the 16 pairs above, which were chosen for sums
of exactly 0 or 2^32 under a sign-extended r1 and, in one pair, for a true and a wrapped sum of
opposite sign: r1 is 0x8000 or more in 11 of them and below it in 5 ((1, 0xffffffff), (0x7fff,
0xffff8001), (0, 0), (0, 0xffffffff) and (5, 0xfffffffb)).

**Results.** iadd32 testnat: 0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0 over the pairs in order,
testpat its complement; testtaz 1 for (0x8000, 0x8000), (0xffff, 1), (1, 0xffffffff), (0x7fff,
0xffff8001), (0, 0) and (5, 0xfffffffb), testtanz its complement. iaddu32: testnat 0 for the 16
pairs, testpat 1 for the 16, testtaz 1 at (0, 0) only. Readings of the iaddu32 zero test: the
wrapped sum of a zero-extended r1 is zero for 6 pairs besides (0, 0), that of a sign-extended r1 for
5, the two sets share 3 pairs ((1, 0xffffffff), (0x7fff, 0xffff8001), (5, 0xfffffffb)), so 8
distinct pairs, and all 8 read nonzero.

**What it shows.** [HW] iadd32's tests use the true signed sum for the sign (one separating pair
here, five in E472) and a sign-extended source 1 for the zero (answering Q126's iadd32 part, the
extension; the zero test of an overflowed iadd32 sum cannot differ between the true and the wrapped
sum: with r2 signed the sum stays within +-2^32, 16 of 16 pairs, and (1, 0xffffffff) reads zero).
iaddu32's sign tests read nothing of the sum (p always, n never) and its zero test counts the carry.
[infer] For iaddu32 the extension of source 1 cannot be told by a zero test: with the carry counted
the sums differ in zero-ness for no pair. A different observable, the value iaddu32 writes, would be
needed: Q126 stays open for it.

**What it does not show.** That the carry-counted zero of `iaddu32` is not 'zero if both operands
are zero' (both fit 16 of 16), `iaddu32` with no test (the assembler refuses it), `chan` fields
other than chan0, the test field's combined conditions (Q137), and pairs other than these 16.
