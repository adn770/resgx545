+++
id = "E1012"
claim = "Round 11 offline (Q261, post hoc on E1005's and E979's kept rows; no run, no held-out row): none of 236 declared edge set-up arithmetics (float coefficients of 8 to 24 bits, round to nearest or toward zero, in nine arrangements; fixed-point truncation; the far vertex on 2^k grids; 32-bit wrap and saturation) draws all 48 far-vertex rows (E1005's 36 pivot rows and its control, E979's ten far rows and control) pixel for pixel (best 46 of 48; float32 11 of 48, as the exact image); written after that miss, a clip of the far edges against a guard x in [-G, 64 + G] on the 64 x 64 target, each new vertex rounded half up to 1/256 pixel and the polygon's edges then tested exactly, draws 48 of 48 rows and 318 of 318 band pixels with G = 16, and with every G from 16 to 22 (G 15 or less misses far-x24p at d = -416, G 23 or more far-x23p at d = -544; the lower bound fits anywhere from -8 to -32, the y bounds untested) [HW data, fitted post hoc; infer: it gives per-triangle displacements without D proportional to the far vertex's distance, and E979's exact image outside the band]"
unit = "isp"
method = "Offline, no run (round 11, decision R11-3 a of closing11/DECISIONS-R11.md and closing11/plan/rank-round11.md, finding 4). Data: r10-geo stage pivot's kept images (render-closing-r10-geo out/20261113-103256/pivot/, E1005's 36 rows and the control far21d0, the vertices from the session's gen/far.py and gen/pivot.py) and r9-x stage far's (render-closing-r9-x out/20261113-081821/far/, E979's ten rows and far-ctl). Check closing11/plan/c6-q261/, three freezes (FREEZE.log): round 1 q261_rule.py (sha256 4a0eaaf19c9a9c64851658c6dd9b694c558183aaf736e79c8adb186781e2d844, 2026-11-13T11:05:32Z, after E1005's intervals had been read: post hoc as a whole), 236 candidates scored by q261_score.py (q261_score.out) with the D_eff diagnostic q261_deff.py (q261_deff.out); round 2 q261_rule2.py (0997a099a36388c1465abe7d26af7403b5422af75bd3ff919c596800b233da93, written after round 1's output), 51 clip candidates (guards [-G, 64 + G] for G 2 to 4096 and [-G, G] for G 128 to 8192, interpolation exact then half up or truncated, or float32 then half up), q261_score2.py (q261_score2.out); round 3 q261_rule3.py (5424683440b720249c4ed9a5f1cbd31d8fbe7c3f7c4b5b349ab24b3b8985cdda), the scan of G from 1 to 48 and asymmetric pairs, q261_score3.py (q261_score3.out); criterion: all 4096 pixels of every row. Exact rational arithmetic (fractions), numpy only for the float32 candidates; engine_test.py checks before the freeze that the candidate 'exact' equals r10-geo far.py's coverage (vertices only). q261_heldout.py (q261_heldout.out, q261_proposals.json) names far vertices whose images part G 16 to 22, the clip from the exact image and a guard relative to the target from an absolute one, for a later row. This fold re-ran q261_score.py, q261_score2.py and q261_score3.py with python -I and got byte-identical outputs"
tiers = ["HW", "infer"]
date = "2026-11-13"
data = ["render-closing-r10-geo:out/20261113-103256/pivot/", "render-closing-r9-x:out/20261113-081821/far/", "cited-scratch:closing11/plan/c6-q261/", "cited-scratch:closing11/plan/rank-round11.md"]
terms = []
+++
**What was done.** E1005 read the band pixels of E979's far triangles (one vertex at (2^23, 2^21),
(2^24, 2^22) or (-2^25, -2^23) pixels on a 64 x 64 target) as the exact coverage of a far vertex
displaced along y by one amount per triangle (far-x24p 339 to 467 pixels, the other two above 586),
not one displacement and not one angle. The round 11 planner looked for an arithmetic that gives
those displacements from the coordinates alone and scored every candidate on all 48 kept rows:
E1005's 36, its control, E979's ten and its control. Every rule was hashed before it was scored, but
each was written after E1005's intervals were known, and rounds 2 and 3 after round 1's miss: the
whole is a post hoc fit with no held-out row.

**Round 1: set-up arithmetic (q261_score.out).** 236 declared candidates: float coefficients a, b, c
of the edge function from exact or rounded products at mantissas of 24 down to 8 bits, round to
nearest or toward zero, in nine arrangements (absolute, tile-relative at 32 and 16, edge start,
near vertex, slope forms); fixed-point truncation of c (2^16 to 2^32); the far vertex floored to a
2^k pixel grid (k 4 to 10); 32-bit wrap and saturation of the 1/256 vertex. None draws all 48. The
best (12 to 14 bit coefficients, tile-relative, slope about the near vertex) draw 46 of 48 and all
318 band pixels and miss far-x24p at d = -416 and -544, where they snap the far edge to slope 1/4
and draw exact ties by the tie rule (q261_deff.out). float32, the fixed-point and the vertex-grid
candidates draw 11 of 48 rows or fewer, as the exact image does (0 of 318 band pixels).

**Round 2: a guard-band clip (q261_score2.out).** The far edges are clipped against a guard
rectangle before set-up, each new vertex is rounded to E607's 1/256 pixel grid, and the polygon is
then tested exactly (centres strictly inside, ties to the owning edges). The far edge becomes the
line from the near vertex through the rounded clip vertex, turned by the rounding error over the
distance to it: a displacement of hundreds of pixels at 2^24. Of 51 candidates one draws all 48
rows:
the guard [-16, 64 + 16], exact intersection, half up, 318 of 318 band pixels. G 2 to 8 miss only
far-x24p at d = -416; float32 interpolation, truncation and guards about the origin do not fit.

**Round 3: the free integer (q261_score3.out).** With the same clip, a symmetric G fits for 16 to
22 (the upper bound x = 80 to 86) and no other: G 15 or less fails far-x24p at d = -416, G 23 or
more far-x23p at d = -544. Far-x25n fits every lower bound from -8 to -32. No far-y row has a band
pixel, so the y bounds are untested. 7 of 48 scanned G fit and they are contiguous.

**What it shows.** [HW data, fitted post hoc] One clip of the far edges to a guard band about 16 to
22 pixels outside the 64 x 64 target, the new vertex on the 1/256 grid, draws every kept far row
pixel for pixel, where no declared coefficient format does. [infer] It explains why the displacement
differs between triangles without growing with the distance (it is the rounding error of a clip
vertex, scaled by the far vertex's distance over the near vertex's distance to the guard), and why
the image outside the band is exact. sgx-pipe's `isp::far_coverage_image` keeps the band
undetermined: the reading is fitted.

**What it does not show.** A held-out row: q261_proposals.json names four far vertices along +x
and three along -x whose predicted images differ by one or two band pixels between G 16 and 22 and
from the exact image, and a 128 x 128 target to tell a guard of 64 + G from an absolute bound of 80
to 86. Also untested: the y bounds, whether the clip is the TA's or the ISP's, and the vertex
format past 2^25 pixels (Q199). Refuted by: a held-out row whose band pixels contradict every G in
16 to 22. E1005's "[infer] rounding of a slope or an edge coefficient" needs no correction before
such a row.
