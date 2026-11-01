<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### `abs`, `not`

Opcodes 13 and 27 **[RE]**: one source, either `ds1[n]` (`w[8]` set) or a first source (`ds0`,
then `ir0`, `ir1`, and for `not` also `tim`).

- **Semantics [HW].** `not` is the bitwise complement (our pixel-event program also tests
  "bit 8 clear" as `not` then `and` then `tstz`). `abs` is the identity unless `alum signed`,
  then the two's complement absolute value, with `abs(0x80000000)` itself. The `ds1[n]` forms
  of both take `n` from bits 15:10, `ds1[0..63]`: `abs`'s bit 15, once unmapped, reads
  `ds1[n + 32]` (E259, E261) **[HW]**.

<!-- @prog pds_pixevent.s match='^\s+not ' -->

<!-- @group pds pat='(abs|not) ' -->
