+++
id = "Q027"
question = "what does the no-wait iteration deliver to pa0: stale values in the first run, and the pixel's own clip x on 60 to 115 pixels per case in the follow-up run?"
unit = "pds"
phase = 7
evidence = ["E131", "E048"]
terms = ["DOUTI0.ATTR_SOURCE", "DOUTU1.WAIT_FETCH"]
+++

In the triangle host's primary pixel program a `douti` with no wait and no fetch delivers no
source-specific value to `pa0` for any of the 64 sources (E131). In the first run `pa0` holds 16
different values over the 67968 triangle pixels of each probe, the most common 0x3e800000 (19866
pixels), 0 (12483) and 2 (12085), and at no pixel the pixel's x + 0.5 or the clip x. In the
follow-up run it holds 54 different values (50 with the coordinate set), 0 on 41067 pixels, and in
each of the 128 cases 60 to 115 pixels hold the pixel's own clip x (5940 and 6004 pixels in all);
the same for all 64 sources, so it is not a delivery by source.

With the fetch wait and a `doutt`, sources 0 and 1 deliver x + 0.5 and the coordinate set's x at
all 1062 pixels (E131). A wait on the iteration (DOUTU1 bit 24) with its completion bit delivers
the iterated value without a fetch (E048).

Open: whether the shader reads `pa0` before the iteration has written it, so the value is the
register's earlier content or a late write that sometimes wins; why the clip x appears only in the
follow-up run; what the stale values are.

To settle it: run the no-wait case ten times in a fresh context, then ten times after a job that
leaves a known value in `pa0`, with a shader that delays its read by 0, 4, 16 and 64 instructions;
count per pixel whether the clip x, the earlier value or neither arrives, and whether the delay
changes the counts.
