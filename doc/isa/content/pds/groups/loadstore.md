<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### Memory: `load`, `store`

Opcodes 6 and 7 **[RE]**: `load addr, dsB[48+i ... ]` and `store addr, dsB[48+i ...]` move one to
eight dwords between memory and the registers from `ds0[48]` or `ds1[48]` up. The address is an
18-bit dword index (printed as a byte address, `× 4`); the count reuses the predicate bits
`w[26:24]` (1-8, 0 meaning 8), so these instructions cannot be predicated.

- **Semantics.** The address is absolute in the program's GPU address space, so these reach
  its first 1 MiB **[HW]** (a fill client's loads from 0, `0x1000` and `0x10000` faulted on
  those pages, under the PDS's own `BIF_INT_STAT` requestor bit 13).
- **Timing [HW]** (E143, with the probe's scratch mapped at `0x10000` through the kernel's
  debugfs `sgx/vm_low`). A `load`'s dwords land in its registers only at the next `rfence` or
  `rwfence`. Without one, the registers keep their old values through four `nop`s and up to
  the program's `douta`. A `store` writes the registers as they are at once, so a `load` not
  yet fenced is not in what it stores. A `load` after a `store` of the same dword reads the
  stored value.
- **Store faults [HW]** (E144). A program whose stores total 2, 3 or 4 dwords faults once
  they have landed. That holds for one store of that size or several smaller ones (1 + 1,
  2 + 1, also with an `rfence` between), on any page. A total of 1 or of 5 and more (4 + 1,
  five of 1, 8 + 2, 8 + 8 + 2) completes. `CR_BIF_FAULT` names the first store's page; its low
  bits are the context's directory slot (`CID`) and `SB`, 2 for totals of 2 and 3 for totals of
  3 or 4 (E145). Why these totals fault, and what `SB` encodes, are **[open]**.
- **In the microkernel's programs:** not used; nor in ours.

<!-- @example pds load 0x00001000, ds0[48-51] -->

<!-- @group pds pat='^(load|store) ' -->
