<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### Tasks and phases

A task is started by the PDS (`doutu`, `doc/specs/pds_isa.md`), by the microkernel's
`emitpds` (which runs a PDS program that starts one), or by the event machinery that runs the
microkernel's own PDS programs (`doc/specs/hw_spec.md`) **[CAP/RE]**. The
`doutu` words give the program's code base and first instruction, its temporaries and flags
such as "wait for the texture result" (`doc/specs/transfer.md` §4.2, §4.4) **[HW]**.

A program can be split into **phases**. `phas` is the phase marker and is the first
instruction of every pixel, vertex and state program we run **[HW]**:

```
phas #<next>, #<temps>, <rate>, <wait>, <mode>
```

- `#<next>`: the instruction index (from the code base) where the next phase starts;
- `#<temps>`: the temporaries of the next phase, a multiple of four;
- `<rate>`: `pixel`, `selective` or `sample`;
- `<wait>`: what the next phase waits for: `none`, `pt`, `vcull` or `end` (no next phase);
- `<mode>`: `parallel` or `perinstance`.

**[HW]** for what our programs do with it: a single-phase program says
`phas #0, #0, pixel, end, parallel`; our vertex shader says `phas #7, #0, pixel, vcull,
parallel`, runs its first phase (copy the vertex to the outputs, `emitvcbvtx`), and its second
phase at instruction 7 (`emitmtevtx`) runs once vertex culling has seen the vertex. The driver
adds the program's own instruction index to `#<next>` when it places the program, as the
operand counts from the code base.

The waits and modes on the hardware (E101) **[HW]**:
- `none` runs the next phase at once, and the temporaries the first phase wrote carry into it,
  for most instances but not all: in a fill some lose them under `parallel` and enough to fault
  under `perinstance` (E119), so a phase should recompute what it needs from the g bank.
- **A phase boundary is a barrier [HW]** (E119): under both modes a quad reaching phase 1 waits
  until the other quads of its 4x4 block, at least, have finished phase 0.
- **Program shape [HW]** (E118): a program must start with a `phas`, and its last phase must be
  closed by a `phas` that declares the end; otherwise the job hangs. A fill's shader starts at
  its code base, so its `#<next>` is the local index.
- Each wait belongs to one kind of task. `vcull` hangs a pixel shader. `pt` hangs a vertex
  shader, and in a pixel shader with no punch-through feedback the next phase never writes
  its pixels. The simulator refuses `pt` and `vcull` in a pixel task, and runs a vertex task's
  first phase only (`sgx-sim --task vertex`).
- The vertex shader draws the same triangle with `none` as with `vcull`. **`vcull` waits for
  the MTE's cull decision and skips the next phase for a culled triangle [HW]** (E121); with
  `none` the phase runs anyway and the MTE drops the triangle.
- `perinstance` does not run instances one at a time: an unlocked counter loses updates under
  it too, though fewer, and it is a barrier as `parallel` is (E110, E119).
- **The mode picks a divergent quad's branch leader [HW]** (E112): under `parallel` a
  predicated branch whose quad disagrees follows the quad's first covered instance, under
  `perinstance` instance 0 even when it covers nothing; `.skipinv` skips the uncovered instances
  under both. **The branch is the quad's [HW]** (E513): in a fill a test of `pa0` selected by
  `xor.testtaz.chan0 !c0, p0, r7, #K` and a `!p0 br` over code ran that code in the four lanes of a
  quad, from the test of its top-left lane (K = 0: the pixels 0, 1, 64 and 65; K = 2: 2, 3, 66 and
  67; K = 1, 3 and a value no instance has: no lane; 9 cases, K = 0 to 2 a replication of the
  first run and K = 3 predicted). So 'one instance' selected by a test
  of `pa0` is a quad of four lanes, and a store or an emit under it is executed by four lanes; a
  test whose result differs across the lanes of a quad other than by `pa0` was not run. The closed
  compiler uses `perinstance` only for a vertex loop whose exit depends on data **[CAP]**.

- **The rates [HW]** (E115): `sample` and `selective` change nothing a 1x or 4x triangle
  shows; the shader still runs once per pixel. The compiler never emits them **[CAP]**. No bit
  of the pixel task's U1 or U2, of the render command's `te_aa` or `aa_mode_3d`, or free bit
  of ISP words 0 and 1 turns per-sample shading on either (E117), nor any bit of the render
  details' sample-related words (`isp_sample_pos`, `isp_multisamplectl`, which holds the sample
  positions, `isp_line_sample_pos`, `reg_0800`, `frag_flags`; E120).
- **A phase's temporaries are its `phas` request [HW]** (E487, E519): in a two-phase fill the marker
  written to a register at the top of the request (`r123` from 124 up to 504, and for the 15
  requests from 512 up `r(T mod 256 - 1)`, `r123` when that is above 123, for the 8 predicted to
  run, `r3` for the 7 predicted to hang) was read back, and the job ran, when the request T mod 256
  was 4 to 192, and the job hung (each hang recovered by the driver with no reload) when it was 0 or
  196 to 252. Ran: 8, 16, 32, 64, 96, 124, 128, 132, 136, 144, 160 and 192 (E487: 15 of 15 jobs, the
  task started with 8, 192 also with 32, 64 and 128), 100 to 120, 148 to 156, 164 to 188 and 260 to
  448 (every multiple of four, 64 requests; E519) and 8 of the 15 requests from 512 to 1016 chosen
  by the rule (516, 576, 640, 704, 772, 832, 896 and 960). Hung: 196, 200, 204, 208, 212, 216, 220,
  224, 252, 256, 508 and 1020 (E487: 15 of 15 jobs, 196 also started with 32, 64 and 128), 228 to
  248 and 452 to 504 (20 requests; E519) and 7 of those 15 (512, 708, 764, 768, 964, 1000 and 1016).
  The rule was written after the first 84 requests and predicted all 15 from 512 up. What a request
  above 256 allocates is not measured, but it is not the value modulo 256 for 260 to 376: with a
  marker of its own in every job (E535, 36 jobs in two runs) a write to `r123` landed and read back
  in 2048 of 2048 pixels under the requests 260, 264, 300, 316, 376 and 448 (12 of 12 jobs) and in
  the 6 controls (124, 128 and 192 with `r123`, 8, 32 and 64 with `r3`, `r31` and `r63`: 12 of 12
  jobs), and was not seen under 4, 8, 16, 32, 64 and 100 (0 of 12 jobs, within the pixels the
  reports list; the pixels read what earlier jobs left). [infer] A request of 260 to 376 therefore
  allocates at least 124 registers and not the 4 to 120 that its value modulo 256 gives (Q144), and
  E519's read-back of `r123` was a landed write, not a stale read. Every request from 124 up to 504
  wrote `r123` only (`r124` and up cannot be named as an ALU operand), so these show that the job
  runs and that `r123` is real storage, not that 192 temporaries are usable; the register numbers a
  program can name end at 123. Every request run was a multiple of four. The 15 jobs of E487 that
  ran took 420 to 583 microseconds, with no cost seen in single samples. A register past a phase's
  request reads as `n mod T` in most instances (*Machine model*; E535's read of `r123` under 100 or
  less returned earlier jobs' contents, a different probe, not reconciled: Q147). **For a firmware
  task [HW]** (E540) the temporaries are the TRC the task is started with: with TRC 8, 9, 12, 16, 24
  and 31 (32 to 124 temporaries) the top register, `r(4T - 1)`, held the marker written to it in 6
  of 6 runs, and the register past the allocation (`r32`, `r36`, `r48`, `r64`, `r96` for 8, 9, 12,
  16 and 24) did not (0 of 5, one job and one read per T; it read 0 or a leftover), as in a fill.
  TRC 32 and above were not run (the arm of 32 failed with its error cut off, [infer] at the fork's
  hazard gate), so the limit of a firmware task above 31 is **[open]** (Q133, Q144).
- **A firmware (EDM) task of ours runs [HW]** (E531 to E534): one start dword of PDS #13 (the
  general slot, which the 1 kHz tick and the host kick reach) pointed at a page of our code at the
  kernel code heap + 0x20000 (instruction index 0x4000), set when the firmware is loaded and undone
  by a reset. The wrapper reads a command dword of a results page the host shares, and when it is
  zero jumps to the task the slot used to start (`mov pclink, rN`, `lapc`, the index a record
  states, E146), which then runs as before (ticks at 964 to 999 Hz, `miscinfo` answered, a fill and
  a triangle exact). The forms it uses: `mov rN, #imm32` (a `limm`, patched by the kernel with the
  results address and the continue index), `ldad.bypassl1`, `stad`, `wdf drc0`, `idf drc0, bif`,
  `and.testtanz.chan0 !c0, pN, rA, rB` and `xor.testtaz.chan0 !c0, pN, rA, #n` for predicates, `pN
  br` with a numeric offset, and `ldr rD, #idx, drcN` and `str #idx, rS` with an immediate index
  only, `mov saN, rM` and `mov rD, saN`, `mov i0, rN` and `mov rN, i0`, `mov rN, pclink`, a
  predicated `mov`, `and.testtanz.chan0 !c0, pN, rA, rB` with a register mask, and `ima32.u rD, rS,
  #1, rM.neg` (a loop counter). A tick hands the task `pa0` = 2, `pa1` = 0x02000000 and `pa2` =
  0x01061a70 (E532, 2 of 2 runs), and a host kick (a GETMISCINFO with no job) `pa0` = 2, `pa1` =
  0x03000000 and the same `pa2`, to the general slot only (E538, 3 of 3 runs; `pa2` was the same in
  all 5 events seen). After a task that wrote `sa`, `r`, `i`, `p` and `pclink` state and ended with
  `nop.end` instead of jumping to the closed one, every later event stopped until a reset (E533, one
  run; skipping the closed task, its arbitrary pclink write and its p values are not separated,
  Q152). **State between firmware tasks [HW]** (E536; a writer that calls the closed task after its
  writes, with the closed task's ticks between): `sa100`, `sa127`, `sa20` and `sa24` (12 of 12
  values in 3 of 3 rounds), `r20` and `r21` (6 of 6) and `i0` and `i1` (6 of 6) written by one task
  were read by the next at the next event and after 1200 ms, and after a client fill all but `r20`
  and `r21`; `sa64` did not take the write (it read 2); at the next event p1 was the writer's 0 (3
  of 3, 1 in the other readings) and `pclink` was 6, the value of the writer's own tail triple
  [infer], not the 0x98 of the other readings, p0 was not the writer's, and p2 and p3 move between
  readings with no writer (Q152). The same writer kept the tick, a task that also wrote `sa63` and
  `sa65` and called the closed task was not followed by its armed reader within 100 ms (E537, one
  run: Q152). No second pass of the wrapper was found busy while a slow task ran, up to 6.9 ms (10
  of 10 runs, E539; ticks only, slot 0, no job). The simulator runs these tasks only through
  `sgx_sim::fwtask`, and models `ldr` and `str` only there: `str` to 0x0814 and 0x0a78 (values
  inside their 17 and 6 bits, the immediate index only) and `ldr` of those two and of `CORE_ID`,
  `CORE_REVISION` and `CR_TIMER`, which a vector seeds (the timer never advances, and no vector
  reads the first two: unit tests alone cover them); a vector may give the task's entry state (`sa`,
  `r`, `i`, `pa`, p and `pclink`) and its temporaries, and the readback the state it must have left;
  everything else stops the run, including a read of `sa64` after the task wrote it.
- **The register form** `phas srcA, srcB` hung or faulted with every source layout tried
  (absolute index, offset or `doutu` U0 layout, against the immediate's fields or high dword);
  none started the next phase (E118).

What enables per-sample shading, how far the barrier reaches, why the compiler wants
`perinstance` there, and what the register form's sources hold are **[open]**.

**In the firmware [RE].** Seven `phas`, all of them the single-phase marker, the
same form our programs use (immediate operands zero, `pixel`, `end`, `parallel`).
