+++
id = "E119"
claim = "A phase boundary is a barrier under both instance modes: in a two-phase fill, the quads that skip phase 0's 4096-iteration spin all read the marker their 4x4 block's spinning quads store at the end of phase 0 (all 2048 pixels, in each of two runs, under parallel and under perinstance), while the same code in one phase leaves 112 of the 128 skipping quads (448 pixels) reading the slot's fill value"
unit = "usse"
method = "on the laptop, linux fork with the debug option on: probes/usse/phases.toml, probes usse-phases-fillbar-parallel, -fillbar-perinstance and -fillbar-onephase (client fill, 64x32, fill_phas_bar.s and fill_one_phase.s), two runs of each in the table, the slot computed again in phase 1"
tiers = ["HW"]
date = "2026-11-01"
data = ["usse-phases"]
terms = []
+++

**What runs.** Each pixel takes the scratch slot of its 4x4 block from g18, g23 and g24 (the
fill's tile and place in the tile). In phase 0 the quads whose g39 has bit 2 or bit 3 set (the
three of a block's four quads with g39 4, 8 and 12) spin 4096 times and store `0x0BADF00D` in
the block's slot, and the quad with g39 0 goes straight on. Phase 1 computes the slot again,
loads it and writes it as the pixel. A quad that reads the slot's fill (`0xd0000000` or'ed
with the slot) did not wait for its block's spinners. The control runs the same code in one
phase. A fill's `phas` names local instruction indices (E118). The 2048 pixels are 512 quads
in 128 blocks, so 128 quads skip the spin.

**Results.** Two phases, parallel: both runs read `0x0badf00d` on 2048 of 2048 pixels. Two
phases, perinstance: the same, both runs. One phase (control): both runs read the marker on
1600 pixels and a fill value of the form `0xd000xxxx` on the other 448, that is 112 quads
of the 128 that skip the spin; the 16 other skipping quads read the marker. The baselines were
exact and no visibility counter counted.

**What it shows.** Under both modes a quad that reaches phase 1 early waits until the spinning
quads of its block have finished phase 0, at least; without the boundary it does not wait. So
parallel and perinstance are both barriers here, and the difference between them is which
instance a divergent branch follows (E112). How far the barrier reaches (a block, a task, the
whole fill) is not shown: the spinners are in the skipper's own block.

**Not shown.** Whether temporaries carry across the boundary in a fill is not tested, because
phase 1 recomputes the slot; in a triangle r5 and r6 carried in the pixel shader of E101.
