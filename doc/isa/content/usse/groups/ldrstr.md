<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### Register file access: `ldr`, `str`

Class 31, other group, operation 6 **[RE]**. `ldr rD, #idx, drcN` reads SGX register `idx`
(dword index, offset `idx × 4`) into a temporary or `pa` register, counted on a data fence;
`str #idx, src` writes it. The index is a 14-bit immediate or a source-2 register; flags
`.skipinv` and `.nosched`.

- **Semantics [HW].** `ldr r0, #7, drc0` returns `CORE_ID` (`0x01150000`) and `ldr r0, #801`
  returns `BIF_DIR_LIST_BASE0`, from a client pixel shader on our render node; a client
  `str #671` (`USE_G0`) changed nothing (measured on our render node). The firmware
  programs the whole GPU with these two instructions. In a firmware (EDM) task of ours, `ldr r,
  #7` and `#8` returned `CORE_ID` and `CORE_REVISION` as the host reads them (E533).
- **Ordering of memory [HW].** A `stad` and a later `ldad` of one dword return the stored value
  without an `idf`, for an instance's own store too (*Memory, data fences and the register file*,
  E481, E512).
- **Ordering of `str` then `ldr` [HW, firmware task of ours].** In a firmware (EDM) task, a `str`
  to 0x0814 (17 bits) or 0x0a78 (6 bits) was seen by the next `ldr` of the same register and by
  the host, with no fence and at every distance run: 318 of 318 runs in four fresh loads (E534),
  of which 228 of the 306 of the matrix could tell a `str` that landed from one that did not (the
  value finally stored differs from the one the register held; 138 on 0x0814, 90 on 0x0a78).
  Between the two there were 0, 1, 2, 4 or 16 `nop`s, a `wdf` with no load outstanding, an `idf`
  and a `wdf`, an `idf` alone, or a second `str` (the later one wins); a second `ldr` 64 `nop`s
  later read the stored value too; an `ldr` of the other register kept that register's own value,
  and a `str` after an `ldr` did not change what the `ldr` read. Scope: 0x0814 and 0x0a78 only,
  while the EDM is idle and no job runs; the closed task's own writes of them are not excluded, and
  the replicates within a load are not independent. **[infer]** That the two are plain storage, and
  that a backend may emit `str` then `ldr` of 0x0814 or 0x0a78 with nothing between them. **[open]**
  (Q154): a register whose write has an effect, a job running, a register another writer changes,
  the register-index forms (never run), a `str` wider than the register (no run stored one) and the
  time of a `str` (the pair read `CR_TIMER` 3 to 4 counts apart, an upper bound in a unit not
  established). A client `str` is **[open]** (Q134).
- **The index [HW].** `ldr rD, rI` masks a register index to 14 bits (*The 14-bit
  `ldr`/`str` index*); `str` with a register index is **[open]**.
- The decoder holds two copies of these forms (an older one and the class-31 family's); the
  older ones match first.

**In the firmware [RE].** 196 `ldr` and 422 `str`; those with an immediate index touch 191
distinct registers, all of them named SGX545 registers (`doc/specs/hw_spec.md`,
`tools/usse-dis/regtouch.py`).

<!-- @example usse ldr r0, #7, drc0 -->

<!-- @example usse str #671, r1 -->

<!-- @group usse class=31 pat='^(ldr|str)' -->
