<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
## Open questions

1. **The ports** `doutc`, `douts`, `slc`, `mr` and `ir0` as destinations, and `movsa` on ports other
   than `doutd`: what they do (*Hardware probes* lists what was seen). `tim` loads the counter the
   ALU reads, `EVENT_TIMER` (its first word, bits 24-0, bit 24 the run bit; settled); whether and
   why an enabled small count hangs the job, seen only in runs by hand with no record, is open
   (Q057). In a primary pixel program `doutc` faults the job and `mr`, `slc`, `douts` and `ir0`
   change nothing seen (E264); `mr01`/`mr23` read 0 after a `movs mr`.
2. **`if0`/`if1`** in pixel programs: neither tests true in any pixel of the primary pixel
   program nor on any tile of the pixel-event program (E262, E263), so Rogue's pixel readings
   (end of tile, end of render) do not hold there; whether anything sets them outside a vertex
   program is open (Q058). *(`adc`/`sbc` setting the flags: settled, they do.)*
3. **`load`/`store`**: why stores totalling 2-4 dwords fault, and why `rwfence` after a store
   (or after a faulted job) touches page 0 (their timing and the fences: E143; which
   programs fault: E144) (Q059).
4. **`mr01`/`mr23`** read 0 in a fill, the primary pixel and the pixel-event programs; `ir1` reads 0
   in the primary pixel program and the event bits in the pixel-event program by every path,
   `mov32`'s `ir1.0` included; a test's source 65 tests zero exactly where `ir0` is 0, so that it
   reads `ir0` **[infer]** (E262, E263; `tstn` of it unmeasured). Open: the vertex-side programs
   (Q060). *(settled: the numbering, selector and bit 9; selector 2 is the fetch pc; `ir0` in a fill
   is the tile position; 8.9, 8.11.)*
5. *(settled: the ALU details, `mov128` and `swap`.)*
6. *(settled: one return register.)*
7. **The `doutu` word** on this build: whether `EXE` really stops at bit 19 (so that `CBASE`
   exists) or the 18 PC bits reach bit 21; our programs keep code low enough for both
   readings to agree (`doc/specs/transfer.md` §4.2; Q061).

8. *(settled: `nop` takes one slot and reads none of its other bits, E260, E261.)*
9. **The specials in a `movs`**, mostly settled: `.l` passes a whole word and `ir0.l` is all of
   `ir0` (*Hardware probes*); in the microkernel's event program `ir1.l` reads what the ALU reads as
   `ir1`, since its fast paths depend on it, and `tim.l` goes to a word the firmware never reads. In
   our pixel-event program `ir1.l` reads what the ALU's `ir1` does, the event bits, and `.h` reads 0
   for `ir0`, `ir1` and `tim` (*Hardware probes*), on every tile of a 128x128 render too, `ir2.l` 0
   there and `ir2.h` 0 on a one-tile render (E263). Still open: `.h` in the vertex-side programs
   (Q060).
10. *(settled: the flags and the carry after every instruction.)*
11. *(settled: a `mov16` into a read-only row keeps its temporary's other half.)*
12. **Bit 9 of the `mov16`/`mov32` specials (`.1`)** on the rest of the family: on SGX545 it
    only makes `mov16` read 0 (8.11). The other pipe's registers (SGX545 alone has two PDS
    pipes), another core's, or 64-bit specials are the readings left **[infer]**. A one-pipe
    core (SGX540 on a PandaBoard, SGX530 on an N950) shows whether its special fields run at
    stride 1, the bit then new with the second pipe; an MP part (SGX544MP2) tests the cores
    (Q063).
13. **The fetch pc's offset**: `pc.0` reads the index plus 3, or 1 or 2 below it (E261). Back
    to back the lag sits at instructions 26-27 in ten of twelve runs whatever the `nop`s before,
    dwords 62-63 after the 36-dword data segment, the last two before a 64-dword boundary;
    some runs lag elsewhere **[infer]**. What sets it, a model of the PDS fetch, is open (Q062).
14. **`mov128`'s bit 15** makes it write the data's row 4 `ds0` pair to both halves of its
    destination whatever its source row (E261); why row 4 (Q077).
