+++
id = "E570"
claim = "In the triangle's pixel task, with the eight-register tagged shader at 13 target configurations of 7 shapes (64x64 to 256x128; 10 shapes with the 8 configurations of the third table) and PDS_SIZE bits 17:16 at 0 to 3, the destination pixels that carry o1's tag, 6995 pairs read from the x and y runs at the same place in the tile, hold the value written from the tile one position later: in the raster order of the target's 32x16 tiles (tile index ty * ceil(W / 32) + tx) in 6362 of 6995 pairs (91 percent) and in the order of the TA data's region headers (regions with a stream) in 6110 (87 percent); the raster rule fails at 64x128 (300 of 402 pairs) and 256x128 (184 of 362), the header order is the better of the two only at 256x128 (262 of 362) and 192x96 size 0 (54 against 52 of 84); the header order was built on 12 configurations (5551 of 6329 pairs there) and gives 559 of 688 on the 8 it was not built on; o2 and o3 land one, two or three tiles back (o2: 743 one, 318 two, 91 three of 2094; o3: 268, 150, 24 of 532) with no setting tried fixing the offset; the same table twice at 128x128 size 3 gives 705 and 463 pairs of tag 2"
unit = "usse"
method = "script tables o23-tiles (26 jobs), o23-order (26 jobs, with --dump-render) and o23-size (16 jobs, with --dump-render), on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion 5AD04F33F6BCDA7B880E238 (installed equal to loaded at the start of every script, never reloaded), stock firmware (own_arm off), tool sgxfive-test-1126 (sha256 751f7223c8c731a08d75cfc3920a5d1050488ca3bdc426be45b7c431e600f82e, unchanged), no kernel or module change, no reboot, no clock-gate register written: the shader of E406 (o0 to o7 each the pixel's own x or y float, pa0 or pa1, with the low 16 bits the job's marker * 16 + the register number + 1; a distinct program a job), the PDS iteration of pds_iter_xy and the 2-coordinate vertex program, state block word 4 = 0x00000001 | size << 16, every pixel read back; each table in an x job and a y job, from which a destination pixel's source (x, y) is read; read again in a fold of the review with its own code (a pair needs the job's own marker in the tag of both jobs, the region headers are the first written TA data page's)"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["usse-output-room-tiles"]
terms = ["PDS_SIZE.BITS17_16", "REGION_HDR.POS", "REGION_HDR.STREAM"]
+++

**What ran.** 68 jobs, all completed (no job failed or hung). The 8 jobs of usse-output-room-size
(E081, E139, E406: 64x64 only) were first read offline: for each destination pixel the x job gives
the source column and the y job the source row of the write that reached it (the pixel's own place
gives the tag's high half, (px + 0.5 - W/2) / (W/2)), and o1's writes landed in a tile that the
raster index of two tile columns puts one back, o2's two back, at the same place in the tile. That
reading (H23-T) is fitted to those jobs; the 64x64 jobs here (size 3 and 0) are its fit. A pair is
a destination pixel whose tag in the x job and in the y job is the job's own marker * 16 + 2 (o1);
7017 pairs in the 20 configurations that have any (o23-order 6329, o23-size 688), 6995 of them at
the same place in the tile as their source.

**Declared and hashed.** The batch's base declaration (declared.tsv, predictions-declared.tsv and
the o23-tiles table) has a modification time of 03:29:58 on the laptop's clock; o23-tiles ran at
03:20:22, so the files that exist are not shown to precede that run, and the hashes of the tables
were written at 03:36:48 (hashes.txt), after it. The two follow-ups (o23-order, o23-size) were
declared 22 and 4 seconds before their runs (03:23:45 and 03:26:19), the predictions of the first
10 seconds before. H23-T itself was read offline from earlier data (E081) before any run.

**The two rules on the same pairs.** [HW] H23-T, declared before the first run, says the source's
tile has the raster index one above the destination's (tile index ty * ceil(W / 32) + tx, 32x16
tiles). H23-O, declared after the first run and built from its tag 2 data (the 12 o23-order
configurations with pairs, the same ones), says the source's region is the next one with a stream
in the index order of the region headers (REGION_HDR.POS, REGION_HDR.STREAM of the first written
TA data page, laid out in blocks of 4 x 8 tiles). Counted the same way, on the pairs at the same
place (one row a configuration, size is PDS_SIZE; table o23-order or o23-size):

| target | size | table | pairs | raster | header order |
|---|---|---|---|---|---|
| 32x96 | 3 | order | 78 | 78 | 78 |
| 64x64 | 0 | order | 446 | 446 | 446 |
| 64x64 | 3 | order | 481 | 481 | 481 |
| 64x96 | 2 | size | 132 | 122 | 108 |
| 64x96 | 3 | size | 206 | 194 | 178 |
| 64x128 | 3 | order | 402 | 300 | 300 |
| 96x64 | 3 | order | 179 | 170 | 170 |
| 96x96 | 0 | size | 73 | 63 | 63 |
| 96x96 | 1 | size | 63 | 43 | 43 |
| 96x96 | 2 | size | 16 | 13 | 13 |
| 96x96 | 3 | size | 44 | 44 | 44 |
| 128x128 | 0 | order | 1190 | 1162 | 1064 |
| 128x128 | 1 | order | 1054 | 1010 | 958 |
| 128x128 | 2 | order | 545 | 545 | 509 |
| 128x128 | 3 | order | 841 | 745 | 693 |
| 128x128 | 3 (repeat) | order | 709 | 621 | 569 |
| 160x48 | 3 | order | 22 | 22 | 21 |
| 192x96 | 0 | size | 84 | 52 | 54 |
| 192x96 | 3 | size | 68 | 67 | 56 |
| 256x128 | 3 | order | 362 | 184 | 262 |
| all | | | 6995 | 6362 | 6110 |

Either rule holds for 6451 of the 6995 pairs and neither for 544. The raster rule's misses are
the 64x128 target (102 of 402 pairs land two tiles back: in rows 0 to 7 of their tile in this
table, in rows 8 to 15 for 114 of the 211 of the first table, o23-tiles, so the rows are not the
rule), the 256x128 target (178 of 362: 114 from column 4 into column 7 of the row above, 48 from
column 2 into column 3 of the row above, 16 from column 4 into column 5) and a minority at 128x128
and the 96-wide targets, where the destination tile is two back or has no stream; the header order
loses 36 to 124 pairs a 128x128 configuration to destinations that have no stream (449 of the 6329
pairs of o23-order, 72 of the 688 of o23-size). The first table (o23-tiles) gave the raster rule
497 of 497 pairs at 64x64 size 3, 452 of 452 at size 0, 29 of 29 at 160x48, 985 of 985 at 128x128
size 2 and 210 of 421 at 64x128. Declared as "every pixel", both rules are a miss in each
configuration that has a few exceptions (H23-T: right in 6 of the 54 held-out scores of the
declared scoring, a miss in 48): the pair counts above, not that criterion, say how near they
are. The header order is no better than the raster order overall (87 against 91 percent) and is
the better of the two only at the two widest targets, 256x128 and 192x96 size 0.

**Fit and held-out.** [HW] H23-O's 5551 of 6329 pairs (88 percent; 5551 of 6309 at the same place)
are on the 12 configurations it was built from: a fit. On the 8 configurations of o23-size (96x96
at sizes 0 to 3, 192x96 at 0 and 3, 64x96 at 2 and 3; shapes it never saw) it gives 559 of 688
pairs (81 percent) and the raster rule 598 of 686 (the 686 at the same place).

**o2 and o3.** [HW] Tag 3 (o2), o23-order: 2094 pairs (a 2099-pair reading counted 5 whose tag
carries another job's marker, stale values), 743 one region back, 318 two, 91 three, 2 other
(offsets -1 and 0), 692 where the x and y jobs read another place (the two jobs of a pair are
separate runs, and a destination pixel's last writer can differ), 248 in a region with no stream.
Tag 4 (o3): 268, 150, 24 of 532, 90 with no stream. The 128x128 jobs show o2 mostly two back at
sizes 0 to 2 (size 0: 101 two, 64 one, 18 three; size 1: 86 of 103; size 2: 77 of 77) and one back
at size 3 (165 one of 181 in a region with a stream); in o23-size o1's dominant offset is 1 in 8 of
8 configurations, o2's is 2 at sizes 0 to 2 in 3 of the 4 configurations that show it (1 at 192x96
size 0) and at size 3 is 1 at 192x96 and 2 at 64x96, o3's is 1 in 6 of the 7 that show it. With
counts this small the dependence on the size field is not established. o4 (tag 5): at 128x128 size 3
192 pairs, 189 in the source's own tile and 3 in the tile before, none at the same place (78
different displacements, (-1, -5) the commonest, 9 pairs); the E406 four-output setup at 128x128 (2
jobs: o2 14 pairs and o4 172 pairs, all in the source's own tile, none at the same place).

**Not deterministic.** [HW] The same table at 128x128 size 3 twice (o23-tiles and its repeat)
shows 705 and 463 pairs of tag 2 and 324 and 237 of tag 3; in o23-order 847 and 716 pairs of tag 2:
which writes survive to the readback depends on the run, so a count of pixels is not a measure
of the rule. The two jobs of a table have different markers and programs; it is the same table
that is run twice.

**What it suggests.** [infer] The output registers o1 to o3 are written into the output area of a
tile one to three positions earlier in the order the tiles are processed, at the place of the
pixel: a tile-sized output area a register. That order is the raster order of the target's tiles
in 91 percent of the pairs; the region-header order, which is the raster order inside each block
of 4 x 8 tiles, is the better description at two targets only. The size field's part is not shown.
**Not shown.** Why some writes land two tiles back (at 64x128 the rows differ between the two
tables); whether the dependence is on the regions the TA lists or on the ones the 3D runs; o5 to
o7; why the sources of column 4 at 256x128 land in column 7 of the row above.
