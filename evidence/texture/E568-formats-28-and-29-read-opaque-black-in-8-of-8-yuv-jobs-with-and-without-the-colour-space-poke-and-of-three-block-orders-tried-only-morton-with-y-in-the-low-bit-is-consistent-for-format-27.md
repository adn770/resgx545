+++
id = "E568"
claim = "YUV formats 28 and 29 on 64x32 type 3 textures read 0xff000000 at all 2048 pixels in all 8 jobs (two patterns, with and without xfer:17^=1 and xfer:18 to 22 poked in the fill's transfer command; the E037 conversion model exact on 0 of 4 csc jobs and on 4 of 4 black ones), so the poke did not reach a loaded colour-space set in a fill (or the set stays unloaded) and the formats cannot be told apart from black here; the names maps of formats 23 to 27 (16x16) read 164, 186, 77, 117 and 28 distinct values; in the block jobs formats 23 and 24 read cells that are constant over 4x4, 8x4 and 4x8 regions under constant data but a data bit changes 7 to 13 pixels (in 0 of 16 blocks does a data bit change exactly one pixel), and format 27 reads its 16 blocks in an order for which, of the three tried, only Morton with y in the low bit is consistent (morton-y0: 16 of 16 blocks; raster 0 of 16, morton-x0 4 of 16; the test fixes the order only up to the permutations that fit the pattern's block map, so other orders are not excluded) with every bit of the low and the high data dword changing exactly one pixel, 16 of 16 blocks each, in the map bit i to (x, y) = (i div 4, i mod 4)"
unit = "texture"
method = "probes/texture/tx-*.toml of phase 11.32 (probes/texture/templates/tx_map.s: one program, 2048 pixels a fill, pa0 = (y << 16) | x, each pixel one smp, the scratch buffer the texture, dword i = 0xD0000000 | i) run by probes/texture/templates/run-all-1132.sh on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion 5AD04F33F6BCDA7B880E238 (installed and loaded alike), tool sgxfive-test-1126 sha256 751f7223...f82e, stock firmware; tools/texture/p1132/declared.tsv sha256 9395f6dd...7b2a and predictions-declared.tsv sha256 4ee35db3...84beb hashed before the first run (the runs began at 02:36:08, the hashes were written at 00:38) and unchanged; no register written, only debugfs reset and /dev/kmsg; raw dumps gzipped under resgx545-data/texture/p1132/<script>/ with the case tables, the stdout of each script in texture/p1132/stdout/ and the kernel logs; recomputed by tools/texture/p1132/recompute/recompute_p1132.py (declared predictions the model no longer renders: 0). Groups formats-names (7), formats-blocks (15) and formats-yuv (8 jobs: csc, nocsc)"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["texture-p1132-tx-formats", "vectors-texture-p1132"]
terms = ["TEXFORMAT"]
+++

**Results.** [HW] D8: the order test compares block i of the B pattern with block (5 i + 3) mod 16
of the A pattern, so any block order whose permutation fits that map passes it: of the
three orders tried only Morton with y in the low bit is consistent, and it is not shown to be the
only one. Formats 23 and 24 read one value for the A pattern (1 distinct value: the blocks do not
differ by index in the colour), which the order test passes in every order, so no order is shown for
them. [infer] That 27 is ETC1 rests on the captures of E342; the bit-to-pixel map here is read for
the data bits that the program writes, not decoded as ETC1.

**Predictions.** The declared YUV prediction (black without the load, the E037 conversion with it)
held for the 4 jobs without the load (4 of 4) and failed for the 4 with it (0 of 4).

**What the simulator adds.** The YUV formats read black in the simulator only where the vector says
that the colour-space set is not loaded (its recorded job pokes do not set xfer:17 bit 0); the
colour-space jobs of this record carry pokes the run did not print, and the E037 landed vectors
carry no job, so they stop.

**Not shown.** The decode of any compressed format (a capture), why the transfer-command poke did
not load the set (a limit of the fill, not a result about the format).
