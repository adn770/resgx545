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
3. **`.syncs`** and the other scheduling flags beyond `.nosched`: a read 0 to 8 instructions
   after a `mov`, `or`, `fmad`, `frcp` or `fexp` sees its result with or without `.nosched`
   (E371); `.syncs` hangs a fill's task (Q052).
4. **The global bank**: what `g18`-`g20` and `g39`-`g43` hold in a vertex task and the
   end-of-tile task; in a triangle's pixel task they read as in a fill (E374), and `g19` reads
   0 through `mov`, 0x11 through the bitwise group and 0x1a as a store's source (E372) (Q053).
5. **Emits**: `.tasks`/`.taske` and `#incp` beyond the vertex emits (incp 1 to 3 on either
   changes nothing a triangle shows; `.cut` on `emitmtevtx` hangs the job, E376), `.twopart`
   on the state emits (needed on `emitvcbvtx`, E102; shows nothing on the state emits, E106);
   the PBE sideband bits beyond the pack mode and bit 9, `TILERELATIVE` (Q054; Q074 asks what
   bit 9 does).
6. **`idf` modes** other than `bif` (each hangs a fill's job at its `wdf`, E375), `lock`/
   `release`, `setm`, and the cache-control operands (Q055).
7. **Instruction timing**: what a result costs in cycles; a fill's instructions cost 0.320 µs
   per 2048 instances, 16.03 instances a 399 MHz cycle (E377) (Q002, Q052).
8. **Encoding bits**: of the 2,161 bits no field maps, 761 were flipped on the hardware; three
   are read, enc[51] on `setfc` and `imo` and enc[44] on `depthf`, which hang the job (E296),
   and `idiv`'s enc[47] is its repeat count's high bit (E367). Words of classes 2, 22 and 26
   that no form decodes end the program when enc[50] is set (E368); what the others do to
   registers is open (Q080).

<!-- @simopen 12 -->
