+++
id = "E069"
claim = "No value of either byte of the copy's background object word bg:10 changes a one-layer copy: all 255 values of bits 7:0 and all 255 of bits 15:8 give the baseline image"
unit = "isp"
method = "two sweeps of probes/isp/background-object.toml (copy-bg10-bits7-0 and copy-bg10-bits15-8), 256 jobs each including the baseline, on the laptop with the linux fork and the debug option on; the third sweep of the table (a fill's background object) is read for bg:10 only; one run"
tiers = ["HW"]
date = "2026-11-01"
data = ["isp-background-object"]
terms = []
+++

**What runs.** The copy job builds a background object whose word 10 holds the layer description of
its one texture layer. The first sweep xors bits 7:0 of that word with each value from 1 to 255, the
second the same for bits 15:8; every case renders the copy on a fresh context. The visibility
counters were sampled in every job and stayed at 0.

**Results.** All 512 jobs completed and all 510 poked ones give the baseline image (hash
0x9b1c0be484ac0d25, the plain copy of E067), in both bytes: none of 255 values of either byte
changes a pixel or writes outside the rectangle. The fill job's own background object (the third
sweep, 579 jobs over its words bg:0 to bg:16) shows the same for bg:10: all 34 values (each bit, 0
and ~0) leave the fill's image alone, while bg:0, bg:1 and bg:2 fault or hang in 29, 4 and 28 of
their 34 cases and bg:3 to bg:16 change nothing.

**What it does not show.** What the two bytes do is not seen with one layer: a copy has a single
texture layer, so a layer count, a layer type or an order in them would not show. The claim covers
the two low bytes of the word; bits 31:16 are not swept here. One run.
