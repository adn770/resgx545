+++
id = "E950"
claim = "Round 9 offline (Q139; no run): with the first macrotile fx tiles wide, a block row of it takes 8 floor(fx / 2) region-header slots (H-EVEN) where R7-BLK (E907) has 16 floor(fx / 4); with E944's block order and R7-BLK's slots otherwise unchanged, H-EVEN gives the wrong-tile set and every header slot of E944's three readable residue dumps (256 x 256 m1-B2-10 and m1-B2-11, 128 of 128 slots each, and 640 x 480 m1-B1-23, 600 of 600), the only one of 24 declared variants of the block-row width, the order and the local bits to give all three [HW, fitted: chosen on B2-10 and B2-11, the 640 x 480 row checked after the form was chosen]; it equals R7-BLK whenever fx is 0 or 1 mod 4, and on the 164 other kept whole images of ta/mtile-fields and ta/mtile-fields-risky it and R7-BLK both give the wrong-tile set of 163 (the miss, 1280 x 720 m2-B3p1, is given by no model); no kept image outside the fit parts the two, every kept job at another fx of 2 or 3 mod 4 faulted or was cut (30 jobs), so H-EVEN is not held out; 4 fx slots a block row (H-4FX) fails 5 of the 5 images where it parts"
unit = "ta"
method = "Offline, no run (round 9, decision S-2 a; seeds plan closing9/seeds/exp-seeds-r9.md finding 4 and section 6). The planner's scripts in closing9/seeds/q139/ (standard library): residue_map.py maps the slots of each residue dump to target tiles; residue_fit.py scores 24 variants (block-row width: R7-BLK's 16 floor(fx / 4), 16 ceil(fx / 4), 4 fx, 8 floor(fx / 2); order: by target position, by macrotile, by macrotile row; the local bits or the target's) on the three readable residue dumps of E944 (render/closing-r8-lgeo out/20261113-024441/q139: the .txt image, the .tri.tadata.bin header slots against the base the two unpoked baselines of the same attempt give, through the session's gen/q139_fit.py and kit lib_dump.py); even_images.py scores R7-BLK, H-EVEN and H-4FX on the wrong-tile sets of every kept whole image of resgx545-data ta/mtile-fields and ta/mtile-fields-risky (E877's datasets, never dumped; the three fit rows marked), and fx_status.py lists every kept job with fx of 2 or 3 mod 4 and whether it kept a whole image. Re-run in this fold with the repository's .venv from resgx545-data's published session (residue_fit.py and residue_map.py given render/closing-r8-lgeo as their argument, the default being the session's old scratch place): residue_fit.out, even_images.out and fx_status.out byte-identical; residue_map.py's output kept as closing9/offline/q139/residue_map.out"
tiers = ["HW"]
date = "2026-11-13"
data = ["render-closing-r8-lgeo:out/20261113-024441/q139/", "ta-mtile-fields", "ta-mtile-fields-risky", "cited-scratch:closing9/seeds/q139/", "cited-scratch:closing9/offline/q139/"]
terms = ["CR_TE_MTILE1", "CR_TE_MTILE2", "CR_TE_MACROTILE_STRIDE"]
+++
**What was done.** E944 held out block order with R7-BLK's slots on 11 strides, and dumped four
residue jobs that no order gives: three whose first macrotile's bounds are not multiples of 4 (256
x 256 m1-B2-10 and m1-B2-11, fx = 10 and 11; 640 x 480 m1-B1-23, fx = 23) and 1280 x 720 m2-B3p1,
whose slots could not be read (no baseline dumped at that size). The round 9 seeds planner read
the slots of the three readable ones, fitted the width of a block row of the first macrotile, and
checked the form on every other kept whole image. This record re-runs those scripts; nothing new
ran on the laptop.

**Results [HW, fitted].** In the three dumps a block row of the first macrotile takes 40 slots at
fx = 10 and at fx = 11, and 88 at fx = 23 (`residue_map.out`): 8 floor(fx / 2), where R7-BLK has
16 floor(fx / 4) (32, 32, 80). With that one change, block order and R7-BLK's other terms give the
wrong-tile set and all header slots of all three (28, 30 and 286 wrong tiles; 128, 128 and 600 of
as many slots); of the 24 declared variants only H-EVEN (with either order key that keeps block
order across the target, and either source of the local bits, which agree here) does so on all
three (`residue_fit.out`). The form was chosen on the two 256 x 256 rows; the 640 x 480 row was
read with it afterwards, in sample. On the 164 kept whole images outside the fit H-EVEN and R7-BLK
give the same 163 wrong-tile sets (`even_images.out`; the miss, 1280 x 720 m2-B3p1, no model
gives); H-4FX, 4 fx slots a block row, fails the 5 images where it parts from them.

**Why it is not held out.** H-EVEN equals R7-BLK when fx is 0 or 1 mod 4; at 2 or 3 mod 4 every
kept job other than the fit faulted or was cut (`fx_status.out`: 30 jobs, E506's risky script),
so no kept image parts the two. A held-out row needs fx = 6, 7, 14 or 15 at 256 x 256 (or B1 = 18,
19 or 22 at 640 x 480), words of the faulting kind (E509): not safe class (round 9 decision R9-7:
not this round).

**What it shows.** [HW, fitted] A block row of the first macrotile spans 8 floor(fx / 2) slots on
the three readable residue dumps, every slot exact, with the rest of R7-BLK and block order
unchanged; [infer] a partial block takes an even number of columns. **What it does not show.** Why
(a held-out fx of 2 or 3 mod 4), the y side of the residue (1280 x 720 m2-B3p1, B3 = 37; the round 9
seeds' stage q139b dumps it against a baseline), the stride's relation to the RT data and E509's
faults (Q139). sgx-pipe keeps refusing poked macrotile words (`ta.rs`, Q139).
