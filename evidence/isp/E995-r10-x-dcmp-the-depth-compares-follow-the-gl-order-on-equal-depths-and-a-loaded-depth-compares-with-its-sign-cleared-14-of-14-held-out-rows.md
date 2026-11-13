+++
id = "E995"
claim = "r10-x stage dcmp (31 jobs, 64 x 32, a flat triangle over a loaded depth buffer, the drawn count of 2048): ISP word 0's compares 0 to 7 follow the GL order never, less, equal, lequal, greater, notequal, gequal, always, exact to the ulp (frozen H-GL held 14 of 14: the eight modes at equal depths 0.5, modes 2, 3, 5, 6 one ulp above and below); a loaded depth is compared with its sign bit cleared, as an unsigned or non-negative value, NaN above every finite value (frozen H-ABS held 14 of 14 over NaN under 2, 3, 5, 6 and loaded -0.25, -0.75 and -0.0 against 0.5 and 0; the unsigned compare of the raw bits failed 4, the IEEE compare 5 and the negative-as-zero rule 5); the three controls (E977's z243-ctl 2048, never 0, always 2048) passed"
unit = "isp"
method = "r10-x (render/closing-r10-x), stage dcmp of the question-closing pass (round 10, decision R10-2 (a), plan closing10/rank/rank-round10.md R10-A (Q241, Q243)), dataset render-closing-r10-x; attempt out/20261113-101116 (dcmp 10:11:16 Mac time; driver log run.log; its freeze FROZEN.sha256 e70077bcfa0c94e9061f3a0356b49113bb78ae47322e9f060c5bb280bd007a47; scores score-dcmp.txt); on the laptop (host cedar, kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5 (linux fork 2a650d74, installed and loaded alike), stock firmware, tool ~/sgxfive-test-rgn4 (sha256 e6951558a93b4b7bc750eeae302997992d7ec6e26719bc527ba1ffc9c6fb779a, built from resgx545 4623753), every job one process of the kit runner (kit/run_stage.sh), a debugfs reset and the health fill and triangle between jobs, every output and dump kept gzipped; the rows are tables/STAGE.txt, the frozen predictions predictions/STAGE.tsv (gen/z.py)); freezes: FROZEN.sha256 e70077bcfa0c94e9061f3a0356b49113bb78ae47322e9f060c5bb280bd007a47 (151 files), PREDICTIONS.sha256 50878089db93e9928483efe7d499118b9a3e578423ed87a2deda89fbd137aa2e (78 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at dd291289, resgx545:tools/closing/kit/lib_kit.sh at dd291289, resgx545:tools/closing/kit/run_stage.sh at dd291289, resgx545:tools/closing/kit/kitscore.py at dd291289, resgx545:tools/closing/kit/fake/sudo at dd291289, resgx545:tools/closing/kit/fake/timeout at dd291289, resgx545:tools/closing/kit/fake/df at dd291289, resgx545:tools/closing/kit/fake/modinfo at dd291289, resgx545:tools/closing/kit/fake/sha256sum at dd291289, resgx545:tools/closing/kit/fake/tool.sh at dd291289, resgx545:tools/closing/kit/fake/tool.py at dd291289, resgx545:tools/closing/kit/fake/ssh.py at dd291289, resgx545:tools/closing/scorekit.py at dd291289, resgx545:tools/closing/sessioncheck.py at dd291289, data:render/closing-r9-x/out/20261113-081821/zls/z242-c-f0.depth.1.bin.gz at 1324301b, data:render/closing-r9-x/out/20261113-081821/zls/z242-c-f1.depth.1.bin.gz at 1324301b, data:render/closing-r9-x/out/20261113-081821/zls/z242-c-f2.depth.1.bin.gz at 1324301b, data:render/closing-r9-x/out/20261113-081821/zls/z243-ctl.depth.1.bin.gz at 1324301b, data:render/closing-r9-x/out/20261113-081821/zls/z242-c-f0.txt.gz at 1324301b, data:render/closing-r9-x/out/20261113-081821/zls/z242-c-f1.txt.gz at 1324301b, data:render/closing-r9-x/out/20261113-081821/zls/z242-c-f2.txt.gz at 1324301b, data:render/closing-r9-x/out/20261113-081821/zls/z243-ctl.txt.gz at 1324301b, data:render/closing-r9-x/out/20261113-081821/zls/z243-f1-less.txt.gz at 1324301b, data:pbe/sideband-channels/pbe-sideband-channels-0208/raw.txt at 1324301b, data:pbe/sideband-channels/pbe-sideband-channels-020f/raw.txt at 1324301b, data:pbe/sideband-channels/pbe-sideband-channels-0207/raw.txt at 1324301b, data:pbe/sideband-channels/pbe-sideband-channels-0247/raw.txt at 1324301b, data:pbe/sideband-channels/pbe-sideband-channels-0208/bins/eot_plain.bin at 1324301b, data:pbe/sideband-channels/pbe-sideband-channels-0208/bins/pbe-sideband-channels-0208__0.bin at 1324301b, data:pbe/sideband-channels/pbe-sideband-channels-0208/bins/pbe-sideband-channels-0208__1.bin at 1324301b, data:isp/msaa-ident/dumps/A-m1-tee0-64x64-x.txt.gz at 1324301b, data:isp/msaa-ident/dumps/A-m0-te20-64x64-x.txt.gz at 1324301b, data:isp/msaa-ident/dumps/A-m1-te60-64x64-x.txt.gz at 1324301b, data:dpm/partial-reload-pos/dpm-partial-reload-pos-pa0/bins/dpm-partial-reload-pos-pa0__0.bin at 1324301b, data:dpm/partial-reload-pos/dpm-partial-reload-pos-pa0/bins/pix_pa0.bin at 1324301b, data:dpm/partial-reload-pos/dpm-partial-reload-pos-pa1/bins/pix_pa1.bin at 1324301b, data:texture/p1141/recompute/msaa_model.py at 1324301b, resgx545:crates/sgx-pipe/src/ta.rs at dd291289, resgx545:crates/sgx-pipe/src/zls.rs at dd291289, 4623753f2cc5b9a34b357736801a4c6e66138bf9 at built; tools: TOOLSRC.sha256: 703cbceaae8cdff3eda280b7ef89f3c5ef14ba7d378dd269bc66ef714aaead69 4623753f2cc5b9a34b357736801a4c6e66138bf9:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=B60AB0B475DD1E8972419B5; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW"]
date = "2026-11-13"
data = ["render-closing-r10-x:out/20261113-101116/dcmp/"]
terms = ["ISP0.DCMP_MODE", "CR_ISP_ZLSCTL"]
+++
**What ran.** E977's z243 form: one render at 64 x 32 loads a depth buffer filled with a constant L
(control 0x0017500e: bits 1 and 14, G 1, format 0) and stores into a second buffer, one flat
`--tri-full` triangle at depth t (0.5 or 0), ISP word 0 = mode << 22 | 0x200 (the depth written);
the reading is the drawn count. Rows: modes 0 to 7 at L = t = 0.5; modes 2, 3, 5, 6 at L one ulp
above (0x3f000001) and below (0x3effffff); NaN (0x7fc00000) under 2, 3, 5, 6; L = -0.25 and -0.75
under less and greater against 0.5; L = -0.25 and -0.0 (0x80000000) under less, equal and greater
against 0. Controls: E977's z243-ctl (0.75 under less), eq-m0 and eq-m7.

**Frozen verdict (as printed).** attempt 20261113-101116, stage dcmp (run.log): `SUMMARY: dcmp:
H-ABS (14 of 14 rows decided)`; attempt 20261113-101116, stage dcmp (run.log): `SUMMARY: dcmp:
H-CLAMP0 is not supported: 9 held, 5 FAILED, 0 cannot tell of 14`; attempt 20261113-101116, stage
dcmp (run.log): `SUMMARY: dcmp: H-GL (14 of 14 rows decided)`; attempt 20261113-101116, stage dcmp
(run.log): `SUMMARY: dcmp: H-IEEE is not supported: 9 held, 5 FAILED, 0 cannot tell of 14`; attempt
20261113-101116, stage dcmp (run.log): `SUMMARY: dcmp: H-UBITS is not supported: 10 held, 4 FAILED,
0 cannot tell of 14`.

**Results [HW].** Drawn of 2048 at equal depths: modes 0, 1, 4, 5 none; 2, 3, 6, 7 all. One ulp
above (L > t): 2 none, 3 all, 5 all, 6 none; one ulp below: 2 none, 3 none, 5 all, 6 all. NaN: 2
none, 3 all, 5 all, 6 none. Negative loads against 0.5: -0.25 less none, greater all; -0.75 less
all, greater none. Against 0: -0.25 less all, equal none, greater none; -0.0 less none, equal all,
greater none. Every row is H-ABS's; H-UBITS failed neg25-m1, neg25-m4, z0-negz-m1 and z0-negz-m2;
H-IEEE
failed nan-m3, neg75-m1, neg75-m4, z0-neg25-m1 and z0-neg25-m4; H-CLAMP0 failed nan-m3, neg75-m1,
neg75-m4, z0-neg25-m1 and z0-neg25-m2.

**What it shows.** The compare modes 2, 3, 5 and 6 are equal, less or equal, not equal and greater
or equal, decided exactly on equal depths (Q241's equal-depth clause), and the flat plane at 0.5
stores and compares as 0x3f000000. A loaded depth enters the compare as its magnitude: -0.25 acts as
0.25, -0.75 as 0.75, -0.0 as 0, and NaN as a value above every depth (with E977's rows: above 0.5
under less and greater); the compare is consistent with an unsigned compare of the dwords after the
sign bit is cleared [infer: a magnitude compare of non-negative floats is the same order]. E977's
"unsigned compare of the bit patterns" holds only for its non-negative loads (its dated
correction).

**What it does not show.** A load at another address than the store's (Q243's moved base); a
triangle depth outside [0, 1]; equal depths away from 0.5 and 0; whether a passing pixel stores the
loaded sign (no store dump was scored).
