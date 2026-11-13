+++
id = "E941"
claim = "R8-lgeo stage tx4 (Q283; E725's map-texture fill moved over type 4 textures by window offsets, 20 jobs, no fault): type 4 stores 32 x 32 blocks of 1024 dwords, (y mod 32) 32 + (x mod 32) inside a block, numbered row by row, block (y div 32) ceil(w / 32) + (x div 32) (H-BLKROW, frozen from E910's post hoc reading: 18 of 18 held-out windows of 64 x 64, 128 x 64, 128 x 128 and 256 x 32), where blocks column by column (H-BLKCOL) held 4 and the block coordinates interleaved (H-BLKZ) 9; controls pass (E910's 64 x 32 and 4 x 16 images); frozen verdict 'Q283 type 4 block order: H-BLKROW (32 x 32 blocks row by row) held (18 of 18 rows decided)'"
unit = "texture"
method = "R8-lgeo stage tx4 (its 20 type 4 rows; the three linear rows are E940's) of the question-closing pass, round 8 (decision R8-8; plan closing8/leftovers/exp-leftovers-r8.md section 3, session L2), dataset render-closing-r8-lgeo, on the laptop, 2026-11-13, one attempt out/20261113-024441 (lead log out/run-r8m.log; no stop, no lead decision), kernel 7.3.0-resgx545, module srcversion 37EC97AB0CB37213C42FCCC (fork 664fd0d0), stock firmware, tool ~/sgxfive-test-rgn4 (t4, sha256 e6951558..., resgx545 4623753), built on the session kit (resgx545 91f21da); jobs `probe --temps 32 --coords --pixels` of bins/r8l-ty4-*.bin, the map axis ORing a window offset (x 0, 64, 128, 192; y 0, 32, 64, 96) into the pixel coordinate before the mask (texbuild.py axis_code), so the 64 x 32 window reads any part of the texture; the held-out rows with --scratch-pages 64 (the tool's tag fill covers its whole scratch, 16384 dwords at the default 16 pages, which is exactly 128 x 128, and 65536 at 64 pages, so that no frozen rival read past it: H-BLKZ reads 256 x 32 up to dword 22527; tests/test_gen.py reads the fill in t4's source); the two controls E910's programs and commands byte for byte; the health fill and triangle after every job, every job class ok. Frozen before the first job (FROZEN.sha256 90ab0f4d..., PREDICTIONS.sha256 df01463d..., FROZEN.commits at resgx545 91f21da and resgx545-data 1e83dc86): H-BLKROW against H-BLKCOL and H-BLKZ as the sha256 of the 2048 sampled dwords (gen/texmodel.py); a row whose scratch line named another size than the frozen one would not have been read. Scored by the frozen score/score.py tx4 in the run (score-tx4.txt); at the fold the same scorer re-ran byte-identical on the kept files and every kept file decompresses to the raw sha256 the laptop logged (out/fold/reproduce.sh)"
tiers = ["HW"]
date = "2026-11-13"
data = ["render-closing-r8-lgeo:out/20261113-024441/tx4/"]
terms = ["TEXTYPE"]
+++
**What ran.** E910 read type 4 post hoc as 32 x 32 blocks of 1024 dwords (columns 32 to 63 at
+1024 at 64 and 128 wide), but its 64-pixel window never reached a second block row or a third
block column. Stage tx4 moved the window with an offset over type 4 textures of 64 x 64 (2
windows), 128 x 64 (4), 128 x 128 (8) and 256 x 32 (4), and froze the block numbering: H-BLKROW
(row by row) against H-BLKCOL (column by column) and H-BLKZ (the two block coordinates
interleaved, x in bit 0). H-BLKCOL parts from it on 14 rows, H-BLKZ on 9, all three at 128 x 64.

**Frozen verdict (as printed).** `Q283 type 4 block order: H-BLKROW (32 x 32 blocks row by row)
held (18 of 18 rows decided)`; `H-BLKCOL held is not supported: 4 held, 14 FAILED`; `H-BLKZ held
is not supported: 9 held, 9 FAILED`. Both controls passed.

**Results [HW].** Every pixel of every row holds a texel tag; texel (X, Y) of a w x h type 4
texture is dword ((Y div 32) ceil(w / 32) + (X div 32)) 1024 + (Y mod 32) 32 + (X mod 32) in all
18 windows, the whole of 64 x 64, 128 x 64 and 128 x 128 and of 256 x 32 read.

**What it shows.** [HW] Type 4 is a layout of 32 x 32 blocks of 1024 dwords in raster order inside
a block and row by row across the texture, held out from 64 x 64 to 128 x 128 and at 256 x 32;
with E910's sizes (4 x 16 to 128 x 32, a single block row) it holds at every size run.

**What it does not show.** Sizes that are not multiples of 32 above 32 (a partial block: whether
its rows keep a pitch of 32), heights past 128 and widths past 256, other formats than 32-bit
texels, other filters and address modes than point and repeat.
