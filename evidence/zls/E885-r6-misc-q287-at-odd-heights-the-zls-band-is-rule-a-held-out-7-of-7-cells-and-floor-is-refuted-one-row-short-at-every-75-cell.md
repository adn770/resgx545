+++
id = "E885"
claim = "R6-misc stage q287 (Q287, 20 depth-dump jobs at W 34, rerun as a second attempt on freeze 2 after freeze 1's runner kept no dump): at odd target heights the ZLS store's band past the target is rule A (y + 0.5 < 1.25 H), not FLOOR (y < floor(1.25 H)): the full-screen triangle stored 42 columns times 9, 14, 29 and 44 rows at H 7, 11, 23 and 35 (y ramp, two runs each) and 24, 29 and 44 rows with the x ramp at 19, 23 and 35, rule A's set and one row more than FLOOR's in every held-out cell (7 of 7), the fit cell 34 x 19 stored 1008 (24 rows) in both runs, the .25 cells 17 and 21 stored 882 and 1092 (A = FLOOR there, 2 of 2) and the controls at 34 x 18 reproduced E831's 924 with the rgn4 tool and with the tool built from main d9b2969 (both ramps); ROUND and CEIL failed every decided cell and y + 1 < 1.25 H the fit and held-out ones; frozen verdict 'rule A held on the held-out cells (7 of 7), FLOOR refuted (0 of 7); fit cell 19: A held, FLOOR refuted; .25 confirmations A 2 of 2; controls pass'"
unit = "zls"
method = "R6-misc stage q287 of the question-closing pass, round 6 (decisions R6-2 a, R6-5 a, R6-6 a; plan closing6/rank/rank-round6.md R6-2), dataset render-closing-r6-misc, on the laptop (host cedar), 2026-11-12, kernel 7.3.0-resgx545, module srcversion 99CD90DA26E3AFF9C450517 (the rgn4 module, installed = loaded, knobs at their defaults at the stage start), stock firmware sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a; tools: ~/sgxfive-test-rgn4 (t4, sha256 e6951558a93b4b7bc750eeae302997992d7ec6e26719bc527ba1ffc9c6fb779a), which refuses odd heights, for one control, and for the other 19 jobs t6 at ~/scratch/r6m/bin/sgxfive-test, built by the lead on the build host from resgx545 d9b2969 (userspace/libsgxfive with a6d78db's 'allow odd target heights', lead/build_tool6.sh, source pinned in TOOL6SRC.sha256) with sha256 97df5c0ebf5bff2786a59b302e9a8a722bad36f0ef2f5dba11b6f2957f4ad98c (TOOL6.sha256, written once by run/freeze_m.sh tool6 and checked on the laptop before every stage with a t6 row); each job E831's g-z command (`tri --tri-full --tri-z 0.25,0.25,0.75` for the y ramp or 0.25,0.75,0.25 for the x ramp, `--depth --depth-ctl 0x17100c --depth-fill 0xdeadbeef --depth-dump --depth-pages 18 --poke blk:1=0x00400200`) at W 34; rows: a dry 34 x 17 first (gate: a refused odd height would end the stage cleanly), the three 34 x 18 controls, the fit cell H 19 twice, held out H 7, 11, 23, 35 twice and the x ramp at 19, 23 and 35, confirmations H 17 and 21; replicates combined (disagreeing runs would be mixed); predictions (r3_geo.py's band rules, a byte copy of round 3's model) frozen before the first job. Attempt 1 (out/20261112-144153, freeze 1: FROZEN.sha256 3199ecac..., PREDICTIONS.sha256 839d74ea...) ran the 20 jobs, all class ok, but its runner made no depth directory, so the tool printed '--depth-dump: No such file or directory' and no dump was written or kept, and the stage was 'cannot tell' with its controls; the lead then saw that stage's and q289's and q086's verdicts, and the session was refrozen (freeze 2: FROZEN.sha256 9a85e828..., PREDICTIONS.sha256 839d74ea..., unchanged; the runner makes the directory and stops with rc 23 when a file a scorer reads is not kept, the scorer's list of required files, the mock's tool needs the directory; no table, prediction or verdict changed; freeze 1 kept in freeze1/) and q287 alone was rerun as attempt out/20261112-152213 (15:22:13 Mac time, run-r6m-q287.log), every job class ok with its dump kept, health ok after the stage, no stop and no lead decision. Scored by freeze 2's score/score_m.py q287 in the run (score-q287.txt); at the fold (2026-11-12) the same scorer re-run on the kept files of both attempts gave output byte-identical to the kept ones, and the 124 kept files of the rerun (104 of attempt 1) decompress to the raw sha256 the laptop logged (fold/reproduce.sh, fold/reproduce.out)"
tiers = ["HW"]
date = "2026-11-12"
data = ["render-closing-r6-misc:out/20261112-152213/q287/", "render-closing-r6-misc:out/20261112-144153/q287/", "render-closing-r6-misc:freeze1/", "render-closing-r6-misc:fold/", "vectors-closing-r6-misc-zls"]
terms = ["CR_ISP_ZLSCTL"]
+++
**What ran.** E831 held rule A, x + 0.5 < 1.25 W and y + 0.5 < 1.25 H, for the band in which the
ZLS store keeps the tile pass's depth past the target, at even sizes, where it equals FLOOR (x <
floor(1.25 W)). They differ by one row where 1.25 H has the fraction .75 (H = 3 mod 4): rule A
keeps ceil(1.25 H - 0.5) rows, FLOOR one fewer. The rgn4 tool refuses odd heights; the lead built
the userspace tool from main d9b2969, which allows them, and stage q287 ran E831's depth-dump job
at W 34 on odd heights: H 19 as the fit cell, 7, 11, 23 and 35 held out (and 19, 23, 35 again with
E831's other ramp), 17 and 21 (fraction .25, where both rules agree) as confirmations, and 34 x 18,
whose 924 stored dwords E831 recorded, as the control with both tools.

**Frozen verdict (as printed, attempt 20261112-152213).** `Q287 (odd heights, W 34): rule A held
on the held-out cells (7 of 7), FLOOR refuted (0 of 7); fit cell 19: A held, FLOOR refuted; .25
confirmations A 2 of 2; controls pass`. Attempt 20261112-144153 printed `Q287: cannot tell:
controls: ...` for every control, its dumps never having been written.

**Results [HW].** Stored (not 1.0f) dwords of the tile area and their extent, from
`out/20261112-152213/score-q287.txt`; rule A's row count, then FLOOR's:

| cells | H | stored | extent (x, y) | A rows | FLOOR rows | runs |
|---|---|---|---|---|---|---|
| control (t4, t6 y ramp, t6 x ramp) | 18 | 924 | 42, 22 | 22 | 22 | 3 |
| gate (dry) and confirmation | 17 | 882 | 42, 21 | 21 | 21 | 2 |
| confirmation | 21 | 1092 | 42, 26 | 26 | 26 | 2 |
| fit | 19 | 1008 | 42, 24 | 24 | 23 | 2 + x ramp |
| held out | 7 | 378 | 42, 9 | 9 | 8 | 2 |
| held out | 11 | 588 | 42, 14 | 14 | 13 | 2 |
| held out | 23 | 1218 | 42, 29 | 29 | 28 | 2 + x ramp |
| held out | 35 | 1848 | 42, 44 | 44 | 43 | 2 + x ramp |

Every stored set is the 42 columns of rule A (and FLOOR) at W 34 times rule A's rows; replicates
and the two ramps agreed in every cell. The tool's image was right in every job (`diff: 0 of W x H
pixels`). ROUND and CEIL failed the fit, held-out and confirmation cells, and the strict x + 1 <
1.25 H (RSTRICT) the fit and held-out ones.

**What it shows.** At odd heights the band's last row is rule A's: a row is kept when its centre,
y + 0.5, lies below 1.25 H, so at H = 3 mod 4 the store keeps one row more than floor(1.25 H). With
E831 that makes rule A the band in y at every height run, even or odd, up to the target's tile area.
The tool built from main reproduced the rgn4 tool's 34 x 18 set exactly.

**What it does not show.** Odd widths: every job here is W 34, and the tool still refuses odd
widths (`userspace/libsgxfive/src/render.c`), so whether x follows rule A at W = 3 mod 4 is not measured (Q287). One
width, the float format, no load, the full-screen triangle only.
