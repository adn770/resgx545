<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### `abs`, `not`

Opcodes 13 and 27 **[RE]**: one source, either `ds1[n]` (`w[8]` set) or a first source (`ds0`,
then `ir0`, `ir1`, and for `not` also `tim`).

- **Semantics [HW].** `not` is the bitwise complement (our pixel-event program also tests
  "bit 8 clear" as `not` then `and` then `tstz`). `abs` is the identity unless `alum signed`,
  then the two's complement absolute value, with `abs(0x80000000)` itself. The `ds1[n]` form
  reaches `ds1[0..31]` only.

<!-- @prog pds_pixevent.s match='^\s+not ' -->

<!-- @group pds pat='(abs|not) ' -->
