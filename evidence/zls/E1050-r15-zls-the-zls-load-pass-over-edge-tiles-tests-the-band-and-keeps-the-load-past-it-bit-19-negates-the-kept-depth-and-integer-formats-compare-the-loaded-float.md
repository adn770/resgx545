+++
id = "E1050"
claim = "r15-zls rows zp- (Q297, 13 jobs in stages zpass and zbits3, t10): over 34 x 18 edge tiles the ZLS load pass tests E831's band against the loaded depth and the loaded stencil and keeps the loaded value past it (frozen H-EDGE 1 of 1 in each stage, 2048 of 2048 dwords and bytes; the clear past the band and edge tiles without a load failed); with bit 19 and a load every stored depth is negated, the kept loaded one too (frozen H-19-RENEG 2 of 2, never and less; H-19-ABS failed 2 of 2); formats 1 and 2 under a load compare the loaded dword as a float and store the floor rule of the depth kept or drawn (frozen H-INT-PASS 2 of 2; the integer reading of the word failed 2 of 2); triangle depths 0, 0.75 and 1 over loaded 0.25 / 0.75 halves are tested strictly less (frozen H-PASS-Z 3 of 4, H-PASS-LE refuted at 0.75: 0 drawn), and at 0.125 both models drew the frozen 2048 pixels but the flat plane stored 1 to 9 ulps below 0.125 (post hoc, fold/look.py), so H-PASS-Z failed that row on the stored floats; all seven controls passed"
unit = "zls"
method = "r15-zls (render/closing-r15-zls), stages zpass, zbits3 of the question-closing pass (round 15, decisions R15-1 (a), R15-6 (a), R15-7 (a) and R15-8 (a): session r15-zls of the round 15 plan, safe class only), dataset render-closing-r15-zls; attempt out/20261114-073826 (zpass 07:38:26, zbits3 07:39:44 Mac time; driver log run.log; its freeze FROZEN.sha256 91c07e1745e3746d5baca61a9530ff02bb5fa4715d1106f18750f95606115029; scores score-zbits3.txt, score-zpass.txt); on the laptop (host cedar, kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5 (linux fork 2a650d74, installed and loaded alike), stock firmware, tool ~/sgxfive-test-t10 (t10, sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, built from resgx545 a581c06), every job one process of the kit runner (kit/run_stage.sh), a debugfs reset and the health fill and triangle between jobs, every output and dump kept gzipped; the rows are tables/STAGE.txt, grouped by the dump their scorer reads, a row's name prefix naming its record (zp- E1050, zv- E1051, zb3- E1053, zl2- E1054), the frozen predictions predictions/STAGE.tsv (gen/z15.py)); freezes: FROZEN.sha256 91c07e1745e3746d5baca61a9530ff02bb5fa4715d1106f18750f95606115029 (92 files), PREDICTIONS.sha256 f287dba043ba6f7286b43414356bd7971836dab499ade6948b8eb5cb2cca4391 (4 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at 158bdc54, resgx545:tools/closing/kit/lib_kit.sh at 158bdc54, resgx545:tools/closing/kit/run_stage.sh at 158bdc54, resgx545:tools/closing/kit/kitscore.py at 158bdc54, resgx545:tools/closing/kit/fake/sudo at 158bdc54, resgx545:tools/closing/kit/fake/timeout at 158bdc54, resgx545:tools/closing/kit/fake/df at 158bdc54, resgx545:tools/closing/kit/fake/modinfo at 158bdc54, resgx545:tools/closing/kit/fake/sha256sum at 158bdc54, resgx545:tools/closing/kit/fake/tool.sh at 158bdc54, resgx545:tools/closing/kit/fake/tool.py at 158bdc54, resgx545:tools/closing/kit/fake/ssh.py at 158bdc54, resgx545:tools/closing/scorekit.py at 158bdc54, resgx545:tools/closing/sessioncheck.py at 158bdc54, data:render/closing-r13-zls/out/20261113-213117/zbase/zb-c-id.depth-store.1.bin.gz at cddc7b60, data:render/closing-r13-zls/out/20261113-213117/zbase/zb-c-id.txt.gz at cddc7b60, data:render/closing-r14-zls/out/20261114-054846/zbits2/zb2-c-base.stencil-store.1.bin.gz at cddc7b60, data:render/closing-r14-zls/out/20261114-054846/zbits2/zb2-c-base.txt.gz at cddc7b60, data:render/closing-r14-zls/out/20261114-054846/zbits2/zb2-c-set.stencil-store.1.bin.gz at cddc7b60, data:render/closing-r14-zls/out/20261114-054846/zbits2/zb2-c-set.txt.gz at cddc7b60, data:render/closing-r14-zls/out/20261114-054846/zbits2/zb2-b23.stencil-store.1.bin.gz at cddc7b60, data:render/closing-r14-zls/out/20261114-054846/zbits2/zb2-b23.txt.gz at cddc7b60, data:render/closing-r14-zls/out/20261114-054846/zbits2/zb2-b15.stencil-store.1.bin.gz at cddc7b60, data:render/closing-r14-zls/out/20261114-054846/zbits2/zb2-b15.txt.gz at cddc7b60, data:render/closing-r14-zls/out/20261114-054846/zbits2/zb2-g21-23.stencil-store.1.bin.gz at cddc7b60, data:render/closing-r14-zls/out/20261114-054846/zbits2/zb2-g21-23.txt.gz at cddc7b60, data:render/closing-r14-zls/out/20261114-054846/zflat/zl-f5-flat.depth.1.bin.gz at cddc7b60, data:render/closing-r14-zls/out/20261114-054846/zflat/zl-f6-0p25.depth.1.bin.gz at cddc7b60, data:render/closing-r14-zls/out/20261114-054846/zflat/zl-f6-0p1234.depth.1.bin.gz at cddc7b60, data:render/closing-r14-zls/out/20261114-054846/zodd/zo-g3.depth.1.bin.gz at cddc7b60, data:render/closing-r14-zls/out/20261114-054846/zodd/zo-g3.txt.gz at cddc7b60, data:render/closing-r14-zls/out/20261114-054846/zodd/zo-65-f0.depth.1.bin.gz at cddc7b60, data:render/closing-r14-zls/out/20261114-054846/zodd/zo-65-f1.depth.1.bin.gz at cddc7b60, data:render/closing-r14-zls/out/20261114-054846/zodd/zo-640-f0.depth.1.bin.gz at cddc7b60, data:render/closing-r14-zls/out/20261114-054846/zodd/zo-640-ov.depth.1.bin.gz at cddc7b60, data:render/closing-r13-zls/out/20261113-213117/zfmt/zf-flat-f6.depth.1.bin.gz at cddc7b60, data:render/closing-r10-zls/out/20261113-102039/zst2/z2y-f6.depth.1.bin.gz at cddc7b60, data:render/closing-r10-x/out/20261113-101116/zov/zov-64x32-g0.depth.1.bin.gz at cddc7b60, data:render/closing-r10-x/out/20261113-101116/zov/zov-64x32-g0-f1.depth.1.bin.gz at cddc7b60, data:render/closing-r10-x/out/20261113-101116/zov/zov-64x32-ctl.depth.1.bin.gz at cddc7b60, data:render/closing-r10-x/out/20261113-101116/zov/zov-160x48-ctl.depth.1.bin.gz at cddc7b60, data:render/closing-r10-x/out/20261113-101116/zov/zov-160x48-g2.depth.1.bin.gz at cddc7b60, data:render/closing-r9-z2/out/20261113-082522/z2/z2-b-f1.depth.1.bin.gz at cddc7b60, data:render/closing-r9-x/out/20261113-081821/zls/z243-ctl.depth-store.1.bin.gz at cddc7b60, data:render/closing-r9-x/out/20261113-081821/zls/z243-ctl.txt.gz at cddc7b60, data:render/closing-r9-x/out/20261113-081821/zls/z243-f1-less.depth-store.1.bin.gz at cddc7b60, data:render/closing-r9-x/out/20261113-081821/zls/z243-f1-less.txt.gz at cddc7b60, data:render/closing-r9-x/out/20261113-081821/zls/z243-f2-less.depth-store.1.bin.gz at cddc7b60, data:render/closing-r9-x/out/20261113-081821/zls/z243-f2-less.txt.gz at cddc7b60, data:render/closing-r10-st1/out/20261113-103934/st1/st1-e-b0.stencil-store.1.bin.gz at cddc7b60, data:render/closing-r10-st1/out/20261113-103934/st1/st1-e-b0.txt.gz at cddc7b60, data:render/closing-r10-x/out/20261113-101116/zov/zov-64x32-g0.txt.gz at cddc7b60, data:render/closing-r14-zls/out/20261114-054846/zodd/zo-65-f2.depth.1.bin.gz at cddc7b60, data:render/closing-r13-zls/tables/zbase.txt at cddc7b60, data:render/closing-r14-zls/tables/zbits2.txt at cddc7b60, data:render/closing-r14-zls/tables/zflat.txt at cddc7b60, data:render/closing-r14-zls/tables/zodd.txt at cddc7b60, data:render/closing-r13-zls/tables/zfmt.txt at cddc7b60, data:render/closing-r10-zls/tables/zst2.txt at cddc7b60, data:render/closing-r10-x/tables/zov.txt at cddc7b60, data:render/closing-r10-st1/tables/st1.txt at cddc7b60, data:render/closing-r10-st1/lead/build_tool10.sh at cddc7b60, resgx545:crates/sgx-pipe/src/zls.rs at 158bdc54, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=B60AB0B475DD1E8972419B5; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW"]
date = "2026-11-14"
data = ["render-closing-r15-zls:out/20261114-073826/zpass/", "render-closing-r15-zls:out/20261114-073826/zbits3/", "render-closing-r15-zls:fold/"]
terms = ["CR_ISP_ZLSCTL", "CR_ISP_ZLOAD_BASE"]
+++
**What ran.** E1029's zbase form (`--tri-full`, `--depth --depth-store`, `--depth-pages 20`, the
depth buffer filled `bit:K`: 0.75f where bit K of the dword index is set, else 0.25f) with the load
and store enables 0x0017500e at G 1 and the depth test less (blk:1 0x00400200) or never: zp-e-dp at
34 x 18 (bit:3), zp-19-nv and zp-19-ls with bit 19 (0x001f500e, bit:9), zp-f1 and zp-f2 in formats 1
and 2 at a triangle depth of 0.375, zp-z0, zp-z125, zp-z75 and zp-z1 at 0, 0.125, 0.75 and 1 over
bit:9's tile halves. In stage zbits3, zp-e-st: E988's st1 form (the stencil loaded from the `bytes`
fill and stored, ISP word 2 0x040501ff) at 34 x 18. The plan's 0.1 and 0.3 ran as 0.125 and 0.375
(README deviation 3). Controls: zp-c-id (E1029's zb-c-id), zp-c-467 (E467's pass at 256 x 128 G 7
on t10, bit:9), zp-c-band (34 x 18 without a load), and zbits3's four.

**Frozen verdict (as printed).** attempt 20261114-073826, stage zpass (run.log): `SUMMARY: zpass:
H-19-ABS is not supported: 0 held, 2 FAILED, 0 cannot tell of 2`; attempt 20261114-073826, stage
zpass (run.log): `SUMMARY: zpass: H-19-RENEG (2 of 2 rows decided)`; attempt 20261114-073826, stage
zpass (run.log): `SUMMARY: zpass: H-EDGE (1 of 1 rows decided)`; attempt 20261114-073826, stage
zpass (run.log): `SUMMARY: zpass: H-EDGE-CLEAR is not supported: 0 held, 1 FAILED, 0 cannot tell of
1`; attempt 20261114-073826, stage zpass (run.log): `SUMMARY: zpass: H-EDGE-SKIP is not supported: 0
held, 1 FAILED, 0 cannot tell of 1`; attempt 20261114-073826, stage zpass (run.log): `SUMMARY:
zpass: H-INT-PASS (2 of 2 rows decided)`; attempt 20261114-073826, stage zpass (run.log): `SUMMARY:
zpass: H-INT-WORD is not supported: 0 held, 2 FAILED, 0 cannot tell of 2`; attempt 20261114-073826,
stage zpass (run.log): `SUMMARY: zpass: H-PASS-LE is not supported: 2 held, 2 FAILED, 0 cannot tell
of 4`; attempt 20261114-073826, stage zpass (run.log): `SUMMARY: zpass: H-PASS-Z is not supported: 3
held, 1 FAILED, 0 cannot tell of 4`; attempt 20261114-073826, stage zbits3 (run.log): `SUMMARY:
zbits3: H-EDGE (1 of 1 rows decided)`; attempt 20261114-073826, stage zbits3 (run.log): `SUMMARY:
zbits3: H-EDGE-CLEAR is not supported: 0 held, 1 FAILED, 0 cannot tell of 1`; attempt
20261114-073826, stage zbits3 (run.log): `SUMMARY: zbits3: H-EDGE-SKIP is not supported: 0 held, 1
FAILED, 0 cannot tell of 1`.

**Results [HW].** Controls: zp-c-id byte for byte E1029's kept store; zp-c-467 32768 of 32768
dwords and 16384 drawn; zp-c-band 2048 of 2048 dwords (0.5 in E831's band, 1.0 past it) and 612
drawn; zbits3's controls passed. zp-e-dp 2048 of 2048 dwords and 288 drawn under H-EDGE
(H-EDGE-CLEAR
924, H-EDGE-SKIP 696); zp-e-st 2048 of 2048 bytes and 306 drawn (H-EDGE-CLEAR 926, H-EDGE-SKIP 518).
zp-19-nv stored 0xbe800000 and 0xbf400000, the loaded floats negated, zp-19-ls 0xbf000000 where it
drew (1024) and 0xbe800000 elsewhere. zp-f1 stored 0x400000 and 0x600000, zp-f2 0x40004000 and
0x60006000, 1024 drawn each. zp-z0 stored 0 at every dword (2048 drawn), zp-z75 and zp-z1 drew none
and kept the load; zp-z125 drew 2048 and stored nine floats from 0x3dfffff7 to 0x3dffffff, 1 to 9
ulps below 0.125, decreasing with x and y alike (fold/look.py). sgx-pipe's `zls::pass` replays every
zpass row dword for dword, zp-z125 fed its own stored floats as the plane
(tests/closing_r15_zls.rs).

**What it shows.** The load pass acts per stored dword as on whole tiles over edge tiles too:
the full-screen triangle's pixels in E831's band test the load, those past it keep it, for the
depth and the stencil alike. Bit 19 negates what the store writes, a loaded depth kept as it is
re-negated. An integer format's pass compares the loaded dword as a float (E977, E1040) and stores
by E991's floor rule. The test is strictly less at any depth of 0 to 1 (E995); what a flat plane
stores at 0.125 is the plane's own error (Q200's dyadic planes storing ulps below the exact plane)
[infer], not the pass's. With the edge-tile, bit-19 and integer clauses decided by held-out rows
and the depth clause by the drawn counts at four depths and the stores at three, every clause of
Q297's line is decided.

**What it does not show.** A non-dyadic triangle depth in a pass (0.1 and 0.3 did not run
here); the plane's error at 0.125 (Q200); a pass over overlapping tiles; a depth outside 0 to 1 in
a pass; the stencil test of a pass other than E988's EQUAL row.
