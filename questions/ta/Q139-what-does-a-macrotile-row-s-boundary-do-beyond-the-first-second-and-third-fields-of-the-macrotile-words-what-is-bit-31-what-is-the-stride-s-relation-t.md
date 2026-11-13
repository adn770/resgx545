+++
id = "Q139"
question = "does a block row of a first macrotile that is not a multiple of 4 wide take 8 floor(fx / 2) slots on held-out hardware rows (E950, fitted on E944's three readable residue dumps, every slot; no safe kept image parts it from R7-BLK, and every kept job at fx 2 or 3 mod 4 faulted), what is the stride's relation to the RT data, and why do the words that fault (E509) fault"
unit = "ta"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E505", "E506", "E509", "E407", "E877", "E907", "E944", "E950", "E959", "E1007"]
terms = ["CR_TE_MTILE1", "CR_TE_MTILE2", "CR_TE_MACROTILE_STRIDE"]
+++

E505, E506, E509 (the safe and the risky script, 329 jobs, 15 of them controls): with two macrotile
columns (256 x 256, 512 x 384) the second boundary B2 alone decides (B1 and B3 over 0 to 20 draw
exactly at 256 x 256, 56 of 56; B2 changed never, 0 of 28), the stride must be the rule's (22 of 22
not exact: below it a wrong image except 0 and 1 at 640 x 480, which fault, above it a fault), and
at four columns (640 x 480, 768 x 640, 1280 x 720) B1, B2 and B3 are all read (B1 other than the
rule's faults or draws wrong, a B3 below the rule's faults, a B2 at or past B3 draws exactly in
CR_TE_MTILE2: 6 of 6). None of the declared PA, PB and PC fits both kinds of size (E509). B2 one
and four more is not exact at all three held-out sizes (12 of 12). Q139 narrows from "what the
fields do" to the points below.

What is open: bit 31 beyond one toggle per size (faults at 256 x 256, wrong at 640 x 480), why a
second boundary at or past the third draws exactly for CR_TE_MTILE2 (6 of 6) and not CR_TE_MTILE1
(none of its 20 B2 values is exact), and the tile maps of the wrong images (67 wrong images are
kept, 8 of the safe and 59 of the risky script: which tiles are missing says which macrotile each
was put in). To settle it: read the digit maps of the wrong images of the two datasets into
per-macrotile maps and test the four-boundary reading against them.

Narrowed 2026-11-12 (round 6, offline, E877). The 67 kept wrong images are wrong in whole 32 x 16
tiles, 67 of 67 [post hoc, data], so the maps are read per region. The test asked for above ran
and failed: the cells that the rule's and the job's boundaries cut hold 5 of the 8 safe and 3 of
the 59 risky wrong images, and a slot reading fitted on the safe dataset (a region's header at its
macrotile's base plus ly times the rule's macrotile width plus lx, dropped when that index reaches
the stride; 61 of 63 safe jobs) and frozen by hash before the risky images were read predicts 39
of the risky dataset's 104 jobs with an image and none of its 59 wrong images (SEMI held out). The
per-macrotile step is done; what places a region under words other than the rule's is not. No
header or stream was dumped in either dataset: a dump of the TA data at the words of the misses
(two macrotile columns, the stride pokes, B2 at or past B3) is the next step.

Narrowed 2026-11-12 (r7-rp q139, E907; the question line is reworded, the question is not
retired). The line read "what does a macrotile row's boundary do beyond the first, second and third
fields of the macrotile words: what is bit 31, what is the stride's relation to the RT data, why is
B2 at or past B3 exact in CR_TE_MTILE2 at 640 x 480, and which rule places a region's header when
the words differ from the rule's (the wrong images lose whole tiles, E877)". The TA data of 21 of
E877's cases was dumped. The frozen H-MOVED (a tile is wrong iff its header left its baseline slot)
is not supported: no wrong tile kept its header in place, but headers also moved for tiles that
drew. Read at the fold on the fit rows, a tile is wrong exactly when no header names it (3296 of
3296 tiles), and the placement rule fitted there (R7-BLK: headers in 4 x 4 tile blocks of 16 slots
per macrotile, counted at the first macrotile's width, the TA writing whole macrotiles past the
target, a later header overwriting an earlier one), hashed and committed before the held-out dumps
were read, predicted their wrong-tile sets and header slots in 9 of 10, with bit 31 clear at 640 x
480 read as n = 2 and B2 past B3 in CR_TE_MTILE2 exact among them; stride 4 failed. Answered: which
rule places a region's header (R7-BLK, 9 of 10 held out), what bit 31 does (the count of
macrotiles per axis and the bounds used), why B2 at or past B3 is exact. Open: the write order
within a macrotile (block order fits all 21 rows only post hoc), the stride's relation to the RT
data, and the faulting words of E509, whose dumps were not taken.

Narrowed 2026-11-13 (round 8, R8-lgeo stage q139, E944; the question line is reworded, the
question is not retired). The write order is answered: with R7-BLK's slots the TA writes the
headers in 4 x 4 tile blocks, block rows across the target, raster inside a block, a later header
overwriting an earlier one; frozen from the round 8 planning's SEMI reading, it gave the wrong-tile
set and every header slot of 11 of 11 held-out strides at 256 x 256 and 640 x 480 (row order 4,
blocks by column 0, macrotile then block 0), and the baselines' headers sit in the same blocks.
sgx-pipe models it for poked strides that drew (`ta::stride_slots`) and writes the library's
headers in those blocks. Open: the four residue jobs, which replicated their datasets' images and
which no order gives (three with bounds that are not multiples of 4; 1280 x 720 had no baseline
dump, so its slots were not read), the stride's relation to the RT data, and the faulting words
of E509 (not run: the session was safe class only).

Narrowed 2026-11-13 (round 9 offline, decision S-2 a, E950; the question line is reworded, the
question is not retired). It read "where does the TA write a region's header when the macrotile
bounds are not multiples of 4 (E944's residue: 256 x 256 m1-B2-10 and m1-B2-11, 640 x 480 m1-B1-23,
which block order and R7-BLK do not give, and 1280 x 720 m2-B3p1), what is the stride's relation to
the RT data, and why do the words that fault (E509) fault". E950 fits the
three readable residue dumps (256 x 256 m1-B2-10 and m1-B2-11, 640 x 480 m1-B1-23) with one change
to R7-BLK: a block row of the first macrotile takes 8 floor(fx / 2) slots, not 16 floor(fx / 4)
(H-EVEN; every slot and the wrong-tile set of all three, in sample). It equals R7-BLK when fx is 0
or 1 mod 4, so no kept image outside the fit parts the two (163 of 164 agree, the miss being 1280 x
720 m2-B3p1), and every kept job at fx of 2 or 3 mod 4 faulted or was cut: a held-out row needs
the faulting words (not safe class; not this round). The round 9 seeds' stage q139b dumps 1280 x
720 m2-B3p1 against a baseline for the y side.

Narrowed 2026-11-13 (round 9, R9-lgeo stage q139b, E959; the question line is reworded, the question
is not retired). It read "where does the TA write a region's header when the macrotile bounds are
not multiples of 4: does a block row of the first macrotile take 8 floor(fx / 2) slots (E950, fitted
on E944's three readable residue dumps, every slot; no safe kept image parts it from R7-BLK) at
other fx, and what does the y side do (1280 x 720 m2-B3p1, which no model gives), what is the
stride's relation to the RT data, and why do the words that fault (E509) fault". Stage q139b dumped
the 1280 x 720 and 768 x 640 baselines and 768 x 640 m2-B3p1: every header at H-EVEN's slot (=
R7-BLK there, fx 12 and 8), held out, and sgx-pipe's `ta::stride_slots` takes the two baselines. The
1280 x 720 residue drew its dataset's 52 wrong tiles with every one of its 1800 headers at H-EVEN's
slot: 12 tiles hold their header and do not draw. Read post hoc at the fold, each kept dump has one
header with flag bit 7 set, on the last target tile in block order, and a tile draws iff its header
lies at or before that slot (every tile of 24 kept dumps; with H-EVEN, 167 of 167 kept whole images
of E877's datasets). Open: H-EVEN held out on hardware (no safe-class job parts it from R7-BLK,
decision R9-7), the bit 7 reading held out, the stride's relation to the RT data, and the faulting
words of E509.

Narrowed 2026-11-13 (round 10, r10-geo stage q139c, E1007; the question line is reworded, the
question is not retired). It read "does a block row of a first macrotile that is not a multiple of 4
wide take 8 floor(fx / 2) slots on held-out hardware rows (E950, fitted on E944's three readable
residue dumps, every slot; no safe kept image parts it from R7-BLK, and every kept job at fx 2 or 3
mod 4 faulted), does header flag bit 7 end the region list the 3D reads (E959, post hoc: it gives
1280 x 720 m2-B3p1's y side), what is the stride's relation to the RT data, and why do the words
that fault (E509) fault". Stage q139c dumped the four y-side `CR_TE_MTILE2` words of
ta/mtile-fields-risky that drew whole and never faulted (two replicates of E907's fy-10 rows, fy 11
and fy 23 with n 4 held out) with the 256 x 256 and 640 x 480 baselines: every header at R7-BLK's
slot and every wrong tile its (2 of 2 held out, 2 of 2 replicates), and in each dump exactly one
header with flag bit 7, at H-EVEN's slot of the last target tile in block order, a tile drawing
iff its header lies at or before it (4 of 4, held out). Answered: bit 7 ends the region list the
3D reads. sgx-pipe's `ta::macrotile_slots` models the measured words with the list end. Open:
H-EVEN held out (fx 2 or 3 mod 4: only faulting words), the stride's relation to the RT data and
the faulting words of E509.
