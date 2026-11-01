+++
id = "E388"
claim = "Bits 17, 18 and 19 of the pixel-event program's data dword 2 add stray writes of 0x00000002 (or 0x00000006) at the first pixel of 16x4 blocks: on the copy bit 17 changes 2-3 pixels in all 10 runs, bit 19 1-2 in 7 of 10, bit 18 2 in 1 of 10 (none in 9); on the fill bit 18 changes 3-5 pixels in 5 of 5; on the triangle bit 18 6-8 in 5 of 5 and bit 17 1-4 in 4 of 5 (the fifth faulted); bit 16 faults every triangle job and leaves the copy unchanged in 10 of 10"
unit = "pds"
method = "probes/pds/pixel-event-word2.toml (three sweeps, tools/sweep) on the laptop over the cable, linux fork b5a86838ae59 with the debug option on: pds:pixev:2 with bits 16, 17, 18 and 19 flipped one at a time, ten times each on the 64x32 copy, five on the fill and the triangle; each case's image against its host's baseline"
tiers = ["HW"]
date = "2026-11-03"
data = ["pds-pixel-event-word2"]
terms = []
+++
**Results.** Changed pixels per run (u: unchanged):

| host | bit 16 | bit 17 | bit 18 | bit 19 |
|---|---|---|---|---|
| copy (10) | u x10 | 3,3,3,3,2,2,2,3,3,3 | 2 once, u x9 | 1,1,1,u,u,u,1,2,1,u |
| fill (5) | u x5 | u x5 | 5,5,3,4,5 | u x5 |
| triangle (5) | fault x5 | 4,2,1,fault,3 | 8,7,7,6,6 | u x5 |

The copy's changed pixels are 0x00000002 at (48, 0), (16, 0), (0, 8), (0, 12), (16, 12) and
0x00000006 at (32, 4): the first pixel of a 16x4 block, a different one from run to run. E043/E046
saw bit 16 fault the copy in both of their runs; here it never did.
