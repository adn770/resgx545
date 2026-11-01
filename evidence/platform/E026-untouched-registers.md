+++
id = "E026"
claim = "Of five registers the firmware never writes (0x0810, 0x0814, 0x0818, 0x0a78 and 0x0abc), the only one that changes a job is 0x0abc: a value with bits 4:1 all clear (0, 1, 0x20 or 0x21) hangs the next fill, copy or triangle, and no other value or single-bit flip of any of the five changes a pixel; the other four, and every other value of 0x0a78 and 0x0abc, change nothing"
unit = "platform"
method = "sweeps of probes/platform/untouched-registers.toml on the laptop, linux fork with the debug option on: kreg-fill, kreg-copy and kreg-tri (every bit of the five registers flipped, and 0 and 0xffffffff, 171 cases each, 64x32 fill and copy and 64x64 triangle) and kreg-values (every one of the 64 values of bits 5:0 of 0x0a78 and of 0x0abc around the triangle, 129 cases); one run"
tiers = ["HW"]
date = "2026-11-01"
data = ["platform-untouched-registers"]
terms = ["CR_REG_0810", "CR_REG_0814", "CR_REG_0818", "CR_PDS_REG_0A78", "CR_PDS_REG_0ABC"]
+++

**What runs.** The kernel fork's register file in debugfs lets a case write one of the
registers before the job and restore it afterwards. Each case writes one register, runs the
job and compares the target to the unwritten job's (fill hash 0xb60c6095080bd325, copy
0x9b1c0be484ac0d25, triangle 0x99385a04ee01c585). The tool also reads each register back
after the write, so the bits that take a write are known.

**Results.** The readbacks are the same for all three jobs:

| register | value before | bits that took a write |
|---|---|---|
| 0x0810 | 0x00000001 | 0 |
| 0x0814 | 0x0000ffff | 16:0 |
| 0x0818 | 0x000007ff | 10:0 |
| 0x0a78 | 0x0000002c | 5:0 |
| 0x0abc | 0x0000000e | 5:0 |

- Fill, copy and triangle: 169 of the 170 poked cases of each table (the 171st is the baseline)
  leave the target identical to the unwritten job's; the one hang is 0x0abc set to 0. Every
  single-bit flip of the five registers, and 0xffffffff, change nothing. The job changed 0x0abc
  itself in that one case only (1 of 34), and none of the other four registers.
- The triangle value sweep: all 64 values of 0x0a78 bits 5:0 leave the image unchanged. For
  0x0abc, 60 values leave it unchanged and four hang the job with the context lost (the target
  has then the hash 0xe4364b426cdce325): 0x0, 0x1, 0x20 and 0x21, the values
  with bits 4:1 all clear. The initial value 0xe has bits 3:1 set, and every single-bit flip
  of it keeps at least two of bits 4:1, which is why the bit sweeps only see the value 0.
- The visibility counters did not count in any of these cases.

**Not shown.** What the register does when it does not hang; why bits 5 and 0 of 0x0abc are
free; bits above 5 of 0x0abc and 0x0a78, which do not take a write; the other registers the
kernel can write.
