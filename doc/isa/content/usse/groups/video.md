<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### Video: `adif`, `adifsum`, `bilin`, `firv`, `firh`

Classes 22 and 23 **[RE]**. Class 22 picks by `enc[53:52]`: `adif` (or `adifsum` with
`enc[38]`), `bilin`, `firv`; class 23 is `firh`. All take the multiply flags and a two-bit
predicate, and work on 8-bit data (`u8`, `s8`, `o8`).

- **Semantics.** `adif` is the per-byte absolute difference and `adifsum` the sum of the four
  plus a 16-bit half of `s0` **[HW]**. `bilin` is a bilinear filter with weights in eighths
  from a pair of bytes of its first source; `firv` a two-tap vertical filter per byte column,
  its taps in the third source; `firh` a horizontal FIR filter along the 12 bytes of its three
  sources, with a coefficient set `fcsN` fixed at boot (`fcs2` is H.264's half-pel kernel), a
  centre `#s`, an edge mode `rep`/`msc`/`mdc` and a result byte `#k` **[HW]**. `firh` keeps
  the other three result bytes in a latch per instance slot, which `firv`'s `latch` adds
  **[HW]**. The formats only change how data bytes are read; results are unsigned bytes,
  saturated (*Video*).
- **In the firmware:** not used.

<!-- @example usse adif r1, r2, r3 -->

<!-- @group usse class=22,23 -->
