+++
id = "E917"
claim = "R7-dpm stage s-v, set A, on the test module 41E2F5C7 (Q210, larger objects; exploration, no verdict frozen: E900 froze no step rule for them): the 2048x2048 calibration of the tool's triangle with 1500 vertices and --vtx-coords 4 repeated R6-dpm's reading 14 of 14 (S2 to S13 0x4f, 0x52, 0x98, 0x9f, 0xe7, 0x12e, 0x133, 0x17d, 0x182, 0x1c7, 0x1cd, 0x214, the need 538, no partial render; its dump's object blocks again 127 dwords, 8 of 8 periods), while the same command with --vtx-coords 8 repeated it 2 of 19: S2 0x4f and no partial render held, but its 17 steps S2 to S18 read 0x4f, 0x50, 0x53, 0x99, 0xa0, 0xe6, 0xe9, 0x130, 0x133, 0x137, 0x17e, 0x183, 0x1c8, 0x1cb, 0x1cf, 0x218, 0x21b against R6-dpm's 0x4f, 0x98, 0x9e, 0xe5, ..., and the need 610 against 691; read after the run, the dump's object blocks run 187, 198, 187, 198, 187 dwords where R6-dpm's ran 187, 187, 198, 198, 198, so at 8 coordinate pairs the scene the TA writes is not the same from one run of the command to the next"
unit = "dpm"
method = "R7-dpm stage s-v (2 jobs: 2048x2048, probe --tri pixel --vertices 1500 --vtx-coords N with --dump-render at P 0x422, N = 4 and 8, the commands R6-dpm's r-v ran as its calibrations, E882) of round 7's laptop session, dataset render-closing-r7-dpm, set A (attempt a1, freeze FROZEN.sha256 against resgx545 main 1c64f3a and data 830641e6), on the laptop (host cedar), 2026-11-12, from 22:26:53 Mac time, health ok after it, no fault, hang or stop; otherwise as E915. Plan decision 5 (a) and PREFLIGHT.md deviation 1: E900 froze no rule for larger objects, so s-v ran two calibrations as exploration (2 jobs, not the plan's 6), each row predicted as R6-dpm's kept reading of the same command (R6-REPEAT, label explore) and the scene premise a second global page and a whole dump. The scorer re-run at the fold on the kept files gave output byte-identical to out/a1/score-s-v.txt. Post hoc (after the run and its scores were read): postrun/misses.py and its output list the head pair offsets on PB page 1 of both dumps, R6-dpm's postrun/ungated.py reading, and the steps read"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r7-dpm:out/a1/s-v/", "render-closing-r7-dpm:postrun/", "render-closing-r6-dpm:out/a2/r-v/", "render-closing-r6-dpm:postrun/"]
terms = ["Dynamic Parameter Management (DPM)", "CR_DPM_GLOBAL_PAGE_STATUS", "CR_DPM_PAGE_STATUS", "CR_DPM_TA_GLOBAL_LIST"]
+++
**What ran.** With 4 and 8 coordinate pairs a vertex the tool's 1500-vertex triangle writes larger
object blocks than the 67 dwords E874's replay is built on, and neither burst rule gave their steps
(E882); E900 read the block sizes of R6-dpm's two calibration dumps (127 dwords at 4 pairs, 79 to
198 at 8) and froze no step rule. Stage s-v ran the two calibrations again, as exploration.

**Results [HW, no verdict frozen].** `out/a1/score-s-v.txt`: "--vtx-coords 4 (exploration, R6-dpm's
readings repeated): 14 held, 0 FAILED, 0 cannot tell of 14 | --vtx-coords 8 (exploration, R6-dpm's
readings repeated): 2 held, 17 FAILED, 0 cannot tell of 19".

| N | steps read (lower ends of the brackets) | need | R6-dpm (E882) |
|---|---|---|---|
| 4 | `0x4f 0x52 0x98 0x9f 0xe7 0x12e 0x133 0x17d 0x182 0x1c7 0x1cd 0x214` | 538 | the same |
| 8 | `0x4f 0x50 0x53 0x99 0xa0 0xe6 0xe9 0x130 0x133 0x137` ... | 610 | `0x4f 0x98` ..., 691 |

At N 8, S12 to S18 read `0x17e`, `0x183`, `0x1c8`, `0x1cb`, `0x1cf`, `0x218`, `0x21b`, 17 steps as
in R6-dpm's run; every step was a one-sample bracket but S11 (`0x137`, `0x138`).

**Read after the run [HW, post hoc].** `postrun/misses.out`: the head pair of PB page 1 recurs at
offsets 0, 127, ..., 1016 in the N 4 dump (8 periods of 127 dwords, as R6-dpm's) and at 0, 187,
385, 572, 770, 957 in the N 8 dump: periods 187, 198, 187, 198, 187, where R6-dpm's N 8 dump read
187, 187, 198, 198, 198 (E882).

**What it shows [infer].** At 4 pairs the scene and its page take repeat exactly across sessions.
At 8 pairs the same command made other object blocks, another step sequence (groups of two and three
steps a few pages apart near the 1500-vertex scene's own steps, as E882 read, but at other page
counts) and a need 81 pages smaller: what the TA receives at 8 pairs differs between runs, so the
N 8 readings of E882 and E900 are of one run each and not of a fixed scene.

**What it does not show.** Why the N 8 object blocks change between runs (the vertex data the tool
submitted was not kept); a step rule for larger objects; the margin at those scenes (no cell ran).
