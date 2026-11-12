+++
id = "E876"
claim = "Round 6 offline reading of the two kept sweeps of the fill's end-of-tile DOUTU1 x field (bits 11:3, 512 cases) and y field (bits 21:12, 1024 cases) (Q289; post hoc, nothing held out): every job completed with no dword stored outside the target and only three image hashes occur per sweep; reading the poked field f in half-tile units (16 pixels in x, 8 rows in y), with each 32 x 16 tile t of the 64 x 32 fill stored at (2t | f) >> 1 or (2t + f) >> 1 and nothing stored where that lies outside the target, reproduces the tool's image hash in 1536 of 1536 cases (8 of 8 class checks), XOR in place of OR fails 4 of 8 (4 of 1536 cases); on this 2 x 2-tile fill OR and ADD give the same image for every case, so which of them holds is not shown"
unit = "transfer"
method = "Offline, no run (round 6, decision R6-1 a: the ranking's offline items fold before any session; ranking closing6/rank/rank-round6.md finding 1 and section 1 R6-1). The ranking's scripts closing6/rank/eot_sweep.py (the job result, diff count, first wrong pixel, outside count and hash of each case, grouped) and eot_hash.py (the images of the half-tile reading under M-OR, M-ADD and M-XOR for x and y field values 1 to 4, hashed with libsgxfive's sgxfive_hash_dwords, FNV-1a 64 over the dwords row after row, userspace/libsgxfive/src/poke.c:127, against the hashes eot_sweep.out printed) read the kept raw.txt of pds/end-of-tile/values-doutu1-x and values-doutu1-y (the fill, 64 x 32, colour 0xff336699, each case a poke 'pds:pixev:12^=V' of the pixel-event program's dword 12, the end-of-tile DOUTU1, V a multiple of 8 for x and of 0x1000 for y, and a baseline); q289_predict.py (no input) prints the tile columns and rows each model leaves unwritten at 128 x 64, 256 x 32 and 64 x 128. In the fold (2026-11-12) closing6/fold-misc/q289/eot_all.py scored the three models on every one of the 1536 cases rather than one per class. Each script was re-run from its published copy (resgx545-data cited/closing6/) and printed output byte-identical to the kept .out files. No frozen verdict: the ranking's author read both sweeps before writing the reading, so the fit is post hoc on both; the held-out fill row the ranking freezes (R6-1, about 23 fills at 128 x 64 and 256 x 32) has not run"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["pds-end-of-tile", "cited-scratch:closing6/rank/", "cited-scratch:closing6/fold-misc/q289/"]
terms = ["PIXEL_EVENT.END_OF_TILE", "DOUTU1.BITS11_3", "DOUTU1.BITS21_12"]
+++
**What was done.** Q289 asks which tile the end-of-tile task's U1 x and y fields name when they
differ from the program's own; the transfer model refuses every such scene (E620; `sgx-pipe`
`xfer`, cited to Q206). E044 gave the fill's outcome per value as counts. The round 6 ranking
re-read the two kept sweeps for their image hashes (`closing6/rank/eot_sweep.py`), wrote the
half-tile reading after reading them, and checked it on one value per class (`eot_hash.py`); the
fold scored the same models on every case (`closing6/fold-misc/q289/eot_all.py`). All re-run from
their published copies: byte-identical.

**Results [HW, read post hoc].** From `eot_sweep.out`: 512 x cases and 1024 y cases, every job
`ok`, `outside: 0` in all 1536. Three hashes per sweep:

| field value f (field units) | x sweep (bits 11:3) | y sweep (bits 21:12) |
|---|---|---|
| 0 (baseline), 1 | `0xb60c6095080bd325`, 0 of 2048 pixels wrong | the same hash, 0 wrong |
| 2, 3 | `0x97334f75829dab25`, 1024 wrong, first at (0, 0) | `0x55d29a878f45ab25`, 1024 wrong |
| 4 to 511 (x), 4 to 1023 (y) | `0xfc8ce806207f8325`, 2048 wrong | the same hash, 2048 wrong |

The models (eot_hash.py): the 64 x 32 fill has 2 x 2 tiles of 32 x 16; tile t (per axis) stores
at op(2t, f) >> 1, the field read in half-tile units (16 pixels in x, 8 rows in y), and a tile
whose place lies outside the target stores nothing; unstored pixels keep `0xdeadbeef`.

- *M-OR and M-ADD* reproduce the printed hash in 8 of 8 class checks (f = 1, 2, 3, 4 on each axis,
  `eot_hash.out`) and in 1536 of 1536 cases (`eot_all.out`: 512 of 512 x, 1024 of 1024 y). At
  f = 2 or 3 tile 0 stores at place 1, and tile 1 at place 1 too (OR) or outside (ADD), so place 0,
  the left column (x) or the top row (y) of tiles, keeps the sentinel; from f = 4 every place is
  outside.
- *M-XOR* fails 4 of 8 class checks (f = 2 and 3 on both axes: it exchanges the two tiles and
  writes every pixel) and 4 of 1536 cases.

**What it shows [infer].** On the fill the x and y fields of the end-of-tile U1 name a place in
half-tile units, combined with the tile's own place by OR or by addition, not by XOR, and a place
outside the target stores nothing: the rule Q289 names as its first test ("the loop's tile is stored
at the tile U1 names and nothing is stored when that lies outside the target"), here on both axes
of the fill. Field bit 0 changes nothing because it is half a tile; the flip of the lowest
`tile_x` and `tile_y` bit that changed no pixel of a 64 x 64 render (pds_isa.md, 2026-10-24) is
that bit.

**What it does not show.** Whether OR or ADD holds: on a 2 x 2-tile fill the two give the same
image for every f (`q289_predict.out`: they first differ at four tiles on an axis, e.g. 128 x 64
with x ^ 0x10 leaves columns {0, 2} unwritten under OR and {0} under ADD); the held-out row
the ranking froze for that has not run. The fit is post hoc on both sweeps, so it is a reading
of kept data, not a held-out test. Nothing here tests the copy (E620's pokes), E126's tile
exchanges on the 128 x 128 triangle render, or how the two fields combine with each other (each
sweep moves one field alone).
