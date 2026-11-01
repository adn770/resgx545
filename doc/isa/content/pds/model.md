<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
## Machine model

### Data registers

The data segment is loaded into two banks, `ds0` and `ds1`, of 64 dwords each **[RE]**. It is
stored **in rows of four dwords, two per bank**: row `r` holds `ds0[2r]`, `ds0[2r+1]`,
`ds1[2r]`, `ds1[2r+1]` **[HW]** (*Hardware probes*). So data dwords 0-3 are `ds0[0]`,
`ds0[1]`, `ds1[0]`, `ds1[1]`, dwords 4-7 are `ds0[2]`, `ds0[3]`, `ds1[2]`, `ds1[3]`, and so on;
every one of our
PDS programs documents its data segment this way, and the hardware reads them so.

Only `ds0[48..63]` and `ds1[48..63]` can be written: the rows below are read-only, and a write
to `dsB[n]` lands in the temporary `dsB[48 + (n & 15)]` **[HW]**. Our programs compute in
`ds0[48]`, `ds1[48]` and `ds1[50]` **[HW]**, and `load`/`store` move memory to and from
`ds0[48]`/`ds1[48]` and up **[RE]**. The temporaries keep their values from one PDS task to the
next, and the read-only rows past the data segment hold what earlier tasks left **[HW]**: a
program must write a temporary before it reads it.

### Input and special registers

- `ir0`, input word 0: the vertex index of a vertex program **[HW]**; the tile position
  `tile_y << 10 | tile_x` (16 x 16 tiles) of a fill's secondary program **[HW]** and of the
  pixel-event program, on every one of 41 tiles of a 128x128 triangle read back
  (`pds-pixel-event-pixev-grid16`) **[HW]**; the request mask the microkernel passes to
  its PDS #14 **[RE]**.
- `ir1`, input word 1: the event bits of the pixel-event program **[CAP/infer]**: on the
  end-of-tile events of the render's last two 16 x 16 tiles, and on no other, bit 2 is set
  **[HW]** (a 128x128 and a 64x64 triangle: the events that have it, sent to the end-of-render
  task instead, leave the bottom-right 32 x 16 pixels unwritten; read back per tile, `ir1` is 6
  on tiles (6, 7) and (7, 7) of the 128x128 render and 2 on every other tile seen); bits 3 and
  8-11 are clear on every end-of-tile event **[HW]** (`tri-pixev-event-bit*`,
  `pds-pixel-event-pixev-grid16`, `probes/pds/pixel-event.toml`); in the
  microkernel's event program, `EVENT_STATUS` bits 22-0 in reverse order (bit k is status bit
  22 - k: all eight bits the handlers acknowledge fit) **[RE/infer]**.
  Rogue's vertex programs get the vertex index in `IR0` and the instance ID in `IR1` (Mesa
  `pvr_pds.c`, MIT, Imagination); for SGX's vertex programs the second is **[infer]**.
- `ir2` **[open]**: in a `movs` it reads 0 in a fill's secondary program **[HW]**; the
  `mov16`/`mov32` fields do not reach it (the field once called `ir2` there is
  `pc.0`, *Hardware probes*) **[HW]**.
- `tim` is the SGX register **`EVENT_TIMER`** (`0xacc`): `VALUE` in bits 23-0, `ENABLE` in bit 24
  (`EUR_CR_EVENT_TIMER` in `sgx545defs.h`, GPL DDK) **[GPL/HW]**, the microkernel's tick. The
  firmware loads it with `HostCtl.ui32uKernelTimerClock | 1 << 24` (core clocks per tick, 400000 at
  400 MHz, for the DDK's 1000 Hz `SYS_SGX_PDS_TIMER_FREQ`); it counts down while enabled, and its
  expiry is `EVENT_STATUS.TIMER` (bit 29), which `EVENT_PDS_ENABLE` sends to the event program
  **[GPL/RE]**. Everything measured fits: a `movs tim` writes it (its first word's bits 24-0), for
  every later job, the firmware's included; reset reprograms it (`0x0102_0000`-`0x0106_1a7f` read
  back) and POWER IDLE writes 0 **[HW]**. The firmware writes it only at boot and on POWER resume,
  so it reloads itself with the period last written **[RE/infer]**; an enabled small count, which
  hung the job, would then raise TIMER events back to back **[infer]**. The ALU, `shl`, `mul` and
  `movs` read it as `tim`, `mov16`/`mov32` as `tim.0` (*Hardware probes*) **[HW]**.
- `pc`, through `mov16`/`mov32` only (`pc.0`): the fetch pc, the reading instruction's index
  plus 3, or plus 1 to 2 where fetch fell behind; the same on every pass of a loop, so not a
  time (*Hardware probes*) **[HW]**.
- `mr01`, `mr23`: 64-bit sources of `mov64`; `mr` is also a `movs` destination **[open]**.

Some operand fields reach only a prefix of the specials (`ir0`, `ir1`; or `ir0`, `ir1`, `tim`):
the field descriptions below say which. `mov16`/`mov32` number theirs apart **[HW]**: special
index `k` (the field less 128, in dwords) is selector `k >> 1` over `ir0`, `ir1`, `pc`, `tim`
and the word's bit 9 (`k & 1`), spelled `.0`/`.1` (`mov32 ds0[48], tim.0`, `mov16 ds0[96],
ir0.1.l`); selectors 4 and up read 0 and stay undecoded. Through `mov16` a `.1` source reads 0
in every case tried; `mov32` does not decode the bit (`.1` reads as `.0`). What it is for is
**[infer]**: another PDS pipe's registers (SGX545 is the only core in the DDK with two,
`SGX_FEATURE_NUM_PDS_PIPES`), another core's on the MP parts, or 64-bit specials; SGX545
cannot tell (*Hardware probes*, 8.11). The
fields were once numbered `ir0`, `ir1`, `pc`, `tim`, `ir2` in dwords, which the hardware does
not follow; this reference spells them as above (8.9).

### Predicates

The predicate field `w[26:24]` reads `p0`, `p1`, `p2`, `if0`, `if1`, `aluz`, `alun` or nothing
(7) **[RE]**:

- `p0`-`p2` are written by `tstz` (`pN = (src == 0)`) and `tstn` (`pN` = bit 31 of `src`)
  **[HW]**. `tstz` setting its predicate on zero is **[CAP/HW]**: our pixel-event program
  matches the captured one in what it tests and where it branches, skipping each case with
  `tstz p0, x; (p0) bra`, and the right task runs for each event.
- `if0` and `if1` are **[open]** on SGX. Our vertex program starts its shader under `(if0)`, as
  the closed driver's vertex programs do **[CAP]**, and in a fill's secondary program neither
  tests true **[HW]**. Rogue's PDS defines them as input predicates: `IF0` "Last Vertex In Task"
  for a vertex program and "End of Tile" for a pixel start/end program, `IF1` "First In Task"
  and "End Render" (Mesa `pvr_rogue_pds_defs.h`, MIT, Imagination); its vertex program issues
  `doutu` once, under `IF0`, on the last vertex (`pvr_pds.c`). Our observations fit that
  reading **[infer]**.
- `aluz` tests a zero result of the last `add`, `sub`, `adc`, `sbc` or `mul`; `alun` a negative
  one, but only under `alum signed`; every other instruction keeps both **[HW]** (*Hardware
  probes*).

`load`, `store`, the fences and `nop` use `w[26:24]` for other purposes or not at all, and
carry no predicate.
