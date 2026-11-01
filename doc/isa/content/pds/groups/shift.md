<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### Shifts: `shl`, `shr`

Opcodes 30 and 31 **[RE]**: `shl dst, src, n` and `shr dst, src, n` with a source from `ds0`,
`ds1`, `ir0` or `ir1` (and, at 130, which the decoder does not name, `tim` **[HW]**) and a
seven-bit amount, which the decoder prints as a signed number widened to 32 bits (so the field
125 prints `4294967293`).

- **Semantics.** `shl` shifts left **[HW]**: our pixel-event program places the tile position with
  `shl` by 3 and the end-of-render bit with `shl` by 20. The amount is the field taken unsigned:
  32-127 give 0, whatever the decoder prints **[HW]**. `shr` is logical, and arithmetic under
  `alum signed`, where 32-127 fill with the sign **[HW]**.

<!-- @prog pds_pixevent.s match='^\s+shl ' -->

<!-- @group pds pat='sh[lr] ' -->
