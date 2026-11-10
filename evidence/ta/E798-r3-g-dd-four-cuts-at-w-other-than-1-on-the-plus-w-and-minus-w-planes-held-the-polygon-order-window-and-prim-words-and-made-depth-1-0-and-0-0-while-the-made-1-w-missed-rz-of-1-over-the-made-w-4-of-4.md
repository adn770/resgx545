+++
id = "E798"
claim = "R3-geo stage g-dd (4 held-out jobs: the tool's triangle on a 64x64 target with z = A x + B and w = C x + D, one vertex beyond a plane; dd-p1 and dd-p2 cut by z = w with made w 11/7 and 13/9, dd-m1 and dd-m2 cut by z = -w with made w 1.05 and 47/28): the structure (4 vertices, the vertex set, the stored order and the prim words) held in 4 of 4 jobs, and HSH (the Sutherland-Hodgman polygon in (x, y, z, w) against z <= w and z >= -w), its window rule (32 + 32 x / w, made vertices at the cut), HZZ (the strip zigzag order), HPR (index | 16 for a boundary edge: (16, 1, 18), (2, 17, 19)) and HDP-made (depth exactly 1.0 at a made vertex on z = w and 0.0 on z = -w, whatever w) were consistent in 4 of 4; HI-w (the made vertex's 1/w = RZ of 1/w_made) was refuted as an exact word (4 of 4) and within 1 ulp (3 of 4): the made 1/w words were 0x3f22e8bb and 0x3f22e8bc (dd-p1), 0x3f313b15 and 0x3f313b14 (dd-p2), 0x3f73cf3f twice (dd-m1) and 0x3f1882ba twice (dd-m2); read after the run (no frozen row), the kept vertices' 1/w was RZ of 1/w at w = 1.3125, 1.0625 and 1.625 and one ulp above it at w = 1.40625, 1.59375 (twice) and 1.6875"
unit = "ta"
method = "R3-geo stage g-dd of the question-closing pass, round 3 (session L1, decision R3-G1; fourth of nine stages, 4 jobs, R1's template vtx_zw.s with the constants A, B, C and D, and pix_green.s), dataset render-closing-r3-geo, on the laptop (host cedar, direct cable), 2026-11-10, stage started 15:50:44 Mac time (out-l1.log), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded), stock firmware, tool ~/sgxfive-test-r1 (sha256 bf4f8be2d8a8fe50034559450928e05695dc96d396d4892f9b00ea6bc0d4f053); each job probe --temps 8 --pixels --tri vtxuse --width 64 --height 64 --vtx-coords 2 --dump-render with --slot pixel=pix_green.bin, all 4 of class ok (rc 0), a debugfs reset before each job; the object decoded by the session's decoder over the landed pbdump and scored by the frozen score/score_r3.py g-dd (out/score-g-dd.txt) against gen/r2models.py's predictions (exact rationals); the stage has no control job, its structure rows are the control (PREFLIGHT); the per-vertex window positions, depth words and kept vertices' 1/w words were read after the run with the same decoder, and the offsets of the 1/w words from RZ of 1/w computed by scratch arithmetic in exact rationals not in the dataset"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["render-closing-r3-geo:out/g-dd/"]
terms = ["PB_OBJ.RHW", "PB_OBJ.PRIM_LIST", "PB_OBJ.ISP_WORDS"]
+++
**What ran.** E782 held the cut polygon, its order, the window rule and the prim words on two cuts
by the +w plane at w other than 1, found the made vertex's 1/w within 1 ulp of RZ of 1/w_made and
exact in 1 of 4, and its depth 1.0 in 3 of 4 made vertices (one at 0x3f7fffff). G-dd repeats the
frozen rows on two more +w cuts and on the -w plane, which no job had cut at w other than 1.

**Frozen verdict (as printed).** `structure (the control) holds in 4 of 4 jobs; held out:
consistent ['clip (4)', 'HSH (Sutherland-Hodgman in (x, y, z, w), planes z <= w and z >= -w) (4)',
'HSH (window = 32 + 32 x/w, made vertices at the cut) (4)', 'HZZ (strip zigzag of the SH polygon)
(4)', 'HPR (index | 16 for a boundary edge) (4)', 'HDP-made (z = +w / -w gives depth 1.0 / 0.0
exactly at a made vertex, whatever w) (4)'], refuted ['HI-w (made 1/w = RZ of 1/w_made), exact word
(4 of 4)', 'HI-w (made 1/w = RZ of 1/w_made), within 1 ulp (3 of 4)']; repeat only: consistent
none, refuted none; made depth exactly 1.0 / 0.0 in 4 of 4 readable jobs (E782 refuted it at 1 of
4 vertices)`.

**Results [HW].** The stored objects, vertices in stored order (window x, y from the packed 1/256
fields; made = a vertex the clip made); prim entries (16, 1, 18) and (2, 17, 19) in all four:

| job | vertex | x, y | depth word | 1/w word | made |
|---|---|---|---|---|---|
| dd-p1 (z = 2x + 1, w = 0.25x + 1.5) | 0 | 37.816, 33.816 | 0x3f800000 | 0x3f22e8bb | yes |
| | 1 | 23.465, 49.066 | 0x3f16c16c | 0x3f360b61 | no |
| | 2 | 37.816, 22.000 | 0x3f800000 | 0x3f22e8bc | yes |
| | 3 | 13.715, 13.715 | 0x3e9e79e8 | 0x3f430c30 | no |
| dd-p2 (z = 2x + 1, w = -0.25x + 1.5) | 0 | 36.922, 35.383 | 0x3f800000 | 0x3f313b15 | yes |
| | 1 | 24.469, 47.059 | 0x3f141414 | 0x3f20a0a1 | no |
| | 2 | 36.922, 20.770 | 0x3f800000 | 0x3f313b14 | yes |
| | 3 | 17.777, 17.777 | 0x3eb425ed | 0x3f17b426 | no |
| dd-m1 (z = 2x - 0.25, w = 0.5x + 1.25) | 0 | 46.770, 24.617 | 0x3f627627 | 0x3f1d89d8 | no |
| | 1 | 20.707, 54.590 | 0x3cf0f100 | 0x3f70f0f0 | no |
| | 2 | 19.809, 11.809 | 0x00000000 | 0x3f73cf3f | yes |
| | 3 | 19.809, 51.809 | 0x00000000 | 0x3f73cf3f | yes |
| dd-m2 (z = 2x - 0.25, w = -0.25x + 1.5) | 0 | 50.285, 22.855 | 0x3f79e79e | 0x3f430c30 | no |
| | 1 | 24.469, 47.059 | 0x3e3ebebe | 0x3f20a0a1 | no |
| | 2 | 18.383, 17.871 | 0x00000000 | 0x3f1882ba | yes |
| | 3 | 18.383, 20.426 | 0x00000000 | 0x3f1882ba | yes |

On the +w plane the made vertices are stored at positions 0 and 2, as in E782; on the -w plane at
2 and 3, as the zigzag of the polygon gives.

**Read after the run [infer: arithmetic in exact rationals, no frozen row].** The made vertices' 1/w
words lie above RZ of 1/w_made by +1 and +2 ulp (dd-p1), +2 and +1 (dd-p2), +3 and +3 (dd-m1) and
+1 and +1 (dd-m2), all above it (E782: +1, 0, -1, +1). The kept vertices' 1/w was RZ of 1/w at w =
1.3125 (dd-p1 vertex 3, dd-m2 vertex 0), 1.625 and 1.0625 (dd-m1) and one ulp above it at w =
1.40625 (dd-p1 vertex 1), 1.59375 (dd-p2 and dd-m2 vertex 1) and 1.6875 (dd-p2 vertex 3).

**What it shows and does not.** The cut at w other than 1 is the Sutherland-Hodgman polygon in
homogeneous coordinates on both planes now, stored in the strip zigzag order with E777's prim words
and every vertex at 32 + 32 x / w of its own w (held out on four more objects, two of them on the -w
plane). The made vertex's depth was exactly 1.0 on z = w and 0.0 on z = -w in all eight made
vertices here; with E782's one vertex at 0x3f7fffff that is 11 of 12 made vertices over the two
sessions [arithmetic], so it is not a rule without exception. The made 1/w is not RZ of 1/w_made
(exact 0 of 8 words here) and no rule for it is offered. The kept vertices' 1/w is not RZ of 1/w at
every w either: E782's seven kept vertices were, four of eight here are one ulp above (with g-da's
w = 9 and 0.7, E795). Polygons of 3 or 5 or more vertices at w other than 1 did not run (Q230).
