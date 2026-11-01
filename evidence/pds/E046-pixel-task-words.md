+++
id = "E046"
claim = "In a pixel task's DOUTU1, bit 25 set on a task with no fetch hangs the job and cleared on the copy's task changes 1410 to 1492 pixels, bit 23 flipped on a pixel task or on the end-of-tile task hangs it, bit 2 does nothing, and bit 22 does nothing on the end-of-tile task but its mask in the pixel-event program hangs when cleared; in the copy's DOUTI0, bits 4:0 pick the fetch coordinates (0 hangs, 2 to 31 give one image), bits 10:5 pick among five images (the baseline and four others), and bits 16:11 pick what the iterator writes (values 37 to 63 give the baseline); EMIT2's bits 15:8 write the same pixels at every value but 0x81"
unit = "pds"
method = "sweep tables probes/pds/data-words.toml (pds-fill, pds-copy, pds-tri, one word at a time), probes/pds/douti-fields.toml (copy-douti-bits4-0, bits10-5, bits16-11: every value of the copy's DOUTI0 field), probes/pbe/emit.toml (every value of EMIT2 source 0 bits 15:8 of the fill) and the event-bit probes of probes/pds/pixel-event.toml, on the laptop, linux fork with the debug option on: 64x32 fill and copy, 64x64 triangle; the data-words and douti tables ran twice (the second is the follow-up run)"
tiers = ["HW"]
date = "2026-11-01"
data = ["pds-data-words", "pds-douti-fields", "pbe-emit", "pds-pixel-event", "pds-data-words-followup", "pds-douti-fields-followup"]
terms = [
    "DOUTU1.WAIT_FETCH", "DOUTU1.EMITPIX_TASK", "DOUTU1.BIT2", "DOUTU1.LAST_TILE",
    "PIXEL_EVENT.LAST_TILE", "DOUTI0.ATTR_SOURCE", "DOUTI0.TEX_COORD_SOURCE", "DOUTI0.BITS10_5",
    "EMIT2.BITS15_8", "PDS_SIZE.BITS17_16",
]
+++

**What runs.** The PDS data words of the jobs are flipped through the sweep tables: `prim:1`,
`sec:1` and `bgprim:1` are the pixel tasks' DOUTU1 (4 in the fill and the triangle, 0x02000004 in
the copy, whose task issues a texture fetch), `pixev:12` is the end-of-tile task's DOUTU1
(0x00800000), `pixev:6` and `pixev:16` its events' case masks, `pixev:8` the EMIT2 word and
`prim:4` the copy's DOUTI0 (0x40012001). The three DOUTI0 tables run every value of one field of
`prim:4` (31, 63 and 63 values); the copy's source is a ramp, so a value that changes what the
task fetches changes the image. The baselines are fill 0xb60c6095080bd325, copy
0x9b1c0be484ac0d25, triangle 0x99385a04ee01c585.

**Results.**

DOUTU1.

- Bit 25 (`^=0x2000000`) set on a task with no fetch (fill, triangle, the secondary tasks): the job
  hangs. On the copy's primary task, which has it set, clearing it gives a job that ends with 1492
  of 2048 pixels wrong in the first run and 1410 in the follow-up run (the pixels the task did not
  wait for hold leftovers, so the count differs between runs); set on the copy's secondary task it
  hangs.
- Bit 23 (`^=0x800000`): flipped on any pixel task (`prim:1`, `sec:1`, `bgprim:1`) or on the
  end-of-tile task (`pixev:12`, where the job sets it) the job hangs, in both runs. Bit 24 set
  hangs everywhere. Bit 1 on a secondary task hangs.
- Bit 2 (`^=0x4`): no change on a pixel task or on the end-of-tile task.
- Bit 22 (`^=0x400000`) on `pixev:12`: no change in the three jobs. Clearing the end-of-tile
  case's mask (`pixev:16 ^=0x400000`, or the whole word to 0) hangs every job; setting bit 21
  of that mask (`^=0x200000`) writes no pixel; flipping bit 2 in the first case's mask
  (`pixev:6 ^=0x4`) hangs. The end-of-tile case's other mask (`pixev:10`) changes nothing.
- Event bits: in the probes of the end-of-tile events, the events that carry bit 2 of the second
  input register leave 512 pixels unwritten (the sentinel) at 64x64 (8 tiles) and at 128x128
  (32 tiles of 32x16), as one 32x16 tile or two 16x16 tiles; bits 3, 8, 9, 10 and 11 leave no
  pixel unwritten (12100 background and 4284 other pixels, as with no flip). In the tile-field
  probes on a 128x128 render, flipping bits 3 to 5 of the end-of-tile word gives that same
  image and bits 6 to 11 write no pixel, and likewise bits 12 to 15 against 16 to 21 for the y
  field.

DOUTI0 of the copy (value of the field, baseline value in brackets).

- Bits 4:0 (1): 0 hangs the job; every value from 2 to 31 gives one and the same image (hash
  0x88e0d03d1b42e325, 2047 of 2048 pixels differ from the ramp); 1 is the baseline.
- Bits 10:5 (0): 1, 8 and 9 give the baseline image; 2, 3, 10 and 11 give one image (2016 pixels
  differ); 4, 5, 12 and 13 another (1984); 6, 7 and every value from 14 to 31 a third (hash
  0xc1dd226ff083f325, 2047); every value from 32 to 63 the image of the fetch coordinates 2 to
  31 above (0x88e0d03d1b42e325). Bits 5 and 8 therefore do nothing, bits 6, 7 and 9 each
  change which texel is read, and bit 10 gives the image that reads one fixed texel.
- Bits 16:11 (36): 36 and 37 to 63 give the baseline image; 0 and 1 give two different images
  (hashes 0x58398aa62f55e925 and 0x5280a219dbc1d125); 2 to 31 and 35 give one image
  (0xb9d103fd6854a325, 2048 pixels differ); 32 and 33 give one image (0xd3522437a14b6325); 34
  gave a third image (0x0f39ce72f6f74325) in the first run and the image of 2 to 31 in the
  follow-up run, so its class is not settled here.

EMIT2 (fill, `pixev:8`, bits 15:8 at 0x80): 255 of the 256 values write the baseline image; 0x81
alone writes no pixel (2048 stay at the sentinel).

**Not shown.** The positions of the missing pixels were not read back except through counts,
so "last column" and "last row" are the data's reading, not a measurement. What the bits of
the fields are called follows from the hash groups only. The copy's DOUTI0 sweeps ran once each
on the copy; the follow-up run agreed in all but value 34. The visibility counters stayed at 0.
