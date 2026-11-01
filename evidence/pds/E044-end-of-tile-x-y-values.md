+++
id = "E044"
claim = "Over every value of DOUTU1 bits 11:3 (x) and bits 21:12 (y) of the fill's end-of-tile task, x or y = 1 changes nothing, x or y = 2 or 3 leaves 1024 of the 2048 pixels unwritten, and every x or y from 4 up leaves the whole target unwritten"
unit = "pds"
method = "sweep tables probes/pds/end-of-tile.toml (values-doutu1-x: 512 values of bits 11:3; values-doutu1-y: 1024 values of bits 21:12) on the laptop, linux fork with the debug option on: 64x32 fill, one run of each case, fresh context each, fields set by XOR against the job's word"
tiers = ["HW"]
date = "2026-11-01"
data = ["pds-end-of-tile"]
terms = ["DOUTU1.BITS11_3", "DOUTU1.BITS21_12", "PIXEL_EVENT.END_OF_TILE"]
+++

**What runs.** The 64x32 fill's end-of-tile task reads its DOUTU1 from `pds:pixev:12`. The x table
gives bits 11:3 of that word each of their 512 values (value 0 is the baseline), the y table
gives bits 21:12 each of their 1024 values. The baseline fills all 2048 pixels (hash
0xb60c6095080bd325). The visibility counters stayed at 0.

**Results.** All 511 x cases and all 1023 y cases complete (`job: ok`). They fall into three
groups in each table.

| field value | pixels left unwritten (of 2048) | cases (x) | cases (y) |
|---|---|---|---|
| 1 | 0 (baseline image) | 1 | 1 |
| 2 and 3 | 1024 | 2 | 2 |
| 4 and up | 2048 (the whole target) | 508 | 1020 |

The unwritten pixels keep the sentinel (0xdeadbeef) and the first of them is at (0, 0). The cases
agree with E043's single-bit flips: bit 3 (x = 1) and bit 12 (y = 1) change nothing, bit 4 and
bit 13 leave 1024 pixels unwritten.

**Not shown.** The target is two 32-pixel columns or two 16-pixel rows of tiles, and 1024 pixels
is half of it, so the data reads as x and y counting from bit 4 and bit 13 in units that
the target is two of, in each direction; it does not show which half is left unwritten, nor
the unit directly (the count 1024 fits a 32-pixel column of the 32-row target and a 16-pixel row
of 64 pixels alike). How far each field reaches on a larger target is not tried here: the
triangle's single-bit flips in E043 give 2048 and 4096 pixels on the 64x64 target.
