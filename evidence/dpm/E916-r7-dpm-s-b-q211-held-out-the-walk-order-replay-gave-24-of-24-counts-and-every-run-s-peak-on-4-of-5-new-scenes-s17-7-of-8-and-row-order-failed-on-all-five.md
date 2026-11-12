+++
id = "E916"
claim = "R7-dpm stage s-b, set A, on the test module 41E2F5C7 (Q211; one default triangle moved to five places never run, one kick): held out, E875's page replay with the regions walked in E899's order (H-REPLAY64) gave the count of partial renders at 24 of 24 cells and every TA run's peak at 23 of 24, so its frozen verdict held on s44a and s44b (4096x4096, moves 0,2304 and 2048,1792; 12 of 12 rows each), s42 (4096x2048, 768,256; 8 of 8) and s22 (2048x2048, 0,384; 8 of 8) and read 'not supported' on s17 (1024x768, 64,64; 7 of 8): at b-s17-0x9 the reader's first run peak was 0 where the replay has 0x9, and read after the run the timeline holds no sample of that first TA run (row 1, before the job's threshold was set, then row 2 155 us later inside the partial render with the page count at 9), so that row reads the capture, not the TA (post hoc); the five calibrations needed HU1's U (157, 131, 145, 78, 22) with no partial render and one global page; H-WALK64 placed every block of b-cal-s22's dump at its page and slot (row order 113 of 2306); the rivals' frozen tallies: row order 15 of 48 rows (it fails on all five scenes), E854's d = 7/4 20 of 24 counts and d = 1 22 of 24"
unit = "dpm"
method = "R7-dpm stage s-b (29 jobs: for each of five scenes of the tool's default triangle, tri --move 1:DX,DY chosen by the frozen scene rule where H-REPLAY64 and row order differ most, a calibration at P 0x422 (b-cal-s22's with --dump-render) and 6 cells at 4096x4096 or 4 at the other targets, thr0 2 to 0x9a) of round 7's laptop session, dataset render-closing-r7-dpm, set A (attempt a1, freeze FROZEN.sha256 against resgx545 main 1c64f3a and data 830641e6), on the laptop (host cedar), 2026-11-12, from 22:18:38 Mac time, health ok after it, no fault, hang or stop and no lead decision during the stage; otherwise as E915 (module 41E2F5C7, tool e6951558..., the 16-register timeline). The count is the number of 0x0658 bit 0 stretches in the job's timeline, a run's peak the highest high half of 0x0724 among the samples of that TA run (row 0 left out, as E875's reading), U the calibration's peak, the scene check every job staying at one global page (29 of 29). Predictions from E899's frozen g2_replay64.py and E875's f7_replay.py (hash-checked at import, HU1 from render/closing-r5-dpm/gen/hu1.py): H-REPLAY64 the headline, row order (E875's post hoc walk, failed in E883), E854's d = 7/4 and d = 1 the rivals, tallied; a peak row holds only when every run's peak is exact; s-b's headlines are gated by s-a0's g-qf control (held, E915) and each scene's calibration. The scorer re-run at the fold on the kept files gave output byte-identical to out/a1/score-s-b.txt; the scorer cuts its printed pred and obs at 24 characters, so b-s44a-0x2's sixth run peak (0x1a) shows only in predictions/s-b.tsv. Post hoc (after the run and its scores were read): postrun/misses.py and its output read b-s17-0x9's first timeline rows"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r7-dpm:out/a1/s-b/", "render-closing-r7-dpm:postrun/"]
terms = ["Dynamic Parameter Management (DPM)", "Parameter Buffer (PB)", "CR_DPM_PAGE_STATUS", "CR_DPM_PARTIAL_RENDER", "REGION_HDR.STREAM"]
+++
**What ran.** E899 read the order in which the TA takes the regions' stream blocks from the kept
dumps, strips of 64 pixel rows walked in 64 x 64-pixel blocks (H-WALK64), and E875's page replay
in that order gave the count and every run's peak of all 89 kept one-triangle cells and the 37
record counts, SEMI: the counts had been tallied before the freeze. Row order, E875's post hoc
walk, had failed held out (E883). Stage s-b froze five new scenes, at four targets, where the two
orders part most, and ran a calibration and its cells for each.

**Results [HW, frozen verdict].** `out/a1/score-s-b.txt`, its verdict lines (rows: one count and
one run-peak row a cell):

| scene (target, move, U) | H-REPLAY64 | row order | d = 7/4 | d = 1 |
|---|---|---|---|---|
| s44a (4096x4096, 0,2304, 157) | 12 of 12 rows decided | 4 held, 8 FAILED | 5 of 6 | 5 of 6 |
| s44b (4096x4096, 2048,1792, 131) | 12 of 12 rows decided | 4 held, 8 FAILED | 5 of 6 | 5 of 6 |
| s42 (4096x2048, 768,256, 145) | 8 of 8 rows decided | 1 held, 7 FAILED | 2 of 4 | 4 of 4 |
| s22 (2048x2048, 0,384, 78) | 8 of 8 rows decided | 2 held, 6 FAILED | 4 of 4 | 4 of 4 |
| s17 (1024x768, 64,64, 22) | not supported: 7 held, 1 FAILED | 4 held, 4 FAILED | 4 of 4 | 4 of 4 |

and "H-WALK64 on the dump of b-cal-s22 (every block at its page and slot) (1 of 1 rows decided); row
order 0 held, 1 FAILED" (row order placed 113 of the dump's 2306 blocks). The cells, thr0: count
and run peaks read, each as H-REPLAY64 froze it but the one marked:

| scene | cells |
|---|---|
| s44a | `0x2`: 5 (`0x2`, 4 x `0x22`, `0x1a`); `0x7`: 4; `0x20`: 3; `0x30`: 2; `0x65`, `0x9a`: 1 |
| s44b | `0x3`: 4 (`0x3 0x23 0x23 0x23 0x1b`); `0x17`: 3; `0x1b`: 2; `0x32`, `0x3e`, `0x81`: 1 |
| s42 | `0x5`: 4 (`0x5 0x25 0x25 0x25 0x24`); `0xd`: 3; `0x1c`: 2; `0x45`: 1 |
| s22 | `0x2`: 3 (`0x2 0x22 0x22 0xb`); `0x6`: 2; `0x18`: 1; `0x49`: 1 |
| s17 | `0x2`: 1 (`0x2 0x15`); `0x9`: 1 (`0x0 0xe`, frozen `0x9 0xe`: FAILED); `0xe`: 1; `0x15`: 1 |

Row order's count misses are 9 of 24: one partial render too many at seven cells (s44a `0x7`, s44b
`0x32`, s42 `0x5`, `0xd`, `0x1c`, s22 `0x6`, `0x18`) and one too few at two (s44a `0x20`, s44b
`0x17`); at the other 15 cells its last run's peak is 1 to 4 pages off.

**Read after the run [HW, post hoc].** `postrun/misses.out`: b-s17-0x9's timeline reads row 0 at
1.2 us and row 1 at 360.9 ms, both with `0x0624` = 2 (the job's threshold not yet written) and no
page taken, then row 2 155 us later with `0x0624` = 9, the partial render running and the page
count at 9, falling to 8 and 7 in the next rows. The first TA run fell between two samples, and the
reader's first run is row 1 alone, peak 0. The other three s17 jobs have 3 to 5 rows before their
partial render.

**What it shows [infer].** The count of partial renders of a one-object, one-kick scene is the page
replay in the walk order read from the dumps, with no fitted number: 24 of 24 held-out counts at
four targets, and every run's peak where the first run was sampled; the order read from dumps,
not chosen on counts, held on a dump never opened (s22's 2306 blocks). Row order, d = 7/4 and d = 1
each miss.

**What it does not show.** The first run peak of b-s17-0x9 (not sampled); scenes of many objects
and multi-kick scenes; HU1's U for wide scenes of many vertices and other shapes (E630, Q211);
targets other than these four.
