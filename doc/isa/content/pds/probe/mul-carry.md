<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### `mul` signedness and the `adc`/`sbc` carry

*Measured on the hardware (2026-10-24).* `mul` multiplies its halves unsigned, and signed under
`alum signed` (`pds-alu-mul`) **[HW]**. `add` and `sub` leave the high dword of their exact result:
+1
after a carry out, -1 after a borrow, 0 otherwise; `adc` adds it (`a + b + c`) and so does `sbc` (`a
- b + c`), which is what chains a multiword add or subtract (`pds-alu-adc-sbc`) **[HW]**. Every
  other
instruction tried keeps that carry for a later `adc`: `and`, `or`, `xor`, `nor`, `nand`, `shl`,
`shr`, `not`, `abs`, `mul`, `mov16`, `mov32`, `mov64`, `mov128`, `tstz`, `tstn`, `alum` and
`nop` (`pds-after-*`, the carry measured in the default unsigned mode) **[HW]**. `adc` and
`sbc` leave the high dword of their own exact result, as `add` and `sub` do, so the carry chains
through a multiword add (`pds-alu-adc-carry`, unsigned) **[HW]**. Under `alum signed` the carry of
`add` and `sub` is the signed overflow: the `c` for which the exact sum is `signed(r) + c × 2³²`,
so `0x7fffffff + 1` carries +1, `0x80000000 - 1` -1 and `-1 + 1` nothing; read unsigned, the same
rule is the unsigned rule (`pds-alu-signed-carry`; the reading was fitted to its first four cases
and confirmed by three more) **[HW]**; `adc` and `sbc` leave the same signed overflow of their
own result (`pds-alu-signed-adc`) **[HW]**. A port write keeps the carry too (`pds-alu-carry-movs`)
**[HW]**.
