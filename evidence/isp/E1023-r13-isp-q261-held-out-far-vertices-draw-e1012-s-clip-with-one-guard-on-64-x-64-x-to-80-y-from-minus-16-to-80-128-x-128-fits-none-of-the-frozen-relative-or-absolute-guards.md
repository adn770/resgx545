+++
id = "E1023"
claim = "r13-isp stage q261 (16 jobs): every held-out far vertex draws E1012's clip (the far edges clipped to a guard, each new vertex rounded half up to 1/256 pixel, the edges then exact) at some value of its own guard (frozen H-CLIP held 14 of 14), and one value of each guard fits every 64 x 64 row (H-CLIP-ONE): x <= 80 (G = 16 of E1012's 16 to 22, 4 rows along +x), x >= -9 or -16 (3 rows along -x), y in [-16, 80] (4 rows along -y); on 128 x 128 the three rows fit x <= 147 (G = 19) and no other frozen value, so one G on both targets (H-REL) and a guard fixed in pixels (H-ABS) both failed; both controls (E979's far-ctl and far-x24p, E1005's d = 0) drew their kept images; post hoc, a guard a quarter of the target past each edge draws all 24 rows of q261 and far"
unit = "isp"
method = "r13-isp (render/closing-r13-isp), stage q261 of the question-closing pass, round 13's session r13-isp (decisions R13-1 (a) and R13-2 (a): safe class only, no held reset, no planned fault; the round 13 ranking plan, sections 2 and 3, row q261 (R11-L1, Q261)), built on the session kit (resgx545 main 05b7039, data 75d01ee20) and frozen before the run, dataset render-closing-r13-isp; attempt out/20261113-215416 (scores score-q261.txt); on the laptop (host cedar, kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5, fork 2a650d74, loaded = installed, the kit's preflight, stock firmware), tool ~/sgxfive-test-t10 (sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, source resgx545 a581c06, recipe data:render/closing-r10-st1/lead/build_tool10.sh, every row replayed on the library mock built from it before the freeze), every job one process of the kit runner (kit/run_stage.sh) with a debugfs reset and the health fill and triangle between jobs, every output kept gzipped; the rows are tables/STAGE.txt, the frozen predictions predictions/STAGE.tsv and predictions/STAGE/ (gen/make.py); run by the lead with the kit's driver, 2026-11-13 (log fold/run-r13i.log), no stop; the frozen score/score.py re-run on the kept files is byte-identical (fold/reproduce.out); freezes: FROZEN.sha256 dedc5a1da3d913bbd4d5d983709441a403fa6932b4fae9414a3a09190101bbe4 (186 files), PREDICTIONS.sha256 7d20451fef043d431b1e438c3d537d714b2b96f10ce92442f48f725d2b93ae9b (115 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at 05b7039e, resgx545:tools/closing/kit/lib_kit.sh at 05b7039e, resgx545:tools/closing/kit/run_stage.sh at 05b7039e, resgx545:tools/closing/kit/kitscore.py at 05b7039e, resgx545:tools/closing/kit/fake/sudo at 05b7039e, resgx545:tools/closing/kit/fake/timeout at 05b7039e, resgx545:tools/closing/kit/fake/df at 05b7039e, resgx545:tools/closing/kit/fake/modinfo at 05b7039e, resgx545:tools/closing/kit/fake/sha256sum at 05b7039e, resgx545:tools/closing/kit/fake/tool.sh at 05b7039e, resgx545:tools/closing/kit/fake/tool.py at 05b7039e, resgx545:tools/closing/kit/fake/ssh.py at 05b7039e, resgx545:tools/closing/scorekit.py at 05b7039e, resgx545:tools/closing/sessioncheck.py at 05b7039e, data:render/closing-r10-x/bins/pos.bin at 75d01ee2, data:render/closing-r7-geo/bins/p1138-it-a0__0.bin at 75d01ee2, data:render/closing-r10-x/bins/pix_pa0.bin at 75d01ee2, data:render/closing-r10-x/bins/pix_pa1.bin at 75d01ee2, data:pds/iteration-sources/pds-iteration-sources-iter-coords/bins/vtx_coords.bin at 75d01ee2, data:render/closing-r9-x/gen/far.py at 75d01ee2, data:render/closing-r10-geo/gen/pivot.py at 75d01ee2, data:cited/closing11/plan/c6-q261/q261_rule2.py at 75d01ee2, data:cited/closing11/plan/c6-q261/q261_rule2.sha256 at 75d01ee2, data:cited/closing11/plan/c6-q261/q261_rule3.py at 75d01ee2, data:cited/closing11/plan/c6-q261/q261_rule3.sha256 at 75d01ee2, data:cited/closing11/plan/c6-q261/q261_proposals.json at 75d01ee2, data:cited/closing11/plan/c6-q261/q261_heldout.out at 75d01ee2, data:cited/closing12/plan/c6-q201/sample0_rule.py at 75d01ee2, data:cited/closing12/plan/c6-q201/sample0_rule.sha256 at 75d01ee2, data:render/closing-r9-x/out/20261113-081821/far/far-ctl.txt.gz at 75d01ee2, data:render/closing-r9-x/out/20261113-081821/far/far-x24p.txt.gz at 75d01ee2, data:render/closing-r9-x/out/20261113-081821/far/far-x25n.txt.gz at 75d01ee2, data:render/closing-r9-x/out/20261113-081821/far/far-x23p.txt.gz at 75d01ee2, data:isp/arith-1138/main/I1/1016.txt.gz at 75d01ee2, data:render/closing-r10-x/out/20261113-101116/win0/w0-te60-64x64-x.txt.gz at 75d01ee2, data:render/closing-r10-x/out/20261113-101116/win0/w0-te60-64x64-y.txt.gz at 75d01ee2, resgx545:crates/sgx-pipe/src/isp.rs at 05b7039e, resgx545:crates/sgx-pipe/src/iter.rs at 05b7039e, resgx545:tools/usse-asm/closing_tables.py at 05b7039e, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=B60AB0B475DD1E8972419B5; stops: none; lead decisions: none"
tiers = ["HW", "infer"]
date = "2026-11-13"
data = ["render-closing-r13-isp:out/20261113-215416/q261/", "render-closing-r13-isp:fold/"]
terms = []
+++
**What ran.** E1012 fitted, post hoc on all 48 kept far rows, a clip of the far edges to a guard x
in [-G, 64 + G] with G 16 to 22, its lower and y bounds untested, and named held-out vertices
(closing11/plan/c6-q261). Stage q261 ran 14 of them at `--tri-unit 5`: c6's 4 along +x (family G =
16 to 22) and 3 along -x (a = 8 to 32, x >= -a), 4 along -y designed by the builder (g = 8 to 32,
y in [-g, 64 + g]; c6's far-y vertices depend on the x guard too) and 3 along +x on a 128 x 128
target (128 + G, against an absolute guard h = 80 to 86), between E979's far-ctl (E684's far21d0)
and far-x24p (E1005's d = 0) as controls. The engine is c6's (q261_rule2.py, a byte copy), each
bound its own parameter (tests: equal to c6's clip where the bounds agree, each row's image
depending on its own guard only). Frozen per row: H-EXACT, the clip family, and on the 64 x 64
rows along x H-PIVOT's pixel intervals.

**Frozen verdict (as printed).** `out/20261113-215416/score-q261.txt`: "SUMMARY: q261: H-CLIP: every
held-out row is the image of E1012's clip at some value of its family (14 of 14 rows decided)";
"READING q261 family G: [16] over 4 rows"; "READING q261 family G128: [19] over 3 rows"; "READING
q261 family a: [9, 16] over 3 rows"; "READING q261 family g: [16] over 4 rows"; "READING q261
family h128: none over 3 rows"; "SUMMARY: q261: H-REL: H-REL: one G fits every +x row of both
targets is not supported: 0 held, 1 FAILED, 0 cannot tell of 1" and the same for H-ABS;
"SUMMARY: q261: H-CLIP-ONE: one value of each guard (G, a, g) fits every held-out row (1 of 1
rows decided)"; "SUMMARY: q261: H-EXACT: ... not supported: 7 held, 7 FAILED"; "SUMMARY: q261:
H-PIVOT: ... (7 of 7 rows decided)". Both CONTROL lines PASS (kept image held, G 16 to 22 fit).

**Results [HW].** Per row the values that draw the kept image pixel for pixel: px1 G 16, 17, 20,
21, 22; px2 16, 17, 19, 20; px3 16, 17, 18, 19, 22; px4 16, 20; nx1 a 8, 9, 15, 16, 22, 23, 29;
nx2 a 9, 11, 14, 16, 19, 21, 24, 26, 29, 31; nx3 a 8 to 11, 15 to 20, 23 to 28, 31, 32; ny1 g 11,
16; ny2 g 8 to 10, 16 to 20, 26 to 30; ny3 g 9, 12, 13, 16, 17, 20, 23, 24, 27, 28, 31; ny4 g 8, 9,
14 to 17, 22 to 25, 29 to 32;
t128-1 G 19 only, t128-2 16, 18 to 21, t128-3 16, 17, 19, 20. H-EXACT drew 7 rows and missed the
other 7 by their band pixels; H-PIVOT found a displacement per row (each row its own triangle).
Post hoc (fold/posthoc_bounds.py, written after the scores): scanning each bound in 1/16 pixel,
the integer bounds every row of its side fits are x <= 80 or 103 and x >= -9, -16, -49 or -56
(64 x 64), y >= -16, and on 128 x 128 x <= 147, 160, 173 or 186; the box a quarter of the target
past each edge ([-W/4, 5W/4] on both axes, clip x and y within 1.5 w) draws all 24 rows of q261 and
far (`QUARTER: 24 of 24`), and on 64 x 64 it is E1012's [-16, 80].

**What it shows.** [HW] Held out, E1012's clip holds: the band of a far edge is the rounding of a
vertex clipped to a guard, with x <= 80 and y in [-16, 80] on 64 x 64 and a lower x bound of -16 or
-9, not E1005's displaced far vertex (whose displacement is per row). The guard is not 64 + G on
every target nor fixed in pixels: on 128 x 128 it is not 144 to 150 nor 80 to 86 (147 fits among
the frozen values). [infer, post hoc] A guard band in clip space, |x|, |y| <= 1.5 w (a quarter of
the target past each edge), fits both targets; it is fitted after the run. sgx-pipe models the
64 x 64 guard (`isp::guard_clip_image`, test `the_guard_clip_draws_every_kept_far_row`: 21 rows
pixel for pixel and E979's and E1005's 47 rows' counts) and refuses other targets (Q261).

**What it does not show.** The guard on targets other than 64 x 64 held out (the quarter rule is
post hoc; 128 x 128's lower and y bounds and the 147/160 choice are untested), whether the lower x
bound is -16 or -9, the y bound's high side apart from far's one +y row (E1024), and whether
the clip is in clip space or in window pixels. One far vertex per row.
