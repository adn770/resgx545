+++
id = "E1049"
claim = "r15-tw stage tw14 (14 probe fills on t14 with a 1 MiB scratch, E1047's tx_map form; safe class, no fault): T3 bit 14 on twiddled W x 32 32-bit textures at W 16, 64 and 128, with u in (0, 1), (1, 2) and (2, 3), reads on every pixel of all six held-out fills the dword of column s + floor(4096 frac(u)) (s the wrapped bit-clear column) in E561's 16 x 16 tiles with a tile row of W + 4096 texels ('H-TWP (6 of 6 rows decided)'; a constant 4128-texel tile row, the 4096 one and the move floor(128 W u) mod 4096 '0 held, 6 FAILED', u clamped to [0, 1] '3 held, 3 FAILED', failing every row past 1), and on a u16 32 x 32 the same form in texels, texel T the half T & 1 of dword T >> 1 ('U16-TX (1 of 1 rows decided)'; the move in dwords and texel pairs a dword 0 of 1); every frozen bilinear footprint failed on two rows whose footprints cross the texture's right edge ('H-FOOT-TW ... 0 held, 2 FAILED', 'H-FOOT-SHIFT ... 1 held, 1 FAILED', 'H-POINT ... 0 held, 2 FAILED'): post hoc, the taps read columns X mod W and X + 1 plus floor(4096 frac(u)), X = floor(W frac(u) - 1/2), on every pixel of both [infer]; all five controls (four bit-clear references, E1047's f1-zero rerun) passed"
unit = "texture"
method = "r15-tw (render/closing-r15-tw), stage tw14 of the question-closing pass (round 15, the round's last session, safe class: decision R15-2 (a) of closing15/DECISIONS-R15.md, plan closing15/plan/rank-round15.md sections 2 and 3, row tw14; folded with the lead's confirmation, the user's standing instruction to proceed at the recommendations), dataset render-closing-r15-tw; attempt out/20261114-074356 (tw14 07:43:57 Mac time; driver log run.log; its freeze FROZEN.sha256 4aa7748a23cc8c96ed438047798f85338ab67aedd20b8424f7e697356592518f; scores score-tw14.txt); on the laptop (host cedar, kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5 (linux fork 2a650d74, installed and loaded alike), stock firmware, tools ~/sgxfive-test-t14 (t14, sha256 aa550b94585aaf6eb5d9b7927d320ad31ea8d1e206b8c5e99e4435c7f0a83859, built from resgx545 c58f9f9 by lead/build_tool14.sh) for the rows and ~/sgxfive-test-t10 (t10, 9bedc2d6..., from a581c06) for the health pair, every job `probe --temps 32 --coords --pixels --scratch-pages 256 bins/NAME.bin`, one process of the kit runner (kit/run_stage.sh at resgx545 158bdc5), a debugfs reset before every row, no debugfs knob written, every output and kernel slice kept gzipped; the rows are tables/tw14.txt, the frozen predictions predictions/tw14.tsv and predictions/tw14/ (gen/make.py from gen/tw.py)); freezes: FROZEN.sha256 4aa7748a23cc8c96ed438047798f85338ab67aedd20b8424f7e697356592518f (113 files), PREDICTIONS.sha256 49023bfa07739ad02f484fd2bd9964bd97cc8d3738b3926b48c0cf001fb5d35c (45 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at 158bdc54, resgx545:tools/closing/kit/lib_kit.sh at 158bdc54, resgx545:tools/closing/kit/run_stage.sh at 158bdc54, resgx545:tools/closing/kit/kitscore.py at 158bdc54, resgx545:tools/closing/kit/fake/sudo at 158bdc54, resgx545:tools/closing/kit/fake/timeout at 158bdc54, resgx545:tools/closing/kit/fake/df at 158bdc54, resgx545:tools/closing/kit/fake/modinfo at 158bdc54, resgx545:tools/closing/kit/fake/sha256sum at 158bdc54, resgx545:tools/closing/kit/fake/tool.sh at 158bdc54, resgx545:tools/closing/kit/fake/tool.py at 158bdc54, resgx545:tools/closing/kit/fake/ssh.py at 158bdc54, resgx545:tools/closing/scorekit.py at 158bdc54, resgx545:tools/closing/sessioncheck.py at 158bdc54, data:texture/p1141/templates/tx_map.s at cddc7b60, data:texture/p1141/support/build.py at cddc7b60, data:texture/p1141/support/texmodel.py at cddc7b60, data:texture/p1141/support/specs.json at cddc7b60, data:texture/p1132/tx-t3/tw32-ctl.txt.gz at cddc7b60, data:render/closing-r10-tex/gen/addr.py at cddc7b60, data:render/closing-r14-flag/gen/pins.py at cddc7b60, data:render/closing-r14-flag/gen/tex.py at cddc7b60, data:render/closing-r14-flag/gen/law.py at cddc7b60, data:render/closing-r14-flag/gen/f1.py at cddc7b60, data:render/closing-r14-flag/lead/build_tool14.sh at cddc7b60, data:render/closing-r14-flag/bins/f1-zero.bin at cddc7b60, data:render/closing-r14-flag/out/20261114-060824/f1/cases.tsv at cddc7b60, data:render/closing-r14-flag/out/20261114-060824/f1/f1-tw32.txt.gz at cddc7b60, data:render/closing-r14-flag/out/20261114-060824/f1/f1-small.txt.gz at cddc7b60, data:render/closing-r14-flag/out/20261114-060824/f1/f1-zero.txt.gz at cddc7b60, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built, c58f9f9c87aa3f8370d2b66917898550d86f6879 at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; TOOLSRC.sha256: 9cef7a202fc8267fa04ab6986145b69fd4ab18beafbe6fdb5e65dd009a00b612 c58f9f9c87aa3f8370d2b66917898550d86f6879:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=B60AB0B475DD1E8972419B5; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW", "infer"]
date = "2026-11-14"
data = ["render-closing-r15-tw:out/20261114-074356/tw14/", "render-closing-r15-tw:fold/", "vectors-closing-r15-tw-pixels"]
terms = ["T3.BIT14"]
+++
**What ran.** E1047's form (E566's tx_map: scratch dword i reads 0xD0000000 | i; the texture at
the scratch's first dword, T0 0x07FE0000, T3 0x00800800 with or without bit 14; t14's
`--scratch-pages 256`), every texture twiddled and 32 rows high, v on texel row y, u a ramp of x
of at most one texel a pixel. Rows in ascending reach (the farthest dword any frozen model read,
134143 at most of 262143): controls tw-ref16, tw-refu16, tw-ref64, tw-ref128 (the bit-clear
image of each new shape, E561's law, u16 in texels) and tw-zero (E1047's f1-zero program byte for
byte, its kept image); held out tw-u16 (u16 32 x 32, u in (0, 1)), tw16-u0 and tw16-u1 (16 x 32,
u in (0, 1) and (1, 2)), tw64-u0 and tw64-u2, tw128-u0 and tw128-u2 (u in (0, 1) and (2, 3)), and
two bilinear rows (T0 | 0x1400) whose footprints all cross the texture's right edge: tw-bl32 (32 x
32, u from 0.984 to 1.015) and tw-bl16 (16 x 32, u from 1.969 to 2.031), kx = x, ky = 16.

**Frozen verdict (as printed).** attempt 20261114-074356, stage tw14 (run.log): `SUMMARY: tw14:
H-CLAMP1: bit 14 point read: u clamped to [0, 1] is not supported: 3 held, 3 FAILED, 0 cannot tell
of 6`; attempt 20261114-074356, stage tw14 (run.log): `SUMMARY: tw14: H-FOOT-SHIFT: bit 14 bilinear:
the second column unwrapped is not supported: 1 held, 1 FAILED, 0 cannot tell of 2`; attempt
20261114-074356, stage tw14 (run.log): `SUMMARY: tw14: H-FOOT-TW: bit 14 bilinear: every tap at its
wrapped texel's bit-14 address is not supported: 0 held, 2 FAILED, 0 cannot tell of 2`; attempt
20261114-074356, stage tw14 (run.log): `SUMMARY: tw14: H-POINT: bit 14 bilinear: the filter dropped
is not supported: 0 held, 2 FAILED, 0 cannot tell of 2`; attempt 20261114-074356, stage tw14
(run.log): `SUMMARY: tw14: H-TWP: bit 14 point read: s + floor(4096 frac u) in tiles, tile row W +
4096 (6 of 6 rows decided)`; attempt 20261114-074356, stage tw14 (run.log): `SUMMARY: tw14:
H-TWP4096: bit 14 point read: tile row 4096 texels is not supported: 0 held, 6 FAILED, 0 cannot tell
of 6`; attempt 20261114-074356, stage tw14 (run.log): `SUMMARY: tw14: H-TWP4128: bit 14 point read:
tile row 4128 texels is not supported: 0 held, 6 FAILED, 0 cannot tell of 6`; attempt
20261114-074356, stage tw14 (run.log): `SUMMARY: tw14: H-WRAPW: bit 14 point read: move floor(128 W
u) mod 4096 is not supported: 0 held, 6 FAILED, 0 cannot tell of 6`; attempt 20261114-074356, stage
tw14 (run.log): `SUMMARY: tw14: U16-DW: bit 14 u16: move and widening in dwords is not supported: 0
held, 1 FAILED, 0 cannot tell of 1`; attempt 20261114-074356, stage tw14 (run.log): `SUMMARY: tw14:
U16-T32: bit 14 u16: tiles of 16 x 16 dwords of texel pairs is not supported: 0 held, 1 FAILED, 0
cannot tell of 1`; attempt 20261114-074356, stage tw14 (run.log): `SUMMARY: tw14: U16-TX: bit 14
u16: H-TWP in texels, 16 x 16 texel tiles (1 of 1 rows decided)`.

**Results [HW].** No fault; the five controls drew their frozen images (2048 of 2048 each). Every
pixel of the six point rows names a scratch dword (READING lines of score-tw14.txt, dwords 256
to 132607) and H-TWP gives 2048 of 2048 on each; H-TWP4128 and H-TWP4096 1024 of each (the tile rows
from 16 on), H-WRAPW 0, H-CLAMP1 2048 on the three rows below 1 (where it is H-TWP) and 0 on the
three past it. tw-u16 reads U16-TX on 2048 of 2048 (the read is the 16-bit half, the high half
0), U16-T32 576 and U16-DW 520. tw-bl16: H-FOOT-SHIFT 2048, H-FOOT-TW 1912, H-POINT 160; tw-bl32:
H-FOOT-TW 1523, H-FOOT-SHIFT 1062, H-POINT 500. Post hoc (fold/bilin_forms.py, written after the
run, its output fold/bilin_forms.out): on tw-bl32 the unwrapped second column holds every pixel
with u below 1 and the wrapped one every pixel past it; a form with the footprint taken on frac(u),
X = floor(W frac(u) - 1/2), the left tap at column X mod W and the right at X + 1, each plus
floor(4096 frac(u)), gives 2048 of 2048 on both rows (a tap moved by its own centre's u, wrapped
or not, 0 to 32 of 512 a region). The frozen scorer re-run on the kept files is byte-identical
(fold/reproduce.out).

**What it shows.** [HW] On a twiddled texture 32 rows high, point sampled in repeat mode, T3 bit
14 reads texel (s + floor(4096 frac(u)), t) of a layout of 16 x 16 tiles with W + 4096 texels a
tile row at widths 16, 32, 64 and 128, u past 1 and 2 taken by its fraction; on u16 the counts are
texels. E1047's W + 4096 is held out against the constant 4128 it could not part. [infer] Under a
bilinear sample the footprint is formed on the fraction of u, so its left column wraps to W - 1
when X is -1 while its right column W is not wrapped; fitted on the two rows run, not held out.

**What it does not show.** The bilinear form held out (post hoc on two rows of one edge each);
heights other than 32 and widths above 128 (the reach of a taller texture passes the 1 MiB
scratch); formats other than 32-bit and u16; address modes other than repeat; mip levels.
sgx-sim's tex.rs models the point and u16 geometries run and refuses the rest (Q078).
