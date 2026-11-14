+++
id = "E1070"
claim = "r18-flag stage f1 (2 jobs, t10: E411's G 3 and G 5 stores in E1051's zv- form with a 16-page depth buffer, never run on t10 at 16 pages, held out; 1 planned fault): G 5 faulted the job with BIF fault 0x90200 at 0x3e016001, buffer page 21, the first page nothing maps (t10's colour buffer, 5 pages with its guard, follows the depth buffer at pages 16 to 20), and G 3, whose stores reach buffer pages 16 and 18 inside that colour buffer, completed with the 20-page control's image (hash 0xd0530839d87ea325, diff 0); frozen 'H-PAST-FAULT ... (2 of 2 rows decided)' and 'H-PAST-FAULT-PAGE ... (1 of 1 rows decided)', H-PAST-ANY and H-DROP '1 held, 1 FAILED', H-PAST-ANY-PAGE '0 held, 2 FAILED'; both references (E1041's and E1051's stores byte for byte, the colour buffer right after the depth buffer) passed"
unit = "zls"
method = "r18-flag (render/closing-r18-flag), stage f1 of the question-closing pass, round 18, the flagged session with the user present: closing18/DECISIONS-R18.md (R18 decisions (a): 8 planned faults and 3 recovered hangs, the #limits capped at 15; no kernel change, no boot, no clock-gate write, no held reset), plan closing18/plan/rank-round18.md sections 2 and 3; folded with the lead's confirmation, dataset render-closing-r18-flag; attempt out/20261114-133536 (f1 13:36:35 Mac time; driver log run.log; its freeze FROZEN.sha256 c17a340fd331ed66ee955021cbcc15f661a3f3d7dce5843deb54adda30a3b3b7; scores score-f1.txt); on the laptop (host cedar, kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5 (linux fork 2a650d74, installed and loaded alike), stock firmware, tool ~/sgxfive-test-t10 (t10, sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, built from resgx545 a581c06) for the rows and t10 for the health pair, every job one process of the kit runner (kit/run_stage.sh at resgx545 2c0fe18), a debugfs reset before every row but a noreset one, a reset and the strict health fill and triangle after every fault and hang (each passed at the first try), every output and kernel slice kept gzipped; the stage gated on its references zv-c-g3 and zv-g5-24 (score-s0.txt: 7 of 7 references passed; no SGX recovery failed line in the attempt); the rows are tables/STAGE.txt, the frozen predictions predictions/STAGE.tsv (gen/make.py)); freezes: FROZEN.sha256 c17a340fd331ed66ee955021cbcc15f661a3f3d7dce5843deb54adda30a3b3b7 (79 files), PREDICTIONS.sha256 bf0fd72e197ac9b63c64a83c3213b6d0507d668473e8149aabd416d1e4e3ac8f (7 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at 2c0fe18e, resgx545:tools/closing/kit/lib_kit.sh at 2c0fe18e, resgx545:tools/closing/kit/run_stage.sh at 2c0fe18e, resgx545:tools/closing/kit/kitscore.py at 2c0fe18e, resgx545:tools/closing/kit/fake/sudo at 2c0fe18e, resgx545:tools/closing/kit/fake/timeout at 2c0fe18e, resgx545:tools/closing/kit/fake/df at 2c0fe18e, resgx545:tools/closing/kit/fake/modinfo at 2c0fe18e, resgx545:tools/closing/kit/fake/sha256sum at 2c0fe18e, resgx545:tools/closing/kit/fake/tool.sh at 2c0fe18e, resgx545:tools/closing/kit/fake/tool.py at 2c0fe18e, resgx545:tools/closing/kit/fake/ssh.py at 2c0fe18e, resgx545:tools/closing/scorekit.py at 2c0fe18e, resgx545:tools/closing/sessioncheck.py at 2c0fe18e, data:render/closing-r15-zls/out/20261114-073826/zovl/zv-c-g3.depth.1.bin.gz at 45423fbc, data:render/closing-r15-zls/out/20261114-073826/zovl/zv-c-g3.txt.gz at 45423fbc, data:render/closing-r15-zls/out/20261114-073826/zovl/zv-g5.depth.1.bin.gz at 45423fbc, data:render/closing-r15-zls/out/20261114-073826/zovl/zv-g5.txt.gz at 45423fbc, data:render/closing-r14-bif/out/20261114-055414/refill/rf-c-depth.depth-store.1.bin.gz at 45423fbc, data:render/closing-r14-bif/out/20261114-055414/refill/rf-c-depth.txt.gz at 45423fbc, data:render/closing-r14-flag/out/20261114-060824/f1/f1-ref-a.txt.gz at 45423fbc, data:render/closing-r14-flag/out/20261114-060824/f2/f2-ctl-256.txt.gz at 45423fbc, data:render/closing-r10-x/out/20261113-101116/isp0x/x-ctl.depth.1.bin.gz at 45423fbc, data:render/closing-r10-x/out/20261113-101116/isp0x/x-ctl.txt.gz at 45423fbc, data:render/closing-s1b/out/g-e4w/ix32-n-r1.txt.gz at 45423fbc, data:render/closing-s1b/out/g-e4w/ix-c.txt.gz at 45423fbc, data:render/closing-r14-flag/bins/f1-ref-a.bin at 45423fbc, data:render/closing-s1b/bins/p1139-green.bin at 45423fbc, data:render/closing-r13-flag/bins/p1131-green__0.bin at 45423fbc, data:render/closing-r13-flag/bins/p1131-blue__0.bin at 45423fbc, data:ta/mtile-fields/cases.tsv at 45423fbc, data:ta/mtile-fields/kernel.log at 45423fbc, data:ta/mtile-fields-risky/cases.tsv at 45423fbc, data:ta/mtile-fields-risky/kernel.log at 45423fbc, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built, c58f9f9c87aa3f8370d2b66917898550d86f6879 at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; TOOLSRC.sha256: 9cef7a202fc8267fa04ab6986145b69fd4ab18beafbe6fdb5e65dd009a00b612 c58f9f9c87aa3f8370d2b66917898550d86f6879:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=B60AB0B475DD1E8972419B5; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW", "infer"]
date = "2026-11-14"
data = ["render-closing-r18-flag:out/20261114-133536/f1/", "render-closing-r18-flag:fold/"]
terms = ["CR_ISP_ZLSCTL", "CR_BIF_INT_STAT"]
+++
**What ran.** Stage f1, after the s0 references: `q299-g3` and `q299-g5`, t10 `tri --keep-going
--wait-ms 20000 --width 64 --height 64 --max-width 64 --max-height 64 --tri-full --tri-z
0.5,0.5,0.5 --depth --depth-ctl C --depth-fill 0xdeadbeef --depth-pages 16 --depth-dump "$W"
--poke blk:1=0x00400200 --kpoke-render 1:rd:13=0xd000`, C 0x0017101c (G 3) and 0x0017102c (G 5),
both `expectfault expectdiff`, `#limit 2`. The store pages are E1041's and E1051's (buffer pages 12,
14, 16 and 18 at G 3; 12, 15, 18 and 21 at G 5). The plan's premise (the depth buffer the last
GENERAL allocation) was read false before the freeze from the kept `layout: fb` lines of E1041 and
E1051 (0x3e015000 and 0x3e019000, right after 20 and 24 pages): the colour buffer follows the depth
buffer, so the hypotheses were frozen on that layout (session README.md, deviation 1). The s0
references zv-c-g3 (20 pages) and zv-g5-24 (24 pages) read their kept stores (sha256 of the dump),
their colour buffers at 0x3e015000 and 0x3e019000 and the depth buffer at 0x3e001000.

**Frozen verdict (as printed).** attempt 20261114-133536, stage f1 (run.log): `SUMMARY: f1: H-DROP:
ZLS stores past the mapping are dropped (both complete) is not supported: 1 held, 1 FAILED, 0 cannot
tell of 2`; attempt 20261114-133536, stage f1 (run.log): `SUMMARY: f1: H-PAST-ANY: any ZLS store
past its buffer faults (G 3 at +0x10000, G 5 at +0x12000) is not supported: 1 held, 1 FAILED, 0
cannot tell of 2`; attempt 20261114-133536, stage f1 (run.log): `SUMMARY: f1: H-PAST-ANY-PAGE: the
stores fault 0x90200 at their first page past the buffer is not supported: 0 held, 2 FAILED, 0
cannot tell of 2`; attempt 20261114-133536, stage f1 (run.log): `SUMMARY: f1: H-PAST-FAULT: a ZLS
store faults at its first unmapped page and lands on a mapped one (G 3 ok, G 5 at +0x15000) (2 of 2
rows decided)`; attempt 20261114-133536, stage f1 (run.log): `SUMMARY: f1: H-PAST-FAULT-PAGE: G 5
faults 0x90200 at depth + 0x15000, its first unmapped page (1 of 1 rows decided)`.

**Results [HW].** `q299-g5`: `BIF fault 0x90200 at 0x3e016001`, `SGX stopped, 1 events seen`, the
reset and the health clean. `q299-g3`: `job: ok`, `depth #1: 16384 dwords, 2048 changed`
(buffer pages 12 and 14), `target: 64x64 hash 0xd0530839d87ea325` (the 20-page control's), `diff:
0 of 4096 pixels`, `layout: fb 0x3e011000`. Both references read every frozen key. The frozen
scorer re-run on the kept files is byte for byte (fold/reproduce.out).

**What it shows.** [HW] A ZLS store that reaches a page nothing maps faults the job there, with
`FAULT_REQ` bit 9 and `FAULT_TYPE` 1 (0x90200); a store past its buffer onto a page that is mapped
lands there without a fault (G 3's pages 16 and 18 in the colour buffer). So E411's table holds
literally: in its arrangement G 3 stored past the 16 pages and G 5 to 17 faulted. [infer] At G 3
the colour the PBE wrote reached the colour buffer's pages after the store, since the image is
exact. Post hoc (read at the fold): with E411's scratch at 0x3e001000, its stencil buffer at page 4,
its depth buffer at page 12 and the same colour buffer after it, the rule gives the page of all 14
of E411's faults (0x3e016, 0x3e017, 0x3e016, 0x3e01e, 0x3e02e, 0x3e04e and 0x3e08e for G 5 to 257,
both runs each; zls/control-bits kernel.log) and none for G 0, 1 and 3; sgx-pipe's
`zls::check_scratch_pitch` predicts those faults (E1070).

**What it does not show.** The order in which the ZLS store and the PBE reach a shared page beyond
this one image, any requestor other than the ZLS store, and a store past a buffer onto a mapping
with PTE flags.
