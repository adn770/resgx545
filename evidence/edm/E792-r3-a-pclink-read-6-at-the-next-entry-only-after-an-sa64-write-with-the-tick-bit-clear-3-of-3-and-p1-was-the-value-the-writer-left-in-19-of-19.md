+++
id = "E792"
claim = "In the 17 R3-events stage a jobs that ran a writer (A1 to A6, 3, 3, 3, 3, 3 and 2 jobs; the two A0 jobs had none) the entry registers our reader stored at the next event after the closed task had run were: pclink 0x98 in 14 jobs and 6 in the 3 A4 jobs, the only writer that wrote sa64 with bit 1 (the tick bit of pa0) clear (sa64 = pa0 & ~2, which the writer read back as 0 in the same pass), against 0x98 after A5's sa64 = pa0 (3 of 3, the tick bit set), A2's sa65 write, A3's, A1's sa63 write and A6's, as the frozen H-ALIAS predicted for A4, A2 and A5 (pclink held in 9 of 9 of those jobs); p0 read 1 in all 19 jobs, whether the writer left it 0 (A1 to A5), 1 (A6) or the previous pass left 0 (A0); p1 read 0 in the 15 jobs of A1 to A5, whose writer set it 0 before its tail call, and 1 in A6 (p0 = p1 = 1 at the tail call) and in the two A0 jobs, so in this stage p1 at the next entry is the value our task's tail left in 19 of 19 jobs (frozen rows for A2 and A5 said 1 and failed, 6 of 6 jobs: the prediction took the reader's own p1 of A0, not the writer's setp, a design error found after the run, E791 and below); the A4 rows' dword 12 difference to the pass count, frozen as passes - 1, was cannot tell (the bracketed intervals (-9, 6), (-8, 5), (-7, 6) contain -1 and 0)"
unit = "edm"
method = "R3-events stage a, the reader's stored entry registers of the jobs of E791 (the same run, 1794307123-28500, dataset edm-closing-r3-events): alias.s command 9 stores r22 (pclink at entry), r23 to r26 (p0 to p3), sa64, sa65, sa63 and pa0 to pa2 of the event at which the reader runs, the first event after the writer's pass and the closed task's; the writer's own copies of sa63 to sa65 at entry and after the write (stad 64 to 72 of command 1 to 5) and the pass count (dword 20, one count per pass) were read from the same page; the tick bracket of the runner (HostCtl dword 12, page, register, page) before and after gave the interval of 'dword 12 - passes' for A4; the frozen predictions (predictions/a.tsv, PREDICTIONS.sha256) for A4 came from E536's reading (sa64 markers with bit 1 clear, next entry pclink 6, p1 as left; the note of 2026-11-10 on Q124 and Q152), those for A2 and A5 from E536's controls (pclink 0x98, p1 1); scored by the frozen score/score_r3.py a; the reading of p1 from the writer's source (setp and the dispatch's tests) and of p0 was made after the run, not held out"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["edm-closing-r3-events:out/a/"]
terms = ["Event Data Master (EDM)"]
+++
**What ran.** E536 read, at the entry after a writer of ours, p1 as the writer left it and pclink 6
(the value of the writer's own tail triple) against p1 1 and pclink 0x98 after an ordinary tick, and
its three sa64 markers all had the tick bit clear (note of 2026-11-10 on Q124). A4 writes an sa64
with the tick bit clear on purpose; A5 and A2 are its controls (sa64 with the bit set, and sa65
alone); the others vary the other writes.

**Results [HW].** Reader at the next event (entry registers): pclink, p0, p1, p2, p3.

| rows | jobs | pclink | p0 | p1 | p2 | p3 |
|---|---|---|---|---|---|---|
| A0 reader only | 2 | 0x98 | 1 | 1 | 0 | 0 |
| A1 sa63, A2 sa65, A3 sa65 restored, A5 sa64 = pa0 | 12 | 0x98 | 1 | 0 | 1 | 1 |
| A4 sa64 = pa0 & ~2 | 3 | 6 | 1 | 0 | 1 | 1 |
| A6 r, i written, p0 = p1 = 1 at the tail | 2 | 0x98 | 1 | 1 | 1 | 1 |

In A4 the writer's own read-back of sa64 after the write was 0 (it took the write inside the pass),
and in A5 2; sa64 at the next entry read 2 in every job (a fresh event). The next entry's sa63 and
sa65 read 0 and 0x02000000 except after A1, where the sa63 marker was still there. The dword 12
difference of A4: its intervals (-9, 6), (-8, 5) and (-7, 6) (the bracket's own uncertainty, a few
ticks) contain the frozen -1, so the sub-row is cannot tell, as the scorer printed.

**The p1 rows of A2 and A5 (frozen FAILED, 6 of 6 jobs) [post hoc, from the writer source, not
held out].** The frozen rows said p1 1 for A2 and A5, taken from A0's reader and from E536's
controls. alias.s sets p0 to p3 to 0, 0, 1, 1 (setp) in commands 1 to 5 before the tail call, so
p1 was 0 when the closed task was called, and the reader at the next entry read 0: the p1 of the
writer's tail, as E536's p1 was ("1 in the other readings" are readers whose own previous tail left
1, as A0's and A6's did). A4's frozen p1 0 held for the same reason, so p1 does not separate A4
from A5: the discriminating register is pclink, and its frozen rows held (0x98 in A2 and A5, 6 in
A4, 9 of 9 jobs). The frozen verdict stands as printed (H-ALIAS listed as refuted because of these
p1 rows); the reading that the prediction was a design error, and that H-ALIAS's pclink and
sa64-bit-1 prediction held on every job, is [infer], read from the source after the run.

**Reading [infer].** After a writer that put a non-tick word (bit 1 clear) in sa64 the closed task
left the pclink of our tail triple and p1 as our task left them, which fits the closed task taking
a path that skips the tick handler (note of 2026-11-10 on Q124); after a tick word it ended as on
any tick (0x98). p1 at the next entry is our tail's p1 in every row, 19 of 19. p0 is not the
writer's: it read 1 in every job, set 0 by A1 to A5 and 1 by A6. p2 and p3 are not separated: A0's
reader read 0, 0 and every other job 1, 1, and the passes before A6's writer are not recorded
register by register, so whether they follow the tail is not shown.

**Not shown.** Whether the closed task's path depends on the tick bit of sa64 alone or also on
other bits of the word (every sa64 here is 0 or 2 or the tick's own value); whether the missed
tick handler shows in the tick counter (the bracket could not tell); p2 and p3.
