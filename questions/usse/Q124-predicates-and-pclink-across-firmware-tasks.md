+++
id = "Q124"
question = "do p0-p3 and pclink survive from one firmware (EDM) task to the next, and does a task start with them clear, set or as the last task left them?"
unit = "usse"
kind = "fw"
phase = 11
evidence = ["E475", "E477", "E484"]
terms = ["Universal Scalable Shader Engine (USSE)", "Event Data Master (EDM)"]
+++

E475 and E477: between fills on the render node, pclink and p0-p3 are left over from the last job
in about 96 and 99 percent of the pixel instances, and from other code in the rest (p0 and p1 in a
fill pair: 96.3 to 100 percent of the instances in 10 of 10 reader jobs, E484). A fill is not
a firmware task: it is started by the PDS of a render, in the pixel phase, not by the EDM
through the microkernel's own dispatch, and what the microkernel does between tasks (it uses pclink
itself: its CCB dispatch moves an address there and jumps, E091) is not seen from here.

What is open: the same pair of jobs as firmware tasks of our own, which needs a replaced
microkernel or a task the existing one runs on request. To settle it: phase 12's firmware tasks
(writer, reader, five pairs) with the pixel count replaced by the instance count of a task; until
then a task must set p0-p3 by a test and write pclink before reading either.
