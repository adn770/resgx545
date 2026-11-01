+++
id = "E138"
claim = "DOUTU1 bit 2 changes no image in any of our runs, set or clear, on a pixel task, the end-of-tile task or the punch-through scene, so we read it as a scheduling hint of the task; this reading is an inference and no run measured a scheduling effect"
unit = "pds"
method = "inference from our measurements: the one-word flips of pds-data-words (prim:1, sec:1, bgprim:1 and pixev:12 with ^=0x4) and the punch-through scene with the bit cleared, both recorded in E046 and E137; the reading is ours"
tiers = ["infer"]
date = "2026-11-01"
data = [
    "pds-data-words", "pds-data-words-followup", "isp-punch-through", "isp-punch-through-followup",
]
terms = ["DOUTU1.BIT2"]
+++

**What supports it.** Bit 2 is set (value 4) in the second USSE word of the pixel tasks of the
fill, the copy and the triangle jobs. E046 flips it on a pixel task and on the end-of-tile task:
no change, in two runs. E137 clears it in the primary program of the working punch-through scene:
the same three images, in two runs. We found no case in which the bit matters, and no public
source in the tree that describes a flag at this position, so the reading is ours: a bit that a
task may carry for the scheduler without changing what the task writes.

**What does not support it.** Nothing measured the scheduling. The runs compare images, and the
timing of a render with the bit set or clear was not taken. E137 also records the ISP visibility
counter 0x0498 reaching 0x43e through the first case with the bit set and 0x44a with it clear, in
both runs; the counters count in some boots only, so nothing is concluded from it, but it is a
difference the images do not show. The reading also fits a bit that is
ignored on this core, or one that acts only in a condition our jobs never reach.

**Not shown.** What would confirm it: a difference in render time with the bit set and clear, under
a load with many concurrent tasks. No such run exists.
