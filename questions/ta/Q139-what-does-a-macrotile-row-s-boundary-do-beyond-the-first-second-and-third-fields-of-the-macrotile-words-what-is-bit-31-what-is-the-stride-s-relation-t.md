+++
id = "Q139"
question = "what does a macrotile row's boundary do beyond the first, second and third fields of the macrotile words: what is bit 31, what is the stride's relation to the RT data, why is B2 at or past B3 exact in CR_TE_MTILE2 at 640 x 480, and which rule places a region's header when the words differ from the rule's (the wrong images lose whole tiles, E877)"
unit = "ta"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E505", "E506", "E509", "E407", "E877"]
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
