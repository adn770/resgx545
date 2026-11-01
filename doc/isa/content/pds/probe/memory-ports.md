<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### `load`, `store`, the fences and the other ports

*Measured on the hardware (2026-10-24).* From the table `probes/pds/load-store.toml`
(recorded). `load` and `store` address the
program's GPU address space from 0: the field is the byte address divided by 4, so they reach the
first 1 MiB, and a fill client has nothing mapped there; every case faulted on the page it named (0,
`0x1000`, `0x10000`), with `BIF_INT_STAT` requestor bit 13, the PDS's own, set
(`pds-load-store-addressing`)
**[HW]**. Their timing and the fences need a mapping there. A `movs` to `mr` leaves `mr01`/`mr23`
reading 0, to `tim` leaves it reading 0, to `ir0` does not change it; `slc` and `douts` show
nothing; after `doutc` the fill's USE task faults storing to page 0 (`pds-load-store-ports`)
**[HW]**. The
`doutu` `EXE` width (*Open questions* 7) needs USE code above 512 KiB of its heap, which the driver
cannot place yet.
