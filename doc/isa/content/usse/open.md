<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
## Open questions

Beyond the undecided parts of the hardware probe results, by how much they would matter to an
open driver:

1. **The behaviour of the groups no program of ours has run**: the visibility group. Of the
   probed groups, mipmaps and the LOD values of `smp`, the border address modes and the
   compressed and YUV formats, `fdpc`'s clip-plane result (likely a vertex-task output), and
   of the video filters `firh` below `#−4`, its rounding biases and how its coefficient sets
   are loaded remain (Q050).
2. **The MOE state as a whole**: `smoa`, `smbo`, `smr`, `imo`, `setfc` and what `moest`
   returns, beyond the `smlsi` increments the probes pinned (Q051).
3. **`.skipinv`, `.syncs`, `.nosched`** and the other scheduling flags: what changes when they
   are set or clear (performance only, or correctness); `.syncs` hangs a fill's task (Q052).
4. **The global bank**: what `g18`-`g20` and `g39`-`g43` hold outside a fill (the constant
   bank, E085, the tile, quad and task registers and that `mov` cannot write `g`, E086, are
   settled) (Q053).
5. **Emits**: `#incp`, `.cut`, `.tasks`/`.taske` and `.twopart` on the state emits (needed
   on `emitvcbvtx`, E102; shows nothing on the state emits, E106); the PBE
   sideband bits beyond the pack mode and bit 9, `TILERELATIVE` (Q054; Q074 asks what bit 9
   does).
6. **`idf` modes** other than `bif`, `lock`/`release`, `setm`, and the cache-control operands
   (Q055).
7. **Instruction timing and hazards**: how many instructions a result takes to be readable,
   whether the hardware interlocks, and what `.nosched` has to do with it (Q052).
8. **The destination bank 6 value 0** (`i.`) (Q056).

<!-- @simopen 12 -->
