+++
id = "Q035"
question = "which tiling words does the macrotile rule set at target sizes other than the sixteen tried, and does register 0x0208 ever change with the size?"
unit = "ta"
phase = 10
evidence = ["E174", "E175"]
terms = ["CR_TE_SCREEN", "cmd_ta.te_screen"]
+++

The library sizes a render context for its target by its own rule, and the triangle is exact at
16 sizes from 64x64 to 4096x4096, two renders each (E174). Between a 64x64 and a 256x256 render
the register file shows four tiling registers change: 0x020c and 0x0214 (the second macrotile
word and the macrotile stride), 0x0210 (`CR_TE_SCREEN`, the last tile column and row) and 0x0248
(the width and height less one). 0x0208, the first macrotile word, stays the same (E175). So
the four registers change with the target; whether the render context's words or the firmware
set them is not shown (E175). 0x0208 is not shown to depend on the size.

What is open: E175 has two sizes, so the rule for the macrotile words is two points. E174 shows
exact images but no register values, and the sizes between 256x256 and 4096x4096 other than
1024x768 were not run: neither 1366x768 (a width that is not a multiple of the 32-pixel tile) nor
2048x2048. Whether a different set of words also draws these sizes is not excluded, and only
one context-size pair (a 256x256 context drawing 64x64) shows a larger context serving a smaller
target.

To settle it: the register snapshot script around renders at 96x64, 512x512, 1366x768, 2048x2048
and 4096x4096, recording 0x0208 to 0x0214 and 0x0248 after each, and comparing every value with
the rule's prediction; check that each image is exact. Then change 0x0208 before one 256x256
render to see whether the TE reads it at all.
