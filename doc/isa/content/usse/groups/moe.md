<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### MOE control: `smoa`, `smr`, `smlsi`, `smbo`, `imo`, `setfc`, `moest`

Class 31 with `enc[53:52]` = 1, the operation in `enc[58:56]`, no predicate and `.nosched` in
`enc[50]` **[RE]**. `smoa`, `smr`, `smlsi` and `smbo` take either two register operands
(`enc[51]` set) or immediates:

- `smoa #o1, #o2, #o3, #o4, m1, m2, m3, m4`: four signed 10-bit offsets and four address modes
  (`none`, `repeat`, `clamp`, `mirror`);
- `smr #a, #b, #c, #d` and `smbo #a, #b, #c, #d`: four 12-bit values (ranges and base
  offsets);
- `smlsi i0, i1, i2, i3, <modes>, #l1, #l2, #l3`: four 8-bit operands (`I0`-`I3` in *`smlsi`
  increments*), each a signed increment or, in swizzle mode, a four-component swizzle, then three
  four-bit limits times four;
- `imo #a, #b, #c, #d` (four 12-bit immediates), `setfc #a, #b` (two bits) and
  `moest d, #sel`, which reads a word of the MOE state back into a register: the selector
  names *SMOA*, *SMLSI*, *SMBO* and *SMR* low and high data and an index word.

- **Semantics [infer].** These set the per-operand register stepping that repeats and fetches
  use (*Repeats and the MOE state*): `smoa` an offset and an address mode per operand, `smbo`
  base offsets, `smr` ranges, `smlsi` increments or swizzles. **[HW]** `smlsi`'s four
  increments are the destination's and sources 0, 1 and 2's for a following repeat (*`smlsi`
  increments*). **[HW]** `smbo`'s first, third and fourth values offset the register numbers
  of the destination, source 1 and source 2 (a store's stored register) of every later
  instruction of the task, immediates excepted; the second, by elimination source 0's, showed
  nothing (E087). **[HW]** `smlsi`'s swizzle mode gives repeat iteration k the swizzle's k-th
  component as its register offset; `moest` writes no register and no memory, and `setfc`
  changes nothing a load or a repeat shows (E097). Nor does `moest` load the state word its
  selector names from its register, and `setfc` changes neither a divergent branch nor a
  `.fetch4` load (E109).
- **`smoa` and `smr` [HW]** (E097, E105). `smoa`'s offsets shift each operand's register number
  on every instruction. Its modes map an operand's first register once, from `smr`'s range for
  that operand (fields in the same order: destination, src0, src1, src2). With i = register +
  offset and M = range - 1:
  - `none` gives i;
  - `clamp` gives min(i, M);
  - `mirror` gives 2M - i when i > M;
  - `repeat` gives i - (M + 1) when i > M (once, not modulo).

  A repeat's iterations then step on from that register unmapped. This holds for the
  destination and source 1; source 2 is assumed to follow and source 0 is not measured. A first
  register below `r0` drops writes and reads values from other storage. `imo`, and what `moest`
  and `setfc` are for, remain **[open]**.

**In the firmware [RE].** Only `smlsi`, eight times, at task entry points, always in
increment mode.

<!-- @example usse smr #4, #0, #0, #0 -->

<!-- @group usse class=31 pat='^(smoa|smr|smlsi|smbo|imo|setfc|moest)' -->
