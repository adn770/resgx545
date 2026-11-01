+++
id = "E526"
claim = "ima32.s r10, iK, r1, r2, r3 (the assembler accepts the .s form with the extra operand, word 0xD000024001404103 for K = 0) writes bits 63:32 of the signed 64-bit sext(a) * sext(b) + sext(c) to iK and bits 31:0 to r10: 282 of 282 jobs over the 282 triples of E525 (K = 0, 1, 2 as there); the readings 'c zero-extended' fits 142 of 282 and 'the unsigned high word' 32 of 282 (the same triples); the other two i registers kept their presets in 282 of 282"
unit = "usse"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1126 (sha256 751f7223c8c731a08d75cfc3920a5d1050488ca3bdc426be45b7c431e600f82e): probes/usse/ima32hi-signed.toml, probe usse-ima32hi-signed-s, 282 jobs, the 282 triples of usse-ima32hi-generic-u (the same seed 112702 draws and corners: the table is built by the same generator run), ima32.s in place of ima32.u; the assembler accepted ima32.s r10, i0, r1, r2, r3, so no raw word was needed; the campaign runner once, no probe.py first run; the prediction (signed operands, c sign-extended; the alternatives c zero-extended and the unsigned high word) was written before the run; recounted from the readbacks by a script outside the kit"
tiers = ["HW"]
date = "2026-11-08"
data = ["usse-ima32hi-signed"]
terms = ["Universal Scalable Shader Engine (USSE)", "REGTYPE.FPINTERNAL"]
+++

**What runs.** As E525 with ima32.s. The model: a, b and c are two's-complement 32-bit values, the
product and the sum are exact in 64 bits, r10 holds the low word and iK the high word (an arithmetic
result: iK = 0xffffffff for a negative 64-bit value that fits in 32 bits).

**Results.** 282 of 282: r10 and iK as modelled, the other i registers at their presets. The
alternatives listed with the table: c zero-extended (142 of 282: the jobs where c is nonnegative or
the result agrees) and the unsigned high word (32 of 282): both fail, so the sign extension of c and
the signed operands matter.

**What it shows.** [HW] ima32.s with the extra operand writes the signed 64-bit high word: a backend
can lower a signed mulh with an addend to it, and E528 uses it for a signed compare. c is read as
signed (sign-extended) by .s: the 140 jobs where the two readings differ all read the sign-extended
one.

**What it does not show.** .neg with the extra operand, the dual-issue form, K = 3, operands other
than registers (immediates, constants), cie or coe with the high word, and the cost. Narrows Q135
(the .s high word on generic register operands).
