<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### Program counter, calls and the end of a program

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
