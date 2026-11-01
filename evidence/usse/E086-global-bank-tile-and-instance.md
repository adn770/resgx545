+++
id = "E086"
claim = "In a 64x32 fill g23 is the pixel's x in its 32x16 tile, g24 its y, g25 its place in the 2x2 quad, g17 the tile quarter (2 * x bit 4 + y bit 3), g18 a per-tile number (0x16, 0x14, 0x12, 0x10 for the tiles (x bit 5, y bit 4) = (0,0), (1,0), (0,1), (1,1)) and g39 the quad's place in a 4x4 block (4 * x bit 1 + 8 * y bit 1); g21 is constant over 4x4 blocks with 27 values from 4 to 0x1f, g22 constant over quads with 12 values from 0 to 0xb, and both differ between two runs (528 and 544 pixels); g20 and g41-g43 are constants"
unit = "usse"
method = "on the laptop, linux fork with the debug option on: probes/usse/constant-banks.toml, probes gbank-pixels and gbank-write, a 64x32 fill whose pixel program writes one g register as the pixel, one case per register (64 cases), every pixel read back; two runs of the table (the second is the follow-up run)"
tiers = ["HW", "infer"]
date = "2026-11-01"
data = ["usse-constant-banks", "usse-constant-banks-followup"]
terms = ["SR.TILE_X_PIX", "SR.TILE_Y_PIX", "SR.INST_NUM", "SR.TASK_ID", "SR.SLOT_NUM"]
+++

**What runs.** 64 cases, g0 to g63, each as the pixel (`mov o0, gN`) over the 64x32 fill
(2048 pixels, four 32x16 tiles). Each register's 2048 values were fitted against the pixel's
x and y bits: the smallest set of bits that determines the value.

**Results.** First run:

| register | value at pixel (x, y) |
|---|---|
| g17 | 2 * x[4] + y[3], the 16x8 quarter of the tile |
| g18 | 0x16 for (x[5], y[4]) = (0,0), 0x14 for (1,0), 0x12 for (0,1), 0x10 for (1,1) |
| g20 | 1 |
| g21 | constant over each 4x4 block (128 blocks), 27 values from 4 to 0x1f |
| g22 | constant over each quad (512 quads), 12 values from 0 to 0xb |
| g23 | x mod 32 |
| g24 | y mod 16 |
| g25 | x[0] + 2 * y[0] |
| g39 | 4 * x[1] + 8 * y[1] |
| g41, g42, g43 | 1, 1.0 (0x3f800000), 0xff000000 |

Every other g register reads 0 in all 2048 pixels, g19 included. In the follow-up run, g21 differs
at 528 pixels and g22 at 544, and no other register differs. A `mov` to a g register is
ignored (gbank-write): after `mov gN, #0x0B0B000n` the register reads what it read before,
for g0, g20, g23 (x mod 32 over all 2048 pixels), g30, g41 and g43, with no fault.

**Reading [infer].** g23, g24 and g25 are the pixel's x and y in its tile and its instance
number in the quad, as the public Rogue special-register names say (tile x, tile y,
instance number), and g21 and g22 behave as a task id and a slot number would: constant over
a task's or a quad's instances, assigned by the scheduler, so different between runs. By
the same offset g20 would be an output-partition register, and g18 and g19 face and cluster
numbers; g19 reads 0 here.

**Not shown.** The meaning of g21 and g22 beyond their grouping, and how many tasks the run
had; g18 and g19 are not tested against a changed fill.
