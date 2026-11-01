+++
id = "Q103"
question = "why does a scene of 100 to 500 triangles hang where the one-triangle scene overflows the parameter buffer and recovers, at 4096x4096 in 0x40 or 0x23 pages from 300 vertices and in 0x100 pages from 900?"
unit = "dpm"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E438", "E310", "E312"]
terms = ["Dynamic Parameter Management (DPM)", "Parameter Buffer (PB)"]
+++
 E438 ran the triangle and copies of it (3 to 1500 vertices) on a 4096x4096 and a 1024x768 target
in 0x422 to 0x23 pages, three runs of each case. At 4096x4096 the 3-vertex scene in 0x100, 0x40 and
0x23 pages overflows and the job fails with its context kept (-ENOSPC, 9 of 9), as E311 found;
scenes of 300, 900 and 1500 vertices in 0x40 and 0x23 pages hang (18 of 18 jobs), and in 0x100
pages 300 vertices overflow (3 of 3) and 900 and 1500 hang (6 of 6). At 1024x768 in 0x23 pages 3,
300 and 1500 vertices overflow and recover (9 of 9), and 4096x4096 in 0x422 pages overflows at 900
and 1500 and recovers. So the hang depends on the scene's size and the buffer's together, and the
registers read 0 after it. Whether the TA, the DPM's partial render or the final render hangs, and
whether the pages run out before the first partial render can free any, is not read: E186 found
that a hung job's memory does not show how far it got.

To settle it: the render memory of the hung jobs against the overflowing ones (the runs' dumps are
in the dpm-partial-wide data), the free list's head and tail registers through a hung job with a
timeline (regtimeline), and the hang with the TA's page threshold raised (kpoke pb).
