+++
id = "E952"
claim = "Round 9 offline (Q260; no run), on E683's 240 S3 cases (negative coordinates at 1/4096, kept images, never read by E914's or E943's readings): E943's post hoc reading 'a sweep misses half away from zero's (HA's) image iff a vertex lies past the target's far edge' fails both ways (61 of the 167 cases with such a vertex are off HA, 106 exact; 6 of the 73 without one are off), and its band (off pixels only within 6.4e-4 pixel of an edge of 195 pixels or more) does not bound E683's 101 off pixels (up to 2.3e-3 pixel from an edge line; 20 of them in cases whose longest edge is below 195 pixels); no threshold on distance over length, over the largest |coordinate|, or over both separates the 101 from the 1931 right pixels within 3e-3 pixel of an edge [HW]; OZ, 1613 declared fixed-point edge-function variants on HA's vertices (the coefficients quantised to b = 4 to 24 fractional bits under three normalisations, three roundings and five origins, or the two products rounded to m = 12 to 40 significant bits), fitted on E914's and E943's 395 kept images, where none beats HA by more than 5 rows (314 of 395 against 309), and frozen by hash (oz_rule.json 6c8d2a50...): held out on E683 the frozen best is exact on 154 of 240 cases, the family's other frozen best 162, HA 173, against a gate of 235; post hoc every variant scores at most 175 [HW, held out offline]; the far-vertex clause is dropped as a rule, and no candidate for the long-edge pixels survives"
unit = "isp"
method = "Offline, no run (round 9, decisions S-2 a and R9-8 a; seeds plan closing9/seeds/exp-seeds-r9.md finding 5 and section 8). Numpy, scratch only, run with an interpreter outside the repository (/Users/jtorra/src/nhc/.venv/bin/python -I -B, Python 3.14.10, numpy 2.4.3; the repository's .venv has none), read only over resgx545-data. The seeds planner's closing9/seeds/q260/far_e683.py (per case: HA's off pixels through the dataset's recompute/model1140.py, whether HA's vertex lies past x > W or y > H, the longest edge, each off pixel's distance to the nearest edge line) and prec_e683.py (the off pixels against the right pixels within 3e-3 pixel of an edge line, by distance over L, over M = the largest |coordinate|, and over L M), re-run in this fold: both outputs byte-identical. OZ (this fold, closing9/offline/oz/): ozlib.py loads E914's zs rows (render/closing-r7-geo out/20261112-211113/zs) and E943's zs2 rows (render/closing-r8-lgeo out/20261113-024441/zs2), every completed job with a whole --pixels image (395 jobs, controls included), and E683's cases through the dataset's own loader, and evaluates each edge of HA's vertices exactly in int64 (the quantised value's sign as 2^b e(S) + eps terms; the product family exact in float64 below 2^53); check_engine.py (a control that could fail) reproduces model1140's HA image on all 395 jobs (0 pixels differ) and E914's and E943's counts (HA 125 of 143 held out and 42 of 51 mirror rows, 738 off pixels on zs2). oz_fit.py scored every variant on the 395 jobs only, then wrote oz_rule.json with the best overall and per family and its sha256 (oz_fit.out); oz_score.py checked both hashes (rule and ozlib.py) and scored HA and the frozen variants on E683's 240 cases, then on the dataset's groups S1, S2 and S5 as controls (oz_score.out; S4, E684's far vertices, holds no main-directory case); oz_post.py, after the score and disclosed as post hoc, scored all 1613 variants on E683 (oz_post.out). E683's cases were read by no OZ step before the freeze; the planner's far_e683.py had read their HA counts, which no variant's choice uses"
tiers = ["HW", "infer"]
date = "2026-11-13"
data = ["isp-coverage-envelope-1140", "render-closing-r7-geo:out/20261112-211113/zs/", "render-closing-r8-lgeo:out/20261113-024441/zs2/", "cited-scratch:closing9/seeds/q260/", "cited-scratch:closing9/offline/oz/"]
terms = []
+++
**What was done.** E914 and E943 found that a negative coordinate 1/512 above the 1/256 grid rounds
away from zero, and that the pixels off HA's image lie within 6.4e-4 pixel of a long edge; read
after E943's run, every sweep with a vertex past the target's far edge missed. Q260 asked for that
reading and the band to be frozen and held out. E683's 240 S3 cases are kept images never used by
those readings, so the seeds planner read both on them, and the round decided an offline step, OZ,
before any laptop row: fit an arithmetic of the edge function on E914's and E943's images, freeze
it, hold it out on E683, and run more sweeps (zs3) only if a candidate is exact on at least 235 of
the 240.

**The far-vertex reading and the band on E683 [HW].** HA is exact on 173 of 240 cases (101 pixels
off in 67), as E683's records give. With a vertex past the far edge: 167 cases, 61 off HA (73
pixels); without: 73 cases, 6 off (10 pixels) (`far_e683.out`). A far vertex raises the miss rate
(37 % against 8 %), but "misses iff a far vertex" fails both ways. The off pixels lie up to 2.3e-3
pixel from an edge line, beyond E943's 6.4e-4, and 20 of them are in cases whose longest edge is
under 195 pixels. Within 3e-3 pixel of an edge, the largest ratio of distance to L, to M or to L M
over the 101 wrong pixels is above the ratio of 1546 to 1739 of the 1931 right ones
(`prec_e683.out`): no threshold of those forms separates them.

**OZ [HW, held out offline].** The variants (`ozlib.py`): HA's vertices on the 1/256 grid, each edge
P -> Q of the winding evaluated at the pixel centre S. Family "coef": the coefficients dx, dy over
a normalisation n (the larger of |dx| and |dy|, the power of two at or above it, or 256: pixel
units) rounded to b fractional bits, b = 4 to 24 (to nearest away from zero, toward zero, floor),
the edge's constant at an origin (the target's corner, the 32 x 16 tile of S, which is the TA's
region, P, Q, or the edge's upper vertex) exact or rounded the same way: 1323 variants. Family
"prod": the two products dx (Sy - Oy) and dy (Sx - Ox) and the constant at O each rounded to m
significant bits, m = 12 to 40 (to nearest even, toward zero), the same origins: 290. E606's tie
rule throughout. On the 395 fit jobs HA is exact on 309; the best variant, prod-m18-RE-top, on 314,
the best "coef", major-b20-FL-top-cx, on 312 (`oz_fit.out`); [infer] a variant fine enough to keep
the pixels the sweeps aim exactly at an edge gives HA's image, and a coarser one breaks those before
it mends the long-edge ones. Frozen (oz_rule.json 6c8d2a50...), on E683: prod-m18-RE-top 154 of 240
(145 pixels), major-b20-FL-top-cx 162 (128), HA 173 (101): no candidate reaches 235, so the gate
fails and zs3 does not run. As controls the two also lose cases HA gets right in the dataset's
positive groups (S1 575 and 494 of 620, S5 78 and 76 of 160; S2 588 of 588 for all)
(`oz_score.out`). Post hoc, all 1613 variants on E683: at most 175 of 240 (major-b22-RN-P-cx), none
at or above 235 (`oz_post.out`).

**What it shows.** [HW] On data that took no part in it, E943's far-vertex reading and its band are
not rules: a far vertex makes a miss likelier, no more. [HW, held out offline] No fixed-point
evaluation of the edge function of these forms, on HA's vertices, gives E683's images better than
HA does. [infer] What decides a pixel this close to a long edge is not a coarser edge function
evaluated on HA's vertices; it may lie before the edge set-up (the vertex as the TA stores it) or
in a form not declared here.

**What it does not show.** Which arithmetic does decide those pixels (Q260); E684's far vertices
(not in the dataset's main directory, so not a control here); forms outside the two families (a
floating edge set-up from the clip words, per-tile re-basing of the vertices, a different tie rule
near a long edge). sgx-pipe keeps refusing a negative vertex with a sub-grid fraction (`isp.rs`).
