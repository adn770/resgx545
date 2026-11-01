+++
id = "E111"
claim = "In a triangle's pixel shader every instance of every quad the triangle touches runs an instruction without .skipinv in four of five runs (291 quads, 4 instances each, 1164 distinct slots, for 1062 covered pixels; one run counted 1112 slots, 278 quads); what varies is whether an uncovered instance's o0 lands, and it lands for a whole quad or not at all: 32 to 36 of the 42 partly covered quads here, 6 to 13 in the shorter shaders of E104 and E103"
unit = "usse"
method = "on the laptop, linux fork with the debug option on: probes/usse/helper-instances.toml, probe usse-helper-instances-helpers (the triangle's pixel shader pix_helpers.s without .skipinv stores a marker holding its quad position g25 to a scratch slot from g18, g23 and g24, then writes o0 green; five runs, every pixel and the scratch read back), compared with the 1062 covered pixels of E104's .skipinv run"
tiers = ["HW"]
date = "2026-11-01"
data = ["usse-helper-instances"]
terms = []
+++

**What runs.** Every instance stores `0xA0000000 | (g18 & 15) << 8 | g25` to the scratch dword
`(g18 & 15) * 512 + g24 * 32 + g23` and then writes o0 green. In a triangle `g18` does not number
the tile, but the slots did not collide in four of the five runs, so the number of distinct
slots is the number of instances that ran. The triangle covers 1062 pixels in 291 quads, 42 of
them partly covered with 102 uncovered pixels between them, and 1062 + 102 = 1164.

**Results.** Five runs, all complete and all with the 1062 covered pixels green. "Slots" are the
distinct scratch slots written and "per g25 value" the markers carrying each quad position 0 to 3.

| run | slots | per g25 value | green pixels | uncovered landed | quads landed |
|-----|-------|---------------|--------------|------------------|--------------|
| 1 | 1164 | 291 each | 1143 | 81 | 33 |
| 2 | 1112 | 278 each | 1141 | 79 | 32 |
| 3 | 1164 | 291 each | 1152 | 90 | 36 |
| 4 | 1164 | 291 each | 1146 | 84 | 34 |
| 5 | 1164 | 291 each | 1143 | 81 | 33 |

Every marker is well formed. In every run each quad that lands shows all its uncovered pixels
green (a whole quad at a time) and nothing outside the 291 quads changes. Run 2 holds 13
quads' markers fewer (52 slots); this table does not say whether those quads' markers
collided in a slot or did not run, and the covered pixels of those quads are still green.
No visibility counter counted.

**What it shows.** An instruction without `.skipinv` runs for all four instances of every quad
the triangle touches, in four runs of five exactly; with `.skipinv` only the covered ones run
(E104). What varies is the tile write of an uncovered instance, per whole quad.

**Not shown.** What decides the quads that land; E113 gives how the number follows the shader's
length. One in five runs is short of 1164 slots.
