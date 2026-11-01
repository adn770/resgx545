<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### Fences and ALU mode: `rfence`, `rwfence`, `alum`

Opcode 15 is a fence, `rfence` or `rwfence` by `w[0]`, without a predicate; opcode 23 is
`alum signed` or `alum unsigned` (`w[0]`) **[RE]**.

- **Fences [HW]** (E142, E143). Both make earlier `load`s land in their registers: a load's
  dwords appear only at a fence. On their own, or after loads only, both are harmless.
  `rwfence` after a `store` faults on page 0, whatever the store's size and with an `rfence`
  or eight `nop`s between; `rfence` does not, and `rwfence` before a `store` completes. After
  a job faults, `rwfence` faults on page 0 in the jobs after it, even with no `store`, until
  a job without it completes (E144). What the write half of `rwfence` waits for, and why that
  touches page 0, is **[open]**.
- **`alum` [infer].** By the name, a mode switch for the ALU's signedness. Neither the
  microkernel's programs nor ours use the fences or `alum`.

<!-- @group pds pat='^\{0\}$|alum' -->
