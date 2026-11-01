<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### `aluz`, `alun`, `tstn` and predicated tests

*Measured on the hardware (2026-10-24).* `add`, `sub`, `adc`, `sbc` and `mul` set the flags from
their result; `and`, `xor`, `shl`, `not`, `mov32` and `tstz` (`pds-alu-flags`), and `or`, `nor`,
`nand`,
`shr`, `abs`, `mov16` and `tstn` (`pds-after-*`, in both `alum` modes), and `mov64`, `mov128`,
`alum` and a `movs` (`pds-flags-*`) leave them **[HW]**. `aluz` is a zero result. `alun` is a
negative result, but only under `alum signed`: in the default unsigned mode it never tests true,
even after a result with bit 31 set (`pds-alu-flags`, `pds-alu-flags-signed`) **[HW]**. `tstn` sets
its
predicate from bit 31, and a predicated test obeys its predicate (`pds-alu-tst`) **[HW]**. In a
fill's
secondary program neither `if0` nor `if1` tests true (`pds-alu-if`, recorded) **[HW]**; what they
mean
in a primary program, whose results `douta` cannot pass on, is still open.
