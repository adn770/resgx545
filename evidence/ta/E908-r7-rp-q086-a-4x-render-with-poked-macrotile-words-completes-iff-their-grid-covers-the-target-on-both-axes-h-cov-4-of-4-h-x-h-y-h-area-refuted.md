+++
id = "E908"
claim = "r7-rp stage q086 (Q086, 11 4x jobs on contexts made for 4x targets, module 41E2F5C7): a 4x render with poked macrotile words completes exactly when their grid (B3 + B1 tiles per axis) covers the target's 1x tile grid on both axes, not when it covers one axis or as many tiles: U2's words (a 12 x 12 grid) faulted the job on the 3D side at 448 x 160 (14 x 10 tiles: short in x, enough in y and in area), 320 x 224 (10 x 14: short in y), 416 x 192 (13 x 12) and 384 x 208 (12 x 13), 4 of 4 as H-COV predicted, where H-X, H-Y and H-AREA each predicted completion in 2 of the 4; the rule's own words completed every one of those sizes and 1024 x 768 with 0 wrong pixels; the bridges repeated E886 on the new module (U2 at 320 x 160 completed, the closed driver's 64 x 64 words FX faulted); every fault BIF requestor 256, word 0x10000011, followed by a reset and a strict health check that passed (5 faults, the 5 predicted, budget 6); frozen verdict 'Q086: H-COV held (4 of 4 rows), H-X refuted (2 of 4 rows), H-Y refuted (2 of 4 rows), H-AREA refuted (2 of 4 rows), H-ANY refuted (0 of 4 rows); bridges: 320x160-U2 ok, 320x160-FX fault; controls pass 5 of 5; 11 unrun E886 rows not pursued, by design'"
unit = "ta"
method = "r7-rp stage q086 of the question-closing pass, round 7 (decisions R7-2 a, R7-5 a; plan closing7/a/exp-pixel-r7.md sections 1.5 and 3.7, user decision 7 a), dataset render-closing-r7-rp, on the laptop (host cedar), 2026-11-12, one attempt out/20261112-205431 (started 20:54:31 Mac time, run-r7r.log; 143 jobs in nine stages, s0 first, the session gate, which passed 4 of 4: the default 64 x 64 triangle exact with t4, t6 and t7 and E831's z-ctl-34x18-y storing 924 with t4), kernel 7.3.0-resgx545, module srcversion 41E2F5C756F96D20F7109A4 (fork 3f0b3e74, installed = loaded, knobs at their defaults at every stage start, read only), stock firmware sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a; tools ~/sgxfive-test-rgn4 (t4, sha256 e6951558a93b4b7bc750eeae302997992d7ec6e26719bc527ba1ffc9c6fb779a), round 6's t6 (built from resgx545 d9b2969, sha256 97df5c0ebf5bff2786a59b302e9a8a722bad36f0ef2f5dba11b6f2957f4ad98c) and t7, built by the lead on the build host from resgx545 1c64f3a, which allows odd widths (lead/build_tool7.sh, source pinned in TOOL7SRC.sha256, sha256 f2df4f99add18f011a3607dc3a73ac42cdfab3ec730d1e1f8cd7621761643375 in TOOL7.sha256, the slot run/freeze_r7.sh tool7 filled once, checked on the laptop before every stage); tables, predictions, models, scorers and runner frozen before the first job (FROZEN.sha256 33237f0d..., PREDICTIONS.sha256 c4be8ddd...; FROZEN.commits pins the resgx545 files read at 1c64f3a and data 830641e6); every stage ran to its end with health ok after it, no stop, no lead decision during the run and no reboot. Scored by the frozen score/score_r7.py in the run (out/ATT/score-STAGE.txt); at the fold (2026-11-12) the same scorer re-run on the kept files gave output byte-identical to the kept one for every stage (p7-rd's once its first line, the absolute path of the kept p7-rdc directory, names the run's tree), and the 944 kept files decompress to the raw sha256 the laptop logged (fold/reproduce.sh, fold/reproduce.out). Rows (t4), the last stage: E886's shape, `tri --tri-full --keep-going --wait-ms 20000 --pixels --width W --height H --max-width W --max-height H --aa4` with the four 4x pokes (`CR_TE_AA` 0xe0000000, MULTISAMPLECTL 0xeaa26e26) and `--kpoke-render 1:ta:143/144/146` over the kernel's words: the bridges R 1024 x 768, U2 at 320 x 160 and FX at 320 x 160 (expected to fault; had it completed the stage would have stopped with rc 19, E886's faults then depending on the old module), then per size its R control and its U2 row at 448 x 160, 320 x 224, 416 x 192 and 384 x 208, sizes computed so that each row splits H-COV, H-X, H-Y and H-AREA two against two; a poked row counts only if its R completed with 0 wrong and FX faulted on the 3D side; fault budget 6 (every fault of the 3D-side class, BIF_INT_STAT 0x0100 and BIF_FAULT 0x100000xx, then a debugfs reset and strict health; a TA-side fault, a -110 or a failed health would have stopped the stage); E886's 11 rows skipped by its budget were not run by design (every rule predicts they fault, so they separate nothing). The faults were the 5 predicted and health was ok after the stage"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r7-rp:out/20261112-205431/q086/", "render-closing-r7-rp:out/20261112-205431/s0/", "render-closing-r7-rp:fold/"]
terms = ["CR_TE_MTILE1", "CR_TE_MTILE2", "CR_TE_MACROTILE_STRIDE", "CR_TE_AA"]
+++
**What ran.** E886 held H-COV out 9 of 9: a 4x render with poked macrotile words completes
exactly when the grid they describe (the last boundary plus one more macrotile of the first's size,
B3 + B1 tiles per axis) covers the target's 1x tiles. In its nine rows the grid was short on both
axes in every fault and covered both in every completion, so "covers in x", "covers in y" and "has
at least as many tiles" fitted as well. Four new sizes with U2's words (a 12 x 12 grid) split them.

**Frozen verdict (as printed).** `Q086: H-COV held (4 of 4 rows), H-X refuted (2 of 4 rows), H-Y
refuted (2 of 4 rows), H-AREA refuted (2 of 4 rows), H-ANY refuted (0 of 4 rows); bridges:
320x160-U2 ok, 320x160-FX fault; controls pass 5 of 5; 11 unrun E886 rows not pursued, by design`.

**Results [HW].** From `out/20261112-205431/score-q086.txt` (grid covered of the target's tiles;
predictions H-COV, H-X, H-Y, H-AREA):

| row | size | grid of tiles | predicted | observed |
|---|---|---|---|---|
| R | 1024 x 768 | 32, 48 of 32, 48 | ok | ok, 0 wrong |
| U2 bridge | 320 x 160 | 12, 12 of 10, 10 | ok | ok |
| FX bridge | 320 x 160 | 4, 4 of 10, 10 | fault | fault |
| R, U2 | 448 x 160 | 12, 12 of 14, 10 | fault, fault, ok, ok | ok; fault |
| R, U2 | 320 x 224 | 12, 12 of 10, 14 | fault, ok, fault, ok | ok; fault |
| R, U2 | 416 x 192 | 12, 12 of 13, 12 | fault, fault, ok, fault | ok; fault |
| R, U2 | 384 x 208 | 12, 12 of 12, 13 | fault, ok, fault, fault | ok; fault |

Every R control completed with 0 wrong pixels; every fault was BIF requestor 256 with
`BIF_FAULT` 0x10000011 (the 3D side), followed by a reset and a strict health check that passed.

**What it shows.** The poked grid must cover the target on both axes: one tile short in x (448 x
160, 416 x 192) or in y (320 x 224, 384 x 208) faults the job even where the grid has more tiles
than the target. With E886 that makes H-COV the validity rule of poked words for our stack's 4x
contexts, 13 of 13 held out over two modules; the FX bridge shows E886's faults did not depend on
its module's tail room.

**What it does not show.** The closed driver's choice of words over sizes (the capture batch, never
run); the RT data's size words for a 4x target; E886's 11 skipped rows (not pursued: every rule
predicts they fault); one poked word set (U2) at the new sizes.