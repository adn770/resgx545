+++
id = "E912"
claim = "R7-geo stages zd and zi (Q262; 128 jobs on 512 x 256, 640 x 480, 1024 x 768, 2048 x 1024 and 4096 x 4096, random triangles with vertices inside the target on the 1/256 grid and depth planes of gradient below 0.03, no fault): E606's coverage rule drew every image and triangle count (H-E606, 100 of 100 depth jobs and 24 of 24 iteration probes) and the depth store wrote the whole tile area and nothing outside it (H-ZLS, 100 of 100), but the stored depth stayed within E606's 3 units of 2^-23 of the plane in 94 of 100 jobs (H-DEPTH; 9.01 units at most) and the iterated clip z within 4 units in 21 of 24 (H-ITER; 11.09 at most); read after the run, each of the 6 depth misses is a triangle covering 1 or 2 pixels, every job covering 5 pixels or more stayed within 2.64 units, and the 3 iteration misses are near-constant offsets of 3.6 to 5.8 units over 2 to 17 pixels; controls pass (E606's cases 412 and 1206, E680's 1024 x 768 case 1400246); frozen verdicts 'Q262 depth H-E606 held on every size (100 of 100 rows decided)', the same for H-ZLS, 'Q262 depth H-DEPTH held on every size is not supported: 94 held, 6 FAILED', 'Q262 iteration H-E606 held (24 of 24 rows decided)' and 'Q262 iteration H-ITER held is not supported: 21 held, 3 FAILED'"
unit = "isp"
method = "R7-geo stages zd and zi of the question-closing pass, round 7 (decisions R7-2 a, R7-7 a; plan closing7/rank/rank-round7.md R7-2 a), dataset render-closing-r7-geo, on the laptop (host cedar), 2026-11-12, attempt out/20261112-211113 (zd started 21:15:18 and zi 21:27:12 Mac time, run-r7g-2.log), kernel 7.3.0-resgx545, module srcversion 41E2F5C756F96D20F7109A4 (fork 3f0b3e74, installed = loaded, knobs at their defaults at each stage start and end), stock firmware sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a, tool ~/sgxfive-test-rgn4 (t4, sha256 e6951558...); zd: 102 jobs of E606's D form (`tri --tri-v --tri-z --depth --depth-ctl` with E465's pitch rule, the buffer filled with 0xdeadbeef and dumped, `--poke blk:1=0x00400200`, `--pixels` up to 512 x 256), 12 small (1 to 4 pixel box) and 12 medium (8 to 40) triangles at each of the four sizes and 4 at 4096 x 4096 (its 64 MB depth buffer dumped whole and gzipped, soft rows), and E606's cases 412 (64 x 64) and 1206 (256 x 128) as controls (kept hash, triangle count and dump sha256); zi: 26 jobs, E606's I0 probe (bins/p1138-it-a0__0.bin, E606's manifest; pa0 = the iterated clip z) on 6 medium triangles at each of the four sizes, E606's I0 case 1016 (kept rows) and E680's 1024 x 768 case 1400246 (kept hash) as controls; every job class ok, no void row, health ok after each stage. Frozen before the first job (FROZEN.sha256 84ba6d23..., PREDICTIONS.sha256 a52a549b...): coverage by E606's rule (gen/model1140.py, a byte copy of resgx545-data isp/coverage-envelope/recompute/model1140.py), the depth layout by E465 and the band (gen/r3_geo.py), H-DEPTH as |stored - plane| at most 3 units of 2^-23 over the covered pixels, H-ITER 4 units, every triangle generated with a gradient below 0.03 (and a clip-z range per root area below 0.05). The first attempt ran nothing (E909's method). Scored by the frozen score/score_g.py zd and zi (score-zd.txt, score-zi.txt); at the fold the same scorer re-ran byte-identical on the kept files, and the 616 and 134 kept files decompress to the raw sha256 the laptop logged (fold/reproduce.sh). Post hoc at the fold, not frozen: fold/depth_read.py (the depth error by class, covered pixels and E606's range per root area) and fold/iter_read.py (the signed pa0 error per row)"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r7-geo:out/20261112-211113/zd/", "render-closing-r7-geo:out/20261112-211113/zi/", "render-closing-r7-geo:fold/"]
terms = []
+++
**What ran.** E606 fitted and held out the coverage rule and the depth and iteration tolerances on
64 x 64, 128 x 128 and 256 x 128: the depth within 3 units of 2^-23 of the plane through the
vertices where the plane's gradient |dz/dx| + |dz/dy| is below 0.03 (1.9 units at most there), the
iterated clip z within 4 units where its range per root area is below 0.05. E680 then showed the
coverage on ten more targets up to 4096 x 4096, colour only. Q262 asked whether the depth and the
iteration hold there. Stage zd ran E606's depth jobs on four of E680's targets and 4096 x 4096, 24
triangles a size (4 at 4096 x 4096), every plane flat enough for the 3-unit class; stage zi ran
E606's I0 iteration probe on 6 triangles at each of the four sizes. H-E606 is the coverage (image,
triangle count, and the dwords below 1.0 exactly where covered), H-ZLS the store (no 0xdeadbeef
left in the target's tile area, nothing written outside it), H-DEPTH and H-ITER the tolerances.

**Frozen verdict (as printed).** zd: `Q262 depth H-E606 held on every size (100 of 100 rows
decided)`, `Q262 depth H-ZLS held on every size (100 of 100 rows decided)`, `Q262 depth H-DEPTH
held on every size is not supported: 94 held, 6 FAILED, 0 cannot tell of 100`. zi: `Q262 iteration
H-E606 held (24 of 24 rows decided)`, `Q262 iteration H-ITER held is not supported: 21 held, 3
FAILED, 0 cannot tell of 24`. All five controls passed.

**Results [HW].** Per size (`score-zd.txt`, `score-zi.txt`; depth and pa0 errors in units of
2^-23 over the covered pixels, largest of the size):

| target | coverage, store | depth within 3 U | largest | pa0 within 4 U | largest |
|---|---|---|---|---|---|
| 512 x 256 | 24 / 24, 24 / 24 | 21 of 24 | 9.01 | 5 of 6 | 5.81 |
| 640 x 480 | 24 / 24, 24 / 24 | 23 of 24 | 4.11 | 4 of 6 | 11.09 |
| 1024 x 768 | 24 / 24, 24 / 24 | 22 of 24 | 5.46 | 6 of 6 | 3.60 |
| 2048 x 1024 | 24 / 24, 24 / 24 | 24 of 24 | 2.07 | 6 of 6 | 2.06 |
| 4096 x 4096 | 4 / 4, 4 / 4 | 4 of 4 | 2.96 | not run | |

The images, triangle counts and depth dumps of the controls equal E606's and E680's kept ones.

**Read after the run (post hoc, not frozen; `fold/depth_read.py`, `fold/iter_read.py`, output in
`fold/reproduce.out`).** The six depth misses are small-class triangles covering 1 or 2 pixels
(areas 0.14 to 1.07 pixel; gradients 0.002 to 0.015; one or two pixels above 3 units each). Over
zd and zf together (E913), every one of the 18 misses covers 1 or 2 pixels, the 202 jobs covering
1 to 4 pixels reach 15.9 units, and the 138 covering 5 or more stay within 2.64; 20 of 6284 covered
pixels are above 3 units. The three pa0 misses are offsets nearly constant over the triangle (5.67
to 5.81 units over 2 pixels at 512 x 256; 3.06 to 11.09, mean 4.22, over 17 pixels and -4.14 to
-3.63 over 15 at 640 x 480), not single pixels.

**What it shows.** [HW] On 512 x 256 to 4096 x 4096 (four macrotiles a row from 640 x 480) E606's
coverage rule and E465's depth store hold for random triangles inside the target, held out: the
coverage of the depth jobs is the rule's, and the store writes every dword of the target's tile
area (32 x 16 tiles) and nothing past it. E606's depth tolerance does not hold as a bound for
every triangle of gradient below 0.03: tiny triangles exceed it, up to 9 units here. The iterated
clip z exceeds 4 units on 3 of 24 medium triangles. [infer] The depth misses depend on the
triangle's size (1 or 2 pixels), not on the target: E913 finds the same on targets from 16 x 8 to
4096 x 16.

**What it does not show.** Whether E606's own three targets give the same misses on 1- and 2-pixel
triangles (E606 reports 1.9 units at most for its 529 triangles below 0.03 and does not split them
by size here); a bound or a rule for the error (Q200); vertices outside the target (every vertex
here is inside); the iterated attributes at 4096 x 4096; perspective, multisampling and depth
compares.
