+++
id = "Q283"
question = "why does type 3 pad a row to 8 dwords below 8 texels wide (rows max(8, w) apart, E940), what pitch does type 4 keep at sizes that are not multiples of 32 above 32 (32 x 32 blocks row by row held out at multiples of 32, E941), and is type 1 read with a stride of the width at widths that are not powers of two (type 3 is, E940)"
unit = "texture"
kind = "hw"
value = "low"
phase = 11
evidence = ["E725", "E567", "E910", "E940", "E941"]
terms = ["TEXTYPE"]
+++
E725: types 3 and 1 stride w at 8, 16 and 32 wide (8 of 8 held-out jobs); type 4 stride 32 at 8,
16 and 32 wide (fitted on the 4 jobs, plus E567's 16 x 16). To settle it: types 1, 3 and 4 at 64 x
8, 128 x 8, 4 x 16 and a width of 24 and 40 (type 3 is the non-power-of-two one), the 64 x 32 fill
window unchanged; then a prediction frozen before the run, "stride 32" against "stride 2 w capped
at 64" for type 4.

Status: open.

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

Narrowed 2026-11-13 (round 8, R8-lgeo stages tx3 and tx4, E940 and E941; the question line
is reworded, the question is not retired). It read "what layout does type 4 read past 32 texels
wide (32 x 32 blocks of 1024 dwords read post hoc at 64 and 128, E910) and in what order are its
blocks, why does type 3 read rows 8 dwords apart at 4 wide, and are types 1 and 3 read with a
stride of the width at widths that are not powers of two". Answered, held out: type 4 stores 32 x
32 blocks of 1024 dwords numbered row by row (18 of 18 windows of 64 x 64 to 128 x 128 and 256 x
32, E941; columns first 4 of 18, interleaved 9); type 3 reads rows max(8, w) dwords apart (5 of
5 at 1, 2 and 4 wide), type 1 the width (2 of 2 at 1 and 2 wide), and type 3 at 24 and 40 wide
the width, not a power of two above it (2 of 2, through the linear axis, E940). The simulator
models these layouts at the sizes run. Open: why type 3 pads to 8 dwords, type 4 at sizes that
are not multiples of 32 above 32 (a partial block), and type 1 at widths that are not powers of
two (not run).
