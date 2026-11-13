+++
id = "E992"
claim = "Round 10 offline (Q202, the perspective clause; no run): on r6-pixel's 114 kept jobs with w other than 1 (stages g6-rwa 8 and g6-rw 106, E859; 64 x 64, w from 2.5e-4 to 8027, 58 distinct snapped triangles), E606's coverage rule (centre sample, vertices rounded half up to 1/256 pixel, E607, top-left ties) applied to the window coordinates 32 + 32 S x / w gives every stored image exactly, 0 of 466944 pixels off, 114 of 114 jobs and 7296 of 7296 rows, under each of four rivals for the divide declared and hashed before any image was compared (rule.json, 830bb58d...: exact x / w, a float32 divide, a float32 reciprocal and product, and the TA's stored window X and Y decoded from each kept parameter buffer) [HW data, held out: E606 frozen 2026-11-09, the jobs ran 2026-11-12]; the stored X and Y equal the exact snapped x / w at all 342 vertices, and no pixel parts the rivals (the w ratio across a triangle is at most 1.1 in 105 jobs, 3.0 at most), so the divide's arithmetic is not split [infer]"
unit = "isp"
method = "Offline, no run (round 10, decisions R10-1 a and R10-7 a, package O10-3; ranking closing10/rank/rank-round10.md finding 3, a helper agent's check in closing10/rank/q202/ with its NOTES.md). Data: r6-pixel (render/closing-r6-pixel, dataset render-closing-r6-pixel) attempt out/20261112-142113, stages g6-rwa and g6-rw: the kept images and parameter buffers of the 114 jobs, the vertices from the session's frozen score/rwdesign5.py and rwdesign6.py (exact fractions, w = C x + D, the scale S; tool and module as E859 gives them); r5-pixel's g5 jobs were named in the rule but not scored. The script closing10/rank/q202/q202_cov.py (numpy for float32 only; checks rule.json against rule.sha256 before it compares an image) rebuilds each job's vertices under each rival, snaps them as E607 does, draws E606's rule over the 64 x 64 target (sgx-pipe's Tri::covers in Python) and compares the covered set with the kept image (0xff00ff00 covered), per job, row and pixel, and counts the pixels where the rivals disagree. Before hashing the rule the helper had read one job's background rows and parameter header to learn the formats, no pixel mask. This record re-ran the script from its directory with the repository's .venv (python -B) and got q202_cov.out byte-identical."
tiers = ["HW", "infer"]
date = "2026-11-13"
data = ["render-closing-r6-pixel:out/20261112-142113/g6-rwa/", "render-closing-r6-pixel:out/20261112-142113/g6-rw/", "cited-scratch:closing10/rank/"]
terms = []
+++
**What was done.** E606 measured the coverage rule with w = 1 only, and Q202 asks first whether the
coverage test on window x / w is exact with perspective. r6-pixel's g6 stages (E859, for the 1/w the
TA stores, Q230) drew 114 triangles with w other than 1 and kept every image and parameter buffer. A
helper agent of the round 10 ranking declared four ways to form the window coordinates, hashed them,
and then compared each job's image with E606's rule drawn from each.

**Results [HW].** Every rival draws every kept image: 0 of 466944 pixels off, 114 of 114 jobs, 7296
of 7296 rows exact for H-EXACT, H-F32, H-F32R and H-STORED alike. The stored window coordinates
equal the exact snapped ones at all 342 vertices (and so do the float32 rivals'). No pixel is
predicted differently by any two rivals (0 discriminating pixels): the w ramp across a triangle is
mild (max / min w 1.0 to 1.1 in 105 jobs, 1.8 in six, 1.4 in one and 3.0 in one), and the centres
closest to an edge are ties exactly on it (9 jobs have a centre within 1e-4 pixel), the same in
every rival.

**What it shows.** [HW] E606's coverage rule holds with perspective on these 114 jobs, given window
x / w: the ISP does nothing perspective-specific in coverage there, and the TA stores the window
coordinates of x / w snapped to 1/256. [infer] Which arithmetic forms x / w (an exact divide, a
float32 divide or a reciprocal) is not split: their results differ by about 1e-6 pixel, which only a
centre that close to an edge would show.

**What it does not show.** A large w ramp across one triangle with a centre within ~1e-5 pixel of an
edge (the row that would split the divide), the depth and attribute planes under perspective (the
pixel side refuses a 1/w other than 1, Q202), multisampling, ISP word 0 bit 28, lines and points
(Q202, Q031, Q159 to Q161).
