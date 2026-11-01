+++
id = "E062"
claim = "Of the state block's MTECTL word (blk:15), bits 1:0 cull one winding (1 the triangle as drawn, 2 the mirrored one) or neither (0, 3), and bit 6 removes the triangle whatever the winding; bits 2-5 and 7 change nothing, in all 256 values of bits 7:0 on both windings"
unit = "mte"
method = "two sweeps of probes/mte/mtectl.toml on the laptop, linux fork with the debug option on: every value of blk:15 bits 7:0 (256 cases) on the 64x64 triangle as drawn (mte-mtectl-tri-mtectl-bits7-0) and on the triangle with vp3 poked to -32.0 (mte-mtectl-tri-mtectl-bits7-0-mirrored)"
tiers = ["HW"]
date = "2026-11-01"
data = ["mte-mtectl"]
terms = ["MTECTL.CULL_MODE"]
+++

**What runs.** The 64x64 triangle job holds blk:15 at 0x01555620 (bits 1:0 = 0, bit 6 = 0). Each
case xors the low byte with one value (1 to 255, plus the unpoked baseline) and runs the job on a
fresh context. The second sweep adds `blk:9=0xc2000000` (-32.0, vp3 of E061) to every case, which
draws the same 1062 pixels upside down and reverses the winding; its baseline hash is
0xe332627534738f85. All 512 jobs completed (no fault, no hang). The visibility counters, sampled in
every case, stayed at 0 throughout.

**Results.** An image is either the baseline or the empty one (0 triangle pixels, 4096 background,
hash 0xfc5ff15e0434a325, 936 pixels away from the baseline); no case gave a third image. In each
winding, 160 of the 256 values gave the empty image and 95 gave the baseline, plus the baseline run
itself. By the value's bits 1:0 and bit 6:

| bits 1:0 | bit 6 clear, triangle as drawn | bit 6 clear, mirrored | bit 6 set (both) |
|---|---|---|---|
| 0 | drawn | drawn | removed |
| 1 | removed | drawn | removed |
| 2 | drawn | removed | removed |
| 3 | drawn | drawn | removed |

Each cell holds for all 32 values of bits 7 and 5:2 of its winding (the bit 6 set column, for both
windings alike), with no exception. So bits 1:0 = 1 cull the winding of the triangle as drawn and 2
the reversed winding, 0 and 3 cull neither, and bit 6 removes the triangle whatever the winding and
whatever bits 1:0. No flip of bits 2 to 5 or 7 changes the image alone.

**What it does not show.** Which of the two windings is clockwise is not asked here; the two are
named by the sweep that draws them. Bits 31:8 of the word were not swept here.
