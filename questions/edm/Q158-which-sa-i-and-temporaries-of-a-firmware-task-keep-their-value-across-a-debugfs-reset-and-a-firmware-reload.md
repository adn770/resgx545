+++
id = "Q158"
question = "which sa, i and temporaries of a firmware task keep their value across a debugfs reset and across a firmware reload and boot (E536's controls read i0, i1, sa100 and sa127 as the writer of phase 11.29 left them 15 minutes and a reset and a reload earlier, and sa20, sa24, sa64, r20 and r21 not)"
unit = "edm"
kind = "hw"
value = "low"
phase = 11
evidence = ["E536", "E537", "E809", "E810"]
terms = ["Event Data Master (EDM)", "Universal Scalable Shader Engine (USSE)"]
+++

E536's two controls and E537's first control. Between the writer of 11.29 (E533) and E536's
controls there were a debugfs reset, a stock check and the reload of the arming; i0, i1, sa100 and
sa127 had the 11.29 values, sa20, sa24 and sa64 did not, and r20 and r21 held what client fills
leave. Between E536's third round and E537's control there was a reload: sa100, sa127, i0 and r21
were E536's, sa20 and sa24 read 0, sa63 0, sa64 2 and sa65 0x02000000. If a reset does not clear
the registers the firmware does not load, a backend that relies on "sa starts at zero" is wrong
above the range the boot loads. To settle it: write a marker to sa100, i0, r20 and sa20 from a
writer, reset (debugfs) and read them with the plain reader; with a reload and boot between; and
across a client fill. The question needs the closed task only for the tick, not for itself.

Narrowed 2026-11-10 (R3x-c3, E810; not retired). With markers of our own, three jobs a row: across a
client fill i0, i1 and sa63 kept, r20 read 0 and r21 the fill counter (0x1000, 0x2000, 0x3000);
across a firmware reload, with no reset and after a debugfs reset alike, i0, i1 and r21 kept and r20
and sa63 read 0 (6 of 6), with sa65 at 0x02000000. sa100, sa127, sa20 and sa24 are not writable by
our task (R2-1 b): they read 0x3cc00010, 0x3f800000, 0 and 0 in every reading, unchanged by every
perturbation, set before the run by what the data does not say. The frozen H-KEEP (i and sa63
survive, r does not) and H-ALL (r survives too) are both refuted (the frozen scorer's 'r20/r21
survived 3/3' was a scorer bug, fixed after the run and disclosed in the dataset). Open: the sa
registers our task may not write, and which step of the reload clears r20 and sa63 and keeps r21.

Moved 2026-11-11 from Q124 (retired as answered by E809; the question was whether p0 to p3 and
pclink survive from one firmware task to the next, and E809 and E810 read them at the next entry in
12 of 12 jobs). What the answer leaves, and is this question's: the state a task finds after a
perturbation is a reading made after the run, not a frozen rule (E809: after a client fill, a
firmware reload and a debugfs reset alike p0 p1 read 1 1, pclink 0x98, p2 0 and p3 the value left,
9 of 9; E536's frozen 0 1 after a fill and 0 0 after a reset held in 1 of 3 and 4 of 6), so "p2
cleared and p3 kept across a fill, a reload and a reset" needs a frozen row; and the state a task
finds after a cold boot has not run (S0 followed the stage's own arm, not a boot).
