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
  its pixels.
- The vertex shader draws the same triangle with `none` as with `vcull`. **`vcull` waits for
  the MTE's cull decision and skips the next phase for a culled triangle [HW]** (E121); with
  `none` the phase runs anyway and the MTE drops the triangle.
- `perinstance` does not run instances one at a time: an unlocked counter loses updates under
  it too, though fewer, and it is a barrier as `parallel` is (E110, E119).
- **The mode picks a divergent quad's branch leader [HW]** (E112): under `parallel` a
  predicated branch whose quad disagrees follows the quad's first covered instance, under
  `perinstance` instance 0 even when it covers nothing; `.skipinv` skips the uncovered
  instances under both. The closed compiler uses `perinstance` only for a vertex loop whose
  exit depends on data **[CAP]**.

- **The rates [HW]** (E115): `sample` and `selective` change nothing a 1x or 4x triangle
  shows; the shader still runs once per pixel. The compiler never emits them **[CAP]**. No bit
  of the pixel task's U1 or U2, of the render command's `te_aa` or `aa_mode_3d`, or free bit
  of ISP words 0 and 1 turns per-sample shading on either (E117), nor any bit of the render
  details' sample-related words (`isp_sample_pos`, `isp_multisamplectl`, which holds the sample
  positions, `isp_line_sample_pos`, `reg_0800`, `frag_flags`; E120).
- **The register form** `phas srcA, srcB` hung or faulted with every source layout tried
  (absolute index, offset or `doutu` U0 layout, against the immediate's fields or high dword);
  none started the next phase (E118).

What enables per-sample shading, how far the barrier reaches, why the compiler wants
`perinstance` there, and what the register form's sources hold are **[open]**.

**In the firmware [RE].** Seven `phas`, all of them the single-phase marker, the
same form our programs use (immediate operands zero, `pixel`, `end`, `parallel`).
