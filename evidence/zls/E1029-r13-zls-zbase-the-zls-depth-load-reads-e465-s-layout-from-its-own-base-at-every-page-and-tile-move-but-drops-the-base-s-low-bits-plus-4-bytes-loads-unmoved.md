+++
id = "E1029"
claim = "r13-zls stage zbase (11 jobs, E977's z243 form on t10 with the depth test never and the load buffer filled with its own dword indices, render details dword 12 poked after the tool's own pokes): the ZLS depth load reads E465's layout from the base in dword 12, not from the store's base, a tile, a page, 16 and 64 KiB away and on the store's own buffer (frozen H-MOVED held 6 of 7 held-out moves; H-STOREBASE and H-UNMOVED failed 6 of 7), but a base moved by 4 bytes loads as the unmoved one (H-MOVED failed on zb-m4: every stored dword its own index) while 64 bytes moved it by 16 dwords; post hoc (fold/look.py) the seven moves fit the base rounded down to 8, 16, 32 or 64 bytes and no frozen rival holds all seven; all four controls passed"
unit = "zls"
method = "r13-zls (render/closing-r13-zls), stage zbase of the question-closing pass (round 13, decisions R13-1 (a), R13-8 (a) and R13-10 (a) of closing13/DECISIONS-R13.md, plan closing13/plan/rank-round13.md sections 2 and 3), dataset render-closing-r13-zls; attempt out/20261113-213117 (zbase 21:31:17 Mac time; driver log run.log; its freeze FROZEN.sha256 c332e68004b987f7bfd7029a9b286f9deaf4eb951c033439c0a95c68cc99f0a3; scores score-zbase.txt); on the laptop (host cedar, kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5 (linux fork 2a650d74, installed and loaded alike), stock firmware, tool ~/sgxfive-test-t10 (t10, sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, built from resgx545 a581c06), every job one process of the kit runner (kit/run_stage.sh), a debugfs reset and the health fill and triangle between jobs, every output and dump kept gzipped; the rows are tables/STAGE.txt, the frozen predictions predictions/STAGE.tsv (gen/z13.py)); freezes: FROZEN.sha256 c332e68004b987f7bfd7029a9b286f9deaf4eb951c033439c0a95c68cc99f0a3 (65 files), PREDICTIONS.sha256 0e47810585de730f38b713e06fb1fa802b19b58b597cce415b00024dce83b4e8 (3 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at 05b7039e, resgx545:tools/closing/kit/lib_kit.sh at 05b7039e, resgx545:tools/closing/kit/run_stage.sh at 05b7039e, resgx545:tools/closing/kit/kitscore.py at 05b7039e, resgx545:tools/closing/kit/fake/sudo at 05b7039e, resgx545:tools/closing/kit/fake/timeout at 05b7039e, resgx545:tools/closing/kit/fake/df at 05b7039e, resgx545:tools/closing/kit/fake/modinfo at 05b7039e, resgx545:tools/closing/kit/fake/sha256sum at 05b7039e, resgx545:tools/closing/kit/fake/tool.sh at 05b7039e, resgx545:tools/closing/kit/fake/tool.py at 05b7039e, resgx545:tools/closing/kit/fake/ssh.py at 05b7039e, resgx545:tools/closing/scorekit.py at 05b7039e, resgx545:tools/closing/sessioncheck.py at 05b7039e, data:render/closing-r9-x/out/20261113-081821/zls/z243-ctl.depth-store.1.bin.gz at 75d01ee2, data:render/closing-r9-x/out/20261113-081821/zls/z243-ctl.txt.gz at 75d01ee2, data:render/closing-r9-x/out/20261113-081821/zls/z242-c-f0.depth.1.bin.gz at 75d01ee2, data:render/closing-r9-x/out/20261113-081821/zls/z242-c-f0.txt.gz at 75d01ee2, data:render/closing-r10-x/out/20261113-101116/dcmp/eq-m0.depth-store.1.bin.gz at 75d01ee2, data:render/closing-r10-x/out/20261113-101116/dcmp/eq-m0.txt.gz at 75d01ee2, data:render/closing-r10-x/out/20261113-101116/zbits/zb-clr-f0.depth.1.bin.gz at 75d01ee2, data:render/closing-r10-x/out/20261113-101116/zbits/zb-clr-f0.txt.gz at 75d01ee2, data:render/closing-r10-st1/out/20261113-103934/st1/st1-b0.txt.gz at 75d01ee2, data:render/closing-r10-st1/out/20261113-103934/st1/q071-b0.txt.gz at 75d01ee2, data:render/closing-r10-zls/out/20261113-102039/zst2/z2y-f6.depth.1.bin.gz at 75d01ee2, data:render/closing-r10-zls/out/20261113-102039/zst2/z2y-f6.txt.gz at 75d01ee2, data:render/closing-r10-zls/out/20261113-102039/zst2/z2y-f0.depth.1.bin.gz at 75d01ee2, data:render/closing-r10-zls/out/20261113-102039/zst2/z2x-f7-s00.depth.1.bin.gz at 75d01ee2, data:render/closing-r10-zls/out/20261113-102039/zst2/z2x-f7-sff.depth.1.bin.gz at 75d01ee2, data:cited/closing11/plan/c7-q120/c7_rule.py at 75d01ee2, data:render/closing-r9-x/tables/zls.txt at 75d01ee2, data:render/closing-r10-x/tables/dcmp.txt at 75d01ee2, data:render/closing-r10-x/tables/zbits.txt at 75d01ee2, data:render/closing-r10-st1/tables/st1.txt at 75d01ee2, data:render/closing-r10-zls/tables/zst2.txt at 75d01ee2, data:render/closing-r10-st1/lead/build_tool10.sh at 75d01ee2, resgx545:userspace/libsgxfive/tools/sgxfive-test.c at 05b7039e, resgx545:crates/sgx-pipe/src/zls.rs at 05b7039e, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=B60AB0B475DD1E8972419B5; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW"]
date = "2026-11-13"
data = ["render-closing-r13-zls:out/20261113-213117/zbase/", "render-closing-r13-zls:fold/"]
terms = ["CR_ISP_ZLSCTL", "CR_ISP_ZLOAD_BASE", "CR_ISP_ZSTORE_BASE"]
+++
**What ran.** E977's z243 rows (64 x 32, --tri-full at 0.5, ZLS control 0x0017500e: the depth
loaded, stored, G 1) with `--poke blk:1=0x00000200` (depth test never, E467's form: the store holds
what was loaded), `--depth-fill index`, `--depth-store` filled 0x3e800000 and `--depth-pages 20`,
and `--kpoke-render 1:rd:12=0x1000 + m`. t10 arms its own pokes first (rd:12 = 0x1000, rd:13 =
0x15000; lead/dryrun_checks.out), and every job printed the depth buffer at 0x3e001000 and the store
at 0x3e015000 (hook_check), so the poked value is the load base. Moves m: +0x1000, +0x4000,
+0x10000, the store's own base (zb-mst, fills swapped), +0x800, +0x40 and +4. Controls: zb-c-ctl
(E977's z243-ctl with rd:12 re-poked to its own value), zb-c-eq0 (E995's eq-m0), zb-c-id (this form,
rd:12 its own), zb-c-off (a +0x1000 move with the load bits 1 and 14 cleared).

**Frozen verdict (as printed).** attempt 20261113-213117, stage zbase (run.log): `SUMMARY: zbase:
H-ALIGN4K is not supported: 5 held, 2 FAILED, 0 cannot tell of 7`; attempt 20261113-213117, stage
zbase (run.log): `SUMMARY: zbase: H-ALIGNTILE is not supported: 6 held, 1 FAILED, 0 cannot tell of
7`; attempt 20261113-213117, stage zbase (run.log): `SUMMARY: zbase: H-MOVED is not supported: 6
held, 1 FAILED, 0 cannot tell of 7`; attempt 20261113-213117, stage zbase (run.log): `SUMMARY:
zbase: H-STOREBASE is not supported: 1 held, 6 FAILED, 0 cannot tell of 7`; attempt 20261113-213117,
stage zbase (run.log): `SUMMARY: zbase: H-UNMOVED is not supported: 1 held, 6 FAILED, 0 cannot tell
of 7`.

**Results [HW].** Controls: zb-c-ctl drew 2048 and its store is E977's kept dump byte for byte,
zb-c-eq0 drew 0 and is E995's byte for byte, zb-c-id stored the identity and zb-c-off 1.0 at all
2048 dwords, the rest of each store its fill. Rows (score-zbase.txt), the store's dword k holding
the depth buffer's dword k + d at all 2048 dwords of every row: +0x1000 d = 1024, +0x4000 4096,
+0x10000 16384, +0x800 512, +0x40 16, the store's own base its own index (read before written), +4 d
= 0. No row drew a pixel and no job faulted. Post hoc (fold/look.py): of the power-of-two granules,
8, 16, 32 and 64 bytes give all seven offsets as the base rounded down, 4 and 128 and up do not.

**What it shows.** The load base is its own register: a load at an address other than the store's
reads E465's tiled layout from it, at any page and tile offset, as the store would write it there,
and a load and store at one address read each tile before it is written. Its low bits are dropped:
+4 bytes is ignored and +64 is kept [post hoc: a granule of 8 to 64 bytes]. The frozen H-MOVED named
a byte-exact base and fails on that one row, so Q243's last clause narrows to the granule.

**What it does not show.** The granule (8, 16, 32 or 64 bytes: +8, +16 and +32 did not run); a moved
base with an integer format, with a stencil load or a moved stencil load base (rd:14), at another
pitch than G 1, past the mapped buffer (no row read outside it), and the moved base under a depth
test other than never.
