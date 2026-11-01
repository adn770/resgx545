+++
id = "E060"
claim = "In the triangle's VDM stream, state word 1 bits 11:9 at 0 remove the triangle and 15:13 at 0, 5 or 6 hang the job (sweep and probe agree); 11:9 at 7 hangs in the sweep but renders in a probe job that sets the same word, in both runs, so that value stays unsettled; all 16 values of the vertex task's bits 31:28 render the triangle alike"
unit = "vdm"
method = "sweep tables probes/vdm/state1.toml (two sweeps and the probe jobs that set vdm word 1) and probes/vdm/vertex-tasks.toml (one sweep and three probe jobs), on the laptop, linux fork with the debug option on: the 64x64 triangle job; the state1 table ran twice (the second is the follow-up run), the vertex-task table once"
tiers = ["HW"]
date = "2026-11-01"
data = ["vdm-state1", "vdm-state1-followup", "vdm-vertex-tasks"]
terms = ["VDM_STATE1.BITS11_9", "VDM_STATE1.BITS15_13", "VDM_STATE1.BIT8", "VDM_TASK0.MAX_VERTICES"]
+++

**What runs.** The triangle job's stream has a state task (`vdm:0`, `vdm:1`) and a vertex task
(`vdm:6`, `vdm:7`). The first table sweeps every value of word `vdm:1` bits 11:9 and bits 15:13 (the
job writes 2 and 1) by XOR, and sets the same words whole in probe jobs that replace the pixel
program by a copy of o0 and read every pixel back. The second sweeps all 16 values of `vdm:6` bits
31:28 (the job writes 15) and repeats three of them in probe jobs. The baseline of every sweep draws
1062 triangle pixels and 3034 background pixels (hash 0x99385a04ee01c585). The visibility counters
stayed at 0 in all runs.

**Results.**

- Bits 11:9, sweep: 3, 1, 6, 4 and 5 give the baseline image (`^=0x200`, `0x600`, `0x800`, `0xc00`,
  `0xe00`). 0 (`^=0x400`) completes with no triangle pixel, 4096 background pixels (hash
  0xfc5ff15e0434a325; 936 pixels differ from the baseline image). 7 (`^=0xa00`) hangs: the job times
  out and the context is lost. The follow-up run gives the same class for every value.
- Bits 11:9, probes: the probe job with 0 gives a uniform background, as the sweep does. The probe
  job with the same word the sweep hangs on, bits 11:9 = 7, does not hang: it completes and draws a
  triangle like the control (the pixels it shows are the o0 leftovers of an unwritten register, 3827
  background and 269 other pixels against 3792 and 304 for the control, and 3911 and 185 against
  3640 and 456 in the follow-up run, so their count is not a fixed number). The sweep hangs and the
  probe renders in both runs, so the difference between the two jobs repeats (E413 explains it as
  an alternation).
- Bits 15:13, sweep: 0 (`^=0x2000`), 5 (`^=0x8000`) and 6 (`^=0xe000`) hang the job; 2, 3, 4 and 7
  (`^=0x4000`, `0x6000`, `0xa000`, `0xc000`) give the baseline image. The three probe jobs setting
  0, 5 and 6 hang as well, in both runs.
- Bit 8 set renders (3695 background and 401 other pixels in the probe, 3230 and 866 in the
  follow-up run, the o0 leftover again). The word with bits 11:9 = 0, 15:13 = 7 and bit 8 set
  removes the triangle in the probe, like 11:9 = 0 alone.
- `vdm:6` bits 31:28: all 16 values (the baseline plus 15 XORs, one run each) give the baseline
  image, hash 0x99385a04ee01c585. The probe jobs with 0, 1 and 7 complete and draw a triangle.

**Not shown.** The vertex-task table ran once. The hang for bits
11:9 = 7 depends on the job (sweep against probe), not on the word alone; what differs between the
two jobs is not tested. The same bits in the end-of-scene state task (`vdm:9`) are not swept here.
