<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### Data moves: `mov16`, `mov32`, `mov64`, `mov128`

Opcodes 1-4 **[RE]**: `mov16 dsB[n], src.h|l` moves a 16-bit half (sources: `ds0`, `ds1`, then
`ir0`, `ir1`, `pc`, `tim`, each `.0` or `.1` (3.2), each `.l` or `.h`); `mov32 dsB[n], src` a
dword (the same sources, whole); `mov64 dsB[2k], src` an aligned pair (from a `ds0`/`ds1`
pair, `mr01` or `mr23`); `mov128 ds[2k], ds[2j]` four dwords, optionally `, swap`.

- **Semantics [HW].** Copies of the named width. `mov16`'s destination index names a 16-bit
  half: `dsB[n]` is the high half of `dsB[n >> 1]` for odd `n`, the low half for even `n`, and
  the other half is kept (so `ds0[96]` is the low half of `ds0[48]`). `mov128 ds[2k]` is the row
  `ds0[2k]`, `ds0[2k+1]`, `ds1[2k]`, `ds1[2k+1]` and `swap` exchanges its two pairs; its source
  reaches `ds[0..30]` only **[RE]**.
- **In the microkernel's programs:** not used; nor in ours.

<!-- @example pds mov16 ds0[3], ds1[2].h -->

<!-- @group pds pat='mov(16|32|64|128) ' -->
