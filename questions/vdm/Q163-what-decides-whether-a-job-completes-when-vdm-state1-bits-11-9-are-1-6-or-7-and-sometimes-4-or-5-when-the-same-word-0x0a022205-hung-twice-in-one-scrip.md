+++
id = "Q163"
question = "what is the state the jobs leave that decides whether a job with VDM_STATE1 bits 11:9 other than 2 hangs (E700: a counter c, cleared by a hang or a reset; a job adds g(v1) + g(v2) with g(v) = v - 2, g(1) = -1 and g(0) = 0 [fitted]; it hangs iff c + add > 8; held out for v 3 to 7 by E1021; E1035: it survives 60 s idle, a fill job and the health fill and triangle, a reset that follows no hang clears it, and it holds for a 128 x 128 one-block job), what makes the job right before a block-2 v = 1 job decide it (E1113: it completes iff that job, no reset between, completed with a block at v 1 or 6, held out 3 of 3, and hangs after v 5 and v 3 jobs at c = 3 and 1), and what does v = 0 in block 1 below c = 4 do, given that the rule held on streams of 24 and 48 vertices, one and two objects and 8 and 16 temporaries (E1076)"
unit = "vdm"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E545", "E413", "E700", "E701", "E060", "E185", "E299", "E1021", "E1035", "E1076", "E1113"]
terms = ["VDM_STATE1.BITS11_9", "VDM_STATE1.BITS15_13"]
+++
In a two-object stream (E545, 133 jobs) the state word's bits 11:9 = 1 hung in block 2 (2 of 2) and
completed in block 1; the grid's 1 hung at rows 1, 2, 3, 8 and completed at 4, 5, 6, 7 (in a later
script); = 6 completed in the xor jobs (4 of 4) and hung in the grid at rows 1, 2, 3, 8, completed
at 4, 7, 9, 255 and 5 (2 of 3), hung at 6, 16; = 7 alternated in the grid (complete, hang, complete,
hang) and once in each block of the xor jobs; = 4 and 5 hung once in four. E413 found that every
second job of = 7 hangs, exactly when the previous completed. The words are equal where the outcomes
differ, so the word is not the whole input; what else is: the previous job's state (a reset or a
hang before), the position in the script, the pages the stream and the heap occupy, or the state of
the TA between jobs.

Open: the variable (not the word) that the completion depends on, and whether a job that completes
leaves a state (for = 7 alone: folded in below).

To settle it: the same word in jobs run after a completed job, after a hang, after a reset, after a
different word, after a sleep of 0 and of 10 seconds, and in a random order, counting hangs per
class; the alternation test of E413 repeated for = 1, 4, 5, 6. No kernel change.

Narrowed in 11.39 (E700, E701; the question is reworded and Q102 is folded in). E413's 130 jobs
fitted a counter; E700 tested it before the run on 52 jobs of one shape and found 52 of 52 right (15
hangs), among them 16 of 16 (7 hangs) on a seeded random walk of v from 2 to 7 in both blocks, the
only held-out set; the nulls are 37 of 52 (never hang) and 39 of 52 (best stateless threshold), and
on the walk a rule with the memory of one job (fitted on it) gets 15 of 16 against 16 of 16 for the
counter. E701's 28 jobs with v below 2 fix g(1) = -1 in block 2 at c = 8 (one sequence), g(0) = 0
(two sequences, the model in which v = 0 resets c is refuted twice), a block-2 v = 1 hanging at c =
0 (4 of 4) and a block-1 v = 1 completing at c = 0 (3 of 3); the variant that fits all 80 jobs (M3)
was formed on them and stays fitted. A debugfs reset cleared c once (E700, A5); a hang is always
followed by the harness's reset, so 'a hang clears c' and 'a reset clears c' are one observation.

Open: what c is (the VDM, the TA or a USE partition), the shape dependence, the effect of time
and of other jobs between (the merged question below holds the experiments), and the held-out
confirmation of the
v below 2 clauses.

Folded in 11.39 from Q102 (retired into this question; a fold is not an answer). Its question was:
what state does a completed job with VDM state word 1 bits 11:9 = 7 leave that makes the next such
job hang, and why does the reset after a hang clear it?

Jobs with bits 11:9 = 7 alternate strictly between completing and hanging (E413, 55 of 55 jobs),
across controls between them, with or without the pixel readback; values 3 and 5 hang sometimes. A
hang's reset restores the state a completed job changes.

What is open: where the state sits (the VDM, the TA, the MTE, the USE partitions), whether a fresh
boot starts a series with a completed job, whether a longer cycle governs 3 and 5, and what a
partition count of 7 (a field of three bits) does that 3 and 5 do less. To settle it: the
regtimeline snapshots of the VDM, TA and DPM registers around a completed and a hung job of the
series, the same series on a fresh boot, and series of 3 and 5 of fifty jobs.

**Correction 2026-11-10:** Q270 is merged into this question (retired as folded into Q163; a fold is
not an answer), and its question is now a clause of the one above. Its question was: does the
counter that decides whether a VDM_STATE1 job hangs (E700: c cleared by a hang or a reset, a job
adds g(v1) + g(v2) with g(v) = v - 2, g(1) = -1, g(0) = 0 [fitted], hang iff c + add > 8) hold for
jobs of other shapes, and what else clears it or changes it.

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

Narrowed in round 12 (offline, E1021). E545's 11.31 sweeps, run before the counter was fitted,
hold it out: 54 of 54 jobs with v 3 to 7 in a block (13 hangs, every one needing the history; a
stateless threshold gets 41) and 31 of 31 at v = 2, with c taken as 0 at each script's start. The
clauses below 2 do not hold there: E701's v = 0 reset fails a third time (`st-b1-b119-4-r2`), its
post hoc block-2 v = 1 hang at c = 0 misses three such hangs at c = 5 (17 of 20), and E700's g(1) =
-1 gets 14 of 20; block-2 v = 1 hung in all 6 jobs of the risky script and completed in the grid's
rows 4 to 7, which the grid's bits 7:0 explain as well as c [infer]. Open: the value of v below 2
(block-2 v = 1 at a controlled c of 0, 2 and 5 with the grid's bits 7:0 held at a completing value;
those jobs hang, so not the safe class), what the counter is, other shapes, and time and other jobs
between.

Narrowed 2026-11-13 (round 13, session r13-flag stage f3, decision R13-4 a; E1035; 19 jobs, 8
recovered hangs, the kit's noreset and idle:S). Held out on single rows: a v = 7 job after a
completed one at c = 5 hangs on a 128 x 128 one-block target, after 60 s idle, after a fill job and
after the kit's health fill and triangle, and completes after a debugfs reset that followed no hang
(M1 5 of 5 on those rows; each clause rival 0 of 1). Below 2 every frozen clause failed: block-2 v =
1 with bits 7:0 at 5 hung at c = 0, 2 and 5 (M1 0 of 3, M3 1 of 3, H-C05 2 of 3). The time,
other-job, reset and target clauses are answered for one job pair each; open: what decides v = 1
(neither c nor the word: E545's sg-v1-r5 and E701's c = 8 completed), v = 0, other stream shapes and
what the counter is.

Narrowed 2026-11-14 (round 18, session r18-flag stage h2, E1076). E700's counter held on two new
stream shapes, 24 vertices in one object with 8 temporaries at 64 x 64 and 48 vertices in two
objects with 16 temporaries at 128 x 64: with block 1 at v = 6 a job after a reset and the next
completed and the third hung (M1 4 of 4 held out; E413's alternation and a scaled threshold failed),
the control on E700's shape completing its first two. The shape clause is answered for these
counts; open: what decides v = 1 and v = 0, and what the counter is.

Narrowed 2026-11-16 (round 29, session r29-flag2 stage h2, E1113; the question line is reworded,
the question is not retired). It read "... what decides block-2 v = 1 (hung at c = 0, 2 and 5
after a reset or a v 2 to 7 job, E1035, completed at c = 3 and 8 in E545's grid and E701), given
that the rule held on streams of 24 and 48 vertices, one and two objects and 8 and 16 temporaries
(E1076)". O29-2 (r29-flag's fit/o29_2.out) formed H-PREV16 after E1035 was read: a block-2 v = 1
job completes iff the job right before it, no reset between, completed with a block at v 1 or 6.
Held out 3 of 3 (completed after (6,2) at c = 8, hung after (5,2) at c = 3 and after (3,2) at c =
1), the control passing; c alone and the previous job's add failed 2 of 3. It fits all 21 kept
block-2 v = 1 jobs. Not retired: what the counter and the previous-job state are, v = 0 in block 1
below c = 4, and a previous job at v 0 in block 1 or v 3 to 7 in block 2 stay open.
