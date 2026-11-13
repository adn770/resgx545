+++
id = "E996"
claim = "r10-x stage zov (11 jobs): with the ZLS pitch G below the tiles across minus one, so that tiles share 512-dword slots, every shared slot holds the 512 dwords of the tile visited last in the region header order (macrotiles column-major, 4 x 4-region blocks raster inside): frozen H-LATE/HDR held 5 of 5 (64 x 32 G 0, 128 x 32 G 1, 96 x 48 G 1, 160 x 48 G 2, 256 x 64 G 3: 1536, 3072, 3584, 5632 and 10240 dwords, every one), and in format 1 at 64 x 32 G 0 by E991's floor rule (1536 of 1536); the rivals each failed where they part from it (H-EARLY/HDR 0 of 5, H-LATE/RASTER 3 of 5 and H-EARLY/RASTER 1 of 5 held, the raster rows parting only at 160 x 48 and 256 x 64); every slot is whole (no tile mixes in a slot); the five full-pitch controls stored a distinct float in every dword of the tiles (E831's count)"
unit = "zls"
method = "r10-x (render/closing-r10-x), stage zov of the question-closing pass (round 10, decision R10-2 (a), plan closing10/rank/rank-round10.md R10-C (Q242)), dataset render-closing-r10-x; attempt out/20261113-101116 (zov 10:14:00 Mac time; driver log run.log; its freeze FROZEN.sha256 e70077bcfa0c94e9061f3a0356b49113bb78ae47322e9f060c5bb280bd007a47; scores score-zov.txt); on the laptop (host cedar, kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5 (linux fork 2a650d74, installed and loaded alike), stock firmware, tool ~/sgxfive-test-rgn4 (sha256 e6951558a93b4b7bc750eeae302997992d7ec6e26719bc527ba1ffc9c6fb779a, built from resgx545 4623753), every job one process of the kit runner (kit/run_stage.sh), a debugfs reset and the health fill and triangle between jobs, every output and dump kept gzipped; the rows are tables/STAGE.txt, the frozen predictions predictions/STAGE.tsv (gen/z.py)); freezes: FROZEN.sha256 e70077bcfa0c94e9061f3a0356b49113bb78ae47322e9f060c5bb280bd007a47 (151 files), PREDICTIONS.sha256 50878089db93e9928483efe7d499118b9a3e578423ed87a2deda89fbd137aa2e (78 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at dd291289, resgx545:tools/closing/kit/lib_kit.sh at dd291289, resgx545:tools/closing/kit/run_stage.sh at dd291289, resgx545:tools/closing/kit/kitscore.py at dd291289, resgx545:tools/closing/kit/fake/sudo at dd291289, resgx545:tools/closing/kit/fake/timeout at dd291289, resgx545:tools/closing/kit/fake/df at dd291289, resgx545:tools/closing/kit/fake/modinfo at dd291289, resgx545:tools/closing/kit/fake/sha256sum at dd291289, resgx545:tools/closing/kit/fake/tool.sh at dd291289, resgx545:tools/closing/kit/fake/tool.py at dd291289, resgx545:tools/closing/kit/fake/ssh.py at dd291289, resgx545:tools/closing/scorekit.py at dd291289, resgx545:tools/closing/sessioncheck.py at dd291289, data:render/closing-r9-x/out/20261113-081821/zls/z242-c-f0.depth.1.bin.gz at 1324301b, data:render/closing-r9-x/out/20261113-081821/zls/z242-c-f1.depth.1.bin.gz at 1324301b, data:render/closing-r9-x/out/20261113-081821/zls/z242-c-f2.depth.1.bin.gz at 1324301b, data:render/closing-r9-x/out/20261113-081821/zls/z243-ctl.depth.1.bin.gz at 1324301b, data:render/closing-r9-x/out/20261113-081821/zls/z242-c-f0.txt.gz at 1324301b, data:render/closing-r9-x/out/20261113-081821/zls/z242-c-f1.txt.gz at 1324301b, data:render/closing-r9-x/out/20261113-081821/zls/z242-c-f2.txt.gz at 1324301b, data:render/closing-r9-x/out/20261113-081821/zls/z243-ctl.txt.gz at 1324301b, data:render/closing-r9-x/out/20261113-081821/zls/z243-f1-less.txt.gz at 1324301b, data:pbe/sideband-channels/pbe-sideband-channels-0208/raw.txt at 1324301b, data:pbe/sideband-channels/pbe-sideband-channels-020f/raw.txt at 1324301b, data:pbe/sideband-channels/pbe-sideband-channels-0207/raw.txt at 1324301b, data:pbe/sideband-channels/pbe-sideband-channels-0247/raw.txt at 1324301b, data:pbe/sideband-channels/pbe-sideband-channels-0208/bins/eot_plain.bin at 1324301b, data:pbe/sideband-channels/pbe-sideband-channels-0208/bins/pbe-sideband-channels-0208__0.bin at 1324301b, data:pbe/sideband-channels/pbe-sideband-channels-0208/bins/pbe-sideband-channels-0208__1.bin at 1324301b, data:isp/msaa-ident/dumps/A-m1-tee0-64x64-x.txt.gz at 1324301b, data:isp/msaa-ident/dumps/A-m0-te20-64x64-x.txt.gz at 1324301b, data:isp/msaa-ident/dumps/A-m1-te60-64x64-x.txt.gz at 1324301b, data:dpm/partial-reload-pos/dpm-partial-reload-pos-pa0/bins/dpm-partial-reload-pos-pa0__0.bin at 1324301b, data:dpm/partial-reload-pos/dpm-partial-reload-pos-pa0/bins/pix_pa0.bin at 1324301b, data:dpm/partial-reload-pos/dpm-partial-reload-pos-pa1/bins/pix_pa1.bin at 1324301b, data:texture/p1141/recompute/msaa_model.py at 1324301b, resgx545:crates/sgx-pipe/src/ta.rs at dd291289, resgx545:crates/sgx-pipe/src/zls.rs at dd291289, 4623753f2cc5b9a34b357736801a4c6e66138bf9 at built; tools: TOOLSRC.sha256: 703cbceaae8cdff3eda280b7ef89f3c5ef14ba7d378dd269bc66ef714aaead69 4623753f2cc5b9a34b357736801a4c6e66138bf9:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=B60AB0B475DD1E8972419B5; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW"]
date = "2026-11-13"
data = ["render-closing-r10-x:out/20261113-101116/zov/"]
terms = ["CR_ISP_ZLSCTL"]
+++
**What ran.** A plane z = 0, ZX, 1 at (0,0), (2W,0), (0,2H) (ZX the largest power of two at most
1/(2H)), so that every pixel of the tile area has its own float, stored by E466's control in format
0
at the full pitch (the controls) and at G 0, 1, 1, 2, 3 for 64 x 32, 128 x 32, 96 x 48, 160 x 48 and
256 x 64 (whole tiles), and at 64 x 32 G 0 in format 1; depth less with writes, every dump kept.
Each dword of an overlapping store is named by its float through the full-pitch control of the same
size.

**Frozen verdict (as printed).** attempt 20261113-101116, stage zov (run.log): `SUMMARY: zov:
H-EARLY/HDR is not supported: 0 held, 5 FAILED, 0 cannot tell of 5`; attempt 20261113-101116, stage
zov (run.log): `SUMMARY: zov: H-EARLY/HDR/H-EXT is not supported: 0 held, 1 FAILED, 0 cannot tell of
1`; attempt 20261113-101116, stage zov (run.log): `SUMMARY: zov: H-EARLY/RASTER is not supported: 1
held, 4 FAILED, 0 cannot tell of 5`; attempt 20261113-101116, stage zov (run.log): `SUMMARY: zov:
H-EARLY/RASTER/H-EXT is not supported: 0 held, 1 FAILED, 0 cannot tell of 1`; attempt
20261113-101116, stage zov (run.log): `SUMMARY: zov: H-LATE/HDR (5 of 5 rows decided)`; attempt
20261113-101116, stage zov (run.log): `SUMMARY: zov: H-LATE/HDR/H-EXT (1 of 1 rows decided)`;
attempt 20261113-101116, stage zov (run.log): `SUMMARY: zov: H-LATE/RASTER is not supported: 3 held,
2 FAILED, 0 cannot tell of 5`; attempt 20261113-101116, stage zov (run.log): `SUMMARY: zov:
H-LATE/RASTER/H-EXT (1 of 1 rows decided)`.

**Results [HW].** Controls: 2048, 4096, 4608, 7680 and 16384 dwords changed, all distinct. Shared
slots: H-LATE/HDR 1536/1536, 3072/3072, 3584/3584, 5632/5632, 10240/10240; H-EARLY/HDR 1024, 2048,
2560, 3584, 4096; H-LATE/RASTER equal to HDR where the orders agree (one macrotile column) and
4608/5632, 4096/10240 at 160 x 48 and 256 x 64; H-EARLY/RASTER 10240/10240 at 256 x 64 (raster's
first is the header order's last there), 4608/5632 at 160 x 48. Format 1: 1536/1536 under H-LATE.

**What it shows.** A shared slot is overwritten whole by each tile the 3D stores into it, in the
order of the region headers: the tile visited last wins (Q242's overlapping-tiles clause). The
format-1 store at an overlapping pitch keeps E991's floor rule. The visit order is the header order
of sgx-pipe's `ta::headers` (E893, E652) on these grids [infer: the store follows the walk].

**What it does not show.** Targets with edge tiles at an overlapping pitch; 640 x 480 and larger
(four macrotiles a side); format 2 at an overlapping pitch; multisampled grids.
