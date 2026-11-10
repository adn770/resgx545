+++
id = "E776"
claim = "R1-pixgeo stage g-t1 (11 jobs, the tool's 64x64 triangle with the viewport's x offset (block word 6) or y offset (word 8) moved, the triangle spanning offset - 24 to offset + 24): with both controls passing (o-x64 an object, o-x1000 none) the TA wrote and listed an object at x offset 87.5 (min x 63.5) and y offset 87.5, wrote none at x offset 88.0, 88.5, 96 and 104 (min x 64.0 and beyond) and none at x offset -24.0 and -24.5 (max x 0.0 and -0.5), and at y offset 88.0 wrote the object's 23 words and no region listed it; the frozen verdict: held out consistent none, refuted HO-region (E542's tile rule on target regions only, low side closed, high side open) 1 of 9 (the -24.0 cell, predicted present) and HO-band (a band beyond the edge) 3 of 6 (88.0, -24.0, -24.5), the written-unlisted cell undecidable for both"
unit = "ta"
method = "R1-pixgeo stage g-t1 of the question-closing pass, round 2 (decision R2-15; 11 jobs: o-x64 and o-x1000 the controls, o-x87.5, o-x88, o-x88.5, o-x96, o-x104, o-xm24, o-xm24.5, o-y87.5 and o-y88 held out) of the dataset render-closing-r1-pixgeo, on the laptop (host cedar), 2026-11-10 from 09:47 laptop time (08:47 UTC), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded), stock firmware, tool ~/sgxfive-test-r1 (sha256 bf4f8be2d8a8fe50034559450928e05695dc96d396d4892f9b00ea6bc0d4f053); each job probe --tri pixel --width 64 --height 64 --blk 6=WORD (or 8=WORD) --dump-render with p1139-green, WORD the float of the offset (0x42800000 = 64.0, 0x447A0000 = 1000.0, 0x42AF0000 = 87.5, 0x42B00000 = 88.0, 0x42B10000 = 88.5, 0x42C00000 = 96.0, 0x42D00000 = 104.0, 0xC1C00000 = -24.0, 0xC1C40000 = -24.5), a debugfs reset before each job, all 11 of class ok (rc 0); the object decoded by the frozen scorer through pbdump (states present, none and written-unlisted: object words in the PB dump that no region header lists, reported and never counted as a hit); frozen predictions from E736's five cells (the HO-region reading of f0f8720's note on E736, a fit) and the proposal's HO-band; scored by the frozen score/score_r1.py g-t1 (out/score-g-t1.txt), re-run on the kept files with the same SUMMARY; the rule at the end of the record was read after the run"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["render-closing-r1-pixgeo:out/g-t1/"]
terms = ["VIEWPORT.X_OFFSET"]
+++
**What ran.** E736's viewport-offset cells showed the object present at offsets 8 and 64 and absent
at 128, 512 and 1000, and f0f8720's note on E736 read them as E542's tile rule applied to the
target's regions only (low side closed, high side open), with the object's minimum x going out of
reach in (64, 104]. HO-band was the alternative, a band beyond the edge. The stage held out the
cells at the target's edge (87.5, 88.0, 88.5, 96, 104 in x and 87.5, 88.0 in y, -24.0 and -24.5 in x
for the other edge).

**Frozen verdict.** `controls pass; held out: consistent none, refuted ["HO-region (E542's tile rule
on target regions only, low side closed) (1 of 9)", 'HO-band (a band B > 0 beyond the edge) (3 of
6)']; repeat only: consistent none, refuted none`. HO-region's nine rows are the nine held-out
cells: eight decidable (seven held, the -24.0 cell missed) and o-y88, which the scorer cannot score
(written-unlisted); HO-band has six rows with a frozen answer (x offset 87.5 and y 87.5 held; 88.0,
-24.0 and -24.5 missed; o-y88 undecidable) and no answer for 88.5, 96 and 104.

**Results [HW].** Controls: o-x64 an object (3 vertices), o-x1000 none, as E736 and E650. Held out:
x offset 87.5 (x from 63.5 to 111.5): an object, vertices at (63.5, 8), (111.5, 20), (75.5, 56),
1/w 0x3f800000; x offsets 88.0, 88.5, 96 and 104: no object words at all; x offsets -24.0 and
-24.5: none; y offset 87.5 (y from 63.5 to 111.5): an object, at (8, 63.5), (56, 75.5), (20, 111.5);
y offset 88.0 (min y 64.0): the object's 23 words written, the same count as at 87.5, and no region
header listed it, so the decoder found no object to read. At the right edge the object therefore
stops between a minimum x of 63.5 and 64.0 (the target's width), and at the left edge the cell
whose maximum x is 0.0 is not listed, which E542's tile rule with the low side closed predicted
it would be. At the y edge the TA still wrote the object's words at 88.0 though nothing listed
them.

**Read after the run [infer over data; not held out, not frozen].** Every x cell, the y cell at
87.5 and E736's five cells fit one rule: an object is listed when the triangle's extent overlaps the
target with positive width and height, that is min x below 64 and max x above 0 (and the same in
y), the target's edges excluded on both sides. At the x edge nothing is written when no region
lists the triangle; at the y edge (88.0) the words were written and not listed, which a rule on
listing alone does not give [infer: whether the TA's write is conditioned on the x test and the
list on both, or the y cell differs for another reason, was not read]. The rule is a fit to the 11
jobs of the stage and the five cells of E736 and has no held-out cell.

**Not shown.** The y edge's other side (-24.0 and -24.5 in y), the cells between 87.5 and 88.0 (the
ladder was 87.5 and 88.0 only), targets other than 64x64, and whether the guard band of E754 (w
other than 1) moves the limit.
