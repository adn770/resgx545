+++
id = "Q075"
question = "what does each HWPerf counter the firmware records (0x0044-0x0064, 0x0e84-0x0e90 and 0x0eb4-0x0ec0) count, and how does the group in CR_HWPERF_CTRL select them?"
unit = "platform"
phase = 11
evidence = ["E149", "E150", "E152", "E359"]
terms = ["CR_HWPERF_CTRL", "CR_HWPERF_COUNTER0"]
+++

The HWPerf routine stores the nine registers 0x0044-0x0064 and eight more from 0x0e84 to 0x0ec0 in
each record (E149); SET_HWPERF_STATUS puts the host's group in CR_HWPERF_CTRL bits 12:9 (E150,
E152).

Narrowed by E359 (all 16 groups, seven jobs each, one run): the group selects what 0x0044-0x0064
count (groups 7 and 9 to 15 count nothing in these jobs, group 8 moves 0x0044, 0x0048 and 0x0050);
in group 0 `CR_HWPERF_COUNTER3` (0x0050) is the number of pixels a job shades, exact on renders,
fills and copies. Whatever the group, 0x0e84 counts renders, 0x0e88 jobs, 0x0e8c rises only with
renders, 0x0e90 with pixels and program length, and 0x0eb8 is the sum of 0x0e8c and 0x0e90 (busy
cycles of the TA side, the pixel side and both, a reading).

What is open: the other counters of each group (the deltas are in E359's data), and 0x0eb4, 0x0ebc
and 0x0ec0, near-constant per kind of job.

To settle it: per group, jobs that differ in one more thing each (triangle count at a fixed pixel
count, texture fetches, depth tests, memory written), read with the same script.
