<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### Data moves: `mov16`, `mov32`, `mov64`, `mov128`

Opcodes 1-4 **[RE]**: `mov16 dsB[n], src.h|l` moves a 16-bit half (sources: `ds0`, `ds1`, then
`ir0`, `ir1`, `pc`, `tim`, each `.0` or `.1` (3.2), each `.l` or `.h`); `mov32 dsB[n], src` a
dword (the same sources, whole); `mov64 dsB[2k], src` an aligned pair (from a `ds0`/`ds1`
pair, `mr01` or `mr23`); `mov128 ds[2k], ds[2j]` four dwords, optionally `, swap`.

- **Semantics [HW].** Copies of the named width. `mov16`'s destination index names a 16-bit half:
  `dsB[n]` is the high half of `dsB[n >> 1]` for odd `n`, the low half for even `n`, and the other
  half is kept (so `ds0[96]` is the low half of `ds0[48]`). `mov128 ds[2k]` is the row `ds0[2k]`,
  `ds0[2k+1]`, `ds1[2k]`, `ds1[2k+1]` and `swap` exchanges its two pairs; its source field is five
  bits, rows 0-31 (`ds[0..62]`), rows 24-31 the temporaries (rows 24 and 27 read back, E261)
  **[HW]**. With `lastpair` (bit 15) set it writes to both halves of its destination row the
  `ds0` pair the last `mov32` or `movs` read from a data row (rows 0-23): a `mov32` from `ds0[9]`
  or `ds0[2]` and a `movs` to `mr` or `douta` from the pair `ds0[2]`, `ds0[3]` or `ds0[6]`,
  `ds0[7]` name that pair, whatever the `mov128`'s source row, `swap` and other unmapped bits
  (23:16, 9, 7, 1:0); a `mov32` from `ds1[9]`, a `not` of a temporary (`ds0[48-55]` or
  `ds1[48-55]`), a `movs` from the temporary pair `ds0[50]`, `ds0[51]` and a `mov64` from `mr01`
  leave it (E261, E379) **[HW]**. These are the instructions the runs placed before it; others
  (another row or pair, `movsa`, a `not` of a data row, `mr23`) were not run, so the pair after
  them is not known. Since the data rows are read-only, the pair named is its value. The decoders
  print the bit as `, lastpair` after `, swap`; the simulator writes the pair after the
  instructions measured and stops otherwise.
- **In the microkernel's programs:** not used; nor in ours.

<!-- @example pds mov16 ds0[3], ds1[2].h -->

<!-- @group pds pat='mov(16|32|64|128) ' -->
