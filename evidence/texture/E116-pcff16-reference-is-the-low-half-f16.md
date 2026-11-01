+++
id = "E116"
claim = "smp's .pcff16 takes its depth-compare reference as the f16 in the low half of the register after the coordinates, at full f16 precision and signed, where .pcf takes the whole register as an f32; the result is the same (1.0 for an f32 texture when the compare holds, else 0), over all eight cases"
unit = "texture"
method = "on the laptop, linux fork with the debug option on: probes/texture/sampler.toml, probe texture-sampler-pcff16 (client fill on dump.s: an f32 texture whose texel (0, 0) is stored as 0.5 first, point sampled with smp2d.pcf or smp2d.pcff16 under the compare mode the case's state word sets, against references that differ in their halves, by one f16 step, and in sign), eight cases, one run"
tiers = ["HW"]
date = "2026-11-01"
data = ["texture-sampler"]
terms = []
+++

**What runs.** The texel holds exactly 0.5. The reference is the register after the
coordinates. Cases set it so that its low and high halves differ, so the half that is read
shows in the result. Each case's value is uniform over the 2048 pixels.

**Results.**

| sample | reference register | compare | result |
|--------|--------------------|---------|--------|
| `.pcf` | `0x3F000000` (f32 0.5) | equal | 1.0 (control) |
| `.pcff16` | `0x3C003800` (low 0.5, high 1.0) | equal | 1.0 |
| `.pcff16` | `0x38003C00` (low 1.0, high 0.5) | equal | 0 |
| `.pcff16` | `0x00003801` (low 0.50049) | equal | 0 |
| `.pcff16` | `0x00003801` | less | 1.0 |
| `.pcff16` | `0x000037FF` (low 0.49976) | greater | 1.0 |
| `.pcff16` | `0x0000B800` (low -0.5) | greater | 1.0 |
| `.pcf` | `0x3C003800` (read as an f32) | equal | 0 |

Baselines before and after were exact.

**What it shows.** `.pcff16` reads the low half of the reference register as an f16 and
ignores the high half. One f16 step above or below 0.5 is told apart (so the compare keeps
full f16 precision), and the f16 is signed. Only the reference's format differs from `.pcf`;
the result is 1.0 when the compare holds, as for `.pcf`, and 0 otherwise.

**Not shown.** Texture formats other than f32 are not in this table. One run.
