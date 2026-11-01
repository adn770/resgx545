+++
id = "E359"
claim = "With the counter group set through SETHWPERFSTATUS, CR_HWPERF_COUNTER0 to 8 count by group (groups 7 and 9 to 15 count nothing in seven jobs; group 8 moves 0x0044, 0x0048 and 0x0050 in all seven, 0x4c889, 0x66e6 and 0x49e in the 64x64 triangle), and in group 0 COUNTER3 (0x0050) counts the pixels a job shades exactly (0x1000 at 64x64, 0x4000 at 128x128, 0x800 for a 64x32 fill); whatever the group, 0x0e84 counts renders, 0x0e88 jobs, 0x0e8c rises only with renders, 0x0e90 with the pixels and the pixel program's length (eight times for eight times the loop) and 0x0eb8 is the sum of 0x0e8c and 0x0e90; one run"
unit = "platform"
method = "probes/platform/hwperf-groups.toml on the laptop, linux fork b5a86838ae59 with the debug option on: for each group 0 to 15 debugfs hwperf sets HostCtl's group and sends SETHWPERFSTATUS with status 0x11 (the counters reset, the group into CR_HWPERF_CTRL); the counters (debugfs hwperf) read before and after each of seven jobs: the triangle at 64x64, at 128x128, twice at 64x64, a 64x64 fill, a 64x64 copy and fills (64x32) whose pixel program loops 128 and 1024 times; the status back to 0 at the end; deltas per job"
tiers = ["HW", "infer"]
date = "2026-11-03"
data = ["platform-hwperf-groups"]
terms = [
    "CR_HWPERF_CTRL", "CR_HWPERF_COUNTER0", "CR_HWPERF_COUNTER1", "CR_HWPERF_COUNTER3",
    "CR_HWPERF_COUNTER4",
]
+++

**Results.** Deltas per job (tri64, tri128, two renders, fill64, copy64, loop 128, loop 1024).

| register | group | deltas |
|---|---|---|
| 0x0050 (COUNTER3) | 0, 4 | 0x1000, 0x4000, 0x2000, 0x1000, 0x1000, 0x800, 0x800 |
| 0x0054 (COUNTER4) | 0, 5 | 0x1275, 0x49aa, 0x24ea, 0x1260, 0x140a, 0x1c3a30, 0xe08b46 |
| 0x0044 (COUNTER0) | 0, 2 | 6, 6, 0xc, 0, 0, 0, 0 |
| 0x0060 (COUNTER7) | 0 | 3, 3, 6, 0, 0, 0, 0 |
| 0x0064 (COUNTER8) | 0 | 0x984, 0xa34, 0x122a, 0, 0, 0, 0 (with 0x0e8c's values) |
| 0x0044 (COUNTER0) | 8 | 0x4c889, 0x52bc1, 0x5ca9c, 0x3be08, 0x3cbfc, 0xac853, 0x3bde80 |
| 0x0048 (COUNTER1) | 8 | 0x66e6, 0x7aa9, 0x78c8, 0x577a, 0x585f, 0x75e1b, 0x387743 |
| 0x0050 (COUNTER3) | 8 | 0x49e, 0x126a, 0x93c, 0x498, 0x507, 0x710b3, 0x3822c6 |
| 0x0e84 | all | 1, 1, 2, 0, 0, 0, 0 |
| 0x0e88 | all | 1, 1, 2, 1, 1, 1, 1 |
| 0x0e8c | all (group 0) | 0x984, 0xa34, 0x122a, 0, 0, 0, 0 |
| 0x0e90 | all (group 0) | 0xc92, 0x26c0, 0x19c2, 0xc6a, 0x1560, 0x71658, 0x384078 |
| 0x0eb8 | all (group 0) | 0x1616, 0x30f4, 0x2bec, 0xc6a, 0x1560, 0x71658, 0x384078 |
| 0x0eb4, 0x0ebc, 0x0ec0 | all | near-constant per kind of job; 0x0ebc and 0x0ec0 about x3 at 128x128 |

- Groups 1 to 6 move other counters of 0x0044-0x0064 (for example group 5 makes 0x0044, 0x0048
  and 0x005c follow the loop length, group 3 makes 0x0050 0x426 per 64x64 render); group 8 moves
  0x0044, 0x0048 and 0x0050 in every job (the others stay 0); groups 7 and 9 to 15 leave all nine
  at 0 in every job. 0x0040 (`CR_HWPERF_CTRL`) is not counted; it reads 0x1ff after the status
  goes back to 0.
- The group-independent counters vary by a few percent between groups for the same job.

**What it shows.**

- `CR_HWPERF_CTRL`'s group selects what 0x0044-0x0064 count; at group 0 COUNTER3 is a pixel
  count, exact on every job [HW].
- 0x0e84 counts renders and 0x0e88 jobs [HW]; 0x0e8c, 0x0e90 and 0x0eb8 behave as busy-cycle
  counts of the TA side, the pixel side and both [infer: they scale with geometry, pixels and
  instructions, and the third is the sum of the others].
