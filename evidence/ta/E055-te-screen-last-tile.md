+++
id = "E055"
claim = "The TA command's screen word (ta:145, CR_TE_SCREEN) holds the last tile's x from bit 0 and its y from bit 12 in tiles of 32x16 pixels: clearing bit 0 leaves the right tile column of the 64x64 target unwritten (2048 pixels), clearing bit 12 the bottom row (1024), clearing bit 13 the bottom two rows (2048), and 0 leaves all but the top left tile (3584); no other bit changes anything; both fresh runs agree"
unit = "ta"
method = "kernel-poke sweep of probes/render/kernel-words.toml (tri-kernel, word ta:145, 34 values) on the laptop, linux fork with the debug option on: the 64x64 triangle job, run twice (the second is the follow-up run)"
tiers = ["HW"]
date = "2026-11-01"
data = ["render-kernel-words", "render-kernel-words-followup"]
terms = [
    "cmd_ta.te_screen", "CR_TE_SCREEN", "CR_TE_SCREEN.LAST_TILE_X", "CR_TE_SCREEN.LAST_TILE_Y",
    "tile",
]
+++

**What runs.** `kpoke` changes word 145 of the kernel-built TA command of the triangle job, which
carries the screen word, after the job is submitted: each of its 32 bits flipped alone, the value
0 and the value 0xffffffff, a fresh context each. The kernel poke applied in all 34 cases. The
unpoked job draws 1062 triangle pixels and 3034 background (hash 0x99385a04ee01c585).

**Results.** Four of the 34 cases differ from the baseline, all `job: ok` with the missing
pixels left at the sentinel (0xdeadbeef):

| value | unwritten pixels | first unwritten | hash |
|---|---|---|---|
| `^=0x1` | 2048 | x 32, y 0 | 0x09214d2af62ec245 |
| `^=0x1000` | 1024 | x 0, y 48 | 0xaa090dae7af4a745 |
| `^=0x2000` | 2048 | x 0, y 32 | 0xfe5dece95a837cc5 |
| `=0` | 3584 | x 32, y 0 | 0x927a9f8b8aa231a5 |

Clearing bit 0 leaves the right half of the target, a 32-pixel column, unwritten; bit 12 the
bottom 16 rows, bit 13 the bottom 32; 0 leaves one 32x16 tile (512 pixels written). The other
30 values (the other bits, and 0xffffffff) give the baseline image. The first two rows have
the same images as E059's high and low half of the terminate word (same hashes). The second
run of the sweep gave the same four results and the same hashes.

**Not shown.** The bits above the ones listed are not seen to do anything, since tiles beyond
the 64x64 target fall outside it, so how far each field reaches is not visible on a target this
small.
