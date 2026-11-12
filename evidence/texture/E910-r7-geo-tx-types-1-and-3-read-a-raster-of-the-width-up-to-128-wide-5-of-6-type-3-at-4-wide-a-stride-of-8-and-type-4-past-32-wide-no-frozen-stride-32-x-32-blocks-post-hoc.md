+++
id = "E910"
claim = "R7-geo stage tx, types 1, 3 and 4 (Q283; E725's 64 x 32 map-texture fill, dword i of the texture 0xD0000000 | i, pixel (x, y) sampling texel (x mod w, y mod h); 11 held-out jobs and E725's type 3 control, no fault): types 1 and 3 read a raster of the width (RASTERW) at 64 x 8 and 128 x 8 and type 1 at 4 x 16 (5 of 6 held-out rows), type 3 at 4 x 16 read none of the frozen layouts (post hoc: a raster of 8 dwords a row); type 4 at 4 x 16 read stride 32 (S32 and SMAXW), and at 64 x 8, 128 x 8, 64 x 32 and 128 x 32 none of S32, SMAXW, S2WCAP, RASTERW and RASTER2W (post hoc: 32 x 32 blocks of 1024 dwords, columns 32 to 63 at +1024, in all 5 rows); FIX16 and S32 failed types 1 and 3 in 6 of 6; controls pass; frozen verdicts 'Q283 types 1 and 3 RASTERW held is not supported: 5 held, 1 FAILED, 0 cannot tell of 6' and 'Q283 type 4 S32 held is not supported: 1 held, 4 FAILED, 0 cannot tell of 5'"
unit = "texture"
method = "R7-geo stage tx of the question-closing pass, round 7 (decisions R7-2 a, R7-7 a; plan closing7/rank/rank-round7.md R7-4), dataset render-closing-r7-geo, on the laptop (host cedar), 2026-11-12, attempt out/20261112-211113 (stage started 21:12:26 Mac time, run-r7g-2.log), kernel 7.3.0-resgx545, module srcversion 41E2F5C756F96D20F7109A4 (fork 3f0b3e74, installed = loaded, knobs at their defaults at the stage start and end), stock firmware sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a, tool ~/sgxfive-test-rgn4 (t4, sha256 e6951558...); jobs `probe --temps 32 --coords --pixels` of the programs in bins/ (r7g-tyT-WxH.bin, assembled from templates/tx_map.s by resgx545 1c64f3a's usse-asm with E725's generator, gen/texbuild.py and gen/texcatalog.py, byte copies of tools/texture/p1132/gen; the control is E725's ty3-32x16 program byte for byte), the health fill and triangle after every job (type 4 and 5 rows are E725's and E567's risky class), every job class ok, health ok after each; stage tx's other six rows are E911's (type 5). Frozen before the first job (FROZEN.sha256 84ba6d23..., PREDICTIONS.sha256 a52a549b...): RASTERW, S32 and FIX16 for types 1 and 3, S32, SMAXW, S2WCAP, RASTERW and RASTER2W for type 4, as the sha256 of the 2048 sampled dwords. The first attempt (out/20261112-211042) ran nothing (E909's method). Scored by the frozen score/score_g.py tx in the run (score-tx.txt); at the fold the same scorer re-run on the kept files gave output byte-identical to the kept one, and the stage's 130 kept files decompress to the raw sha256 the laptop logged (fold/reproduce.sh, fold/reproduce.out). Post hoc at the fold, not frozen: fold/tx_read.py tries every raster stride from 1 to 256 dwords and 32 x 32 blocks on each row"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r7-geo:out/20261112-211113/tx/", "render-closing-r7-geo:fold/"]
terms = ["TEXTYPE"]
+++
**What ran.** E725 read types 3 and 1 as a raster of the texture's width (8 of 8 held out, 8 x 8 to
32 x 32) and type 4 as a raster of 32 dwords a row, fitted on its four sizes up to 32 wide. Q283
asked for widths below 8 and above 32. Stage tx ran E725's map-texture fill (a 64 x 32 window,
every texel dword naming its own offset) for types 1 and 3 at 4 x 16, 64 x 8 and 128 x 8 (RASTERW
frozen, S32 and FIX16 as rivals) and for type 4 at 4 x 16, 64 x 8, 128 x 8, 64 x 32 and 128 x 32
(S32 against SMAXW, stride max(32, w); S2WCAP, min(2 w, 64), Q283's own rival; RASTERW; RASTER2W).
Q283's widths 24 and 40 were not run (the map window maps power-of-two sizes only), nor a 128 x 64
fill for type 4 (the probe fill is fixed at 64 x 32): 64 x 32 and 128 x 32 took its place
(README, deviation 2). The controls were E725's 32 x 16 type 3 program and image, and type 5 at
16 x 16 (E894's image, E911).

**Frozen verdict (as printed).** `Q283 types 1 and 3 RASTERW held is not supported: 5 held, 1
FAILED, 0 cannot tell of 6`; FIX16 and S32 on types 1 and 3 `0 held, 6 FAILED`; `Q283 type 4 S32
held is not supported: 1 held, 4 FAILED, 0 cannot tell of 5`, SMAXW the same, S2WCAP, RASTERW
and RASTER2W `0 held, 5 FAILED`. Both controls passed.

**Results [HW].** Every one of the 2048 pixels of every row holds a texel tag (0xD000xxxx). The
frozen matches (`score-tx.txt`), and the stride read after the run (`fold/tx_read.py`: the raster
strides s with offset (y mod h) s + (x mod w) that give all 2048 pixels; 32 x 32 blocks):

| row | frozen match | raster stride (post hoc) | 32 x 32 blocks (post hoc) |
|---|---|---|---|
| type 1 at 4 x 16, 64 x 8, 128 x 8 | RASTERW | 4, 64, 128 | no |
| type 3 at 64 x 8, 128 x 8 | RASTERW | 64, 128 | no |
| type 3 at 4 x 16 | none | 8 | no |
| type 4 at 4 x 16 | S32, SMAXW | 32 | yes |
| type 4 at 64 x 8, 128 x 8, 64 x 32, 128 x 32 | none | none | yes |

At 64 and 128 wide type 4's columns 0 to 31 read offsets (y mod 32) 32 + x and columns 32 to 63 the
same plus 1024, at every height run (8 and 32 rows): the 64-pixel window does not reach columns
past 63 or rows past 31, so the block order beyond the first two blocks of a row is not read. The
control's 32 x 16 type 3 image equals E725's byte for byte.

**What it shows.** [HW] Type 1 reads a raster of the texture's width at 4, 64 and 128 wide as at
8 to 32, and type 3 at 64 and 128, held out; type 3 at 4 x 16 does not: its rows are 8 dwords
apart. Type 4 is not a raster of 32 dwords past 32 wide: no frozen stride fits. [infer] Read post
hoc, type 4 is a layout of 32 x 32 blocks of 1024 dwords, which E725's widths up to 32 could not
tell from a stride of 32, and type 3 rounds a row below 8 dwords up to 8; neither was predicted.

**What it does not show.** Columns past 63 and rows past 31 (the window), so neither type 4's
block order nor the right half of the 128-wide rasters; widths that are not powers of two (24,
40: not run); type 3 at widths 4 and below 8 other than 4; other formats than 32-bit texels.
