+++
id = "Q152"
question = "what must a task of ours that runs in place of the closed general task (or before it) leave or do so that the next event is delivered and the 1 kHz tick continues: what in E533's task (an arbitrary pclink write, p0 to p3 = 1, 0, 1, 0, `nop.end` instead of the closed task), in E536's writer (3 of 3 rounds kept the tick) and in E537's writer (sa63 and sa65 written, p0 = p1 = 1: the armed reader did not run) differs, and does the closed task use p0 to p3, sa63 or sa65"
unit = "edm"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E533", "E155", "E536", "E537"]
terms = ["Event Data Master (EDM)", "CR_EVENT_TIMER"]
+++

E533: `HostCtl` dword 12 and `USE0_SERV_EVENT` stopped after a task of ours that ended with
`nop.end` for one tick (one run, the stage's own trigger), and a debugfs reset recovered. That task
did two things in the same run: it skipped the closed general task, and it wrote `sa64`, `sa100`,
`sa127`, `sa20`, `sa24`, `r20`, `r21`, `i0`, `i1`, `p0` to `p3` and `pclink`, then stored a command
for the next event. The cause is confounded: skipping the closed task, clobbering state the closed
task or the PDS needs, the `EVENT_TIMER` write of the tick handler (E155) that the closed task would
have made [infer], or something our command-1 path left undone are all consistent with the run.

Narrowed in 11.30 (not retired). The second half of the question is answered for one writer: a task
of ours that wrote sa100, sa127, sa20, sa24, r20, r21, i0, i1 and set p0 to p3, and then called the
closed general task, kept the tick (E536, 3 of 3 rounds, tick 910.8 to 1005.4 Hz) and what it wrote
to sa100, sa127, sa20, sa24, r20, r21, i0 and i1 was read by the next task, after 1200 ms and (not
r20 and r21) after a client fill. The first half is not answered, and E537 makes it wider: a writer
that wrote two more sa (sa63 and sa65), set no predicate and called the closed task was not followed
by its armed reader within 100 ms (1 run, HostCtl dword 12 frozen in the dumps after it). Against
E533's task (which wrote an arbitrary pclink, p0 to p3 = 1, 0, 1, 0, and ended with `nop.end`),
E536's writer differs by no arbitrary pclink write (the tail triple's own write only, which every
pass makes), the tail call, and the p values (0, 0, 1, 1), so it shows the sa, r, i and p writes of
its list are not enough to stop the tick when the closed task follows; it does not separate skipping
the closed task from the arbitrary pclink write, nor from the p values. The pclink write cannot be
repeated with the fixed verifier of the fork (it refuses `mov pclink` outside the patched triple);
E533's task and E536's ran with the earlier one. To settle what remains of E533: `nop.end` after
E536's writes, with no arbitrary pclink write and no closed task (the control that separates the
missing closed task from the pclink write and the p values), predictions frozen first; the
differences inside E537 are the second half of this question, folded in below from the question that
asked them.

Reworded in 11.39 (merge 3: Q152, Q155 and Q156 in one question; the wording is drafted from the
three
landed texts and no new run bears on it). The known parts: E536's writer kept the tick and what it
wrote to sa100, sa127, sa20, sa24, r20, r21, i0 and i1 was read by the next task; E533 and E537
stopped it; sa65 held 0x02000000, the value of a tick's pa1, before any writer of E537; E536's
reader found p = 1, 0, 1, 1 and pclink 6 after the writer, pclink 0x98 and p1 = 1 after the
controls. Q156's candidates are one list: the predicates at the closed task's entry, the sa63 or
sa65 write, the sa64 write, the missing closed task, the arbitrary pclink write (not repeatable
with the fixed verifier of the fork). To settle it: the state3.s variants of Q155 and Q156 and the
control of this question (`nop.end` after E536's writes, no arbitrary pclink write), predictions
frozen first. The experiments wait for the `nop.end` stub.

Folded in 11.39 from Q155 (retired into this question; a fold is not an answer). Its question was:
why do p1 and pclink at the entry of the event after a writer of ours hold the writer's values (p1 =
0 and pclink = 6, the continue index of its tail call, in 3 of 3 rounds) when after an ordinary tick
they hold 1 and 0x98 (8 of 8 readings), and is the closed general task's path on that tick different
from its path on a tick that follows no task of ours

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

Folded in 11.39 from Q156 (retired into this question; a fold is not an answer). Its question was:
which of the differences between the writer whose armed reader did not run within 100 ms (E537: sa
and r and i written with sa63 and sa65, p0 = p1 = 1 at the tail call, 1 run) and the writer that was
not (E536: no sa63 and sa65, p0 to p3 = 0, 0, 1, 1, 3 of 3 rounds) stops the tick after the closed
task is called, and does the closed task use p0 to p3, sa63 or sa65 at all

Narrows Q152. E533's task skipped the closed task, E536's called it and kept the tick, and E537's
called it and did not. Candidates: the predicates the closed task finds at its entry (p0 = p1 = 1
against 0, 0, 1, 1), the write of sa63 or sa65 (sa65 held 0x02000000, the value of a tick's `pa1`),
the sa64 write (in both writers), and a first stop after a command that E536's rounds did not
see (E536 was 3 of 3, E537 1 of 1, and the two are different blobs). The writer of E533 and the
earlier wrappers (E532) are not controls: they differ in more than one of these.

To settle it: state3.s cmd 2, 3 and 1, each three times, then cmd 4 last, one reset at most per
stop, the stop rule first (a second stop ends the stage), predictions frozen after E537 and before
the first run. A repeat of cmd 4 alone would say whether the stop repeats.
