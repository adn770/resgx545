+++
id = "E493"
claim = "The extra i operand of ima32, ima32.u d, iK, a, b, c (enc[38] set, iK in enc[37:36]), writes the high 32 bits of a * b + c to iK for the operands run: d = the low 32 bits and iK = bits 63:32 in 15 of 15 cases (K = 0, 1 and 2 over the five triples of unsigned `.u` register operands (3, 7, 100), (0xffffffff, 1, 1), (0xffffffff, 0xffffffff, 0xffffffff), (0x10000, 0x10000, 0) and (0x80000000, 2, 0xffffffff), the other two of i0, i1 and i2 keeping their presets 0x55, 0x66 and 0x77); the reading 'iK = the carry out of the 32-bit add' fits 6 of 15 and 'iK unchanged' 0 of 15; and eight raw ima32.u words that differ from the plain word 0xD000000001404103 outside what the assembler writes (enc[38] set with enc[37:36] = 3, enc[38] clear with enc[37:36] = 1, 2 and 3, and one of the bits 46, 45, 44 and 35 set), each over three triples (24 jobs), gave the plain result in r10 and left i0, i1 and i2 at their presets in 24 of 24, and in the 21 jobs of the words without bit 46 no other dumped register changed, but with bit 46 set r14 read 0x2255 instead of its preset 0xb0b1b2b3 in 3 of 3 jobs"
unit = "usse"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1124 (sha256 58907b06a8e9030472a809cd669d2c3823946fd67aaf4775f942704a90f6a5ae): probes/usse/ima32-forms.toml probe extra-i (dump.s, 15 cases) and probes/usse/raw25.toml probes ima32-x (12 jobs: the four selector words, three triples each) and ima32-bits (12 jobs: the four bit words, three triples each), raw `.long` words of the plain `ima32.u r10, r1, r2, r3` with the bits above changed; the raw tables ran last, in file order after the two test-field probes, with the campaign runner's baseline checked between probes and no job failed; the campaign runner once for each table, no probe.py first run. The tables' hypotheses compared r10 and r11-r13 only: the r14 word of the bit-46 jobs was found afterwards in the readback (report.txt of usse-raw25-ima32-bits), so the runner's verdict for that probe (SETTLED: the plain result and the i registers unchanged) does not mention it"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["usse-ima32-forms", "usse-raw25"]
terms = ["Universal Scalable Shader Engine (USSE)", "REGTYPE.FPINTERNAL"]
+++

**What runs.** i0, i1 and i2 are preset to 0x55, 0x66, 0x77 with `mov iN, rN`, then `ima32.u r10,
iK, r1, r2, r3` for K = 0, 1 and 2 over the five triples above, and `mov r11, i0; mov r12, i1; mov
r13, i2` after (dump.s also stores r14-r17 and r1-r8, preset 0xb0b1b2b3 and the inputs). The
assembler writes this form `ima32.u d, iK, a, b, c`; E469 to E471 never used it, and the form the
model called `coe` (`ima32 ... coe, i0`) is refused by the assembler. The raw words are the plain
word 0xD000000001404103 with (enc[38], enc[37:36]) = (1, 3) (0xD000007001404103, an `i3` the
assembler does not write), (0, 1), (0, 2) and (0, 3), and with one of the bits 46, 45, 44 and 35
set, over the triples (3, 7, 100), (0xffffffff, 0xffffffff, 0xffffffff) and (0xffffffff, 1, 1).

**Results.** Text form: r10 = (a * b + c) mod 2^32 and iK = (a * b + c) >> 32 in 15 of 15:
(0xffffffff, 1, 1) gives iK = 1, (0xffffffff, 0xffffffff, 0xffffffff) gives 0xffffffff (where the
high word and a carry of 1 differ), (0x10000, 0x10000, 0) gives 1 and (0x80000000, 2, 0xffffffff)
gives 1. 'iK = the carry out of the 32-bit sum (a * b mod 2^32) + c' fits 6 of 15 (the (3, 7, 100)
and (0xffffffff, 1, 1) triples, for each K). Raw: r10 = the plain result and r11-r13 = 0x55, 0x66,
0x77 in 24 of 24 jobs; r14-r17 and r1-r8 as they were in 21 of 21 jobs of the words without bit 46;
in the 3 jobs of the bit-46 word r14 read 0x00002255 (the same in all three triples, so not a
function of the operands) and the other dumped words were unchanged.

**What it shows.** [HW] ima32 has a second result, the high 32 bits of the product with the addend,
delivered through the extra operand for `.u` and iK in i0 to i2, for the five register triples run
(and, in E501, for b * 0xffffffff + a over eight values of b): no run has two generic multi-limb
operands, an immediate or a constant other than c56 with the high word. The carry out of a 32-bit
add is that high word when the product is the identity (`a * 1 + c`), which is the `coe` the model
hoped for, and E501 uses it for a subtract with a borrow. The raw words show for the bits and fields
run, and for r10, i0-i2 and r14-r17: the fields enc[37:36] without enc[38] and the bits 45, 44 and
35 change nothing seen; the selector 3 with enc[38] did not change i0-i2 (an i3 is not read by any
`mov` of the assembler's text: i3 reads i0 of the next instance of the quad and drops writes, so
what the high word does there is open); bit 46 changes a register (r14 = 0x2255) that the
instruction does not name: [infer] it is written by the bit, and what the bit does is open (Q135).
The bits other than those listed were not set, and only the registers listed were read.

**What it does not show.** Operands other than the five triples (generic register operands with two
multi-limb values, immediates and constants other than c56 in the high-word form), `.s` with the
extra operand (the high word of a signed product), the extra operand together with `cie` (the
assembler writes `ima32.u d, iK, a, b, c, cie, iJ`; not run), the dual-issue form, `.neg` with it,
the destination being a register other than r10, an iK that is also a source, and K = 3. Narrows
Q127: its first item (the extra i register) is answered for `.u` and its raw carry-out word for the
words run; the rest stays open (Q135).

**Correction, 2026-11-08 (11.27).** The measurements above are unchanged. E525 ran generic register
operands: `ima32.u r10, iK, r1, r2, r3` over 282 jobs (42 corner triples, among them 0x12345678 x
0x9abcdef0 with c = 0 and c = 0xffffffff, and 200 random triples, K = 0, then K = 1 and 2 over 20
random triples each) wrote bits 63:32 of the exact 64-bit a * b + c to iK in 282 of 282, the other
two i registers keeping their presets, and E526 ran `ima32.s` with the extra operand over the same
triples: the signed high word with c sign-extended, 282 of 282 (no raw word was needed). So 'the
five triples', 'no run has two generic multi-limb operands' and '`.s` with the extra operand not
run' above no longer limit the high word for register operands. Still not run: immediates and
constants other than c56 with the high word, `cie` or `.neg` with the extra operand, K = 3, the
dual-issue form, an iK that is also a source, and a destination other than r10 (Q135).
