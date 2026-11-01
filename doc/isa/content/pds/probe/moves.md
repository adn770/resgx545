<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### `mov16`, `mov64`, `mov128` and `swap`

*Measured on the hardware (2026-10-24).* `mov16`'s destination index names a 16-bit half: `dsB[n]`
is the high half of `dsB[n >> 1]` when `n` is odd, the low half when even, and the other half is
kept (`pds-moves-mov16`) **[HW]**. `mov64` moves an aligned pair across the banks as named; `mov128
ds[2k]` is the row `ds0[2k]`, `ds0[2k+1]`, `ds1[2k]`, `ds1[2k+1]`, and `swap` exchanges its two
pairs (`pds-moves-mov-wide`) **[HW]**. A `mov16` into a half of a read-only row `dsB[0..47]` lands,
as any write there, in the temporary `dsB[48 + ((n >> 1) & 15)]`, whose other half is kept: the
constant row's other half plays no part (`pds-moves-mov16-constants`, rows inside and past the data
segment) **[HW]**.
