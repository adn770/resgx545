+++
id = "E528"
claim = "A signed compare built from the high word of ima32.s exists and is exact on the pairs run: ima32.s r11, i0, r2, c56, r1 (c56 = 0xffffffff, signed -1: the signed 64-bit a - b, whose high word is 0xffffffff for a < b and 0 otherwise) then xor.testtanz.chan0 !c0, p0, i0, #0 (true when i0 is nonzero) sets p0 to a < b signed in 164 of 164 pairs (the 64 pairs of the eight values 0, 1, 0xffff, 0x10000, 0x7fffffff, 0x80000000, 0x80000001, 0xffffffff, the equal pairs and the pairs across the sign boundary included, and 100 seeded random pairs; 78 with a < b signed)"
unit = "usse"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1126 (sha256 751f7223c8c731a08d75cfc3920a5d1050488ca3bdc426be45b7c431e600f82e): probes/usse/scmp.toml probe usse-scmp-ima32s, 164 jobs (the pairs: the 64 of the eight values in the order a outer, b inner, and 100 draws of Python random.Random(112702) after the draws of the triples of E525); the prediction (written before the run, as an extension of E526: if the .s high word is the signed 64-bit one this holds) was written before the run; the campaign runner once, no probe.py first run; recounted by a script outside the kit (164 of 164, corner 64 of 64, random 100 of 100)"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["usse-scmp"]
terms = ["Universal Scalable Shader Engine (USSE)", "REGTYPE.FPINTERNAL", "REGTYPE.FPCONSTANT"]
+++

**What runs.** mov i0, #0x55; ima32.s r11, i0, r2, c56, r1; xor.testtanz.chan0 !c0, p0, i0, #0; mov
r10, #0; p0 mov r10, #1; the pixel r10. The test is xor of i0 with the immediate #0 (test of a
nonzero value), assembled to 0x48091281200CBE00.

**Results.** 164 of 164 (corner 64 of 64, random 100 of 100), 78 with a < b.

**What it shows.** [HW] A signed 32-bit compare is two instructions, against the six of E472 and
E497, for the 164 pairs run. [infer] That it holds for every pair is the arithmetic of E526 (the
signed high word of b * (-1) + a is the sign of the 64-bit difference); 164 pairs do not prove it.
No padding between the two instructions was run for this form (E527 ran padding for the unsigned one
only).

**What it does not show.** Padding, the form with a register source other than c56 for the constant
-1, the dual-issue form, and the cost (not measured).
