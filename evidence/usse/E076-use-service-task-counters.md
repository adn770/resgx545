+++
id = "E076"
claim = "The USEn_SERV_PIXEL and USEn_SERV_VERTEX registers (n = 0-3) read 0x00010000 after a firmware load or stop and count tasks in bits 15:0 with bit 16 set: pixel tasks on all four pipes (a 64x64 triangle 85, 86, 85, 85; the debugfs fill 130 and copy 120 and a client fill 40 on every pipe), vertex tasks on pipe 0 only (3 for a triangle)"
unit = "usse"
method = "on the laptop, linux fork with the debug option on: the register snapshot script (probes/platform/register-snapshots.toml), a dump of the debugfs register file before and after each of 14 job types, differences kept"
tiers = ["HW"]
date = "2026-11-01"
data = ["platform-register-snapshots"]
terms = ["CR_USE0_SERV_PIXEL", "CR_USE0_SERV_VERTEX", "CR_USE1_SERV_PIXEL", "CR_USE1_SERV_VERTEX", "CR_USE2_SERV_PIXEL", "CR_USE2_SERV_PIXEL.EMPTY", "CR_USE2_SERV_PIXEL.TASK_COUNT", "CR_USE2_SERV_VERTEX", "CR_USE2_SERV_VERTEX.EMPTY", "CR_USE2_SERV_VERTEX.TASK_COUNT", "CR_USE3_SERV_PIXEL", "CR_USE3_SERV_PIXEL.EMPTY", "CR_USE3_SERV_PIXEL.TASK_COUNT", "CR_USE3_SERV_VERTEX", "CR_USE3_SERV_VERTEX.EMPTY", "CR_USE3_SERV_VERTEX.TASK_COUNT", "CR_USE0_SERV_EVENT"]
+++

**What runs.** The script dumps the debugfs register file, runs one job, dumps it again and keeps
the difference, for the firmware load, boot, a miscinfo query, a power idle, the debugfs transfer
fill and copy, a 64x64 triangle, two triangles in a row, a 256x256 triangle, a client fill, eight
render contexts, a stop, a second boot and a reread. The pixel registers are at 0x0b0c, 0x0b18,
0x0b88 and 0x0b94 (pipes 0 to 3), the vertex registers at 0x0b10, 0x0b1c, 0x0b8c and 0x0b98.

**Results.** After the load, and again after the stop, the pixel and vertex registers that change
read 0x00010000: count 0, bit 16 set. Every later value has bit 16 set and the task count in bits
15:0. The counts per job, as differences of bits 15:0:

| job | pipe 0 | pipe 1 | pipe 2 | pipe 3 | vertex, pipe 0 |
|---|---|---|---|---|---|
| debugfs fill | 130 | 130 | 130 | 130 | 0 |
| debugfs copy | 120 | 120 | 120 | 120 | 0 |
| triangle 64x64 | 85 | 86 | 85 | 85 | 3 |
| two triangles 64x64 | 170 | 172 | 170 | 170 | 6 |
| triangle 256x256 | 1302 | 1302 | 1300 | 1300 | 3 |
| client fill 64x32 | 40 | 40 | 40 | 40 | 0 |

The vertex registers of pipes 1 to 3 (0x0b1c, 0x0b8c, 0x0b98) appear in no difference. The transfer
jobs and the fill count as pixel tasks, so the pixel registers count transfer work too. The two
triangles of the pair add the same counts as one triangle each, so the counts repeat from job to job
on a pipe (the second pipe runs one or two tasks more than the others in the 64x64 jobs). Every
triangle of the three sizes drew its 1062 or 17208 covered pixels exactly.

**Not shown.** The registers wrap at 16 bits, so they bound only small jobs. The data does not say
which task of a job ran on which pipe, or why pipe 1 runs one or two more.
