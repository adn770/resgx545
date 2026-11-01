+++
id = "E072"
claim = "Against a loaded depth of 0.5 plus n ulp (n from 0 to 512, eleven steps), depth test less, the 64x64 triangle at depth 0.5 is removed at n = 0 and drawn from n = 1 up, with 0x0418 (rd:26) at 0 and at 1: the compare is exact to the ulp and 0x0418 is not a depth precision mode in this range"
unit = "isp"
method = "the hand script depth-test.sh of probes/isp/depth-test.toml (function depth_precision): 22 jobs of the 64x64 triangle with ISP0 = 0x00400200 (depth less, written), the depth loaded through the ZLS from a scratch buffer filled with 0x3f000000 + n, rd:26 at 0 and at 1, the visibility counters sampled around each job, on the laptop with the linux fork and the debug option on; one run"
tiers = ["HW"]
date = "2026-11-01"
data = ["isp-depth-test"]
terms = ["CR_ISP_LINE_SAMPLE_POS"]
+++

**What runs.** The ZLS load is set up (`ta:7` bit 7, the ZLS base, load control 0x11700a, the load
base at the scratch buffer), so the depth in the tile starts as the buffer's value. The scratch
buffer is filled with 0x3f000000 (0.5), 0x3f000001, 0x3f000002, 4, 8, 0x10, 0x20, 0x40, 0x80, 0x100
and 0x200, once with rd:26 poked to 0 and once to 1. The triangle's depth is 0.5, and depth test
less passes where 0.5 is below the loaded value.

**Results.** All 22 jobs completed, and the scratch buffer was not changed (0 dwords) in any. With
the loaded depth at exactly 0.5 the triangle is removed (0 triangle pixels, 936 pixels away from the
CPU's image), for rd:26 = 0 and for rd:26 = 1. From 0.5 plus 1 ulp up to 0.5 plus 512 ulp (ten
values) it is drawn whole (1062 pixels, 0 wrong), again for both values of rd:26. The two series are
identical. The visibility counters stayed at 0.

**What it does not show.** Only the triangle's depth of 0.5 and loaded values just above it were
tried, so a precision change away from 0.5 or in the range of larger depths is not excluded. The
mode that 0x0418 selects at its other values is not seen: the held value of the register outside
renders is 1 and the implemented bit is bit 0 (E067), and both values of that bit give the same
compare here. One run.
