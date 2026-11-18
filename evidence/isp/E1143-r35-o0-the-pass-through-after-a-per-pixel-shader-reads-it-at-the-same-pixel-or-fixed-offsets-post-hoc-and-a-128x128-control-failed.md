+++
id = "E1143"
claim = "r35-o0 stage o (27 t10 probe triangles, module 7CE8E38E), Q073: the frozen rule printed NARROW with nothing decided, because the three A' controls at 128 x 128 failed and the frozen gate put the 128 x 128 control in front of every row: 'Q073 RULE CONTROLS: 13 of 16 passed: c0a-a128 FAILED, h2a-a FAILED, h2b-a FAILED'; 'Q073 RULE: NARROW: nothing decided; open: controls, (a), (b)'. A shader storing (pa0 & 0xffff0000) | (pa1 >> 16) stored that value of its own pixel on 1062 of 1062 pixels at 64 x 64 in 10 of 10 rows, and on 4269, 4254 and 4283 of 4284 pixels at 128 x 128: the other pixels, in 4 x 4 blocks (x 100-103, y 44-47 in all three), hold the value of another triangle pixel (40 of 46) or of none (6); the pass-through after the constant 0xff00ff00 kept it on 426 of 1062 pixels twice (E417's count). Post hoc, not frozen: at 64 x 64 the pass-through's kept pixels read the previous job's o0 at the same pixel (148 of 188 in three rows), 32 rows lower (36) or 32 columns right and 16 rows up (4); a debugfs reset between keeps the same 188, the t10 fill between replaces all with its colour (651), and after a 128 x 128 job a 64 x 64 pass-through keeps nothing (2 of 2)"
unit = "isp"
method = "r35-o0 (render/closing-r35-o0), stage o of the question-closing pass (round 35: closing29/plan/rank-round35.md section 3.1, R35-1 a, safe class), dataset render-closing-r35-o0; attempt out/20261118-085126 (scores score-o.txt); on the laptop at home (192.168.12.234, kernel 7.3.0-resgx545, module srcversion 7CE8E38EDB97FC5EA4F6C90 (installed and loaded alike), stock firmware, tool ~/sgxfive-test-t10 (t10, sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, built from resgx545 a581c06) for every row (`probe --temps 32 --pixels --tri pixel --width N --height N --max-width 128 --max-height 128 FILE`, N 64 or 128, E417's form; A' with --vtx-coords 2 and E081's pds_iter_xy and vtx_coords slots) and the kit's health pair, every job one process of the kit runner (kit/run_stage.sh at resgx545 eea6d2a), a debugfs reset before every A' and K row and h4's P, `noreset` elsewhere, 2026-11-18 from 08:51:26; the rows are tables/o.txt, the frozen predictions predictions/o.tsv (gen/make.py), the rule score/score.py's q073 command (fold/q073-rule.out), the score reproduced byte for byte (fold/reproduce.out), the post hoc reading fold/posthoc.out (fold/posthoc.py)); freezes: FROZEN.sha256 d4b279e8e402cb15d3606e73b3d62513280fbaa05e65343861b48e3e4209b511 (60 files), PREDICTIONS.sha256 4bf30a661d3e01ead4a49331d389f479489fce8b278b09da280ceaf945835835 (1 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at eea6d2ab, resgx545:tools/closing/kit/lib_kit.sh at eea6d2ab, resgx545:tools/closing/kit/run_stage.sh at eea6d2ab, resgx545:tools/closing/kit/kitscore.py at eea6d2ab, resgx545:tools/closing/kit/fake/sudo at eea6d2ab, resgx545:tools/closing/kit/fake/timeout at eea6d2ab, resgx545:tools/closing/kit/fake/df at eea6d2ab, resgx545:tools/closing/kit/fake/modinfo at eea6d2ab, resgx545:tools/closing/kit/fake/sha256sum at eea6d2ab, resgx545:tools/closing/kit/fake/tool.sh at eea6d2ab, resgx545:tools/closing/kit/fake/tool.py at eea6d2ab, resgx545:tools/closing/kit/fake/ssh.py at eea6d2ab, resgx545:tools/closing/scorekit.py at eea6d2ab, resgx545:tools/closing/sessioncheck.py at eea6d2ab, data:isp/o0-start/isp-o0-start-64/raw.txt at 1f5ebe6b, data:isp/o0-start/isp-o0-start-128/raw.txt at 1f5ebe6b, data:isp/o0-start/isp-o0-start-64/bins/isp-o0-start-64__0.bin at 1f5ebe6b, data:isp/o0-start/isp-o0-start-64/bins/isp-o0-start-64__1.bin at 1f5ebe6b, data:usse/output-registers/usse-output-registers-oreg-x/raw.txt at 1f5ebe6b, data:usse/output-registers/usse-output-registers-oreg-y/raw.txt at 1f5ebe6b, data:usse/output-registers/usse-output-registers-oreg-x/bins/pds_iter_xy.bin at 1f5ebe6b, data:usse/output-registers/usse-output-registers-oreg-x/bins/vtx_coords.bin at 1f5ebe6b, data:usse/output-registers/usse-output-registers-oreg-x/bins/usse-output-registers-oreg-x__0.bin at 1f5ebe6b, data:render/closing-r34-q010/out/20261116-231015/c/begin.fill1.txt.gz at 1f5ebe6b, data:render/closing-r34-q010/out/20261116-231015/c/begin.health1.txt.gz at 1f5ebe6b, resgx545:probes/isp/o0-start.toml at eea6d2ab, resgx545:probes/usse/output-registers.toml at eea6d2ab, resgx545:probes/usse/templates/pix_op.s at eea6d2ab, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=7CE8E38EDB97FC5EA4F6C90; pinned commits named by the session: resgx545 main eea6d2ab8f45; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW"]
date = "2026-11-18"
data = ["render-closing-r35-o0:out/20261118-085126/o/", "render-closing-r35-o0:fold/"]
terms = ["ISP0.PASS_TYPE"]
+++
**What ran.** One stage o of 27 t10 probe triangles in a 128 x 128 render context, in groups,
the second replicate in reverse group order. Programs: A' stores (pa0 & 0xffff0000) | ((pa1 >>
16) & 0xffff) with E081's pixpds (pa = (c + 0.5) * 2 / n - 1, unique per pixel by construction);
K stores 0xff00ff00 and P stores o0 unchanged (E417's kept bytes). Groups: c0 (A' at 64 and
128, the decoder's known value), c1 (K then P, twice), h1 (A' 64 then P 64, three times), h2 (A'
128 then P 64), h3 (A' 64 then P 128), h4 (A' 64, a debugfs reset, P 64), h5 (A' 64, the t10
fill, P 64); each P `noreset` after its A' but h4's. The pixels of each P were read against its
group's A' image.

**Frozen verdict (as printed).** Every SUMMARY line reads `controls FAILED: c0a-a128: FAILED;
h2a-a: FAILED; h2b-a: FAILED` (H-SAMEPIX, H-SLOTMAP, H-OTHER, H-TILESLOT, H-RESETKEEP,
H-RESETCLEAR, H-FILLREPLACE, H-TRIONLY). `Q073 RULE CONTROLS: 13 of 16 passed: c0a-a128 FAILED,
h2a-a FAILED, h2b-a FAILED`; `Q073 RULE: NARROW: nothing decided; open: controls, (a), (b)`.

**Results [HW].**

- A' at 64 x 64: A'(x, y) on 1062 of 1062 pixels in all 10 rows. K: 1062 pixels of 0xff00ff00
  (2 of 2). P after K: 426 of 1062 pixels of K, the rest the background (2 of 2).
- A' at 128 x 128: 4269, 4254 and 4283 of 4284 pixels A'(x, y). The 15, 30 and 1 others lie in
  4 x 4 blocks (x 100-103, y 44-47 in all three rows; also x 52-55 and 60-63, y 28-31 in h2a-a);
  40 of the 46 values are A' of another triangle pixel, 26 to 64 columns to the left, 6 are A'
  of no pixel.
- Counts of P's non-background pixels: h1 292, 188, 279; h2 0, 0; h3 344, 6; h4 188, 188; h5 651.

**Post hoc readings (not frozen, not decided).** At 64 x 64 the kept pixels of P read A' of the
same pixel (148 of 188 in h1b, h4a and h4b alike; 167 of 292 in h1a; 148 of 279 in h1c), of the
pixel 32 rows lower (36; 85 in h1a), of the pixel 32 columns right and 16 rows up (4), in h1c of
the pixel 16 rows up (59); h1a and h1c also show 36 pixels of 0xff00ff00, the colour of the job
before the A' (a P that had kept K). A reset between kept the same 188 pixels as h1b; the fill
between gave 651 pixels of its colour 0xff336699 and none of A'. P at 64 after A' at 128 kept no
pixel (2 of 2); P at 128 after A' at 64 kept 68 pixels at the same pixel, 36 at 64 columns left
and 16 rows up and 240 values A' never wrote (h3a), or 6 at the same pixel (h3b).

**What it shows.** Nothing frozen decided. The A' construction holds (every 64 x 64 pixel and all
but 1 to 30 of 4284 at 128 x 128); its 128 x 128 failures are a hardware reading: a few 4 x 4
blocks of the A' job itself store another instance's o0 [infer: the misplacement E081 saw for
o1-o3 and E1139's aliasing]. The builder's error was the gate: exactness at 128 x 128, which no
kept record had shown (E081 ran at 64 x 64 only; E417's constant colours cannot show a
misplaced pixel), was put in front of every row, the 64 x 64 rows included. The post hoc
readings suggest o0 starts as an earlier job's o0 at the same pixel or at one of a few fixed
offsets of 16 or 32 rows or 32 columns [infer]; r35-o0b freezes them as its fit.

**What it does not show.** Which pixels keep a value and why the counts differ from E417's; what
the offsets are (slots, tiles); the translucent pass; anything at 128 x 128 that the failed
controls gate.
