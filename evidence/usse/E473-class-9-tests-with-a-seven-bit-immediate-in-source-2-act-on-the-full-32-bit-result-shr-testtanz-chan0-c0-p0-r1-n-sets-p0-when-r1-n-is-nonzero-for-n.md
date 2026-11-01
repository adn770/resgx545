+++
id = "E473"
claim = "Class 9 tests with a seven-bit immediate in source 2 act on the full 32-bit result: shr.testtanz.chan0 !c0, p0, r1, #n sets p0 when r1 >> n is nonzero, for n in 0, 1, 3, 7, 15, 16, 31, 32, 33 and 127, with n of 32 and over giving a result of zero (80 of 80 cases over eight values of r1; reading n mod 32 fits 64), xor.testtaz.chan0 !c0, p0, r1, #n sets p0 when all 32 bits of r1 ^ n are zero (18 of 18 cases for n of 0, 7 and 127 including r1 = 0x10000 and 0x80000000; looking at the low 16 bits only fits 11), and and, or, xor and rol with testtanz and asr and shl with testnat test their 32-bit result (48 of 48); the assembler refuses ~ in the three test forms tried (and.testtanz with ~#7 and with ~r2, xor.testtaz with ~#7), while and r10, r1, ~#7 assembles; or, rol and xor with ~r2 in a test were not tried, and no raw word was run"
unit = "usse"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1122 (sha256 ec423efc3d9aa34576553da70916be4ceb715a729cbc02cc4bd89fa052511244): probes/usse/compare32.toml, probes compare32-shr-imm (80 cases), compare32-xor-imm (18) and compare32-other-imm (48), each case `<op>.chan0 !c0, p0, r1, #n`, `mov r10, #0`, `p0 mov r10, #1`; two runs of each (probe.py outside the data, the campaign runner the dataset, the same readback in all 146 cases); the refusals are those of tools/usse-asm at 8665d77, unchanged since 1c90a19 (28 of the 61 one-line forms tried for E469 to E476 are refused), not hardware runs"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["usse-compare32"]
terms = ["Universal Scalable Shader Engine (USSE)"]
+++

**What runs.** `shr.testtanz.chan0 !c0, p0, r1, #n` over n in {0, 1, 3, 7, 15, 16, 31, 32, 33, 127}
and r1 in {0, 1, 0xffff, 0x10000, 0x7fffffff, 0x80000000, 0x80000001, 0xffffffff} (80 cases);
`xor.testtaz.chan0 !c0, p0, r1, #n` over n in {0, 7, 127} and r1 in {0, 1, 6, 7, 0x7e, 0x7f,
0x10000, 0x10007, 0x1007f, 0x80000000, 0x80000007, 0x8000007f, 0xffffffff} (18 cases, the values
chosen next to n); and/or/xor `testtanz` with #7, #0, #1, `rol.testtanz` #1, `asr.testnat` #31 and
`shl.testnat` #1, eight values each (48 cases).

**Results (campaign run).** shr: 80 of 80 for `(r1 >> n) != 0`, with n = 32, 33 and 127 giving
p0 clear for every r1 (including 0xffffffff), which agrees with HW 7.8's "a shift by 32 or more
gives 0"; xor: 18 of 18 for `(r1 ^ n) == 0`; the others 48 of 48 for the test of the 32-bit result
(for example `shl.testnat #1` of 0x80000001 is clear because the result 0x00000002 is positive,
`asr.testnat #31` of 0x80000000 is set).

**What it shows.** [HW] The two discarded-result tests a compiler needs, `shr.testtanz.chan0 !c0,
p0, r, #n` and `xor.testtaz.chan0 !c0, p0, r, #n`, work as it expects on 32 bits, and so do the
other bitwise and shift tests with an immediate that had no hardware run. [infer] `and.testtanz ...
~#7` is refused by the assembler, and so are `and.testtanz ... ~r2` and `xor.testtaz ... ~#7` (the
three forms tried), while `and r10, r1, ~#7` and `and r10, r1, ~r2` assemble; that this is an
encoding limit and not an assembler gap is a guess: the test forms use enc[43:42] for the sign test,
where the bitwise group keeps its invert bit. An immediate in a test is seven bits (`#128` refused
by the assembler, also [infer]). To test `x & ~mask`, a compiler computes the inverted value first
(`and r11, r1, ~#7`, then a test of r11).

**What it does not show.** The encoding claim is not a hardware result: no word with the invert bit
set in a test was run (a raw word of the E474 kind would settle it; not run), and `~` was not tried
in `or`, `rol` or `xor ~r2` test forms. Tests with an immediate on 8-bit or 16-bit lane operations,
and with `chan1` to `chan3`, are not run here.

**Correction, 2026-11-08 (11.25).** The measurements above are unchanged. The encoding statement is
now a hardware result for the forms run: E499 ran raw words of the sixteen class 9 test words
(`and`, `or`, `xor` and `rol`, with r2 or #7, testtaz and testtanz) and the same words with bit 43
set, the bit that `~` sets in `and r10, r1, ~r2`. Bit 43 of a test word is the pat bit of the test
field enc[43:40] (taz 1, tanz 2, nat 4, pat 8, not enc[43:42] alone): with it set the test reads the
plain condition ANDed with pat (96 of 96), and it does not invert source 2 (that fits 53 of 96). So
the test words have no invert bit, and the assembler's refusal of `~` in a test fits that; 'no word
with the invert bit set was run' no longer holds, and '`or`, `rol` and `xor ~r2` were not tried'
holds for the text forms only: the raw words ran for all four operations, while the text forms `or`,
`rol` and `xor` with `~` were still not tried. That no other bit of a test word inverts a source was
not run, and the rule was read out of the data (E499 states which counts are predictions).
