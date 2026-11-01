+++
id = "E175"
claim = "Between a 64x64 and a 256x256 triangle render the debugfs register file shows four tiling registers change as the target grows (0x020c, 0x0210, 0x0214 and 0x0248, whose values are the tile counts and pixel size minus one) and 0x0208 stay unchanged; the render is exact"
unit = "ta"
method = "the register snapshot script of probes/platform/register-snapshots.toml on the laptop, linux fork with the debug option on: the debugfs register file before and after sgxfive-test tri (64x64) and tri --width 256 --height 256, as the diff; one run"
tiers = ["HW"]
date = "2026-11-01"
data = ["platform-register-snapshots"]
terms = ["CR_TE_MTILE1", "CR_TE_MTILE2", "CR_TE_SCREEN", "CR_TE_MACROTILE_STRIDE", "CR_PPP_SCREEN"]
+++

**What runs.** The script dumps the debugfs register file, runs one job and dumps it again,
keeping the diff. Three of its steps draw the triangle: `tri` (64x64), `tri -n 2` (64x64, two
renders) and `tri --width 256 --height 256`, in that order on one boot. The register file lists
only registers that read differently at some point; a register absent from a diff did not change
across that step. The 256x256 step's "before" is the state the 64x64 renders left.

**Results.** The 256x256 render is exact (17208 triangle, 48328 background pixels, 0 wrong,
diff 0 of 65536). Across it the tiling registers read:

| register | name | 64x64 (before) | 256x256 (after) |
|---|---|---|---|
| 0x020c | `CR_TE_MTILE2` | 0x01004004 | 0x02008008 |
| 0x0210 | `CR_TE_SCREEN` | 0x00003001 | 0x0000f007 |
| 0x0214 | `CR_TE_MACROTILE_STRIDE` | 0x00000010 | 0x00000020 |
| 0x0248 | `CR_PPP_SCREEN` | 0x003f003f | 0x00ff00ff |

`CR_TE_SCREEN` holds the last tile column in bits 11:0 and the last tile row in bits 23:12 (E055),
in tiles of 32x16 pixels: 1 and 3 for 64x64, 7 and 15 for 256x256, which are the width in tiles less
one and the height in tiles less one. `CR_PPP_SCREEN` holds width less one in bits 15:0 and height
less one in bits 31:16 (0x3f and 0x3f, 0xff and 0xff). `CR_TE_MTILE1` (0x0208) is not in the diff,
so it read the same before and after. The 64x64 steps list none of the four registers, and neither
do the firmware load, boot and stop steps: they kept the values of earlier 64x64 renders, so the
64x64 column is what the registers held, not a value read after a 64x64 job of this script alone.

**Not shown.** The rule that produces `CR_TE_MTILE2` and `CR_TE_MACROTILE_STRIDE` from the target
size is not stated or tested here: two sizes are two points. That the values reach the TE
registers from the render context's words, rather than being set by the firmware, is not
separated. `CR_TE_MTILE1` is shown only as unchanged. One run.
