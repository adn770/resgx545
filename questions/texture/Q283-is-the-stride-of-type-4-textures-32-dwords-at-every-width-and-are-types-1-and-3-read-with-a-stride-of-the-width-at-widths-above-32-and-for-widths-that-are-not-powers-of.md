+++
id = "Q283"
question = "what layout does type 4 read past 32 texels wide (32 x 32 blocks of 1024 dwords read post hoc at 64 and 128, E910) and in what order are its blocks, why does type 3 read rows 8 dwords apart at 4 wide, and are types 1 and 3 read with a stride of the width at widths that are not powers of two"
unit = "texture"
kind = "hw"
value = "low"
phase = 11
evidence = ["E725", "E567", "E910"]
terms = ["TEXTYPE"]
+++
E725: types 3 and 1 stride w at 8, 16 and 32 wide (8 of 8 held-out jobs); type 4 stride 32 at 8,
16 and 32 wide (fitted on the 4 jobs, plus E567's 16 x 16). To settle it: types 1, 3 and 4 at 64 x
8, 128 x 8, 4 x 16 and a width of 24 and 40 (type 3 is the non-power-of-two one), the 64 x 32 fill
window unchanged; then a prediction frozen before the run, "stride 32" against "stride 2 w capped
at 64" for type 4.

Status: open. Narrows Q178 (types 1, 3, 4 layouts at 8 to 32 wide).

Narrowed 2026-11-12 (round 7, R7-geo stage tx, E910). Held out: type 1 reads a raster of the
width at 4 x 16, 64 x 8 and 128 x 8 and type 3 at 64 x 8 and 128 x 8 (5 of the 6 rows of the
frozen "raster w"); type 4 at 4 x 16 reads 32 dwords a row. Not predicted: type 3 at 4 x 16 reads
rows 8 dwords apart (a raster of max(8, w) fits, post hoc, one row), and type 4 at 64 x 8, 128 x
8, 64 x 32 and 128 x 32 matches none of the five frozen strides; read after the run, all five are
32 x 32 blocks of 1024 dwords, columns 32 to 63 at +1024. The question keeps those two readings to
be frozen and held out (type 4 at 64 x 64 and wider, so that a second block row and a third block
column are read; type 3 at 2 and 4 wide beside 8), the widths that are not powers of two (24, 40:
the map window takes powers of two only) and the columns past 63 that the 64-pixel window does not
reach (a larger fill or an offset window). The simulator admits type 1 at 4 x 16 and 64 x 8 and
type 3 at 64 x 8 beside E725's sizes; 128 x 8 stays refused (half its columns were not read).
