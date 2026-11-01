<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### Loops, `call` and `rtn`

*Measured on the hardware (2026-10-24).* `bra` goes to the label's instruction index both ways, and
predicated (`pds-alu-loop`) **[HW]**. There is one return register, not a stack: a single
`call`/`rtn`
returns, a nested one loops and the job fails (`pds-alu-call`) **[HW]**.
