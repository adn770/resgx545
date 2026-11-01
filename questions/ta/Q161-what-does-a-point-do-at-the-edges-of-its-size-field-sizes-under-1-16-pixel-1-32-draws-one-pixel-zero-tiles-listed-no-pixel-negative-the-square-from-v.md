+++
id = "Q161"
question = "what does a point do at the edges of its size field: sizes under 1/16 pixel (1/32 draws one pixel), zero (tiles listed, no pixel), negative (the square from v - S/2 to the far edge of the target), 63, 64 and 100 (three points written as two objects), and does the closed driver's extra output row of its point-size shader hold the size the way our o4 does"
unit = "ta"
kind = "hw"
value = "low"
phase = 11
evidence = ["E544", "E346"]
terms = ["CSTREAM.PRIM_POINTS", "OUTSEL", "ISP0.OBJ_TYPE"]
+++

E544 gives the rule for sizes 0.5 to 256 (the pixels with centre in [v - S/2, v + S/2) in 40 of 42
jobs; the sizes 100, 255 and 256 cover the whole 64 x 64 target, so they show only that the field
reaches at least 95 pixels) and per vertex (4 of 4). Its misses: S = 1/32 draws 1 pixel at each
point (the rule says none) and lists the vertex's tile, S = 0 lists the tile and draws none, S = -4
draws x and y from v + 2 on to the target's edge (2704 pixels). S = 63, 64 and 100 split the three
points into two objects (0x405 with two and 0x804 with one at 63 and 64, 0x404 with one and 0x805
with two at 100; 255 and 256 do not), which a decoder that reads only the first object counts as a
point fewer per tile: with every object read, the footprint rule lists the observed tiles in 41 of
42 jobs, the one miss being S = -4. This question also carries the third clause of the old points
question, whether the closed driver's extra output row holds the size, which E544 does not answer.

Open: the rounding of a size under 1/16 (up, or a floor for a non-zero size), the reading of a
negative or very large size (the field as unsigned sixteenths: 4092 / 16 = 255.75), the size at
which the object splits (between 48 and 63; 100 splits, 255 and 256 do not) and why, and whether the
size reaches the object the same way from the closed driver's point shader (E346's extra output
row).

To settle it: our size program at sizes 49 to 62 in steps of 1, at 0.03125, 0.0625, 0.09375,
-0.0625, -1, -16, 300, 1000 and 4096; the closed driver's point corpus against ours (the capture
tables of 11.11), reading the object's packed block and the region lists. No kernel change.
