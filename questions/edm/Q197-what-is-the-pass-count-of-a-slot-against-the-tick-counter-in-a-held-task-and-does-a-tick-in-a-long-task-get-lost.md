+++
id = "Q197"
question = "what is the pass count of the tick-driven slot against the tick counter while the EDM is held by a task of 0.7 to 6.5 ms (and above), is a tick that falls inside a long task lost, queued or delayed, and is an event that arrives while a task of ours runs (a tick of any slot, a TA or 3D event, a host kick) lost, queued or merged, for tasks up to and above 7 ms"
unit = "edm"
kind = "fw"
phase = 11
evidence = ["E539", "E605", "E478", "E480", "E532", "E534", "E601", "E602"]
terms = []
+++
E539 (tick only, slot 0, up to 6.9 ms) saw the counter 1.9 to 2.2 behind the expected ticks. E605
(all four slots armed, tick only, 0.7 and 6.5 ms) kept the overlap flags at 0 and slots 1 to 3 at 0
passes, but its comparison of the pass count with the tick count is not decided: the tick counter
is read through the `regs` dump before the command and after the job and the page after that (the
dump's duration is not measured), so passes (17 to 21) and ticks (10 to 13) both carry an offset
of about 10 against the expected 0.8 to 6.2 from the job's wall time. The difference between the
two task lengths (2.3 ticks and 3.3 passes against 5.2 expected) is consistent with E539's lag,
from five jobs.

To settle it: an instrument that stamps the job inside the task (the task reads the tick counter
register at entry and at exit, through a register read it may do, and stores both, so the host
reads only the page), and a table of task lengths from 0.3 ms to 20 ms (the E539 lag grows with
the task, Q033's follow-up needs more than 7 ms). f14b (a host kick) and f14c (a client triangle
during the task, hold_recovery as q033q2) were not run and stay prepared.

Folded in 11.39 (merge 2): the question line is extended with the events of other slots, a TA or 3D
event and a host kick, which is the open list of Q131; Q131's evidence moves here. Its experiments
(f14a, f14b, f14c) stay prepared and wait for the stage, with Q197's own (a stamp inside the task).

Folded in 11.39 from Q131 (retired into this question; a fold is not an answer). Its question was:
can the hardware run two firmware (EDM) tasks at once

The firmware toolchain's question whether two EDM tasks overlap, and the firmware half of E478 to
E480: a fill is started by the PDS of a render in its pixel phase, not by the EDM through the
microkernel's dispatch, so none of the fill measurements (wdf covers loads, an empty wdf is a no-op,
the dword the host reads after a job holds the stored value) is shown for an EDM task. What is open:
the same probes as firmware tasks of our own, and a second task started while one runs (two tasks in
flight, one frame per task). To settle it: phase 12's firmware tasks (a task that loops while
another is started by a request); until then a Rust frame for state is one per task.

Narrowed in 11.29 (not retired). In a firmware task of ours (E531), a `wdf` with no load outstanding
on `drc0` between a `str` and an `ldr` changed nothing (X3, 18 of 18 runs, 15 of which could show a
change), and a `stad` of the result followed by a load of the run id, a `wdf` and two more stores,
then the flag with no `idf`, landed (X9, 18 of 18), as in a fill (E534; E532 has the `idf` and `wdf`
variant). Of the three fill facts above, two are shown for an EDM task, for two registers: an empty
`wdf` is a no-op (X3, on the assumption that a `str` is not outstanding to a `wdf drc0`) and the
dword the host reads holds the stored value (X9). That `wdf` covers loads was not run in a firmware
task (every task of ours does `ldad`, `wdf`, then uses the value, which agrees but is not a case,
and no task had several loads in flight). Narrowed again in 11.30 (not retired). The first half is
answered for the ticks only: a task of ours that held the EDM for 0.7, 2.2 and 6.5 ms (10000, 30000
and 100000 iterations of a three-instruction loop) was never found busy by a second wrapper pass of
the general slot: the overlap flag stayed 0 in 10 of 10 runs (E539), so no second pass was seen
while one of our tasks ran, up to 6.9 ms, for a tick-only stream in one slot with no TA or 3D event
(the flag cannot see a pass that starts before the busy store, a pass of another slot, or an event
queued or dropped). The tick counter was 1.9 to 2.2 behind in the three 100000 runs (+1.7 to -0.7 in
the others), so at most two of the six ticks of the busy window were lost, or the counter is not the
handler's alone; queued or dropped is not settled. A Rust frame may assume one task at a time for
ticks of one slot up to 6.9 ms (a recommendation, not a measurement); it may not assume that every
tick is served, as two of six may be lost while a long task runs. What is open: events that arrive
while a task runs (queued or dropped: a counter in the handler's own path, a flag per tick), tasks
of other slots, a TA or 3D event during a task, tasks longer than 7 ms, and `wdf` covering several
loads in a task. To settle it: a task that holds the EDM while a job is queued, with the handler's
runs counted by a flag per tick.

Narrowed in 11.36 (not retired). Two of the open parts were run in firmware tasks of ours (stage f12
and f8, data p1137-f12 and p1137-f8). One `wdf` over N = 2 to 100 `ldad.bypassl1` loads from two
page bases at mixed offsets (every 11th load a repeated address) left every destination holding its
own load in 21 of 21 jobs, so loads, one `wdf` and the stores is sufficient in a firmware task with
a backend-like mix of offsets; the `wdf` was not shown to wait or to be needed, since the control
landed without it at 32 slots (E602); and p0 kept across up to 64 `mov` limm, 32 `ldad` with a
`wdf`, `wdf` and `idf` and a taken branch (E601, 72 of 72). The control did not do what a fill did:
32 loads followed by 32 stores with no `wdf` stored the new value in 32 of 32 stores in 3 of 3 jobs
(E602, prediction P37_F12b failed), so the missing-`wdf` hazard of E517 is not shown in a firmware
task at that distance (Q194). Still open: events that arrive while a task runs (queued or dropped),
tasks of other slots, a TA or 3D event during a task and tasks longer than 7 ms (the stages f14a,
f14b, f14c and q033q2 were not run in this phase; the follow-up stages are run separately).
