+++
id = "E403"
claim = "With 0x0810, 0x0814 and 0x0818 each narrowed (down to 0), no job's median time falls outside 0.81 to 1.21 of the init values' (inside the spread of the init runs), from a 64x32 fill to a 2048x2048 triangle, eight back-to-back renders and pixel loops of 9.6 to 62 ms, and no job faults or hangs (64 chained transfers all report ok; the tool prints no time for them); every output holds but a triangle with 0x0818 = 0x3ff (E404); one reset restored all three to their init values"
unit = "platform"
method = "probes/platform/register-limits.toml (register-limits.sh): 15 cases of the three registers written through the debug group's kreg, each run with 12 workloads, three times (542 runs with the post-reset ones), one process of the tool a run, the job time its own line (job time: N us, tri WxH #1: N us); probes/platform/init-register-copy.toml and init-register-tri.toml: the 147-case value sweeps of E122 around a 64x32 copy and a 64x64 triangle; on the laptop over the direct cable, linux fork f1fad0ed9d0e with the debug option on"
tiers = ["HW"]
date = "2026-11-07"
data = ["platform-register-limits", "platform-init-register-copy", "platform-init-register-tri"]
terms = []
+++

**Cases.** The init values; 0x0814 at 0x1ffff, 0x7fff, 0x3ff, 0xff, 0xf, 0x1 and 0; 0x0818
at 0x3ff, 0xff, 0xf, 0x1 and 0; 0x0810 at 0; all three at 0. Each case ran, with its registers
read back after the write and after the jobs, a fill, a copy and a triangle at their default
targets (64x32, 64x32, 64x64), a fill and a copy at 1024x1024, the triangle at 1024x1024 (1024
tiles of 32x32 [infer]) and 2048x2048 (4096), eight renders at 256x256 in one context, 64 chained
dummy transfers and a fill whose pixel program loops 1000, 400000 and 1250000 times.

**Times.** For every workload with a job time, the median of every case is within 0.81 to 1.21 of
the init values' median (fill 64x32 0.97 to 1.21, whose job takes 0.57 ms; copy 64x32 0.81 to 1.01;
the other workloads 0.95 to 1.04): the registers do not change how long these jobs take. The
64 chained transfers print no job time (45 runs, wall time 231 to 256 ms, each reporting
"64 jobs ok"), so nothing is shown of their time. The jobs'
times under the init values (min, median, max over three runs): fill 64x32 538, 567, 786 us; copy
64x32 570, 665, 2826 us; triangle 64x64 5.9, 6.1, 6.4 ms; fill 1024x1024 2.2, 2.5, 2.6 ms; copy
1024x1024 5.1, 5.2, 5.5 ms; triangle 1024x1024 1144, 1146, 1156 ms; triangle 2048x2048 4581,
4587, 4588 ms; eight renders at 256x256 73.3, 74.8, 74.9 ms the first; loops 9.8, 61.7 and 44.1
ms: the loops' times do not scale with their counts (1000, 400000 and 1250000 iterations; the
largest count is the middle time), so a longer loop is not a longer job, whatever the program
stops on [infer]. The 147
cases of each of the copy and triangle value sweeps (the values of E122, 0 to 0x80000000 and
the init value's low bits flipped) all end unchanged, 64x32 copy and 64x64 triangle, with times
in 0.56 to 4.4 ms and 6.2 to 10.6 ms around medians of 0.79 and 7.8 ms; the two copies over twice
the median (4447 and 2427 us) are single runs [infer: noise of a sub-millisecond job].

**Faults.** None: 533 runs end with exit status 0 and the nine others, with 1, are the wrong
outputs below; no run's driver log has a line naming a fault, hang or recovery (its one reset
line is the script's own reset, below); and the registers read back as written after every job
(no job changes them).

**Outputs.** Every run's output equals the init values' (target hash and 0 wrong pixels) but the
nine runs of 0x0818 = 0x3ff with the triangle at 1024x1024, 2048x2048 and eight renders at
256x256 (three each): the job reports ok and draws wrong pixels (E404).

**Reset.** One reset, with 0x0810 = 0, 0x0814 = 0x3ff and 0x0818 = 0xff before it: debugfs
reset gives 0x1, 0xffff and 0x7ff, so the init script runs again at a reset (one reset, not
repeated). The fill and the triangle after it hold.

This shows no timing, fault or output dependence of 0x0810, 0x0814 or any value of 0x0818 but
those of E404 on the loads tried: the largest, 4096 tiles, 62 ms of pixel loop and 64 queued
transfers, reached no limit. It does not exclude a limit at loads the tool cannot build.
