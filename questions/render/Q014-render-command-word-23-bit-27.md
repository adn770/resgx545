+++
id = "Q014"
question = "why does a background object whose first PDS word has a high bit wrong render part or all of the first 32x16 tile before the job faults?"
unit = "render"
phase = 6
evidence = ["E029", "E301"]
terms = ["cmd_ta.pds_bgnd"]
+++

What word 23 is and where its surviving pixels lie are answered (E301). Render command word 23 is
the background object's first pixel PDS word, which the kernel puts in TA command dword 2
(`cmd_ta.pds_bgnd[0]`): the same flip there, in its one run, gives one of the two images the flip of
word 23 gives (5 rows) [infer]. With bit 27, 28, 30 or 31 flipped the job faults; the pixels that
agree with the baseline are always in the target's first 32x16 tile, in whole rows from row 0. Under
bits 27 and 28 the number of rows changes from run to run: over the sweep's two runs and E301's two,
bit 27 kept 5, 5, 4 and 5 rows and bit 28 3, 4, 3 and 3, so 4 rows came under either bit, with the
same image; bits 30 and 31 kept the whole tile (512 pixels) in all four. Everything else holds the
sentinel.

What is open: why the first tile, or its first rows, is rendered with a pointer that faults, and
what sets the number of rows, which varies from run to run under one flip; what the low bits (which
fault with no pixel, Q014's sweep) and bits 24-26 (which do not fail) mean in the word.

To settle it: the same flips on targets of 64x32 and 128x128 and with the background object's
other two words flipped, every pixel printed, ten runs each; the BIF fault address after each
(kernel log) to see what the 3D fetched.
