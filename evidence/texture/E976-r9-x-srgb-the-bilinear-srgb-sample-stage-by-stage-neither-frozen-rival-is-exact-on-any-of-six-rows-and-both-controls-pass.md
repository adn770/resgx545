+++
id = "E976"
claim = "r9-x stage srgb (8 jobs): with T0 bit 27 (sRGB) and bilinear filtering on injected strided texels, each lerp stage alone (fy = 0 on two jobs, fx = 0 on two, every 1/64 weight) and both (two jobs at fy 21/64 and 43/64), neither frozen rival is exact on any row: H-HALF2 (decode to half, lerps in half, closing9/rank q282_rule.json) 498 to 1009 of 2048 pixels, H-BF11 (block float, 11 bits a pair, q282_rule3.json) 502 to 733; the controls passed (E723's g-bl-st-a rerun 2048 of 2048, the equal-corner job 2048 of 2048: a lerp of equal decoded halves returns the half, stage 2 at fy = 0 returns stage 1)"
unit = "texture"
method = "r9-x (render/closing-r9-x), stage srgb of the question-closing pass (round 9, decision R9-2 (a), plan closing9/rank/rank-round9.md R9-B (Q282)), dataset render-closing-r9-x; attempt out/20261113-081821 (srgb 08:20:09 Mac time; driver log run.log; its freeze FROZEN.sha256 11292e03289f1a5147c6510706dd248eae88a906bd316f1938cfd06fbfd75c37; scores score-srgb.txt); on the laptop (host cedar, kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5 (linux fork 2a650d74, installed and loaded alike), stock firmware, tool ~/sgxfive-test-rgn4 (sha256 e6951558a93b4b7bc750eeae302997992d7ec6e26719bc527ba1ffc9c6fb779a, built from resgx545 4623753), every job one process of the kit runner (kit/run_stage.sh), a debugfs reset and the health fill and triangle between jobs, every output and dump kept gzipped; the rows are tables/STAGE.txt, the frozen predictions predictions/STAGE.tsv and predictions/STAGE/ (gen/STAGE.py)); freezes: FROZEN.sha256 11292e03289f1a5147c6510706dd248eae88a906bd316f1938cfd06fbfd75c37 (216 files), PREDICTIONS.sha256 b0d34b59ae03da1b4c3261fc7dc44b929c7ba8e8c18f8f2a972d87c5e266da7c (91 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at f32dfacc, resgx545:tools/closing/kit/lib_kit.sh at f32dfacc, resgx545:tools/closing/kit/run_stage.sh at f32dfacc, resgx545:tools/closing/kit/kitscore.py at f32dfacc, resgx545:tools/closing/kit/fake/sudo at f32dfacc, resgx545:tools/closing/kit/fake/timeout at f32dfacc, resgx545:tools/closing/kit/fake/df at f32dfacc, resgx545:tools/closing/kit/fake/modinfo at f32dfacc, resgx545:tools/closing/kit/fake/sha256sum at f32dfacc, resgx545:tools/closing/kit/fake/tool.sh at f32dfacc, resgx545:tools/closing/kit/fake/tool.py at f32dfacc, resgx545:tools/closing/kit/fake/ssh.py at f32dfacc, resgx545:tools/closing/scorekit.py at f32dfacc, resgx545:tools/closing/sessioncheck.py at f32dfacc, data:texture/p1141/templates/tx_map.s at 2d666bfa, data:texture/p1141/support/build.py at 2d666bfa, data:texture/p1141/support/texmodel.py at 2d666bfa, data:texture/p1141/support/specs.json at 2d666bfa, data:texture/p1141/gen/cases.json at 2d666bfa, data:texture/p1141/out-hw/p1141tex-dumps/tex-d-t0b27/g-bl-st-a.txt.gz at 2d666bfa, data:texture/p1141/stage-bins/p1141-t0b27__4.bin at 2d666bfa, data:texture/p1132/tx-t3/s64x32-ctl.txt.gz at 2d666bfa, data:texture/p1132/tx-t3/s64x32-t3b14.txt.gz at 2d666bfa, data:texture/p1132/tx-t3/s32x32-t3b14.txt.gz at 2d666bfa, data:texture/p1132/tx-t3/s64x16-ctl.txt.gz at 2d666bfa, data:texture/p1132/tx-t3/s64x32-t3b10.txt.gz at 2d666bfa, data:texture/p1132/tx-t3/s64x32-t3b11.txt.gz at 2d666bfa, data:texture/p1132/tx-t3/s64x32-t3b12.txt.gz at 2d666bfa, data:texture/p1141/out-hw/p1141tex-dumps/tex-d-t0b27/g-bl-st-b.txt.gz at 2d666bfa, data:texture/p1132/tx-lod/an-ctl.txt.gz at 2d666bfa, data:texture/p1132/tx-lod/an-t3b11.txt.gz at 2d666bfa, data:texture/p1132/tx-lod/an-t3b12.txt.gz at 2d666bfa, data:texture/p1132-recomp/raw/tx-t3bits/bins/tx-t3bits__0.bin at 2d666bfa, data:texture/p1132-recomp/raw/tx-t3bits/bins/tx-t3bits__14.bin at 2d666bfa, data:isp/coverage-envelope/far/raw/1401720.txt.gz at 2d666bfa, data:isp/coverage-envelope/far/raw/1401724.txt.gz at 2d666bfa, resgx545:crates/sgx-pipe/src/zls.rs at f32dfacc, 4623753f2cc5b9a34b357736801a4c6e66138bf9 at built; tools: TOOLSRC.sha256: 703cbceaae8cdff3eda280b7ef89f3c5ef14ba7d378dd269bc66ef714aaead69 4623753f2cc5b9a34b357736801a4c6e66138bf9:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=B60AB0B475DD1E8972419B5; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW"]
date = "2026-11-13"
data = ["render-closing-r9-x:out/20261113-081821/srgb/"]
terms = ["T0.BIT27"]
+++
**What ran.** srgb-ctl (E723's g-bl-st-a program), srgb-eq (equal corners, rows of decreasing
bytes), srgb-a1 and a2 (an 8 x 64 texture, columns 3 and 4 holding a byte pair per row and channel,
fy = 0, fx = x / 64), srgb-b1 and b2 (a 64 x 8 texture, fx = 0, fy = x / 64), srgb-c1 and c2 (a1's
and a2's textures at fy 21/64 and 43/64). Two half channels a pixel from texel bytes 0 and 1.

**Frozen verdict (as printed).** attempt 20261113-081821, stage srgb (run.log): `SUMMARY: srgb:
H-BF11 is not supported: 0 held, 6 FAILED, 0 cannot tell of 6`; attempt 20261113-081821, stage srgb
(run.log): `SUMMARY: srgb: H-HALF2 is not supported: 0 held, 6 FAILED, 0 cannot tell of 6`.

**Results [HW].** Pixels exact (of 2048) and halves exact (of 4096): a1 H-HALF2 1009 / 2867, H-BF11
631 / 2249; a2 899 / 2799, 623 / 2395; b1 1007 / 2928, 733 / 2455; b2 997 / 2917, 502 / 2155; c1 498
/ 2058, 647 / 2276; c2 567 / 2253, 690 / 2439. Controls 2048 of 2048 each.

**What it shows.** Each lerp stage alone already differs from both declared arithmetics: the error
is in a single stage's arithmetic, not only in how two stages combine. The kept a and b rows are a
reading table of one stage's output per weight for known corner pairs (decoded halves known exactly
from E723), on which a stage rule can be fitted and then scored on c and E723's g-bl-st-b.

**What it does not show.** No rule is held; the fit on a and b and its held-out score on c are a
later step (fold or offline), stated as post hoc if made. Only the half output of bytes 0 and 1 was
read.
