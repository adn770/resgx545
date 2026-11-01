+++
id = "Q270"
question = "does the counter that decides whether a VDM_STATE1 job hangs (E700: c cleared by a hang or a reset, a job adds g(v1) + g(v2) with g(v) = v - 2, g(1) = -1, g(0) = 0 [fitted], hang iff c + add > 8) hold for jobs of other shapes, and what else clears it or changes it"
unit = "vdm"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E700", "E701", "E413", "E545"]
terms = ["VDM_STATE1.BITS11_9"]
+++
E700 (52 jobs, 16 of them a seeded random walk) and E701 (28 jobs, a post hoc variant of the counter
for v below 2) describe one job shape: 12 vertices in two objects, 32 temporaries, a 64x64 target,
two blocks with v1 and v2. Nothing says that the threshold 8 and the step v - 2 are properties of
the VDM_STATE1 word and not of that stream: the vertex count, the object sizes, the number of
blocks, the temporaries, the target and the pixel readback were all constant.

Known: after every hang (15 and 8 in the two tables) c was 0 for the next job, but the harness
resets the GPU and runs a health triangle after every hang, so 'a hang clears c' and 'a reset clears
c' are one observation; a debugfs reset that follows a completed job cleared it once (E700, A5's
first job, which would have hung from c = 6), the single job that shows a reset clearing c. Open:
the counter on other shapes (E413's and E545's streams used others, and the fit on E413 was in
sample), the effect of time between jobs (a sleep of seconds and minutes), of a job of another kind
between two (a plain job, a fill, a job of a second context), of a reset that follows no hang (one
observation), what the counter is (a count in the VDM's state, in the TA, in a USE partition), and
the value of v = 1 and 0 in block 1 below c = 4 (E701's B4 and B5 do not separate the variants).

To settle it: a held-out run of the E700 series on three other shapes (24 and 48 vertices, one and
three objects, 8 and 32 temporaries, 64x64 and 128x128) with a random walk each, the counter
predicted per shape from the shape-1 rule before the run; series with plain jobs between the jobs; a
sleep of 0, 10 and 60 seconds at c = 6; a reset at c = 6 after a completed job (the separation E700
had once), repeated; E701's variants at other counts (block-2 v = 1 at c = 1, v = 0 at c = 5, 6, 7),
fixed before the run. The jobs are cheap (a hang costs a reset).
