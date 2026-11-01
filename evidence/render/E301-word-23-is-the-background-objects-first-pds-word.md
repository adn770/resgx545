+++
id = "E301"
claim = "Render command word 23 is the background object's first PDS word, the one the kernel puts in TA command dword 2 (cmd_ta.pds_bgnd): flipping bit 27 there through the kernel poke (one run) gives one of the two images the same flip of word 23 gives; with bits 27, 28, 30 or 31 flipped the job faults after part of the first 32x16 tile is written, whole rows from row 0 or the whole tile, and every other pixel stays at the sentinel; under bits 27 and 28 the number of rows changes from run to run: over these two runs and the two of the earlier sweep, bit 27 kept 5, 5, 4 and 5 rows and bit 28 3, 4, 3 and 3, while bits 30 and 31 kept the whole tile in all four"
unit = "render"
method = "probes/render/bg-pds-word.toml on the laptop, linux fork with the debug option on: its script bg-pds-word.sh runs sgxfive-test tri with every pixel printed (--pixels), unpoked, with cmd:23 bit 27, 28, 30 or 31 flipped (twice each), and with ta:2 bit 27 flipped through the kernel poke; the surviving pixels located with ta_words.py pixels"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["render-bg-pds-word", "render-command-words", "render-command-words-followup"]
terms = ["cmd_ta.pds_bgnd", "hw_render_details.pds_bgnd"]
+++

**What runs.** The render command (struct drm_sgxfive_render_cmd, words 0-25) ends in the
background object's three pixel PDS words, word 23 first; the kernel copies them to TA command
dwords 2-4 (linux fork, sgx_render.c). The flips of Q014, with every pixel printed.

**Results.**

Rows of the first tile like the control, per run (the earlier sweep's two runs, render-command-words
and its follow-up, then this table's two):

| flip | sweep | sweep follow-up | run 1 | run 2 |
|---|---|---|---|---|
| cmd:23 bit 27 | 5 (3936 differ) | 5 (3936) | 4 (3968) | 5 (3936) |
| cmd:23 bit 28 | 3 (4000) | 4 (3968) | 3 (4000) | 3 (4000) |
| cmd:23 bit 30 | the whole tile (3584) | the whole tile | the whole tile | the whole tile |
| cmd:23 bit 31 | the whole tile (3584) | the whole tile | the whole tile | the whole tile |
| ta:2 bit 27 | | | 5 (3936) | |

Every case faults.

Every surviving pixel lies in the target's first 32x16 tile, x 0-31, in whole rows from row 0; under
bits 30 and 31 its 112 triangle pixels are green and its 400 others the background colour. All other
pixels hold the sentinel, 0xdeadbeef. Equal counts give equal hashes: bit 27's first run here (4
rows, 0x39efaba83319a125) is the sweep follow-up's bit 28 image, and bit 28's 3 rows here are the
first sweep's (0xdcf6c0e2040198a5).

**What it shows.** Word 23 reaches the firmware as `cmd_ta.pds_bgnd[0]` [infer: one run of the ta:2
flip, matching one of the two outcomes of word 23's flip, the 5 rows], the background object's first
pixel PDS word (secondary pointer, size, primary pointer in the kernel's order). With its high bits
wrong the 3D renders part or all of the first tile and then faults; the rows done before the fault
are kept [infer: the fault stops the render in tile order]. Why the first tile, or part of it,
survives a bad pointer is not shown, nor what sets the number of rows: it changes from run to run
under one flip, and two flips give the same image.
