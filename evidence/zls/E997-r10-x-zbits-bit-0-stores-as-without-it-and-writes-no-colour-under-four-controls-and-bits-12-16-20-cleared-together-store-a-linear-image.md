+++
id = "E997"
claim = "r10-x stage zbits (11 jobs, E977's z242-c ramp at 80 x 40 G 2 and its z243-ctl load): ZLS control bit 0 stores the depth exactly as without it and writes no colour pixel under formats 0, 1 and 2 at G 2 and with the depth load (frozen H-E665 held 4 of 4: E977's kept dumps and store line, drawn 0); bits 15, 21 to 23 and 27 to 31 set together change nothing (H-INERT held: dump, drawn and hash equal to E977's), and the load row with all the bits changed nothing seen (H-INERT held on the load buffer and the store line); bits 12, 16 and 20 cleared together keep every value and the counts but move the dwords (H-INERT failed 3 of 3: zb-clr-f0, zb-all-f0, zb-all-f1); post hoc (fold/zbits_layout.py), every dword then holds the pixel of a linear image of the tile area with rows of 32 (G + 1) dwords (4608 of 4608 by the x each value names), not the twiddled tiles; both controls passed"
unit = "zls"
method = "r10-x (render/closing-r10-x), stage zbits of the question-closing pass (round 10, decision R10-2 (a), plan closing10/rank/rank-round10.md R10-D (Q071)), dataset render-closing-r10-x; attempt out/20261113-101116 (zbits 10:15:13 Mac time; driver log run.log; its freeze FROZEN.sha256 e70077bcfa0c94e9061f3a0356b49113bb78ae47322e9f060c5bb280bd007a47; scores score-zbits.txt); on the laptop (host cedar, kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5 (linux fork 2a650d74, installed and loaded alike), stock firmware, tool ~/sgxfive-test-rgn4 (sha256 e6951558a93b4b7bc750eeae302997992d7ec6e26719bc527ba1ffc9c6fb779a, built from resgx545 4623753), every job one process of the kit runner (kit/run_stage.sh), a debugfs reset and the health fill and triangle between jobs, every output and dump kept gzipped; the rows are tables/STAGE.txt, the frozen predictions predictions/STAGE.tsv (gen/z.py)); freezes: FROZEN.sha256 e70077bcfa0c94e9061f3a0356b49113bb78ae47322e9f060c5bb280bd007a47 (151 files), PREDICTIONS.sha256 50878089db93e9928483efe7d499118b9a3e578423ed87a2deda89fbd137aa2e (78 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at dd291289, resgx545:tools/closing/kit/lib_kit.sh at dd291289, resgx545:tools/closing/kit/run_stage.sh at dd291289, resgx545:tools/closing/kit/kitscore.py at dd291289, resgx545:tools/closing/kit/fake/sudo at dd291289, resgx545:tools/closing/kit/fake/timeout at dd291289, resgx545:tools/closing/kit/fake/df at dd291289, resgx545:tools/closing/kit/fake/modinfo at dd291289, resgx545:tools/closing/kit/fake/sha256sum at dd291289, resgx545:tools/closing/kit/fake/tool.sh at dd291289, resgx545:tools/closing/kit/fake/tool.py at dd291289, resgx545:tools/closing/kit/fake/ssh.py at dd291289, resgx545:tools/closing/scorekit.py at dd291289, resgx545:tools/closing/sessioncheck.py at dd291289, data:render/closing-r9-x/out/20261113-081821/zls/z242-c-f0.depth.1.bin.gz at 1324301b, data:render/closing-r9-x/out/20261113-081821/zls/z242-c-f1.depth.1.bin.gz at 1324301b, data:render/closing-r9-x/out/20261113-081821/zls/z242-c-f2.depth.1.bin.gz at 1324301b, data:render/closing-r9-x/out/20261113-081821/zls/z243-ctl.depth.1.bin.gz at 1324301b, data:render/closing-r9-x/out/20261113-081821/zls/z242-c-f0.txt.gz at 1324301b, data:render/closing-r9-x/out/20261113-081821/zls/z242-c-f1.txt.gz at 1324301b, data:render/closing-r9-x/out/20261113-081821/zls/z242-c-f2.txt.gz at 1324301b, data:render/closing-r9-x/out/20261113-081821/zls/z243-ctl.txt.gz at 1324301b, data:render/closing-r9-x/out/20261113-081821/zls/z243-f1-less.txt.gz at 1324301b, data:pbe/sideband-channels/pbe-sideband-channels-0208/raw.txt at 1324301b, data:pbe/sideband-channels/pbe-sideband-channels-020f/raw.txt at 1324301b, data:pbe/sideband-channels/pbe-sideband-channels-0207/raw.txt at 1324301b, data:pbe/sideband-channels/pbe-sideband-channels-0247/raw.txt at 1324301b, data:pbe/sideband-channels/pbe-sideband-channels-0208/bins/eot_plain.bin at 1324301b, data:pbe/sideband-channels/pbe-sideband-channels-0208/bins/pbe-sideband-channels-0208__0.bin at 1324301b, data:pbe/sideband-channels/pbe-sideband-channels-0208/bins/pbe-sideband-channels-0208__1.bin at 1324301b, data:isp/msaa-ident/dumps/A-m1-tee0-64x64-x.txt.gz at 1324301b, data:isp/msaa-ident/dumps/A-m0-te20-64x64-x.txt.gz at 1324301b, data:isp/msaa-ident/dumps/A-m1-te60-64x64-x.txt.gz at 1324301b, data:dpm/partial-reload-pos/dpm-partial-reload-pos-pa0/bins/dpm-partial-reload-pos-pa0__0.bin at 1324301b, data:dpm/partial-reload-pos/dpm-partial-reload-pos-pa0/bins/pix_pa0.bin at 1324301b, data:dpm/partial-reload-pos/dpm-partial-reload-pos-pa1/bins/pix_pa1.bin at 1324301b, data:texture/p1141/recompute/msaa_model.py at 1324301b, resgx545:crates/sgx-pipe/src/ta.rs at dd291289, resgx545:crates/sgx-pipe/src/zls.rs at dd291289, 4623753f2cc5b9a34b357736801a4c6e66138bf9 at built; tools: TOOLSRC.sha256: 703cbceaae8cdff3eda280b7ef89f3c5ef14ba7d378dd269bc66ef714aaead69 4623753f2cc5b9a34b357736801a4c6e66138bf9:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=B60AB0B475DD1E8972419B5; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW"]
date = "2026-11-13"
data = ["render-closing-r10-x:out/20261113-101116/zbits/", "render-closing-r10-x:fold/"]
terms = ["CR_ISP_ZLSCTL"]
+++
**What ran.** E977's z242-c rows (80 x 40, G 2, the ramp 1, 0, 1, store control 0x00171014 with the
format in bits 26:24) and its z243-ctl load row (0x0017500e) with: bits 15, 21 to 23 and 27 to 31
set and 12, 16, 20 cleared at once (formats 0 and 1 and the load row), each half alone (format 0),
and bit 0 with format 0, 1, 2 and the load row. Controls: the z242-c-f0 and -f1 reruns against
E977's
kept dumps.

**Frozen verdict (as printed).** attempt 20261113-101116, stage zbits (run.log): `SUMMARY: zbits:
H-E665 (4 of 4 rows decided)`; attempt 20261113-101116, stage zbits (run.log): `SUMMARY: zbits:
H-INERT is not supported: 2 held, 7 FAILED, 0 cannot tell of 9`.

**Results [HW].** Controls: dumps, drawn 3200 and hash 0xafb12e5a2a9a6725 equal to E977's.
zb-set-f0:
equal. zb-clr-f0, zb-all-f0, zb-all-f1: drawn 3200, the same hash and the same `depth #1:` line
(4608 changed, 138 distinct), 4465 dwords at other places. zb-all-load: load buffer and store line
equal, drawn 2048. Bit 0: drawn 0 (the image keeps the background, hash 0xd73c160502cc0925 at 80 x
40
in all three formats), dumps equal to E977's, the load row's store line equal. Post hoc
(fold/zbits_layout.py, not frozen): with 12, 16, 20 cleared the dump is H-STRIDE (dword 96 y + x)
4608/4608 by the x its value names, H-TWID 143, raster-in-tile 1610.

**What it shows.** Bit 0 suppresses the colour write and nothing of the depth path under the
formats, the load and another pitch (Q071's bit-0 clause; E665's model widens). Bits 15, 21 to 23
and 27 to 31 are inert together as alone. Bits 12, 16 and 20 cleared together, unlike any one alone
(E411), turn the tiled store into a linear image of the tile area, rows 32 (G + 1) dwords apart,
with the same values [post hoc: the x of each dword is named; the y of a row is not, the ramp is in
x only]; which of the three bits does it is not separated [infer: the window controls set 12, 16
and 20 and E337's texture attachment clears 12 and 16].

**What it does not show.** Which of bits 12, 16, 20 (or which pair) selects the linear layout;
the linear layout's y (a ramp in y); what the load reads under it (the load row's store line is
equal, its layout not dumped in a readable form); the stencil test (R10-4, the stage E988 ran).

**Correction 2026-11-13:** the last sentence named the stencil-order question for the stencil test;
that question is answered by E988 (r10-st1), whose stage ran the test, and E989 ran this record's
control mask under it. Nothing measured here changes.
