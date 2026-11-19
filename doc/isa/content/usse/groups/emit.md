<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### Emits: `emitpix1`, `emitpix2`, `emitvcb*`, `emitmte*`, `emitpds`

Class 31, other group, operation 3 **[RE]**. An emit hands words (and, by its kind, the task's
output registers) to another unit. All take an `#incp` number (three bits) and `.nosched`,
`.end` and `.freep`; the sources are register operands, and the pixel and PDS emits end with a
14-bit sideband immediate (scattered over `enc[27:22]`, `enc[40:35]` and `enc[55:54]`).

- **`emitpix1 #incp, s0, s1`** and **`emitpix2 #incp, s0, s1, s2, #sideband`** feed the pixel
  back end (PBE) **[HW]**: our end-of-tile program sends PBE words 0 and 1 (the clip
  rectangle) with `emitpix1`, then words 2 and 3 (count and line stride, the surface address)
  with `emitpix2`, whose sideband carries the pack mode (bits 5-0) and `TILERELATIVE`
  (bit 9); its third source is not used by that emit. The end-of-render program sends an
  `emitpix2` with zero words and sideband `0x200` (`doc/specs/transfer.md` §4.2).
- **`emitvcbvtx`** hands the vertex in the outputs to the vertex cache and **`emitmtevtx`** to the
  MTE; **`emitvcbst`** and **`emitmtest`** do the same for a state block **[HW]**: our first
  triangle's vertex shader and state tasks. `.twopart` (bit
  42) is set
  on every captured vertex and state emit **[CAP]**. On the vertex emits **[HW]** (E102),
  `emitvcbvtx` needs it: without it
  there, the job hangs. `emitmtevtx` draws the same without it, and with neither emit flagged no
  triangle is drawn. On the state emits `.twopart` changes nothing a triangle shows, on either emit
  or both (E106). What it is for there, and `.cut`, are **[open]**.
- **`emitpds.tasks.taske #incp, s0, s1, s2, #sideband`** starts a PDS program **[CAP/RE]**: the
  microkernel's boot task launches PDS programs #11 and #12 this way and its request path #14; the
  control word carries the program's data size in four-dword units at bits 27-23
  (`doc/specs/hw_spec.md`) and, below it, an addend. A client fill shader can execute it **[HW]**
  (E488, one quad of four lanes emitting: E513, a copy's shader): with `s1` the pixel PDS heap
  offset of the fill's PDS secondary shifted right by four (4 for the copy's, at heap base + 0x40),
  two data rows and the addend 0x100, the named program ran in 18 of the 19 `ir0.0` probes (it
  stored 3 in 16 and 2 in 2, where the fill's own run leaves 0x400 to 0x403), and **the addend
  matters [HW]** (E520, 39 probes, every emitting job faulted or hung): with 0xFFF, 0x1000, 0x1001,
  0x1010, 0x1100 and 0x2000 the dwords the program stores read the fill's own 0x403 (12 of 12
  probes, in two orders, so not a drift in time), where 0x100 read 3 or 2 (11 of 11) and 0, 0xF0,
  0xFF, 0x101, 0x110, 0x200, 0x400, 0x4000, 0x8000 and 0x10000 did too (12 of 12 probes), 0x800 read
  0x401 and 0x400 (2 probes) and 0x10 read 3 and 0x400 (2 probes); the emitted run may not store in
  the window **[infer]**. **`s2` is not `ir0` or `ir1` of the started program**: with `s2` 0, 1,
  0xFFFFFFFF and 0xE17D0001 the program saw `ir0.0` 3, 3, 2 and 3, and `ir1.0` 0 for 0, 0xFFFFFFFF
  and 0xE17D0001 (against the reading of E146, which came from the operand order). `.tasks`,
  `.taske`, both, neither, `.freep`, `.nosched`, `#incp` 1 to 3, the sideband 0x1, 0x200 and 0x2000
  and a data size of 1, 2 or 4 rows each changed nothing seen of whether the program ran (one probe
  each). **Every job that executed an `emitpds` then faulted or hung, 24 of 24 in E488 (`BIF fault`
  at page 0xd2000 in 22, 0x92000 once with sideband 0x1, a hang for two emits in a row) and 39 of 39
  in E520 (37 faults, 2 hangs), each recovered by the driver with no reload** (Q128): a client emit
  is a hang risk, not a tool, and the model's start of a PDS program is not the whole of it. What
  `.tasks`/`.taske` do is **[open]** (Q054).
- **From an EDM task of ours [HW].** Our form (`emitpds.tasks.taske #0, r2, r3, r4, #0x0`,
  the firmware's but for the 14-bit sideband, which its #12 and #14 emits set to 0x843; the
  kernel's control word 0x01000100, its PDS image's address >> 4 and 0; the image
  `douta` to attributes 0 and 2, `doutu` our entry 1) did not fault the bus, but the started
  entry left no write within 200 ms and the EDM's tick stopped in that window, recovered by a
  reset, in its one job (E1148, Q128). Whether the image ran, and where an emitted `douta` lands,
  is **[open]**.
- **The issuer goes on; the program does not start [HW, infer].** With breadcrumbs (E1149,
  E1150: one job each, the same form and image, then a `tim`-marking image) the issuing task
  went on past the `emitpds` and the started entry never made its first store, while the tick
  stopped within 10 ticks of the command **[HW]**; the marking image's first `movs tim` never
  showed at 0x0acc, so the emitted program never executed its first instruction **[infer]**: that
  rests on a `movs tim` from an emitted program writing the 0x0acc the host reads, as a client
  fill's PDS program's does: the host's 0x0acc took a client's `movs tim` value at once and held
  it to the reset (E1152) **[HW]**; an emitted program's has never been seen to run (Q128).
- **The stop needs the emit [HW].** The same task with the `emitpds` taken out (E1151: the same
  arm, command, stores, fences and tail call, one job) ran its command to done with the tick
  going at its rate through and after the job, so our cmd-1 path does not stop the EDM by itself;
  which part of the emit does is **[open]** (Q128).
- **Not the program, its page, rows or control word [HW, infer].** A lone `halt` image (v1's two
  data rows, the kernel's own page, E1153) stopped the tick within 9 ticks as v1 and crumb did,
  the issuer going on, so the stop needs no instruction of the program **[HW]**. crumb's program
  with 3 data rows and #14's control word 0x01800100, placed in the firmware's own PDS #14 page
  (0x30011100, that page's flags, E1154) never showed its first `tim` marker and stopped the
  tick the same way **[HW]**, so it never started there either **[infer, as E1150]**. Left open
  (Q128): our `s2` operand or the encoding form, and emitting from our task's timer pass where
  the firmware emits from its kick pass.
- **Mirrored, the emitted program runs [HW].** From a host GETMISCINFO kick pass, our form and
  `s2` 0 read as if crumb3 never started and the tick stopped **[infer]**, but the score is
  CANNOT TELL (the tick stopped 7 from the kick, outside the frozen band 8-11; E1155). With the
  sideband 0x843 (0xfb20b10800c08184) and `s2` 0x00020000, the request bit #14's emit carries,
  from the same kick pass, the same crumb3 image in #14's page ran to its last `tim` marker
  (0x005a3305 at 0x0acc), its `doutu` started our entry 1 and that ran to done (E1156): the first
  program our task emitted that ran, and an emitted program's `tim` write lands at 0x0acc as a
  client's does. Which of the sideband, `s2` and the kick pass is needed: the next item. Where
  its `douta` land is **[open]** (not `pa0` or `pa2` in any run; `sa0` and `sa2` hold those
  values anyway).
- **The sideband decides [HW].** One change at a time against that run (E1157-E1160): with
  #14's sideband 0x843 the emitted program ran and our entry to done from a kick pass or a tick
  pass, with `s2` 0 or 0x00020000 (4 of 4: E1156, E1157, E1159, E1160); with our sideband 0 it
  never started and the tick stopped, from a tick pass with `s2` 0 (E1154) or a kick pass with
  `s2` 0x00020000 (E1158). So the stop after our earlier emits came from the 14-bit sideband
  being 0; `s2` and the pass are not needed. What the sideband's bits mean (#11's emit carries
  0x0c43, #12's and #14's 0x0843), whether another nonzero value runs and what stops the tick
  with 0 are **[open]** (Q128).
- **`.freep`** frees the task's resources after the emit **[infer]**; **`#incp`** is always 0
  in our programs and its meaning is **[open]**.
- The assembler writes the unprinted source of `emitvcbst`/`emitvcbvtx` and the unprinted
  bank bit of `emitmtest` as the closed compiler does, so that the hardware sees the words it
  was tested with (`tools/usse-asm/README.md`).

**In the firmware [RE].** Three `emitpds`, all `.tasks.taske`; no other emit (the firmware
does not render).

<!-- @prog use_eot.s match='emit' -->

<!-- @prog use_vtx.s match='emit' -->

<!-- @group usse class=31 pat='^emit' -->
