+++
id = "E956"
claim = "R9-geo stage cube2, ties and edges (Q284; 8 probe fills, no fault): a tie of the two largest coordinates went to the face of the higher axis (z over y over x) on 4 of 4 held-out sweeps of x = y and y = z with the tied coordinates of opposite signs (128 of 128 tie pixels; H-LOWAXIS 0 of 4, H-POS, the positive axis, 2 of 4), but post hoc 7 of the 599 two-axis tie pixels of all kept cube jobs (r8-geo's and r9-geo's, none of the sweeps') read the lower axis's face, with the third coordinate 0.62 to 0.93 of |ma| [fitted reading, no rule]; texel ties at |ma| 1.5 went up or down by the boundary exactly in E931's pattern for 1.75, 1.625 and 1.875, at 1.25 the same but for boundary 11 of s and of t (down); bilinear at a face edge: the in pixels read their exact in-face blend within 1 (768 of 768 each), and the out pixels the adjacent texel of the neighbour face (H-SEAM-ADJ) on the -y/+x edge (96 of 96) but not on the +z/+x edge (64 of 96), H-SEAM-WRAP 0 of 2; frozen verdicts 'H-HIGHAXIS on every tie pixel (4 of 4 rows decided)', 'H-SEAM-ADJ on every out pixel is not supported: 1 held, 1 FAILED', 'H-SEAM-WRAP ... 0 held, 2 FAILED'"
unit = "texture"
method = "R9-geo stage cube2 of the question-closing pass, round 9 (S9-geo, decision R9-3 a of the seeds plan closing9/seeds/exp-seeds-r9.md section 3), on the laptop (host cedar), 2026-11-13, attempt out/20261113-081038 (dataset render-closing-r9-geo; the only attempt, 77 jobs in four stages, every job class ok, no stop, no lead decision), kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5 (fork 2a650d74, the one-shot test boot; installed = loaded, knobs at their defaults at every stage start), tool ~/sgxfive-test-rgn4 (t4, sha256 e6951558..., bound by FROZEN.commits' built line to resgx545 4623753 userspace/libsgxfive/tools/sgxfive-test.c, sha256 703cbcea...), the session kit of resgx545 f32dfacc (kit/run_stage.sh with run/hooks.sh, a debugfs reset before each job; every row replayed before the freeze on the library mock built from the tool's source, none refused); frozen before the first job: FROZEN.sha256 ce1fd939..., PREDICTIONS.sha256 2693875c..., FROZEN.commits; scored by the frozen score/score.py (out/ATT/score-STAGE.txt), re-run at the fold on the kept files with byte-identical output, every kept file decompressing to the raw sha256 the laptop logged (out/fold/reproduce.sh, reproduce.out). Jobs: `probe --temps 32 --coords --pixels` of programs of r8-geo's form (gen/cube.py): four face-tie sweeps at 16 x 16, a constant coordinate +-0.75 and the tied one a ramp crossing its magnitude in column 32 with the other sign, the third coordinate 0.25 (1 + y / 32) - 0.375 (-0.125 to 0.117); two texel-tie grids (w = |ma| 1.5 and 1.25 constant on +z, u and v ramps putting a texel boundary every 8th column and 4th row); two bilinear jobs (T0 0x07fe1400) with the major coordinate 0.75, one minor a ramp from 0.564 to 0.749 of it along x and the other on a texel centre: +z towards +x and -y towards +x (the plan's -y/+z edge was replaced before the freeze: across it the two rivals predict the same texel, 96 of 96). Frozen: per tie pixel the face of H-HIGHAXIS, H-LOWAXIS and H-POS [infer]; per edge pixel the exact per-byte blend (in pixels: the in-face taps; out pixels: the outer tap under H-SEAM-ADJ, the texel the rule gives for the tap centre's direction past the edge, or H-SEAM-WRAP, the neighbour face at the tap's own (s, t) mod 16), a rival holding when every out pixel's four bytes are within 1, gated by 90% of the in pixels within 1 of theirs (E931's kept in pixels: 1536 of 1536, the calibration; on E931's two edges H-SEAM-ADJ matched 0 of 96 and 64 of 128 and H-SEAM-WRAP 0, gen/insample.out, read before the freeze); texel ties readings only. Post hoc at the fold: out/fold/post_read.py (every kept tie pixel of r8-geo's and r9-geo's cube jobs, a direction run at several sizes counted once; each edge job's outer tap solved from the blend)"
tiers = ["HW", "infer"]
date = "2026-11-13"
data = ["render-closing-r9-geo:out/20261113-081038/cube2/", "render-closing-r9-geo:out/fold/", "render-closing-r8-geo:out/20261113-015842/cube/"]
terms = ["TEXTYPE"]
+++
**What ran.** E931 read a tie of |w| and |u| going to w's face for both signs of u, texel ties
going up or down by their boundary, and one bilinear edge job taking another face's texel. Stage
cube2 ran four face-tie sweeps on the other axis pairs (x = y, y = z) with the tied coordinates of
opposite signs, so that the higher axis, the lower and the positive one part; two texel-tie grids;
and two bilinear edges with rivals for which texel the out-of-face tap reads.

**Frozen verdict (as printed).** `H-HIGHAXIS on every tie pixel (4 of 4 rows decided)`;
`H-LOWAXIS ... 0 held, 4 FAILED`; `H-POS ... 2 held, 2 FAILED`; `H-SEAM-ADJ on every out pixel is
not supported: 1 held, 1 FAILED, 0 cannot tell of 2`; `H-SEAM-WRAP ... 0 held, 2 FAILED`. The
control passed.

**Results [HW].** Face ties: the 32 tie pixels of each sweep read one face, -y (x = +0.75 against
y), +y, -z and +z, whatever the third coordinate's sign; every other predicted pixel (1889 a job)
read the rule. Texel ties (|ma| 1.5 and 1.25, per boundary): s 4 to 8 up, 9 and 10 down, 11 up at
1.5; t 5 to 8 up, 9 and 10 down, 11 up, 12 down at 1.5: E931's table for 1.75, 1.625 and 1.875;
at 1.25 the same but s 11 and t 11 down (out/20261113-081038 score-cube2.txt). Edges: every in pixel
within 1 of its exact blend (768 of 768 each, the premise
met); out pixels, solved for the outer tap (post hoc): +z/+x reads face 0 at a low byte of 22 to 24
where H-SEAM-ADJ's texel is 21 (64 of 96 within 1), -y/+x reads face 0 at 127.7 to 127.8 where
H-SEAM-ADJ's is 127 (96 of 96).

**Post hoc [fitted reading].** Over every two-axis tie pixel of the kept cube jobs of r8-geo and
r9-geo (out/fold/post_read.py), 592 of 599 read the higher axis's face; the 7 others (two in
r8-geo's a1, four in a2, one in r9-geo's c3) the lower, all with the third coordinate 0.62 to 0.93
of |ma|, where many others still read the higher (four three-way ties apart).

**What it shows.** [HW] A face tie with a small third coordinate goes to the higher axis for every
pair and sign run, so neither the lower axis nor the sign decides it; the rule is not universal
[infer: the select compares something other than the exact magnitudes when the third coordinate is
large]. At a face edge the filter's out-of-face tap reads the neighbour face near the adjacent
texel on both edges, exactly on one; the wrapped local texel is refuted [HW].

**What it does not show.** The tie rule at a large third coordinate, the texel-tie rule, and which
texel (or blend of texels) the out-of-face tap takes on the +z/+x edge.
