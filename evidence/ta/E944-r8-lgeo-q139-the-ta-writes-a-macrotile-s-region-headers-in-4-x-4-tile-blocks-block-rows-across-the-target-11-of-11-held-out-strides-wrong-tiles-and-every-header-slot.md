+++
id = "E944"
claim = "R8-lgeo stage q139 (Q139; 20 TA-dump jobs at 256 x 256, 640 x 480 and 1280 x 720, one --kpoke-render of the stride or a macrotile word inside the ranges that drew without a fault in the kept data, no fault): with R7-BLK's slots (E907) the TA writes the region headers in 4 x 4 tile blocks, block rows across the target, a later header overwriting an earlier one (block order, frozen from the round 8 planning's SEMI reading P1: the wrong-tile set and every header slot of 11 of 11 held-out strides, 256 x 256 strides 3, 5, 6, 7, 12, 20 and 640 x 480 strides 5, 6, 7, 8, 12), where row order (E907 as frozen) held 4 (the strides where the two give one map), blocks column by column 0 and macrotile then block 0; the fit strides 1 and 2 replicated their datasets' images with block order's slots; P1's four residue jobs replicated their images and no order gives them; controls pass; frozen verdict 'Q139 write order on the held-out strides: block order (blkrow) predicts the wrong-tile sets and every header slot (11 of 11 rows decided)'"
unit = "ta"
method = "R8-lgeo stage q139 of the question-closing pass, round 8 (decision R8-8; plan closing8/leftovers/exp-leftovers-r8.md sections 0 (P1) and 3, session L2), dataset render-closing-r8-lgeo, on the laptop, 2026-11-13, one attempt out/20261113-024441 (lead log out/run-r8m.log; no stop, no lead decision), kernel 7.3.0-resgx545, module srcversion 37EC97AB0CB37213C42FCCC (fork 664fd0d0), stock firmware, tool ~/sgxfive-test-rgn4 (t4, sha256 e6951558..., resgx545 4623753), built on the session kit (resgx545 91f21da); jobs: r7-rp's q139 command token for token, `tri --tri-full --pixels --width W --height H --max-width W --max-height H [--kpoke-render 1:ta:N=V] --wait-ms 20000 --keep-going --dump-render \"$W\"` (the TA data and parameter buffer copied after the render), the unpoked 256 x 256 and 640 x 480 baselines and 256 x 256 stride 4 (controls), strides 1 and 2 (fit, their images kept by ta/mtile-fields-risky, never dumped), 11 held-out strides, and the residue: 256 x 256 m1-B2-10 and m1-B2-11, 640 x 480 m1-B1-23, 1280 x 720 m2-B3p1 with their datasets' own pokes; every job class ok. Frozen before the first job (FROZEN.sha256 90ab0f4d..., PREDICTIONS.sha256 df01463d..., FROZEN.commits at resgx545 91f21da and resgx545-data 1e83dc86): per row and order the wrong-tile set and the header slot of every target tile (gen/q139model.py over a byte copy of render/closing-r7-rp/fold/q139_fit.py, the planning's order keys; predictions/q139/NAME.ORDER.slots); a held-out row holds for an order iff its wrong-tile set (lib_dump.image_tiles, E877's reading) and every tile's slot (lib_dump.observed_slots from the baseline's header base) are the order's; controls: the baselines' exact image, one header a tile and R7-BLK's slots, and stride 4's kept wrong set (E907's held-out row). Block order rests on the planning's P1 (SEMI: read from r7-rp's 21 dumps, stride 4 among them, and held out on 136 of 140 kept images of the datasets without a dump). Scored by the frozen score/score.py q139 in the run (score-q139.txt); at the fold the same scorer re-ran byte-identical on the kept files and every kept file decompresses to the raw sha256 the laptop logged (out/fold/reproduce.sh)"
tiers = ["HW"]
date = "2026-11-13"
data = ["render-closing-r8-lgeo:out/20261113-024441/q139/", "ta-mtile-fields", "ta-mtile-fields-risky"]
terms = ["CR_TE_MTILE1", "CR_TE_MTILE2", "CR_TE_MACROTILE_STRIDE"]
+++
**What ran.** E907 fitted R7-BLK, the slot a region header takes under poked macrotile words, and
froze row order for the writes, which missed stride 4 (9 of 10 held out); 4 x 4 tile blocks fit
all 21 dumped rows only post hoc, and the round 8 planning (P1) found block order exact on 136 of
140 kept images of E877's datasets never dumped. Stage q139 froze block order (blkrow: block rows
across the target, a block's tiles row by row) against row order (raster), blocks column by
column (blkdown) and macrotile then block (mtblk), with the wrong-tile set and every header slot,
on 11 held-out strides inside the ranges that drew without a fault, and dumped P1's four residue
jobs, which no order gives.

**Frozen verdict (as printed).** `Q139 write order on the held-out strides: block order (blkrow)
predicts the wrong-tile sets and every header slot (11 of 11 rows decided)`; `raster held is not
supported: 4 held, 7 FAILED`; `blkdown ... 0 held, 11 FAILED`; `mtblk ... 0 held, 11 FAILED`. The
three controls passed (the baselines' 128 and 600 headers at R7-BLK's slots; stride 4's 84 wrong
tiles as kept).

**Results [HW].** Every held-out row's wrong-tile set and all its header slots (128 of 128 at 256
x 256, 600 of 600 at 640 x 480) are block order's; row order gives the same map at 256 x 256
strides 12 and 20 and 640 x 480 strides 8 and 12 and misses the others (strides 3, 5, 6, 7 at 256
x 256 and 5, 6, 7 at 640 x 480). The fit strides 1 and 2 replicated their datasets' 93 and 90
wrong tiles with block order's 128 slots. The residue rows replicated their datasets' images (28,
30, 286 and 52 wrong tiles); no order gives their sets (at 1280 x 720 no baseline was dumped, so
its slots were not read).

**What it shows.** [HW] Under poked stride and macrotile words the TA writes a macrotile's region
headers block by block, 4 x 4 tiles a block, block rows across the target, each at R7-BLK's slot,
a later header overwriting an earlier one, and a tile draws iff its own header survives: held out
on 11 strides at two sizes, slots included.

**What it does not show.** The residue: jobs whose macrotile bounds are not multiples of 4 (three of
the four) and 1280 x 720 m2-B3p1, which no order and R7-BLK give; the stride's relation to the RT
data; the faulting words of E509 (not run: safe class); sizes other than 256 x 256 and 640 x 480
for the order.
