<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### Shift amounts and the `shr` fill

*Measured on the hardware (2026-10-24).* The amount is the seven-bit field taken unsigned: 0-31
shift, 32-127 (which includes what the assembler writes for a negative amount) give 0; `shr` is
logical (`pds-alu-shifts`), and arithmetic under `alum signed` (`pds-alu-alum-shr`) **[HW]**, where
32-127
fill the result with the sign bit (`pds-alu-ashr-big`) **[HW]**.
