+++
id = "E070"
claim = "ISP word 1 (blk:2, 0x10f0 in the job) with bit 3 set makes the job count the triangle's 1062 pixels (0x426) into a visibility counter: bits 2:0 = 0 count into 0x0498 and bits 2:0 = 7 into 0x04b4, and with bit 3 clear nothing counts; the counters of 1, 2, 3 and 4 were not exercised, so that bits 2:0 name the counter is shown for two of its eight values"
unit = "isp"
method = "the state-block words of the sweep in probes/vdm/stream-words.toml (blk:2, 34 cases, with the counters 0x0494-0x04b4 sampled in every job), run twice (the second is the follow-up run), and the probe isp-sample-positions-0520-vistest of probes/isp/sample-positions.toml, on the laptop with the linux fork and the debug option on"
tiers = ["HW"]
date = "2026-11-01"
data = ["vdm-stream-words", "isp-sample-positions", "vdm-stream-words-followup"]
terms = [
    "ISP1.VISTEST", "ISP1.VISREG", "CR_ISP_VISIBILITY_COUNT0", "CR_ISP_VISIBILITY_COUNT1",
    "CR_ISP_VISIBILITY_COUNT2", "CR_ISP_VISIBILITY_COUNT3", "CR_ISP_VISIBILITY_COUNT4",
    "CR_ISP_VISIBILITY_COUNT7", "CR_ISP_VISIBILITY_CTRL", "ISP0.PASS_TYPE",
]
+++

**What runs.** The sweep flips each of the 32 bits of every state-block word and sets 0 and ~0. For
blk:2 that is 34 jobs. Each runs inside a sampler that reads the nine registers 0x0494 to 0x04b4
from before the job to its exit, so the first sample shows what the previous job left. The probe
renders the triangle with ISP1 at 0x10f8 (bit 3 set) instead of 0x10f0.

**Results.** All 34 blk:2 jobs draw the baseline image (1062 triangle pixels): the word changes
nothing that the image shows. Four jobs of the whole sweep (1055 cases) show a non-zero counter, in
both runs and in the same cases:

- `blk:2^=0x8` (bit 3 set, bits 2:0 = 0): the register at 0x0498 goes from 0 to 0x426 = 1062, the
  triangle's pixels, during the job.
- `blk:2=0xffffffff` (bit 3 set, bits 2:0 = 7): the register at 0x04b4 goes from 0 to 0x426.
- the jobs right after each of them (`blk:2^=0x10` and `blk:3^=0x1`) start with the same value in
  the same register and have it at 0 in the following sample: a counter keeps its value to the next
  job's start and is cleared within that job.

The probe, with ISP1 bit 3 set and bits 2:0 = 0, gives 0x0 to 0x426 at 0x0498 as well. The other 84
probes of that table, whose ISP1 has bit 3 clear, count nothing. Of the other 32 blk:2 jobs, none
counts a new value: not the flips of bits 0, 1 and 2 alone, not the value 0, not any bit above 3.

**What it does not show.** The registers 0x049c to 0x04a8 never counted, because no job set bits 2:0
to 1, 2, 3 or 4 with bit 3 (the sweep flips one bit at a time); that those bits name the counter is
shown for 0 and 7 only. The counts by pass type (ISP0 bits 27:25 with bit 3) are not tested here
(E065). The counters count in some boots only; in this boot they counted from this bit.
