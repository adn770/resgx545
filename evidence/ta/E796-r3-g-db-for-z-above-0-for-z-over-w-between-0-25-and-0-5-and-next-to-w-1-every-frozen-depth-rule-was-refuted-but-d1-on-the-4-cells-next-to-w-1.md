+++
id = "E796"
claim = "R3-geo stage g-db (16 held-out jobs, the triangle and template of g-da, whose controls it takes): six cells with z > 0 (z / w from 0.508 to 0.973), six with |z / w| in (0.25, 0.5) (three positive, three negative) and four with z = -0.750953436 at w next to 1 (1 + 2^-23, 1 - 2^-23, 1.5 and 1.0000004); all 16 objects were unclipped at the original position; on the z > 0 cells every frozen product rule combined with every rounding of the sum was refuted (21 labels, 2 to 4 misses of 6 each), on the q cells every label (15 with the product at float32 precision, 1 to 4 misses of 6; 4 with the product kept on the sum's 2^-23 grid, 4 or 5 misses), and on the four cells next to w = 1 D1 (the product z RZ(1/w) rounded to nearest) was consistent 4 of 4 while D2 missed 2, D5 1 and T26, T27, K23, T26d and T27d 3 each; read after the run (no frozen row), the stored 1/w was one ulp above RZ of 1/w at w = 9 (db-pos1, db-q3) and RZ of 1/w in the other 14 jobs"
unit = "ta"
method = "R3-geo stage g-db of the question-closing pass, round 3 (session L1, decision R3-G1; second of nine stages, 16 jobs, template vtx_wzclip.s), dataset render-closing-r3-geo, on the laptop (host cedar, direct cable), 2026-11-10, stage started 15:48:12 Mac time (out-l1.log), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded), stock firmware, tool ~/sgxfive-test-r1 (sha256 bf4f8be2d8a8fe50034559450928e05695dc96d396d4892f9b00ea6bc0d4f053); each job probe --temps 32 --pixels --tri vtxuse --width 64 --height 64 --dump-render, all 16 of class ok (rc 0), a debugfs reset before each job; scored by the frozen score/score_r3.py g-db (out/score-g-db.txt) with g-da's controls; the labels are the frozen product rules (D1, D5, T26, T27, T26d, T27d, K23) combined with three roundings of the sum 0.5 + 0.5 q' (to nearest even, toward zero, half up) on the z > 0 cells, the same with the product at float32 precision ('own') or kept on the sum's grid on the q cells, and the eight rules on the near-1 cells, all from gen/r3models.py; the 1/w words (printed by the scorer) were compared with RZ of 1/w after the run by scratch arithmetic in exact rationals not in the dataset"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["render-closing-r3-geo:out/g-db/"]
terms = ["PB_OBJ.RHW", "PB_OBJ.ISP_WORDS"]
+++
**What ran.** G-da tested the sign of z < 0 with z / w in (-1, -0.5], where the sum 0.5 + 0.5 q is
exact. G-db takes the depth rules where the sum rounds: z > 0 (z / w in [0.5, 1)), |z / w| in
(0.25, 0.5) of both signs, and w next to 1, each rule's word frozen per cell, keeping only cells
where the candidates differ.

**Frozen verdict (as printed, abridged).** `controls pass (g-da's); held out: consistent ['in band
(x, y scaled by w): no clip (16)', 'D1 (RN(z RZ(1/w)), the product to nearest; near-1 group)
(4)'], refuted [...]`: all 21 labels of the z > 0 group (misses of 6: D1+rn 3, D1+rz 2, D1+rh 3,
D5+rn 4, D5+rz 3, D5+rh 3, T26+rn 2, T26+rz 2, T26+rh 3, T27+rn 3, T27+rz 3, T27+rh 3, T26d+rn 3,
T26d+rz 3, T26d+rh 2, T27d+rn 2, T27d+rz 2, T27d+rh 2, K23+rn 4, K23+rz 3, K23+rh 4), all 15
'own' labels of the q group (D1+rn 3, D1+rz 1, D1+rh 3, D5+rn 1, D5+rz 1, D5+rh 2, T26+rn 3,
T26+rz 2, T26+rh 2, T27+rn 3, T27+rz 1, T27+rh 3, K23+rn 4, K23+rz 2, K23+rh 2) and the four grid
labels (D1 4, D5 4, T26 5, T27 5), and on the near-1 group D2 (2 of 4), D5 (1 of 4), T26, T27,
K23, T26d and T27d (3 of 4 each). The full line is in out/score-g-db.txt.

**Results [HW].** The stored depth word (the same at the three vertices) and the labels that give
it, as the scorer printed them:

| job | z, w | word | labels giving it |
|---|---|---|---|
| db-pos1 | 8.082, 9 | 0x3f72f1aa | D1, T26, T27, T26d, T27d with +rn and +rh |
| db-pos2 | 4.865, 5 | 0x3f7c8b43 | D1+rh, D5+rh, T26 (3), T27+rh, T26d+rh, T27d+rh, K23 (3) |
| db-pos3 | 3.335, 5 | 0x3f556041 | D1+rz, D5 (3), T26+rz, T27+rz, T26d (3), T27d (3), K23+rz |
| db-pos4 | 3.875, 5 | 0x3f633333 | 17 of the 21 |
| db-pos5 | 2.54, 5 | 0x3f410624 | D1, D5, T26, T27, T26d, T27d with +rn and +rz |
| db-pos6 | 2.6, 5 | 0x3f428f5b | D1+rz, D5+rz, T26d+rz, T27d+rz |
| db-q1 | 1.395, 5 | 0x3f23b645 | D1+rz, D5 (3), T26+rz, T27+rz, K23+rz, D1+grid, D5+grid |
| db-q2 | 2.16, 5 | 0x3f374bc6 | D1, D5, T26, T27 with +rn and +rz, K23 (3), D5+grid |
| db-q3 | 4.131, 9 | 0x3f3ac083 | D1 (3), D5+rn, D5+rh, T26 (3), T27 (3), K23+rh, D1, T26, T27 +grid |
| db-q4 | -5.313, 11 | 0x3e845a1d | D1 (3), D5 (3), T26+rh, T27 (3), K23+rz |
| db-q5 | -2.415, 5 | 0x3e845a1d | D1+rz, D5+rz, T26 (3), T27+rz, K23 (3) |
| db-q6 | -1.29, 5 | 0x3ebdf3b7 | D1+rh, D5 (3), T26+rh, T27+rh, K23+rh |
| db-near1 | -0.750953, 1 + 2^-23 | 0x3dff0618 | D1, D2, D5 |
| db-near2 | -0.750953, 1 - 2^-23 | 0x3dff0608 | D1, T26, T27, K23, T26d, T27d |
| db-near3 | -0.750953, 1.5 | 0x3e7facb2 | D1, D5 |
| db-near4 | -0.750953, 1.0000004 | 0x3dff0624 | D1, D2, D5 |

"(3)" is the rule with all three sum roundings. db-q4 and db-q5 (z / w = -0.483 at w = 11 and 5)
stored the same word. The objects were unclipped at the original position in 16 of 16.

**Read after the run [HW, no frozen row].** The stored 1/w was RZ of 1/w in 14 of the 16 jobs (w =
5, 11, 1.5 and the three w next to 1) and one ulp above it at w = 9 in both jobs that used it
(db-pos1 and db-q3: 0x3de38e39, RZ 0x3de38e38), as in g-da's three cells at w = 9 (E795). The frozen
words of every label at those two cells were computed from RZ of 1/w.

**What it shows and does not.** No frozen depth rule holds on the z > 0 or the q cells, in any
rounding of the sum; the best labels miss 1 of 6 (four 'own' labels on the q cells) or 2 of 6 (on
the z > 0 cells). D1 held, held out, on the four cells of the near-1 group (w = 1 + 2^-23, 1 -
2^-23, 1.0000004 and 1.5); every D1 label misses 1 to 4 of the 6 cells of each other group, so D1 is
not the rule at w other than 1. Two of the twelve z > 0 and q cells ran at w = 9, where the 1/w the
hardware stored is not the one the labels assumed. The depth at w other than 1 stays without a
formula and the simulator keeps refusing it (Q230).
