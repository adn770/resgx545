<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### The pixel-event program's inputs and its attribute room

*Measured on the hardware (2026-10-27; the triangle probes of
`probes/pds/pixel-event.toml`, recorded runs).* The probe replaces the
triangle's pixel-event program with `pixev_dump.s` and passes what it reads to the end-of-tile
task with `douta` **[HW]**:

- **The attribute room.** `douta` reaches the task's `sa0`-`sa15` only when bits 2:0 of the
  render's pixel-event info word (`EVENT_PIXEL_PDS_INFO`, `cmd:20` of our render command, 1 in
  every closed capture) are zero: with any of them set (1, 2, 4, 0x101, 0x102, 0x104) the task
  reads the tile's colours there, with 0, 0x80, 0x100-0x8000 or 0x10000 it reads the values
  passed on (a one-tile render, poked through the kernel's `rd:25`). On the 128x128 render
  bits 3, 4 and 5 stop it as well (0x8, 0x10, 0x20: no tile's values arrive), and every value
  from 0x40 up with bits 5:0 clear delivers as 0 does: the gate is bits 5:0. With them set
  (1, on a one-tile render) no `douta` value is in `sa0`-`sa127`: they hold the pixels of the
  task's 16 x 8 block, in 2 x 2 quads taken in raster order across it, `sa(4q + i)` pixel `i`
  of quad `q` (top left, top right, bottom left, bottom right). All 128 match that order and no
  other tried (raster, column, 4 x 4 or 8 x 8 blocks, quads across the 32-pixel target). They
  are the tile buffer itself: an end-of-tile task that writes `sa0`-`sa3` before its emit
  changes pixels (0, 0), (1, 0), (0, 1), (1, 1) of every 16 x 8 block of the target, at (0, 0),
  (16, 0), (0, 8), (16, 8), with either info value. With bits 5:0 clear, `douta` writes into
  that buffer: the markers come out as pixels, `sa4`-`sa15` at x 2-7 of rows 0-1. So the
  gate picks where `douta` lands, the tile buffer or elsewhere; a 16 x 16 tile's event runs the
  task once for each 16 x 8 half. The probes write 0.
- **The primary attributes** (the `pa-dump` runs: the 16-marker program, the
  end-of-tile task storing `pa0`-`pa15` instead): with info 0 they hold the 16 markers in
  order, as `sa` does; with info 1, `pa0`-`pa3` hold markers 12-15 (the last four attributes)
  and `pa4` on other values; with info 4 nothing recognisable; with 0x10 the background
  colour throughout. So the info word moves where the passed attributes and the tile sit
  against `pa` and `sa`; no one offset fits the four readings: open.
- **A whole tile pass** (the `sa-tile` runs): an end-of-tile task that writes
  `0xa0000000 | k` into every `sak`, `k` 0-127, before its emit turns all 512 pixels of a
  32x16 target into exactly the values that order predicts. On larger targets it does not
  hold: on 64x64 (info 1) only the 32x16 tiles (0, 0) and (0, 2) come out written, the
  other six as the triangle renders them, the same in three runs (128x128: 3968 of 16384
  pixels); with info 0 the pixel-event program's markers land in the other tiles. Where those
  tiles' `sa` writes go is open.
  On a 128x128 render the same layout races: some tiles' tasks get colours in `sa15` (the
  fault address was the scratch base plus `0xff20 × 0x3040`), a different set each run. The
  per-tile store (`eot_tile.s`) now clamps its slot word to the buffer, so such a tile only
  loses its record: 34 or 35 of the 64 tiles come back per run, 41 in three runs.
- **Per tile** (`pds-pixel-event-pixev-grid16`, 128x128, 8 x 8 tiles of 16 x 16): on every tile read
  back
  `ir0` is `tile_y << 10 | tile_x`, as `ir0.l` and through the ALU, and `ir1` is 2 (the end of
  the tile), except on tiles (6, 7) and (7, 7), where it is 6: the last tile's bit comes with
  the last two 16 x 16 tiles, the bottom-right 32 x 16 pixels.
- **`ir0`, `ir1`, `tim` on a one-tile render**, twice alike: `ir0` is 0 (tile 0, 0) as `ir0.l`,
  through the ALU and through `mov32` `.0` and `.1`; `ir1` is 6 as `ir1.l` and through the ALU:
  bit 1, the end of the tile, and bit 2, the render's last tile (*Machine model*); `.h` reads 0
  for all three. `tim` reads `0x0104xxxx`, `ENABLE` and a count that falls through the program:
  the ALU's read first, a `movs` nine lower, a later `movs` another 0x74 lower. `mov32 pc.0`
  reads 0x1a.
- **Past bit 16** (`pds-pixel-event-pixev-tall`, 32x4096, two 16 x 16 tiles a row): of the 47
  records
  that come back whole (`ir1` 2 by both paths, `.h` 0), the 29 whose `ir0` passes bit 15
  (tile rows 66-127, `ir0` up to `0x1fc01`) read the same word as `ir0.l`, through the ALU and
  through `mov32` `.0` and `.1`: `.l` passes all of `ir0`. Rows from 128 share their slots
  with lower ones in that probe's layout, so none is read.
- **The plain task of `pds-pixel-event-readback`** (started with U1 0, no PBE) passes the 16
  markers, but
  every second run of it hangs: something it leaves is cleared only by the reset after a hang.
  Ending it with `ptoff.end` instead of `nop.end` changes nothing (hang, ok, hang, ok). It
  ends without the `.freep` emit that the end-of-tile tasks free their tile buffer with
  [infer: what it holds on to].
