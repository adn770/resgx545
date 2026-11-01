+++
id = "E372"
claim = "g19 reads by the instruction that reads it, the same in every pixel of the fill: 0 through mov, 0x11 as source 1 or 2 of or and and, 0x1a as a store's source (each pixel storing to its own dword and loading it back), two runs each; g18 reads the same through mov, or and a store (0x10, 0x12, 0x14 and 0x16, 512 pixels each), g23 through mov and a store (0 to 3, 64 pixels each), and g17 (0 to 3) and g20 (1) were read through a store only; g24 through mov only (0 to 3, 128 pixels each)"
unit = "usse"
method = "on the laptop, linux fork b5a86838ae59 with the debug option on: probes/usse/g19.toml: value.s with every pixel read back (mov r10, g19; or and and with g19 as source 1 and as source 2 against 0 and ~0; g18, g23, g24 alike), and store_pixel.s (each instance stores the register to scratch dword g18 x 512 + g24 x 32 + g23 and loads it back as its pixel) for g17, g18, g19, g20 and g23; two runs"
tiers = ["HW", "infer"]
date = "2026-11-03"
data = ["usse-g19"]
terms = []
+++

**Results.**

| read | g19 | g18 | g17, g20, g23 |
|---|---|---|---|
| `mov r10, gN` | 0 on 2048 pixels | 0x10, 0x12, 0x14, 0x16, 512 pixels each | g23 0-3, 64 pixels each; g17, g20 not read; g24 0-3, 128 each |
| `or`/`and`, either source | 0x11 on 2048 | `or` as through `mov` (`and` not run) | not read |
| store's source, per pixel | 0x1a on 2048 | as through `mov` | g17 0-3, 512 each; g20 1; g23 as through `mov` |

Both runs agree pixel for pixel. So the three readings of E085/E086 are not one instance's: every
pixel reads 0x1a as a store's source and 0 through a `mov`.

**Reading [infer].** g19's value depends on the unit that executes the read (the moves, the
bitwise group, the store path), not on the instance; it is not a per-instance register of the
fill like g17, g18, g23 and g24.

**Not shown.** g17 and g20 through `mov` or `or`, `and` with g18; g19 through other instruction groups (float, integer multiply-add, tests) and in
other task types; whether it changes with the fill's size or place.
