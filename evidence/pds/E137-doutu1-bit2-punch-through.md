+++
id = "E137"
claim = "Clearing DOUTU1 bit 2 in the primary pixel program of the working punch-through scene (U1 0x01000000 against 0x01000004) gives the same image in each of the three cases, in both runs: 2998 background pixels, 1062 of 0x00000000 and 36 of 0x3d800000 in the always fb case and 4096 background pixels in the other two"
unit = "pds"
method = "probes isp-punch-through-pt2-punch and isp-punch-through-pt2-punch-nob2 of probes/isp/punch-through.toml on the laptop, linux fork with the debug option on: a 64x64 render of five depth-ordered triangle copies whose pixel shader (pix_pt2.s) ends its punch-through phase in the case's atst8 or nop.end, with the primary pixel program of pds_iter_pt.s (U1 0x01000004) or of pds_iter_pt_nob2.s (U1 0x01000000); two runs (the second is the follow-up run)"
tiers = ["HW"]
date = "2026-11-01"
data = ["isp-punch-through", "isp-punch-through-followup"]
terms = ["DOUTU1.BIT2", "DOUTU1.WAIT_ITER"]
+++

**What runs.** Five copies of a triangle are drawn at increasing depths. The pixel shader has a
punch-through phase, then writes; the three cases end the phase in `atst8 ... fb` ("always fb"),
`atst8 ... nfb` ("always nfb") and `nop.end`. The primary pixel program starts the task with
DOUTU1 `0x01000004` (the wait-for-iteration bit and bit 2) in `pt2-punch`, and with `0x01000000`
in `pt2-punch-nob2` (nob2: bit 2 cleared), whose program is otherwise the same: the same two
iterations, the same words.

**Results.** The rows of every case, all 64 rows and the summary line, are the same in
`pt2-punch` and `pt2-punch-nob2`, in the first run and in the follow-up run:

| case | image |
|---|---|
| always fb | 2998 pixels of 0xff203040, 1062 of 0x00000000, 36 of 0x3d800000 |
| always nfb | 4096 pixels of 0xff203040 |
| nop.end | 4096 pixels of 0xff203040 |

The ISP visibility counter 0x0498 counts from 0 to 0x43e through the first case with bit 2 set
and to 0x44a with it clear, in both runs, and does not move during the second case in either
variant. The counters count in some boots only, so this difference is recorded here and nothing
is concluded from it.

**Not shown.** The field's effect on any other scene, on a timing, or on the end-of-tile task
(that last is in E046). Two runs of one scene.
