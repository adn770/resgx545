+++
id = "E987"
claim = "r10-zls stages zbgc, zbg and zw (13 jobs, 256 x 128, G 7): render details dword 16 (CR_ISP_BGOBJDEPTH) is the background depth, 1.0 and 0.25 poked stored at all 28279 background pixels, and at 0.25 a triangle at 0.5 under depth less drew none of its 3721 pixels; poked to -0.25 it is stored with its sign cleared in every format (H-ABS 6 of 6: 0x3e800000 in format 0 and 0xbe800000 with bit 19, 0x400000 in format 1 and 0x40004000 in format 2 with and without bit 19), H-RAW, H-CLAMP0 and H-CLAMP0P failing 6 of 6 and H-B19-INT 4, and -0.0 stores 0 (format 1); state-block word 10 poked to 0.5 reproduced E977's z242-a-f0 byte for byte, at 0.75 and 1.0 the depth is t + w - 0.5 at every dword of the target (H-OFF), at 0.125 it is 0.4 t on the frozen mask (H-LIN; 31856 of 32768 dwords post hoc), so no frozen rival held on all three rows (H-OFF 2, H-LIN 1, H-HYP 0)"
unit = "zls"
method = "r10-zls (render/closing-r10-zls), stages zbgc, zbg, zw of the question-closing pass (round 10, decision R10-4 (a), plan closing10/seeds/exp-seeds-r10.md section 6), dataset render-closing-r10-zls; attempt out/20261113-102039 (zbgc 10:23:02, zbg 10:23:32, zw 10:24:24 Mac time; driver log run.log; its freeze FROZEN.sha256 9b2abee89bbac2ffa239877c9bb6d68f131d5dcf0763c1e58cbeff6baf9a80ed; scores score-zbg.txt, score-zbgc.txt, score-zbgc.txt, score-zw.txt); on the laptop (host cedar, kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5 (linux fork 2a650d74), stock firmware, tool ~/sgxfive-test-t9 (t9, sha256 7a28be3952fb310170e861da0622d890a2e215cb761d6f21bc9321223e1b40ce, built from resgx545 97447b04 by lead/build_tool9.sh), every job one process of the kit runner, a debugfs reset and the health pair between jobs, every output and dump kept; the rows are tables/zbgc.txt, zbg.txt and zw.txt, the predictions predictions/STAGE.tsv (gen/zbg.py); zbg ran only once zbgc's two controls passed (the kit's gate)); freezes: FROZEN.sha256 9b2abee89bbac2ffa239877c9bb6d68f131d5dcf0763c1e58cbeff6baf9a80ed (60 files), PREDICTIONS.sha256 27b5b614decf201f2ea70b566948e52dc554d435b46f6af4f2d22a8ed954918d (4 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at 9849dab7, resgx545:tools/closing/kit/lib_kit.sh at 9849dab7, resgx545:tools/closing/kit/run_stage.sh at 9849dab7, resgx545:tools/closing/kit/kitscore.py at 9849dab7, resgx545:tools/closing/kit/fake/sudo at 9849dab7, resgx545:tools/closing/kit/fake/timeout at 9849dab7, resgx545:tools/closing/kit/fake/df at 9849dab7, resgx545:tools/closing/kit/fake/modinfo at 9849dab7, resgx545:tools/closing/kit/fake/sha256sum at 9849dab7, resgx545:tools/closing/kit/fake/tool.sh at 9849dab7, resgx545:tools/closing/kit/fake/tool.py at 9849dab7, resgx545:tools/closing/kit/fake/ssh.py at 9849dab7, resgx545:tools/closing/scorekit.py at 9849dab7, resgx545:tools/closing/sessioncheck.py at 9849dab7, data:render/closing-r9-x/out/20261113-081821/zst/z120-ctl-s.depth.1.bin.gz at 1324301b, data:render/closing-r9-x/out/20261113-081821/zst/z120-f3-s.depth.1.bin.gz at 1324301b, data:render/closing-r9-x/out/20261113-081821/zst/z120-f3-s.stencil.1.bin.gz at 1324301b, data:render/closing-r9-x/out/20261113-081821/zst/z120-f4-s.depth.1.bin.gz at 1324301b, data:render/closing-r9-x/out/20261113-081821/zst/z120-f4-s.stencil.1.bin.gz at 1324301b, data:render/closing-r9-x/out/20261113-081821/zst/z120-f6-s.depth.1.bin.gz at 1324301b, data:render/closing-r9-x/out/20261113-081821/zls/z242-a-f0.depth.1.bin.gz at 1324301b, data:render/closing-r9-z2/out/20261113-082522/z2/z2-a-f0.depth.1.bin.gz at 1324301b, data:render/closing-r9-z2/out/20261113-082522/z2/z2-b-f0.depth.1.bin.gz at 1324301b, data:render/closing-r9-x/tables/zst.txt at 1324301b, data:render/closing-r9-x/tables/zls.txt at 1324301b, data:render/closing-r9-k1/lead/build_tool9.sh at 1324301b, resgx545:crates/sgx-pipe/src/zls.rs at 9849dab7, 4623753f2cc5b9a34b357736801a4c6e66138bf9 at built, 97447b04b38cadac7733f0cd12503e2ef207a3bf at built; tools: TOOLSRC.sha256: 703cbceaae8cdff3eda280b7ef89f3c5ef14ba7d378dd269bc66ef714aaead69 4623753f2cc5b9a34b357736801a4c6e66138bf9:userspace/libsgxfive/tools/sgxfive-test.c; TOOLSRC.sha256: 5de429431a93ddbdcd9c20141f5c286dcc5cc72265f95d662279e09b655a3f50 97447b04b38cadac7733f0cd12503e2ef207a3bf:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=B60AB0B475DD1E8972419B5; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW"]
date = "2026-11-13"
data = ["render-closing-r10-zls:out/20261113-102039/zbgc/", "render-closing-r10-zls:out/20261113-102039/zbg/", "render-closing-r10-zls:out/20261113-102039/zw/", "render-closing-r10-zls:fold/"]
terms = ["CR_ISP_ZLSCTL", "CR_ISP_BGOBJDEPTH", "hw_render_details.isp_bgobjdepth"]
+++
**What ran.** zbgc and zbg: the triangle (0,0) (128,0) (0,64) at depth 0.5 on a 256 x 128 target,
depth less with writes, no load, the buffer filled 0xdeadbeef, `--kpoke-render 1:rd:16=V`: V = 1.0
and 0.25 in format 0 (controls), -0.25 in formats 0, 1 and 2 without and with bit 19, -0.0 in format
1; scored on the 28279 pixels with (x + 0.5) / 128 + (y + 0.5) / 64 >= 1.05 (14106 dword pairs in
format 2). zw: r9-z2's ramp (the triangle (0,0) (512,0) (0,256) at depths 0, 1, 0, format 0) with
`--poke blk:10=w`, w = 0.5 (a control against E977's kept dump), 0.75, 1.0 and 0.125, scored where x
/ 512 + y / 256 <= 0.5 within 1e-5 relative. Post hoc: fold/look.py (fold/look.out).

**Frozen verdict (as printed).** attempt 20261113-102039, stage zbgc (run.log): `SUMMARY: zbgc:
H-BGDEPTH (dword 16 is the background depth) (2 of 2 rows decided)`; attempt 20261113-102039, stage
zbg (run.log): `SUMMARY: zbg: H-ABS (6 of 6 rows decided)`; attempt 20261113-102039, stage zbg
(run.log): `SUMMARY: zbg: H-B19-INT is not supported: 2 held, 4 FAILED, 0 cannot tell of 6`; attempt
20261113-102039, stage zbg (run.log): `SUMMARY: zbg: H-CLAMP0 is not supported: 0 held, 6 FAILED, 0
cannot tell of 6`; attempt 20261113-102039, stage zbg (run.log): `SUMMARY: zbg: H-CLAMP0P is not
supported: 0 held, 6 FAILED, 0 cannot tell of 6`; attempt 20261113-102039, stage zbg (run.log):
`SUMMARY: zbg: H-RAW is not supported: 0 held, 6 FAILED, 0 cannot tell of 6`; attempt
20261113-102039, stage zbg (run.log): `SUMMARY: zbg: H-ZERO (1 of 1 rows decided)`; attempt
20261113-102039, stage zw (run.log): `SUMMARY: zw: H-HYP is not supported: 0 held, 3 FAILED, 0
cannot tell of 3`; attempt 20261113-102039, stage zw (run.log): `SUMMARY: zw: H-LIN is not
supported: 1 held, 2 FAILED, 0 cannot tell of 3`; attempt 20261113-102039, stage zw (run.log):
`SUMMARY: zw: H-OFF is not supported: 2 held, 1 FAILED, 0 cannot tell of 3`.

**Results [HW].** Controls: zbg-c1 and zbg-c25 32768 changed dwords and the poked word at every
background pixel; the triangle's 3721 pixels 0x3f000000 under 1.0 and 0x3e800000 under 0.25. zbg:
every background dword 0x3e800000 (format 0), 0xbe800000 (format 0, bit 19), 0x00400000 (format 1,
both), 0x40004000 (format 2, both); 0 under -0.0. zw: zw-c50 equal to E977's z242-a-f0; the median z
/ t on the mask 2.718 (w 0.75), 4.436 (1.0) and 0.4000 (0.125); over the whole target H-OFF holds at
32768 of 32768 dwords for w 0.75 and 1.0 and at none for 0.125, H-LIN at 31856 of 32768 for 0.125;
at y = 0, x = 0, 64, 128, 255: 0.25098, 0.37598, 0.50098, 0.74902 (w 0.75).

**What it shows.** The background depth reaches the store as a load does, with its sign cleared
(E467) [infer: the same path], so a negative depth meets the integer conversion by neither the
background nor the viewport (E981) route, and bit 19 again changes no integer dword; the background
depth is also the depth test's start value. Word 10 is the viewport's z offset (3d.md) while the
plane stays at or above 0 (w 0.5 to 1.0); below, the plane is scaled, 0.4 t at 0.125 and 0.6 t at
0.25 (E981's ramp a), on the line 1.6 w + 0.2 through those two and w = 0.5 [infer: post hoc, two
points].

**What it does not show.** Why a negative near depth turns the offset into a scale, and the bend of
E981's ramp past x / 512 + y / 256 = 0.81 (the 912 dwords of zw-0125 off H-LIN lie there too); bit
19 with a negative depth that reaches an integer conversion unsigned (no route ran).
