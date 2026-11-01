<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
## Machine model

A USSE program runs as a **task** over a set of **instances** (pixels of a batch, vertices,
or the single instance of a firmware or state task) **[infer]**. Each instruction is executed
for the instances of the task; the predicates and `.skipinv` decide which. The model below is
what our programs, the firmware and the captures show; the parts nobody has measured are
marked.

### Register banks

| bank | names | what it holds |
|------|-------|---------------|
| temporaries | `r0`-`r123` (`r0`-`r127` as load destinations) | per-task scratch |
| primary attributes | `pa0`-`pa127` | per-instance inputs written by the PDS |
| secondary attributes | `sa0`-`sa127` | per-task (shared) inputs written by the PDS |
| outputs | `o0`-`o127` | results handed to the next unit by the emits |
| constants, globals | `c0`-`c63`, `g0`-`g63` | a constant table; tile, quad and task state |
| internal | `i0`-`i3` | the accumulators of `efo`, `fddp`, the dual issue and the carries |
| index | `i.l`, `i.h` (`il`, `ih` in operands) | the bases of indexed operands |
| link | `pclink` | the return address of a call |

- **Temporaries [HW].** The number of temporaries a task gets is set when it is started: the PDS's
  `doutu` word U0 carries it in fours (`TRC`, `doc/specs/transfer.md` §4.2), and `phas` names it for
  the next phase. Our end-of-tile program asks for four and uses `r0`-`r3`. Temporaries are **not
  cleared** between tasks: a client shader that reads one before writing it sees what an earlier
  task left there, firmware data included (measured from a client pixel shader on our render node);
  `r40` and `r47` written by one fill were read by the next in 7 of 7 reader jobs (2048 of 2048
  pixels each), and by one two fills later, after a fill that wrote no temporary, in 2 of 2 (E484: a
  pair of fills, not EDM tasks; Q124, Q197). In firmware (EDM) tasks of ours `r20` and `r21` written
  by one task were read by the next at the next event and after 1200 ms (6 of 6) and replaced by a
  client fill (0 of 6 kept), and `i0` and `i1` also after a fill (6 of 6) **[HW]** (E536). The
  registers sampled up to `r123` are separate storage in a fill started with up to 128 temporaries
  (`--temps` 52, 64, 80, 96, 112, 124 and 128: 14 of 14 cases, every second or fourth register from
  `r2` and the top one; E485) **[HW]**. **A register at or past the task's allocation `T` reads as
  register `n mod T` in most instances, and a write to it was not seen to reach it [HW]**: in client
  pixel tasks `r(n)` read the marker written to `r(n mod T)` in 88 to 99.6 percent of the 2048
  instances in 15 of 15 cases (by `T`: 95.3 to 99.6 percent at 8, 95.3 to 98.4 at 16, 88.3 to 96.1
  at 32, 92.1 to 92.2 at 64), the rest of the instances reading other values, so the rule is "most
  instances" and no program may rely on it; in 4 of 4 cases that also wrote a marker to `r(n)` (`T`
  = 8 and 32 only) the instances read the value of `r(n mod T)`, not the one written; nothing
  faulted or hung (E486); and with a marker of its own in every job a write to `r123` under a
  request of 4 to 100 was not seen by the read of `r123` in the same job (0 of 12 jobs, within the
  pixels the reports list, E535). The
  model gave such a register storage of its own or a fault. A `phas` request is the allocation of
  its phase (*Tasks and phases*).
- **Primary attributes [HW].** The PDS fills them per task: `doutd` DMAs memory into them
  (the vertex fetch of our triangle lands in `pa0`-`pa3`), `douti` has the iterator write
  them and `doutt` returns a texture fetch into them (our copy shader reads its texel from
  `pa0`). Programs may also write them: our MTE state tasks load into `pa0` again. **In a fill's
  pixel task a write to `pa0` by `mov` or by `ima32` is lost [HW]** (E496: `ima32.u pa0, ...` in 2
  jobs and `mov pa0, r1` in 1, each read back in the same job as before, 3 of 3; the probe table's
  model had every destination take the result, and `ima32.u` writes `sa0`, `o0`, `i1`, `i2` and the
  six r-bank destinations run, r0, r9, r18, r28, r30 and r31): an unwritten `pa0` read 0xff00ff00 in
  1536 pixels and 0xff203040 in 512 in the first seven jobs of that table, each job outputting the
  colour it read (Q098, Q136).
- **Secondary attributes [CAP/RE].** Shared by the instances of a task and written by a
  secondary PDS program. The firmware keeps its base pointers there (`sa0`-`sa2`, DMAed from
  the TA/3D control block at boot) and some of its state (`sa8`, `sa9`, `sa19`), and it does
  write them (`doc/specs/hw_spec.md` 12.1). In a pair of fills on the render node **[HW]** an `sa`
  written by one job is read by the next (`sa1`, `sa5` and `sa7`: 9 of 9 reader jobs, 2048 of 2048
  pixels each) but not by one two jobs on: after a job that wrote no `sa` the reader read that
  job's pixel colour (3 of 3), as it does for an `sa` nobody wrote (2 of 2) (E484, Q098); 12
  pixels (4 of each value) of each of the 18 jobs that wrote `sa1`, `sa5` and `sa7` show the `sa`
  value as their colour (Q129). Job 8 of a table read 0x79 in `sa0`, written by `ima32.u` in job 7,
  which is also the colour job 7 output (2048 of 2048 pixels, E496), so one job's persistence of an
  `sa0` written by `ima32` is not separated from the colour rule; the job after that read it in
  `pa0`, which is also the colour the job before output (Q136).
  In an end-of-tile task `sa0`-`sa127` are the tile buffer the task's emit sends: one
  instance of the task covers 16 x 8 pixels, `sa(4q + i)` pixel `i` (top left, top right,
  bottom left, bottom right) of the block's 2 x 2 quad `q` in raster order, and what the task
  writes there is what is emitted (`mov sa0`-`sa3` before the emit changes those four pixels
  of every 16 x 8 block) **[HW]** (2026-10-24 the dump of all 128, 2026-10-27 the order and the
  writes; `doc/specs/pds_isa.md` 8.12). A 16 x 16 tile's end-of-tile event runs two such
  instances, one for each half; the pixel-event program's `douta` before that task was
  seen in neither its `sa` nor its `pa`. A plain task (no PBE flags) that the pixel-event
  program starts sees the same: `sa0`-`sa95` hold the tile's colours, none of the 16 values
  the program passed with `douta`, and reading `sa96` and up hung the job (3 runs of 3)
  **[HW]**. Such a task ran only from the PTOFF program's place (a copy elsewhere hung; a `br`
  from there to it runs it), and hung once in three identical runs **[HW]**.
- **Outputs [HW].** Pixel programs leave the colour in `o0` for the end-of-tile emit; the vertex
  shader of our triangle writes `o0`-`o3`, and the state tasks copy whole state blocks through
  `o0`-`o17` before emitting them. In a translucent pass (ISP0 pass type 1) a pixel program finds
  the pixel's current colour in `o0` when it starts: `mov o0, o0` leaves every pixel of our triangle
  as the background under it, `xor o0, o0, r1` inverts it (1062 of 1062,
  `usse-output-registers-fbf-translucent`); in
  the opaque pass `o0` holds what an earlier task left (`usse-output-registers-fbf-opaque`)
  **[HW]**. The closed
  driver's blended pixel program works the same way: it ends with a two-source blend whose
  destination colour is `o0`, the source colour against `o0` **[CAP]**.
- **Constants [HW] and globals [HW].** `c0`-`c63` read a fixed table, the same through a store's
  source and through `mov` (E085): 0 (`c0`-`c2`), 1.0 (`c3`), 2^1 to 2^10 (`c4`-`c13`), 2^-1 to
  2^-14 (`c14`-`c27`), e, 1/e, sqrt 2, 1/sqrt 2, pi/4, pi/2, pi, 1/pi, 2/pi, 4/pi, 2 pi, 1/65536
  (`c28`-`c39`), then series coefficients, f16 pairs of 1.0, 1.0 x4, ~0 x4 and `0x7fff7fff` x4:
  up to `c39`, Rogue's special constants in the same order. `g0`-`g63` are per-instance and
  per-task state (E086): in a fill `g23` is the pixel's x within its 32x16 tile, `g24` its y,
  `g25` its place in the 2x2 quad, `g17` the tile quarter, `g18` a per-tile number, `g39` the
  quad's place in a 4x4 block, and `g21`/`g22` scheduler-assigned task and slot ids; `g21`-`g25`
  follow Rogue's special registers 47-51 in order (`SR.TASK_ID`, `SLOT_NUM`, `TILE_X_PIX`,
  `TILE_Y_PIX`, `INST_NUM`). A `mov` to `g` is ignored (E086). The firmware reads two globals
  once each (as a source of an `xor` and of a `shl`) and otherwise names `c0` only as the dummy
  destination of a test that does not write its result (`!c0`, see the test group) **[RE]**.
- **Internal registers [RE].** `i0`-`i3` print where a temporary number reaches past the
  temporaries (bank 0, numbers 124-127; in the half-float and c10 readings, earlier). They
  are the accumulators of the dual-issue and `efo` groups and the carry registers of `imae`/`ima32`,
  and the extra operand `ima32.u d, iK, a, b, c` writes the high 32 bits of the product with the
  addend to `iK`, K = 0 to 2 **[HW]** on register operands, `.u` and `.s` (E493, E501, E525, E526;
  the probe table's model had the `i` registers keep their values). **[HW]** `i0`-`i2` are per
  instance, hold what `mov` or `fddp` writes and keep it from one task to the next, also another
  client's (9 of 9 reader jobs after a writer fill, E484); `i3` reads `i0` of the next instance of
  the 2x2 quad and drops writes, and `efo.gpiext` reaches across the quad (*Internal registers*,
  *`efo`*).
- **Index registers [RE].** A destination bank writes `i.l`, `i.h` or both (`i.lh`); an
  indexed operand `r[il + #n]` names a register of a bank (`r`, `o`, `pa`, `sa`) by index plus
  offset. The firmware loads `i.l` from a temporary 79 times and uses 79 indexed operands,
  all on the `sa` bank, as tables kept in the secondary attributes **[RE]**. **[HW]**
  `r[il + #n]` and `sa[il + #n]` are the bank's register `i.l + n`, counted from `r0`/`sa0`,
  and bits 10 and up of `i.l` are ignored; `i.h` and `ih` work the same way, and `mov i.lh, s`
  loads `i.l` from the low and `i.h` from the high half of `s` (*Index registers*).
- **The register file.** SGX's own MMIO registers are reached with `ldr`/`str` by dword
  index, not through a bank (*Register file access*).
