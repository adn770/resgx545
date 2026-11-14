+++
id = "E1076"
claim = "r18-flag stage h2 (8 jobs, t10, the kit's noreset; 2 planned hangs): with block 1 at VDM_STATE1 bits 11:9 = 6 (E700's M1: add 4 a job), a job after a reset then two noreset jobs completed, completed and hung on two new stream shapes, 24 vertices in one object with 8 temporaries at 64 x 64 and 48 vertices in two objects with 16 temporaries at 128 x 64, as M1 gives (c = 4, 8, then 12 > 8); frozen 'M1-SHAPE ... (4 of 4 rows decided)', H-ALT '0 held, 4 FAILED', H-SCALE '2 held, 2 FAILED'; the control (E700's two-block shape, the triple's first two jobs) completed both"
unit = "vdm"
method = "r18-flag (render/closing-r18-flag), stage h2 of the question-closing pass, round 18, the flagged session with the user present: closing18/DECISIONS-R18.md (R18 decisions (a): 8 planned faults and 3 recovered hangs, the #limits capped at 15; no kernel change, no boot, no clock-gate write, no held reset), plan closing18/plan/rank-round18.md sections 2 and 3; folded with the lead's confirmation, dataset render-closing-r18-flag; attempt out/20261114-133536 (h2 13:40:10 Mac time; driver log run.log; its freeze FROZEN.sha256 c17a340fd331ed66ee955021cbcc15f661a3f3d7dce5843deb54adda30a3b3b7; scores score-h2.txt); on the laptop (host cedar, kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5 (linux fork 2a650d74, installed and loaded alike), stock firmware, tool ~/sgxfive-test-t10 (t10, sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, built from resgx545 a581c06) for the rows and t10 for the health pair, every job one process of the kit runner (kit/run_stage.sh at resgx545 2c0fe18), a debugfs reset before every row but a noreset one, a reset and the strict health fill and triangle after every fault and hang (each passed at the first try), every output and kernel slice kept gzipped; the stage gated on its own control h2-c-b (score-s0.txt: 7 of 7 references passed; no SGX recovery failed line in the attempt); the rows are tables/STAGE.txt, the frozen predictions predictions/STAGE.tsv (gen/make.py)); freezes: FROZEN.sha256 c17a340fd331ed66ee955021cbcc15f661a3f3d7dce5843deb54adda30a3b3b7 (79 files), PREDICTIONS.sha256 bf0fd72e197ac9b63c64a83c3213b6d0507d668473e8149aabd416d1e4e3ac8f (7 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at 2c0fe18e, resgx545:tools/closing/kit/lib_kit.sh at 2c0fe18e, resgx545:tools/closing/kit/run_stage.sh at 2c0fe18e, resgx545:tools/closing/kit/kitscore.py at 2c0fe18e, resgx545:tools/closing/kit/fake/sudo at 2c0fe18e, resgx545:tools/closing/kit/fake/timeout at 2c0fe18e, resgx545:tools/closing/kit/fake/df at 2c0fe18e, resgx545:tools/closing/kit/fake/modinfo at 2c0fe18e, resgx545:tools/closing/kit/fake/sha256sum at 2c0fe18e, resgx545:tools/closing/kit/fake/tool.sh at 2c0fe18e, resgx545:tools/closing/kit/fake/tool.py at 2c0fe18e, resgx545:tools/closing/kit/fake/ssh.py at 2c0fe18e, resgx545:tools/closing/scorekit.py at 2c0fe18e, resgx545:tools/closing/sessioncheck.py at 2c0fe18e, data:render/closing-r15-zls/out/20261114-073826/zovl/zv-c-g3.depth.1.bin.gz at 45423fbc, data:render/closing-r15-zls/out/20261114-073826/zovl/zv-c-g3.txt.gz at 45423fbc, data:render/closing-r15-zls/out/20261114-073826/zovl/zv-g5.depth.1.bin.gz at 45423fbc, data:render/closing-r15-zls/out/20261114-073826/zovl/zv-g5.txt.gz at 45423fbc, data:render/closing-r14-bif/out/20261114-055414/refill/rf-c-depth.depth-store.1.bin.gz at 45423fbc, data:render/closing-r14-bif/out/20261114-055414/refill/rf-c-depth.txt.gz at 45423fbc, data:render/closing-r14-flag/out/20261114-060824/f1/f1-ref-a.txt.gz at 45423fbc, data:render/closing-r14-flag/out/20261114-060824/f2/f2-ctl-256.txt.gz at 45423fbc, data:render/closing-r10-x/out/20261113-101116/isp0x/x-ctl.depth.1.bin.gz at 45423fbc, data:render/closing-r10-x/out/20261113-101116/isp0x/x-ctl.txt.gz at 45423fbc, data:render/closing-s1b/out/g-e4w/ix32-n-r1.txt.gz at 45423fbc, data:render/closing-s1b/out/g-e4w/ix-c.txt.gz at 45423fbc, data:render/closing-r14-flag/bins/f1-ref-a.bin at 45423fbc, data:render/closing-s1b/bins/p1139-green.bin at 45423fbc, data:render/closing-r13-flag/bins/p1131-green__0.bin at 45423fbc, data:render/closing-r13-flag/bins/p1131-blue__0.bin at 45423fbc, data:ta/mtile-fields/cases.tsv at 45423fbc, data:ta/mtile-fields/kernel.log at 45423fbc, data:ta/mtile-fields-risky/cases.tsv at 45423fbc, data:ta/mtile-fields-risky/kernel.log at 45423fbc, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built, c58f9f9c87aa3f8370d2b66917898550d86f6879 at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; TOOLSRC.sha256: 9cef7a202fc8267fa04ab6986145b69fd4ab18beafbe6fdb5e65dd009a00b612 c58f9f9c87aa3f8370d2b66917898550d86f6879:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=B60AB0B475DD1E8972419B5; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW"]
date = "2026-11-14"
data = ["render-closing-r18-flag:out/20261114-133536/h2/", "render-closing-r18-flag:fold/"]
terms = ["VDM_STATE1.BITS11_9"]
+++
**What ran.** Stage h2: `h2-c-a`, `h2-c-b` (noreset, the control) on E700's two-block stream
(E1035's form, 12 vertices, objects of 6); `h2-a1`, `h2-a2`, `h2-a3` (shape A: `probe --tri pixel
--temps 8 --pixels --width 64 --height 64 --vertices 24`) and `h2-b1`, `h2-b2`, `h2-b3` (shape B:
`--temps 16 --width 128 --height 64 --vertices 48 --obj2 24` with E545's second-block words), each
with `--vdm 1^=0x00000800` (block 1 at v = 6) and p1131-blue; the second and third rows of each
shape `noreset expectfault`, `#limit 4`. Frozen: M1-SHAPE against H-ALT (E413's alternation) and
H-SCALE (the threshold scales with the stream) [infer].

**Frozen verdict (as printed).** attempt 20261114-133536, stage h2 (run.log): `SUMMARY: h2: H-ALT:
E413's alternation (each second row hangs) is not supported: 0 held, 4 FAILED, 0 cannot tell of 4`;
attempt 20261114-133536, stage h2 (run.log): `SUMMARY: h2: H-SCALE: the threshold scales with the
stream (no row hangs) is not supported: 2 held, 2 FAILED, 0 cannot tell of 4`; attempt
20261114-133536, stage h2 (run.log): `SUMMARY: h2: M1-SHAPE: E700's counter M1 on two new shapes
(each third row at c = 8 + 4 hangs) (4 of 4 rows decided)`.

**Results [HW].** `h2-c-a`, `h2-c-b`, `h2-a1`, `h2-a2`, `h2-b1`, `h2-b2` completed (o0 lines read);
`h2-a3` (`job 1875 hung, recovering`) and `h2-b3` (`job 1880 hung, recovering`) hung, each `SGX
stopped, 5 events seen`, the reset and the health clean. Scorer re-run byte for byte
(fold/reproduce.out).

**What it shows.** [HW] E700's counter, held out on two stream shapes it was not fitted on: a job
adds v - 2 = 4 for block 1 at v = 6 whatever the vertex count (24, 48), the objects (one, two),
the temporaries (8, 16) and the target (64 x 64, 128 x 64), and the job that takes c past 8 hangs;
two completed jobs in a row at v = 6 do not hang (E413's alternation is the v = 7 case of the same
rule).

**What it does not show.** What decides v = 1 and v = 0 (E1035), and what the counter is.
