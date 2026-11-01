+++
id = "Q163"
question = "what is the state the jobs leave that decides whether a job with VDM_STATE1 bits 11:9 other than 2 hangs (E700: a counter c, cleared by a hang or a reset; a job adds g(v1) + g(v2) with g(v) = v - 2, g(1) = -1 and g(0) = 0 [fitted]; it hangs iff c + add > 8), and does the rule hold beyond the one job shape that was tested (Q270)"
unit = "vdm"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E545", "E413", "E700", "E701", "E060", "E185", "E299"]
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
and of other jobs between (Q270 holds the experiments), and the held-out confirmation of the
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
