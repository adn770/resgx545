+++
id = "Q139"
question = "in what order does the TA write a macrotile's region headers (row by row fits 20 of E907's 21 dumped cases and misses stride 4, 4 x 4 tile blocks fit all 21, read after the held-out rows), what is the stride's relation to the RT data, and why do the words that fault (E509) fault"
unit = "ta"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E505", "E506", "E509", "E407", "E877", "E907"]
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
