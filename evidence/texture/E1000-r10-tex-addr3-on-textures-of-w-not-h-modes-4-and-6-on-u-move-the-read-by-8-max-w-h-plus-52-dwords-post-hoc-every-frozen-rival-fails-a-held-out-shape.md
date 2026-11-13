+++
id = "E1000"
claim = "r10-tex stage addr3 (11 probe fills of twiddled 32-bit textures at page 12 of a 32-page named scratch, the swept u over 128 positions at one texel a step, v on texel H / 2, no fault): every frozen rival for the offset that u modes 4 and 6 add past E561's index failed a held-out shape: 'H-W (heldout) is not supported: 4 held, 2 FAILED, 0 cannot tell of 6', 'H-H (heldout) is not supported: 5 held, 1 FAILED, 0 cannot tell of 6', H-SQ and H-WH 3 held, 3 FAILED; the 32 x 8 replicate read + 308 (H-W, E565's), 8 x 32 + 308 and 16 x 64 + 564 (the height's), 64 x 16 + 564 (the width's), 64 x 64 in modes 4 and 6 + 564 and 4 x 4 + 84 (every rival), 2048 of 2048 pixels each; u mode 5: H-B5 held at 32 x 16 and H-B5H at 16 x 32 (1 held, 1 FAILED each); post hoc (out/fold/post_addr.py, not frozen) every pixel of all eleven jobs is 8 max(W, H) + 52 dwords past the index, and mode 5 reads 5 max(W, H) + 52 + t left and 6 max(W, H) + 52 + t right of the texture [fitted]; the mode 0 control passed"
unit = "texture"
method = "r10-tex (render/closing-r10-tex), stage addr3 of the question-closing pass (round 10, decision R10-2 (a), plan closing10/seeds/exp-seeds-r10.md section 2 (Q177)), dataset render-closing-r10-tex; attempt out/20261113-102730 (scores score-addr3.txt); on the laptop (host cedar, kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5 (linux fork 2a650d74, installed and loaded alike), stock firmware, tool ~/sgxfive-test-rgn4 (sha256 e6951558a93b4b7bc750eeae302997992d7ec6e26719bc527ba1ffc9c6fb779a, built from resgx545 4623753), every job one `probe --temps 32 --coords --pixels` of a program assembled by gen/make.py from the pinned p1141 template tx_map.s, one process of the kit runner (kit/run_stage.sh), a debugfs reset and the health fill and triangle between jobs, no debugfs knob written, every output kept gzipped; the rows are tables/addr3.txt, the frozen predictions predictions/addr3.tsv and predictions/addr3/ (gen/addr.py)); freezes: FROZEN.sha256 6f8e1d070ae4ca90d8b7bd77fa66f973a30b6809cff827bde4486d10b76f387e (297 files), PREDICTIONS.sha256 5523f5dc2e511c6ddf2133040599a15bcfa4952d5ad3f747c290aaccb40db114 (120 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at 9849dab7, resgx545:tools/closing/kit/lib_kit.sh at 9849dab7, resgx545:tools/closing/kit/run_stage.sh at 9849dab7, resgx545:tools/closing/kit/kitscore.py at 9849dab7, resgx545:tools/closing/kit/fake/sudo at 9849dab7, resgx545:tools/closing/kit/fake/timeout at 9849dab7, resgx545:tools/closing/kit/fake/df at 9849dab7, resgx545:tools/closing/kit/fake/modinfo at 9849dab7, resgx545:tools/closing/kit/fake/sha256sum at 9849dab7, resgx545:tools/closing/kit/fake/tool.sh at 9849dab7, resgx545:tools/closing/kit/fake/tool.py at 9849dab7, resgx545:tools/closing/kit/fake/ssh.py at 9849dab7, resgx545:tools/closing/scorekit.py at 9849dab7, resgx545:tools/closing/sessioncheck.py at 9849dab7, data:render/closing-r8-geo/bins/cube-off-a2.bin at 1324301b, data:render/closing-r8-geo/out/20261113-015842/cube/cube-off-a2.txt.gz at 1324301b, data:render/closing-r4-render4x/bins/p1141-cube__4.bin at 1324301b, data:render/closing-r9-geo/gen/q284_rule.json at 1324301b, data:render/closing-r9-geo/bins/addr-ctl-u0.bin at 1324301b, data:render/closing-r9-geo/bins/addr-u4-rep.bin at 1324301b, data:render/closing-r9-geo/out/20261113-081038/addr2/addr-ctl-u0.txt.gz at 1324301b, data:render/closing-r9-geo/out/20261113-081038/addr2/addr-u4-rep.txt.gz at 1324301b, data:render/closing-r9-geo/out/20261113-081038/addr2/addr-u4-n8.txt.gz at 1324301b, data:render/closing-r9-geo/out/20261113-081038/addr2/addr-u4-n32.txt.gz at 1324301b, data:render/closing-r9-geo/out/20261113-081038/addr2/addr-u5-rep.txt.gz at 1324301b, data:render/closing-r9-geo/out/20261113-081038/cube2/cube-edge-zx.txt.gz at 1324301b, data:render/closing-r9-geo/out/20261113-081038/cube2/cube-edge-yx.txt.gz at 1324301b, data:render/closing-r9-x/bins/b14-u01.bin at 1324301b, data:render/closing-r9-x/gen/srgb.py at 1324301b, data:render/closing-r9-x/out/20261113-081821/srgb/srgb-a1.txt.gz at 1324301b, data:render/closing-r9-x/out/20261113-081821/srgb/srgb-a2.txt.gz at 1324301b, data:render/closing-r9-x/out/20261113-081821/srgb/srgb-b1.txt.gz at 1324301b, data:render/closing-r9-x/out/20261113-081821/srgb/srgb-b2.txt.gz at 1324301b, data:render/closing-r9-x/out/20261113-081821/srgb/srgb-c1.txt.gz at 1324301b, data:render/closing-r9-x/out/20261113-081821/srgb/srgb-c2.txt.gz at 1324301b, data:render/closing-r9-x/out/20261113-081821/t3/b14-u01.txt.gz at 1324301b, data:render/closing-r9-x/out/20261113-081821/t3/b14-w32s32.txt.gz at 1324301b, data:texture/p1132/tx-t3/s64x32-ctl.txt.gz at 1324301b, data:texture/p1132/tx-t3/s64x32-t3b14.txt.gz at 1324301b, data:texture/p1132/tx-t3/s64x16-ctl.txt.gz at 1324301b, data:texture/p1132-recomp/raw/tx-t3bits/bins/tx-t3bits__0.bin at 1324301b, data:texture/p1132-recomp/raw/tx-t3bits/bins/tx-t3bits__14.bin at 1324301b, data:texture/p1141/gen/cases.json at 1324301b, data:texture/p1141/stage-bins/p1141-t0b27__4.bin at 1324301b, data:texture/p1141/out-hw/p1141tex-dumps/tex-d-t0b27/g-bl-st-a.txt.gz at 1324301b, data:texture/p1141/out-hw/p1141tex-dumps/tex-d-t0b27/g-bl-st-b.txt.gz at 1324301b, data:texture/p1141/out-hw/p1141tex-dumps/tex-h-cube/cu-xn.txt.gz at 1324301b, data:texture/p1141/out-hw/p1141tex-dumps/tex-h-cube/cu-xp.txt.gz at 1324301b, data:texture/p1141/support/build.py at 1324301b, data:texture/p1141/support/specs.json at 1324301b, data:texture/p1141/support/texmodel.py at 1324301b, data:texture/p1141/templates/tx_map.s at 1324301b, 4623753f2cc5b9a34b357736801a4c6e66138bf9 at built; tools: TOOLSRC.sha256: 703cbceaae8cdff3eda280b7ef89f3c5ef14ba7d378dd269bc66ef714aaead69 4623753f2cc5b9a34b357736801a4c6e66138bf9:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=B60AB0B475DD1E8972419B5; stops in the logs: none; lead decisions in the logs: none; post hoc at the fold: out/fold/ (reproduce.sh, post_*.py and their .out)"
tiers = ["HW", "infer"]
date = "2026-11-13"
data = ["render-closing-r10-tex:out/20261113-102730/addr3/", "render-closing-r10-tex:out/fold/"]
terms = ["T0.ADDRMODE_U", "T0.ADDRMODE_V"]
+++
**What ran.** Twiddled 32-bit textures (T1 0x0c000000 | (W - 1) << 12 | (H - 1)) at dword 12288 of
a scratch whose every dword is named (T2 0x5CAFC000, `--scratch-pages 32`), the index read decoding
to its dword through E561's tile law at every shape (tiles of up to 16 x 16, raster, s first). u
swept (p - 64 + 1/2) / W over p = x | (y & 1) << 6, v on texel H / 2. Rows: the mode 0 control and
the 16 x 16 mode 4 replicate (r9-geo's programs byte for byte), E565's 32 x 8 form (u and v mode 4),
8 x 32, 16 x 64, 64 x 16 (the four rivals part on every pixel), 64 x 64 in modes 4 and 6 and 4 x 4
(every rival agrees), and u mode 5 at 16 x 32 and 32 x 16. Frozen: H-W 8 W + 52 (E957's fit), H-H
8 H + 52, H-SQ 8 sqrt(W H) + 52, H-WH 4 (W + H) + 52; mode 5 H-B5 (left 5 W + 52 + t, right
6 W + 52 + t) and H-B5H (H for W).

**Frozen verdict (as printed).** `H-B5 (heldout) is not supported: 1 held, 1 FAILED, 0 cannot tell
of 2`; `H-B5H (heldout) is not supported: 1 held, 1 FAILED, 0 cannot tell of 2`; `H-H (heldout) is
not supported: 5 held, 1 FAILED, 0 cannot tell of 6`; `H-H (replicate) is not supported: 1 held, 1
FAILED, 0 cannot tell of 2`; `H-SQ (heldout) is not supported: 3 held, 3 FAILED, 0 cannot tell of
6`; `H-SQ (replicate) is not supported: 1 held, 1 FAILED, 0 cannot tell of 2`; `H-W (heldout) is not
supported: 4 held, 2 FAILED, 0 cannot tell of 6`; `H-W (replicate) (2 of 2 rows decided)`; `H-WH
(heldout) is not supported: 3 held, 3 FAILED, 0 cannot tell of 6`; `H-WH (replicate) is not
supported: 1 held, 1 FAILED, 0 cannot tell of 2`; the control passed.

**Results [HW].** Read less E561's index, every pixel (score-addr3.txt):

| job | W x H | offset | held |
|---|---|---|---|
| addr3-u4-rep | 16 x 16 | +180 | all four |
| addr3-ns32x8-u4 | 32 x 8 | +308 | H-W |
| addr3-8x32-u4 | 8 x 32 | +308 | H-H |
| addr3-16x64-u4 | 16 x 64 | +564 | H-H |
| addr3-64x16-u4 | 64 x 16 | +564 | H-W |
| addr3-64x64-u4, -u6 | 64 x 64 | +564 | all four |
| addr3-4x4-u4 | 4 x 4 | +84 | all four |

Mode 5: inside the texture + 308 at 16 x 32 and 32 x 16; past it 16 x 32 read H-B5H's 5 x 32 + 52
+ 16 and 6 x 32 + 52 + 16, 32 x 16 H-B5's 5 x 32 + 52 + 8 and 6 x 32 + 52 + 8. Post hoc
8 max(W, H) + 52 (and mode 5 with max(W, H)) fits 2048 of 2048 on all eleven jobs
(out/fold/post_addr.out).

**What it shows.** [HW] The offset is set by the longer side, not by the width alone (E957's fitted
8 N + 52 is the square case): each single-side rival held exactly where its side is the longer.
[fitted] 8 max(W, H) + 52 dwords and mode 5's reads with max(W, H), formed after the run; no row
holds them out. The 4 x 4 texture reads + 84 = 8 x 4 + 52: the form holds below 8.

**What it does not show.** A held-out row for max(W, H); why 52 and 8 per texel of the longer
side; formats other than 32-bit, other texture types and mip chains; mode 5 with v outside the
texture.
