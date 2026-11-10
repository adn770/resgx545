+++
id = "Q124"
question = "do p0-p3 and pclink survive from one firmware (EDM) task to the next, and does a task start with them clear, set or as the last task left them?"
unit = "usse"
kind = "fw"
phase = 11
evidence = ["E475", "E477", "E484", "E533", "E536", "E537"]
terms = ["Universal Scalable Shader Engine (USSE)", "Event Data Master (EDM)"]
+++

E475 and E477: between fills on the render node, pclink and p0-p3 are left over from the last job
in about 96 and 99 percent of the pixel instances, and from other code in the rest (p0 and p1 in a
fill pair: 96.3 to 100 percent of the instances in 10 of 10 reader jobs, E484). A fill is not
a firmware task: it is started by the PDS of a render, in the pixel phase, not by the EDM
through the microkernel's own dispatch, and what the microkernel does between tasks (it uses pclink
itself: its CCB dispatch moves an address there and jumps, E091) is not seen from here.

Narrowed in 11.30 (not retired). The pair was run as firmware tasks of ours that keep the tick (the
writer calls the closed task after its writes, E536). The reader at the next event, with the closed
task run in between, read: p1 = 0 (the writer's value) in 3 of 3 rounds, against 1 in all 8 other
readings; p2 = 1 and p3 = 1 (the writer's flags, but they also read 1, 1 after 1200 ms and move
between readings with no writer, controls 0, 0 and after a fill 0, 1, so they show nothing about
persistence); p0 = 1 (the writer set 0); pclink = 6 (3 of 3), against 0x98 in the 8 other readings,
where 6 is the value of the writer's own tail triple, which every pass of the wrapper writes
[infer]. After 1200 ms and after a client fill p1 = 1 and pclink 0x98 as in the controls, while p2
and p3 differ between readings with no writer (controls 0, 0; after 1200 ms 1, 1; after a fill 0,
1). So a task of ours does not start with p0 to p3 and pclink clear or as an ordinary tick leaves
them: at the next entry p1 was as our writer left it and pclink was the writer's own triple value,
p0 was not, and Q152 asks why. The pclink write that the question first named cannot be run: the
earlier task (E533) wrote it, the fixed verifier of the fork refuses `mov pclink` outside the
patched triple, and the prediction that was frozen for it (11.29's Q124_pred: p0 to p3 survive as 1,
0, 1, 0 and pclink keeps bits 17:0 of 0x2a5a5) was written for that task and was never evaluated
(its stage stopped, E533); the writers of 11.30 write no arbitrary pclink (only the tail triple's
own write, which every pass of the wrapper makes).

What is open: p0, p2 and p3 (a writer whose flags differ from the control's in each of them), a
writer that leaves pclink as a call does (E475, a taken or untaken call writes it), and whether the
closed task's path is what keeps p1 and pclink (Q152). Until then a task must set p0-p3 by a test
and write pclink before reading either, as a fill must (E477).

Note 2026-11-10 (a reading of E536's data before the round 2 runs, not a new measurement; see
Q152). The three sa64 markers of E536's writers (0x8add1e25, 0xeec4f0dd, 0xf8a4ac80) all have bit 1
clear [data]. The tick is `pa0` bit 1 (E155), so on those passes the word the closed task dispatches
on was not a tick, and the closed task may have skipped the tick handler; that would leave p1 as the
writer left it and pclink at 6 on the next entry, against 1 and 0x98 after an ordinary tick [infer,
untested: nothing wrote a marker with bit 1 set; a count of HostCtl dword 12 short by one on those
passes, which would support it, is not recorded in the files read for this note]. It would explain
p1 and pclink and not p0 (written 0, read 1), p2 and p3.
