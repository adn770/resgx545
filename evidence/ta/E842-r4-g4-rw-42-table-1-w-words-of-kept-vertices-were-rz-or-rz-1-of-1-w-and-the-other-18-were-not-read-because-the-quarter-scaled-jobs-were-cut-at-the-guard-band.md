+++
id = "E842"
claim = "R4-pixel stage g4-rw (Q230, 24 jobs: R2's t3-nocut shape, z = 0 and w = C x + D on the tool's three vertices, a table of 60 w split 30 FIT and 30 HELD OUT by the sha256 of their bits before the run): the four controls passed (w = 1; 3, 9, 4.5; 7, 10, 7.75; 1.40625, 1.78125, 1.5: three vertices at the window rule's positions, depth 0x3f000000, the known words exact); in the 14 jobs at scale 1 and 4 (42 w in 1.03 to 7.84) the PB_OBJ.RHW word of every kept vertex was RZ of 1/w (31) or RZ + 1 (11: w 1.125, 1.40625, 1.49219, 1.75638, 4.2782, 4.67374, 6.375, 6.75, 7.125, 7.375, 7.83901), 19 of 19 FIT and 23 of 23 HELD OUT words read; the 6 jobs at scale 1/4 (18 w in 0.254 to 0.443) read no word: frozen verdict 'every table word is RZ or RZ+1 of 1/w (42 of 60 rows decided); analysis not run: 19 of 30 FIT and 23 of 30 HELD OUT words read' (job shape 14 held, 6 FAILED), so the frozen fit of the algorithm families did not run; read at the fold, those 6 jobs' window coordinates 32 + 32 x / w (frozen from -62.4 to 120.9) lie beyond the guard band of the 64 x 64 target, and the TA cut each triangle to a polygon of 5 to 7 vertices every one of which lies on x or y = -16 or 80, so no kept vertex, and no 1/w of a table w, was stored"
unit = "ta"
method = "R4-pixel stage g4-rw of the question-closing pass, round 4 (decision: Q230 table a, plan closing4/pixel/exp-pixel-r4.md section 3.5), dataset render-closing-r4-pixel, on the laptop (host cedar, direct cable), 2026-11-11, attempt out/20261111-210423 (the third and last stage of the attempt, started 21:10:36 Mac time; run2.log), kernel 7.3.0-resgx545, module srcversion 99CD90DA26E3AFF9C450517 (installed = loaded), stock firmware sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a, tool ~/sgxfive-test-rgn4 (sha256 e6951558a93b4b7bc750eeae302997992d7ec6e26719bc527ba1ffc9c6fb779a); the freeze of the first attempt (FROZEN.sha256 f9b0fa03..., the FIT and HELD OUT split in predictions/g4-rw.tsv, PREDICTIONS.sha256 c939d0f5...), no refreeze; every job after a debugfs reset, `probe --temps 8 --pixels --tri vtxuse --width 64 --height 64 --vtx-coords 2 --dump-render DIR --slot pixel=pix_green.bin rw-NN.bin` (templates/vtx_zw.s, C and D chosen so that every w is exact in float32; three w a job, w3 = 0.75 w1 + 0.25 w2, a third of the jobs at scale 1, 4 and 1/4), the words decoded from the kept parameter buffer and TA data by pbdump.first_object and matched to the frozen window position of each vertex (tolerance 1/32 pixel); health ok after the stage; scored by the frozen score/score_r4.py g4-rw (score/score_rw.py, rwfam.py, rwdesign.py; out/20261111-210423/score-g4-rw.txt, gate-g4-rw.txt: PASS), both reproduced byte for byte at the fold (2026-11-11); the frozen analysis runs only when all 60 words are read and was not run, then or at the fold; the decoding of the 6 jobs whose words were not read is a post hoc reading at the fold with the scorer's own decode_object (fold/posthoc_rw_objects.py and its output)"
tiers = ["HW", "infer"]
date = "2026-11-11"
data = ["render-closing-r4-pixel:out/20261111-210423/g4-rw/", "render-closing-r4-pixel:fold/"]
terms = ["PB_OBJ.RHW"]
+++
**What ran.** The 1/w word of a kept vertex is RZ of 1/w at most w and one ulp above it at some w
(E754, E795, E796, E798), and no threshold of the exact quotient's fraction separates the two
(Q230's note of 2026-11-11). Stage g4-rw reads a table of 60 w so that algorithm families can be
fitted on 30 FIT words and scored on 30 HELD OUT words, the split frozen with the table; the only
frozen assertion is that every word is RZ or RZ + 1 of 1/w.

**Frozen verdict (as printed).** `Q230 (g4-rw): controls rw-k0 PASS; rw-k1 PASS; rw-k2 PASS;
rw-k3 PASS`; `frozen assertion 'every word is RZ or RZ+1', FIT: 19 held, 0 FAILED, 11 cannot tell
of 30`; `frozen assertion 'every word is RZ or RZ+1', HELD OUT: 23 held, 0 FAILED, 7 cannot tell of
30`; `job shape (object, 3 vertices, window, depth 0x3f000000): 14 held, 6 FAILED, 0 cannot tell of
20`; `SUMMARY: every table word is RZ or RZ+1 of 1/w (42 of 60 rows decided); analysis not run: 19
of 30 FIT and 23 of 30 HELD OUT words read`; `gate g4-rw: PASS`.

**Results [HW].** The words read (got - RZ, by half):

| half | RZ | RZ + 1 | not read |
|---|---|---|---|
| FIT | 13 | 6 | 11 |
| HELD OUT | 18 | 5 | 7 |

RZ + 1 at w = 1.125, 1.40625 (as E798), 1.49219, 1.75638, 4.2782, 4.67374, 6.375, 6.75, 7.125,
7.375 and 7.83901; RZ at the other 31, among them 1.5, 1.5625, 1.75, 5 and 7.5. Every word read
is in `out/20261111-210423/score-g4-rw.txt` with its w and RZ.

**Why 18 words are missing (read at the fold, post hoc).** They are the 18 w of the six jobs
rw-15 to rw-20, the third of the table scaled by 1/4 (w 0.254 to 0.443): 11 FIT and 7 HELD OUT,
exactly the shortfall. The frozen window positions 32 + 32 x / w of their vertices run from -62.4
to 120.9, beyond the guard band of the 64 x 64 target, so the TA clipped each triangle: the
stored objects have 5, 6 or 7 vertices, each with x or y at -16 or 80 (the band's edges, E777),
and none at a frozen position (`fold/posthoc_rw_objects.txt`). Their 1/w words are those of made
vertices, which the stage did not ask about. The design's own note "no clip: z = 0 is inside +-w"
was true of z and missed the window coordinates. The 14 other jobs stored 3 vertices each at the
frozen positions with depth 0x3f000000.

**What it shows and does not.** The frozen assertion holds on 42 more words of kept vertices
(with E754 to E798, 65 of 65): the 1/w word is RZ of 1/w or one ulp above it, never further and
never below, from 1.03 to 7.84. The fit of the algorithm families was meant to run on all 30 FIT
words and be scored on all 30 HELD OUT words; with 19 and 23 it was not run, and running it now
on what was read would not be the frozen test. So which w store RZ + 1 still has no rule. [infer]
The quarter-scaled third needs its x scaled with w to stay inside the band. Not shown: the rule
of the RZ + 1 words, w below 1, the made vertex's 1/w, the depth word at w other than 1.
