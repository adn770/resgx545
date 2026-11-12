+++
id = "E907"
claim = "r7-rp stage q139 (Q139, 24 TA-dump jobs at E877's missed macrotile cases, 256 x 256 and 640 x 480): every case replicated its dataset's wrong-tile map (21 of 21), and the frozen H-MOVED, a tile is wrong iff its region header is not at the baseline's slot, is not supported on the fit rows (2 held, 8 failed of 10): every wrong tile's header had left its slot (no wrong tile with its header in place, H-INPLACE never) but in 9 fit rows headers also moved for tiles that drew; read at the fold from the fit rows' dumps, a target tile is wrong exactly when no header names it (3296 of 3296 tiles), and a placement rule fitted on them (R7-BLK: headers in 4 x 4 tile blocks of 16 slots per macrotile, N * S + block * 16 + (y mod 4) * 4 + x mod 4 with the blocks counted from the macrotile's first tile at the first macrotile's width over 4, the TA writing tiles past the target to the last bound plus the first macrotile's width, a later header overwriting an earlier one) matched all 11 fit rows tile for tile, was hashed and committed to the data repository (8e6fd91b) and then predicted the held-out rows' wrong-tile sets and header slots in 9 of 10, bit 31 clear at 640 x 480 among them, and failed at stride 4 (68 of 84 wrong tiles in common, 96 of 128 slots); held-out verdict as printed 'Q139 held out: the fitted placement model predicts the held-out wrong-tile sets is not supported: 9 held, 1 FAILED, 0 cannot tell of 10'; read after that, a write order by 4 x 4 tile block fits all 21 rows, stride 4 included [post hoc]"
unit = "ta"
method = "r7-rp stage q139 of the question-closing pass, round 7 (decisions R7-2 a; plan closing7/a/exp-pixel-r7.md section 3.6, user decision 6 a), dataset render-closing-r7-rp, on the laptop (host cedar), 2026-11-12, one attempt out/20261112-205431 (started 20:54:31 Mac time, run-r7r.log; 143 jobs in nine stages, s0 first, the session gate, which passed 4 of 4: the default 64 x 64 triangle exact with t4, t6 and t7 and E831's z-ctl-34x18-y storing 924 with t4), kernel 7.3.0-resgx545, module srcversion 41E2F5C756F96D20F7109A4 (fork 3f0b3e74, installed = loaded, knobs at their defaults at every stage start, read only), stock firmware sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a; tools ~/sgxfive-test-rgn4 (t4, sha256 e6951558a93b4b7bc750eeae302997992d7ec6e26719bc527ba1ffc9c6fb779a), round 6's t6 (built from resgx545 d9b2969, sha256 97df5c0ebf5bff2786a59b302e9a8a722bad36f0ef2f5dba11b6f2957f4ad98c) and t7, built by the lead on the build host from resgx545 1c64f3a, which allows odd widths (lead/build_tool7.sh, source pinned in TOOL7SRC.sha256, sha256 f2df4f99add18f011a3607dc3a73ac42cdfab3ec730d1e1f8cd7621761643375 in TOOL7.sha256, the slot run/freeze_r7.sh tool7 filled once, checked on the laptop before every stage); tables, predictions, models, scorers and runner frozen before the first job (FROZEN.sha256 33237f0d..., PREDICTIONS.sha256 c4be8ddd...; FROZEN.commits pins the resgx545 files read at 1c64f3a and data 830641e6); every stage ran to its end with health ok after it, no stop, no lead decision during the run and no reboot. Scored by the frozen score/score_r7.py in the run (out/ATT/score-STAGE.txt); at the fold (2026-11-12) the same scorer re-run on the kept files gave output byte-identical to the kept one for every stage (p7-rd's once its first line, the absolute path of the kept p7-rdc directory, names the run's tree), and the 944 kept files decompress to the raw sha256 the laptop logged (fold/reproduce.sh, fold/reproduce.out). Rows (t4): the datasets' own commands (ta/mtile-fields and ta/mtile-fields-risky cases.tsv, token for token: `tri --tri-full --pixels --width W --height H --max-width W --max-height H --kpoke-render 1:ta:14x=V`) plus `--keep-going` (without it the tool keeps no dump of a wrong image) and `--dump-render`: controls (the unpoked 256 x 256 and 640 x 480 baselines, the poked exact m1-B1-5), 10 fit rows (m1-B2-8, m1-B2-5, m2-B2-10, stride-8, stride-16, part1-8_8_8 at 256 x 256; m1-B1-20, m1-B2-20, m2-B1-17 and m2-B2-24 at 640 x 480), 10 held-out rows (m1-B2-12, m2-B2-12, stride-4, stride-24, part2-10_10_10 at 256 x 256; m1-B1-28, m1-B2-32, m2-B1-20, m2-B2-28 and m1-flag0, bit 31 clear, at 640 x 480) and the replicate m1-B2-8; replication gating (a case whose wrong-tile set is not its dataset's is dropped), H-MOVED [infer] and its rival H-INPLACE scored on the fit rows only, the region headers read from the TA data dump at the first written page, 12 bytes a slot (score_dump.py, lib_dump.py over byte copies of pbdump.py and region_tiles.py). The held-out rows were not read in the run: the frozen protocol has the fold fit and hash a model first. At the fold (2026-11-12): fold/q139_fitdata.out is `score_dump.py q139-fitdata` (controls and fit rows only); fold/q139_fit.py fitted R7-BLK on it (written after reading the fit rows' slot maps, post hoc as a fit) and wrote fold/q139-model.json (its predictions for the ten held-out rows, wrong tiles and a slot per tile); the four files were hashed in fold/q139_FROZEN.sha256 and committed to resgx545-data (8e6fd91b, 2026-11-12 22:44:50 +0100) before `score_dump.py q139-heldout`, which refuses a model whose sha256 is not the one given, read the held-out dumps (fold/q139_heldout.out). The held-out wrong-tile sets themselves are the datasets' (E509 kept the images, E877 read them) and stood in the session's frozen predictions as the replication gate; the fold's fit read the fit and control lines of that file and not the held-out ones, and no held-out dump had been read by anyone, so the slots are held out and the wrong-tile sets held out from the fit only. fold/q139_order_posthoc.py was written and run after the held-out read. Every job class ok, no fault"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r7-rp:out/20261112-205431/q139/", "render-closing-r7-rp:out/20261112-205431/s0/", "render-closing-r7-rp:fold/", "ta-mtile-fields", "ta-mtile-fields-risky"]
terms = ["CR_TE_MTILE1", "CR_TE_MTILE2", "CR_TE_MACROTILE_STRIDE"]
+++
**What ran.** E877 tested two readings of how the macrotile words place a region's header on the
images of E505, E506 and E509 alone (no header was ever dumped) and both failed. This stage reran 21
of those cases with the TA data dumped: controls, ten fit cases among E877's misses, ten held out
and a replicate. Frozen before the run: replication, and H-MOVED (a tile is wrong iff its header is
not at its baseline slot) against H-INPLACE, on the fit rows; the held-out dumps were to be read
only after the fold had fitted and hashed a placement model.

**Frozen verdict (as printed).** `q139: Q139 H-MOVED: a tile of a poked macrotile word is wrong iff
its region header is not at the slot the baseline of its size has it at (fit rows) is not
supported: 2 held, 8 FAILED, 0 cannot tell of 10; headers moved for tiles that drew in 9 fit rows`;
after the fold's model, `q139 held out: Q139 held out: the fitted placement model predicts the
held-out wrong-tile sets is not supported: 9 held, 1 FAILED, 0 cannot tell of 10; H-MOVED on the
held-out rows: 2 held, 8 FAILED, 0 cannot tell of 10`.

**Results [HW].** Controls: both baselines exact, every target tile with one header with a
stream (128 slots at 256 x 256, 1024 at 640 x 480, base 0x4000); m1-B1-5 exact with every header in
place. Every case replicated its dataset's wrong-tile set (12 to 288 tiles; m2-B2-24 and m2-B2-28
none). Fit rows: wrong 12, 32, 24, 32, 48, 72, 288, 112, 108, 0 tiles; headers moved 16, 96, 40,
96, 112, 120, 472, 120, 108, 0; no wrong tile had its header in place. Held out
(`fold/q139_heldout.out`):

| case | size | wrong | R7-BLK | slots as predicted |
|---|---|---|---|---|
| m1-B2-12 | 256 x 256 | 32 | held | 128 of 128 |
| m2-B2-12 | 256 x 256 | 48 | held | 128 of 128 |
| part2-10_10_10 | 256 x 256 | 24 | held | 128 of 128 |
| stride-24 | 256 x 256 | 24 | held | 128 of 128 |
| stride-4 | 256 x 256 | 84 | FAILED (68 in common) | 96 of 128 |
| m1-B1-28 | 640 x 480 | 288 | held | 600 of 600 |
| m1-B2-32 | 640 x 480 | 112 | held | 600 of 600 |
| m1-flag0 (bit 31 clear) | 640 x 480 | 288 | held | 600 of 600 |
| m2-B1-20 | 640 x 480 | 144 | held | 600 of 600 |
| m2-B2-28 | 640 x 480 | 0 | held | 600 of 600 |

**Read at the fold [HW, post hoc on the fit rows].** In the 11 fit and replicate rows a target tile
is wrong exactly when no header in the dump names it, and drawn when one does wherever it is (3296
of 3296 tiles; `fold/q139_fit.out`). R7-BLK, fitted on their slots: the TA takes each tile's
macrotile from the job's words (the bounds compared in order of use, E877), writes its header at N *
S + ((ly >> 2) * (f >> 2) + (lx >> 2)) * 16 + (y & 3) * 4 + (x & 3), N = mcol * n + mrow, S the
stride word, f the first macrotile's width, lx and ly the tile's offset from its macrotile's first
tile; it writes every tile up to the last bound plus f per axis, past the target too (the dumps hold
such headers, the 640 x 480 baseline's too), row by row, a later header overwriting an earlier one;
a target tile whose header survives is drawn. It matched every fit row tile for tile and was frozen
before the held-out read.

**Read after the held-out read [post hoc].** At stride 4, below one block's 16 slots, the headers
of tile columns 4 to 7 in rows 8, 9, 12 and 13 survived where row by row order has rows 10, 11, 14
and 15 of columns 0 to 3 overwrite them; writing block by block (4 x 4 tiles, blocks across, then
the block's rows) fits all 21 rows, stride 4 included (`fold/q139_order_posthoc.out`).

**What it shows.** A poked macrotile word loses a tile when its region header is overwritten (or
never written in the walk), not because the header moved: the 3D draws each header it finds, at any
slot. Headers sit in 4 x 4 tile blocks of 16 slots, the blocks of a macrotile counted at the first
macrotile's width, and the TA writes the regions of whole macrotiles past the target; with those
three facts the wrong-tile maps of nine held-out cases follow from the words, including bit 31
clear at 640 x 480 (n = 2) and B2 at or past B3 in `CR_TE_MTILE2` drawing exactly. [infer] The order
of writes within a macrotile is the 4 x 4 block's, which row order matches whenever blocks do not
overlap.

**What it does not show.** The block write order is post hoc (one held-out miss, stride 4);
strides below 16 other than 4 and 8; sizes other than 256 x 256 and 640 x 480; why the closed
driver's words are what they are; the faulting cases of E509, whose dumps were not taken.
