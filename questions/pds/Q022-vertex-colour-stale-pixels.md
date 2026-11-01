+++
id = "Q022"
question = "why do about 30 percent of the pixels keep the previous case's value in the vertex-colour iteration cases, in both runs?"
unit = "pds"
phase = 7
evidence = ["E133"]
terms = ["DOUTI0.ATTR_SOURCE", "DOUTI0.SHADEMODEL", "DOUTU1.WAIT_ITER"]
+++

With state words 13 = 0x83800 and 16 = 5, source 32 gives a vertex colour of the 1062 triangle
pixels (E133). Shade model 0 gives vertex 0's colour on 753 pixels, model 1 vertex 1's on 751 and
model 2 vertex 2's on 723. The rest, about 300 pixels per case, do not hold the case's colour: in
the first three cases they lie in the second row of tiles (rows 16 to 31, columns 16 to 63, a few
elsewhere) and they hold what the previous case gave most of its pixels (0 for case 0; vertex 0's
colour on 299 pixels of model 1, vertex 1's on 310 of model 2). The cases run in order, one job
each.

The follow-up run repeats it with other counts: 736, 757 and 746 pixels take the colour, with 314,
286 and 310 holding the previous case's. So the group is there in both runs, about 300 pixels a
case, and its size varies by a few tens.

Open: whether the pixels keep the previous job's value because their tile did not run (no write at
all, so the buffer keeps the previous case's image), or ran and read stale iteration data; why it is
the second row of tiles; whether it depends on the order of the cases.

To settle it: run each shade-model case first in a fresh context, then in the reverse order, with
the target filled with a sentinel before every job, and read back the pixels that hold the
sentinel. If the sentinel survives, the tile was not written; if the previous colour appears, the
data is stale. Vary the triangle size to see whether the group follows the tile row or the pixel
count.
