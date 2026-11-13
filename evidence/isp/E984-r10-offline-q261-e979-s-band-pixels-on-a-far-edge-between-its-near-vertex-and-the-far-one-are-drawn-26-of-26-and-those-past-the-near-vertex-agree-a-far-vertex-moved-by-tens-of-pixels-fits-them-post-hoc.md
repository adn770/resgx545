+++
id = "E984"
claim = "Round 10 offline (Q261, post hoc on E979's kept rows; no run): of the 46 pixels of E979's 11 rows whose centre lies within 1e-3 pixel of an edge line (E684's band), the 26 that lie on a far edge between its near vertex and the far vertex (2 in far-x23p, 10 in far-x24p, 14 in far-x25n, 1.2e-6 to 1.16e-4 pixel off the line) are all drawn where the exact test leaves them out, while the 19 near the same lines past the near vertex and the control's one agree with the exact image; with the near vertices fixed, the far vertex moved alone fits every band pixel of those three rows only from 43, 52 and 42 pixels in y (or -171, -206, -167 in x) at 2^23, 2^24 and -2^25 pixels, a bound from one side only, far above float32's spacing there (0.25 to 1 pixel) [HW, fitted post hoc; the pivot about the near vertex is an inference]; note: 352 floating-point edge set-ups fitted on E914, E943 and these 11 rows give at most 156 of E683's 240 cases held out (half away from zero 173, gate 235, 174 post hoc), and the 38 coarse ones (11 to 19 bits) that reproduce the 46 band pixels give at most 139"
unit = "isp"
method = "Offline, no run (round 10, decisions R10-1 a and R10-9 a of the seeds plan closing10/seeds/exp-seeds-r10.md, finding 4 and sections 9 and 11). Data: r9-x stage far's kept images (render-closing-r9-x out/20261113-081821/far/, the vertices from the session's gen/far.py: E979's ten rows and E684's far21d0 as far-ctl) and, for the note, E683's 240 S3 cases (isp-coverage-envelope-1140), E914's and E943's 395 images through round 9's closing9/offline/oz/ozlib.py. Scripts, standard library unless marked: closing10/seeds/q261/band_far.py (each band pixel against the exact coverage of E606, its distance to the nearest edge line, output band_far.out) and pivot.py (the far vertex moved by whole pixels from -400 to 400 along x or y alone, exact arithmetic in fractions, the interval that makes every band pixel of the row agree, output pivot.out); closing10/offline2/q261/segment_side.py, written by this fold (the band pixel's projection on its nearest edge: on the segment from the near vertex to the far one, or past the near vertex, output segment_side.out). The note: closing10/seeds/q260/ (numpy), fplib.py declares 352 variants (the coefficient form A x + B y + C, relative to a vertex, to the target or the tile origin, a slope form, mantissas of 11 to 24 bits, round to nearest even or truncation, on half away from zero's vertices or float ones); check_fp.py checks that the engine reproduces half away from zero on the fit set and its 26 misses here; fp_fit.py fits on E914 + E943 + E979 without reading E683 and freezes the best and the four family bests (fp_rule.json, sha256 8b05140b..., with fplib's and ozlib's hashes); fp_score.py checks the hashes and scores E683; fp_post.py scores all 352 on E683 and the band afterwards. This fold re-ran band_far.py, pivot.py and fp_score.py with python -I -B and got byte-identical outputs"
tiers = ["HW", "infer"]
date = "2026-11-13"
data = ["render-closing-r9-x:out/20261113-081821/far/", "isp-coverage-envelope-1140", "cited-scratch:closing10/seeds/q261/", "cited-scratch:closing10/offline2/q261/", "cited-scratch:closing10/seeds/q260/", "cited-scratch:closing9/offline/oz/"]
terms = []
+++
**What was done.** E979 put one vertex at up to 2^24 pixels both ways and -2^25 (two at +-2^23 and
+-2^24) on a 64 x 64 target and found the exact coverage outside E684's 1e-3 pixel band in 10 of
10 rows; the band pixels were not scored. The round 10 seeds planner scored them against the exact
coverage and asked which far-vertex displacement would draw them; this fold located each band pixel
on its edge (segment_side.py) and re-ran the planner's scripts. The planner also fitted a family of
floating-point edge set-ups for Q260 on the same rows; its held-out score is noted here.

**Results [HW, post hoc].** 46 band pixels in the 11 rows (segment_side.out, band_far.out):
- 26 lie on a far edge, between its near vertex and the far vertex, 1.2e-6 to 1.16e-4 pixel on
  the outer side of the line: every one is drawn, every one outside by the exact test (2 in
  far-x23p, 10 in far-x24p, 14 in far-x25n, the vertex at 2^23, 2^24 and -2^25 pixels). They run
  contiguously from the near vertex along the edge to the target's border.
- 19 lie within the band of the same far edges' lines but past the near vertex, where another edge
  excludes them: all agree (not drawn).
- The control's one band pixel (E684's far21d0, a vertex at 2^21) agrees.

Every band pixel lies on the outer side of its line. The rows with the far vertex along y
(far-y22n to far-y25n), at 2^22 along x, and with two far vertices have no band pixel at all.

**The far vertex moved alone (pivot.out).** With the two near vertices fixed and the far one moved
by whole pixels along one axis, every band pixel of far-x23p, far-x24p and far-x25n agrees with the
hardware exactly for y displacements of 43, 52 and 42 pixels and up (to the search's end, 400), or
x displacements of -171, -206 and -167 and down. The bound is one-sided, about the same at every
distance, and far above float32's spacing of the far vertex's coordinates (0.25 to 1 pixel at 2^23
to
2^25) [infer].

**Note: a floating-point edge does not explain it (Q260's family).** 352 variants were declared
before the fit (the q260 directory's fplib.py). The engine at 24 bits reproduces half away from
zero's
(HA's) 309 exact fit rows and HA's 26 misses here (check_fp.out). Fitted on E914's and E943's 395
images
and these 11 rows and frozen by hash before E683 was read, the best held out 156 of E683's 240 cases
and the four family bests 172, 173, 172 and 156, against HA's 173 and the gate of 235; post hoc the
best of all 352 is 174 (fp_score.out, fp_post.out). The 38 coarse variants (11 to 19 bits) that
draw all 46 band pixels as the hardware does give at most 139 of E683's cases.

**What it shows.** [HW, post hoc] Near a vertex at 2^23 pixels or more along x, the hardware draws
the pixels just outside the far edge between its near vertex and the target's border, and only
those: the band is one-sided, not noise. [infer] The hardware's far edge is the exact line turned
about the near vertex, as if the far vertex sat tens of pixels from where it is; a global
floating-point edge set-up of the declared forms does not give it without breaking E683.

**What it does not show.** The displacement itself (only a one-sided bound, from 3 rows), its
dependence on the distance and the edge's direction (the rows with the far vertex along y had no
band pixel), and whether it is a displacement at all: the seeds plan's
stage pivot (section 9) sweeps the far vertex to pin it. sgx-pipe's `far_coverage_image` keeps the
band undetermined. Q260 parks its rows (no candidate after E952 and this family).
