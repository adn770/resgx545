+++
id = "E1038"
claim = "r14-tex stage srgb4 on module B60AB0B4 (Q282; sRGB, T0 bit 27, 13 probe fills): the three controls passed (E723's g-bl-st-a, r13-tex's srgb3-tri and srgb3-x1's channel 0 read through the second output register, their kept images, 2048 of 2048); 'TRI-G15 (heldout) (7 of 7 rows decided)': a trilinear sRGB sample (smp2dreplace, T0 bit 9) lerps the two levels' bilinear halves (each E1025's flushed stage rule) with both floored to 2^-14 of the larger one's leading bit, the lerp exact at f/64, rounded nearest with ties up and a result below 2^-14 flushed to +0, on every pixel of a 16 x 16 counting chain at LOD 1.125, 1.5, 1.75, 1.984375, 0.25 and 1.2 and of a dark 4 x 4 chain at LOD 0.125 (fitted on E1025's row before the run, frozen by hash); E1025's post hoc 16-bit grid failed 3 rows ('TRI-RNTU ... 4 held, 3 FAILED'), the unflushed form the dark row ('TRI-G15-NF ... 6 held, 1 FAILED'), every QN- form at LOD 1.2 (f = 12, the fraction floored, 0 of 2048); texel bytes 2 and 3 (the sample's second register) on the x stage alone, the y stage alone and both: byte 2 by bytes 0 and 1's rule ('B2-FTZ-OUT (heldout) (3 of 3 rows decided)'), byte 3 decoded b / 255 (not sRGB) and filtered by the same stage rule ('A-LIN (heldout) (3 of 3 rows decided)'; A-SRGB 0 and A-BYTE 207 to 225 of 2048)"
unit = "texture"
method = "r14-tex (render/closing-r14-tex), round 14's session r14-tex (decision R14-1 (a): safe class only; the round 14 ranking plan, sections 2 and 3, stage srgb4), built on the session kit (resgx545 main dddadbd, data 3309b5fd9) and frozen before the run, dataset render-closing-r14-tex; attempt out/20261114-054258 (scores score-srgb4.txt); run by the lead with the kit's driver (log fold/run-r14t.log), 2026-11-14, on the laptop (host cedar, kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5, fork 2a650d74, loaded = installed, the kit's preflight, stock firmware), tool ~/sgxfive-test-t10 (sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, source resgx545 a581c06), every row replayed on the library mock built from its source before the freeze (each a probe of a program of ours, 'program not simulated'); a debugfs reset and the kit's health check around each job, no knob written; no stop, fault, hang or lead decision. The frozen scorer re-run on the kept files gave output byte-identical to the kept score files (fold/reproduce.out); no post-run fix. Stage srgb4 (13 jobs, probe --temps 32 --coords --pixels of programs gen/make.py assembled from the p1141 templates tx_map.s and tx_map_r11.s): srgb4-ctl, srgb4-trir, srgb4-b2x1 (controls), srgb4-t1125, t15, t175, t1984, t025, t12, tdark (trilinear), srgb4-ax, ay, axy (bytes 2 and 3); frozen rules: gen/srgb4.py on closing11 c2's rule_b.py (sha256 84bd4264..., pinned) TRI-RNTU, TRI-G15 (fit/tri_fam.py, fitted on E1025's kept srgb3-tri before the run), their -NF and QN- variants, TRI-RNE, TRI-BF11, TRI-OUT, B2-FTZ-OUT, A-LIN (fit/r11.py: E723's kept r11 point jobs, post hoc, before the run), A-SRGB, A-BYTE. Post hoc: none. freezes: FROZEN.sha256 e49eeb9efc93e74f34a118cec674b04f6f58abbe37c3c600dbe987f80cd3e15f (287 files), PREDICTIONS.sha256 e55fd102e29b393caa8ed96ae09744516d0befee1ea4a087105e5a68fff1157d (168 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at dddadbdd, resgx545:tools/closing/kit/lib_kit.sh at dddadbdd, resgx545:tools/closing/kit/run_stage.sh at dddadbdd, resgx545:tools/closing/kit/kitscore.py at dddadbdd, resgx545:tools/closing/kit/fake/sudo at dddadbdd, resgx545:tools/closing/kit/fake/timeout at dddadbdd, resgx545:tools/closing/kit/fake/df at dddadbdd, resgx545:tools/closing/kit/fake/modinfo at dddadbdd, resgx545:tools/closing/kit/fake/sha256sum at dddadbdd, resgx545:tools/closing/kit/fake/tool.sh at dddadbdd, resgx545:tools/closing/kit/fake/tool.py at dddadbdd, resgx545:tools/closing/kit/fake/ssh.py at dddadbdd, resgx545:tools/closing/scorekit.py at dddadbdd, resgx545:tools/closing/sessioncheck.py at dddadbdd, data:cited/closing11/plan/c2-texture/rule_b.py at 3309b5fd, data:render/closing-r10-tex/bins/addr3-16x64-u4.bin at 3309b5fd, data:render/closing-r10-tex/bins/srgb2-ctl.bin at 3309b5fd, data:render/closing-r10-tex/out/20261113-102730/addr3/addr3-16x64-u4.txt.gz at 3309b5fd, data:render/closing-r13-tex/bins/addr4-64x16-uv5.bin at 3309b5fd, data:render/closing-r13-tex/bins/srgb3-tri.bin at 3309b5fd, data:render/closing-r13-tex/bins/srgb3-x1.bin at 3309b5fd, data:render/closing-r13-tex/out/20261113-214825/addr4/addr4-16x64-uv5.txt.gz at 3309b5fd, data:render/closing-r13-tex/out/20261113-214825/addr4/addr4-64x16-uv5.txt.gz at 3309b5fd, data:render/closing-r13-tex/out/20261113-214825/srgb3/srgb3-tri.txt.gz at 3309b5fd, data:render/closing-r13-tex/out/20261113-214825/srgb3/srgb3-x1.txt.gz at 3309b5fd, data:texture/p1132-recomp/raw/tx-border/bins/tx-border__17.bin at 3309b5fd, data:texture/p1132-recomp/raw/tx-types-risky/bins/tx-types-risky__0.bin at 3309b5fd, data:texture/p1132-recomp/raw/tx-types-risky/bins/tx-types-risky__6.bin at 3309b5fd, data:texture/p1132-recomp/raw/tx-types/bins/tx-types__10.bin at 3309b5fd, data:texture/p1132/tx-border/bd-uv5.txt.gz at 3309b5fd, data:texture/p1132/tx-types-risky/rt1-2d.txt.gz at 3309b5fd, data:texture/p1132/tx-types-risky/rt4-2d.txt.gz at 3309b5fd, data:texture/p1132/tx-types/ty3-2d.txt.gz at 3309b5fd, data:texture/p1141/gen/cases.json at 3309b5fd, data:texture/p1141/out-hw/p1141tex-dumps/tex-d-t0b27/g-bl-st-a.txt.gz at 3309b5fd, data:texture/p1141/out-hw/p1141tex-dumps/tex-d-t0b27/g-bl-st-b.txt.gz at 3309b5fd, data:texture/p1141/out-hw/p1141tex-dumps/tex-d-t0b27/g-st8x4-r11.txt.gz at 3309b5fd, data:texture/p1141/out-hw/p1141tex-dumps/tex-d-t0b27/g-tw8x8-r11.txt.gz at 3309b5fd, data:texture/p1141/support/build.py at 3309b5fd, data:texture/p1141/support/specs.json at 3309b5fd, data:texture/p1141/support/texmodel.py at 3309b5fd, data:texture/p1141/templates/tx_map.s at 3309b5fd, data:texture/p1141/templates/tx_map_r11.s at 3309b5fd, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=B60AB0B475DD1E8972419B5; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW", "infer"]
date = "2026-11-14"
data = ["render-closing-r14-tex:out/20261114-054258/srgb4/", "render-closing-r14-tex:fold/", "vectors-closing-r14-tex-pixels"]
terms = ["T0.BIT27", "T0.MIPFILTER"]
+++
**What ran.** E1025 held the bilinear sRGB stage rule with its flush below 2^-14 and found its
one trilinear row (a 16 x 16 chain at LOD 1.25) fitting no frozen form; post hoc a lerp of the two
levels' halves on a finer grid fitted 4091 of 4096 halves. Before this run a declared family of
level lerps (fit/tri_fam.py) found the grid 2^-14 of the larger half's leading bit exact on that row
(4096 of 4096); both were frozen with their rivals. Stage srgb4 ran the same chain at six other LODs
(levels 1 and 2 at f 8, 32, 48, 63 and 12.8, levels 0 and 1 at f 16) and a 4 x 4 chain injected so
that one channel is dark on both levels (its third lerp lands below 2^-14) and the other lerps a
dark
level 0 towards a bright level 1 (the two grids part). For bytes 2 and 3 it ran E723's tx_map_r11.s
(the sample's second register) on r10-tex's strided forms, each stage alone and both.

**Frozen verdict (as printed).** `out/20261114-054258/score-srgb4.txt`: "CONTROL srgb4-ctl: H-E723
2048/2048 pixels: PASS", "CONTROL srgb4-trir: H-R13 2048/2048 pixels: PASS", "CONTROL srgb4-b2x1:
H-X1 2048/2048 pixels: PASS"; "SUMMARY: srgb4: TRI-G15 (heldout) (7 of 7 rows decided)"; "TRI-RNTU
(heldout) is not supported: 4 held, 3 FAILED"; "TRI-G15-NF (heldout) is not supported: 6 held, 1
FAILED"; "TRI-RNE ... 0 held, 7 FAILED"; "TRI-BF11 ... 2 held, 5 FAILED" (TRI-OUT alike); every QN-
model "0 held, 1 FAILED"; "B2-FTZ-OUT (heldout) (3 of 3 rows decided)"; "A-LIN (heldout) (3 of 3
rows
decided)"; "A-SRGB ... 0 held, 3 FAILED"; "A-BYTE ... 0 held, 3 FAILED".

**Results [HW].** TRI-G15 2048 of 2048 on all seven rows. TRI-RNTU missed 7 (LOD 1.125), 6 (1.2) and
137 (dark) pixels, exactly where the grids part; TRI-G15-NF missed 224 pixels of the dark row, where
the lerp's result is below 2^-14 and reads +0; TRI-RNE 1587 to 2042, TRI-BF11 and TRI-OUT 436 to
2048
(they hold at LOD 1.75 and 1.984375 only). At LOD 1.2 (float32 0x3f99999a, 64 frac = 12.8) every
form
with f = 13 read 0 pixels: f is 12. Bytes 2 and 3: the low half of the second register is byte 2 by
the first register's rule (sRGB decode, the flushed stage rule) and the high half byte 3 as b / 255
by the same stage rule, 2048 of 2048 on each of the three rows; byte 3 decoded sRGB matched no
pixel, texmodel's byte blend 207 to 225.

**What it shows.** A trilinear sRGB sample takes each level's bilinear halves (E1025's rule) and
lerps them by the LOD's fraction in 64ths, floored, with both halves floored to 2^-14 of the larger
one's leading bit (a 15-bit grid; the stage rule's is 11), the lerp exact, rounded to nearest with
ties up and flushed below 2^-14, held out on seven rows, two chains, levels 0 to 2 and LOD
fractions 8 to 63. The second register of an sRGB sample holds texel bytes 2 and 3: byte 2 decoded
and filtered as bytes 0 and 1, byte 3 (alpha) decoded linearly, b / 255 to a half, and filtered by
the same stage rule, held out on three bilinear rows. [infer] Negative values are void (sRGB and
linear byte decodes are non-negative and the weights are non-negative).

**What it does not show.** Why the level lerp's grid is 15 bits and the stage's 11; a LOD whose
fraction rounds otherwise (one row parted floor from nearest); the second register under a trilinear
sample (the alpha rows were bilinear, level 0); formats other than this 32-bit one.
