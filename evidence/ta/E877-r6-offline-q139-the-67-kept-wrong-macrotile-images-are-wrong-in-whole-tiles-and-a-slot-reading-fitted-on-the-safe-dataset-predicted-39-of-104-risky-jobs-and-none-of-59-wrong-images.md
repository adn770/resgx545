+++
id = "E877"
claim = "Round 6 offline reading of the kept images of Q100's macrotile-word pokes (Q139): all 67 wrong images (8 of ta/mtile-fields, 59 of ta/mtile-fields-risky) are wrong in whole 32 x 16 tiles, no tile partly wrong [post hoc, data]; the offline macrotile test then failed: the ranking's set test (wrong tiles a union of the cells the rule's and the job's boundaries cut) holds for 5 of the 8 safe and 3 of the 59 risky wrong images, and a slot reading fitted on the safe dataset (each target region's header at N * stride + ly * mx + lx of the macrotile the job's words give it, dropped when ly * mx + lx reaches the stride, later regions winning a shared slot; 61 of its 63 jobs with an image) and frozen by hash before the risky images were read predicted the risky dataset's wrong-tile set in 39 of 104 jobs, 39 of 45 exact images and 0 of 59 wrong ones (held out by the dataset's own split: 0 of 4), so H-SLOT is FAILED"
unit = "ta"
method = "Offline, no run (round 6, decision R6-1 a; ranking closing6/rank/rank-round6.md finding 2, section 1 R6-3 and user decision 7 a). The ranking's closing6/rank/q139_tiles.py read every kept tool output (dumps/NAME.txt.gz) of resgx545-data ta/mtile-fields (E505, E506) and ta/mtile-fields-risky (E509) and counted, per job with a whole image, the 32 x 16 tiles with a pixel other than the triangle's 0xff00ff00 and whether each was wholly wrong. In the fold (2026-11-12) the macrotile test was written as closing6/fold-misc/q139/q139_model.py (readings R-CELL, the ranking's set test, and R-SLOT, a family of 48 variants over five declared axes: macrotile numbering, row pitch, clip, write order, padding) and q139_fit.py, which reads the safe dataset only and freezes the variant with the most jobs matched exactly, the first in the declared order on a tie; the model, the fit and score scripts, the fit's output and the frozen variant were hashed in q139_FROZEN.sha256 and committed to resgx545-data (106de56f, 2026-11-12 12:52:03 +0100) before q139_score.py, which checks those hashes first, read the risky dataset. The fit's author had seen q139_tiles.out, which prints each risky wrong image's tile count and column and row span, but no risky tile map before the freeze, so the score is SEMI held out. Every script was re-run from its published copy (cited/closing6/rank/, cited/closing6/fold-misc/q139/; the fit from a copy, since it writes its frozen variant beside itself) and printed output byte-identical to the kept .out files"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["ta-mtile-fields", "ta-mtile-fields-risky", "cited-scratch:closing6/rank/", "cited-scratch:closing6/fold-misc/q139/"]
terms = ["CR_TE_MTILE1", "CR_TE_MTILE2", "CR_TE_MACROTILE_STRIDE"]
+++
**What was done.** Q139 asked for the wrong images' tile maps, read per macrotile, and a test of
the four-boundary reading against them (E505, E506, E509 kept the images but read only counts). The
ranking counted the wrong tiles (`closing6/rank/q139_tiles.py`); the fold wrote the test it
describes (fit on the safe dataset, score on the risky one, the rule frozen by hash before
scoring, `closing6/fold-misc/q139/`). All re-run from their published copies: byte-identical.

**Results [HW, read post hoc]: whole tiles.** Of the safe dataset's 106 jobs, 55 drew exactly, 8
drew a wrong image and 43 faulted or kept no whole image; of the risky dataset's 223, 45, 59 and
119 (`q139_tiles.out`). In 67 of 67 wrong images every tile with a wrong pixel is wrong in all of
its 512 pixels (left `0xdeadbeef`); none is partly wrong.

**The safe fit [HW, post hoc].** Reading R-CELL (no parameter: the tiles cut into cells by the
rule's and the job's boundaries, x by `CR_TE_MTILE1`, y by `CR_TE_MTILE2`; a wrong image passes when
its wrong tiles are a union of cells) holds for 5 of the 8 safe wrong images (`q139_fit.out`). The
three it fails are at 1280 x 720: `CR_TE_MTILE1` B3 37 and 40 lose tile columns 36 to B3 - 1 in rows
0 to 43 but not in row 44, the last tile row, and `CR_TE_MTILE2` B3 37 loses row 36 and also the
tiles of rows 41 to 43 in columns 36 to 39. Of the R-SLOT family (`q139_model.py`: the TA puts each
target region's header at slot N * S + ly * P + lx of the macrotile the job's words give it, the
boundaries compared in order of use, S the job's stride, and the render draws each header in the
rule's slots; a region whose slot another region writes later, or that is dropped, is not drawn) the
best variants match 61 of the 63 safe jobs with an image (55 of 55 exact, 6 of 8 wrong): the eight
that drop a region when ly * P + lx reaches S and write no padding regions. The frozen one (the
first of the tie): macrotiles numbered down then across (E652), P the rule's macrotile width, that
clip, regions written row by row over the target, no padding regions. Its two safe misses are
`CR_TE_MTILE2` B1 16 at 640 x 480 (rows 0 to 7 lost in tile columns 8 to 19, where it predicts rows
8 to 15 lost) and the 1280 x 720 `CR_TE_MTILE2` B3 37 job (rows 41 to 43).

**The risky score [HW, SEMI held out].** Frozen verdicts (`q139_score.out`): H-SLOT FAILED, 39 of
104 jobs with an image predicted exactly: 39 of 45 exact images, 0 of 55 wrong images of the fit
cases and 0 of 4 of the held-out cases (B2 one and four more at 512 x 384). R-CELL FAILED, 3 of 59
wrong images are unions of cells. The six exact images it misses are E509's `CR_TE_MTILE2` B2 24 to
40 at 640 x 480 (B2 at or past B3), which it predicts wrong. Its wrong-image misses are not near
misses: at 256 x 256 it predicts 64 lost tiles for the `CR_TE_MTILE1` B2 values 8 to 20, which lose
28 to 32, and two thirds of the tiles lost for the `CR_TE_MTILE2` ones; the stride pokes there lose
3 to 96 tiles against 4 to 128 predicted. Post hoc, over the whole family (not a verdict), no
variant predicts more than 56 of the 104.

**What it shows.** [HW] A wrong macrotile word loses whole tiles: what decides a tile is per region
(its header or its stream), not per pixel or sample, as Q139's "per-macrotile map" step needed
[infer]. [HW] Neither the ranking's set test nor the slot reading fitted on the safe dataset
describes the risky dataset's maps, so the four-boundary reading as these two state it is refuted
on kept data (SEMI held out). [infer] The safe jobs at four macrotile columns fit "a region whose
index in its macrotile reaches the stride is not drawn, and one that lands on a slot the target does
not use is", post hoc, which explains the surviving last tile row at 1280 x 720.

**What it does not show.** Which rule places a region's header when the words differ from the
rule's, at two macrotile columns (256 x 256, 512 x 384, all of R-SLOT's held-out misses) or when a
stride or bit 31 is poked; why B2 at or past B3 of `CR_TE_MTILE2` draws exactly; what bit 31 is.
No header or stream was dumped in either dataset, so the slot reading is a reading of images only.
The 162 faulted jobs keep no image and were not scored.
