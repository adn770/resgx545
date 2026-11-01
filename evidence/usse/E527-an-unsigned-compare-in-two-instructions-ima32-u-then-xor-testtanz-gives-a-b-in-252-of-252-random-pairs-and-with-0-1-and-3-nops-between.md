+++
id = "E527"
claim = "The two-instruction unsigned compare of E501, ima32.u r11, i0, r2, c56, r1 then xor.testtanz.chan0 !c0, p0, r2, i0, sets p0 to a < b unsigned in 252 of 252 seeded pairs (200 random, 20 equal, 12 differing in one bit at the positions 0, 8, 15, 16, 24 and 31 in both orders, 10 with equal low half and 10 with equal high half; 127 with a < b), and with 0, 1 and 3 nops between the two instructions over 48 of those pairs each (24 random, 8 equal, 8 with equal low half, 8 with equal high half; 21 with a < b): 48 of 48 for each of the three paddings"
unit = "usse"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1126 (sha256 751f7223c8c731a08d75cfc3920a5d1050488ca3bdc426be45b7c431e600f82e): probes/usse/ucmp2-random.toml probe usse-ucmp2-random-pairs (252 jobs) and probes/usse/ucmp2-pad.toml probes usse-ucmp2-pad-0, -1 and -3 (48 jobs each); the pairs are draws of Python random.Random(112703) (the random, equal and same-half kinds) and of the same generator for the single-bit pairs; the prediction (p0 = [a < b] unsigned in every job) was written before the run; the campaign runner once for each table, no probe.py first run; recounted from the readbacks by a script outside the kit (252, 48, 48, 48)"
tiers = ["HW"]
date = "2026-11-08"
data = ["usse-ucmp2-random", "usse-ucmp2-pad"]
terms = ["Universal Scalable Shader Engine (USSE)", "REGTYPE.FPINTERNAL", "REGTYPE.FPCONSTANT"]
+++

**What runs.** mov i0, #0x55; ima32.u r11, i0, r2, c56, r1; [nop x n]; xor.testtanz.chan0 !c0, p0,
r2, i0; mov r10, #0; p0 mov r10, #1 with r1 = a and r2 = b; the pixel r10 is read. The pair kinds
are in the labels of the report ("random", "equal", "bitK", "same-low", "same-high"). The padded
table runs 48 of the pairs with n = 0, 1 and 3 in three probes.

**Results.** 252 of 252 (random 200 of 200, equal 20 of 20, bit pairs 12 of 12, same-low 10 of 10,
same-high 10 of 10); padded 48 of 48 for n = 0, for n = 1 and for n = 3, each with 21 pairs where a
< b.

**What it shows.** [HW] E501's two-instruction unsigned compare is exact on random pairs and on the
pairs that differ only in the high or the low half or in one bit, and needs no gap after the ima32
for the three paddings run, as the six instruction signed compare of E497. It rests on the high word
of b * 0xffffffff + a, which E525 shows for generic operands: the compare is no longer resting on
the eight values of E501.

**What it does not show.** Paddings other than 0, 1 and 3 (E497 ran 1, 3 and 6 for the signed
compare), i1 and i2 in the compare, the dual-issue form, the compare when the second instruction
reads a register written by a third instruction in the gap, and the cost of the form. Narrows
nothing of Q127 beyond E501.
