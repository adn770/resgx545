+++
id = "Q283"
question = "is the stride of type 4 textures 32 dwords at every width and are types 1 and 3 read with a stride of the width at widths above 32 and for widths that are not powers of two"
unit = "texture"
kind = "hw"
value = "low"
phase = 11
evidence = ["E725", "E567"]
terms = ["TEXTYPE"]
+++
E725: types 3 and 1 stride w at 8, 16 and 32 wide (8 of 8 held-out jobs); type 4 stride 32 at 8,
16 and 32 wide (fitted on the 4 jobs, plus E567's 16 x 16). To settle it: types 1, 3 and 4 at 64 x
8, 128 x 8, 4 x 16 and a width of 24 and 40 (type 3 is the non-power-of-two one), the 64 x 32 fill
window unchanged; then a prediction frozen before the run, "stride 32" against "stride 2 w capped
at 64" for type 4.

Status: open. Narrows Q178 (types 1, 3, 4 layouts at 8 to 32 wide).
