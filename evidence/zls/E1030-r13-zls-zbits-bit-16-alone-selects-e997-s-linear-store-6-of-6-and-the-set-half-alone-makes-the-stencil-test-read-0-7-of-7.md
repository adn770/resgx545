+++
id = "E1030"
claim = "r13-zls stage zbits (16 jobs, t10): of the ZLS control's bits 12, 16 and 20 cleared alone and in pairs, bit 16 alone turns E977's tiled ramp store into E997's linear image (frozen L-BIT-16 held 6 of 6 held-out rows, each dump byte for byte E977's or E997's; every other L rival failed), and none of the six makes the stencil test read 0 (1024 drawn each, E988's count), while bits 15, 21 to 23 and 27 to 31 set with 12, 16 and 20 kept set do (2048 drawn, every stored stencil byte 0xff: frozen Z-SET held 7 of 7, every other Z rival failed); post hoc (fold/look.py, 2048 of 2048 bytes each) bit 12 cleared makes the stencil load read a linear image of 64-byte rows and bit 16 cleared makes the stencil store one; all three controls passed"
unit = "zls"
method = "r13-zls (render/closing-r13-zls), stage zbits of the question-closing pass (round 13, decisions R13-1 (a), R13-8 (a) and R13-10 (a) of closing13/DECISIONS-R13.md, plan closing13/plan/rank-round13.md sections 2 and 3), dataset render-closing-r13-zls; attempt out/20261113-213117 (zbits 21:32:31 Mac time; driver log run.log; its freeze FROZEN.sha256 c332e68004b987f7bfd7029a9b286f9deaf4eb951c033439c0a95c68cc99f0a3; scores score-zbits.txt); on the laptop (host cedar, kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5 (linux fork 2a650d74, installed and loaded alike), stock firmware, tool ~/sgxfive-test-t10 (t10, sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, built from resgx545 a581c06), every job one process of the kit runner (kit/run_stage.sh), a debugfs reset and the health fill and triangle between jobs, every output and dump kept gzipped; the rows are tables/STAGE.txt, the frozen predictions predictions/STAGE.tsv (gen/z13.py)); freezes: FROZEN.sha256 c332e68004b987f7bfd7029a9b286f9deaf4eb951c033439c0a95c68cc99f0a3 (65 files), PREDICTIONS.sha256 0e47810585de730f38b713e06fb1fa802b19b58b597cce415b00024dce83b4e8 (3 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at 05b7039e, resgx545:tools/closing/kit/lib_kit.sh at 05b7039e, resgx545:tools/closing/kit/run_stage.sh at 05b7039e, resgx545:tools/closing/kit/kitscore.py at 05b7039e, resgx545:tools/closing/kit/fake/sudo at 05b7039e, resgx545:tools/closing/kit/fake/timeout at 05b7039e, resgx545:tools/closing/kit/fake/df at 05b7039e, resgx545:tools/closing/kit/fake/modinfo at 05b7039e, resgx545:tools/closing/kit/fake/sha256sum at 05b7039e, resgx545:tools/closing/kit/fake/tool.sh at 05b7039e, resgx545:tools/closing/kit/fake/tool.py at 05b7039e, resgx545:tools/closing/kit/fake/ssh.py at 05b7039e, resgx545:tools/closing/scorekit.py at 05b7039e, resgx545:tools/closing/sessioncheck.py at 05b7039e, data:render/closing-r9-x/out/20261113-081821/zls/z243-ctl.depth-store.1.bin.gz at 75d01ee2, data:render/closing-r9-x/out/20261113-081821/zls/z243-ctl.txt.gz at 75d01ee2, data:render/closing-r9-x/out/20261113-081821/zls/z242-c-f0.depth.1.bin.gz at 75d01ee2, data:render/closing-r9-x/out/20261113-081821/zls/z242-c-f0.txt.gz at 75d01ee2, data:render/closing-r10-x/out/20261113-101116/dcmp/eq-m0.depth-store.1.bin.gz at 75d01ee2, data:render/closing-r10-x/out/20261113-101116/dcmp/eq-m0.txt.gz at 75d01ee2, data:render/closing-r10-x/out/20261113-101116/zbits/zb-clr-f0.depth.1.bin.gz at 75d01ee2, data:render/closing-r10-x/out/20261113-101116/zbits/zb-clr-f0.txt.gz at 75d01ee2, data:render/closing-r10-st1/out/20261113-103934/st1/st1-b0.txt.gz at 75d01ee2, data:render/closing-r10-st1/out/20261113-103934/st1/q071-b0.txt.gz at 75d01ee2, data:render/closing-r10-zls/out/20261113-102039/zst2/z2y-f6.depth.1.bin.gz at 75d01ee2, data:render/closing-r10-zls/out/20261113-102039/zst2/z2y-f6.txt.gz at 75d01ee2, data:render/closing-r10-zls/out/20261113-102039/zst2/z2y-f0.depth.1.bin.gz at 75d01ee2, data:render/closing-r10-zls/out/20261113-102039/zst2/z2x-f7-s00.depth.1.bin.gz at 75d01ee2, data:render/closing-r10-zls/out/20261113-102039/zst2/z2x-f7-sff.depth.1.bin.gz at 75d01ee2, data:cited/closing11/plan/c7-q120/c7_rule.py at 75d01ee2, data:render/closing-r9-x/tables/zls.txt at 75d01ee2, data:render/closing-r10-x/tables/dcmp.txt at 75d01ee2, data:render/closing-r10-x/tables/zbits.txt at 75d01ee2, data:render/closing-r10-st1/tables/st1.txt at 75d01ee2, data:render/closing-r10-zls/tables/zst2.txt at 75d01ee2, data:render/closing-r10-st1/lead/build_tool10.sh at 75d01ee2, resgx545:userspace/libsgxfive/tools/sgxfive-test.c at 05b7039e, resgx545:crates/sgx-pipe/src/zls.rs at 05b7039e, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=B60AB0B475DD1E8972419B5; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW"]
date = "2026-11-13"
data = ["render-closing-r13-zls:out/20261113-213117/zbits/", "render-closing-r13-zls:fold/"]
terms = ["CR_ISP_ZLSCTL", "ISP2"]
+++
**What ran.** Stencil rows: E988's st1-b0 (64 x 32, the stencil loaded from the bytes fill, ISP word
2 EQUAL against mask 0x01 with SOP3 invert, `--isp2 0x040501ff`) with the control 0x0017300e's bits
12, 16 and 20 cleared alone and in pairs (6 rows) and with bits 15, 21 to 23 and 27 to 31 set
(zbs-set). Ramp rows: E977's z242-c-f0 (80 x 40, G 2, 0x00171014) with the same six clears.
Controls: zbs-base (E988's st1-b0), zbs-q071 (E989's q071-b0) and zbr-ctl (E977's z242-c-f0).

**Frozen verdict (as printed).** attempt 20261113-213117, stage zbits (run.log): `SUMMARY: zbits:
L-ALL is not supported: 3 held, 3 FAILED, 0 cannot tell of 6`; attempt 20261113-213117, stage zbits
(run.log): `SUMMARY: zbits: L-ANY is not supported: 3 held, 3 FAILED, 0 cannot tell of 6`; attempt
20261113-213117, stage zbits (run.log): `SUMMARY: zbits: L-BIT-12 is not supported: 2 held, 4
FAILED, 0 cannot tell of 6`; attempt 20261113-213117, stage zbits (run.log): `SUMMARY: zbits:
L-BIT-16 (6 of 6 rows decided)`; attempt 20261113-213117, stage zbits (run.log): `SUMMARY: zbits:
L-BIT-20 is not supported: 2 held, 4 FAILED, 0 cannot tell of 6`; attempt 20261113-213117, stage
zbits (run.log): `SUMMARY: zbits: L-PAIR-12+16 is not supported: 4 held, 2 FAILED, 0 cannot tell of
6`; attempt 20261113-213117, stage zbits (run.log): `SUMMARY: zbits: L-PAIR-12+20 is not supported:
2 held, 4 FAILED, 0 cannot tell of 6`; attempt 20261113-213117, stage zbits (run.log): `SUMMARY:
zbits: L-PAIR-16+20 is not supported: 4 held, 2 FAILED, 0 cannot tell of 6`; attempt
20261113-213117, stage zbits (run.log): `SUMMARY: zbits: Z-ALL is not supported: 6 held, 1 FAILED, 0
cannot tell of 7`; attempt 20261113-213117, stage zbits (run.log): `SUMMARY: zbits: Z-ANY is not
supported: 0 held, 7 FAILED, 0 cannot tell of 7`; attempt 20261113-213117, stage zbits (run.log):
`SUMMARY: zbits: Z-BIT-12 is not supported: 3 held, 4 FAILED, 0 cannot tell of 7`; attempt
20261113-213117, stage zbits (run.log): `SUMMARY: zbits: Z-BIT-16 is not supported: 3 held, 4
FAILED, 0 cannot tell of 7`; attempt 20261113-213117, stage zbits (run.log): `SUMMARY: zbits:
Z-BIT-20 is not supported: 3 held, 4 FAILED, 0 cannot tell of 7`; attempt 20261113-213117, stage
zbits (run.log): `SUMMARY: zbits: Z-PAIR-12+16 is not supported: 5 held, 2 FAILED, 0 cannot tell of
7`; attempt 20261113-213117, stage zbits (run.log): `SUMMARY: zbits: Z-PAIR-12+20 is not supported:
5 held, 2 FAILED, 0 cannot tell of 7`; attempt 20261113-213117, stage zbits (run.log): `SUMMARY:
zbits: Z-PAIR-16+20 is not supported: 5 held, 2 FAILED, 0 cannot tell of 7`; attempt
20261113-213117, stage zbits (run.log): `SUMMARY: zbits: Z-SET (7 of 7 rows decided)`.

**Results [HW].** Controls: zbs-base drew 1024, zbs-q071 2048, zbr-ctl 4608 changed dwords byte for
byte E977's dump. Ramp rows: zbr-c16, zbr-c12-16 and zbr-c16-20 are byte for byte E997's linear
zb-clr-f0, zbr-c12, zbr-c20 and zbr-c12-20 byte for byte E977's tiled dump (4608 changed each).
Stencil rows: the six clears drew 1024 each; the image is zbs-base's with bit 12 set and another
with bit 12 cleared (columns of even x, not rows of even y); zbs-set drew 2048. Post hoc
(fold/look.py), reading each stored stencil byte as the loaded one inverted where the pixel drew:
with bit 12 cleared the loaded byte of pixel (x, y) is byte 64 y + x of the buffer, with bit 16
cleared the store writes it at byte 64 y + x, with both both, 2048 of 2048 bytes in each of the
seven clear rows (E988's in-tile order elsewhere); zbs-set stored 0xff at every byte, as E989.

**What it shows.** Bit 16 is the linear store of E997 (the depth, and [post hoc] the stencil); bit
20 changes nothing seen alone or paired; bit 12 changes the order the stencil load reads, not the
depth store [post hoc]. The test's read of 0 under E989's word comes from the set half (15, 21 to
23, 27 to 31), not from 12, 16 and 20, though E411 and E997 saw that half inert without a stencil
test. sgx-pipe's zls models bit 16's store and the stencil source of the words that ran
(tests/closing_r13_zls.rs replays all 16 rows).

**What it does not show.** Which bit of the set half reads 0; the rows of the linear stencil images
at another pitch (64 bytes is both the width and 32 (G + 1) here); bit 12 with a depth load; bit 16
with a depth load or the 16-bit format; bit 0 under other controls; what bit 20 does.
