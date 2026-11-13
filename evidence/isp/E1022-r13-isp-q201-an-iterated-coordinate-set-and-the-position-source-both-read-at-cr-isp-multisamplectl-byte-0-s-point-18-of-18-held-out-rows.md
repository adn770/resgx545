+++
id = "E1022"
claim = "r13-isp stage q201 (23 jobs, one 64 x 64 triangle that is not the tool's default): under CR_ISP_MULTISAMPLECTL byte 0 = 0x3c, 0x0f, 0xf0, 0x5a and 0x26 (bytes 1 to 3 at 0) both the position source (E437's source 0) and coordinate set 0 iterating the vertices' clip x and y read at byte 0's point (x + lo/16, y + hi/16, lo = bits 3:0) at every drawn pixel, the position source exactly and the coordinate set within 3.8e-6 pixel (frozen H-SAMPLE0 held 18 of 18 held-out rows, x and y of both programs), and the drawn set is E1018's coverage at that point (18 of 18); H-CENTRE and H-SWAP failed 18 of 18, H-SPLIT (the coordinate set stays at the centre) 10 of 18; the five controls (0x88 coordinate set x, y and its end replicate, 0x26 position source x, y) passed"
unit = "isp"
method = "r13-isp (render/closing-r13-isp), stage q201 of the question-closing pass, round 13's session r13-isp (decisions R13-1 (a) and R13-2 (a): safe class only, no held reset, no planned fault; the round 13 ranking plan, sections 2 and 3, row q201 (R12-L1, Q201)), built on the session kit (resgx545 main 05b7039, data 75d01ee20) and frozen before the run, dataset render-closing-r13-isp; attempt out/20261113-215416 (scores score-q201.txt); on the laptop (host cedar, kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5, fork 2a650d74, loaded = installed, the kit's preflight, stock firmware), tool ~/sgxfive-test-t10 (sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, source resgx545 a581c06, recipe data:render/closing-r10-st1/lead/build_tool10.sh, every row replayed on the library mock built from it before the freeze), every job one process of the kit runner (kit/run_stage.sh) with a debugfs reset and the health fill and triangle between jobs, every output kept gzipped; the rows are tables/STAGE.txt, the frozen predictions predictions/STAGE.tsv and predictions/STAGE/ (gen/make.py); run by the lead with the kit's driver, 2026-11-13 (log fold/run-r13i.log), no stop; the frozen score/score.py re-run on the kept files is byte-identical (fold/reproduce.out); freezes: FROZEN.sha256 dedc5a1da3d913bbd4d5d983709441a403fa6932b4fae9414a3a09190101bbe4 (186 files), PREDICTIONS.sha256 7d20451fef043d431b1e438c3d537d714b2b96f10ce92442f48f725d2b93ae9b (115 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at 05b7039e, resgx545:tools/closing/kit/lib_kit.sh at 05b7039e, resgx545:tools/closing/kit/run_stage.sh at 05b7039e, resgx545:tools/closing/kit/kitscore.py at 05b7039e, resgx545:tools/closing/kit/fake/sudo at 05b7039e, resgx545:tools/closing/kit/fake/timeout at 05b7039e, resgx545:tools/closing/kit/fake/df at 05b7039e, resgx545:tools/closing/kit/fake/modinfo at 05b7039e, resgx545:tools/closing/kit/fake/sha256sum at 05b7039e, resgx545:tools/closing/kit/fake/tool.sh at 05b7039e, resgx545:tools/closing/kit/fake/tool.py at 05b7039e, resgx545:tools/closing/kit/fake/ssh.py at 05b7039e, resgx545:tools/closing/scorekit.py at 05b7039e, resgx545:tools/closing/sessioncheck.py at 05b7039e, data:render/closing-r10-x/bins/pos.bin at 75d01ee2, data:render/closing-r7-geo/bins/p1138-it-a0__0.bin at 75d01ee2, data:render/closing-r10-x/bins/pix_pa0.bin at 75d01ee2, data:render/closing-r10-x/bins/pix_pa1.bin at 75d01ee2, data:pds/iteration-sources/pds-iteration-sources-iter-coords/bins/vtx_coords.bin at 75d01ee2, data:render/closing-r9-x/gen/far.py at 75d01ee2, data:render/closing-r10-geo/gen/pivot.py at 75d01ee2, data:cited/closing11/plan/c6-q261/q261_rule2.py at 75d01ee2, data:cited/closing11/plan/c6-q261/q261_rule2.sha256 at 75d01ee2, data:cited/closing11/plan/c6-q261/q261_rule3.py at 75d01ee2, data:cited/closing11/plan/c6-q261/q261_rule3.sha256 at 75d01ee2, data:cited/closing11/plan/c6-q261/q261_proposals.json at 75d01ee2, data:cited/closing11/plan/c6-q261/q261_heldout.out at 75d01ee2, data:cited/closing12/plan/c6-q201/sample0_rule.py at 75d01ee2, data:cited/closing12/plan/c6-q201/sample0_rule.sha256 at 75d01ee2, data:render/closing-r9-x/out/20261113-081821/far/far-ctl.txt.gz at 75d01ee2, data:render/closing-r9-x/out/20261113-081821/far/far-x24p.txt.gz at 75d01ee2, data:render/closing-r9-x/out/20261113-081821/far/far-x25n.txt.gz at 75d01ee2, data:render/closing-r9-x/out/20261113-081821/far/far-x23p.txt.gz at 75d01ee2, data:isp/arith-1138/main/I1/1016.txt.gz at 75d01ee2, data:render/closing-r10-x/out/20261113-101116/win0/w0-te60-64x64-x.txt.gz at 75d01ee2, data:render/closing-r10-x/out/20261113-101116/win0/w0-te60-64x64-y.txt.gz at 75d01ee2, resgx545:crates/sgx-pipe/src/isp.rs at 05b7039e, resgx545:crates/sgx-pipe/src/iter.rs at 05b7039e, resgx545:tools/usse-asm/closing_tables.py at 05b7039e, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=B60AB0B475DD1E8972419B5; stops: none; lead decisions: none"
tiers = ["HW"]
date = "2026-11-13"
data = ["render-closing-r13-isp:out/20261113-215416/q201/", "render-closing-r13-isp:fold/"]
terms = ["CR_ISP_MULTISAMPLECTL", "CR_ISP_MULTISAMPLECTL.SAMPLE0_X", "CR_ISP_MULTISAMPLECTL.SAMPLE0_Y"]
+++
**What ran.** E1018 read byte 0 of CR_ISP_MULTISAMPLECTL (the render's cmd:16) as the
single-sampled pixel's sample point from E064's triangle counts and hashes, and inferred that the
position source reads the same point; no kept job iterated an attribute under a byte 0 other than
0x88 (Q201). Stage q201 ran one triangle, (5.29, 3.70), (60.10, 17.90), (14.60, 58.20) pixels on
the 1/256 grid (`--tri-v`), on a 64 x 64 target with `--cmd 16=0x000000NN` and two primary PDS
programs that differ in their DOUTI word only: E437's source 0 (0x20400000, `bins/pos.bin`) and
E606's coordinate set 0 (0x20400800, `bins/cset.bin`), every row with `--vtx-coords 2` and
`vtx_coords.bin` (o4, o5 the vertex's clip x and y). A shader wrote pa0 (x) or pa1 (y) as the
colour, so each (byte, program) took an x and a y job: 0x3c, 0x0f, 0xf0, 0x5a and 0x26 with both
programs (18 held out; 0x26's coordinate set is the bridge), plus five controls. The scorer read
each drawn pixel's float32 back to its offset s (value = x + s, or (x + s) / 32 - 1 for the clip
coordinate) and held a model on a row when every drawn pixel lay within 1/64 pixel of its offset.

**Frozen verdict (as printed).** `out/20261113-215416/score-q201.txt`: "SUMMARY: q201: H-SAMPLE0:
an iterated coordinate set and the position source both read at byte 0's point (x + lo/16, y +
hi/16) (18 of 18 rows decided)"; "SUMMARY: q201: H-CENTRE: both read at the pixel centre whatever
byte 0 is not supported: 0 held, 18 FAILED, 0 cannot tell of 18"; "SUMMARY: q201: H-SWAP: both
read at (x + hi/16, y + lo/16) is not supported: 0 held, 18 FAILED, 0 cannot tell of 18";
"SUMMARY: q201: H-SPLIT: the position source moves with byte 0, the coordinate set stays at the
centre is not supported: 8 held, 10 FAILED, 0 cannot tell of 18"; "SUMMARY: q201: E1018: the drawn
set is E1018's coverage at byte 0's point (18 of 18 rows decided)". Every CONTROL line PASS.

**Results [HW].** Each row read one offset at all its 1427 to 1429 drawn pixels: the position
source exactly (spread 0), the coordinate set to within 3.81e-6 pixel (one float32 step of the
clip coordinate at 1/32 pixel per unit). The offsets read are byte 0's nibbles in sixteenths: 0x3c
(12, 3), 0x0f (15, 0), 0xf0 (0, 15), 0x5a (10, 5), 0x26 (6, 2), the same for both programs; the
controls read (8, 8) for the coordinate set under 0x88 and (6, 2) for the position source under
0x26. The drawn set of every row is E1018's coverage at its point (all 4096 pixels). H-SPLIT held
the 8 source-0 rows only, where it says what H-SAMPLE0 says.

**What it shows.** [HW] Byte 0 of CR_ISP_MULTISAMPLECTL is the point at which the single-sampled
pixel is covered, its position read and its coordinate sets iterated: x + lo/16, y + hi/16 with x
the low nibble, one point for all three. E1018's [infer] that the position source reads byte 0's
point is now measured, and E606's centre is this rule at 0x88. Q201 is answered (sgx-pipe
`iter::sample_point` gives the point, test `an_attribute_is_iterated_at_byte_0s_point`).

**What it does not show.** One triangle, one 64 x 64 target, one coordinate set of two
components with w = 1, bytes 1 to 3 at 0 (the multisampled modes and ISP word 0 bit 28 sample
with them: Q202). The iteration error at other points than the centre is read only on this plane
(gradient 1/32 per pixel), not E606's conditioning range (Q200).
