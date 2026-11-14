+++
id = "E1067"
claim = "r17-tw stage tw17 (14 probe fills on t14 with a 1 MiB scratch, E1047's tx_map form; safe class, no fault, no stop): T3 bit 14 on a twiddled 32-bit texture samples a texture W' = W + 4096 texels wide at frac(u) (H-WIDE, fitted post hoc on E1049's and E1058's kept bilinear rows, held out here): under a bilinear sample columns floor(x) and floor(x) + 1 mod W', x = W' frac(u) - 1/2, rows y0 and y0 + 1 mod H, on every pixel of seven held-out fills at 16, 64, 128, 256 and 512 by 32 and 2048 by 16, across the left wrap, the right wrap and the v edge, on and off the 1/4096 grid ('H-WIDE: bit 14 bilinear: the sample over W + 4096 texels at frac u, columns mod W' (7 of 7 rows decided)'); column -1 reads W' - 1, not W - 1, by the pre-declared exact-byte rule ('LEFT-WRAP: 189 parting pixels, H-WIDE exact 188, H-WIDE-G exact 1: column -1 reads W' - 1 (H-WIDE)'); column W' reads 0, not the next tile row ('H-WIDE-NEXT ... 3 held, 4 FAILED', failing every row where it parts); a point sample reads column floor(W' frac(u)) off the 1/4096 grid at 128 by 32, 256 by 16 and 512 by 16 ('H-WIDE-PT ... (3 of 3 rows decided)'; E1049's s + floor(4096 frac(u)) 'H-TWP ... 0 held, 3 FAILED'); E1058's post hoc reading, E1049's form and the dropped filter fail ('UNWRAP-G ... 2 held, 5 FAILED', 'F-FRAC ... 1 held, 6 FAILED', 'H-POINT ... 0 held, 7 FAILED'); all four controls (E1058's bl64left rerun, the bit-clear 256 x 32, 512 x 16 and 2048 x 16) passed"
unit = "texture"
method = "r17-tw (render/closing-r17-tw), stage tw17 of the question-closing pass (round 17, safe class: decisions R17-1 to R17-4 (a) of closing17/DECISIONS-R17.md, plan closing17/plan/rank-round17.md sections 2 and 3, row tw17; H-WIDE re-derived by the builder from the kept files before the freeze, gen/derive.py, fit/derive.out; folded with the lead's confirmation, the user's standing instruction to proceed at the recommendations), dataset render-closing-r17-tw; attempt out/20261114-104432 (tw17 10:44:32 Mac time; driver log fold/run-r17w.log; scores score-tw17.txt); on the laptop (host cedar, kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5 (linux fork 2a650d74, installed and loaded alike), stock firmware, tools ~/sgxfive-test-t14 (t14, sha256 aa550b94585aaf6eb5d9b7927d320ad31ea8d1e206b8c5e99e4435c7f0a83859, built from resgx545 c58f9f9 by lead/build_tool14.sh) for the rows and ~/sgxfive-test-t10 (t10, 9bedc2d6..., from a581c06) for the health pair, every job `probe --temps 32 --coords --pixels --scratch-pages 256 bins/NAME.bin`, one process of the kit runner (kit/run_stage.sh at resgx545 c2180e6), a debugfs reset before every row, no debugfs knob written, every output and kernel slice kept gzipped; the rows are tables/tw17.txt, the frozen predictions predictions/tw17.tsv and predictions/tw17/ (gen/make.py from gen/tw17.py)); freezes: FROZEN.sha256 cb31819b5be9eb3f16bd186dad7b2351fadeda9550b9fc45dd4215a1c0b9b461 (145 files), PREDICTIONS.sha256 ee4480a50de85c7e581f4130a6fa2b82de4e596cfd1b7dce13fe721d409b39f5 (53 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at c2180e64, resgx545:tools/closing/kit/lib_kit.sh at c2180e64, resgx545:tools/closing/kit/run_stage.sh at c2180e64, resgx545:tools/closing/kit/kitscore.py at c2180e64, resgx545:tools/closing/kit/fake/sudo at c2180e64, resgx545:tools/closing/kit/fake/timeout at c2180e64, resgx545:tools/closing/kit/fake/df at c2180e64, resgx545:tools/closing/kit/fake/modinfo at c2180e64, resgx545:tools/closing/kit/fake/sha256sum at c2180e64, resgx545:tools/closing/kit/fake/tool.sh at c2180e64, resgx545:tools/closing/kit/fake/tool.py at c2180e64, resgx545:tools/closing/kit/fake/ssh.py at c2180e64, resgx545:tools/closing/scorekit.py at c2180e64, resgx545:tools/closing/sessioncheck.py at c2180e64, data:texture/p1141/templates/tx_map.s at af46e807, data:texture/p1141/support/build.py at af46e807, data:texture/p1141/support/texmodel.py at af46e807, data:render/closing-r16-tw/gen/tw16.py at af46e807, data:render/closing-r16-tw/gen/law.py at af46e807, data:render/closing-r16-tw/gen/pins.py at af46e807, data:render/closing-r16-tw/gen/tex.py at af46e807, data:render/closing-r16-tw/lead/build_tool14.sh at af46e807, data:render/closing-r14-flag/lead/build_tool14.sh at af46e807, data:render/closing-r16-tw/bins/bl64left.bin at af46e807, data:render/closing-r16-tw/out/20261114-093404/tw16/cases.tsv at af46e807, data:render/closing-r16-tw/out/20261114-093404/tw16/bl64in.txt.gz at af46e807, data:render/closing-r16-tw/out/20261114-093404/tw16/bl64left.txt.gz at af46e807, data:render/closing-r16-tw/out/20261114-093404/tw16/bl128right.txt.gz at af46e807, data:render/closing-r16-tw/out/20261114-093404/tw16/bl128vedge.txt.gz at af46e807, data:render/closing-r16-tw/out/20261114-093404/tw16/bl16h16in.txt.gz at af46e807, data:render/closing-r16-tw/out/20261114-093404/tw16/bl128h16right.txt.gz at af46e807, data:render/closing-r16-tw/out/20261114-093404/tw16/pt32h8.txt.gz at af46e807, data:render/closing-r16-tw/out/20261114-093404/tw16/pt128h8.txt.gz at af46e807, data:render/closing-r16-tw/out/20261114-093404/tw16/pt32h16.txt.gz at af46e807, data:render/closing-r16-tw/out/20261114-093404/tw16/pt128h16.txt.gz at af46e807, data:render/closing-r16-tw/out/20261114-093404/tw16/pt16h64u0.txt.gz at af46e807, data:render/closing-r16-tw/out/20261114-093404/tw16/pt16h64u1.txt.gz at af46e807, data:render/closing-r16-tw/out/20261114-093404/tw16/pt64h64u0.txt.gz at af46e807, data:render/closing-r16-tw/out/20261114-093404/tw16/pt64h64u1.txt.gz at af46e807, data:render/closing-r15-tw/gen/tw.py at af46e807, data:render/closing-r15-tw/out/20261114-074356/tw14/cases.tsv at af46e807, data:render/closing-r15-tw/out/20261114-074356/tw14/tw-bl32.txt.gz at af46e807, data:render/closing-r15-tw/out/20261114-074356/tw14/tw-bl16.txt.gz at af46e807, data:render/closing-r15-tw/out/20261114-074356/tw14/tw16-u0.txt.gz at af46e807, data:render/closing-r15-tw/out/20261114-074356/tw14/tw16-u1.txt.gz at af46e807, data:render/closing-r15-tw/out/20261114-074356/tw14/tw64-u0.txt.gz at af46e807, data:render/closing-r15-tw/out/20261114-074356/tw14/tw64-u2.txt.gz at af46e807, data:render/closing-r15-tw/out/20261114-074356/tw14/tw128-u0.txt.gz at af46e807, data:render/closing-r15-tw/out/20261114-074356/tw14/tw128-u2.txt.gz at af46e807, resgx545:tools/usse-asm/closing_tables.py at c2180e64, resgx545:crates/sgx-sim/src/tex.rs at c2180e64, resgx545:crates/sgx-pipe/tests/texture_t3b14.rs at c2180e64, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built, c58f9f9c87aa3f8370d2b66917898550d86f6879 at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; TOOLSRC.sha256: 9cef7a202fc8267fa04ab6986145b69fd4ab18beafbe6fdb5e65dd009a00b612 c58f9f9c87aa3f8370d2b66917898550d86f6879:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=B60AB0B475DD1E8972419B5; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW", "infer"]
date = "2026-11-14"
data = ["render-closing-r17-tw:out/20261114-104432/tw17/", "render-closing-r17-tw:fold/", "render-closing-r17-tw:fit/", "vectors-closing-r17-tw-pixels"]
terms = ["T3.BIT14"]
+++
**What ran.** E1047's, E1049's and E1058's form (E566's tx_map: scratch dword i reads 0xD0000000 |
i; the texture at the scratch's first dword, T0 0x07FE0000 point or 0x07FE1400 bilinear, T3
0x00800800 with or without bit 14; t14's `--scratch-pages 256`), every texture twiddled and 32-bit,
u and v float32-exact ramps of x and y, u at most one texel a pixel, v in (0, 1], every bilinear
weight a whole 64th under every frozen form. In run order: bl64leftr (control: E1058's bl64left
program byte for byte, its kept image within 1 a byte), bl16left (16 x 32, u = 1 + x / 1024: the
left wrap on the 1/4096 grid), bl64grid (64 x 32, u stepping 1/4096 across 3: both edges on the
grid), bl128off3 (128 x 32, u stepping 3/8192: pixels on and off the grid), pt128off (128 x 32,
point, u stepping 1/8192), ref256 and ref512h16 (controls: the bit-clear 256 x 32 and 512 x 16,
point, across the u edge, each with a sentinel dword its width's rows waited on), pt256off and
pt512off (256 and 512 by 16, point, off the grid), bl256edge and bl512edge (256 and 512 by 32, u
stepping 1/16384 and 1/32768 across 3 and 1), bl256corner (256 x 32 across the right edge and the v
edge at once), ref2048h16 (control: the bit-clear 2048 x 16) and bl2048edge (2048 x 16, u stepping
1/131072 across 2: 320 right-wrap pixels). The widths 256, 512 and 2048 had never run with bit 14
and came last, each after its reference; every frozen form's farthest dword was below 150000
(147541), inside E1058's 224351.

The frozen form, H-WIDE, was fitted after E1058 on the kept files of E1049 (tw-bl32, tw-bl16) and
E1058 (its six bilinear rows): the builder re-derived it with its own generator before the freeze
(gen/derive.py, fit/derive.out: 16384 of 16384 kept pixels within 1 a byte, and at the 128 left-wrap
pixels H-WIDE exact on 124, H-WIDE-G on 0). tw17's rows are held out: no kept job ran their inputs.
Its rivals: H-WIDE-G (column -1 at W - 1, names 65536 dwords apart from H-WIDE's, so within 1 a byte
one image: decided by the LEFT-WRAP rule, at least 90 % exact against at most 10 % at the pixels the
two frozen images part, at least 64 of them), H-WIDE-NEXT (column W' unwrapped, the next tile row's
first column), UNWRAP-G (E1058's post hoc reading: columns X + m and X + 1 + m, X = floor(W
frac(u) - 1/2), m = floor(4096 frac(u)), weights from W frac(u)), F-FRAC (E1049's form, refuted by
E1058), H-POINT (the filter dropped); for the point rows H-WIDE-PT (column floor(W' frac(u)))
against H-TWP (E1058's s + m). The bilinear images were frozen as texmodel's joint blend
((sum + 2048) >> 12), scored within 1 a byte.

**Frozen verdict (as printed).** attempt 20261114-104432, stage tw17 (fold/run-r17w.log): `SUMMARY:
tw17: H-WIDE: bit 14 bilinear: the sample over W + 4096 texels at frac u, columns mod W' (7 of 7
rows decided)`; `SUMMARY: tw17: H-WIDE-PT: bit 14 point read: column floor((W + 4096) frac u) (3 of
3 rows decided)`; `SUMMARY: tw17: LEFT-WRAP: 189 parting pixels, H-WIDE exact 188, H-WIDE-G exact 1:
column -1 reads W' - 1 (H-WIDE)`; `SUMMARY: tw17: H-WIDE-G: bit 14 bilinear: H-WIDE with column -1
at W - 1 (within 1) (7 of 7 rows decided)`; `SUMMARY: tw17: H-WIDE-NEXT: bit 14 bilinear: H-WIDE
with column W' the next tile row is not supported: 3 held, 4 FAILED, 0 cannot tell of 7`; `SUMMARY:
tw17: UNWRAP-G: bit 14 bilinear: columns X + m, X + 1 + m, -1 at W - 1 is not supported: 2 held, 5
FAILED, 0 cannot tell of 7`; `SUMMARY: tw17: F-FRAC: bit 14 bilinear: taps X mod W, X + 1 plus m is
not supported: 1 held, 6 FAILED, 0 cannot tell of 7`; `SUMMARY: tw17: H-POINT: bit 14 bilinear: the
filter dropped is not supported: 0 held, 7 FAILED, 0 cannot tell of 7`; `SUMMARY: tw17: H-TWP: bit
14 point read: column floor(W frac u) + floor(4096 frac u) is not supported: 0 held, 3 FAILED, 0
cannot tell of 3`.

**Results [HW].** No fault, no stop; the four controls drew their frozen images (2048 of 2048 each),
so every held-out row was decided. Every pixel of every row names a scratch dword or a blend of four
(READING lines of score-tw17.txt; the farthest, 147454, on bl512edge). H-WIDE holds within 1 on all
seven bilinear rows. At the left wrap the two frozen images part on 31 or 32 pixels of each row but
bl256corner (1): H-WIDE is exact on 188 of 189, H-WIDE-G on 1 (LEFTWRAP lines). At the right wrap
H-WIDE holds on all 32, 96, 32 and 320 pixels of bl256edge, bl512edge, bl256corner and bl2048edge
where H-WIDE-NEXT parts, and H-WIDE-NEXT on none of them (RIGHTWRAP lines; it holds only on the
three rows with no right-wrap pixel). Point: H-WIDE-PT 2048 of 2048 on each of the three rows, H-TWP
1536, 1280 and 1152, missing every off-grid pixel where the two part. UNWRAP-G holds only on
bl16left and bl64grid (on the grid, where it parts from H-WIDE by exact bytes only) and F-FRAC only
on bl16left. The frozen scorer re-run on the kept files is byte-identical (fold/reproduce.out).

Post hoc (fold/twostage.py, written after the run, its output fold/twostage.out; not part of the
frozen test): with E720's two-stage filter (each 8-bit channel (a (64 - f) + b f + 32) >> 6, x on
both rows then y; sgx-sim's rule) in place of the joint blend the frozen scorer used, H-WIDE's taps
give every byte of every pixel exactly on all sixteen bilinear bit-14 rows kept, E1049's 2, E1058's
6 and these 8 (32768 of 32768), and at the 352 left-wrap pixels where H-WIDE-G's two-stage value
differs H-WIDE-G is exact on none. The joint blend's within-1 misses (about a quarter of the pixels)
are that filter's rounding, not the footprint.

**What it shows.** [HW] On a twiddled 32-bit texture in repeat mode, T3 bit 14 makes the sampler
address a texture W' = W + 4096 texels wide (E561's tiles of 16 x min(H, 16) texels, a tile row of
W' texels, E1049 and E1058) at frac(u). A point sample reads column floor(W' frac(u)); on the 1/4096
grid that is E1049's s + floor(4096 frac(u)), off it only the wide form holds. A bilinear sample
takes x = W' frac(u) - 1/2 and the columns floor(x) and floor(x) + 1 repeated over W': column -1
reads W' - 1 and column W' reads 0, both within the wide texture, never W - 1 or the next tile row;
the rows and the v edge are the bit-clear sample's (y0 and y0 + 1 mod H); the weights come from x's
fraction in 64ths. That holds at widths 16 to 512 by 32 and 2048 by 16, on and off the 1/4096 grid.
[infer] With E720's two-stage filter it is exact on every kept pixel of three rounds (post hoc
above), so bit 14 changes the address only, not the filter. sgx-sim's tex.rs models it (point and
bilinear at the sizes run) and sgx-pipe's texture_t3b14.rs replays E1049's, E1058's and these rows
pixel for pixel.

**What it does not show.** Bilinear at heights other than 16 and 32, on 16-bit textures, or point at
widths above 128 by 32; widths past 2048; address modes other than repeat; mip levels and the LOD;
formats other than 32-bit (and u16 point); why the width grows by 4096 texels. The bit-clear
references show E561's law at 256 x 32, 512 x 16 and 2048 x 16 only across the u edge (columns W -
32 to 31).
