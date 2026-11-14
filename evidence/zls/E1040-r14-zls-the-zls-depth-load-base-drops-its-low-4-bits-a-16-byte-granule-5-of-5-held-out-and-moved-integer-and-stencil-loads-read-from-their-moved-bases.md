+++
id = "E1040"
claim = "r14-zls rows zg- (Q243, 12 jobs in stages zgran and zbits2, t10): the ZLS depth load base (render details dword 12) is rounded down to 16 bytes: frozen G16 held 5 of 5 held-out moves (+8 loaded unmoved, +16, +32, +0x1008 and +0x1020 moved by 16-byte steps) while G8, G32, G64 and H-BYTE failed, and with E1029's six offset moves no other granule of 4 to 128 bytes fits (fold/look.py); formats 1 and 2 loaded from a base moved by +0x1000 read E465's 32-bit layout from it, each dword a float stored by the floor rule (frozen I-MOVED-L32 2 of 2; the 16-bit layout, the unmoved base and the store's buffer failed); the stencil load base (dword 14) moved by +0x1000 moves the stencil load (frozen S-MOVED, 2048 of 2048 bytes; S-UNMOVED and S-STOREBASE failed); all six controls passed"
unit = "zls"
method = "r14-zls (render/closing-r14-zls), stages zgran, zbits2 of the question-closing pass (round 14, decisions R14-1 (a), R14-7 (a), R14-9 (a) and R14-10 (a): session r14-zls of the round 14 plan, safe class only), dataset render-closing-r14-zls; attempt out/20261114-054846 (zgran 05:48:47, zbits2 05:51:21 Mac time; driver log run.log; its freeze FROZEN.sha256 9279b1fe886c085b630c81e36dc7be61f2252f374d81ed10c32db8c91709ce45; scores score-zbits2.txt, score-zgran.txt); on the laptop (host cedar, kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5 (linux fork 2a650d74, installed and loaded alike), stock firmware, tool ~/sgxfive-test-t10 (t10, sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, built from resgx545 a581c06), every job one process of the kit runner (kit/run_stage.sh), a debugfs reset and the health fill and triangle between jobs, every output and dump kept gzipped; the rows are tables/STAGE.txt, grouped by the dump their scorer reads, a row's name prefix naming its record (zg- E1040, zo- E1041, zb2- E1042, zl- E1043), the frozen predictions predictions/STAGE.tsv (gen/z14.py)); freezes: FROZEN.sha256 9279b1fe886c085b630c81e36dc7be61f2252f374d81ed10c32db8c91709ce45 (86 files), PREDICTIONS.sha256 f4d7d7697e09afbfbb86bc512d1e129a6de18812cdf13f6ea3c4d5351f5be4b6 (4 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at dddadbdd, resgx545:tools/closing/kit/lib_kit.sh at dddadbdd, resgx545:tools/closing/kit/run_stage.sh at dddadbdd, resgx545:tools/closing/kit/kitscore.py at dddadbdd, resgx545:tools/closing/kit/fake/sudo at dddadbdd, resgx545:tools/closing/kit/fake/timeout at dddadbdd, resgx545:tools/closing/kit/fake/df at dddadbdd, resgx545:tools/closing/kit/fake/modinfo at dddadbdd, resgx545:tools/closing/kit/fake/sha256sum at dddadbdd, resgx545:tools/closing/kit/fake/tool.sh at dddadbdd, resgx545:tools/closing/kit/fake/tool.py at dddadbdd, resgx545:tools/closing/kit/fake/ssh.py at dddadbdd, resgx545:tools/closing/scorekit.py at dddadbdd, resgx545:tools/closing/sessioncheck.py at dddadbdd, data:render/closing-r9-x/out/20261113-081821/zls/z243-ctl.depth-store.1.bin.gz at 3309b5fd, data:render/closing-r9-x/out/20261113-081821/zls/z243-ctl.txt.gz at 3309b5fd, data:render/closing-r9-x/out/20261113-081821/zls/z243-f1-less.depth-store.1.bin.gz at 3309b5fd, data:render/closing-r9-x/out/20261113-081821/zls/z243-f2-less.depth-store.1.bin.gz at 3309b5fd, data:render/closing-r9-x/out/20261113-081821/zls/z242-c-f0.depth.1.bin.gz at 3309b5fd, data:render/closing-r9-x/out/20261113-081821/zls/z242-c-f1.depth.1.bin.gz at 3309b5fd, data:render/closing-r9-x/out/20261113-081821/zls/z242-c-f2.depth.1.bin.gz at 3309b5fd, data:render/closing-r13-zls/out/20261113-213117/zbase/zb-m4.depth-store.1.bin.gz at 3309b5fd, data:render/closing-r13-zls/out/20261113-213117/zbase/zb-m4.txt.gz at 3309b5fd, data:render/closing-r13-zls/out/20261113-213117/zbase/zb-m40.depth-store.1.bin.gz at 3309b5fd, data:render/closing-r13-zls/out/20261113-213117/zbits/zbs-base.txt.gz at 3309b5fd, data:render/closing-r13-zls/out/20261113-213117/zbits/zbs-base.stencil-store.1.bin.gz at 3309b5fd, data:render/closing-r13-zls/out/20261113-213117/zbits/zbs-c12.txt.gz at 3309b5fd, data:render/closing-r13-zls/out/20261113-213117/zbits/zbs-c12.stencil-store.1.bin.gz at 3309b5fd, data:render/closing-r13-zls/out/20261113-213117/zbits/zbs-c16.txt.gz at 3309b5fd, data:render/closing-r13-zls/out/20261113-213117/zbits/zbs-c16.stencil-store.1.bin.gz at 3309b5fd, data:render/closing-r13-zls/out/20261113-213117/zbits/zbs-set.txt.gz at 3309b5fd, data:render/closing-r13-zls/out/20261113-213117/zbits/zbs-set.stencil-store.1.bin.gz at 3309b5fd, data:render/closing-r13-zls/out/20261113-213117/zbits/zbr-c16.depth.1.bin.gz at 3309b5fd, data:render/closing-r13-zls/out/20261113-213117/zfmt/zf-flat-f6.depth.1.bin.gz at 3309b5fd, data:render/closing-r13-zls/out/20261113-213117/zfmt/zf-flat-f6.txt.gz at 3309b5fd, data:render/closing-r10-x/out/20261113-101116/zov/zov-64x32-g0.depth.1.bin.gz at 3309b5fd, data:render/closing-r10-x/out/20261113-101116/zov/zov-64x32-g0.txt.gz at 3309b5fd, data:render/closing-r10-x/out/20261113-101116/zov/zov-64x32-ctl.depth.1.bin.gz at 3309b5fd, data:render/closing-r10-x/out/20261113-101116/zov/zov-256x64-ctl.depth.1.bin.gz at 3309b5fd, data:render/closing-r10-x/out/20261113-101116/zov/zov-256x64-g3.depth.1.bin.gz at 3309b5fd, data:render/closing-r10-x/out/20261113-101116/zbits/zb-clr-f0.depth.1.bin.gz at 3309b5fd, data:render/closing-r10-zls/out/20261113-102039/zst2/z2y-f6.depth.1.bin.gz at 3309b5fd, data:render/closing-r10-zls/out/20261113-102039/zst2/z2y-f7.depth.1.bin.gz at 3309b5fd, data:render/closing-r10-zls/out/20261113-102039/zst2/z2d-f7.depth.1.bin.gz at 3309b5fd, data:cited/closing11/plan/c7-q120/c7_rule.py at 3309b5fd, data:render/closing-r9-x/tables/zls.txt at 3309b5fd, data:render/closing-r10-x/tables/zov.txt at 3309b5fd, data:render/closing-r10-x/tables/zbits.txt at 3309b5fd, data:render/closing-r10-st1/tables/st1.txt at 3309b5fd, data:render/closing-r10-zls/tables/zst2.txt at 3309b5fd, data:render/closing-r13-zls/tables/zbase.txt at 3309b5fd, data:render/closing-r13-zls/tables/zbits.txt at 3309b5fd, data:render/closing-r13-zls/tables/zfmt.txt at 3309b5fd, data:render/closing-r10-st1/lead/build_tool10.sh at 3309b5fd, resgx545:userspace/libsgxfive/tools/sgxfive-test.c at dddadbdd, resgx545:crates/sgx-pipe/src/zls.rs at dddadbdd, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=B60AB0B475DD1E8972419B5; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW"]
date = "2026-11-14"
data = ["render-closing-r14-zls:out/20261114-054846/zgran/", "render-closing-r14-zls:out/20261114-054846/zbits2/", "render-closing-r14-zls:fold/"]
terms = ["CR_ISP_ZLSCTL", "CR_ISP_ZLOAD_BASE", "CR_ISP_ZSTORE_BASE"]
+++
**What ran.** Granule and integer rows: E1029's zbase form (64 x 32, --tri-full at 0.5, ZLS control
0x0017500e, the depth test never, `--depth-pages 20`: depth buffer 0x3e001000, store 0x3e015000)
with `--kpoke-render 1:rd:12=0x1000 + m` after the tool's own pokes. The granule rows (zg-m8,
zg-m10, zg-m20, zg-m1008, zg-m1020) fill the depth buffer `index` and the store 0x3e800000; the
integer rows (zg-f1, zg-f2: controls 0x0117500e and 0x0217500e, m = +0x1000) fill the depth buffer
`bit:10` (dword i holds 0.75 where bit 10 of i is set, else 0.25) and the store 0.5. Stencil row
zg-s14 (stage zbits2): E988's st1 form (the stencil loaded and stored, ISP word 2 0x040501ff) with
the stencil filled `index` and `--kpoke-render 1:rd:14=0x80014000` (the tool's own 0x80013000
moved +0x1000), read model-free: the loaded byte is the stored byte at E988's position XOR 0xff
where the pixel drew. Controls: zg-c-ctl (E977's z243-ctl), zg-c-m4 and zg-c-m40 (E1029's +4 and
+0x40, byte for byte its kept stores), zg-c-sid (the stencil row with rd:14 its own), and in zbits2
zb2-c-base and zb2-c-set (E988's and E1030's counts).

**Frozen verdict (as printed).** attempt 20261114-054846, stage zgran (run.log): `SUMMARY: zgran:
G16 (5 of 5 rows decided)`; attempt 20261114-054846, stage zgran (run.log): `SUMMARY: zgran: G32 is
not supported: 4 held, 1 FAILED, 0 cannot tell of 5`; attempt 20261114-054846, stage zgran
(run.log): `SUMMARY: zgran: G64 is not supported: 2 held, 3 FAILED, 0 cannot tell of 5`; attempt
20261114-054846, stage zgran (run.log): `SUMMARY: zgran: G8 is not supported: 3 held, 2 FAILED, 0
cannot tell of 5`; attempt 20261114-054846, stage zgran (run.log): `SUMMARY: zgran: H-BYTE is not
supported: 3 held, 2 FAILED, 0 cannot tell of 5`; attempt 20261114-054846, stage zgran (run.log):
`SUMMARY: zgran: I-MOVED-L16 is not supported: 0 held, 1 FAILED, 0 cannot tell of 1`; attempt
20261114-054846, stage zgran (run.log): `SUMMARY: zgran: I-MOVED-L32 (2 of 2 rows decided)`; attempt
20261114-054846, stage zgran (run.log): `SUMMARY: zgran: I-STOREBASE is not supported: 0 held, 2
FAILED, 0 cannot tell of 2`; attempt 20261114-054846, stage zgran (run.log): `SUMMARY: zgran:
I-UNMOVED-L16 is not supported: 0 held, 1 FAILED, 0 cannot tell of 1`; attempt 20261114-054846,
stage zgran (run.log): `SUMMARY: zgran: I-UNMOVED-L32 is not supported: 0 held, 2 FAILED, 0 cannot
tell of 2`; attempt 20261114-054846, stage zbits2 (run.log): `SUMMARY: zbits2: S-MOVED (1 of 1 rows
decided)`; attempt 20261114-054846, stage zbits2 (run.log): `SUMMARY: zbits2: S-STOREBASE is not
supported: 0 held, 1 FAILED, 0 cannot tell of 1`; attempt 20261114-054846, stage zbits2 (run.log):
`SUMMARY: zbits2: S-UNMOVED is not supported: 0 held, 1 FAILED, 0 cannot tell of 1`.

**Results [HW].** Controls: zg-c-ctl drew 2048 and its store is E977's byte for byte; zg-c-m4
and zg-c-m40 are E1029's stores byte for byte; zg-c-sid read the index stencil in E988's order at
2048 of 2048 pixels; zb2-c-base drew 1024, zb2-c-set 2048 with every stored byte 0xff. Granule rows,
the store's dword k holding the depth buffer's dword k + d at all 2048 dwords: +8 d = 0, +0x10 d =
4, +0x20 d = 8, +0x1008 d = 1024, +0x1020 d = 1032 (score-zgran.txt). zg-f1 stored 0x400000 and
0xc00000 at 2048 of 2048 dwords as the floor rule of the moved base's floats in E465's layout, zg-f2
0x40004000 and 0xc000c000 at 1024 of 1024 (the 16-bit layout's read 512 of 1024). zg-s14 drew 1536;
its loaded bytes are the index fill 0x1000 bytes on at 2048 of 2048 pixels (unmoved 1536, the
store's fill 2). Post hoc (fold/look.py): of granules 4 to 128 bytes only 16 gives the eleven
offsets of E1029's and E1040's moves.

**What it shows.** The depth load reads from its own base rounded down to 16 bytes, at any page
or tile offset, in E465's layout (`zls::load_base`, held out); an integer-format load reads that
layout from the moved base and takes each dword as a float, as E977 read it at the store's base;
the stencil load has its own base, dword 14 (with bit 31 set), and follows it as the depth load
follows dword 12. With E977's and E995's answers on the integer formats, NaN, infinity and equal
depths, every clause of Q243's question line is decided by held-out rows with passing controls.

**What it does not show.** The stencil base's own granule (only a page move ran); a moved base
at another pitch than G 1, past the mapped buffer, or under a depth test other than never; the
load and pass over edge tiles (E831's note) and bit 19 with a load, which sgx-pipe still refuses
citing Q243.
