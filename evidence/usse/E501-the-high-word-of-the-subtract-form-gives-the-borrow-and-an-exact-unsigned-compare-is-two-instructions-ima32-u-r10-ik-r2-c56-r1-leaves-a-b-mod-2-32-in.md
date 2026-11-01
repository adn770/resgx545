+++
id = "E501"
claim = "The high word of the subtract form gives the borrow, and an exact unsigned compare is two instructions on the pairs run: ima32.u r10, iK, r2, c56, r1 leaves a - b mod 2^32 in r10 and b - [a < b] in iK (75 of 75 cases: K = 0 over the 49 pairs of the seven values 0, 1, 0xffff, 0x10000, 0x7fffffff, 0x80000000 and 0xffffffff, K = 1 and K = 2 over the same 13 pairs, the other two i registers keeping their presets 0x55, 0x66 and 0x77; as E493's high word predicts, b * 0xffffffff + a = (b - 1) * 2^32 + (2^32 - b + a) for a < b), so ima32.u r11, i0, r2, c56, r1 followed by xor.testtanz.chan0 !c0, p0, r2, i0 sets p0 to a < b unsigned in 64 of 64 pairs (unsigned only, not padded, with r11 as the destination and the sources r1 and r2 as a and b: all pairs of the eight values 0, 1, 0xffff, 0x10000, 0x7fffffff, 0x80000000, 0x80000001 and 0xffffffff, 28 of them with a < b, the equal pairs and the pairs across the sign boundary included), where E472's formula takes six instructions and was run on the 64 pairs of those eight values; the high word was run for b * 0xffffffff + a only (its source 2 is c56 = 0xffffffff in all 75 cases)"
unit = "usse"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1124 (sha256 58907b06a8e9030472a809cd669d2c3823946fd67aaf4775f942704a90f6a5ae): probes/usse/ima32hi.toml (dump.s, 75 cases) and probes/usse/ucmp2.toml (64 cases, i0 only); both are predictions written from E493 before the runs; the campaign runner once for each table, no probe.py first run; the two tables were recounted from the readbacks (75 of 75 and 64 of 64)"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["usse-ima32hi", "usse-ucmp2"]
terms = ["Universal Scalable Shader Engine (USSE)", "REGTYPE.FPINTERNAL", "REGTYPE.FPCONSTANT"]
+++

**What runs.** `mov i0, r5; mov i1, r6; mov i2, r7` (0x55, 0x66, 0x77), then `ima32.u r10, iK, r2,
c56, r1` with r1 = a and r2 = b and `mov r11, i0; mov r12, i1; mov r13, i2`; the prediction was r10
= (a - b) mod 2^32 and iK = (b - [a < b]) mod 2^32, the others unchanged (the alternative 'iK = the
borrow alone' fits less). ima32hi: K = 0 over all 49 pairs of the seven values; K = 1 and K = 2 over
the 13 pairs (0, 0), (0, 1), (0, 0xffff), (0, 0xffffffff), (1, 0), (0xffff, 0), (0xffff, 0xffff),
(0xffff, 0xffffffff), (0x7fffffff, 0x80000000), (0x80000000, 0x7fffffff), (0xffffffff, 0),
(0xffffffff, 0xffff) and (0xffffffff, 0xffffffff). The compare table runs `mov i0, #0x55; ima32.u
r11, i0, r2, c56, r1; xor.testtanz.chan0 !c0, p0, r2, i0; mov r10, #0; p0 mov r10, #1` over the 64
pairs of the eight values.

**Results.** ima32hi: the prediction fits 75 of 75 (the runner's verdict: SETTLED on it alone).
ucmp2: r10 = [a < b] in 64 of 64 cases, 28 with a < b and 36 without.

**What it shows.** [HW] The carry out that the model hoped to find in `ima32` is the high word
through the extra operand, and a borrow follows from it in one more instruction: a < b unsigned is
`ima32.u t, i0, b, c56, a; xor.testtanz p, b, i0` for the pairs run (two instructions against six,
E472). [infer] That `b xor (b - [a < b])` is nonzero exactly when a < b is the arithmetic of the
high word of b * 0xffffffff + a, shown for the eight values of b run (75 of 75 cases); the other
pairs follow only if that high word is exact for them, which was not run. [infer] The signed compare
is not given by this: the high word of `.s` was not run (Q135).

**What it does not show.** Pairs other than those listed (no pair with a value outside the eight,
and no random pair; the high word of b * 0xffffffff + a for a b outside the eight, and of any other
product, was not run), i1 and i2 in the compare (they were run for the high word only), the
dual-issue form, padding between the two instructions (E497 padded the six-instruction signed
compare only), what the instruction costs (a fill's timing was not measured), and the signed
compare. Narrows Q127 (the extra operand) with E493.
