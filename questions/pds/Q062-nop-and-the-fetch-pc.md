+++
id = "Q062"
question = "what makes the PDS fetch pc read one or two below the reading instruction's index plus 3, at instructions 26-27 back to back (the end of a 64-dword block) in most runs?"
unit = "pds"
phase = 11
evidence = ["E128", "E142", "E143", "E260", "E261", "E384"]
terms = []
+++

rfence and rwfence leave the data-segment registers as they are in a program with no load or store
(E142); a load's dwords arrive at the next fence (E143). nop takes one instruction slot and none of
its other 27 bits changes a result (E260, E261).

pc.0 reads index + 3 at most places and index + 2 or + 1 at others, never more nor less, over 399
reads in 27 programs: back to back, after 0-14 nops, after each kind of instruction, across branches
and a call and after loads (E261). Where it reads less is mostly a fixed place in the program
[infer]: back to back, two consecutive reads at instructions 26-27 in ten of twelve runs whatever
the nops before them (0-3), and 19-20 in two; the branch program reads the same in all three runs,
and the nop-gap programs do but at their first read and one read of one run. With the 36-dword data
segment, instructions 26-27 are dwords 62-63, the last two before a 64-dword boundary. The simulator
gives index + 3 and accepts the hardware's value up to 2 below.

Narrowed in 11.14 (E384): with 1 to 4 and 8 words of 0 ((p0) movs mr, ds0[0], ...) before the reads,
every read is still its index + 3 or + 2 (480 reads, five runs each), the leading words counted as
instructions; a lag pair sits at instructions 24-25 (dwords 60-61) in 14 of the 20 runs with 1-4
leading words and among the first four reads in 19; with no leading words the pair sat at 26-27 in
two runs, at 19-20 in two and nowhere in one, so the baseline varies (E261's ten of twelve was not
repeated); with 8 at 35-36 in all five runs. The 16-byte offsets and the other pipe busy were not
run (the tool does not place programs).

What is open (pds_isa.md §7, item 13): whether the lag is the fetch crossing a 64-dword (256-byte)
boundary, what makes it fall elsewhere in some runs (the other PDS pipe, memory traffic), and so a
model of the fetch that gives the exact value.

To settle it: the back-to-back case ten times with the data segment grown or shrunk by 1-4 dwords,
so that the 64-dword boundary moves against the instructions, and with the program placed at each
16-byte offset of a 64-byte line; alone and with the other pipe busy (a fill of one tile against
eight), counting where the lag falls per run.
