<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### Data rows, and the banks past the data segment

*Measured on the hardware (2026-10-24).* Sixteen data words come back unchanged through `douta`
(`pds-alu-readback`), and different words in the two banks follow the row rule for every dword of
the
segment (`pds-alu-banks`) **[HW]**. The rows `ds0[0..47]`, `ds1[0..47]` are read-only: a write to
`dsB[n]` lands in the temporary `dsB[48 + (n & 15)]`, so each bank has sixteen writable registers,
`dsB[48..63]`, and the destination's low four bits pick one (`pds-alu-constants`: a write to
`ds1[1]`
appears in `ds1[49]`, one to `ds0[36]` in `ds0[52]`, one to `ds1[19]` in `ds1[51]`) **[HW]**. Past
the data segment the read-only rows hold what earlier tasks left, not zeros. The temporaries are not
cleared between runs: `pds-alu-uninit` read `ds0[60]` and `ds1[60]` as the value an earlier run of
the
same probe had written there **[HW]**.
