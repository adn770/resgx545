+++
id = "E472"
claim = "A class 9 test of a 32-bit register through source 2 tests all 32 bits (iadd32.testnat, testpat, testtaz and testtanz.chan0 !c0, p0, #0, rN: bit 31 set, bit 31 clear, all zero, any set, 8 of 8 corner values each; iaddu32.testtanz 8 of 8; iaddu32.testnat never true, 8 of 8), but with a source 1 the sum is not the wrapped 32-bit sum, for the tests run: n and p of iadd32 read the sign of the true sum sext16(r1) + r2 (r2 signed), so r1 = 0x7fff with r2 = 0x7fffffff leaves n clear and p set (12 pairs, of which 5 overflow the signed 32-bit sum and separate the readings: the true sum fits 12 of 12, the wrapped one 7 of 12), and the nonzero test of iaddu32 sees the carry out of bit 31, so r1 = 1 with r2 = 0xffffffff is nonzero (8 of 8, the wrapped sum fits 5 or 7; the one pair (1, 0xffffffff) decides it for a zero- and a sign-extended r1 alike, the two others whose wrapped sum is zero only if r1 is zero-extended); z of iadd32 and testpat, testtaz of iaddu32 were not separated; the exact unsigned and signed compares of two 32-bit registers cost six instructions each with the borrow formula over t = ima32.u r11, r2, c56, r1 (64 of 64 pairs each, and 16 of 16 for the unsigned compare only with three nops after the ima32), and ima32 itself has no test field"
unit = "usse"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1122 (sha256 ec423efc3d9aa34576553da70916be4ceb715a729cbc02cc4bd89fa052511244): probes/usse/compare32.toml (dump.s; 14 probes of the compare and the sum tests, 358 cases, 146 of them the immediate-test probes of E473) and probes/usse/compare32x.toml (4 probes, 44 cases: the follow-up after case 9 of usse-compare32-iadd32-testnat-src1 read n clear where the model said set); two runs of the compare32 probes (the first by probe.py outside the data, the second by the campaign runner, the dataset: the same readback in all 358 cases) and one run of compare32x by probe.py (outside the data) and one by the campaign runner (the dataset: the same readback in all 44)"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["usse-compare32", "usse-compare32x"]
terms = ["Universal Scalable Shader Engine (USSE)"]
+++

**What runs.** The sum tests are `iadd32.<test>.chan0 !c0, p0, #0, r2` (the test of a full 32-bit
register through source 2, source 1 the immediate 0), then `mov r10, #0` and `p0 mov r10, #1`, over
the eight corner values 0, 1, 0xffff, 0x10000, 0x7fffffff, 0x80000000, 0xffffffff, 0x80000001.
The source-1 forms are `iadd32.testnat.chan0 !c0, p0, r1, r2` and `testtaz` over ten pairs where
the full 32-bit r1 + r2 and the sext16 one differ. The follow-up compare32x runs `testnat`,
`testpat` and `testtaz` with r1 a 16-bit value and r2 a 32-bit one over twelve pairs that overflow
the signed 32-bit sum or not, and `iaddu32.testtanz` over eight pairs with a carry out of bit 31.
The compares: `t = ima32.u r11, r2, c56, r1` (a - b with a = r1, b = r2), then for the unsigned
one `xor r12, r1, r2; and r13, r2, ~r1; and r14, r11, ~r12; or r13, r13, r14; shr.testtanz.chan0
!c0, p0, r13, #31` (the borrow `((~a & b) | (~(a ^ b) & t)) >> 31`), for the signed one `xor r12,
r1, r2; xor r13, r1, r11; and r12, r12, r13; xor r12, r12, r11; shr.testtanz ... r12, #31`
(`((a ^ b) & (a ^ t)) ^ t` at bit 31), and `iadd32.testnat.chan0 !c0, p1, #0, r13` on the same
word; r10 = the compare, r11-r15 the formula's words, over the 8 x 8 pairs of the corner values
plus 0x80000001.

**Results (campaign run).**

| probe | cases | fits |
|---|---|---|
| compare32-ult | 64 | 64 of 64 (r10 = a < b unsigned, r11 = a - b, r12 = a ^ b, r13 = the borrow word, r15 = the iadd32.testnat reading of it) |
| compare32-ult-padded | 16 | 16 of 16 (the unsigned compare only, 9 distinct a values; three nops after the ima32: the same as without) |
| compare32-slt | 64 | 64 of 64 (r10 = a < b signed) |
| iadd32-testnat, testpat, testtaz, testtanz -src2 | 8 each | 32 of 32 (bit 31 set, clear, zero, nonzero) |
| iaddu32-testnat-src2 | 8 | 8 of 8 (never true) |
| iaddu32-testtanz-src2 | 8 | 8 of 8 (nonzero) |
| iadd32-testtaz-src1 | 10 | 10 of 10 (sext16(r1) + r2; the full 32-bit r1 + r2 fits 7) |
| iadd32-testnat-src1 | 10 | 9 of 10; case 9 (r1 = 0x7fff, r2 = 0x7fffffff) read n clear, the model said set |
| compare32x iadd32-ovf-testnat | 12 | 12 of 12 for the sign of the true sum, 7 of 12 for the wrapped sum (5 pairs overflow and separate) |
| compare32x iadd32-ovf-testpat | 12 | 12 of 12 true, 7 of 12 wrapped |
| compare32x iadd32-ovf-testtaz | 12 | 12 of 12 for both (no pair separates a zero) |
| compare32x iaddu32-carry-testtanz | 8 | 8 of 8 for the sum with its carry, 5 for the wrapped sum with r1 zero-extended, 7 sign-extended |

The pairs that separate the true sum from the wrapped one: (0x7fff, 0x7fffffff) n clear (the true
sum is positive, the wrapped one 0x80007ffe is negative), (1, 0x7fffffff) n clear, (0x8000,
0x80000000) n set (the true sum is negative, the wrapped one is positive), (0xffff, 0x80000000) n
set, (0x8000, 0x80000001) n set; testpat reads the opposite in each. For `iaddu32`, (1, 0xffffffff)
sums to 2^32 and reads nonzero, so does (0xffff, 0xffff0001), and (0x8000, 0xffff8000) reads nonzero
too.

**What it shows.** [HW] The class 9 tests apply to a 33-bit sum, not the wrapped 32-bit one, for the
tests shown: `iadd32`'s n and p read the sign of the true sum (N xor V of a signed add), and
`iaddu32`'s nonzero test includes the carry (one decisive pair). Whether z of `iadd32` or the other
`iaddu32` tests do the same is not shown. A test through source 2 of a register therefore reads that
register's bits exactly (source 1 = #0 adds nothing). A compare of two 32-bit registers is the
software formula: exact over the 64 pairs for both signednesses, and `ima32` needs no gap before its
result is read (16 of 16 padded, unsigned compare only, and 64 of 64 unpadded agree). `ima32` itself
is not testable: `ima32.u.testtaz` does not assemble [infer: the class has no test field; assembler
refusal, not a hardware run]. [infer] The `iadd32` sum needs one operand of at most 16 bits, so
`iadd32.testnat` cannot subtract two 32-bit registers; there is no one-instruction 32-bit compare.

**What it does not show.** Whether `iaddu32` zero- or sign-extends source 1: the pairs that
would tell (a source 1 above 0x7fff) read nonzero under both. The zero test of a sum that
overflows has no separating pair (testtaz of `iadd32` fits both readings in all 12), and
`testpat` and `testtaz` of `iaddu32` were not run. The `iaddu32` result rests on one decisive pair,
(1, 0xffffffff): of the other two pairs whose wrapped sum is zero, (0xffff, 0xffff0001) and (0x8000,
0xffff8000) separate the readings only if r1 is zero-extended, so they depend on Q126. Only the
twelve pairs listed were run for the overflow of `iadd32`, and only five of them separate the
readings. A signed compare was not run with padding (`compare32-slt` ran unpadded only).

**Correction, 2026-11-08 (11.25).** The measurements above are unchanged; the statements under 'What
it shows' and 'What it does not show' are corrected as follows. (1) The compare: an unsigned compare
of two 32-bit registers is two instructions on the pairs run, `ima32.u r11, i0, r2, c56, r1` and
`xor.testtanz.chan0 !c0, p0, r2, i0` (64 of 64 pairs of the same eight values, E501), through the
high word of E493; the signed compare is still the six-instruction formula, now run padded with 1, 3
and 6 nops after the `ima32` (16 pairs each, 48 of 48, E497), so 'a signed compare was not run with
padding' no longer holds, and 'ima32 itself is not testable' and 'no one-instruction 32-bit compare'
stand. (2) The sum tests: E498 ran 16 pairs (five of them with r1 below 0x8000) for `iadd32` and
`iaddu32` with the four tests: `iadd32` n and p read the true signed sum (16 of 16; the wrapped sum
fits 15, one pair separating them here and five in the twelve above), z and nz read the zero of the
sum with r1 sign-extended (16 of 16; zero-extended 11; the true and the wrapped sum cannot differ in
zero-ness), `iaddu32` p is always true and n never (16 of 16 each) and its z is true for (0, 0)
only: the sum with its carry fits 16 of 16 under either extension of r1 and the wrapped sum under
neither. So 'z of `iadd32` and testpat and testtaz of `iaddu32` were not separated' no longer holds,
and the `iaddu32` result no longer rests on one pair; whether `iaddu32` extends source 1 by zero or
sign is still not told by a test (Q126).
