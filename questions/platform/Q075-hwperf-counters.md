+++
id = "Q075"
question = "what does each HWPerf counter the firmware records (0x0044-0x0064, 0x0e84-0x0e90 and 0x0eb4-0x0ec0) count, and how does the group in CR_HWPERF_CTRL select them?"
unit = "platform"
phase = 11
evidence = ["E149", "E150", "E152"]
terms = ["CR_HWPERF_CTRL", "CR_HWPERF_COUNTER0"]
+++

The HWPerf routine stores the nine registers 0x0044-0x0064 and eight more from 0x0e84 to 0x0ec0 in
each record (E149). SET_HWPERF_STATUS writes CR_HWPERF_CTRL = 0x1ff and pulses CR_HWPERF_PULSE when
bit 0 of its data is set, and puts the host's group in CR_HWPERF_CTRL bits 12:9 (E150, E152). Read
from a shader in a run with no group set, the first nine read 0, three of the others stay the same
and five rise (3d.md §13).

What is open (3d.md §13): what each counts.

To settle it: on the laptop, the counters sampled with regtimeline before and after jobs that differ
in one thing (pixels drawn, triangles, texture fetches, instructions), under each group value of
CR_HWPERF_CTRL bits 12:9.
