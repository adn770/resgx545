+++
id = "E465"
claim = "The ZLS store writes the 32 x 16 pixel tile (tx, ty) at dword 512 * (ty * (G + 1) + tx) of the depth buffer, G being CR_ISP_ZLSCTL bits 11:3, with the dword index inside the tile made of the bits y0 x0 y1 x1 y2 x2 y3 x3 x4 from the lowest; in 18 cases on 13 target sizes (one run each) every stored dword is at the rule's address in 16, and in the two overflowed 4096 x 4096 jobs 80640 and 48000 stored dwords are not (the zeros of E468 [infer]), and with a pitch smaller than the tiles of a row the tiles overlap, so the window is (th - 1) * (G + 1) + tw tiles (64512 dwords at 1024 x 768 and 326656 at 4096 x 4096 for the control 0x0017100c, G = 1)"
unit = "zls"
method = "probes/zls/store-layout.toml (store-layout.sh) on the laptop (direct cable), linux fork 6ee9501832af: sgxfive-test tri --tri-full --tri-z (a triangle over the whole target whose depth ramps across x in one job and across y in a second, so that a stored dword names its pixel), --depth with the buffer filled with 0xdeadbeef, --depth-ctl 0x0017100c with bits 11:3 replaced by G, the depth test less, on 18 cases (13 target sizes, pitches G 0 to 511); every dword that left the fill was decoded to its pixel on the laptop (python3) and compared with the rule; each case ran once, after one run by hand of the same 18 cases (outside the data); the datasets hold output.txt, kernel.log, env.toml and the script and no raw dumps, so the address rule was checked by the script at run time and cannot be recomputed from the stored data"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["zls-store-layout"]
terms = ["CR_ISP_ZLSCTL", "CR_ISP_ZSTORE_BASE", "FRAG_FLAGS.DEPTH_BUFFER"]
+++

**What runs.** `tri --tri-full --tri-z A,B,C` (new in this phase) draws the triangle (0,0),
(3W,0), (0,3H) over the whole W x H target with a depth of 0.25 + 0.5 * x / (3W) (A, B, C = 0.25,
0.75, 0.25) or the same in y (0.25, 0.25, 0.75). The depth is stored as a float (E466), so a
stored dword says which pixel it holds: x = (z - 0.25) * 6W and y = (z - 0.25) * 6H, each within
0.05 of a pixel's centre. The buffer is filled with 0xdeadbeef. The rule below was fitted on the
1024 x 768 runs and the small targets of the earlier exploration (runs outside the data, by the
author's statement: 1000 x 600, 640 x 480, 2048 x 1024, 96 x 48, 258 x 130, 2000 x 2000, 1536 x
1010 and 34 x 18 with other pitches, and the 4096 x 4096 case with G = 0, each predicted before it
ran and matched).

**Provenance of the cases.** The script labels 4 lines `fit` (1024 x 768) and 14 `ho` (its header
says "sizes and G not used to find the formula"). "Held out" is only the script's label, written
by the author; the data cannot show it, and the exploration above used 8 of the sizes of the `ho`
lines and the 4096 x 4096 case with G = 0. All 18 cases were first run by hand on the laptop
before the campaign, with the lines identical to the data's (debug/phase11/sl.out, outside the
data), so no case is a validation on data the author had not seen. By the text above, the cases
not seen in the exploration are 640 x 480 with G = 511 and 4096 x 4096 with G = 1, and perhaps 64
x 64, 128 x 64 and 256 x 256 (not stated). The formulas of E466 and the tile orders of E468
changed after the hand run, see there. Each case ran once; no case was repeated, and sizes 640 x
480 and 4096 x 4096 appear twice with different G. The datasets hold output.txt, kernel.log,
env.toml and the script and no raw depth dumps (the dumps were reduced on the laptop and not
kept): the address rule was checked by the script at run time, which prints counts, and cannot be
recomputed from the stored data.

**The rule.** Tile (tx, ty) = (x div 32, y div 16) starts at dword 512 * (ty * (G + 1) + tx) and
the pixel (x mod 32, y mod 16) is at dword 512 * (ty * (G + 1) + tx) + i, where the bits of i from
the lowest are y0, x0, y1, x1, y2, x2, y3, x3, x4. G is bits 11:3 of the ZLS control word
(0x0017100c has G = 1, 0x0017110c G = 33).

**Results.** The script prints, per target, the dwords stored, the slots (tiles of 512 dwords)
touched, the slots the rule predicts, the stored dwords not at the predicted address and whether
the two slot sets are equal:

| target | G | dwords stored | slots (observed = predicted) | dwords not at the rule's address |
|---|---|---|---|---|
| 1024 x 768 (fit) | 0, 1, 2, 33 | 40448, 64512, 88576, 786432 | 79, 126, 173, 1536 | 0 |
| 1000 x 600 | 7 | 167936 | 328 | 0 |
| 640 x 480 | 12 | 203264 | 397 | 0 |
| 258 x 130 | 4 | 25088 | 49 | 0 |
| 96 x 48 | 0 | 2560 | 5 | 0 |
| 2048 x 1024 | 0 | 65024 | 127 | 0 |
| 2000 x 2000 | 9 | 667136 | 1303 | 0 |
| 1536 x 1010 | 12 | 443904 | 867 | 0 |
| 640 x 480 | 511 | 307200 | 600 | 0 |
| 34 x 18 | 3 | 2048 (924 hold the ramp, 1124 the background 1.0) | 4 | 0 |
| 64 x 64, 128 x 64, 256 x 256 | 1 | 4096, 5120, 19456 | 8, 10, 38 | 0 |
| 4096 x 4096 | 1, 0 | 326656, 196096 | 638, 383 | 80640, 48000 (zeros [infer], E468) |

16 of the 18 cases match the rule in every stored dword (the ramp's pixel at the rule's address,
the background 1.0 outside the target as counted). The two at 4096 x 4096 overflowed the parameter
buffer even with `render_pb_pages` 0x2000 (the full-screen triangle has more tiles to list than
the library's default one, E468), and 80640 (G = 1) and 48000 (G = 0) of their stored dwords,
326656 and 196096 in all, are not at the rule's address; the other 246016 and 148096 are. The
script counts the dwords it cannot place and does not classify them: 80640 equals E461's leading
zeros of an overflowed 4096 x 4096 job and E468 shows overflowed jobs storing zeros, so they are
read as zeros [infer], while 48000 has no such number to match. The slot sets are equal to the
rule's in all 18 cases. The window sizes are the rule's (th - 1) * (G + 1) + tw tiles: 47 * 2 + 32
= 126 and 255 * 2 + 128 = 638 tiles (64512 and 326656 dwords) for G = 1 at 1024 x 768 (48 rows of
32 tiles) and 4096 x 4096 (256 rows of 128): the windows of E461; the 638 tiles at 4096 x 4096 are
seen in an overflowed job, the exact store of E461 being the one that held its scene. The tiles of
the first row overlap in the library's setup (a pitch of two tiles for 32 or 128 tiles in a row):
the last tile written to an address keeps it.

The edge tile case (34 x 18): the four tiles are stored whole; 612 of the 2048 dwords are the
target's pixels (34 x 18), 312 are pixels outside the target that the triangle covers (the ramp
continues) and 1124 hold the background depth 1.0 (Q122). The script counts only the 1124
background dwords; 312 is by subtraction (2048 - 1124 = 924 ramp dwords, minus 612).

**What it shows.** The window of E461 is the arithmetic of a store whose tile pitch is two tiles
in a row of 32 or 128: a pitch the library never set (the field G, bits 11:3 of the control). With
G + 1 at least tw (the tiles in a row) the whole depth buffer is stored, one tile after another,
512 dwords a tile for the 32-bit formats. The closed driver's controls (0x0017100c, 0x0017700e)
have G = 1 too, so a closed-driver buffer of a larger target is not addressed by this field alone,
or is also stored as a window [infer]; this is not measured.

**E411 under the rule [infer].** The pitch reading of E411 is an inference; no run of this phase
reproduces a fault (the script's buffers were sized to the window, `pages = max(..., tiles / 2) +
16`, and kernel.log of the three datasets has no fault line). It is derived by hand from E411's
stored pages. E411's 64 x 64 target is 2 x 4 tiles with the stencil at page 4 and the depth at
pages 12 to 15 (four mapped pages of 1024 dwords) in a 16-page scratch buffer. G = 0 (bit 3
cleared) gives a window of 5 slots: the stencil 640 dwords (5 x 128) on page 4 and the depth 2560
dwords, pages 12 and 13 full and page 14 half, which are E411's pages for that flip. G = 3 (bit 4
set) puts the slots at 0, 1, 4, 5, 8, 9, 12 and 13: the stencil 512 dwords on each of pages 4 and
5 and the depth on pages 12 and 14 only, pages 16 and 18 lying past the four mapped pages, which
are E411's pages for that flip. E411's bit 26 row (640 dwords on each of pages 12 and 13, 1280 for
8 tiles, 160 a tile) is the count of format 4 with a stencil (E466: 245760 dwords for 1536 tiles).
Bit 5 set gives G = 5 and bit 6 G = 9, bits 7 to 11 more, tiles at pages further out, which fits
the faults of E411 and is not shown. So bits 3 and 4 of E411 read as the pitch G and its bits 5 to
11 as the pitch running out of the scratch buffer, not as a region [infer].

**What it does not show.** The 16-bit and other formats' pitch (E466 reads the 16-bit one); the
rule for a tile larger than 32 x 16 or for multisampled targets; whether bit 12 or the bits above
the field change the pitch (the control's other bits did not change the layout in E411 or E466);
which order the tiles are written in (it decides which tile keeps an overlapped address, E468).
