+++
id = "E262"
claim = "In the primary pixel program of a 64x64 and a 128x128 triangle, per pixel: if0 and if1 never test true; ir0 is 0 only on tile (0, 0); the ALU's ir1, mov32's ir1.0, mr01 and mr23 read 0; tim and pc.0 are never 0; tstz of the source the decoder names ir1 tests true exactly where ir0 is 0; bit by bit on the 64x64 triangle, ir0 is the 16x16 tile position tile_y << 10 | tile_x (bits 0, 1, 10, 11 follow the tile, bits 2-9 and 12-15 are clear) and the ALU's ir1 has bits 0-11 clear"
unit = "pds"
method = "probes/pds/task-inputs.toml (pds-task-inputs-primary-flags-64, -flags-128, -primary-bits) on the laptop, linux fork with the debug option on: the triangle probe host with pds_iter_if.s as the primary pixel program (slot pixpds), pix_pa0.s as the shader and vtx_coords.s giving the vertices a coordinate set; the program starts the shader with U1 0x1000004 (the iteration wait), then issues one iteration with DOUTI0 bit 29: 0x20000800 (source 1, the coordinate set) by default, 0x20000000 (source 0, x + 0.5) where the case's condition held (a predicated mov32 of the word); every pixel read back and classified as x + 0.5 or not; one run"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["pds-task-inputs"]
terms = ["DOUTI0.ATTR_SOURCE", "DOUTU1.WAIT_ITER", "tile"]
+++

**Controls.** With no condition every one of the 1062 triangle pixels (4284 at 128x128) holds a
coordinate-set value, never x + 0.5; with the source-0 word unconditional every one holds its x +
0.5. The background (3034 and 12100 pixels) is untouched in every case.

**The conditions**, pixels where it held, 64x64 then 128x128:

| condition | 64x64 (1062) | 128x128 (4284) |
|---|---|---|
| `(if0)` | 0 | 0 |
| `(if1)` | 0 | 0 |
| `tstz p0, ir0` | 48: all of tile (0, 0), no other | 0 (the triangle misses tile (0, 0)) |
| `tstz p0, ir1` | 48: all of tile (0, 0), no other | 0 |
| `or` of the ALU's `ir1` with 0, `tstz` | 1062 | 4284 |
| `mov32` of `ir1.0`, `tstz` | 1062 | 4284 |
| `or` of `tim` with 0, `tstz` | 0 | 0 |
| `mov64` of `mr01`, low and high dword, `tstz` | 1062 each | 4284 each |
| `mov64` of `mr23`, low and high dword, `tstz` | 1062 each | 4284 each |
| `mov32` of `pc.0`, `tstz` | 0 | 0 |

**The bits** (64x64): `and` of `ir0` or the ALU's `ir1` with one bit, `tstz` of the result. `ir0`
bit 0 is clear on all pixels of tile columns 0 and 2 and set on columns 1 and 3; bit 1 clear on
columns 0 and 1; bit 10 clear on tile rows 0 and 2; bit 11 clear on rows 0 and 1; bits 2-9 and
12-15 clear on all 1062. The ALU's `ir1` has bits 0-11 clear on all 1062. Every tile the
triangle touches is uniform in each bit: ir0 is `tile_y << 10 | tile_x` for 16 x 16 tiles, as in
a fill's secondary program and the pixel-event program.

So `tstz` of the field the decoder spells `ir1` (source 65) tests zero exactly where `ir0` is 0: it
held on the 48 pixels of tile (0, 0) only, as `tstz` of `ir0`, while the ALU's `ir1` is 0
everywhere. Only zero-ness was measured, and only by `tstz`.
[infer] Source 65 reads `ir0`. That fits this run, E263, and the earlier fill (`tstz` of `ir1`
tested nonzero where the ALU's `ir1` reads 0, on one tile whose `ir0` is not 0).
