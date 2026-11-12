+++
id = "E883"
claim = "R6-dpm stage r-b on the rgn4 module (Q211; 4096x4096, one default triangle moved to four new places, single kick): every frozen headline printed 'cannot tell', gated by r-a0's control without a reading (E881); the four g-qf controls repeated E832's counts 4, 3, 2, 1 at P 0x53, 0x54, 0xa2, 0xa3 and the four calibrations needed HU1's U (262, 243, 220, 179) with no partial render; over the 32 held-out cells, E875's replay in row order (post hoc there) placed 1, 3, 4 and 5 of 8 cells' every run's peak exactly (13 of 32; within 3 pages 4, 8, 8 and 8, as printed beside the gated headlines) and, read ungated after the run, 28 of 32 counts (s262 4 of 8, one partial render too many at thr0 0xb, 0x2b, 0x43 and 0x74; s243, s220, s179 8 of 8 each), so H-REPLAY in row order (count and every run's peak) fails held out; the rivals' counts: the frozen column order 19 of 32, E854's d = 7/4 18 of 32 and d = 1 27 of 32"
unit = "dpm"
method = "R6-dpm stage r-b (40 jobs: the four g-qf controls at 4096x4096; four scenes of one default triangle moved on a 256-pixel grid where row and column order differ most, s262 --move 1:256,1280, s243 1:1536,0, s220 1:1792,256 and s179 1:2048,1024, HU1's U frozen at build by gen/hu1.py; for each a calibration at P 0x422 and 8 cells, thr0 2 to 0x74) of the question-closing pass, round 6, dataset render-closing-r6-dpm, attempt a2 (freeze 2; attempt a1's stop and the refreeze are in E881's method), on the laptop (host cedar), 2026-11-12, from 15:03:42 to 15:19:51 Mac time, health ok after it; the count is the number of 0x0658 bit 0 stretches in the job's timeline, a run's peak the highest 0x0724 count of that TA run, U the calibration's peak, the scene check every job staying at one global page (40 of 40); otherwise as E881. Predictions from E875's frozen f7_replay.py (hash-checked at import): row order the plan's hypothesis (named post hoc in E875, held out here), column order (E875's frozen pick W*) and E854's spacings d = 7/4 and d = 1 a tally. The scorer prints, per scene, a headline over the row-order counts (gated) followed by the peaks tally, a within-3-pages count and the rivals' counts; a peak row holds only when every run's peak is exact. The scorer re-run at the fold on the kept files gave output byte-identical to out/a2/score-r-b.txt. Post hoc (after the run): postrun/ungated.py and its output tally the row-order count rows the gated headlines did not print"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r6-dpm:out/a2/r-b/", "render-closing-r6-dpm:postrun/"]
terms = ["Dynamic Parameter Management (DPM)", "Parameter Buffer (PB)", "CR_DPM_PAGE_STATUS", "CR_DPM_PARTIAL_RENDER"]
+++
**What ran.** E875 replayed the count of partial renders of a one-triangle scene page by page:
HU1's regions walked in an order, one stream each from its macrotile's current page, 32 a page,
every page but the global one freed at a partial render, the one raise. The order its frozen rule
picked (columns) missed 3 of 29 kept counts; row order, named after the counts were read, gave 54
of 56 and every run's peak within 3 pages in 29 of 29. Stage r-b held row order out on four new
scenes, with the four g-qf controls first.

**Results [HW, frozen verdict].** `out/a2/score-r-b.txt`, its verdict lines:
"cannot tell: controls: r-a0 a0-cal-2048f grow: cannot tell" (the g-qf controls), then for s262,
s243, s220 and s179 "cannot tell: controls: r-a0 a0-cal-2048f grow: cannot tell; row peaks exact
1 held, 7 FAILED, 0 cannot tell of 8, within 3 pages 4; rivals: H-REPLAY-COL 6 held, 2 FAILED,
..., d=7/4 4 held, 4 FAILED, ..., d=1 6 held, 2 FAILED", "... exact 3 held, 5 FAILED ..., within
3 pages 8; rivals: H-REPLAY-COL 4 held, d=7/4 4 held, d=1 8 held", "... exact 4 held, 4 FAILED
..., within 3 pages 8; rivals: H-REPLAY-COL 4 held, d=7/4 5 held, d=1 7 held" and "... exact 5
held, 3 FAILED ..., within 3 pages 8; rivals: H-REPLAY-COL 5 held, d=7/4 5 held, d=1 6 held". The
controls' rows held: counts 4, 3, 2, 1, U 262, 243, 220, 179, one global page in every job.

**Read after the run, ungated [HW, post hoc].** `postrun/ungated.out`, the counts:

| scene (U) | row order | column order | d = 7/4 | d = 1 | row-order peaks exact |
|---|---|---|---|---|---|
| s262 | 4 of 8 | 6 of 8 | 4 of 8 | 6 of 8 | 1 of 8 |
| s243 | 8 of 8 | 4 of 8 | 4 of 8 | 8 of 8 | 3 of 8 |
| s220 | 8 of 8 | 4 of 8 | 5 of 8 | 7 of 8 | 4 of 8 |
| s179 | 8 of 8 | 5 of 8 | 5 of 8 | 6 of 8 | 5 of 8 |
| all | 28 of 32 | 19 of 32 | 18 of 32 | 27 of 32 | 13 of 32 |

Row order's four misses, all at s262 (thr0 `0xb`, `0x2b`, `0x43`, `0x74`), predict one partial
render more than ran, the extra run a short one (a peak of 3 pages). Its peak misses elsewhere are
the last run's peak by 1 to 2 pages (s243 `0x19`: `0x34` read, `0x36` predicted) or a run in the
middle by one; 12 of column order's 13 count misses are one render too many.

**What it shows [infer].** Held out, the row-order replay gives the counts of three of the four
scenes and misses the fourth at half its cells, and it gives the exact peaks of 13 of 32 cells:
H-REPLAY as frozen (count and every run's peak) fails, and E875's 54 of 56 do not carry over to
new scenes. Its counts are still closer than column order's or d = 7/4's, and d = 1, a spacing
that failed E832's cells, gives 27 of 32 here. The walk picks the pages up nearly right (28 of 32
peaks within 3 pages) but not what the last run of s262 needs.

**What it does not show.** No frozen verdict: every headline is gated (E881), and the count tallies
are post hoc. Why s262 (the scene moved down, 256, 1280) takes one render less; whether another
walk order or a rule for what a partial render frees fits all six scenes; scenes of many objects
and multi-kick scenes.
