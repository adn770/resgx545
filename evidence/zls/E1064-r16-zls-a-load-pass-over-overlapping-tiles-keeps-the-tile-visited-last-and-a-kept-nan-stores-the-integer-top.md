+++
id = "E1064"
claim = "r16-zls rows zo- (Q299, 11 jobs in stages zovp and zbits4, t10): a load pass over overlapping tiles (64 x 32 G 0 and 160 x 48 G 2) loads each tile's slot by E465, passes each tile on its own and leaves in a shared slot the tile visited last in region header order, for the depth load over E996's plane and the stencil load under E988's test (frozen H-OVL-PASS 4 of 4; the first tile failed 2 of 2, shared slots without a load 4 of 4); a NaN load (0x7fc00000, 0xffc00000, 0x7f800001) kept under never stores 0x00ffffff in format 1 and 0xffffffff in format 2 (H-NAN-SAT 5 of 5; 0 and the word's low bits failed 5 of 5); both controls passed"
unit = "zls"
method = "r16-zls (render/closing-r16-zls), stages zovp, zbits4 of the question-closing pass (round 16, decisions R16-1 (a), R16-3 (a), R16-6 (a) and R16-8 (a): session r16-zls of the round 16 plan, safe class only), dataset render-closing-r16-zls; attempt out/20261114-092344 (zbits4 09:25:15, zovp 09:26:42 Mac time; driver log run.log; its freeze FROZEN.sha256 cf144d4f151072150ee03d328ed2705ac2725970a1c5ea15d4e91338357610ce; scores score-zbits4.txt, score-zovp.txt); on the laptop (host cedar, kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5 (linux fork 2a650d74, installed and loaded alike), stock firmware, tool ~/sgxfive-test-t10 (t10, sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, built from resgx545 a581c06), every job one process of the kit runner (kit/run_stage.sh), a debugfs reset and the health fill and triangle between jobs, every output and dump kept gzipped; the rows are tables/STAGE.txt, grouped by the dump their scorer reads, a row's name prefix naming its record (zp2- E1059, zb4- E1063, zo- E1064, zw2- E1066), the frozen predictions predictions/STAGE.tsv (gen/z16.py)); freezes: FROZEN.sha256 cf144d4f151072150ee03d328ed2705ac2725970a1c5ea15d4e91338357610ce (85 files), PREDICTIONS.sha256 4fa8e22324d9eff9d97b5ee73eda6fc68295612c08d7db9228e56f6ac14f7604 (4 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at b2b5288c, resgx545:tools/closing/kit/lib_kit.sh at b2b5288c, resgx545:tools/closing/kit/run_stage.sh at b2b5288c, resgx545:tools/closing/kit/kitscore.py at b2b5288c, resgx545:tools/closing/kit/fake/sudo at b2b5288c, resgx545:tools/closing/kit/fake/timeout at b2b5288c, resgx545:tools/closing/kit/fake/df at b2b5288c, resgx545:tools/closing/kit/fake/modinfo at b2b5288c, resgx545:tools/closing/kit/fake/sha256sum at b2b5288c, resgx545:tools/closing/kit/fake/tool.sh at b2b5288c, resgx545:tools/closing/kit/fake/tool.py at b2b5288c, resgx545:tools/closing/kit/fake/ssh.py at b2b5288c, resgx545:tools/closing/scorekit.py at b2b5288c, resgx545:tools/closing/sessioncheck.py at b2b5288c, data:render/closing-r15-zls/out/20261114-073826/zpass/zp-z125.depth-store.1.bin.gz at 62cb03b3, data:render/closing-r15-zls/out/20261114-073826/zpass/zp-c-467.depth-store.1.bin.gz at 62cb03b3, data:render/closing-r15-zls/out/20261114-073826/zpass/zp-f1.depth-store.1.bin.gz at 62cb03b3, data:render/closing-r14-zls/out/20261114-054846/zbits2/zb2-c-base.stencil-store.1.bin.gz at 62cb03b3, data:render/closing-r14-zls/out/20261114-054846/zbits2/zb2-c-base.depth.1.bin.gz at 62cb03b3, data:render/closing-r14-zls/out/20261114-054846/zbits2/zb2-c-base.txt.gz at 62cb03b3, data:render/closing-r14-zls/out/20261114-054846/zbits2/zb2-b23.stencil-store.1.bin.gz at 62cb03b3, data:render/closing-r14-zls/out/20261114-054846/zbits2/zb2-b23.depth.1.bin.gz at 62cb03b3, data:render/closing-r13-zls/out/20261113-213117/zfmt/zf-flat-f6.stencil-store.1.bin.gz at 62cb03b3, data:render/closing-r13-zls/out/20261113-213117/zfmt/zf-flat-f6.depth.1.bin.gz at 62cb03b3, data:render/closing-r13-zls/out/20261113-213117/zfmt/zf-flat-f6.txt.gz at 62cb03b3, data:render/closing-r13-zls/out/20261113-213117/zfmt/zf-7k-3f.stencil-store.1.bin.gz at 62cb03b3, data:render/closing-r13-zls/out/20261113-213117/zfmt/zf-7k-3f.depth.1.bin.gz at 62cb03b3, data:render/closing-r13-zls/out/20261113-213117/zfmt/zf-7k-3f.txt.gz at 62cb03b3, data:render/closing-r13-zls/out/20261113-213117/zbits/zbs-c16.stencil-store.1.bin.gz at 62cb03b3, data:render/closing-r13-zls/out/20261113-213117/zbits/zbs-c16.depth.1.bin.gz at 62cb03b3, data:render/closing-r13-zls/out/20261113-213117/zbits/zbs-c16.txt.gz at 62cb03b3, data:render/closing-r14-zls/out/20261114-054846/zgran/zb2-d12.depth-store.1.bin.gz at 62cb03b3, data:render/closing-r14-zls/out/20261114-054846/zgran/zb2-d12.txt.gz at 62cb03b3, data:render/closing-r14-zls/out/20261114-054846/zodd/zo-640-f0.depth.1.bin.gz at 62cb03b3, data:render/closing-r14-zls/out/20261114-054846/zodd/zo-640-f0.txt.gz at 62cb03b3, data:render/closing-r10-x/out/20261113-101116/zov/zov-64x32-ctl.depth.1.bin.gz at 62cb03b3, data:render/closing-r10-x/out/20261113-101116/zov/zov-160x48-ctl.depth.1.bin.gz at 62cb03b3, data:render/closing-r10-x/out/20261113-101116/zov/zov-64x32-g0.depth.1.bin.gz at 62cb03b3, data:render/closing-r10-zls/out/20261113-102039/zw/zw-0125.depth.1.bin.gz at 62cb03b3, data:render/closing-r9-z2/out/20261113-082522/z2/z2-a-f0.depth.1.bin.gz at 62cb03b3, data:render/closing-r15-zls/tables/zpass.txt at 62cb03b3, data:render/closing-r14-zls/tables/zbits2.txt at 62cb03b3, data:render/closing-r14-zls/tables/zgran.txt at 62cb03b3, data:render/closing-r14-zls/tables/zodd.txt at 62cb03b3, data:render/closing-r13-zls/tables/zfmt.txt at 62cb03b3, data:render/closing-r13-zls/tables/zbits.txt at 62cb03b3, data:render/closing-r10-zls/tables/zw.txt at 62cb03b3, data:render/closing-r9-z2/tables/z2.txt at 62cb03b3, data:render/closing-r10-x/tables/zov.txt at 62cb03b3, data:render/closing-r10-st1/lead/build_tool10.sh at 62cb03b3, resgx545:crates/sgx-pipe/src/zls.rs at b2b5288c, resgx545:crates/sgx-pipe/src/isp.rs at b2b5288c, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=B60AB0B475DD1E8972419B5; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW"]
date = "2026-11-14"
data = ["render-closing-r16-zls:out/20261114-092344/zovp/", "render-closing-r16-zls:out/20261114-092344/zbits4/", "render-closing-r16-zls:fold/"]
terms = ["CR_ISP_ZLSCTL"]
+++
**What ran.** E996's plane (z 0, ZX, 1 at (0,0), (2W,0), (0,2H)) at 64 x 32 G 0 (0x00175006) and 160
x 48 G 2 (0x00175016), the depth loaded from a buffer filled 0.2f (0x3e4ccccd) and stored, depth
less; E988's st1 row at the same pitches (0x00173006, 0x00173016, the `bytes` stencil, in stage
zbits4); E1050's zpass form under never (blk:1 0x00000200) in formats 1 (0x0117500e) and 2
(0x0217500e) with the load buffer filled 0x7fc00000, 0xffc00000 (format 1) and 0x7f800001. Controls:
zo-c-64 (the 64 x 32 pass row without the load, 0x00171004: E996's owner rule from the kept
full-pitch reference, held on E996's kept zov-64x32-g0 dword for dword offline) and zo-c-f1 (E1050's
zp-f1, its kept store byte for byte). The plane of each pixel was named by E996's kept zov-64x32-ctl
and zov-160x48-ctl (H-PASS-TWIN, E1059).

**Frozen verdict (as printed).** attempt 20261114-092344, stage zbits4 (run.log): `SUMMARY: zbits4:
H-OVL-PASS (2 of 2 rows decided)`; attempt 20261114-092344, stage zbits4 (run.log): `SUMMARY:
zbits4: H-OVL-SKIP is not supported: 0 held, 2 FAILED, 0 cannot tell of 2`; attempt 20261114-092344,
stage zovp (run.log): `SUMMARY: zovp: H-NAN-LOW is not supported: 0 held, 5 FAILED, 0 cannot tell of
5`; attempt 20261114-092344, stage zovp (run.log): `SUMMARY: zovp: H-NAN-SAT (5 of 5 rows decided)`;
attempt 20261114-092344, stage zovp (run.log): `SUMMARY: zovp: H-NAN-ZERO is not supported: 0 held,
5 FAILED, 0 cannot tell of 5`; attempt 20261114-092344, stage zovp (run.log): `SUMMARY: zovp:
H-OVL-FIRST is not supported: 0 held, 2 FAILED, 0 cannot tell of 2`; attempt 20261114-092344, stage
zovp (run.log): `SUMMARY: zovp: H-OVL-PASS (2 of 2 rows decided)`; attempt 20261114-092344, stage
zovp (run.log): `SUMMARY: zovp: H-OVL-SKIP is not supported: 0 held, 2 FAILED, 0 cannot tell of 2`.

**Results [HW].** Controls: zo-c-64 1536 of 1536 dwords and 2048 drawn, zo-c-f1 byte for byte and
1024 drawn. zo-p-64 1536 of 1536 dwords and 806 drawn, zo-p-160 5632 of 5632 and 3040 under
H-OVL-PASS (H-OVL-FIRST 1146 and 4416, H-OVL-SKIP 1024 and 4288 with 1440 and 5728 predicted drawn);
zo-s-64 1536 of 1536 bytes and 1024 drawn, zo-s-160 5632 of 5632 and 3840. Every NaN row stored one
value at every dword of the target: 0x00ffffff (format 1) or 0xffffffff (format 2), 0 drawn. The
frozen scorer re-run on the kept files is byte for byte the run's (fold/reproduce.out). sgx-pipe's
`zls::pass_plane` now passes overlapping whole tiles in visit order and `encode_depth` stores a NaN
at the top of the range; tests/closing_r16_zls.rs replays every zo- row.

**What it shows.** The load pass and the overlapping store compose: each tile reads its own slot
(the shared slot's dwords for every tile sharing it) and E996's last-visited tile owns the stored
slot [infer: with E1050's pass, per tile]. A NaN kept from the load reaches the integer conversion
as above every depth, as in the compare (E995), and clamps there (E1051).

**What it does not show.** A store past its buffer (E411's faults: a planned fault, Q299's remaining
clause); a pass over overlapping tiles with edge tiles; a NaN produced by the plane rather than the
load; infinity loaded into an integer store.
