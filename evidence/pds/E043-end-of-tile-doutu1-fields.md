+++
id = "E043"
claim = "In the end-of-tile task's DOUTU1 word, bits 4 to 11 and bits 13 to 21 each change what the job writes when flipped alone, bits 3, 12 and 22 and the other bits below 23 and above bit 2 change nothing, and bits 1, 23, 24, 25, the value 0 and 0xffffffff hang the job; fill, copy (two sources) and triangle agree, and a second run reproduces the cases"
unit = "pds"
method = "sweep tables probes/pds/data-words.toml (pds-fill, pds-copy, copy-every-pds, pds-tri: every bit of every data dword of the PDS programs, word pixev:12 here) on the laptop, linux fork with the debug option on: 64x32 fill, 64x32 copy with the ramp source and with the every-value source, 64x64 triangle; the fill, copy and triangle tables ran twice (the second is the follow-up run)"
tiers = ["HW"]
date = "2026-11-01"
data = ["pds-data-words", "pds-data-words-followup"]
terms = ["DOUTU1.BITS11_3", "DOUTU1.BITS21_12", "PIXEL_EVENT.END_OF_TILE", "tile"]
+++

**What runs.** The pixel-event program of each job has a data dword (`pds:pixev:12`) that the
end-of-tile task reads as its DOUTU1. The tables flip each of its 32 bits alone and also set
it to 0 and to 0xffffffff, one case, one fresh context each, after a baseline without a poke.
The jobs are a 64x32 fill (hash 0xb60c6095080bd325), a 64x32 copy (0x9b1c0be484ac0d25), the
copy over a source that holds every value (0x88c655df5891e325) and a 64x64 triangle
(0x99385a04ee01c585).

**Results.** The same bits do the same in all four jobs; the number of missing pixels scales
with the target.

| bit flipped | fill and copy (2048 pixels) | triangle (4096 pixels) |
|---|---|---|
| 1 | hang | hang |
| 2, 3, 12, 22 | baseline image | baseline image |
| 4 | 1024 pixels unwritten | 2048 |
| 5 to 11 | 2048 (all) | 4096 (all) |
| 13 | 1024 | 2048 |
| 14 | 2048 (all) | 2048 |
| 15 to 21 | 2048 (all) | 4096 (all) |
| 23, 24, 25 | hang | hang |
| value 0, value 0xffffffff | hang | hang |

Bits 0 and 26 to 31 are not listed: they gave the baseline image in every job. The unwritten
pixels keep the sentinel (0xdeadbeef) and the first one is at (0, 0) in every changed case
examined. A hang here is a job that times out; the context is lost. In the follow-up run of the
fill, copy and triangle tables the 33 cases of this word (bits, 0, 0xffffffff) gave the same
class and the same pixel count in every job. The visibility counters stayed at 0 in the fill
and copy runs; in the triangle table the counter 0x04b4 counted in seven cases of other words
(`bgprim:0`, `sec:0`, `pixev:6`), none of this one.

**Not shown.** Which pixels are missing is known only by their count and the first one, so a
column and a row cannot be told apart here. The widths of the two fields are given by E044,
and what the other bits of the word do in a task that is not the end of tile is in E046.
