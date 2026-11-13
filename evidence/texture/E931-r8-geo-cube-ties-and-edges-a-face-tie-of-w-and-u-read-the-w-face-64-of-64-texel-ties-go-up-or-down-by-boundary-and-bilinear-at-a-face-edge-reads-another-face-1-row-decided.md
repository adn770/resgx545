+++
id = "E931"
claim = "R8-geo stage cube, ties and edges (Q284; 8 probe fills of TEXTYPE 2 by smp3d, no fault, readings of the frozen plan with no rule frozen but the edge rivals): at a face tie |w| = |u| (column 32 of two w sweeps at 1/1024 a column, u = +0.75 and -0.75) all 64 tie pixels read the +z face (w's, whatever u's sign); at exact texel boundaries the direction depends on the boundary, not on |ma| among 1.75, 1.625 and 1.875 (s boundaries 4 to 8 and 11 and t 5 to 8 and 11 the upper texel, s 9, 10 and t 9, 10, 12 the lower, the same 8 of 16 counts in all three jobs) while at |ma| 0.90625 every boundary goes up; bilinear (T0 0x07fe1400) at a face edge, frozen H-CLAMP against H-SEAM: in cube-edge-dz the 'in' pixels blend (768 of 768) and every 'out' pixel reads a G byte other than its face (128 of 128, G 3 on face 4): H-SEAM held, H-CLAMP failed; cube-edge-dx cannot tell (256 of 768 'in' pixels blended, under the frozen half), its 96 'out' pixels G 1 on face 0; frozen verdicts 'H-CLAMP ... is not supported: 0 held, 1 FAILED, 1 cannot tell of 2', 'H-SEAM (taps from the neighbour face) [infer] (1 of 2 rows decided)'"
unit = "texture"
method = "R8-geo stage cube of the question-closing pass, round 8 (decisions R8-2 a and R8-4 a; plan closing8/rank/rank-round8.md R8-2 (c) and (d)), on the laptop (host cedar), 2026-11-13, attempt out/20261113-015842 (dataset render-closing-r8-geo; the first attempt, out/20261113-015816, ran nothing: the lead passed SGX_TARGET_SSH_OPTS where the kit reads SGX_TARGET_HOST_KEY_ALIAS, so staging failed, and the lead's run log inside the session directory was a new file the freeze refused), kernel 7.3.0-resgx545, module srcversion 37EC97AB0CB37213C42FCCC (fork 664fd0d0, installed = loaded, knobs at their defaults at the stage start), tool ~/sgxfive-test-rgn4 (t4, sha256 e6951558..., resgx545 4623753), the session kit of resgx545 d97c4739 (kit/run_stage.sh with run/hooks.sh, a debugfs reset before each job, every job class ok, no stop, no lead decision); frozen before the first job: FROZEN.sha256 2687abf3..., PREDICTIONS.sha256, FROZEN.commits; scored by the frozen score/score.py (out/ATT/score-STAGE.txt), re-run at the fold on the kept files with byte-identical output, every kept file decompressing to the raw sha256 the laptop logged (out/fold/reproduce.sh, reproduce.out). Jobs: the stage's form (E930's method): cube-ftie-fu and fn (u = +0.75 or -0.75, v a small y ramp, w = 0.75 + (x - 32) / 1024), cube-ttie-tMMMM (w = |ma| constant, u = |ma| (x / 64 - 1/2), v = |ma| (y / 32 - 1/2): the s boundary at every 8th column, t at every 4th row) and cube-edge-dx and dz (T0 0x07fe1400, T0.MAGFILTER and MINFILTER 1; +x with v, +z with -u running to 0.749 of the major coordinate, two texels a 64-pixel row; the 'out' and 'in' pixels frozen in predictions/cube/NAME.edge.txt). The ties were frozen as 'cannot tell' and read by the frozen scorer's READ lines; the edge rivals frozen: an 'out' pixel (the outer tap past the face on one axis with weight 0.4 or more) reads G (bits 15:8, the face of a 16 x 16 tap) = its face under H-CLAMP, another under H-SEAM, decided only when at least half the 'in' pixels whose taps differ by 2 or more read neither tap. Per-boundary directions and G bytes post hoc at the fold (out/fold/post_read.py)"
tiers = ["HW", "infer"]
date = "2026-11-13"
data = ["render-closing-r8-geo:out/20261113-015842/cube/", "render-closing-r8-geo:out/fold/"]
terms = ["TEXTYPE", "T0.MAGFILTER", "T0.MINFILTER"]
+++
**What ran.** E923 left three clauses of Q284 open: the face at a tie of the two largest
magnitudes (never run), the texel at an exact boundary when |ma| is no power of two (E844's six
misses went down, 193 such pixels went up), and bilinear filtering at a face's edge. Stage cube ran
two face-tie sweeps, four texel-tie grids (one |ma| a job, two of the pairs that had gone both ways
and two more) and two bilinear jobs at a face edge. E930 has the stage's other rows and control.

**Frozen verdict (as printed).** `H-CLAMP (taps clamped inside the face) is not supported: 0 held,
1 FAILED, 1 cannot tell of 2`; `H-SEAM (taps from the neighbour face) [infer] (1 of 2 rows
decided)`. The face and texel ties were frozen as readings: every non-tie pixel of the six tie jobs
read the rule (1952 and 1344 of as many).

**Results [HW].** Face ties: 32 of 32 tie pixels read face 4 (+z) in cube-ftie-fu (u = +0.75,
against +x) and 32 of 32 in cube-ftie-fn (u = -0.75, against -x). Texel ties (per boundary, upper
or lower texel; s every 24 pixels, t every 56):

| |ma| | upper | lower |
|---|---|---|
| 1.75, 1.625, 1.875 | s 4 to 8, 11; t 5 to 8, 11 | s 9, 10; t 9, 10, 12 |
| 0.90625 | every boundary | none |

Edges: cube-edge-dz, 'in' pixels 768 of 768 differ from the point sample, 'out' pixels G = 3 in 128
of 128 (face 4); cube-edge-dx, 'in' 256 of 768 (under the frozen half: cannot tell), 'out' G = 1 in
96 of 96 (face 0), the row running d0000030, d0000048, d0000160, d0000178 into the edge.

**What it shows.** [HW] A tie between |w| and |u| goes to w's face (+z) for both signs of u: not by
the sign, and to the axis of the larger index of the two that were run [infer: one pair of axes].
An exact texel boundary at the three |ma| near 1.75 goes up or down by the boundary's place in the
same pattern for all three, and at 0.90625 always up: a rule of the boundary, not of |ma| alone
[infer]. Bilinear at a face edge mixes in a texel of another face (G between faces) in the one
decided job: H-SEAM's reading [infer: which neighbour texel is not read].

**What it does not show.** The tie rule for other axis pairs and signs, the texel-tie rule itself
(no rule was frozen: post hoc pattern, two faces' worth of boundaries), which neighbour and texel
the edge taps take, and the edge in a job whose filter the scorer saw blending at x (cube-edge-dx).
