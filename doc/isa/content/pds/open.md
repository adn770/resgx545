<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
## Open questions

1. **The ports** `doutc`, `douts`, `slc`, `mr` and `ir0` as destinations, and `movsa` on ports
   other than `doutd`: what they do (*Hardware probes* lists what was seen). `tim` loads the
   counter the ALU reads, `EVENT_TIMER` (its first word, bits 24-0, bit 24 the run bit;
   settled 2026-10-24); why an enabled small count hangs the job is open.
2. **`if0`/`if1`** in a primary program (Rogue's reading: last/first in task, end of tile/end
   of render; *Input and special registers*). *(`adc`/`sbc` setting the flags: settled
   2026-10-24, they do.)*
3. **`load`/`store`**: why stores totalling 2-4 dwords fault, and why `rwfence` after a store
   (or after a faulted job) touches page 0 (their timing and the fences: E143; which
   programs fault: E144).
4. **`mr01`/`mr23`**, and what `ir1` holds outside a fill (where it reads 0); whether the
   `mov16`/`mov32` selector `ir1` (`ir1.0`, 0 in a fill) is the ALU's `ir1`. *(settled
   2026-10-25: the numbering, selector and bit 9; selector 2 is the fetch pc; `ir0` in a
   fill is the tile position; 8.9, 8.11.)*
5. *(settled 2026-10-24: the ALU details, `mov128` and `swap`.)*
6. *(settled 2026-10-24: one return register.)*
7. **The `doutu` word** on this build: whether `EXE` really stops at bit 19 (so that `CBASE`
   exists) or the 18 PC bits reach bit 21; our programs keep code low enough for both
   readings to agree (`doc/specs/transfer.md` §4.2).

8. **Semantics stated only by name**: `nop` (the fences: E142, E143).
9. **The specials in a `movs`**, mostly settled 2026-10-24: `.l` passes a whole word and
   `ir0.l` is all of `ir0` (*Hardware probes*); in the microkernel's event program `ir1.l`
   reads what the ALU reads as `ir1`, since its fast paths depend on it, and `tim.l` goes to a
   word the firmware never reads In our pixel-event
   program `ir1.l` reads what the ALU's `ir1` does, the event bits, and `.h` reads 0 for
   `ir0`, `ir1` and `tim` (*Hardware probes*, 2026-10-27). Still open: whether `.h` reads 0 in
   every task, and the per-tile inputs of a multi-tile render.
10. *(settled 2026-10-24: the flags and the carry after every instruction.)*
11. *(settled 2026-10-24: a `mov16` into a read-only row keeps its temporary's other half.)*
12. **Bit 9 of the `mov16`/`mov32` specials (`.1`)** on the rest of the family: on SGX545 it
    only makes `mov16` read 0 (8.11). The other pipe's registers (SGX545 alone has two PDS
    pipes), another core's, or 64-bit specials are the readings left **[infer]**. A one-pipe
    core (SGX540 on a PandaBoard, SGX530 on an N950) shows whether its special fields run at
    stride 1, the bit then new with the second pipe; an MP part (SGX544MP2) tests the cores.
13. **The fetch pc's offset**: why `pc.0` reads the index plus 1 or 2, not 3, at some places
    (8.11); a model of the PDS fetch would say.
