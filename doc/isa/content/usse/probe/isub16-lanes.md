<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### `isub16`/`usub16` lanes

*Measured on the hardware (2026-10-22).* **`isub16` and `usub16` subtract both 16-bit lanes**, each
wrapping, with **no saturation** **[HW]**: `0x12340005 - #1` is `0x12330004` (an immediate is
subtracted from both lanes), `0 - #1` is `0xffffffff`, `0x00050007 - 0x00010002` is `0x00040005`,
and `usub16 0 - #1` is `0xffffffff`. `chan0` tests the **low lane**: `z` from its 16 bits, `n` from
bit 15 (not bit 31), `p` is `>= 0` on it (probes `usse-integer-isub16-value`,
`usse-integer-isub16-zero`, `usse-integer-isub16-sign-n`,
`usse-integer-isub16-sign-p`, `usse-integer-isub16-reg`, `usse-integer-usub16-value`,
`usse-integer-usub16-zero`). The
firmware's counter comparisons read only the low lane **[RE]**, which fits.

`iadd16`, `uadd16`, `imul16` and `umul16` have two lanes too, tested as channels 0 and 2 **[HW]**
(*Test channels*).

**Undecided:** `usub16`'s sign tests.
