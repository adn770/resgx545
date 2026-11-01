+++
id = "E263"
claim = "In the pixel-event program, on a one-tile render, the ALU, shl, abs, and mov32's ir1.0 and ir1.1 and mov16's ir1.0.l and .h all read 6, the event bits; per tile of a 128x128 render, on the slots whose slot word names the tile of their ir0, the ALU's ir1 and mov32's ir1.0 and ir1.1 read 2 on every tile but (6, 7) and (7, 7), where 6; about a third of the slots carry a slot word that is not their own; if0 and if1 never test true, the last tiles included; mr01, mr23, ir2.l and the .h of ir0, ir1 and tim read 0 on every tile, ir2.h on the one tile; tstz of ir1 tests true on the one-tile render (ir0 0) and false on every other tile read"
unit = "pds"
method = "probes/pds/task-inputs.toml (pds-task-inputs-pixev-one-tile, -pixev-tiles) on the laptop, linux fork with the debug option on: the triangle probe host with pixev_dump.s as the pixel-event program and the reads passed to the end-of-tile task with douta, eot_dump.s storing sa0-sa15 (one 32x16 tile) or eot_tile.s storing them to a slot of 16 dwords per tile (128x128, 8 x 8 tiles of 16x16, dword 15 the slot word); three repeats of each; slots whose words are colours (the race of the earlier per-tile probes) set aside"
tiers = ["HW"]
date = "2026-11-02"
data = ["pds-task-inputs"]
terms = ["PIXEL_EVENT.END_OF_TILE", "tile"]
+++

**One tile** (32x16), the three runs alike. The sixteen values passed: the ALU's `ir1` 6; `mov32`
`ir1.0` 6 and `ir1.1` 6; `mov16` of `ir1.0.l` and `.h` into one dword 6; `tstz p0, ir1` true (the
marker passed); `(if0)` and `(if1)` false; `mr01` and `mr23` 0 in all four dwords; `ir2.l` and
`ir2.h` (`movs` special 3) 0; `shl` of `ir1` by 0 6; `abs` of `ir1` 6; `tim.h` 0.

**Per tile** (128x128). A run brings back 62, 62 and 61 of the 64 slots; slots 0 and 1 never, and in
run 3 one more. The slot word (dword 15, `(64 << 16) | slot`) is not the slot's own in 19, 24 and 18
of them: mostly 2 above it (slot 2 holds `ir0` 0x002, the tile (2, 0), with word 0x400004; slot 11
holds `ir0` 0x403 with word 13); in run 3 slot 42 has word 46, and slot 43 holds tile (5, 5)'s `ir0`
with that tile's word, 45. Slot 61 holds tile (5, 7)'s `ir0` with word 63 and the values 2, 6, 6 in
runs 1 and 2, and slot 60 in run 2 tile (4, 7)'s `ir0` with word 62 and 2, 2, 6: these fit the same
offset, not a fault of tile (7, 7). The record ties the slot word to its tile only where it names
the tile of the slot's `ir0`, 43, 38 and 44 slots; on those, in the three runs: `ir0.l` the tile,
`tile_y << 10 | tile_x`; the ALU's `ir1` and `mov32`'s `ir1.0` and `ir1.1` equal, 6 on tiles (6, 7)
and (7, 7) and 2 on all others; `tstz p0, ir1` false; `(if0)`, `(if1)` false; `mr01`, `mr23`,
`ir2.l`, `ir1.h`, `ir0.h` and `tim.h` 0. Per tile only these were read: not `mov16`, `shl`, `abs` or
`ir2.h`.

So in this program `mov32`'s selector 1 is the ALU's `ir1`, as in a fill where both read 0, and
the `.h` of a special reads 0 on every tile. `tstz` of `ir1` follows `ir0` being 0 (the one tile)
or not (every tile here), not `ir1` (6 on the one tile, never 0), as E262 shows per pixel.
