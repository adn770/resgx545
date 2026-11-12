+++
id = "E884"
claim = "R6-misc stage q289 (Q289, 23 fills, one attempt, no fault): with the fill's end-of-tile DOUTU1 x field (bits 11:3) or y field (bits 21:12) poked by XOR, M-OR (each 32 x 16 tile t stored at (2t | f) >> 1, the field f read in half-tile units, nothing stored past the target) gave the tool's image hash in 20 of 20 held-out rows (128 x 64 x and y pokes, 256 x 32 x pokes), 8 of 8 of the rows where it differs from M-ADD, which failed all 8; every job stored no dword outside the target and the controls passed (E876's 64 x 32 x ^ 0x10 hash 0x97334f75829dab25 and the two baselines 0xf7befd67a3c8e325); frozen verdict 'M-OR held (20 of 20 held-out rows, 8 of 8 separating); M-ADD refuted (12 of 20 held-out rows, 0 of 8 separating); controls pass'; read after the run, E126's 19 flips of the same fields on a 128 x 128 render fit the same place rule with the probe's XOR (19 of 19 pictures, post hoc)"
unit = "transfer"
method = "R6-misc stage q289 of the question-closing pass, round 6 (decisions R6-1 a, R6-2 a, R6-5 a; plan closing6/rank/rank-round6.md R6-1), dataset render-closing-r6-misc, on the laptop (host cedar), 2026-11-12, attempt out/20261112-144153 (stage started 14:41:53 Mac time, the first of three; driver log run-r6m.log), kernel 7.3.0-resgx545, module srcversion 99CD90DA26E3AFF9C450517 (the rgn4 module, installed = loaded, knobs at their defaults at the stage start, checked read-only by the runner), stock firmware sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a, tool ~/sgxfive-test-rgn4 (t4, sha256 e6951558a93b4b7bc750eeae302997992d7ec6e26719bc527ba1ffc9c6fb779a, TOOL.sha256) for every row; files under ~/scratch/r6m/ and one mktemp work directory under ~/scratch/tmp, a debugfs reset before each job; 23 jobs `fill` at 64 x 32 (the control), 128 x 64 and 256 x 32 with `--poke pds:pixev:12^=V` (V a multiple of 8 for x, of 0x1000 for y) or none, every job class ok, health ok after the stage; tables and predictions (M-OR, M-ADD and M-XOR images hashed with libsgxfive's FNV-1a, gen/models.py) frozen before the first job (freeze 1: FROZEN.sha256 3199ecac..., PREDICTIONS.sha256 839d74ea..., kept in freeze1/; FROZEN.commits pins the resgx545 files read at d9b2969); the session was refrozen after this attempt for stage q287 only (freeze 2 changed the runner and the scorer's list of required files, no verdict, tables and predictions identical), and the lead had seen this stage's verdict before the refreeze; no stop and no lead decision during the stage. Scored by the frozen score/score_m.py q289 in the run (score-q289.txt); at the fold (2026-11-12) freeze 2's scorer re-run on the kept files gave output byte-identical to the kept one, and all 119 kept files decompress to the raw sha256 the laptop logged (fold/reproduce.sh, fold/reproduce.out; freeze 1's own scorer is not kept). Post hoc at the fold, not frozen: fold/q289_e126.py compares E126's kept 128 x 128 pictures (pds-pixel-event, the tile-x and tile-y flips) with the place rule"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r6-misc:out/20261112-144153/q289/", "render-closing-r6-misc:fold/", "pds-pixel-event"]
terms = ["PIXEL_EVENT.END_OF_TILE", "DOUTU1.BITS11_3", "DOUTU1.BITS21_12"]
+++
**What ran.** E876 read the kept x and y sweeps of the 64 x 32 fill post hoc: each 32 x 16 tile t
(per axis) stores at op(2t, f) >> 1, the poked field f read in half-tile units (16 pixels in x, 8
rows in y), and a tile whose place lies outside the target stores nothing; OR and ADD fit all 1536
cases and differ only from four tiles on an axis. Stage q289 froze both as M-OR and M-ADD (M-XOR,
refuted by E876, as the scorer's negative control) and ran the fill where they differ: 128 x 64
with the x field poked by 0x8 to 0x40 (8) and the y field by 0x1000 to 0x8000 (8), 256 x 32 with
x pokes 0x10, 0x18, 0x30 and 0x50 (4), a baseline at each size and E876's 64 x 32 x ^ 0x10 case,
whose hash is known, as the control. The verdict is decided on the 8 rows where M-OR and M-ADD
predict different images; a hash on neither, or a dword stored outside the target, refutes both.

**Frozen verdict (as printed).** `Q289: M-OR held (20 of 20 held-out rows, 8 of 8 separating);
M-ADD refuted (12 of 20 held-out rows, 0 of 8 separating); controls pass`.

**Results [HW].** From `out/20261112-144153/score-q289.txt` (diff: pixels unlike the one colour,
of 8192 at 128 x 64 and 256 x 32; outside: dwords stored past the target):

| rows | hash | diff | outside | OR / ADD / XOR |
|---|---|---|---|---|
| control 64 x 32 x ^ 0x10 | `0x97334f75829dab25` (E876's) | 1024 | 0 | y / y / n |
| baselines 128 x 64, 256 x 32; 128 x 64 x ^ 0x8, y ^ 0x1000 | `0xf7befd67a3c8e325` | 0 | 0 | y / y / y |
| 128 x 64 x ^ 0x10, 0x18 | `0xa817f56116104325` | 4096 | 0 | y / n / n |
| 128 x 64 x ^ 0x20, 0x28 | `0xaf016f5dd2704325` | 4096 | 0 | y / y / n |
| 128 x 64 x ^ 0x30, 0x38 | `0xc9cc7aa1d233f325` | 6144 | 0 | y / y / n |
| 128 x 64 x ^ 0x40, y ^ 0x8000 | `0x5ec3ba0b1597a325` | 8192 | 0 | y / y / y |
| 128 x 64 y ^ 0x2000, 0x3000 | `0xf23d6f8934b04325` | 4096 | 0 | y / n / n |
| 128 x 64 y ^ 0x4000, 0x5000 | `0x3e3983590cb04325` | 4096 | 0 | y / y / n |
| 128 x 64 y ^ 0x6000, 0x7000 | `0x18433299fd23f325` | 6144 | 0 | y / y / n |
| 256 x 32 x ^ 0x10, 0x18 | `0xa817f56116104325` | 4096 | 0 | y / n / n |
| 256 x 32 x ^ 0x30 | `0xc9cc7aa1d233f325` | 6144 | 0 | y / n / n |
| 256 x 32 x ^ 0x50 | `0x36dfdb536893f325` | 6144 | 0 | y / n / n |

M-OR matched every row; M-ADD failed the 8 rows that separate them (128 x 64 x and y at f = 2 and
3, all four 256 x 32 rows) and M-XOR 16 of 20. At f = 2 or 3 on 128 x 64 OR leaves the tile
columns (rows) 0 and 2 unwritten and ADD only column (row) 0; the tool's 4096 wrong pixels are
OR's two columns (rows) of the four. All 23 jobs completed.

**Read after the run (post hoc, not frozen; `fold/q289_e126.py`, output in `fold/reproduce.out`).**
E126's probe XORs a mask into the x or y field it builds from the tile position on a 128 x 128
triangle render. With the same place rule (32 x 16 tiles, place = field >> 1, nothing stored past
the target) and the probe's XOR, the 19 kept pictures are predicted pixel for pixel: x bits 3 to
5 and y bits 12 to 15 move 32-pixel columns and 16-row rows by (mask >> 1), 0 of 16384 pixels
differing, and x bits 6 to 11 and y bits 16 to 21 write no pixel, as recorded. The bit 3 and bit
12 pictures stand for the unflipped one (E126), so those two rows check only that the rule leaves
the tiles in place. In the pipeline simulator the rule also gives the recorded image of every
scene of the PDS data-word sweeps whose poke moves a tile (69 fills and copies, pokes of the
U1 word and of the tile masks, E620's data; reported fitted, as the rule was read on E876's
sweeps), with no mismatch.

**What it shows.** The end-of-tile task stores its tile at the place its U1 tile fields name, in
32 x 16 tiles: field >> 1 on each axis, the field's bit 0 being half a tile, and it stores nothing
when that place lies past the target (no dword outside in any job). How the field is formed is the
pixel-event program's own arithmetic: the fill's program ORs its U1 data word into the tile's
field, which is why OR and not addition held, and E126's probe XORs, which is why its tiles
exchanged. [infer] The task stores at the place the U1 names whatever the program computed;
the place rule was read post hoc on the 64 x 32 sweeps (E876) and is held out here only on the
fill.

**What it does not show.** Both fields moved at once: every job here, in E876 and in E126 moved
one field alone, so where a tile with both moved goes is not measured. The copy is covered only by
the post hoc replay of E620's data-word sweeps, not by a held-out row. One run of each case; fills
up to 256 pixels wide and 64 rows high.
