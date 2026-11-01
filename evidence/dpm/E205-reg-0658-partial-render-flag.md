+++
id = "E205"
claim = "CR_DPM_PARTIAL_RENDER (0x0658) is 1 while a partial render runs and 0 otherwise; in our data the firmware sets and clears it, so it reads as a status the EDM keeps, and that it is also an enable is not shown"
unit = "dpm"
method = "comparison of the register timeline of E204 with the firmware writes of E199 (our disassembly of the firmware, for interoperability; facts only, no code); the reading is ours, no public source is cited (the tree holds no citation record for one); one run of two sweeps on the laptop with the linux fork and the debug option on"
tiers = ["HW", "RE", "infer"]
date = "2026-11-01"
data = ["dpm-parameter-buffer", "firmware-edm-dataflow"]
terms = ["CR_DPM_PARTIAL_RENDER"]
+++

**The question.** A register that is 1 during partial renders can be an enable that a driver
programs or a status the firmware keeps. The reading below is ours: no citation record of this tree
covers a partial-render register of another GPU.

**What the data show.** The firmware writes 0x0658 itself: 1 in the partial-render routine, 0 in the
resume and in every 3D kick, and nowhere else (E199). The register reads 1 in 24 timelines of jobs
that overflow their parameter buffer, in one stretch for each partial render the job made (1 at
1024x768, 1 to 10 at 4096x4096), and stays 0 in the 16 timelines that do not overflow (E204). The
register is therefore 1 while a partial render runs, and 0 otherwise; it held no other value in any
sample.

**Reading [infer].** It is the partial-render flag, set and cleared by the EDM around a partial
render. That it is also an enable, in the sense that setting it would start or allow a partial
render, is not tested: no run here sets it, and the firmware's own write of 1 is made inside the
partial-render routine.

**Not shown.** Whether a host write of 1 does anything; the effect of the flag inside the DPM. One
run of each table.
