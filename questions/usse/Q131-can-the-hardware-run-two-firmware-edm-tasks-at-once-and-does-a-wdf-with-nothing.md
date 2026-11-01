+++
id = "Q131"
question = "can the hardware run two firmware (EDM) tasks at once, and does a wdf with nothing outstanding or an unfenced store at the end of a task behave as it does in a fill"
unit = "usse"
kind = "fw"
phase = 11
evidence = ["E478", "E480"]
terms = []
+++

The firmware toolchain's question whether two EDM tasks overlap, and the firmware half of E478 to
E480: a fill is started by the PDS of a render in its pixel phase, not by the EDM through the
microkernel's dispatch, so none of the fill measurements (wdf covers loads, an empty wdf is a no-op,
the dword the host reads after a job holds the stored value) is shown for an EDM task. What is open:
the same probes as firmware tasks of our own, and a second task started while one runs (two tasks in
flight, one frame per task). To settle it: phase 12's firmware tasks (a task that loops while
another is started by a request); until then a Rust frame for state is one per task.
