<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### `abs` and `not`

*Measured on the hardware (2026-10-24).* `not` is the bitwise complement from both source forms
(`pds-alu-abs-not`) **[HW]**. `abs` is the identity in the default unsigned mode (`pds-alu-abs-not`:
`abs(-5)` is `-5`), and the two's complement absolute value under `alum signed`, with
`abs(0x80000000)` itself (`pds-alu-abs-signed`), from both source forms **[HW]**.
