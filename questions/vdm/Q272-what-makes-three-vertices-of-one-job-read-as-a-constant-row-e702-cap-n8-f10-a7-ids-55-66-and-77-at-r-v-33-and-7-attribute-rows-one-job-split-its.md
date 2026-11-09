+++
id = "Q272"
question = "what makes three vertices of one job read as a constant row (E702: cap-n8-f10-a7, ids 55, 66 and 77 at R * V = 33 and 7 attribute rows; 3 pixels of the render differ), one job change its render by 260 pixels with every vertex identity present and its vertices split 15, 15, 15, 15, 15, 15, 15, 9 and 12 (a = 12), and one job hang (N = 2, 16 vertices, 32 attribute rows), and are these and E546's lost vertex at 33 with 8 rows the same kind of event"
unit = "vdm"
kind = "hw"
value = "low"
phase = 11
evidence = ["E702", "E546", "E738"]
terms = ["VDM_TASK1.OUTPUT_SIZE"]
+++
In E702's 16 jobs at R * V of 32 and 33 and 1 to 32 attribute rows, 13 are plain (the tool's o0
histogram equal to the other jobs of the same N) and three differ, each once: attribute rows 7 at N
= 8 (3 vertices, 11 apart in id, read 0x3f3a2e8b 0x3f800000 0x3f900000 ... the same nine words in
the three: a constant row in place of the vertex; o0 0xff203040 x2285 against x2288, 3 pixels),
attribute rows 12 at N = 8 (objects of 15 seven times, 9 and 12, 126 vertices all present, but o0
0xff203040 x2028 against x2288: 260 pixels differ, another image), and attribute rows 32 at N = 2
(a hang, `job hung, recovering`, no dump). E546's one lost vertex at 33 with 8 rows was not seen in
the two a = 8 jobs here, which ran under another module and tool, so it is not repeated either.
The three N = 8 events are alike: not repeated, pending a repeat; none supports or refutes a limit at
33.

Open: whether the three repeat (one run each), what the constant row is (the vertex the program or
the PDS reads from a default, the first row of the attribute area), what attribute rows between 24
and 32 do, and whether the hang is the attribute count or its product with N and V (a counter state,
E700, is excluded for the job: it followed a reset).

To settle it: repeats of the three and of the a = 8 job (three runs each, a reset before each),
attribute rows 7 at N = 2 and 11, 12 at N = 2 and 11, and rows 24, 28, 31 and 32 at N = 8 and 11,
with a reset before every job.

Narrowed 2026-11-09 (S1, E738; the repeat clause, frozen held out, after controls that reproduced
E702's histograms 2288 and 2821). The a = 7 event repeats: x2285 in 3 of 3 runs (a frozen result,
HD), and the hang at 32 attribute rows at N = 2 repeats (3 of 3). The a = 12 event repeats as a
change but not as E702's: x2582 in 3 of 3 (neither E702's x2028 nor the base x2288; the frozen
scorer's label "HO" does not fit the frozen definitions). The a = 8 job changed the render in 2 of
3 runs (x2288, x2156, x2156), not a function of the words alone. Post hoc (decoded after the run
with the vertex-fate functions, not held out): the a = 7 jobs lose ids 55, 66 and 77 in 3 of 3, the
a = 12 jobs keep every vertex in the regular split of 15 x 8 and 6 (E702's job split 15 x 7, 9
and 12), and the two changed a = 8 jobs lose vertex 70 with objects of 15, 15, 15, 15, 9, 15, 9,
15, 15 and 3. Still open: what the constant row is, what makes a = 8 split in some runs (a reset
before it or not), what a = 12 changes when every vertex is present, and whether these are
the kind of event E546's lost vertex was.
