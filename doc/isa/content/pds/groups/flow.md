<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### Flow control: `bra`, `call`, `rtn`, `halt`, `nop`

Opcodes 18-22 **[RE]**: `bra` and `call` take a 24-bit target (bits 23:0: a target with any
of bits 19-23 set sent the fetch 2 MiB and more past the program, where the job faulted, E260)
**[HW]**, `rtn` and `halt` none, `nop` has no predicate.

- **`bra`** jumps to an instruction index counted from the first instruction after the data
  segment **[RE/CAP]**: the captured programs' control flow only makes sense that way, and our
  pixel-event program, assembled with labels on that basis, works **[HW]**.
- **`halt`** ends the program **[HW]**: every program of ours ends with it.
- **`call`** and **`rtn`**: one return register, not a stack: a nested call's return loops
  **[HW]**. Neither is used by our programs.
- **`nop`** takes one instruction slot and does nothing else: the fetch pc reads one more after
  each (E261), and none of its 27 other bits changed a result (E260) **[HW]**.

<!-- @prog pds_pixevent.s match='bra|halt' -->

<!-- @group pds pat='(bra|call) |rtn$|halt$|^nop$' -->
