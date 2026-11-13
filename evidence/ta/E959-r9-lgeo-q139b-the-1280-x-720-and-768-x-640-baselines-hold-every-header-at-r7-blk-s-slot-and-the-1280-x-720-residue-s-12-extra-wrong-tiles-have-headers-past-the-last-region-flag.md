+++
id = "E959"
claim = "R9-lgeo stage q139b (Q139; 4 TA-dump jobs at 1280 x 720 and 768 x 640, the datasets' own commands, no fault): the unpoked baselines draw exactly and hold one header with a stream for every target tile (controls), at the slots H-EVEN gives (8 floor(fx / 2) slots a block row of the first macrotile; equal to R7-BLK and every round 8 order at fx 12 and 8: 1800 of 1800 and 960 of 960 slots); 768 x 640 m2-B3p1 replicated its dataset's 24 wrong tiles with every header slot H-EVEN gives (960 of 960); 1280 x 720 m2-B3p1 (the residue, a reading) replicated its dataset's 52 wrong tiles, 40 of them the row no header names and 12 (columns 36 to 39, rows 41 to 43) tiles whose one header sits at H-EVEN's slot with a stream like their neighbours'; frozen verdicts 'Q139 the baselines' header slots at 1280 x 720 and 768 x 640: H-EVEN (= R7-BLK at fx 12 and 8) gives every baseline header slot (2 of 2 rows decided)' and 'Q139 768 x 640 m2-B3p1: H-EVEN (= R7-BLK and the round 8 orders there) predicts the wrong-tile set and every header slot (1 of 1 rows decided)'; read post hoc at the fold [infer]: each dump holds one header with flag bit 7 set, the residue's at slot 2211 before the 12 tiles' slots 2212 to 2223, and 'a tile draws iff its header lies at or before that slot' gives every tile of all 24 kept dumps (r8-lgeo's 20 and these 4), and with the flag on the last target tile the TA writes in block order, H-EVEN gives the wrong-tile set of 167 of 167 kept whole images of ta/mtile-fields and ta/mtile-fields-risky (166 without it)"
unit = "ta"
method = "R9-lgeo stage q139b of the question-closing pass, round 9 (decision S-4 (a) of closing9/DECISIONS-R9.md; plan closing9/seeds/exp-seeds-r9.md section 6, session S9-lgeo; H-EVEN the plan's finding 4, fitted offline on E944's three readable residue dumps), dataset render-closing-r9-lgeo, on the laptop, 2026-11-13, one attempt out/20261113-080029 (lead log out/run-r9m.log; no stop, no lead decision), kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5 (fork 2a650d74), stock firmware, tool ~/sgxfive-test-rgn4 (t4, sha256 e6951558..., resgx545 4623753 bound by source, TOOLSRC.sha256; every row replayed on the library mock before the run), built on the session kit (resgx545 f32dfac); jobs: ta/mtile-fields' command token for token, `tri --tri-full --pixels --width W --height H --max-width W --max-height H [--kpoke-render 1:ta:144=0x03018025] --wait-ms 20000 --keep-going --dump-render \"$W\"`, the unpoked 1280 x 720 and 768 x 640 baselines (controls: exact image and one header with a stream a target tile, lib_dump.baseline_layout), 768 x 640 m2-B3p1 (held out) and 1280 x 720 m2-B3p1 (residue); every job class ok. Frozen before the first job (FROZEN.sha256 bc18b46e..., PREDICTIONS.sha256 3e70e55e..., FROZEN.commits at resgx545 f32dfac and resgx545-data 2d666bfa): per row and model (H-EVEN, R7-BLK, raster, blkdown, mtblk; gen/q139even.py over r8-lgeo's gen/q139model.py and r7-rp's q139_fit.py, byte copies) the wrong-tile set and the header slot of every target tile (predictions/q139b/NAME.MODEL.slots); a row holds iff its wrong-tile set (lib_dump.image_tiles, E877's reading) and every tile's slot (lib_dump.observed_slots from the same size's baseline header base) are the model's. Scored by the frozen score/score.py q139b in the run (score-q139b.txt); at the fold the same scorer re-ran byte-identical on the kept files and every kept file decompresses to the raw sha256 the laptop logged (fold/reproduce.sh). Post hoc at the fold, not frozen: fold/q139b_residue.py (the residue's headers and streams around the 12 tiles), fold/q139b_lastflag.py (the flag reading on every kept dump of r8-lgeo and r9-lgeo, and the model side without a dump) and fold/q139b_images.py (H-EVEN with and without it on the datasets' kept images, the seeds plan's scan)"
tiers = ["HW", "infer"]
date = "2026-11-13"
data = ["render-closing-r9-lgeo:out/20261113-080029/q139b/", "render-closing-r9-lgeo:fold/", "vectors-closing-r9-lgeo-ta-slots", "render-closing-r8-lgeo:out/20261113-024441/q139/", "ta-mtile-fields", "ta-mtile-fields-risky"]
terms = ["CR_TE_MTILE1", "CR_TE_MTILE2", "CR_TE_MACROTILE_STRIDE"]
+++
**What ran.** E944 held block order with R7-BLK's slots on 11 strides at 256 x 256 and 640 x 480
and left a residue no order gave: three jobs whose first macrotile is not a multiple of 4 wide,
which the round 9 seeds plan fitted offline with H-EVEN (a block row of the first macrotile takes
8 floor(fx / 2) slots, R7-BLK 16 floor(fx / 4)), and 1280 x 720 m2-B3p1, whose slots could not be
read without a baseline of its size. Stage q139b dumped the 1280 x 720 and 768 x 640 baselines,
768 x 640 m2-B3p1 (24 wrong tiles in its dataset) and the 1280 x 720 residue. At these sizes fx is
12 and 8, so H-EVEN equals R7-BLK and every round 8 order: the rows test the slot rule at two new
sizes and do not part H-EVEN from R7-BLK (no safe-class row does: decision R9-7).

**Frozen verdict (as printed).** `Q139 the baselines' header slots at 1280 x 720 and 768 x 640:
H-EVEN (= R7-BLK at fx 12 and 8) gives every baseline header slot (2 of 2 rows decided)`; `Q139 768
x 640 m2-B3p1: H-EVEN (= R7-BLK and the round 8 orders there) predicts the wrong-tile set and every
header slot (1 of 1 rows decided)`. Both controls passed (exact images; 1800 and 960 headers, base
0x7000).

**Results [HW].** The baselines' headers sit at the frozen slots, 1800 of 1800 and 960 of 960;
768 x 640 m2-B3p1 drew its dataset's 24 wrong tiles, every header at its slot. The 1280 x 720
residue drew its dataset's 52 wrong tiles: the 40 of row 36, which no header names (the last
macrotile row starts at 37), and 12 more, columns 36 to 39 of rows 41 to 43, whose one header each
sits at H-EVEN's slot (2212 to 2223) with a three-word stream like those of the tiles that drew; all
1800 tiles' slots are H-EVEN's.

**What it shows.** [HW] The TA writes the region headers of 1280 x 720 and 768 x 640 baselines and
of 768 x 640 m2-B3p1 at R7-BLK's slots in block order (= H-EVEN there), held out; at 1280 x 720
m2-B3p1 a tile can hold its header at the right slot and still not draw, so "a tile draws iff its
header survives" (E907) does not hold there. [infer, post hoc] Each kept dump holds exactly one
header with flag bit 7 set (the residue's at 2211, tile (39, 44), the last target tile in block
order); a tile draws iff its header lies at or before that slot, on every tile of all 24 kept dumps,
and with H-EVEN this gives every kept whole image of E877's two datasets, 167 of 167: the bit reads
as the last region of the list, and headers written at later slots are not rendered. Fitted on the
one job that parts it (with its r8-lgeo replicate); not held out.

**What it does not show.** That bit 7 is a list end (a job whose last-written tile is not its
highest slot elsewhere would hold it out); H-EVEN against R7-BLK on hardware (fx 2 or 3 mod 4 drew
only with faulting words, R9-7); the stride's relation to the RT data; the faulting words of E509.
