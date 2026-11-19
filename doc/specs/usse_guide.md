# SGX545 USSE programmer's guide

The **USSE** (universal scalable shader engine) is the programmable core of the PowerVR SGX
Series 5: on the SGX545 of Intel's Cedar Trail it runs every vertex, pixel and state program of
a scene, and the firmware. This guide is for writing and reading those programs: the machine a
program runs on, its operands, the assembler syntax, what every group of instructions does, and
what the hardware was measured to do.

It is the reference's text without its encodings. The instruction set reference
(`doc/specs/usse_isa.md`) is built from the same snippets and adds, for every group, the bit
layouts, field lists and an appendix of every form; read it to decode or encode a word by hand.
Both state behaviour with the conventions below, and both end every group with what the
simulator (`crates/sgx-sim`) models of it, checked against the hardware vectors: a rule the
simulator holds is one a program can rely on, and one it stops on is still open.

> **Generated file.** This document is assembled by `doc/isa/build.py` from the snippet library
> in `doc/isa/` (see `doc/isa/README.md`). Edit the snippets, not this file, and rebuild; the
> test `doc/isa/test_build.py` fails while the committed copy is stale. Bit diagrams, field
> lists, form lists and encoding examples are generated from the form tables of our clean-room
> disassemblers and assemblers (`tools/usse-dis`, `tools/usse-asm`), so they cannot drift from
> the tools; the prose around them is handwritten.

## 1. Conventions

### 1.1 Where each fact comes from

This is a reconstruction, not a vendor document. Every statement about what an instruction
*does* carries a tag, as in `doc/specs/hw_spec.md`:

- **[HW]** measured on the laptop: our own programs or probes ran and behaved as stated.
- **[CAP]** captured from the closed driver running under the extraction harness (its
  programs, the words it writes), so exact for that build.
- **[RE]** read from the closed microkernel's code with our disassembler, or established by
  black-box probing of the layouts (bit flips and value sweeps). Encodings and assembler
  spellings are **[RE]** in this sense: our decoder decodes every word of the firmware and the
  captures, and nothing more is implied about behaviour.
- **[DDK]** read in the GPL DDK sources (register names, structure layouts).
- **[infer]** an inference from names, context or how the firmware uses an instruction;
  verify before relying on it.
- **[open]** not known. Said plainly rather than guessed.

Two tags joined by a slash (**[CAP/HW]**, **[RE/CAP]**) mean both kinds of evidence agree, the
first being the primary one. The design documents also use **[patent]** and **[decide]**
(HACKING.md).

**Names.** Most spellings are the decoder's **[RE]**; where a public
source (the Rogue ISR, Mesa, Rogue's register headers) spells the same thing, the tables take its
spelling. The rest keep their names when the hardware confirms what the name says or a public source
outside PowerVR uses the same word for the same thing, and carry a name of ours where the
name would mislead: `sop3c`, `lrp`, `alrp`/`alrpc`, `latch`, `usub8`, `usub16`, `.quadlead`
(a quad's first instance, E088) and `.twopart` (bit 42). Eight names stay without a measured
meaning, so
they are kept as printed and marked **[open]** where they appear: `bexception` (its bit 51), `setm`,
`.bypassl1`, `.dm_nomatch`, `moest`, `setfc`, `twosided` and `optdwd`. `perinstance` (E112) and
`.pcff16` (E116) have one.

Facts asked of the hardware with our probe programs are collected in one section, one snippet
per fact, marked *Measured on the hardware (2026-10-22)* (with what stays undecided) or *Not
probed yet*.

### 1.2 Clean room

Everything here was written from our own decoders, our own programs, the GPL DDK and our
hardware runs. No vendor ISA text is quoted. Examples are either our own programs
(`asm/`) or instructions assembled fresh for this document; no instruction
word of the closed firmware appears. Where the firmware's use of an instruction is described,
it is described in words and counts, not quoted.

## 2. Machine model

A USSE program runs as a **task** over a set of **instances** (pixels of a batch, vertices,
or the single instance of a firmware or state task) **[infer]**. Each instruction is executed
for the instances of the task; the predicates and `.skipinv` decide which. The model below is
what our programs, the firmware and the captures show; the parts nobody has measured are
marked.

### 2.1 Register banks

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
  pair of fills, not EDM tasks). An unwritten `r20` read right after the fill that wrote it showed
  the marker in 2024 of 2048 pixels and another value in 24, against a control frozen at 2048, so
  that session decided nothing on which job an unwritten temporary reads (E1145, Q193). In
  firmware (EDM) tasks of ours `r20` and `r21` written by one task were read by the next at the next
  event and after 1200 ms (6 of 6) and replaced by a client fill (0 of 6 kept), and `i0` and `i1`
  also after a fill (6 of 6) **[HW]** (E536). After a
  firmware reload, and after a reset and a reload, `i0`, `i1` and `r21` kept the markers and `r20`
  and `sa63` read 0 (6 of 6; after a fill `r21` read 0x1000 to 0x3000 and `sa63` kept its marker)
  **[HW]** (E810). The registers sampled up to `r123` are separate storage in a fill started with up
  to 128 temporaries (`--temps` 52, 64, 80, 96, 112, 124 and 128: 14 of 14 cases, every second or
  fourth register from `r2` and the top one; E485) **[HW]**. **A register at or past the task's
  allocation `T` reads as register `n mod T` in most instances, and a write to it was not seen to
  reach it [HW]**: in client pixel tasks `r(n)` read the marker written to `r(n mod T)` in 88 to
  99.6 percent of the 2048 instances in 15 of 15 cases (by `T`: 95.3 to 99.6 percent at 8, 95.3 to
  98.4 at 16, 88.3 to 96.1 at 32, 92.1 to 92.2 at 64), the rest of the instances reading other
  values, so the rule is "most instances" and no program may rely on it; in 4 of 4 cases that also
  wrote a marker to `r(n)` (`T` = 8 and 32 only) the instances read the value of `r(n mod T)`, not
  the one written; nothing faulted or hung (E486); and with a marker of its own in every job a write
  to `r123` under a request of 4 to 100 was not seen by the read of `r123` in the same job (0 of 12
  jobs, within the pixels the reports list, E535). The
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
  colour it read (Q098); the first value was the colour of the health triangle before the table
  (E1140).
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
  `pa0`, which is also the colour the job before output. Separated since **[HW]** (E1140,
  held out after E1139's post hoc reading):
  - an `sa0` written by `iaddu32` is read by the next job (2048 of 2048 pixels), across a debugfs
    reset and 120 s idle with no job between, and any job between (a fill writing no `sa`, the
    health fill or triangle) replaces it with that job's colour: it lasts one job;
  - `pa0` reads the colour of the job before, across a reset too, and after the health triangle
    0xff00ff00 in 1536 and 0xff203040 in 512 pixels, E496's first-job mixture.
  - an `sa5` write is replaced by the next job's output also when that job writes another `sa`
    (`sa1`), so it lasts one job whatever the job between writes (E1144);
  - a fill writing `sa_n` (n = 0 to 15) with `iaddu32` shows the value at exactly 4 pixels, the
    same 4 in every run, one per 16 x 8 block of the top-left 32 x 16, and three writes show the
    union; post hoc [infer] (x, y) = ((n & 1) + 2 (n >> 2) + {0, 16}, ((n >> 1) & 1) + {0, 8})
    (E1144, Q129).
  A reader that outputs anything but the value it read sees that output come back: its later
  instances read what its earlier ones wrote to `o0` (E1139 [infer]).
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
  `TILE_Y_PIX`, `INST_NUM`). In a triangle's pixel program the same held out: `g25` = (x & 1) |
  (y & 1) << 1, `g23` = x mod 32 and `g24` = y mod 16 (E808: 29 of 29 rows at three triangles; E772
  post hoc). A `mov` to `g` is ignored (E086). The firmware reads two globals
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

### 2.2 Predicates

There are four predicate registers, `p0`-`p3`, per instance **[RE]**. Most instructions take an
execution predicate in `enc[58:56]`, printed before the mnemonic:

| value | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|-------|---|---|---|---|---|---|---|---|
| prints | (always) | `p0` | `p1` | `p2` | `p3` | `!p0` | `!p1` | `Pn` |

The integer multiply-add, colour, dot-product and video groups have only a two-bit predicate
`enc[58:57]`: always, `p0`, `p1`, `!p0`; the dual-issue group has the same four in
`enc[57:56]`, and they act as printed on both operations **[HW]** (*Dual issue*).

- An instruction whose predicate is false does nothing for that instance (**[HW]**, if
  indirectly): our vertex and state programs issue a four-register load into `pa0`-`pa3`,
  predicated on `p0`, right after a test that leaves `p0` false; had it run, it would have
  replaced the vertex the PDS had just DMAed there, and the triangle renders exactly.
- Predicates are written by the **test group** (`p0`-`p3`, chosen by `enc[35:34]`), by
  `rlp` (a seven-bit predicate number) and by `atst8` (`p0`-`p3`, optionally negated)
  **[RE]**. **[HW]** `rlp`'s predicate numbers 4 and up alias `p0`-`p3` (*`rlp`*); whether
  `atst8` reaches more is **[open]**.
- `Pn` (value 7) **never runs** the instruction, whatever `p0`-`p3` hold **[HW]** (*`br`
  offsets and the `Pn` predicate*): the decoder prints it for value 7 of the
  full field and nothing in the firmware or the captures uses it.
- A repeated instruction tests its predicate once, for the whole instruction **[HW]**
  (*Predicates on repeated instructions*).
- **Predicates and control flow [HW].** `p0`-`p3` are not changed by `ba`, `br`, `ba.savelink`,
  `br.savelink`, `lapc` or a predicated one of these, taken or not (E477: 28 of 28 cases with the
  patterns 1010, 0101, 1111 and 0000, and 16 of 16 through `ba.savelink` and `lapc`). A routine's
  own tests change them for its caller: there is no save and restore of `p0`-`p3` around a call. A
  predicated branch is taken when its predicate is set (`!pN` when clear).
- **The predicates are not reset between jobs [HW].** A job that reads `p0`-`p3` before it sets them
  reads the pattern the job before it left, in 98 to 99 percent of its 2048 pixel instances (E477:
  2016 to 2032 pixels in each of the ten readers that followed a setter) and another pattern in the
  others. The probe table's model, "cleared at the start of a job", fails. A task sets `p0`-`p3` by
  a test before it reads them; across firmware tasks, p1 at the next entry was the writer's 0 and p0
  was not after a writer that called the closed task **[HW]** (E536, 3 of 3 rounds; p2 and p3
  equalled the flags but also move between readings with no writer, so they show nothing). Held
  out, p1, p2 and p3 at the next entry are what the task left and p0 reads 1 (E809: 8 of 8 jobs
  where a flag was 0); after a fill, a reload or a reset p0 p1 read 1 1, p2 0 and p3 as left
  (E810). The rest is **[open]** (Q158). A second table agrees: `p0` and `p1` after a setter read
  the kept value in 96.3 to 100 percent of the pixels in 10 of 10 reader jobs (E484).

**In the firmware [RE].** The microkernel's predicates guard branches above all: 591 of its
954 `ba` are predicated (`p0` 318, `!p0` 94, `p2` 76, `p1` 72, `!p1` 26, `p3` 5). A few dozen
stores, moves, loads and bitwise operations are predicated too. A typical sequence tests a
flag into `p0` without writing a register and branches on it.

### 2.3 Program counter, calls and the end of a program

- **The PC counts instructions** from the code base the task was started from **[HW]**. The
  PDS starts a task with a `doutu` word naming a code base (`USE_CODE_BASE_n`, n in
  `U0[3:0]`) and an instruction index; the SGX545 has 18 PC bits, which is also the width of
  the branch target fields **[CAP/RE]**.
- **`ba #n`** jumps to instruction `n` of the code base (absolute) **[RE/HW]**. **`br`** takes
  a signed 18-bit offset **counted from the `br` itself** (`br #1` is the next instruction)
  **[HW]** (*`br` offsets and the `Pn` predicate*); the assembler accepts only a number for
  `br`, not a label (`tools/usse-asm/README.md`). **A backward `br` loops [HW]** in a vertex task
  (E784, E807: up to 1760 iterations, proved by the stored depth word), in a fill (E804: 2048 of
  2048 pixels, with a mark written only where the counter reached zero) and in a triangle's pixel
  program placed in the `--tri` slot at code index 0x20 (E806: every pixel of the target at seven
  sizes). **A predicated `ba` whose predicate is false falls through** to the next instruction
  (E596: `p0 ba` with p0 0 and `!p0 ba` with p0 1, 10 of 10 fills); the taken predicated `ba` was
  not run there.
- **Calls.** `ba.savelink` and `br.savelink` write the index of the instruction after the call to
  `pclink` **[HW]** (E475: calls with the next instruction at index 20, 40, 64, 127 and 128, and a
  taken predicated call: 9 of 9; both forms store the same index, counted from the program start of
  a fill and in general from the code base, below). **A call that is not taken writes `pclink` too
  [HW]** (E491): `ba.savelink` and `br.savelink` under `p0`, `p1`, `p2` and `p3` with the predicate
  false, and under `!p0` and `!p1` with the predicate false, left the index of the instruction after
  the call in 16 of 16 calls of a fill table (the preset 0x77, 0 or 0x3ffff never read back; next
  instructions at indices 24, 48 and 84), in 3 of 3 not-taken calls of a chain of two calls and in
  10 of 10 jobs of five programs placed at 0x10000 and 0x1ff000 (`ba.savelink` placed at 0x10000
  only), where the probe table's model said a call not taken leaves the link as it was (0 of 29
  cases); the taken calls write the same link. A routine that is called under a predicate must save
  `pclink` first. `!p2` and `!p3` calls, `lapc` under a predicate, a call with a repeat and calls in
  firmware tasks were not run. `lapc` jumps to `pclink` **[HW]** (E476). The firmware builds return
  addresses as instruction indices (it loads an index into a temporary and moves it to `pclink`
  before a `lapc`), and the kernel CCB dispatch jumps to a handler the same way (the address moved
  into `pclink`, then `lapc`; `doc/specs/hw_spec.md`) **[RE]**.
- **`pclink` is 18 bits wide [HW].** `mov pclink, rN` keeps bits 17:0 of `rN` (E475: 19 of 19 cases;
  0x40000 reads back 0, 0x7fffffff reads 0x3ffff, 0xa5a5a5a5 reads 0x1a5a5, and the whole 32 bits
  come back for no value above 0x3ffff), so the bits above 17 of a register never reach a jump; the
  probe table's model kept 32. `mov pclink, rN` followed at once by `lapc` jumps to the new value,
  with no instruction between them and with or without `.nosched` on either (19 of 19; the call's
  stale link is never used). There is one link register, so a routine that calls another saves
  `pclink` in a temporary first (`mov rN, pclink` ... `mov pclink, rN`) **[RE]**, and nested calls
  so written return twice **[HW]** (E476: 2 of 2).
- **`lapc` lands exactly on the index in `pclink` [HW]** for the indices run (E476): in a fill 30,
  31, 32, 34, 37, 45, 69 and 129, forward, the target a constant or computed by an `ima32` add (8 of
  8 and 8 of 8), backward 0, 1, 2, 5, 20 and 100 instructions (6 of 6), the call returns near 20,
  and in programs placed in the code heap 0x2081, 0x20c8 and 0x20fa and the link plus 8 (0x200a,
  0xa, 0xfe0a, 0xa, 0xa). The link values themselves (0x2002, 0xfe02, 2) are reads, not targets. No
  index outside these is known to fail. With programs placed across the 0x80000 step (E1098) a
  run of nops, a `ba` and a `lapc` cross index 0xffff to 0x10000 and 0x1ffff to 0x20000 and land
  on their target word, a run reaches word 8100 of a placed program of 8192 words and a `lapc`
  lands on word 590 of one: the index is an 18-bit counter from the code base **[HW]** (E1098). A
  `lapc` and a `ba` in a placed program of 8192 words land on ten words drawn at random from 256 to
  8191, both ends included, frozen and held out (E1102: 10 of 10) **[HW]**.
- **Where indices count from [HW].** The index of a `ba`, `lapc` or `pclink` counts from the code
  base the task was started with (E476). A program placed at heap offset X by `sgxfive-test probe
  --place X=FILE --place-form cbase` runs with the code base X rounded down to a multiple of 0x80000
  bytes (65536 instructions) and starts at (X mod 0x80000) / 8: the link read in a program placed at
  0x10000 is 0x2002, at 0x100000 it is 2, at 0x1ff000 it is 0xfe02, at 0x200000 and at 0x400000 it
  is 2 (5 placements, 2 runs each). The 0x80000 step rests on ten placements (0x10000, 0x100000,
  0x1ff000, 0x200000 and 0x400000 in E476, 0x2ff000, 0x1a0000, 0x3a8000, 0x4ff000 and 0x300008 in
  E492: links 0xfe02, 0x4002, 0x5002, 0xfe02 and 0x3), seven of them not multiples of the step, and
  no other power of two from 0x1000 to 0x1000000 fits all ten (E492), nor any multiple of 8 up to
  16 MiB (E1098, post hoc). Held out at four more placements, 0x0c3010, 0x2ca7f8, 0x3d0100 and
  0x1c8008, the read and jump programs read 0x8604, 0x9501, 0xa022 and 0x9003 as the step predicts,
  where 0x20000, 0x40000, 0x100000 and a code base of 0 each predict another link (E1102: 8 of 8).
  A jump to an index counted from the program start, in a program placed at
  0x10000, faulted the job (5 of 5: 3 `lapc` and 2 `ba #T`) or hung it (2 of 2, a `lapc`); that it
  went to index 129 of the code base instead is **[infer]**. A computed target independent of the
  base is the link read at run time plus a constant (`br.savelink #1; mov rN, pclink; ima32.u rM,
  rN, #1, rK; mov pclink, rM; lapc`), which landed in all ten placements (E476 five, E492 five)
  **[HW]**.
- **`pclink` is not reset between jobs [HW].** A job that reads `pclink` before it writes it reads
  what an earlier job left, in 94 to 98 percent of its 2048 pixel instances (E475: the ten readers
  of one table; usually the last job's value, the others 0xeb3 or 0x98, in aligned 2 x 2 quads of
  pixels). Four runs of that table (E500, 40 reader jobs) show the 0xeb3 pixels in exactly 64 pixels
  (16 quads) in 29 of the 40 jobs and in 48 to 80 in all, 0x98 in 16 to 64 pixels of 12 of them and
  no other value, and the quad positions repeat from run to run in part (two runs share 4 to 52
  pixels of a job, where chance gives about 2 pixels), not whole; two reader jobs of one run share 1
  to 16 quads, as much, so the positions are neither fixed nor independent across jobs or runs
  (Q125). A task writes `pclink` before it reads it; across firmware tasks, after a writer that
  called the closed task p1 at the next entry was the writer's, `pclink` was 6 (the value of the
  writer's own tail triple **[infer]**) and p0 was not **[HW]** (E536); at the next entry `pclink`
  read 0x98, p0 1 and p1 to p3 what the writer left, 12 of 12 (E809); after a fill, a reload or a
  reset p0 p1 read 1 1, `pclink` 0x98, p2 0 and p3 as left (E810). The start state after other
  perturbations and a cold boot is **[open]** (Q158).
- **Branch flags [open].** `.nosched`, `.synce`/`.syncent` and `.mon` decode on `ba`, `br`
  and `lapc`; their effect is not established, and the firmware uses none of them.
- **`bexception` [HW].** Hangs a fill's pixel task, with or without `.nosched`: it neither
  falls through nor ends the task (E100). What it raises, and where to, is **[open]**.
- **The end of a program [HW].** A program ends at an instruction carrying `.end`, which
  still executes. There is no return to the PDS: every one of our programs ends this way
  (`mov.skipinv.end`, `nop.end`, `emitpix2.end.freep`, `ptoff.end`, ...). The firmware's tasks
  end in a shared routine with a `nop.end` or `mov.end` (eight `.end` in all).

**In the firmware [RE].** 954 `ba` (232 of them `.savelink` calls), 12 `br`, 74 `lapc`, 205
moves into `pclink` and 193 out of it.

### 2.4 Repeats and the MOE state

Many instructions can **repeat**: one instruction stands for N consecutive operations on
consecutive registers. Where a group allows it, `enc[53]` turns the write-mask field
`enc[47:44]` into a repeat count (`.repeat2`-`.repeat16`, the field value plus one); the float
groups have a two-bit count (`.repeat2`-`.repeat4`), the multiply-add and colour groups a
three-bit one (`.repeat2`-`.repeat8`) **[RE]**. Loads and stores use the same count either as
a repeat or, with the MOE-expand bit `enc[53]` clear, as a **fetch** of N registers
(`.fetch1`-`.fetch16`, see *Loads and stores*).

- **What a plain repeat does [HW].** `mov.skipinv.repeat4 o0, pa0` copies `pa0`-`pa3` to
  `o0`-`o3`: our vertex shader writes the position this way, our state tasks copy 16 and 2
  registers with `.repeat16` and `.repeat2`, and the outputs reach the MTE intact. So with
  the default MOE state each operand register number advances by one per iteration. The
  iterations run one after the other in ascending order, so overlapping ranges propagate,
  and one predicate covers the whole instruction (*Repeat order and overlapping ranges*,
  *Predicates on repeated instructions*). **A repeated load or store steps its pointer register
  too [HW]**: iteration `i` of `stad.repeatN [rb,...], rs` uses `r(b + i)` as its address, not
  `rb` (E483, E515, *Loads and stores*).
- **The MOE state.** The register advance per iteration is programmable: the MOE group sets
  per-operand increments or swizzles (`smlsi`), base offsets (`smbo`), address modes and
  offsets (`smoa`) and ranges (`smr`) **[RE]**: the decoder names the state
  words they write (*SMOA*, *SMLSI*, *SMBO*, *SMR* low and high data, and an index word) when
  `moest` reads them back. How each value acts on the operand numbers is **[infer]** from those
  names, except that `smlsi`'s four increments are the destination's and sources 0, 1 and
  2's **[HW]** (*`smlsi` increments*).
- **`.incsXYZ`.** The float groups carry three increment bits per instruction when they
  repeat (`.incs000`-`.incs111`): X, Y and Z let source 0, 1 and 2 advance, the destination
  always does, and without `.incs` everything does **[HW]** (*`.incsXYZ`*).
- **Write masks** are repeats of four with iterations left out: component k writes `d + k` from
  every register source `+ k` **[HW]** (*Write masks*).
- **Open:** what a repeated test writes into its predicate, repeats after the other MOE
  instructions, `.partial` and `.quadlead` (*Hardware probe results*).

**In the firmware [RE].** The microkernel never repeats an ALU instruction (no `.repeatN` at
all); it moves blocks with fetches instead (120 `.fetchN` loads and stores, mostly
`.fetch2`). It executes `smlsi` eight times, each time at the start of a task entry point and
each time with the same operands: increments 0, 0, 0 and 1 in increment mode, limits 0. It
uses no other MOE instruction.

### 2.5 Scheduling flags

Most groups carry a handful of one-bit flags printed after the mnemonic. Their bit positions
are in each group's field list in the reference; what is known of their effect:

- **`.end`** ends the program after this instruction **[HW]** (*Program counter, calls and
  the end of a program*).
- **`.skipinv`** skips invalid instances **[HW]** (E104). In a triangle's pixel shader an
  instruction with it runs only for covered pixels. One without it also runs for some of the
  uncovered pixels in the quads the triangle covers, and their `o0` reaches the tile. The
  closed compiler's pixel and state programs (and ours, which follow them) set it on nearly
  every instruction. The same reading explains an end-of-tile task where a `mov.skipinv` did
  not run but the plain `mov` did, if that task's instance is invalid **[infer]**. It is
  Rogue's default turned into a flag: Rogue's instructions run only for enabled instances
  unless they carry `(ignorepe)` ("PowerVR Instruction Set Reference", pp. 20, 66). Without it an
  instruction runs for all four instances of every
  quad the triangle touches, the same in every run **[HW]** (E111). Whether an uncovered
  instance's `o0` lands varies, by whole quads: of 102 helper pixels, 26 to 43 land at 0 to 16
  `nop`s,
  71 at 32 and 53 to 59 from 64 on, mostly quads whose instance 0 is covered (E113);
  what decides it per quad is **[open]**.
- **`.nosched`** is a scheduling hint, probably "do not switch to another task after this
  instruction" **[infer]**; it changes nothing a fill's pixels see **[HW]** (*`.tpres`,
  `.partial`, `.nosched`, `.syncs`*). Our programs carry it only where the captured programs do
  (`nop.nosched` before the DMA wait); the firmware uses it once, in the same idiom.
- **`.syncs`** decodes in most groups; **in a fill it hangs the task** **[HW]** (on `mov` and
  `fmad`), so it waits for something a fill never gives; what is **[open]**. Unused by the
  firmware and by us.
- **`.partial`** (the bitwise group) changes nothing a fill sees **[HW]**. **`.quadlead`** runs the
  instruction for instance 0 of each 2x2 quad only, the others keeping their destination **[HW]**
  (E088). The closed compiler sets it on a fragment loop's exit test, so only the quad's lead
  instance computes the predicate the loop's branch follows **[CAP]**; `.partial` on the
  test group is **[open]**.
- **`.freep`** on the emits frees the task's resources once the emit is done **[infer]**:
  every final emit of our pixel and state programs carries it, as the captured ones do.
- **`.tog`** and **`.trigger`** (`nop`), **`.tpres`** (single-source floats), **`.gpiext`**
  (`efo`), **`.twopart`**/**`.cut`** (the vertex and MTE emits) and
  **`.tasks`**/**`.taske`** (`emitpds`) are discussed with their groups; most are **[open]**.

The radare2 emulation of the firmware assumes that `.skipinv`, `.syncs`, `.nosched` and `.end`
do not change what one instance computes, and ignores them (`tools/usse-dis/r2/README.md`);
nothing contradicts that so far.

### 2.6 Tasks and phases

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
  its code base, so its `#<next>` is the local index. A firmware task follows the second half of
  the rule and not the first: a pass of ours that ends `idf; wdf; phas #0, #0, pixel, end,
  parallel; nop.end` keeps the tick with no `phas` at its start, and one that ends without the
  `phas` stops it (E817, E830; below) **[HW]**; that this is E118's rule seen in an EDM task is
  **[infer]**.
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
  allocates at least 124 registers and not the 4 to 120 that its value modulo 256 gives (Q133), and
  E519's read-back of `r123` was a landed write, not a stale read. Every request from 124 up to 504
  wrote `r123` only (`r124` and up cannot be named as an ALU operand), so these show that the job
  runs and that `r123` is real storage, not that 192 temporaries are usable; the register numbers a
  program can name end at 123. Every request run was a multiple of four. The 15 jobs of E487 that
  ran took 420 to 583 microseconds, with no cost seen in single samples. A register past a phase's
  request reads as `n mod T` in most instances (*Machine model*; E535's read of `r123` under 100 or
  less returned earlier jobs' contents, a different probe, not reconciled: Q132). **For a firmware
  task [HW]** (E540) the temporaries are the TRC the task is started with: with TRC 8, 9, 12, 16, 24
  and 31 (32 to 124 temporaries) the top register, `r(4T - 1)`, held the marker written to it in 6
  of 6 runs, and the register past the allocation (`r32`, `r36`, `r48`, `r64`, `r96` for 8, 9, 12,
  16 and 24) did not (0 of 5, one job and one read per T; it read 0 or a leftover), as in a fill.
  TRC 32 and above were not run (the arm of 32 failed with its error cut off, [infer] at the fork's
  hazard gate), so the limit of a firmware task above 31 is **[open]** (Q133).
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
  0x01061a70 (E532, 2 of 2 runs), and a host kick (a GETMISCINFO with no job) one event to the
  general slot, `pa0` = 0, `pa1` = (count << 24) | 0x100 and a `pa2` that is a sample of the event
  timer (E746, 3 of 3; E538's 0x03000000 was the tick after the kick, see its correction). After a
  task that wrote `sa`, `r`, `i`, `p` and `pclink` state and ended with
  `nop.end` instead of jumping to the closed one, every later event stopped until a reset (E533, one
  run; a task that wrote nothing and ended a tick pass that way stopped it in 2 of 2 runs, so
  skipping the closed task is enough, E793; no single write of sa63, sa64 or sa65 and no tail call
  with p0 = p1 = 1 stopped it, E791; what the EDM needs is the phase end, E817 and E830, in the
  contract below).
  **State between firmware tasks [HW]** (E536; a writer that calls the closed task after its
  writes, with the closed task's ticks between): `sa100`, `sa127`, `sa20` and `sa24` (12 of 12
  values in 3 of 3 rounds), `r20` and `r21` (6 of 6) and `i0` and `i1` (6 of 6) written by one task
  were read by the next at the next event and after 1200 ms, and after a client fill all but `r20`
  and `r21`; `sa64` did not take the write (it read 2); at the next event p1 was the writer's 0 (3
  of 3, 1 in the other readings) and `pclink` was 6, the value of the writer's own tail triple
  [infer], not the 0x98 of the other readings, p0 was not the writer's, and p2 and p3 move between
  readings with no writer (held out later: they are what the task left, E809). The same writer
  kept the tick, a task that also wrote `sa63` and
  `sa65` and called the closed task was not followed by its armed reader within 100 ms (E537, one
  run: Q294). No second pass of the wrapper was found busy while a slow task ran, up to 6.9 ms (10
  of 10 runs, E539; ticks only, slot 0, no job). The simulator runs these tasks only through
  `sgx_sim::fwtask`, and models `ldr` and `str` only there: `str` to 0x0814 and 0x0a78 (values
  inside their 17 and 6 bits, the immediate index only) and `ldr` of those two and of `CORE_ID`,
  `CORE_REVISION` and `CR_TIMER`, which a vector seeds (the timer never advances, and no vector
  reads the first two: unit tests alone cover them); a vector may give the task's entry state (`sa`,
  `r`, `i`, `pa`, p and `pclink`) and its temporaries, and the readback the state it must have left;
  everything else stops the run, including a read of `sa64` after the task wrote it.
- **The contract of a firmware task of ours [HW]** (records E809 to E823, E830, E835, E836;
  what a task of ours starts with and must leave, each line with its record):
  - *Start.* At the next entry after a task of ours `pclink` reads 0x98, p0 1 and p1, p2 and p3
    what the task left (E809: 12 of 12 writer jobs, H-SET refuted 8 of 8); after a client fill, a
    firmware reload or a reset p0 p1 read 1 1, `pclink` 0x98, p2 0 and p3 as left (E810, 9 of 9).
    `i0`, `i1` and `r21` survive a reload and a reset, `r20` and `sa63` read 0 (E810, 6 of 6);
    the start state of a fresh arm was `pclink` 0x98, p0 to p3 1 1 0 0, `r20` 0, `sa63` 0, `sa64`
    2 and `sa65` 0x02000000 (E810, one reading). After other perturbations and a cold boot: Q158.
  - *The event words.* `pa0` to `pa4` read `sa64` to `sa68` (E748, 3 of 3). A `mov` to `pa3`
    writes `sa67`, read in the same pass and the next; to `pa2` writes `sa66` for the pass only
    (the next event rewrites it [infer]); to `pa4` is lost, read through neither bank (E820, 3 of
    3 each). A write to `sa67` or `sa68` reads back through `pa3` or `pa4` (E748).
  - *The end of a pass.* A plain tick pass of ours keeps the tick iff it executes `phas #0, #0,
    pixel, end, parallel` before its `nop.end`: with it 13 of 13 jobs kept (E817 FB and FPH, E830
    fb and fk), without it 7 of 7 stopped (E793 x2, E818 T2, E817 FCF, E830 x3, held out and
    replicated in three blocks); `cfi.global` is neither needed nor enough. The closed exit
    reached by the `cont4` tail call keeps it (E817, E830: 8 of 8), and so does any closed path
    that reaches it, the general task's or slot 2's (E813 X1, X20: H-EXIT). A kick pass ended
    with `idf, wdf, nop.end` stops it too (E813 B3), and ended with the `phas` keeps it, 2 of 2,
    its command left unread (read = write - 1) since the closed reader never ran (E835). Slot 3's
    end-of-render pass ended with the `phas` instead of the closed handler is finished too (10
    ticks after it, E836), but the held render stops the tick 20 tick passes after the fill's kick,
    whatever the tick's rate, with the lockup counted and the recovery requested (E855, E856: 7 of
    7): the EDM's 3D lockup check, which the closed handler's end-of-render path would have ended
    and which host clears of bit 18 and a command do not end (E857). A task of ours therefore
    skips no closed slot 3 handler. A stop reads the busy signature
    (`CR_CLKGATESTATUS` 0x000ccfa0, `USE0_SERV_EVENT` bit 16 clear and its count frozen, the
    event timer counting, `CR_EVENT_STATUS` 0x20000000), answers no host command, and one debugfs
    reset recovers it; the signature cannot tell a stop from a long task (E811). The own end
    therefore is `idf drc0, bif; wdf drc0; phas #0, #0, pixel, end, parallel; nop.end`.
  - *What does not stop the tick.* A pass with the tick bit of `sa64` clear (50 passes) leaves
    `pclink` 6 and does not advance HostCtl dword 12; single `sa65` words without bit 8 (bits 2,
    3, 6, 14, 15, 16, 19, 23, the count byte) keep it (E812). `sa65` bit 8 alone makes the closed
    reader take an empty command and stop with HostCtl dword 14 0xad002600 (E814 D2), and E537's
    word without bit 8 stops it with no mark (E814 D1).
  - *Stores.* A `str` of the tick handler's own word 0x01061a80 to `CR_EVENT_TIMER` followed by
    the closed task keeps the tick and moves the next entry to 25114 units (E818 T1, 2 of 2); it
    does not replace the phase end (E818 T2, 1 stop). A `str` to `CR_EVENT_HOST_CLEAR2` clears the
    bits written, as the host's write does (E822, 3 of 3). Which registers a task may store to is
    HACKING.md's allow list.
- **The register form** `phas srcA, srcB` hung or faulted with every source layout tried
  (absolute index, offset or `doutu` U0 layout, against the immediate's fields or high dword);
  none started the next phase (E118).

What enables per-sample shading, how far the barrier reaches, why the compiler wants
`perinstance` there, and what the register form's sources hold are **[open]**.

**In the firmware [RE].** Seven `phas`, all of them the single-phase marker, the
same form our programs use (immediate operands zero, `pixel`, `end`, `parallel`).

### 2.7 Memory, data fences and the register file

- **Loads complete asynchronously.** A load (`ld*`, `eld*`, `ldr`, the samplers) names a data fence
  counter, `drc0` or `drc1` (two bits for `ldr` and the samplers, `drc0`-`drc3`), and `wdf drcN`
  waits until the loads counted on it have landed **[RE/HW]**. In a fill one `wdf drc0` covers every
  load outstanding on `drc0`, whether `ldad`, `ldad.fetchN` (the whole fetch) or `ldr`: 1, 2, 4, 8
  and 16 independent `ldad`, five mixes with fetches of 2, 4, 8 and 16 dwords and `ldr`, and, in the
  growth runs, 24, 32, 48, 64, 80 and 100 distinct `ldad` on `drc0`, 32, 64 and 100 on `drc1` and 2,
  4, 8, 12 and 16 `ldad.fetch16` (256 dwords) were all complete after the one `wdf`, and no limit on
  the number outstanding was seen up to 100 distinct `ldad` on one counter and 16 `ldad.fetch16`
  **[HW]** (E478), nor up to 192 distinct-line `ldad` on one counter, the first 100 into `r4` to
  `r103` and the rest reloading `r4` onward with other lines (104, 112, 128, 160 and 192 on `drc0`,
  128 and 192 on `drc1`: each of 8 sampled registers held the line of its last load, 7 of 7 jobs,
  the 4 or 5 reloaded registers read per job; E518). Three more cases, 128, 160 and 200 `ldad`
  reloading the same eight lines into eight registers, were complete too (27 of 27 cases in all, one
  run each), but they issue the same loads again, so a lost or late reload would leave the registers
  unchanged: they cannot show a lost reload; E518 can, for the reloaded registers it read (5 of 92
  at 192), and saw none lost. 200 distinct loads in one program were not run. A load is not complete
  without the `wdf` in the sense that one `ldad` read by a `stad` still holds the register's old
  value after 0, 1, 2, 4, 8, 16 or 32 `nop`s and four `ldad` after 0 or 16 (9 of 9); an ALU
  instruction (`ima32.u r11, r10, #1, r12`) reads the old value after 0, 1, 4, 16, 32 and 48 `nop`s
  too (6 of 6, E517), so the reader has no interlock whichever it is; a load not waited for had
  landed when a `stad` read it after 40, 100 and 128 `nop`s and not after 48 and 64 (one sample
  each, a timing effect **[infer]**), so no instruction count stands in for the `wdf`; and a `mov`
  to the register issued after the `ldad` and before its `wdf` is overwritten by the load (4 of 4),
  while one after the `wdf` wins (E517; the texture unit and the dual-issue secondary as readers
  were not run, Q052, Q146). A `wdf` with nothing outstanding returns at once and hangs nothing (11
  of 11 cases: as the first instruction, on a counter never used, twice in a row, on all four
  counters, and after an `idf drcN, bif` with nothing stored; E480). **A `wdf drcN` does not wait
  for the loads of the other counters [HW]** (E479): loads of another counter issued after the
  waited ones were still in flight in 10 of 10 runs (four `ldad` on `drc1` after two `ldr` on
  `drc2`, `wdf drc2` only) and in 2 of 10 (four `ldad` on `drc0` after four on `drc1`, `wdf drc1`
  only), and complete in the runs that had waited on four `ldad` first (28 of 30), so what has
  landed depends on timing: each counter counts its own loads **[infer]**, and a program waits on
  every counter it used. The counts of ten runs are those of scratch runs recounted by the reviewer;
  the data hold one run of each case (2 of the 8 cases show the markers in it). All this was
  measured in client pixel tasks; the EDM task of ours of E534 shows the same for a result `stad`
  followed by a load, a `wdf` and two more stores and then the flag the host reads with no `idf`
  (18 of 18) and for a `wdf` with no load outstanding between a `str` and an `ldr` (18 of 18, 15 of
  which could show a change, and none did), and no more. The firmware almost always follows
  its loads with a `wdf` before using the data (711 `wdf drc0`, 96 `wdf drc1`), and our programs
  wait with `wdf drc0` for the attribute DMA the PDS started.
- **`idf drcN, bif`** appears 124 times in the firmware, mostly right before a `wdf` on the same
  counter, after stores **[RE]**: it looks like a fence that makes earlier memory writes visible
  (through the BIF, the memory interface) and is counted on `drcN` **[infer]**. In a fill no
  measured case needed it **[HW]**: a `stad` and a later load of the same dword, all 2048 instances
  of the fill storing the same value to that dword, returned the stored value with no `idf` in 16 of
  16 cases (`ldad`, `.bypassl1`, `.fcfill`, `eldd`, `.bpcache`, on `drc1`, after two stores and
  after sixteen; E481), and the dword the host read held the stored value after seven short programs
  (one or sixteen `stad`) that ended with no fence, an `idf` only, a `wdf` only, both, or a `nop`
  (E480). Both show a dword that every instance wrote with one value, so by themselves they do not
  show that one instance sees its own store. **An instance sees its own unfenced `stad`, and its
  store changes the dword the host reads with no fence [HW]** (E512): with each of the 2048
  instances of the fill storing a value of its own to a dword of its own, the load returned the
  instance's own value in 2048 of 2048 pixels in each of nine cases (`ldad`, `.bypassl1`, `.fcfill`,
  `drc1`, a `wdf` only between, two stores where the load returns the later value, an `idf` and its
  wait between, and the `idf` at the end) and 2048 dwords changed (32 values read) in the seven
  cases that ended with no `idf` and no fence. A load of another instance's store returns it when
  that instance ran earlier (the x and y neighbours in its quad: 2048 of 2048, n ^ 65 not run;
  lower-numbered instances of other quads: 1024 of 1024 in each of three masks; the right 32 columns
  of the 64 x 32 target reading the left 32: 1024 of 1024) and in part when it runs later (64 of
  1024 at no delay, 792 and 984 after 64 and 192 `nop`s for the next quad in x, none for 32 columns
  on): a rule of timing and of the order of the tiles, the left half first **[infer]** (E514), and
  no case needed an `idf`. The `idf` in the storing instance, the host reading during the job, a
  texture fetch of the stored data are **[open]** (Q143); an EDM task's own store lands with
  no `idf` before the flag the host reads (E534). `str` then `ldr` is ordered for two registers in
  an EDM task of ours (E534, below). The `pixelbe` and reserved modes of `idf` are **[open]**.
- **Addresses.** Loads and stores take a base register and an offset counted in elements of
  the access size (4 bytes for `d`, 2 for `w`, 1 for `b`) **[DDK/HW]**; the addressing modes
  and the fetch rule are in *Loads and stores*. Addresses are device virtual addresses of the
  task's memory context **[HW]**.
- **The SGX register file** is not memory: `ldr rD, #idx` and `str #idx, src` read and write
  the SGX register at offset `idx × 4` **[RE/HW]**. A client pixel shader on our render node
  reads any register this way; a client store to the one register tried was dropped
  (measured on our render node). **In a firmware (EDM) task of ours a `str` to 0x0814 or 0x0a78 is
  seen by the next `ldr` of that register and by the host, with no fence and at every distance
  run [HW]** (E534: 318 of 318 runs, 0 to 16 instructions between and a second `ldr` 64 `nop`s
  later, a `wdf`, an `idf`, both or neither, two `str`; an earlier `ldr` is not changed by a later
  `str`; four fresh loads, and the replicates within a load are not independent). It is **[open]**
  for a client `str` (no client `str` was seen to change a register, Q134), for a register whose
  write has an effect, with a job running, and for the register-index forms (Q154).
- **Caches.** `ci`, `cf` and `cfi` invalidate, flush, or flush and invalidate the levels their
  last operand names (L0 and L1, L2, or all three) **[infer]**, from the names the reference
  disassembler prints; the cache mode flags of loads and stores (`.bpcache`, `.fcfill`,
  `.bypassl1`) are discussed under *Loads and stores*.

## 3. Operand encodings

### 3.1 Register operands

A register operand is a seven-bit number plus bank bits. Destinations, sources 1 and 2, and
source 0 number their banks differently **[RE]** (the printers were derived by sweeping every
number and bank through the decoder, and hold in every form checked). The
tables below are generated from the decoder's printers: each row is a bank code (the value
bits above the number) and what numbers 0, 1 and 127 print in it.

**Destination** (`enc[27:21]` number, `enc[33:32]` bank, `enc[51]` bank extension):

| bank | number 0 | number 1 | number 127 |
|---|---|---|---|
| 0 | `r0` | `r1` | `i3` |
| 1 | `o0` | `o1` | `o127` |
| 2 | `pa0` | `pa1` | `pa127` |
| 3 | `r[il + #0]` | `r[il + #1]` | `sa[ih + #15]` |
| 4 | `sa0` | `sa1` | `sa127` |
| 5 | `c0` | `c1` | `g63` |
| 6 | `i.` | `i.l` | `i.lh` |
| 7 | `i0` | `i1` | `i127` |

**Sources 1 and 2** (source 1: `enc[13:7]`, `enc[31:30]`, `enc[49]`; source 2: `enc[6:0]`,
`enc[29:28]`, `enc[48]`). Bank 6 is a seven-bit immediate, printed in decimal or, by some
instructions (`mov`, the bitwise group's source 1), in hex:

| bank | number 0 | number 1 | number 127 |
|---|---|---|---|
| 0 | `r0` | `r1` | `i3` |
| 1 | `o0` | `o1` | `o127` |
| 2 | `pa0` | `pa1` | `pa127` |
| 3 | `sa0` | `sa1` | `sa127` |
| 4 | `r[il + #0]` | `r[il + #1]` | `sa[ih + #15]` |
| 5 | `c0` | `c1` | `g63` |
| 6 | `#0` | `#1` | `#127` |
| 7 | `i0` | `i1` | `i127` |

**Source 0** (`enc[20:14]`, `enc[34]`, and `enc[51]` where the instruction has no
destination extension): temporaries, `pa`, `o` and `sa` only; no immediates.

| bank | number 0 | number 1 | number 127 |
|---|---|---|---|
| 0 | `r0` | `r1` | `i3` |
| 1 | `pa0` | `pa1` | `pa127` |
| 2 | `o0` | `o1` | `o127` |
| 3 | `sa0` | `sa1` | `sa127` |

- **Temporaries and internal registers.** In bank 0, numbers 124-127 print as `i0`-`i3` **[RE]**;
  as load destinations they are not the internal registers: `ldad.fetch4 r124` in a job started
  with 128 temporaries left `i0`-`i2` as they were (one case, E485) **[HW]**. In
  the 6-bit readings below (half floats, c10, the colour groups) the temporaries stop at `r59`
  (`r29` for half-float halves) and the internal registers follow. A load destination is
  either `r0`-`r127` or `pa0`-`pa127` (one bank bit, `enc[39]`).
- **Bank 7** prints `i0`-`i127` in both tables. Numbers past 3 read the other instances of
  the 2x2 quad, modulo 16, and writes to them are dropped **[HW]** (*Internal registers*).
- **Indexed operands** `bank[il + #n]` and `bank[ih + #n]`: the bank is `r`, `o`, `pa` or `sa`,
  the base the index register `i.l` or `i.h`, and `n` 0-15 (0-7 in the 6-bit readings)
  **[RE]**; the register used is the index plus `n`, in registers, for `r` and `sa` **[HW]**
  (*Index registers*).
- **Destination bank 6** writes the index registers: `i.l`, `i.h`, both (`i.lh`), or neither
  (`i.`, the number's low two bits 0): a `mov` to numbers 0, 4, 8, 16, 64 and 124 changes no
  temporary, internal or index register or the pixel a fill reads, and none of pa and sa for
  0, 4 and 64 **[HW]** (E366); the simulator stops on the other numbers.
- **Constants** `c0`-`c63` and **globals** `g0`-`g63` share bank 5 (numbers 64 up are `g`).

### 3.2 Immediates

- **Seven-bit immediates** are source bank 6 (`#0`-`#127`), in sources 1 and 2.
- **The 32-bit move** (`mov dst, #imm32`, class 31) scatters its immediate over three ranges:
  value bits 20-0 in `enc[20:0]`, 25-21 in `enc[40:36]` and 31-26 in `enc[49:44]` **[RE/HW]**.
  The driver patches colours and PBE words into our programs exactly there
  (`doc/specs/fw_format.md` §4, the `USSE_LIMM` patch). For example:

`mov.skipinv.end o0, #0x12345678` assembles with form #0: enc[63:32] = `0xFCA44111`, enc[31:0] =
`0x00145678`; in memory (little endian) `78 56 14 00 11 41 A4 FC`.

| field | value | prints |
|---|---|---|
| `pred` | 0x0 | (none) |
| `skipinv` | 0x1 | `.skipinv` |
| `nosched` | 0x0 | (none) |
| `end` | 0x1 | `.end` |
| `dst` | 0x80 | `o0` |
| `imm` | 0x12345678 | `0x12345678` |

- **The rotated immediate** of the bitwise group (source 2 written as `#imm`) is a 16-bit field
  rotated left by the five-bit rotation field `enc[42:38]` **[HW]** (E474: raw words with the fields
  0xffff, 0x8001 and 0x1234 under all 32 rotations, 96 of 96), so redundant encodings of one value
  agree, and any 32-bit value with at most 16 significant contiguous bits (cyclically) can be
  written directly; the assembler finds the first rotation that fits. `~#X` complements the whole
  32-bit operand after the rotation (19 of 19). A shift or rotate by a rotated immediate uses the
  whole 32-bit value as the amount: `shl` and `shr` give 0 and `asr` the sign for 32 and over, and
  `rol` takes it mod 32 (36 of 36). The assembler refuses values that are not `rotl(m16, r)`
  (0x00010001, 0x55555555, 0x12345678); that no other encoding exists is **[infer]**:

`and r1, r2, #0x00FF0000` assembles with form #16: enc[63:32] = `0x50011230`, enc[31:0] =
`0x203F8100`; in memory (little endian) `00 81 3F 20 30 12 01 50`.

| field | value | prints |
|---|---|---|
| `pred` | 0x0 | (none) |
| `op` | 0x0 | `and` |
| `flags` | 0x0 | (none) |
| `dst` | 0x1 | `r1` |
| `wmask` | 0x1 | (none) |
| `src1` | 0x2 | `r2` |
| `inv` | 0x0 | (none) |
| `imm` | 0x8ff00 | `0x00FF0000` |

- **Register indices** of `ldr`/`str` are 14 bits in two seven-bit halves (`enc[6:0]` low,
  `enc[20:14]` high), counted in dwords (`ldr r0, #7, drc0` reads `CORE_ID` at offset `0x1c`)
  **[RE/HW]**. A register index is masked to 14 bits **[HW]** (*The 14-bit `ldr`/`str`
  index*).
- **Branch targets** are 18 bits (`enc[17:0]`): absolute for `ba`, signed for `br`.
- Smaller numbers (counts, `phas` operands, the MOE values, emit sidebands) are described with
  their groups.

### 3.3 Write masks, byte masks and repeat counts

- **Destination write mask.** `enc[47:44]` (bits w, z, y, x from high to low) prints after the
  destination: `.x` alone prints nothing, `0` prints a lone `.`, the rest name the enabled
  components (`r1.xz`). It shares its bits with the repeat count, chosen by `enc[53]` **[RE]**.
  A component is a register, not a byte: component k writes `d + k` from every register source
  `+ k`, as a repeat of four would, and mask 0 writes nothing **[HW]** (*Write masks*).

`mov r1.xz, r2` assembles with form #1: enc[63:32] = `0x28015000`, enc[31:0] = `0x20200100`; in
memory (little endian) `00 01 20 20 00 50 01 28`.

| field | value | prints |
|---|---|---|
| `pred` | 0x0 | (none) |
| `skipinv` | 0x0 | (none) |
| `syncs` | 0x0 | (none) |
| `nosched` | 0x0 | (none) |
| `end` | 0x0 | (none) |
| `dst` | 0x1 | `r1` |
| `wmask` | 0x5 | `.xz` |
| `src1` | 0x2 | `r2` |

- **Byte masks.** The pack/unpack group writes a byte mask after its destination (`enc[37:34]`,
  printed only when not all four bytes are enabled), and `sop2wm` always prints one **[RE]**.
  The mask is spelled as the Rogue ISR's element selectors: `.eN` for each enabled byte N, in
  rising order (`r10.e0.e2.e3`), and `.enone` for no byte.
  On a pack, mask bit N enables byte N of the destination, and the others keep their values
  **[HW]** (*Pack and unpack lanes*). `sop2wm`'s mask works the same way **[HW]** (*Colour
  operations*).
- **Repeat counts** (`.repeatN`) are described in *Repeats and the MOE state*.

### 3.4 Source modifiers and data readings

The same register bits are read in several ways, chosen by the instruction **[RE]**:

- **Float sources** take `.neg` and `.abs` (`-|x|` when both, as the emulation models it),
  one bit each next to the operand. Source 0 of the float groups has `.abs` only.
- **Half floats.** With the group's half-float bit (`enc[54]` in classes 0-4) a source number
  of 64-127 names a 16-bit half of a 32-bit register, `(n - 64) / 2`, printed with a
  component suffix: `.flt16.0`/`.flt16.2` for the low and high half (`fsubflr` and the third
  operand of the dot products print `.flt16` and `.flt16.2`). Numbers below 64 keep their
  32-bit reading, and in that reading the temporaries stop at `r29`.

`fmad r0, r1.flt16.0, r2.flt16.2, r3.flt16.0` assembles with form #42: enc[63:32] = `0x00600000`,
enc[31:0] = `0x0010A2C6`; in memory (little endian) `C6 A2 10 00 00 00 60 00`.

| field | value | prints |
|---|---|---|
| `pred` | 0x0 | (none) |
| `op` | 0x0 | `fmad` |
| `flags` | 0x0 | (none) |
| `repeat` | 0x0 | (none) |
| `incs` | 0x1 | (none) |
| `dst` | 0x0 | `r0` |
| `src0` | 0x42 | `r1.flt16.0` |
| `src1` | 0x45 | `r2.flt16.2` |
| `src2` | 0x46 | `r3.flt16.0` |

- **c10** is a 10-bit fixed-point colour reading (`.c10`): number bit 6 selects it in the
  colour, dot-product and `fpma` groups and in some float tests. It reads three signed 10-bit
  lanes, 1.0 = 255 **[HW]** (*Colour operations*).
- **Integer halves and components.** `.low`/`.high` pick a 16-bit half (`imae`, `ima16`,
  `adifsum`); `.0`-`.3` pick a byte or half of a pack/unpack source; `.neg` negates an
  integer source of `ima16`/`ima32`; `.comp` complements a colour-group selector (`1 - x`
  **[infer]**).
- **Swizzles** of `fmad16` (`.swzll`, `.swzhh`, `.swzf32`) select which halves of a source
  feed the two 16-bit lanes **[infer]**.
- **Inverted source.** `~src2` in the bitwise group is the bitwise complement **[RE]** (the
  firmware builds masks with an `xor` against an inverted immediate; the emulation models it).

What each modifier does to a value was never measured on the hardware except where a group
section says so.

## 4. Assembler syntax

The syntax is the one our disassembler prints, so
that `asm(disasm(word))` decodes as `word` and `disasm(asm(text))` gives `text` back
(`tools/usse-asm/README.md`). One statement per line:

| statement | meaning |
|-----------|---------|
| `p0 mov.skipinv.end o0, #0x12345678` | an instruction: predicate, mnemonic, modifiers, operands |
| `.long 0x0123456789ABCDEF` | a raw 64-bit word (several, comma-separated) |
| `name:` | a label, an instruction index; it may share the line with a statement |
| `; ...`, `/* ... */` | comments |
| `12: 0x...\tphas ...` | a disassembler listing line: index and hex columns are ignored |

- **Order.** Predicate, mnemonic, then modifiers in the order the decoder prints them (flags
  before the repeat count, the repeat count before `.incsXYZ`, ...), then the operands. The
  destination's write mask follows the destination (`r1.xz`).
- **Leniency.** Letters match in either case, blanks may vary (around commas too), numbers
  may be decimal or hex, and the `/* incp */` comments the decoder prints are optional.
  Mnemonics, modifiers and register names are otherwise exact.
- **Labels.** `ba #label` takes a label as an absolute instruction index; `br` takes only a
  number, since its offset base is not established.
- **Canonical words.** Text that several words print assembles to one of them: the first form
  in table order and, within it, zeros for ignored bits, except where the captured programs
  show a convention (an unused source 2 written as immediate 0, the unprinted sources of
  the vertex-side emits). With those, every decoded word of the microkernel and of our
  programs reassembles bit for bit.

Our programs in `asm/` are written in this syntax; `make -C tools/usse-asm`
builds the assembler, `tools/usse-asm/usse-asm -l prog.s` prints a listing.

## 5. Assembling, disassembling and running

Three tools cover a program's life: the assembler and the disassembler exist in C (`tools/`) and
in Rust (`crates/sgx-tools`), the two held byte for byte to each other, and the simulator in Rust
only:

- **`usse-asm`** assembles source in the syntax above into raw little-endian 64-bit words;
  `-l` lists each word with its text. Labels name instruction indices, so branches and
  `lapc` targets can be written by name.
- **`usse-dis`** prints a blob of words, one instruction per line, as the assembler reads it
  back; any decodable word round-trips through the two.
- **`sgx-sim`** runs a program on the simulator, as one instance or as the 2x2 quad of a pixel
  (`--quad X,Y`), and prints every register it wrote and every scratch dword it changed;
  `--trace` shows each instruction with its writes, `--set REG=VALUE` presets registers (and
  `pclink`; a preset predicate counts as written), `--task vertex` runs a vertex task (the
  default is a pixel task), `--near` lets the float functions give their near values and
  `--vectors FILE` runs hardware
  vectors (the data repository's `vectors/`). It stops, with the reason, at the first instruction
  whose behaviour
  is not established.

```
$ printf 'mov r1, #0x5caf0010\nmov r2, #7\nstad [r1,+#0], r2\nmov.end o0, r2\n' |
    cargo run -q -p sgx-tools --bin sgx-sim -- --trace -
0: mov r1, #0x3E003010
    r1 = 0x3e003010
1: mov r2, #0x00000007
    r2 = 0x00000007
2: stad [r1,+#0], r2
    [0x3e003010] = 0x00000007
3: mov.end o0, r2
    o0 = 0x00000007
ended after 4 steps
```

The simulator's memory is the probe harness's scratch buffer (64 KiB at `0x3e003000`, and a
`limm` of `0x5cafnnnn` loads its address + `nnnn`), so a probe program runs unchanged; our own
pixel, vertex and state programs are in `asm/`.

## 6. Syntax index

Every mnemonic the assembler reads, with the operand syntax of each form shape it can
take, generated from the encoder's own patterns. `usse-asm --explain` prints the closest
of these lines when a source line does not assemble.

Fields are `<name>`; a mnemonic in `<op>` is printed by an operation field, and
`+name` is the second operation of a dual-issue or dot form.

```
+aadd        <pred>u8dot3<op><flags> <dst>, Cx<cx>, <src1>, <src2>+<sop1> Ax<sax>, <sop2>
adif         <pred>adif<flags> <dst>, <src1>, <src2>
adifsum      <pred>adifsum<flags> <dst>, <src0>.<half>, <src1>, <src2>
+alrp        <pred>sop3<flags> <dst>, <src0>, <src1>, <src2>, <op>+alrp <sop>
+alrp        <pred>sop3c<flags> <dst>, <src0>, <src1>, <src2>, <op>+alrp <sop>
+alrp        <pred>u8dot3<op><flags> <dst>, Cx<cx>, <src1>, <src2>+<sop1> <ssrc0>, <sop2>
+alrpc       <pred>u8dot3<op><flags> <dst>, Cx<cx>, <src1>, <src2>+<sop1> <ssrc0>, <sop2>
and          <pred><op><flags> <dst><wmask>, <src1>, <inv>#<imm>
and          <pred><op><flags><repeat> <dst>, <src1>, <inv>#<imm>
and          <pred><op><flags> <dst><wmask>, <src1>, <inv><src2>
and          <pred><op><flags><repeat> <dst>, <src1>, <inv><src2>
and          <pred><op><flags>.<test> <w><dst><wmask>, p<p>, <src1>, <src2>
and          <pred><op><flags>.<test> <w><dst><wmask>, <src1>, <src2>
+arsop       <pred>sop3<flags> <dst>, <src0>, <src1>, <src2>, <op>+arsop <sop>
+asop        <pred>sop3<flags> <dst>, <src0>, <src1>, <src2>, <op>+asop <sop>
+asop        <pred>lrp<flags> <dst>, <src0>, <src1>, <src2>, <op>+asop <sop>
+asop2       <pred>sop2<flags> <dst>, <src1>, <src2>, <op>+asop2 <sop>
asr          <pred><op><flags> <dst><wmask>, <src1>, <inv>#<imm>
asr          <pred><op><flags><repeat> <dst>, <src1>, <inv>#<imm>
asr          <pred><op><flags> <dst><wmask>, <src1>, <inv><src2>
asr          <pred><op><flags><repeat> <dst>, <src1>, <inv><src2>
asr          <pred><op><flags>.<test> <w><dst><wmask>, p<p>, <src1>, <src2>
asr          <pred><op><flags>.<test> <w><dst><wmask>, <src1>, <src2>
+asub        <pred>u8dot3<op><flags> <dst>, Cx<cx>, <src1>, <src2>+<sop1> Ax<sax>, <sop2>
atst8        <pred>atst8<flags> <dst>, <w>p<p>, <src0>, <src1>, <src2><extra><op>
ba           <pred>ba<flags> #<imm>
bexception   <pred>bexception<flags> #<imm>
bexception   <pred>bexception.rel<flags> <imm>
bilin        <pred>bilin<flags> <dst>, <src0>, <src1>, <src2>, <op1>, <op2>, <op3><extra>
br           <pred>br<flags> <imm>
cf           <op><flags> <src1>, <src2>, #<imm>
cfi          <op><flags> <src1>, <src2>, #<imm>
ci           <op><flags> <src1>, <src2>, #<imm>
depthf       <pred>depthf<flags> <src0>, <src1>, <src2><extra><op>
efo          <pred>efo<flags> <dst>= <reg>, <f4>, <op1>, <op2>, <src0>, <src1>, <src2>
eldd         <pred>eld<op><flags> <dst>, [<base>, <src0>, #<imm>], <src2>, drc<drc>
eldq         <pred>eld<op><flags> <dst>, [<base>, <src0>, #<imm>], <src2>, drc<drc>
emitmtest    emitmtest<nosched><end><twopart><freep> #<imm> /* incp */, <src1>, <src2>
emitmtevtx   emitmtevtx<nosched><end><twopart><cut><freep> #<imm> /* incp */, <src1>, <src2>
emitpds      emitpds<nosched><end><tasks><taske><freep> #<imm1> /* incp */, <src0>, <src1>,
                <src2>, #<imm2>
emitpix1     emitpix1<nosched><end><freep> #<imm> /* incp */, <src0>, <src1>
emitpix2     emitpix2<nosched><end><freep> #<imm1> /* incp */, <src0>, <src1>, <src2>, #<imm2>
emitvcbst    emitvcbst<nosched><end><twopart><freep> #<imm> /* incp */, <src2>
emitvcbvtx   emitvcbvtx<nosched><end><twopart><freep> #<imm> /* incp */, <src2>
+fadd        <pred><op> <dst>, <src0>, <src1>, <src2>+<sop> <sreg>, <ssrc1>, <ssrc2>
+fadd        <pred><op> <dst>, <src1>+<sop> <sreg>, <ssrc1>, <ssrc2>
+fadd        <pred><op> <dst>, i0, <src0>, <src1>, <src2>+<sop> <sreg>, <ssrc1>, <ssrc2>
+fadd        <pred><op> <dst>, <src1>, <src2>+<sop> <sreg>, <ssrc1>, <ssrc2>
fadd         <pred><op><flags>.<test> <w><dst><wmask>, p<p>, <src1>, <src2>
fadd         <pred><op><flags>.<test> <w><dst><wmask>, <src1>, <src2>
fadm         <pred><op><flags><repeat><incs> <dst>, <src0>, <src1>, <src2>
fadm         <pred><op> <dst>, <src0>, <src1>, <src2>+<sop> <ssrc0>, <ssrc1>, <ssrc2>
fadm         <pred><op> <dst>, <src0>, <src1>, <src2>+<sop> <sreg>, <ssrc1>, <ssrc2>
fadm         <pred><op> <dst>, <src0>, <src1>, <src2>+<sop> <sreg>, <ssrc1>
fadm         <pred><op> <dst>, <src0>, <src1>, <src2>+<sop> <sreg>, <ssrc0>
fadm         <pred><op> <dst>, <src0>, <src1>, <src2>+<sop> <sreg>, <ssrc2>
+fcos        <pred><op> <dst>, <src0>, <src1>, <src2>+<sop> <sreg>, <ssrc1>
+fcos        <pred><op> <dst>, <src1>+<sop> <sreg>, <ssrc1>
+fcos        <pred><op> <dst>, i0, <src0>, <src1>, <src2>+<sop> <sreg>, <ssrc1>
+fcos        <pred><op> <dst>, <src1>, <src2>+<sop> <sreg>, <ssrc1>
fcos         <pred><op><flags1> <dst><wmask>, <src1><flags2>
fcos         <pred><op><flags1><repeat> <dst>, <src1><flags2>
fddp         <pred>fddp<flags><repeat><incs> <dst>, i<i>, <src0>, <src1>, <src2>
fddp         <pred><op> <dst>, i0, <src0>, <src1>, <src2>+<sop> <ssrc0>, <ssrc1>, <ssrc2>
fddp         <pred><op> <dst>, i0, <src0>, <src1>, <src2>+<sop> <sreg>, <ssrc1>, <ssrc2>
fddp         <pred><op> <dst>, i0, <src0>, <src1>, <src2>+<sop> <sreg>, <ssrc1>
fddp         <pred><op> <dst>, i0, <src0>, <src1>, <src2>+<sop> <sreg>, <ssrc0>
fddp         <pred><op> <dst>, i0, <src0>, <src1>, <src2>+<sop> <sreg>, <ssrc2>
fddpc        <pred>fddpc<flags><repeat> <dst>, i<i>, cp<cp1>, cp<cp2>, <src0>, <src1>, <src2>
fdp          <pred><op><flags>.<test> <w><dst><wmask>, p<p>, <src1>, <src2>
fdp          <pred>fdp<flags><repeat><incs> <dst>, <src1>, <src2>
fdp          <pred><op><flags>.<test> <w><dst><wmask>, <src1>, <src2>
fdpc         <pred>fdpc<flags><repeat><incs> <dst>, cp<cp>, <src1>, <src2>
fdsx         <pred><op><flags>.<test> <w><dst><wmask>, p<p>, <src1>, <src2>
fdsx         <pred><op><flags><repeat><incs> <dst>, <src1>, <src2>
fdsx         <pred><op><flags>.<test> <w><dst><wmask>, <src1>, <src2>
fdsy         <pred><op><flags>.<test> <w><dst><wmask>, p<p>, <src1>, <src2>
fdsy         <pred><op><flags><repeat><incs> <dst>, <src1>, <src2>
fdsy         <pred><op><flags>.<test> <w><dst><wmask>, <src1>, <src2>
+fexp        <pred><op> <dst>, <src0>, <src1>, <src2>+<sop> <sreg>, <ssrc1>
+fexp        <pred><op> <dst>, <src1>+<sop> <sreg>, <ssrc1>
+fexp        <pred><op> <dst>, i0, <src0>, <src1>, <src2>+<sop> <sreg>, <ssrc1>
+fexp        <pred><op> <dst>, <src1>, <src2>+<sop> <sreg>, <ssrc1>
fexp         <pred><op><flags>.<test> <w><dst><wmask>, p<p>, <src1>
fexp         <pred><op><flags1> <dst><wmask>, <src1><flags2>
fexp         <pred><op><flags1><repeat> <dst>, <src1><flags2>
fexp         <pred><op><flags>.<test> <w><dst><wmask>, <src1>
firh         <pred>firh<flags> <dst>, <src0>, <src2>, <op1>, <op2>, #<imm1>, #<imm2>
firv         <pred>firv<flags> <w><dst>, <src0>, <src2>, <op><extra>
+flog        <pred><op> <dst>, <src0>, <src1>, <src2>+<sop> <sreg>, <ssrc1>
+flog        <pred><op> <dst>, <src1>+<sop> <sreg>, <ssrc1>
+flog        <pred><op> <dst>, i0, <src0>, <src1>, <src2>+<sop> <sreg>, <ssrc1>
+flog        <pred><op> <dst>, <src1>, <src2>+<sop> <sreg>, <ssrc1>
flog         <pred><op><flags>.<test> <w><dst><wmask>, p<p>, <src1>
flog         <pred><op><flags1> <dst><wmask>, <src1><flags2>
flog         <pred><op><flags1><repeat> <dst>, <src1><flags2>
flog         <pred><op><flags>.<test> <w><dst><wmask>, <src1>
+fmad        <pred><op> <dst>, <src0>, <src1>, <src2>+<sop> <ssrc0>, <ssrc1>, <ssrc2>
+fmad        <pred><op> <dst>, <src1>+<sop> <ssrc0>, <ssrc1>, <ssrc2>
+fmad        <pred><op> <dst>, i0, <src0>, <src1>, <src2>+<sop> <ssrc0>, <ssrc1>, <ssrc2>
+fmad        <pred><op> <dst>, <src1>, <src2>+<sop> <ssrc0>, <ssrc1>, <ssrc2>
fmad         <pred><op><flags><repeat><incs> <dst>, <src0>, <src1>, <src2>
fmad         <pred><op> <dst>, <src0>, <src1>, <src2>+<sop> <ssrc0>, <ssrc1>, <ssrc2>
fmad         <pred><op> <dst>, <src0>, <src1>, <src2>+<sop> <sreg>, <ssrc1>, <ssrc2>
fmad         <pred><op> <dst>, <src0>, <src1>, <src2>+<sop> <sreg>, <ssrc1>
fmad         <pred><op> <dst>, <src0>, <src1>, <src2>+<sop> <sreg>, <ssrc0>
fmad         <pred><op> <dst>, <src0>, <src1>, <src2>+<sop> <sreg>, <ssrc2>
+fmad16      <pred><op> <dst>, <src0>, <src1>, <src2>+<sop> <ssrc0>, <ssrc1>, <ssrc2>
+fmad16      <pred><op> <dst>, <src1>+<sop> <ssrc0>, <ssrc1>, <ssrc2>
+fmad16      <pred><op> <dst>, i0, <src0>, <src1>, <src2>+<sop> <ssrc0>, <ssrc1>, <ssrc2>
+fmad16      <pred><op> <dst>, <src1>, <src2>+<sop> <ssrc0>, <ssrc1>, <ssrc2>
fmad16       <pred>fmad16<flags1><flags2> <dst>, <src0><flags3>, <src1><flags4>, <src2><flags5>
fmax         <pred><op><flags>.<test> <w><dst><wmask>, p<p>, <src1>, <src2>
fmax         <pred><op><flags>.<test> <w><dst><wmask>, <src1>, <src2>
+fmaxmin     <pred><op> <dst>, <src0>, <src1>, <src2>+<sop> <ssrc0>, <ssrc1>, <ssrc2>
+fmaxmin     <pred><op> <dst>, <src1>+<sop> <ssrc0>, <ssrc1>, <ssrc2>
+fmaxmin     <pred><op> <dst>, i0, <src0>, <src1>, <src2>+<sop> <ssrc0>, <ssrc1>, <ssrc2>
+fmaxmin     <pred><op> <dst>, <src1>, <src2>+<sop> <ssrc0>, <ssrc1>, <ssrc2>
fmaxmin      <pred><op><flags><repeat><incs> <dst>, <src0>, <src1>, <src2>
fmin         <pred><op><flags>.<test> <w><dst><wmask>, p<p>, <src1>, <src2>
fmin         <pred><op><flags>.<test> <w><dst><wmask>, <src1>, <src2>
fminmax      <pred><op><flags><repeat><incs> <dst>, <src0>, <src1>, <src2>
fminmax      <pred><op> <dst>, <src0>, <src1>, <src2>+<sop> <ssrc0>, <ssrc1>, <ssrc2>
fminmax      <pred><op> <dst>, <src0>, <src1>, <src2>+<sop> <sreg>, <ssrc1>, <ssrc2>
fminmax      <pred><op> <dst>, <src0>, <src1>, <src2>+<sop> <sreg>, <ssrc1>
fminmax      <pred><op> <dst>, <src0>, <src1>, <src2>+<sop> <sreg>, <ssrc0>
fminmax      <pred><op> <dst>, <src0>, <src1>, <src2>+<sop> <sreg>, <ssrc2>
+fmsa        <pred><op> <dst>, <src0>, <src1>, <src2>+<sop> <ssrc0>, <ssrc1>, <ssrc2>
+fmsa        <pred><op> <dst>, <src1>+<sop> <ssrc0>, <ssrc1>, <ssrc2>
+fmsa        <pred><op> <dst>, i0, <src0>, <src1>, <src2>+<sop> <ssrc0>, <ssrc1>, <ssrc2>
+fmsa        <pred><op> <dst>, <src1>, <src2>+<sop> <ssrc0>, <ssrc1>, <ssrc2>
fmsa         <pred><op><flags><repeat><incs> <dst>, <src0>, <src1>, <src2>
fmsa         <pred><op> <dst>, <src0>, <src1>, <src2>+<sop> <ssrc0>, <ssrc1>, <ssrc2>
fmsa         <pred><op> <dst>, <src0>, <src1>, <src2>+<sop> <sreg>, <ssrc1>, <ssrc2>
fmsa         <pred><op> <dst>, <src0>, <src1>, <src2>+<sop> <sreg>, <ssrc1>
fmsa         <pred><op> <dst>, <src0>, <src1>, <src2>+<sop> <sreg>, <ssrc0>
fmsa         <pred><op> <dst>, <src0>, <src1>, <src2>+<sop> <sreg>, <ssrc2>
+fmul        <pred><op> <dst>, <src0>, <src1>, <src2>+<sop> <sreg>, <ssrc1>, <ssrc2>
+fmul        <pred><op> <dst>, <src1>+<sop> <sreg>, <ssrc1>, <ssrc2>
+fmul        <pred><op> <dst>, i0, <src0>, <src1>, <src2>+<sop> <sreg>, <ssrc1>, <ssrc2>
+fmul        <pred><op> <dst>, <src1>, <src2>+<sop> <sreg>, <ssrc1>, <ssrc2>
fmul         <pred><op><flags>.<test> <w><dst><wmask>, p<p>, <src1>, <src2>
fmul         <pred><op><flags>.<test> <w><dst><wmask>, <src1>, <src2>
fpadd8       <pred><op><flags>.<test> <w><dst><wmask>, p<p>, <src1>, <src2>
fpadd8       <pred><op><flags>.<test> <w><dst><wmask>, <src1>, <src2>
fpma         <pred>fpma<flags> <dst>, <src0>, <src1>, <src2>, <op1>, <op2>
fpmul8       <pred><op><flags>.<test> <w><dst><wmask>, p<p>, <src1>, <src2>
fpmul8       <pred><op><flags>.<test> <w><dst><wmask>, <src1>, <src2>
fpsub8       <pred><op><flags>.<test> <w><dst><wmask>, p<p>, <src1>, <src2>
fpsub8       <pred><op><flags>.<test> <w><dst><wmask>, <src1>, <src2>
+frcp        <pred><op> <dst>, <src0>, <src1>, <src2>+<sop> <sreg>, <ssrc1>
+frcp        <pred><op> <dst>, <src1>+<sop> <sreg>, <ssrc1>
+frcp        <pred><op> <dst>, i0, <src0>, <src1>, <src2>+<sop> <sreg>, <ssrc1>
+frcp        <pred><op> <dst>, <src1>, <src2>+<sop> <sreg>, <ssrc1>
frcp         <pred><op><flags>.<test> <w><dst><wmask>, p<p>, <src1>
frcp         <pred><op><flags1> <dst><wmask>, <src1><flags2>
frcp         <pred><op><flags1><repeat> <dst>, <src1><flags2>
frcp         <pred><op><flags>.<test> <w><dst><wmask>, <src1>
+frsq        <pred><op> <dst>, <src0>, <src1>, <src2>+<sop> <sreg>, <ssrc1>
+frsq        <pred><op> <dst>, <src1>+<sop> <sreg>, <ssrc1>
+frsq        <pred><op> <dst>, i0, <src0>, <src1>, <src2>+<sop> <sreg>, <ssrc1>
+frsq        <pred><op> <dst>, <src1>, <src2>+<sop> <sreg>, <ssrc1>
frsq         <pred><op><flags>.<test> <w><dst><wmask>, p<p>, <src1>
frsq         <pred><op><flags1> <dst><wmask>, <src1><flags2>
frsq         <pred><op><flags1><repeat> <dst>, <src1><flags2>
frsq         <pred><op><flags>.<test> <w><dst><wmask>, <src1>
+fsin        <pred><op> <dst>, <src0>, <src1>, <src2>+<sop> <sreg>, <ssrc1>
+fsin        <pred><op> <dst>, <src1>+<sop> <sreg>, <ssrc1>
+fsin        <pred><op> <dst>, i0, <src0>, <src1>, <src2>+<sop> <sreg>, <ssrc1>
+fsin        <pred><op> <dst>, <src1>, <src2>+<sop> <sreg>, <ssrc1>
fsin         <pred><op><flags1> <dst><wmask>, <src1><flags2>
fsin         <pred><op><flags1><repeat> <dst>, <src1><flags2>
fsqrt        <pred><op><flags1> <dst><wmask>, <src1><flags2>
fsqrt        <pred><op><flags1><repeat> <dst>, <src1><flags2>
fssq         <pred><op> <dst>, <src1>, <src2>+<sop> <ssrc0>, <ssrc1>, <ssrc2>
fssq         <pred><op> <dst>, <src1>, <src2>+<sop> <sreg>, <ssrc1>, <ssrc2>
fssq         <pred><op> <dst>, <src1>, <src2>+<sop> <sreg>, <ssrc1>
fssq         <pred><op> <dst>, <src1>, <src2>+<sop> <sreg>, <ssrc0>
fssq         <pred><op> <dst>, <src1>, <src2>+<sop> <sreg>, <ssrc2>
+fsub        <pred><op> <dst>, <src0>, <src1>, <src2>+<sop> <sreg>, <ssrc1>, <ssrc2>
+fsub        <pred><op> <dst>, <src1>+<sop> <sreg>, <ssrc1>, <ssrc2>
+fsub        <pred><op> <dst>, i0, <src0>, <src1>, <src2>+<sop> <sreg>, <ssrc1>, <ssrc2>
+fsub        <pred><op> <dst>, <src1>, <src2>+<sop> <sreg>, <ssrc1>, <ssrc2>
fsub         <pred><op><flags>.<test> <w><dst><wmask>, p<p>, <src1>, <src2>
fsub         <pred><op><flags>.<test> <w><dst><wmask>, <src1>, <src2>
+fsubflr     <pred><op> <dst>, <src0>, <src1>, <src2>+<sop> <sreg>, <ssrc1>, <ssrc2>
+fsubflr     <pred><op> <dst>, <src1>+<sop> <sreg>, <ssrc1>, <ssrc2>
+fsubflr     <pred><op> <dst>, i0, <src0>, <src1>, <src2>+<sop> <sreg>, <ssrc1>, <ssrc2>
+fsubflr     <pred><op> <dst>, <src1>, <src2>+<sop> <sreg>, <ssrc1>, <ssrc2>
fsubflr      <pred><op><flags>.<test> <w><dst><wmask>, p<p>, <src1>, <src2>
fsubflr      <pred>fsubflr<flags><repeat><incs> <dst>, <src1>, <src2>
fsubflr      <pred><op><flags>.<test> <w><dst><wmask>, <src1>, <src2>
iadd16       <pred><op><flags>.<test> <w><dst><wmask>, p<p>, <src1>, <src2>
iadd16       <pred><op><flags>.<test> <w><dst><wmask>, <src1>, <src2>
iadd32       <pred><op><flags>.<test> <w><dst><wmask>, p<p>, <src1>, <src2>
iadd32       <pred><op><flags>.<test> <w><dst><wmask>, <src1>, <src2>
iadd8        <pred><op><flags>.<test> <w><dst><wmask>, p<p>, <src1>, <src2>
iadd8        <pred><op><flags>.sat.<test> <w><dst><wmask>, p<p>, <src1>, <src2>
iadd8        <pred><op><flags>.<test> <w><dst><wmask>, <src1>, <src2>
iadd8        <pred><op><flags>.sat.<test> <w><dst><wmask>, <src1>, <src2>
iaddu32      <pred><op><flags>.<test> <w><dst><wmask>, p<p>, <src1>, <src2>
iaddu32      <pred><op><flags>.<test> <w><dst><wmask>, <src1>, <src2>
idf          idf drc<drc>, bif
idf          idf<nosched> drc<drc>, <op>
idiv         <pred>idiv<flags> <dst>, <src1>, <src2>, drc<drc>
ima16        <pred>ima16<flags>.<type><rs> <dst><abs>, <src0>, <src1>, <src2><neg>, u16, u16
ima16        <pred>ima16<flags>.<type><rs> <dst><abs>, <src0>, <src1>, <src2>, <op>
+ima32       <pred><op> <dst>, <src0>, <src1>, <src2>+<sop> <ssrc0>, <ssrc1>, <ssrc2>
+ima32       <pred><op> <dst>, <src1>+<sop> <ssrc0>, <ssrc1>, <ssrc2>
+ima32       <pred><op> <dst>, i0, <src0>, <src1>, <src2>+<sop> <ssrc0>, <ssrc1>, <ssrc2>
+ima32       <pred><op> <dst>, <src1>, <src2>+<sop> <ssrc0>, <ssrc1>, <ssrc2>
ima32        <pred>ima32<flags>.<type> <dst>, <src0>, <src1><neg1>, <src2><neg2>
ima32        <pred><op> <dst>, <src0>, <src1>, <src2>+<sop> <ssrc0>, <ssrc1>, <ssrc2>
ima32        <pred><op> <dst>, <src0>, <src1>, <src2>+<sop> <sreg>, <ssrc1>, <ssrc2>
ima32        <pred><op> <dst>, <src0>, <src1>, <src2>+<sop> <sreg>, <ssrc1>
ima32        <pred><op> <dst>, <src0>, <src1>, <src2>+<sop> <sreg>, <ssrc0>
ima32        <pred><op> <dst>, <src0>, <src1>, <src2>+<sop> <sreg>, <ssrc2>
ima32        <pred>ima32<flags>.<type> <dst><extra1>, <src0>, <src1>, <src2><extra2>
ima8         <pred>ima8<flags><sat> <dst>, <src0>, <src1>, <src2>, <op>
imae         <pred>imae<flags>.<type><rs> <dst>, <src0>.<half1>, <src1>.<half2>, <src2>, u32
imae         <pred>imae<flags>.<type><rs> <dst>, <src0>, <src1>, <src2>, <op>
imo          imo<nosched> #<imm1>, #<imm2>, #<imm3>, #<imm4>
imul16       <pred><op><flags>.<test> <w><dst><wmask>, p<p>, <src1>, <src2>
imul16       <pred><op><flags>.<test> <w><dst><wmask>, <src1>, <src2>
imul8        <pred><op><flags>.<test> <w><dst><wmask>, p<p>, <src1>, <src2>
imul8        <pred><op><flags>.sat.<test> <w><dst><wmask>, p<p>, <src1>, <src2>
imul8        <pred><op><flags>.<test> <w><dst><wmask>, <src1>, <src2>
imul8        <pred><op><flags>.sat.<test> <w><dst><wmask>, <src1>, <src2>
isub16       <pred><op><flags>.<test> <w><dst><wmask>, p<p>, <src1>, <src2>
isub16       <pred><op><flags>.<test> <w><dst><wmask>, <src1>, <src2>
isub8        <pred><op><flags>.<test> <w><dst><wmask>, p<p>, <src1>, <src2>
isub8        <pred><op><flags>.sat.<test> <w><dst><wmask>, p<p>, <src1>, <src2>
isub8        <pred><op><flags>.<test> <w><dst><wmask>, <src1>, <src2>
isub8        <pred><op><flags>.sat.<test> <w><dst><wmask>, <src1>, <src2>
lapc         <pred>lapc<flags>
ldab         <pred>ld<op><flags> <dst>, [<base>,<mode><sign><src1>]<extra>, drc<drc>
ldab         <pred>ld<op><flags> <dst>, [<base>,<step><src1>]<extra>, drc<drc>
ldab         <pred>ld<op><flags> <dst>, [<base>,<src1><step>]<extra>, drc<drc>
ldad         <pred>ld<op><flags> <dst>, [<base>,<mode><sign><src1>]<extra>, drc<drc>
ldad         <pred>ld<op><flags> <dst>, [<base>,<step><src1>]<extra>, drc<drc>
ldad         <pred>ld<op><flags> <dst>, [<base>,<src1><step>]<extra>, drc<drc>
ldaw         <pred>ld<op><flags> <dst>, [<base>,<mode><sign><src1>]<extra>, drc<drc>
ldaw         <pred>ld<op><flags> <dst>, [<base>,<step><src1>]<extra>, drc<drc>
ldaw         <pred>ld<op><flags> <dst>, [<base>,<src1><step>]<extra>, drc<drc>
ldlb         <pred>ld<op><flags> <dst>, [<base>,<mode><sign><src1>]<extra>, drc<drc>
ldlb         <pred>ld<op><flags> <dst>, [<base>,<step><src1>]<extra>, drc<drc>
ldlb         <pred>ld<op><flags> <dst>, [<base>,<src1><step>]<extra>, drc<drc>
ldld         <pred>ld<op><flags> <dst>, [<base>,<mode><sign><src1>]<extra>, drc<drc>
ldld         <pred>ld<op><flags> <dst>, [<base>,<step><src1>]<extra>, drc<drc>
ldld         <pred>ld<op><flags> <dst>, [<base>,<src1><step>]<extra>, drc<drc>
ldlw         <pred>ld<op><flags> <dst>, [<base>,<mode><sign><src1>]<extra>, drc<drc>
ldlw         <pred>ld<op><flags> <dst>, [<base>,<step><src1>]<extra>, drc<drc>
ldlw         <pred>ld<op><flags> <dst>, [<base>,<src1><step>]<extra>, drc<drc>
ldr          ldr<flags> <dst>, #<imm>, drc<drc>
ldr          ldr<flags> <dst>, <src2>, drc<drc>
ldtb         <pred>ld<op><flags> <dst>, [<base>,<mode><sign><src1>]<extra>, drc<drc>
ldtb         <pred>ld<op><flags> <dst>, [<base>,<step><src1>]<extra>, drc<drc>
ldtb         <pred>ld<op><flags> <dst>, [<base>,<src1><step>]<extra>, drc<drc>
ldtd         <pred>ld<op><flags> <dst>, [<base>,<mode><sign><src1>]<extra>, drc<drc>
ldtd         <pred>ld<op><flags> <dst>, [<base>,<step><src1>]<extra>, drc<drc>
ldtd         <pred>ld<op><flags> <dst>, [<base>,<src1><step>]<extra>, drc<drc>
ldtw         <pred>ld<op><flags> <dst>, [<base>,<mode><sign><src1>]<extra>, drc<drc>
ldtw         <pred>ld<op><flags> <dst>, [<base>,<step><src1>]<extra>, drc<drc>
ldtw         <pred>ld<op><flags> <dst>, [<base>,<src1><step>]<extra>, drc<drc>
lock         <op><nosched> #<imm>
lrp          <pred>lrp<flags> <dst>, <src0>, <src1>, <src2>, <op>+asop <sop>
moest        moest<skipinv><nosched> <dst>, #<imm>
+mov         <pred><op> <dst>, <src0>, <src1>, <src2>+<sop> <sreg>, <ssrc0>
+mov         <pred><op> <dst>, <src0>, <src1>, <src2>+<sop> <sreg>, <ssrc1>
+mov         <pred><op> <dst>, <src0>, <src1>, <src2>+<sop> <sreg>, <ssrc2>
+mov         <pred><op> <dst>, <src1>+<sop> <sreg>, <ssrc0>
+mov         <pred><op> <dst>, <src1>+<sop> <sreg>, <ssrc1>
+mov         <pred><op> <dst>, <src1>+<sop> <sreg>, <ssrc2>
+mov         <pred><op> <dst>, i0, <src0>, <src1>, <src2>+<sop> <sreg>, <ssrc0>
+mov         <pred><op> <dst>, i0, <src0>, <src1>, <src2>+<sop> <sreg>, <ssrc1>
+mov         <pred><op> <dst>, i0, <src0>, <src1>, <src2>+<sop> <sreg>, <ssrc2>
+mov         <pred><op> <dst>, <src1>, <src2>+<sop> <sreg>, <ssrc0>
+mov         <pred><op> <dst>, <src1>, <src2>+<sop> <sreg>, <ssrc1>
+mov         <pred><op> <dst>, <src1>, <src2>+<sop> <sreg>, <ssrc2>
mov          <pred>mov<skipinv><nosched><end> <dst>, #<imm>
mov          <pred>mov<skipinv><syncs><nosched><end> <dst><wmask>, <src1>
mov          <pred>mov<skipinv><syncs><nosched><end><repeat> <dst>, <src1>
mov          mov pclink, <src1>
mov          mov <dst>, pclink
mov          <pred><op> <dst>, <src1>+<sop> <ssrc0>, <ssrc1>, <ssrc2>
mov          <pred><op> <dst>, <src1>+<sop> <sreg>, <ssrc1>, <ssrc2>
mov          <pred><op> <dst>, <src1>+<sop> <sreg>, <ssrc1>
mov          <pred><op> <dst>, <src1>+<sop> <sreg>, <ssrc0>
mov          <pred><op> <dst>, <src1>+<sop> <sreg>, <ssrc2>
mov          <pred>mov<nosched> pclink, <src1>
mov          <pred>mov<nosched> <dst>, pclink
movc         <pred>movc<flags1><flags2><flags3> <dst><wmask>, <src0>, <src1>, <src2>
movc         <pred>movc<flags1><flags2><repeat><flags3> <dst>, <src0>, <src1>, <src2>
movc         <pred>movc<flags1><repeat>.i8<flags2> <dst>, <src0>, <src1>, <src2>
movmsk       <pred>movmsk<flags1><flags2> <dst><wmask>, <src1>, <src2><flags3>
movmsk       <pred>movmsk<flags1><flags2><repeat> <dst>, <src1>, <src2><flags3>
movmsk       <pred>movmsk<flags1><flags2>.smsk <dst><wmask>, <src0>, <src1>, <src2><flags3>
movmsk       <pred>movmsk<flags1><flags2>.smsk<repeat> <dst>, <src0>, <src1>, <src2><flags3>
movmsk       <pred>movmsk<flags1>.u8 <dst><wmask>, <src1>, <src2><flags2>
movmsk       <pred>movmsk<flags1><repeat>.u8 <dst>, <src1>, <src2><flags2>
movmsk       <pred>movmsk<flags1>.smsk.u8 <dst><wmask>, <src0>, <src1>, <src2><flags2>
movmsk       <pred>movmsk<flags1>.smsk<repeat>.u8 <dst>, <src0>, <src1>, <src2><flags2>
nop          nop<syncs><nosched><end><tog><trigger>
or           <pred><op><flags> <dst><wmask>, <src1>, <inv>#<imm>
or           <pred><op><flags><repeat> <dst>, <src1>, <inv>#<imm>
or           <pred><op><flags> <dst><wmask>, <src1>, <inv><src2>
or           <pred><op><flags><repeat> <dst>, <src1>, <inv><src2>
or           <pred><op><flags>.<test> <w><dst><wmask>, p<p>, <src1>, <src2>
or           <pred><op><flags>.<test> <w><dst><wmask>, <src1>, <src2>
pckc10f16    <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
pckc10f16    <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
pckc10f32    <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
pckc10f32    <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
pckc10s16    <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
pckc10s16    <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
pckc10u16    <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
pckc10u16    <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
pckf16f16    <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
pckf16f16    <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
pckf16f32    <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
pckf16f32    <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
pckf16s16    <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
pckf16s16    <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
pckf16u16    <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
pckf16u16    <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
pcko8f16     <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
pcko8f16     <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
pcko8f32     <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
pcko8f32     <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
pcko8s16     <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
pcko8s16     <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
pcko8u16     <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
pcko8u16     <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
pcks16f16    <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
pcks16f16    <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
pcks16f32    <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
pcks16f32    <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
pcks16s16    <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
pcks16s16    <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
pcks16u16    <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
pcks16u16    <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
pcks8f16     <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
pcks8f16     <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
pcks8f32     <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
pcks8f32     <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
pcks8s16     <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
pcks8s16     <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
pcks8u16     <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
pcks8u16     <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
pcku16f16    <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
pcku16f16    <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
pcku16f32    <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
pcku16f32    <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
pcku16s16    <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
pcku16s16    <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
pcku16u16    <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
pcku16u16    <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
pcku8f16     <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
pcku8f16     <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
pcku8f32     <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
pcku8f32     <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
pcku8s16     <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
pcku8s16     <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
pcku8u16     <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
pcku8u16     <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
pcoeff       pcoeff<nosched><end> <src0>, <src1>, <src2>
phas         phas<end> #<imm1>, #<imm2>, <op1>, <op2>, <op3>
phas         phas<nosched><end> <src1>, <src2>
ptoff        ptoff<nosched><end>
release      <op><nosched> #<imm>
rlp          <pred>rlp<flags> <dst><wmask>, <src1>, p<p>
rlp          <pred>rlp<flags><repeat> <dst>, <src1>, p<p>
rol          <pred><op><flags> <dst><wmask>, <src1>, <inv>#<imm>
rol          <pred><op><flags><repeat> <dst>, <src1>, <inv>#<imm>
rol          <pred><op><flags> <dst><wmask>, <src1>, <inv><src2>
rol          <pred><op><flags><repeat> <dst>, <src1>, <inv><src2>
rol          <pred><op><flags>.<test> <w><dst><wmask>, p<p>, <src1>, <src2>
rol          <pred><op><flags>.<test> <w><dst><wmask>, <src1>, <src2>
setfc        setfc<nosched> #<imm1>, #<imm2>
setm         setm<nosched> #<imm>
shl          <pred><op><flags> <dst><wmask>, <src1>, <inv>#<imm>
shl          <pred><op><flags><repeat> <dst>, <src1>, <inv>#<imm>
shl          <pred><op><flags> <dst><wmask>, <src1>, <inv><src2>
shl          <pred><op><flags><repeat> <dst>, <src1>, <inv><src2>
shl          <pred><op><flags>.<test> <w><dst><wmask>, p<p>, <src1>, <src2>
shl          <pred><op><flags>.<test> <w><dst><wmask>, <src1>, <src2>
shr          <pred><op><flags> <dst><wmask>, <src1>, <inv>#<imm>
shr          <pred><op><flags><repeat> <dst>, <src1>, <inv>#<imm>
shr          <pred><op><flags> <dst><wmask>, <src1>, <inv><src2>
shr          <pred><op><flags><repeat> <dst>, <src1>, <inv><src2>
shr          <pred><op><flags>.<test> <w><dst><wmask>, p<p>, <src1>, <src2>
shr          <pred><op><flags>.<test> <w><dst><wmask>, <src1>, <src2>
smbo         smbo<nosched> <src1>, <src2>
smbo         smbo<nosched> #<imm1>, #<imm2>, #<imm3>, #<imm4>
smlsi        smlsi<nosched> <src1>, <src2>
smlsi        smlsi<nosched> <f1>, <f2>, <f3>, <f4><extra>, #<imm1>, #<imm2>, #<imm3>
smoa         smoa<nosched> <src1>, <src2>
smoa         smoa<nosched> #<imm1>, #<imm2>, #<imm3>, #<imm4>, <op1>, <op2>, <op3>, <op4>
smp1d        <pred>smp<op><flags1> <dst><wmask>, <src0><flags2>, <src1>, drc<drc>
smp1d        <pred>smp<op><flags1><repeat> <dst>, <src0><flags2>, <src1>, drc<drc>
smp1dbias    <pred>smp<op><flags1> <dst><wmask>, <src0><flags2>, <src1>, <src2>, drc<drc>
smp1dbias    <pred>smp<op><flags1><repeat> <dst>, <src0><flags2>, <src1>, <src2>, drc<drc>
smp1dgrad    <pred>smp<op><flags1> <dst><wmask>, <src0><flags2>, <src1>, <src2>, drc<drc>
smp1dgrad    <pred>smp<op><flags1><repeat> <dst>, <src0><flags2>, <src1>, <src2>, drc<drc>
smp1dreplace <pred>smp<op><flags1> <dst><wmask>, <src0><flags2>, <src1>, <src2>, drc<drc>
smp1dreplace <pred>smp<op><flags1><repeat> <dst>, <src0><flags2>, <src1>, <src2>, drc<drc>
smp2d        <pred>smp<op><flags1> <dst><wmask>, <src0><flags2>, <src1>, drc<drc>
smp2d        <pred>smp<op><flags1><repeat> <dst>, <src0><flags2>, <src1>, drc<drc>
smp2dbias    <pred>smp<op><flags1> <dst><wmask>, <src0><flags2>, <src1>, <src2>, drc<drc>
smp2dbias    <pred>smp<op><flags1><repeat> <dst>, <src0><flags2>, <src1>, <src2>, drc<drc>
smp2dgrad    <pred>smp<op><flags1> <dst><wmask>, <src0><flags2>, <src1>, <src2>, drc<drc>
smp2dgrad    <pred>smp<op><flags1><repeat> <dst>, <src0><flags2>, <src1>, <src2>, drc<drc>
smp2dreplace <pred>smp<op><flags1> <dst><wmask>, <src0><flags2>, <src1>, <src2>, drc<drc>
smp2dreplace <pred>smp<op><flags1><repeat> <dst>, <src0><flags2>, <src1>, <src2>, drc<drc>
smp3d        <pred>smp<op><flags1> <dst><wmask>, <src0><flags2>, <src1>, drc<drc>
smp3d        <pred>smp<op><flags1><repeat> <dst>, <src0><flags2>, <src1>, drc<drc>
smp3dbias    <pred>smp<op><flags1> <dst><wmask>, <src0><flags2>, <src1>, <src2>, drc<drc>
smp3dbias    <pred>smp<op><flags1><repeat> <dst>, <src0><flags2>, <src1>, <src2>, drc<drc>
smp3dgrad    <pred>smp<op><flags1> <dst><wmask>, <src0><flags2>, <src1>, <src2>, drc<drc>
smp3dgrad    <pred>smp<op><flags1><repeat> <dst>, <src0><flags2>, <src1>, <src2>, drc<drc>
smp3dreplace <pred>smp<op><flags1> <dst><wmask>, <src0><flags2>, <src1>, <src2>, drc<drc>
smp3dreplace <pred>smp<op><flags1><repeat> <dst>, <src0><flags2>, <src1>, <src2>, drc<drc>
smr          smr<nosched> <src1>, <src2>
smr          smr<nosched> #<imm1>, #<imm2>, #<imm3>, #<imm4>
sop2         <pred>sop2<flags> <dst>, <src1>, <src2>, <op>+asop2 <sop>
sop2wm       <pred>sop2wm<flags1> <dst><flags2>, <src1>, <src2>, <op>
sop3         <pred>sop3<flags> <dst>, <src0>, <src1>, <src2>, <op>+asop <sop>
sop3         <pred>sop3<flags> <dst>, <src0>, <src1>, <src2>, <op>+arsop <sop>
sop3         <pred>sop3<flags> <dst>, <src0>, <src1>, <src2>, <op>+alrp <sop>
sop3c        <pred>sop3c<flags> <dst>, <src0>, <src1>, <src2>, <op>+alrp <sop>
stab         <pred>st<op><flags> [<base>,<mode><sign><src1>], <src2>
stab         <pred>st<op><flags> [<base>,<step><src1>], <src2>
stab         <pred>st<op><flags> [<base>,<src1><step>], <src2>
stad         <pred>st<op><flags> [<base>,<mode><sign><src1>], <src2>
stad         <pred>st<op><flags> [<base>,<step><src1>], <src2>
stad         <pred>st<op><flags> [<base>,<src1><step>], <src2>
statomic     <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
statomic     <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
staw         <pred>st<op><flags> [<base>,<mode><sign><src1>], <src2>
staw         <pred>st<op><flags> [<base>,<step><src1>], <src2>
staw         <pred>st<op><flags> [<base>,<src1><step>], <src2>
stlb         <pred>st<op><flags> [<base>,<mode><sign><src1>], <src2>
stlb         <pred>st<op><flags> [<base>,<step><src1>], <src2>
stlb         <pred>st<op><flags> [<base>,<src1><step>], <src2>
stld         <pred>st<op><flags> [<base>,<mode><sign><src1>], <src2>
stld         <pred>st<op><flags> [<base>,<step><src1>], <src2>
stld         <pred>st<op><flags> [<base>,<src1><step>], <src2>
stlw         <pred>st<op><flags> [<base>,<mode><sign><src1>], <src2>
stlw         <pred>st<op><flags> [<base>,<step><src1>], <src2>
stlw         <pred>st<op><flags> [<base>,<src1><step>], <src2>
str          str<flags> #<imm>, <src1>
str          str<flags> <src2>, <src1>
sttb         <pred>st<op><flags> [<base>,<mode><sign><src1>], <src2>
sttb         <pred>st<op><flags> [<base>,<step><src1>], <src2>
sttb         <pred>st<op><flags> [<base>,<src1><step>], <src2>
sttd         <pred>st<op><flags> [<base>,<mode><sign><src1>], <src2>
sttd         <pred>st<op><flags> [<base>,<step><src1>], <src2>
sttd         <pred>st<op><flags> [<base>,<src1><step>], <src2>
sttw         <pred>st<op><flags> [<base>,<mode><sign><src1>], <src2>
sttw         <pred>st<op><flags> [<base>,<step><src1>], <src2>
sttw         <pred>st<op><flags> [<base>,<src1><step>], <src2>
u16dot3      <pred><op1>dot3<op2><flags> <dst>, Cx<cx>, Ax<ax>, <src1>, <src2>
u16dot3      <pred>u16dot3<op><flags> <dst>, Cx<cx>, <src1>, <src2><mode>
u16dot3off   <pred><op1>dot3<op2><flags> <dst>, Cx<cx>, Ax<ax>, <src1>, <src2>
u16dot3off   <pred>u16dot3<op><flags> <dst>, Cx<cx>, <src1>, <src2><mode>
u16dot4      <pred><op1>dot4<op2><flags> <dst>, Cx<cx>, Ax<ax>, <src1>, <src2>
u16dot4off   <pred><op1>dot4<op2><flags> <dst>, Cx<cx>, Ax<ax>, <src1>, <src2>
u8dot3       <pred><op1>dot3<op2><flags> <dst>, Cx<cx>, Ax<ax>, <src1>, <src2>
u8dot3       <pred>u8dot3<op><flags> <dst>, Cx<cx>, <src1>, <src2>+<sop1> Ax<sax>, <sop2>
u8dot3       <pred>u8dot3<op><flags> <dst>, Cx<cx>, <src1>, <src2>+<sop1> <ssrc0>, <sop2>
u8dot3off    <pred><op1>dot3<op2><flags> <dst>, Cx<cx>, Ax<ax>, <src1>, <src2>
u8dot3off    <pred>u8dot3<op><flags> <dst>, Cx<cx>, <src1>, <src2>+<sop1> Ax<sax>, <sop2>
u8dot3off    <pred>u8dot3<op><flags> <dst>, Cx<cx>, <src1>, <src2>+<sop1> <ssrc0>, <sop2>
u8dot4       <pred><op1>dot4<op2><flags> <dst>, Cx<cx>, Ax<ax>, <src1>, <src2>
u8dot4off    <pred><op1>dot4<op2><flags> <dst>, Cx<cx>, Ax<ax>, <src1>, <src2>
uadd16       <pred><op><flags>.<test> <w><dst><wmask>, p<p>, <src1>, <src2>
uadd16       <pred><op><flags>.<test> <w><dst><wmask>, <src1>, <src2>
uadd8        <pred><op><flags>.<test> <w><dst><wmask>, p<p>, <src1>, <src2>
uadd8        <pred><op><flags>.sat.<test> <w><dst><wmask>, p<p>, <src1>, <src2>
uadd8        <pred><op><flags>.<test> <w><dst><wmask>, <src1>, <src2>
uadd8        <pred><op><flags>.sat.<test> <w><dst><wmask>, <src1>, <src2>
umul16       <pred><op><flags>.<test> <w><dst><wmask>, p<p>, <src1>, <src2>
umul16       <pred><op><flags>.<test> <w><dst><wmask>, <src1>, <src2>
umul8        <pred><op><flags>.<test> <w><dst><wmask>, p<p>, <src1>, <src2>
umul8        <pred><op><flags>.sat.<test> <w><dst><wmask>, p<p>, <src1>, <src2>
umul8        <pred><op><flags>.<test> <w><dst><wmask>, <src1>, <src2>
umul8        <pred><op><flags>.sat.<test> <w><dst><wmask>, <src1>, <src2>
unpckc10c10  <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
unpckc10c10  <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
unpckf16c10  <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
unpckf16c10  <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
unpckf16o8   <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
unpckf16o8   <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
unpckf16s8   <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
unpckf16s8   <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
unpckf16u8   <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
unpckf16u8   <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
unpckf32c10  <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
unpckf32c10  <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
unpckf32f16  <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
unpckf32f16  <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
unpckf32f32  <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
unpckf32f32  <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
unpckf32o8   <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
unpckf32o8   <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
unpckf32s16  <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
unpckf32s16  <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
unpckf32s8   <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
unpckf32s8   <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
unpckf32u16  <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
unpckf32u16  <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
unpckf32u8   <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
unpckf32u8   <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
unpcks16c10  <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
unpcks16c10  <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
unpcks16o8   <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
unpcks16o8   <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
unpcks16s8   <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
unpcks16s8   <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
unpcks16u8   <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
unpcks16u8   <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
unpcku16c10  <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
unpcku16c10  <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
unpcku16o8   <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
unpcku16o8   <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
unpcku16s8   <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
unpcku16s8   <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
unpcku16u8   <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
unpcku16u8   <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
unpcku8s8    <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
unpcku8s8    <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
unpcku8u8    <pred><op1> <dst><flags><wmask>, <src1>, <src2>, <op2>
unpcku8u8    <pred><op1><repeat> <dst><flags>, <src1>, <src2>, <op2>
usub16       <pred><op><flags>.<test> <w><dst><wmask>, p<p>, <src1>, <src2>
usub16       <pred><op><flags>.<test> <w><dst><wmask>, <src1>, <src2>
usub8        <pred><op><flags>.<test> <w><dst><wmask>, p<p>, <src1>, <src2>
usub8        <pred><op><flags>.sat.<test> <w><dst><wmask>, p<p>, <src1>, <src2>
usub8        <pred><op><flags>.<test> <w><dst><wmask>, <src1>, <src2>
usub8        <pred><op><flags>.sat.<test> <w><dst><wmask>, <src1>, <src2>
wdf          wdf drc<drc>
wdf          wdf<nosched> drc<drc>
wop          wop<nosched><twopart> #<imm>
xor          <pred><op><flags> <dst><wmask>, <src1>, <inv>#<imm>
xor          <pred><op><flags><repeat> <dst>, <src1>, <inv>#<imm>
xor          <pred><op><flags> <dst><wmask>, <src1>, <inv><src2>
xor          <pred><op><flags><repeat> <dst>, <src1>, <inv><src2>
xor          <pred><op><flags>.<test> <w><dst><wmask>, p<p>, <src1>, <src2>
xor          <pred><op><flags>.<test> <w><dst><wmask>, <src1>, <src2>
```

## 7. Instruction groups

One section per opcode group: what the group does and what is known of it, how the firmware
uses it, its mnemonics and modifiers, and what the simulator models of it. The bit layouts are
in the reference, group by group under the same titles.

### 7.1 Moves: `mov`, the 32-bit immediate and `pclink`

- **`mov dst, src`** (class 5, type `enc[42:40]` = 0) copies a source-1 operand to the
  destination, under a write mask or repeated **[HW]**: our fill shader, copy shader and
  state copies are built from it. A source immediate prints in hex.
- **`mov dst, #imm32`** (class 31) loads a full 32-bit immediate **[HW]**; the driver patches
  colours and PBE words into it.
- **`mov pclink, src`** and **`mov dst, pclink`** save and restore the link register **[RE]**
  (*Program counter, calls and the end of a program*). Two encodings exist for each: a plain one
  with a temporary, and a general one with a predicate, `.nosched` and any operand. `pclink` is 18
  bits wide, so `mov pclink, rN` keeps bits 17:0 of `rN` and a `mov rN, pclink` reads at most
  0x3ffff **[HW]** (E475).

**In the firmware [RE].** `mov` is its most common instruction (1497): 626 immediates into
temporaries (constants, addresses, and the nine address-patch sites the loader fills), moves
between temporaries and the `sa`/`pa` banks, 79 into `i.l`, 79 through indexed `sa`
operands, and the `pclink` traffic of its calls.

Examples, from our programs and assembled fresh:

From `asm/transfer/use_copy.s`:

```
        mov.skipinv.end o0, pa0                 ; o0 = the fetched texel; end
```

`mov.skipinv.repeat4 o0, pa0` assembles with form #2: enc[63:32] = `0x28A13001`, enc[31:0] =
`0xA0000000`; in memory (little endian) `00 00 00 A0 01 30 A1 28`.

| field | value | prints |
|---|---|---|
| `pred` | 0x0 | (none) |
| `skipinv` | 0x1 | `.skipinv` |
| `syncs` | 0x0 | (none) |
| `nosched` | 0x0 | (none) |
| `end` | 0x0 | (none) |
| `repeat` | 0x3 | `.repeat4` |
| `dst` | 0x80 | `o0` |
| `src1` | 0x100 | `pa0` |

Mnemonics: `mov`.

Modifiers: `.end`, `.nosched`, `.repeatN`, `.skipinv`, `.syncs`.

Simulator (`crates/sgx-sim`, from `doc/isa/sim-coverage.json`): 7 of 7 forms have semantics. The
probe vectors that test them: 2603 match the hardware, 116 stop unsupported, 0 mismatch
(`usse-alpha-test-pcoeff-depthf` 1/0/0, `usse-branch-bexc-none` 1/0/0, `usse-callfalse-chain` 3/0/0,
`usse-callfalse-link` 36/0/0, `usse-callfalse2-chain` 3/0/0, `usse-callfalse2-link` 36/0/0,
`usse-compare32-iadd32-testnat-src1` 10/0/0, `usse-compare32-iadd32-testnat-src2` 8/0/0,
`usse-compare32-iadd32-testpat-src2` 8/0/0, `usse-compare32-iadd32-testtanz-src2` 8/0/0,
`usse-compare32-iadd32-testtaz-src1` 10/0/0, `usse-compare32-iadd32-testtaz-src2` 8/0/0,
`usse-compare32-iaddu32-testnat-src2` 8/0/0, `usse-compare32-iaddu32-testtanz-src2` 8/0/0,
`usse-compare32-other-imm` 48/0/0, `usse-compare32-shr-imm` 80/0/0, `usse-compare32-xor-imm` 18/0/0,
`usse-compare32x-iadd32-ovf-testnat` 12/0/0, `usse-compare32x-iadd32-ovf-testpat` 12/0/0,
`usse-compare32x-iadd32-ovf-testtaz` 12/0/0, `usse-compare32x-iaddu32-carry-testtanz` 8/0/0,
`usse-constant-banks-gbank-write` 0/10/0, `usse-decoder-vectors-and-taz` 14/0/0,
`usse-decoder-vectors-iadd16-taz` 14/0/0, `usse-decoder-vectors-iadd16-taz-chan1` 14/0/0,
`usse-decoder-vectors-iadd16-taz-chan2` 14/0/0, `usse-decoder-vectors-iadd16-taz-chan3` 14/0/0,
`usse-decoder-vectors-iadd32-nat` 14/0/0, `usse-decoder-vectors-iadd32-pat` 14/0/0,
`usse-decoder-vectors-iadd32-tanz` 14/0/0, `usse-decoder-vectors-iadd32-taz` 14/0/0,
`usse-decoder-vectors-iaddu32-taz` 14/0/0, `usse-decoder-vectors-isub16-taz` 14/0/0,
`usse-decoder-vectors-shl-pat` 14/0/0, `usse-decoder-vectors-uadd16-taz` 14/0/0,
`usse-decoder-vectors-usub16-taz` 14/0/0, `usse-decoder-vectors-xor-nat` 14/0/0,
`usse-destination-bank6-attributes` 0/19/0, `usse-destination-bank6-moved-high` 0/21/0,
`usse-destination-bank6-moved-low` 0/21/0, `usse-destination-bank6-temps` 19/0/0,
`usse-encoding-bits-mov` 25/0/0, `usse-encoding-bits-mov-imm` 7/0/0,
`usse-encoding-gaps-end-flips-class22` 0/3/0, `usse-encoding-gaps-end-words` 1/9/0,
`usse-flags-other` 1/0/0, `usse-form-coverage-form2-test-e50` 9/1/0,
`usse-form-coverage-lapc-pclink` 4/0/0, `usse-form-coverage-test-fn` 5/0/0,
`usse-fw37-pred-pred-notp0-mov-imm` 10/0/0, `usse-fw37-pred-pred-notp0-mov-reg` 18/0/0,
`usse-fw37-pred-pred-p0-mov-imm` 10/0/0, `usse-fw37-pred-pred-p0-mov-reg` 18/0/0,
`usse-g19-read-paths` 0/2/0, `usse-iaddu32-pairs-iadd32-testnat` 16/0/0,
`usse-iaddu32-pairs-iadd32-testpat` 16/0/0, `usse-iaddu32-pairs-iadd32-testtanz` 16/0/0,
`usse-iaddu32-pairs-iadd32-testtaz` 16/0/0, `usse-iaddu32-pairs-iaddu32-testnat` 16/0/0,
`usse-iaddu32-pairs-iaddu32-testpat` 16/0/0, `usse-iaddu32-pairs-iaddu32-testtanz` 16/0/0,
`usse-iaddu32-pairs-iaddu32-testtaz` 16/0/0, `usse-indexing-index-high` 0/12/0,
`usse-indexing-index-store` 4/0/0, `usse-indexing-index-unit` 7/0/0, `usse-indexing-index-width`
3/0/0, `usse-indexing-index-width2` 7/0/0, `usse-indexing-index-width3` 6/0/0,
`usse-instance-masking-setm` 1/0/0, `usse-instance-masking-skipinv-inst` 3/0/0,
`usse-internal-registers-across-tasks` 4/4/0, `usse-internal-registers-bank7` 57/0/0,
`usse-internal-registers-ireg-index` 4/4/0, `usse-internal-registers-mov-and-tasks` 0/8/0,
`usse-internal-registers-per-pixel` 12/0/0, `usse-lane-integer-rogue-int` 11/0/0,
`usse-link-ba-savelink-read` 10/0/0, `usse-link-lapc-gap` 19/0/0, `usse-link-pclink-leftover`
10/0/0, `usse-link-pclink-roundtrip` 38/0/0, `usse-memory-mem-forms` 2/0/0, `usse-moe-moest-load`
6/0/0, `usse-moe-state-next-job` 6/0/0, `usse-numbered-modifiers-family-repeat` 32/0/0,
`usse-pa-dest-persist` 0/2/0, `usse-pclink-pixels` 10/0/0, `usse-pclink-repeat-a` 10/0/0,
`usse-pclink-repeat-b` 10/0/0, `usse-pclink-repeat-c` 10/0/0, `usse-pflow-flow` 12/0/0,
`usse-phases-filladdr` 2/0/0, `usse-predicates-predicate-pn` 6/0/0, `usse-raw25-test-bit43` 96/0/0,
`usse-raw25-test-plain` 96/0/0, `usse-rawchan-1-and` 36/0/0, `usse-rawchan-2-and` 36/0/0,
`usse-rawchan-3-and` 36/0/0, `usse-rawchan-4-and` 36/0/0, `usse-rawchan-5-and` 36/0/0,
`usse-rawchan-6-and` 36/0/0, `usse-rawchan-7-and` 36/0/0, `usse-rawcond-and-codes` 90/0/0,
`usse-rawcond2-and-imm` 90/0/0, `usse-rawcond2-or-reg` 90/0/0, `usse-rawcond2-rol-reg` 90/0/0,
`usse-rawcond2-xor-imm` 90/0/0, `usse-rawcond2-xor-reg` 90/0/0, `usse-rawjoin-o-and` 90/0/0,
`usse-rawjoin-o2-and7-fields` 90/0/0, `usse-rawjoin-o2-or-fields` 90/0/0,
`usse-rawjoin-o2-xor-fields` 90/0/0, `usse-repeat-order` 3/0/0, `usse-repeat-pred` 4/0/0,
`usse-risky-lapc-backward` 6/0/0, `usse-risky-lapc-computed` 8/0/0, `usse-risky-lapc-direct` 8/0/0,
`usse-risky-lapc-high-bits` 4/0/0, `usse-risky-link-ba-return` 3/0/0, `usse-risky-link-nested`
2/0/0, `usse-store-own-one` 1/0/0, `usse-store-own2-quad` 1/0/0, `usse-test-channels-lanes-other`
74/0/0, `usse-unorm8-add-sub-mul` 12/0/0, `usse-unorm8-mul` 12/0/0, `usse-write-masks-wmask-mov`
16/0/0); unsupported mostly for reads paN before the program writes it (41); reads saN before the
program writes it (22); rN is past the task's N temporaries (12).

Confirmed on the hardware (a passing vector): #0, #1, #2, #3, #4, #126, #127.

### 7.2 Conditional and masked moves: `movc`, `movmsk`

Class 5 with a type `enc[42:40]` other than 0. `movc` (types 1-5: `.i8`, `.i16`, `.i32`,
`.flt`, `.i10`) takes three sources and a test (`.tz`, `.tnz`, `.tn`, `.tp|z`); `movmsk`
(types 6 and 7, the second adding `.smsk` and a source 0) takes a mask format (`.mask`,
`.flt16`, `.flt`, `.u8`) and a component select on its last source **[RE]**.

- **`movc`** is a select per lane: `d = test(s0) ? s1 : s2` in each lane of the type (`.i32`
  one, `.i16` two, `.i8` four, `.i10` three 10-bit lanes with bits 30-31 cleared, `.flt` the
  float with denormals as zero and a NaN failing all but `.tnz`) **[HW]**.
- **`movmsk.<fmt> d, s1, s2.c`** writes `s1` into `d` when `s2` passes: `.mask` bit 0 of byte
  `c`, `.u8` bit 7 of byte `c`, `.flt` `s2 >= 0.5`, `.flt16` half `c >= 0.5` **[HW]**. With
  `.smsk` the move also needs bit 0 of source 0, except for `.mask` **[HW]** (*Conditional and
  masked moves*).
- **Write masks** pick registers as for `mov` **[HW]** (*Write masks*).
- **In the firmware:** not used. Neither do our programs use them.

`movc.i32.tz r1, r2, r3, r4` assembles with form #188: enc[63:32] = `0x28001300`, enc[31:0] =
`0x00208184`; in memory (little endian) `84 81 20 00 00 13 00 28`.

| field | value | prints |
|---|---|---|
| `pred` | 0x0 | (none) |
| `flags1` | 0x0 | (none) |
| `flags2` | 0x3 | `.i32` |
| `flags3` | 0x0 | `.tz` |
| `dst` | 0x1 | `r1` |
| `wmask` | 0x1 | (none) |
| `src0` | 0x2 | `r2` |
| `src1` | 0x3 | `r3` |
| `src2` | 0x4 | `r4` |

Mnemonics: `movc`, `movmsk`.

Modifiers: `.end`, `.flt`, `.flt16`, `.i10`, `.i16`, `.i32`, `.i8`, `.mask`, `.nosched`, `.repeatN`,
`.skipinv`, `.smsk`, `.syncs`, `.tn`, `.tnz`, `.tp|z`, `.tz`, `.u8`.

Simulator (`crates/sgx-sim`, from `doc/isa/sim-coverage.json`): 11 of 11 forms have semantics. The
probe vectors that test them: 138 match the hardware, 0 stop unsupported, 0 mismatch
(`usse-encoding-bits-movc` 5/0/0, `usse-encoding-bits-movc-i8` 5/0/0,
`usse-encoding-bits-movc-repeat` 5/0/0, `usse-encoding-bits-movmsk` 11/0/0,
`usse-encoding-bits-movmsk-repeat` 11/0/0, `usse-encoding-bits-movmsk-smsk` 3/0/0,
`usse-encoding-bits-movmsk-smsk-u8` 3/0/0, `usse-encoding-bits-movmsk-u8` 11/0/0,
`usse-form-coverage-movc-movmsk-repeat` 11/0/0, `usse-movc-flt` 8/0/0, `usse-movc-i10` 8/0/0,
`usse-movc-i16` 8/0/0, `usse-movc-i32` 8/0/0, `usse-movc-i8` 8/0/0, `usse-movc-movmsk-flt` 2/0/0,
`usse-movc-movmsk-flt16` 4/0/0, `usse-movc-movmsk-mask` 4/0/0, `usse-movc-movmsk-smsk` 2/0/0,
`usse-movc-movmsk-smsk2` 16/0/0, `usse-movc-movmsk-u8` 4/0/0, `usse-write-masks-wmask-other` 1/0/0).

Confirmed on the hardware (a passing vector): #188, #189, #190, #191, #192, #193, #194, #195, #196,
#197, #198.

### 7.3 Bitwise operations and shifts: `and`, `or`, `xor`, `shl`, `shr`, `rol`, `asr`

Classes 10-13 share one layout. `enc[63:60]` selects the pair of classes (5 for `and`/`or`
and `xor`, 6 for the shifts) and the operation is `enc[59]` with `enc[35]` **[RE]**:

| `enc[63:60]` | `enc[59]`, `enc[35]` = 00 | 01 | 10 | 11 |
|---|---|---|---|---|
| 5 | `and` | `or` | `xor` | (does not decode) |
| 6 | `shl` | `rol` | `shr` | `asr` |

- **Semantics [infer].** `d = s1 op s2` on 32 bits: `and`, `or`, `xor`; `shl` and `shr` shift
  left and right (logical), `rol` rotates left, `asr` shifts right arithmetically, by source
  2. `~` before source 2 complements it first. This is the reading the radare2 emulation of
  the firmware uses, and the firmware's code makes sense under it throughout. **[HW]** By a
  register amount of 32 and over, `shl`/`shr` give 0, `asr` the sign and `rol` takes the
  amount mod 32, immediate amounts the same, and `~` complements an amount as any source 2
  (*Shift amounts of 32 and over*).
- **Immediates.** Source 2 written `#imm` is the rotated 16-bit immediate (*Immediates*); a
  source-1 immediate is the usual seven-bit one, printed in hex.
- **Write mask or repeat**, as for `mov` (`enc[53]`).
- **`.partial`** (`enc[34]`) changes nothing a fill sees **[HW]** (*`.tpres`, `.partial`,
  `.nosched`, `.syncs`*).

**In the firmware [RE].** The workhorses of its flag logic: 602 `and`, 208 `or`, 199 `xor`,
95 `shl`, 60 `shr`, 1 `rol`, mostly on temporaries and on words loaded from its control
blocks; masks are often built with `xor` against an inverted immediate.

`and r1, r2, #0x00FF0000` assembles with form #16: enc[63:32] = `0x50011230`, enc[31:0] =
`0x203F8100`; in memory (little endian) `00 81 3F 20 30 12 01 50`.

| field | value | prints |
|---|---|---|
| `pred` | 0x0 | (none) |
| `op` | 0x0 | `and` |
| `flags` | 0x0 | (none) |
| `dst` | 0x1 | `r1` |
| `wmask` | 0x1 | (none) |
| `src1` | 0x2 | `r2` |
| `inv` | 0x0 | (none) |
| `imm` | 0x8ff00 | `0x00FF0000` |

`xor.repeat2 r4, r6, ~r8` assembles with form #19: enc[63:32] = `0x58201800`, enc[31:0] =
`0x00800308`; in memory (little endian) `08 03 80 00 00 18 20 58`.

| field | value | prints |
|---|---|---|
| `pred` | 0x0 | (none) |
| `op` | 0x2 | `xor` |
| `flags` | 0x0 | (none) |
| `dst` | 0x4 | `r4` |
| `repeat` | 0x1 | `.repeat2` |
| `src1` | 0x6 | `r6` |
| `inv` | 0x1 | `~` |
| `src2` | 0x8 | `r8` |

Mnemonics: `and`, `asr`, `or`, `rol`, `shl`, `shr`, `xor`.

Modifiers: `.end`, `.nosched`, `.partial`, `.repeatN`, `.skipinv`, `.syncs`.

Simulator (`crates/sgx-sim`, from `doc/isa/sim-coverage.json`): 8 of 8 forms have semantics. The
probe vectors that test them: 857 match the hardware, 41 stop unsupported, 0 mismatch
(`usse-branch-br-offset` 5/0/0, `usse-branch-divergent` 6/2/0, `usse-compare32-pad-slt-padded`
16/0/0, `usse-compare32-pad-slt-padded1` 16/0/0, `usse-compare32-pad-slt-padded6` 16/0/0,
`usse-compare32-slt` 64/0/0, `usse-compare32-ult` 64/0/0, `usse-compare32-ult-padded` 16/0/0,
`usse-decoder-vectors-and` 16/0/0, `usse-decoder-vectors-andn` 16/0/0, `usse-decoder-vectors-asr`
30/0/0, `usse-decoder-vectors-br1` 2/0/0, `usse-decoder-vectors-br2` 2/0/0,
`usse-decoder-vectors-br3` 2/0/0, `usse-decoder-vectors-br4` 2/0/0, `usse-decoder-vectors-br5`
2/0/0, `usse-decoder-vectors-brn1` 2/0/0, `usse-decoder-vectors-brn2` 2/0/0,
`usse-decoder-vectors-brn3` 2/0/0, `usse-decoder-vectors-brn4` 2/0/0, `usse-decoder-vectors-brn5`
2/0/0, `usse-decoder-vectors-or` 16/0/0, `usse-decoder-vectors-rol` 30/0/0,
`usse-decoder-vectors-shl` 30/0/0, `usse-decoder-vectors-shr` 30/0/0, `usse-decoder-vectors-xor`
16/0/0, `usse-dot-products-fdpc` 6/0/0, `usse-dot-products-fdpc-clip` 16/0/0,
`usse-encoding-bits-and` 15/0/0, `usse-encoding-bits-and-repeat` 15/0/0, `usse-encoding-bits-shl`
15/0/0, `usse-encoding-bits-shr-repeat` 15/0/0, `usse-flags-other` 2/0/0,
`usse-form-coverage-bitwise-repeat` 9/0/0, `usse-g19-read-paths` 0/8/0, `usse-ima32-forms-banks`
15/25/0, `usse-ima32-forms-nosched` 16/0/0, `usse-instance-masking-skipinv-inst` 1/0/0,
`usse-integer-asr-reg` 7/0/0, `usse-integer-rol-reg` 7/0/0, `usse-integer-shift-immediates` 25/0/0,
`usse-integer-shl-reg` 7/0/0, `usse-integer-shr-reg` 7/0/0, `usse-memory-mem-forms` 3/0/0,
`usse-moe-setfc-branch` 10/0/0, `usse-moe-smbo-operands` 2/4/0,
`usse-numbered-modifiers-family-repeat` 30/2/0, `usse-pflow-leftover` 20/0/0,
`usse-phases-phasbr-fill-parallel` 1/0/0, `usse-phases-phasbr-fill-perinstance` 1/0/0,
`usse-risky-lapc-high-bits` 4/0/0, `usse-rot-imm-field-1234` 32/0/0, `usse-rot-imm-field-8001`
32/0/0, `usse-rot-imm-field-ffff` 32/0/0, `usse-rot-imm-invert` 19/0/0, `usse-rot-imm-shifts`
36/0/0, `usse-rot-imm-text` 18/0/0, `usse-write-masks-wmask-and-imm` 16/0/0,
`usse-write-masks-wmask-or` 16/0/0); unsupported mostly for reads paN before the program writes it
(9); reads saN before the program writes it (9); gN (per-instance values, not modelled) (8).

Confirmed on the hardware (a passing vector): #16, #17, #18, #19, #20, #21, #22, #23.

### 7.4 The test group: ALU operations with a test

Classes 9 and 15 run an ALU operation (`enc[19:14]`) and **test its result**: class 9 into a
predicate `p0`-`p3` (`enc[35:34]`), class 15 into a byte, word or dword mask (`.bmsk`,
`.wmsk`, `.dmsk`). With `enc[20]` clear the result itself is not written (`!` before the
destination) **[RE]**. The operations: the bitwise group and shifts, integer adds, subtracts
and multiplies on 8, 16 and 32 bits (`iadd8` ... `iaddu32`, the 8-bit ones with `.sat`), and
float adds, multiplies, min/max, derivatives, dot product and reciprocal-type operations,
with the operand formats of their own groups when `enc[50]` is set. The bitwise group, the
integer adds, subtracts and multiplies and `fadd`/`fsub`/`fmul` are measured as tests (*Test
channels* and the pages it links); the other operations, the one-source tests and the
`enc[50]` forms are **[open]**.

The test is `.test<S><J><Z>.<chan>`, from `enc[43:36]`:

| part | bits | values |
|---|---|---|
| sign test `S` | `enc[43:42]` | `t`, `n` (negative), `p` (positive) |
| join `J` | `enc[39]` | `o` (or), `a` (and) |
| zero test `Z` | `enc[41:40]` | `t`, `z` (zero), `nz` (not zero) |
| channel | `enc[38:36]` | `chan0`-`chan3`, `andall`, `orall`, `and02`, `or02` |

- **The tests [HW].** On 32-bit results tested on `chan0`: `z` and `nz` test the result for
  zero, `n` tests bit 31 and `p` is its complement (`>= 0`, so zero passes), and `t` is true
  in either join: `testtaz`/`testtanz` are "zero" and "not zero", an `o` join with a `t` side
  is always true (*The test sign `p`*, *`t` in the `a`/`o` joins of a test*). The firmware
  tests flags this way hundreds of times, and sign bits by shifting the flag to bit 31 first
  (`shl.testnat`); our state and vertex programs rely on `and.testtanz` of 0 and 0 leaving
  the predicate false (*Predicates*).
- **The 32-bit adds [HW]** are not full 32-bit adds: `iadd32`/`iaddu32` add source 1's low 16 bits,
  sign- or zero-extended (`iadd32` sign-extends: E498; `iaddu32` zero-extends in the value it
  writes: E521),
  to the 32-bit source 2, and a test of some of them applies to the true 33-bit sum, not the wrapped
  one (E472, E498; the probe table's model tested the wrapped sum): `iadd32`'s `n` and `p` read the
  sign of the true sum sext16(r1) + r2 (r1 = 0x7fff with r2 = 0x7fffffff leaves `n` clear; 12 pairs
  in E472, 5 of which separate the readings, and 16 in E498, where only (0xffff, 0x80000000), one of
  those 5, does), `iadd32`'s `z` and `nz` read the zero of that sum with r1 sign-extended (16 pairs:
  (0x8000, 0x8000) and (0xffff, 1) read zero, which a zero-extended r1 does not give, 11 of 16; no
  pair can tell the true sum from the wrapped one: with r2 signed the sum stays within +-2^32, so
  they agree in zero-ness on 16 of 16 pairs, and (1, 0xffffffff) reads zero), `iaddu32`'s `p` is
  always true and its `n` never (16 of 16 pairs each) and its `z` is true for the pair (0, 0) only:
  the sum with its carry out of bit 31 is zero for no other pair of the 16 under either extension of
  r1 (nor is 'both operands zero': the 16 pairs do not separate the two), so 1 + 0xffffffff is
  nonzero, and the wrapped sum reads zero for pairs that are nonzero (E498 lists the 16 pairs).
  The value `iaddu32` writes is the low 16 bits of source 1, zero-extended, plus source 2 **[HW]**
  (E521: 16 pairs, seven of which a sign extension writes otherwise, such as 0x8000 + 0x8000 =
  0x10000), and so it does with source 2 `#1`, `#127` and `c56` (0xffffffff) and into `i0` (E1061:
  eight pairs each, seven with bit 15 of r1 set, 8 of 8 each); a write mask `.xy` or `.xyzw` on the
  test repeats it as on the other forms, component k writing d + k from r1 + k and r5 + k (E1061,
  16 of 16; the predicate it leaves was not read). Into `sa0`, read back by `mov`, with every
  instance of the fill writing, two of eight dwords held another pair's value and the pixels mixed
  four values (E1061: one register shared by the fill's instances **[infer]**); with one writer
  quad alone (a branch on `pa0` as E513's) it writes the same zero-extended value as into `r10`, 8
  of 8 dwords in 6 of 6 rows over two sets of eight pairs and two quads, the sign extension and the
  mixture 0 of 6 (E1106 **[HW]**); which extension its
  test reads is not observable **[infer]**: no test of the 16 pairs of E498 tells it. With source 1
  = `#0`
  the test reads source 2's 32 bits exactly: `n`, `p`, `z` and `nz` (8 of 8 values each) (*The
  32-bit adds `iadd32` and `iaddu32`*).
- **The test field is two parts, ANDed under the `a` join and ORed under the `o` join [HW]** (E499,
  E529): `enc[43:40]` holds taz = bit 40, tanz = bit 41, nat = bit 42 and pat = bit 43 (the
  assembler's `.test<S><J><Z>` writes the sign and zero conditions together: `.testpanz` is the
  field 0xa, `.testnaz` and `.testnoz` the field 5 with the `a` and the `o` join, `.testtoz` the
  field 1 with the `o` join, checked with usse-asm on the host; the words ran on the hardware as raw
  words). Run as raw words, with enc[39] = 1 (join `a`) and chan0 in all 732 words, the zero part is
  tanz if bit 41 is set, else taz if bit 40, the sign part is pat if bit 43 is set, else nat if bit
  42, and the test is true when the parts present are all true: `and` with r1, r2 over the 15 values
  of the field and six input pairs (90 of 90, a rule read out of those cases, the plain AND of the
  set conditions fitting 69 and the OR 57), then predicted on `or`, `xor` and `rol` with registers
  and `and` and `xor` with #7 (450 of 450, 90 cases each, join `a` and chan0 only). Bit 43 is the
  bit that `~` sets in `and r10, r1, ~r2`; set in the sixteen test words the assembler writes
  (`and`, `or`, `xor`, `rol`, with r2 or #7, testtaz and testtanz) it is the `pat` condition ANDed
  with the test, not an invert (96 of 96; the invert of source 2, the probe table's model, fits 53
  of 96): so a test word has no `~`, taz with pat is taz, and tanz with pat is the one-instruction
  "greater than zero" test, which the assembler writes as `.testpanz` and which ran as a raw word.
  Under the `o` join (enc[39] = 0, chan0) the two parts are ORed and a part absent from the field
  counts as true, so a field of one part, and the fields 3 and 0xc, is always true, and 0xa, 0xb,
  0xe and 0xf (tanz with pat) are tautologies that only the fields 5, 6, 7, 9 and 0xd separate from
  always true (E529: `and r1, r2` over the 15 values and six pairs, 90 of 90 for a rule read from
  those readbacks after the first prediction, the parts ORed with an absent part false, fitted 75 of
  90; then 270 of 270 predicted on `or` and `xor` with registers and `and` with #7, 90 cases each;
  `and` with #7 gives no negative result). **The same rule holds on the shifts, the #7 forms and
  the sums under both joins [HW]** (E1062, frozen from sgx-sim and held out: `shl`, `shr` and `asr`
  with registers, `or` and `rol` with #7, `iadd32`, whose sign is the true sum's, and `iaddu32`,
  whose zero is the carry-counted sum's and whose sign is always positive, each with the fields 0 to
  15 over six pairs under the `a` and the `o` join, 14 of 14 rows; the field value 0, both parts
  absent, is always true), with E499's and E529's tables replicated as controls. That no other bit
  of a test word inverts a source is not run **[infer]** (E473, E499).
- **Tests with an immediate [HW]** act on the 32-bit result (E473): `shr.testtanz.chan0 !c0, p0, r,
  #n` is "r >> n is nonzero", with n of 32 and over giving zero (80 of 80), `xor.testtaz` is "r ^ n
  is zero" over all 32 bits (18 of 18), and `and`, `or`, `xor` and `rol` with `testtanz` and `asr`
  and `shl` with `testnat` test their 32-bit result (48 of 48). The immediate of a test is seven
  bits. The assembler refuses `~` in the three test forms tried (`and.testtanz ... ~#7` and `~r2`,
  `xor.testtaz ... ~#7`), while `and r10, r1, ~#7` assembles; `or`, `rol` and `xor ~r2` were not
  tried as text. The reason is in the test field below: the bit that `~` sets in the non-test forms
  is the `pat` bit of a test word (E499). To test `x & ~mask`, a compiler computes the inverted
  value first (`and r11, r1, ~#7`, then a test of r11).
- **A 32-bit compare [HW]** of two registers runs as two instructions, unsigned or signed, or as six
  for the signed one without the high word. Unsigned: with `ima32.u r11, i0, r2, c56, r1` (`r11` is
  a minus b, `i0` = b - [a < b]: the high word of the extra operand, E493, which ran for b *
  0xffffffff + a over eight values of b) and `xor.testtanz.chan0 !c0, p0, r2, i0`, `p0` is a < b (64
  of 64 pairs of the eight values 0, 1, 0xffff, 0x10000, 0x7fffffff, 0x80000000, 0x80000001 and
  0xffffffff, 28 of them with a < b; E501; 252 of 252 seeded pairs, 200 random among them, and 48 of
  48 pairs with each of 0, 1 and 3 nops between the two instructions, E527; registers and c56 only,
  the destination r11, no K = 3, `cie` or `.neg`; that `b xor (b - [a < b])` is nonzero exactly when
  a < b for the pairs not run is **[infer]** from the arithmetic, the high word being shown for 200
  random triples, E525). Signed: with `t = ima32.u r11, r2, c56, r1` (a - b), the signed one is bit
  31 of `(((a ^ b) & (a ^ t)) ^ t)`, tested by `shr.testtanz.chan0 !c0, p0, rX, #31` (64 of 64 pairs
  of the same eight values, unpadded, and 16 pairs with 1, 3 and 6 nops after the `ima32`, 48 of 48;
  E472, E497); the six-instruction unsigned formula, bit 31 of `((~a & b) | (~(a ^ b) & t))`, was
  also exact on the 64 pairs (E472, 16 of 16 with three nops after the `ima32`). **Signed, in two
  instructions:** `ima32.s r11, i0, r2, c56, r1` (c56 reads -1 signed, so `i0` is the high word of
  the signed a - b, 0xffffffff for a < b and 0 otherwise) and `xor.testtanz.chan0 !c0, p0, i0, #0`
  set `p0` to a < b signed (164 of 164 pairs: the 64 of the eight values and 100 random pairs, 78
  with a < b; E528); registers and c56 only, not padded, and not run beyond those pairs, the rest
  being **[infer]** from the arithmetic of E526. `ima32` has no test field **[infer]** (the
  assembler refuses a test on it).
- **The 16-bit operations [HW]:** `isub16`/`usub16` subtract both lanes, wrapping, and `chan0`
  tests the low lane (*`isub16`/`usub16` lanes*). `iadd16`, `uadd16`, `imul16`, `umul16`,
  `iadd8`, `isub8`, `imul8`, `fadd`, `fmul` and `fsub` test their lanes as the channels say, a
  16-bit lane on its full result before it is cut **[HW]** (*Test channels*).
- **Channels [HW]:** a test has one result per channel: bytes 0-3 for the 8-bit operations, the low
  and high halves as channels 0 and 2 for the 16-bit ones, the value as channel 0 otherwise; a
  channel without a lane tests as a positive non-zero value. `chan0`-`chan3` pick one,
  `andall`/`orall` combine all four, `and02`/`or02` channels 0 and 2 (*Test channels*). **Write
  `chan0` for every test of a 32-bit value [HW]:** the chan field is not ignored there (E530): with
  the `a` join and the fields taz, tanz, nat, pat, taz with pat and tanz with pat over six pairs (36
  jobs a table), none of chan1 to chan7 reads as chan0 as a table (chan4 and chan6 equal it for
  tanz, pat and tanz with pat, chan5 and chan7 for taz, nat and taz with pat); chan1 to chan3 read
  one constant per field (taz 0, tanz 1, nat 0, pat 1, taz with pat 0, tanz with pat 1), chan4 and
  chan6 (`andall`, `and02`) read tanz and pat of the value with taz and nat false, and chan5 and
  chan7 (`orall`, `or02`) taz and nat of the value with tanz and pat true, which is the rule just
  given applied after the data (**[infer]**, 252 of 252 cases; not predicted). On 8-bit and 16-bit
  lane operations the same rule held, predicted, under both joins (E1062: `iadd8` with the bytes
  0, 3, 0xf1, 8 and `iadd16` with the halves 0 and -15, chan0 to or02, the nine fields the
  assembler names, 144 of 144 tests a join). The masks of class 15, `.partial` and `.quadlead` on
  tests are **[open]**.
- **The unsigned and unorm byte operations [HW]** (E092, E094). `uadd8`, `usub8`, `umul8`,
  `uadd16` and `umul16` work lane by lane, unsigned and wrapping, and `.sat` clamps a byte at
  255 (the Rogue ISR's `UADD8`, `UMUL8`, `UADD16`, `UMUL16`). The unorm8 operations clamp per
  byte: `fpadd8` is x + y up to 255, `fpsub8` x - y down to 0 (x86's `PSUBUSB`), and `fpmul8`
  round(x · y / 255), exactly rounded (the GL texture combiners' modulate on unorm8). A test sees
  each byte's unclamped result: `fpsub8` of 3 and 85 writes 0 but does not test as zero.

**In the firmware [RE].** 671 tests, every one on `chan0` and into a predicate, mostly `and` and
`xor` with the zero and non-zero tests, a few `shl`, `isub16`, `or` and `iaddu32`. Most discard the
result (`!c0`): test, then branch on the predicate.

From `asm/tri/use_mtest18.s`:

```
        and.skipinv.testtanz.chan0 !r0, p0, #0x00000000, #0
```

`xor.testtaz.chan0 r1, p2, r1, r3` assembles with form #24: enc[63:32] = `0x48001188`, enc[31:0] =
`0x003C8083`; in memory (little endian) `83 80 3C 00 88 11 00 48`.

| field | value | prints |
|---|---|---|
| `pred` | 0x0 | (none) |
| `op` | 0x32 | `xor` |
| `flags` | 0x0 | (none) |
| `test` | 0x18 | `testtaz.chan0` |
| `w` | 0x1 | (none) |
| `dst` | 0x1 | `r1` |
| `wmask` | 0x1 | (none) |
| `p` | 0x2 | `2` |
| `src1` | 0x1 | `r1` |
| `src2` | 0x3 | `r3` |

`isub16.testpat.chan0 r1, p2, r3, #4` assembles with form #25: enc[63:32] = `0x48011888`, enc[31:0]
= `0x2035C184`; in memory (little endian) `84 C1 35 20 88 18 01 48`.

| field | value | prints |
|---|---|---|
| `pred` | 0x0 | (none) |
| `op` | 0x17 | `isub16` |
| `flags` | 0x0 | (none) |
| `test` | 0x88 | `testpat.chan0` |
| `w` | 0x1 | (none) |
| `dst` | 0x1 | `r1` |
| `wmask` | 0x1 | (none) |
| `p` | 0x2 | `2` |
| `src1` | 0x3 | `r3` |
| `src2` | 0x304 | `#4` |

Mnemonics: `and`, `asr`, `fadd`, `fdp`, `fdsx`, `fdsy`, `fexp`, `flog`, `fmax`, `fmin`, `fmul`,
`fpadd8`, `fpmul8`, `fpsub8`, `frcp`, `frsq`, `fsub`, `fsubflr`, `iadd16`, `iadd32`, `iadd8`,
`iaddu32`, `imul16`, `imul8`, `isub16`, `isub8`, `or`, `rol`, `shl`, `shr`, `uadd16`, `uadd8`,
`umul16`, `umul8`, `usub16`, `usub8`, `xor`.

Modifiers: `.and02`, `.andall`, `.bmsk`, `.chan0`, `.chan1`, `.chan2`, `.chan3`, `.dmsk`,
`.nosched`, `.or02`, `.orall`, `.partial`, `.quadlead`, `.sat`, `.skipinv`, `.syncs`, `.testnanz`,
`.testnat`, `.testnaz`, `.testnonz`, `.testnot`, `.testnoz`, `.testpanz`, `.testpat`, `.testpaz`,
`.testponz`, `.testpot`, `.testpoz`, `.testtanz`, `.testtat`, `.testtaz`, `.testtonz`, `.testtot`,
`.testtoz`, `.wmsk`.

Simulator (`crates/sgx-sim`, from `doc/isa/sim-coverage.json`): 18 of 18 forms have semantics. The
probe vectors that test them: 2205 match the hardware, 16 stop unsupported, 0 mismatch
(`usse-alpha-test-pcoeff-depthf` 1/0/0, `usse-compare32-iadd32-testnat-src1` 10/0/0,
`usse-compare32-iadd32-testnat-src2` 8/0/0, `usse-compare32-iadd32-testpat-src2` 8/0/0,
`usse-compare32-iadd32-testtanz-src2` 8/0/0, `usse-compare32-iadd32-testtaz-src1` 10/0/0,
`usse-compare32-iadd32-testtaz-src2` 8/0/0, `usse-compare32-iaddu32-testnat-src2` 8/0/0,
`usse-compare32-iaddu32-testtanz-src2` 8/0/0, `usse-compare32-other-imm` 48/0/0,
`usse-compare32-shr-imm` 80/0/0, `usse-compare32-xor-imm` 18/0/0,
`usse-compare32x-iadd32-ovf-testnat` 12/0/0, `usse-compare32x-iadd32-ovf-testpat` 12/0/0,
`usse-compare32x-iadd32-ovf-testtaz` 12/0/0, `usse-compare32x-iaddu32-carry-testtanz` 8/0/0,
`usse-decoder-vectors-and-taz` 14/0/0, `usse-decoder-vectors-iadd16-taz` 14/0/0,
`usse-decoder-vectors-iadd16-taz-chan1` 14/0/0, `usse-decoder-vectors-iadd16-taz-chan2` 14/0/0,
`usse-decoder-vectors-iadd16-taz-chan3` 14/0/0, `usse-decoder-vectors-iadd32-nat` 14/0/0,
`usse-decoder-vectors-iadd32-pat` 14/0/0, `usse-decoder-vectors-iadd32-tanz` 14/0/0,
`usse-decoder-vectors-iadd32-taz` 14/0/0, `usse-decoder-vectors-iaddu32-taz` 14/0/0,
`usse-decoder-vectors-isub16-taz` 14/0/0, `usse-decoder-vectors-shl-pat` 14/0/0,
`usse-decoder-vectors-uadd16-taz` 14/0/0, `usse-decoder-vectors-usub16-taz` 14/0/0,
`usse-decoder-vectors-xor-nat` 14/0/0, `usse-encoding-bits-test-mask-fadd` 4/0/0,
`usse-encoding-bits-test-mask-frcp` 0/14/0, `usse-encoding-bits-test-mask-iadd8` 4/0/0,
`usse-encoding-bits-test-mask-xor` 4/0/0, `usse-form-coverage-form2-test-e50` 9/1/0,
`usse-form-coverage-form2-test-mask` 12/1/0, `usse-form-coverage-test-fn` 5/0/0,
`usse-fw37-pred-pred-notp0-mov-imm` 10/0/0, `usse-fw37-pred-pred-notp0-mov-reg` 10/0/0,
`usse-fw37-pred-pred-p0-mov-imm` 10/0/0, `usse-fw37-pred-pred-p0-mov-reg` 10/0/0,
`usse-iaddu32-pairs-iadd32-testnat` 16/0/0, `usse-iaddu32-pairs-iadd32-testpat` 16/0/0,
`usse-iaddu32-pairs-iadd32-testtanz` 16/0/0, `usse-iaddu32-pairs-iadd32-testtaz` 16/0/0,
`usse-iaddu32-pairs-iaddu32-testnat` 16/0/0, `usse-iaddu32-pairs-iaddu32-testpat` 16/0/0,
`usse-iaddu32-pairs-iaddu32-testtanz` 16/0/0, `usse-iaddu32-pairs-iaddu32-testtaz` 16/0/0,
`usse-integer-iadd32-n` 4/0/0, `usse-integer-iadd32-p` 3/0/0, `usse-integer-iadd32-src1-imm` 2/0/0,
`usse-integer-iadd32-value` 4/0/0, `usse-integer-iadd32-z` 5/0/0, `usse-integer-iaddu32-imm` 4/0/0,
`usse-integer-iaddu32-np` 3/0/0, `usse-integer-iaddu32-tests` 6/0/0, `usse-integer-iaddu32-value`
4/0/0, `usse-integer-isub16-reg` 3/0/0, `usse-integer-isub16-sign-n` 4/0/0,
`usse-integer-isub16-sign-p` 4/0/0, `usse-integer-isub16-value` 6/0/0, `usse-integer-isub16-zero`
6/0/0, `usse-integer-shl-test-reg` 4/0/0, `usse-integer-usub16-value` 3/0/0,
`usse-integer-usub16-zero` 3/0/0, `usse-lane-integer-rogue-int` 11/0/0, `usse-pflow-flow` 12/0/0,
`usse-predicates-predicate-pn` 6/0/0, `usse-raw25-test-bit43` 96/0/0, `usse-raw25-test-plain`
96/0/0, `usse-rawchan-1-and` 36/0/0, `usse-rawchan-2-and` 36/0/0, `usse-rawchan-3-and` 36/0/0,
`usse-rawchan-4-and` 36/0/0, `usse-rawchan-5-and` 36/0/0, `usse-rawchan-6-and` 36/0/0,
`usse-rawchan-7-and` 36/0/0, `usse-rawcond-and-codes` 48/0/0, `usse-rawcond2-and-imm` 48/0/0,
`usse-rawcond2-or-reg` 48/0/0, `usse-rawcond2-rol-reg` 48/0/0, `usse-rawcond2-xor-imm` 48/0/0,
`usse-rawcond2-xor-reg` 48/0/0, `usse-rawjoin-o-and` 48/0/0, `usse-rawjoin-o2-and7-fields` 48/0/0,
`usse-rawjoin-o2-or-fields` 48/0/0, `usse-rawjoin-o2-xor-fields` 48/0/0,
`usse-test-channels-chan-and` 12/0/0, `usse-test-channels-chan-isub16` 5/0/0,
`usse-test-channels-chan-preds` 8/0/0, `usse-test-channels-chan-tests` 360/0/0,
`usse-test-channels-lanes-other` 74/0/0, `usse-tests-join-t-not` 3/0/0, `usse-tests-join-t-tonz`
2/0/0, `usse-tests-join-t-toz` 2/0/0, `usse-tests-sign-n-iadd32` 4/0/0, `usse-tests-sign-n-iaddu32`
4/0/0, `usse-tests-sign-p-and` 3/0/0, `usse-tests-sign-p-shl` 4/0/0, `usse-tests-zero-z-iadd32`
4/0/0, `usse-unorm8-add-sub-mul` 12/0/0, `usse-unorm8-mul` 12/0/0); unsupported mostly for frcp test
of a near value (14); test fpmulN with enc[N] (not measured) (1); test isubN.sat with enc[N] (not
measured) (1).

Confirmed on the hardware (a passing vector): #24, #25, #26, #199, #200, #201, #202, #203, #204,
#205, #206, #207, #208, #209, #210, #211, #212, #213.

### 7.5 Integer multiply-add: `imae`, `ima16`, `ima32`, `ima8`, `idiv`

Four classes **[RE]**: 21 `imae` (16 × 16 + 32), 20 `ima16` (16-bit), 26 `ima32` (32-bit) and
`idiv`, 19 `ima8` (four 8-bit lanes with colour-style selectors). They carry the multiply
flags (`.skipinv`, `.nosched`, `.end`, a three-bit repeat) and a two-bit predicate (`ima32`
and `idiv` the full one).

- **`imae.{u,s} d, a.{low,high}, b.{low,high}, c, u32`** computes `d = a16 × b16 + c`, the halves
  zero-extended for `.u` **[infer]** and sign-extended for `.s` **[HW]** (6 cases; E471: `.s`
  multiplies the halves as signed values and adds `c` as an unsigned 32-bit number, a formula
  fitted after the six cases): the firmware's
  addition idiom is a multiply-add by an immediate 1 of a 16-bit value, 205 times, and its address
  arithmetic multiplies indices by structure sizes the same way. **[HW]** `.usat`/`.ssat` saturate,
  `.rsN` shifts the result right, a `u16` source 2 is sign-extended and a `z16` one zero-extended
  (*Integer multiply-add modes*). `coe, iN` writes the carry out of the 32-bit sum to `iN`, 0 or 1,
  overwriting it whether or not the sum carried (14 of 14 with `i0`, E471; 8 of 8 with `i0` and `i1`
  over four triples, one of which carries, E494, the other `i` registers keeping their values);
  `cie, iN` adds bit 0 of `iN` only (10 of 10 with `i0`: `iN` = 2 adds nothing, 0xffff and
  0xffffffff add 1; 8 of 8 with `i0` and `i1` and the values 0x10000, 0x80000000, 0x10001 and 1,
  E494); `coe` and `cie` on one `iN` write the
  carry of the sum that includes the added bit (14 of 14); two `imae` chained through `i0`, a `coe`
  then a `cie`, are an exact 64-bit accumulate of 16 × 16 products (10 of 10) (E471). `imae` has no
  negated source and no `i2` form for `coe` and `cie` (the assembler refuses them **[infer]**: no
  raw word was run).
- **`ima32.{u,s} d, a, b, c`** computes the low 32 bits of `a × b + c` **[HW]** (E469: 826 of 826
  cases, the corner cube of 343 included; `.s` gives the same bits as `.u`, with no saturation). Its
  operands a, b and c are sources 1, 2 and 3: sources 2 and 3 can be a register, a 7-bit immediate
  or a constant-bank register read as an integer (c0 reads 0, c56-c59 read 0xffffffff,
  c60 0x7fff7fff: E085), source 1 a register; the assembler refuses an immediate or a constant in
  source 1 **[infer]**, while pa, sa, o and i operands in source 1 and pa, sa, o, g and i operands
  in sources 2 and 3 assemble, and read 0 where `mov` reads 0 (40 of 40, E496: 31 of the 40 cases
  read 0 by both routes, so only `i0` to `i2` show a nonzero value). What ran: the immediates 0, 1,
  2, 3, 4, 5, 6, 7, 8, 15, 16, 17, 31, 32, 33, 63, 64, 65, 100, 125, 126 and 127 in source 2 and the
  same without 3 in source 3 (22 and 21 of the 128 values: E469, E495, so 'every 7-bit immediate' is
  **[infer]** for the others); the constants c0, c3, c13, c60 (and
  c45, c56 as source 3 only); the destinations r0, r9, r10, r18, r28, r30, r31, sa0, o0, i1 and i2,
  and **a pa0 destination is not written** (E496; the probe table's model had every destination take
  the result). So `add` is `ima32.u d, a, #1, c` and `mul` is
  `ima32.u d, a, b, c0`.
- **Operand order [HW]** (E597): `ima32.u d, i0, a, b, c` and `ima32.s` read their sources
  before the write in every one of the 15 partitions of d, a, b and c into registers (any of them
  alike, all four the same): d held the low word and i0 the high word of the 64-bit a × b + c (c
  sign-extended for `.s`) in 300 of 300 fills. Not run in a firmware task (the verifier refuses
  the form).
- **A 32-bit subtract [HW]** is `ima32.u d, b, c56, a`, which is `a - b` mod 2^32, and so is
  `ima32.u d, a, #1, b.neg` (E470: 80 of 80 through c56, 6 of 6 through c57, c58, c59 `.u` and c59
  `.s`). `.neg` on source 2 (`enc[40]`) or source 3 (`enc[39]`) negates that source in two's
  complement, `-(a × b) + c` and `a × b - c` (90 of 90 cases in nine probes; the readings
  "complement" and "ignored" fail in all of them and "fields swapped" in the eight probes with one
  negated source, 80 of 90 cases), with `.u` and `.s` on registers (E470) and on the immediates and
  constants of E495 (`.s` with #1.neg and #5.neg in source 2, #1.neg and #127.neg in source 3,
  c56.neg and c3.neg in source 2 and c56.neg in source 3; `.u` with #5.neg and #127.neg in source 2
  and #127.neg in source 3: 80 of 80). Source 1 has no `.neg` (the assembler's refusal **[infer]**).
  **The borrow comes with the high word [HW]:** `ima32.u d, i0, b, c56, a` leaves `a - b` in `d`
  and `b - [a < b]` in `i0` (75 of 75 cases, E501: `i0` over the 49 pairs of the values 0, 1,
  0xffff, 0x10000, 0x7fffffff, 0x80000000 and 0xffffffff, `i1` and `i2` over 13 pairs of them), so
  that `xor.testtanz.chan0 !c0, p0, b, i0` sets `p0` to `a < b` unsigned: two instructions instead
  of six (*The test group*), run on the 64 pairs of the eight values 0, 1, 0xffff, 0x10000,
  0x7fffffff, 0x80000000, 0x80000001 and 0xffffffff (E501) and on 252 seeded pairs, 200 random among
  them, and with 0, 1 and 3 `nop`s between the two instructions on 48 of those pairs each (252 of
  252 and 48 of 48 three times, E527), registers only, the destination `r11`; that it is exact for
  every pair is **[infer]** from the arithmetic of the high word, which E525 shows for 200 random
  register triples. **A signed compare is two instructions too [HW]:** `ima32.s r11, i0, r2, c56,
  r1` then `xor.testtanz.chan0 !c0, p0, i0, #0` sets `p0` to `a < b` signed (164 of 164 pairs: the
  64 of the eight values and 100 random, E528; `c56` reads -1 signed, `i0` is the high word of the
  signed `a - b`, 0xffffffff for `a < b`), against the six of *The test group*; it was not padded
  and was not run beyond the 164 pairs (**[infer]** for the rest).
- **The extra `i` operand and `cie` of `ima32` [HW].** `ima32.u d, iK, a, b, c` (`enc[38]` set, `iK`
  in `enc[37:36]`) writes the low 32 bits of `a × b + c` to `d` and the high 32 bits to `iK`, the
  bits 63:32 of the exact 64-bit `a × b + c` on register operands (E525: 282 of 282 jobs, 42 corner
  triples, 0x12345678 × 0x9abcdef0 among them, and 200 random triples with `K` = 0, then `K` = 1 and
  2 over 20 random triples each; `.s` gives the signed high word with `c` sign-extended, 282 of 282,
  E526; E493's five `.u` triples, (3, 7, 100), (0xffffffff, 1, 1), (0xffffffff, 0xffffffff,
  0xffffffff), (0x10000, 0x10000, 0) and (0x80000000, 2, 0xffffffff), 15 of 15 cases with `K` = 0, 1
  and 2, and `b * 0xffffffff + a` for eight values of `b`, E501, are cases of it): the probe table's
  model, that the `i` registers keep their values, fits 0 of 15, and `iK` = the carry out of the
  32-bit add fits 6 of the 15 and 10 of the 282. A backend may lower a 32 × 32 + 32 high-word
  multiply to it for register operands; its cost was not measured. Raw words with the field
  `enc[37:36]` set and `enc[38]` clear, with `enc[38]` set and `iK` = 3 and with the bits 45, 44 and
  35 set changed neither `r10`, `i0` to `i2` nor `r14` to `r17`; with bit 46 set `r14` read 0x2255
  in 3 of 3 jobs, what the bit does is **[open]** (Q127). Immediates and constants other than c56
  with the extra operand, the extra operand together with `cie` or `.neg`, an `iK` that is also a
  source, a destination other than `r10`, the dual-issue form and `K` = 3 are **[open]** (Q127).
  `ima32 ... cie, iN` adds bit 0 of `iN` only **[HW]**: `i0` to `i2` with the values 0x10000,
  0x80000000, 0xfffffffe, 0x10001, 0x80000001, 2, 0x55555554 and 0xaaaaaaab (24 of 24, E494; and 10
  of 10 with 0, 1, 2, 0xffff and 0xffffffff in `i0`, E470; adding all of `iN` fits 0 of 24, E494).
  Dependent `ima32` need no gap: four in a row are exact (10 of 10, E470), and a reader (`ima32`,
  `mov` or `xor`) after 0, 1, 2, 3, 4, 5, 6 or 8 `nop`s sees the result, with or without `.nosched`
  on the writer (48 of 48, E495). `ima32` as a dual-issue secondary (two 16-bit lanes: *Dual
  issue*), `u16`/`z16` sources and `.rsN` on `ima32`, and `imae` with a repeat are **[open]**
  (Q127).
- **`ima16`** multiplies 16-bit values, its sources read as `u16`, `u8`, `s8` or `o8` with a
  half select. With `u16, u16` it computes `a × b + c` (or `- c`) in each 16-bit lane,
  wrapping **[HW]** (*`ima16` lanes and source formats*); with `u8`, `s8`, `o8` each lane reads
  the `.low`/`.high` byte of its own half **[HW]** (*Integer multiply-add modes*).
  The firmware has two, both `.s` with a negated source.
- **`idiv d, a, b, drcN`** writes the unsigned quotient to `d` and the remainder to `d + 1`,
  asynchronously: `wdf drcN` waits for them **[HW]** (*Integer multiply-add modes*). Its repeat
  count has four bits, enc[47:44] + 1: iteration k divides `a + k` by `b + k`, its quotient
  to `d + k` and its remainder to `d + k + 1`, which the next quotient overwrites **[HW]**
  (E367).
- **`ima8`** computes `x + y × z` per byte from its selectors (`s0`, `s1`, `s2` and their alpha
  forms), wrapping or with `.sat` clamping **[HW]** (*Integer multiply-add modes*).

`imae.u r2, r4.low, #1.low, r2, u32` assembles with form #27: enc[63:32] = `0xA8020080`, enc[31:0] =
`0x80410082`; in memory (little endian) `82 00 41 80 80 00 02 A8`.

| field | value | prints |
|---|---|---|
| `pred` | 0x0 | (none) |
| `flags` | 0x0 | (none) |
| `type` | 0x0 | `u` |
| `rs` | 0x0 | (none) |
| `dst` | 0x2 | `r2` |
| `src0` | 0x4 | `r4` |
| `half1` | 0x0 | `low` |
| `src1` | 0x301 | `#1` |
| `half2` | 0x0 | `low` |
| `src2` | 0x2 | `r2` |

`ima32.u r1, r2, r3, r4` assembles with form #29: enc[63:32] = `0xD0000000`, enc[31:0] =
`0x00208184`; in memory (little endian) `84 81 20 00 00 00 00 D0`.

| field | value | prints |
|---|---|---|
| `pred` | 0x0 | (none) |
| `flags` | 0x0 | (none) |
| `type` | 0x0 | `u` |
| `dst` | 0x1 | `r1` |
| `src0` | 0x2 | `r2` |
| `src1` | 0x3 | `r3` |
| `neg1` | 0x0 | (none) |
| `src2` | 0x4 | `r4` |
| `neg2` | 0x0 | (none) |

Mnemonics: `idiv`, `ima16`, `ima32`, `ima8`, `imae`.

Modifiers: `.end`, `.nosched`, `.repeatN`, `.rsN`, `.s`, `.sat`, `.skipinv`, `.ssat`, `.u`, `.usat`.

Simulator (`crates/sgx-sim`, from `doc/isa/sim-coverage.json`): 12 of 12 forms have semantics. The
probe vectors that test them: 3675 match the hardware, 56 stop unsupported, 0 mismatch
(`usse-compare32-pad-slt-padded` 16/0/0, `usse-compare32-pad-slt-padded1` 16/0/0,
`usse-compare32-pad-slt-padded6` 16/0/0, `usse-compare32-slt` 64/0/0, `usse-compare32-ult` 64/0/0,
`usse-compare32-ult-padded` 16/0/0, `usse-decoder-vectors-idiv` 17/0/0,
`usse-decoder-vectors-ima16s` 16/0/0, `usse-decoder-vectors-ima16u` 16/0/0,
`usse-decoder-vectors-ima32s` 16/0/0, `usse-decoder-vectors-ima32u` 16/0/0,
`usse-encoding-bits-idiv` 19/1/0, `usse-encoding-bits-ima16` 2/0/0, `usse-encoding-bits-ima16-8bit`
3/0/0, `usse-encoding-bits-ima16-s8` 3/0/0, `usse-encoding-bits-ima16-u8u8` 2/0/0,
`usse-encoding-bits-ima32` 4/0/0, `usse-encoding-bits-imae` 2/0/0,
`usse-form-coverage-ima16-ignored` 3/0/0, `usse-fw37-compare-scmp-prev-i0` 32/0/0,
`usse-fw37-compare-scmp-r123r122r121` 16/0/0, `usse-fw37-compare-scmp-r26r27r28` 16/0/0,
`usse-fw37-compare-scmp-r31r30r25` 16/0/0, `usse-fw37-compare-scmp-r5r6r7` 16/0/0,
`usse-fw37-compare-scmp-r64r65r66` 16/0/0, `usse-fw37-compare-scmp-t-is-a` 16/0/0,
`usse-fw37-compare-ucmp-prev-i0` 32/0/0, `usse-fw37-compare-ucmp-r123r122r121` 16/0/0,
`usse-fw37-compare-ucmp-r26r27r28` 16/0/0, `usse-fw37-compare-ucmp-r31r30r25` 16/0/0,
`usse-fw37-compare-ucmp-r5r6r7` 16/0/0, `usse-fw37-compare-ucmp-r64r65r66` 16/0/0,
`usse-fw37-compare-ucmp-t-is-a` 16/0/0, `usse-fw37-ima32hi-repeat-his-aaaa` 10/0/0,
`usse-fw37-ima32hi-repeat-his-aaab` 10/0/0, `usse-fw37-ima32hi-repeat-his-aaba` 10/0/0,
`usse-fw37-ima32hi-repeat-his-aabb` 10/0/0, `usse-fw37-ima32hi-repeat-his-aabc` 10/0/0,
`usse-fw37-ima32hi-repeat-his-abaa` 10/0/0, `usse-fw37-ima32hi-repeat-his-abab` 10/0/0,
`usse-fw37-ima32hi-repeat-his-abac` 10/0/0, `usse-fw37-ima32hi-repeat-his-abba` 10/0/0,
`usse-fw37-ima32hi-repeat-his-abbb` 10/0/0, `usse-fw37-ima32hi-repeat-his-abbc` 10/0/0,
`usse-fw37-ima32hi-repeat-his-abca` 10/0/0, `usse-fw37-ima32hi-repeat-his-abcb` 10/0/0,
`usse-fw37-ima32hi-repeat-his-abcc` 10/0/0, `usse-fw37-ima32hi-repeat-his-abcd` 10/0/0,
`usse-fw37-ima32hi-repeat-hiu-aaaa` 10/0/0, `usse-fw37-ima32hi-repeat-hiu-aaab` 10/0/0,
`usse-fw37-ima32hi-repeat-hiu-aaba` 10/0/0, `usse-fw37-ima32hi-repeat-hiu-aabb` 10/0/0,
`usse-fw37-ima32hi-repeat-hiu-aabc` 10/0/0, `usse-fw37-ima32hi-repeat-hiu-abaa` 10/0/0,
`usse-fw37-ima32hi-repeat-hiu-abab` 10/0/0, `usse-fw37-ima32hi-repeat-hiu-abac` 10/0/0,
`usse-fw37-ima32hi-repeat-hiu-abba` 10/0/0, `usse-fw37-ima32hi-repeat-hiu-abbb` 10/0/0,
`usse-fw37-ima32hi-repeat-hiu-abbc` 10/0/0, `usse-fw37-ima32hi-repeat-hiu-abca` 10/0/0,
`usse-fw37-ima32hi-repeat-hiu-abcb` 10/0/0, `usse-fw37-ima32hi-repeat-hiu-abcc` 10/0/0,
`usse-fw37-ima32hi-repeat-hiu-abcd` 10/0/0, `usse-idiv-enc47-grid` 5/9/0,
`usse-idiv-enc47-repeat-sets` 16/0/0, `usse-ima32-forms-banks` 15/25/0, `usse-ima32-forms-cie-in`
24/0/0, `usse-ima32-forms-dest` 30/3/0, `usse-ima32-forms-extra-i` 15/0/0,
`usse-ima32-forms-imae-cie-in` 8/0/0, `usse-ima32-forms-imae-coe-in` 8/0/0,
`usse-ima32-forms-imm-range` 68/0/0, `usse-ima32-forms-nosched` 48/0/0, `usse-ima32-forms-s-neg`
80/0/0, `usse-ima32-full-bimm0` 14/0/0, `usse-ima32-full-bimm1` 49/0/0, `usse-ima32-full-bimm1-s`
14/0/0, `usse-ima32-full-bimm127` 14/0/0, `usse-ima32-full-bimm2` 14/0/0, `usse-ima32-full-bimm3`
14/0/0, `usse-ima32-full-bothimm` 21/0/0, `usse-ima32-full-c0-mul` 49/0/0, `usse-ima32-full-c0-src2`
10/0/0, `usse-ima32-full-c13-src2` 10/0/0, `usse-ima32-full-c13-src3` 8/0/0,
`usse-ima32-full-c3-src2` 10/0/0, `usse-ima32-full-c3-src3` 8/0/0, `usse-ima32-full-c45-src3` 8/0/0,
`usse-ima32-full-c56-src3` 8/0/0, `usse-ima32-full-c60-src2` 10/0/0, `usse-ima32-full-c60-src3`
8/0/0, `usse-ima32-full-carry` 22/0/0, `usse-ima32-full-cimm0` 8/0/0, `usse-ima32-full-cimm1`
21/0/0, `usse-ima32-full-cimm127` 8/0/0, `usse-ima32-full-cimm2` 8/0/0, `usse-ima32-full-s-cube`
147/0/0, `usse-ima32-full-u-cube` 343/0/0, `usse-ima32-neg-c56-src3` 8/0/0, `usse-ima32-neg-chain`
10/0/0, `usse-ima32-neg-cie-width` 10/0/0, `usse-ima32-neg-ima32-s-r10-r1-r2-neg-r3` 10/0/0,
`usse-ima32-neg-ima32-s-r10-r1-r2-r3-neg` 10/0/0, `usse-ima32-neg-ima32-u-r10-r1-1-r3-neg` 10/0/0,
`usse-ima32-neg-ima32-u-r10-r1-c56-neg-r3` 10/0/0, `usse-ima32-neg-ima32-u-r10-r1-r2-1-neg` 10/0/0,
`usse-ima32-neg-ima32-u-r10-r1-r2-c56-neg` 10/0/0, `usse-ima32-neg-ima32-u-r10-r1-r2-neg-r3` 10/0/0,
`usse-ima32-neg-ima32-u-r10-r1-r2-neg-r3-neg` 10/0/0, `usse-ima32-neg-ima32-u-r10-r1-r2-r3-neg`
10/0/0, `usse-ima32-neg-sub-c56` 80/0/0, `usse-ima32-neg-sub-c57u` 6/0/0, `usse-ima32-neg-sub-c58u`
6/0/0, `usse-ima32-neg-sub-c59s` 6/0/0, `usse-ima32-neg-sub-c59u` 6/0/0, `usse-ima32-neg-sub-reg`
8/0/0, `usse-ima32hi-generic-u` 282/0/0, `usse-ima32hi-signed-s` 282/0/0, `usse-ima32hi-sub-high`
75/0/0, `usse-imae-neg-chain64` 10/0/0, `usse-imae-neg-cie-width` 10/0/0, `usse-imae-neg-coe`
14/0/0, `usse-imae-neg-coe-cie` 14/0/0, `usse-imae-neg-coe-signed` 6/0/0, `usse-integer-idiv` 7/0/0,
`usse-integer-ima16` 4/0/0, `usse-integer-ima16-8bit` 8/0/0, `usse-integer-ima16-imm-c` 2/0/0,
`usse-integer-ima16-plain` 3/0/0, `usse-integer-ima16-reg-b` 2/0/0, `usse-integer-ima8` 8/0/0,
`usse-integer-imae-modes` 14/0/0, `usse-link-filler-control` 3/0/0, `usse-load-readers-alu` 0/6/0,
`usse-numbered-modifiers-family-rs` 32/0/0, `usse-pa-dest-persist` 1/0/0, `usse-raw25-ima32-bits`
3/9/0, `usse-raw25-ima32-x` 9/3/0, `usse-risky-lapc-backward` 6/0/0, `usse-risky-lapc-computed`
8/0/0, `usse-risky-lapc-direct` 8/0/0, `usse-scmp-ima32s` 164/0/0, `usse-ucmp2-pad-0` 48/0/0,
`usse-ucmp2-pad-1` 48/0/0, `usse-ucmp2-pad-3` 48/0/0, `usse-ucmp2-random-pairs` 252/0/0,
`usse-ucmp2-two-instructions` 64/0/0); unsupported mostly for reads R(N) before its DRC result lands
(wdf) (15); reads paN before the program writes it (12); flag .repeatN (9).

Confirmed on the hardware (a passing vector): #27, #28, #29, #172, #173, #174, #175, #176, #177,
#178, #179, #180.

### 7.6 Colour operations: `sop2`, `sop3`, `lrp`, `sop3c`, `sop2wm`

Classes 16-18 combine 8-bit colour channels, a colour part and an alpha part in one
instruction, with selectors naming what feeds each multiplier (`zero`, `s1`, `s2a`, `asat`,
`s2scale`, ...), `.comp` complements and an operation (`add`, `sub`, `min`, `max`) **[RE]**:

- `sop2 d, s1, s2, <colour>+asop2 <alpha>`: two sources;
- `sop3 d, s0, s1, s2, <colour>+asop|arsop|alrp <alpha>`: three sources;
- `lrp`: an interpolation between sources; `sop3c`: a sum of two products whose sources may be
  complemented;
- `sop2wm`: `sop2` with a destination byte mask and separate colour and alpha operations.

Operands use the 6-bit c10 reading (`.c10` after the register, *Source modifiers*).

- **Semantics [HW].** They read like the fixed-function blend and texture-combine operations of a
  GLES 1 era pipeline **[infer]**. Measured: per colour channel (bytes 0-2) `op(s1 × f1, s2 × f2)`,
  per alpha (byte 3) the same with the alpha selectors, the products summed exactly, divided by 255
  once, rounded and saturated; `min`/`max` compare the sources themselves; `asat` is `min(s1a, 1 -
  s2a)`, `s2scale` doubles the result and `zeros` makes `s2` signed. `lrp` is a lerp by `s0` or
  `s0a`, `sop3c` a sum of two selected products, `alrp` a lerp by `s0a`. `.c10` operands are signed
  10-bit lanes with 1.0 = 255, clamped to ±510 (*Colour operations*). `sop2.repeatN` advances the
  destination and both sources per iteration **[HW]**.
- **In the firmware:** not used **[RE]**; nor in the closed GLES2 programs we captured **[CAP]**.

`sop2 r0, r1, r2, s1, s2, add+asop2 s1a, s2a, add` assembles with form #165: enc[63:32] =
`0x80100450`, enc[31:0] = `0x00000082`; in memory (little endian) `82 00 00 00 50 04 10 80`.

| field | value | prints |
|---|---|---|
| `pred` | 0x0 | (none) |
| `flags` | 0x0 | (none) |
| `dst` | 0x0 | `r0` |
| `src1` | 0x1 | `r1` |
| `src2` | 0x2 | `r2` |
| `op` | 0x42 | `s1, s2, add` |
| `sop` | 0x22 | `s1a, s2a, add` |

Mnemonics: `+alrp`, `+arsop`, `+asop`, `+asop2`, `lrp`, `sop2`, `sop2wm`, `sop3`, `sop3c`.

Modifiers: `.end`, `.nosched`, `.repeatN`, `.skipinv`.

Simulator (`crates/sgx-sim`, from `doc/isa/sim-coverage.json`): 7 of 7 forms have semantics. The
probe vectors that test them: 407 match the hardware, 0 stop unsupported, 0 mismatch
(`usse-colour-ops-c10` 16/0/0, `usse-colour-ops-c10-other` 9/0/0, `usse-colour-ops-dot-repeats`
6/0/0, `usse-colour-ops-sop2-ops` 42/0/0, `usse-colour-ops-sop2-random` 24/0/0,
`usse-colour-ops-sop2-selectors` 88/0/0, `usse-colour-ops-sop2wm` 40/0/0,
`usse-colour-ops-sop2wm-bytemask` 5/0/0, `usse-colour-ops-sop3-lrp` 152/0/0,
`usse-colour-ops-sop3-random` 16/0/0, `usse-encoding-bits-sop2wm` 9/0/0).

Confirmed on the hardware (a passing vector): #165, #166, #167, #168, #169, #170, #171.

### 7.7 Integer dot products: `u8dot3`, `u8dot4`, `u16dot3`, `u16dot4`

Class 24 **[RE]**: three- and four-component dot products (`enc[56]` picks dot4, `enc[53:52]`
the result width), `off` variants (`enc[38]`), colour and alpha scales `Cx1`-`Cx8` and
`Ax1`-`Ax8`, complemented sources, and for `u8dot3` an alpha operation (`aadd`/`asub` with
selectors, or `alrp`/`alrpc` with a source 0).

- **Semantics [HW].** `S = Σ s1[i] × s2[i]` over bytes 0-2 (dot3) or 0-3 (dot4), or with `off`
  over `(s1[i] - 128)(s2[i] - 128)`. `u8dot` writes `S × Cx / 255` to every colour byte and
  `S × Ax / 255` (or the alpha operation) to byte 3, rounded, saturated to 0..255; `u16dot`
  writes `S × Cx × 32767 / 255²` to both halves, saturated to `0x7fff` (±`0x7fff` with `off`).
  The alpha operations add, subtract or interpolate the source alphas; a repeat advances
  the destination and both sources (*Integer dot products*).
- **In the firmware:** not used.

Mnemonics: `+aadd`, `+alrp`, `+alrpc`, `+asub`, `u16dot3`, `u16dot3off`, `u16dot4`, `u16dot4off`,
`u8dot3`, `u8dot3off`, `u8dot4`, `u8dot4off`.

Modifiers: `.end`, `.nosched`, `.repeatN`, `.skipinv`.

Simulator (`crates/sgx-sim`, from `doc/isa/sim-coverage.json`): 5 of 5 forms have semantics. The
probe vectors that test them: 152 match the hardware, 0 stop unsupported, 0 mismatch
(`usse-colour-ops-dot-repeats` 9/0/0, `usse-encoding-bits-u16dot3` 12/0/0,
`usse-encoding-bits-u8dot3` 10/0/0, `usse-encoding-bits-u8dot3-aadd` 5/0/0,
`usse-encoding-bits-u8dot4` 12/0/0, `usse-integer-dot-intdot-alpha` 32/0/0,
`usse-integer-dot-intdot-lanes` 72/0/0).

Confirmed on the hardware (a passing vector): #181, #182, #183, #184, #185.

### 7.8 `rlp`

Class 14 **[RE]**: `rlp d, s1, pN` with the bitwise group's flags, a write mask or repeat
count, one source and a seven-bit predicate number in `enc[20:14]`; the reference
disassembler reads no source 2.

- **Semantics [HW].** Rotate left through the predicate: `d = s << 1 | pN`, then `pN` takes
  bit 31 of `s`. Predicate numbers 4 and up alias `p0`-`p3` (number mod 4) (*`rlp`*).
- **In the firmware:** not used.

`rlp r1, r2, p0` assembles with form #186: enc[63:32] = `0x70001000`, enc[31:0] = `0x00200100`; in
memory (little endian) `00 01 20 00 00 10 00 70`.

| field | value | prints |
|---|---|---|
| `pred` | 0x0 | (none) |
| `flags` | 0x0 | (none) |
| `dst` | 0x1 | `r1` |
| `wmask` | 0x1 | (none) |
| `src1` | 0x2 | `r2` |
| `p` | 0x0 | `0` |

Mnemonics: `rlp`.

Modifiers: `.end`, `.nosched`, `.partial`, `.repeatN`, `.skipinv`, `.syncs`.

Simulator (`crates/sgx-sim`, from `doc/isa/sim-coverage.json`): 2 of 2 forms have semantics. The
probe vectors that test them: 77 match the hardware, 0 stop unsupported, 0 mismatch
(`usse-encoding-bits-followup-rlp-p0` 20/0/0, `usse-encoding-bits-followup-rlp-repeat-p0` 20/0/0,
`usse-form-coverage-rlp-repeat` 2/0/0, `usse-rlp-high-predicates` 3/0/0,
`usse-rlp-result-and-predicate` 32/0/0).

Confirmed on the hardware (a passing vector): #186, #187.

### 7.9 Pack and unpack: `pck*`, `unpck*`, `statomic`

Class 8 converts between data formats **[RE]**. `enc[43:38]` names the destination and source
formats together: `pck<dst><src>` packs to a narrower format, `unpck<dst><src>` widens, with
`u8`, `s8`, `o8` (offset 8-bit), `u16`, `s16`, `f16`, `f32` and `c10` (value 8 is `statomic`
instead). Each instruction takes two sources, each with a component select (`.0`-`.3`), a
destination byte mask (`.bytemaskXXXX`, all four bytes print nothing), a rounding mode
(`nearest`, `down`, `up`, `zero`) and `.scale` (`.renable` for the float-to-float ones).

- **What is known [CAP].** The closed GLES2 fragment program of our capture converts its four
  f16 colour components to 8-bit with `pcku8f16` into an attribute register
  and its clear vertex program unpacks the four bytes of a
  vertex colour to floats. So the group does carry colour conversion, as the names say.
- **Lanes [HW].** Source 1 and 2 fill the destination's lanes in turn (bytes 1, 2, 1, 2;
  halves 1, 2; `c10` lanes 1, 2, 1); the byte mask enables byte N with bit N and decides which
  source each enabled byte takes; component selects pick a byte, a half or a `c10` lane
  (*Pack and unpack lanes*).
- **Conversions [HW].** Unscaled conversions round in the instruction's mode and saturate;
  `.scale` maps 1.0 to 255, 127, 65535 or 32767 (`o8`: `x × 127 + 128`), symmetric for the
  signed formats, always to nearest even; `c10` is `x × 255` clamped to ±2.0; `pckf16f32`
  truncates unless `.renable`, which rounds to an integer; unpacks invert these exactly
  (*Pack and unpack conversions*).
- **`statomic`** writes, in both halves, the selected bytes of source 1 (low) and source 2
  (high) read as signed bytes, negatives made 0 **[HW]** (*Pack and unpack lanes*); what it is
  for is unknown.
- **In the firmware:** not used.

`pckf16f32 r0, r1.0, r1.1, nearest` assembles with form #161: enc[63:32] = `0x40001D7C`, enc[31:0] =
`0x00004081`; in memory (little endian) `81 40 00 00 7C 1D 00 40`.

| field | value | prints |
|---|---|---|
| `pred` | 0x0 | (none) |
| `op1` | 0x35 | `pckf16f32` |
| `wmask` | 0x1 | (none) |
| `dst` | 0x0 | `r0` |
| `flags` | 0xf | (none) |
| `src1` | 0x1 | `r1.0` |
| `src2` | 0x401 | `r1.1` |
| `op2` | 0x0 | `nearest` |

`unpckf32u8 r0, r1.0, r1.1, nearest` assembles with form #161: enc[63:32] = `0x400011BC`, enc[31:0]
= `0x00004081`; in memory (little endian) `81 40 00 00 BC 11 00 40`.

| field | value | prints |
|---|---|---|
| `pred` | 0x0 | (none) |
| `op1` | 0x6 | `unpckf32u8` |
| `wmask` | 0x1 | (none) |
| `dst` | 0x0 | `r0` |
| `flags` | 0xf | (none) |
| `src1` | 0x1 | `r1.0` |
| `src2` | 0x401 | `r1.1` |
| `op2` | 0x0 | `nearest` |

Mnemonics: `pckc10f16`, `pckc10f32`, `pckc10s16`, `pckc10u16`, `pckf16f16`, `pckf16f32`,
`pckf16s16`, `pckf16u16`, `pcko8f16`, `pcko8f32`, `pcko8s16`, `pcko8u16`, `pcks16f16`, `pcks16f32`,
`pcks16s16`, `pcks16u16`, `pcks8f16`, `pcks8f32`, `pcks8s16`, `pcks8u16`, `pcku16f16`, `pcku16f32`,
`pcku16s16`, `pcku16u16`, `pcku8f16`, `pcku8f32`, `pcku8s16`, `pcku8u16`, `statomic`, `unpckc10c10`,
`unpckf16c10`, `unpckf16o8`, `unpckf16s8`, `unpckf16u8`, `unpckf32c10`, `unpckf32f16`,
`unpckf32f32`, `unpckf32o8`, `unpckf32s16`, `unpckf32s8`, `unpckf32u16`, `unpckf32u8`,
`unpcks16c10`, `unpcks16o8`, `unpcks16s8`, `unpcks16u8`, `unpcku16c10`, `unpcku16o8`, `unpcku16s8`,
`unpcku16u8`, `unpcku8s8`, `unpcku8u8`.

Modifiers: `.end`, `.nosched`, `.repeatN`, `.scale`, `.skipinv`, `.syncs`.

Simulator (`crates/sgx-sim`, from `doc/isa/sim-coverage.json`): 4 of 4 forms have semantics. The
probe vectors that test them: 321 match the hardware, 0 stop unsupported, 0 mismatch
(`usse-form-coverage-pack-repeat` 4/0/0, `usse-memory-statomic` 24/0/0, `usse-pack-c10` 10/0/0,
`usse-pack-f16` 10/0/0, `usse-pack-o8-int` 7/0/0, `usse-pack-o8-scale` 6/0/0, `usse-pack-round-down`
5/0/0, `usse-pack-round-nearest` 5/0/0, `usse-pack-round-scale` 4/0/0, `usse-pack-round-up` 5/0/0,
`usse-pack-round-zero` 5/0/0, `usse-pack-s16-int` 7/0/0, `usse-pack-s16-scale` 6/0/0,
`usse-pack-s8-int` 7/0/0, `usse-pack-s8-scale` 6/0/0, `usse-pack-u16-bytemask` 16/0/0,
`usse-pack-u16-int` 7/0/0, `usse-pack-u16-scale` 6/0/0, `usse-pack-u8-bytemask` 16/0/0,
`usse-pack-u8-int` 7/0/0, `usse-pack-u8-scale` 6/0/0, `usse-pack-u8-scale-sweep` 6/0/0,
`usse-pack-unpack-16-scale` 4/0/0, `usse-pack-unpack-c10` 1/0/0, `usse-pack-unpack-c10-16` 28/0/0,
`usse-pack-unpack-c10-int` 8/0/0, `usse-pack-unpack-f16` 1/0/0, `usse-pack-unpack-o8-scale` 32/0/0,
`usse-pack-unpack-s16s8` 1/0/0, `usse-pack-unpack-s16u8` 1/0/0, `usse-pack-unpack-s8-scale` 32/0/0,
`usse-pack-unpack-select` 1/0/0, `usse-pack-unpack-u16s8` 1/0/0, `usse-pack-unpack-u16u8` 1/0/0,
`usse-pack-unpack-u8-scale` 32/0/0, `usse-pack-unpack-u8s8` 1/0/0, `usse-write-masks-wmask-other`
2/0/0).

Confirmed on the hardware (a passing vector): #161, #162, #163, #164.

### 7.10 Float multiply-add: `fmad`, `fadm`, `fmsa`, `fsubflr`

Class 0 **[RE]**. `enc[42:41]` picks `fmad`, `fadm`, `fmsa` (three sources) or `fsubflr` (two);
`enc[54]` reads the sources as half floats (*Source modifiers*; what it computes is **[open]**); the
float flags, a two-bit repeat (`.repeat2`-`.repeat4`) and, when `enc[53]` is clear, `.incsXYZ`.
Sources carry `.neg`/`.abs` (source 0 `.abs` only).

- **`fmad d, a, b, c`** computes `a × b + c` in IEEE binary32 **[infer]**: the firmware's six
  uses fit, and our emulation models it so. **[HW]** It rounds to nearest even, rounds the
  product before adding (not fused) and flushes denormals to a zero of their sign (*Float
  rounding and NaN*, *Denormals*). `fmad` with no source modifiers is also the usual way to
  write a float move or add: `a × 1 + -0` gives `a` for normals, infinities and zeros
  **[HW]**, flushing denormals and turning NaNs into `0x7fc00000` (*Denormals*).
- **`fadm d, a, b, c` = `a·c + b·c`**, **`fmsa d, a, b, c` = `a·a + b·c`** (products then
  the sum rounded) and **`fsubflr d, a, b` = `a - floor(b)`** **[HW]** (*`fadm`, `fmsa`,
  `fsubflr`*).
- **`.incsXYZ`**: X, Y and Z let `a`, `b` and `c` advance in a repeat; the destination always
  advances, and without `.incs` everything does **[HW]** (*`.incsXYZ`*).
- **The SGX540** reads these classes differently (a write mask, source-0 negation, no
  `.incs`) **[RE]**; the decoder only decodes them for the SGX545.

`fmad r0, r1, r2, r3` assembles with form #40: enc[63:32] = `0x00200000`, enc[31:0] = `0x00004103`;
in memory (little endian) `03 41 00 00 00 00 20 00`.

| field | value | prints |
|---|---|---|
| `pred` | 0x0 | (none) |
| `op` | 0x0 | `fmad` |
| `flags` | 0x0 | (none) |
| `repeat` | 0x0 | (none) |
| `incs` | 0x1 | (none) |
| `dst` | 0x0 | `r0` |
| `src0` | 0x1 | `r1` |
| `src1` | 0x2 | `r2` |
| `src2` | 0x3 | `r3` |

`fmad.repeat2.incs011 r0, r2, r4, r6` assembles with form #40: enc[63:32] = `0x00005100`, enc[31:0]
= `0x00008206`; in memory (little endian) `06 82 00 00 00 51 00 00`.

| field | value | prints |
|---|---|---|
| `pred` | 0x0 | (none) |
| `op` | 0x0 | `fmad` |
| `flags` | 0x0 | (none) |
| `repeat` | 0x1 | `.repeat2` |
| `incs` | 0x6 | `.incs011` |
| `dst` | 0x0 | `r0` |
| `src0` | 0x2 | `r2` |
| `src1` | 0x4 | `r4` |
| `src2` | 0x6 | `r6` |

Mnemonics: `fadm`, `fmad`, `fmsa`, `fsubflr`.

Modifiers: `.end`, `.incsXYZ`, `.nosched`, `.repeatN`, `.skipinv`, `.syncs`.

Simulator (`crates/sgx-sim`, from `doc/isa/sim-coverage.json`): 4 of 4 forms have semantics. The
probe vectors that test them: 152 match the hardware, 0 stop unsupported, 0 mismatch
(`usse-encoding-bits-fsubflr` 10/0/0, `usse-encoding-bits-fsubflr-f16` 10/0/0,
`usse-float-functions-sweep-fmad` 48/0/0, `usse-float-misc-fadm-fmsa-fsubflr` 27/0/0,
`usse-float-misc-fadm-fmsa-fsubflr-specials` 3/0/0, `usse-fmad-denormal` 3/0/0, `usse-fmad-fused`
1/0/0, `usse-fmad-move` 14/0/0, `usse-fmad-round` 3/0/0, `usse-fmad-zero-sign` 6/0/0,
`usse-form-coverage-form2-flt16` 4/0/0, `usse-moe-smlsi-three-sources` 14/0/0,
`usse-write-masks-incs-fmad` 9/0/0).

Confirmed on the hardware (a passing vector): #40, #41, #42, #43.

### 7.11 Single-source float functions: `frcp`, `frsq`, `flog`, `fexp`, `fsqrt`, `fsin`, `fcos`

Class 1 **[RE]**: one source (source 1) with `.neg`, `.abs` and a data type (`.flt16.0`/`.2`
for a half, `.c10.0`-`.3` for a c10 component), a destination with a write mask or a repeat
count, the float flags plus `.tpres`. The operation is `enc[42:41]` with `enc[48]`.

- **Semantics [HW].** `frcp` = 1/x, `frsq` = 1/√x, `fsqrt` = √x, within one ulp, not
  always correctly rounded; their sources are flushed if denormal and an invalid result is the
  NaN `0x7fffffff` (*`frcp`, `frsq` and `fsqrt` precision*). `flog` = log2 and `fexp` = 2^x
  within an ulp or two; `fsin`/`fcos` take quarter turns (`sin(πx/2)`) and return 15
  fraction bits (*`flog`, `fexp`, `fsin`, `fcos`*).
- **`.tpres`** changes nothing in a fill **[HW]** (*`.tpres`, `.partial`, `.nosched`,
  `.syncs`*); its purpose is unknown.
- **In the firmware:** not used.

`frcp r1, r2` assembles with form #44: enc[63:32] = `0x08001000`, enc[31:0] = `0x00200100`; in
memory (little endian) `00 01 20 00 00 10 00 08`.

| field | value | prints |
|---|---|---|
| `pred` | 0x0 | (none) |
| `op` | 0x0 | `frcp` |
| `flags1` | 0x0 | (none) |
| `dst` | 0x1 | `r1` |
| `wmask` | 0x1 | (none) |
| `src1` | 0x2 | `r2` |
| `flags2` | 0x0 | (none) |

`frsq.repeat2 r4, r2.abs` assembles with form #45: enc[63:32] = `0x08201240`, enc[31:0] =
`0x00800100`; in memory (little endian) `00 01 80 00 40 12 20 08`.

| field | value | prints |
|---|---|---|
| `pred` | 0x0 | (none) |
| `op` | 0x1 | `frsq` |
| `flags1` | 0x0 | (none) |
| `repeat` | 0x1 | `.repeat2` |
| `dst` | 0x4 | `r4` |
| `src1` | 0x2 | `r2` |
| `flags2` | 0x2 | `.abs` |

Mnemonics: `fcos`, `fexp`, `flog`, `frcp`, `frsq`, `fsin`, `fsqrt`.

Modifiers: `.end`, `.nosched`, `.repeatN`, `.skipinv`, `.syncs`, `.tpres`.

Simulator (`crates/sgx-sim`, from `doc/isa/sim-coverage.json`): 2 of 2 forms have semantics. The
probe vectors that test them: 274 match the hardware (242 with near values, each within the bound
the hardware was measured to), 0 stop unsupported, 0 mismatch (`usse-encoding-bits-frcp` 18/0/0,
`usse-encoding-bits-frcp-repeat` 18/0/0, `usse-flags-other` 3/0/0, `usse-float-functions-frcp`
6/0/0, `usse-float-functions-frsq` 5/0/0, `usse-float-functions-fsingle-base` 4/0/0,
`usse-float-functions-fsingle-specials` 4/0/0, `usse-float-functions-fsqrt` 5/0/0,
`usse-float-functions-sweep-fcos` 12/0/0, `usse-float-functions-sweep-fexp` 12/0/0,
`usse-float-functions-sweep-flog` 12/0/0, `usse-float-functions-sweep-frcp` 48/0/0,
`usse-float-functions-sweep-frsq` 48/0/0, `usse-float-functions-sweep-fsin` 12/0/0,
`usse-float-functions-sweep-fsqrt` 48/0/0, `usse-form-coverage-fsc-repeat` 3/0/0,
`usse-write-masks-wmask-frcp` 16/0/0).

Confirmed on the hardware (a passing vector): #44, #45.

### 7.12 Float dot products: `fdp`, `fdpc`, `fddp`, `fddpc`

Class 2 **[RE]**: `enc[42:41]` picks `fdp` (with `enc[14]` set, `fdpc` and a clip-plane number
`cp0`-`cp7`), `fddp` and `fddpc`. The `fddp` forms write an internal register `i0`/`i1` besides the
destination and so lose the destination's bank extension bit; `fddpc` takes two `cp` operands and
has no `.incs`. Half-float reading with `enc[54]` (what it computes is **[open]**).

- **`fdp.repeatN d, a, b`** sums the `N` products `(a+k)·(b+k)` and writes the sum to
  register `d + N - 1` only **[HW]**: `fdp.repeat3` is a three-component dot product. Each
  product is rounded, then the sums in order, to nearest even, as chained `fmad`s would; denormals
  are flushed and an invalid result is the NaN `0x7fc00000` **[HW]** (*Float dot products*).
- **`.incsXYZ`**: X, Y and Z let source 0, 1 and 2 advance **[HW]** (*`.incsXYZ`*).
- **`fddp d, iM, s0, s1, s2`** writes `d + N - 1 = s0·s1` and `iM = s0·s2` **[HW]**; `fddpc`
  the same with its sources held still **[HW]**.
- **`fdpc`, `fddpc`**: the value is `fdp`'s and `fddp`'s, and it also becomes user clip plane
  `cpN`'s distance for the vertex (E096) **[HW]**; it lands nowhere a program reads: not in
  `p0`-`p3`, `i0`-`i2` or the registers after `d` **[HW]**.
- **In the firmware:** not used.

`fdp r0, r4, r8` assembles with form #46: enc[63:32] = `0x10200000`, enc[31:0] = `0x00000208`; in
memory (little endian) `08 02 00 00 00 00 20 10`.

| field | value | prints |
|---|---|---|
| `pred` | 0x0 | (none) |
| `flags` | 0x0 | (none) |
| `repeat` | 0x0 | (none) |
| `incs` | 0x1 | (none) |
| `dst` | 0x0 | `r0` |
| `src1` | 0x4 | `r4` |
| `src2` | 0x8 | `r8` |

Mnemonics: `fddp`, `fddpc`, `fdp`, `fdpc`.

Modifiers: `.end`, `.incsXYZ`, `.nosched`, `.repeatN`, `.skipinv`, `.syncs`.

Simulator (`crates/sgx-sim`, from `doc/isa/sim-coverage.json`): 8 of 8 forms have semantics. The
probe vectors that test them: 128 match the hardware, 10 stop unsupported, 0 mismatch
(`usse-dot-products-fddp` 6/0/0, `usse-dot-products-fddpc` 3/0/0, `usse-dot-products-fdp-count`
4/0/0, `usse-dot-products-fdp-incs` 9/0/0, `usse-dot-products-fdp-rounding` 48/0/0,
`usse-dot-products-fdp-specials` 8/0/0, `usse-dot-products-fdpc` 6/0/0,
`usse-dot-products-fdpc-clip` 16/0/0, `usse-encoding-bits-fddpc` 0/4/0, `usse-encoding-bits-fdp`
9/0/0, `usse-encoding-bits-fdp-f16` 9/0/0, `usse-encoding-bits-fdpc` 0/6/0,
`usse-encoding-bits-fdpc-f16` 6/0/0, `usse-form-coverage-form2-flt16` 4/0/0); unsupported mostly for
fdpc rounding (not measured) (6); fddpc rounding (not measured) (4).

Confirmed on the hardware (a passing vector): #46, #47, #48, #49, #50, #51, #52, #53.

### 7.13 Float min/max: `fminmax`, `fmaxmin`

Class 3 **[RE]**: the class-0 layout with three sources, the operation in `enc[41]` (`enc[42]`
does not decode).

- **`fminmax d, a, b, c` = `min(max(a, b), c)`** and **`fmaxmin d, a, b, c` = `max(min(a, c),
  b)`** **[HW]**: both clamp `a` to `[b, c]`, and differ when `b > c` (`c`, `b`). min and max
  are IEEE minNum/maxNum (a NaN loses, `-0 < +0`), denormals flushed **[HW]** (*Float min/max*).
- **`.incsXYZ`** as for `fmad` **[HW]**.
- **In the firmware:** not used.

`fminmax r0, r1, r2, r3` assembles with form #54: enc[63:32] = `0x18200200`, enc[31:0] =
`0x00004103`; in memory (little endian) `03 41 00 00 00 02 20 18`.

| field | value | prints |
|---|---|---|
| `pred` | 0x0 | (none) |
| `op` | 0x1 | `fminmax` |
| `flags` | 0x0 | (none) |
| `repeat` | 0x0 | (none) |
| `incs` | 0x1 | (none) |
| `dst` | 0x0 | `r0` |
| `src0` | 0x1 | `r1` |
| `src1` | 0x2 | `r2` |
| `src2` | 0x3 | `r3` |

Mnemonics: `fmaxmin`, `fminmax`.

Modifiers: `.end`, `.incsXYZ`, `.nosched`, `.repeatN`, `.skipinv`, `.syncs`.

Simulator (`crates/sgx-sim`, from `doc/isa/sim-coverage.json`): 2 of 2 forms have semantics. The
probe vectors that test them: 88 match the hardware, 0 stop unsupported, 0 mismatch
(`usse-float-minmax-allnan` 1/0/0, `usse-float-minmax-fmaxmin-roles` 16/0/0,
`usse-float-minmax-fmaxmin-specials` 22/0/0, `usse-float-minmax-fminmax-incs` 9/0/0,
`usse-float-minmax-fminmax-roles` 16/0/0, `usse-float-minmax-fminmax-specials` 22/0/0,
`usse-form-coverage-form2-flt16` 2/0/0).

Confirmed on the hardware (a passing vector): #54, #55.

### 7.14 Screen-space derivatives: `fdsx`, `fdsy`

Class 4 **[RE]**: two sources in the class-0 layout, the operation in `enc[41]`.

- **Semantics [HW].** Coarse derivatives over the 2x2 quad (GLSL `dFdx`/`dFdy`): `fdsx d, a, b`
  = `a`(top-right) − `b`(top-left), `fdsy d, a, b` = `a`(bottom-left) − `b`(top-left), the
  same value in all four pixels (*Derivatives*).
- **In the firmware:** not used.

`fdsx r1, r2, r3` assembles with form #56: enc[63:32] = `0x20200000`, enc[31:0] = `0x00200103`; in
memory (little endian) `03 01 20 00 00 00 20 20`.

| field | value | prints |
|---|---|---|
| `pred` | 0x0 | (none) |
| `op` | 0x0 | `fdsx` |
| `flags` | 0x0 | (none) |
| `repeat` | 0x0 | (none) |
| `incs` | 0x1 | (none) |
| `dst` | 0x1 | `r1` |
| `src1` | 0x2 | `r2` |
| `src2` | 0x3 | `r3` |

Mnemonics: `fdsx`, `fdsy`.

Modifiers: `.end`, `.incsXYZ`, `.nosched`, `.repeatN`, `.skipinv`, `.syncs`.

Simulator (`crates/sgx-sim`, from `doc/isa/sim-coverage.json`): 2 of 2 forms have semantics. The
probe vectors that test them: 44 match the hardware, 0 stop unsupported, 0 mismatch
(`usse-encoding-bits-fdsx` 10/0/0, `usse-encoding-bits-fdsx-f16` 10/0/0,
`usse-form-coverage-form2-flt16` 2/0/0, `usse-gradients-fds-incs` 12/0/0, `usse-gradients-fds-quad`
6/0/0, `usse-instance-masking-skipinv-grad` 4/0/0).

Confirmed on the hardware (a passing vector): #56, #57.

### 7.15 Half-float multiply-add: `fmad16`

Class 6 **[RE]**: three sources, each with a swizzle (`.swzll`, `.swzhh`, `.swzf32`) and
`.neg`/`.abs` (source 0 `.abs` only); `enc[44]` is a repeat of two, which brings `.incsXYZ`;
no `.end`.

- **Semantics [HW].** Two half-float multiply-adds at once, `a × b + c` on the low and on the
  high halves: the product rounded to binary32, the sum to a half, both to nearest even (one
  rounding for two halves), half denormals kept. `.swzll`/`.swzhh` feed both lanes one half;
  `.swzf32` feeds the 32-bit register as a binary32 value. `.incsXYZ` as for `fmad`
  (*Half-float multiply-add*).
- **In the firmware:** not used.

`fmad16 r0, r1, r2, r3` assembles with form #58: enc[63:32] = `0x30000000`, enc[31:0] =
`0x00004103`; in memory (little endian) `03 41 00 00 00 00 00 30`.

| field | value | prints |
|---|---|---|
| `pred` | 0x0 | (none) |
| `flags1` | 0x0 | (none) |
| `flags2` | 0x0 | (none) |
| `dst` | 0x0 | `r0` |
| `src0` | 0x1 | `r1` |
| `flags3` | 0x0 | (none) |
| `src1` | 0x2 | `r2` |
| `flags4` | 0x0 | (none) |
| `src2` | 0x3 | `r3` |
| `flags5` | 0x0 | (none) |

Mnemonics: `fmad16`.

Modifiers: `.incsXYZ`, `.nosched`, `.repeatN`, `.skipinv`, `.syncs`.

Simulator (`crates/sgx-sim`, from `doc/isa/sim-coverage.json`): 1 of 1 forms have semantics. The
probe vectors that test them: 67 match the hardware, 0 stop unsupported, 0 mismatch
(`usse-fmad16-incs` 8/0/0, `usse-fmad16-lanes` 36/0/0, `usse-fmad16-rounding` 20/0/0,
`usse-fmad16-specials` 3/0/0).

Confirmed on the hardware (a passing vector): #58.

### 7.16 Extended float operation: `efo`

Class 7 **[RE]**. Every bit is a field: two multipliers `m0`, `m1` and two adders `a0`, `a1`
whose inputs are selections among the three sources and the internal registers `i0`, `i1`;
the destination takes one of `i0`, `i1`, `a0`, `a1`; `i0` and `i1` are written (or not,
`!i0`) from the adders or multipliers; each source has a `.neg`; flags `.skipinv`,
`.nosched`, `.gpiext` and a repeat.

```
efo d= <i0|i1|a0|a1>, <i0/i1 writes>, a0=<x>+<y>, a1=<x>+<y>, m0=<x>*<y>, m1=<x>*<y>, s0, s1, s2
```

- **Semantics [HW].** A small dataflow of two multiplies and two adds per instruction,
  with `i0`/`i1` as accumulators across instructions: the text the decoder prints is the
  dataflow. Each product and each sum is rounded to binary32; the destination's `i0`/`i1`
  are the values before the instruction's own writes. Sources print both their 32-bit and
  half-float readings (`r1/r1.flt16.0`) where the two differ; the 32-bit reading is the one we
  probed.
- **`.gpiext` [HW]** works across the 2x2 quad: the multipliers read the instance's `i2` and
  `i0` for `i0` and `i1`, an `i0` write goes to its `i2`, and the four `i1` writes end in the
  top-right instance's `i0`, whose reads during the instruction see the top-left instance's
  `i0` or, by timing, its write (*`efo`*).
- **In the firmware:** not used.

Mnemonics: `efo`.

Modifiers: `.gpiext`, `.nosched`, `.repeatN`, `.skipinv`.

Simulator (`crates/sgx-sim`, from `doc/isa/sim-coverage.json`): 1 of 1 forms have semantics. The
probe vectors that test them: 83 match the hardware, 16 stop unsupported, 0 mismatch
(`usse-efo-dataflow` 41/0/0, `usse-efo-denormals` 0/4/0, `usse-efo-rounding` 24/0/0,
`usse-internal-registers-efo-gpiext` 0/8/0, `usse-internal-registers-efo-gpiext-quad` 18/0/0,
`usse-internal-registers-efo-gpiext-race` 0/4/0); unsupported mostly for efo.gpiext reaches the
other instances of the quad (8); reads iN before the program writes it (4); the top-right iN read
races the iN writes (4).

Confirmed on the hardware (a passing vector): #59.

### 7.17 Fixed-point multiply-add: `fpma`

Class 25 **[RE]**: destination and three sources in the c10 reading, then colour selections
(`s0`/`s1`/`s0a`/`s1a`, `s1`/`s1a`, `s2`/`s2a`) and alpha selections, each with a `.comp`
complement; the flags carry a three-bit repeat and `.sat`.

- **Semantics [HW].** A colour multiply-add, `c0 + c1 × c2` per channel with the first
  selection the addend, on 8-bit channels or, with `.c10`, signed 10-bit ones (*`fpma`*);
  `.sat` changes nothing we measured, also on `c10` results out of 0..1.0, and a repeat
  advances every operand **[HW]**.
- **In the firmware:** not used.

Mnemonics: `fpma`.

Modifiers: `.end`, `.nosched`, `.repeatN`, `.sat`, `.skipinv`.

Simulator (`crates/sgx-sim`, from `doc/isa/sim-coverage.json`): 1 of 1 forms have semantics. The
probe vectors that test them: 51 match the hardware, 0 stop unsupported, 0 mismatch
(`usse-colour-ops-dot-repeats` 3/0/0, `usse-colour-ops-fpma` 36/0/0, `usse-colour-ops-fpma-sat`
12/0/0).

Confirmed on the hardware (a passing vector): #60.

### 7.18 Dual issue: two operations in one word

Class 27 **[RE]** packs a **primary** operation on the usual operands and a **secondary**
operation on internal registers into one word, printed `primary + secondary`:

```
fmad r0, r1, r2, r3+fmad i0, i0, i1, i2
mov r0, r1+frcp i0, i1
```

- **Primary** (`enc[51:50]` with `enc[58]`): `fmad`, `fadm`, `fmsa`, `fminmax`, `ima32`,
  `mov`, `fddp` or `fssq`, with `.skipinv`, `.syncs`, `.nosched` and `.repeat2`, a two-bit
  predicate and a destination without the bank extension.
- **Secondary** (`enc[41:38]`): `fmad`, `fmad16`, `fmsa`, `fmaxmin`, `ima32`, `fsubflr`,
  `fadd`, `fsub`, `fmul`, `frcp`, `frsq`, `fexp`, `flog`, `fsin`, `fcos` or `mov`. Its
  destination is `i0`-`i2`; its operands are `i0`-`i2` or, for selection 3, the primary's
  source in the same position. Because of that shared reference, one form exists per
  secondary operand shape and per selection, which is why the class has some sixty forms.
- `enc[54]` reads the sources as half floats, as in class 0 (what it computes is **[open]**).
- **Semantics [HW].** Two operations issued together: both read the values from before the
  word, the secondary wins a shared destination, a selection-3 source is the primary's register
  without its `.neg`, `.repeat2` repeats both, and the two-bit predicate (`enc[57:56]`: always,
  `p0`, `p1`, `!p0`) covers both; `fssq d, a, b` is `a·a + b·b`. Pairs that need the same unit
  give mixed results, the secondary taking the primary's intermediate value (*Dual issue*).
- **In the firmware:** not used.

`mov r0, r1+frcp i0, i1` assembles with form #69: enc[63:32] = `0xD8044140`, enc[31:0] =
`0x00000080`; in memory (little endian) `80 00 00 00 40 41 04 D8`.

| field | value | prints |
|---|---|---|
| `sop` | 0x5 | `frcp` |
| `sreg` | 0x0 | `i0` |
| `ssrc1` | 0x401 | `i1` |
| `pred` | 0x0 | (none) |
| `op` | 0x1 | `mov` |
| `dst` | 0x0 | `r0` |
| `src1` | 0x1 | `r1` |

Mnemonics: `+fadd`, `+fcos`, `+fexp`, `+flog`, `+fmad`, `+fmad16`, `+fmaxmin`, `+fmsa`, `+fmul`,
`+frcp`, `+frsq`, `+fsin`, `+fsub`, `+fsubflr`, `+ima32`, `+mov`, `fadm`, `fddp`, `fmad`, `fminmax`,
`fmsa`, `fssq`, `ima32`, `mov`.

Modifiers: `.nosched`, `.repeatN`, `.skipinv`, `.syncs`.

Simulator (`crates/sgx-sim`, from `doc/isa/sim-coverage.json`): 59 of 59 forms have semantics. The
probe vectors that test them: 226 match the hardware (39 with near values, each within the bound the
hardware was measured to), 5 stop unsupported, 0 mismatch (`usse-dual-issue-conflicts` 12/0/0,
`usse-dual-issue-ima32` 34/0/0, `usse-dual-issue-pairs` 23/0/0, `usse-dual-issue-predicates` 12/0/0,
`usse-dual-issue-shared` 14/0/0, `usse-encoding-bits-dual-dual-fddp-frcp` 0/3/0,
`usse-encoding-bits-dual-dual-fddp-mov` 0/2/0, `usse-encoding-bits-dual-dual-fmad-frcp` 3/0/0,
`usse-encoding-bits-dual-dual-fmad-mov` 2/0/0, `usse-encoding-bits-dual-dual-fssq-fadd` 9/0/0,
`usse-encoding-bits-dual-dual-fssq-frcp` 11/0/0, `usse-encoding-bits-dual-dual-fssq-mov` 2/0/0,
`usse-encoding-bits-dual-dual-mov-fadd` 10/0/0, `usse-encoding-bits-dual-dual-mov-fmad` 2/0/0,
`usse-encoding-bits-dual-dual-mov-frcp` 22/0/0, `usse-encoding-bits-dual-dual-mov-mov` 13/0/0,
`usse-form-coverage-dual` 19/0/0, `usse-form-coverage-form2-dual-flt16` 38/0/0); unsupported mostly
for fddp rounding (not measured) (5).

Confirmed on the hardware (a passing vector): #61, #62, #63, #65, #67, #68, #69, #70, #71, #72, #73,
#74, #75, #76, #77, #78, #79, #80, #81, #82, #83, #84, #85, #86, #87, #88, #89, #90, #91, #92, #93,
#94, #95, #96, #97, #98, #99, #100, #101, #102, #103, #104, #105, #106, #107, #108, #109, #110,
#111, #112, #113, #114, #115, #116, #117, #118, #119; not yet confirmed (as decoded; no passing
vector yet): #64, #66.

### 7.19 Loads and stores: `ld*`, `st*`, `eldd`, `eldq`

Classes 29 (loads) and 30 (stores) **[RE]**. The mnemonic is `ld`/`st` plus an address mode and
a data type: `ldad` = load, absolute (`a`), dword (`d`); `l` and `t` are the other address
modes (local and tiled **[infer]**, both **[open]**), `w` and `b` 16- and 8-bit data. The base
is a source-0 operand, the offset a source-1 operand (an immediate or a register), and
`enc[41:40]` picks plain, pre-increment or post-increment addressing. Flags: `.skipinv`,
`.syncs`, `.nosched` (stores), the cache mode (`.bpcache`, `.fcfill`, `.bypassl1`), `.noread`
and `.rangeenable` (stores), and a count used as `.fetchN` (MOE-expand bit `enc[53]` clear)
or `.repeatN` (set). A load can name a range operand (source 2) and always names a data fence
`drc0`/`drc1`.

**Addressing [HW/RE].** Offsets count elements of the data size (4 bytes for `d`, 2 for `w`):

| form | elements accessed | base writeback |
|------|-------------------|----------------|
| `[b,+#k]` / `[b,-#k]` | `b+k` / `b-k` | none |
| `[b,++#k]` (pre) | `b+k` | `b += k` |
| `[b,#k++]` (post) | `b` | `b += k` |
| `.fetchN [b,+#k]` | **`b+k+1` ... `b+k+N`** | none |
| `.fetchN [b,#k++]` | `b+k` ... `b+k+N-1` | `b += N` |

A fetch with a base-plus-offset address starts **one element after** the printed offset:
`ldad.fetch4 r3, [r2,+#1]` loads dwords 2-5 into `r3`-`r6`. This holds for every count from 2 to
16, by immediate and by register offset, and a plain load reads the offset itself **[HW]**
(*E093*). The post-increment fetch was checked on the laptop (the kernel CCB fetch and the
GETMISCINFO reply, `doc/specs/hw_spec.md`) **[HW]**; its writeback follows from the
firmware's loops **[infer]**. Before any `smlsi`, a fetch steps its destination by one register
**[HW]**. After one, it steps by the fourth `smlsi` increment **[infer]**: the firmware sets
`0, 0, 0, 1` before its fetches. A fetch whose registers would run past the task's temporaries
writes **none of them**: with 32 temporaries, `ldad.fetch4 r28` loads `r28`-`r31`, while
`ldad.fetch4 r29` and `r30` leave all four as they were **[HW]** (*E093*; the reason vector `vec1`'s
`ldad.fetch4 r30` left `r31` unchanged). A **register** offset `o` (`[b,+rN]`) is
`(o >> 16) × (o & 0xffff)` bytes, and a fetch starts one element after it too **[HW]** (*Register
offsets of loads and stores*); the firmware has four such stores.

- **A store has a fetch too [HW].** `stad.fetchN [rb,+#k], rs` stores `rs` to `rs + N - 1` in the N
  consecutive dwords `b + k + 1` to `b + k + N`, the one-dword shift of a load fetch (N = 2, 4 and
  16 with `k` = 1 and N = 4 with `k` = 0: 4 of 4 cases, E482; `fetch4` with `k` = 2, 3, 4, 7, 8 and
  15, `fetch8` with 3 and `fetch16` with 2: 8 of 8, E516), `stad.fetchN [rb,#k++], rs` stores them
  from `b + k` and moves `rb` by N once for `k` = 1 to 4 (`k` = 1 with N = 2, 4 and 16: 3 of 3,
  E482; `fetch4` with `k` = 2 and 3, `fetch8` with 2 and `fetch2` with 4: 4 of 4, E516: the step is
  the fetch width, not `k`), and `stad.fetchN [rb,++#k], rs` stores them from `b + k + 1` and moves
  `rb` by N for `k` = 1 and 2 (`fetch4` with `k` = 1 and 2 and `fetch16` with 1: 3 of 3, E516); the
  post- and pre-increment rules were read from those readbacks after the first predictions failed. A
  copy of 16 dwords is so `ldad.fetch16 rA, [rS,+#0], drc0; wdf drc0; stad.fetch16 [rD,+#0], rA`
  with `rD` one dword below the destination (1 of 1 case: 16 dwords in order). A fetch wider than
  16, `k` above 15 and a copy with `k` other than 0 were not run.
- **`.repeatN` of a store or a load steps the pointer register too [HW].** In
  `stad.repeatN [rb,...], rs` iteration `i` stores `r(s + i)` at the address held in `r(b + i)` (the
  data address read for every `i`: N = 2, 3, 4, 8 and 16 in E483, 5 to 7 and 9 to 15 in E515), and
  the pointer registers `r(b + i)` for `i` < N move by the form's own increment: `k` after its
  access for `[rb,#k++]`, `k` before it for `[rb,++#k]`, none for `[rb,+#k]`, and the other pointers
  stay (E483: 26 of 26 cases with 16 valid pointers `r40`-`r55`, N = 2, 3, 4, 8 and 16 plain, N = 2,
  4, 8 and 16 post-increment, N = 2 and 4 pre-increment, twelve after an `smlsi` and one copy, the
  movement read for `r40` to `r43`; E515: a marker past each of the sixteen pointers, N = 5 to 16
  post-incremented with `k` = 1 and N = 8, 12 and 16 with `k` = 2 (15 of 15), N = 8, 12 and 16
  pre-incremented with `k` = 1 and N = 8 with `k` = 2 (4 of 4), so `r44` to `r55` move as `r40` to
  `r43` do and the unused pointers stay). `ldad.repeatN rd, [rb,...]` loads likewise the dword
  `r(b + i)` addresses into `r(d + i)` (E483: 7 of 7 cases, N = 2, 4, 8 and 16, the pointer movement
  read for 2 or 4 pointers; E515: from `r(56 + i)` into `r(10 + i)` in 11 of 11 plain cases, N = 5
  to 7 and 9 to 16, and `r(56 + i)` moved for `i` < N in 10 of 10 post-incremented cases). A
  pre-incremented `ldad.repeat`, an `smlsi` before a repeat of five or more and N above 16 were not
  run. The model had N accesses from the one pointer `rb`. With only `rb` (and `r41` for the loads)
  holding an address, the registers after it are read as pointers too: the first run faulted the job
  in all 7 `ldad.repeatN` cases and in the 9 of 9 `stad.repeatN` cases with N of 4, 8 and 16, while
  `stad.repeat2` and `repeat3` completed, storing `r3` at the address `r41` held (E483). The
  one-pointer series is `smlsi #0, #0, #0, #1` first (*`smlsi` increments*):
  `stad.repeat16 [rb,#1++], r2` then stores `r2` to `r17` at 16 consecutive dwords and moves `rb` by
  16 (2 of 2 cases, two instructions, no one-dword shift).
- **Cache modes.** The firmware uses `.bpcache` on almost every access; `.fcfill` once.
  The SGX540 swaps the two cache-mode bits; `usse-dis --core 540` follows it. No mode, `eld`'s
  `.bypassl1` included, makes a reload miss a store, in one instance or across instances
  **[HW]** (E098). Nor does any mode keep an old dword when the host writes it while the job
  runs: every load mode, after a warming load of any mode, reads the host's value within one
  reload **[HW]** (E107). What the modes change is **[open]**; it does not show in the data
  a load returns.
- **`eldd`/`eldq d, [base, index, #offset], limit`** (class 29 with `enc[54]` set) load the
  dword (`eldd`) or four dwords (`eldq`) of element `index + offset` from the base when it is
  below `limit`, and zeros otherwise: a bounds-checked load **[HW]** (E098). Indices or limits
  with bit 31 set are **[open]**; the firmware does not use them.

**Byte and halfword loads [HW]** (E598, fills): `ldab` and `ldaw` with an immediate offset n read
the byte at base + n and the halfword at base + 2n, zero-extended (the offset counts elements of
the access size; 16 of 16 jobs), and `ldaw` and `ldad` at an address that is not a multiple of
their size read the bytes at that address, across the dword boundary too (6 of 6). Not run in a
firmware task (the verifier refuses the forms).

**In the firmware [RE].** 598 loads and 349 stores, nearly all `ldad`/`stad` with `.bpcache`
on its control blocks through `sa0`-`sa2` or computed bases; 120 fetches; `ldaw` twice. Its
807 `wdf` (for 598 loads and 196 `ldr`) show the pattern: issue the loads, then wait on the
counter before the first use.

From `asm/tri/use_vtx.s`:

```
        p0 ldad.skipinv.fetch4 pa0, [pa0,+#0], drc0
```

`ldad.fetch4 r3, [r2,+#1], drc0` assembles with form #30: enc[63:32] = `0xE8033000`, enc[31:0] =
`0xA0608080`; in memory (little endian) `80 80 60 A0 00 30 03 E8`.

| field | value | prints |
|---|---|---|
| `pred` | 0x0 | (none) |
| `op` | 0x0 | `ad` |
| `flags` | 0x60 | `.fetch4` |
| `dst` | 0x3 | `r3` |
| `base` | 0x2 | `r2` |
| `mode` | 0x0 | (none) |
| `sign` | 0x0 | `+` |
| `src1` | 0x301 | `#1` |
| `extra` | 0x300 | (none) |
| `drc` | 0x0 | `0` |

`stad [r2,+#7], r9` assembles with form #33: enc[63:32] = `0xF0220000`, enc[31:0] = `0x80008389`; in
memory (little endian) `89 83 00 80 00 00 22 F0`.

| field | value | prints |
|---|---|---|
| `pred` | 0x0 | (none) |
| `op` | 0x0 | `ad` |
| `flags` | 0x80 | (none) |
| `base` | 0x2 | `r2` |
| `mode` | 0x0 | (none) |
| `sign` | 0x0 | `+` |
| `src1` | 0x307 | `#7` |
| `src2` | 0x9 | `r9` |

Mnemonics: `eldd`, `eldq`, `ldab`, `ldad`, `ldaw`, `ldlb`, `ldld`, `ldlw`, `ldtb`, `ldtd`, `ldtw`,
`stab`, `stad`, `staw`, `stlb`, `stld`, `stlw`, `sttb`, `sttd`, `sttw`.

Modifiers: `.bpcache`, `.bypassl1`, `.fcfill`, `.fetchN`, `.noread`, `.nosched`, `.rangeenable`,
`.repeatN`, `.skipinv`, `.syncs`.

Simulator (`crates/sgx-sim`, from `doc/isa/sim-coverage.json`): 7 of 7 forms have semantics. The
probe vectors that test them: 757 match the hardware, 113 stop unsupported, 0 mismatch
(`texture-mipmaps-mip-bias` 5/0/0, `texture-mipmaps-mip-grad` 8/0/0, `texture-mipmaps-mip-level`
13/0/0, `texture-mipmaps-mip-minfilter` 15/0/0, `texture-mipmaps-mip-mipfilter` 24/0/0,
`texture-mipmaps-mip-t0-field` 12/0/0, `texture-sampler-cache-texcache-cold` 2/0/0,
`texture-sampler-pcff16` 8/0/0, `texture-sampler-smp-srd` 15/0/0, `usse-cache-control-cross` 0/54/0,
`usse-cache-control-eld-address` 48/0/0, `usse-cache-control-eld-limit` 44/12/0,
`usse-cache-control-levels` 40/0/0, `usse-decoder-vectors-ldad-imm0` 1/0/0,
`usse-decoder-vectors-ldad-imm1` 1/0/0, `usse-decoder-vectors-ldad-imm16` 1/0/0,
`usse-decoder-vectors-ldad-imm2` 1/0/0, `usse-decoder-vectors-ldad-imm3` 1/0/0,
`usse-decoder-vectors-ldad-imm63` 1/0/0, `usse-decoder-vectors-ldad-imm7` 1/0/0,
`usse-decoder-vectors-ldad-postinc` 1/0/0, `usse-decoder-vectors-ldad-reg` 10/0/0,
`usse-decoder-vectors-ldad-regneg` 5/0/0, `usse-decoder-vectors-stad-imm0` 2/0/0,
`usse-decoder-vectors-stad-imm1` 2/0/0, `usse-decoder-vectors-stad-imm16` 2/0/0,
`usse-decoder-vectors-stad-imm2` 2/0/0, `usse-decoder-vectors-stad-imm3` 2/0/0,
`usse-decoder-vectors-stad-imm63` 2/0/0, `usse-decoder-vectors-stad-imm7` 2/0/0,
`usse-decoder-vectors-stad-postinc` 6/0/0, `usse-decoder-vectors-stad-reg` 10/0/0,
`usse-fence-batching-counters` 1/6/0, `usse-fence-batching-empty-wdf` 2/0/0,
`usse-fence-batching-mixed` 5/0/0, `usse-fence-batching-no-wait` 0/9/0,
`usse-fence-batching-one-wdf` 5/0/0, `usse-fence-batching-store-then-load` 22/0/0,
`usse-fence-batching-store-then-load-recorded` 12/0/0, `usse-fence-growth-fetch16` 5/0/0,
`usse-fence-growth-ldad-drc0` 6/0/0, `usse-fence-growth-ldad-drc1` 3/0/0,
`usse-fence-growth-ldad-reuse` 3/0/0, `usse-form-coverage-ld-pre` 4/0/0, `usse-form-coverage-st-pre`
6/0/0, `usse-fw37-narrow-ld-unaligned` 6/0/0, `usse-fw37-narrow-ldab-offsets` 8/0/0,
`usse-fw37-narrow-ldaw-offsets` 8/0/0, `usse-fw37-narrow-stab` 16/0/0,
`usse-fw37-narrow-stad-unaligned-control` 3/0/0, `usse-fw37-narrow-staw` 7/0/0,
`usse-fw37-pred-pred-notp0-mov-imm` 6/0/0, `usse-fw37-pred-pred-notp0-mov-reg` 6/0/0,
`usse-fw37-pred-pred-p0-mov-imm` 6/0/0, `usse-fw37-pred-pred-p0-mov-reg` 6/0/0,
`usse-internal-registers-ireg-ldad` 0/20/0, `usse-load-readers-alu` 0/6/0, `usse-load-readers-slots`
0/5/0, `usse-load-readers-waw` 5/0/0, `usse-memory-ldad-reg-off` 16/0/0,
`usse-memory-ldad-reg-off-fetch` 2/0/0, `usse-memory-ldad-reg-off-neg` 4/0/0,
`usse-memory-mem-forms` 3/0/0, `usse-memory-stad-reg-off` 6/0/0,
`usse-memory-stad-reg-off-unaligned` 3/0/0, `usse-moe-setfc` 10/0/0, `usse-moe-setfc-fetch` 10/0/0,
`usse-numbered-modifiers-family-fetch` 32/0/0, `usse-numbered-modifiers-family-fetch-dst` 8/0/0,
`usse-numbered-modifiers-family-fetch-edge` 6/0/0, `usse-reload-growth-n104-drc0` 1/0/0,
`usse-reload-growth-n112-drc0` 1/0/0, `usse-reload-growth-n128-drc0` 1/0/0,
`usse-reload-growth-n128-drc1` 1/0/0, `usse-reload-growth-n160-drc0` 1/0/0,
`usse-reload-growth-n192-drc0` 1/0/0, `usse-reload-growth-n192-drc1` 1/0/0,
`usse-repeat-ptrs-fetch-offset` 8/0/0, `usse-repeat-ptrs-fetch-post` 4/0/0,
`usse-repeat-ptrs-fetch-pre` 3/0/0, `usse-repeat-ptrs-ldad-plain` 11/0/0,
`usse-repeat-ptrs-ldad-post` 10/0/0, `usse-repeat-ptrs-stad-plain` 10/0/0,
`usse-repeat-ptrs-stad-post` 15/0/0, `usse-repeat-ptrs-stad-pre` 4/0/0, `usse-store-own-cross`
9/0/0, `usse-store-own-load` 20/0/0, `usse-store-own-one` 12/0/0, `usse-store-own2-cross` 14/0/0,
`usse-store-own2-load` 20/0/0, `usse-store-own2-quad` 14/0/0, `usse-store-repeat-copy16` 4/0/0,
`usse-store-repeat-fetch-spelling` 7/0/0, `usse-store-repeat-plain` 1/1/0,
`usse-store-repeat-postinc` 2/0/0, `usse-store-repeat-preinc` 1/0/0, `usse-store-repeat-regs-copy16`
2/0/0, `usse-store-repeat-regs-ldad-repeat` 7/0/0, `usse-store-repeat-regs-plain` 5/0/0,
`usse-store-repeat-regs-postinc` 5/0/0, `usse-store-repeat-regs-preinc` 3/0/0,
`usse-store-repeat-regs-smlsi` 12/0/0, `usse-store-repeat-regs2-ldad-repeat` 7/0/0,
`usse-store-repeat-smlsi` 2/0/0); unsupported mostly for gN (per-instance values, not modelled)
(54); reads R(N) before its DRC result lands (wdf) (26); fetch past the temporaries (16).

Confirmed on the hardware (a passing vector): #30, #31, #32, #33, #34, #35, #124.

### 7.20 Texture sampling: `smp1d`, `smp2d`, `smp3d`

Class 28 **[RE]**: the dimension (`1d`, `2d`, `3d`, `enc[43:42]`) and a LOD mode (none,
`bias`, `replace`, `grad`, `enc[41:40]`; `3d` with a LOD mode does not decode); flags
`.skipinv`, `.syncs`, `.nosched`, the PCF mode (`.pcf`, `.pcff16`) and the SRD mode (`.sinf`,
`.rsd`); a destination `r` or `pa` with a two-bit write mask or a repeat count; the
coordinates as a source-0 operand with a format (`.flt16`, `.c10`); the texture state as a
source-1 operand; the LOD value as source 2 when a LOD mode is set; a data fence `drc0`-`drc3`.

- **Semantics [HW].** Source 1 holds the four texture state words (`s` to `s + 3`, the `doutt`
  words of our copies), source 0 the normalized coordinates (`c`, `c + 1`; `.flt16`: two halves
  of one register); the texel arrives in the destination once `drcN` is waited for. Point
  sampling clamps to the edge (*Texture sampling*); filters, address modes, formats, conversions
  and `.pcf` follow the state words (*Sampler state*). **[HW]** A LOD mode's source 2 selects
  the mip level, with `grad` from the logarithm of a footprint of the four derivatives (E041): the
  largest component fits where only `dudx` and `dvdx` are set and the Euclidean length where all
  four are, on the cases run, neither on the rest (E563); held out with independent operands
  the footprint is the larger of the two Euclidean lengths and the fraction of the LOD in 1/64 is
  truncated (E721; the residual pixels and the quad's own derivatives are Q280); a non-square
  twiddled chain halves both sides down to 1x1 (E562); `.sinf` returns the level and the blend
  fraction instead of a texel, and `.rsd` the 2x2 texels per level that a filtered sample blends
  (E042). Our copy path does not use it: the PDS issues the texture fetch (`doutt`) and the result
  arrives in `pa0` before the task starts (`doc/specs/transfer.md`
  §4.4.3) **[HW]**.
- **`smp3d` without a LOD mode [HW]** (E567, in a fill of our own): on TEXTYPE 0, 6 and 7, point
  sampled, a 16x16 twiddled texture and a 64x32 stride one, the third coordinate is not read and
  the texel is the `smp2d` one (8 of 8 jobs, 3 sweeps, `rt7` at two values); on TEXTYPE 2 it
  changes the image (three images for `smp2d`, 0.5 and 1.5): type 2 is the cube layout, its face
  chosen by the dominant coordinate (E725, E726, E844). With any one of 19 sampler-word bits
  flipped on the twiddled texture (T0 14 to 16 and 27 to 30, T3 8 to 12, 15, 18, 20 to 22, 27
  and 28: every bit that ran there without a fault), the third coordinate at 0 and at 1.5 still
  gives one image at all 2048 pixels (19 of 19 held out, E1105): no single bit of those names a
  volume. The simulator reads `smp3d` as `smp2d` on the first and stops on every other state.
- **In the firmware:** not used.
- **The sampler cache [HW]** (E114). The sampler keeps what it fetched, in lines that hold at
  least two neighbouring texels: once a texel is sampled, a USSE store to it or beside it is
  not seen by later samples in the job, whatever fence or cache operation comes between. A
  texel not yet fetched shows the store.

`smp2d r0, r4, c0, drc0` assembles with form #120: enc[63:32] = `0xE0021400`, enc[31:0] =
`0x40010000`; in memory (little endian) `00 00 01 40 00 14 02 E0`.

| field | value | prints |
|---|---|---|
| `pred` | 0x0 | (none) |
| `op` | 0x1 | `2d` |
| `flags1` | 0x0 | (none) |
| `wmask` | 0x1 | (none) |
| `dst` | 0x0 | `r0` |
| `src0` | 0x4 | `r4` |
| `flags2` | 0x0 | (none) |
| `src1` | 0x280 | `c0` |
| `drc` | 0x0 | `0` |

Mnemonics: `smp1d`, `smp1dbias`, `smp1dgrad`, `smp1dreplace`, `smp2d`, `smp2dbias`, `smp2dgrad`,
`smp2dreplace`, `smp3d`, `smp3dbias`, `smp3dgrad`, `smp3dreplace`.

Modifiers: `.nosched`, `.pcf`, `.pcff16`, `.repeatN`, `.rsd`, `.sinf`, `.skipinv`, `.syncs`.

Simulator (`crates/sgx-sim`, from `doc/isa/sim-coverage.json`): 4 of 4 forms have semantics. The
probe vectors that test them: 363 match the hardware, 30 stop unsupported, 0 mismatch
(`texture-mipmaps-mip-bias` 5/0/0, `texture-mipmaps-mip-grad` 8/0/0, `texture-mipmaps-mip-level`
13/0/0, `texture-mipmaps-mip-level-hostfill` 5/0/0, `texture-mipmaps-mip-minfilter` 15/0/0,
`texture-mipmaps-mip-mipfilter` 24/0/0, `texture-mipmaps-mip-t0-field` 12/0/0,
`texture-sampler-cache-texcache-cold` 2/0/0, `texture-sampler-pcff16` 8/0/0,
`texture-sampler-smp-address` 40/0/0, `texture-sampler-smp-address-border` 4/0/0,
`texture-sampler-smp-bilinear` 21/0/0, `texture-sampler-smp-convert` 48/0/0,
`texture-sampler-smp-filter-modes` 6/2/0, `texture-sampler-smp-formats` 57/0/0,
`texture-sampler-smp-formats-other` 12/28/0, `texture-sampler-smp-lod` 11/0/0,
`texture-sampler-smp-pcf` 28/0/0, `texture-sampler-smp-point` 13/0/0, `texture-sampler-smp-srd`
15/0/0, `texture-sampler-smp-twiddled` 16/0/0); unsupported mostly for four texels fix no decoder
(16); YUV through a colour-space set the vector does not record (8); EN's, EN's and EN's words only)
(4).

Confirmed on the hardware (a passing vector): #120, #122; not yet confirmed (as decoded; no passing
vector yet): #121, #123.

### 7.21 Register file access: `ldr`, `str`

Class 31, other group, operation 6 **[RE]**. `ldr rD, #idx, drcN` reads SGX register `idx`
(dword index, offset `idx × 4`) into a temporary or `pa` register, counted on a data fence;
`str #idx, src` writes it. The index is a 14-bit immediate or a source-2 register; flags
`.skipinv` and `.nosched`.

- **Semantics [HW].** `ldr r0, #7, drc0` returns `CORE_ID` (`0x01150000`) and `ldr r0, #801`
  returns `BIF_DIR_LIST_BASE0`, from a client pixel shader on our render node; a client
  `str #671` (`USE_G0`) changed nothing (measured on our render node). The firmware
  programs the whole GPU with these two instructions. In a firmware (EDM) task of ours, `ldr r,
  #7` and `#8` returned `CORE_ID` and `CORE_REVISION` as the host reads them (E533).
- **Ordering of memory [HW].** A `stad` and a later `ldad` of one dword return the stored value
  without an `idf`, for an instance's own store too (*Memory, data fences and the register file*,
  E481, E512).
- **Ordering of `str` then `ldr` [HW, firmware task of ours].** In a firmware (EDM) task, a `str`
  to 0x0814 (17 bits) or 0x0a78 (6 bits) was seen by the next `ldr` of the same register and by
  the host, with no fence and at every distance run: 318 of 318 runs in four fresh loads (E534),
  of which 228 of the 306 of the matrix could tell a `str` that landed from one that did not (the
  value finally stored differs from the one the register held; 138 on 0x0814, 90 on 0x0a78).
  Between the two there were 0, 1, 2, 4 or 16 `nop`s, a `wdf` with no load outstanding, an `idf`
  and a `wdf`, an `idf` alone, or a second `str` (the later one wins); a second `ldr` 64 `nop`s
  later read the stored value too; an `ldr` of the other register kept that register's own value,
  and a `str` after an `ldr` did not change what the `ldr` read. Scope: 0x0814 and 0x0a78 only,
  while the EDM is idle and no job runs; the closed task's own writes of them are not excluded, and
  the replicates within a load are not independent. **[infer]** That the two are plain storage, and
  that a backend may emit `str` then `ldr` of 0x0814 or 0x0a78 with nothing between them. **[open]**
  (Q154): a register whose write has an effect, a job running, a register another writer changes,
  the register-index forms (never run), a `str` wider than the register (no run stored one) and the
  time of a `str` (the pair read `CR_TIMER` 3 to 4 counts apart, an upper bound in a unit not
  established). A client `str` is **[open]** (Q134).
- **The index [HW].** `ldr rD, rI` masks a register index to 14 bits (*The 14-bit
  `ldr`/`str` index*); `str` with a register index is **[open]**.
- The decoder holds two copies of these forms (an older one and the class-31 family's); the
  older ones match first.

**In the firmware [RE].** 196 `ldr` and 422 `str`; those with an immediate index touch 191
distinct registers, all of them named SGX545 registers (`doc/specs/hw_spec.md`,
`tools/usse-dis/regtouch.py`).

`ldr r0, #7, drc0` assembles with form #36: enc[63:32] = `0xFE210000`, enc[31:0] = `0x20000007`; in
memory (little endian) `07 00 00 20 00 00 21 FE`.

| field | value | prints |
|---|---|---|
| `flags` | 0x0 | (none) |
| `dst` | 0x0 | `r0` |
| `imm` | 0x7 | `7` |
| `drc` | 0x0 | `0` |

`str #671, r1` assembles with form #38: enc[63:32] = `0xFE290000`, enc[31:0] = `0x2001409F`; in
memory (little endian) `9F 40 01 20 00 00 29 FE`.

| field | value | prints |
|---|---|---|
| `flags` | 0x0 | (none) |
| `imm` | 0x29f | `671` |
| `src1` | 0x1 | `r1` |

Mnemonics: `ldr`, `str`.

Modifiers: `.nosched`, `.skipinv`.

Simulator (`crates/sgx-sim`, from `doc/isa/sim-coverage.json`): 8 of 8 forms have semantics. The
probe vectors that test them: 8 match the hardware, 69 stop unsupported, 0 mismatch
(`usse-encoding-bits-load-ldr` 0/31/0, `usse-encoding-bits-load-ldr-imm` 0/24/0,
`usse-fence-batching-counters` 1/2/0, `usse-fence-batching-mixed` 3/0/0,
`usse-indexing-ldr-index-mask` 1/4/0, `usse-internal-registers-ireg-ldr` 2/8/0,
`usse-memory-mem-forms` 1/0/0); unsupported mostly for no SGX registers on this bus (59); rN is past
the task's N temporaries (8); reads R(N) before its DRC result lands (wdf) (2).

Confirmed on the hardware (a passing vector): #36, #37; not yet confirmed (as decoded; no passing
vector yet): #38, #39, #145, #146, #147, #148.

### 7.22 Flow control: `ba`, `br`, `lapc`, `bexception`

Class 31 with `enc[54:52]` = 0 and the operation in `enc[40:38]` **[RE]**: 0 `ba`, 1 `br`,
2 `lapc`, 3 and 4 the `pclink` moves (*Moves*), 5 `nop` (*Synchronisation and misc*);
`bexception` sits next to them. The branch flags are `.nosched`, `.synce`/`.syncent`,
`.savelink` and `.mon`; `ba` and `br` take the full predicate.

- **`ba #n`** jumps to instruction `n`; **`br #k`** by a signed offset from the `br` itself
  **[HW]**; `.savelink` makes either a call, which writes `pclink` even when its predicate is false
  (16 of 16 calls not taken in a fill, E491); **`lapc`** returns to `pclink` **[HW]** (E475, E476).
  See *Program counter, calls and the end of a program* for the evidence.
- **A quad whose instances disagree** on a predicated branch goes, all four instances, where its
  top-left instance goes, without masking **[HW]** (E089): in a triangle, the first covered instance
  under `phas`'s `parallel` and instance 0 under `perinstance` (E112). **`.synce`** and **`.mon`**
  hang a fill; **`.syncent`** and **`.nosched`** change nothing there **[HW]**.
- **`bexception #n`** jumps to instruction `n` and **`bexception.rel #k`** (bit 38) by `k`
  from itself, under the full predicate: a branch with `ba`'s and `br`'s fields **[HW]**
  (E108). The `.rel` spelling is ours. With every field 0, the bare `bexception` the reference
  disassembler prints, it jumps to instruction 0 and hangs a fill (E100). What `enc[51]` adds
  to the branch, and what `.synce`, `.syncent` and `.mon` are for, is **[open]**.

**In the firmware [RE].** 954 `ba` (591 predicated, 232 calls), 12 `br`, 74 `lapc`. The kernel
CCB dispatch jumps to its handler by moving the handler's address into `pclink` and running
`lapc`.

`ba.savelink #0x00000100` assembles with form #12: enc[63:32] = `0xF8000200`, enc[31:0] =
`0x00000100`; in memory (little endian) `00 01 00 00 00 02 00 F8`.

| field | value | prints |
|---|---|---|
| `pred` | 0x0 | (none) |
| `flags` | 0x8 | `.savelink` |
| `imm` | 0x100 | `0x00000100` |

`p0 ba #0x00000010` assembles with form #12: enc[63:32] = `0xF9000000`, enc[31:0] = `0x00000010`; in
memory (little endian) `10 00 00 00 00 00 00 F9`.

| field | value | prints |
|---|---|---|
| `pred` | 0x1 | `p0` |
| `flags` | 0x0 | (none) |
| `imm` | 0x10 | `0x00000010` |

`br -#0x00000003` assembles with form #13: enc[63:32] = `0xF8000040`, enc[31:0] = `0x0003FFFD`; in
memory (little endian) `FD FF 03 00 40 00 00 F8`.

| field | value | prints |
|---|---|---|
| `pred` | 0x0 | (none) |
| `flags` | 0x0 | (none) |
| `imm` | 0x3fffd | `-#0x00000003` |

`p0 bexception.rel #0x00000004` assembles with form #15: enc[63:32] = `0xF9080040`, enc[31:0] =
`0x00000004`; in memory (little endian) `04 00 00 00 40 00 08 F9`.

| field | value | prints |
|---|---|---|
| `pred` | 0x1 | `p0` |
| `flags` | 0x0 | (none) |
| `imm` | 0x4 | `#0x00000004` |

Mnemonics: `ba`, `bexception`, `br`, `lapc`.

Modifiers: `.mon`, `.nosched`, `.rel`, `.savelink`, `.synce`, `.syncent`.

Simulator (`crates/sgx-sim`, from `doc/isa/sim-coverage.json`): 5 of 5 forms have semantics. The
probe vectors that test them: 219 match the hardware, 32 stop unsupported, 0 mismatch
(`usse-branch-bexc2-ba10` 0/1/0, `usse-branch-bexc2-ba2` 0/1/0, `usse-branch-bexc2-br5` 0/1/0,
`usse-branch-bexc2-np0-t10` 0/1/0, `usse-branch-bexc2-p0-t10` 0/1/0, `usse-branch-bexc2-rel5` 0/1/0,
`usse-branch-bexc2-t10` 0/1/0, `usse-branch-bexc2-t2` 0/1/0, `usse-branch-br-offset` 5/0/0,
`usse-branch-divergent` 6/2/0, `usse-cache-control-cross` 0/22/0, `usse-callfalse-chain` 3/0/0,
`usse-callfalse-link` 8/0/0, `usse-callfalse2-chain` 3/0/0, `usse-callfalse2-link` 8/0/0,
`usse-decoder-vectors-br1` 2/0/0, `usse-decoder-vectors-br2` 2/0/0, `usse-decoder-vectors-br3`
2/0/0, `usse-decoder-vectors-br4` 2/0/0, `usse-decoder-vectors-br5` 2/0/0,
`usse-decoder-vectors-brn1` 2/0/0, `usse-decoder-vectors-brn2` 2/0/0, `usse-decoder-vectors-brn3`
2/0/0, `usse-decoder-vectors-brn4` 2/0/0, `usse-decoder-vectors-brn5` 2/0/0,
`usse-form-coverage-lapc-pclink` 6/0/0, `usse-fw37-pred-pred-notp0-ba-not-taken` 5/0/0,
`usse-fw37-pred-pred-p0-ba-not-taken` 5/0/0, `usse-link-ba-savelink-read` 1/0/0,
`usse-link-control-e091` 2/0/0, `usse-link-lapc-gap` 38/0/0, `usse-moe-setfc-branch` 10/0/0,
`usse-pflow-flow` 24/0/0, `usse-phases-filladdr` 2/0/0, `usse-phases-phasbr-fill-parallel` 1/0/0,
`usse-phases-phasbr-fill-perinstance` 1/0/0, `usse-risky-lapc-backward` 12/0/0,
`usse-risky-lapc-computed` 16/0/0, `usse-risky-lapc-direct` 16/0/0, `usse-risky-lapc-high-bits`
4/0/0, `usse-risky-link-ba-return` 4/0/0, `usse-risky-link-nested` 3/0/0, `usse-risky-pflow-call`
16/0/0); unsupported mostly for gN (per-instance values, not modelled) (22); rN is past the task's N
temporaries (8); branch flag .syncent (2).

Confirmed on the hardware (a passing vector): #12, #13, #125; not yet confirmed (as decoded; no
passing vector yet): #14, #15.

### 7.23 Synchronisation and misc: `nop`, `wdf`, `idf`, `setm`, `wop`, `lock`, `release`

Class 31 **[RE]**: `nop` is flow-control operation 5; the rest are the "other" group
(`enc[53:52]` = 2) with the operation in `enc[58:56]`: 0 `idf`, 1 `wdf`, 2 `setm`, 5
`lock`/`release` (by `enc[0]`, a three-bit mutex number), 7 `wop`.

- **`nop`** does nothing **[infer]**; with `.end` it ends the program **[HW]** (our USE
  secondary program). `.tog` and `.trigger` are **[open]**.
- **`wdf drcN`** waits for the loads counted on `drcN` **[RE/HW]**, all of them whatever their form,
  up to 192 distinct `ldad` seen (E518 read 4 or 5 reloaded registers per job), and not for those of
  another counter (E478, E518, E479); with nothing outstanding it returns at once (E480). **`idf
  drcN, bif`** is a fence on memory writes counted the same way **[infer]**, which no fill case
  needed (*Memory, data fences and the register file*). **`idf drcN, pixelbe`** hangs a fill,
  waiting for something a fill never gives (the pixel back end?) **[HW]** (E114).
- **`wop #n`** waits for the outputs to drain before an emit **[infer]**: our state programs
  issue `wop #0` between `emitvcbst` and `emitmtest`, as the captured ones do **[CAP/HW]**.
  `.twopart` is **[open]**.
- **`lock #n` / `release #n`** take and give back one of eight mutexes **[HW]** (table
  `probes/usse/quad-lock.toml`,
  measured 2026-10-27): every pixel
  instance of a 64x32 fill adding 1 to one scratch dword ends at 44 without a mutex (lost
  updates), and at exactly 512 inside `lock #0` ... `release #0` or `lock #3` ...
  `release #3`, each of the 512 values seen by the four pixels of one aligned 2 x 2 quad: the
  mutex serialises quads, in no screen order, and the four instances of a quad load and store
  together. A `lock` never released hangs the job, the next quad waiting for it. A second
  `lock` of a mutex the quad still holds blocks the quad itself: with `lock #0` twice the fill hung
  with no update stored, whether one or two `release #0` followed; `lock #0` then `lock #1` does
  not hang (E921) **[HW]**. The firmware executes `lock` twice and never `release` (R-6 reads
  the two as `lock #0`, on the EDM's lockup path); that the EDM blocks at its second `lock` as a
  pixel program does is **[infer]**, and whether something else releases its mutex is **[open]**.
- **`setm #n`** (a four-bit number): `#0`, `#1`, `#2`, `#4`, `#8` and `#15` before a locked update
  leave it as without (E088),
  mask no pixel of a fill and none of a single-sample triangle (E099), and no sample at 4x under
  any `phas` rate, nor once any task or render word tried enables per-sample shading, which
  none did (E103, E115, E117) **[HW]**; the closed compiler never emits it **[CAP]**. What it
  sets is **[open]**.

**In the firmware [RE].** 807 `wdf` (711 on `drc0`), 124 `idf ..., bif`, 87 `nop` (5 with
`.end`, 1 with `.nosched`), 2 `lock`.

From `asm/tri/use_mtest18.s`:

```
        nop.nosched
        wdf drc0
        wop #0
```

`idf drc1, bif` assembles with form #6: enc[63:32] = `0xF8200001`, enc[31:0] = `0x00000000`; in
memory (little endian) `00 00 00 00 01 00 20 F8`.

| field | value | prints |
|---|---|---|
| `drc` | 0x1 | `1` |

Mnemonics: `idf`, `lock`, `nop`, `release`, `setm`, `wdf`, `wop`.

Modifiers: `.end`, `.nosched`, `.syncs`, `.tog`, `.trigger`, `.twopart`.

Simulator (`crates/sgx-sim`, from `doc/isa/sim-coverage.json`): 8 of 9 forms have semantics (not
yet: #143). The probe vectors that test them: 365 match the hardware, 12 stop unsupported, 0
mismatch (`texture-mipmaps-mip-bias` 5/0/0, `texture-mipmaps-mip-grad` 8/0/0,
`texture-mipmaps-mip-level` 13/0/0, `texture-mipmaps-mip-minfilter` 15/0/0,
`texture-mipmaps-mip-mipfilter` 24/0/0, `texture-mipmaps-mip-t0-field` 12/0/0,
`texture-sampler-cache-texcache-cold` 1/0/0, `texture-sampler-pcff16` 8/0/0,
`texture-sampler-smp-srd` 15/0/0, `usse-alpha-test-pcoeff-depthf` 1/0/0,
`usse-constant-banks-gbank-pixels` 110/2/0, `usse-decoder-vectors-stad-imm0` 1/0/0,
`usse-decoder-vectors-stad-imm1` 1/0/0, `usse-decoder-vectors-stad-imm16` 1/0/0,
`usse-decoder-vectors-stad-imm2` 1/0/0, `usse-decoder-vectors-stad-imm3` 1/0/0,
`usse-decoder-vectors-stad-imm63` 1/0/0, `usse-decoder-vectors-stad-imm7` 1/0/0,
`usse-decoder-vectors-stad-postinc` 3/0/0, `usse-decoder-vectors-stad-reg` 5/0/0,
`usse-encoding-bits-state-nop` 37/0/0, `usse-encoding-bits-state-setm` 50/0/0,
`usse-encoding-gaps-class2` 1/0/0, `usse-encoding-gaps-class22` 1/0/0, `usse-encoding-gaps-class26`
1/0/0, `usse-encoding-gaps-class31` 1/0/0, `usse-encoding-gaps-end-words` 1/0/0,
`usse-fence-batching-store-then-load` 2/0/0, `usse-fence-batching-store-then-load-recorded` 4/0/0,
`usse-form-coverage-ld-pre` 2/0/0, `usse-form-coverage-st-pre` 2/0/0, `usse-instance-masking-setm`
22/0/0, `usse-internal-registers-ireg-ldad` 0/10/0, `usse-link-ba-savelink-read` 4/0/0,
`usse-memory-mem-forms` 1/0/0, `usse-store-own-cross` 2/0/0, `usse-store-own-load` 1/0/0,
`usse-store-own-one` 1/0/0, `usse-store-own2-cross` 3/0/0, `usse-store-own2-load` 1/0/0,
`usse-store-own2-quad` 1/0/0); unsupported mostly for fetch past the temporaries (8); gN
(per-instance values, not modelled) (2); rN is past the task's N temporaries (2).

Confirmed on the hardware (a passing vector): #5, #6, #140, #142; not yet confirmed (as decoded; no
passing vector yet): #7, #128, #141, #143, #144.

### 7.24 MOE control: `smoa`, `smr`, `smlsi`, `smbo`, `imo`, `setfc`, `moest`

Class 31 with `enc[53:52]` = 1, the operation in `enc[58:56]`, no predicate and `.nosched` in
`enc[50]` **[RE]**. `smoa`, `smr`, `smlsi` and `smbo` take either two register operands
(`enc[51]` set) or immediates:

- `smoa #o1, #o2, #o3, #o4, m1, m2, m3, m4`: four signed 10-bit offsets and four address modes
  (`none`, `repeat`, `clamp`, `mirror`);
- `smr #a, #b, #c, #d` and `smbo #a, #b, #c, #d`: four 12-bit values (ranges and base
  offsets);
- `smlsi i0, i1, i2, i3, <modes>, #l1, #l2, #l3`: four 8-bit operands (`I0`-`I3` in *`smlsi`
  increments*), each a signed increment or, in swizzle mode, a four-component swizzle, then three
  four-bit limits times four;
- `imo #a, #b, #c, #d` (four 12-bit immediates), `setfc #a, #b` (two bits) and
  `moest d, #sel`, which reads a word of the MOE state back into a register: the selector
  names *SMOA*, *SMLSI*, *SMBO* and *SMR* low and high data and an index word.

- **Semantics [infer].** These set the per-operand register stepping that repeats and fetches
  use (*Repeats and the MOE state*): `smoa` an offset and an address mode per operand, `smbo`
  base offsets, `smr` ranges, `smlsi` increments or swizzles. **[HW]** `smlsi`'s four
  increments are the destination's and sources 0, 1 and 2's for a following repeat (*`smlsi`
  increments*). **[HW]** `smbo`'s first, third and fourth values offset the register numbers
  of the destination, source 1 and source 2 (a store's stored register) of every later
  instruction of the task, immediates excepted; the second, by elimination source 0's, showed
  nothing (E087). **[HW]** `smlsi`'s swizzle mode gives repeat iteration k the swizzle's k-th
  component as its register offset; `moest` writes no register and no memory, and `setfc`
  changes nothing a load or a repeat shows (E097). Nor does `moest` load the state word its
  selector names from its register, and `setfc` changes neither a divergent branch nor a
  `.fetch4` load (E109).
- **`smoa` and `smr` [HW]** (E097, E105). `smoa`'s offsets shift each operand's register number
  on every instruction. Its modes map an operand's first register once, from `smr`'s range for
  that operand (fields in the same order: destination, src0, src1, src2). With i = register +
  offset and M = range - 1:
  - `none` gives i;
  - `clamp` gives min(i, M);
  - `mirror` gives 2M - i when i > M;
  - `repeat` gives i - (M + 1) when i > M (once, not modulo).

  A repeat's iterations then step on from that register unmapped. This holds for the
  destination and source 1; source 2 is assumed to follow and source 0 is not measured. A first
  register below `r0` drops writes and reads values from other storage. `imo`, and what `moest`
  and `setfc` are for, remain **[open]**.

**In the firmware [RE].** Only `smlsi`, eight times, at task entry points, always in
increment mode.

`smr #4, #0, #0, #0` assembles with form #134: enc[63:32] = `0xF9100040`, enc[31:0] = `0x00000000`;
in memory (little endian) `00 00 00 00 40 00 10 F9`.

| field | value | prints |
|---|---|---|
| `nosched` | 0x0 | (none) |
| `imm1` | 0x4 | `4` |
| `imm2` | 0x0 | `0` |
| `imm3` | 0x0 | `0` |
| `imm4` | 0x0 | `0` |

Mnemonics: `imo`, `moest`, `setfc`, `smbo`, `smlsi`, `smoa`, `smr`.

Modifiers: `.nosched`, `.skipinv`.

Simulator (`crates/sgx-sim`, from `doc/isa/sim-coverage.json`): 6 of 11 forms have semantics (not
yet: #129, #130, #131, #132, #137). The probe vectors that test them: 752 match the hardware, 261
stop unsupported, 0 mismatch (`usse-encoding-bits-state-imo` 0/5/0, `usse-encoding-bits-state-moest`
39/0/0, `usse-encoding-bits-state-setfc` 51/0/0, `usse-encoding-bits-state-smbo-imm` 5/0/0,
`usse-encoding-bits-state-smlsi-imm` 5/0/0, `usse-encoding-bits-state-smoa-imm` 5/0/0,
`usse-encoding-bits-state-smr-imm` 5/0/0, `usse-moe-moest-dest` 30/0/0, `usse-moe-moest-load`
54/0/0, `usse-moe-moest-state` 14/6/0, `usse-moe-moest-store` 4/54/0, `usse-moe-setfc` 8/0/0,
`usse-moe-setfc-fetch` 8/0/0, `usse-moe-smbo-operands` 6/14/0, `usse-moe-smlsi-three-sources`
14/0/0, `usse-moe-smoa-all-clamp` 56/0/0, `usse-moe-smoa-all-mirror` 12/44/0,
`usse-moe-smoa-all-none` 36/0/0, `usse-moe-smoa-all-pred` 48/0/0, `usse-moe-smoa-all-repeat` 36/0/0,
`usse-moe-smoa-all-src` 20/28/0, `usse-moe-smoa-hi-clamp` 56/0/0, `usse-moe-smoa-hi-mirror` 12/44/0,
`usse-moe-smoa-hi-none` 36/0/0, `usse-moe-smoa-hi-pred` 48/0/0, `usse-moe-smoa-hi-repeat` 36/0/0,
`usse-moe-smoa-hi-src` 20/28/0, `usse-moe-smr-smoa` 6/12/0, `usse-moe-state-next-job` 3/0/0,
`usse-moe-swizzle` 8/2/0, `usse-moe-window` 12/8/0, `usse-moe-window-reset` 56/16/0,
`usse-store-repeat-regs-copy16` 1/0/0, `usse-store-repeat-smlsi` 2/0/0); unsupported mostly for smoa
takes dst to r-N (not modelled) (128); smlsi with non-zero limits (58); smoa takes srcN to r-N (not
modelled) (32).

Confirmed on the hardware (a passing vector): #133, #134, #135, #136, #138, #139; not yet confirmed
(as decoded; no passing vector yet): #129, #130, #131, #132, #137.

### 7.25 Phases: `phas`

Class 31 **[RE]**. The immediate form is described in *Tasks and phases*: the next phase's
instruction index (18 bits), its temporaries (eight bits, times four; a request runs when it is 4 to
192 modulo 256, *Tasks and phases*), the rate, the wait condition and the instance mode, plus
`.end`. A register form takes two source operands instead (presumably the same information computed
at run time **[infer]**). Both exist twice in the decoder's table, as for `ldr`/`str`.

From `asm/tri/use_vtx.s`:

```
        phas #7, #0, pixel, vcull, parallel
        phas #0, #0, pixel, end, parallel
```

`phas #7, #0, pixel, vcull, parallel` assembles with form #8: enc[63:32] = `0xFA440200`, enc[31:0] =
`0x00000007`; in memory (little endian) `07 00 00 00 00 02 44 FA`.

| field | value | prints |
|---|---|---|
| `end` | 0x0 | (none) |
| `imm1` | 0x7 | `7` |
| `imm2` | 0x0 | `0` |
| `op1` | 0x0 | `pixel` |
| `op2` | 0x2 | `vcull` |
| `op3` | 0x0 | `parallel` |

Mnemonics: `phas`.

Modifiers: `.end`, `.nosched`.

Simulator (`crates/sgx-sim`, from `doc/isa/sim-coverage.json`): 2 of 4 forms have semantics (not
yet: #159, #160).

Not yet confirmed (as decoded; no passing vector yet): #8, #9, #159, #160.

### 7.26 Emits: `emitpix1`, `emitpix2`, `emitvcb*`, `emitmte*`, `emitpds`

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
  client's does. Which of the sideband, `s2` and the kick pass is needed, alone or together, is
  **[open]** (Q128); where its `douta` land is open too (not `pa0` or `pa2`; `sa0` and `sa2`
  hold those values anyway).
- **`.freep`** frees the task's resources after the emit **[infer]**; **`#incp`** is always 0
  in our programs and its meaning is **[open]**.
- The assembler writes the unprinted source of `emitvcbst`/`emitvcbvtx` and the unprinted
  bank bit of `emitmtest` as the closed compiler does, so that the hardware sees the words it
  was tested with (`tools/usse-asm/README.md`).

**In the firmware [RE].** Three `emitpds`, all `.tasks.taske`; no other emit (the firmware
does not render).

From `asm/transfer/use_eot.s`:

```
        emitpix1.freep #0 /* incp */, r0, r1
        emitpix2.end.freep #0 /* incp */, r2, r3, r0, #0x00000000
```

From `asm/tri/use_vtx.s`:

```
        emitvcbvtx.end.twopart #0, #0
        emitmtevtx.end.twopart.freep #0, #0, #0
```

Mnemonics: `emitmtest`, `emitmtevtx`, `emitpds`, `emitpix1`, `emitpix2`, `emitvcbst`, `emitvcbvtx`.

Modifiers: `.cut`, `.end`, `.freep`, `.nosched`, `.taske`, `.tasks`, `.twopart`.

Simulator (`crates/sgx-sim`, from `doc/isa/sim-coverage.json`): 7 of 7 forms have semantics.

Not yet confirmed (as decoded; no passing vector yet): #10, #11, #149, #150, #151, #152, #153.

### 7.27 Visibility tests: `pcoeff`, `ptoff`, `atst8`, `depthf`

Class 31 with `enc[53:52]` = 3 **[RE]**: operation 0 is `pcoeff` or `ptoff` (by `enc[47]`), 1
`atst8`, 3 `depthf`. `atst8` writes a destination and a predicate `p0`-`p3` (or not, `!`),
with `.c10`; `atst8` and `depthf` test three sources with `twosided` and a feedback mode
(`fb`, `nfb`, `optdwd`) and take a two-bit predicate.

- **`ptoff`** signals the end of the punch-through phase for the pixels of the task
  **[infer]**: our 3D render's PTOFF task is the single instruction `ptoff.end`, and renders
  run with it **[HW]**.
- **`atst8 dst, [!]pN, src0, src1, src2[, twosided], mode`** is an alpha test **[HW]**
  (table `probes/usse/alpha-test.toml`, measured 2026-10-27 in a
  fill's pixel task, E083): it compares src0's top byte (bits 31:24, the alpha) with src2's top
  byte (the reference) by the function in src2 bits 15:13, numbered as the ISP's compares (0
  never, 1 less, 2 equal, 3 lequal, 4 greater, 5 notequal, 6 gequal, 7 always; `alpha FUNC
  reference`, every function checked just below, at and above the reference). On a pass it
  writes src0 to the destination and makes the predicate true; on a fail it leaves the
  destination and makes the predicate false. `!pN` does not write the predicate. No other bit
  of src2 changed the result from ~0 down, src1 (0 or ~0) changes nothing, and in a fill
  `fb`, `nfb`, `optdwd` and `twosided` give the same result: what the feedback does reaches
  only a punch-through pass. A discard shader ends its `pt` phase with an `atst8` in feedback
  mode whose third source holds the compare function and the reference.
- **`depthf`** (depth feedback) and **`pcoeff`** (plane coefficients) **[HW]**. In a fill's
  pixel task neither does anything seen (`usse-alpha-test-pcoeff-depthf`): what they do, like
  `atst8`'s feedback, reaches only a punch-through pass.
- **Punch-through feedback [HW]** (E083): in a punch-through
  pass a pixel is kept only if its `pt` phase runs `atst8 ... fb` or `depthf src0, src1,
  src2, fb` with a control word in src1 that has bits 0 and 14 set (either bit
  clear discards the pixel, bit 2 or 3 set makes its depth win as if the test were always;
  the glossary's `FEEDBACK_CTL` rows);
  a failing alpha test, `nfb` or no feedback discards it and the object behind shows. The
  kept pixels' depth is resolved by the ISP the same every run only with `pcoeff pa2, pa3,
  sa4` fed by iteration source 34 (`DOUTI0.ATTR_SOURCE` 34): `pcoeff` hands the ISP the
  depth plane its feedback test uses; its third source changed nothing seen.
  `atst8` must not directly follow `pcoeff`: with no instruction between, the object is not
  drawn at all **[HW]**.
- **The stencil in a punch-through pass [HW]**: the pass neither tests the
  ISP stencil (all eight compares draw alike) nor writes it (a later opaque object testing
  for the reference finds nothing), with `fb`, `optdwd` and each with `twosided`. What
  `twosided` and `optdwd` change is **[open]**.
- **`depthf src0, src1, src2, fb` [HW]**: src0 is the pixel's depth, which
  replaces the iterated one in the depth test and the depth written (1.0 fails a less test
  against the background's 1.0; 0.5 - z reverses the copies' order), in pass 4 and 5 alike.
- **In the firmware:** not used.

From `asm/tri/use_ptoff.s`:

```
; use_ptoff.s -- the PTOFF task of a 3D render.
;
; pds_pixevent.s starts it for the PTOFF pixel event (ir1 bit 3). A transfer never
; sees that event and points the PTOFF case at its end-of-tile task; a 3D render
; gives it a task of its own that only signals ptoff and ends ([infer], from the
; instruction's name).

        phas #0, #0, pixel, end, parallel       ; the phase marker, as in use_fill.s
        ptoff.end
```

`ptoff.end` assembles with form #155: enc[63:32] = `0xF8348000`, enc[31:0] = `0x00000000`; in memory
(little endian) `00 00 00 00 00 80 34 F8`.

| field | value | prints |
|---|---|---|
| `nosched` | 0x0 | (none) |
| `end` | 0x1 | `.end` |

Mnemonics: `atst8`, `depthf`, `pcoeff`, `ptoff`.

Modifiers: `.c10`, `.end`, `.nosched`, `.syncs`.

Simulator (`crates/sgx-sim`, from `doc/isa/sim-coverage.json`): 4 of 4 forms have semantics. The
probe vectors that test them: 737 match the hardware, 0 stop unsupported, 0 mismatch
(`usse-alpha-test-atst8-bytes` 12/0/0, `usse-alpha-test-atst8-fb` 9/0/0,
`usse-alpha-test-atst8-func` 24/0/0, `usse-alpha-test-atst8-modes` 16/0/0,
`usse-alpha-test-atst8-nfb` 585/0/0, `usse-alpha-test-atst8-optdwd` 9/0/0,
`usse-alpha-test-atst8-src2-bits` 32/0/0, `usse-alpha-test-pcoeff-depthf` 5/0/0,
`usse-encoding-bits-state-atst8` 5/0/0, `usse-encoding-bits-state-depthf` 17/0/0,
`usse-encoding-bits-state-pcoeff` 23/0/0).

Confirmed on the hardware (a passing vector): #154, #156, #157; not yet confirmed (as decoded; no
passing vector yet): #155.

### 7.28 Cache control: `ci`, `cf`, `cfi`

Class 31 with `enc[54:52]` = 4, operation 0 **[RE]**: `ci`, `cf` or `cfi` by `enc[45:44]` (0
does not decode), flags `.nosched`, `.global`, `.dm_nomatch`, two sources and a cache-level
operand that the decoder annotates: 1 `L0 and L1`, 2 `L2`, 3 `L0, L1 and L2`.

- **Semantics [infer].** Cache invalidate, flush, and flush-and-invalidate over the named
  levels, for the address range the sources give (or everything, `.global`?). **[HW]** none
  of the forms writes a register, loses a store or makes the task's next load stale (*Cache
  control*). Nor do they reach the texture sampler's cache: after a texel is sampled, a store
  to it stays unseen by the next sample whatever `ci`, `cf` or `cfi`, level or flag comes
  between **[HW]** (E114). What they act on is **[open]**.

**In the firmware [RE].** Four `ci.global` and one `cfi.global`, all on the three levels.

`ci r1, r2, #1 /* L0 and L1 */` assembles with form #158: enc[63:32] = `0xF8401100`, enc[31:0] =
`0x00000082`; in memory (little endian) `82 00 00 00 00 11 40 F8`.

| field | value | prints |
|---|---|---|
| `op` | 0x1 | `ci` |
| `flags` | 0x0 | (none) |
| `src1` | 0x1 | `r1` |
| `src2` | 0x2 | `r2` |
| `imm` | 0x1 | `1 /* L0 and L1 */` |

Mnemonics: `cf`, `cfi`, `ci`.

Modifiers: `.dm_nomatch`, `.global`, `.nosched`.

Simulator (`crates/sgx-sim`, from `doc/isa/sim-coverage.json`): 1 of 1 forms have semantics. The
probe vectors that test them: 20 match the hardware, 0 stop unsupported, 0 mismatch
(`usse-cache-control-levels` 20/0/0).

Confirmed on the hardware (a passing vector): #158.

### 7.29 Video: `adif`, `adifsum`, `bilin`, `firv`, `firh`

Classes 22 and 23 **[RE]**. Class 22 picks by `enc[53:52]`: `adif` (or `adifsum` with
`enc[38]`), `bilin`, `firv`; class 23 is `firh`. All take the multiply flags and a two-bit
predicate, and work on 8-bit data (`u8`, `s8`, `o8`).

- **Semantics.** `adif` is the per-byte absolute difference and `adifsum` the sum of the four
  plus a 16-bit half of `s0` **[HW]**. `bilin` is a bilinear filter with weights in eighths
  from a pair of bytes of its first source; `firv` a two-tap vertical filter per byte column,
  its taps in the third source; `firh` a horizontal FIR filter along the 12 bytes of its three
  sources, with a coefficient set `fcsN` fixed at boot (`fcs2` is H.264's half-pel kernel), a
  centre `#s`, an edge mode `rep`/`msc`/`mdc` and a result byte `#k` **[HW]**. `firh` keeps
  the other three result bytes in a latch per instance slot, which `firv`'s `latch` adds
  **[HW]**. The formats only change how data bytes are read; results are unsigned bytes,
  saturated (*Video*).
- **In the firmware:** not used.

`adif r1, r2, r3` assembles with form #214: enc[63:32] = `0xB0000000`, enc[31:0] = `0x00200103`; in
memory (little endian) `03 01 20 00 00 00 00 B0`.

| field | value | prints |
|---|---|---|
| `pred` | 0x0 | (none) |
| `flags` | 0x0 | (none) |
| `dst` | 0x1 | `r1` |
| `src1` | 0x2 | `r2` |
| `src2` | 0x3 | `r3` |

Mnemonics: `adif`, `adifsum`, `bilin`, `firh`, `firv`.

Modifiers: `.end`, `.nosched`, `.repeatN`, `.skipinv`.

Simulator (`crates/sgx-sim`, from `doc/isa/sim-coverage.json`): 5 of 5 forms have semantics. The
probe vectors that test them: 20342 match the hardware (15153 with near values, each within the
bound the hardware was measured to), 1435 stop unsupported, 0 mismatch (`usse-encoding-bits-adif`
19/0/0, `usse-encoding-bits-adifsum` 10/0/0, `usse-encoding-bits-bilin` 6/0/0,
`usse-encoding-bits-firh` 2/0/0, `usse-encoding-bits-firv` 7/0/0, `usse-filter-bank2-fcs2` 0/23/0,
`usse-filter-bank2-fcs3` 0/23/0, `usse-filter-banks-bank0-fcs2-mdc-c0` 13/0/0,
`usse-filter-banks-bank0-fcs2-mdc-c2` 13/0/0, `usse-filter-banks-bank0-fcs2-mdc-c4` 13/0/0,
`usse-filter-banks-bank0-fcs2-msc-c0` 13/0/0, `usse-filter-banks-bank0-fcs2-msc-c2` 13/0/0,
`usse-filter-banks-bank0-fcs2-msc-c4` 13/0/0, `usse-filter-banks-bank0-fcs2-rep-c0` 13/0/0,
`usse-filter-banks-bank0-fcs2-rep-c2` 13/0/0, `usse-filter-banks-bank0-fcs2-rep-c4` 13/0/0,
`usse-filter-banks-bank0-fcs3-mdc-c0` 13/0/0, `usse-filter-banks-bank0-fcs3-mdc-c2` 13/0/0,
`usse-filter-banks-bank0-fcs3-mdc-c4` 13/0/0, `usse-filter-banks-bank0-fcs3-msc-c0` 13/0/0,
`usse-filter-banks-bank0-fcs3-msc-c2` 13/0/0, `usse-filter-banks-bank0-fcs3-msc-c4` 13/0/0,
`usse-filter-banks-bank0-fcs3-rep-c0` 13/0/0, `usse-filter-banks-bank0-fcs3-rep-c2` 13/0/0,
`usse-filter-banks-bank0-fcs3-rep-c4` 13/0/0, `usse-filter-banks-bank0-fcs4-mdc-c0` 13/0/0,
`usse-filter-banks-bank0-fcs4-mdc-c2` 13/0/0, `usse-filter-banks-bank0-fcs4-mdc-c4` 13/0/0,
`usse-filter-banks-bank0-fcs4-msc-c0` 13/0/0, `usse-filter-banks-bank0-fcs4-msc-c2` 13/0/0,
`usse-filter-banks-bank0-fcs4-msc-c4` 13/0/0, `usse-filter-banks-bank0-fcs4-rep-c0` 13/0/0,
`usse-filter-banks-bank0-fcs4-rep-c2` 13/0/0, `usse-filter-banks-bank0-fcs4-rep-c4` 13/0/0,
`usse-filter-banks-bank0-fcs5-mdc-c0` 13/0/0, `usse-filter-banks-bank0-fcs5-mdc-c2` 13/0/0,
`usse-filter-banks-bank0-fcs5-mdc-c4` 13/0/0, `usse-filter-banks-bank0-fcs5-msc-c0` 13/0/0,
`usse-filter-banks-bank0-fcs5-msc-c2` 13/0/0, `usse-filter-banks-bank0-fcs5-msc-c4` 13/0/0,
`usse-filter-banks-bank0-fcs5-rep-c0` 13/0/0, `usse-filter-banks-bank0-fcs5-rep-c2` 13/0/0,
`usse-filter-banks-bank0-fcs5-rep-c4` 13/0/0, `usse-filter-banks-bank1-fcs2-mdc-c0` 0/13/0,
`usse-filter-banks-bank1-fcs2-mdc-c2` 0/13/0, `usse-filter-banks-bank1-fcs2-mdc-c4` 0/13/0,
`usse-filter-banks-bank1-fcs2-msc-c0` 0/13/0, `usse-filter-banks-bank1-fcs2-msc-c2` 0/13/0,
`usse-filter-banks-bank1-fcs2-msc-c4` 0/13/0, `usse-filter-banks-bank1-fcs2-rep-c0` 0/13/0,
`usse-filter-banks-bank1-fcs2-rep-c2` 0/13/0, `usse-filter-banks-bank1-fcs2-rep-c4` 0/13/0,
`usse-filter-banks-bank1-fcs3-mdc-c0` 0/13/0, `usse-filter-banks-bank1-fcs3-mdc-c2` 0/13/0,
`usse-filter-banks-bank1-fcs3-mdc-c4` 0/13/0, `usse-filter-banks-bank1-fcs3-msc-c0` 0/13/0,
`usse-filter-banks-bank1-fcs3-msc-c2` 0/13/0, `usse-filter-banks-bank1-fcs3-msc-c4` 0/13/0,
`usse-filter-banks-bank1-fcs3-rep-c0` 0/13/0, `usse-filter-banks-bank1-fcs3-rep-c2` 0/13/0,
`usse-filter-banks-bank1-fcs3-rep-c4` 0/13/0, `usse-filter-banks-bank1-fcs4-mdc-c0` 0/13/0,
`usse-filter-banks-bank1-fcs4-mdc-c2` 0/13/0, `usse-filter-banks-bank1-fcs4-mdc-c4` 0/13/0,
`usse-filter-banks-bank1-fcs4-msc-c0` 0/13/0, `usse-filter-banks-bank1-fcs4-msc-c2` 0/13/0,
`usse-filter-banks-bank1-fcs4-msc-c4` 0/13/0, `usse-filter-banks-bank1-fcs4-rep-c0` 0/13/0,
`usse-filter-banks-bank1-fcs4-rep-c2` 0/13/0, `usse-filter-banks-bank1-fcs4-rep-c4` 0/13/0,
`usse-filter-banks-bank1-fcs5-mdc-c0` 0/13/0, `usse-filter-banks-bank1-fcs5-mdc-c2` 0/13/0,
`usse-filter-banks-bank1-fcs5-mdc-c4` 0/13/0, `usse-filter-banks-bank1-fcs5-msc-c0` 0/13/0,
`usse-filter-banks-bank1-fcs5-msc-c2` 0/13/0, `usse-filter-banks-bank1-fcs5-msc-c4` 0/13/0,
`usse-filter-banks-bank1-fcs5-rep-c0` 0/13/0, `usse-filter-banks-bank1-fcs5-rep-c2` 0/13/0,
`usse-filter-banks-bank1-fcs5-rep-c4` 0/13/0, `usse-filter-banks-bank2-fcs2-mdc-c0` 0/13/0,
`usse-filter-banks-bank2-fcs2-mdc-c2` 0/13/0, `usse-filter-banks-bank2-fcs2-mdc-c4` 0/13/0,
`usse-filter-banks-bank2-fcs2-msc-c0` 0/13/0, `usse-filter-banks-bank2-fcs2-msc-c2` 0/13/0,
`usse-filter-banks-bank2-fcs2-msc-c4` 0/13/0, `usse-filter-banks-bank2-fcs2-rep-c0` 0/13/0,
`usse-filter-banks-bank2-fcs2-rep-c2` 0/13/0, `usse-filter-banks-bank2-fcs2-rep-c4` 0/13/0,
`usse-filter-banks-bank2-fcs2-rep-c4-low` 0/13/0, `usse-filter-banks-bank2-fcs3-mdc-c0` 0/13/0,
`usse-filter-banks-bank2-fcs3-mdc-c2` 0/13/0, `usse-filter-banks-bank2-fcs3-mdc-c4` 0/13/0,
`usse-filter-banks-bank2-fcs3-msc-c0` 0/13/0, `usse-filter-banks-bank2-fcs3-msc-c2` 0/13/0,
`usse-filter-banks-bank2-fcs3-msc-c4` 0/13/0, `usse-filter-banks-bank2-fcs3-rep-c0` 0/13/0,
`usse-filter-banks-bank2-fcs3-rep-c2` 0/13/0, `usse-filter-banks-bank2-fcs3-rep-c4` 0/13/0,
`usse-filter-banks-bank2-fcs3-rep-c4-low` 0/13/0, `usse-filter-banks-bank2-fcs4-mdc-c0` 0/13/0,
`usse-filter-banks-bank2-fcs4-mdc-c2` 0/13/0, `usse-filter-banks-bank2-fcs4-mdc-c4` 0/13/0,
`usse-filter-banks-bank2-fcs4-msc-c0` 0/13/0, `usse-filter-banks-bank2-fcs4-msc-c2` 0/13/0,
`usse-filter-banks-bank2-fcs4-msc-c4` 0/13/0, `usse-filter-banks-bank2-fcs4-rep-c0` 0/13/0,
`usse-filter-banks-bank2-fcs4-rep-c2` 0/13/0, `usse-filter-banks-bank2-fcs4-rep-c4` 0/13/0,
`usse-filter-banks-bank2-fcs5-mdc-c0` 0/13/0, `usse-filter-banks-bank2-fcs5-mdc-c2` 0/13/0,
`usse-filter-banks-bank2-fcs5-mdc-c4` 0/13/0, `usse-filter-banks-bank2-fcs5-msc-c0` 0/13/0,
`usse-filter-banks-bank2-fcs5-msc-c2` 0/13/0, `usse-filter-banks-bank2-fcs5-msc-c4` 0/13/0,
`usse-filter-banks-bank2-fcs5-rep-c0` 0/13/0, `usse-filter-banks-bank2-fcs5-rep-c2` 0/13/0,
`usse-filter-banks-bank2-fcs5-rep-c4` 0/13/0, `usse-filter-control-firh-fcs0-c0x0` 13/0/0,
`usse-filter-control-firh-fcs0-c0x1` 13/0/0, `usse-filter-control-firh-fcs0-c0x10` 13/0/0,
`usse-filter-control-firh-fcs0-c0x100` 13/0/0, `usse-filter-control-firh-fcs0-c0x2` 13/0/0,
`usse-filter-control-firh-fcs0-c0x4` 13/0/0, `usse-filter-control-firh-fcs0-c0x8` 13/0/0,
`usse-filter-control-firh-fcs0-c0xffffffff` 13/0/0, `usse-filter-control-firh-fcs1-c0x0` 13/0/0,
`usse-filter-control-firh-fcs1-c0x1` 13/0/0, `usse-filter-control-firh-fcs1-c0x10` 13/0/0,
`usse-filter-control-firh-fcs1-c0x100` 13/0/0, `usse-filter-control-firh-fcs1-c0x2` 13/0/0,
`usse-filter-control-firh-fcs1-c0x4` 13/0/0, `usse-filter-control-firh-fcs1-c0x8` 13/0/0,
`usse-filter-control-firh-fcs1-c0xffffffff` 13/0/0, `usse-filter-control-firh-fcs2-c0x0` 13/0/0,
`usse-filter-control-firh-fcs2-c0x1` 0/13/0, `usse-filter-control-firh-fcs2-c0x10` 13/0/0,
`usse-filter-control-firh-fcs2-c0x100` 13/0/0, `usse-filter-control-firh-fcs2-c0x2` 0/13/0,
`usse-filter-control-firh-fcs2-c0x4` 13/0/0, `usse-filter-control-firh-fcs2-c0x8` 13/0/0,
`usse-filter-control-firh-fcs2-c0xffffffff` 13/0/0, `usse-filter-control-firh-fcs3-c0x0` 13/0/0,
`usse-filter-control-firh-fcs3-c0x1` 0/13/0, `usse-filter-control-firh-fcs3-c0x10` 13/0/0,
`usse-filter-control-firh-fcs3-c0x100` 13/0/0, `usse-filter-control-firh-fcs3-c0x2` 0/13/0,
`usse-filter-control-firh-fcs3-c0x4` 13/0/0, `usse-filter-control-firh-fcs3-c0x8` 13/0/0,
`usse-filter-control-firh-fcs3-c0xffffffff` 13/0/0, `usse-filter-control-firh-fcs4-c0x0` 13/0/0,
`usse-filter-control-firh-fcs4-c0x1` 0/13/0, `usse-filter-control-firh-fcs4-c0x10` 13/0/0,
`usse-filter-control-firh-fcs4-c0x100` 13/0/0, `usse-filter-control-firh-fcs4-c0x2` 0/13/0,
`usse-filter-control-firh-fcs4-c0x4` 13/0/0, `usse-filter-control-firh-fcs4-c0x8` 13/0/0,
`usse-filter-control-firh-fcs4-c0xffffffff` 13/0/0, `usse-filter-control-firh-fcs5-c0x0` 13/0/0,
`usse-filter-control-firh-fcs5-c0x1` 0/13/0, `usse-filter-control-firh-fcs5-c0x10` 13/0/0,
`usse-filter-control-firh-fcs5-c0x100` 13/0/0, `usse-filter-control-firh-fcs5-c0x2` 0/13/0,
`usse-filter-control-firh-fcs5-c0x4` 13/0/0, `usse-filter-control-firh-fcs5-c0x8` 13/0/0,
`usse-filter-control-firh-fcs5-c0xffffffff` 13/0/0, `usse-filter-edges-fcs67-mode0` 2/0/0,
`usse-filter-edges-fcs67-mode1` 0/2/0, `usse-filter-edges-fcs67-mode2` 0/2/0,
`usse-filter-edges-mdc` 32/0/0, `usse-filter-edges-msc` 32/0/0, `usse-filter-edges-rep` 32/0/0,
`usse-filter-gain-firh-fcs0-w0b0-v01` 17/0/0, `usse-filter-gain-firh-fcs0-w0b0-v02` 17/0/0,
`usse-filter-gain-firh-fcs0-w0b0-v80` 17/0/0, `usse-filter-gain-firh-fcs0-w0b0-vff` 17/0/0,
`usse-filter-gain-firh-fcs0-w0b1-v01` 17/0/0, `usse-filter-gain-firh-fcs0-w0b1-v02` 17/0/0,
`usse-filter-gain-firh-fcs0-w0b1-v80` 17/0/0, `usse-filter-gain-firh-fcs0-w0b1-vff` 17/0/0,
`usse-filter-gain-firh-fcs0-w0b2-v01` 17/0/0, `usse-filter-gain-firh-fcs0-w0b2-v02` 17/0/0,
`usse-filter-gain-firh-fcs0-w0b2-v80` 17/0/0, `usse-filter-gain-firh-fcs0-w0b2-vff` 17/0/0,
`usse-filter-gain-firh-fcs0-w0b3-v01` 17/0/0, `usse-filter-gain-firh-fcs0-w0b3-v02` 17/0/0,
`usse-filter-gain-firh-fcs0-w0b3-v80` 17/0/0, `usse-filter-gain-firh-fcs0-w0b3-vff` 17/0/0,
`usse-filter-gain-firh-fcs0-w1b0-v01` 17/0/0, `usse-filter-gain-firh-fcs0-w1b0-v02` 17/0/0,
`usse-filter-gain-firh-fcs0-w1b0-v80` 17/0/0, `usse-filter-gain-firh-fcs0-w1b0-vff` 17/0/0,
`usse-filter-gain-firh-fcs0-w1b1-v01` 17/0/0, `usse-filter-gain-firh-fcs0-w1b1-v02` 17/0/0,
`usse-filter-gain-firh-fcs0-w1b1-v80` 17/0/0, `usse-filter-gain-firh-fcs0-w1b1-vff` 17/0/0,
`usse-filter-gain-firh-fcs0-w1b2-v01` 17/0/0, `usse-filter-gain-firh-fcs0-w1b2-v02` 17/0/0,
`usse-filter-gain-firh-fcs0-w1b2-v80` 17/0/0, `usse-filter-gain-firh-fcs0-w1b2-vff` 17/0/0,
`usse-filter-gain-firh-fcs0-w1b3-v01` 17/0/0, `usse-filter-gain-firh-fcs0-w1b3-v02` 17/0/0,
`usse-filter-gain-firh-fcs0-w1b3-v80` 17/0/0, `usse-filter-gain-firh-fcs0-w1b3-vff` 17/0/0,
`usse-filter-gain-firh-fcs0-w2b0-v01` 17/0/0, `usse-filter-gain-firh-fcs0-w2b0-v02` 17/0/0,
`usse-filter-gain-firh-fcs0-w2b0-v80` 17/0/0, `usse-filter-gain-firh-fcs0-w2b0-vff` 17/0/0,
`usse-filter-gain-firh-fcs0-w2b1-v01` 17/0/0, `usse-filter-gain-firh-fcs0-w2b1-v02` 17/0/0,
`usse-filter-gain-firh-fcs0-w2b1-v80` 17/0/0, `usse-filter-gain-firh-fcs0-w2b1-vff` 17/0/0,
`usse-filter-gain-firh-fcs0-w2b2-v01` 17/0/0, `usse-filter-gain-firh-fcs0-w2b2-v80` 17/0/0,
`usse-filter-gain-firh-fcs0-w2b3-v01` 17/0/0, `usse-filter-gain-firh-fcs0-w2b3-v80` 17/0/0,
`usse-filter-gain-firh-fcs1-w0b0-v01` 17/0/0, `usse-filter-gain-firh-fcs1-w0b0-v02` 17/0/0,
`usse-filter-gain-firh-fcs1-w0b0-v80` 17/0/0, `usse-filter-gain-firh-fcs1-w0b0-vff` 17/0/0,
`usse-filter-gain-firh-fcs1-w0b1-v01` 17/0/0, `usse-filter-gain-firh-fcs1-w0b1-v02` 17/0/0,
`usse-filter-gain-firh-fcs1-w0b1-v80` 17/0/0, `usse-filter-gain-firh-fcs1-w0b1-vff` 17/0/0,
`usse-filter-gain-firh-fcs1-w0b2-v01` 17/0/0, `usse-filter-gain-firh-fcs1-w0b2-v02` 17/0/0,
`usse-filter-gain-firh-fcs1-w0b2-v80` 17/0/0, `usse-filter-gain-firh-fcs1-w0b2-vff` 17/0/0,
`usse-filter-gain-firh-fcs1-w0b3-v01` 17/0/0, `usse-filter-gain-firh-fcs1-w0b3-v02` 17/0/0,
`usse-filter-gain-firh-fcs1-w0b3-v80` 17/0/0, `usse-filter-gain-firh-fcs1-w0b3-vff` 17/0/0,
`usse-filter-gain-firh-fcs1-w1b0-v01` 17/0/0, `usse-filter-gain-firh-fcs1-w1b0-v02` 17/0/0,
`usse-filter-gain-firh-fcs1-w1b0-v80` 17/0/0, `usse-filter-gain-firh-fcs1-w1b0-vff` 17/0/0,
`usse-filter-gain-firh-fcs1-w1b1-v01` 17/0/0, `usse-filter-gain-firh-fcs1-w1b1-v02` 17/0/0,
`usse-filter-gain-firh-fcs1-w1b1-v80` 17/0/0, `usse-filter-gain-firh-fcs1-w1b1-vff` 17/0/0,
`usse-filter-gain-firh-fcs1-w1b2-v01` 17/0/0, `usse-filter-gain-firh-fcs1-w1b2-v02` 17/0/0,
`usse-filter-gain-firh-fcs1-w1b2-v80` 17/0/0, `usse-filter-gain-firh-fcs1-w1b2-vff` 17/0/0,
`usse-filter-gain-firh-fcs1-w1b3-v01` 17/0/0, `usse-filter-gain-firh-fcs1-w1b3-v02` 17/0/0,
`usse-filter-gain-firh-fcs1-w1b3-v80` 17/0/0, `usse-filter-gain-firh-fcs1-w1b3-vff` 17/0/0,
`usse-filter-gain-firh-fcs1-w2b0-v01` 17/0/0, `usse-filter-gain-firh-fcs1-w2b0-v02` 17/0/0,
`usse-filter-gain-firh-fcs1-w2b0-v80` 17/0/0, `usse-filter-gain-firh-fcs1-w2b0-vff` 17/0/0,
`usse-filter-gain-firh-fcs1-w2b1-v01` 17/0/0, `usse-filter-gain-firh-fcs1-w2b1-v02` 17/0/0,
`usse-filter-gain-firh-fcs1-w2b1-v80` 17/0/0, `usse-filter-gain-firh-fcs1-w2b1-vff` 17/0/0,
`usse-filter-gain-firh-fcs1-w2b2-v01` 17/0/0, `usse-filter-gain-firh-fcs1-w2b2-v80` 17/0/0,
`usse-filter-gain-firh-fcs1-w2b3-v01` 17/0/0, `usse-filter-gain-firh-fcs1-w2b3-v80` 17/0/0,
`usse-filter-gain-firh-fcs2-w0b0-v01` 17/0/0, `usse-filter-gain-firh-fcs2-w0b0-v02` 17/0/0,
`usse-filter-gain-firh-fcs2-w0b0-v80` 17/0/0, `usse-filter-gain-firh-fcs2-w0b0-vff` 17/0/0,
`usse-filter-gain-firh-fcs2-w0b1-v01` 17/0/0, `usse-filter-gain-firh-fcs2-w0b1-v02` 17/0/0,
`usse-filter-gain-firh-fcs2-w0b1-v80` 17/0/0, `usse-filter-gain-firh-fcs2-w0b1-vff` 17/0/0,
`usse-filter-gain-firh-fcs2-w0b2-v01` 17/0/0, `usse-filter-gain-firh-fcs2-w0b2-v02` 17/0/0,
`usse-filter-gain-firh-fcs2-w0b2-v80` 17/0/0, `usse-filter-gain-firh-fcs2-w0b2-vff` 17/0/0,
`usse-filter-gain-firh-fcs2-w0b3-v01` 17/0/0, `usse-filter-gain-firh-fcs2-w0b3-v02` 17/0/0,
`usse-filter-gain-firh-fcs2-w0b3-v80` 17/0/0, `usse-filter-gain-firh-fcs2-w0b3-vff` 17/0/0,
`usse-filter-gain-firh-fcs2-w1b0-v01` 17/0/0, `usse-filter-gain-firh-fcs2-w1b0-v02` 17/0/0,
`usse-filter-gain-firh-fcs2-w1b0-v80` 17/0/0, `usse-filter-gain-firh-fcs2-w1b0-vff` 17/0/0,
`usse-filter-gain-firh-fcs2-w1b1-v01` 17/0/0, `usse-filter-gain-firh-fcs2-w1b1-v02` 17/0/0,
`usse-filter-gain-firh-fcs2-w1b1-v80` 17/0/0, `usse-filter-gain-firh-fcs2-w1b1-vff` 17/0/0,
`usse-filter-gain-firh-fcs2-w1b2-v01` 17/0/0, `usse-filter-gain-firh-fcs2-w1b2-v02` 17/0/0,
`usse-filter-gain-firh-fcs2-w1b2-v80` 17/0/0, `usse-filter-gain-firh-fcs2-w1b2-vff` 17/0/0,
`usse-filter-gain-firh-fcs2-w1b3-v01` 17/0/0, `usse-filter-gain-firh-fcs2-w1b3-v02` 17/0/0,
`usse-filter-gain-firh-fcs2-w1b3-v80` 17/0/0, `usse-filter-gain-firh-fcs2-w1b3-vff` 17/0/0,
`usse-filter-gain-firh-fcs2-w2b0-v01` 17/0/0, `usse-filter-gain-firh-fcs2-w2b0-v02` 17/0/0,
`usse-filter-gain-firh-fcs2-w2b0-v80` 17/0/0, `usse-filter-gain-firh-fcs2-w2b0-vff` 17/0/0,
`usse-filter-gain-firh-fcs2-w2b1-v01` 17/0/0, `usse-filter-gain-firh-fcs2-w2b1-v02` 17/0/0,
`usse-filter-gain-firh-fcs2-w2b1-v80` 17/0/0, `usse-filter-gain-firh-fcs2-w2b1-vff` 17/0/0,
`usse-filter-gain-firh-fcs2-w2b2-v01` 17/0/0, `usse-filter-gain-firh-fcs2-w2b2-v80` 17/0/0,
`usse-filter-gain-firh-fcs2-w2b3-v01` 17/0/0, `usse-filter-gain-firh-fcs2-w2b3-v80` 17/0/0,
`usse-filter-sets-firh-fcs0-load0` 17/0/0, `usse-filter-sets-firh-fcs0-nv12` 17/0/0,
`usse-filter-sets-firh-fcs0-ramp` 17/0/0, `usse-filter-sets-firh-fcs1-load0` 17/0/0,
`usse-filter-sets-firh-fcs1-nv12` 17/0/0, `usse-filter-sets-firh-fcs1-ramp` 17/0/0,
`usse-filter-sets-firh-fcs2-load0` 17/0/0, `usse-filter-sets-firh-fcs2-nv12` 17/0/0,
`usse-filter-sets-firh-fcs2-ramp` 17/0/0, `usse-filter-sets-firh-fcs3-load0` 17/0/0,
`usse-filter-sets-firh-fcs3-nv12` 17/0/0, `usse-filter-sets-firh-fcs3-ramp` 17/0/0,
`usse-filter-sets-firh-fcs4-load0` 17/0/0, `usse-filter-sets-firh-fcs4-nv12` 17/0/0,
`usse-filter-sets-firh-fcs4-ramp` 17/0/0, `usse-filter-sets-firh-fcs5-load0` 17/0/0,
`usse-filter-sets-firh-fcs5-nv12` 17/0/0, `usse-filter-sets-firh-fcs5-ramp` 17/0/0,
`usse-filter-sets-firh-fcs6-load0` 17/0/0, `usse-filter-sets-firh-fcs6-nv12` 17/0/0,
`usse-filter-sets-firh-fcs6-ramp` 17/0/0, `usse-filter-sets-firh-fcs7-load0` 17/0/0,
`usse-filter-sets-firh-fcs7-nv12` 17/0/0, `usse-filter-sets-firh-fcs7-ramp` 17/0/0,
`usse-filter-sets-firh-s4-fcs0-w0b0` 13/0/0, `usse-filter-sets-firh-s4-fcs0-w0b1` 13/0/0,
`usse-filter-sets-firh-s4-fcs0-w0b2` 13/0/0, `usse-filter-sets-firh-s4-fcs0-w0b3` 13/0/0,
`usse-filter-sets-firh-s4-fcs0-w1b0` 13/0/0, `usse-filter-sets-firh-s4-fcs0-w1b1` 13/0/0,
`usse-filter-sets-firh-s4-fcs0-w1b2` 13/0/0, `usse-filter-sets-firh-s4-fcs0-w1b3` 13/0/0,
`usse-filter-sets-firh-s4-fcs1-w0b0` 13/0/0, `usse-filter-sets-firh-s4-fcs1-w0b1` 13/0/0,
`usse-filter-sets-firh-s4-fcs1-w0b2` 13/0/0, `usse-filter-sets-firh-s4-fcs1-w0b3` 13/0/0,
`usse-filter-sets-firh-s4-fcs1-w1b0` 13/0/0, `usse-filter-sets-firh-s4-fcs1-w1b1` 13/0/0,
`usse-filter-sets-firh-s4-fcs1-w1b2` 13/0/0, `usse-filter-sets-firh-s4-fcs1-w1b3` 13/0/0,
`usse-filter-sets-firh-s4-fcs2-w0b0` 13/0/0, `usse-filter-sets-firh-s4-fcs2-w0b1` 13/0/0,
`usse-filter-sets-firh-s4-fcs2-w0b2` 13/0/0, `usse-filter-sets-firh-s4-fcs2-w0b3` 13/0/0,
`usse-filter-sets-firh-s4-fcs2-w1b0` 13/0/0, `usse-filter-sets-firh-s4-fcs2-w1b1` 13/0/0,
`usse-filter-sets-firh-s4-fcs2-w1b2` 13/0/0, `usse-filter-sets-firh-s4-fcs2-w1b3` 13/0/0,
`usse-filter-taps-firh-fcs0-e3` 468/0/0, `usse-filter-taps-firh-fcs0-e7` 468/0/0,
`usse-filter-taps-firh-fcs1` 468/0/0, `usse-filter-taps-firh-fcs1-e3` 468/0/0,
`usse-filter-taps-firh-fcs1-e7` 468/0/0, `usse-filter-taps-firh-fcs2` 468/0/0,
`usse-filter-taps-firh-fcs2-e3` 468/0/0, `usse-filter-taps-firh-fcs2-e7` 468/0/0,
`usse-filter-taps-firh-fcs3` 468/0/0, `usse-filter-taps-firh-fcs4` 468/0/0,
`usse-filter-taps-firh-fcs5` 468/0/0, `usse-video-filters-amp-l00-firv-base` 196/0/0,
`usse-video-filters-amp-l00-firv-latch` 196/0/0, `usse-video-filters-amp-l00-firv-o8` 196/0/0,
`usse-video-filters-amp-l00-firv-s8` 196/0/0, `usse-video-filters-amp-l00-firv-scale` 196/0/0,
`usse-video-filters-amp-l00-firv-src2` 196/0/0, `usse-video-filters-amp-l40-firv-base` 196/0/0,
`usse-video-filters-amp-l40-firv-latch` 196/0/0, `usse-video-filters-amp-l40-firv-o8` 196/0/0,
`usse-video-filters-amp-l40-firv-s8` 196/0/0, `usse-video-filters-amp-l40-firv-scale` 196/0/0,
`usse-video-filters-amp-l40-firv-src2` 196/0/0, `usse-video-filters-bilin-base` 34/0/0,
`usse-video-filters-bilin-d-base-apart` 40/0/0, `usse-video-filters-bilin-d-base-r1` 40/0/0,
`usse-video-filters-bilin-d-base-r2` 40/0/0, `usse-video-filters-bilin-d-base-same` 40/0/0,
`usse-video-filters-bilin-d-interleaved-apart` 40/0/0, `usse-video-filters-bilin-d-interleaved-r1`
40/0/0, `usse-video-filters-bilin-d-interleaved-r2` 40/0/0,
`usse-video-filters-bilin-d-interleaved-same` 40/0/0, `usse-video-filters-bilin-interleaved` 34/0/0,
`usse-video-filters-bilin-o8` 34/0/0, `usse-video-filters-bilin-rnd` 34/0/0,
`usse-video-filters-bilin-s8` 34/0/0, `usse-video-filters-bilin-src01-dst23` 34/0/0,
`usse-video-filters-bilin-src23-dst01` 34/0/0, `usse-video-filters-bilin-src23-dst23` 34/0/0,
`usse-video-filters-bilin-w-base` 20/0/0, `usse-video-filters-bilin-w-interleaved` 20/0/0,
`usse-video-filters-bilin-w-o8` 20/0/0, `usse-video-filters-bilin-w-rnd` 20/0/0,
`usse-video-filters-bilin-w-s8` 20/0/0, `usse-video-filters-bilin-w-src01-dst23` 20/0/0,
`usse-video-filters-c10-firh-fcs3-s5neg-ped` 648/0/0, `usse-video-filters-c11-latch-fill5a` 2/0/0,
`usse-video-filters-c11-latch-merge` 0/18/0, `usse-video-filters-c11-latch-pixel` 0/8/0,
`usse-video-filters-c11-latch-read` 2/0/0, `usse-video-filters-c11-latch-writers` 2/12/0,
`usse-video-filters-c7-bilin-round-o8` 80/0/0, `usse-video-filters-c7-bilin-round-o8-rnd` 80/0/0,
`usse-video-filters-c7-bilin-round-s8` 80/0/0, `usse-video-filters-c7-bilin-round-s8-rnd` 80/0/0,
`usse-video-filters-c7-bilin-round-u8` 80/0/0, `usse-video-filters-c7-bilin-round-u8-rnd` 80/0/0,
`usse-video-filters-c7-bilin-src23-base` 40/0/0, `usse-video-filters-c7-bilin-src23-interleaved`
40/0/0, `usse-video-filters-c7-firh-fcs0-taps` 124/0/0, `usse-video-filters-c7-firh-fcs1-taps`
124/0/0, `usse-video-filters-c7-firh-fcs2-o8` 54/0/0, `usse-video-filters-c7-firh-fcs2-s5` 64/0/0,
`usse-video-filters-c7-firh-fcs2-s8` 54/0/0, `usse-video-filters-c7-firh-fcs2-taps` 124/0/0,
`usse-video-filters-c7-firh-fcs3-s5` 64/0/0, `usse-video-filters-c7-firh-fcs3-taps` 124/0/0,
`usse-video-filters-c7-firh-fcs4-taps` 124/0/0, `usse-video-filters-c7-firh-fcs5-taps` 124/0/0,
`usse-video-filters-c7-firh-fcs6-taps` 124/0/0, `usse-video-filters-c7-firh-fcs7-taps` 124/0/0,
`usse-video-filters-c8-firh-fcs5-small` 50/0/0, `usse-video-filters-c9-firh-fcs2-round` 512/0/0,
`usse-video-filters-c9-firh-fcs2-s5neg` 144/0/0, `usse-video-filters-c9-firh-fcs3-round` 512/0/0,
`usse-video-filters-c9-firh-fcs3-s5neg` 144/0/0, `usse-video-filters-c9-firh-fcs4-round` 512/0/0,
`usse-video-filters-cross-firv-base` 260/0/0, `usse-video-filters-cross-firv-s8` 260/0/0,
`usse-video-filters-cross-firv-scale` 260/0/0, `usse-video-filters-cross-firv-src2` 260/0/0,
`usse-video-filters-firh-base-izero` 34/0/0, `usse-video-filters-firh-base-pix` 34/0/0,
`usse-video-filters-firh-fcs2-izero` 34/0/0, `usse-video-filters-firh-k1` 34/0/0,
`usse-video-filters-firh-k1-izero` 34/0/0, `usse-video-filters-firh-k2` 34/0/0,
`usse-video-filters-firh-k2-izero` 34/0/0, `usse-video-filters-firh-k3` 34/0/0,
`usse-video-filters-firh-mdc` 34/0/0, `usse-video-filters-firh-msc` 34/0/0,
`usse-video-filters-firh-o8` 34/0/0, `usse-video-filters-firh-s5-1` 34/0/0,
`usse-video-filters-firh-s5-15` 34/0/0, `usse-video-filters-firh-s5-4` 34/0/0,
`usse-video-filters-firh-s5-m1` 34/0/0, `usse-video-filters-firh-s5-m16` 34/0/0,
`usse-video-filters-firh-s8` 34/0/0, `usse-video-filters-firv-all` 0/34/0,
`usse-video-filters-firv-all-izero` 0/34/0, `usse-video-filters-firv-base` 34/0/0,
`usse-video-filters-firv-latch` 0/34/0, `usse-video-filters-firv-latch-izero` 0/34/0,
`usse-video-filters-firv-latch-pix` 0/34/0, `usse-video-filters-firv-o8` 34/0/0,
`usse-video-filters-firv-s8` 34/0/0, `usse-video-filters-firv-scale` 34/0/0,
`usse-video-filters-firv-src2` 34/0/0, `usse-video-filters-ped-firh-base` 54/0/0,
`usse-video-filters-ped-firh-fcs1` 54/0/0, `usse-video-filters-ped-firh-fcs2` 54/0/0,
`usse-video-filters-ped-firh-fcs2-k1` 54/0/0, `usse-video-filters-ped-firh-fcs2-k2` 54/0/0,
`usse-video-filters-ped-firh-fcs2-k3` 54/0/0, `usse-video-filters-ped-firh-fcs2-mdc` 54/0/0,
`usse-video-filters-ped-firh-fcs2-msc` 54/0/0, `usse-video-filters-ped-firh-fcs2-s5-1` 54/0/0,
`usse-video-filters-ped-firh-fcs2-s5-15` 54/0/0, `usse-video-filters-ped-firh-fcs2-s5-4` 54/0/0,
`usse-video-filters-ped-firh-fcs2-s5-m1` 54/0/0, `usse-video-filters-ped-firh-fcs2-s5-m16` 54/0/0,
`usse-video-filters-ped-firh-fcs3` 54/0/0, `usse-video-filters-ped-firh-fcs4` 54/0/0,
`usse-video-filters-ped-firh-fcs5` 54/0/0, `usse-video-filters-ped-firh-fcs6` 54/0/0,
`usse-video-filters-ped-firh-fcs7` 54/0/0, `usse-video-filters-ped-firh-k1` 54/0/0,
`usse-video-filters-ped-firh-k2` 54/0/0, `usse-video-filters-ped-firh-k3` 54/0/0,
`usse-video-filters-ped-firh-mdc` 54/0/0, `usse-video-filters-ped-firh-msc` 54/0/0,
`usse-video-filters-ped-firh-o8` 54/0/0, `usse-video-filters-ped-firh-s5-1` 54/0/0,
`usse-video-filters-ped-firh-s5-15` 54/0/0, `usse-video-filters-ped-firh-s5-4` 54/0/0,
`usse-video-filters-ped-firh-s5-m1` 54/0/0, `usse-video-filters-ped-firh-s5-m16` 54/0/0,
`usse-video-filters-ped-firh-s8` 54/0/0, `usse-video-filters-ped-firv-all` 0/54/0,
`usse-video-filters-ped-firv-base` 54/0/0, `usse-video-filters-ped-firv-latch` 0/54/0,
`usse-video-filters-ped-firv-o8` 54/0/0, `usse-video-filters-ped-firv-s8` 54/0/0,
`usse-video-filters-ped-firv-scale` 54/0/0, `usse-video-filters-ped-firv-src2` 54/0/0,
`usse-video-ops-adif` 24/0/0, `usse-video-ops-filters` 18/3/0); unsupported mostly for firh's fixed
bank 1 or 2, whose taps are fitted to these vectors (in-sample, not a hardware check) (1112); bytes
of the firh latch the task did not write (read in rN) (285); the firh latch, which a later firh may
reach first (read in rN) (30).

Confirmed on the hardware (a passing vector): #214, #215, #216, #217, #218.

## 8. Hardware probe results

What the instruction text leaves open was asked of the GPU on 2026-10-22: our own pixel
programs ran each instruction under test on preset inputs and wrote the result to the pixel
(the probe runner and the tables under `probes/usse/` of the data repository). The results are
given with their evidence in
`tools/usse-dis/r2/README.md` ("Hardware probes"), whose radare2 ESIL models them. Each fact is
one snippet in `doc/isa/content/usse/probe/`, marked *Measured on the hardware (2026-10-22)*,
with what stays undecided and what would settle it, or *Not probed yet*:

- §8.1 The test sign `p` **[HW]**
- §8.2 `t` in the `a`/`o` joins of a test **[HW]**
- §8.3 The 32-bit adds `iadd32` and `iaddu32` **[HW]**
- §8.4 Test channels **[HW]**
- §8.5 `isub16`/`usub16` lanes **[HW]**
- §8.6 `ima16` lanes and source formats **[HW]**
- §8.7 Integer multiply-add modes **[HW]**
- §8.8 Shift amounts of 32 and over **[HW]**
- §8.9 Index registers **[HW]**
- §8.10 Register offsets of loads and stores **[HW]**
- §8.11 The 14-bit `ldr`/`str` index **[HW]**
- §8.12 Repeat order and overlapping ranges **[HW]**
- §8.13 Predicates on repeated instructions **[HW]**
- §8.14 `br` offsets and the `Pn` predicate **[HW]**
- §8.15 `smlsi` increments **[HW]**
- §8.16 Float rounding and NaN **[HW]**
- §8.17 `frcp`, `frsq` and `fsqrt` precision **[HW]**
- §8.18 Denormals **[HW]**
- §8.19 Write masks **[HW]**
- §8.20 `.incsXYZ` **[HW]**
- §8.21 Pack and unpack lanes **[HW]**
- §8.22 Pack and unpack conversions **[HW]**
- §8.23 Float dot products **[HW]**
- §8.24 Internal registers **[HW]**
- §8.25 Float min/max **[HW]**
- §8.26 Conditional and masked moves **[HW]**
- §8.27 Colour operations **[HW]**
- §8.28 Integer dot products **[HW]**
- §8.29 `fpma` **[HW]**
- §8.30 Half-float multiply-add **[HW]**
- §8.31 `efo` **[HW]**
- §8.32 `fadm`, `fmsa`, `fsubflr` **[HW]**
- §8.33 `flog`, `fexp`, `fsin`, `fcos` **[HW]**
- §8.34 Dual issue **[HW]**
- §8.35 Derivatives `fdsx`, `fdsy` **[HW]**
- §8.36 Texture sampling `smp` **[HW]**
- §8.37 Sampler state **[HW]**
- §7.8 `rlp` **[HW]**
- §8.39 Cache control `ci`, `cf`, `cfi` **[HW]**
- §8.40 Video `adif`, `adifsum`, `bilin`, `firv`, `firh` **[HW]**
- §8.41 Encoding bits no field maps **[HW]**
- §8.42 `.tpres`, `.partial`, `.nosched`, `.syncs` **[HW]**

### 8.1 The test sign `p`

*Measured on the hardware (2026-10-22).* The sign part of a test (`.test<S>...`) is `t`, `n` or `p`.
On a 32-bit result `n` is bit 31 and **`p` is its complement, `>= 0`**, so a zero result passes `p`
**[HW]**: `shl.testpat` and `and.testpat` set the predicate for 0, 1 and `0x7fffffff` and not for
`0x80000000` (probes `usse-tests-sign-p-shl`, `usse-tests-sign-p-and`).
The earlier open
reading `> 0` is wrong. The firmware's `testpat` on `shl` and `isub16` results therefore asks "bit
clear" (after the shift) and "not negative" **[infer]**. On the 16-bit tests of `chan0`, `p` is
`>= 0` on the low lane (*`isub16`/`usub16` lanes*); `iaddu32`, unsigned, passes `p` always (*The
32-bit adds*).

### 8.2 `t` in the `a`/`o` joins of a test

*Measured on the hardware (2026-10-22).* A test joins a sign test and a zero test with `a` (and) or
`o` (or), and either can be `t`. **`t` means true** **[HW]**: `and.testnot`, `.testtoz` and
`.testtonz` set the predicate for every input (probes `usse-tests-join-t-not`,
`usse-tests-join-t-toz`, `usse-tests-join-t-tonz`). So an `o` join with a `t` side is always true,
`testtaz` is "zero",
`testtanz` "not zero", `testnat` "negative" and `testpat` "not negative"; the "not tested" reading
is ruled out.

### 8.3 The 32-bit adds `iadd32` and `iaddu32`

*Measured on the hardware (2026-10-22).* **`iadd32` and `iaddu32` are not full 32-bit adds**
**[HW]**: they add **source 1's low 16 bits**, sign-extended (`iadd32`) or zero-extended
(`iaddu32`), to the 32-bit source 2, modulo 2^32. `0x12345678 + 0x11111111` gives `0x11116789` and
`iadd32 0xffff + 1` gives 0, while `#1 + r` is the plain increment the firmware uses **[RE]** (an
`iaddu32` of the immediate 1 and a register). The test reads the sum: `z` and `n` as usual
for `iadd32` (but see the true sum below); `iaddu32` is unsigned, its `n` is never and its `p`
always true, also for `0x80000000`
(probes `usse-integer-iadd32-value`, `usse-integer-iaddu32-value`, `usse-integer-iaddu32-imm`,
`usse-integer-iadd32-src1-imm`, `usse-integer-iadd32-z`, `usse-integer-iadd32-n`,
`usse-integer-iadd32-p`, `usse-integer-iaddu32-tests`, `usse-integer-iaddu32-np`).

*Later probes (2026-11-08).* **A test reads the true 33-bit sum, not the wrapped 32-bit one**
**[HW]** (E472, E498; probes `usse-compare32x-iadd32-ovf-testnat`,
`usse-compare32x-iadd32-ovf-testpat`, `usse-compare32x-iaddu32-carry-testtanz`,
`usse-iaddu32-pairs-*`): `iadd32`'s `n` and `p` read the sign of `sext16(r1) + r2` with `r2` signed,
so r1 = 0x7fff with r2 = 0x7fffffff leaves `n` clear and `p` set (12 pairs in E472, of which 5
overflow the signed 32-bit sum: the true sum fits 12 of 12, the wrapped one 7; and 16 pairs in E498,
where the true sum fits 16 and the wrapped one 15, the one pair that separates them, (0xffff,
0x80000000), being one of the 5). `iadd32`'s `z` and `nz` read the zero of the same sum with r1
**sign-extended** (E498: 16 of 16, the pairs (0x8000, 0x8000) and (0xffff, 1) read zero, a
zero-extended r1 fits 11; with r2 signed the sum stays within +-2^32, so the true and the wrapped
sum agree in zero-ness on 16 of 16 pairs, and (1, 0xffffffff) reads zero). The nonzero test of
`iaddu32` sees the carry out of bit 31, so r1 = 1 with r2 = 0xffffffff is nonzero: E472's 8 pairs,
and E498's 16, where `testtaz` is true for (0, 0) only and `testtanz` for the other 15 (the sum with
its carry fits under either extension of r1, the wrapped sum under neither, and so does 'zero if
both operands are zero': the 16 pairs do not separate the two); `iaddu32`'s `p` is always true and
its `n` never (16 of 16 pairs each). The probe table's model tested the wrapped sum. With source 1 =
`#0` a test through source 2 reads that register's 32 bits exactly: `n`, `p`, `z` and `nz` of
`iadd32` (8 of 8 values each), `nz` of `iaddu32` (8 of 8) and its `n`, never true (8 of 8).

The value `iaddu32` writes zero-extends source 1 **[HW]** (E521, from the readbacks of two earlier
probes, `usse-decoder-vectors-iaddu32-taz` and `usse-integer-iaddu32-value`: 16 distinct pairs,
seven that a sign extension writes otherwise, such as (0x8000, 0x8000) giving 0x10000), with source
2 `#1`, `#127` and `c56` and into `i0` as well, and under a write mask `.xy` or `.xyzw`, which
repeats the test as on the other forms (E1061, held out). The combined conditions of the test
field and the `o` join read on these adds as on the bitwise group (E1062, held out).

With one writer quad alone writing `sa0` (a branch on `pa0`, E513's), the value read back is the
same
zero-extended sum, 8 of 8 dwords in 6 of 6 rows (E1106, held out; E1061's sa0 row, every instance
writing, mixed other pairs' values).

**Not observable [infer]:** which extension the test of `iaddu32` reads for a source 1 above 0x7fff:
E498's flag rules give the same flag for every pair under both extensions (the sums that would tell
it are nonzero under both readings, and z is true for (0, 0) only under either), so no test settles
it.

### 8.4 Test channels

*Measured on the hardware (2026-10-22).* **A test gives one result per channel, and the channel
field picks one or combines them** **[HW]** (probe `usse-test-channels-chan-tests`, 360 cases):

- an 8-bit operation (`iadd8`, ...) has four channels, **bytes 0-3**, each tested on its own
  (`n` is the byte's bit 7);
- a 16-bit operation has **the low half as channel 0 and the high half as channel 2**;
- a 32-bit or float operation has its value as channel 0;
- **a channel with no lane tests as a positive non-zero value**: `z` and `n` false, `nz` and `p`
  true. That is why the first probes saw `chan1`-`chan3` clear the predicate on a zero test;
- `chan0`-`chan3` take one channel, **`andall`/`orall` all four** (and/or), **`and02`/`or02`
  channels 0 and 2**.

*Later probes (2026-10-22).* **`imul16`, `umul16`, `iadd16` and `uadd16` test their lanes as
channels 0 and 2 on the full product or sum, before it is cut to 16 bits**: `0x100 × 0x100`
writes 0 but does not test as zero, nor does `uadd16`'s `0xffff + 1` or `iadd16`'s
`-0x8000 + -0x8000`. `fmul` and `fsub` test channel 0 like `fadd`, and `isub8`/`imul8` a byte per
channel **[HW]** (probe `usse-test-channels-lanes-other`).

A float test of an exact zero product tests the hardware's `+0`: `fmul` of 0 and -3 gives `+0`,
not IEEE's `-0` **[HW]** (probe `x-misc`).

*Later probes (2026-11-08).* **On a 32-bit result the raw `and` test words with the chan field 1 to
7 and the `a` join do not read as `chan0` as a table** **[HW]** (E530: six field values and six
input pairs in each of seven tables, the prediction that the field is ignored having failed), and
they read as this rule says **[infer]** (252 of 252 cases; the rule was applied after the data, it
predates the runs and was not predicted for them): `chan1`-`chan3` test a channel with no lane, and
`andall`, `orall`, `and02` and `or02` (chan4 to chan7) combine channel 0 with such channels, so a
test of a 32-bit value must name `chan0`. On 8-bit and 16-bit lane operations, where the other
channels have lanes, the same rule held under both joins **[HW]** (E1062: `iadd8` and `iadd16`,
chan0 to or02, the nine fields the assembler names, predicted and held, 288 of 288 tests).

**Undecided:** the mask forms of class 15 (`.bmsk`/`.wmsk`/`.dmsk`); float tests of `-0`,
infinities and NaNs; the one-source tests (`frcp`, `frsq`, `flog`, `fexp`); `fsubflr`, `fdp`,
`fmin`, `fmax`, `fdsx`, `fdsy`, `uadd8`, `usub8`, `umul8` and the `fp*8` operations as
tests; and the operand formats of the `enc[50]` forms.

### 8.5 `isub16`/`usub16` lanes

*Measured on the hardware (2026-10-22).* **`isub16` and `usub16` subtract both 16-bit lanes**, each
wrapping, with **no saturation** **[HW]**: `0x12340005 - #1` is `0x12330004` (an immediate is
subtracted from both lanes), `0 - #1` is `0xffffffff`, `0x00050007 - 0x00010002` is `0x00040005`,
and `usub16 0 - #1` is `0xffffffff`. `chan0` tests the **low lane**: `z` from its 16 bits, `n` from
bit 15 (not bit 31), `p` is `>= 0` on it (probes `usse-integer-isub16-value`,
`usse-integer-isub16-zero`, `usse-integer-isub16-sign-n`,
`usse-integer-isub16-sign-p`, `usse-integer-isub16-reg`, `usse-integer-usub16-value`,
`usse-integer-usub16-zero`). The
firmware's counter comparisons read only the low lane **[RE]**, which fits.

`iadd16`, `uadd16`, `imul16` and `umul16` have two lanes too, tested as channels 0 and 2 **[HW]**
(*Test channels*).

**Undecided:** `usub16`'s sign tests.

### 8.6 `ima16` lanes and source formats

*Measured on the hardware (2026-10-22).* **`ima16 ..., u16, u16` computes `a × b + c`** (`a × b - c`
with `.neg` on source 2) **in each 16-bit lane, wrapping** **[HW]**: `0x00020005 × #3 - 0x00010007`
is `0x00050008` and `0x0000ffff × #3` is `0x0000fffd`; an immediate `b` or `c` is in both lanes, a
register one is taken lane by lane (probes `ima16`, `usse-integer-ima16-plain`,
`usse-integer-ima16-imm-c`, `usse-integer-ima16-reg-b`). This is the firmware's `u16, u16` use
**[RE]**.

**Undecided:** saturation (`.usat`, `.ssat`), `.rsN` and `.abs` on the destination, and an
8-bit source given as an immediate. The 8-bit formats `u8`, `s8` and `o8` are settled (*Integer
multiply-add modes*).

### 8.7 Integer multiply-add modes

*Measured on the hardware (2026-10-22).* The later probes (table `integer.toml`) **[HW]**:

- **`idiv d, a, b, drcN`** writes the **unsigned quotient to `d` and the remainder to `d + 1`**,
  `0xffffffff` to both for `b = 0`; the results arrive once `wdf drcN` returns (without the
  wait the remainder was still missing at the next store) (probe `idiv`).
- **`ima16` with 8-bit formats** reads, in each 16-bit lane, the byte `.low` or `.high` of that
  lane's half of `b` and `c`: `u8` unsigned, `s8` signed, `o8` the byte minus 128; `a` stays
  `u16` (probe `usse-integer-ima16-8bit`).
- **`ima8 d, a, b, c, x, y, z, xa, ya, za`** computes **`x + y × z` per byte**, the colour
  selectors `x`, `y`, `z` for bytes 0-2 and the alpha ones for byte 3 (`s0`, `s1`, `s2` = `a`,
  `b`, `c`; `.comp` = 255 − the byte), wrapping, or clamping to 255 with `.sat` (probe
  `ima8`).
- **`imae`**: `.usat`/`.ssat` saturate the 32-bit result (`.ssat` signed), `.rsN` shifts it right by
  N, source 2 typed `u16` is its half **sign**-extended and `z16` zero-extended, **`coe, iN` writes
  the carry out to `iN` and `cie, iN` adds bit 0 of `iN`** (probe `usse-integer-imae-modes`);
  `ima32`'s `cie, iN` adds bit 0 of `iN` only, as `imae`'s does (E470, E471: 10 of 10 each; E494:
  `ima32` 24 of 24 with `i0` to `i2` and the values 0x10000, 0x80000000, 0xfffffffe, 0x10001,
  0x80000001, 2, 0x55555554 and 0xaaaaaaab, `imae` 8 of 8 with `i0` and `i1`).

- **`idiv` repeats** 1 to 16 times, the count enc[47:44] + 1 (enc[47], outside every field
  before, is its high bit): iteration k divides `a + k` by `b + k`, the quotient to `d + k` and
  the remainder to `d + k + 1`, so after the last iteration `d` to `d + n - 1` hold the
  quotients and `d + n` the last remainder; a divisor 0 gives `0xffffffff` for both. The 21
  cases (three input sets, counts 1 to 16, other destinations) in which no iteration reads a
  register an earlier one writes match this exactly. In the nine in which one does, every such
  read saw what an iteration ten or more before it wrote, and the register's old value where the
  writer ran nine or fewer iterations before (probes `usse-idiv-enc47-grid`,
  `usse-idiv-enc47-repeat-sets`, E367).

*Later probes (2026-11-08).* **`ima32` is the low 32 bits of `a × b + c`**, `.u` and `.s` alike,
with the immediates, the constants, `.neg` on sources 2 and 3, a subtract in one instruction and the
one-bit `cie`, and **`imae`'s carry out and carry in** write and take exactly 0 or 1, in one
instruction or two, chained to a 64-bit accumulate **[HW]** (E469, E470, E471). In a second batch,
with the same forms: **`ima32.u d, iK, a, b, c` writes the high 32 bits of the product with the
addend to `iK`** (15 of 15 cases of five `.u` register triples, E493, then 282 of 282 jobs of
generic register triples, 200 of them random, and the signed form in 282 of 282, E525, E526; the
probe table's model had the `i` registers keep their values, 0 of 15), a borrow follows in one more
instruction, `ima32.u r10, iK, r2, c56, r1` leaving `a - b` and `b - [a < b]` (75 of 75, E501) and
an unsigned compare of two registers being that and `xor.testtanz.chan0 !c0, p0, r2, i0` (64 of 64
pairs of the eight values 0, 1, 0xffff, 0x10000, 0x7fffffff, 0x80000000, 0x80000001 and 0xffffffff,
E501; 252 of 252 seeded pairs and 48 of 48 with each of 0, 1 and 3 `nop`s between, E527), and a
signed compare from `ima32.s` and `xor.testtanz.chan0 !c0, p0, i0, #0` (164 of 164 pairs, E528); 17
more seven-bit immediates, `.neg` on `.s` immediates and constants, and a dependent reader after 0
to 6 and 8 `nop`s are exact (E495); the operand banks `pa`, `sa`, `o`, `g` and `i` are accepted and
read 0 where `mov` reads 0 (31 of 40 cases), and the six r-bank destinations run, r0, r9, r18, r28,
r30 and r31, `sa0`, `o0`, `i1` and `i2` take the result while `pa0` does not (E496); `imae coe, iN`
writes the iN named for `i0` and `i1` (E494).

**Undecided:** `imae` with both `.rsN` and saturation, or with a repeat, a `u16`/`z16` source or a
`.rsN` shift and its carries; `ima32` with `cie` or `.neg` and the extra operand, or with immediates
and constants other than c56 there, its dual-issue secondary form, its selector 3 and what bit 46 of
its word does to `r14` (Q127); when a repeated `idiv`'s result becomes visible to its own
later iterations.

### 8.8 Shift amounts of 32 and over

*Measured on the hardware (2026-10-22).* By a **register** amount of 32 and over, `shl` and `shr`
give 0, `asr` gives the sign (0 or `0xffffffff`) and `rol` takes the amount modulo 32 **[HW]**:
amounts 32, 33, 64, `0x100` and `0xffffffff` behave so, and `shl.testnat` tests the same result
(probes `usse-integer-shl-reg`, `usse-integer-shr-reg`, `usse-integer-asr-reg`,
`usse-integer-rol-reg`, `usse-integer-shl-test-reg`).

*Later probes (2026-10-22).* **Immediate amounts of 32 and over act as register ones** (`#32`,
`#33`,
`#40`, `#127`), and **`~` complements the 32-bit amount or operand before use**: `shl d, a, ~r2`
with `r2 = 0xfffffffc` shifts by 3, `~#3` is `0xfffffffc` (so `shl`/`shr` give 0 and `rol` turns
by 28), and `and`/`or`/`xor` with `~#3` take the complement as their operand **[HW]** (probe
`usse-integer-shift-immediates`).

### 8.9 Index registers

*Measured on the hardware (2026-10-22).* `mov i.l, src` loads the index register and **`r[il + #n]`
is the temporary `i.l + n`, counted from `r0`** in units of one register, as a source and as a
destination **[HW]**; `sa[il + #n]` is the same on the secondaries, counted from `sa0`. **Bits 10
and up of `i.l` are ignored**: `0x401`, `0x40001` and `0xfffffc02` index `r1`, `r1` and `r2` (probes
`usse-indexing-index-unit`, `usse-indexing-index-width`, `usse-indexing-index-width2`,
`usse-indexing-index-width3`, `usse-indexing-index-store`, `usse-indexing-index-sa-unit`,
`usse-indexing-index-sa-store`, `usse-indexing-sa-values`). An index
past the task's temporaries
reaches the next instances' registers **[infer]**: the share of pixels reading other values grows
with it. The firmware's `0x00040000 | index` (bit 18) **[RE]** is the stride of a register
**offset** of a load or store (*Register offsets of loads and stores*), not a mode of an index
register.

*Later probes (2026-10-22).* **`i.h` and `r[ih + #n]` work as `i.l` does** (one register from `r0`,
bits 10 and up ignored), and **`mov i.lh, s` loads `i.l` from the low and `i.h` from the high 16
bits of `s`** **[HW]** (probe `usse-indexing-index-high`).

**Undecided:** the `o` and `pa` banks through an index, and indexed operands of anything but
`mov`; probes like `usse-indexing-index-unit` with `o`/`pa` and an ALU instruction would settle
them.

### 8.10 Register offsets of loads and stores

*Measured on the hardware (2026-10-22).* An immediate offset counts elements of the access size
**[HW/RE]**. A **register** offset `o` (`ldad d, [b,+o]`, `stad [b,+o], s`) is
**`(o >> 16) × (o & 0xffff)` bytes**, both halves unsigned, added modulo 2^32 **[HW]**: `0x00040003`
is +12, `0x00010001` +1, `0x01000001` +256, `0x00000005` +0, and `0xffffffff` faults at the base
minus `0x1ffff`. `[b,-o]` subtracts; `ldad.fetchN [b,+o]` starts one element after, as the immediate
forms do. A load from an address that is not a multiple of 4 reads those bytes; a store there lands
nowhere and does not fault (probes `usse-memory-ldad-reg-off`, `usse-memory-ldad-reg-off-sign`,
`usse-memory-ldad-reg-off-neg`,
`usse-memory-ldad-reg-off-fetch`, `usse-memory-stad-reg-off`, `usse-memory-stad-reg-off-unaligned`).
The
firmware's register offsets OR `0x00040000` (a stride of 4) into a dword index **[RE]**.

**Undecided:** the word and byte forms (`ldaw`/`staw`, ...), the pre- and post-increment forms with
a register offset (what is written back), and the negative fetch `[b,-o]`; the same probes on those
forms would settle them.

### 8.11 The 14-bit `ldr`/`str` index

*Measured on the hardware (2026-10-22).* The immediate register index of `ldr`/`str` has 14 bits (a
reach of 64 KiB of register space) **[RE]**, and **`ldr rD, rI` masks a register index to 14 bits**
**[HW]**: `0x4007`, `0x8007`, `0x10007` and `0x40007` read `CORE_ID` like 7 (probe
`usse-indexing-ldr-index-mask`). A validator can reduce an index modulo `0x4000`.

**Undecided:** `str` with a register index (a client `str` was not seen to land; a probe from the
EDM's own task, on a register that is safe to write, would settle it).

### 8.12 Repeat order and overlapping ranges

*Measured on the hardware (2026-10-22).* With the default MOE state a `.repeatN` steps every operand
by one register per iteration, and **the iterations run one after the other, in ascending order**
**[HW]**: `mov.repeat2 r2, r1` leaves `r3 = r1` (overlapping ranges propagate), and
`mov.repeat3 r1, r2` gives `r1 = r2`, `r2 = r3`, `r3 = r4` (probe `usse-repeat-order`). A repeat of
`mov` behaves like N instructions in sequence;
other forms are taken to as well **[infer]**, as their own probes confirm for `fmad`, the dot
products and the colour group (*`.incsXYZ`*, *Colour operations*).

### 8.13 Predicates on repeated instructions

*Measured on the hardware (2026-10-22).* **One predicate covers the whole instruction** **[HW]** on
`mov` (other repeated forms are taken to behave alike **[infer]**): `p0 mov.repeat2` with
`p0 = 1, p1 = 0` writes both registers and with `p0 = 0, p1 = 1` neither (probe `usse-repeat-pred`).

**Undecided:** what a repeated test writes into its predicate; a probe of `and.testtaz.repeat2`
with inputs that differ per iteration would settle it (`Pn` is settled: *`br` offsets and the
`Pn` predicate*).

### 8.14 `br` offsets and the `Pn` predicate

*Measured on the hardware (2026-10-22).* **`br #k` jumps `k` instructions on from the `br`
itself**: `br #1` runs the next instruction, `br #2` skips one (probe `usse-branch-br-offset`; `ba`
agrees
with the absolute index). **An instruction predicated `Pn` (value 7) never runs**, whatever
`p0`-`p3` hold (probe `usse-predicates-predicate-pn`) **[HW]**.

### 8.15 `smlsi` increments

*Measured on the hardware (2026-10-22).* `smlsi #I0, #I1, #I2, #I3, ...` sets four signed 8-bit
increments **[RE]**: before `mov.repeat2 r20, r10`, **`I0` is the destination's increment and `I2`
the source's** (0 repeats a register, 2 skips one); `I1` and `I3` change nothing there **[HW]**
(probe `usse-repeat-smlsi`). **On a three-source repeat (`fmad.repeat2`)
`I1` is source 0's increment, `I2` source 1's and `I3` source 2's** **[HW]** (probe
`usse-moe-smlsi-three-sources`); `mov`'s source is source 1. With the firmware's `0, 0, 0, 1` at
every task
entry **[RE]** a following `mov` repeat would hold its destination and its source still; the
firmware repeats nothing itself; its 1 is taken to step fetch destinations **[infer]** (*Loads and
stores*).

*Measured on the hardware (2026-11-08).* On `stad.repeatN [rb,...], rs` the base is source 0 and
the data source 2, so by the same rule **`I1` is the base register's increment and `I3` the data
register's** **[HW]** (E483, 12 of 12 cases with 16 valid pointers): with `0, 0, 0, 1` the data
steps by one and the pointer stays, one post-incremented `rb` for the whole repeat (`stad.repeat4
[r40,#1++]` stores `r2`-`r5` at four consecutive dwords); `0, 0, 0, 2` stores every second
register, `0, 0, 0, 0` the same register N times, `0, 1, 0, 1` and `0, 2, 0, 1` step the pointer
by one and by two registers; `I0` and `I2` changed nothing to a store, varied only together
(`1, 0, 1, 1` and `1, 1, 1, 1`). Without an `smlsi` both step by one. The first and the third
increment alone were not run on a store.

The first recorded run of `usse-moe-smlsi-three-sources` began with a case `(1, 1, 1, 1)` that the
table
no longer has: each of its readbacks is the previous case's, and with that shift every case
fits the rule above.

**Undecided:** swizzle mode, the limits, how long the state lasts, and which increment a fetch
uses.

### 8.16 Float rounding and NaN

*Measured on the hardware (2026-10-22).* Floats are IEEE binary32 bit patterns in the 32-bit
registers **[RE]**. **`fmad` rounds to nearest even** and **is not fused**: it rounds `a × b` to
binary32, then the sum **[HW]**. `(1+2^-12)^2` and `(1+2^-12)(1+3×2^-12)`, both ties, round to even,
also when negative; `(1+2^-12)^2 - (1+2^-11)` is 0, not 2^-24; 48 random triples agree (probes
`usse-fmad-round`, `usse-fmad-fused`, `usse-float-functions-sweep-fmad`; `doc/specs/hw_spec.md`
§14). An invalid result is the
NaN **`0x7fffffff`** (`frsq` and `fsqrt` of -1), not the IEEE default `0x7fc00000`. The radare2 ESIL
rounds to nearest even but forms `fmad`'s sum through a double, so a sum of very different
magnitudes can round twice there (`tools/usse-dis/r2/README.md`).

The dot products round each product, then each sum, the same way, but their invalid result is
the NaN `0x7fc00000` **[HW]** (*Float dot products*).

`efo`, `fadm` and `fmsa` round each product and each sum the same way, `fadm`/`fmsa`/`fsubflr`
return the NaN `0x7fc00000` too, and `fmad16` rounds its product to binary32 and its sum to a
half, which for two halves is once, fused **[HW]** (*`efo`*, *`fadm`, `fmsa`, `fsubflr`*,
*Half-float multiply-add*).

**Undecided:** `efo`'s NaN and infinite inputs, and the half-float source forms (`enc[54]`) of
`fmad`, `fadm` and `fmsa`.

### 8.17 `frcp`, `frsq` and `fsqrt` precision

*Measured on the hardware (2026-10-22).* **`frcp`, `frsq` and `fsqrt` are within one ulp but not
always correctly rounded** **[HW]**: of 48 random normal inputs 46, 42 and 44 are exact and the
others one ulp off (at most 0.65 ulp from the true value); `1/3`, `1/5`, `1/√2` and `√3` are exact.
Specials: `frcp(0) = +inf`, `frcp(-0) = -inf`, `frcp` of a denormal `+inf` (its source is flushed),
`frsq(0) = +inf`, `fsqrt(0) = 0`, `frsq` and `fsqrt` of -1 the NaN `0x7fffffff` (probes `frcp`,
`frsq`, `fsqrt`, `usse-float-functions-sweep-frcp`, `usse-float-functions-sweep-frsq`,
`usse-float-functions-sweep-fsqrt`). The
radare2 ESIL rounds them correctly, so it can differ by one ulp, and does not model the specials.

`flog`, `fexp`, `fsin` and `fcos` are measured in *`flog`, `fexp`, `fsin`, `fcos`*.

*Later probes (2026-10-22).* The sweeps' expectations now say so: **within one ulp of the exact
value** settles all three in every run, while "correctly rounded" and "rounded toward zero" do
not fit (the same inputs give the same results run after run).

**Undecided:** `frcp`, `frsq`, `fsqrt` of infinite inputs.

### 8.18 Denormals

*Measured on the hardware (2026-10-22).* **`fmad` flushes denormal inputs, product and result to a
zero of their sign** **[HW]**: `2^-70 × 2^-70` is 0, `-2^-70 × 2^-70 + -0` is -0, `2^-140 × 2^100`
is 0 (probes `usse-fmad-denormal`, `usse-fmad-zero-sign`). The sources
of
`frcp`, `frsq` and `fsqrt` are flushed too (`frcp` of a denormal is `+inf`). No denormal result was
seen.

The dot products and the min/max flush their inputs and results the same way **[HW]** (*Float dot
products*, *Float min/max*); pack and unpack do not: `pckf16f32` keeps a denormal half and
`unpckf32f16` converts one exactly **[HW]** (*Pack and unpack conversions*).

`fadm`, `fmsa`, `fsubflr` flush their inputs too, `flog` of a denormal is `-inf` and `fexp`
flushes results below 2^-126 **[HW]**, while **`fmad16` keeps half denormals** (*`fadm`, `fmsa`,
`fsubflr`*, *`flog`, `fexp`, `fsin`, `fcos`*, *Half-float multiply-add*).

**`efo` flushes as `fmad`** **[HW]** (probe `usse-efo-denormals`): a denormal source, a
denormal product and a denormal sum all give a zero. **`fmad x, 1, -0` is a move** of normals,
infinities and zeros (`+0` as `c` turns `-0` into `+0`), not of denormals (flushed) or NaNs
(`0x7fc00000`) **[HW]** (probe `usse-fmad-move`).

### 8.19 Write masks

*Measured on the hardware (2026-10-22).* The destination write mask (`.x`, `.y`, `.z`, `.w` and
combinations, `enc[47:44]`) **is a repeat of four with iterations left out: component k writes
register `d + k`, computed from every register source `+ k`; an immediate stays the same, and the
lone `.` (mask 0) writes nothing** **[HW]**. `mov r10.xz, r1` writes `r10 = r1` and `r12 = r3`,
`frcp r10.y, r1` writes `r11 = 1/r2`; a component is not a byte. All 16 masks on `mov`, `or`,
`and` with an immediate and `frcp`, and masks on `movc` and on a pack together with its byte
mask, agree (probes `usse-write-masks-wmask-mov`, `usse-write-masks-wmask-or`,
`usse-write-masks-wmask-and-imm`, `usse-write-masks-wmask-frcp`, `usse-write-masks-wmask-other`).
The firmware **[RE]** and our programs use only the default `.x`.

**Undecided:** the test group's masks (with a predicate result) and the 540's reading; the same
probe would settle them.

### 8.20 `.incsXYZ`

*Measured on the hardware (2026-10-22).* The float multiply-add, dot-product, min/max and
derivative groups print `.incsXYZ` (`enc[47]`, `enc[46]`, `enc[40]`) when `enc[53]` is clear
**[RE]**. **Each bit lets one source advance by one register per iteration: X source 0, Y source
1, Z source 2; the destination advances whatever the bits say, and without `.incs` (`enc[53]`
set) every source advances** **[HW]**. `fmad.repeat2.incs001 d, a, b, c` computes `d = a·b + c`
and `d+1 = a·b + (c+1)`; `.incs000` repeats the first operation into `d+1` (probes
`usse-write-masks-incs-fmad`, `usse-dot-products-fdp-incs`, `fddp`,
`usse-float-minmax-fminmax-incs`). `fdp` has no
source 0, so its X bit does nothing, and `fddpc`, which has no `.incs`, never advances its
sources (probe `fddpc`).

`fmad16.repeat2.incsXYZ` advances `a`, `b`, `c` the same way (probe `usse-fmad16-incs`).

**`fdsx`/`fdsy` advance the same way: their `a` and `b` are sources 1 and 2**, so Y advances `a`,
Z advances `b` and X nothing **[HW]** (probe `usse-gradients-fds-incs`; the simulator does not model
`fdsx`/`fdsy` repeats yet).

### 8.21 Pack and unpack lanes

*Measured on the hardware (2026-10-22).* A pack or unpack converts **two values, source 1 and
source 2, and lays them out in the destination format** **[HW]** (probes `usse-pack-u8-bytemask`,
`usse-pack-u16-bytemask`, `usse-pack-c10`, `usse-pack-unpack-select`,
`usse-write-masks-wmask-other`; `doc/specs/hw_spec.md`
§14):

- **8-bit results** (`u8`, `s8`, `o8`): bytes 0-3 take source 1, 2, 1, 2. **`.bytemaskXXXX`**
  enables byte N with bit N (the rightmost digit is byte 0); a disabled byte keeps its value, and
  an enabled byte takes source 1 or 2 by this rule (bN: byte N enabled): byte 0 source 1, byte 1
  `s[b0]`, byte 2 `s[b0 xor b1]`, byte 3 `s[b0 or b1 or b2]`, where `s[0]` is source 1. So
  `.e0.e1` writes source 1 and 2 into bytes 0 and 1, `.e2.e3` into bytes 2 and 3.
- **16-bit results** (`u16`, `s16`, `f16`): the low half source 1, the high half source 2; under
  a byte mask the high half takes source 2 only when byte 0 is enabled.
- **`c10`**: three 10-bit lanes at bits 0, 10 and 20 take source 1, 2, 1; bits 30-31 are 0.
- **Component selects** read a source: byte `c` for 8-bit formats; for 16-bit formats `.0` bits
  0-15, `.1` bits 8-23, `.2` bits 16-31, `.3` nothing (0); the `c10` lane `c` (`.3` is 0); an
  `f32` source ignores its select. An unpack to `f32` converts source 1 only.
- **The write mask** and **`.repeatN`** advance the register sources as everywhere (*Write
  masks*).

**`statomic d, s1.c, s2.c`** (format value 8) writes, in both 16-bit halves, byte `c` of `s1` in
the low byte and byte `c` of `s2` in the high one, each read as a signed byte with negatives
made 0 (`0x80`, `0x7f` give `0x7f00`); the rounding mode and `.scale` change nothing (probe
`statomic`, 2026-10-22). The first probes' `0x78007800` was such a value.

**Undecided:** a byte mask on `c10` results, `.1`/`.3` of an `f32` source on `unpckf32f32`
(`.1` read a shifted value), and what `statomic` is for.

### 8.22 Pack and unpack conversions

*Measured on the hardware (2026-10-22).* **[HW]** throughout (probes `pack-*`, `unpack-*`):

- **From `f32`, without `.scale`:** round to an integer in the instruction's mode (`nearest` ties
  to even, `down`, `up`, `zero`), then saturate to the format: `u8` 0..255, `s8` -128..127, `o8`
  `x + 128` in 0..255, `u16`, `s16`. 300 packs to 255, -5 to 0 (`u8`) or 123 (`o8`).
- **With `.scale`:** `u8` `x × 255`, `s8` `x × 127` clamped to ±127, `o8` `x × 127 + 128` clamped
  to 1..255, `u16` `x × 65535`, `s16` `x × 32767` clamped to ±32767; the product is exact and then
  rounded to nearest even **whatever the mode** (96 random values agree).
- **`c10`** is `x × 255` in a signed 10-bit lane, to nearest even, clamped to ±510 (±2.0),
  with or without `.scale`.
- **`pckf16f32`:** without `.renable` it truncates toward zero in the modes measured (`nearest`,
  `up`), keeps denormal
  results and saturates to 65504; **`.renable` rounds to an integer** in the mode (`up` turns
  1.0005 into 2.0).
- **To `f32`:** integers exactly; with `.scale` `u8/255`, `s8/127`, `o8 (x - 128)/127`,
  `u16/65535`, `s16/32767`, correctly rounded, with -128, 0 (`o8`) and -32768 giving -1.0 (every
  byte value checked); `c10` lanes are always `/255`, clamped to ±2.0; `f16` converts exactly,
  denormals and infinities included, and a NaN becomes `0x7fffffff`.
- **Integer to integer:** `unpcks16s8` sign-extends, `unpcks16u8` and `unpcku16u8`
  zero-extend, `unpcku16s8` turns a negative into 0, and `unpcku8s8` turns a negative into
  `0x7f`, not 0.

- **`c10` to the 16-bit integers is no conversion** **[HW]**: `unpcku16c10` and
  `unpcks16c10`, with or without `.scale`, read **lane 0 of source 1 whatever the selects** and
  write three of its bits into the low half: bit 15 = lane bit 4, bits 1-14 = lane bit 6, bit 0
  = lane bit 8; the high half is 0 (every lane value, probe `usse-pack-unpack-c10-16`). A compiler
  should not
  emit them.

**Undecided:** `.scale` on the integer-to-integer forms, the other `f16` sources, `pckf16f32`
in the modes `down` and `zero`, and the rounding modes of the `c10` packs and of the unpacks
to `f32`.

### 8.23 Float dot products

*Measured on the hardware (2026-10-22).* **[HW]** throughout (probes `usse-dot-products-fdp-count`,
`usse-dot-products-fdp-incs`,
`usse-dot-products-fdp-rounding`, `usse-dot-products-fdp-specials`, `fdpc`, `fddp`, `fddpc`):

- **`fdp.repeatN d, a, b`** sums `N` products `(a+k)·(b+k)` (`N` = 1 without a repeat, up to 4)
  and **writes only register `d + N - 1`**; `d` to `d + N - 2` keep their values. `.incsXYZ`
  chooses which sources advance (*`.incsXYZ`*).
- **Rounding:** each product is rounded to binary32, then they are added in order, each sum
  rounded to nearest even, as a chain of `fmad` would (6 crafted and 42 random cases).
  Denormal inputs and results are flushed, `x - x` is +0, `-0 + -0` is -0, an overflow is `+inf`
  and an invalid operation (`inf × 0`) gives the NaN **`0x7fc00000`**, not the `0x7fffffff` of
  `frsq`.
- **`fdpc d, cpN, a, b`** gives `fdp`'s value and leaves `p0`-`p3` alone.
- **`fddp.repeatN d, iM, s0, s1, s2`** writes `d + N - 1 = s0·s1` and `iM = s0·s2` (`iM` is `i0`
  or `i1`). **`fddpc`** does the same but never advances its sources.

- **`fdpc` writes only its destination** **[HW]**: for every `cp0`-`cp7` and either sign, `d + 1`
  to `d + 3`, `i0`-`i2` and `p0`-`p3` keep their values (probe `usse-dot-products-fdpc-clip`).

**Undecided:** the rounding of `fdpc`, `fddp` and `fddpc` when a product or a sum is inexact
(measured on `fdp`; their exact results agree with it), the half-float source forms, and where
the clip-plane result of `fdpc`/`fddpc` (`cpN`) goes. Presumably to the
clipper with a vertex's outputs **[infer]**. A vertex program that runs `fdpc.repeat4` of the
position against a plane every vertex is outside of (or inside of, or half), on `cp0` and
`cp5`, before it emits, draws the first triangle exactly as without it **[HW]** (E095): with
the TA state our kernel sets, the result clips nothing. The user clip planes are enabled by
`OUTSEL` bits 7:0, and each takes its distance from a vertex output after the position: with
plane 0 on and a fifth vertex dword, `fdpc`'s value written there removes the triangle when it
is negative, as `fdp`'s does, and a triangle with any vertex outside is removed whole **[HW]**.
`cpN` names the plane `fdpc`'s value goes to, and it replaces that plane's distance
from the output dword; `fddpc` gives `s0 · s1` to its first `cp` and `s0 · s2` to its second
**[HW]** (E096).

### 8.24 Internal registers

*Measured on the hardware (2026-10-22).* **`i0`-`i2` are ordinary 32-bit registers to `mov`,
one set per instance** **[HW]**: a fill that gives every pixel its own `i0`-`i2` (from
the pixel's coordinates) reads each pixel's own values back (probe
`usse-internal-registers-per-pixel`). **`i3` reads `i0` of the next instance of the pixel's 2x2
quad**, in the order top-left, top-right, bottom-left, bottom-right and round again, and **a
write to `i3` is dropped** **[HW]**. The first probes saw `i3` read "`i0`" only because every pixel
held
the same value.

**They keep their values from one task to the next**, also from one client to another **[HW]**:
a fill writes `i0`-`i2`, and the next probe, in another process, reads them back (probe
`usse-internal-registers-mov-and-tasks`; `fddp` leaves its result there too). The next task's pixels
see the
values of other pixels: a whole quad of instances moves to another quad of pixels, its four
positions kept, so `i3` stays within the quad (probe `usse-internal-registers-across-tasks`,
recorded). They are not cleared by a task start, as the temporaries are not
(measured on our render node): `i0`, `i1` and `i2` written by one fill were read by the next in 9
of 9 reader jobs (E484).

`efo` reads `i0`/`i1` and writes them after its own reads; **`efo.gpiext`** reaches the other
instances of the quad (*`efo`*).

*Later probes (2026-10-22).* **Bank 7 numbers past `i3` name the other instances of the quad**:
number
`n`, taken modulo 16 (`i31`, `i63` and `i127` read as `i15`), is `4m + j`; `j` = 0-2 reads `ij` of
the instance `m` places on (TL, TR, BL, BR, round again), and `j` = 3 reads `i2` of that instance,
but `i0` of the next one for `i3` itself. **Writes to `i4`-`i7` are dropped**: no instance's
`i0`-`i2` change **[HW]** (probe `usse-internal-registers-bank7`, every pixel). The carries of
`imae`/`ima32` go through `iN` (*Integer multiply-add modes*).

### 8.25 Float min/max

*Measured on the hardware (2026-10-22).* **`fminmax d, a, b, c` is `min(max(a, b), c)` and
`fmaxmin d, a, b, c` is `max(min(a, c), b)`** **[HW]**: both clamp `a` to `[b, c]` when
`b <= c`; when `b > c`, `fminmax` gives `c` and `fmaxmin` gives `b` (six orders of 1, 2, 3 and
ten random triples; probes `usse-float-minmax-fminmax-roles`, `usse-float-minmax-fmaxmin-roles`).
**min and max are IEEE minNum
and maxNum**: a NaN operand loses to a number, `-0` is below `+0`, infinities order as numbers
and denormals are flushed to a zero of their sign (22 special triples, probes
`usse-float-minmax-fminmax-specials`, `usse-float-minmax-fmaxmin-specials`; `doc/specs/hw_spec.md`
§14). `.incsXYZ` as for
`fmad` (probe `usse-float-minmax-fminmax-incs`).

When both operands of a step are NaN, the step returns its **second operand**, payload and
signalling bit kept (`fminmax` of three NaNs gives `c`, `fmaxmin` gives `b`; probe
`usse-float-minmax-allnan`, 2026-10-22).

**Undecided:** the half-float source forms (`enc[54]`), as for `fmad`.

### 8.26 Conditional and masked moves

*Measured on the hardware (2026-10-22).* **[HW]** throughout (probes `movc-*`, `movmsk-*`):

- **`movc.<type>.<test> d, s0, s1, s2`** is a select per lane: each lane of `d` is `s1`'s if the
  test holds for that lane of `s0`, else `s2`'s. Lanes: `.i32` one, `.i16` two, `.i8` four,
  `.i10` three 10-bit lanes at bits 0, 10, 20 (bits 30-31 of `d` become 0). Tests: `.tz` zero,
  `.tnz` not zero, `.tn` the lane's sign bit set, `.tp|z` clear. **`.flt`** tests the float:
  denormals and `-0` are zero, `.tn` is `< 0`, `.tp|z` `>= 0`, and a NaN fails all but `.tnz`.
- **`movmsk.<fmt> d, s1, s2.c`** moves `s1` into `d` when `s2` passes, else leaves `d` alone:
  `.mask` bit 0 of byte `c`, `.u8` bit 7 of byte `c`, `.flt` `s2 >= 0.5` (a NaN fails, `c`
  ignored), `.flt16` half `c >= 0.5` (`.0` bits 0-15, `.1` bits 8-23, `.2` and `.3` bits 16-31).
- **`.smsk`** adds source 0: the move also needs **bit 0 of `s0`** for `.u8`, `.flt` and
  `.flt16`, while `.mask.smsk` ignores `s0` (16 values of `s0` against a passing and a failing
  `s2` per format; probe `usse-movc-movmsk-smsk2`, 2026-10-22).

### 8.27 Colour operations

*Measured on the hardware (2026-10-22).* **[HW]** throughout (probes
`usse-colour-ops-sop2-selectors`,
`usse-colour-ops-sop2-ops`, `usse-colour-ops-sop2-random`, `usse-colour-ops-sop3-lrp`,
`usse-colour-ops-sop3-random`, `sop2wm`, `usse-colour-ops-c10`). Bytes 0-2 are the colour channels
and byte 3 the alpha; a
channel `x` stands for `x/255`:

- **`sop2 d, s1, s2, f1, f2, op+asop2 g1, g2, aop`** computes per colour channel
  `op(s1 × f1, s2 × f2)` and per alpha `aop(s1a × g1, s2a × g2)`: `add` and `sub` sum the two
  exact products, divide by 255 once, round to nearest and saturate to 0..255 (a negative
  difference is 0); `min` and `max` take the smaller or larger **source**, ignoring the
  factors. Factors: `zero`, `s1`, `s2` (the same channel), `s1a`, `s2a`, `asat` =
  `min(s1a, 1 - s2a)`, `s2scale` = `s2` and the whole result doubled (also for `min`/`max`),
  and as second factor `zeros` = 0, which makes `s2` signed (`s2 - 0.5`) in `add`/`sub`.
  `.comp` gives `1 - f` (`asat.comp` = `min(1 - s1a, s2a)`, `s2scale.comp` = `2(1 - s2)`).
  A leading `comp, ` complements `s1` itself in `add`/`sub`; the alpha's `, neg` negates its
  result before saturating (so `sub, neg` is `s2a × g2 - s1a × g1`).
- **`sop3 d, s0, s1, s2, f1, f2, op`** is the same colour operation (`add`/`sub`) with
  factors `zero`, `asat`, `s0`, `s0a`, `s1`, `s1a`, `s2`, `s2a`; with `, neg` (the `alrp`
  form) it is `-op(s1 × f2, s2 × f1)`, the factors swapped. Alpha: `asop a, f2, op` =
  `op(s1a × a, s2a × f2)`; `arsop a, op` = `-op(s1a × f2, s2a × a)`; `alrp a, b` =
  `a × (1 - s0a) + b × s0a`. A factor read for the alpha takes the alpha channels; `asat`
  reads 1 there.
- **`lrp d, s0, s1, s2, x, y, t`**: colour `x × (1 - t) + y × t`, `x` one of `zero`/`s1`, `y`
  one of `zero`/`s2` (each with `.comp`), `t` = `s0` or `s0a`; its alpha is `asop` with two
  free factors. **`sop3c d, s0, s1, s2, f1, f2, m1, m2`**: `f1 × m1 + f2 × m2` with the pairs
  (`s1`, `s2`), (`s1`, `1 - s2`), (`1`, `s2`), (`1 - s1`, `s2`); alpha `alrp`.
- **`sop2wm d.bytemaskN, s1, s2, f1, f2, cop, aop`**: `sop3`'s factors without `s0`, the
  colour operation on bytes 0-2 and the alpha one on byte 3; mask bit N writes byte N.
- **`.c10` operands** are three signed 10-bit lanes (bits 0, 10, 20), 1.0 = 255, clamped to
  ±510 when read and when written; a `c10` source's alpha is its lane 0; a `c10` destination
  gets bits 30-31 clear and an 8-bit destination the saturated channels. The colour formulas
  above hold unchanged.

- **`sop2.repeatN`** computes each iteration on the next registers: the destination
  and both sources advance by one **[HW]** (probe `usse-colour-ops-dot-repeats`). `sop3`, `lrp`,
  `sop3c` and `sop2wm` have no repeat form.

*Later probes (2026-10-22).* **`.c10` operands read the same way on `sop3`, `lrp` and `sop2wm`**
(three signed 10-bit lanes, 1.0 = 255, clamped to ±510, the alpha lane 0) **[HW]** (probe
`usse-colour-ops-c10-other`, against the bytes read as 8-bit channels and an alpha from lane 2), and
**`sop2wm`'s mask bit N writes byte N** as a pack's does (probe `usse-colour-ops-sop2wm-bytemask`).

**Undecided:** `.c10` on `sop3c`.

### 8.28 Integer dot products

*Measured on the hardware (2026-10-22).* **[HW]** throughout (probes
`usse-integer-dot-intdot-lanes`,
`usse-integer-dot-intdot-alpha`):

- **`u8dot4 d, Cx, Ax, s1, s2`** sums the four byte products `s1[i] × s2[i]` and writes the
  same value to every byte: `S × Cx / 255` to bytes 0-2 and `S × Ax / 255` to byte 3, each
  rounded to nearest and saturated to 0..255. **`u8dot3`** sums bytes 0-2 only. `.comp`
  complements a source's bytes first.
- **`off`** makes every byte signed around 128: the products are `(s1[i] - 128)(s2[i] - 128)`,
  and a negative result saturates to 0.
- **`u16dot4`, `u16dot3`** read the same bytes but write a 16-bit fraction to both halves:
  `S × Cx × 32767 / 255²` rounded, saturated to `0x7fff`, or to ±`0x7fff` for `off` (signed);
  `Ax` changes nothing.
- **`u8dot3`'s alpha** (byte 3), when it has an operation: `aadd Ax, f1, a1, f2, a2` =
  `(f1 × a1 + f2 × a2) × Ax / 255` and `asub` the difference, with `a1` = `s1a`, `a2` = `s2a`
  (each possibly `.comp`) and factors `zero`, `s1a`, `s2a`; `alrp s0, x, y` = `x × (1 -
  s0a) + y × s0a` and `alrpc s0, x, y` = `(1 - x)(1 - s0a) + y × s0a`.
- **Repeats** : `u8dot3.repeat2`, `u8dot4.repeat3`, `u16dot4.repeat2` advance the
  destination and both sources by one per iteration **[HW]** (probe `usse-colour-ops-dot-repeats`).

**Undecided:** `.c10` operands (sources, source 0 and the destination), and the `u8dot3`
alpha selections the probes did not try.

### 8.29 `fpma`

*Measured on the hardware (2026-10-22).* **`fpma d, s0, s1, s2, c0, c1, c2, a0, a1, a2` is
`c0 + c1 × c2`** per colour channel and `a0 + a1 × a2` for the alpha **[HW]**: the first
selection is the addend (`s0`, `s1`, `s0a`, `s1a`), the other two the factors (`s1`/`s1a`,
`s2`/`s2a`), each `.comp` giving `1 - x`; with channels as `x/255`, the result is
`(255 c0 + c1 c2) / 255` rounded to nearest and saturated to 0..255. `.neg` negates `s0`.
`.c10` operands read and write the signed 10-bit lanes of the colour operations (±510);
`.sat` changes nothing that we saw (probe `fpma`).

Also: **`.sat` changes nothing** also for `c10` results below 0 and above 1.0, which stay
clamped to ±2.0 only (probe `usse-colour-ops-fpma-sat`), and **`fpma.repeatN` advances the
destination and the
three sources by one per iteration** (probe `usse-colour-ops-dot-repeats`) **[HW]**.

**Undecided:** `.neg` together with an added `s1`.

### 8.30 Half-float multiply-add

*Measured on the hardware (2026-10-22).* **`fmad16 d, a, b, c` computes `a × b + c` in each
16-bit half** (low half from the low halves, high from the high) **[HW]**: the product rounded to
binary32, then the sum to a half, both to nearest even. A product of two halves fits a binary32,
so for halves this is one rounding, fused (20 random cases tell it from rounding the product to a
half first). Half denormals are kept, zeros keep their IEEE signs, overflow gives infinity and an
invalid result the half NaN `0x7fff`. **`.swzll`** feeds both lanes the operand's low half,
**`.swzhh`** its high half, and **`.swzf32`** the whole register as a binary32 value (not rounded
to a half: `8209.25 × 1.5 + 3` gives `0x7204`, not the `0x7203` of rounding 8209.25 to a half
first); with it the product can need more than 24 bits, and the hardware rounds it to binary32:
of 992 `.swzf32` results one tells this from a single rounding (`-0.41455 × 40.8136 + 2.0625`,
probe `x-fmad16`, checked by `crates/sgx-sim`). `.neg`, `.abs` act on the operand;
`.repeat2.incsXYZ` advances `a`, `b`, `c` as `fmad` does (probes `usse-fmad16-lanes`,
`usse-fmad16-incs`,
`usse-fmad16-specials`, `usse-fmad16-rounding`).

**Undecided:** a denormal or NaN `binary32` behind `.swzf32` (flushed or not).

### 8.31 `efo`

*Measured on the hardware (2026-10-22).* **`efo` does what its text prints** **[HW]**: `m0` and
`m1` multiply the named sources (`src0`-`src2`, each with its `.neg`, or `i0`/`i1`); `a0` and
`a1` add (or subtract) the named values; the destination takes `a0`, `a1`, or the **old**
`i0`/`i1`; `i0` and `i1` are written after, unless marked `!`. Every product and every sum is
rounded to binary32 (24 random cases); a repeat's second iteration sees the first one's `i0`
and `i1` (probes `usse-efo-dataflow`, `usse-efo-rounding`).

**`.gpiext`**, with a different `i0`-`i2` in every pixel (probe
`usse-internal-registers-efo-gpiext-quad`)
**[HW]**:

- the multipliers read the instance's own **`i2` for `i0` and its own `i0` for `i1`**; the
  adders and the destination read its own `i0`/`i1`;
- a write of `i0` goes to the instance's own **`i2`**;
- the four instances' writes of `i1` all end in **one register, the top-right pixel's `i0`**,
  which holds the bottom-right pixel's value afterwards; the other pixels' `i0` and `i1` are
  left alone. Through `i3` (the next instance's `i0`) the top-left pixel then reads it too.

While an instruction writes `i1`, the top-right pixel's reads of `i0` (destination, multiplier
or adder) give the **top-left pixel's `i0`**, and now and then (about 1 read in 3000) the value
the top-left pixel is writing: the result depends on timing (probe
`usse-internal-registers-efo-gpiext-race`,
recorded). Every effect stays within the pixel's own 2x2 quad, which belongs to one task:
300 jobs of two clients submitted concurrently never saw the other client's values within a
task (a stress run of the probe table, its readbacks not kept). The earlier "one pixel
in four" is the top-right pixel of every quad.

**Undecided:** repeats beyond two, and whether the four `i1` writes go to the top-right `i0`
in order (the bottom-right one last) or only the bottom-right one is kept.

### 8.32 `fadm`, `fmsa`, `fsubflr`

*Measured on the hardware (2026-10-22).* **[HW]** (probes `usse-float-misc-fadm-fmsa-fsubflr`,
`usse-float-misc-fadm-fmsa-fsubflr-specials`):

- **`fadm d, a, b, c` = `a·c + b·c`**, each product and then the sum rounded to binary32 (not
  `(a + b) × c`: 24 random cases fit only this order), like a two-term `fdp`;
- **`fmsa d, a, b, c` = `a·a + b·c`**, rounded the same way;
- **`fsubflr d, a, b` = `a - floor(b)`**, one rounding.

Denormal inputs are flushed; an invalid result (`inf × 0`, `inf - inf`, a NaN input) is the
NaN `0x7fc00000`, as for the dot products.

**Undecided:** the half-float source forms (`enc[54]`), as for `fmad`.

### 8.33 `flog`, `fexp`, `fsin`, `fcos`

*Measured on the hardware (2026-10-22).* **[HW]** (probes `usse-float-functions-fsingle-base`,
`usse-float-functions-fsingle-specials`,
`usse-float-functions-sweep-flog`, `usse-float-functions-sweep-fexp`,
`usse-float-functions-sweep-fsin`, `usse-float-functions-sweep-fcos`):

- **`flog` is `log2`**: exact on powers of two; within one ulp elsewhere, or within 2^-22
  near 1 (`log2(1 + 2^-23)` gives 2^-23); 0, `-0` and denormals give `-inf`, `+inf` gives
  `+inf`, negatives and NaN the NaN `0x7fffffff`.
- **`fexp` is `2^x`**: exact on integers, within two ulps elsewhere (78 of 95 exploration
  cases within one); results below 2^-126 are 0, from 128 up `+inf`; `-inf` gives 0, a NaN
  `0x7fffffff`.
- **`fsin`, `fcos` take the argument in quarter turns**: `sin(πx/2)`, `cos(πx/2)`, period 4,
  exact on integers; the result is a fixed-point value with 15 fraction bits (absolute error up
  to about 2^-15.5, so tiny results are 0 or 2^-15); an infinite or NaN argument gives
  `0x7fffffff`. Odd multiples of 1/2 are not exact: `fcos(0.5)` is 23171/2^15, the nearest
  being 23170/2^15 (probe `x-fcos`).
- **The zeros at integers have a sign** (probes `x-fsin`, `x-fcos`,
  `usse-float-functions-fsingle-specials`):
  `fsin` is odd and `fcos` even, and in quarter turns `r = |x| mod 4` `fsin` gives `+0` at
  `r = 0` and `-0` at `r = 2`, `fcos` `-0` at `r = 1` and `+0` at `r = 3`: `fsin(-0)` is `-0`,
  `fsin(2)` `-0`, `fsin(4)`, `fsin(100)` and `fsin(10^6)` `+0`, `fcos(1)` and `fcos(-1)` `-0`,
  `fcos(3)` `+0`. A denormal argument is flushed (`fcos` of one is 1).

*Simulator check, 2026-10-23.* The simulator (`crates/sgx-sim`, `func.rs`)
gives these functions and `frcp`, `frsq`, `fsqrt` exactly where the hardware is exact and
otherwise, as a *near* value, the nearest one with the bound above; the vector tests accept a
near value within its bound and stop on anything computed from one. All the recorded vectors
of the seven functions fit, write masks included (as *Write masks*).

**Undecided:** `.flt16` and `.c10` sources, repeats on these, and the sign of a tiny
result rounded to zero.

### 8.34 Dual issue

*Measured on the hardware (2026-10-22).* **A dual-issue word runs two operations that read
before either writes** **[HW]** (probes `dual-issue`, `usse-dual-issue-predicates`; 144 pairings
explored by `x-dual`):

- the primary computes on its operands as alone (`fssq d, a, b` is `a·a + b·b`, each product
  rounded), the secondary on `i0`-`i2` and, for a source naming a register, **the primary's
  source in that position, without its `.neg`**;
- both read the values from before the word: a primary reading `i0` gets the old `i0` while the
  secondary writes it, and a secondary reading `i0` the old one while the primary writes it;
  when both write one register, **the secondary's value stays**;
- `.repeat2` repeats **both**: the primary's operands advance, the secondary runs twice on the
  internal registers (`fadd i0, i0, i1` adds `i1` twice);
- the two-bit predicate (always, `p0`, `p1`, `!p0`) **covers both operations**.

**Pairs that co-issue** cleanly: with a `mov` primary every secondary but `ima32`; with `fmad`
or `ima32` the secondaries `fmad`, `fadd`, `fsub`, `fmul`, `fsubflr`, the single-source
functions and `mov` (`ima32` also `fmad16`, `fmsa`); with `fadm`, `fmsa` or `fssq` the
add-type (`fadd`, `fsub`) and single-source secondaries and `mov`; with `fminmax` only `fmul`, the
single-source functions and `mov`. **Other pairs share a unit and give mixed results**
(probe `usse-dual-issue-conflicts`, recorded): the secondary gets the primary's intermediate value
(`fadm` + `fmul` gives the primary's second product, `fminmax` + `fadd` its comparison
difference, `fmad` + `fmsa` the primary's result) or the primary is lost (`fmad` + `fmad16`
writes 0). An `fddp` primary wrote its second product to the secondary's destination and the
secondary nothing (recorded, not settled).

*Later probes (2026-10-22).* **`ima32` as a secondary computes two 16-bit lanes**, `a × b + c` in
each, wrapping, as `ima16` with `u16` sources; next to an `fmad`, `fadm`, `fmsa` or `fssq`
primary its `b` is **the primary's source 1** whatever it names, next to a `mov` the register it
names **[HW]** (probe `usse-dual-issue-ima32`, integer and float inputs). **The pairs that share a
unit are deterministic** (probe `usse-dual-issue-shared`, new values; the earlier cases fit too):

- a multiplying secondary (`fmul`, `fmad`) of a two-product primary (`fadm`, `fmsa`, `fssq`)
  gets the primary's second product, plus its own `c` for `fmad`;
- an `fmsa` secondary of `fmad`, `fadm` or `fmsa` writes the primary's result, as does an
  `ima32` secondary of an `ima32` primary;
- the add-type and `fmad` secondaries of `fminmax` get `max(a, b) - c` (the primary's last
  comparison difference);
- `fmad` + `fmaxmin` computes `a·b - c` for the primary and `b - c` for the secondary;
- `fmad` + `fmad16`: the secondary as alone, the primary 0.

**Undecided:** the secondaries' half-float (`enc[54]`) forms; `fminmax` + `ima32`; `fddp`
primaries; `fsubflr` and `fmad16` after `fadm`, `fmsa`, `fssq` or `fminmax`; `fmaxmin` after
anything but `fmad`; `fmsa` after `fssq` or `fminmax`; `.abs` on a primary source; and a
register operand of the secondary under `.repeat2`.

### 8.35 Derivatives `fdsx`, `fdsy`

*Measured on the hardware (2026-10-22).* **`fdsx d, a, b` = `a`(top-right) − `b`(top-left) and
`fdsy d, a, b` = `a`(bottom-left) − `b`(top-left), the same value for all four pixels of the 2x2
quad** **[HW]** (coarse derivatives; probe `usse-gradients-fds-quad`, on per-pixel values from the
pixel
coordinates). The difference is rounded once to binary32;
`.neg` and `.abs` act on the source before. The quads are the aligned 2x2 blocks of the
render target (even x and y at the top left).

**Undecided:** partly covered quads (the probes fill whole quads), denormal inputs, and the
half-float source forms (`enc[54]`).

### 8.36 Texture sampling `smp`

*Measured on the hardware (2026-10-22).* **`smp2d d, c, s, drcN` samples the texture whose four
state words are in `s`, `s + 1`, `s + 2`, `s + 3` at the normalized coordinates in `c` and
`c + 1`, and writes the texel to `d` when the fence `drcN` is waited for** **[HW]** (probe
`texture-sampler-smp-point`). The state words are those the PDS gives
the
texture unit for our copies (`doutt`, `doc/specs/transfer.md` §4.4), built in temporaries
by the program itself:

- point sampling picks texel `floor(u × width)`, `floor(v × height)`; coordinates outside
  `[0, 1)` **clamp to the edge**; the texel arrives as stored (the raw B8G8R8A8 dword);
- `smp1d` reads `u` alone, row 0; `.flt16` takes both coordinates as halves of one register
  (`u` low); `smp2dbias`, `smp2dreplace`, `smp2dgrad` with a LOD of 0 sample the same texel;
- with `.repeat2` or a write mask the job faults at an address made of the state's fourth word,
  as if the next iteration read the state one register on **[infer]** (probe
  `texture-sampler-smp-repeat-mask`).

**The gradient footprint (E721, 8 of 8 held-out jobs with independent operands).** The LOD
of `smp2dgrad` is the logarithm of the larger of the two Euclidean lengths of the vectors (op0,
op2) and (op1, op3), scaled by the level size (1992 to 2048 of 2048 pixels, 4 jobs exact, the
rest off by whole columns or rows; at most 256 for the five other footprints declared), and its
fraction is truncated to 1/64 (2016 to 2048 of 2048 on 8 of 8 ladders, against 1160 to 1840 for
rounding). The residual pixels are Q280. A ladder of the fraction over 64 columns with u and v
held constant wrote one dword a job, so no step was placed there (E744).

**Undecided:** the LOD of a quad's own derivatives, `.sinf`/`.rsd`, `.c10` coordinates, `smp3d`
beyond the point-sampled textures of E567, and state read from `sa` or `c` (only temporaries were
used); the state fields, the mip chains and the LOD values are measured in *Sampler state* and
E041, E441, E562 and E563.

### 8.37 Sampler state

*Measured on the hardware (2026-10-22).* A later series varied the four state words an `smp` program
builds (T0-T3, the `doutt` words; `doc/specs/transfer.md` §4.4) on a texture in the
scratch buffer whose dwords count up, so every result names the texels it came from **[HW]**
(table `probes/texture/state-words.toml`):

- **Filtering (T0 bits 13:12, probes `texture-sampler-smp-bilinear`,
  `texture-sampler-smp-filter-modes`).** 1 and 2 are
  bilinear, 0 and 3 point. **Bilinear weights are truncated to 1/64 and each 8-bit channel is
  filtered in two stages, x on both rows and then y, each stage `(a (64 - f) + b f + 32) >> 6`**
  (E720: 8 of 8 held-out jobs on the 1/64 grid, the joint sum rounded to nearest with halves up
  0 of 8; the 21 `smp-bilinear` vectors give the same words under both forms), before any
  conversion: between texels 255 and 15 at `v + k/256` the f32 result steps every four `k`. The
  minification field does not act while magnifying (every case magnifies: the LOD forms never left
  level 0).
- **Addressing (T0 bits 8:6 U, 5:3 V; `texture-sampler-smp-address`).** A stride texture (T1 type 6,
  our copy
  sources) clamps to the edge whatever the modes say. On a twiddled texture (type 0) **0
  repeats, 1 mirrors (period twice the size), 2 clamps to the edge, 3 mirrors once** (the
  absolute coordinate, then clamped); bits 2:0 do not act on `u`. **Modes 4-7 (E565):** on the
  v axis 6 and 7 clamp and 4 and 5 repeat (held out at a pitch of one texel, E932); on the u axis
  none of clamp, nomask or border fits, and every read is the v rule's index plus 180 dwords in
  modes 4, 6 and 7 at 16 x 16 (post hoc, at three bases, E932; whatever T3 or the v mode, E957),
  116 at 8 x 8 and 308 at 32 x 32 (E957; 8 N + 52 fitted), and 308 on every pixel of E565's
  32 x 8 jobs (SEMI, E983). On held-out textures of W != H (E1000) the frozen rivals (the width,
  the height, the size as a square, the mean side) each fail a shape: 8 x 32 reads the height's
  308; post hoc every read of eleven jobs is **8 max(W, H) + 52** dwords past the index, mode 5's
  reads left and right of the texture 5 max(W, H) + 52 + t and 6 max(W, H) + 52 + t, t the texel
  row, and one dword per corner with v outside too (E983) [fitted, not held out]. No kept job
  outside those eleven parts max(W, H) from W; mode 5 with s inside and t outside reads 7 M + 52 + s
  above and 4 M + 52 + s below, not the inside offset, and the corner dwords move with the shape
  (16 to 19 at 16 x 16, 20 to 23 at 32 x 8) (E1017, held out offline against the frozen form,
  the forms post hoc). **Held out (E1026): 8 max(W, H) + 52 texels** at 32 x 64, 8 x 64 and 128 x 32
  in modes 4, 6 and 7 and on a u16 texture (texels, not dwords), and with u and v in mode 5 the
  side, above and below reads follow max(W, H) too; the corner base is 24 at 64 x 16 and 16 x 64, no
  frozen form (post hoc 4 log2 max(W, H)); a strided texture reads modes 4 to 7 as mode 0 (E565).
  **Held out (E1039): the corner base is 4 log2 max(W, H)**, corners above left, above right, below
  left, below right at + 0 to 3, at 8 x 8, 32 x 32, 128 x 32, 32 x 128, 128 x 128 and 256 x 32,
  every other region of mode 5 by max(W, H) there too. Types 1, 3 and 4 at 16 x 16 in u mode 4
  read neither their mode 0 image nor it plus 180: a named dword past the texture with each byte
  halved, the rows alike (post hoc). **Held out (E1055): types 1, 3 and 4 read every pixel in u
  modes 4 to 7 as a named dword halved byte by byte, rows alike**, at 32 x 32 (mode 4) and 16 x 16
  (modes 5 to 7); in mode 4 the name follows the column inside the texture (676 + (x mod 16) at 16 x
  16, 1300 + (x mod 32) at 32 x 32 post hoc); modes 6 and 7 read mode 4's last column and mode 5 one
  other name (post hoc). **The size form failed (E1065): 39 W + 52 (type 4 40 W + 20) read none of
  8 x 8, 64 x 64 and 64 x 16 on types 1 and 3**; post hoc type 1 reads W H + 7 W + 52 + (x mod W) at
  five sizes. Why these constants, the size form and the half are open (Q177).
- **Twiddled layout (`texture-sampler-smp-twiddled`).** Texel `(x, y)` lies at the Morton index with
  **`y` in
  bit 0, `x` in bit 1**, and so on; a non-square texture puts the longer side's extra bits
  above (16 × 16, 8 × 8, 16 × 4 and 4 × 16 tried). **Above 16 on a side the texture is tiles
  (E561, 32-bit texels, sizes 8 to 128 on a side):** each tile of up to 16 × 16 texels is
  interleaved as above and the tiles follow in raster order, `x` first; 32-bit texels of 14
  sizes were run, and other sizes and texel sizes were not. The mip chain of a non-square
  texture halves both sides down to 1 × 1 and the T0 fields read it as a square chain (E562),
  held out with a side of 1 at level 0, on a 1D texture (`smp1dreplace`, 64 × 1), at 64 × 32 and
  256 × 32 and at u16, whose levels are packed in 16-bit texels and whose MIPFILTER blend is one
  16-bit lerp (E1052).
- **Formats (T1 bits 28:24, no conversion; `texture-sampler-smp-formats`).** 0 and 1 return the byte
  (`s8`
  not extended), 7-11 the half, 12, 15-18, 22 and 31 the dword; **2, 3, 4 and 5
  (`4444`, `8332`, `1555`, `565`) expand to B8G8R8A8 by repeating each field's bits**, alpha
  `0xff` when the format has none; 13 swaps red and blue (R8G8B8A8), 19 clears the sign bit,
  21 the top byte, 30 sets it. 6, 14, 20 and 23-29 (signed, 10-bit, compressed or YUV
  layouts) are recorded (`texture-sampler-smp-formats-other`); 14 writes two registers. **28 and
  29 (YUV) read opaque black** in a fill with the colour-space set not loaded (E568, through a
  dangling poke set, see its correction); with the set loaded a fill reads E037's conversion of
  its texel, format 28 as Y0 U Y1 V and 29 as U Y0 V Y1, two texels a dword (E1097: 2048 of 2048
  in 7 fills) **[HW]**. The set is kept from one job to the next, across a debugfs reset: a copy
  that does not load it reads the last loaded set (E1097, post hoc). A fill's transfer command
  loads set 0 when its load flag (xfer:17 bit 0) is set, as a copy's does (E037): BT.601 words
  turn a set of zeros into the conversion, zeros turn the conversion into black, and a later fill
  without the flag keeps the loaded set (E1103, held out, formats 28 and 29) **[HW]**. A copy
  without the flag reads zeros after the kit's health fill and triangle, with or without a
  recovered hang before them, while a debugfs reset alone keeps the set (E1112) **[HW]**. Of the
  pair it is the triangle: a copy without the flag reads zeros after the health triangle (t10
  `tri`, a 64 x 64 render) and keeps the loaded set after the health fill, a plain copy, a debugfs
  reset and 60 s or 120 s of idle (E1134, held out, both replicates) **[HW]**; which part of a
  render clears it is not measured.
- **Conversion (T3 bits 17:16, normalization bit 15; `texture-sampler-smp-convert`).** 1 gives
  **c10**: the
  B, G, R channels in the 10-bit fields of the first register (the 8-bit value unscaled,
  1.0 = 255 as `.c10` operands read it) and A in the second; 2 gives **f16** pairs R, G then
  B, A (alpha 1.0 when the format has none); 3 gives **f32** B, G, R, A, one register each.
  Values are the integers (0-255, 0-65535) unless bit 15 is set, which divides by 255 (by
  65535 for `u16`). T3 26:23 changes no `smp` result (fetch spacing). **Without alpha
  (565) c10 and f32 leave its register unwritten** (c10 one register, f32 three) and f16 gives
  1.0 even unnormalized. **The other formats convert their channels** (cases 24-47): format 0
  is one u8 channel, 7 two (the low byte first), 9 one u16; c10 puts channel k in the k-th
  10-bit field of one register (a u16 as its top byte: `0xd000` gives `0xd0`), f16 packs the
  channels in pairs (low half first: format 7's `0x0451` gives `h(81) | h(4) << 16`), f32 gives
  one register per channel.
- **PCF (`texture-sampler-smp-pcf`).** `smp2d.pcf` compares **texel OP reference**, the reference
  being the
  f32 in the register after the coordinates (`.pcff16`: the f16 in its low half, full precision
  and signed, E116), by T3 bits 31:29
  (0 never, 1 `<`, 2 `==`, 3 `<=`, 4 `>`, 5 `>=`, 6 `!=`, 7 always), and returns 1.0 for an f32
  texture (format 18) or `0xffff` for `u16` (format 9, compared as texel / 65535) when it
  holds, else 0; with bilinear filtering the four results are averaged (`0x8000` for one of two
  texels at half weight, the only split measured). A colour format ignores `.pcf`.
- **Other state bits (exploration `x-smp2`, E566, E564).** In `smp` T3 bits 3:0 and 7:4 are the
  row and column offsets at every value tried (E566). Bits 8, 9, 20, 21 and 22 change nothing on a
  strided texture, nor do 11 and 12, but on a twiddled chain texture bits 11 and 12 change every
  pixel (E564): bit 11 cleared reads level 0's texel (x, y) and bit 12 set the 1 x 1 level, at
  one LOD on one chain (post hoc). **Held out with smp2dreplace (E1027): bits 12:11 pick the level
  whatever the LOD: 00 level 0, 01 the LOD's level, 11 and 10 the last level T0's max level allows**
  (not a LOD bias, not a constant address). Bits 10, 14, 18, 27 and 28 offset the texel by an amount
  that changes with the
  pixel position, and bit 13 faults the job. Setting T0 bits 30 or 31 reads other values: they
  act, how is not known.
- **The address bits (E722, 13 of 16 held-out fills; the other 3 faulted past the probe's
  scratch, E743, E787).** **T3 bits 28:27 pick a level L and bits 19:18 a scale e: the texel is
  read at base + ((off + idx) << e) dwords**, off the sum over k < L of max(1, w >> k) max(1,
  h >> k) (the level sizes, not the stride times the height) and idx the tile-law index of (X >>
  L, Y >> L), or X >> L + stride (Y >> L) on a strided texture; **bit 10 reads the base dword**;
  the offset bits 7:0 act before. Run on twiddled textures up to 64 x 64 and strided 128 x 32, a
  32-bit format only; the scale shifts the dword address, not the index alone (3 jobs). Bits 11
  and 12 select the level (above, E1027). **Bit 14 shears a strided read** (E968): at a width equal
  to the
  stride (64) the dword plus 32 plus 64 per column, held out offline on a second job; at width 32,
  stride 64 the six frozen forms fail, and post hoc dword + floor(S * S * u), u clamped to [0, 1],
  fits all three strided jobs; on a twiddled texture it faulted (E566). **It moves the read by
  floor(4096 clamp(u, 0, 1)) texels** (E975 post hoc in dwords on 32-bit texels; E1003 held out
  on six strided geometries: strides 16 and 256, u off the grid and past both ends, v varying, and
  a 16-bit format, where it is texels, not dwords, 6 of 6; sgx-sim models it point sampled at
  formats 9 and 12); under a bilinear sample it moves the whole footprint by that count, u the
  sample's coordinate (E1027, one row); on a twiddled texture the sample is taken over a texture
  W + 4096 texels wide at frac(u), point and bilinear, its columns repeated over that width
  (E1047, E1049, E1058, E1067; sgx-sim models it at the sizes run).
- **sRGB (T0 bit 27; E723).** **A point-sampled texel byte is decoded sRGB to half float** (4 of
  4 held-out fills exact over 2048 pixels: strided 8 x 4, twiddled 8 x 8 twice, twiddled 32 x
  32). Under bilinear filtering neither declared order fits (filter then decode 0 of 2048 pixels,
  decode then filter 1147 and 876 of 2048, 2 held-out fills). **Each lerp stage floors both
  halves to the larger one's ulp, lerps exactly and rounds to nearest with ties up** (weight
  0 returns the first half unchanged), x then y: fitted on single stages and held out offline on
  three two-stage fills, every pixel, with weights on the 1/64 grid (E982); a later held-out row
  missed it where a stage result is subnormal (E1004), and **a stage result below 2^-14 is
  flushed to +0**: held out offline on an-t0b27's 12 halves that part it, one pixel column
  (E1016), **the y stage's own result included** (E1025: held out on five strided rows, every 1/64
  weight of each stage alone and both together; the threshold between 5.69e-5 and 6.16e-5, the
  smallest normal half [infer]). A trilinear sample's level lerp is not that stage rule (E1025, one
  row). **The level lerp floors both levels' halves to 2^-14 of the larger one's leading bit**
  (a 15-bit grid), lerps exactly by the LOD's fraction in 64ths, floored, rounds to nearest with
  ties up and flushes below 2^-14 (E1038: held out on seven rows, two chains, levels 0 to 2).
  **The second register holds texel bytes 2 and 3**: byte 2 decoded and filtered as bytes 0 and 1
  (low half), byte 3 decoded linearly, b / 255, and filtered by the stage rule (high half) (E1038:
  three held-out bilinear rows; E723's point reads post hoc).
- **ETC1 (format 27; E724).** **Format 27 is ETC1 with the 4 x 4 blocks in Morton order, y in the
  low bit** (6 of 6 held-out fills of random valid blocks exact over 2048 pixels, 8 x 8 to 32 x
  16; raster block order and Morton with x low 0 of 6). Formats 23 to 26 are not decoded.
- **Texture types (E725, E726, E910, E940, E941, E958).** **Types 3 and 1 are read as a raster, the
  window wrapping at the texture's size** (8 of 8 held-out fills exact, 8 x 8 to 32 x 32; E567's
  fixed 16 refuted, 0 of 8; held out again at 64 x 8 and 128 x 8, E910). **Type 1's rows are the
  width apart, type 3's max(8, w) texels**: type 3 at 1, 2 and 4 wide pads a row to 8 texels (5 of
  5 held out at format 12, where a texel is a dword, E940, after E910's one row at 4 x 16; at
  format 5, 16 bits a texel, the low half of a dword first, rows of 8 texels, not 8 dwords: 2 of
  2, E958), type 1 at 1, 2 and 4 wide does not (E910, E940); at 24 and 40 wide the rows of type 3
  and of type 1 are the width apart, not a power of two above it (E940, E958, 2 of 2 each).
  **Type 4 stores 32 x 32 blocks of 1024 dwords, raster inside a block, the blocks row by row**:
  texel (X, Y) is dword ((Y div 32) ceil(w / 32) + (X div 32)) 1024 + (Y mod 32) 32 + (X mod 32)
  (18 of 18 held-out windows of 64 x 64 to 128 x 128 and 256 x 32, E941; read post hoc at
  64 and 128 wide by E910); up to 32 wide that is E725's stride of 32. At widths that are not
  multiples of 32 a block row keeps ceil(w / 32) whole blocks (7 of 7 held-out windows of 48 x
  64, 80 x 64 and 96 x 32, E958; the power of two above the width and a partial block refuted).
  **Type 2 is a cube map: six 16 x 16 faces consecutive at 256 dwords a face, read for
  +x, -x, +y, -y, +z, -z as faces 0 to 5** (each axis direction reads one face over 2048 of 2048
  pixels, E726). **The face is that of the coordinate of largest magnitude, with its sign**: E726's
  post hoc rule held out on two off-axis programs whose dominant axis changes inside the image,
  2048 of 2048 pixels each, all six faces between them (E844). **In a face, (s, t) is the public
  cube-map table** (+x s = -w, t = -v; -x s = +w, t = -v; +y s = +u, t = +w; -y s = +u, t = -w;
  +z s = +u, t = -v; -z s = -u, t = -v; over |ma|, texel floor((q + 1) / 2 * 16), Morton with t
  in bit 0), fitted on E726 and held out on E844's jobs at 4090 of 4096 pixels, the misses exact
  texel boundaries at a |ma| not a power of two (E923); held out on hardware on four new 16 x 16
  programs and at 8 x 8 faces (the rule with 8 for 16, faces 64 dwords apart); 32 x 32 faces read
  the fifth bits of s and t in the other order (post hoc, E930), which is E561's twiddle law, tiles
  of 16 x 16 in raster order with s first (E951), held out at 32 x 32 and 64 x 64 faces, and 4 x 4
  faces sit 16 dwords apart (E955). A face tie reads the higher axis's face on every sweep run (z
  over y over x, E931, E956) but not on 7 of 599 kept tie pixels with a large third coordinate; a
  tie of two bit-identical fmad ramps with x the lower axis reads +x on 58 of 64 columns (E1001,
  three rows of six; constant ties and ties of y and z read the higher axis, 9 of 12 rows), and
  bilinear at a face edge mixes in a texel of the neighbour face near the adjacent one (E931, E956),
  the neighbour face's bilinear at the outer tap centre's direction on -y/+x and not on +z/+x
  (E1002).
  The ties, texel boundaries and face edges: Q284.
  **Type 5 reads one bit per 8 texels**: with format 12 texel t = (Y mod h) w + (X mod w)
  returns `0x0000ffff` iff bit 0 of texture dword floor(t / 8) is set, else 0 (E942: 13 of 13
  held-out rows with stored dwords that part it from bit 1 of dword floor(t / 4), and 8 of 8 rows
  where the two agree; E911's memory rows and size steps, E894's 16-column step, are this rule
  on the map fill). With format 9 one row read bit 0 of 16-bit word floor(t / 8), and format 18
  and the bilinear filter gave the format 12 point images (post hoc, one row each, E942).

*Simulator check, 2026-10-23.* The simulator's texture unit
(`crates/sgx-sim`, `tex.rs`) follows this page and *Texture sampling*; it reproduces every
recorded sampling vector it models and stops on the rest: the LOD values, the bits above, the
recorded formats and modes, tiled textures, and filtered `.pcf` at other weights. After the
11.32 tables it also takes the tile law of E561 on 32-bit texels in the sizes run, non-square
chains in the five sizes run, `smp3d` as `smp2d` where it ran, and the YUV formats as black only
for a job that records the colour-space set as unloaded.

**Undecided:** why type 3 pads to 8 texels and the other 16-bit and 8-bit formats on types 1, 3
and 4 (E958 ran format 5 on type 3), type 5 with other formats, the LOD fraction's residual
(Q280), the border modes on the u axis, formats 23 to 26 and the YUV conversion in a fill,
the sRGB second register under a trilinear sample, the cube
map's edges and (s, t) within a face (Q284), `smp3d`
beyond the textures it ran on, `.sinf`/`.rsd`, and state from `sa` or `c`.

### 8.38 `rlp`

*Measured on the hardware (2026-10-22).* **`rlp d, s, pN` rotates left through the predicate**:
`d = s << 1 | pN`, then `pN` = bit 31 of `s` **[HW]** (probe `rlp`, 32 cases over every
predicate). **Predicate numbers from 4 up alias `p0`-`p3`** (number mod 4: `rlp ..., p4` reads
and writes `p0`) **[HW]** (probe `usse-rlp-high-predicates`).

### 8.39 Cache control `ci`, `cf`, `cfi`

*Measured on the hardware (2026-10-22).* **A load after `ci`, `cf` or `cfi`, on any of the
three level selections, with `.global` or `.dm_nomatch`, returns the pixel's own store**
**[HW]**: none of them drops a store or makes a later load read stale memory, and none
writes a register (probe `cache-control`, every pixel on its own dword).

**Undecided:** what they do to other units' view of memory (the texture cache, the host),
which our probes cannot see.

### 8.40 Video `adif`, `adifsum`, `bilin`, `firv`, `firh`

*Measured on the hardware (2026-10-22).* **`adif d, a, b` = `|a − b|` per byte; `adifsum d,
s0.low|high, a, b` = the sum of the four byte differences plus that 16-bit half of `s0`**, as a
32-bit value; a repeat advances the destination and the sources **[HW]** (probe
`usse-video-ops-adif`).

*Filter probes (2026-10-25).* The three filters, from impulse responses, pedestals and amplitude
sweeps (table `probes/usse/video-filters.toml`, probes `x-*`, every result recorded).
Every formula below fits every recorded case unless it says otherwise. Bytes are numbered
from the least significant; `x.bN` is byte N of `x`.

**Data formats.** `u8`, `s8` and `o8` only change how the data bytes are read: as they are,
as signed bytes, or as the byte minus 0x80. **Every result byte is unsigned, saturated to
0-255** **[HW]**, whatever the format, so a negative result reads 0.

**`bilin d, w, a, b, fmt, planar|interleaved, srcPQ, dstPQ[, rnd]` is a bilinear filter**
**[HW]** (636 cases). With `fx` = (`w.bP` & 7)/8 and `fy` = (`w.bQ` & 7)/8, the weights in
eighths (`src01` takes them from bytes 0-1 of `w`, `src23` from bytes 2-3; the bits above
the low three are ignored):

- `v_k` = `a.bk` + `fy` · (`b.bk` − `a.bk`), each byte of `a` towards the same byte of `b`;
- result byte `j` (0, 1) = `v_j` + `fx` · (`v_n` − `v_j`), `n` = `j` + 1 (`planar`) or
  `j` + 2 (`interleaved`);
- truncated, or rounded half up with `rnd`; written to bytes 0-1 (`dst01`) or 2-3 (`dst23`)
  of `d`, the other two bytes zero.

**`firv d, a, b, c, fmt[, +src2.2][, latch][, scale]` is a two-tap vertical filter, one per
byte column** **[HW]** (750 cases): result byte `k` = `a.bk` · `c.b0` + `b.bk` · `c.b1`, the
two taps signed bytes; `+src2.2` adds `c.b2`, `scale` shifts the sum right by `c.b3`, and
`latch` adds byte `k` of the *firh latch* (below); the order of `latch` and `scale` together
was not measured.

**`firh d, a, b, c, fmt, edge, fcsN, #s, #k` is a horizontal FIR filter along one 12-byte
line** **[HW]** (1711 cases, then every `firh` vector with its job, E292): the line is
`a.b0`-`a.b3`, `b.b0`-`b.b3`, `c.b0`-`c.b3`, the kernel of set `fcsN` is centred on position
`s`, and the result, Σ tap · sample plus a bias, shifted right and saturated, is written to byte
`k`. The sets come from the USE filter block, which the job loads or not (E078): a transfer
command with load flag bit 2 loads `CR_USE_COEFFS_MODE` and three groups of three words, one
per set 0, 1 and 2; a group's first word holds the signed taps at −3..0 (bytes 3..0), its
second +1..+4, its third the shift (bits 3:0) and a signed 16-bit bias (bits 19:4).
`CR_USE_COEFFS_MODE` bits 1:0 pick what sets 2-5 are:

| mode | `fcs0`, `fcs1` | `fcs2` | `fcs3`-`fcs5` | `fcs6`, `fcs7` |
|---|---|---|---|---|
| 0 | the loaded groups 0, 1 | fixed bank 0 | fixed bank 0 | 0 |
| 1, 2 | the loaded groups 0, 1 | fixed bank 1, 2 | fixed bank 1, 2 | not 0, taps open (E298) |
| 3 | the loaded groups 0, 1 | group 2, taps −3, 0 and +3 only | 0 | 0 |

A job that loads nothing runs with mode 0 and every group zero, whatever the job before it
loaded (`usse-filter-sets` load0 cases after loaded ones). The fixed banks, in 128ths, shift 7
(bank 0 E079; banks 1 and 2 E079, E080, E293):

| bank / set | taps from `s` − | taps | bias |
|---|---|---|---|
| 0 / `fcs2` | 2 | [4 −20 80 80 −20 4]: [1 −5 20 20 −5 1]/32, H.264 | 64-79 |
| 0 / `fcs3` | 1 | [32 64 32]: [1 2 1]/4 | 64-95 |
| 0 / `fcs4` | 3 | [−4 12 −24 80 80 −24 12 −4] | 48-63 |
| 0 / `fcs5` | 2 | [1 −5 20 20 −5 1], no shift | 0 |
| 1 / `fcs2`, `fcs3` | 1 | about [−8 72 72 −8]: [−1 9 9 −1]/16 | |
| 1 / `fcs4` | 1 | about [−9 106 36 −5] | |
| 1 / `fcs5` | 1 | about [−6 105 37 −7] | |
| 2 / `fcs2` | 1 | about [16 −64 64 −16]: [1 −4 4 −1]/8 | |
| 2 / `fcs3` | 2 | about [128 −256 64 64]: [1 −2 ½ ½] | |
| 2 / `fcs4` | 2 | about [16 32 32 32 16]: [1 2 2 2 1]/8 | |
| 2 / `fcs5` | 2 | about [32 32 32 32]: [1 1 1 1]/4 | |

The bias column of bank 0 is the range that fits every case; `fcs4`'s is below a half
**[HW]**, so it does not simply round. Banks 1 and 2 are known to a fitted family
**[infer]**: every tap vector within 5 per tap of E079's changes times 4 (E293's taps for bank
2's `fcs2` and `fcs3`), with its own bias range, that fits all their cases (`usse-filter-banks`,
`usse-filter-control`, `usse-filter-bank2`; `tools/usse-asm/firh_banks.py`). The simulator gives
a result only where the whole family agrees, and counts it as fitted, not as a hardware check:
the families come from the same vectors (E292).

Positions off the line follow `edge`: `rep` repeats the end sample, `msc` mirrors without
repeating it (−1 reads 1, 12 reads 10), `mdc` mirrors with it (−1 reads 0, 12 reads 11), up to
position 18; **from position 19 every mode reads 0** **[HW]** (a loaded identity filter on a ramp
line, every centre, E298). **The centre is −4 to 27**: the field's values written `#−16` to
`#−5` are centres 16 to 27 **[HW]**, which gives every case below `#−4`: all three `fcs3` taps at
`#−16` and `#−15` (centres 16, 17), 96/128 at `#−14`, 32/128 at `#−13`, nothing from `#−12`
(probes `x-c9-*`, `x-c10-*`; 1126 vectors). `r4`-`r8` are never read.

**The firh latch.** `firh` writes all four bytes of `d`: byte `k` is its result, the other
three come from a hidden 32-bit latch that every `firh` updates at byte `k` **[HW]**. So four
`firh` with `#k` 0-3 build a whole word, each destination getting the bytes merged so far
(0x11, 0x2211, 0x332211, 0x44332211); `firv`'s `latch` reads it; `firv` and `bilin` never write
it. **The latch belongs to an instance slot, not to a pixel** **[HW]**: a fill where every pixel
writes its own number reads back 32 values, those of the last pixels each slot ran, and a slot
carries the latch from one pixel to the next and from one task, and one client, to the next,
as `i0`-`i2` do (*Internal registers*). At power-up it holds garbage: the first run gave every
pixel 0x00 or 0xff bytes until `firh` probes with `#k` 1-3 had written them. With two to five
instructions between `firh`s, a destination can catch a later `firh`'s byte, which fits a latch
shared by instances interleaved on one slot **[infer]** (probe
`usse-video-filters-c11-latch-merge`). A program
that relies on the latch should write all four bytes first. The bytes a task did not write
read what the slot's last task left (for example 0xffffff, 0, 0x5a5a5a or 0x80803e in the
runs): the simulator checks the byte `firh` wrote and takes the others as any value, and stops
on a byte the task wrote but it could not compute (E292).

**Undecided:** `fcs6` and `fcs7` under banks 1 and 2; the exact taps of banks 1 and 2 within
their families, and whether the families hold on lines outside the fit; the timing of the latch
under interleaving.

### 8.41 Encoding bits no field maps

*Measured on the hardware (2026-11-02; `probes/usse/encoding-bits*.toml` and
`encoding-gaps.toml`, written by `tools/usse-asm/usse_bits.py`, recorded runs).* The 219 forms
leave 2,161 bits neither identifying nor in a field. Each probe runs one form's base instruction
as a raw word in a fill's pixel program (`dump.s`) and flips one such bit per case; a bit is read
if the readback differs from the base's, or the job fails **[HW]**. 761 bits of 73 forms ran:

- **Read: 4 bits.** `idiv`'s enc[47] changes every destination from r10 to r17, not only the
  quotient and the remainder (E295): it is the high bit of `idiv`'s repeat count, now a field
  (E367). enc[51] on `setfc` and on `imo` (the
  bit that selects the register forms of `smoa`, `smr`, `smlsi` and `smbo`) and enc[44] on
  `depthf` hang the job (E296).
- **Ignored: the other 757.** The moves, the bitwise group, integer multiply-add, `fsubflr`,
  `frcp`, the dot products and `fdsx` (f32 and f16 sources), `sop2wm`, the colour and integer
  dot products, `rlp` (with `p0` set first), `movc`, `movmsk`, the masked tests, `adif`,
  `adifsum`, `bilin`, `firv`, `firh`, `idiv`'s other 18, eleven dual-issue pairs, both `ldr`
  forms (E295); `nop`, `setfc`, `moest`, `setm`, `imo`, the immediate `smoa`, `smr`, `smbo`
  and `smlsi`, `pcoeff`, `depthf` and `atst8` (E296), each but the bits above.

The other 1,400 unmapped bits belong to forms with no base yet: the register forms of the MOE
group, `wop`, `lock`, `phas`, the emits, `str`, `ba`, `br`, `bexception`, `lapc`, the `pclink`
moves, the other dual-issue pairs and the forms whose words an earlier form decodes first.

**Words no form decodes.** About 4 percent of random words match no form's mask and value, all
of classes 2, 22, 26 and 31; the decoder rejects about a quarter, counting words that match a
mask but hold a reserved field value. Three words of each class that the decoder rejects ran in
place of an instruction: none hung or faulted; class 31's changed nothing, but three of class 2,
one of class 26 and one of class 22 (bilin's word with format 3, a reserved value rather than a
gap) left the program's later stores unwritten, and two of class 22 changed some pixels (E297,
Q080). The five that lost the stores are those of classes 2, 22 and 26 with enc[50] set, the
`.end` bit of mov, nop, fmad and bilin. Run again with a marker moved to the pixel after the
word, each of the nine words of classes 2, 22 and 26 with enc[50] set lost the stores and the
pixel's own write, the pixel keeping what the job before left, and each with it clear kept them,
or hung the job (three cases): with enc[50] set the program ends at the word. Of the other bits,
flipped one at a time on three of the words, none changes that; flips of bits 51 to 58 of a
class 2 and a class 26 word, and of bits 32, 33 and 51 of a class 22 word, change which pixels
the word writes **[HW]** (E368). The simulator stops on a word no form decodes, and on a word
with one of the three read bits that remain set.

### 8.42 `.tpres`, `.partial`, `.nosched`, `.syncs`

*Measured on the hardware (2026-10-22).* In a fill, **`.tpres` (`frcp`, `frsq`, `fsqrt`),
`.partial` (`and`, `or`) and `.nosched` change nothing a pixel sees, while `.syncs` (on `mov`
and `fmad`) hangs the task**, which the driver recovers from with `-ETIMEDOUT` **[HW]** (probe
`usse-flags-other`). `.syncs` may wait for something a fill
never provides **[infer]**; what is **[open]**.

## 9. Open questions

Beyond the undecided parts of the hardware probe results, by how much they would matter to an
open driver:

1. **The behaviour of the groups no program of ours has run**: the visibility group. Of the
   probed groups, the LOD of a quad's own derivatives (Q280; the gradient footprint is E721) of
   `smp`, the border address modes on the u axis (E565), the compressed and YUV
   formats (E568), `fdpc`'s clip-plane result (likely a vertex-task output), and
   of the video filters `firh`'s sets 6 and 7 under fixed banks 1 and 2 and the exact taps of
   those banks within their families remain; how the coefficient sets are loaded, what the
   centres below `#−4` and the positions past the line read are settled (E292, E293, E298)
   (Q050).
2. **The MOE state as a whole**: what `smoa`, `smbo`, `smr`, `imo` and `setfc` set beyond the
   offsets, modes and increments pinned, and what `moest` returns: it writes nothing a fill
   reads. The state does not outlive the job that sets it, and the sequences that faulted did
   so through the stores after them, whose address register the offsets and the mirror mode
   moved (E369, E370) (Q051).
3. **`.syncs`** and the other scheduling flags beyond `.nosched`: a read 0 to 8 instructions after a
   `mov`, `or`, `fmad`, `frcp` or `fexp` sees its result with or without `.nosched` (E371); a load
   read by a `stad` after up to 32 `nop`s still holds the register's old value with no `wdf` (E478;
   by an ALU instruction after up to 48, E517); a dependent reader of an `ima32` result sees it
   after 0, 1, 2, 3, 4, 5, 6 and 8 `nop`s with or without `.nosched` on the writer (E495); `.syncs`
   hangs a fill's task (Q052).
4. **The global bank**: what `g18` and `g21` hold in a vertex task (they follow the task, 0xe to
   0x16 and 0x1a to 0x1f by the vertices a task holds, with no rule found, E571) and what the
   end-of-tile task of each tile reads in `g18` and `g21` (with E130's register-offset store to a
   slot of its own, 5 of 5 jobs completed and 32 tiles held `g19` 0x1a, `g25` 3, `g23` 1 or 0x11,
   `g24` 1 or 9, `g17` 0 to 3, `g18` and `g21` changing from tile to tile, E708; E572's store fault
   was not reproduced by its own program, E707; Q183). The others are read. In a vertex task
   `g16`, `g19` (through `mov`), `g26`-`g31` and `g40` read 0, `g20` 1, `g42` 1.0, `g41` 0xf and
   `g43` 0xdf000000 (0x3 and 0x20000000 in a last task of 2 vertices), and `g17`, `g22`-`g25`
   and `g39` follow the vertex's task and lane (E571); in the end-of-tile task of the last tile
   they read as in a pixel task (E572); in a triangle's pixel task as in a fill (E374, E808), and
   `g19` reads 0 through `mov`, 0x11 through the bitwise group and 0x1a as a store's source (E372)
   (Q053).
5. **Emits**: `.tasks`/`.taske` and `#incp` beyond the vertex emits (incp 1 to 3 on either
   changes nothing a triangle shows; `.cut` on `emitmtevtx` hangs the job, E376), `.twopart`
   on the state emits (needed on `emitvcbvtx`, E102; shows nothing on the state emits, E106);
   the PBE sideband bits beyond the pack mode and bit 9, `TILERELATIVE` (bits 11 and 12: Q046;
   Q074 asks what bit 9 does); `emitpds` runs the PDS program it names from a client fill but
   ends the job in a fault or hang, 63 of 63 (E488, E520, Q128).
6. **`idf` modes** other than `bif` (each hangs a fill's job at its `wdf`, E375), `lock`/
   `release`, `setm`, and the cache-control operands (Q055).
7. **Instruction timing**: what a result costs in cycles; a fill's instructions cost 0.320 µs
   per 2048 instances, 16.03 instances a 399 MHz cycle (E377) (Q002, Q052).
8. **Encoding bits**: of the 2,161 bits no field maps, 761 were flipped on the hardware; three
   are read, enc[51] on `setfc` and `imo` and enc[44] on `depthf`, which hang the job (E296),
   and `idiv`'s enc[47] is its repeat count's high bit (E367). Words of classes 2, 22 and 26
   that no form decodes end the program when enc[50] is set (E368); what the others do to
   registers is open (Q080).
9. **Calls, the program counter, the integer forms and the tests**: `p0`-`p3` and `pclink` at the
   start of a firmware task after a perturbation or a cold boot (Q158; at the next entry they are
   what the task left, E809, E810); what leaves
   0xeb3 and 0x98 in them across jobs (Q125: four runs of the readers show 64 pixels of 0xeb3 in 29
   of 40 jobs and quads that repeat in part, E500); `ima32`'s dual-issue form, `cie`, `.neg` and
   immediates with
   the extra operand, its selector 3 and what bit 46 does, and `imae`'s repeats, `u16`/`z16`
   sources and `.rsN` shifts with the carries, with the operand values and immediates not run
   (Q127); why a write to `pa0` is lost (Q098).
10. **Fences, repeats, registers and persistence for a firmware compiler**: why a `wdf` waits for
   another counter's loads in some runs and not in others (Q130); whether a firmware (EDM) task runs
   two at once (no second pass was seen in 12 of 12 holds of up to 90 ticks, E749, E751, and an
   event that arrives meanwhile is queued, up to four ticks and a kick or a job's events once, E751,
   E752; a `wdf` with
   nothing outstanding and an unfenced store at the end of a task act as in a fill, E534); what a
   client `str` changes (Q134; `str` then `ldr` of 0x0814 and 0x0a78 is ordered in a firmware task,
   E534, and its other registers and the register-index forms are Q154); when another reader sees
   an unfenced store and what an `idf` is needed for beyond an instance's own store (Q143), and when
   a load not waited for lands (Q146); why a client `emitpds` faults the job and why its addend
   0xFFF to 0x2000 leaves the fill's value (Q128); why 4 pixels of an `sa` writer show the `sa`
   and the rule placing them (Q129); where a write past the allocation goes (Q132); what bounds a
   `phas` request
   and what a request above 256 allocates, which is [infer] at least 124 for 260 to 376, T = 101 to
   123 not run (Q133). What survives from one firmware task to the next beyond one writer's
   `sa`, `r`, `i` and p (E809, E810; Q158), whether a task that ends a skipped slot 3 pass and
   clears the 3D lockup check's arm keeps the tick (the check is E855 to E857) and the allocation
   of a firmware task above TRC 31 are not measured.

The simulator (`crates/sgx-sim`) reproduces 30846 probe vectors (15526 of them with near values:
float functions within their measured bound) and 493 pixel vectors; it stops on 2174 rather than
guess, most often because (vectors, from `doc/isa/sim-coverage.json`):

- firh's fixed bank 1 or 2, whose taps are fitted to these vectors (in-sample, not a hardware check)
  (1112)
- bytes of the firh latch the task did not write (read in rN) (285)
- rN is past the task's N temporaries (66)
- smoa takes dst to r-N (not modelled) (64)
- no SGX registers on this bus (59)
- gN (per-instance values, not modelled) (48)
- reads saN before the program writes it (36)
- reads R(N) before its DRC result lands (wdf) (35)
- reads paN before the program writes it (35)
- four texels fix no decoder (30)
- the firh latch, which a later firh may reach first (read in rN) (24)
- a LOD from the quad's derivatives (23)
