<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### Flow control: `bra`, `call`, `rtn`, `halt`, `nop`

Opcodes 18-22 **[RE]**: `bra` and `call` take a 19-bit target, `rtn` and `halt` none, `nop`
has no predicate.

- **`bra`** jumps to an instruction index counted from the first instruction after the data
  segment **[RE/CAP]**: the captured programs' control flow only makes sense that way, and our
  pixel-event program, assembled with labels on that basis, works **[HW]**.
- **`halt`** ends the program **[HW]**: every program of ours ends with it.
- **`call`** and **`rtn`**: one return register, not a stack: a nested call's return loops
  **[HW]**. Neither is used by our programs.
- **`nop`** does nothing **[infer]**.

<!-- @prog pds_pixevent.s match='bra|halt' -->

<!-- @group pds pat='(bra|call) |rtn$|halt$|^nop$' -->
