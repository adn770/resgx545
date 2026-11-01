+++
id = "E525"
claim = "ima32.u r10, iK, r1, r2, r3 writes bits 63:32 of the exact 64-bit a * b + c to iK and bits 31:0 to r10 on generic 32-bit register operands: 282 of 282 jobs (42 corner triples and 200 random triples with K = 0, then K = 1 and K = 2 over 20 of the random triples each), the other two i registers keeping their presets 0x55, 0x66 and 0x77 in 282 of 282; the reading 'iK = the high word of a * b alone' (no carry from c) fits 141 of 282 and 'iK = the carry out of the 32-bit sum (a * b mod 2^32) + c' fits 10 of 282"
unit = "usse"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1126 (sha256 751f7223c8c731a08d75cfc3920a5d1050488ca3bdc426be45b7c431e600f82e): probes/usse/ima32hi-generic.toml, probe usse-ima32hi-generic-u, 282 jobs (dump.s: mov i0, r5; mov i1, r6; mov i2, r7 from 0x55, 0x66, 0x77, then ima32.u r10, iK, r1, r2, r3, then mov r11, i0; mov r12, i1; mov r13, i2); the campaign runner once, no probe.py first run; the prediction was written before the run (r10 = (a * b + c) mod 2^32 and iK = (a * b + c) >> 32, the 64-bit product exact and unsigned; the alternatives listed with it: iK = the high word of a * b alone, iK = the carry out of the 32-bit sum); the 200 random triples are Python random.Random(112702) draws in the order of gen1127b.py (the seed is the record of them); the runner's verdict (SETTLED on the prediction) was recounted from the readbacks by a script outside the kit (282 of 282: low word, high word and the two other i words each 282)"
tiers = ["HW"]
date = "2026-11-08"
data = ["usse-ima32hi-generic"]
terms = ["Universal Scalable Shader Engine (USSE)", "REGTYPE.FPINTERNAL"]
+++

**What runs.** The 42 corner triples are a in (0xffffffff, 0x80000000, 0x7fffffff, 0x10000, 0xffff,
1) with b in (0xffffffff, 0x80000000, 0x10001) and c in (0, 0xffffffff) (36), then (0x12345678,
0x9abcdef0, 0), (0x12345678, 0x9abcdef0, 0xffffffff), (0, 0, 0), (0, 0xffffffff, 0x80000000),
(0x80000000, 0x80000000, 0x80000000) and (0x7fffffff, 0x7fffffff, 0x7fffffff). The 200 random
triples are three random 32-bit words each (seed 112702). K = 0 runs over all 242; K = 1 and K = 2
over the first 20 and the next 20 random triples. All operands are registers (r1 = a, r2 = b, r3 =
c); the destination is r10.

**Results.** 282 of 282 jobs: r10 = (a * b + c) mod 2^32, iK = (a * b + c) >> 32, the other two i
registers at their presets. The alternatives written with the table: iK = the high word of a * b
alone fits 141 of 282 (the jobs where adding c does not carry into bit 32), and iK = the carry out
of (a * b mod 2^32) + c fits 10 of 282 (E493 excluded it for one triple). The runner's verdict is
SETTLED on the prediction alone.

**What it shows.** [HW] The high word of ima32.u is the high 32 bits of the full 64-bit a * b + c on
generic register operands, with two multi-limb operands (0x12345678 * 0x9abcdef0) and 200 random
triples, not only the six operand classes of E493 and E501. E493's five triples and E501's b *
0xffffffff + a are now two cases of many. A backend may lower an unsigned 32 x 32 + 32 high-word
multiply (umulh with an addend) to ima32.u d, iK, a, b, c for register operands.

**What it does not show.** Operands that are immediates or constants other than c56 with the high
word, a destination other than r10, an iK that is also a source, K = 3, the extra operand with cie,
.neg or the dual-issue form, and the timing or cost of the instruction. The random triples are
32-bit uniform draws: the corners listed are all the structured cases. Narrows Q135 (the .u high
word on generic operands is shown).
