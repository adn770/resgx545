+++
id = "E434"
claim = "Under HWPerf group 0 register 0x0060 counts 3, 15, 45 and 126 for the triangle probe with 1, 5, 15 and 42 triangles (three vertices each) and group 1's 0x0050 counts the same, group 0's 0x004c counts 7 a triangle for 1 to 15 triangles and 304 for 42, and 0x0e84 (renders) is 1 for each triangle job in all 16 groups; the same in 3 of 3 runs of the table (48 group-runs), with the fills of 128x32 and 256x16 and the 128x32 copy run at strides equal to their widths"
unit = "platform"
method = "probes/platform/hwperf-vary.toml (hwperf-vary.sh) on the laptop (direct cable), linux fork f1fad0ed9d0e with the debug option on: under each of the 16 counter groups (debugfs hwperf, group G status 0x11) the counter registers 0x0044-0x0064 and 0x0e84-0x0ec0 read before and after sgxfive-test probe --tri with 1, 5, 15 and 42 triangles at 64x64, fills of 64x64, 128x32 and 256x16 and copies of 64x64 and 128x32, three runs (432 jobs; the strides of the 128x32 and 256x16 fills and the 128x32 copy set to their widths); the deltas computed from the reads"
tiers = ["HW", "infer"]
date = "2026-11-07"
data = ["platform-hwperf-vary"]
terms = ["CR_HWPERF_CTRL", "CR_HWPERF_COUNTER0"]
+++

**Results** (deltas of one job; the counters do not reset between the jobs of a group):

- Group 0, triangles 1, 5, 15, 42: 0x0060 3, 15, 45, 126 (0 in every other group); 0x004c 7, 35,
  105, 304; 0x0044 6, 17, 53, 149; 0x0058 58 to 59, 135, 337 to 338 and 879 to 882 over the three
  runs; 0x0064 and 0x0e8c (equal in group 0) 2498 to 3084, 3030 to 3188, 4282 to 5052 and 5906 to
  6190 over the three runs, and 44 to 46 distinct values per size over the 48 group-runs (2358 to
  3084 for one triangle): they do not repeat; 0x0050 4096 (the target's pixels) for each of the
  nine jobs; 0x0048 4096 for the two copies only (the texture fetches [infer]).
- Group 1: 0x0050 3, 15, 45, 126 (as group 0's 0x0060); 0x004c 1, 5, 19, 58. Group 3: 0x0048 21,
  70, 217, 631; 0x0050 1062, 5406, 16182, 45264 (about 1080 a triangle: the triangle's pixels,
  1062 for one).
- In all 16 groups 0x0e84 is 1 for each of the four triangle jobs and 0 for the five others; 0x0e88
  is 1 for all nine jobs (432 of 432); 0x0e90 (pixels and program length) and 0x0eb8 grow with
  the number of triangles in group 0; over all groups and runs 0x0eb4, 0x0ebc and 0x0ec0 move by
  2593 to 7521, 1376 to 1836 and 17792 to 22462 for the four triangle jobs and the 64x64 fill and
  copy, and by 2572 to 3862, 1378 to 1433 and 17800 to 18020 for the other three jobs.
- Every job moves 0x0050 of group 0 by 4096 and prints ok, the 128x32 and 256x16 fills and the
  128x32 copy included (their strides equal their widths).

**What it shows.** Counter 0x0060 of group 0 and 0x0050 of group 1 count vertices (three a
triangle, exactly at four sizes); 0x0050 of group 0 counts the pixels a job shades (as E359). The
other counters of each group (all deltas in the data) are not identified. The identified counters
(0x0060, 0x004c, 0x0044, group 1's 0x0050 and 0x004c, group 3's 0x0048 and 0x0050) repeat exactly in
three runs; 0x0058 repeats to within 3 and 0x0064 and 0x0e8c do not repeat. Q075 stays open.
