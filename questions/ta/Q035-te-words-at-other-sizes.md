+++
id = "Q035"
question = "does the tiling engine read CR_TE_MTILE1 (0x0208) at all, and does any set of tiling words other than the macrotile rule's also draw a target exactly?"
unit = "ta"
phase = 10
evidence = ["E174", "E175", "E247", "E257"]
terms = ["CR_TE_SCREEN", "CR_TE_MTILE1", "cmd_ta.te_screen", "cmd_ta.te_mtile1"]
+++

The library sizes a render context for its target by its own macrotile rule, and the triangle is
exact at 16 sizes from 64x64 to 4096x4096 (E174). At eight sizes, 96x64 and 1366x768 among them,
the five tiling registers read after the TA exactly what the rule gives, and every image is exact
(E257). 0x0208 is the same at 64x64, 96x64 and 256x256 (as E175 saw) and changes from 512x512
on; its bit 31 is set from 1024x768 on, where the rule chooses four macrotiles across. Each word's
fields are known from the bits that take a write (E247).

What is open: the TA kick loads all the tiling registers from the TA command, so whether the
tiling engine reads 0x0208, and how it uses each field, is not shown: every run so far gave the
rule's words. Only one context-size pair (a 256x256 context drawing 64x64) shows a larger context
serving a smaller target.

To settle it: poke the TA command word that loads 0x0208 (`cmd_ta.te_mtile1`) before a 256x256
and a 1024x768 render, with bit 31 flipped and with each field changed by 4, and compare the
images and the region headers with the rule's; then the same for `cmd_ta.te_mtile2`.
