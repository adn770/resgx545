+++
id = "E783"
claim = "R2-geo stage g-t4 (8 jobs: the tool's triangle with x and y scaled by w so that the window position is the original (8, 8), (56, 20), (20, 56) of a 64x64 target, z the same at all three vertices, z within +-w so that nothing clips; 2 controls t4-ctl-z0-w3 (z = 0, w = 3: depth word 0x3f000000, 1/w 0x3eaaaaaa as E754) and t4-ctl-zm05-w1 (z = -0.5, w = 1: 0x3e800000), and 6 held-out (z, w) pairs): both controls passed; the object was written unclipped at the original position (6 of 6) and the stored 1/w was RZ of 1/w in 6 of 6 pairs (0x3eaaaaaa at w = 3, 0x3e124924 at 7, 0x43a6aaaa at 0.003, 0x3f68ba2e at 1.1; RN refuted 5 of 5 where it differs), but each of the six frozen depth formulas was refuted by at least one pair (D1 0.5 + 0.5 (z RZ(1/w)) rounded to nearest by 1 of 6, D2 0.5 + 0.5 RZ(z/w) by 1 of 6, D3 0.5 + 0.5 RN(z/w) by 5 of 6, D5 0.5 + 0.5 RZ(z RZ(1/w)) by 4 of 6, D6 RN(RN(z + w) / (2 w)) by 6 of 6, D7 by 5 of 6); the measured depth word (the same at the three vertices of a job) was 0x3e19999c for (-2.1, 3), 0x3d88888c for (-2.6, 3), 0x3df8af8c for (-5.3, 7), 0x3d4cccd0 for (-0.0027, 0.003), 0x3dfb5874 for (-0.83, 1.1) and 0x3d83a840 for (-6.1, 7), each above the exact 0.5 + 0.5 z / w by 0.27 to 0.57 of 2^-24"
unit = "ta"
method = "R2-geo stage g-t4 of the question-closing pass, round 2 (the second of five stages, 8 jobs, templates vtx_wzclip.s and pix_green.s, R1's simulator-checked templates unchanged), dataset render-closing-r2-geo, on the laptop (host cedar), 2026-11-10 at 10:48:59 laptop time (09:48 UTC), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded), stock firmware, tool ~/sgxfive-test-r1 (sha256 bf4f8be2d8a8fe50034559450928e05695dc96d396d4892f9b00ea6bc0d4f053); each job probe --temps 8 --pixels --tri vtxuse --width 64 --height 64 --vtx-coords 2 --dump-render with a vertex program built for the pair (z and w as the vertex program's constants, x and y multiplied by w), all 8 of class ok (rc 0), a debugfs reset before each job; the object decoded through pbdump and scored by the frozen score/score_r2.py g-t4 (out/score-g-t4.txt); the frozen candidates D1 to D7 come from gen/r2models.py (exact float32 rounding), the six pairs were chosen so that every pair of candidates differs in at least one of them; the offsets in units of 2^-24 and the search for another formula were made after the run from the kept words (arithmetic on the six words with exact fractions, not a test): 768 combinations of the rounding modes RN, RZ, RU and RD at the reciprocal, the product, the sum and the halving, in three orders of the operations, none fits 6 of 6 and the best fit 5 of 6"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["render-closing-r2-geo:out/g-t4/"]
terms = ["PB_OBJ.RHW", "PB_OBJ.ISP_WORDS"]
+++
**What ran.** E754 measured the stored 1/w at w = 3, 7, 0.003 and 3e-5 with z = 0 and did not score
the depth at w other than 1. T4 gives the vertex program a z other than 0 at the same w, so the
depth word, stored as 0.5 + 0.5 z / w if the divide is the viewport's, carries the divide's
rounding. Six pairs (z, w) were frozen against six formulas.

**Frozen verdict.** `controls pass; held out: consistent [in band (x, y scaled by w): no clip (6),
in band (6), RZ (1/w = RZ of 1/W: E754 in band 7 of 7) (6)], refuted [D1 (0.5 + 0.5 (Z * RZ(1/W)),
the product rounded to nearest) (1 of 6), D2 (0.5 + 0.5 RZ(Z/W)) (1 of 6), D3 (0.5 + 0.5 RN(Z/W))
(5 of 6), D5 (0.5 + 0.5 RZ(Z * RZ(1/W))) (4 of 6), D6 (RN(RN(Z + W) / (2 W))) (6 of 6), D7 (0.5 +
0.5 (Z * RN(1/W)), the product rounded to nearest) (5 of 6), RN (1/w = RN of 1/W) (5 of 5)]`. The
stage's own reading of the candidates is "the candidate right in 6 of 6, or none with the words
recorded": none, so the words are the result.

**Results [HW].** Per pair, the stored depth word (the same at all three vertices), the 1/w word
and the candidates whose prediction equals the word:

| (z, w) | depth word | 1/w word | candidates equal to it |
|---|---|---|---|
| (0, 3) control | 0x3f000000 | 0x3eaaaaaa | as frozen |
| (-0.5, 1) control | 0x3e800000 | 0x3f800000 | as frozen |
| (-2.1, 3) | 0x3e19999c | 0x3eaaaaaa | D1, D2 |
| (-2.6, 3) | 0x3d88888c | 0x3eaaaaaa | D2, D3 |
| (-5.3, 7) | 0x3df8af8c | 0x3e124924 | D1, D2 |
| (-0.0027, 0.003) | 0x3d4cccd0 | 0x43a6aaaa | D1, D2 |
| (-0.83, 1.1) | 0x3dfb5874 | 0x3f68ba2e | D1, D2, D5, D7 |
| (-6.1, 7) | 0x3d83a840 | 0x3e124924 | D1, D5 |

The six objects were unclipped triangles at the original window position (8, 8), (56, 20), (20, 56)
with the prim entry (16, 17, 18). D1 and D2 each fit five of the six pairs, D1 failing (-2.6, 3)
and D2 failing (-6.1, 7); no candidate fits all six.

**Read after the run [infer; a fit, no held-out row].** The six words are all above the exact value
0.5 + 0.5 z / w (computed on the float32 values of z and w): by 0.33, 0.33, 0.36, 0.33, 0.27 and
0.57 of 2^-24 for the pairs in table order. The six z / w lie in (-1, -0.5], where 0.5 + 0.5 q is
exact (the frozen note of the table: Sterbenz), so the word is a function of the stored q alone,
and q is then above its exact value, toward zero, by 0.67, 0.67, 0.71, 0.66, 0.54 and 1.14 ulp of
q (2^-24 there): a single correctly rounded operation is off by at most 0.5 (to nearest) or less
than 1 (toward zero), so the sixth pair needs at least two roundings. A search over 768
combinations of rounding modes (to nearest, toward zero, up, down) at the reciprocal, the product,
the sum and the halving, in three orders, found no formula giving all six words (the best gave 5
of 6, the forms D1 and D2 are among them), so no model of the depth at w other than 1 is offered.
The stored depth at w = 1 is 0.5 + 0.5 z exactly (E777) and at z = 0 it is 0.5 whatever w (the
control and t3-nocut of E782).

**What it shows and does not.** Inside the guard band the 1/w is the float32 reciprocal truncated
toward zero at six more (z, w) pairs, now with z other than 0, as E754 found at z = 0 (round to
nearest refuted). The depth at w other than 1 is not 0.5 + 0.5 z / w rounded in any of the six
frozen ways; its words are recorded here for a later fit, and the simulator keeps refusing the depth
at w other than 1 (Q230). What a fit still needs: pairs with w near 1 and with z of both signs, to
see where the stored word and the exact value part, and the made vertex of E782, whose depth was
1.0 in 3 of 4 and one ulp below at one.

**Correction 2026-11-10:** (an offline fit on the six words above, made before the round 3 runs; not a new
measurement; post hoc fit, no held-out row). Each stored word is 0.5 + 0.5 q' with q' a float32, and
q' is the float below or above |p| = |z * RZ(1/w)| (the stored 1/w is the RZ value in all six
pairs). Round to nearest of p misses one pair only (-2.6, 3), where the fraction of |p| in its ulp
is 0.467 and the hardware went up. One family fits 6 of 6: round |p| up when its fraction exceeds t,
t in (0.3655, 0.4667) (the fractions of the six pairs in table order are 0.967 up, 0.467 up, 0.957
up, 0.870 up, 0.365 down, 0.271 down). Of 257 models in five families declared before the fit (the
four frozen formulas, an internal reciprocal of 24 to 32 bits, double rounding of the product at 25
to 29 bits, an operand cut to 12 to 23 bits, a threshold grid), 13 fit 6 of 6, all of this one
family (plus one operand-cut model), and 69 fit 5 of 6, D1 and D2 among them. Degrees of freedom:
each word chooses one of two neighbours of p, so six words carry at most 6 bits and five of them are
what round to nearest already gives; the fit rests on one word, (-2.6, 3) (t4-m2p6-3), and about 4
of 257 models fit 6 of 6 by chance alone (257 / 2^6). It is a hypothesis for a held-out run, not a
finding, and the simulator keeps refusing the depth at w other than 1.

**Correction 2026-11-10:** (arithmetic on the six words above, in exact fractions) the offsets of
the second pair, (-2.6, 3), word 0x3d88888c, are given in the "Read after the run" paragraph as 0.33
of 2^-24 above the exact value and 0.67 ulp of q. The exact values are 0.17 of 2^-24 and 0.33 ulp of
q (q = -0.8667 lies in [0.5, 1), ulp 2^-24, and the word is 0.5 + 0.5 q, so the word's offset is
half of q's). The other five pairs agree with the paragraph (0.33, 0.36, 0.33, 0.27, 0.57 of 2^-24;
0.67, 0.71, 0.66, 0.54, 1.14 ulp of q). The table of words and the verdict are unaffected.

**Correction 2026-11-10:** (R3-geo, E795 and E796; held out) The first correction above, the post
hoc fit made before round 3, does not hold. Its threshold family (round |p| away from zero iff its
fraction exceeds one t in (0.3655, 0.4667)) was frozen as H-thr and refuted on 21 held-out cells:
5 of the 11 outside cells were off its direction (E795). The word it rested on, t4-m2p6-3's
0x3d88888c, repeated. D1, D2, D5, T26, T27 and K23 were refuted there too, and on g-db's cells with
z > 0 and |z / w| in (0.25, 0.5) every frozen rule, while D1 held on the four cells next to w = 1
(E796). The statement "inside the guard band the 1/w is the float32 reciprocal truncated toward
zero" holds for the w of the six pairs above and not at every w: the stored 1/w was one ulp above
RZ of 1/w at w = 9 and 0.7 (E795, E796; read after the run). The words and the verdict above are
unaffected.
