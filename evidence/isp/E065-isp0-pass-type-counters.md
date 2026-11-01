+++
id = "E065"
claim = "ISP0 pass types 1, 2, 4, 5 and 6 draw the 64x64 triangle exactly as type 0 does and types 3 and 7 remove it (types 2, 4 and 5 also at 32x32, 128x128 and 256x256); the nine ISP visibility registers (0x0494-0x04b4), among them the low half of 0x04b4, stayed at 0 in every job of these tables and in the 956 jobs of the four ISP constant-register scenes, pass type 4 included"
unit = "isp"
method = "five sweeps of probes/isp/pass-counters.toml (CR_ISP_CTL and ISP0 flips with the counters sampled, ISP0 bits 28:25 three times each at 64x64, pass types 2, 4, 5 three times each at 32x32, 128x128 and 256x256) and the four sweeps of probes/isp/constant-registers.toml (pass types 0, 1, 4 and a depth-equal scene), on the laptop with the linux fork and the debug option on; one run of each"
tiers = ["HW"]
date = "2026-11-01"
data = ["isp-pass-counters", "isp-constant-registers"]
terms = ["ISP0.PASS_TYPE", "CR_ISP_CTL", "CR_ISP_VISIBILITY_COUNT7"]
+++

**What runs.** Every case runs inside a sampler of the nine ISP registers 0x0494 to 0x04b4, from
before the job to its exit. The first sweep flips every bit of the CR_ISP_CTL word (`cmd:12`) and of
ISP0 (`blk:1`); the second xors ISP0 bits 28:25 with each pass type 1 to 7 and bit 28 (15 values,
three runs each, two baselines); the other three repeat pass types 2, 4 and 5 three times on a
triangle scaled to 32x32, 128x128 and 256x256. The triangle covers 1062 pixels at 64x64, and 261,
4284 and 17208 at the other sizes.

**Results.** In the 64x64 repeat sweep (48 jobs), pass types 1, 2, 4, 5 and 6 give the baseline hash
in all three runs, so these types draw as type 0; types 3 and 7 give the empty image (0 triangle
pixels, 936 pixels away) in all three runs. With bit 28 added, types 0, 1, 2, 4, 5 and 6 give a
single other image (1098 triangle pixels, edge moves only, 0 wrong pixels), types 3 and 7 the empty
one. At 32x32, 128x128 and 256x256, pass types 2, 4 and 5 give the baseline image in all nine runs
of each size.

The flip sweep adds the single flips of the two words: bits 0 to 5 of CR_ISP_CTL and ~0 empty the
image; for ISP0, bits 8, 16, 17, 21 and 22 and the values 0 and ~0 do, bit 15 leaves 48 triangle
pixels, bit 18 faults the job and bit 28 gives the 1098-pixel image. 69 jobs, 51 unchanged.

Not one of the 153 sampled jobs shows a non-zero value in any of the nine registers, and the same
holds for the 956 jobs of the constant-register sweeps (E066), among them 239 jobs under pass type 4
on the same 64x64 triangle. The visibility counters count in some boots only; in this one they
counted when the test-enable bit of ISP word 1 was set (E070), and none of the jobs here sets it. So
the zeros answer for pass type alone: no pass type counted without the enable bit.

**What it does not show.** What the counters would count under a pass type is not tested: these
tables never set the test-enable bit together with a pass type. One run per table; the pass-type
outcomes repeat three times inside each run.
