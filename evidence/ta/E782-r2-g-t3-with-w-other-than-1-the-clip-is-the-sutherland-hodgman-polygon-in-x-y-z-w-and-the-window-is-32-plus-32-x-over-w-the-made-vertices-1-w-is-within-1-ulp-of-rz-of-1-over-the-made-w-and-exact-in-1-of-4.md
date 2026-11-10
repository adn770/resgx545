+++
id = "E782"
claim = "R2-geo stage g-t3 (4 jobs: vertex programs with z = A x + B and w = C x + D on the tool's triangle on a 64x64 target; the control z-cut-p at w = 1, the held-out t3-w-pos (z = 2x + 1, w = 0.5x + 1.25, cut by z = w at x = 1/6) and t3-w-neg (z = 2x + 1, w = -0.5x + 1.25, cut at x = 0.1) and t3-nocut (z = 0, w = 0.5x + 1.25, no clip)): the control reproduced S1b's object, and every frozen row about the clip held on both cut objects (HSH 2 of 2 on the polygon of 4 vertices cut in (x, y, z, w) against z <= w and z >= -w, the window position 32 + 32 x / w at every vertex the made ones included, HZZ the strip zigzag order, HPR the prim words (16, 1, 18) and (2, 17, 19)) and on t3-nocut (nothing crosses: 3 vertices in input order, window 32 + 32 x / w per vertex, depth word 0x3f000000 at all three, w differing between the vertices); the stored 1/w of the 7 original vertices (the two kept ones of each cut object and t3-nocut's three) equalled RZ of 1/w exactly, 7 of 7 (0x3f70f0f0, 0x3f924924, 0x3f321642 and 0x3f1d89d8, the first two again in t3-nocut with 0x3f1d89d8), but the 4 clip-made vertices' 1/w words were 0x3f400001 and 0x3f400000 (HI-w predicted 0x3f400000, RZ of 1/(4/3)) and 0x3f555554 and 0x3f555556 (predicted 0x3f555555, 1/1.2), so HI-w held within 1 ulp in 4 of 4 and exact in 1 of 4 (the frozen exact rows refuted 2 of 2 jobs), and HI-rhw (the ends' 1/w interpolated with the cut parameter: 0x3f48c8c8, 0x3f520d20, 0x3f626cc2, 0x3f6a0ea0) was refuted 2 of 2 in both its forms; the depth of the made vertices was 0x3f800000 in 3 of the 4 and 0x3f7fffff (one ulp below 1.0) at one, t3-w-neg's (34.668, 39.332), so HDP-made (1.0 exactly whatever w) was refuted 1 of 2 jobs"
unit = "ta"
method = "R2-geo stage g-t3 of the question-closing pass, round 2 (decisions R2-5, R2-12, R2-14, R2-15 and R2-17; first of the five stages, 4 jobs, templates vtx_zw.s and pix_green.s assembled on the Mac and frozen by sha256), dataset render-closing-r2-geo, on the laptop (host cedar), 2026-11-10 at 10:48 laptop time (09:48 UTC), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded), stock firmware (core 545 rev 0x1000d, DDK 1.7.17 build 862890 in the health line), tool ~/sgxfive-test-r1 (sha256 bf4f8be2d8a8fe50034559450928e05695dc96d396d4892f9b00ea6bc0d4f053, not rebuilt); each job probe --temps 8 --pixels --tri vtxuse --width 64 --height 64 --vtx-coords 2 --dump-render, all 4 of class ok (rc 0), a debugfs reset before each job; the object decoded through pbdump (vertices in stored order, packed 24-bit coordinates, depth words, prim entries, 1/w words) and scored by the frozen score/score_r2.py g-t3 (out/score-g-t3.txt), which refuses to run unless the freeze verifies; the frozen predictions come from gen/r2models.py (Sutherland-Hodgman in (x, y, z, w), the strip zigzag, window = 32 + 32 x / w, RZ of the exact reciprocal, depth 1.0 at a made vertex on the +w plane), the made 1/w by two candidates HI-w and HI-rhw each exact and within 1 ulp; the scorer's per-vertex differences and the depth words of the made and original vertices were read again from the kept dumps after the run with the same decoder (the scorer prints only the 1/w differences), and the thought that the one-ulp scatter is the rounding of the made w is an inference, not tested"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["render-closing-r2-geo:out/g-t3/"]
terms = ["PB_OBJ.RHW", "PB_OBJ.PRIM_LIST"]
+++
**What ran.** E777 held out the clip's vertex set, order and prim words at w = 1, and E754 gave the
stored 1/w inside the guard band at one w for all three vertices, truncated toward zero (RZ). T3
asks the two together: a vertex program whose w depends on x (w = 0.5x + 1.25 or -0.5x + 1.25),
so that the clip makes vertices at w other than 1 and the originals have three different w. The
control is z-cut-p of S1/S1b at w = 1; t3-nocut has no clip (z = 0) and w different at each vertex.

**Frozen verdict.** `controls pass; held out: consistent [clip (2), HSH (Sutherland-Hodgman in (x,
y, z, w), planes z <= w and z >= -w) (2), HSH (window = 32 + 32 x/w, made vertices at the cut) (2),
HZZ (strip zigzag of the SH polygon) (2), HPR (index | 16 for a boundary edge) (2), HI-w (made 1/w
= RZ of 1/w_made), within 1 ulp (2), no clip: z = 0 is inside +-w (1), HSH (nothing crosses) (1),
HPD (window = 32 + 32 x/w per vertex, input order kept) (1), HI-w (original vertices: RZ of 1/w),
exact word (1), HDP (z = 0: depth 0.5 whatever w) (1)], refuted [HI-w (made 1/w = RZ of 1/w_made),
exact word (2 of 2), HI-rhw (made 1/w = the 1/w of the ends interpolated with the edge
parameter), exact word (2 of 2), HI-rhw (made 1/w = the 1/w of the ends interpolated with the edge
parameter), within 1 ulp (2 of 2), HDP-made (z = +w / -w gives depth 1.0 / 0.0 exactly at a made
vertex, whatever w) (1 of 2)]`.
The control row passed (4 vertices, set, order, prim words and depth words of S1b's object).

**Results [HW].** The stored objects, vertices in stored order, window x, y, depth word and 1/w
word (the window values are the packed 1/256 fields):

| job | vertex | x, y | depth word | 1/w word | made |
|---|---|---|---|---|---|
| t3-w-pos | 0 | 36.0, 37.0 | 0x3f800000 | 0x3f400001 | yes |
| | 1 | 20.707, 54.590 | 0x3f1e1e1e | 0x3f70f0f0 | no |
| | 2 | 36.0, 19.5 | 0x3f800000 | 0x3f400000 | yes |
| | 3 | 4.570, 4.570 | 0x3e5b6db8 | 0x3f924924 | no |
| t3-w-neg | 0 | 34.668, 39.332 | 0x3f7fffff | 0x3f555554 | yes |
| | 1 | 23.652, 48.695 | 0x3f1642c8 | 0x3f321642 | no |
| | 2 | 34.668, 17.668 | 0x3f800000 | 0x3f555556 | yes |
| | 3 | 17.230, 17.230 | 0x3eb13b14 | 0x3f1d89d8 | no |
| t3-nocut | 0 | 4.570, 4.570 | 0x3f000000 | 0x3f924924 | no |
| | 1 | 46.770, 24.617 | 0x3f000000 | 0x3f1d89d8 | no |
| | 2 | 20.707, 54.590 | 0x3f000000 | 0x3f70f0f0 | no |

Prim entries (16, 1, 18) and (2, 17, 19) for the two four-vertex objects, (16, 17, 18) for
t3-nocut. The made vertices sit on the +w plane in both cut jobs (z = w at x = 1/6 and 0.1; the -w
plane is not reached), at the window position 32 + 32 x / w with the made w (4/3 and 1.2). The
stored 1/w minus HI-w's word, vertex by vertex in stored order: t3-w-pos +1 0 0 0, t3-w-neg -1 0
+1 0, t3-nocut 0 0 0. The made vertices' offsets are +1, 0, -1 and +1 ulp: no one-sided rounding of
the exact reciprocal of the exact made w; a made vertex of the control (0x3f800001 at w = 1,
32.0, 14.0) is the same kind of one-ulp deviation S1b saw. The kept vertices' depth words at w
other than 1 are listed and are not scored here (E783 scores them against formulas).

**What it shows and does not.** The clip is the polygon of E777 taken in homogeneous coordinates
before the divide, and the window position of every vertex, made or not, is 32 + 32 x / w with the
vertex's own w (the viewport's x offset of 32, E736's reading, with w): both are held out on two
cut objects and one uncut one. The 1/w of a kept vertex is RZ of 1/w, exact (as E754 at one w).
The made vertex's 1/w is within one ulp of RZ of the reciprocal of the made w and not equal to it
in 3 of 4 words; two of the four are a rounding of the made w away in one direction, one in the
other [infer: the made w is an interpolated float32 and the reciprocal is taken from that, so the
words would follow its rounding; the made w is not read anywhere, untested]. The hypothesis that
the 1/w is interpolated along the edge like the depth is refuted. The depth of a made vertex is 1.0
in 3 of 4 and one ulp below at one: "exactly 1.0 or 0.0" (E777 at w = 1) does not extend to w other
than 1 as a rule; no job here separates why that vertex differs. Nothing tests a made vertex on the
-w plane at w other than 1, a polygon of 3 or 5 vertices, or a w below 3e-5; those stay open (Q230).

**Correction 2026-11-10:** (R3-geo, E798 and E795; read after the run, no frozen row) "The 1/w of
a kept vertex is RZ of 1/w, exact" holds for the seven kept vertices above (w = 0.875, 1.0625,
1.4375 and 1.625) and not at every w: in g-dd's cut objects the kept vertices' 1/w was one ulp
above RZ of 1/w at w = 1.40625, 1.59375 (twice) and 1.6875 and RZ at 1.3125, 1.0625 and 1.625, and
with one w at all three vertices it was one ulp above at w = 9 and 0.7 (E795). The made vertex's
depth, 1.0 in 3 of 4 here, was exactly 1.0 on z = w and 0.0 on z = -w at all eight made vertices of
g-dd (HDP-made consistent 4 of 4 jobs, held out, E798); the vertex above at 0x3f7fffff stands. The
table and the frozen verdict above are unaffected.
