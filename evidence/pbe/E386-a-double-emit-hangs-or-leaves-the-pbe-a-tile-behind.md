+++
id = "E386"
claim = "Two end-of-tile emits per tile hang the job on a 64x64 target (eight tiles) whatever SIDEBAND bit 9 on either emit, in both runs of each of three variants (6 hangs); on a one-tile target a double emit with bit 9 on both or on the first only completes and leaves every later job storing the tile of the job before it (the later single-emit and blank jobs of a sequence store a tile or none by turns, a blank job (EMIT2 count 0) included) until a hang's recovery reset; the campaign's check after the one-tile table found 2164 of 4096 pixels different from the one before it; with bit 9 on the second emit only, a job one or two later hangs (one in run 1, two in run 2)"
unit = "pbe"
method = "probes/pbe/emit-twice.toml on the laptop over the cable, linux fork b5a86838ae59 with the debug option on: eot_emits.s in the end-of-tile slot with the case's emits (two emitpix1/emitpix2 pairs, the first without .end and .freep, sidebands 0x200/0x200, 0x000/0x200, 0x200/0x000), a single emit, and a blank job (EMIT2 bits 15:8 = 0); on 64x64 (sequence of 9 jobs) and 32x16 (9 jobs), each sequence twice; pix_colour.s; every pixel read back; the table ran twice and the second execution is kept, with its kernel log and the campaign's check of the image before and after it"
tiers = ["HW", "infer"]
date = "2026-11-03"
data = ["pbe-emit-twice"]
terms = ["SIDEBAND.BIT9", "PIXEL_EVENT.END_OF_TILE"]
+++
**Results.** On 64x64 every double emit hung and was recovered (6 hangs, in the kernel log with
the 2 of the one-tile table); the blank jobs after them wrote no pixel. On 32x16 (one tile),
run 1 and run 2:

| job | run 1 | run 2 |
|---|---|---|
| two emits, 0x200 and 0x200 | the tile | no pixel |
| one emit after it | the tile | the tile |
| a blank job after that | the tile | the tile |
| two emits, 0x000 and 0x200 | no pixel | the tile |
| one emit after it | hung | no pixel |
| a blank job after that | no pixel | hung |
| two emits, 0x200 and 0x000 | the tile | the tile |
| one emit after it | the tile | the tile |
| a blank job after that | the tile | the tile |

A blank job alone stores nothing (E266, and the 64x64 sequence). The campaign's check after the
one-tile table found 2164 of 4096 pixels different from its check before it (0 of 4096), the first
at (0, 0) 0xdeadbeef where 0xff203040 was expected.

**Reading [infer].** A completed double emit leaves the PBE one emit behind: the later jobs store
a tile or none by turns, as if each stored what the emit before it was given, until a reset. E239's
wrong next image may be this. This table's data show the sequence of tiles and gaps, not whose tile
each was.
