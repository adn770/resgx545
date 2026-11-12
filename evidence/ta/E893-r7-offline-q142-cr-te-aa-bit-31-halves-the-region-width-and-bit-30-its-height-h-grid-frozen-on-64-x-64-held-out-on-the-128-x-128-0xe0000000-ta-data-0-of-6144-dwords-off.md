+++
id = "E893"
claim = "Round 7 offline decode of E504's dumps (Q142): with CR_TE_AA bit 29 set, bit 31 halves the TA's region width (32 to 16 pixels) and bit 30 its height (16 to 8), a macrotile keeping its pixel area and number; the position fields count 16 pixels in x and 8 in y at every setting, a halved grid's macrotile is written in 4 x 4-region sub-blocks, streams are allocated in the writer's walk over the finer regions and a macrotile with more than 32 streams takes a second page: H-GRID, fitted on the nine 64 x 64 pairs (0 of 6144 TA-data dwords off and streams equal to the opened blocks in 9 of 9) and frozen by hash before the 128 x 128 jobs were opened, predicted te-m2-e0-128x128 from its 0x20000000 twin with 0 of 6144 TA-data dwords off (384 non-zero) and its 128 streams exactly the 128 blocks the parameter dump opens [held out, one job]; the control H-HALF (same regions, position halved) failed there, 353 dwords off. So 0x60000000 and 0xa0000000 change the same number of dwords by different values because they double the region grid along y and along x"
unit = "ta"
method = "Offline, no run (round 7, decisions R7-1 a and R7-7 a; ranking closing7/rank/rank-round7.md finding 3 and R7-1). The ranking had read the 64 x 64 0x20000000, 0x60000000, 0xa0000000 and 0xe0000000 TA data of E504 and the first 6 lines of the 128 x 128 0xe0000000 parameter diff; its closing7/rank/q142_diff.py also wrote a run summary of the 128 x 128 TA-data diff into the last line of its output, which the ranking says it did not read and this fold did not read. The fold wrote closing7/fold-rank/q142/q142_grid.py (H-GRID and the H-HALF control, from the TA data of the 0x20000000 job of the same size: its regions' streams are inherited by their finer regions) and q142_fit.py (the nine 64 x 64 pairs of modes 0 and 2, the r2 repeats and CR_TE_AA 0 included), froze the model, the fit, the scorer q142_score.py, the fit's output and FREEZE.md by sha256 in FROZEN.sha256 (a file, not a commit: 2026-11-12T17:42:11Z) before te-m2-20-128x128 or te-m2-e0-128x128 was opened, then predicted from te-m2-20-128x128 (the predictions hashed into the same file) and scored on te-m2-e0-128x128: every TA-data dword, and the 0x80-byte blocks of the slot in [0x2000, 0x100000) with a non-zero dword against the predicted streams. Gates: the 0x20000000 model gives the 128 x 128 input back (0 dwords off) and H-HALF fails. Standard library only, the repository's .venv; every script re-run from its published copy (cited/closing7/fold-rank/q142/) printed output and wrote predictions byte-identical to the kept files"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["isp-msaa-te-dumps", "cited-scratch:closing7/fold-rank/q142/", "cited-scratch:closing7/rank/"]
terms = ["CR_TE_AA", "REGION_HDR.POS", "REGION_HDR.FLAGS", "REGION_HDR.STREAM"]
+++
**What was done.** Q142 asked what the dwords that `CR_TE_AA` bits 30 and 31 change hold (E504:
76 parameter and 132 TA-data dwords for 0x60000000 and 0xa0000000, 204 and 279 for 0xe0000000 at
64 x 64, 805 and 367 at 128 x 128). The ranking read the 64 x 64 TA data as region headers in a
finer grid (finding 3). The fold wrote that reading as a predictor of the whole TA data from the
0x20000000 job of the same size, fitted it on the 64 x 64 pairs, froze it by hash with its scorer
and a control, and only then opened the 128 x 128 jobs (`closing7/fold-rank/q142/FREEZE.md`).

**H-GRID as frozen** (`q142_grid.py`). With bit 29: bit 31 halves a region's width and bit 30 its
height; a macrotile keeps its pixel area and its number (word 0 bits 15:12), so it holds twice the
regions along a halved axis; word 0's position counts 16 pixels in x (bits 23:16) and 8 in y (bits
11:0) at every setting; a macrotile's headers are written in 4 x 4-region sub-blocks, raster order
across them and inside one (the library's macrotile of 4 x 4 is one); the flags are the writer's
(E652); a finer region has a stream when its 32 x 16 parent has one; streams are allocated per
macrotile in the writer's walk (blocks of 2 regions across and 4 down) over the finer regions,
0x80 bytes apart, each macrotile from a new page and taking as many 0x1000 pages as it fills.

**Fit [HW, seen].** On the nine 64 x 64 pairs (0x60000000 and 0xa0000000 in modes 0 and 2,
0xe0000000 and its repeat, the 0x20000000 repeat and CR_TE_AA 0 in both modes) H-GRID leaves 0 of
6144 TA-data dwords off and its streams are the opened blocks in 9 of 9 (`q142_fit.out`); H-HALF is
off by 121 to 273 dwords in the six pairs with bit 30 or 31.

**Held out [HW].** The 0x20000000 model gave te-m2-20-128x128's TA data back (0 dwords off). The
frozen verdicts (`score.out`): H-GRID held, 0 of 6144 TA-data dwords off (384 non-zero: 256
headers, 128 streams) and its 128 streams are exactly the 128 blocks the parameter dump opens;
H-HALF FAILED, 353 dwords off and 32 streams. Headline: H-GRID held, one held-out job, controls
passed. At 128 x 128 each of the two target macrotiles holds 64 regions of 16 x 8 with a stream:
the first takes 0x2000 to 0x3f80 and the second starts at 0x4000, so a macrotile's streams run
past one page and the next macrotile starts on the next free page [HW]; the flags put 0x10 on the
first macrotile's last header and 0x90 on the second's.

**Read after the scoring [HW, post hoc].** The parameter dumps differ from their 0x20000000 twins
only in the stream blocks at 64 x 64 (no object dword, nothing else); every block holds one of the
five stream forms the 0x20000000 jobs use (`0x46880007`, `0x4688000f` twice, `0x4688000e`,
`0x4690ffff`, each with the object word `0x0c000407`), in new proportions (128 x 128: 79, 7, 5, 25
and 12 blocks). At 128 x 128 five dwords from parameter dword 1083393 on differ as well, outside
the stream blocks.

**What it shows.** [HW, held out on one job] The TA data under `CR_TE_AA` bits 30 and 31 is the
region-header array of a region grid halved along y (bit 30) and x (bit 31); the 132 TA-data
dwords of 0x60000000 and 0xa0000000 are the added and moved headers of the same count of regions,
doubled along different axes, which is why the counts are equal and the values differ. The
parameter-buffer change is the stream blocks of the added regions (which blocks: held out). The
simulator's `ta::region_data` now gives these headers and streams for the library's grid and the
halved ones (tests from E504's dumps); a render with such a word stays refused (Q142).

**What it does not show.** Which stream form a 16 x 8 or 16 x 16 region takes (the tile test of a
region narrower or shorter than two 16 x 16 tiles: post hoc, not modelled), the five dwords outside
the stream blocks at 128 x 128, sizes whose macrotiles hold other than 4 x 4 regions, mode 1, which
samples the ISP stores (E503's window, Q030, Q089), and whether the coarse parent's stream decides
a finer region's when a triangle covers only part of the parent (both jobs draw the full target).
[infer] A finer region that the triangle misses may have no stream; the frozen inheritance was not
tested on such a region.
