+++
id = "E1074"
claim = "r18-flag stage f3 (2 jobs, t10, E1048's form at 384 x 256, a size of none of E509's cases, two CR_TE_MTILE1 words never run; 2 planned faults): 0x00c00005 (B2 = 0, every bound of the x axis 0) faulted with 0x90004 at 0x20008021, the TA's header write, and 0x00406001 (fx 6, a second macrotile inside the target) with 0x90100 at 0x10000011, the 3D's read at the parameter heap's first page, as E1073's form H-KIND gives; frozen 'H-KIND ... (2 of 2 rows decided)', H-ONE-KIND '1 held, 1 FAILED', the page form H-PAGE-END '1 held, 1 FAILED' (the TA's fault at page 0x20008, not the first page past the kernel's 0x6000 bytes of TA data); the reference f2-ctl-256 passed"
unit = "ta"
method = "r18-flag (render/closing-r18-flag), stage f3 of the question-closing pass, round 18, the flagged session with the user present: closing18/DECISIONS-R18.md (R18 decisions (a): 8 planned faults and 3 recovered hangs, the #limits capped at 15; no kernel change, no boot, no clock-gate write, no held reset), plan closing18/plan/rank-round18.md sections 2 and 3; folded with the lead's confirmation, dataset render-closing-r18-flag; attempt out/20261114-133536 (f3 13:38:09 Mac time; driver log run.log; its freeze FROZEN.sha256 c17a340fd331ed66ee955021cbcc15f661a3f3d7dce5843deb54adda30a3b3b7; scores score-f3.txt); on the laptop (host cedar, kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5 (linux fork 2a650d74, installed and loaded alike), stock firmware, tool ~/sgxfive-test-t10 (t10, sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, built from resgx545 a581c06) for the rows and t10 for the health pair, every job one process of the kit runner (kit/run_stage.sh at resgx545 2c0fe18), a debugfs reset before every row but a noreset one, a reset and the strict health fill and triangle after every fault and hang (each passed at the first try), every output and kernel slice kept gzipped; the stage gated on its reference f2-ctl-256 (score-s0.txt: 7 of 7 references passed; no SGX recovery failed line in the attempt); the rows are tables/STAGE.txt, the frozen predictions predictions/STAGE.tsv (gen/make.py)); freezes: FROZEN.sha256 c17a340fd331ed66ee955021cbcc15f661a3f3d7dce5843deb54adda30a3b3b7 (79 files), PREDICTIONS.sha256 bf0fd72e197ac9b63c64a83c3213b6d0507d668473e8149aabd416d1e4e3ac8f (7 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at 2c0fe18e, resgx545:tools/closing/kit/lib_kit.sh at 2c0fe18e, resgx545:tools/closing/kit/run_stage.sh at 2c0fe18e, resgx545:tools/closing/kit/kitscore.py at 2c0fe18e, resgx545:tools/closing/kit/fake/sudo at 2c0fe18e, resgx545:tools/closing/kit/fake/timeout at 2c0fe18e, resgx545:tools/closing/kit/fake/df at 2c0fe18e, resgx545:tools/closing/kit/fake/modinfo at 2c0fe18e, resgx545:tools/closing/kit/fake/sha256sum at 2c0fe18e, resgx545:tools/closing/kit/fake/tool.sh at 2c0fe18e, resgx545:tools/closing/kit/fake/tool.py at 2c0fe18e, resgx545:tools/closing/kit/fake/ssh.py at 2c0fe18e, resgx545:tools/closing/scorekit.py at 2c0fe18e, resgx545:tools/closing/sessioncheck.py at 2c0fe18e, data:render/closing-r15-zls/out/20261114-073826/zovl/zv-c-g3.depth.1.bin.gz at 45423fbc, data:render/closing-r15-zls/out/20261114-073826/zovl/zv-c-g3.txt.gz at 45423fbc, data:render/closing-r15-zls/out/20261114-073826/zovl/zv-g5.depth.1.bin.gz at 45423fbc, data:render/closing-r15-zls/out/20261114-073826/zovl/zv-g5.txt.gz at 45423fbc, data:render/closing-r14-bif/out/20261114-055414/refill/rf-c-depth.depth-store.1.bin.gz at 45423fbc, data:render/closing-r14-bif/out/20261114-055414/refill/rf-c-depth.txt.gz at 45423fbc, data:render/closing-r14-flag/out/20261114-060824/f1/f1-ref-a.txt.gz at 45423fbc, data:render/closing-r14-flag/out/20261114-060824/f2/f2-ctl-256.txt.gz at 45423fbc, data:render/closing-r10-x/out/20261113-101116/isp0x/x-ctl.depth.1.bin.gz at 45423fbc, data:render/closing-r10-x/out/20261113-101116/isp0x/x-ctl.txt.gz at 45423fbc, data:render/closing-s1b/out/g-e4w/ix32-n-r1.txt.gz at 45423fbc, data:render/closing-s1b/out/g-e4w/ix-c.txt.gz at 45423fbc, data:render/closing-r14-flag/bins/f1-ref-a.bin at 45423fbc, data:render/closing-s1b/bins/p1139-green.bin at 45423fbc, data:render/closing-r13-flag/bins/p1131-green__0.bin at 45423fbc, data:render/closing-r13-flag/bins/p1131-blue__0.bin at 45423fbc, data:ta/mtile-fields/cases.tsv at 45423fbc, data:ta/mtile-fields/kernel.log at 45423fbc, data:ta/mtile-fields-risky/cases.tsv at 45423fbc, data:ta/mtile-fields-risky/kernel.log at 45423fbc, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built, c58f9f9c87aa3f8370d2b66917898550d86f6879 at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; TOOLSRC.sha256: 9cef7a202fc8267fa04ab6986145b69fd4ab18beafbe6fdb5e65dd009a00b612 c58f9f9c87aa3f8370d2b66917898550d86f6879:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=B60AB0B475DD1E8972419B5; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW", "infer"]
date = "2026-11-14"
data = ["render-closing-r18-flag:out/20261114-133536/f3/", "render-closing-r18-flag:fold/"]
terms = ["CR_TE_MTILE1", "CR_BIF_INT_STAT"]
+++
**What ran.** Stage f3: `f3-k4` and `f3-k100`, t10 `tri --tri-full --pixels --width 384 --height 256
--max-width 384 --max-height 256 --kpoke-render 1:ta:143=V --wait-ms 20000 --keep-going
--dump-render "$W"`, V 0x00c00005 and 0x00406001, both `expectfault expectdiff`, `#limit 2`. The
kind was frozen on E1073 (fit/o18_1.py, its output fit/o18_1.out); the page was frozen apart
(H-PAGE-END: the first page past the TA data of the kernel's layout at 384 x 256, 0x6000 bytes, as
E1048's 24576 at 256 x 256) [infer]. The s0 reference f2-ctl-256 read E1048's hash and 24576 bytes
of TA data. 384 x 256 (n = 2) was chosen because E509's three 0x90004 faults at 640 x 480 needed two
health retries each, its four at 256 x 256 none (session README.md, deviation 3).

**Frozen verdict (as printed).** attempt 20261114-133536, stage f3 (run.log): `SUMMARY: f3: H-KIND:
O18-1's kind: an empty axis faults 0x90004 (the TA), other words 0x90100 (the 3D) (2 of 2 rows
decided)`; attempt 20261114-133536, stage f3 (run.log): `SUMMARY: f3: H-ONE-KIND: every faulting
word faults 0x90100 is not supported: 1 held, 1 FAILED, 0 cannot tell of 2`; attempt
20261114-133536, stage f3 (run.log): `SUMMARY: f3: H-PAGE-END: f3's faults at the TA data's first
unmapped page (0x20006) and the parameter heap's (0x10000) is not supported: 1 held, 1 FAILED, 0
cannot tell of 2`.

**Results [HW].** `f3-k4`: `BIF fault 0x90004 at 0x20008021`, `SGX stopped, 0 events seen`;
`f3-k100`: `BIF fault 0x90100 at 0x10000011`, `SGX stopped, 1 events seen`; the health passed at
the first try after both. Scorer re-run byte for byte (fold/reproduce.out).

**What it shows.** [HW] Held out on two words at a new size, the kind of a faulting macrotile word
is E1073's: a word whose axis bounds are all 0 faults the TA's region header write (`FAULT_REQ`
bit 2, 0x90004, on a TA data page), and a word whose first macrotile ends inside the target with a
second macrotile there faults the 3D's read at the parameter heap's first page (bit 8, 0x90100,
page 0x10000, `SB` 1). [infer] The TA's faulting write is at TA data page 0x20008 at 384 x 256 on
this module, the page of E509's x-side 256 x 256 faults on module 14D09986: not the first page
past the kernel's TA data (0x20006), so its address does not follow the layout's end.

**What it does not show.** Why the TA writes at page 0x20008 (no TA data is dumped after a failed
render), the stride's relation to the RT data, and the kind of a word at four macrotiles a side.
