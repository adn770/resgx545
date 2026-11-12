+++
id = "E903"
claim = "r7-rp stage q287 (Q287, 25 depth-dump jobs at H 18, odd widths through t7, the tool built from main 1c64f3a): at odd target widths the ZLS store's band past the target is rule A (x + 0.5 < 1.25 W), not FLOOR (x < floor(1.25 W)): the full-screen triangle stored 22 rows times 9, 14, 29, 44, 54 and 64 columns at W 7, 11, 23, 35, 43 and 51 (two runs each at 7 to 35) and 24, 29 and 44 columns with the y ramp at 19, 23 and 35, rule A's set and one column more than FLOOR's in every held-out cell (9 of 9), the fit cell 19 x 18 stored 528 (24 columns) in both runs, the .25 cells 17 and 21 stored 462 and 572 (A = FLOOR, 2 of 2), the gate row 33 x 18 902 (41 columns), and 34 x 18 reproduced E831's 924 with t4, t6 and t7 (both ramps with t7); ROUND, CEIL and the strict x + 1 < 1.25 W failed every fit and held-out cell; and in the poke twins at W 20 (frozen with no favourite) the band followed the viewport words, not CR_MTE_SCREEN: the screen word poked to 19 x 18 left W 20's 25 columns (550) and the viewport's x scale and offset poked to 9.5 stored W 19's 24 (528), both together 528; frozen verdict 'rule A held on the held-out cells (9 of 9), FLOOR refuted (0 of 9); fit cell 19: A held, FLOOR refuted; .25 confirmations A 2 of 2; controls pass; poke twins (W 20, gate nothing): scr H-VP, vp H-VP, both both (same set)'"
unit = "zls"
method = "r7-rp stage q287 of the question-closing pass, round 7 (decisions R7-2 a, R7-3 a; plan closing7/a/exp-pixel-r7.md sections 1.3 and 3.2), dataset render-closing-r7-rp, on the laptop (host cedar), 2026-11-12, one attempt out/20261112-205431 (started 20:54:31 Mac time, run-r7r.log; 143 jobs in nine stages, s0 first, the session gate, which passed 4 of 4: the default 64 x 64 triangle exact with t4, t6 and t7 and E831's z-ctl-34x18-y storing 924 with t4), kernel 7.3.0-resgx545, module srcversion 41E2F5C756F96D20F7109A4 (fork 3f0b3e74, installed = loaded, knobs at their defaults at every stage start, read only), stock firmware sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a; tools ~/sgxfive-test-rgn4 (t4, sha256 e6951558a93b4b7bc750eeae302997992d7ec6e26719bc527ba1ffc9c6fb779a), round 6's t6 (built from resgx545 d9b2969, sha256 97df5c0ebf5bff2786a59b302e9a8a722bad36f0ef2f5dba11b6f2957f4ad98c) and t7, built by the lead on the build host from resgx545 1c64f3a, which allows odd widths (lead/build_tool7.sh, source pinned in TOOL7SRC.sha256, sha256 f2df4f99add18f011a3607dc3a73ac42cdfab3ec730d1e1f8cd7621761643375 in TOOL7.sha256, the slot run/freeze_r7.sh tool7 filled once, checked on the laptop before every stage); tables, predictions, models, scorers and runner frozen before the first job (FROZEN.sha256 33237f0d..., PREDICTIONS.sha256 c4be8ddd...; FROZEN.commits pins the resgx545 files read at 1c64f3a and data 830641e6); every stage ran to its end with health ok after it, no stop, no lead decision during the run and no reboot. Scored by the frozen score/score_r7.py in the run (out/ATT/score-STAGE.txt); at the fold (2026-11-12) the same scorer re-run on the kept files gave output byte-identical to the kept one for every stage (p7-rd's once its first line, the absolute path of the kept p7-rdc directory, names the run's tree), and the 944 kept files decompress to the raw sha256 the laptop logged (fold/reproduce.sh, fold/reproduce.out). Rows: E831's and E885's depth row (`tri --keep-overflow --tri-full --tri-z 0.25,0.75,0.25` for the x ramp or 0.25,0.25,0.75 for the y ramp, `--depth --depth-ctl 0x17100c --depth-fill 0xdeadbeef --depth-dump --depth-pages 18 --poke blk:1=0x00400200`) at H 18: the dry 33 x 18 first (gate: a refused odd width would have skipped the odd rows and ended the stage with rc 21; it was accepted), the controls 34 x 18 with t4, t6 and t7 (x ramp) and t7 (y ramp), the fit cell W 19 twice, held out W 7, 11, 23 and 35 twice, the y ramp at 19, 23 and 35 and W 43 and 51 once, confirmations W 17 and 21, and the three twins at W 20 (`--poke cmd:9=0x00110012`; `--poke blk:6=0x41180000 --poke blk:7=0x41180000`; both), all with t7 but the t4 and t6 controls; predictions from round 3's band model (r3_geo.py, published with r6-misc) per row, replicates combined (a disagreeing pair would be mixed); the depth store is tile-major at CR_ISP_ZLSCTL's pitch, so the colour buffer's padded pitch at odd widths does not enter the reading. Every job class ok, every dump kept, 0 tile-area dwords left at the pre-fill in any row"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r7-rp:out/20261112-205431/q287/", "render-closing-r7-rp:out/20261112-205431/s0/", "render-closing-r7-rp:fold/", "vectors-closing-r7-rp-zls"]
terms = ["CR_ISP_ZLSCTL"]
+++
**What ran.** E831 held rule A, x + 0.5 < 1.25 W and y + 0.5 < 1.25 H, for the band in which the ZLS
store keeps the tile pass's depth past the target, at even sizes, and E885 at odd heights. Rule A
and FLOOR (x < floor(1.25 W)) differ by one column where 1.25 W has the fraction .75 (W = 3 mod 4),
widths the tool refused. t7, the tool built from main 1c64f3a after "libsgxfive: allow odd target
widths" (the colour row pitch rounded up to even pixels), ran E885's depth row at H 18 and odd
widths: W 19 as the fit cell, 7, 11, 23, 35, 43 and 51 held out (and 19, 23, 35 with the y ramp), 17
and 21 (fraction .25, where both rules agree) as confirmations, 33 as the gate, 34 x 18 (E831's 924)
as the control with three tools. Three twins at W 20, frozen with no favourite, asked which word
carries the band's W: H-SCR (`CR_MTE_SCREEN`'s x field plus 1) or H-VP (2.5 times the viewport's x
half width).

**Frozen verdict (as printed).** `Q287 (odd widths, H 18): rule A held on the held-out cells (9 of
9), FLOOR refuted (0 of 9); fit cell 19: A held, FLOOR refuted; .25 confirmations A 2 of 2; controls
pass; poke twins (W 20, gate nothing): scr H-VP, vp H-VP, both both (same set)`.

**Results [HW].** Stored (not 1.0f) dwords of the tile area at the store's pitch (two tiles a row),
from `out/20261112-205431/score-q287.txt` and the table `vectors/closing/r7-rp/zls-extents/
q287.table.json`; rule A's column count, then FLOOR's:

| cells | W | stored | extent (x, y) | A cols | FLOOR cols | runs |
|---|---|---|---|---|---|---|
| control (t4, t6, t7 x ramp, t7 y ramp) | 34 | 924 | 42, 22 | 42 | 42 | 4 |
| gate | 33 | 902 | 41, 22 | 41 | 41 | 1 |
| confirmation | 17 | 462 | 21, 22 | 21 | 21 | 1 |
| confirmation | 21 | 572 | 26, 22 | 26 | 26 | 1 |
| fit | 19 | 528 | 24, 22 | 24 | 23 | 2 + y ramp |
| held out | 7 | 198 | 9, 22 | 9 | 8 | 2 |
| held out | 11 | 308 | 14, 22 | 14 | 13 | 2 |
| held out | 23 | 638 | 29, 22 | 29 | 28 | 2 + y ramp |
| held out | 35 | 968 | 44, 22 | 44 | 43 | 2 + y ramp |
| held out | 43 | 1188 | 54, 22 | 54 | 53 | 1 |
| held out | 51 | 1408 | 64, 22 | 64 | 63 | 1 |

The twins at W 20, one run each: `cmd:9=0x00110012` (the screen word at 19 x 18) stored 550 (25
columns; H-SCR predicted 24, H-VP 25), `blk:6` and `blk:7` = 9.5 stored 528 (24 columns; H-SCR 25,
H-VP 24), both together 528 (24 under either).

Every stored set is rule A's columns times the 22 rows of H 18; replicates and both ramps agreed in
every cell, no tile-area dword was left at the pre-fill, and the image was right in every job
(`diff: 0 of W x H pixels`). At W 51 rule A's 64 columns fill both tiles of the row, FLOOR's 63
would leave the last column at 1.0. ROUND and CEIL failed the fit, held-out and .25 cells,
the strict x + 1 < 1.25 W the fit and held-out ones.

**What it shows.** At odd widths the band's last column is rule A's: a column is kept when its
centre, x + 0.5, lies below 1.25 W, so at W = 3 mod 4 the store keeps one column more than
floor(1.25 W). With E831 and E885 rule A is the band at every width and height run, even or odd. The
twins put the band's W in the viewport: with `CR_MTE_SCREEN` alone poked to 19 x 18 the store kept
W 20's 25 columns, and with the viewport's x words poked to 9.5 (a 19-pixel viewport) it kept W 19's
24 whatever the screen word [HW, one run each]; [infer] the band is 1.25 times the viewport's
extent, which the tool sets to the target's.

**What it does not show.** One height (18), the float format, no load, the full-screen triangle
only; the twins are one run each and change the x words only (the y side's word is inferred by
symmetry, not run). Read in the session's README before the run, not measured: the tool's minimum
depth buffer (W x H dwords + 16) is below the store's tile extent at small N, so a default
`--depth-pages` could let the store run past the buffer at any width [infer]; every row here passed
N = 18.
