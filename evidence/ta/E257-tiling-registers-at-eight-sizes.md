+++
id = "E257"
claim = "At eight target sizes from 64x64 to 4096x4096, 1366x768 among them, the triangle draws exact and the tiling registers 0x0208, 0x020c, 0x0210, 0x0214 and 0x0248 read after the TA exactly the values the library's macrotile rule gives, which the TA command loads: the hardware accepts the rule's encoding; 0x0208 changes with the size from 512x512 on, and its bit 31 is set from 1024x768 on, where the rule chooses four macrotiles across"
unit = "ta"
method = "probes/platform/register-timelines.toml on the laptop, linux fork with the debug option on: regtimeline samples 206 registers (every glossary register and the 13 with no row, less the four that move on their own and those the kernel's register file never reads) from 50 ms before each job to its end, printing each change: the debugfs fills and copies, the 64x64 triangle, two renders in one context, two render contexts and the 1024x768 triangle in a 0x30-page parameter buffer, twice each, then the triangle at 96x64, 256x256, 512x512, 1024x768, 1366x768, 2048x2048 and 4096x4096; one run"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["platform-register-timelines"]
terms = [
    "CR_TE_MTILE1", "CR_TE_MTILE2", "CR_TE_SCREEN", "CR_TE_MACROTILE_STRIDE", "CR_PPP_SCREEN",
    "cmd_ta.te_mtile1", "cmd_ta.te_mtile2", "cmd_ta.te_screen", "cmd_ta.te_macrotile_stride",
    "tile",
]
+++

**What runs.** The register timelines of the snapshot table, the triangle at each size; the values
are the registers' last sample, after the job. Every image is exact (`diff: 0`).

| target | `0x0208` | `0x020c` | `0x0210` | `0x0214` | `0x0248` | library rule |
|---|---|---|---|---|---|---|
| 64x64 | `01004004` | `01004004` | `00003001` | `00000010` | `003f003f` | same |
| 96x64 | `01004004` | `01004004` | `00003002` | `00000010` | `003f005f` | same |
| 256x256 | `01004004` | `02008008` | `0000f007` | `00000020` | `00ff00ff` | same |
| 512x512 | `02008008` | `04010010` | `0001f00f` | `00000080` | `01ff01ff` | same |
| 1024x768 | `82010018` | `03018024` | `0002f01f` | `00000060` | `02ff03ff` | same |
| 1366x768 | `83018024` | `03018024` | `0002f02a` | `00000090` | `02ff0555` | same |
| 2048x2048 | `84020030` | `08040060` | `0007f03f` | `00000200` | `07ff07ff` | same |
| 4096x4096 | `88040060` | `100800c0` | `000ff07f` | `00000800` | `0fff0fff` | same |

"Library rule" is `sgxfive_tiling` of libsgxfive: 32x16-pixel tiles; four macrotiles across and down
from 640x480 pixels on, else two; a macrotile spans the tiles over that count rounded up to a
multiple of 4; the stride is 16 per 4x4-tile block of a macrotile. Each value above is the one the
rule gives for that size.

**Reading.** This is a comparison with the library's rule, not a measurement of what the fields
mean: the TA command loads these words from what our library computes, so the registers reading
the rule's values shows only that the hardware accepts the rule's encoding and draws each size
exact with it. Read through the rule and the fields of E247 [infer]: `CR_TE_SCREEN` holds the last
tile column (7:0) and row (20:12), 42 and 47 at 1366x768, whose width is not a multiple of 32; each
macrotile word holds the macrotile's size in tiles in its top field (29:22 or 30:22) and the second
and third boundaries below, the three fields equal with two macrotiles; bit 31 of 0x0208 is set
exactly where the rule chooses four macrotiles across. E175 saw 0x0208 unchanged between 64x64 and
256x256, as here; it changes from 512x512 on, where the rule's macrotile grows past four tiles.

**Not shown.** Whether the tiling engine reads 0x0208 at all, or takes the layout from the other
words: the TA kick loads all of them from the TA command, so changing one needs the TA command word
poked, not the register.
