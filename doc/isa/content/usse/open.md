<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
## Open questions

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
   of 40 jobs and quads that repeat in part, E500); which extension the test of `iaddu32` reads for
   a source 1 above 0x7fff, which no test tells (Q126); `ima32`'s dual-issue form, `cie`, `.neg` and immediates with
   the extra operand, its selector 3 and what bit 46 does, and `imae`'s repeats, `u16`/`z16`
   sources and `.rsN` shifts with the carries, with the operand values and immediates not run
   (Q127); how long an `sa0` written by `ima32` lasts (Q136) and why a write to `pa0` is lost
   (Q098).
10. **Fences, repeats, registers and persistence for a firmware compiler**: why a `wdf` waits for
   another counter's loads in some runs and not in others (Q130); whether a firmware (EDM) task runs
   two at once (no second pass was seen in 12 of 12 holds of up to 90 ticks, E749, E751, and an
   event that arrives meanwhile is queued, up to four ticks and a kick or a job's events once, E751,
   E752; a `wdf` with
   nothing outstanding and an unfenced store at the end of a task act as in a fill, E534); what a
   client `str` changes and what an `idf` is needed for beyond an instance's own store (Q134; `str`
   then `ldr` of 0x0814 and 0x0a78 is ordered in a firmware task, E534, and its other registers and
   the register-index forms are Q154); when another reader sees an unfenced store and when a load
   not waited for lands (Q143, Q146); why a client `emitpds` faults the job and why its addend 0xFFF
   to 0x2000 leaves the fill's value (Q128); the 12 pixels of an `sa` writer that show the
   `sa` (Q129); where a write past the allocation goes (Q132); what bounds a `phas` request
   and what a request above 256 allocates, which is [infer] at least 124 for 260 to 376, T = 101 to
   123 not run (Q133). What survives from one firmware task to the next beyond one writer's
   `sa`, `r`, `i` and p (E809, E810; Q158), whether a task that ends a skipped slot 3 pass and
   clears the 3D lockup check's arm keeps the tick (the check is E855 to E857) and the allocation
   of a firmware task above TRC 31 are not measured.

<!-- @simopen 12 -->
