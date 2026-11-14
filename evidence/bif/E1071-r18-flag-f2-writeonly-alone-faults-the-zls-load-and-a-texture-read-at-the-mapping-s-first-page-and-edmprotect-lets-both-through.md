+++
id = "E1071"
claim = "r18-flag stage f2 (4 jobs, t14, the debugfs knobs vm_pte_addr and vm_pte_flags on a mapping only read, held out; 2 planned faults): WRITEONLY alone (0x2) faulted r14-bif's ZLS load of the depth buffer with 0x80200 at 0x3e001001 and E566's texture read of the probe's scratch with 0x80002 at 0x3e003001, each at the mapping's first page; EDMPROTECT alone (0x10) let both through, the load storing E1046's store byte for byte and the texture read giving E1047's image; frozen 'H-WO-ALL ... (2 of 2 rows decided)', 'H-EDM-READ ... (2 of 2 rows decided)', H-WO-LOAD-OK, H-EDM-ZLS and H-EDM-TEX '0 held, 1 FAILED' each; both references passed"
unit = "bif"
method = "r18-flag (render/closing-r18-flag), stage f2 of the question-closing pass, round 18, the flagged session with the user present: closing18/DECISIONS-R18.md (R18 decisions (a): 8 planned faults and 3 recovered hangs, the #limits capped at 15; no kernel change, no boot, no clock-gate write, no held reset), plan closing18/plan/rank-round18.md sections 2 and 3; folded with the lead's confirmation, dataset render-closing-r18-flag; attempt out/20261114-133536 (f2 13:37:12 Mac time; driver log run.log; its freeze FROZEN.sha256 c17a340fd331ed66ee955021cbcc15f661a3f3d7dce5843deb54adda30a3b3b7; scores score-f2.txt); on the laptop (host cedar, kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5 (linux fork 2a650d74, installed and loaded alike), stock firmware, tool ~/sgxfive-test-t14 (t14, sha256 aa550b94585aaf6eb5d9b7927d320ad31ea8d1e206b8c5e99e4435c7f0a83859, built from resgx545 c58f9f9, recipe lead/build_tool14.sh, its built line lead/TOOL14.built) for the rows and t10 for the health pair, every job one process of the kit runner (kit/run_stage.sh at resgx545 2c0fe18), a debugfs reset before every row but a noreset one, a reset and the strict health fill and triangle after every fault and hang (each passed at the first try), every output and kernel slice kept gzipped; the stage gated on its references rf-c-depth and f1-ref-a (score-s0.txt: 7 of 7 references passed; no SGX recovery failed line in the attempt); the rows are tables/STAGE.txt, the frozen predictions predictions/STAGE.tsv (gen/make.py)); freezes: FROZEN.sha256 c17a340fd331ed66ee955021cbcc15f661a3f3d7dce5843deb54adda30a3b3b7 (79 files), PREDICTIONS.sha256 bf0fd72e197ac9b63c64a83c3213b6d0507d668473e8149aabd416d1e4e3ac8f (7 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at 2c0fe18e, resgx545:tools/closing/kit/lib_kit.sh at 2c0fe18e, resgx545:tools/closing/kit/run_stage.sh at 2c0fe18e, resgx545:tools/closing/kit/kitscore.py at 2c0fe18e, resgx545:tools/closing/kit/fake/sudo at 2c0fe18e, resgx545:tools/closing/kit/fake/timeout at 2c0fe18e, resgx545:tools/closing/kit/fake/df at 2c0fe18e, resgx545:tools/closing/kit/fake/modinfo at 2c0fe18e, resgx545:tools/closing/kit/fake/sha256sum at 2c0fe18e, resgx545:tools/closing/kit/fake/tool.sh at 2c0fe18e, resgx545:tools/closing/kit/fake/tool.py at 2c0fe18e, resgx545:tools/closing/kit/fake/ssh.py at 2c0fe18e, resgx545:tools/closing/scorekit.py at 2c0fe18e, resgx545:tools/closing/sessioncheck.py at 2c0fe18e, data:render/closing-r15-zls/out/20261114-073826/zovl/zv-c-g3.depth.1.bin.gz at 45423fbc, data:render/closing-r15-zls/out/20261114-073826/zovl/zv-c-g3.txt.gz at 45423fbc, data:render/closing-r15-zls/out/20261114-073826/zovl/zv-g5.depth.1.bin.gz at 45423fbc, data:render/closing-r15-zls/out/20261114-073826/zovl/zv-g5.txt.gz at 45423fbc, data:render/closing-r14-bif/out/20261114-055414/refill/rf-c-depth.depth-store.1.bin.gz at 45423fbc, data:render/closing-r14-bif/out/20261114-055414/refill/rf-c-depth.txt.gz at 45423fbc, data:render/closing-r14-flag/out/20261114-060824/f1/f1-ref-a.txt.gz at 45423fbc, data:render/closing-r14-flag/out/20261114-060824/f2/f2-ctl-256.txt.gz at 45423fbc, data:render/closing-r10-x/out/20261113-101116/isp0x/x-ctl.depth.1.bin.gz at 45423fbc, data:render/closing-r10-x/out/20261113-101116/isp0x/x-ctl.txt.gz at 45423fbc, data:render/closing-s1b/out/g-e4w/ix32-n-r1.txt.gz at 45423fbc, data:render/closing-s1b/out/g-e4w/ix-c.txt.gz at 45423fbc, data:render/closing-r14-flag/bins/f1-ref-a.bin at 45423fbc, data:render/closing-s1b/bins/p1139-green.bin at 45423fbc, data:render/closing-r13-flag/bins/p1131-green__0.bin at 45423fbc, data:render/closing-r13-flag/bins/p1131-blue__0.bin at 45423fbc, data:ta/mtile-fields/cases.tsv at 45423fbc, data:ta/mtile-fields/kernel.log at 45423fbc, data:ta/mtile-fields-risky/cases.tsv at 45423fbc, data:ta/mtile-fields-risky/kernel.log at 45423fbc, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built, c58f9f9c87aa3f8370d2b66917898550d86f6879 at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; TOOLSRC.sha256: 9cef7a202fc8267fa04ab6986145b69fd4ab18beafbe6fdb5e65dd009a00b612 c58f9f9c87aa3f8370d2b66917898550d86f6879:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=B60AB0B475DD1E8972419B5; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW"]
date = "2026-11-14"
data = ["render-closing-r18-flag:out/20261114-133536/f2/", "render-closing-r18-flag:fold/", "vectors-closing-r18-flag-pte"]
terms = ["CR_BIF_FAULT", "CR_BIF_INT_STAT"]
+++
**What ran.** Stage f2 in order: `q108-edm-load` and `q108-wo-load`, r14-bif's rf-c-depth argv (t14
`tri -n 2 ... --depth --depth-ctl 0x0017500e --depth-fill index --depth-store --depth-store-fill
0x3e800000 --depth-pages 20 --depth-dump "$W" --poke blk:1=0x00000200`: the load reads the depth
buffer at 0x3e001000, the store goes to the separate store buffer) with
`dbg:vm_pte_addr=0x3e001000`;
`q108-edm-tex` and `q108-wo-tex`, r14-flag's f1-ref-a argv (t14 `probe --temps 32 --coords
--pixels --scratch-pages 256` of E566's tx_map, whose PRE is empty: the program writes only o0)
with `dbg:vm_pte_addr=0x3e003000`; `dbg:vm_pte_flags` 0x10 on the edm rows (run first), 0x2 on the
wo rows. Every row `expectfault`, `#limit 4`. The s0 references read the depth buffer's address
(rf-c-depth, E1046's store byte for byte) and the scratch's (f1-ref-a, E1047's image).

**Frozen verdict (as printed).** attempt 20261114-133536, stage f2 (run.log): `SUMMARY: f2:
H-EDM-READ: EDMPROTECT lets the ZLS load and the texture read through (2 of 2 rows decided)`;
attempt 20261114-133536, stage f2 (run.log): `SUMMARY: f2: H-EDM-TEX: EDMPROTECT stops the texture
read (0xa0002) is not supported: 0 held, 1 FAILED, 0 cannot tell of 1`; attempt 20261114-133536,
stage f2 (run.log): `SUMMARY: f2: H-EDM-ZLS: EDMPROTECT stops the ZLS load (0xa0200) is not
supported: 0 held, 1 FAILED, 0 cannot tell of 1`; attempt 20261114-133536, stage f2 (run.log):
`SUMMARY: f2: H-WO-ALL: WRITEONLY faults a read: the ZLS load (0x80200) and the texture read
(0x80002) (2 of 2 rows decided)`; attempt 20261114-133536, stage f2 (run.log): `SUMMARY: f2:
H-WO-LOAD-OK: WRITEONLY does not stop the ZLS load is not supported: 0 held, 1 FAILED, 0 cannot tell
of 1`.

**Results [HW].** The kernel's `vm_map 0x3e001000 +0x14000: PTE flags F` and `vm_map 0x3e003000
+0x100000: PTE flags F` lines name each knob. `q108-wo-load`: `BIF fault 0x80200 at 0x3e001001`;
`q108-wo-tex`: `BIF fault 0x80002 at 0x3e003001`; both reset clean. `q108-edm-load`: `job: ok` in
both renders, its store E1046's byte for byte (sha256 ca4cf128..., fold/score-f2-dumps.txt);
`q108-edm-tex`: its 2048 pixels E1047's image (sha256 182d6d0a...). Scorer re-run byte for byte
(fold/reproduce.out). The four rows are the table `vectors/closing/r18-flag/pte/f2.table.json`.

**What it shows.** [HW] WRITEONLY alone stops a read before anything is read: the ZLS load
(`FAULT_REQ` bit 9) and the texture read (bit 1), `FAULT_TYPE` 0, at the mapping's first page,
`SB` 0; E945's and E946's read faults with other flags are WRITEONLY's. EDMPROTECT alone stops
neither: the load read every dword (E1046's store) and the texture read every texel (E1047's
image). sgx-pipe's `bif::pte_access` takes the four ends and replays the table.

**What it does not show.** The flags on the TA's and the EDM's own buffers, data cached within one
render under WRITEONLY, and the flags together on a read.
