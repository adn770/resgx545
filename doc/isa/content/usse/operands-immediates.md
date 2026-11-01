<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### Immediates

- **Seven-bit immediates** are source bank 6 (`#0`-`#127`), in sources 1 and 2.
- **The 32-bit move** (`mov dst, #imm32`, class 31) scatters its immediate over three ranges:
  value bits 20-0 in `enc[20:0]`, 25-21 in `enc[40:36]` and 31-26 in `enc[49:44]` **[RE/HW]**.
  The driver patches colours and PBE words into our programs exactly there
  (`doc/specs/fw_format.md` §4, the `USSE_LIMM` patch). For example:

<!-- @example usse mov.skipinv.end o0, #0x12345678 -->

- **The rotated immediate** of the bitwise group (source 2 written as `#imm`) is a 16-bit field
  rotated left by the five-bit rotation field `enc[42:38]` **[HW]** (E474: raw words with the fields
  0xffff, 0x8001 and 0x1234 under all 32 rotations, 96 of 96), so redundant encodings of one value
  agree, and any 32-bit value with at most 16 significant contiguous bits (cyclically) can be
  written directly; the assembler finds the first rotation that fits. `~#X` complements the whole
  32-bit operand after the rotation (19 of 19). A shift or rotate by a rotated immediate uses the
  whole 32-bit value as the amount: `shl` and `shr` give 0 and `asr` the sign for 32 and over, and
  `rol` takes it mod 32 (36 of 36). The assembler refuses values that are not `rotl(m16, r)`
  (0x00010001, 0x55555555, 0x12345678); that no other encoding exists is **[infer]**:

<!-- @example usse and r1, r2, #0x00FF0000 -->

- **Register indices** of `ldr`/`str` are 14 bits in two seven-bit halves (`enc[6:0]` low,
  `enc[20:14]` high), counted in dwords (`ldr r0, #7, drc0` reads `CORE_ID` at offset `0x1c`)
  **[RE/HW]**. A register index is masked to 14 bits **[HW]** (*The 14-bit `ldr`/`str`
  index*).
- **Branch targets** are 18 bits (`enc[17:0]`): absolute for `ba`, signed for `br`.
- Smaller numbers (counts, `phas` operands, the MOE values, emit sidebands) are described with
  their groups.
