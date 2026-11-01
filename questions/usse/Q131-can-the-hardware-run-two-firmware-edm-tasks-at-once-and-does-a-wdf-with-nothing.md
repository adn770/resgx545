+++
id = "Q131"
question = "can the hardware run two firmware (EDM) tasks at once"
unit = "usse"
kind = "fw"
phase = 11
evidence = ["E478", "E480", "E532", "E534"]
terms = []
+++

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
and no task had several loads in flight). What is open is the first half, whether a second task
starts while one runs: the stage that would have asked it (item 11, a task that spins while the 1
kHz tick arrives) was not run, because the stage before it stopped (E533). To settle it: that stage
with a wrapper that keeps the tick (Q152); until then a Rust frame for state is one per task.
