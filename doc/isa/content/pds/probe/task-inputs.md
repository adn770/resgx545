<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### The inputs of the primary pixel and pixel-event programs

*Measured on the hardware (2026-11-02; `probes/pds/task-inputs.toml`, recorded runs).*

- **The primary pixel program** (E262, E264) **[HW]**. `pds_iter_if.s` starts the triangle's shader
  with the iteration wait and then issues one iteration: of the coordinate set, or of the pixel's
  `x + 0.5` where the case's condition held, so every pixel shows the condition in the program that
  served it. On a 64x64 and a 128x128 triangle: `if0` and `if1` hold nowhere; `ir0` is 0 only on
  tile (0, 0); the ALU's `ir1`, `mov32`'s `ir1.0`, `mr01` and `mr23` read 0 on every pixel; `tim`
  and `pc.0` are never 0; `tstz` of `ir1` is true exactly where `ir0` is 0. Bit by bit, on the 64x64
  triangle only: `ir0` is the 16 x 16 tile's position `tile_y << 10 | tile_x` (bits 0, 1, 10 and 11
  follow the tile, all others are clear), and the ALU's `ir1` has bits 0-11 clear. `movs` to `mr`,
  `slc`, `douts` and `ir0` leave the image as the control's, `mr01` reading 0 and `ir0` the tile
  after them; `movs doutc` faults the job (BIF status 0xd0400, the address 0x0401f030).
- **The pixel-event program** (E263) **[HW]**. `pixev_dump.s` with the reads passed to the
  end-of-tile task, three runs each. On a one-tile render `ir1` reads 6 through the ALU, `shl`,
  `abs`, `mov32` (`ir1.0` and `ir1.1`) and `mov16`; `tstz` of `ir1` is true (`ir0` is 0); `if0`,
  `if1`, `mr01`, `mr23`, `ir2.l`, `ir2.h` and `tim.h` read 0 or false. Per tile of a 128x128 render
  (61 or 62 of 64 slots a run come back; slots 0 and 1 never): 18 to 24 slots a run hold a slot word
  that is not their own, mostly 2 above it, among them slot 61 (tile (5, 7)'s `ir0`, word 63) and
  slot 60 in one run, whose `ir1` reads disagree. On the 38 to 44 slots whose word names the tile of
  their `ir0`: `ir0.l` the tile, `ir1` by the ALU and by `mov32` (`ir1.0`, `ir1.1`) alike, 2, or 6
  on tiles (6, 7) and (7, 7); `if0`, `if1` false and `mr01`, `mr23`, `ir2.l`, `.h` of `ir0`, `ir1`
  and `tim` 0. Per tile only those were read.
