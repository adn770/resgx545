<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
## Open questions

Beyond the undecided parts of the hardware probe results, by how much they would matter to an
open driver:

1. **The behaviour of the groups no program of ours has run**: the visibility group. Of the
   probed groups, mipmaps and the LOD values of `smp`, the border address modes and the
   compressed and YUV formats, `fdpc`'s clip-plane result (likely a vertex-task output), and
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
   a read by an ALU instruction was not run); a dependent reader of an `ima32` result sees it after
   0, 1, 2, 3, 4, 5, 6 and 8 `nop`s with or without `.nosched` on the writer (E495); `.syncs` hangs
   a fill's task (Q052).
4. **The global bank**: what `g18`-`g20` and `g39`-`g43` hold in a vertex task and the
   end-of-tile task; in a triangle's pixel task they read as in a fill (E374), and `g19` reads
   0 through `mov`, 0x11 through the bitwise group and 0x1a as a store's source (E372) (Q053).
5. **Emits**: `.tasks`/`.taske` and `#incp` beyond the vertex emits (incp 1 to 3 on either
   changes nothing a triangle shows; `.cut` on `emitmtevtx` hangs the job, E376), `.twopart`
   on the state emits (needed on `emitvcbvtx`, E102; shows nothing on the state emits, E106);
   the PBE sideband bits beyond the pack mode and bit 9, `TILERELATIVE` (Q054; Q074 asks what
   bit 9 does); `emitpds` runs the PDS program it names from a client fill but ends the job in a
   fault or hang, 24 of 24 (E488, Q128).
6. **`idf` modes** other than `bif` (each hangs a fill's job at its `wdf`, E375), `lock`/
   `release`, `setm`, and the cache-control operands (Q055).
7. **Instruction timing**: what a result costs in cycles; a fill's instructions cost 0.320 µs
   per 2048 instances, 16.03 instances a 399 MHz cycle (E377) (Q002, Q052).
8. **Encoding bits**: of the 2,161 bits no field maps, 761 were flipped on the hardware; three
   are read, enc[51] on `setfc` and `imo` and enc[44] on `depthf`, which hang the job (E296),
   and `idiv`'s enc[47] is its repeat count's high bit (E367). Words of classes 2, 22 and 26
   that no form decodes end the program when enc[50] is set (E368); what the others do to
   registers is open (Q080).
9. **Calls, the program counter, the integer forms and the tests**: indices of 256 to 8191 in a fill
   and a jump across a 65536-word step of the code base (Q123; the step of 0x80000 is shown by ten
   placements: E492); `p0`-`p3` and `pclink` at the start of a firmware task, which no program of
   ours has run (Q124); what leaves 0xeb3 and 0x98 in them across jobs (Q125: four runs of the
   readers show 64 pixels of 0xeb3 in 29 of 40 jobs and quads that repeat in part, E500); how
   `iaddu32` extends a source 1 above 0x7fff, which no test tells (Q126); `ima32`'s dual-issue form,
   `.s` and `cie` with the extra operand, its selector 3 and what bit 46 does (Q135), and `imae`'s
   repeats, `u16`/`z16` sources and `.rsN` shifts with the carries, with the operand values and
   immediates not run (Q127); the rule of the test field on the shifts, the chan fields and the
   other classes (Q137); how long an `sa0` written by `ima32` lasts and why a write to `pa0` is lost
   (Q136).
10. **Fences, repeats, registers and persistence for a firmware compiler**: why a `wdf` waits
   for another counter's loads in some runs and not in others (Q130); whether a firmware (EDM)
   task behaves as a fill for `wdf`, unfenced stores and two tasks at once (Q131, firmware);
   what a client `str` changes and whether `str` then `ldr` is ordered (Q134); why a client
   `emitpds` faults the job (Q128); the 12 pixels of an `sa` writer that show the `sa` (Q129);
   where a write past the allocation goes (Q132); what bounds a `phas` request at 192 (Q133).
   The overlap of two firmware tasks and `str` then `ldr` are not answered (Q131, Q134).

<!-- @simopen 12 -->
