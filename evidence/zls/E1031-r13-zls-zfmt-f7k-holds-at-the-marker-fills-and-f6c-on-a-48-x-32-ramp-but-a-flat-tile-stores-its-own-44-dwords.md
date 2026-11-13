+++
id = "E1031"
claim = "r13-zls stage zfmt (6 jobs, t10): E1015's format-7 template F7K holds held out at the stencil fills 0x3f and 0x1f, equal to its markers (48 of 48 dwords each, no other dword changed; the fixed-byte rival 0 of 48), and its format-6 groups F6C hold on a 48 x 32 y ramp of another origin (8 of 8 groups of its two full tiles, F6RAW 0 of 8; the edge tiles' 152 dwords undecoded) but fail on a flat 0.5 where every row of every tile is one depth (0 of 16 groups, F6RAW 0): there each 512-dword block holds the same 44 dwords (post hoc, fold/look.py), no rule fitted; the z2y-f6 rerun is E986's dump byte for byte"
unit = "zls"
method = "r13-zls (render/closing-r13-zls), stage zfmt of the question-closing pass (round 13, decisions R13-1 (a), R13-8 (a) and R13-10 (a) of closing13/DECISIONS-R13.md, plan closing13/plan/rank-round13.md sections 2 and 3), dataset render-closing-r13-zls; attempt out/20261113-213117 (zfmt 21:34:05 Mac time; driver log run.log; its freeze FROZEN.sha256 c332e68004b987f7bfd7029a9b286f9deaf4eb951c033439c0a95c68cc99f0a3; scores score-zfmt.txt); on the laptop (host cedar, kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5 (linux fork 2a650d74, installed and loaded alike), stock firmware, tool ~/sgxfive-test-t10 (t10, sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, built from resgx545 a581c06), every job one process of the kit runner (kit/run_stage.sh), a debugfs reset and the health fill and triangle between jobs, every output and dump kept gzipped; the rows are tables/STAGE.txt, the frozen predictions predictions/STAGE.tsv (gen/z13.py)); freezes: FROZEN.sha256 c332e68004b987f7bfd7029a9b286f9deaf4eb951c033439c0a95c68cc99f0a3 (65 files), PREDICTIONS.sha256 0e47810585de730f38b713e06fb1fa802b19b58b597cce415b00024dce83b4e8 (3 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at 05b7039e, resgx545:tools/closing/kit/lib_kit.sh at 05b7039e, resgx545:tools/closing/kit/run_stage.sh at 05b7039e, resgx545:tools/closing/kit/kitscore.py at 05b7039e, resgx545:tools/closing/kit/fake/sudo at 05b7039e, resgx545:tools/closing/kit/fake/timeout at 05b7039e, resgx545:tools/closing/kit/fake/df at 05b7039e, resgx545:tools/closing/kit/fake/modinfo at 05b7039e, resgx545:tools/closing/kit/fake/sha256sum at 05b7039e, resgx545:tools/closing/kit/fake/tool.sh at 05b7039e, resgx545:tools/closing/kit/fake/tool.py at 05b7039e, resgx545:tools/closing/kit/fake/ssh.py at 05b7039e, resgx545:tools/closing/scorekit.py at 05b7039e, resgx545:tools/closing/sessioncheck.py at 05b7039e, data:render/closing-r9-x/out/20261113-081821/zls/z243-ctl.depth-store.1.bin.gz at 75d01ee2, data:render/closing-r9-x/out/20261113-081821/zls/z243-ctl.txt.gz at 75d01ee2, data:render/closing-r9-x/out/20261113-081821/zls/z242-c-f0.depth.1.bin.gz at 75d01ee2, data:render/closing-r9-x/out/20261113-081821/zls/z242-c-f0.txt.gz at 75d01ee2, data:render/closing-r10-x/out/20261113-101116/dcmp/eq-m0.depth-store.1.bin.gz at 75d01ee2, data:render/closing-r10-x/out/20261113-101116/dcmp/eq-m0.txt.gz at 75d01ee2, data:render/closing-r10-x/out/20261113-101116/zbits/zb-clr-f0.depth.1.bin.gz at 75d01ee2, data:render/closing-r10-x/out/20261113-101116/zbits/zb-clr-f0.txt.gz at 75d01ee2, data:render/closing-r10-st1/out/20261113-103934/st1/st1-b0.txt.gz at 75d01ee2, data:render/closing-r10-st1/out/20261113-103934/st1/q071-b0.txt.gz at 75d01ee2, data:render/closing-r10-zls/out/20261113-102039/zst2/z2y-f6.depth.1.bin.gz at 75d01ee2, data:render/closing-r10-zls/out/20261113-102039/zst2/z2y-f6.txt.gz at 75d01ee2, data:render/closing-r10-zls/out/20261113-102039/zst2/z2y-f0.depth.1.bin.gz at 75d01ee2, data:render/closing-r10-zls/out/20261113-102039/zst2/z2x-f7-s00.depth.1.bin.gz at 75d01ee2, data:render/closing-r10-zls/out/20261113-102039/zst2/z2x-f7-sff.depth.1.bin.gz at 75d01ee2, data:cited/closing11/plan/c7-q120/c7_rule.py at 75d01ee2, data:render/closing-r9-x/tables/zls.txt at 75d01ee2, data:render/closing-r10-x/tables/dcmp.txt at 75d01ee2, data:render/closing-r10-x/tables/zbits.txt at 75d01ee2, data:render/closing-r10-st1/tables/st1.txt at 75d01ee2, data:render/closing-r10-zls/tables/zst2.txt at 75d01ee2, data:render/closing-r10-st1/lead/build_tool10.sh at 75d01ee2, resgx545:userspace/libsgxfive/tools/sgxfive-test.c at 05b7039e, resgx545:crates/sgx-pipe/src/zls.rs at 05b7039e, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=B60AB0B475DD1E8972419B5; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW"]
date = "2026-11-13"
data = ["render-closing-r13-zls:out/20261113-213117/zfmt/", "render-closing-r13-zls:fold/"]
terms = ["CR_ISP_ZLSCTL"]
+++
**What ran.** E986's zst2 form on t10 (64 x 32, the stencil loaded and stored, --poke
blk:1=0x00400200): format 7 (0x0717300e) on E986's x ramp under the stencil fills 0x3f3f3f3f and
0x1f1f1f1f; format 6 (0x0617300e) on a 48 x 32 y ramp at depths 0.375, 0.375, 0.875 with its
format-0 reference (zf-y48-f0, a reading row: F6C's row values), and on a flat 0.5 at 64 x 32 (v =
0x3f000000 every row). Control: zf-y6-ctl, E986's z2y-f6 rerun.

**Frozen verdict (as printed).** attempt 20261113-213117, stage zfmt (run.log): `SUMMARY: zfmt: F6C
is not supported: 1 held, 1 FAILED, 0 cannot tell of 2`; attempt 20261113-213117, stage zfmt
(run.log): `SUMMARY: zfmt: F6RAW is not supported: 0 held, 2 FAILED, 0 cannot tell of 2`; attempt
20261113-213117, stage zfmt (run.log): `SUMMARY: zfmt: F7K (2 of 2 rows decided)`; attempt
20261113-213117, stage zfmt (run.log): `SUMMARY: zfmt: F7K-FIX is not supported: 0 held, 2 FAILED, 0
cannot tell of 2`.

**Results [HW].** Control: 212 changed dwords, byte for byte E986's. zf-7k-3f and zf-7k-1f: the 48
predicted dwords equal, no other dword changed; with S fixed at 0xa5, 0 of 48. zf-y48-f6:
zf-y48-f0's tile rows are constant in the two full tiles (32 rows) and in neither edge tile (x 32 to
63, past the target at 48), so F6C applies to all four groups of blocks 0 and 1: 8 of 8 equal, F6RAW
0; the 152 other changed dwords are the edge tiles' blocks. zf-flat-f6: 176 changed dwords, 44 at
the start of each block and the four blocks alike (bytes 0 to 159 a stream of 0x00, 0x3f, 0x9e and
0xc0, 160 to 175 zero), F6C 0 of 16 groups.

**What it shows.** F7K's S is the fill byte even where it equals a marker, at four fills now; F6C
holds at another size and origin where the groups' rows differ from one another. A tile of one depth
is not four F6C groups: it has its own 44-dword form [infer: the run or plane compression E1015
inferred takes another shape when the rows repeat each other].

**What it does not show.** The flat block's layout and how it depends on the depth; format 7 under a
varying stencil; format 5 under constant rows; format 6's edge tiles (the 152 dwords past 48) and
its variable-length runs; any packed format without a stencil buffer.
