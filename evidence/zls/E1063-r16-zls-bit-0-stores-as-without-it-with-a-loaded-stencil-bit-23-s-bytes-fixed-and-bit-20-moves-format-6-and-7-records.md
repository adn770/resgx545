+++
id = "E1063"
claim = "r16-zls rows zb4- (Q071, 14 jobs in stages zbits4, zovp and zoff, t10): bit 0 under E988's stencil row, E1030's bit 16 cleared and E1031's flat format-6 and F7K rows writes no colour pixel and leaves the depth dump and the stencil store byte for byte the kept twin's (frozen H-B0 4 of 4; nothing stored, H-B0-NOSTORE, failed 4 of 4); bit 23's bytes 0x3f, 0x80 and 0 by x mod 16 stay with the reference at 0x80, the compare mask at 0xff and the background stencil (CR_ISP_BGOBJVALS, render details dword 17) at 0x5a (H23-FIXED 3 of 3, each named source refuted on its own row); bit 20 cleared changed nothing at 640 x 480 in format 0 nor with bit 12 cleared and a depth load (H-INERT20 2 of 2 there), but in formats 6 and 7 it moved the stored records (H-INERT20 failed 2 of 2: post hoc, the twin's per-tile records packed one after another from dword 2048); all controls passed"
unit = "zls"
method = "r16-zls (render/closing-r16-zls), stages zbits4, zovp, zoff of the question-closing pass (round 16, decisions R16-1 (a), R16-3 (a), R16-6 (a) and R16-8 (a): session r16-zls of the round 16 plan, safe class only), dataset render-closing-r16-zls; attempt out/20261114-092344 (zbits4 09:25:15, zovp 09:26:42, zoff 09:27:49 Mac time; driver log run.log; its freeze FROZEN.sha256 cf144d4f151072150ee03d328ed2705ac2725970a1c5ea15d4e91338357610ce; scores score-zbits4.txt, score-zoff.txt, score-zovp.txt); on the laptop (host cedar, kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5 (linux fork 2a650d74, installed and loaded alike), stock firmware, tool ~/sgxfive-test-t10 (t10, sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, built from resgx545 a581c06), every job one process of the kit runner (kit/run_stage.sh), a debugfs reset and the health fill and triangle between jobs, every output and dump kept gzipped; the rows are tables/STAGE.txt, grouped by the dump their scorer reads, a row's name prefix naming its record (zp2- E1059, zb4- E1063, zo- E1064, zw2- E1066), the frozen predictions predictions/STAGE.tsv (gen/z16.py)); freezes: FROZEN.sha256 cf144d4f151072150ee03d328ed2705ac2725970a1c5ea15d4e91338357610ce (85 files), PREDICTIONS.sha256 4fa8e22324d9eff9d97b5ee73eda6fc68295612c08d7db9228e56f6ac14f7604 (4 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at b2b5288c, resgx545:tools/closing/kit/lib_kit.sh at b2b5288c, resgx545:tools/closing/kit/run_stage.sh at b2b5288c, resgx545:tools/closing/kit/kitscore.py at b2b5288c, resgx545:tools/closing/kit/fake/sudo at b2b5288c, resgx545:tools/closing/kit/fake/timeout at b2b5288c, resgx545:tools/closing/kit/fake/df at b2b5288c, resgx545:tools/closing/kit/fake/modinfo at b2b5288c, resgx545:tools/closing/kit/fake/sha256sum at b2b5288c, resgx545:tools/closing/kit/fake/tool.sh at b2b5288c, resgx545:tools/closing/kit/fake/tool.py at b2b5288c, resgx545:tools/closing/kit/fake/ssh.py at b2b5288c, resgx545:tools/closing/scorekit.py at b2b5288c, resgx545:tools/closing/sessioncheck.py at b2b5288c, data:render/closing-r15-zls/out/20261114-073826/zpass/zp-z125.depth-store.1.bin.gz at 62cb03b3, data:render/closing-r15-zls/out/20261114-073826/zpass/zp-c-467.depth-store.1.bin.gz at 62cb03b3, data:render/closing-r15-zls/out/20261114-073826/zpass/zp-f1.depth-store.1.bin.gz at 62cb03b3, data:render/closing-r14-zls/out/20261114-054846/zbits2/zb2-c-base.stencil-store.1.bin.gz at 62cb03b3, data:render/closing-r14-zls/out/20261114-054846/zbits2/zb2-c-base.depth.1.bin.gz at 62cb03b3, data:render/closing-r14-zls/out/20261114-054846/zbits2/zb2-c-base.txt.gz at 62cb03b3, data:render/closing-r14-zls/out/20261114-054846/zbits2/zb2-b23.stencil-store.1.bin.gz at 62cb03b3, data:render/closing-r14-zls/out/20261114-054846/zbits2/zb2-b23.depth.1.bin.gz at 62cb03b3, data:render/closing-r13-zls/out/20261113-213117/zfmt/zf-flat-f6.stencil-store.1.bin.gz at 62cb03b3, data:render/closing-r13-zls/out/20261113-213117/zfmt/zf-flat-f6.depth.1.bin.gz at 62cb03b3, data:render/closing-r13-zls/out/20261113-213117/zfmt/zf-flat-f6.txt.gz at 62cb03b3, data:render/closing-r13-zls/out/20261113-213117/zfmt/zf-7k-3f.stencil-store.1.bin.gz at 62cb03b3, data:render/closing-r13-zls/out/20261113-213117/zfmt/zf-7k-3f.depth.1.bin.gz at 62cb03b3, data:render/closing-r13-zls/out/20261113-213117/zfmt/zf-7k-3f.txt.gz at 62cb03b3, data:render/closing-r13-zls/out/20261113-213117/zbits/zbs-c16.stencil-store.1.bin.gz at 62cb03b3, data:render/closing-r13-zls/out/20261113-213117/zbits/zbs-c16.depth.1.bin.gz at 62cb03b3, data:render/closing-r13-zls/out/20261113-213117/zbits/zbs-c16.txt.gz at 62cb03b3, data:render/closing-r14-zls/out/20261114-054846/zgran/zb2-d12.depth-store.1.bin.gz at 62cb03b3, data:render/closing-r14-zls/out/20261114-054846/zgran/zb2-d12.txt.gz at 62cb03b3, data:render/closing-r14-zls/out/20261114-054846/zodd/zo-640-f0.depth.1.bin.gz at 62cb03b3, data:render/closing-r14-zls/out/20261114-054846/zodd/zo-640-f0.txt.gz at 62cb03b3, data:render/closing-r10-x/out/20261113-101116/zov/zov-64x32-ctl.depth.1.bin.gz at 62cb03b3, data:render/closing-r10-x/out/20261113-101116/zov/zov-160x48-ctl.depth.1.bin.gz at 62cb03b3, data:render/closing-r10-x/out/20261113-101116/zov/zov-64x32-g0.depth.1.bin.gz at 62cb03b3, data:render/closing-r10-zls/out/20261113-102039/zw/zw-0125.depth.1.bin.gz at 62cb03b3, data:render/closing-r9-z2/out/20261113-082522/z2/z2-a-f0.depth.1.bin.gz at 62cb03b3, data:render/closing-r15-zls/tables/zpass.txt at 62cb03b3, data:render/closing-r14-zls/tables/zbits2.txt at 62cb03b3, data:render/closing-r14-zls/tables/zgran.txt at 62cb03b3, data:render/closing-r14-zls/tables/zodd.txt at 62cb03b3, data:render/closing-r13-zls/tables/zfmt.txt at 62cb03b3, data:render/closing-r13-zls/tables/zbits.txt at 62cb03b3, data:render/closing-r10-zls/tables/zw.txt at 62cb03b3, data:render/closing-r9-z2/tables/z2.txt at 62cb03b3, data:render/closing-r10-x/tables/zov.txt at 62cb03b3, data:render/closing-r10-st1/lead/build_tool10.sh at 62cb03b3, resgx545:crates/sgx-pipe/src/zls.rs at b2b5288c, resgx545:crates/sgx-pipe/src/isp.rs at b2b5288c, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=B60AB0B475DD1E8972419B5; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW"]
date = "2026-11-14"
data = ["render-closing-r16-zls:out/20261114-092344/zbits4/", "render-closing-r16-zls:out/20261114-092344/zovp/", "render-closing-r16-zls:out/20261114-092344/zoff/", "render-closing-r16-zls:fold/"]
terms = ["CR_ISP_ZLSCTL", "CR_ISP_BGOBJVALS.STENCIL", "ISP2"]
+++
**What ran.** E988's st1-b0 form (64 x 32, the stencil loaded from the `bytes` fill and stored, ISP
word 2 0x040501ff) and E1031's zfmt form (the `index` stencil, depth less) with bit 0 set on st1-b0
(0x0017300f), E1030's zbs-c16 (0x0016300f), zf-flat-f6 (0x0617300f) and zf-7k-3f (0x0717300f); bit
20 cleared on zf-flat-f6 (0x0607300e), zf-7k-3f (0x0707300e), E1042's zb2-d12 (0x0007400e, in stage
zovp) and E1041's zo-640-f0 (0x0007109c, 640 x 480, in stage zoff); E1042's zb2-b23 (0x0097300e)
with `--poke blk:1^=0x80` (the reference, ISP word 0 bits 7:0), `--isp2 0x0405ffff` (the compare
mask 0xff) and `--kpoke-render 1:rd:17=0x35a` (t10's background word 0x300 with STENCIL 0x5a, 3d.md
11.3). Each changed row is its kept twin's argv with one word moved (tests/test_gen.py). Controls:
zb4-c-base (st1-b0), zb4-c-b23 (zb2-b23) and zb4-c-f6 (zf-flat-f6), their kept dumps byte for byte.

**Frozen verdict (as printed).** attempt 20261114-092344, stage zbits4 (run.log): `SUMMARY: zbits4:
H-B0 (4 of 4 rows decided)`; attempt 20261114-092344, stage zbits4 (run.log): `SUMMARY: zbits4:
H-B0-NOSTORE is not supported: 0 held, 4 FAILED, 0 cannot tell of 4`; attempt 20261114-092344, stage
zbits4 (run.log): `SUMMARY: zbits4: H-INERT20 is not supported: 0 held, 2 FAILED, 0 cannot tell of
2`; attempt 20261114-092344, stage zbits4 (run.log): `SUMMARY: zbits4: H23-BG is not supported: 2
held, 1 FAILED, 0 cannot tell of 3`; attempt 20261114-092344, stage zbits4 (run.log): `SUMMARY:
zbits4: H23-FIXED (3 of 3 rows decided)`; attempt 20261114-092344, stage zbits4 (run.log): `SUMMARY:
zbits4: H23-MASK is not supported: 2 held, 1 FAILED, 0 cannot tell of 3`; attempt 20261114-092344,
stage zbits4 (run.log): `SUMMARY: zbits4: H23-REF is not supported: 2 held, 1 FAILED, 0 cannot tell
of 3`; attempt 20261114-092344, stage zovp (run.log): `SUMMARY: zovp: H-INERT20 (1 of 1 rows
decided)`; attempt 20261114-092344, stage zoff (run.log): `SUMMARY: zoff: H-INERT20 (1 of 1 rows
decided)`.

**Results [HW].** Controls: 1024 and 1536 drawn and 176 depth dwords changed, each dump byte for
byte the kept twin's. The four bit-0 rows drew 0 and stored the twin's depth dump and stencil store
byte for byte (the format 6 and 7 rows store no stencil: E1031). zb4-23-ref drew 1536 and zb4-23-bg
1536, zb4-23-msk 1024 (the zero bytes only under the full mask), and on all three the byte the test
read (the stored byte, XOR 0xff where drawn) was 0x3f, 0x80 or 0 by x mod 16 exactly as E1053's,
2048 of 2048; the rd:17 poke line was printed. zb4-20-d12 stored zb2-d12's store byte for byte (0
drawn), zb4-20-640 zo-640-f0's 307200 dwords. zb4-20-f6 and zb4-20-f7 drew 2048 and left the stencil
store as the twin's, but their depth dumps differ: the twin's 176 and 48 dwords (44 and 24 a tile
record, at each slot's start) are not at the slots, and the same dwords lie packed in tile order at
dwords 2048 to 2223 and 2048 to 2095 (fold/look.py, fold/look.out, post hoc). The frozen scorer
re-run on the kept files is byte for byte the run's (fold/reproduce.out). sgx-pipe's
`zls::Ctl::decode` takes bit 0 with a loaded stencil and refuses bit 20 cleared with formats 5 to 7
(tests/closing_r16_zls.rs).

**What it shows.** Bit 0 suppresses the colour write and nothing of the depth or stencil path under
every control it ran with (E997's four, these four) [infer: every route]. Bit 23's bytes come from
neither the reference, the compare mask nor the background stencil. Bit 20 is not inert: in formats
6 and 7 it chooses where the per-tile records go, at their slots (set, as the closed driver's
values) or packed after the four slots (cleared) [post hoc, one size], and it changed nothing seen
in formats 0 and with a linear depth load.

**What it does not show.** Bit 20 cleared at another size or pitch, in formats 3 to 5 or with a
stencil but no format-6/7 depth (the packed records' start: after the slots or at a fixed offset);
where bit 23's bytes come from; bits 27 to 31 on routes other than E1042's; the ISP's use of the
control beyond these.
