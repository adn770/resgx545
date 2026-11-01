+++
id = "Q155"
question = "why do p1 and pclink at the entry of the event after a writer of ours hold the writer's values (p1 = 0 and pclink = 6, the continue index of its tail call, in 3 of 3 rounds) when after an ordinary tick they hold 1 and 0x98 (8 of 8 readings), and is the closed general task's path on that tick different from its path on a tick that follows no task of ours"
unit = "edm"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E536", "E537"]
terms = ["Event Data Master (EDM)"]
+++

E536: after the writer of the state2 wrapper (sa, r and i written, p0 to p3 set to 0, 0, 1, 1,
a tail call to the closed task) the reader at the next event read p = 1, 0, 1, 1 and pclink 6,
while the two controls, the reader after 1200 ms and the reader after a fill read pclink 0x98 and
p1 = 1. p0 read 1 although the writer set 0, and p2 and p3 equal the writer's flags but also occur
in the other readings, so p1 and pclink are the registers that differ. Either the closed task
leaves pclink and p1 alone on the tick after our writer (it takes a path it does not take
otherwise, which would then depend on something we wrote, such as the flags or the stored command)
or the registers at the entry of a task are not what the previous task, the closed one, left. The
pclink value 6 is the one the writer's own tail triple wrote (`mov r30, #cont0; mov pclink, r30;
lapc`, which every pass of the wrapper executes, ours in command 0 too), and after a normal tick the
next entry reads 0x98, so the closed task rewrites it on a normal pass and did not after the writer
[infer]. That favours "the closed task took another path" over "the entry registers are not what
the previous task left", which would not explain the 0x98 after normal passes; neither is shown.

To settle it: the writer variants of state3.s (cmd 2 arm only, cmd 3 predicates only, cmd 1 with
the flags all 1), each three times, with cmd 4 (the writer whose armed reader did not run, E537)
last and a second stop ending the stage; Q156 asks what that stop depends on.
