+++
id = "Q163"
question = "what decides whether a job completes when VDM_STATE1 bits 11:9 are 1, 6 or 7 (and sometimes 4 or 5), when the same word 0x0a022205 hung twice in one script and completed in another"
unit = "vdm"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E545", "E413"]
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
leaves a state (Q102 asks it for = 7 alone).

To settle it: the same word in jobs run after a completed job, after a hang, after a reset, after a
different word, after a sleep of 0 and of 10 seconds, and in a random order, counting hangs per
class; the alternation test of E413 repeated for = 1, 4, 5, 6. No kernel change.
