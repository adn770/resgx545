+++
id = "E1042"
claim = "r14-zls rows zb2- (Q071, 20 jobs in stages zbits2, zgran and zodd, t10): no frozen model of the set half held all 11 rows (best Z-ONE-23 and Z-GRP-21-23, 9 of 11): bits 21 to 23 set together make E988's stencil test read 0 (2048 drawn, every stored byte 0xff) while 21, 22 and 27 to 31 alone and 27 to 31 together change nothing (1024 drawn, E988's image), and post hoc bit 15 alone fails the test at every pixel (0 drawn, the loaded bytes stored unchanged) and bit 23 alone has it read a value of x mod 16 (1536 drawn, 0x00, 0x80 or 0x3f by column), not the loaded byte; the linear stencil images have rows of 32 (G + 1) bytes (frozen P-G 4 of 4 at 96 x 32 and 64 x 32, G 2; P-64 failed 4, the width 2); bit 12 cleared with a depth load reads the depth linearly, pixel (x, y) at dword 64 y + x (frozen H-DEPTH-LIN 1 of 1, 2048 of 2048); bit 16 cleared on the 16-bit format stores a linear image of 16-bit values, halfword 96 y + x at G 2 (frozen L16-HALF 1 of 1, 2304 of 2304); all five controls passed"
unit = "zls"
method = "r14-zls (render/closing-r14-zls), stages zbits2, zgran, zodd of the question-closing pass (round 14, decisions R14-1 (a), R14-7 (a), R14-9 (a) and R14-10 (a): session r14-zls of the round 14 plan, safe class only), dataset render-closing-r14-zls; attempt out/20261114-054846 (zgran 05:48:47, zodd 05:49:59, zbits2 05:51:21 Mac time; driver log run.log; its freeze FROZEN.sha256 9279b1fe886c085b630c81e36dc7be61f2252f374d81ed10c32db8c91709ce45; scores score-zbits2.txt, score-zgran.txt, score-zodd.txt); on the laptop (host cedar, kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5 (linux fork 2a650d74, installed and loaded alike), stock firmware, tool ~/sgxfive-test-t10 (t10, sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, built from resgx545 a581c06), every job one process of the kit runner (kit/run_stage.sh), a debugfs reset and the health fill and triangle between jobs, every output and dump kept gzipped; the rows are tables/STAGE.txt, grouped by the dump their scorer reads, a row's name prefix naming its record (zg- E1040, zo- E1041, zb2- E1042, zl- E1043), the frozen predictions predictions/STAGE.tsv (gen/z14.py)); freezes: FROZEN.sha256 9279b1fe886c085b630c81e36dc7be61f2252f374d81ed10c32db8c91709ce45 (86 files), PREDICTIONS.sha256 f4d7d7697e09afbfbb86bc512d1e129a6de18812cdf13f6ea3c4d5351f5be4b6 (4 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at dddadbdd, resgx545:tools/closing/kit/lib_kit.sh at dddadbdd, resgx545:tools/closing/kit/run_stage.sh at dddadbdd, resgx545:tools/closing/kit/kitscore.py at dddadbdd, resgx545:tools/closing/kit/fake/sudo at dddadbdd, resgx545:tools/closing/kit/fake/timeout at dddadbdd, resgx545:tools/closing/kit/fake/df at dddadbdd, resgx545:tools/closing/kit/fake/modinfo at dddadbdd, resgx545:tools/closing/kit/fake/sha256sum at dddadbdd, resgx545:tools/closing/kit/fake/tool.sh at dddadbdd, resgx545:tools/closing/kit/fake/tool.py at dddadbdd, resgx545:tools/closing/kit/fake/ssh.py at dddadbdd, resgx545:tools/closing/scorekit.py at dddadbdd, resgx545:tools/closing/sessioncheck.py at dddadbdd, data:render/closing-r9-x/out/20261113-081821/zls/z243-ctl.depth-store.1.bin.gz at 3309b5fd, data:render/closing-r9-x/out/20261113-081821/zls/z243-ctl.txt.gz at 3309b5fd, data:render/closing-r9-x/out/20261113-081821/zls/z243-f1-less.depth-store.1.bin.gz at 3309b5fd, data:render/closing-r9-x/out/20261113-081821/zls/z243-f2-less.depth-store.1.bin.gz at 3309b5fd, data:render/closing-r9-x/out/20261113-081821/zls/z242-c-f0.depth.1.bin.gz at 3309b5fd, data:render/closing-r9-x/out/20261113-081821/zls/z242-c-f1.depth.1.bin.gz at 3309b5fd, data:render/closing-r9-x/out/20261113-081821/zls/z242-c-f2.depth.1.bin.gz at 3309b5fd, data:render/closing-r13-zls/out/20261113-213117/zbase/zb-m4.depth-store.1.bin.gz at 3309b5fd, data:render/closing-r13-zls/out/20261113-213117/zbase/zb-m4.txt.gz at 3309b5fd, data:render/closing-r13-zls/out/20261113-213117/zbase/zb-m40.depth-store.1.bin.gz at 3309b5fd, data:render/closing-r13-zls/out/20261113-213117/zbits/zbs-base.txt.gz at 3309b5fd, data:render/closing-r13-zls/out/20261113-213117/zbits/zbs-base.stencil-store.1.bin.gz at 3309b5fd, data:render/closing-r13-zls/out/20261113-213117/zbits/zbs-c12.txt.gz at 3309b5fd, data:render/closing-r13-zls/out/20261113-213117/zbits/zbs-c12.stencil-store.1.bin.gz at 3309b5fd, data:render/closing-r13-zls/out/20261113-213117/zbits/zbs-c16.txt.gz at 3309b5fd, data:render/closing-r13-zls/out/20261113-213117/zbits/zbs-c16.stencil-store.1.bin.gz at 3309b5fd, data:render/closing-r13-zls/out/20261113-213117/zbits/zbs-set.txt.gz at 3309b5fd, data:render/closing-r13-zls/out/20261113-213117/zbits/zbs-set.stencil-store.1.bin.gz at 3309b5fd, data:render/closing-r13-zls/out/20261113-213117/zbits/zbr-c16.depth.1.bin.gz at 3309b5fd, data:render/closing-r13-zls/out/20261113-213117/zfmt/zf-flat-f6.depth.1.bin.gz at 3309b5fd, data:render/closing-r13-zls/out/20261113-213117/zfmt/zf-flat-f6.txt.gz at 3309b5fd, data:render/closing-r10-x/out/20261113-101116/zov/zov-64x32-g0.depth.1.bin.gz at 3309b5fd, data:render/closing-r10-x/out/20261113-101116/zov/zov-64x32-g0.txt.gz at 3309b5fd, data:render/closing-r10-x/out/20261113-101116/zov/zov-64x32-ctl.depth.1.bin.gz at 3309b5fd, data:render/closing-r10-x/out/20261113-101116/zov/zov-256x64-ctl.depth.1.bin.gz at 3309b5fd, data:render/closing-r10-x/out/20261113-101116/zov/zov-256x64-g3.depth.1.bin.gz at 3309b5fd, data:render/closing-r10-x/out/20261113-101116/zbits/zb-clr-f0.depth.1.bin.gz at 3309b5fd, data:render/closing-r10-zls/out/20261113-102039/zst2/z2y-f6.depth.1.bin.gz at 3309b5fd, data:render/closing-r10-zls/out/20261113-102039/zst2/z2y-f7.depth.1.bin.gz at 3309b5fd, data:render/closing-r10-zls/out/20261113-102039/zst2/z2d-f7.depth.1.bin.gz at 3309b5fd, data:cited/closing11/plan/c7-q120/c7_rule.py at 3309b5fd, data:render/closing-r9-x/tables/zls.txt at 3309b5fd, data:render/closing-r10-x/tables/zov.txt at 3309b5fd, data:render/closing-r10-x/tables/zbits.txt at 3309b5fd, data:render/closing-r10-st1/tables/st1.txt at 3309b5fd, data:render/closing-r10-zls/tables/zst2.txt at 3309b5fd, data:render/closing-r13-zls/tables/zbase.txt at 3309b5fd, data:render/closing-r13-zls/tables/zbits.txt at 3309b5fd, data:render/closing-r13-zls/tables/zfmt.txt at 3309b5fd, data:render/closing-r10-st1/lead/build_tool10.sh at 3309b5fd, resgx545:userspace/libsgxfive/tools/sgxfive-test.c at dddadbdd, resgx545:crates/sgx-pipe/src/zls.rs at dddadbdd, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=B60AB0B475DD1E8972419B5; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW"]
date = "2026-11-14"
data = ["render-closing-r14-zls:out/20261114-054846/zbits2/", "render-closing-r14-zls:out/20261114-054846/zgran/", "render-closing-r14-zls:out/20261114-054846/zodd/", "render-closing-r14-zls:fold/"]
terms = ["CR_ISP_ZLSCTL", "ISP2"]
+++
**What ran.** E988's stencil row (st1-b0: 64 x 32, the stencil loaded from the bytes fill and
stored, ISP word 2 0x040501ff, control 0x0017300e) with each set-half bit set alone (15, 21, 22, 23,
27 to 31) and the groups 21 to 23 and 27 to 31; bits 12 and 16 cleared at 96 x 32 and 64 x 32 with G
2 (0x00173016), read model-free (the loaded byte is the stored one XOR 0xff where the pixel drew);
in stage zgran zb2-d12, E1029's identity row with bit 12 cleared (0x0017400e, the depth loaded from
an `index` fill); in stage zodd zb2-f2-16, E977's z242-c-f2 with bit 16 cleared (0x02161014).
Controls: zb2-c-base (E988's 1024), zb2-c-set (E1030's zbs-set), zb2-c-r16 (E1030's zbr-c16, E997's
linear dump), and zgran's three.

**Frozen verdict (as printed).** attempt 20261114-054846, stage zgran (run.log): `SUMMARY: zgran:
H-DEPTH-LIN (1 of 1 rows decided)`; attempt 20261114-054846, stage zgran (run.log): `SUMMARY: zgran:
H-DEPTH-UNCH is not supported: 0 held, 1 FAILED, 0 cannot tell of 1`; attempt 20261114-054846, stage
zodd (run.log): `SUMMARY: zodd: L16-DW is not supported: 0 held, 1 FAILED, 0 cannot tell of 1`;
attempt 20261114-054846, stage zodd (run.log): `SUMMARY: zodd: L16-HALF (1 of 1 rows decided)`;
attempt 20261114-054846, stage zodd (run.log): `SUMMARY: zodd: L16-PAIR is not supported: 0 held, 1
FAILED, 0 cannot tell of 1`; attempt 20261114-054846, stage zodd (run.log): `SUMMARY: zodd:
L16-TILED is not supported: 0 held, 1 FAILED, 0 cannot tell of 1`; attempt 20261114-054846, stage
zbits2 (run.log): `SUMMARY: zbits2: P-64 is not supported: 0 held, 4 FAILED, 0 cannot tell of 4`;
attempt 20261114-054846, stage zbits2 (run.log): `SUMMARY: zbits2: P-G (4 of 4 rows decided)`;
attempt 20261114-054846, stage zbits2 (run.log): `SUMMARY: zbits2: P-W is not supported: 2 held, 2
FAILED, 0 cannot tell of 4`; attempt 20261114-054846, stage zbits2 (run.log): `SUMMARY: zbits2:
Z-ANY is not supported: 1 held, 10 FAILED, 0 cannot tell of 11`; attempt 20261114-054846, stage
zbits2 (run.log): `SUMMARY: zbits2: Z-GROUP is not supported: 8 held, 3 FAILED, 0 cannot tell of
11`; attempt 20261114-054846, stage zbits2 (run.log): `SUMMARY: zbits2: Z-GRP-21-23 is not
supported: 9 held, 2 FAILED, 0 cannot tell of 11`; attempt 20261114-054846, stage zbits2 (run.log):
`SUMMARY: zbits2: Z-GRP-27-31 is not supported: 7 held, 4 FAILED, 0 cannot tell of 11`; attempt
20261114-054846, stage zbits2 (run.log): `SUMMARY: zbits2: Z-ONE-15 is not supported: 8 held, 3
FAILED, 0 cannot tell of 11`; attempt 20261114-054846, stage zbits2 (run.log): `SUMMARY: zbits2:
Z-ONE-21 is not supported: 8 held, 3 FAILED, 0 cannot tell of 11`; attempt 20261114-054846, stage
zbits2 (run.log): `SUMMARY: zbits2: Z-ONE-22 is not supported: 8 held, 3 FAILED, 0 cannot tell of
11`; attempt 20261114-054846, stage zbits2 (run.log): `SUMMARY: zbits2: Z-ONE-23 is not supported: 9
held, 2 FAILED, 0 cannot tell of 11`; attempt 20261114-054846, stage zbits2 (run.log): `SUMMARY:
zbits2: Z-ONE-27 is not supported: 6 held, 5 FAILED, 0 cannot tell of 11`; attempt 20261114-054846,
stage zbits2 (run.log): `SUMMARY: zbits2: Z-ONE-28 is not supported: 6 held, 5 FAILED, 0 cannot tell
of 11`; attempt 20261114-054846, stage zbits2 (run.log): `SUMMARY: zbits2: Z-ONE-29 is not
supported: 6 held, 5 FAILED, 0 cannot tell of 11`; attempt 20261114-054846, stage zbits2 (run.log):
`SUMMARY: zbits2: Z-ONE-30 is not supported: 6 held, 5 FAILED, 0 cannot tell of 11`; attempt
20261114-054846, stage zbits2 (run.log): `SUMMARY: zbits2: Z-ONE-31 is not supported: 6 held, 5
FAILED, 0 cannot tell of 11`..

**Results [HW].** Controls: zb2-c-base 1024, zb2-c-set 2048 with every stored byte 0xff,
zb2-c-r16 byte for byte E997's dump; zgran's passed. Set-half rows (score-zbits2.txt): b21, b22, b27
to b31 and g27-31 drew 1024 with zb2-c-base's image and the loaded bytes explain 2048 of 2048 stored
bytes; g21-23 drew 2048, every byte 0xff; b15 drew 0 and the store holds the loaded bytes unchanged;
b23 drew 1536, 48 of each 64-pixel row in a pattern of period 16 in x alike in every row, the byte
the test saw (stored, XOR 0xff where drawn) 0x00 or 0x80 where drawn and 0x3f where not
(fold/look.py). Pitch rows: P-G explains 3072 of 3072 bytes at 96 x 32 and 2048 of 2048 at 64 x 32
for both bits. zb2-d12 stored the load of dword 64 y + x at pixel (x, y)'s tiled dword, 2048
of 2048.
zb2-f2-16 stored 2304 dwords, the 16-bit value of pixel (x, y) (E977's kept z242-c-f2) at halfword
96 y + x.

**What it shows.** The stencil test's read of 0 comes from bits 21 to 23 together; no set-half
bit alone does it, bits 27 to 31 do nothing seen, and bits 15 and 23 alone change the test in other
ways [post hoc]. Bits 12 and 16 select a linear image with rows of 32 (G + 1) units for the loads
and
the stores respectively, depth and stencil alike, and for the 16-bit format a halfword a pixel.

**What it does not show.** What bits 15 and 23 alone do (a reading, no frozen form); bit 21 or
22 with 23 alone; bit 0 under other controls; bit 20; the ISP's use of the control.
