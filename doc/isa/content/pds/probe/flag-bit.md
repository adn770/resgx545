<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### Bit 9 of the `mov16`/`mov32` specials, the fetch pc, `ir0` and the two PDS pipes

*Measured on the hardware (2026-10-25; the table `probes/pds/moves.toml`, recorded runs).* What bit
9 of the special index (`.1`) does, each reading
put to the hardware in turn **[HW]**:

- **It writes a 16-bit 0, nothing else.** A `.1` `mov16` into one half of a marked temporary
  leaves the other half's mark (`pds-moves-mov-flag-write`): no extension, swap, packing or
  saturation; `tim.1` gives 0 where `tim.0` gives the counter (`0x0102c45a`), so not another
  16-bit select either.
- **No condition and no side effect.** It reads 0 after setups that set `aluz`, `alun`, the
  carry, a borrow, or `p0`-`p2` true or false (`pds-moves-mov-flag-cond`); it leaves the flags and
  the carry (`pds-moves-mov-flag-flags`); the register it reads is unchanged before and after
  (`pds-moves-mov-flag-side`).
- **Not `if0`/`if1`.** In a vertex program, a kick under "a `.1` `mov16` of `pc.l` is
  nonzero" never starts a vertex (the render hangs with nothing stored), where the plain
  `pc.0.l` kicks every vertex (`pds-vertex-programs-flag-pc`, `-plain-pc`, `-zero`); `if0` holds on
  the
  last vertex (`pds-vertex-programs-if0`).
- **`mov32` has no other select.** Its unused bits (0, 8, 23-17) and `alum`'s (23-1) change
  no read (`pds-moves-mov32-spare`, `pds-alu-alum-spare`); `mov64`'s sources 64-127 read 0
  (`pds-moves-index-mov64`).
- **Not the other pipe's live registers, in a fill.** SGX545 has two PDS pipes
  (`SGX_FEATURE_NUM_PDS_PIPES`, the `PDS0`/`PDS1` clock gates, GPL DDK), and runs two PDS
  programs at once: the same four-instruction loop runs in aggregate at 3.14 ns an instruction
  over a fill's 8 tiles and at 6.28 over a triangle's 3 vertices, which fits tiles two at a
  time and vertices one at a time (predicted time ratio 1.50, measured 1.497). With every tile
  sampling a `.1` `mov16` of `pc`, `ir0` and `tim` 50000 times while two of them ran, every
  sample was 0 (`pds-moves-mov-flag-pipes` lengthened). (Timed by hand: `CLKGATESTATUS` polled
  read-only through `/dev/mem`; `PDS0` and `PDS1` gate together,
  so the status bits do not tell the pipes apart.)

So on SGX545 the bit has no observable meaning beyond "`mov16` reads 0". It is kept apart
in the spelling (`.0`/`.1`) because it likely means more elsewhere **[infer]**: the other
pipe's registers (SGX545 is the only core in the DDK with two PDS pipes, so the bit may have
come with the second one), another core's on the MP parts, or 64-bit specials. The one-pipe
cores can test the first: if their special fields run at stride 1, as the reference
disassembler numbers them, the bit arrived with SGX545's second pipe (*Open questions*).

The other results of the round **[HW]**:

- `pc.0` is the fetch pc: the reading instruction's index plus 3 back to back and after
  `mul`s, plus 1 or 2 at some places (instructions 26-27 here, and after some `nop` gaps), and
  the same on both passes of a loop (`pds-moves-mov-pc`).
- `ir0` in a fill's secondary program is the tile position `tile_y << 10 | tile_x` for 16 x 16
  tiles: 0-3 on the top row of the 64 x 32 fill, `0x400`-`0x403` on the bottom
  (`pds-moves-mov-flag-pipes`, per pixel). The `0x402`/`0x403` of the earlier rounds was whichever
  bottom-right tile stored its readback last.
- In a vertex program, `(if1)` and `(if0)` kicks together, a kick on every vertex and a kick
  only where `if0` is false each hang the render; an `(if1)` kick alone works as `(if0)` does,
  one task of the three vertices (`probes/pds/vertex-programs.toml`).
