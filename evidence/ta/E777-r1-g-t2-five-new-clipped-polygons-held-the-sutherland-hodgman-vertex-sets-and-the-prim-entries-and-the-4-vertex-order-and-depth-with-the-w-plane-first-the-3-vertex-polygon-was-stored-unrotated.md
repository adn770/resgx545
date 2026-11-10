+++
id = "E777"
claim = "R1-pixgeo stage g-t2 (7 jobs: vertex programs with z = A x + B or A y + B on the tool's triangle, w = 1, both controls passing, E651's z-flat099 object and the 4-vertex z-cut-p object of S1b): the objects of the five clipped polygons (z-cut-p05, z-slab, z-cut-ym, z-cut-m-slope and the replicate z-cut-p-r2) were written as clipped polygons (clip 5 of 5), their vertex sets equalled the Sutherland-Hodgman polygon over the edges A to B, B to C, C to A in 5 of 5 (nvert and set, HSH 10 of 10 rows) and their prim lists were the strip triangles with entry = stored index | 16 for a boundary edge in 5 of 5 (HPR, (16, 1, 18) and (2, 17, 19) for 4 vertices, (16, 17, 18) for 3); the stored order and depth words (0.5 + 0.5 z at every vertex, the clip-made ones 0 or 1) were those of the strip zigzag of the polygon in the 2 four-vertex objects of the two-plane programs (z-slab, z-cut-m-slope) when the -w plane is applied first and not when the +w plane is (-w first 2 of 2, +w first refuted 2 of 2), and in 2 of 3 of the single-plane polygons (z-cut-p05 and its replicate) but not in z-cut-ym, whose 3 vertices were stored in the Sutherland-Hodgman order itself, one place from the frozen zigzag (the frozen rows HZZ and HDP without a plane order refuted 1 of 3 each, the three being z-cut-p05, z-cut-ym and the replicate)"
unit = "ta"
method = "R1-pixgeo stage g-t2 of the question-closing pass, round 2 (decision R2-15; 7 jobs: z-flat099, z-cut-p, z-cut-p05, z-slab, z-cut-ym, z-cut-m-slope and the replicate z-cut-p-r2 which runs z-cut-p05's program again) of the dataset render-closing-r1-pixgeo, on the laptop (host cedar), 2026-11-10 from 09:48 laptop time (08:48 UTC), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded), stock firmware, tool ~/sgxfive-test-r1 (sha256 bf4f8be2d8a8fe50034559450928e05695dc96d396d4892f9b00ea6bc0d4f053); each job probe --temps 8 --pixels --tri vtxuse --width 64 --height 64 --vtx-coords 2 --dump-render with the vertex program zNAME__0.bin (assembled on the Mac from probes/mte/templates/vtx_zab.s, z-cut-ym from templates/vtx_zab_pa1.s with one changed line) and the pixel program pix_green, the programs frozen by sha256; a debugfs reset before each job, all 7 of class ok; the object decoded through pbdump (vertices in stored order, packed 24-bit coordinates, depth words, prim entries, 1/w words); frozen predictions by the generator's model (gen/r1models.py predict_zclip: a plane runs only when a vertex crosses it, Sutherland-Hodgman, strip zigzag p1 p2 p0 p3 ..., entries index | 16, depth 0.5 + 0.5 z), both orders of the two planes frozen for the two-plane programs, which corrects the proposal's z-cut-m-slope row (B has z = 2 > w and is clipped too; PREFLIGHT.md section 5); scored by the frozen score/score_r1.py g-t2 (out/score-g-t2.txt), re-run on the kept files with the same SUMMARY; the 3-vertex reading at the end was made after the run by running the frozen model's Sutherland-Hodgman step"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["render-closing-r1-pixgeo:out/g-t2/"]
terms = ["PB_OBJ.PRIM_LIST", "PB_OBJ.RHW"]
+++
**What ran.** f0f8720's corrections of E181, E546 and Q070 read the primitive list as a strip of
index plus edge flag, and the stored vertex order of a clipped polygon as the strip zigzag of its
Sutherland-Hodgman polygon, from the 41 objects of S1 and S1b's g-e3 (a fit). The stage held out
five new objects: a z cut like S1b's z-cut-p with z = 2x + 0.5 (z-cut-p05), a slab cut by both
planes (z-slab: z = 4x), a cut along y (z-cut-ym, z = 2y - 1), a second two-plane polygon
(z-cut-m-slope: z = 4x - 1) and a replicate.

**Frozen verdict.** `controls pass; held out: consistent ['clip (5)', 'HSH (Sutherland-Hodgman
polygon of A->B, B->C, C->A) (10)', 'HPR (prim entry = stored index | 16 for a boundary edge,
strip triangles) (5)', 'HZZ (strip zigzag of the SH polygon) (-w plane first) (2)', 'HDP (stored
depth = 0.5 + 0.5 z at every vertex, clip-made included) (-w plane first) (2)'], refuted ['HZZ
(strip zigzag of the SH polygon) (1 of 3)', 'HDP (stored depth = 0.5 + 0.5 z at every vertex,
clip-made included) (1 of 3)', 'HZZ (strip zigzag of the SH polygon) (+w plane first) (2 of 2)',
'HDP (stored depth = 0.5 + 0.5 z at every vertex, clip-made included) (+w plane first) (2 of
2)']; repeat only: consistent none, refuted none`.

**Results [HW].** Controls: z-flat099 the default object (8,8), (56,20), (20,56) with depth
0x3f7eb852 at the three vertices; z-cut-p the 4 vertices (32,44), (20,56), (32,14), (8,8), depth
1.0, 0.625, 1.0, 0.25. Held out, in stored order:
- z-cut-p05: (40,36), (20,56), (40,16), (8,8), depth 1.0, 0.375, 1.0, 0.0, prims (16,1,18),
  (2,17,19); the replicate z-cut-p-r2 the same words.
- z-slab: (40,36), (24,52), (40,16), (24,12), depth 1.0, 0.0, 1.0, 0.0, no original vertex kept; the
  frozen order for the +w plane first was (24,52), (24,12), (40,36), (40,16) with depth 0, 0, 1, 1,
  which is not what was stored.
- z-cut-m-slope: (48,28), (32,44), (48,18), (32,14), depth 1.0, 0.0, 1.0, 0.0; again the -w-first
  order, not the +w-first one.
- z-cut-ym: 3 vertices (44,32), (20,56), (14,32), depth 0.0, 0.75, 0.0, prims (16,17,18), the set
  and the prim entries as frozen; the frozen order was (20,56), (14,32), (44,32).
The 1/w words, which no frozen row predicted, were 1.0 (0x3f800000) at the original vertices and
within 2 ulp of it at the made ones (0x3f800001 at one made vertex of z-cut-p05, at three of
z-cut-m-slope's four, at the first and fourth of z-slab with 0x3f7ffffe at its third, at one of
z-cut-ym's).

**What it shows.** The clip's vertex set (Sutherland-Hodgman over the input edges), its prim entries
(strip triangles, boundary flags) and the depth at the clip-made vertices (0 or 1 exactly) hold on
5 new objects, 4 and 3 vertices, a cut in x and in y, one and two planes. For two planes the -w
plane acts first; the order and depths of both two-plane objects follow the zigzag of that polygon.

**Read after the run [infer over data; not held out, not frozen].** The model's step for z-cut-ym
gives the Sutherland-Hodgman polygon (44,32), (20,56), (14,32) after the one plane that runs (-w),
which is the stored order itself; the frozen rule rotated it by one place (zigzag of 3 vertices:
p1, p2, p0). So the zigzag p1, p2, p0, p3 holds for four vertices (5 of 5 here with the control
and the replicate, 41 of 41 in S1 and S1b), and a single-pass 3-vertex polygon is stored in the
polygon's own order; whether that is because the unclipped triangle also keeps the input order
(e3z-flat099) or a rule on the vertex count was not told apart. The stage has one 3-vertex
clipped object.

**Not shown.** The plane order for a polygon with more than 4 vertices, a z cut through the
guard band's plane in the same program, the 1/w word at a made vertex (T3 did not run; the ulp
offsets above are one reading each), the depth at w other than 1 (T4 did not run), a cut with the
triangle wholly outside (E736's none, post hoc).
