<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### Write masks, byte masks and repeat counts

- **Destination write mask.** `enc[47:44]` (bits w, z, y, x from high to low) prints after the
  destination: `.x` alone prints nothing, `0` prints a lone `.`, the rest name the enabled
  components (`r1.xz`). It shares its bits with the repeat count, chosen by `enc[53]` **[RE]**.
  A component is a register, not a byte: component k writes `d + k` from every register source
  `+ k`, as a repeat of four would, and mask 0 writes nothing **[HW]** (*Write masks*).

<!-- @example usse mov r1.xz, r2 -->

- **Byte masks.** The pack/unpack group writes a byte mask after its destination (`enc[37:34]`,
  printed only when not all four bytes are enabled), and `sop2wm` always prints one **[RE]**.
  The mask is spelled as the Rogue ISR's element selectors: `.eN` for each enabled byte N, in
  rising order (`r10.e0.e2.e3`), and `.enone` for no byte.
  On a pack, mask bit N enables byte N of the destination, and the others keep their values
  **[HW]** (*Pack and unpack lanes*). `sop2wm`'s mask works the same way **[HW]** (*Colour
  operations*).
- **Repeat counts** (`.repeatN`) are described in *Repeats and the MOE state*.
