+++
id = "E1058"
claim = "r16-tw stage tw16 (17 probe fills on t14 with a 1 MiB scratch, E1047's tx_map form; safe class, no fault, no stop): T3 bit 14 on twiddled 32-bit textures point sampled at 32 and 128 by 8, 32 and 128 by 16 and 16 and 64 by 64 (u in (0, 1), (1, 2) and (2, 2.5), frac(u) at most 0.37 at H 64) reads on every pixel of all eight held-out fills texel (s + floor(4096 frac(u)), floor(H v) mod H) in E561's tiles of 16 x min(H, 16) texels with a tile row of W + 4096 texels ('H-TWP-H ... (8 of 8 rows decided)'; 16 x 16 tiles at H 8 '6 held, 2 FAILED', failing both H 8 rows; the move and widening 128 H '0 held, 4 FAILED'; rows mod 32, one 4096 x H strip and a 4128 tile row each failing the four H 64 rows); E1049's post hoc bilinear form failed its held-out test: taps at columns X mod W and X + 1 plus floor(4096 frac(u)) 'F-FRAC ... 3 held, 3 FAILED' (held on the three rows whose footprints stay inside the texture or cross only the v edge, failed on the three that cross the left edge), and every other frozen footprint failed too ('H-FOOT-SHIFT ... 3 held, 3 FAILED', 'H-FOOT-TW ... 3 held, 3 FAILED', 'F-VNEXT ... 1 held, 5 FAILED', 'H-POINT ... 0 held, 6 FAILED'); all three controls (bit-clear 32 x 8 and 16 x 64, E1049's tw-bl32 rerun) passed"
unit = "texture"
method = "r16-tw (render/closing-r16-tw), stage tw16 of the question-closing pass (round 16, the round's last session, safe class: decision R16-2 (a) of closing16/DECISIONS-R16.md, plan closing16/plan/rank-round16.md sections 2 and 3, row tw16; folded with the lead's confirmation, the user's standing instruction to proceed at the recommendations), dataset render-closing-r16-tw; attempt out/20261114-093404 (tw16 09:34:05 Mac time; driver log fold/run-r16w.log; scores score-tw16.txt); on the laptop (host cedar, kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5 (linux fork 2a650d74, installed and loaded alike), stock firmware, tools ~/sgxfive-test-t14 (t14, sha256 aa550b94585aaf6eb5d9b7927d320ad31ea8d1e206b8c5e99e4435c7f0a83859, built from resgx545 c58f9f9 by lead/build_tool14.sh) for the rows and ~/sgxfive-test-t10 (t10, 9bedc2d6..., from a581c06) for the health pair, every job `probe --temps 32 --coords --pixels --scratch-pages 256 bins/NAME.bin`, one process of the kit runner (kit/run_stage.sh at resgx545 b2b5288), a debugfs reset before every row, no debugfs knob written, every output and kernel slice kept gzipped; the rows are tables/tw16.txt, the frozen predictions predictions/tw16.tsv and predictions/tw16/ (gen/make.py from gen/tw16.py)); freezes: FROZEN.sha256 cfeb04d94e291a883c1c6e89aa18639909bcbce4db3588cfd993893a314c127c (152 files), PREDICTIONS.sha256 bb51998a4612ad6a03c9a3a2e9bff223e322d4195f139d1f1b4b8f3807ad57ce (78 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at b2b5288c, resgx545:tools/closing/kit/lib_kit.sh at b2b5288c, resgx545:tools/closing/kit/run_stage.sh at b2b5288c, resgx545:tools/closing/kit/kitscore.py at b2b5288c, resgx545:tools/closing/kit/fake/sudo at b2b5288c, resgx545:tools/closing/kit/fake/timeout at b2b5288c, resgx545:tools/closing/kit/fake/df at b2b5288c, resgx545:tools/closing/kit/fake/modinfo at b2b5288c, resgx545:tools/closing/kit/fake/sha256sum at b2b5288c, resgx545:tools/closing/kit/fake/tool.sh at b2b5288c, resgx545:tools/closing/kit/fake/tool.py at b2b5288c, resgx545:tools/closing/kit/fake/ssh.py at b2b5288c, resgx545:tools/closing/scorekit.py at b2b5288c, resgx545:tools/closing/sessioncheck.py at b2b5288c, data:texture/p1141/templates/tx_map.s at 62cb03b3, data:texture/p1141/support/build.py at 62cb03b3, data:texture/p1141/support/texmodel.py at 62cb03b3, data:render/closing-r15-tw/gen/tw.py at 62cb03b3, data:render/closing-r15-tw/gen/law.py at 62cb03b3, data:render/closing-r15-tw/gen/pins.py at 62cb03b3, data:render/closing-r15-tw/gen/tex.py at 62cb03b3, data:render/closing-r15-tw/lead/build_tool14.sh at 62cb03b3, data:render/closing-r15-tw/fold/bilin_forms.py at 62cb03b3, data:render/closing-r15-tw/bins/tw-bl32.bin at 62cb03b3, data:render/closing-r15-tw/out/20261114-074356/tw14/cases.tsv at 62cb03b3, data:render/closing-r15-tw/out/20261114-074356/tw14/tw-bl32.txt.gz at 62cb03b3, data:render/closing-r15-tw/out/20261114-074356/tw14/tw-bl16.txt.gz at 62cb03b3, data:render/closing-r15-tw/out/20261114-074356/tw14/tw16-u0.txt.gz at 62cb03b3, data:render/closing-r15-tw/out/20261114-074356/tw14/tw16-u1.txt.gz at 62cb03b3, data:render/closing-r15-tw/out/20261114-074356/tw14/tw64-u0.txt.gz at 62cb03b3, data:render/closing-r15-tw/out/20261114-074356/tw14/tw64-u2.txt.gz at 62cb03b3, data:render/closing-r15-tw/out/20261114-074356/tw14/tw128-u0.txt.gz at 62cb03b3, data:render/closing-r15-tw/out/20261114-074356/tw14/tw128-u2.txt.gz at 62cb03b3, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built, c58f9f9c87aa3f8370d2b66917898550d86f6879 at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; TOOLSRC.sha256: 9cef7a202fc8267fa04ab6986145b69fd4ab18beafbe6fdb5e65dd009a00b612 c58f9f9c87aa3f8370d2b66917898550d86f6879:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=B60AB0B475DD1E8972419B5; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW", "infer"]
date = "2026-11-14"
data = ["render-closing-r16-tw:out/20261114-093404/tw16/", "render-closing-r16-tw:fold/", "vectors-closing-r16-tw-pixels"]
terms = ["T3.BIT14"]
+++
**What ran.** E1047's and E1049's form (E566's tx_map: scratch dword i reads 0xD0000000 | i;
the texture at the scratch's first dword, T0 0x07FE0000 point or 0x07FE1400 bilinear, T3
0x00800800 with or without bit 14; t14's `--scratch-pages 256`), every texture twiddled, 32-bit,
u and v ramps of x and y of at most one texel a pixel, v in (0, 1]. Rows in ascending reach (the
farthest dword any frozen model read, 224351 at most of 262143): controls ref32h8 and ref16h64
(the bit-clear 32 x 8 and 16 x 64 images, E561's law, 16 x 8 tiles at H 8) and bl32r (E1049's
tw-bl32 program byte for byte, its kept image within 1 a byte); held out pt128h8, pt32h8 (H 8),
pt128h16, pt32h16 (H 16), six bilinear rows (bl16h16in and bl64in inside the texture, bl128vedge
every footprint across the v edge, bl64left 992 pixels across the left edge, bl128right and
bl128h16right half across the right edge and half across the left, u stepping 1/8192 a pixel),
then pt16h64u0, pt16h64u1, pt64h64u0 and pt64h64u1 (tile rows 2 and 3, u in (0, 0.37) and (1,
1.37)). The two H 16 rows carried a sentinel (H-TWP-H's farthest dword) that would have stopped
the stage before any farther row; both printed it.

**Frozen verdict (as printed).** attempt 20261114-093404, stage tw16 (fold/run-r16w.log):
`SUMMARY: tw16: F-FRAC: bit 14 bilinear: taps X mod W, X + 1 plus m, rows wrapped is not supported:
3 held, 3 FAILED, 0 cannot tell of 6`; `SUMMARY: tw16: F-VNEXT: bit 14 bilinear: F-FRAC with the
second row the next tile row is not supported: 1 held, 5 FAILED, 0 cannot tell of 6`; `SUMMARY:
tw16: H-FOOT-SHIFT: bit 14 bilinear: the second column unwrapped from x0 is not supported: 3 held,
3 FAILED, 0 cannot tell of 6`; `SUMMARY: tw16: H-FOOT-TW: bit 14 bilinear: every tap at its wrapped
texel's bit-14 address is not supported: 3 held, 3 FAILED, 0 cannot tell of 6`; `SUMMARY: tw16:
H-MOVEH: bit 14 point read: move and widening 128 H is not supported: 0 held, 4 FAILED, 0 cannot
tell of 4`; `SUMMARY: tw16: H-POINT: bit 14 bilinear: the filter dropped is not supported: 0 held,
6 FAILED, 0 cannot tell of 6`; `SUMMARY: tw16: H-TWP-H: bit 14 point read at H 8, 16, 64: H-TWP with
E561's tile height (8 of 8 rows decided)`; `SUMMARY: tw16: H-TWP-STRIP: bit 14 point read: one 4096
x H strip after the texture is not supported: 4 held, 4 FAILED, 0 cannot tell of 8`; `SUMMARY:
tw16: H-TWP-T16: bit 14 point read: 16 x 16 tiles at any height is not supported: 6 held, 2 FAILED,
0 cannot tell of 8`; `SUMMARY: tw16: H-TWP-V32: bit 14 point read: the wide layout spans 32 rows is
not supported: 4 held, 4 FAILED, 0 cannot tell of 8`; `SUMMARY: tw16: H-TWP4128: bit 14 point read:
tile row 4128 texels is not supported: 4 held, 4 FAILED, 0 cannot tell of 8`.

**Results [HW].** No fault, no stop; the three controls drew their frozen images (2048 of 2048
each). Every pixel of the eight point rows names a scratch dword (READING lines of
score-tw16.txt, dwords 128 to 224351) and H-TWP-H gives 2048 of 2048 on each; 16 x 16 tiles give 0
on both H 8 rows (where they part) and are H-TWP-H's image at H 16 and 64; H-MOVEH 0 on all four
rows it was scored on; rows mod 32 and the 4128 tile row 0 on the H 64 rows, the strip 976 to
1008. Bilinear: F-FRAC 2048 of 2048 on bl64in, bl16h16in and bl128vedge (where F-FRAC,
H-FOOT-SHIFT and H-FOOT-TW are one image; F-VNEXT 324 on bl128vedge, so the v edge's second row
wraps to row 0) and 1792, 944 and 912 on bl64left, bl128right and bl128h16right. Post hoc
(fold/bilin_post.py, written after the run, its output fold/bilin_post.out; not held out):
F-FRAC misses 256 of bl64left's 992 left-edge pixels, while columns X + m and X + 1 + m (the left
column not wrapped to W - 1) give all 992 and 2048 of 2048 on the row; on bl128right and
bl128h16right that unwrapped form gives every right-edge pixel whose u lies on the 1/4096 grid
(512 of 512), 480 of the 512 left-edge ones on it (the 32 misses where floor(4096 frac(u)) = 0,
column -1), and only 48 to 224 of 512 where u lies between two 1/4096 steps (the odd pixels of
those rows), 1232 and 1280 of 2048 in all; no column or move shift of up to three texels fits
those off-grid pixels as one rule. The same unwrapped form misses 17 pixels of each of E1049's
two rows, where F-FRAC held, so neither form covers both rounds. The frozen scorer re-run on the
kept files is byte-identical (fold/reproduce.out).

**What it shows.** [HW] On a twiddled 32-bit texture point sampled in repeat mode, T3 bit 14
reads texel (s + floor(4096 frac(u)), t) of E1049's wide layout at heights 8, 16 and 64 as at 32:
E561's tile height (16 x 8 at H 8), tile rows t div 16, each W + 4096 texels; the move and
widening do not scale with the height. Under a bilinear sample, E1049's post hoc footprint holds
inside the texture and across the v edge (whose second row wraps to row 0) and fails where the
footprint crosses the left edge (bl64left) and where u lies off the 1/4096 grid (bl128right,
bl128h16right).

**What it does not show.** The bilinear footprint at the edges: no frozen form held, and the post
hoc readings above fit neither this round's three failing rows nor E1049's two together [infer:
the left column's wrap may depend on the move or on u's fraction below 1/4096]; heights above 64
and widths other than those run; formats other than 32-bit at these heights; address modes other
than repeat; mip levels. sgx-sim's tex.rs models the point geometries run and refuses the
bilinear sample (Q078).
